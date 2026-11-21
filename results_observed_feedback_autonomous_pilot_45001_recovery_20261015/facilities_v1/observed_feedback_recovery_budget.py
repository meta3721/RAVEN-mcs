"""Explicit20261015 resource extension; closed old wall, new activity intervals."""
import json,sys,os,time,argparse,tempfile,math
from pathlib import Path
ROOT=Path(__file__).resolve().parents[1];sys.path.insert(0,str(ROOT/'src'))
OUT=ROOT/'results_observed_feedback_autonomous_pilot_45001_recovery_20261015'
REPORT=ROOT/'ccf-review-report/observed_feedback_autonomous_pilot_45001_recovery_20261015'
OLD=ROOT/'results_observed_feedback_autonomous_pilot_45001_20261014'
from observed_feedback_recovery_io import durable_json,file_hash
def ledger():
 auth=json.loads((OUT/'RESOURCE_AUTHORITY.json').read_text());rows=[json.loads(p.read_text()) for p in sorted(OUT.glob('charge_*.json'))]
 used=30.+sum(r['root_CPU'] for r in rows);interval=json.loads((OUT/'ACTIVITY_INTERVAL.json').read_text())
 excluded=sum(x['seconds'] for x in interval.get('excluded_approval_waits',[]))
 active=interval.get('closed_duration',max(0.,time.time()-interval['start_utc_epoch']-excluded))
 wall=interval['preinitialize_seconds_conservative']+active
 value=dict(stage_limit=1800,stage_charged_CPU=used,stage_remaining_CPU=1800-used,stage_actual_audited_CPU=sum(r['root_CPU'] for r in rows if r['audit']),stage_conservative_CPU=30+sum(r['root_CPU'] for r in rows if not r['audit']),stage_unknown_actual_CPU='unmetered preparation/delivery and any unaudited failure remain UNKNOWN',old_charged_CPU=2983.859375,continuous_CPU_limit=4800,continuous_charged_CPU=2983.859375+used,continuous_remaining_CPU=4800-2983.859375-used,old_wall_snapshot=14373.550642,stage_wall_limit=9000,stage_active_wall=wall,stage_remaining_wall=9000-wall,preinitialize_wall_conservative=interval['preinitialize_seconds_conservative'],excluded_approval_wait_seconds=excluded,continuous_wall_limit=23400,continuous_wall_used=14373.550642+wall,job_actual_wall=sum(r['wall'] for r in rows if r.get('wall_role','measured')=='measured'),categories=dict(setup=30.),charges=rows,state='RUNNING' if 'closed_duration' not in interval else 'WAITING_USER_REVIEW',authority=auth,old_balance_not_extra_authority=True,historical_plus_continuous_CPU=5522.609375+2983.859375+used)
 for r in rows:
  for k,v in r['categories'].items():value['categories'][k]=value['categories'].get(k,0.)+v
 durable_json(OUT/'BUDGET.json',value,previous=True);return value
