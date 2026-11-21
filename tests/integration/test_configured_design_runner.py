"""Behavior checks of the real loss/reconstruction/solver/update chain, not performance experiments."""
from pathlib import Path
from unittest.mock import patch
import copy
import json
import numpy as np
import pandas as pd
import pytest
import torch

from raven_mcs.aggregation.method_policy import get_method_policy
from raven_mcs.aggregation.methods import RavenAggregator
from raven_mcs.e3.real_runner.fixture import build_correctness_fixture, load_fixture_dataset
from raven_mcs.models.common_ndmf import deterministic_common_ndmf
from raven_mcs.simulation.event_trace import EventTrace, EventTraceMetadata
from raven_mcs.sag.r1l_design import DesignConfiguration
from raven_mcs.training.window_runner import FullWindowRunner
from raven_mcs.sag.certificates import compute_certificates


class ObservedRaven(RavenAggregator):
    def __init__(self):
        super().__init__()
        self.payloads = []

    def compute_server_weights(self, payload):
        self.payloads.append(copy.deepcopy(payload))
        return super().compute_server_weights(payload)


@pytest.fixture(scope="module")
def context(tmp_path_factory):
    torch.set_num_threads(1)
    fx = build_correctness_fixture(tmp_path_factory.mktemp('design_data'))
    ds = load_fixture_dataset(Path(fx['data_dir']))
    rows, tar = [], {}
    masses = [[.04,.08,.16,.32],[.02,.06,.12,.20]]
    for win in range(2):
        for i, cid in enumerate(['client-000','client-001']):
            units = ds.atomic_df.loc[(ds.atomic_df.spatial_id==f'n{i}') & (ds.atomic_df.split=='train')].sort_values('time_index')
            ids = units.unit_id.tolist()
            for r, mass in zip(units.itertuples(), masses[i]):
                tar[(cid, r.opportunity_stratum)] = mass
            rows.append(dict(window_id=win,client_id=cid,risk_set_unit_ids=ids,
                opportunity_features={},observed_unit_ids=ids,O={u:1 for u in ids},
                registration_time=win,downloaded_version=win,model_age=0,tau=0,
                device_profile='test',network_profile='test',compute_success=True,compute_duration=.1,
                network_success=True,network_duration=.1,arrival_time=win+.2,U=1,raw_workload=4,
                oracle_p=.5,oracle_q=.5,hidden_confounder=0))
    trace=EventTrace(pd.DataFrame(rows),EventTraceMetadata('behavior_fixture',26001,2,2))
    trace.validate()
    return ds,trace,tar


def make_runner(context, design=True, legacy=False):
    ds,trace,tar=context
    runner=FullWindowRunner(trace=trace,dataset=ds,model=deterministic_common_ndmf(ds.num_spatial,seed=26001),
        aggregator=ObservedRaven(),policy=get_method_policy('raven_coverage_legacy' if legacy else 'raven_mcs'),
        mu=np.ones(ds.num_groups)/ds.num_groups,num_groups=ds.num_groups,pi_target=tar,
        pi_opp_joint={key:1/8 for key in tar},local_steps=1,
        design_configuration=None if legacy else DesignConfiguration(design,'paired_behavior_fixture'))
    runner.observed_trainer_inputs=[]
    real_train=runner._trainer.train_step
    def capture(**kw):
        runner.observed_trainer_inputs.append(np.asarray(kw['a_bar_weights']).copy())
        return real_train(**kw)
    runner._trainer.train_step=capture
    return runner


def diagnostic(gate, state='CERTIFIED'):
    # Only the diagnostic output is controlled; correction, training, rebuilding,
    # the complete Raven solver and model updates are the production code.
    def generate(*args,**kwargs):
        result=compute_certificates(*args,**kwargs)
        result.C_cov_LCB=.06 if gate else .04
        result.diagnostics.update(certificate_state=state,C_LCB=result.C_cov_LCB,tau_cov=.05)
        return result
    return generate


def execute(context, design, gate, state='CERTIFIED',legacy=False):
    runner=make_runner(context,design,legacy)
    with patch('raven_mcs.training.window_runner.compute_certificates',side_effect=diagnostic(gate,state)):
        metric=runner._process_window(0,runner.trace.events)
    return runner,metric


