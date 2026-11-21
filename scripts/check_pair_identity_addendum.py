"""Same facility fixture: reject a mismatched private observation cursor."""
import json,copy
from action_difference_revision_budget import OUT
from raven_mcs_execution.paired_checkpoint import PairedCheckpointStore
if __name__=='__main__':
    root=OUT/'facility_pairs_rename';marker=root/'02_before_stop.complete.json'
    record=json.loads(marker.read_text());store=PairedCheckpointStore(root)
    model,private=store.read(marker,expected_identity=record['identity'])
    bad=copy.deepcopy(private);bad['tick']+=1
    try:store.validate_pair_content(model,bad,record['identity'],record['model_hash'])
    except ValueError:pass
    else:raise AssertionError('same namespace with inconsistent tick must not be accepted')
    (OUT/'B_PAIR_IDENTITY_PASS.json').write_text(json.dumps(dict(status='PASS',new_saves=0,new_measurements=0,
        valid_old_commit_readable=True,mixed_tick_rejected=True,training=0)))
    print('paired checkpoint cursor / endpoint identity PASS')
