from __future__ import annotations
import json, time, argparse
from concurrent.futures import ProcessPoolExecutor
import pandas as pd
import numpy as np
import torch
from common import *
from raven_mcs.e3.real_runner.generator_r3 import materialize_r3_trace

def prepare_one(spec):
    name,seed=spec; t=time.monotonic()
    ds=load_dataset(name); mapping=load_spatial_to_client(ROOT,name)
    ep=event_dir(name,seed)
    if not ep.exists():
        print(f'TRACE_START {name} {seed}',flush=True)
        materialize_r3_trace(dataset=name, atomic=ds.atomic_df, spatial_to_client=mapping,
            out_dir=ep.parent, seed=seed, num_windows=int(load_horizon(ROOT,name)['chosen_E3_formal_windows']),
            m_mc=2000, delivery_mode='nominal')
    ds,trace,ident=load_inputs(name,seed); train=delivered_frame(ds,trace)
    query=ds.atomic_df.loc[ds.atomic_df.split=='validation'].reset_index(drop=True)
    predictions,history,coverage=baseline_predictions(train,query)
    rows=[dict(dataset=name,seed=seed,baseline=k,**score(ds,name,query,p),**coverage) for k,p in predictions.items()]
    out=OUT/'prepared'/name/f'seed{seed}'; out.mkdir(parents=True,exist_ok=True)
    train.to_parquet(out/'delivered.parquet',index=False)
    pd.DataFrame(rows).to_csv(out/'validation_baselines.csv',index=False)
    result=dict(dataset=name,seed=seed,n_unique_delivered=len(train),n_observed_usable=sum(len(x) for x in trace.events.loc[trace.events.U==1,'observed_unit_ids']),
        trace_hash=ident['trace_hash'],n_windows=trace.metadata.num_windows,**coverage,elapsed_seconds=time.monotonic()-t)
    k=trace.events.loc[(trace.events.U==1)&trace.events.observed_unit_ids.map(bool)].groupby('window_id').client_id.nunique()
    result.update(n_active_windows=len(k), K_median=float(k.median()),K_max=int(k.max()),singleton_share=float((k<=3).mean()),K_ge8_share=float((k>=8).mean()))
    save(out/'audit.json',result)
    print(f'TRACE_DONE {name} {seed} {json.dumps(result)}',flush=True)
    return result

def main():
    for name in DATASETS: load_dataset(name)
    config=dict(date='2026-10-12', stage='P0_P1',datasets=list(DATASETS), seeds=list(SEEDS),
        information_track='offline_train_delivered_only_no_validation_or_test_history',
        score_domain='physical_input_targets_exact_frozen_spatial_time_mu',
        optimizer_grid={'central':[ ['adam',x] for x in [3e-4,1e-3,3e-3]]+[['sgd',x] for x in [1e-3,1e-2,3e-2]],
            'uniform_local_adam_lr':[3e-4,1e-3,3e-3], 'server_rho':[0.5,1.]},
        budget_nodes=[1,3,10,30,100,200],batch_size=64,local_max_batches=5,plateau_threshold=0.005,
        meaningful_gain=0.02,second_backbone='historical_residual_64_32',
        device=torch.cuda.get_device_name(0) if torch.cuda.is_available() else 'cpu',torch_version=torch.__version__,
        plan='ccfa-review-reports/raven-mcs-main-experiment-rebuild-design-20261011.md',
        test_access='metadata audit only; no test baseline or neural scoring during selection')
    save(OUT/'P0_P1_FROZEN_CONFIG.json',config)
    audits=[]
    for name in DATASETS:
        ds=load_dataset(name); a=ds.atomic_df
        parts={s:dict(n=len(f),tmin=str(f.absolute_time.min()),tmax=str(f.absolute_time.max()),n_spatial=f.spatial_id.nunique()) for s,f in a.groupby('split')}
        audits.append(dict(dataset=name,splits=parts,train_label_scale_diagnostic={'mean':ds.target_mean,'std':ds.target_std},
            measurement_source='station=client exact target measurement, same as formal TrafficE3Dataset' if name=='traffic' else 'frozen controlled client measurement',
            source_atomic_sha=sha(ROOT/'data/processed'/name/'atomic_units.parquet'),source_client_sha=sha(ROOT/'data/processed'/name/'client_measurements.parquet')))
    save(OUT/'P0_DATA_AUDIT.json',audits)
    with ProcessPoolExecutor(max_workers=3) as ex:
        records=list(ex.map(prepare_one,[(d,s) for s in SEEDS for d in DATASETS]))
    save(OUT/'P0_SUPPLY_AUDIT.json',records)
    frames=[pd.read_csv(OUT/'prepared'/d/f'seed{s}'/'validation_baselines.csv') for d in DATASETS for s in SEEDS]
    pd.concat(frames,ignore_index=True).to_csv(OUT/'P0_VALIDATION_BASELINES.csv',index=False)
    print('P0_COMPLETE',flush=True)

if __name__=='__main__': main()
