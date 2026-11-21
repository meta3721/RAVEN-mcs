"""Hand-authored B0 fixtures only. No data loading, local learning or trajectories."""
from dataclasses import replace
import json
import os
from pathlib import Path
import numpy as np
import pytest

from raven_mcs.control.schema import ControlConfig, P2Settings, Registration
from raven_mcs.sag.r1l_design import DesignConfiguration
from raven_mcs.control.stage1 import freeze_stage1
from raven_mcs.control.probability import EvidenceLogisticQ, PendingQModel,policy_context_hash
from raven_mcs.control.predictor import FrozenServiceModel, JointMark, RiskCell
from raven_mcs.control.lifecycle import ArrayBackend, DynamicWindowRunner
from raven_mcs.utils.hashing import sha256_json


def emit(name,obj):
    if os.environ.get('B0_EVIDENCE_DIR'):
        path=Path(os.environ['B0_EVIDENCE_DIR'])/(os.environ['B0_EVIDENCE_LABEL']+'-'+name+'.json')
        with path.open('x',encoding='utf-8') as f:json.dump(obj,f,ensure_ascii=False,indent=2,allow_nan=False)


@pytest.fixture
def config():return ControlConfig('B0_explicit_deterministic_fixture',DesignConfiguration(True,'B0_explicit_fixture'))


def summary(config,now,group=0,num_groups=2):
    return freeze_stage1(config=config,target_opportunity=[.05,.1,.15,.2],lagged_opportunity=[.25]*4,
        p_obs=[.5]*4,observation=[1]*4,group_ids=[group]*4,num_groups=num_groups,now=now,
        estimator_as_of=min(now,20.),estimator_version='B0_lagged_fixture',provenance='isolated_valid_inputs')


def q_model(config,pending=False,groups=2):
    if pending:return PendingQModel(as_of=20.)
    return EvidenceLogisticQ('B0_test_q_not_calibrated',20.,'isolated_test_fixture',
        (-.2,.1,-.02,.03,-.01),(('public_device','public_network'),),100,
        policy_context_hash(config,P2Settings(),[1/groups]*groups,'B0_frozen_history'),
        role='isolated_test_input')


def model(config,*,marks=(),cells=(),pending=False,groups=2):
    return FrozenServiceModel('B0_frozen_history',20.,tuple(cells),tuple(marks),q_model(config,pending,groups).to_dict(),
                              schedule_complete_until=100.)


def runner(config,*,groups=2,marks=(),cells=(),pending=False,backend=None):
    return DynamicWindowRunner(config=config,settings=P2Settings(),mu=[1/groups]*groups,
        predictor=model(config,marks=marks,cells=cells,pending=pending,groups=groups),q_model=q_model(config,pending,groups),
        backend=backend or ArrayBackend([1.,2.,3.]),seed=26004,experiment_end=40.,open_time=20.,
        isolated_test=True,data_identity=sha256_json('B0_hand_authored_data'),target_identity=sha256_json([1/groups]*groups))


def register(r,key,client,time=20.,group=0,download=0):
    reg=Registration(key,client,time,download,'public_device','public_network')
    r.on_register(reg,summary(r.config,time,group,len(r.mu)))
    return reg


def deliver(r,key,time,update=(.1,.2,.3)):
    r.on_completion(key,time,update=update)


@pytest.fixture
def populated(config):
    r=runner(config)
    for i in range(4):register(r,f'key{i}',f'client{i}',20.,i%2)
    for i in range(4):deliver(r,f'key{i}',20.2)
    r.advance_time(21.)
    return r
