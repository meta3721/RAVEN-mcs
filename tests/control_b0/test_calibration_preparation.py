from dataclasses import asdict,replace
import copy
import numpy as np
import pytest
from raven_mcs.control.schema import InputError,DependencyPending,P2Settings,Registration
from raven_mcs.control.probability import DiagnosticPriorQ,RegistrationFeatures,policy_context_hash,AttemptRecord
from raven_mcs.control.calibration_identity import ClockNamespace,applicability,endpoint,service_parameters_hash
from raven_mcs.control.predictor import FrozenServiceModel
from raven_mcs.control.lifecycle import DynamicWindowRunner
from raven_mcs.training.dynamic_control import CalibrationAuthorization
from raven_mcs.experiments.conditional_bundle import prepare_conditional_bundle
from raven_mcs.control.planner import plan
from test_persistence_and_full_connection import full_owner
from conftest import summary

def context():
    return applicability(learning=dict(model='CommonNDMF',optimizer='existing_hajek_sgd',local_steps=1,learning_rate=.01,
        initial_model_hash='fixture_hash',scaler={'train':True},feature_schema='spatial/hour/weekday/trend'),
        service={'full_parameters':[.7,.9,.98]},experiment_end=100.,data_identity='data',target_identity='target',stage1={'lagged':True})

def session(config):
    owner=full_owner(config);owner.seed=43001
    scope=context();namespace=asdict(ClockNamespace('unit_fixture_not_acquisition','2026-10-13T00:00:00Z'))
    prior=DiagnosticPriorQ(policy_context_hash(config,P2Settings(),owner.mu,'service_fixture',scope))
    model=FrozenServiceModel('service_fixture',0.,(),(),prior.to_dict())
    return prepare_conditional_bundle(owner,config=config,predictor=model,q_model=prior,seed=43001,experiment_end=100.,open_time=0.,
        data_identity='a'*64,target_identity='b'*64,stage1_as_of=0.,calibration_only=True,probability_applicability=scope,clock_namespace=namespace)

def test_prior_is_not_calibrated_and_production_rejects(config):
    s=session(config);q=s.runner.q_model.predict_at_registration(RegistrationFeatures(0,'d','n',4.,0,0,s.runner.q_model.configuration_hash,0.))
    assert q.role=='diagnostic_prior' and q.value==.5
    with pytest.raises(DependencyPending):q.require(isolated_test=True)
    assert q.require(isolated_test=False,calibration_only=True)==.5
    with pytest.raises(InputError,match='prohibited'):
        s.owner._dynamic_control_owner=False
        s.owner.build_dynamic_control(config=config,predictor=s.runner.predictor,q_model=s.runner.q_model,seed=43001,
            experiment_end=100.,open_time=0.,data_identity='a'*64,target_identity='b'*64)

def test_endpoint_prefix_and_physical_censor_are_distinct(config):
    s=session(config);r=s.runner
    r.on_register(Registration('pending','c',0.,0,'d','n'),summary(config,0.))
    r.advance_time(3.);r.finish_observation()
    assert r.attempts['pending'].consumed is None and r.attempts['pending'].right_censored_at==3.
    with pytest.raises(InputError):r.finish_finite_endpoint()
    r.advance_time(100.);r.finish_finite_endpoint()
    rec=r.attempts['pending']
    assert rec.consumed==0 and rec.terminal_reason=='horizon_unconsumed' and rec.physical_outcome=='pending'
    with pytest.raises(InputError):endpoint(3.)

def test_probability_identity_covers_learning_service_endpoint(config):
    c=context();h=policy_context_hash(config,P2Settings(),[.5,.5],'s',c)
    for field,subkey in [('learning','learning_rate'),('service','full_parameters'),('endpoint','T')]:
        other=copy.deepcopy(c);other[field][subkey]='changed'
        assert h!=policy_context_hash(config,P2Settings(),[.5,.5],'s',other)
    a=ClockNamespace('a','UTC_a');b=ClockNamespace('b','UTC_b')
    with pytest.raises(InputError):a.require_same_run(b)
    a.require_same_run(a)

def test_full_runner_calibration_admission_and_restoration_no_sgd(config,monkeypatch):
    s=session(config);r=s.runner;reg=Registration('first','c',0.,0,'d','n')
    r.on_register(reg,summary(config,0.))
    assert plan(r.snapshot(),r.predictor).reason=='common_warmup'
    actual=[]
    def supplied(*,model_state,observed_records,a_bar_weights,local_steps):
        actual.append(a_bar_weights.copy())
        from raven_mcs.training.client import _flatten_params
        return np.zeros_like(_flatten_params(model_state)),0.
    monkeypatch.setattr(s.owner._trainer,'train_step',supplied)
    r.start_local_training('first',[{}]*4,authorization=CalibrationAuthorization('unit_path_no_actual_sgd'))
    np.testing.assert_allclose(actual[0],[.1,.2,.3,.4])
    assert r.backend.local_optimizer_steps==1
    r.backend.local_optimizer_steps=5000
    with pytest.raises(DependencyPending,match='BUDGET'):r.start_local_training('first',[{}]*4,authorization=CalibrationAuthorization('fixture'))
    packet=r.to_dict();other=session(config)
    restored=DynamicWindowRunner.from_dict(packet,backend=other.runner.backend)
    assert restored.to_dict()==r.to_dict()
    assert restored.calibration_only and restored.snapshot().clock_namespace==r.clock_namespace
    assert restored.registration_features(reg).service_parameters_hash==service_parameters_hash(r.predictor)
