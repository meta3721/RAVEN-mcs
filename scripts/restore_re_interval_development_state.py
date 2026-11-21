"""Restore a same-run prefix bundle without training, replay or resetting cost."""
import copy,json
from pathlib import Path
from types import SimpleNamespace
import numpy as np
import pandas as pd
import torch
from raven_mcs_re_interval.schema import ControlConfig
from raven_mcs_re_interval.session import DevelopmentSession
from raven_mcs_re_interval.training_backend import DevelopmentBackend
from raven_mcs_re_interval.development_acquisition import DevelopmentProducer
from raven_mcs_re_interval.persistence import restore_checkpoint,source_identity
from raven_mcs_re_interval.lifecycle import DynamicWindowRunner
from raven_mcs_re_interval.isolation import IsolatedController
from raven_mcs.experiments.calibration_first import load_inputs
from raven_mcs.training.window_runner import FullWindowRunner
from raven_mcs.aggregation.method_policy import get_method_policy
from raven_mcs.aggregation.methods import RavenAggregator
from raven_mcs.models.common_ndmf import deterministic_common_ndmf
from raven_mcs.simulation.event_trace import EventTrace,EventTraceMetadata
from raven_mcs.utils.hashing import sha256_file

def restore_bundle(root,out,checkpoint,producer_checkpoint,*,engineering_patch=None):
    """Return session/producer/tick for explicitly authorized continuation only.

    No entry loop or automatic resumption. Caller must retain the same batch
    root ledger and wall deadline. Censoring in historical prefixes is retained.
    """
    root=Path(root);out=Path(out);checkpoint=Path(checkpoint)
    payload=json.loads(Path(producer_checkpoint).read_text());packet=json.loads(checkpoint.read_text());raw=packet['state']
    if payload['checkpoint_hash']!=sha256_file(checkpoint) or raw['seed']!=44001:
        raise ValueError('same-run checkpoint pair mismatch')
    config=ControlConfig.from_dict(raw['config']);i=load_inputs(root,out)
    owner=FullWindowRunner(trace=EventTrace(pd.DataFrame(columns=['client_id']),EventTraceMetadata('traffic_RE_interval_development',44001,100,len(i.clients))),
        dataset=SimpleNamespace(),model=deterministic_common_ndmf(len(i.clients),seed=43001),aggregator=RavenAggregator(),
        policy=get_method_policy('raven_mcs'),mu=np.asarray(i.mu),num_groups=len(i.mu),local_steps=1,learning_rate=.01,
        seed=44001,design_configuration=config.design,pi_target=i.pi,pi_opp_joint=i.opp)
    if engineering_patch is None:r=restore_checkpoint(checkpoint,backend=DevelopmentBackend(owner))
    else:
        amendment=json.loads(Path(engineering_patch).read_text())
        current_sources=source_identity()
        if packet['sources']!=amendment['before_sources'] or current_sources!=amendment['after_sources']:
            raise ValueError('engineering source bridge mismatch')
        changed=[k for k in packet['sources'] if packet['sources'][k]!=current_sources[k]]
        if changed!=['src/raven_mcs_re_interval/predictor.py'] or not amendment['same_method_no_threshold_change']:
            raise ValueError('unapproved method/source change')
        if packet['method']!=config.method_version or packet['q_event']!='I(100)|H,R=1,E=1':raise ValueError('method / q event mismatch')
        r=DynamicWindowRunner.from_dict(raw,backend=DevelopmentBackend(owner))
    if r.clock_namespace!=payload['clock_namespace'] or r.experiment_end!=100.:raise ValueError('clock/endpoint mismatch')
    owner._dynamic_control_owner=True
    controller=IsolatedController();controller.accounting=copy.deepcopy(payload['controller']['accounting'])
    session=DevelopmentSession(owner,r,controller,out/'trajectory')
    producer=DevelopmentProducer(i,session);producer.restore(payload['state'])
    torch.set_rng_state(torch.tensor(payload['torch_rng'],dtype=torch.uint8))
    if r.backend.local_optimizer_steps!=sum(w['training_started'] for w in r.backend.work.values()):
        raise ValueError('restored cumulative SGD mismatch')
    return session,producer,payload['tick']
