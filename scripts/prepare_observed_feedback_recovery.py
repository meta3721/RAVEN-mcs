"""Versioned facility/resource-only preparation and narrow interruption audit."""
import json,hashlib,sys,shutil,time
from pathlib import Path
ROOT=Path(__file__).resolve().parents[1];sys.path.insert(0,str(ROOT/'src'))
from observed_feedback_recovery_io import durable_json,file_hash
OUT=ROOT/'results_observed_feedback_autonomous_pilot_45001_recovery_20261015';OLD=ROOT/'results_observed_feedback_autonomous_pilot_45001_20261014'
authpath=ROOT/'src/raven_mcs_observed_feedback/authorization.py';arch=OUT/'old_authorization.py';assert not arch.exists();shutil.copyfile(authpath,arch)
oldmanifest=json.loads((OLD/'PILOT_FROZEN_PLAN.json').read_text())['source_closure'];assert file_hash(arch)==oldmanifest['raven_mcs_observed_feedback/authorization.py']
original=authpath.read_text()
extension='''
@dataclass(frozen=True)
class PilotRecoveryAuthorization(AutonomousPilotAuthorization):
    CPU_limit:float=4800.
    extension:str='user20261015_pilot_interruption_recovery'
    stage_CPU_limit:float=1800.
    stage_wall_limit:float=9000.
    def require(self,*,seed,source):
        if self.strategy not in ('fixed_time_0.5','fixed_time_2','OF-no-Q-stop') or (self.source,self.seed,self.method,self.role,self.T,self.max_steps,self.CPU_limit,self.batch_steps,self.extension,self.stage_CPU_limit,self.stage_wall_limit)!=(PILOT_SOURCE,45001,METHOD_VERSION,'P1_autonomous_P3_pre_pilot',100.,5000,4800.,20000,'user20261015_pilot_interruption_recovery',1800.,9000.):
            raise DependencyPending('not the approved remaining three-arm resource extension')
        if seed!=self.seed or source!=self.source:raise DependencyPending('pilot recovery seed/source mismatch')
'''
updated=original.replace("cls=AutonomousPilotAuthorization if 'strategy' in obj else DiagnosticCollectionAuthorization","cls=PilotRecoveryAuthorization if 'extension' in obj else (AutonomousPilotAuthorization if 'strategy' in obj else DiagnosticCollectionAuthorization)")
assert updated!=original;authpath.write_text(updated+extension,encoding='utf-8')
durable_json(OUT/'SOURCE_RESOURCE_MIGRATION.json',dict(old_manifest=oldmanifest,changed={'raven_mcs_observed_feedback/authorization.py':dict(old=file_hash(arch),new=file_hash(authpath),archive=str(arch),role='explicit resource-only authorization subclass and serialization dispatch; original classes retained')},scientific_parameters_changed=False,old_probability_applicability_retained=True))
# Independent metering entry retains the verified original Job/PID logic.
meter=(ROOT/'scripts/coordinated_windows_cpu_meter.py').read_text()
meter=meter.replace('from pathlib import Path','from pathlib import Path\nfrom observed_feedback_recovery_io import durable_json')
old="(log.with_suffix('.process.json')).write_text(json.dumps(dict(root_pid=pid,root_image=records[pid]['image'],command=[str(x) for x in command],suspended_start=legacy_attach_delay is None,assigned_before_execution=legacy_attach_delay is None),indent=2))"
new="durable_json(log.with_suffix('.process.json'),dict(root_pid=pid,root_image=records[pid]['image'],command=[str(x) for x in command],suspended_start=legacy_attach_delay is None,assigned_before_execution=legacy_attach_delay is None,launch_utc_epoch=time.time()))"
assert old in meter;meter=meter.replace(old,new)
old="log.with_suffix('.meter.json').write_text(json.dumps(result,indent=2),encoding='utf-8')"
assert old in meter;meter=meter.replace(old,"durable_json(log.with_suffix('.meter.json'),result)\n            durable_json(log.with_suffix('.worker_exit.json'),dict(returncode=code.value,limit_reason=reason,job_active_processes=a.active,audit_passed=valid,root_PID=pid,UTC_epoch=time.time()))")
meter=meter.replace('    finally:\n        terminate(job,124)',"    except Exception as exc:\n        durable_json(log.with_suffix('.monitor_exception.json'),dict(error=repr(exc),UTC_epoch=time.time(),final_PID_audit='UNKNOWN',last_valid_root=str(publisher.path.with_name('LAST_VALID_ROOT.json')) if publisher else None))\n        raise\n    finally:\n        terminate(job,124)")
(ROOT/'scripts/observed_feedback_recovery_meter.py').write_text(meter,encoding='utf-8')
# Inspect only this registration/training dependency and one recorded launch.
producer=(ROOT/'src/raven_mcs_observed_feedback/acquisition.py').read_text();backend=(ROOT/'src/raven_mcs_observed_feedback/backend.py').read_text()
assert 'self.next_clock>=100' in producer and 'self.next_client+=1' in producer and 'self.next_clock+=1' in producer
assert "if work['training_started']" in backend and 'self.owner.local_steps!=1' in backend and 'self.local_optimizer_steps+=self.owner.local_steps' in backend
launch=json.loads((OLD/'fixed05_run1.process.json').read_text());assert launch['command'][-2:]==['--strategy','fixed_time_0.5']
assert len(list(OLD.glob('fixed05*process.json')))==1 and not (OLD/'fixed05_resume1').exists()
durable_json(OUT/'FINITE_WORK_AUDIT.json',dict(status='PASS',registered_prefix=3225,persisted_SGD=2493,total_registrations=4300,old_unknown_suffix_upper=1075,old_session_physical_upper=3568,resume_SGD_upper=1075,fixed05_total_physical_upper=4643,batch_physical_upper=16597,one_session_launch=launch,conditions=['causal producer advances only100 clocks x43 clients','one local SGD per observed key','duplicate training rejected','no internal retry in adapter; exception leaves current trajectory','no previous fixed05 recovery session'],scope='structural upper bounds, not measured old suffix; new failed work separately counted'))
# Preserve first registration of activity ledger; increase the conservative
# unmetered prelude to15min, never remove old development time or approval wait.
interval=json.loads((OUT/'ACTIVITY_INTERVAL.json').read_text());durable_json(OUT/'INITIAL_ACTIVITY_INTERVAL.json',interval)
interval['preinitialize_seconds_conservative']=900;durable_json(OUT/'ACTIVITY_INTERVAL.json',interval)
print('RESOURCE_MIGRATION_AND_FINITE_WORK_AUDIT_PASS')
