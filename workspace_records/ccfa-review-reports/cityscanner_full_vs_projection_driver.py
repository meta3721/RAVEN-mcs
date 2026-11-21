"""Bounded, paired City Scanner comparison. No changes to project source or old runs."""
from __future__ import annotations
import os
for key in ('OMP_NUM_THREADS','MKL_NUM_THREADS','OPENBLAS_NUM_THREADS','NUMEXPR_NUM_THREADS'):
    os.environ[key]='1'
import ctypes, csv, gc, hashlib, json, math, pathlib, sys, time, traceback
from dataclasses import asdict
from datetime import datetime, timezone

ROOT=pathlib.Path('C:/Cursor/raven.mcs')
OUT=ROOT/'results_cityscanner_full_vs_projection_20261018'
REPORT=ROOT/'ccf-review-report/cityscanner_full_vs_projection_20261018'
CPU_LIMIT=1200.0
WALL_LIMIT=1800.0
START_CPU=time.process_time()
START_WALL=time.perf_counter()
LOW_SINCE=None
CURRENT=None

def utc():return datetime.now(timezone.utc).isoformat()
def save(path,obj):
    path=pathlib.Path(path);path.parent.mkdir(parents=True,exist_ok=True)
    tmp=path.with_suffix(path.suffix+'.pending')
    tmp.write_text(json.dumps(obj,ensure_ascii=False,indent=2,default=str)+'\n',encoding='utf-8')
    os.replace(tmp,path)
def memory():
    class MS(ctypes.Structure):
        _fields_=[('length',ctypes.c_ulong),('load',ctypes.c_ulong)]+[(n,ctypes.c_ulonglong) for n in ('total','available','page_total','page_available','virtual_total','virtual_available','extended')]
    s=MS();s.length=ctypes.sizeof(s)
    if not ctypes.windll.kernel32.GlobalMemoryStatusEx(ctypes.byref(s)):raise ctypes.WinError()
    return s.available
def guard():
    global LOW_SINCE
    if time.process_time()-START_CPU>CPU_LIMIT-30:raise RuntimeError('WORKER_CPU_CAP_SAVE_AND_STOP')
    if time.perf_counter()-START_WALL>WALL_LIMIT-30:raise RuntimeError('WALL_CAP_SAVE_AND_STOP')
    avail=memory()
    if avail<2*2**30:
        if LOW_SINCE is None:LOW_SINCE=time.perf_counter()
        elif time.perf_counter()-LOW_SINCE>=30:raise RuntimeError('LOW_AVAILABLE_MEMORY_SAVE_AND_STOP')
    else:LOW_SINCE=None
    return avail

OUT.mkdir(exist_ok=False);REPORT.mkdir(parents=True,exist_ok=False)
save(OUT/'SCOPE_AND_FREEZE.json',{
 'created_utc':utc(),'authorization':'user requests five outlines then direct comparison',
 'question':'Full P2 versus Euclidean projection of the same reconstructed reference',
 'blocks':{'cityscanner':[32001,32002,32003],'pilot2':[33001,33002,33003]},
 'seed_selection':'first three existing trace/model seeds in numeric order; already-used development evidence',
 'arms':['full_p2','reference_projection'],'windows':100,'local_steps':2,
 'design':'preconfigured on throughout','coverage':'diagnostic only',
 'learning_rate':.01,'server_eta':.01,'alpha_max':.5,'e_min':3,
 'projection':'argmin ||alpha-beta_hat||_2^2 subject to same simplex/cap/ESS',
 'projection_source':'scripts/w1_v51a_oracle.py:project_Cr; full two-multiplier routine, not a proxy',
 'selection_correction':'same dataset, target maps, p/q estimation, local Hajek and trace in each pair',
 'no_parameter_search':True,'no_OF_restart':True,'paper_changes':False,
 'metrics':['RMSE_mu','WorstGroupRMSE','Delta_group','Delta_c_s','weight_compute_CPU','instrumented_run_wall'],
 'decision':'descriptive paired effects and dominance; no significance or noninferiority claim from three reused seeds',
 'resources':{'worker_CPU_limit_seconds':CPU_LIMIT,'wall_limit_seconds':WALL_LIMIT,'GPU':0,'workers':1,'torch_threads':1},
 'budget_semantics':'worker process CPU including native single-process computation; outside orchestration CPU not claimed as complete root CPU',
 'partial_runs':'retained, excluded from full endpoint comparisons; no early scientific stop on a losing seed',
 'source':str(pathlib.Path(__file__).resolve()),
})

