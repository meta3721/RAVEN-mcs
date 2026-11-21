"""Generate a separate recovery entry from the frozen causal driver."""
from pathlib import Path
ROOT=Path(__file__).resolve().parents[1]
s=(ROOT/'scripts/run_observed_feedback_autonomous_pilot.py').read_text()
s=s.replace('from observed_feedback_pilot_common import build_arm,OUT as BATCH,ARM_NAMES','from observed_feedback_recovery_common import fresh_arm as build_arm,OUT as BATCH,OLD,ARM_NAMES,restore_fixed05,require_resource_source_identity\nfrom observed_feedback_recovery_io import durable_json\nfrom pathlib import Path')
s=s.replace("OUT=BATCH/ARM_NAMES[STRATEGY]","OUT=BATCH/('fixed05_resume1' if STRATEGY=='fixed_time_0.5' else ARM_NAMES[STRATEGY])")
s=s.replace('from observed_feedback_pilot_account import PilotAccount as RollingAccount','from observed_feedback_recovery_account import RecoveryAccount as RollingAccount')
s=s.replace('    a=RollingAccount(OUT);r=p=None;',"    a=RollingAccount(OUT);a.session_start=time.perf_counter();r=p=None;")
s=s.replace("save_capacity=19.4775;closing_capacity=15.331367", "save_capacity=113.33740118986273 if STRATEGY=='fixed_time_0.5' else 19.4775;closing_capacity=15.331367")
s=s.replace("parent_marker=None;freeze=json.loads((BATCH/'PILOT_FROZEN_PLAN.json').read_text());original_closure=freeze['source_closure'];prefix_rows=[];identity={}","parent_marker=OLD/'fixed05/trajectory/tick0750.complete.json' if STRATEGY=='fixed_time_0.5' else None;freeze=json.loads((OLD/'PILOT_FROZEN_PLAN.json').read_text());original_closure=require_resource_source_identity();prefix_rows=[];identity={};offset=1075 if STRATEGY=='fixed_time_0.5' else 0\n    if parent_marker:\n        for line in (OLD/'fixed05/DECISION_METRICS.jsonl').open():\n            row=json.loads(line)\n            if row['time']>75:break\n            prefix_rows.append(row)\n        assert len(prefix_rows)==750\n        next_tick=751;last_saved=750\n        previous_segment.update(time=75.,registrations=3225,SGD=2493,grid=750,R1=2493)")
s=s.replace('        inputs,runner,producer,frozen=build_arm(STRATEGY,OUT,a.root)',"        if parent_marker:\n            inputs,runner,producer,frozen,equality=restore_fixed05(OUT,a.root)\n            durable_json(OUT/'RESUMPTION_CHECK.json',equality)\n        else:inputs,runner,producer,frozen=build_arm(STRATEGY,OUT,a.root)")
s=s.replace('        assert runner.now==0. and runner.model_version==0 and runner.backend.local_optimizer_steps==0 and not any(runner.debt) and runner.last_release is None',"        if not parent_marker:assert runner.now==0. and runner.model_version==0 and runner.backend.local_optimizer_steps==0 and not any(runner.debt) and runner.last_release is None")
s=s.replace("        with (OUT/'ARM_FROZEN_PLAN.json').open('x') as f:json.dump(frozen,f,indent=2)","        assert not (OUT/'ARM_FROZEN_PLAN.json').exists();durable_json(OUT/'ARM_FROZEN_PLAN.json',frozen)")
s=s.replace("SGD=0)","SGD=runner.backend.local_optimizer_steps)")
s=s.replace("initial_Q_zero=True,initial_L_empty=True", "initial_Q_zero=not any(runner.debt),initial_L_empty=runner.last_release is None")
s=s.replace("parent_run_id=None,parent_checkpoint=None,decision_start_tick=1,", "parent_run_id=identity.get('clock_namespace',{}).get('run_id') if parent_marker else None,parent_checkpoint=str(parent_marker) if parent_marker else None,decision_start_tick=751 if parent_marker else 1,")
s=s.replace("        sizes=json.loads(marker.read_text())['sizes'];growth=", "        a.checkpoint_session(marker,r,p,next_tick,offset)\n        sizes=json.loads(marker.read_text())['sizes'];growth=")
s=s.replace("json.loads((BATCH/'SGD0_AUTONOMOUS_CHECK.json').read_text())", "json.loads((OLD/'SGD0_AUTONOMOUS_CHECK.json').read_text())")
s=s.replace("        (OUT/'ARM_INITIAL_CHECK.json').write_text(json.dumps(check,indent=2));status='STARTED_PREFIX_INCOMPLETE';last_marker=None;persist('tick0000_initial')", "        durable_json(OUT/'ARM_INITIAL_CHECK.json',check);status='STARTED_PREFIX_INCOMPLETE';last_marker=parent_marker\n        if not parent_marker:persist('tick0000_initial')\n        else:a.checkpoint_session(parent_marker,r,p,next_tick,offset)")
s=s.replace("if category=='training' and r.backend.local_optimizer_steps>=5000", "if category=='training' and r.backend.local_optimizer_steps+offset+1>5000")
old="(OUT/'PROGRESS.json').write_text(json.dumps(dict(time=r.now,SGD=r.backend.local_optimizer_steps,grid=next_tick-1,registrations=len(r.attempts),model_version=r.model_version,root_batch_CPU=a.root.read()['batch_used'],remaining_effective_CPU=a.root.read()['effective_remaining'],reserve=a.reserve,forecast_warning=value['warning'],last_complete_marker=str(last_marker)),indent=2))"
new="durable_json(OUT/'PROGRESS.json',dict(time=r.now,SGD=r.backend.local_optimizer_steps,physical_upper=r.backend.local_optimizer_steps+offset,grid=next_tick-1,registrations=len(r.attempts),model_version=r.model_version,root_batch_CPU=a.root.read()['batch_used'],remaining_effective_CPU=a.root.read()['effective_remaining'],reserve=a.reserve,forecast_warning=value['warning'],last_complete_marker=str(last_marker)))"
assert old in s;s=s.replace(old,new)
s=s.replace('r.backend.local_optimizer_steps<=5000','r.backend.local_optimizer_steps+offset<=5000')
# On completion, materialize only the saved750 original rows plus the new250.
needle="                (OUT/'OPERATION_RECORDS.json').write_text(json.dumps(a.records))"
replacement="""                if parent_marker:
                    for name in ('DECISION_METRICS.jsonl','DECISION_SNAPSHOTS.jsonl','PRIVATE_EXOGENOUS_PAIRING.jsonl'):
                        suffix_bytes=(OUT/name).read_bytes();(OUT/('SUFFIX_'+name)).write_bytes(suffix_bytes)
                        limit=3225 if name=='PRIVATE_EXOGENOUS_PAIRING.jsonl' else 750
                        with (OLD/'fixed05'/name).open('rb') as stream:original_prefix=b''.join(next(stream) for _ in range(limit))
                        assert len(original_prefix.splitlines())==limit
                        (OUT/name).write_bytes(original_prefix+suffix_bytes)
                (OUT/'OPERATION_RECORDS.json').write_text(json.dumps(a.records))"""
