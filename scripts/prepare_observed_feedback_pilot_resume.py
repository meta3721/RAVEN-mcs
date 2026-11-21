"""Facility-only live-root retry and actual saved-state resume; no scientific change."""
from pathlib import Path
import json,hashlib
ROOT=Path(__file__).resolve().parents[1];BATCH=ROOT/'results_observed_feedback_autonomous_pilot_45001_20261014'
old=BATCH/'first_session_scripts';old.mkdir(exist_ok=True)
for name,h in json.loads((BATCH/'IMPLEMENTATION_SCRIPT_FREEZE.json').read_text()).items():
 data=(ROOT/'scripts'/name).read_bytes()
 if name=='observed_feedback_pilot_budget.py' and hashlib.sha256(data).hexdigest()!=h:
  text=data.decode('utf-8').replace(" family=a.arm.split('_resume')[0] if a.arm else None\n arm_wall=sum(x['wall'] for x in prior['charges'] if x.get('arm') and x['arm'].split('_resume')[0]==family) if a.arm else 0", " arm_wall=sum(x['wall'] for x in prior['charges'] if x.get('arm')==a.arm) if a.arm else 0")
  text=text.replace("cats.setdefault('events',0.);cats['events']", "cats['events']");data=text.encode('utf-8')
 assert hashlib.sha256(data).hexdigest()==h
 if (old/name).exists():assert (old/name).read_bytes()==data
 else:(old/name).write_bytes(data)
