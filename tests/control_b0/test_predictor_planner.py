from dataclasses import asdict, replace
import copy
import numpy as np
import pytest

from raven_mcs.control.schema import DecisionSnapshot, InputError, Registration, ReleaseSummary
from raven_mcs.control.predictor import (FrozenServiceModel, ServiceRecord, JointMark, RiskCell,
                                       ForecastEvent, UnsupportedPrediction, PublicOpportunity)
from raven_mcs.control.planner import plan,evaluate_plans
from raven_mcs.control.isolation import IsolatedController
from conftest import runner,register,deliver,summary,q_model,model,emit


def test_competing_risk_and_censoring_arithmetic(config):
    records=[]
    for i in range(5):
        reg=Registration(f'c{i}',f'c{i}',19.,0,'public_device','public_network')
        records.append(ServiceRecord(reg,19.2,'completion',summary(config,19.,i%2),0))
    for i in range(3):
        reg=Registration(f'f{i}',f'f{i}',19.,0,'public_device','public_network')
        records.append(ServiceRecord(reg,19.1,'notified_failure'))
    for i in range(2):
        reg=Registration(f'r{i}',f'r{i}',19.,0,'public_device','public_network')
        records.append(ServiceRecord(reg,19.1,'right_censored'))
    m=FrozenServiceModel.from_history(records,cutoff=20.,version='history',q_model=q_model(config),schedule_complete_until=40.)
    first,second=m.cells[:2]
    assert (first.risk,first.completions,first.failures)==(10,0,3)
    assert (second.risk,second.completions,second.failures)==(5,5,0)
    with pytest.raises(InputError,match='cutoff'):
        FrozenServiceModel.from_history([replace(records[0],observed_until=20.1)],cutoff=20.,version='x',q_model=q_model(config))
    emit('risk_table',m.to_dict())


def test_client_marks_not_reassigned_and_frozen_download(config):
    r=runner(config);register(r,'known','specific_client',20.1,download=0)
    r.advance_time(20.2)
    wrong=JointMark('other',('public_device','public_network'),summary(config,19.),19.2,0)
    cells=(RiskCell(('public_device','public_network'),2,5,5,0),)
    m=model(config,marks=[wrong],cells=cells)
    with pytest.raises(UnsupportedPrediction,match='COMPATIBLE_MARK'):m.sample_scenarios(r.snapshot())
    good=replace(wrong,client='specific_client')
    m=model(config,marks=[good],cells=cells)
    for scenario in m.sample_scenarios(r.snapshot()):
        assert len(scenario)==1
        assert scenario[0].registration.client=='specific_client' and scenario[0].registration.downloaded_version==0
        assert scenario[0].summary is good.summary


def test_joint_support_uses_multistep_path_and_no_real_mutation(config):
    r=runner(config,groups=3)
    for i in range(3):register(r,f'a{i}',f'a{i}',20.,group=0)
    for i in range(3):deliver(r,f'a{i}',20.2)
    rb=register(r,'b','b',20.3,group=1);rc=register(r,'c','c',20.3,group=2)
    r.advance_time(21.)
    scenario=(ForecastEvent(21.5,'completion',rb,summary(config,19.,1,3)),
              ForecastEvent(21.8,'completion',rc,summary(config,19.,2,3)))
    scenarios=(scenario,)*4;snapshot=r.snapshot();before=copy.deepcopy(r.to_dict())
    multi=evaluate_plans(snapshot,r.predictor,scenarios)
    single=evaluate_plans(snapshot,r.predictor,scenarios,offsets=(0.,.1),horizon=.1)
    assert single.action=='CLOSE' and multi.action=='WAIT'
    assert multi.selected_offset>=.5 and multi.p2_solves>0
    assert r.to_dict()==before and r.backend.local_optimizer_steps==0
    assert multi.scenario_digest==single.scenario_digest
    emit('joint_support',dict(multistep=asdict(multi),one_step=asdict(single),
         local_optimizer_steps=0,evidence_role='mechanism_fixture_not_performance'))


def test_snapshot_does_not_accept_future_or_hidden_fields(populated):
    r=populated;obj=asdict(r.snapshot())
    with pytest.raises(TypeError):DecisionSnapshot(**obj,future_payload='hidden')
    with pytest.raises(InputError,match='future message'):
        replace(r.snapshot(),pool=(replace(r.snapshot().pool[0],completed_at=22.),))
    future_event_table={'time':100,'payload':[1,0],'hidden_success':True}
    before=plan(r.snapshot(),r.predictor)
    future_event_table.update(payload=[0,1],hidden_success=False)
    after=plan(r.snapshot(),r.predictor)
    assert before==after
    assert not hasattr(r.snapshot(),'private_stage1') and not hasattr(r.snapshot(),'backend')


