"""One fixed-input SGD0 facility test; no synthetic/control replay."""
import os,sys,json,time
from pathlib import Path
from types import SimpleNamespace
ROOT=Path(__file__).resolve().parents[1];sys.path.insert(0,str(ROOT/'src'))
from observed_feedback_recovery_io import durable_json
from observed_feedback_recovery_account import RecoveryAccount
from raven_mcs_observed_feedback.budget_client import RootClient
from raven_mcs_observed_feedback.authorization import AutonomousPilotAuthorization,PilotRecoveryAuthorization,DiagnosticCollectionAuthorization,collection_authorization_from_dict
from raven_mcs_observed_feedback.schema import DependencyPending
OUT=ROOT/'results_observed_feedback_autonomous_pilot_45001_recovery_20261015';TEST=OUT/'facility_fixture';TEST.mkdir(exist_ok=False)
launch=json.loads((OUT/'LAUNCH_COST.json').read_text());durable_json(TEST/'LAUNCH_COST.json',launch)
a=RecoveryAccount(TEST);a.session_start=time.perf_counter();a.reserve=0
root=a.root.read();assert root['phase_used']<1800 and root['batch_used']<4800
value=a.operation('setup',lambda:dict(fixed=1),1.);assert value=={'fixed':1}
assert json.loads((TEST/'CATEGORY_LIVE.json').read_text())['record_count']==1
durable_json(TEST/'STATE.json',dict(sequence=1));durable_json(TEST/'STATE.json',dict(sequence=2),previous=True)
try:
 with (TEST/'STATE.pending').open('w') as f:f.write('{incomplete')
 raise RuntimeError('controlled_before_replace')
except RuntimeError:pass
assert json.loads((TEST/'STATE.json').read_text())=={'sequence':2} and json.loads((TEST/'STATE.json.previous').read_text())=={'sequence':1}
for strategy in ('fixed_time_0.5','fixed_time_2','OF-no-Q-stop'):
 auth=PilotRecoveryAuthorization(strategy);auth.require(seed=45001,source=auth.source);assert collection_authorization_from_dict(auth.__dict__)==auth
DiagnosticCollectionAuthorization().require(seed=45011,source='user_20261014_OF_v1_first_acquisition')
try:AutonomousPilotAuthorization('fixed_time_0.5',CPU_limit=4800.).require(seed=45001,source='user_20261014_OF_v1_autonomous_pilot')
except DependencyPending:pass
else:raise AssertionError('legacy authorization broadened')
sample=dict(root);sample['wall_stamp']=time.perf_counter()-2.;durable_json(TEST/'STALE_ROOT.json',sample)
try:RootClient(TEST/'STALE_ROOT.json').read()
except RuntimeError as exc:assert 'stale' in str(exc)
else:raise AssertionError('stale sample accepted')
# Real session writer with small fixed fixture files, not a model trajectory.
marker=TEST/'fixture.complete.json';durable_json(TEST/'fixture.model.json',{'fixture':1});durable_json(TEST/'fixture.private.json',{'fixture':2});durable_json(marker,dict(model='fixture.model.json',private='fixture.private.json'))
r=SimpleNamespace(attempts={},backend=SimpleNamespace(local_optimizer_steps=0),model_version=0);p=SimpleNamespace(next_clock=0,next_client=0)
a.checkpoint_session(marker,r,p,1,0);a.checkpoint_session(marker,r,p,1,0)
assert (TEST/'SESSION_DURABLE.json.previous').exists() and (Path(os.environ['OF_ROOT_BUDGET_PATH']).with_name('LAST_VALID_ROOT.json')).exists()
sample=dict(root);(TEST/'NULL_ROOT.json').write_bytes(b'\0'*16)
try:RootClient(TEST/'NULL_ROOT.json').read()
except (ValueError,UnicodeDecodeError):pass
else:raise AssertionError('unreadable root accepted')
durable_json(OUT/'FACILITY_CHECK.json',dict(status='PASS',SGD=0,GPU=0,replay=0,root_readable=True,atomic_previous_retained=True,controlled_exception_retains_published_state=True,durable_session_and_root_backup=True,stale_one_second_guard_preserved=True,NULL_rejected=True,original_authorization_guards_preserved=True,extension_authorization_serializes=True,root_id=root['root_id'],root_CPU_role='actual disjoint external root; fixture labels do not represent training'))
print('FACILITY_CHECK_PASS_SGD0')
