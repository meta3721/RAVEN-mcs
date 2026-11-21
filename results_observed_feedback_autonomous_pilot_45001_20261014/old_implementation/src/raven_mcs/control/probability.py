"""Registration-frozen joint consumption probability; this module does not fit q."""
from __future__ import annotations

from dataclasses import asdict, dataclass
from typing import Protocol

from raven_mcs.control import METHOD_VERSION
from raven_mcs.control.schema import QValue, Registration, InputError, finite
from raven_mcs.utils.hashing import sha256_json


def policy_context_hash(config,settings,mu,predictor_version,applicability=None):
    """q is policy-specific, including target and all aggregation constraints."""
    return sha256_json(dict(control=config.to_dict(),settings=asdict(settings),mu=list(mu),
                           predictor_version=predictor_version,**({'applicability':applicability} if applicability is not None else {})))


@dataclass(frozen=True)
class RegistrationFeatures:
    model_age: int
    device_class: str
    network_class: str
    maximum_deadline_slack: float
    pool_count: int
    in_flight_count: int
    configuration_hash: str
    as_of: float
    policy_version: str = METHOD_VERSION
    clock_run_id: str = ''
    service_parameters_hash: str = ''

    def __post_init__(self):
        finite((self.maximum_deadline_slack,self.as_of), 'registration features', nonnegative=True)
        if min(self.model_age,self.pool_count,self.in_flight_count) < 0:
            raise InputError("invalid registration history counts")
        if self.policy_version != METHOD_VERSION or not self.configuration_hash:
            raise InputError("registration feature policy/config mismatch")


class FrozenQModel(Protocol):
    version: str
    as_of: float

    def predict_at_registration(self, features: RegistrationFeatures) -> QValue: ...
    def to_dict(self) -> dict: ...


@dataclass(frozen=True)
class PendingQModel:
    version: str = 'q-calibration-pending'
    as_of: float = 0.

    def predict_at_registration(self, features):
        if self.as_of > features.as_of:
            raise InputError("future q model")
        return QValue(None,features.as_of,self.version,METHOD_VERSION,'','dependency_pending',
                      sha256_json(asdict(features)))

    def to_dict(self):
        return dict(kind='pending',**asdict(self))


@dataclass(frozen=True)
class DiagnosticPriorQ:
    """Approved acquisition prior Beta(1,1); never a calibrated estimate."""
    configuration_hash: str
    version: str = 'pi_boot/Beta_1_1_prior_v1'
    as_of: float = 0.
    def predict_at_registration(self,features):
        if features.configuration_hash!=self.configuration_hash or self.as_of>features.as_of:
            raise InputError('diagnostic prior applicability/time mismatch')
        return QValue(.5,features.as_of,self.version,METHOD_VERSION,'predeclared_Beta(1,1)',
            'diagnostic_prior',sha256_json(asdict(features)))
    def to_dict(self):return dict(kind='diagnostic_prior',**asdict(self))


@dataclass(frozen=True)
class EvidenceQTable:
    """Externally calibrated, frozen values indexed by exact lawful feature hash.

    No extrapolation or constant cold-start. Actual calibration evidence is supplied
    by the next authorized stage. Isolated fixtures are explicitly inadmissible in
    production and cannot establish calibration.
    """
    version: str
    as_of: float
    evidence_id: str
    values: tuple[tuple[str,float], ...]
    policy_version: str = METHOD_VERSION
    role: str = 'calibrated_estimate'

    def __post_init__(self):
        if self.policy_version != METHOD_VERSION or self.role not in {'calibrated_estimate','isolated_test_input'}:
            raise InputError("invalid q model identity")
        if not self.version or not self.evidence_id:
            raise InputError("q calibration evidence required")
        finite((v for _,v in self.values),'q estimates')
        if any(not 0 < v <= 1 for _,v in self.values) or len(dict(self.values)) != len(self.values):
            raise InputError("q table values/keys invalid")

    def predict_at_registration(self, features):
        if self.as_of > features.as_of:
            raise InputError("future q model")
        key=sha256_json(asdict(features))
        value=dict(self.values).get(key)
        if value is None:
            return PendingQModel(self.version,self.as_of).predict_at_registration(features)
        return QValue(value,features.as_of,self.version,self.policy_version,self.evidence_id,self.role,key)

    def to_dict(self):
        return dict(kind='evidence_table',**asdict(self))