assert needle in s;s=s.replace(needle,replacement)
s=s.replace("(OUT/'EXECUTION_RESULT.json').write_text(json.dumps(dict(","durable_json(OUT/'EXECUTION_RESULT.json',dict(")
s=s.replace("state='WAITING_USER_REVIEW'),indent=2))", "state='WAITING_USER_REVIEW',physical_unknown_offset_upper=offset,physical_upper=(r.backend.local_optimizer_steps if r else (2493 if parent_marker else 0))+offset,root_final_audit='external .meter.json plus .worker_exit.json'))")
s=s.replace("source_packages_changed=False", "source_packages_changed=True,source_change_role='resource-only explicit authorization migration; original archive retained'")
s=s.replace("now=r.now if r else 0.","now=r.now if r else (75. if parent_marker else 0.)")
# Evidence state JSON is atomically replaced; append-only diagnostics are synced
# together at the full checkpoints instead of rewriting the model per heartbeat.
for name,expr in [('ATTEMPT_LABELS.json','[x.to_dict() for x in r.attempts.values()]'),('PUBLICATION_BRIDGE.json','p.publication_bridge'),('CLOSURES.json','r.closures'),('MERGED_DECISION_METRICS.json','merged'),('OPERATION_RECORDS.json','a.records')]:
 import re
 s=re.sub(r"\(OUT/'"+name+r"'\)\.write_text\(json\.dumps\("+re.escape(expr)+r"(?:,allow_nan=False)?\)\)","durable_json(OUT/'"+name+"',"+expr+")",s)
compile(s,'recovery_entry','exec')
(ROOT/'scripts/run_observed_feedback_pilot_recovery.py').write_text(s,encoding='utf-8')
print('RECOVERY_ENTRY_COMPILES')