def test_four_combinations_and_gate_parity(context, tmp_path):
    evidence=[]
    for design in (True,False):
        paired=[]
        for gate in (0,1):
            r,m=execute(context,design,gate)
            payload=r.aggregator.payloads[0]
            expected_ratios=[np.array([.32,.64,1.28,2.56]),np.array([.16,.48,.96,1.60])]
            for i,(diag,actual_weights) in enumerate(zip(r.diagnostics,r.observed_trainer_inputs)):
                ratio=expected_ratios[i] if design else np.ones(4)
                np.testing.assert_allclose(diag['zeta_hat'],ratio,rtol=0,atol=1e-14)
                np.testing.assert_allclose(actual_weights,ratio/ratio.sum(),rtol=0,atol=1e-14)
                col=payload.compositions[:,i]
                observed=np.flatnonzero(col)
                np.testing.assert_allclose(col[observed],ratio/ratio.sum(),rtol=0,atol=1e-14)
            # The production observation predictor's cold-start probability is .2.
            assert all(np.allclose(d['p_hat'],.2) for d in r.diagnostics)
            np.testing.assert_allclose(payload.total_masses,[24.,16.] if design else [20.,20.],atol=1e-13)
            np.testing.assert_allclose(payload.beta_hat,[.6,.4] if design else [.5,.5],atol=1e-13)
            assert m.actual_design == int(design) and m.coverage_gate == gate
            assert r.sag_window_logs[0]['actual_design']==int(design)
            evidence.append(dict(design=int(design),gate=gate,ratios=[d['zeta_hat'] for d in r.diagnostics],
                trainer_weights=[x.tolist() for x in r.observed_trainer_inputs],total_masses=payload.total_masses.tolist(),
                beta=payload.beta_hat.tolist(),composition=payload.compositions.tolist(),
                alpha=m.alpha,theta_hash=m.theta_hash_after,method_version=m.method_version))
            paired.append((r,m))
        a,b=paired
        assert a[1].theta_hash_after==b[1].theta_hash_after
        assert a[1].alpha==b[1].alpha
        assert a[1].train_loss==b[1].train_loss
        np.testing.assert_array_equal(a[0].debt,b[0].debt)
        assert a[0].variance_count==b[0].variance_count
        for key in a[0].theta:
            assert torch.equal(a[0].theta[key],b[0].theta[key])
    assert evidence[0]['theta_hash'] != evidence[2]['theta_hash']
    # Optional durable evidence is explicitly requested by the validation entry.
    import os
    if os.environ.get('DESIGN_ALIGNMENT_EVIDENCE'):
        Path(os.environ['DESIGN_ALIGNMENT_EVIDENCE']).write_text(json.dumps(evidence,indent=2),encoding='utf-8')


@pytest.mark.parametrize('state',['WARMUP','RESET'])
def test_diagnostic_state_does_not_close_design(context,state):
    r,m=execute(context,True,1,state)
    assert m.actual_design==1 and m.coverage_gate==0
    assert not np.allclose(r.diagnostics[0]['zeta_hat'],1)


def test_configuration_frozen_before_diagnostic_and_changes_next_window(context):
    r=make_runner(context)
    original=diagnostic(0)
    def change_during_window(*args,**kwargs):
        r.design_configuration=DesignConfiguration(False,'explicit_next_window')
        return original(*args,**kwargs)
    with patch('raven_mcs.training.window_runner.compute_certificates',side_effect=change_during_window):
        first=r._process_window(0,r.trace.events)
    with patch('raven_mcs.training.window_runner.compute_certificates',side_effect=diagnostic(1)):
        second=r._process_window(1,r.trace.events)
    assert first.actual_design==1 and second.actual_design==0
    assert first.configuration_source=='paired_behavior_fixture'
    assert second.configuration_source=='explicit_next_window'
    assert not np.allclose(r.diagnostics[0]['zeta_hat'],1)
    assert all(np.allclose(d['zeta_hat'],1) for d in r.diagnostics if d['window_id']==1)


@pytest.mark.parametrize('design',[True,False])
def test_fixed_running_configuration_gate_only_changes_diagnostics(context,design):
    a,b=make_runner(context,design),make_runner(context,design)
    # CommonNDMF local training consumes torch RNG (dropout); pair the same
    # starting RNG for each real window, as required by the comparison.
    import random
    for window in range(2):
        states=torch.get_rng_state(),np.random.get_state(),random.getstate()
        with patch('raven_mcs.training.window_runner.compute_certificates',side_effect=diagnostic(window)):
            ma=a._process_window(window,a.trace.events)
        torch.set_rng_state(states[0]);np.random.set_state(states[1]);random.setstate(states[2])
        with patch('raven_mcs.training.window_runner.compute_certificates',side_effect=diagnostic(1-window)):
            mb=b._process_window(window,b.trace.events)
        assert ma.actual_design==mb.actual_design==int(design)
        assert ma.theta_hash_after==mb.theta_hash_after and ma.alpha==mb.alpha
        np.testing.assert_array_equal(a.aggregator.payloads[-1].beta_hat,b.aggregator.payloads[-1].beta_hat)
        np.testing.assert_array_equal(a.aggregator.payloads[-1].compositions,b.aggregator.payloads[-1].compositions)
        np.testing.assert_array_equal(a.debt,b.debt)


