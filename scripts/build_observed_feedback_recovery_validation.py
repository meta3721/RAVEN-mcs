"""Separate read-only validators retain original scientific conditions."""
from pathlib import Path
ROOT=Path(__file__).resolve().parents[1]
s=(ROOT/'scripts/verify_observed_feedback_autonomous_arm.py').read_text()
s=s.replace("choices=('of','of_resume1','fixed05','fixed2','noqstop')","choices=('fixed05_resume1','fixed2','noqstop')")
s=s.replace("BATCH=ROOT/'results_observed_feedback_autonomous_pilot_45001_20261014';OUT=BATCH/args.arm", "OLD=ROOT/'results_observed_feedback_autonomous_pilot_45001_20261014';BATCH=ROOT/'results_observed_feedback_autonomous_pilot_45001_recovery_20261015';OUT=BATCH/args.arm")
s=s.replace("(BATCH/'INITIAL_BACKEND.json')","(OLD/'INITIAL_BACKEND.json')").replace("(BATCH/'PILOT_FROZEN_PLAN.json')","(OLD/'PILOT_FROZEN_PLAN.json')").replace("(BATCH/'PROTECTED_HISTORY.json')","(OLD/'PROTECTED_HISTORY.json')")
s=s.replace("waste=dict(wasted_physical_SGD_lower=0,wasted_physical_SGD_upper=0);assert e['actual_SGD']<=5000", "offset=1075 if args.arm=='fixed05_resume1' else 0\nassert e['physical_unknown_offset_upper']==offset and e['physical_upper']==e['actual_SGD']+offset\nwaste=dict(wasted_physical_SGD_lower=0,wasted_physical_SGD_upper=offset);assert e['physical_upper']<=5000")
s=s.replace('source_packages_unchanged=True','recorded_resource_migration_and_source_valid=True')
s=s.replace("parent_prefix_rows_preserved=0,suffix_rows=len(rows)","parent_prefix_rows_preserved=750 if args.arm=='fixed05_resume1' else 0,suffix_rows=250 if args.arm=='fixed05_resume1' else len(rows)")
s=s.replace("root_publication_partial_attempts='none in this arm'", "root_publication_partial_attempts='old fixed05 final PID/CPU unavailable; this recovery session has independent final audit' if args.arm=='fixed05_resume1' else 'none in this arm'")
insert="""
from observed_feedback_recovery_common import require_resource_source_identity
require_resource_source_identity()
auth=state['collection_authorization'];assert auth['extension']=='user20261015_pilot_interruption_recovery' and auth['CPU_limit']==4800 and auth['stage_CPU_limit']==1800
assert (OUT/'SESSION_DURABLE.json').exists() and (OUT/'SESSION_DURABLE.json.previous').exists()
durable=json.loads((OUT/'SESSION_DURABLE.json').read_text());assert durable['logical_SGD']==e['actual_SGD'] and durable['next_grid']==1001
if args.arm=='fixed05_resume1':
 equality=json.loads((OUT/'RESUMPTION_CHECK.json').read_text());assert equality['original_state_hash_equal_before_any_SGD_or_events'] and equality['producer_RNG_hash_equal'] and equality['numerical_state_unchanged_by_resource_migration']
 for name,n in [('DECISION_METRICS.jsonl',750),('DECISION_SNAPSHOTS.jsonl',750),('PRIVATE_EXOGENOUS_PAIRING.jsonl',3225)]:
  with (OLD/'fixed05'/name).open('rb') as old,(OUT/name).open('rb') as new:
   assert all(next(old)==next(new) for _ in range(n)),'ORIGINAL_PREFIX_CHANGED'
 assert len(rows)==1000 and len(json.loads((OUT/'SUFFIX_DECISION_METRICS.jsonl').read_text().splitlines()[0]))>0
 # The saved prefix is the only state before75; old lost suffix is never read.
 assert state['clock_namespace']==equality['original_clock']
"""
s=s.replace("summary=dict(status='PASS'",insert+"\nsummary=dict(status='PASS'")
s=s.replace("print(json.dumps(summary))","print(json.dumps({k:summary[k] for k in ['status','strategy','full_T100','now','logical_SGD','total_physical_SGD_upper','G_800','W_mean_post20_including_empty','max_actual_request_root_upper']}))")
compile(s,'new_validator','exec');(ROOT/'scripts/verify_observed_feedback_recovery_arm.py').write_text(s,encoding='utf-8')
# Screen formulas are unchanged; retain the already verified OF result.
c=(ROOT/'scripts/compare_observed_feedback_autonomous_pilot.py').read_text()
c=c.replace("OUT=ROOT/'results_observed_feedback_autonomous_pilot_45001_20261014'","OLD=ROOT/'results_observed_feedback_autonomous_pilot_45001_20261014';OUT=ROOT/'results_observed_feedback_autonomous_pilot_45001_recovery_20261015'")
c=c.replace("paths={a:('of_resume1' if a=='of' else a) for a in ARMS}","paths={a:(str(OLD/'of_resume1') if a=='of' else ('fixed05_resume1' if a=='fixed05' else a)) for a in ARMS}")
c=c.replace("scripts=json.loads((OUT/'IMPLEMENTATION_SCRIPT_FREEZE_v2.json').read_text());assert all(hashlib.sha256((ROOT/'scripts'/p).read_bytes()).hexdigest()==h for p,h in scripts.items())", "scripts=json.loads((OUT/'RECOVERY_SCRIPT_FREEZE.json').read_text());assert all(hashlib.sha256((ROOT/'scripts'/p).read_bytes()).hexdigest()==h for p,h in scripts.items())")
c=c.replace("original=json.loads((OUT/'IMPLEMENTATION_SCRIPT_FREEZE.json').read_text());assert all(hashlib.sha256((OUT/'first_session_scripts'/p).read_bytes()).hexdigest()==h for p,h in original.items())", "original=json.loads((OLD/'IMPLEMENTATION_SCRIPT_FREEZE.json').read_text());assert all(hashlib.sha256((OLD/'first_session_scripts'/p).read_bytes()).hexdigest()==h for p,h in original.items())")
compile(c,'new_screen','exec');(ROOT/'scripts/compare_observed_feedback_recovery_pilot.py').write_text(c,encoding='utf-8')
import json,hashlib
names=('observed_feedback_recovery_io.py','observed_feedback_recovery_publisher.py','observed_feedback_recovery_account.py','observed_feedback_recovery_meter.py','observed_feedback_recovery_budget.py','observed_feedback_recovery_common.py','run_observed_feedback_pilot_recovery.py','verify_observed_feedback_recovery_arm.py','compare_observed_feedback_recovery_pilot.py','observed_feedback_pilot_common.py','observed_feedback_pilot_account.py')
frozen={name:hashlib.sha256((ROOT/'scripts'/name).read_bytes()).hexdigest() for name in names}
out=ROOT/'results_observed_feedback_autonomous_pilot_45001_recovery_20261015'
assert not (out/'RECOVERY_SCRIPT_FREEZE.json').exists()
(out/'RECOVERY_SCRIPT_FREEZE.json').write_text(json.dumps(frozen,indent=2))
print('READONLY_VALIDATOR_AND_UNCHANGED_SCREEN_COMPILE')
