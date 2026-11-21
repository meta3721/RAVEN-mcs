from __future__ import annotations
import json, sys, hashlib
from pathlib import Path
import numpy as np
import pandas as pd
import torch

ROOT = Path(__file__).resolve().parents[1]
OUT = Path(__file__).resolve().parent
sys.path.insert(0, str(ROOT / 'src'))
from raven_mcs.data.base import DatasetMetadata
from raven_mcs.data.processed_dataset import ProcessedDataset
from raven_mcs.e3.canary.dataset_load import load_spatial_to_client, load_horizon
from raven_mcs.e3.stratum_seal.remap import apply_sealed_opportunity_stratum
from raven_mcs.e3.target_pair.target_wiring import production_target_bundle
from raven_mcs.models.features import extract_features
from raven_mcs.simulation.event_trace import load_event_trace

DATASETS = ('traffic', 'sensorscope', 'uair')
SEEDS = (41001, 41002, 41003)

def save(path, obj):
    path = Path(path); path.parent.mkdir(parents=True, exist_ok=True)
    path.write_text(json.dumps(obj, ensure_ascii=False, indent=2, allow_nan=False, default=str), encoding='utf-8')

def sha(path):
    return hashlib.sha256(Path(path).read_bytes()).hexdigest()

def load_dataset(name):
    stage = OUT / 'data' / name
    if not (stage / 'atomic_units.parquet').exists():
        stage.mkdir(parents=True, exist_ok=True)
        atomic = pd.read_parquet(ROOT / 'data/processed' / name / 'atomic_units.parquet')
        if name == 'traffic':
            client = pd.DataFrame([dict(client_id=str(r.spatial_id), unit_id=str(r.unit_id),
                potential_measurement=float(r.target_value), controlled_generator_parameters='{}',
                split=str(r.split), source_trace_id=f'station::{r.spatial_id}::{r.unit_id}')
                for r in atomic.itertuples(index=False)])
        else:
            client = pd.read_parquet(ROOT / 'data/processed' / name / 'client_measurements.parquet')
        atomic.to_parquet(stage / 'atomic_units.parquet', index=False)
        client.to_parquet(stage / 'client_measurements.parquet', index=False)
    meta = DatasetMetadata(**json.loads((ROOT / 'data/interim' / name / 'metadata.json').read_text(encoding='utf-8')))
    ds = ProcessedDataset(stage, meta)
    atomic, seal = apply_sealed_opportunity_stratum(ds.atomic_df, dataset=name, root=ROOT)
    ds._atomic_df = atomic
    return ds

def event_dir(name, seed):
    return OUT / 'eventtraces' / name / f'seed{seed}' / 'training_eventtrace'

def load_inputs(name, seed):
    ds = load_dataset(name)
    trace, ident = load_event_trace(event_dir(name, seed))
    return ds, trace, ident

def delivered_frame(ds, trace):
    lookup = ds._client_df.set_index(['client_id', 'unit_id'])['potential_measurement']
    rows = []
    for rec in trace.events.itertuples(index=False):
        if not int(rec.U): continue
        for uid in rec.observed_unit_ids:
            rows.append(dict(client_id=str(rec.client_id), unit_id=str(uid),
                observation=float(lookup.loc[(str(rec.client_id), str(uid))]), window_id=int(rec.window_id)))
    f = pd.DataFrame(rows)
    f = f.drop_duplicates(['client_id', 'unit_id'], keep='first')
    f = f.merge(ds.atomic_df.drop(columns=['public_features']), on='unit_id', validate='many_to_one')
    if not (f['split'] == 'train').all(): raise RuntimeError('non-training delivery')
    return f.sort_values(['absolute_time', 'client_id', 'unit_id']).reset_index(drop=True)

def features(ds, frame):
    hours = pd.to_datetime(frame.absolute_time, utc=True).astype('datetime64[ns, UTC]').astype('int64').to_numpy() / 3.6e12
    f = extract_features(frame.spatial_id.astype(str).tolist(), hours.tolist(), frame.time_index.astype(int).tolist(),
        ds._spatial_to_idx, int(ds.atomic_df.time_index.max())+1)
    return f

