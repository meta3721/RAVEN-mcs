"""Same facility case's admission addendum; reuse its single save measurement."""
import json
from action_difference_revision_budget import OUT
from raven_mcs_execution.budget import RootBudgetPublisher,RootBudgetReader,checkpoint_due
from raven_mcs_execution.paired_checkpoint import PairedCheckpointStore
if __name__=='__main__':
    measured=json.loads((OUT/'B_FACILITY_RESULT.json').read_text());r=measured['save_reserve_CPU']
    publisher=RootBudgetPublisher(dict(path=str(OUT/'MODELLED_ROOT_BOUND.json'),prior_batch=0.,prior_phase=0.,batch_limit=r+10,
        phase_limit=r+10),r+10);publisher.publish(1.,.25,force=True)
    reader=RootBudgetReader(OUT/'MODELLED_ROOT_BOUND.json');assert reader.can_plan(r,operation_root_ceiling=4.)
    publisher.publish(1.,8.6,force=True);assert not reader.can_plan(r,operation_root_ceiling=4.);reader.require_save(r)
    assert checkpoint_due(811,800,remaining=reader.read()['effective_remaining'],save_reserve=r,operation_root_ceiling=4.)
    try:reader.can_plan(r)
    except TypeError:pass
    else:raise AssertionError('controller 2-CPU limit must not silently stand for the full root cost')
    record=json.loads((OUT/'facility_pairs_rename/02_before_stop.complete.json').read_text())
    store=PairedCheckpointStore(OUT/'facility_pairs_rename');store.read(OUT/'facility_pairs_rename/02_before_stop.complete.json',expected_identity=record['identity'])
    (OUT/'B_ADMISSION_CONTRACT_PASS.json').write_text(json.dumps(dict(status='PASS',new_save_measurements=0,
        controller_CPU_limit_unchanged=2,full_root_operation_bound_required=True,fixture_root_operation_bound=4.,
        missing_root_bound_rejected=True,prior_complete_pair_still_valid=True)))
    print('root admission contract PASS; original paired-save measurement reused')
