"""Immutable, serializable current information. No event-trace or label fields."""
from __future__ import annotations

from dataclasses import asdict, dataclass
import math
from typing import Any

from raven_mcs_observed_feedback import METHOD_VERSION
from .design import DesignConfiguration
from raven_mcs.utils.hashing import sha256_json


class InputError(ValueError):
    pass


class DependencyPending(InputError):
    pass


def finite(values, name: str, *, nonnegative: bool = False):
    if any(not math.isfinite(float(x)) or (nonnegative and float(x) < 0) for x in values):
        raise InputError(f"invalid {name}")


@dataclass(frozen=True)
class ControlConfig:
    source: str
    design: DesignConfiguration
    grid: float = .1
    deadline: float = 4.
    age_max: int = 5
    warmup: float = 20.
    age_weight: float = .02
    wait_weight: float = .20
    minimum_clients: int = 3
    scoring_tolerance: float = 1e-7
    planning_cpu_seconds: float = 2.
    theta: float = .02
    kappa: float = .10
    patience: float = .20
    method_version: str = METHOD_VERSION

    def __post_init__(self):
        if not self.source or not isinstance(self.design, DesignConfiguration):
            raise InputError("explicit configured Design and source required")
        expected = dict(grid=.1, deadline=4., age_max=5,
                        warmup=20., age_weight=.02, wait_weight=.20,
                        minimum_clients=3, scoring_tolerance=1e-7, theta=.02, kappa=.10, patience=.20,
                        planning_cpu_seconds=2., method_version=METHOD_VERSION)
        if any(getattr(self, k) != v for k, v in expected.items()):
            raise InputError("configuration changes frozen OF-v1 definition")

    def to_dict(self):
        return asdict(self)

    @classmethod
    def from_dict(cls, obj):
        obj = dict(obj)
        obj['design'] = DesignConfiguration.from_dict(obj['design'])
        return cls(**obj)


@dataclass(frozen=True)
class P2Settings:
    lambda_group: float = 1.
    lambda_beta: float = 1.
    lambda_variance: float = .1
    lambda_staleness: float = .1
    alpha_max: float = .5
    e_min: float = 3.
    server_eta: float = .01
    max_server_learning_rate: float = 1.
    d_max: float = 10.
    q_min: float = .05
    v_floor: float = 1e-4

    def __post_init__(self):
        finite(asdict(self).values(), 'P2 settings', nonnegative=True)
        if not (self.alpha_max > 0 and self.e_min > 0 and 0 < self.q_min <= 1 and self.d_max > 0):
            raise InputError("invalid P2/probability bounds")
        defaults=dict(lambda_group=1.,lambda_beta=1.,lambda_variance=.1,lambda_staleness=.1,alpha_max=.5,e_min=3.,
            server_eta=.01,max_server_learning_rate=1.,d_max=10.,q_min=.05,v_floor=1e-4)
        if asdict(self)!=defaults:raise InputError('OF-v1 requires the frozen full P2 settings')


@dataclass(frozen=True)
class Stage1Summary:
    masses: tuple[float, ...]
    local_weights: tuple[float, ...]
    effective_n: float
    observed_count: int
    design_enabled: bool
    design_source: str
    frozen_at: float
    estimator_version: str
    ratio: tuple[float, ...]
    p_obs: tuple[float, ...]
    provenance: str
    observed_positions: tuple[int, ...] = ()

    def __post_init__(self):
        finite(self.masses+self.local_weights+self.ratio+self.p_obs+
               (self.effective_n, self.frozen_at), 'stage1', nonnegative=True)
        if not self.masses or any(x > 1 for x in self.p_obs):
            raise InputError("stage1 observation estimates must be in [0,1]; legal clipping is retained")
        if not self.design_source or not self.estimator_version or not self.provenance:
            raise InputError("stage1 provenance required")
        if self.total > 0 and (abs(sum(self.local_weights)-1) > 1e-9 or self.effective_n <= 0):
            raise InputError("stage1 normalization invalid")
        if len(self.observed_positions)!=self.observed_count or any(i<0 or i>=len(self.local_weights) for i in self.observed_positions):
            raise InputError("stage1 observed indices invalid")

    @property
    def total(self):
        return sum(self.masses)

    @property
    def composition(self):
        return tuple(x/self.total for x in self.masses) if self.total else tuple(0. for _ in self.masses)

    @classmethod
    def from_dict(cls, obj):
        obj = dict(obj)
        for k in ('masses','local_weights','ratio','p_obs','observed_positions'):
            obj[k] = tuple(obj[k])
        return cls(**obj)


@dataclass(frozen=True)
class Registration:
    key: str
    client: str
    registered_at: float
    downloaded_version: int
    device_class: str
    network_class: str

    def __post_init__(self):
        finite((self.registered_at,), 'registration time', nonnegative=True)
        if not self.key or not self.client or not self.device_class or not self.network_class:
            raise InputError("public registration metadata missing")
        if type(self.downloaded_version) is not int or self.downloaded_version < 0:
            raise InputError("invalid downloaded version")

    @property
    def stratum(self):
        return (self.device_class, self.network_class)


