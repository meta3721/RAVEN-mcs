"""OF-v1 registration-frozen consumption identity; never fits a model."""
from dataclasses import asdict,dataclass
from . import METHOD_VERSION
from .schema import QValue,Registration,InputError,DependencyPending,finite
from raven_mcs.utils.hashing import sha256_json

@dataclass(frozen=True)
class RegistrationFeatures:
    model_age:int
    device_class:str
    network_class:str
    maximum_deadline_slack:float
    pool_count:int
    in_flight_count:int
    configuration_hash:str
    as_of:float
    history_hash:str
    history_json:str
    clock_run_id:str
    service_parameters_hash:str
    policy_version:str=METHOD_VERSION
    def __post_init__(self):
        finite((self.as_of,self.maximum_deadline_slack),'q registration time',nonnegative=True)
        if min(self.model_age,self.pool_count,self.in_flight_count)<0 or self.policy_version!=METHOD_VERSION:
            raise InputError('q registration version/domain mismatch')
        if not all((self.configuration_hash,self.history_hash,self.clock_run_id,self.service_parameters_hash)):
            raise InputError('q applicability/history/clock missing')
        import json
        if sha256_json(json.loads(self.history_json))!=self.history_hash:raise InputError('registration public-history digest mismatch')

def policy_context_hash(config,settings,mu,applicability):
    return sha256_json(dict(event='I(100)|H_reg,R=1,E=1',policy=METHOD_VERSION,control=config.to_dict(),
        settings=asdict(settings),mu=list(mu),applicability=applicability))

@dataclass(frozen=True)
class PendingQModel:
    version:str='OF-v1/q-calibration-pending'
    as_of:float=0.
    def predict_at_registration(self,features):
        if self.as_of>features.as_of:raise InputError('future q model')
        return QValue(None,features.as_of,self.version,METHOD_VERSION,'','dependency_pending',sha256_json(asdict(features)))
    def to_dict(self):return dict(kind='pending',**asdict(self))

@dataclass(frozen=True)
class IsolatedQ:
    value:float=.5
    version:str='OF-v1/isolated-input-not-calibrated'
    as_of:float=0.
    def predict_at_registration(self,features):
        if self.as_of>features.as_of:raise InputError('future q model')
        return QValue(self.value,features.as_of,self.version,METHOD_VERSION,'explicit_math_fixture','isolated_test_input',sha256_json(asdict(features)))
    def to_dict(self):return dict(kind='isolated_test',**asdict(self))

@dataclass(frozen=True)
class EvidenceQTable:
    version:str
    as_of:float
    evidence_id:str
    configuration_hash:str
    values:tuple
    def __post_init__(self):
        finite((v for _,v in self.values),'q evidence')
        if not self.evidence_id or not self.configuration_hash or any(not 0<=v<=1 for _,v in self.values):raise InputError('q evidence missing/invalid')
        if len(dict(self.values))!=len(self.values):raise InputError('duplicate q feature')
    def predict_at_registration(self,features):
        if self.as_of>features.as_of:raise InputError('future q model')
        if self.configuration_hash!=features.configuration_hash:raise DependencyPending('OF-v1 probability applicability mismatch')
        key=sha256_json(asdict(features));v=dict(self.values).get(key)
        if v is None:return PendingQModel(self.version,self.as_of).predict_at_registration(features)
        return QValue(v,features.as_of,self.version,METHOD_VERSION,self.evidence_id,
            'zero_support' if v==0 else 'calibrated_estimate',key)
    def to_dict(self):return dict(kind='evidence_table',**asdict(self))

def q_model_from_dict(obj):
    obj=dict(obj);kind=obj.pop('kind')
    if kind=='pending':return PendingQModel(**obj)
    if kind=='isolated_test':return IsolatedQ(**obj)
    if kind=='evidence_table':obj['values']=tuple(tuple(x) for x in obj['values']);return EvidenceQTable(**obj)
    raise InputError('OF-v1 q kind unsupported; legacy/diagnostic q not accepted')

@dataclass
class AttemptRecord:
    registration:Registration
    features:RegistrationFeatures
    q:QValue
    R:int
    E:int
    stage1_hash:str
    physical_outcome:str='pending'
    accepted_at:float|None=None
    completed_at:float|None=None
    terminal_reason:str|None=None
    terminal_at:float|None=None
    consumed:int|None=None
    right_censored_at:float|None=None
    def mature(self,reason,now):
        if self.consumed is not None:raise InputError('attempt already terminal')
        if now<self.registration.registered_at or reason not in {'consumed','compute_failure','network_failure','no_observations','superseded','expired','horizon_unconsumed'}:
            raise InputError('invalid terminal event')
        self.terminal_reason=reason;self.terminal_at=now;self.consumed=int(reason=='consumed');self.right_censored_at=None
    def censor(self,now):
        if self.consumed is None:self.right_censored_at=now
    def to_dict(self):return asdict(self)
    @classmethod
    def from_dict(cls,obj):
        obj=dict(obj);obj['registration']=Registration(**obj['registration']);obj['features']=RegistrationFeatures(**obj['features']);obj['q']=QValue(**obj['q'])
        return cls(**obj)
