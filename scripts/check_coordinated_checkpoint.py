"""One deterministic facility case, real-size paired save, zero model execution."""
import json,time,sys
from pathlib import Path
from action_difference_revision_budget import ROOT,OUT
from raven_mcs_execution.budget import RootBudgetReader,RootBudgetPublisher,checkpoint_due
from raven_mcs_execution.paired_checkpoint import PairedCheckpointStore,read_legacy_pair
if __name__=='__main__':
    budget=RootBudgetReader(OUT/'ROOT_BUDGET_LIVE.json');initial=budget.read()
    old=ROOT/'results_re_interval_development_44001_20261013/trajectory'
    model,private=read_legacy_pair(old/'PERIODIC_RESUME_tick0800.json',old/'PERIODIC_RESUME_producer_tick0800.json')
    identity=dict(method=model['method'],seed=44001,clock_namespace=model['state']['clock_namespace'])
    tag=sys.argv[1] if len(sys.argv)>1 else ''
    store=PairedCheckpointStore(OUT/('facility_pairs'+tag))
    # The measurement is admitted while the root has ample fixture budget.
    cpu=time.process_time();wall=time.perf_counter()
    first=store.publish('01_measurement',model,private,identity,budget=budget,save_reserve=1.)
    measured_cpu=time.process_time()-cpu;measured_wall=time.perf_counter()-wall
    reserve=2*measured_cpu+.5
    live=budget.read();assert live['batch_used']>=initial['batch_used'] and live['driver_CPU']>=initial['driver_CPU']
    # Synthetic *accounting inputs* test external growth; they are not billed as
    # measured CPU. The actual root ledger independently admits both saves.
    fake=RootBudgetPublisher(dict(path=str(OUT/'MODELLED_ACCOUNTING.json'),prior_batch=0.,prior_phase=0.,batch_limit=reserve+10,
        phase_limit=reserve+10),reserve+10)
    fake.publish(1.,.25,force=True);reader=RootBudgetReader(OUT/'MODELLED_ACCOUNTING.json')
    assert reader.can_plan(reserve,operation_root_ceiling=4.)
    fake.publish(1.,8.6,force=True)
    assert not reader.can_plan(reserve,operation_root_ceiling=4.);reader.require_save(reserve)
    assert checkpoint_due(811,800,remaining=reader.read()['effective_remaining'],save_reserve=reserve,operation_root_ceiling=4.)
    second=store.publish('02_before_stop',model,private,identity,budget=budget,save_reserve=reserve)
    try:store.publish('03_interrupted',model,private,identity,budget=budget,save_reserve=reserve,interrupt_after_model=True)
    except InterruptedError:pass
    else:raise AssertionError('interruption not injected')
    assert not (store.root/'03_interrupted.complete.json').exists()
    assert store.latest(expected_identity=identity)==second
    store.read(first,expected_identity=identity)
    read_legacy_pair(old/'PERIODIC_RESUME_tick0800.json',old/'PERIODIC_RESUME_producer_tick0800.json')
    result=dict(status='PASS',one_deterministic_case=True,training=0,SGD=0,new_collection=0,
        legacy_sizes=[(old/'PERIODIC_RESUME_tick0800.json').stat().st_size,(old/'PERIODIC_RESUME_producer_tick0800.json').stat().st_size],
        measured_pair_CPU=measured_cpu,measured_pair_wall=measured_wall,save_reserve_CPU=reserve,
        reserve_status='measurement-based engineering margin, not a universal worst-case guarantee',
        root_admission_before_save=live,modelled_external_growth_prevents_new_plan=True,save_before_stop=str(second),
        incomplete_pair_rejected=True,old_complete_pair_readable=True,
        normal_checkpoint_interval=50,near_budget_interval=10,actual_root_costs_not_modelled_inputs=True)
    with (OUT/'B_FACILITY_RESULT.json').open('x') as f:json.dump(result,f,indent=2)
    print(json.dumps({k:result[k] for k in ('status','legacy_sizes','measured_pair_CPU','save_reserve_CPU','incomplete_pair_rejected')}))
