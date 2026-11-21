from raven_mcs.sag.r1l_design import DesignConfiguration, configured_decide_gate_and_design


def test_window_close_receives_frozen_design_and_separate_gate():
    rec=configured_decide_gate_and_design({'certificate_state':'WARMUP'},configuration=DesignConfiguration(True,'test'),window_id=0)
    assert rec['Design_t']==1 and rec['Gate_t']==0
    assert rec['coverage_role']=='diagnostic_only'
