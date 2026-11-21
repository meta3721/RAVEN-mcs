from dataclasses import replace, asdict
import copy
import json
from pathlib import Path
from types import SimpleNamespace
import numpy as np
import pytest
import torch
import pandas as pd

from raven_mcs.control.schema import InputError, DependencyPending
from raven_mcs.control.persistence import initialize_control_run,save_checkpoint,restore_checkpoint
from raven_mcs.control.lifecycle import ArrayBackend,DynamicWindowRunner
from raven_mcs.control.planner import plan
from raven_mcs.control.isolation import IsolatedController
from raven_mcs.training.dynamic_control import connect_full_runner
from raven_mcs.training.window_runner import FullWindowRunner
from raven_mcs.training.client import ClientTrainer,_flatten_params
from raven_mcs.training.window_timing import WindowClock
from raven_mcs.aggregation.method_policy import get_method_policy
from raven_mcs.aggregation.methods import RavenAggregator
from raven_mcs.models.common_ndmf import deterministic_common_ndmf
from raven_mcs.simulation.event_trace import EventTrace,EventTraceMetadata
from raven_mcs.correction.stage1 import reconstruct_stage1
from raven_mcs.correction.hajek import raw_weights,group_mass,total_mass,composition,normalized_weights
from raven_mcs.correction.effective_sample_size import effective_sample_size
from conftest import runner,register,deliver,model,q_model,emit

ROOT=Path(__file__).resolve().parents[2]


def test_production_save_restore_same_suffix_and_no_overwrite(populated,tmp_path):
    r=populated;register(r,'inflight','fifth',21.)
    out=tmp_path/'dynamic_new_run'
    manifest=initialize_control_run(r,out,repo_root=ROOT)
    assert manifest.validate()==[] and manifest.git_state_scope=='explicit_computational_source_closure'
    controller=IsolatedController();controller.accounting.append(dict(previous_decision_cpu=0.))
    checkpoint=save_checkpoint(r,out,name='checkpoint_0.json',controller=controller)
    restored,saved_controller=restore_checkpoint(checkpoint,backend=ArrayBackend([0.,0.,0.]),repo_root=ROOT,
        expected_config=r.config,expected_data_identity=r.data_identity,expected_target_identity=r.target_identity)
    assert saved_controller==controller.to_dict()
    assert restored.to_dict()==r.to_dict()
    for target in (r,restored):
        deliver(target,'inflight',21.1)
        target.advance_time(22.)
    a,b=plan(r.snapshot(),r.predictor),plan(restored.snapshot(),restored.predictor)
    assert a==b
    for target in (r,restored):target.apply_release(target.preview_release())
    assert restored.to_dict()==r.to_dict()
    with pytest.raises(FileExistsError):save_checkpoint(r,out,name='checkpoint_0.json')
    with pytest.raises(InputError,match='overwrite'):initialize_control_run(r,out,repo_root=ROOT)
    with pytest.raises(InputError,match='config'):
        restore_checkpoint(checkpoint,backend=ArrayBackend([0.,0.,0.]),repo_root=ROOT,
            expected_config=replace(r.config,design=replace(r.config.design,enabled=False)))
    emit('production_persistence',dict(manifest=manifest.to_dict(),identical_suffix=True,
        restored_pool_keys=[m.key for m in restored.snapshot().pool],
        restored_model_version=restored.model_version,actions=[asdict(a),asdict(b)],training_steps=0))


def full_owner(config):
    torch.set_num_threads(1)
    # Empty event inventory initializes infrastructure only; no event replay.
    return FullWindowRunner(trace=EventTrace(pd.DataFrame(columns=['client_id']),
        EventTraceMetadata('B0_no_trajectory',26004,2,100)),dataset=SimpleNamespace(),
        model=deterministic_common_ndmf(2,seed=26004),aggregator=RavenAggregator(),
        policy=get_method_policy('raven_mcs'),mu=np.array([.5,.5]),num_groups=2,local_steps=1,
        design_configuration=config.design)


