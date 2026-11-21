"""Predefined one-seed screen, private exogenous pairing, no significance/fitting."""
import json,hashlib
from pathlib import Path
ROOT=Path(__file__).resolve().parents[1];OLD=ROOT/'results_observed_feedback_autonomous_pilot_45001_20261014';OUT=ROOT/'results_observed_feedback_autonomous_pilot_45001_recovery_20261015'
ARMS=('of','fixed05','fixed2','noqstop');summaries={};rows={};snaps={};exogenous={};closures={};paths={a:(str(OLD/'of_resume1') if a=='of' else ('fixed05_resume1' if a=='fixed05' else ('fixed2_resume1' if a=='fixed2' else a))) for a in ARMS}
for arm in ARMS:
 p=OUT/paths[arm]
 if not (p/'VALIDATION_AND_SUMMARY.json').exists():continue
 s=json.loads((p/'VALIDATION_AND_SUMMARY.json').read_text());assert s['status']=='PASS' and s['full_T100'];summaries[arm]=s
 rows[arm]=json.loads((p/'MERGED_DECISION_METRICS.json').read_text())
 exogenous[arm]=[json.loads(x) for x in (p/'PRIVATE_EXOGENOUS_PAIRING.jsonl').read_text().splitlines()]
 assert len(exogenous[arm])==4300 and len({x['key'] for x in exogenous[arm]})==4300
 snaps[arm]={x['time']:x['snapshot'] for x in (json.loads(z) for z in (p/'DECISION_SNAPSHOTS.jsonl').read_text().splitlines())}
 closures[arm]=json.loads((p/'CLOSURES.json').read_text())
complete=len(summaries)==4
result=dict(status='PAIRING_INCOMPLETE',complete=complete,arms_completed=list(summaries),missing=[x for x in ARMS if x not in summaries],result_paths=paths,screen=None,waiting_user_review=True,automatic_next_batch=False)
if complete:
 assert len({json.dumps(s['initial_identity'],sort_keys=True) for s in summaries.values()})==1
 assert sum(s['total_physical_SGD_upper'] for s in summaries.values())<=20000
 base=exogenous['of'];pairing={}
 for arm in ARMS:
  other=exogenous[arm];assert [x['key'] for x in base]==[x['key'] for x in other]
  mismatches=[x['key'] for x,y in zip(base,other) if x['draws_hash']!=y['draws_hash'] or x['R']!=y['R']]
  assert not mismatches,'EXOGENOUS_PAIRING_FAILED_'+arm
  pairing[arm]=dict(exogenous_keys=4300,draw_hash_mismatch=0,R_mismatch=0,E_difference=sum(x['E']!=y['E'] for x,y in zip(base,other)),
   download_version_difference=sum(x['downloaded_version']!=y['downloaded_version'] for x,y in zip(base,other)),actual_service_difference=sum(x['actual_service_notice']!=y['actual_service_notice'] for x,y in zip(base,other)),
   local_CPU_difference=sum(x['training_CPU']!=y['training_CPU'] for x,y in zip(base,other)),
   interpretation='exogenous draws paired;CPU-floor/service,download age,models,consumption andlagged p may differ endogenously')
 comparisons={};G=summaries['of']['G_800'];W=summaries['of']['W_mean_post20_including_empty']
 for arm in ('fixed05','fixed2','noqstop'):
  b=summaries[arm];Gb=b['G_800'];Wb=b['W_mean_post20_including_empty'];rW=(Wb-W)/Wb;rG=(Gb-G)/Gb;dG=G-Gb
  wait=rW>=.05 and dG<=.01;match=rG>=.02 and W<=1.05*Wb
  common=[(x,y) for x,y in zip(rows['of'],rows[arm]) if 20<x['time']<100]
  Qdiff=sum(snaps['of'][x['time']]['debt']!=snaps[arm][x['time']]['debt'] for x,y in common)
  comparisons[arm]=dict(Gb=Gb,Wb=Wb,Gof=G,Wof=W,rW=rW,rG=rG,dG=dG,W_ratio=W/Wb,wait_route=wait,match_route=match,
   protects_wait_quality=dG<=.01,protects_match_wait=W<=1.05*Wb,
   autonomous_action_difference_799=sum(x['action']!=y['action'] for x,y in common),
   dynamic_Q_different_grids=Qdiff,model_version_different_grids=sum(x['model_version_after']!=y['model_version_after'] for x,y in common),
   closure_times_equal=[x['time'] for x in closures['of']]==[x['time'] for x in closures[arm]],
   interpretation='same global time, different endogenous state;not same-state counterfactual')
 primary=comparisons['fixed05'];promising=primary['wait_route'] or primary['match_route']
 dominated=summaries['fixed2']['G_800']<G and summaries['fixed2']['W_mean_post20_including_empty']<W
 # Descriptive Pareto test of the stop-only ablation;no extra utility-screen gate.
 nq=summaries['noqstop'];q_visible_benefit=(G<nq['G_800'] and W<=nq['W_mean_post20_including_empty']) or (W<nq['W_mean_post20_including_empty'] and G<=nq['G_800'])
 qclaim='Q_STOP_DYNAMIC_DESCRIPTIVE_BENEFIT_OBSERVED' if q_visible_benefit else 'Q_STOP_CLAIM_UNSUPPORTED'
 result.update(status='PILOT_UTILITY_PROMISING' if promising else 'PILOT_UTILITY_NOT_ESTABLISHED',screen=primary,main_baseline='fixed_time_0.5',comparisons=comparisons,pairing=pairing,
  secondary_dominates_OF=dominated,utility_risk=bool(promising and dominated),Q_stop_claim=qclaim,
  Q_stop_interpretation='one-seed descriptive only;tradeoff orno improvement cannot establish causal benefit;no adjusted kappa',
  summaries={k:{n:v for n,v in s.items() if n!='configuration'} for k,s in summaries.items()},no_significance=True,
  no_L_ablation=True,no_P2_Q_ablation=True,prediction_performance='NOT_REVALIDATED',q_calibrated=False)
 (OUT/'PAIRING_RESULT.json').write_text(json.dumps(dict(status='PASS',initial_values_identical=True,independent_run_ids=len({s['configuration']['clock_namespace']['run_id'] for s in summaries.values()})==4,
  independent_UTC_origins=len({s['configuration']['clock_namespace']['origin_utc'] for s in summaries.values()})==4,exogenous=pairing),indent=2))
scripts=json.loads((OUT/'RECOVERY_SCRIPT_FREEZE_v2.json').read_text());assert all(hashlib.sha256((ROOT/'scripts'/p).read_bytes()).hexdigest()==h for p,h in scripts.items())
original=json.loads((OLD/'IMPLEMENTATION_SCRIPT_FREEZE.json').read_text());assert all(hashlib.sha256((OLD/'first_session_scripts'/p).read_bytes()).hexdigest()==h for p,h in original.items())
(OUT/'PILOT_COMPARISON.json').write_text(json.dumps(result,indent=2));print(json.dumps({k:v for k,v in result.items() if k not in ('summaries','pairing')}))
