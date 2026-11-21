import dataclasses
import pytest
from raven_mcs.aggregation.method_policy import get_method_policy
from raven_mcs.experiments.r1m_method_freeze import formal_cli_parser, assert_frozen
from raven_mcs.sag.r1l_design import DesignConfiguration, configuration_for_method, configured_decide_gate_and_design
from raven_mcs.training.cache_identity import configured_cache_identity, validate_configured_cache
from raven_mcs.training.cache_identity import load_configured_artifact


def test_configuration_roundtrip_and_explicit_cli():
    parser=formal_cli_parser()
    for setting in ('on','off'):
        args=parser.parse_args(['--design',setting])
        config=configuration_for_method(args.method,args.design,source=args.design_source)
        assert DesignConfiguration.from_dict(config.to_dict())==config
        with pytest.raises(dataclasses.FrozenInstanceError):
            config.enabled=False
    with pytest.raises(ValueError,match='CONFIGURATION_REQUIRED'):
        configuration_for_method('raven_mcs',None,source='test')
    assert_frozen()


def test_diagnostic_and_configuration_have_distinct_authority():
    for enabled in (True,False):
        cfg=DesignConfiguration(enabled,'explicit_test')
        for gate in (0,1):
            rec=configured_decide_gate_and_design({'certificate_state':'CERTIFIED','C_LCB':.06 if gate else .04},configuration=cfg,window_id=0)
            assert rec['Design_t']==int(enabled) and rec['Gate_t']==gate
    assert get_method_policy('raven_mcs').design_control=='configured'
    assert get_method_policy('raven_coverage_legacy').legacy_only


def test_design_dependent_cache_rejects_legacy_and_changed_configuration():
    config=DesignConfiguration(True,'explicit_test')
    expected=configured_cache_identity(config,target_id='frozen_target',eventtrace_id='fixed_trace',optimizer='SGD')
    validate_configured_cache(expected,expected)
    for old in ({'gate_mode':'aggregate_coverage'}, {}, configured_cache_identity(DesignConfiguration(False,'explicit_test'),**expected['dependencies'])):
        with pytest.raises(ValueError,match='CACHE_IDENTITY_ERROR'):
            validate_configured_cache(old,expected)


def test_actual_cache_reader_requires_identity_before_loading(tmp_path):
    import torch
    import json
    config=DesignConfiguration(True,'explicit_test')
    expected=configured_cache_identity(config,eventtrace='unique',target='frozen',model='fixed',optimizer='SGD')
    path=tmp_path/'weights.pt'
    torch.save({'weights':torch.tensor([2.,4.])},path)
    with pytest.raises(ValueError,match='CACHE_IDENTITY_ERROR'):
        load_configured_artifact(path,expected)
    path.with_suffix('.pt.identity.json').write_text(json.dumps(expected),encoding='utf-8')
    assert torch.equal(load_configured_artifact(path,expected)['weights'],torch.tensor([2.,4.]))


def test_resolved_configuration_records_identity():
    from raven_mcs.utils.config import resolve_run_config
    with pytest.raises(ValueError,match='CONFIGURATION_REQUIRED'):
        resolve_run_config(method='raven_mcs')
    cfg=resolve_run_config(method='raven_mcs',overrides={'design':'off','design_source':'explicit_test'})
    assert cfg['method_version']=='configured-design-v1'
    assert cfg['design_configuration']['enabled'] is False
    assert cfg['coverage_role']=='diagnostic_only'


def test_legacy_configuration_explicitly_identified_and_no_ignored_design():
    from raven_mcs.utils.config import resolve_run_config
    from raven_mcs.experiments.legacy_coverage_freeze import formal_cli_parser
    cfg=resolve_run_config(method='raven_coverage_legacy')
    assert cfg['method_version']=='coverage-controlled-v1'
    assert cfg['coverage_role']=='controls_legacy_design' and cfg['design_configuration'] is None
    with pytest.raises(ValueError,match='legacy controls'):
        resolve_run_config(method='raven_coverage_legacy',overrides={'design':'on'})
    with pytest.raises(SystemExit):
        formal_cli_parser().parse_args([])
    assert formal_cli_parser().parse_args(['--method','raven_coverage_legacy']).method=='raven_coverage_legacy'