@dataclass(frozen=True)
class EvidenceLogisticQ:
    """A deserialized externally fitted model, never fitted by the controller.

    Features have a fixed lawful encoding. Unknown public strata/count ranges
    return pending rather than an invented cold-start probability.
    """
    version: str
    as_of: float
    evidence_id: str
    weights: tuple[float, ...]  # intercept, age, max slack, pool, pending
    strata: tuple[tuple[str,str], ...]
    max_counts: int
    configuration_hash: str
    policy_version: str = METHOD_VERSION
    role: str = 'calibrated_estimate'

    def __post_init__(self):
        finite(self.weights+(self.as_of,), 'q model')
        if len(self.weights)!=5 or not self.version or not self.evidence_id or self.max_counts<0:
            raise InputError("invalid q model parameters")
        if self.role not in {'calibrated_estimate','isolated_test_input'} or self.policy_version!=METHOD_VERSION:
            raise InputError("q model belongs to another policy")

    def predict_at_registration(self, features):
        import math
        if self.as_of > features.as_of: raise InputError("future q model")
        if ((features.device_class,features.network_class) not in self.strata or
                max(features.pool_count,features.in_flight_count)>self.max_counts or
                features.configuration_hash!=self.configuration_hash):
            return PendingQModel(self.version,self.as_of).predict_at_registration(features)
        x=(1.,features.model_age,features.maximum_deadline_slack,features.pool_count,features.in_flight_count)
        logit=sum(a*b for a,b in zip(self.weights,x))
        probability=1/(1+math.exp(-logit)) if logit>=0 else math.exp(logit)/(1+math.exp(logit))
        if probability <= 0: raise InputError("q numerically zero; positivity unavailable")
        return QValue(probability,features.as_of,self.version,self.policy_version,self.evidence_id,
                      self.role,sha256_json(asdict(features)))

    def to_dict(self): return dict(kind='evidence_logistic',**asdict(self))


def q_model_from_dict(obj):
    obj=dict(obj); kind=obj.pop('kind')
    if kind=='pending': return PendingQModel(**obj)
    if kind=='diagnostic_prior':return DiagnosticPriorQ(**obj)
    if kind=='evidence_table':
        obj['values']=tuple(tuple(x) for x in obj['values'])
        return EvidenceQTable(**obj)
    if kind=='evidence_logistic':
        obj['weights']=tuple(obj['weights']);obj['strata']=tuple(tuple(x) for x in obj['strata'])
        return EvidenceLogisticQ(**obj)
    raise InputError("unknown q model")


@dataclass
class AttemptRecord:
    registration: Registration
    features: RegistrationFeatures
    q: QValue
    physical_outcome: str = 'pending'
    accepted_at: float | None = None
    completed_at: float | None = None
    terminal_reason: str | None = None
    terminal_at: float | None = None
    consumed: int | None = None
    right_censored_at: float | None = None

    def mature(self, reason: str, now: float):
        if self.consumed is not None:
            raise InputError("attempt already has a terminal outcome")
        if now < self.registration.registered_at:
            raise InputError("terminal result precedes registration")
        if reason not in {'consumed','compute_failure','network_failure','no_observations','superseded','expired','horizon_unconsumed'}:
            raise InputError("unknown terminal reason")
        self.terminal_reason=reason; self.terminal_at=now
        self.consumed=int(reason=='consumed')
        self.right_censored_at=None

    def censor(self, now: float):
        if self.consumed is None:
            self.right_censored_at=now

    @property
    def mature_label(self):
        return self.consumed

    def to_dict(self): return asdict(self)

    @classmethod
    def from_dict(cls,obj):
        obj=dict(obj)
        obj['registration']=Registration(**obj['registration'])
        obj['features']=RegistrationFeatures(**obj['features'])
        obj['q']=QValue(**obj['q'])
        return cls(**obj)