def test_unsupported_prediction_fallback_and_hard_deadline(populated):
    r=populated
    # Lack of client-compatible history affects prediction, not q validity.
    register(r,'pending','never_observed',21.)
    decision=plan(r.snapshot(),r.predictor)
    assert decision.action=='WAIT' and 'UNSUPPORTED_PREDICTION' in decision.reason
    r.advance_time(22.);assert plan(r.snapshot(),r.predictor).action=='CLOSE'
    r.advance_time(24.);assert plan(r.snapshot(),r.predictor).reason=='hard_deadline'


def test_isolated_normal_and_controlled_cpu_timeout(populated):
    r=populated;controller=IsolatedController()
    normal=controller.decide(r.snapshot(),r.predictor)
    assert normal.reason=='conditional_bundle' and normal.p2_solves>0
    r.advance_time(22.)
    timeout=controller.decide(r.snapshot(),r.predictor,test_fault='burn_cpu')
    assert timeout.action=='CLOSE' and timeout.reason=='CPU_TIMEOUT/fixed_time_2'
    assert controller.accounting[-1]['child_terminated']
    assert all(x['total_cpu_seconds']<=2 for x in controller.accounting)
    emit('isolation',dict(normal=asdict(normal),timeout=asdict(timeout),accounting=controller.accounting))


def test_public_future_registration_and_q_freeze(config):
    from raven_mcs.control.probability import EvidenceLogisticQ
    r=runner(config)
    register(r,'old','old_client',20.)
    old_q=r.attempts['old'].q
    r.advance_time(20.1)
    newer=replace(q_model(config),version='B0_second_fixture',weights=(-.7,.1,-.02,.03,-.01))
    with pytest.raises(InputError,match='before the next window'):
        r.freeze_next_estimators(predictor=replace(model(config),q_model=newer.to_dict()),q_model=newer)
    r.apply_release(r.preview_release())
    opportunity=PublicOpportunity('scheduled','public_client',20.2,'public_device','public_network',19.)
    mark=JointMark('public_client',('public_device','public_network'),summary(config,19.),19.5,0)
    predictor=replace(model(config),q_model=newer.to_dict(),opportunities=(opportunity,),marks=(mark,),
        cells=(RiskCell(('public_device','public_network'),1,5,5,0),))
    r.freeze_next_estimators(predictor=predictor,q_model=newer)
    assert r.attempts['old'].q==old_q
    register(r,'new','new_client',20.1)
    assert r.attempts['new'].q.model_version==newer.version
    # Only the scheduled client's future request has historical joint support.
    snapshot=replace(r.snapshot(),in_flight=tuple(x for x in r.snapshot().in_flight if x.registration.client=='old_client'))
    old_mark=replace(mark,client='old_client')
    predictor=replace(predictor,marks=(mark,old_mark),cells=(
        RiskCell(('public_device','public_network'),2,5,5,0),
        RiskCell(('public_device','public_network'),1,5,5,0)))
    scenarios=predictor.sample_scenarios(snapshot)
    assert len(scenarios)==4
    for scenario in scenarios:
        future=[x for x in scenario if x.registration.client=='public_client']
        assert [x.kind for x in future]==['register','completion']
        assert future[0].registration.downloaded_version==0  # sampled historical lag placeholder
    decision=evaluate_plans(snapshot,predictor,scenarios)
    assert decision.p2_solves>0
    emit('public_registration',dict(old_q=asdict(old_q),new_q=asdict(r.attempts['new'].q),
        scenarios=[[asdict(x) for x in s] for s in scenarios],decision=asdict(decision)))


def test_future_joint_mark_keeps_quality_and_registration_age_together(config):
    r=runner(config);r.advance_time(20.1)
    opportunity=PublicOpportunity('future','public_client',20.2,'public_device','public_network',19.)
    marks=tuple(JointMark('public_client',('public_device','public_network'),summary(config,19.,g),19.5,g)
                for g in (0,1))
    predictor=replace(model(config),opportunities=(opportunity,),marks=marks,
        cells=(RiskCell(('public_device','public_network'),1,5,5,0),))
    for scenario in predictor.sample_scenarios(r.snapshot()):
        registration,completion=scenario
        expected=marks[registration.registration.downloaded_version].summary
        assert completion.summary==expected
