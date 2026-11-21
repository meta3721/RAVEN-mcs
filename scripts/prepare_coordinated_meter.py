"""Preserve legacy meter; generate a readable root-feedback fork of its loop."""
from pathlib import Path
root=Path(__file__).resolve().parents[1]
source=(root/'scripts/windows_cpu_meter.py').read_text()
signature='def run_metered(command, log, *, cpu_limit, wall_limit, cwd, legacy_attach_delay=None):'
init="log=Path(log);start=time.perf_counter();cpu0=time.process_time()"
progress='total=(a.user+a.kernel)/1e7+time.process_time()-cpu0'
for token in (signature,init,progress):assert source.count(token)==1
source=source.replace(signature,'def run_coordinated_metered(command, log, *, cpu_limit, wall_limit, cwd, legacy_attach_delay=None, budget_feedback=None):')
source=source.replace(init,init+"\n    from raven_mcs_execution.budget import RootBudgetPublisher\n    publisher=RootBudgetPublisher(budget_feedback,cpu_limit) if budget_feedback else None")
source=source.replace(progress,progress+"\n                if publisher:publisher.publish((a.user+a.kernel)/1e7,time.process_time()-cpu0)")
source=source.replace("return result\n    finally:","if publisher:publisher.publish(total,time.process_time()-cpu0,force=True,finished=True)\n            return result\n    finally:")
with (root/'scripts/coordinated_windows_cpu_meter.py').open('x',encoding='utf-8') as f:f.write(source)
print('legacy meter unchanged; coordinated root loop created')
