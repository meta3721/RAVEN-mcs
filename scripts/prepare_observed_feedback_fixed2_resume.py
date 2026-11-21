"""Ordinary facilities repair; exact96 known replayed steps, no scientific change."""
import json,hashlib,shutil
from pathlib import Path
ROOT=Path(__file__).resolve().parents[1];OUT=ROOT/'results_observed_feedback_autonomous_pilot_45001_recovery_20261015'
frozen=json.loads((OUT/'RECOVERY_SCRIPT_FREEZE.json').read_text());archive=OUT/'facilities_v1';archive.mkdir(exist_ok=False)
for name,h in frozen.items():
 p=ROOT/'scripts'/name
 if name=='observed_feedback_recovery_budget.py':
  # Its sole resource-family sum was just repaired; recover the already
  # recorded version with the exact inverse text and verify the old bytes.
  s=p.read_text().replace("family=a.arm.split('_resume')[0] if a.arm else None\n prior_arm_wall=sum(r['wall'] for r in prior['charges'] if r.get('arm') and r['arm'].split('_resume')[0]==family) if a.arm else 0\n arm_limit=(2328.8 if family=='fixed05' else 7200)-prior_arm_wall", "prior_arm_wall=sum(r['wall'] for r in prior['charges'] if r.get('arm')==a.arm) if a.arm else 0\n arm_limit=(2328.8 if a.arm=='fixed05_resume1' else 7200)-prior_arm_wall")
  assert hashlib.sha256(s.encode()).hexdigest()==h;(archive/name).write_text(s,encoding='utf-8',newline='')
 else:assert hashlib.sha256(p.read_bytes()).hexdigest()==h;shutil.copyfile(p,archive/name)
