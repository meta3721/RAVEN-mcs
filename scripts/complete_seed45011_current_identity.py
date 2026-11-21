import json
from pathlib import Path
ROOT=Path(__file__).resolve().parents[1];OLD=ROOT/'results_observed_feedback_acquisition_45011_20261014';OUT=ROOT/'results_observed_feedback_continuation_45011_20261014'
v=json.loads((OUT/'SEED_REVIEW.json').read_text())
assert v['status']=='NO_PRIOR_SELECTION_OR_EXECUTION_FOUND'
auth=json.loads((OLD/'AUTHORIZATION.json').read_text());result=json.loads((OLD/'FINAL_EXECUTION_RESULT.json').read_text());fixture=json.loads((OLD/'SGD0_RESULT.json').read_text())
assert auth['seed']==45011 and result['actual_45011_trajectory_started'] is False and result['actual_45011_initialization'] is False and result['SGD']==fixture['SGD']==0
v['matches'] += [dict(path=str(OLD/'AUTHORIZATION.json'),classification='current_pending_authorization',identity=auth),dict(path=str(OLD/'FINAL_EXECUTION_RESULT.json'),classification='current_NOT_STARTED_no_actual_SGD',identity={k:result[k] for k in ('status','actual_45011_initialization','actual_45011_trajectory_started','SGD')}),dict(path=str(OLD/'SGD0_RESULT.json'),classification='current_deterministic_mathematical_fixture_no_trajectory',identity=dict(SGD=fixture['SGD'],status=fixture['status']))]
v['explicit_current_assets']='Prior inventory excluded this then-current output; three known authoritative identities read directly, no rescan.'
v['omission_disposition']={'COLD_NUMERIC_RESULT':'deterministic K43 request; companion FROZEN_INPUT and EXECUTION_COST_PROTOCOL retained','BACKUP_MANIFEST':'source backup inventory, not run identity','SERVICE_FROZEN_AT_20':'44001/43001 histories; parent acquisition frozen plans and run results read','S2_RESULT':'revision feasibility stage; companion frozen plans/seed records read'}
(OUT/'SEED_REVIEW.json').write_text(json.dumps(v,indent=2));print('TARGETED_SEED_REVIEW_COMPLETE_NO_PRIOR_USE_CONFLICT')
