"""Freeze the same correction used by the full runner, before local work."""
from __future__ import annotations
import numpy as np

from raven_mcs.correction.design_ratio import zeta_hat_stratum
from raven_mcs.correction.stage1 import reconstruct_stage1
from raven_mcs.control.schema import ControlConfig, InputError, Stage1Summary
from raven_mcs.sag.r1l_design import apply_configured_design_zeta


def freeze_stage1(*, config: ControlConfig, target_opportunity, lagged_opportunity,
                 p_obs, observation, group_ids, num_groups, now: float,
                 estimator_as_of: float, estimator_version: str, provenance: str,
                 a_max=20., p_min=.05, pi_min=1e-6) -> Stage1Summary:
    if estimator_as_of > now:
        raise InputError("stage1 uses future estimator")
    tar=np.asarray(target_opportunity,dtype=float)
    opp=np.asarray(lagged_opportunity,dtype=float)
    if tar.shape != opp.shape or not np.all(np.isfinite(tar)) or not np.all(np.isfinite(opp)):
        raise InputError("invalid design inputs")
    if np.any(tar < 0) or np.any(opp <= 0):
        raise InputError("missing/invalid lagged opportunity support")
    ratio=zeta_hat_stratum(tar,opp,pi_min=pi_min)
    factor=apply_configured_design_zeta(ratio,int(config.design.enabled))
    result=reconstruct_stage1(factor,p_obs,observation,group_ids,num_groups=num_groups,
                              a_max=a_max,p_min=p_min)
    return Stage1Summary(tuple(result.groups),tuple(result.weights),result.effective_n,
        int(np.sum(observation)),config.design.enabled,config.design.source,now,
        estimator_version,tuple(factor),tuple(float(x) for x in p_obs),provenance,
        tuple(int(i) for i in np.flatnonzero(observation)))
