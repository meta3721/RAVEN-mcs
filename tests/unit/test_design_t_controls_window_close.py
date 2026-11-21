import numpy as np
from raven_mcs.sag.r1l_design import apply_configured_design_zeta


def test_frozen_design_controls_factor():
    ratio=np.array([2.,4.])
    np.testing.assert_array_equal(apply_configured_design_zeta(ratio,1),ratio)
    np.testing.assert_array_equal(apply_configured_design_zeta(ratio,0),[1.,1.])