def main():
 # A dispatch marker is written immediately before the tool asks for external
 # execution approval. There is no worker during that interval. Close it at
 # process entry, not by directory age or by a guessed historical reset.
 pending=OUT/'EXECUTION_APPROVAL_PENDING.json'
 if pending.exists():
  request=json.loads(pending.read_text(encoding='utf-8-sig'));interval=json.loads((OUT/'ACTIVITY_INTERVAL.json').read_text())
  interval.setdefault('excluded_approval_waits',[]).append(dict(start_utc_epoch=request['start'],end_utc_epoch=time.time(),seconds=max(0.,time.time()-request['start']),evidence=request['evidence'],execution='no worker before this command entry'))
  durable_json(OUT/'ACTIVITY_INTERVAL.json',interval);pending.rename(OUT/('APPROVAL_CLOSED_'+request['id']+'.json'))
 p=argparse.ArgumentParser();p.add_argument('--initialize',action='store_true');p.add_argument('--close',action='store_true');p.add_argument('--label');p.add_argument('--arm');p.add_argument('--cap',type=float,default=100);p.add_argument('command',nargs=argparse.REMAINDER);a=p.parse_args()
 if a.initialize:
  OUT.mkdir(exist_ok=False);REPORT.mkdir(exist_ok=False)
  assert json.loads((OLD/'BUDGET.json').read_text())['charged_CPU']==2983.859375
  (OUT/'OLD_BUDGET_IMMUTABLE.json').write_bytes((OLD/'BUDGET.json').read_bytes())
  durable_json(OUT/'RESOURCE_AUTHORITY.json',dict(source='user20261015_pilot_interruption_recovery',instruction='observed-feedback-v1-pilot-interruption-recovery-instruction-20261015.md delivered by human',stage_CPU=1800,continuous_CPU=4800,stage_wall=9000,continuous_wall=23400,fixed05_wall=9000,fixed05_old_wall_envelope=6671.2,fixed05_recovery_wall=2328.8,other_arm_wall=7200,old_CPU=2983.859375,old_wall=14373.550642,physical_steps_each=5000,physical_steps_all=20000,old_fixed05_lost_suffix_upper=1075))
  durable_json(OUT/'ACTIVITY_INTERVAL.json',dict(start_utc_epoch=time.time(),preinitialize_seconds_conservative=300,role='active execution interval only; old closed snapshot not directory age; future user approval excluded'))
  print(json.dumps({k:v for k,v in ledger().items() if k!='charges'}));return 0
 if a.close:
  interval=json.loads((OUT/'ACTIVITY_INTERVAL.json').read_text());excluded=sum(x['seconds'] for x in interval.get('excluded_approval_waits',[]));interval.update(closed_duration=time.time()-interval['start_utc_epoch']-excluded,closed_utc_epoch=time.time());durable_json(OUT/'ACTIVITY_INTERVAL.json',interval);ledger();return 0
 prior=ledger();path=OUT/('charge_'+a.label+'.json');assert not path.exists()
 cap=min(a.cap,prior['stage_remaining_CPU']-8,prior['continuous_remaining_CPU']-8);assert cap>=1
 armout=OUT/a.arm if a.arm else OUT;armout.mkdir(exist_ok=True)
 prior_arm_wall=sum(r['wall'] for r in prior['charges'] if r.get('arm')==a.arm) if a.arm else 0
 arm_limit=(2328.8 if a.arm=='fixed05_resume1' else 7200)-prior_arm_wall
 wall_cap=min(prior['stage_remaining_wall'],23400-prior['continuous_wall_used'],arm_limit if a.arm else 300)
 if wall_cap<=0:raise RuntimeError('ACTIVITY_WALL_EXHAUSTED')
 live=Path(tempfile.mkdtemp(prefix='root_feedback_',dir=armout))/'root.json';os.environ['OF_ROOT_BUDGET_PATH']=str(live);os.environ['OF_ARM_WALL_LIMIT']=str(wall_cap)
 os.environ['OF_RECOVERY_STAGE_OUT']=str(OUT)
 bootstrap=time.process_time();durable_json(armout/'LAUNCH_COST.json',dict(label=a.label,bootstrap_CPU=bootstrap,used_categories=prior['categories'],prior_batch=prior['continuous_charged_CPU'],prior_phase=prior['stage_charged_CPU'],wall_cap=wall_cap))
 cmd=a.command[1:] if a.command[:1]==['--'] else a.command
 from raven_mcs_execution import budget as shared
 from observed_feedback_recovery_publisher import RecoveryPublisher
 shared.RootBudgetPublisher=RecoveryPublisher
 from observed_feedback_recovery_meter import run_coordinated_metered
 start=time.perf_counter();durable_json(OUT/('launch_'+a.label+'.json'),dict(command=cmd,UTC_epoch=time.time(),wall_cap=wall_cap,CPU_cap=cap,arm=a.arm,root_path=str(live)))
 try:
  r=run_coordinated_metered(cmd,OUT/(a.label+'.log'),cpu_limit=cap,wall_limit=wall_cap,cwd=ROOT,budget_feedback=dict(path=str(live),prior_batch=prior['continuous_charged_CPU']+bootstrap,prior_phase=prior['stage_charged_CPU']+bootstrap,batch_limit=4800,phase_limit=1800))
  cost=r['process_tree_cpu_seconds']+time.process_time();cats={'setup':cost}
  if a.arm and (armout/'CATEGORY_LIVE.json').exists():
   cats=json.loads((armout/'CATEGORY_LIVE.json').read_bytes())['spent'];cats.setdefault('events',0.);cats['events']+=max(0.,cost-sum(cats.values()))
  row=dict(label=a.label,arm=a.arm,root_CPU=cost,job_CPU=r['process_tree_cpu_seconds'],driver_CPU=time.process_time(),categories=cats,wall=r['wall_seconds'],wall_role='measured',exit=r['returncode'],audit=r['audit_passed'],limit=r['limit_reason'],root_feedback=str(live),actual_worker_state='exited',final_PID_audit=str(OUT/(a.label+'.meter.json')))
 except Exception as exc:
  # Reserve the allocated cap after an unaudited failure; never relabel it as actual.
  row=dict(label=a.label,arm=a.arm,root_CPU=cap+bootstrap,categories={'repair':cap+bootstrap},wall=time.perf_counter()-start,wall_role='observed exception envelope',exit=repr(exc),audit=False,actual_CPU='UNKNOWN',traceback=__import__('traceback').format_exc(),last_valid_root=str(live.with_name('LAST_VALID_ROOT.json')))
 durable_json(path,row);durable_json(OUT/('EXIT_'+a.label+'.json'),row)
 v=ledger();print(json.dumps({k:v[k] for k in ['stage_charged_CPU','stage_remaining_CPU','continuous_charged_CPU','stage_active_wall','stage_remaining_wall']}))
 return 0 if row['audit'] and row['exit']==0 else 1
if __name__=='__main__':raise SystemExit(main())
