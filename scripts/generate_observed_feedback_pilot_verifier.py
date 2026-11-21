"""Adapt already verified read-only invariants to independent pilot arms."""
from pathlib import Path
ROOT=Path(__file__).resolve().parents[1]
s=(ROOT/'scripts/verify_and_summarize_rolling45011.py').read_text()
s=s.replace("OUT=ROOT/'results_observed_feedback_rolling_45011_20261014_s2';PARENT=ROOT/'results_observed_feedback_continuation_45011_20261014'","import argparse\nparser=argparse.ArgumentParser();parser.add_argument('--arm',required=True,choices=('of','fixed05','fixed2','noqstop'));args=parser.parse_args()\nBATCH=ROOT/'results_observed_feedback_autonomous_pilot_45001_20261014';OUT=BATCH/args.arm")
s=s.replace("freeze=json.loads((PARENT/'ACQUISITION_FROZEN_PLAN.json').read_text())","freeze=read('ARM_FROZEN_PLAN.json')")
s=s.replace("state['seed']==45011","state['seed']==45001")
a=s.index('prefix=[json.loads');b=s.index('snapshots={}',a)
s=s[:a]+"assert len(rows)==sum(1 for _ in (OUT/'DECISION_METRICS.jsonl').open())\n"+s[b:]
s=s.replace('for directory in (PARENT,OUT):','for directory in (OUT,):')
s=s.replace("def differences(part,field):return sum(x['action']!=x['shadow'][field] for x in part)","def differences(part,field):\n if any(x['shadow'].get(field) is None for x in part):return None\n return sum(x['action']!=x['shadow'][field] for x in part)")
s=s.replace(" comp=row['components'];assert", " comp=row['components']\n if not comp:continue\n assert")
s=s.replace("component_ranges={name:","component_rows=[x for x in nonforced if x['components']]\ncomponent_ranges={name:")
s=s.replace("for x in nonforced),maximum=max(x['components'][name] for x in nonforced),mean=sum(x['components'][name] for x in nonforced)/len(nonforced))","for x in component_rows),maximum=max(x['components'][name] for x in component_rows),mean=sum(x['components'][name] for x in component_rows)/len(component_rows))")
s=s.replace(" if nonforced else {}"," if component_rows else {}")
s=s.replace('previous_R1=32','previous_R1=0')
a=s.index("protected=json.loads(");b=s.index('eligible=[',a)
s=s[:a]+'''protected=json.loads((BATCH/'PROTECTED_HISTORY.json').read_text());changed=[p for p,h in protected.items() if hashlib.sha256(Path(p).read_bytes()).hexdigest()!=h];assert not changed
waste=dict(wasted_physical_SGD_lower=0,wasted_physical_SGD_upper=0);assert e['actual_SGD']<=5000
initial=read('ARM_INITIAL_CHECK.json');shared=json.loads((BATCH/'PILOT_FROZEN_PLAN.json').read_text());assert initial['initial_identity']==shared['initial_identity']
assert state['collection_authorization']['strategy']==freeze['strategy']==state['probability_applicability']['strategy']
assert state['calibration_only'] and not state['isolated_test']
''' +s[b:]
s=s.replace('parent_prefix_rows_preserved=10,suffix_rows=len(rows)-10','parent_prefix_rows_preserved=0,suffix_rows=len(rows)')
s=s.replace("root_publication_partial_attempts='S1 preserved, not merged into final causal grid; SGD/cost accounted separately'","root_publication_partial_attempts='none in this arm',strategy=freeze['strategy'],method=freeze['method'],seed=45001,q_role='diagnostic_prior_not_calibrated',configuration=freeze,initial_identity=initial['initial_identity']")
s=s.replace("performance='RESULTS_NOT_REVALIDATED'","performance='PREDICTION_RESULTS_NOT_REVALIDATED_SINGLE_SEED_CONTROL_PILOT_ONLY'")
(ROOT/'scripts/verify_observed_feedback_autonomous_arm.py').write_text(s,encoding='utf-8')
print('PILOT_VERIFIER_CREATED')