def metric_weights(ds, name, frame):
    bundle = production_target_bundle(root=ROOT, dataset_name=name, dataset=ds)
    groups = frame.target_group.astype(str).to_numpy()
    counts = pd.Series(groups).value_counts()
    mu = dict(zip(bundle['group_id_by_index'], bundle['mu']))
    missing = [g for g, p in mu.items() if p > 0 and g not in counts]
    if missing: raise RuntimeError(f'{name}: positive target groups absent in score split: {missing[:4]}')
    w = np.asarray([mu.get(g, 0.) / counts[g] for g in groups], dtype=np.float64)
    return w / w.sum(), bundle

def score(ds, name, frame, pred):
    w, bundle = metric_weights(ds, name, frame)
    error = np.asarray(pred, dtype=np.float64) - frame.target_value.to_numpy(dtype=np.float64)
    g = pd.DataFrame({'group':frame.target_group.astype(str).to_numpy(), 'sq':error**2})
    return dict(RMSE_mu=float(np.sqrt(w @ (error**2))), MAE_mu=float(w @ np.abs(error)),
        WorstGroupRMSE=float(np.sqrt(g.groupby('group')['sq'].mean().max())), n=len(frame))

def baseline_predictions(train, query, mean=None):
    mean = float(train.observation.mean()) if mean is None else mean
    byspace = train.groupby('spatial_id').observation.mean().to_dict()
    seasonal = train.assign(hour=pd.to_datetime(train.absolute_time, utc=True).dt.hour).groupby(['spatial_id','hour']).observation.mean().to_dict()
    pools = {str(s):f.sort_values('absolute_time').drop_duplicates('absolute_time', keep='last') for s,f in train.groupby('spatial_id')}
    qs = pd.to_datetime(query.absolute_time, utc=True).astype('datetime64[ns, UTC]').astype('int64').to_numpy()/3.6e12
    pred = {x:[] for x in ['train_mean','spatial_mean','persistence','seasonal_mean','seasonal_naive_day','seasonal_naive_week']}
    history = np.zeros((len(query), 30), dtype=np.float32)
    covered = []; seasonal_cov = {24:[],168:[]}; repeated_cov={24:[],168:[]}; ages=[]
    for j,(row,t) in enumerate(zip(query.itertuples(index=False), qs)):
        sid = str(row.spatial_id); sm = float(byspace.get(sid,mean)); base = float(seasonal.get((sid,int(t%24)),sm))
        pool = pools.get(sid)
        times = np.array([]) if pool is None else pd.to_datetime(pool.absolute_time,utc=True).astype('datetime64[ns, UTC]').astype('int64').to_numpy()/3.6e12
        vals = np.array([]) if pool is None else pool.observation.to_numpy()
        i = int(np.searchsorted(times,t,side='left'))
        past = vals[:i]; pt = times[:i]; persistence = float(past[-1]) if i else sm
        covered.append(bool(i)); ages.append(float(t-pt[-1]) if i else None)
        pred['train_mean'].append(mean); pred['spatial_mean'].append(sm); pred['seasonal_mean'].append(base); pred['persistence'].append(persistence)
        for k in range(min(8,i)):
            history[j,k]=float(past[-1-k]); history[j,8+k]=1.; history[j,16+k]=np.log1p(float(t-pt[-1-k]))/np.log(1000.)
        for col,lag in enumerate((24,168)):
            lag_time=t-lag; ix=np.flatnonzero(np.isclose(pt,lag_time,atol=1e-5,rtol=0))
            available=len(ix)>0; value=float(past[ix[-1]]) if available else base
            phase=np.flatnonzero(np.isclose(np.mod(t-pt,lag),0.,atol=1e-5,rtol=0))
            repeated_cov[lag].append(len(phase)>0)
            forecast=float(past[phase[-1]]) if len(phase) else base
            pred['seasonal_naive_day' if lag==24 else 'seasonal_naive_week'].append(forecast)
            history[j,24+col]=value; history[j,26+col]=float(available); seasonal_cov[lag].append(available)
        history[j,28]=base; history[j,29]=persistence
    return {k:np.asarray(v,dtype=np.float64) for k,v in pred.items()}, history, dict(
        history_coverage=float(np.mean(covered)), daily_lag_coverage=float(np.mean(seasonal_cov[24])),
        weekly_lag_coverage=float(np.mean(seasonal_cov[168])), fallback_rate=float(1-np.mean(covered)),
        daily_repeated_phase_coverage=float(np.mean(repeated_cov[24])),weekly_repeated_phase_coverage=float(np.mean(repeated_cov[168])),
        median_age_hours=float(np.median([x for x in ages if x is not None])) if any(covered) else None)
