"""New-state persistence through the existing verified pair publisher."""
from pathlib import Path
from . import METHOD_VERSION
from .schema import InputError
from .lifecycle import DynamicWindowRunner
from raven_mcs.utils.hashing import sha256_json
from raven_mcs.utils.hashing import sha256_file

def source_closure():
    src=Path(__file__).resolve().parents[1]
    return {str(p.relative_to(src).as_posix()):sha256_file(p) for package in ('raven_mcs','raven_mcs_observed_feedback','raven_mcs_execution')
        for p in sorted((src/package).rglob('*.py'))}

def save_pair(runner,store,name,*,producer_state,budget,save_reserve):
    state=runner.checkpoint_state()
    packet=dict(schema='OF-v1-checkpoint',method=METHOD_VERSION,state=state,state_hash=sha256_json(state),source_closure=source_closure())
    identity=dict(method=METHOD_VERSION,seed=runner.seed,clock_namespace=runner.clock_namespace)
    private=dict(producer_state)
    if private.get('clock_namespace')!=runner.clock_namespace or private.get('T')!=100. or abs(private.get('tick',-1)*.1-runner.now)>1e-9:
        raise InputError('producer/current causal cursor mismatch')
    return store.publish(name,packet,private,identity,budget=budget,save_reserve=save_reserve)

def restore_pair(store,marker,*,identity,backend,expected_config=None,expected_data=None,expected_target=None):
    if identity.get('method')!=METHOD_VERSION:raise InputError('legacy checkpoint identity prohibited')
    packet,producer=store.read(marker,expected_identity=identity)
    if packet.get('schema')!='OF-v1-checkpoint' or packet.get('method')!=METHOD_VERSION or packet['state_hash']!=sha256_json(packet['state']):raise InputError('OF checkpoint content/version mismatch')
    if packet.get('source_closure')!=source_closure():raise InputError('checkpoint computational implementation changed')
    state=packet['state']
    if expected_config is not None and state['config']!=expected_config.to_dict():raise InputError('checkpoint configuration mismatch')
    for field,value in (('data_identity',expected_data),('target_identity',expected_target)):
        if value is not None and state[field]!=value:raise InputError('checkpoint data/target mismatch')
    return DynamicWindowRunner.from_dict(state,backend=backend),producer
