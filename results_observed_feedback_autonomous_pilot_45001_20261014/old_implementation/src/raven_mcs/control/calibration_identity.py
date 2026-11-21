"""Explicit finite-consumption estimand and run-local clock identity."""
from dataclasses import dataclass, asdict
from raven_mcs.control.schema import InputError
from raven_mcs.utils.hashing import sha256_json

@dataclass(frozen=True)
class ClockNamespace:
    run_id: str
    origin_utc: str
    unit: str = 'controlled_service_unit'
    def __post_init__(self):
        if not self.run_id or not self.origin_utc or self.unit!='controlled_service_unit':
            raise InputError('explicit run clock required')
    def require_same_run(self,other):
        if self!=other:raise InputError('cross-run logical times are not comparable; publication bridge required')

def endpoint(T):
    if T!=100.:raise InputError('calibration endpoint must remain T=100')
    return dict(name='consumed_by_T_v1',T=T,registration_interval='[0,T)',
        order='causal events through T; scheduled decision; close remaining pool once; administrative termination',
        event='at least one actual server consumption of this attempt at tau<=T',
        unresolved_at_full_T='terminal nonconsumption, physical service remains censored',
        interrupted_before_T='right censored, never assigned zero')

def applicability(*,learning,service,experiment_end,data_identity,target_identity,stage1):
    required_learning={'model','optimizer','local_steps','learning_rate','initial_model_hash','scaler','feature_schema'}
    if not required_learning.issubset(learning) or not service or not stage1:
        raise InputError('incomplete probability applicability')
    return dict(schema='q_policy_applicability_v2',learning=learning,service=service,
        endpoint=endpoint(experiment_end),data_identity=data_identity,target_identity=target_identity,
        stage1=stage1,service_fit_rule='warmup20 observed competing risks and same-client joint marks; frozen thereafter',
        consumption_policy='conditional-bundle-v2 with prior role; no calibration evidence')

def service_parameters_hash(model):
    obj=model.to_dict();obj.pop('q_model') # no recursive q/self hash
    return sha256_json(obj)