def test_real_model_and_existing_trainer_connected_but_no_sgd(config,monkeypatch,tmp_path):
    owner=full_owner(config)
    def forbidden_training(*args,**kwargs):raise AssertionError('SGD executed in B0')
    monkeypatch.setattr(owner._trainer,'train_step',forbidden_training)
    dynamic=owner.build_dynamic_control(config=config,predictor=model(config),q_model=q_model(config),
        seed=26004,experiment_end=40.,open_time=20.,data_identity=runner(config).data_identity,
        target_identity=runner(config).target_identity,isolated_test=True)
    old=_flatten_params(owner.theta).copy()
    for i in range(4):register(dynamic,f'full{i}',f'c{i}',20.,i%2)
    for i in range(4):deliver(dynamic,f'full{i}',20.2,np.full_like(old,.1*(i+1)))
    with pytest.raises(DependencyPending):dynamic.start_local_training('full0',[],authorization=None)
    with pytest.raises(RuntimeError,match='owns'):owner.run()
    preview=dynamic.preview_release()
    expected=old-.01*sum(a*np.full_like(old,.1*(i+1)) for i,a in enumerate(preview.alpha))
    dynamic.apply_release(preview)
    np.testing.assert_allclose(_flatten_params(owner.theta),expected,rtol=0,atol=1e-7)
    assert owner.clock.model_version==dynamic.model_version==1
    assert set(owner.variance_count.values())=={1}
    np.testing.assert_allclose(owner.debt,dynamic.debt)
    assert owner.model_versions[1] and dynamic.backend.local_optimizer_steps==0
    # Save/restore also uses the production backend's tensors/variance/checkpoints.
    packet=dynamic.to_dict();second_owner=full_owner(config)
    second=second_owner.build_dynamic_control(config=config,predictor=model(config),q_model=q_model(config),
        seed=26004,experiment_end=40.,open_time=20.,data_identity=dynamic.data_identity,
        target_identity=dynamic.target_identity,isolated_test=True)
    restored=DynamicWindowRunner.from_dict(packet,backend=second.backend)
    assert restored.to_dict()==dynamic.to_dict()
    emit('full_model_connection',dict(model=type(owner.model).__name__,backend=dynamic.backend.kind,
        configured_method=owner.policy.method_version,preview=preview.to_dict(),
        model_version=dynamic.model_version,actual_local_training_steps=0,update_tensor_origin='hand_authored'))


def test_shared_stage1_exact_existing_formulas_and_legal_clipping():
    zeta=np.array([.2,.4,1.2,1.6]);p=np.array([.1,.2,.5,1.]);o=np.array([1,0,1,1]);groups=np.array([0,1,0,1])
    actual=reconstruct_stage1(zeta,p,o,groups,num_groups=2)
    a=raw_weights(zeta,p);m=group_mass(o,a,groups,n_groups=2);total=total_mass(m)
    np.testing.assert_array_equal(actual.raw,a);np.testing.assert_array_equal(actual.groups,m)
    np.testing.assert_array_equal(actual.weights,normalized_weights(o,a,total))
    np.testing.assert_array_equal(actual.composition,composition(m,total))
    assert actual.effective_n==effective_sample_size(o,a,total_mass=total)
    clipped=reconstruct_stage1(zeta,np.zeros(4),o,groups,num_groups=2)
    np.testing.assert_array_equal(clipped.raw,raw_weights(zeta,np.zeros(4)))


def test_invalid_numeric_inputs_not_prediction_fallback(config):
    from raven_mcs.control.stage1 import freeze_stage1
    with pytest.raises(InputError,match='design'):
        freeze_stage1(config=config,target_opportunity=[1.],lagged_opportunity=[float('nan')],p_obs=[.5],
            observation=[1],group_ids=[0],num_groups=2,now=20.,estimator_as_of=19.,
            estimator_version='v',provenance='fixture')
    with pytest.raises(InputError,match='future estimator'):
        freeze_stage1(config=config,target_opportunity=[1.],lagged_opportunity=[1.],p_obs=[.5],
            observation=[1],group_ids=[0],num_groups=2,now=20.,estimator_as_of=21.,
            estimator_version='v',provenance='fixture')


