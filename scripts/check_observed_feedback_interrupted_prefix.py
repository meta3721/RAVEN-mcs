"""Read-only interruption audit; no replay, solver, training, or probability fitting."""
import json,sys,hashlib,time
from pathlib import Path
ROOT=Path(__file__).resolve().parents[1];sys.path.insert(0,str(ROOT/'src'))
OUT=ROOT/'results_observed_feedback_autonomous_pilot_45001_20261014';ARM=OUT/'fixed05'
import importlib.util
# Load the unchanged hashing helper directly: package __init__ pulls optional
# training dependencies into an otherwise standard-library-only read audit.
spec=importlib.util.spec_from_file_location('readonly_original_hashing',ROOT/'src/raven_mcs/utils/hashing.py')
hashing=importlib.util.module_from_spec(spec);spec.loader.exec_module(hashing)
sha256_json=hashing.sha256_json
marker=ARM/'trajectory/tick0750.complete.json';record=json.loads(marker.read_text())
assert record['schema']=='paired_checkpoint_commit_v1'
mp=marker.parent/record['model'];pp=marker.parent/record['private']
assert hashing.sha256_file(mp)==record['model_hash'] and hashing.sha256_file(pp)==record['private_hash']
packet=json.loads(mp.read_text());private=json.loads(pp.read_text());state=packet['state'];identity=record['identity']
assert packet['method']==state['config']['method_version']==identity['method']
assert state['seed']==identity['seed'] and state['clock_namespace']==private['clock_namespace']==identity['clock_namespace']
assert private['checkpoint_hash']==record['model_hash'] and private['T']==state['experiment_end']
assert abs(private['tick']*state['config']['grid']-state['now'])<=1e-9
assert sha256_json(state)==packet['state_hash']
assert state['now']==75 and state['backend']['local_optimizer_steps']==2493 and state['model_version']==128
assert len(state['attempts'])==3225 and private['next_grid_tick']==751
assert state['collection_authorization']['strategy']=='fixed_time_0.5' and state['calibration_only'] and not state['isolated_test']
assert state['backend']['theta']==state['backend']['versions']['128']
for p,h in packet['source_closure'].items():assert hashlib.sha256((ROOT/'src'/p).read_bytes()).hexdigest()==h
protected=json.loads((OUT/'PROTECTED_HISTORY.json').read_text());assert all(hashlib.sha256(Path(p).read_bytes()).hexdigest()==h for p,h in protected.items())
files=[]
for p in [ARM/'CATEGORY_LIVE.json',ARM/'root_feedback_lgdpze5u/root.json',OUT/'fixed05_run1.log']:
 b=p.read_bytes();files.append(dict(path=str(p),bytes=len(b),all_null=bool(b) and not any(b),hash=hashlib.sha256(b).hexdigest(),mtime=p.stat().st_mtime))
# Prefix pairing only; never substitutes for four complete trajectories.
def lines(p):
 valid=[];invalid=0
 for line in p.read_bytes().splitlines():
  try:valid.append(json.loads(line))
  except (ValueError,UnicodeDecodeError):invalid+=1
 return valid,invalid
fixed,invalid=lines(ARM/'PRIVATE_EXOGENOUS_PAIRING.jsonl');of,_=lines(OUT/'of_resume1/PRIVATE_EXOGENOUS_PAIRING.jsonl')
bykey={x['key']:x for x in of};usable=[x for x in fixed if x['key'] in state['attempts']]
assert len(usable)==3225 and len({x['key'] for x in usable})==3225
assert all(x['draws_hash']==bykey[x['key']]['draws_hash'] and x['R']==bykey[x['key']]['R'] for x in usable)
result=dict(status='PREFIX_PAIR_READABLE_SOURCE_AND_HISTORY_UNCHANGED',full_T100=False,marker=str(marker),now=75,grid=750,next_grid=751,registrations=3225,logical_SGD=2493,model_version=128,source_files_checked=len(packet['source_closure']),protected_history_files_checked=len(protected),model_private_sizes=record['sizes'],private_next_clock=private['state']['next_clock'],private_next_client=private['state']['next_client'],private_active_registration=private['state']['active_registration'],prefix_exogenous_keys_paired=3225,invalid_tail_exogenous_lines=invalid,damaged_files=files,unpersisted_suffix='after t75 until unknown process termination; not restored from logs',physical_SGD_lower=2493,physical_SGD_upper=5000,physical_upper_role='authorization and frozen per-operation guard; exact lost suffix UNKNOWN; not measured physical steps',full_online_maximum_and_PID_audit='UNKNOWN for interrupted suffix',training=0,replay=0,q_fit=0,checked_at=time.time())
(OUT/'INTERRUPTED_PREFIX_CHECK.json').write_text(json.dumps(result,indent=2));print(json.dumps(result))
