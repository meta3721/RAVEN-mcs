"""One parent, one resident worker, two pre-frozen read-only requests."""
import json,sys,time,subprocess,hashlib
from pathlib import Path
ROOT=Path(__file__).resolve().parents[1];sys.path.insert(0,str(ROOT/'src'));sys.path.insert(0,str(ROOT/'scripts'))
OUT=ROOT/'results_observed_feedback_persistent_cost_20261014'
from raven_mcs_observed_feedback.budget_client import read_shared_json
from coordinated_windows_cpu_meter import process_times
rows=[];responses={}
def sample_after(wall):
    while True:
        sample=read_shared_json(OUT/'ROOT_BUDGET_LIVE.json')
        if not sample['finished'] and sample['wall_stamp']>=wall+.01:return sample
        time.sleep(.005)
def flush():
    (OUT/'LIVE_PHASE_RESULT.json').write_text(json.dumps(dict(measurements=rows,responses=responses),indent=2))
def record(label,begin,end,local,parent_cpu,child_cpu,wall,*,first=False):
    bootstrap=json.loads((OUT/'LAUNCH_COST.json').read_text())['launcher_bootstrap_CPU'] if first else 0.
    delta=end['command_used']-(begin['command_used'] if begin else 0.)+bootstrap
    monitor=end['driver_CPU']-(begin['driver_CPU'] if begin else 0.)
    floor=parent_cpu+child_cpu+monitor+bootstrap
    row=dict(label=label,root_sample_difference_CPU=delta,conservative_root_upper_CPU=max(delta+.02,floor+.02),
        parent_process_CPU=parent_cpu,worker_process_CPU=child_cpu,outer_monitor_CPU=monitor,
        local_CPU=local,wall=wall,root_begin=begin,root_end=end,PID_floor_not_added_to_total=True)
    rows.append(row);return row
hash_before=hashlib.sha256((OUT/'FROZEN_INPUT.json').read_bytes()).hexdigest()
started=time.perf_counter();err=(OUT/'WORKER_STDERR.log').open('x',encoding='utf-8')
worker=subprocess.Popen([sys.executable,str(ROOT/'scripts/observed_feedback_persistent_worker.py')],cwd=ROOT,
    stdin=subprocess.PIPE,stdout=subprocess.PIPE,stderr=err,text=True,encoding='utf-8',bufsize=1)
worker_handle=int(worker._handle)
ready=json.loads(worker.stdout.readline());assert ready['kind']=='READY' and ready['solver_calls']==0 and ready['cache_entries']==0
assert ready['input_hash']==hash_before
end=sample_after(time.perf_counter())
init=record('INITIALIZATION',None,end,None,time.process_time(),process_times(worker_handle)['cpu_seconds'],time.perf_counter()-started,first=True)
status='PERSISTENT_REQUEST_COST_CHECK_PASSED' if init['conservative_root_upper_CPU']<=6 else 'COST_REVISION_FAILED'
stop_reason=None if status.endswith('PASSED') else 'INITIALIZATION_EXCEEDS_6'
try:
    if status.endswith('PASSED'):
        for label in ('A','B'):
            request=dict(op='DECIDE',label=label,input_hash=hash_before)
            begin=sample_after(time.perf_counter());pcpu=time.process_time();ccpu=process_times(worker_handle)['cpu_seconds'];wall=time.perf_counter()
            worker.stdin.write(json.dumps(request,separators=(',',':'))+'\n');worker.stdin.flush()
            text=worker.stdout.readline();reply=json.loads(text)
            assert reply['label']==label and reply['pid']==ready['pid']
            assert reply.get('error') or all(k in reply['preview'] for k in ('fingerprint','dependency_hash','keys','alpha','M','omega','ell','age'))
            # Minimal necessary commit payload was received and parsed before this endpoint.
            end=sample_after(time.perf_counter());row=record('ONLINE_'+label,begin,end,reply.get('Controller_CPU'),
                time.process_time()-pcpu,process_times(worker_handle)['cpu_seconds']-ccpu,time.perf_counter()-wall)
            replies_valid=not reply.get('error') and reply['current_binding_valid'] and reply['new_binding_object']
            expected=(reply.get('P2'),reply.get('cache'),reply.get('original_solver_calls'))==((1,0,1) if label=='A' else (0,1,0))
            replies_valid=replies_valid and expected and (label!='B' or reply['reused_numeric_object'])
            responses[label]=reply;row['response_bytes']=len(text.encode());row['semantic_checks_passed']=replies_valid
            flush()
            if not replies_valid or row['conservative_root_upper_CPU']>2:
                status='COST_REVISION_FAILED';stop_reason='ONLINE_'+label+'_INVALID_OR_OVER_2';break
    final_begin=time.perf_counter();pcpu=time.process_time();ccpu=process_times(worker_handle)['cpu_seconds']
    worker.stdin.write(json.dumps(dict(op='FINALIZE'))+'\n');worker.stdin.flush()
    finalized=json.loads(worker.stdout.readline());assert finalized['kind']=='FINALIZED'
    worker.stdin.close();worker.wait(timeout=15);assert worker.returncode==0
    final=dict(parent_CPU=time.process_time()-pcpu,worker_CPU=process_times(worker_handle)['cpu_seconds']-ccpu,
        wall=time.perf_counter()-final_begin,worker_dump_CPU=finalized['dump_CPU'],includes_shutdown=True)
    old=json.loads((ROOT/'results_observed_feedback_readiness_20261014/COLD_NUMERIC_RESULT.json').read_text())['numeric']
    audit=json.loads((OUT/'FULL_WORKER_AUDIT.json').read_text());new=audit['numeric']
    consistency=None
    if new:
        diff={field:max(abs(a-b) for a,b in zip(new[field],old[field])) for field in ('alpha','omega')}
        diff.update(ell=abs(new['ell']-old['ell']),age=abs(new['age']-old['age']))
        # Prior four-path consistency tolerances; not adjusted in response to this result.
        consistency=all(x<=1e-7 for x in diff.values())
        finite=all(__import__('math').isfinite(x) for field in ('alpha','omega','beta','masses') for x in new[field]) and all(__import__('math').isfinite(x) for x in audit['objective_terms'].values())
        numeric_valid=finite and new['solver']['normalized_weight_residual']<=1e-7
        if not consistency or not numeric_valid:status='COST_REVISION_FAILED';stop_reason='NUMERIC_OR_CONSISTENCY_FAILED'
    else:diff=None;numeric_valid=False
    assert audit['same_state_fingerprint'] and audit['consumed_keys']==audit['closures']==audit['SGD']==0
    assert hashlib.sha256((OUT/'FROZEN_INPUT.json').read_bytes()).hexdigest()==hash_before
    flush()
    (OUT/'PERSISTENT_COST_RESULT.json').write_text(json.dumps(dict(status=status,stop_reason=stop_reason,READY=ready,measurements=rows,
        finalization_local=final,numeric_valid=numeric_valid,old_result_consistency=consistency,max_abs_difference=diff,
        initialized_workers=1,request_labels=list(responses),input_hash=hash_before,no_model_or_clock_update=True,
        old_P3_remains='FAIL',SGD=0,GPU=0,q_fit=0,real_random_trajectories=0,next_status='WAITING_USER_REVIEW'),indent=2))
    print(json.dumps(dict(status=status,measurements=[dict(label=r['label'],root_upper=r['conservative_root_upper_CPU']) for r in rows],consistency=consistency)))
finally:
    if worker.poll() is None:worker.kill();worker.wait()
    err.close()
