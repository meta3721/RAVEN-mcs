"""Shared production reconstruction for fixed and dynamic configured runners."""
from dataclasses import dataclass
import numpy as np

from raven_mcs.correction.hajek import raw_weights, group_mass, total_mass, normalized_weights, composition
from raven_mcs.correction.effective_sample_size import effective_sample_size


@dataclass(frozen=True)
class Stage1Masses:
    raw: np.ndarray
    groups: np.ndarray
    total: float
    weights: np.ndarray
    composition: np.ndarray
    effective_n: float


def reconstruct_stage1(zeta, p_obs, observation, group_ids, *, num_groups, a_max=20., p_min=.05):
    arrays=[np.asarray(x) for x in (zeta,p_obs,observation,group_ids)]
    if any(x.ndim != 1 or x.shape != arrays[0].shape for x in arrays):
        raise ValueError("stage1 vectors must have matching one-dimensional shapes")
    zeta,p_obs,observation,group_ids=arrays
    if any(not np.all(np.isfinite(x)) for x in arrays):
        raise ValueError("stage1 inputs must be finite")
    if np.any(p_obs < 0) or np.any(p_obs > 1) or np.any(zeta < 0):
        raise ValueError("invalid stage1 design/observation probability")
    if np.any((observation != 0) & (observation != 1)):
        raise ValueError("observation must be binary")
    if num_groups <= 0 or np.any(group_ids < 0) or np.any(group_ids >= num_groups) or np.any(group_ids != group_ids.astype(int)):
        raise ValueError("invalid target group IDs")
    raw=raw_weights(zeta,p_obs,a_max=a_max,p_min=p_min)
    groups=group_mass(observation,raw,group_ids,n_groups=num_groups)
    total=total_mass(groups)
    weights=normalized_weights(observation,raw,total)
    return Stage1Masses(raw,groups,total,weights,composition(groups,total),
                        effective_sample_size(observation,raw,total_mass=total))
