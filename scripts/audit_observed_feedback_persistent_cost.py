"""Retained raw evidence audit only; no controller or numerical imports."""
import json,hashlib,math
from pathlib import Path
ROOT=Path(__file__).resolve().parents[1]
OUT=ROOT/'results_observed_feedback_persistent_cost_20261014'
REPORT=ROOT/'ccf-review-report/observed_feedback_persistent_cost_20261014'
baseline=json.loads((OUT/'PROTECTED_BEFORE.json').read_text())
changed=[p for p,h in baseline.items() if not Path(p).exists() or hashlib.sha256(Path(p).read_bytes()).hexdigest()!=h]
assert not changed,changed
frozen=json.loads((OUT/'FROZEN_EXECUTION.json').read_text())
assert all(hashlib.sha256((ROOT/p).read_bytes()).hexdigest()==h for p,h in frozen['source_hashes'].items())
result=json.loads((OUT/'PERSISTENT_COST_RESULT.json').read_text());audit=json.loads((OUT/'FULL_WORKER_AUDIT.json').read_text())
meter=json.loads((OUT/'persistent_A_B.meter.json').read_text())
assert result['status']=='PERSISTENT_REQUEST_COST_CHECK_PASSED'
actual_pid=result['READY']['pid'];retained=[p for p in meter['pids'] if p['pid']==actual_pid]
assert len(retained)==1 and retained[0]['root_job_member'] and retained[0]['cpu_seconds']>0
assert result['request_labels']==['A','B'] and result['initialized_workers']==1
assert result['READY']['solver_calls']==result['READY']['cache_entries']==0
assert len(audit['solver_calls'])==1 and audit['consumed_keys']==audit['closures']==audit['SGD']==0
assert len(audit['numeric']['alpha'])==43 and len(audit['numeric']['omega'])==172
assert all(math.isfinite(x) for row in audit['numeric']['M'] for x in row)
assert audit['numeric']['solver']['normalized_weight_residual']<=1e-7
phases=result['measurements'];corrections=[]
for phase in phases:
    if phase['label']=='INITIALIZATION':
        bootstrap=phase['root_sample_difference_CPU']-phase['root_end']['command_used']
        worker_cpu=result['READY']['CPU'];worker_source='worker process_time to READY construction; root includes serialization/startup'
    else:
        bootstrap=0.;label=phase['label'].split('_')[-1]
        worker_cpu=next(p['request_CPU_including_response_serialization'] for p in audit['responses'] if p['label']==label)
        worker_source='actual worker self-reported process_time interval including response serialization/flush; actual PID independently retained in root audit'
    corrected=max(phase['root_sample_difference_CPU']+.02,phase['parent_process_CPU']+worker_cpu+phase['outer_monitor_CPU']+bootstrap+.02)
    assert corrected==phase['conservative_root_upper_CPU']
    assert corrected<=(6 if phase['label']=='INITIALIZATION' else 2)
    corrections.append(dict(label=phase['label'],actual_worker_local_CPU=worker_cpu,source=worker_source,
        recalculated_root_upper=corrected,original_upper_unchanged=True))
addendum=dict(issue='Popen handle measures venv launcher, not its real interpreter; raw worker_process_CPU zeros must not be interpreted as actual worker cost',
    root_all_descendants_unaffected=True,actual_worker_PID=actual_pid,actual_worker_final_retained_CPU=retained[0]['cpu_seconds'],
    method='Recalculate only upward max floor using already retained worker process_time intervals; no rerun and no PID added to total root cost',
    phases=corrections,finalization_worker_dump_CPU=result['finalization_local']['worker_dump_CPU'],
    finalization_root_remaining=json.loads((OUT/'FINALIZATION_ROOT_COST.json').read_text())['remaining_root_CPU'],
    missing='Direct live API per-phase differences for the actual child PID were not sampled; raw launcher handle cannot supply them')
with (OUT/'MEASUREMENT_ADDENDUM.json').open('x') as f:json.dump(addendum,f,indent=2)
check=dict(status='PERSISTENT_REQUEST_COST_CHECK_PASSED',protected_files_checked=len(baseline),changed_protected_files=[],
    frozen_protocol_source_match=True,old_input_bytes_identical=(OUT/'FROZEN_INPUT.json').read_bytes()==(ROOT/'results_observed_feedback_readiness_20261014/FROZEN_INPUT.json').read_bytes(),
    numerical_requests=2,solver_calls=1,READY_without_solve=True,no_state_or_model_update=True,
    old_cold_failure_preserved=True,worker_PID_root_verified=True,measurement_addendum='MEASUREMENT_ADDENDUM.json',
    collection_entry_implemented=False,SGD=0,GPU=0,q_fit=0,trajectories=0,state='WAITING_USER_REVIEW')
with (OUT/'FINAL_DELIVERY_CHECK.json').open('x') as f:json.dump(check,f,indent=2)
print(json.dumps(check))