def test_official_registration_uses_full_runner_lagged_inputs(config,monkeypatch):
    from raven_mcs.experiments.conditional_bundle import prepare_conditional_bundle
    from raven_mcs.control.schema import Registration
    owner=full_owner(config)
    owner.pi_target={('public_client',f's{i}'):p for i,p in enumerate([.05,.1,.15,.2])}
    owner.pi_opp_joint={key:.25 for key in owner.pi_target}
    monkeypatch.setattr(owner._trainer,'train_step',lambda *a,**k:pytest.fail('SGD in B0'))
    session=prepare_conditional_bundle(owner,config=config,predictor=model(config),q_model=q_model(config),
        seed=26004,experiment_end=40.,open_time=20.,data_identity=runner(config).data_identity,
        target_identity=runner(config).target_identity,isolated_test=True,stage1_as_of=19.)
    owner.pi_opp_joint={key:.5 for key in owner.pi_target}
    owner.obs_propensity.prior_rate=.4
    q=session.register_observations(Registration('official','public_client',20.,0,'public_device','public_network'),
        stratum_ids=[f's{i}' for i in range(4)],p_pre_features=[{'bias':1.}]*4,
        observation=[1,1,1,1],group_ids=[0,0,1,1],metadata_as_of=19.,provenance='B0_public_pre_registration')
    state=session.runner.private_stage1['official']
    np.testing.assert_allclose(state.ratio,[.2,.4,.6,.8],atol=1e-14)
    np.testing.assert_allclose(state.p_obs,[.2]*4)
    np.testing.assert_allclose(state.masses,[3.,7.])
    for key,value in owner.model.state_dict().items():
        np.testing.assert_array_equal(value,owner.theta[key])
    assert q.role=='isolated_test_input' and session.runner.backend.local_optimizer_steps==0
    restored_owner=full_owner(config)
    restored=restored_owner.build_dynamic_control(config=config,predictor=model(config),q_model=q_model(config),
        seed=26004,experiment_end=40.,open_time=20.,data_identity=session.runner.data_identity,
        target_identity=session.runner.target_identity,isolated_test=True)
    restored=DynamicWindowRunner.from_dict(session.runner.to_dict(),backend=restored.backend)
    assert restored.to_dict()==session.runner.to_dict()
    np.testing.assert_allclose(restored.backend.stage1_context()._compute_p_hat([{'bias':1.}]),[.2])
    session.runner.advance_time(20.1)
    with pytest.raises(InputError,match='before the next window'):
        session.freeze_stage1_for_next_window(as_of=20.)
    session.close()
    session.freeze_stage1_for_next_window(as_of=20.1)
    new=session.runner.backend.stage1_context()
    np.testing.assert_allclose(new._compute_p_hat([{'bias':1.}]),[.4])
    assert session.runner.private_stage1['official']==state
    emit('official_registration',dict(frozen_ratio=list(state.ratio),frozen_p=list(state.p_obs),
        masses=list(state.masses),window_mutation_ignored=True,restore_inputs_identical=True,
        next_window_p=.4,old_message_unchanged=True,training_steps=0))


def test_probability_rejects_other_target_policy_context(config):
    r=runner(config);r.mu=(.7,.3)
    register(r,'foreign','c',20.)
    assert r.attempts['foreign'].q.value is None and r.attempts['foreign'].q.role=='dependency_pending'


def test_official_missing_p_is_input_error(config):
    from raven_mcs.experiments.conditional_bundle import prepare_conditional_bundle
    owner=full_owner(config);owner.obs_propensity=None
    with pytest.raises(InputError,match='missing observation'):
        prepare_conditional_bundle(owner,config=config,predictor=model(config),q_model=q_model(config),
            seed=26004,experiment_end=40.,open_time=20.,data_identity=runner(config).data_identity,
            target_identity=runner(config).target_identity,isolated_test=True,stage1_as_of=19.)


def test_official_disk_restore_same_registration_suffix(config,tmp_path):
    from raven_mcs.experiments.conditional_bundle import prepare_conditional_bundle,restore_conditional_bundle
    from raven_mcs.control.schema import Registration
    owner=full_owner(config)
    owner.pi_target={('c','s'):.5};owner.pi_opp_joint={('c','s'):.25}
    identities=runner(config)
    session=prepare_conditional_bundle(owner,config=config,predictor=model(config),q_model=q_model(config),
        seed=26004,experiment_end=40.,open_time=20.,data_identity=identities.data_identity,
        target_identity=identities.target_identity,isolated_test=True,stage1_as_of=19.,
        run_dir=tmp_path/'official',repo_root=ROOT)
    session.controller.accounting.append(dict(status='prior_fixture_record',total_cpu_seconds=0.))
    checkpoint=session.save('before_registration.json')
    restored=restore_conditional_bundle(full_owner(config),checkpoint,repo_root=ROOT,expected_config=config,
        expected_data_identity=identities.data_identity,expected_target_identity=identities.target_identity)
    reg=Registration('suffix','c',20.1,0,'public_device','public_network')
    for target in (session,restored):
        target.register_observations(reg,stratum_ids=['s'],p_pre_features=[{'bias':1.}],observation=[1],
            group_ids=[0],metadata_as_of=19.,provenance='lawful_fixture')
    assert session.runner.to_dict()==restored.runner.to_dict()
    assert session.controller.to_dict()==restored.controller.to_dict()
    with pytest.raises(RuntimeError,match='owns'):restored.owner.run()
    emit('official_disk_restore',dict(identical_registration_suffix=True,controller_restored=True,
         stage1_frozen_inputs_restored=True,training_steps=0,manifest_required=True))