p=ROOT/'scripts/observed_feedback_pilot_account.py';s=p.read_text()
s=s.replace('class PilotAccount(CategoryAccountant):', '''from raven_mcs_observed_feedback.budget_client import RootClient
class FreshRootClient(RootClient):
    def read(self):
        end=time.perf_counter()+2.
        while True:
            try:return super().read()
            except RuntimeError as exc:
                if str(exc)!='root budget stale; no new operation' or time.perf_counter()>=end:raise
                time.sleep(.01)
class PilotAccount(CategoryAccountant):
    def __init__(self,out):
        super().__init__(out);self.root=FreshRootClient(self.root.path)
''')
p.write_text(s,encoding='utf-8')
s=(ROOT/'scripts/resume_observed_feedback_45011_s2.py').read_text()
s=s.replace("OUT=ROOT/'results_observed_feedback_rolling_45011_20261014_s2';PARENT=ROOT/'results_observed_feedback_continuation_45011_20261014'", "BATCH=ROOT/'results_observed_feedback_autonomous_pilot_45001_20261014';PARENT=BATCH/'of';OUT=BATCH/'of_resume1'")
s=s.replace('from observed_feedback_rolling_costs import RollingAccount','from observed_feedback_pilot_account import PilotAccount as RollingAccount')
s=s.replace('from raven_mcs_observed_feedback.authorization import DiagnosticCollectionAuthorization','from raven_mcs_observed_feedback.authorization import AutonomousPilotAuthorization')
s=s.replace('from raven_mcs_observed_feedback.acquisition import CausalProducer','from observed_feedback_pilot_common import AuditedProducer as CausalProducer')
s=s.replace('from raven_mcs_observed_feedback.controller import Controller','from raven_mcs_observed_feedback.pilot_controller import PilotController as Controller')
s=s.replace('next_tick=11;last_saved=10.7','next_tick=333;last_saved=332.9')
s=s.replace('save_capacity=5.96875;closing_capacity=8.',"save_capacity=121.5559578169703;closing_capacity=15.331367;started_wall=time.perf_counter();wall_cap=float(os.environ['OF_ARM_WALL_LIMIT'])")
s=s.replace("parent_marker=PARENT/'trajectory/stopped_0011_0206.complete.json'","parent_marker=Path(json.loads((PARENT/'EXECUTION_RESULT.json').read_text())['last_complete_marker'])")
s=s.replace("freeze=json.loads((PARENT/'ACQUISITION_FROZEN_PLAN.json').read_text())","freeze=json.loads((PARENT/'ARM_FROZEN_PLAN.json').read_text())")
s=s.replace("(OUT/'PUBLIC_CATALOGUE.parquet').write_bytes((PARENT/'PUBLIC_CATALOGUE.parquet').read_bytes())","(OUT/'PUBLIC_CATALOGUE.parquet').write_bytes((BATCH/'PUBLIC_CATALOGUE.parquet').read_bytes())")
s=s.replace('45011','45001')
s=s.replace('collection_authorization=DiagnosticCollectionAuthorization()','collection_authorization=AutonomousPilotAuthorization(\'OF-v1\')')
s=s.replace("producer=CausalProducer(inputs,restored,np.random.default_rng(0),np.random.default_rng(1))","producer=CausalProducer(inputs,restored,np.random.default_rng(0),np.random.default_rng(1),OUT)")
s=s.replace('restored.now==1.07 and restored.model_version==1 and restored.backend.local_optimizer_steps==32 and priv[\'next_grid_tick\']==11 and producer.next_clock==1 and producer.next_client==3 and producer.active_registration is None',"restored.now==packet['state']['now'] and restored.backend.local_optimizer_steps==1134 and priv['next_grid_tick']==333 and producer.active_registration is None")
s=s.replace('assert len(prefix_rows)==10 and len(restored.decisions)==10','assert len(prefix_rows)==332 and len(restored.decisions)==332')
s=s.replace('restored_now=restored.now,restored_SGD=32,model_version=1,next_grid_tick=11,next_clock=1,next_client=3','restored_now=restored.now,restored_SGD=1134,model_version=restored.model_version,next_grid_tick=333,next_clock=producer.next_clock,next_client=producer.next_client')
s=s.replace('decision_start_tick=11','decision_start_tick=333').replace('r.backend.local_optimizer_steps+22>=5000','r.backend.local_optimizer_steps>=5000')
s=s.replace('control=Controller(root_budget=',"control=Controller('OF-v1',root_budget=")
s=s.replace('            at=round(next_tick*.1,10)',"            if time.perf_counter()-started_wall>=wall_cap-60.:raise RuntimeError('WALL_HEADROOM_SAVE_AND_STOP')\n            at=round(next_tick*.1,10)")
s=s.replace(' if r else 32',' if r else 1134').replace(' if r else 1.07',' if r else 33.29')
s=s.replace('source_packages_changed=False,','source_packages_changed=False,strategy=\'OF-v1\',seed=45001,')
# Preserve original raw suffix/failure in parent; materialize transparent merged read-only streams in new session.
s=s.replace("def final_evidence():\n", "def final_evidence():\n                (OUT/'ARM_FROZEN_PLAN.json').write_bytes((PARENT/'ARM_FROZEN_PLAN.json').read_bytes())\n                (OUT/'ARM_INITIAL_CHECK.json').write_bytes((PARENT/'ARM_INITIAL_CHECK.json').read_bytes())\n")
s=s.replace("(OUT/'MERGED_DECISION_METRICS.json').write_text(json.dumps(merged))", "(OUT/'MERGED_DECISION_METRICS.json').write_text(json.dumps(merged))\n                for name in ('DECISION_METRICS.jsonl','DECISION_SNAPSHOTS.jsonl','PRIVATE_EXOGENOUS_PAIRING.jsonl'):\n                    suffix=(OUT/name).read_bytes();(OUT/('SUFFIX_'+name)).write_bytes(suffix);(OUT/name).write_bytes((PARENT/name).read_bytes()+suffix)")
(ROOT/'scripts/resume_observed_feedback_autonomous_pilot.py').write_text(s,encoding='utf-8')
(BATCH/'IMPLEMENTATION_SCRIPT_FREEZE_v2.json').write_text(json.dumps({n:hashlib.sha256((ROOT/'scripts'/n).read_bytes()).hexdigest() for n in (*json.loads((BATCH/'IMPLEMENTATION_SCRIPT_FREEZE.json').read_text()),'resume_observed_feedback_autonomous_pilot.py')},indent=2))
print('FACILITY_RETRY_AND_TRUE_RESUME_CREATED')
