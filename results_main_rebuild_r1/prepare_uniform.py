"""Exact production propensity/coverage pipeline, without neural training.

For U the aggregate-coverage Gate reads only past realized target coverage.
Neither U's alpha nor this Gate depends on model/variance/debt. Neural training
is performed separately on the captured local losses and the exact stale bases.
The zero-update probe is preprocessing, never an experimental method/result.
"""
from __future__ import annotations
import dataclasses, time
from concurrent.futures import ProcessPoolExecutor
from common import *
from raven_mcs.training.window_runner import FullWindowRunner
from raven_mcs.aggregation.base import Aggregator
from raven_mcs.aggregation.method_policy import POLICY_MAP
from raven_mcs.correction.pi_target import build_pi_target
from raven_mcs.e3.real_runner.generator_r3 import build_joint_pi_opp
from raven_mcs.simulation.event_trace import EventTrace
from raven_mcs.models.common_ndmf import deterministic_common_ndmf

class Capture(Aggregator):
    name='rebuild_U'
    def __init__(self): self.rows=[]
    def compute_server_weights(self,p):
        self.rows.append(dict(client_ids=p.client_ids,beta=p.beta_hat.copy(),M=p.compositions.copy(),mu=p.mu.copy()))
        return np.ones(len(p.client_ids))/len(p.client_ids)

class Probe:
    def __init__(self): self.rows=[]
    def train_step(self,model_state,observed_records,a_bar_weights,local_steps):
        self.rows.append(dict(records=observed_records,weights=np.array(a_bar_weights),base=None))
        return np.zeros(1),0.

class UniqueHistoryRunner(FullWindowRunner):
    def _record_sag_window(self,**kwargs):
        before=len(self.sag_state.history)
        super()._record_sag_window(**kwargs)
        if kwargs['window_id']>=self.original_windows:
            del self.sag_state.history[before:]
    def _update_lagged_estimators(self,window_slice,client_data):
        if window_slice.window_id<self.original_windows:
            super()._update_lagged_estimators(window_slice,client_data)

def run_one(spec):
    name,seed=spec; dest=OUT/'prepared'/name/f'seed{seed}'/'uniform_cache.pt'
    if dest.exists():return dict(dataset=name,seed=seed,status='CACHED')
    torch.set_num_threads(1); t=time.monotonic()
    ds,trace,identity=load_inputs(name,seed); N=trace.metadata.num_windows
    mapping=load_spatial_to_client(ROOT,name)
    atomic=ds.atomic_df.copy(); atomic['target_group_main']=atomic.target_group.astype(str)
    pi=build_pi_target(atomic,mapping,split='test')
    pit={(str(r.client_id),str(r.opportunity_stratum)):float(r.pi_k_s_tar) for r in pi.itertuples()}
    strata={}
    for r in atomic.itertuples():
        c=mapping[str(r.spatial_id)];strata.setdefault(c,set()).add(str(r.opportunity_stratum))
    opp=build_joint_pi_opp(sorted(strata),{k:sorted(v) for k,v in strata.items()})
    _,bundle=metric_weights(ds,name,atomic.loc[atomic.split=='validation'])
    events=trace.events.copy()
    replay=events.copy();replay.window_id+=N
    replay.downloaded_version=np.maximum(0,replay.window_id-replay.tau)
    replay.registration_time+=N;replay.arrival_time+=N
    expanded=EventTrace(pd.concat([events,replay],ignore_index=True),dataclasses.replace(trace.metadata,num_windows=2*N))
    agg=Capture(); probe=Probe()
    policy=dataclasses.replace(POLICY_MAP['raven_mcs'],uses_debt=False,
        uses_instant_calibration=False,uses_reference_penalty=False,uses_variance_penalty=False,uses_staleness_penalty=False)
    runner=UniqueHistoryRunner(trace=expanded,dataset=ds,model=deterministic_common_ndmf(ds.num_spatial,seed=seed),
        aggregator=agg,policy=policy,mu=bundle['mu'],num_groups=ds.num_groups,pi_target=pit,
        pi_opp_joint=opp,local_steps=1,seed=seed,s_max=trace.metadata.s_max)
    runner.original_windows=N;runner._trainer=probe
    windows=[]; geometry=[]
    for win in range(2*N):
        start=len(probe.rows); n_payload=len(agg.rows)
        rows=expanded.events.loc[expanded.events.window_id==win].sort_values('client_id')
        metric=runner._process_window(win,expanded.events)
        trained=probe.rows[start:]
        attempted=[r for r in rows.itertuples(index=False) if len(r.observed_unit_ids)]
        if len(attempted)!=len(trained):raise RuntimeError('probe record order mismatch')
        byclient={str(r.client_id):v for r,v in zip(attempted,trained)}
        order=metric.active_clients
        items=[]
        for cid in order:
            er=rows.loc[rows.client_id==cid].iloc[0];v=byclient[cid]
            items.append(dict(client_id=cid,unit_ids=list(er.observed_unit_ids),
                records=v['records'],weights=v['weights'],tau=int(er.tau)))
        record=dict(window_id=win%N,phase='first' if win<N else 'replay',g_r=metric.g_r,clients=items,
            beta=metric.beta_hat,alpha=metric.alpha)
        if len(agg.rows)>n_payload:
            payload=agg.rows[-1];record['M']=payload['M'];record['mu']=payload['mu']
            if win<N:
                M=payload['M'];K=M.shape[1]
                centered=M-M.mean(axis=1,keepdims=True)
                geometry.append(dict(dataset=name,seed=seed,window_id=win,K=K,composition_rank=int(np.linalg.matrix_rank(centered,tol=1e-10)),
                    ess_ratio=min(3,K)/K,cap=max(.5,1/K),singleton=K<=3,gate=metric.g_r))
        windows.append(record)
        runner.model_versions={k:v for k,v in runner.model_versions.items() if k>=runner.clock.model_version-8}
        runner.diagnostics.clear()
    torch.save(dict(windows=windows,trace_hash=identity['trace_hash'],calibration_unique_windows=len(runner.sag_state.history),
        gate_mode='aggregate_coverage',loss_policy=dataclasses.asdict(policy)),dest)
    pd.DataFrame(geometry).to_csv(dest.parent/'geometry.csv',index=False)
    result=dict(dataset=name,seed=seed,status='READY',seconds=time.monotonic()-t,calibration_unique_windows=len(runner.sag_state.history),
        first_design_on=int(sum(x['g_r'] for x in windows[:N])),replay_design_on=int(sum(x['g_r'] for x in windows[N:])))
    save(dest.parent/'uniform_cache_audit.json',result);print('UNIFORM_CACHE',json.dumps(result),flush=True)
    return result

def main():
    with ProcessPoolExecutor(max_workers=3) as ex: results=list(ex.map(run_one,[(d,s) for d in DATASETS for s in SEEDS]))
    save(OUT/'P1_UNIFORM_CACHE_AUDIT.json',results)

if __name__=='__main__': main()
