"""Lightweight configured-Design value with the exact shared serialized identity."""
from dataclasses import dataclass,asdict
@dataclass(frozen=True)
class DesignConfiguration:
    enabled:bool
    source:str
    method_version:str='configured-design-v1'
    def __post_init__(self):
        if type(self.enabled) is not bool or not self.source or self.source.strip()!=self.source or self.method_version!='configured-design-v1':
            raise ValueError('explicit configured Design/source/version required')
    def to_dict(self):return asdict(self)
    @classmethod
    def from_dict(cls,obj):return cls(**dict(obj))
def apply_configured_design_zeta(ratio,enabled):
    import numpy as np
    if enabled not in (0,1):raise ValueError('frozen Design must be 0/1')
    ratio=np.asarray(ratio,dtype=np.float64)
    if not int(enabled):return np.ones_like(ratio)
    if not np.all(np.isfinite(ratio)) or np.any(ratio<0):raise ValueError('invalid lagged opportunity ratio')
    return ratio.copy()
