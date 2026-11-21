"""Reuse verified causal execution/pair lifecycle; fresh45001 arm dispatch."""
from pathlib import Path
ROOT=Path(__file__).resolve().parents[1]
s=(ROOT/'scripts/resume_observed_feedback_45011_s2.py').read_text()
s=s.replace("OUT=ROOT/'results_observed_feedback_rolling_45011_20261014_s2';PARENT=ROOT/'results_observed_feedback_continuation_45011_20261014'","from observed_feedback_pilot_common import build_arm,OUT as BATCH,ARM_NAMES\nargs=argparse.ArgumentParser();args.add_argument('--strategy',required=True,choices=list(ARM_NAMES));args=args.parse_args();STRATEGY=args.strategy\nOUT=BATCH/ARM_NAMES[STRATEGY];OUT.mkdir(exist_ok=True)")
s=s.replace('from raven_mcs_observed_feedback.controller import Controller','from raven_mcs_observed_feedback.pilot_controller import PilotController as Controller')
s=s.replace('next_tick=11;last_saved=10.7;last_sizes=None;previous_segment=None','next_tick=1;last_saved=0;last_sizes=None;previous_segment=dict(time=0.,registrations=0,R1=0,SGD=0,notices=0,grid=0,spent=dict.fromkeys(a.spent,0.),driver_CPU=0.,cost_record_count=0)')
s=s.replace('save_capacity=5.96875;closing_capacity=8.',"save_capacity=19.4775;closing_capacity=15.331367;started_wall=time.perf_counter();wall_cap=float(os.environ['OF_ARM_WALL_LIMIT'])")
a=s.index('    parent_marker=PARENT/');b=s.index('    def append(',a)
s=s[:a]+"    parent_marker=None;freeze=json.loads((BATCH/'PILOT_FROZEN_PLAN.json').read_text());original_closure=freeze['source_closure'];prefix_rows=[];identity={}\n"+s[b:]
a=s.index('    def restore_actual():');b=s.index('    def persist(name):',a)
s=s[:a]+'''    def restore_actual():
        nonlocal identity
        inputs,runner,producer,frozen=build_arm(STRATEGY,OUT,a.root)
        assert source_closure()==original_closure
        assert runner.now==0. and runner.model_version==0 and runner.backend.local_optimizer_steps==0 and not any(runner.debt) and runner.last_release is None
        identity=dict(method=runner.config.method_version,seed=45001,clock_namespace=runner.clock_namespace)
        with (OUT/'ARM_FROZEN_PLAN.json').open('x') as f:json.dump(frozen,f,indent=2)
        return runner,producer,dict(status='PASS',strategy=STRATEGY,initial_identity=frozen['initial_identity'],initial_Q_zero=True,initial_L_empty=True,isolated_test=False,calibration_only=True,SGD=0)
''' +s[b:]
s=s.replace("identity['clock_namespace']['run_id']","r.clock_namespace['run_id']").replace('decision_start_tick=11','decision_start_tick=1')
s=s.replace("(OUT/'RESUMPTION_CHECK.json')","(OUT/'ARM_INITIAL_CHECK.json')")
s=s.replace('last_marker=parent_marker',"last_marker=None;persist('tick0000_initial')")
s=s.replace('r.backend.local_optimizer_steps+22>=5000','r.backend.local_optimizer_steps>=5000')
s=s.replace('control=Controller(root_budget=','control=Controller(STRATEGY,root_budget=')
s=s.replace('            at=round(next_tick*.1,10)',"            if time.perf_counter()-started_wall>=wall_cap-60.:raise RuntimeError('WALL_HEADROOM_SAVE_AND_STOP')\n            at=round(next_tick*.1,10)")
s=s.replace("shadow=shadow_actions(context['shadow'],d)","shadow=shadow_actions(context['shadow'],d) if STRATEGY in ('OF-v1','OF-no-Q-stop') else dict(forced=d.reason in {'TERMINAL','WARMUP','DEADLINE','MIN_CLIENTS'},no_Q_stop=None,no_Q_B=None,P2_recomputed=False,OF_same_state=None)")
s=s.replace(' if r else 32',' if r else 0').replace(' if r else 1.07',' if r else 0.')
s=s.replace('parent_checkpoint=str(parent_marker),decision_start_tick=1,source_packages_changed=False','parent_checkpoint=None,decision_start_tick=1,source_packages_changed=False,strategy=STRATEGY,seed=45001')
c=(ROOT/'scripts/observed_feedback_rolling_costs.py').read_text().replace('class RollingAccount(CategoryAccountant):','class PilotAccount(CategoryAccountant):')
c=c.replace('time=1.07,registrations=46,SGD=32,notices=16,grid=10','time=0.,registrations=0,SGD=0,notices=0,grid=0')
c=c.replace("current['registrations']-46","current['registrations']").replace('tick-10','tick')
(ROOT/'scripts/observed_feedback_pilot_account.py').write_text(c,encoding='utf-8')
s=s.replace('from observed_feedback_rolling_costs import RollingAccount','from observed_feedback_pilot_account import PilotAccount as RollingAccount')
(ROOT/'scripts/run_observed_feedback_autonomous_pilot.py').write_text(s,encoding='utf-8')
print('PILOT_DRIVER_CREATED')