try:
    if memory()<2.5*2**30:raise RuntimeError('INSUFFICIENT_AVAILABLE_MEMORY_BEFORE_IMPORT')
    k=ctypes.WinDLL('kernel32',use_last_error=True)
    k.GetCurrentProcess.restype=ctypes.c_void_p
    k.SetPriorityClass.argtypes=[ctypes.c_void_p,ctypes.c_uint]
    if not k.SetPriorityClass(k.GetCurrentProcess(),0x4000):raise ctypes.WinError(ctypes.get_last_error())
    sys.path[:0]=[str(ROOT/'src'),str(ROOT/'scripts')]
    import numpy as np
    import torch
    torch.set_num_threads(1);torch.set_num_interop_threads(1)
    import run_nodesign_supplement as ns
    import run_joint_ou_cs_p2 as p2
    import w1_v51a_oracle as oracle
    from raven_mcs.aggregation.base import Aggregator
    from raven_mcs.training.window_runner import build_full_runner
    from raven_mcs.simulation.event_trace import load_event_trace
    from raven_mcs.e3.real_runner.runner import _predict,_mu_weights_for_test
    from raven_mcs.metrics.accuracy import rmse_mu,mae_mu
    from raven_mcs.metrics.distribution import delta_group

    def sha_obj(o):return hashlib.sha256(json.dumps(o,sort_keys=True,default=str).encode()).hexdigest()
    def file_sha(p):return hashlib.sha256(pathlib.Path(p).read_bytes()).hexdigest()
    save(OUT/'ENVIRONMENT.json',{'utc':utc(),'python':sys.executable,'torch':torch.__version__,
      'numpy':np.__version__,'device':'cpu','threads':torch.get_num_threads(),'available_memory_bytes':memory(),
      'below_normal_priority_requested_and_set':True,
      'source_files':{str(p.relative_to(ROOT)):file_sha(p) for p in [
          ROOT/'scripts/run_nodesign_supplement.py',ROOT/'scripts/run_joint_ou_cs_p2.py',ROOT/'scripts/w1_v51a_oracle.py',
          ROOT/'src/raven_mcs/training/window_runner.py',ROOT/'src/raven_mcs/aggregation/methods.py',ROOT/'src/raven_mcs/aggregation/p2_cvxpy.py']}})

    class RecordedAggregator(Aggregator):
        def __init__(self,original,arm):
            self.original=original;self.arm=arm;self.name=arm;self.rows=[];self.cpu=0.;self.wall=0.
        def compute_server_weights(self,p):
            guard();K=len(p.client_ids);ab=min(1.,max(.5,1./K));eb=min(3.,K)
            beta=np.asarray(p.beta_hat,dtype=float);beta=beta/beta.sum()
            c0=time.process_time();w0=time.perf_counter()
            if self.arm=='full_p2':
                a=np.asarray(self.original.compute_server_weights(p),dtype=float)
                kind='full_P2';mult=None
            else:a,kind,mult=oracle.project_Cr(beta,ab,eb)
            call_cpu=time.process_time()-c0;call_wall=time.perf_counter()-w0
            self.cpu+=call_cpu;self.wall+=call_wall
            feasible=oracle.feasibility(a,ab,eb)
            if not np.isfinite(a).all() or feasible>1e-7:raise RuntimeError(f'WEIGHT_FEASIBILITY:{self.arm}:{feasible}')
            row={'active_index':len(self.rows),'client_ids':list(p.client_ids),'beta':beta.tolist(),
                 'M':np.asarray(p.compositions).tolist(),'mu':np.asarray(p.mu).tolist(),
                 'alpha':a.tolist(),'debt':np.asarray(p.debt).tolist(),
                 'variance':np.asarray(p.variance_diag).tolist(),'staleness':np.asarray(p.staleness).tolist(),
                 'alpha_bar':ab,'e_bar':eb,'primal_residual':feasible,'kind':kind,
                 'weight_CPU':call_cpu,'weight_wall':call_wall}
            if mult and kind!='degenerate_uniform':
                kk=oracle.kkt_residuals(a,a-beta,ab,eb,**mult)
                row['projection_KKT']=kk
            self.rows.append(row)
            return a

    results=[];pair_checks=[];baseline_gates={};initials={}
    def run_one(block,setup,seed,arm):
        global CURRENT
        guard();cfg=ns.BLOCKS[block];dataset=cfg['dataset'];dest=OUT/'runs'/block/f'seed{seed}'/arm
        dest.mkdir(parents=True,exist_ok=False);CURRENT={'block':block,'seed':seed,'arm':arm,'window':-1,'path':str(dest)}
        save(OUT/'PROGRESS.json',{'status':'RUNNING','current':CURRENT,'completed':len(results),'utc':utc()})
        trace,ident=load_event_trace(pathlib.Path(cfg['trace_root'])/dataset/f'seed{seed}'/'training_eventtrace')
        assert trace.metadata.num_windows==100
        t0=time.perf_counter();c0=time.process_time()
        r=build_full_runner(trace,setup['ds'],method='raven_mcs',design='on',design_source='user_direct_full_vs_projection',
            n_groups=4,model_seed=seed,learning_rate=.01,local_steps=2,target_mu=setup['mu'],pi_target=setup['pi_target'],
            s_max=5,device='cpu',use_coarse_time_groups=False,pi_opp_joint=setup['pi_opp'])
        before=r._theta_hash();key=(block,seed)
        if key in initials and initials[key]!=before:raise RuntimeError('INITIAL_MODEL_MISMATCH')
        initials[key]=before
        rec=RecordedAggregator(r.aggregator,arm);r.aggregator=rec
        orig=r._process_window
        vers={w:set() for w in range(100)}
        for w,v in zip(trace.events.window_id.astype(int),trace.events.downloaded_version.astype(int)):
            if 0<=w<100:vers[w].add(int(v))
        future={};acc=set()
        for w in reversed(range(100)):future[w]=set(acc);acc|=vers[w]
        def process(w,events):
            guard();wm=orig(w,events)
            assert wm.configured_design==wm.actual_design==1
            needed=future[int(w)]|{int(r.clock.model_version)}
            for v in list(r.model_versions):
                if int(v) not in needed:del r.model_versions[v]
            CURRENT['window']=int(w)
            if int(w)%10==0:
                save(OUT/'PROGRESS.json',{'status':'RUNNING','current':CURRENT,'completed':len(results),
                     'worker_CPU':time.process_time()-START_CPU,'elapsed_wall':time.perf_counter()-START_WALL,'utc':utc()})
                print('progress',block,seed,arm,int(w),flush=True)
            gc.collect();return wm
        r._process_window=process
        try:wms=r.run()
        except Exception:
            save(dest/'INCOMPLETE.json',{'current':CURRENT,'traceback':traceback.format_exc(),'windows_completed':len(r.metrics)})
            torch.save({'theta':r.theta,'method':arm,'window':CURRENT['window'],'ended':False},dest/'partial_model.pt')
            raise
        train_wall=time.perf_counter()-t0;train_cpu=time.process_time()-c0
        pred=_predict(r,setup['ds'],split='test');mu_w=_mu_weights_for_test(pred,setup['mu'])
        rmse=float(rmse_mu(pred['y_pred'],pred['y_true'],mu_w));mae=float(mae_mu(pred['y_pred'],pred['y_true'],mu_w))
        wg=[p2._wrmse_block(pred['y_true'],pred['y_pred'],pred['groups']==g,mu_w) for g in range(4)]
        # Both arms retain the same local Hajek correction. 'raven' is the existing scorer's local-weight role only.
        cs=p2.accumulate_delta_cs(window_metrics=wms,diagnostics=r.diagnostics,atomic=setup['atomic'],pi_target=setup['pi_target'],method='raven')
        active=[wm for wm in wms if wm.active]
        if len(active)!=len(rec.rows):raise RuntimeError('AGGREGATOR_WINDOW_COUNT_MISMATCH')
        for wm,rr in zip(active,rec.rows):rr['window_id']=wm.window_id
        row={'block':block,'dataset':dataset,'seed':seed,'arm':arm,'n_windows':len(wms),'n_active':len(active),
            'RMSE_mu':rmse,'MAE_mu':mae,'WorstGroupRMSE':float(np.nanmax(wg)),'Delta_group':float(delta_group(r.omega_bar(),setup['mu'])),
            'Delta_c_s':float(cs['Delta_c_s']),'weight_compute_CPU':rec.cpu,'weight_compute_wall':rec.wall,
            'instrumented_training_CPU':train_cpu,'instrumented_training_wall':train_wall,
            'trace_hash':ident.get('trace_hash'),'initial_theta_hash':before,'final_theta_hash':r._theta_hash(),
            'configured_design':1,'gate_role':'diagnostic_only','source_method':'raven_mcs/configured-design-v1',
            'max_weight_feasibility_residual':max((x['primal_residual'] for x in rec.rows),default=0.),
            'worker_SGD_clients':sum(int(x.b_r_size) for x in wms),'local_steps':2,
            'solver_warning_count':sum(bool(x.get('warning')) for x in rec.original.solve_results) if arm=='full_p2' else 0,
            'status':'COMPLETE_100_WINDOWS','scored_split':'test from already-used development protocol; no tuning',
            'path':str(dest)}
        save(dest/'RESULT.json',row);save(dest/'weights.json',rec.rows);save(dest/'window_metrics.json',[asdict(w) for w in wms])
        if arm=='full_p2':save(dest/'solver_results.json',rec.original.solve_results)
        np.savez_compressed(dest/'predictions.npz',y_pred=pred['y_pred'],y_true=pred['y_true'],groups=pred['groups'],mu_weights=mu_w)
        torch.save({'theta':r.theta,'initial_theta_hash':before,'method':arm,'complete_windows':len(wms)},dest/'final_model.pt')
        if arm=='full_p2':
            frozen_path=pathlib.Path(cfg['frozen_runs'])/dataset/'raven'/f'seed{seed}'/cfg['frozen_marker']
            old=json.loads(frozen_path.read_text(encoding='utf-8'))
            diffs={k:float(row[k])-float(old[k]) for k in ('RMSE_mu','WorstGroupRMSE','Delta_group','Delta_c_s')}
            gate={'block':block,'seed':seed,'old_source':str(frozen_path),'differences':diffs,
                  'trace_equal':row['trace_hash']==old['eventtrace_hash'],
                  'pass':row['trace_hash']==old['eventtrace_hash'] and max(abs(v) for v in diffs.values())<=1e-7}
            baseline_gates[f'{block}:{seed}']=gate;save(OUT/'BASELINE_REPRODUCTION.json',baseline_gates)
            if not gate['pass']:
                results.append(row);save(OUT/'RESULTS.json',results)
                raise RuntimeError('HISTORICAL_FULL_METHOD_REPRODUCTION_MISMATCH')
        results.append(row);save(OUT/'RESULTS.json',results)
        print('complete',json.dumps(row,ensure_ascii=False),flush=True)
        del r,rec,trace,pred;gc.collect()

    for block,seeds in [('cityscanner',[32001,32002,32003]),('pilot2',[33001,33002,33003])]:
        setup=ns.build_setup(block)
        save(OUT/f'SETUP_{block}.json',{'checks':setup['setup_checks'],'mu':setup['mu'].tolist(),
             'pi_target':[[*k,float(v)] for k,v in sorted(setup['pi_target'].items())],
             'pi_opp':[[*k,float(v)] for k,v in sorted(setup['pi_opp'].items())]})
        for i,seed in enumerate(seeds):
            for arm in (['full_p2','reference_projection'] if i%2==0 else ['reference_projection','full_p2']):
                run_one(block,setup,seed,arm)
            full=json.loads((OUT/'runs'/block/f'seed{seed}'/'full_p2/weights.json').read_text())
            proj=json.loads((OUT/'runs'/block/f'seed{seed}'/'reference_projection/weights.json').read_text())
            if len(full)!=len(proj):raise RuntimeError('PAIRED_ACTIVE_WINDOW_MISMATCH')
            checks={'block':block,'seed':seed,'active_windows':len(full),'clients_equal':True,'max_beta_difference':0.,'max_M_difference':0.}
            for f,p in zip(full,proj):
                if f['window_id']!=p['window_id'] or f['client_ids']!=p['client_ids']:raise RuntimeError('PAIRED_SUPPORT_MISMATCH')
                checks['max_beta_difference']=max(checks['max_beta_difference'],float(np.max(np.abs(np.asarray(f['beta'])-p['beta']))))
                checks['max_M_difference']=max(checks['max_M_difference'],float(np.max(np.abs(np.asarray(f['M'])-p['M']))))
            if max(checks['max_beta_difference'],checks['max_M_difference'])>1e-10:raise RuntimeError('PAIRED_FRONTEND_MISMATCH')
            pair_checks.append(checks);save(OUT/'PAIRING_CHECKS.json',pair_checks)
        del setup;gc.collect()
    save(OUT/'EXECUTION_STATUS.json',{'status':'COMPLETE','completed_runs':len(results),'pairs':len(pair_checks),
        'worker_CPU':time.process_time()-START_CPU,'wall':time.perf_counter()-START_WALL,'utc':utc(),
        'new_training':True,'new_full_seed_confirmation':False,'paper_modified':False})
except Exception as e:
    obj={'status':'STOPPED','reason':repr(e),'traceback':traceback.format_exc(),'current':CURRENT,
         'worker_CPU':time.process_time()-START_CPU,'wall':time.perf_counter()-START_WALL,'utc':utc()}
    save(OUT/'EXECUTION_STATUS.json',obj);save(REPORT/'FAILURE_REPORT.json',obj)
    print(json.dumps(obj,ensure_ascii=False),flush=True)
    raise