@pytest.mark.parametrize('gate',[0,1])
def test_legacy_full_runner_still_uses_gate(context,gate):
    r,m=execute(context,True,gate,legacy=True)
    assert m.actual_design==gate and m.coverage_gate==gate
    assert np.allclose(r.diagnostics[0]['zeta_hat'],1)==(gate==0)
    assert m.method_version=='coverage-controlled-v1'


@pytest.mark.parametrize('bad',[None,float('nan'),-1.])
def test_missing_invalid_design_inputs_are_errors_even_when_gate_off(context,bad):
    r=make_runner(context)
    r.pi_target={} if bad is None else {key:bad for key in r.pi_target}
    with patch('raven_mcs.training.window_runner.compute_certificates',side_effect=diagnostic(0)):
        with pytest.raises((ValueError,RuntimeError),match='target|DESIGN_INPUT|nonnegative'):
            r._process_window(0,r.trace.events)


def test_real_window_uses_lagged_opportunity_before_history_update(context):
    r=make_runner(context)
    r.pi_opp_joint=None
    initial=r.opportunity_estimator.pi_hat().to_dict()
    calls=[]
    compute=r._compute_zeta
    update=r._update_lagged_estimators
    def record_compute(*args,**kw):
        assert r.opportunity_estimator.pi_hat().to_dict()==initial
        calls.append('compute')
        return compute(*args,**kw)
    def record_update(*args,**kw):
        assert calls and set(calls)=={'compute'}
        calls.append('update')
        return update(*args,**kw)
    r._compute_zeta=record_compute
    r._update_lagged_estimators=record_update
    with patch('raven_mcs.training.window_runner.compute_certificates',side_effect=diagnostic(0)):
        r._process_window(0,r.trace.events)
    assert calls[-1]=='update' and calls.count('update')==1
    np.testing.assert_allclose(r.diagnostics[0]['zeta_hat'],[.32,.64,1.28,2.56])


def test_experiment_cli_full_runner_serializes_configured_identity(context,tmp_path):
    import importlib.util
    root=Path(__file__).resolve().parents[2]
    spec=importlib.util.spec_from_file_location('alignment_cli',root/'scripts/run_experiment.py')
    cli=importlib.util.module_from_spec(spec);spec.loader.exec_module(cli)
    ds,trace,tar=context
    build=cli.build_full_runner
    def frozen_fixture_builder(**kw):
        return build(**kw,target_mu=np.ones(ds.num_groups)/ds.num_groups,pi_target=tar,pi_opp_joint={k:1/8 for k in tar})
    args=['--experiment','E2_misalignment','--dataset','behavior_fixture','--method','raven_mcs',
          '--design','on','--design-source','explicit_cli_test','--num-windows','2',
          '--local-steps','1','--scenario','balanced','--seed','26001','--output-dir',str(tmp_path)]
    with patch.object(cli,'_get_or_generate_trace',return_value=(trace,'fixture_trace')), patch.object(cli,'ProcessedDataset',return_value=ds), patch.object(cli,'build_full_runner',side_effect=frozen_fixture_builder):
        assert cli.main(args)==0
    result=json.loads((tmp_path/'E2_misalignment_summary.json').read_text(encoding='utf-8'))['results'][0]
    assert result['method_version']=='configured-design-v1'
    assert result['design_configuration']['enabled'] is True
    assert len(result['design_window_logs'])==2
    assert all(r['configured_design']==r['Design_t']==1 for r in result['design_window_logs'])
    assert all(r['configuration_source']=='explicit_cli_test' for r in result['design_window_logs'])
    with pytest.raises(FileExistsError,match='preserved'):
        cli.main(args)


def test_configured_diagnostic_identity_cannot_be_overridden_by_legacy_attribute(context):
    configured=make_runner(context)
    configured.sag_cov_mode='event_count_cp'
    assert configured.policy.coverage_diagnostic=='aggregate_coverage'
    assert configured._certificate_context().cov_mode=='aggregate_stable_regime'
    legacy=make_runner(context,legacy=True)
    legacy.sag_cov_mode='event_count_cp'
    assert legacy._certificate_context().cov_mode=='event_count_cp'
