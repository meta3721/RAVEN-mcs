"""Thin batch launcher using the existing validated Windows Job root meter."""
import ctypes, json, pathlib, sys, time, os
ROOT=pathlib.Path(__file__).resolve().parents[1]
OUT=pathlib.Path(__file__).resolve().parent
sys.path[:0]=[str(ROOT/'scripts'),str(ROOT/'src')]
from observed_feedback_recovery_io import durable_json
from observed_feedback_recovery_meter import run_coordinated_metered
from raven_mcs_execution import budget as shared_budget
from observed_feedback_recovery_publisher import RecoveryPublisher
shared_budget.RootBudgetPublisher=RecoveryPublisher
ctypes.windll.kernel32.SetPriorityClass(ctypes.windll.kernel32.GetCurrentProcess(),0x4000)
label=sys.argv[1]; cap=float(sys.argv[2]); wall=float(sys.argv[3]); command=sys.argv[4:]
charges=[json.loads(p.read_text()) for p in OUT.glob('charge_*.json')]
prior=30+sum(x['charged_CPU'] for x in charges)
assert prior+cap+5 <=1000
live=OUT/(label+'_root.json');os.environ['OF_ROOT_BUDGET_PATH']=str(live)
os.environ['OF_ARM_WALL_LIMIT']=str(wall)
durable_json(OUT/'LAUNCH_COST.json',dict(label=label,bootstrap_CPU=time.process_time(),used_categories=dict(setup=prior)))
start=time.perf_counter()
try:
 r=run_coordinated_metered(command,OUT/(label+'.log'),cpu_limit=cap,wall_limit=wall,cwd=ROOT,
  budget_feedback=dict(path=str(live),prior_batch=prior,prior_phase=0,batch_limit=1000,phase_limit=cap+5))
 cost=r['process_tree_cpu_seconds']+time.process_time()
 row=dict(label=label,charged_CPU=cost,job_CPU=r['process_tree_cpu_seconds'],launcher_and_monitor_CPU=time.process_time(),audit=r['audit_passed'],returncode=r['returncode'],limit=r['limit_reason'],wall=r['wall_seconds'],actual_CPU=cost)
except Exception as e:
 row=dict(label=label,charged_CPU=cap+5,actual_CPU='UNKNOWN',audit=False,returncode=repr(e),wall=time.perf_counter()-start,traceback=__import__('traceback').format_exc())
durable_json(OUT/('charge_'+label+'.json'),row)
print(json.dumps(row))
raise SystemExit(0 if row['audit'] and row['returncode']==0 else 1)