shutil.copyfile(OUT/'RECOVERY_SCRIPT_FREEZE.json',OUT/'RECOVERY_SCRIPT_FREEZE_v1.json')
ap=ROOT/'scripts/observed_feedback_recovery_account.py';s=ap.read_text();assert 'deadline=time.perf_counter()+2.' in s;s=s.replace('deadline=time.perf_counter()+2.','deadline=time.perf_counter()+10.')
ap.write_text(s,encoding='utf-8')
# Same real causal driver, with only its actual restoration adapter and prefix.
s=(ROOT/'scripts/run_observed_feedback_pilot_recovery.py').read_text()
s=s.replace('restore_fixed05,require_resource_source_identity','restore_fixed05,require_resource_source_identity\nfrom observed_feedback_fixed2_restore import restore_fixed2')
s=s.replace("OUT=BATCH/('fixed05_resume1' if STRATEGY=='fixed_time_0.5' else ARM_NAMES[STRATEGY])","OUT=BATCH/'fixed2_resume1'")
s=s.replace("parent_marker=OLD/'fixed05/trajectory/tick0750.complete.json' if STRATEGY=='fixed_time_0.5' else None", "parent_marker=BATCH/'fixed2/trajectory/tick0050.complete.json'")
s=s.replace("offset=1075 if STRATEGY=='fixed_time_0.5' else 0","offset=96")
s=s.replace("(OLD/'fixed05/DECISION_METRICS.jsonl')","(BATCH/'fixed2/DECISION_METRICS.jsonl')").replace("if row['time']>75:break","if row['time']>5:break").replace('assert len(prefix_rows)==750','assert len(prefix_rows)==50').replace('next_tick=751;last_saved=750','next_tick=51;last_saved=50').replace('time=75.,registrations=3225,SGD=2493,grid=750,R1=2493','time=5.,registrations=215,SGD=170,grid=50,R1=170')
s=s.replace('restore_fixed05(OUT,a.root)','restore_fixed2(OUT,a.root)')
s=s.replace('decision_start_tick=751 if parent_marker else 1','decision_start_tick=51').replace("limit=3225 if name=='PRIVATE_EXOGENOUS_PAIRING.jsonl' else 750","limit=215 if name=='PRIVATE_EXOGENOUS_PAIRING.jsonl' else 50").replace("(OLD/'fixed05'/name)","(BATCH/'fixed2'/name)")
s=s.replace('physical_unknown_offset_upper=offset','physical_unknown_offset_upper=0,physical_known_replay_steps=96').replace('(2493 if parent_marker else 0)','(170 if parent_marker else 0)').replace('(75. if parent_marker else 0.)','(5. if parent_marker else 0.)')
compile(s,'fixed2_actual_resume','exec');(ROOT/'scripts/run_observed_feedback_fixed2_resume.py').write_text(s,encoding='utf-8')
v=(ROOT/'scripts/verify_observed_feedback_recovery_arm.py').read_text().replace("choices=('fixed05_resume1','fixed2','noqstop')","choices=('fixed05_resume1','fixed2','fixed2_resume1','noqstop')")
v=v.replace("offset=1075 if args.arm=='fixed05_resume1' else 0", "offset=1075 if args.arm=='fixed05_resume1' else (96 if args.arm=='fixed2_resume1' else 0)")
v=v.replace("assert e['physical_unknown_offset_upper']==offset and e['physical_upper']==e['actual_SGD']+offset","assert e['physical_unknown_offset_upper']==(0 if args.arm=='fixed2_resume1' else offset) and e['physical_upper']==e['actual_SGD']+offset")
v=v.replace('wasted_physical_SGD_lower=0,wasted_physical_SGD_upper=offset','wasted_physical_SGD_lower=96 if args.arm==\'fixed2_resume1\' else 0,wasted_physical_SGD_upper=offset')
v=v.replace("parent_prefix_rows_preserved=750 if args.arm=='fixed05_resume1' else 0,suffix_rows=250 if args.arm=='fixed05_resume1' else len(rows)","parent_prefix_rows_preserved=750 if args.arm=='fixed05_resume1' else (50 if args.arm=='fixed2_resume1' else 0),suffix_rows=250 if args.arm=='fixed05_resume1' else (950 if args.arm=='fixed2_resume1' else len(rows))")
v=v.replace("summary=dict(status='PASS'", "if args.arm=='fixed2_resume1':\n assert e['physical_known_replay_steps']==96\n for name,n in [('DECISION_METRICS.jsonl',50),('DECISION_SNAPSHOTS.jsonl',50),('PRIVATE_EXOGENOUS_PAIRING.jsonl',215)]:\n  with (BATCH/'fixed2'/name).open('rb') as old,(OUT/name).open('rb') as new:assert all(next(old)==next(new) for _ in range(n))\nsummary=dict(status='PASS'")
compile(v,'v2read_only_verifier','exec');(ROOT/'scripts/verify_observed_feedback_recovery_arm_v2.py').write_text(v,encoding='utf-8')
c=(ROOT/'scripts/compare_observed_feedback_recovery_pilot.py').read_text().replace("('fixed05_resume1' if a=='fixed05' else a)","('fixed05_resume1' if a=='fixed05' else ('fixed2_resume1' if a=='fixed2' else a))")
c=c.replace("'RECOVERY_SCRIPT_FREEZE.json'","'RECOVERY_SCRIPT_FREEZE_v2.json'")
(ROOT/'scripts/compare_observed_feedback_recovery_pilot_v2.py').write_text(c,encoding='utf-8')
names=list(frozen)+['observed_feedback_fixed2_restore.py','run_observed_feedback_fixed2_resume.py','verify_observed_feedback_recovery_arm_v2.py','compare_observed_feedback_recovery_pilot_v2.py']
(OUT/'RECOVERY_SCRIPT_FREEZE_v2.json').write_text(json.dumps({n:hashlib.sha256((ROOT/'scripts'/n).read_bytes()).hexdigest() for n in names},indent=2))
(OUT/'FIXED2_REPAIR_PLAN.json').write_text(json.dumps(dict(reason='bounded wait for a fresh sample expired; no NULL, final root/PID audit PASS',failed_now=8.11,failed_actual_steps=266,resume_now=5,resume_logical_steps=170,known_replayed_steps=96,guard='logicalS+96+1<=5000',wait_bound_seconds=10,accepted_sample_max_age_seconds=1,stop_point='stopped_0082_01732 preserved but active trained registration has incomplete audit draw context; restore prior completed frame instead',version='facilities_v2',scientific_rule_changed=False),indent=2))
print('FIXED2_BOUNDARY_RESUME_COMPILES_KNOWN_WASTE96')
