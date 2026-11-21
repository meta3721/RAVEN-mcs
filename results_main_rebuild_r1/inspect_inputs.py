from pathlib import Path
import json, sys
import pandas as pd
import torch

ROOT = Path(__file__).resolve().parents[1]
sys.path.insert(0, str(ROOT / 'src'))
from raven_mcs.e3.canary.dataset_load import load_spatial_to_client, load_horizon

print('DEVICE', torch.cuda.get_device_name(0) if torch.cuda.is_available() else 'cpu', flush=True)
for name in ['traffic', 'sensorscope', 'uair']:
    a = pd.read_parquet(ROOT / 'data/processed' / name / 'atomic_units.parquet')
    c = pd.read_parquet(ROOT / 'data/processed' / name / 'client_measurements.parquet')
    print(name, 'columns', a.columns.tolist(), c.columns.tolist(), flush=True)
    print('atomic', a.head(2).to_dict('records'), flush=True)
    print('measure', c.head(2).to_dict('records'), flush=True)
    print('splits', a.groupby('split').agg(n=('unit_id','size'), tmin=('absolute_time','min'), tmax=('absolute_time','max'), mean=('target_value','mean'), sd=('target_value','std')).to_string(), flush=True)
    print('mapping', len(load_spatial_to_client(ROOT, name)), 'clients', len(set(load_spatial_to_client(ROOT, name).values())), 'horizon', load_horizon(ROOT, name), flush=True)