@dataclass(frozen=True)
class QValue:
    value: float | None
    frozen_at: float
    model_version: str
    policy_version: str
    evidence_id: str
    role: str  # calibrated_estimate / dependency_pending / isolated_test_input
    feature_hash: str

    def __post_init__(self):
        if self.policy_version != METHOD_VERSION:
            raise InputError("q belongs to a different policy")
        finite((self.frozen_at,), 'q time', nonnegative=True)
        if self.role not in {'calibrated_estimate','dependency_pending','isolated_test_input','diagnostic_prior','structural_zero','outside_R','zero_support'}:
            raise InputError("unrecognized q role")
        if self.value is not None:
            finite((self.value,), 'q')
            if not (self.value == 0 and self.role in {'structural_zero','outside_R','zero_support'}) and not 0 < self.value <= 1:
                raise InputError("q must be in (0,1]")
        if self.role in {'structural_zero','outside_R','zero_support'} and self.value != 0:
            raise InputError('domain-excluded records must have mechanism/condition zero')
        if self.role == 'dependency_pending' and self.value is not None:
            raise InputError("pending calibration cannot provide a probability")
        if self.role != 'dependency_pending' and (self.value is None or not self.evidence_id or not self.model_version):
            raise InputError("q evidence/model missing")

    def require(self, *, isolated_test: bool, calibration_only: bool = False):
        if self.role in {'structural_zero','outside_R','zero_support'}:
            raise DependencyPending('excluded-domain record cannot enter inverse probability denominator')
        if self.value is None:
            raise DependencyPending("Q_CALIBRATION_DEPENDENCY_PENDING")
        if self.role == 'isolated_test_input' and not isolated_test:
            raise DependencyPending("test q prohibited in production")
        if self.role == 'diagnostic_prior' and not calibration_only:
            raise DependencyPending('diagnostic prior allowed only in calibration_only')
        return self.value


@dataclass(frozen=True)
class Delivered:
    registration: Registration
    summary: Stage1Summary
    q: QValue
    completed_at: float

    def __post_init__(self):
        if self.completed_at < self.registration.registered_at or self.summary.frozen_at > self.completed_at:
            raise InputError("noncausal delivery")
        if self.q.frozen_at != self.registration.registered_at:
            raise InputError("q must be frozen at this attempt's registration")

    @property
    def key(self):
        return self.registration.key


@dataclass(frozen=True)
class InFlight:
    registration: Registration
    q: QValue
    R: int = 1
    E: int = 1

    def __post_init__(self):
        if self.q.frozen_at != self.registration.registered_at:
            raise InputError("in-flight q registration mismatch")


@dataclass(frozen=True)
class ReleaseSummary:
    time: float
    ell: float
    age: float
    duration: float
    omega: tuple[float,...] = ()

    def score(self, config: ControlConfig):
        return self.ell+config.age_weight*self.age+config.wait_weight*self.duration/config.deadline


@dataclass(frozen=True)
class DecisionSnapshot:
    now: float
    window_open: float
    model_version: int
    revision: int
    config: ControlConfig
    settings: P2Settings
    mu: tuple[float, ...]
    debt: tuple[float, ...]
    pool: tuple[Delivered, ...]
    in_flight: tuple[InFlight, ...]
    last_release: ReleaseSummary | None
    variance: tuple[tuple[str, float], ...]
    seed: int
    experiment_end: float
    isolated_test: bool = False
    calibration_only: bool = False
    probability_applicability: dict | None = None
    clock_namespace: dict | None = None
    service_parameters_hash: str = ''
    q_model_version: str = ''

    def __post_init__(self):
        finite(self.mu+self.debt+(self.now,self.window_open,self.experiment_end), 'snapshot', nonnegative=True)
        if self.calibration_only:raise InputError('calibration_only not authorized for OF-v1')
        if self.experiment_end!=100.:raise InputError('OF-v1 requires T100')
        if self.last_release and len(self.last_release.omega)!=len(self.mu):raise InputError('last actual omega missing')
        if sum(self.debt)>.01*self.model_version*(1+len(self.mu)*43e-7)+1e-8:raise InputError('debt exceeds actual-release finite bound')
        if not self.mu or abs(sum(self.mu)-1) > 1e-9 or len(self.debt) != len(self.mu):
            raise InputError("mu/debt invalid")
        if self.window_open > self.now or self.experiment_end < self.now or self.model_version < 0:
            raise InputError("invalid snapshot clock")
        clients=set()
        keys=set()
        for m in self.pool:
            if m.completed_at > self.now or m.registration.registered_at > self.now:
                raise InputError("future message in snapshot")
            if len(m.summary.masses) != len(self.mu) or m.summary.total <= 0:
                raise InputError("invalid corrected mass in pool")
            age=self.model_version-m.registration.downloaded_version
            if age < 0 or age > self.config.age_max:
                raise InputError("illegal message age")
            if m.registration.client in clients or m.key in keys:
                raise InputError("duplicate client/message")
            clients.add(m.registration.client); keys.add(m.key)
        for item in self.in_flight:
            r=item.registration
            if r.registered_at > self.now or r.downloaded_version > self.model_version:
                raise InputError("future registration/download")
        finite((v for _,v in self.variance), 'variance', nonnegative=True)

    @property
    def fingerprint(self):
        return sha256_json(asdict(self))

    @classmethod
    def from_dict(cls, obj):
        obj=dict(obj)
        obj['config']=ControlConfig.from_dict(obj['config'])
        obj['settings']=P2Settings(**obj['settings'])
        obj['mu']=tuple(obj['mu']); obj['debt']=tuple(obj['debt'])
        obj['variance']=tuple(tuple(x) for x in obj['variance'])
        obj['pool']=tuple(delivered_from_dict(x) for x in obj['pool'])
        obj['in_flight']=tuple(InFlight(Registration(**r['registration']),QValue(**r['q'])) for r in obj['in_flight'])
        if obj['last_release'] is not None:
            obj['last_release']=ReleaseSummary(**dict(obj['last_release'],omega=tuple(obj['last_release']['omega'])))
        return cls(**obj)


def delivered_from_dict(obj: dict[str, Any]):
    return Delivered(Registration(**obj['registration']), Stage1Summary.from_dict(obj['summary']),
                     QValue(**obj['q']), obj['completed_at'])
