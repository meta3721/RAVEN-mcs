from dataclasses import asdict, replace
import copy
import numpy as np
import pytest

from raven_mcs.control.schema import DependencyPending, InputError, Registration
from raven_mcs.control.preview import preview_release
from raven_mcs.control.planner import plan
from raven_mcs.control.lifecycle import ArrayBackend
from raven_mcs.control.predictor import FrozenServiceModel
from conftest import runner,register,deliver,summary,emit


def test_corrected_preview_application_and_stale_rejection(populated):
    r=populated;before=copy.deepcopy(r.to_dict());p=r.preview_release()
    assert r.to_dict()==before
    assert p.solver['normalized_weight_residual']<=1e-7
    assert np.isfinite(p.solver['objective_actual_weights'])
    assert abs(p.solver['objective_actual_weights']-p.solver['objective_solver_candidate'])<1e-10
    assert p.reachability.secondary_value is not None
    assert p.reachability.lower_bound<=p.reachability.d+1e-7
    assert abs(p.reachability.d-p.ell)>1e-5 # full P2 is not pure target projection
    masses=np.array([m.summary.total for m in r.snapshot().pool])
    q=np.array([m.q.value for m in r.snapshot().pool])
    expected=masses*np.minimum(10.,1/np.maximum(q,.05));expected/=expected.sum()
    np.testing.assert_allclose(p.beta,expected,atol=1e-12)
    np.testing.assert_allclose(p.M,np.array([m.summary.composition for m in r.snapshot().pool]).T)
    old=r.backend.theta.copy()
    expected_theta=old-r.settings.server_eta*sum(a*r.backend.updates[k] for k,a in zip(p.keys,p.alpha))
    record=r.apply_release(p)
    np.testing.assert_allclose(r.backend.theta,expected_theta,rtol=0,atol=1e-14)
    assert r.model_version==1 and len(r.consumed)==4 and not r.pool
    assert all(r.attempts[k].mature_label==1 for k in p.keys)
    assert r.last_release.ell==p.ell and r.backend.local_optimizer_steps==0
    with pytest.raises(InputError,match='STALE'):r.apply_release(p)
    emit('preview_application',dict(preview=p.to_dict(),theta_before=old.tolist(),
        theta_after=r.backend.theta.tolist(),record=record,local_optimizer_steps=0))


def test_missing_q_not_silently_replaced(config):
    r=runner(config,pending=True);register(r,'pending','c',20.);deliver(r,'pending',20.2)
    assert r.attempts['pending'].q.value is None
    with pytest.raises(DependencyPending,match='CALIBRATION'):r.preview_release()
    with pytest.raises(DependencyPending):plan(r.snapshot(),r.predictor)
    assert r.model_version==0 and r.attempts['pending'].mature_label is None


def test_replacement_out_of_order_and_physical_outcome(config):
    r=runner(config);register(r,'old','c',20.);register(r,'new','c',20.1)
    deliver(r,'old',20.2);deliver(r,'new',20.3)
    assert r.pool['c'].key=='new' and r.attempts['old'].terminal_reason=='superseded'
    assert r.attempts['old'].physical_outcome=='completion' and r.attempts['old'].accepted_at==20.2
    register(r,'later','c',20.4);register(r,'latest','c',20.5)
    deliver(r,'latest',20.6);deliver(r,'later',20.7)
    assert r.pool['c'].key=='latest' and r.attempts['later'].accepted_at is None
    with pytest.raises(InputError,match='duplicate'):deliver(r,'latest',20.8)


def test_inflight_expiry_empty_close_and_mature_labels(config):
    r=runner(config)
    register(r,'pending','late',20.)
    # Six actual deterministic server updates, not local training or replay.
    for i in range(6):
        time=20.+.2*i
        register(r,f'usable{i}',f'c{i}',time,download=r.model_version)
        deliver(r,f'usable{i}',time+.1)
        r.apply_release(r.preview_release())
    assert r.attempts['pending'].terminal_reason=='expired'
    assert 'pending' not in r.in_flight
    version=r.model_version;last=r.last_release;debt=r.debt
    r.advance_time(23.);r.apply_release(r.preview_release())
    assert r.model_version==version and r.last_release==last and r.debt==debt
    assert r.closures[-1]['empty']
    deliver(r,'pending',23.1)
    assert not r.pool and r.attempts['pending'].mature_label==0
    register(r,'unfinished','u',23.2,download=r.model_version)
    r.advance_time(24.);r.finish_observation()
    assert r.attempts['unfinished'].mature_label is None and r.attempts['unfinished'].right_censored_at==24.
    r.apply_release(r.preview_release())
    assert r.attempts['unfinished'].mature_label is None


def test_future_checkpoint_invalid_tensor_and_stale_snapshot(populated):
    r=populated;p=r.preview_release();r.advance_time(21.1)
    with pytest.raises(InputError,match='STALE'):r.apply_release(p)
    with pytest.raises(InputError,match='checkpoint'):
        register(r,'future','future',21.1,download=1)
    register(r,'bad','bad',21.1)
    with pytest.raises(InputError,match='malformed'):deliver(r,'bad',21.2,[float('nan')]*3)
    assert r.attempts['bad'].physical_outcome=='pending'


def test_design_freeze_and_gate_has_no_computation_effect(populated):
    r=populated;other=type(r).from_dict(r.to_dict(),backend=ArrayBackend([0.,0.,0.]))
    for target,gate,state in ((r,0,'WARMUP'),(other,1,'RESET')):target.diagnostic(gate=gate,state=state)
    assert r.snapshot()==other.snapshot()
    a,b=r.preview_release(),other.preview_release()
    np.testing.assert_allclose(a.alpha,b.alpha,atol=1e-14)
    for m in r.pool.values():
        assert m.summary.design_enabled and not np.allclose(m.summary.ratio,1)
    payload=r.config.to_dict();payload['design']['enabled']=False
    assert r.config.design.enabled
    with pytest.raises(AttributeError):r.config=replace(r.config,design=replace(r.config.design,enabled=False))
    with pytest.raises(TypeError):r.predictor.q_model['weights']=(1.,)*5
    with pytest.raises(InputError,match='next window'):r.freeze_next_estimators(predictor=r.predictor,q_model=r.q_model)
    r.apply_release(a);other.apply_release(b)
    np.testing.assert_array_equal(r.backend.theta,other.backend.theta)


def test_probability_frozen_per_attempt_and_failure_censoring(config):
    r=runner(config);reg=register(r,'one','c',20.)
    q=r.attempts['one'].q
    r.advance_time(20.2);r.apply_release(r.preview_release())
    assert r.attempts['one'].q==q and r.attempts['one'].mature_label is None
    r.on_failure('one',20.4,reason='network_failure')
    assert r.attempts['one'].mature_label==0 and len(r.mature_rows())==1
    register(r,'two','d',20.4);r.finish_observation()
    assert r.attempts['two'].mature_label is None
    assert 'actual_close' not in asdict(r.attempts['two'].features)
    assert r.attempts['two'].features.maximum_deadline_slack==pytest.approx(3.8)
