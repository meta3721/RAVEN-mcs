"""Dynamic message lifecycle shared by adaptive and fixed closing policies."""
from __future__ import annotations

from dataclasses import asdict
import copy
import numpy as np

from raven_mcs.aggregation.debt import update_debt
from raven_mcs.control.schema import (ControlConfig, DecisionSnapshot, Delivered, InFlight, InputError,
    P2Settings, Registration, ReleaseSummary, Stage1Summary, delivered_from_dict)
from raven_mcs.control.probability import AttemptRecord, RegistrationFeatures, q_model_from_dict,policy_context_hash
from raven_mcs.control.preview import ReleasePreview, preview_release
from raven_mcs.control.predictor import FrozenServiceModel
from raven_mcs.utils.hashing import sha256_json


class ArrayBackend:
    """Isolated deterministic update fixture, never a local-training substitute."""
    kind='isolated_array_backend'

    def __init__(self, theta):
        self.theta=np.asarray(theta,dtype=float).copy()
        if self.theta.ndim!=1 or not np.all(np.isfinite(self.theta)):
            raise InputError("invalid server vector")
        self.versions={0:self.theta.copy()}
        self.work={};self.updates={}
        self.local_optimizer_steps=0

    def has_version(self, version): return version in self.versions

    def prepare_work(self, registration, summary):
        self.work[registration.key]=dict(downloaded_version=registration.downloaded_version,
                                         weights=list(summary.local_weights),training_started=False)

    def start_local_training(self, *args, **kwargs):
        raise InputError("array fixture cannot execute local training")

    def complete(self, key, update):
        value=np.asarray(update,dtype=float)
        if key not in self.work or value.shape!=self.theta.shape or not np.all(np.isfinite(value)):
            raise InputError("missing/malformed actual update")
        self.updates[key]=value.copy()

    def apply(self, keys, alpha, eta, new_version):
        if any(k not in self.updates for k in keys):
            raise InputError("actual update missing; refusing consumption")
        new=self.theta.copy()
        for k,a in zip(keys,alpha): new-=eta*a*self.updates[k]
        if not np.all(np.isfinite(new)): raise InputError("nonfinite server update")
        self.theta=new;self.versions[new_version]=new.copy()
        for key in keys:self.updates.pop(key)
        return {}

    def to_dict(self):
        return dict(kind=self.kind,theta=self.theta.tolist(),versions={str(k):v.tolist() for k,v in self.versions.items()},
                    work=copy.deepcopy(self.work),updates={k:v.tolist() for k,v in self.updates.items()},
                    local_optimizer_steps=self.local_optimizer_steps)

    def restore(self,obj):
        if obj['kind']!=self.kind: raise InputError("backend checkpoint identity mismatch")
        self.theta=np.asarray(obj['theta'],dtype=float)
        self.versions={int(k):np.asarray(v,dtype=float) for k,v in obj['versions'].items()}
        self.work=copy.deepcopy(obj['work']);self.updates={k:np.asarray(v,dtype=float) for k,v in obj['updates'].items()}
        self.local_optimizer_steps=obj['local_optimizer_steps']


class DynamicWindowRunner:
    """Consumes causal events, not EventTrace.U or a future event queue.

    The backend owns model/checkpoint/update tensors. DecisionSnapshot exposes
    none of them and no uncompleted Stage1 payload. Fixed policies call the same
    apply_release method as conditional-bundle-v2.
    """
    def __init__(self, *, config: ControlConfig, settings: P2Settings, mu, predictor: FrozenServiceModel,
                 q_model, backend, seed: int, experiment_end: float, open_time=0.,
                 isolated_test=False, data_identity: str, target_identity: str,
                 calibration_only=False,probability_applicability=None,clock_namespace=None):
        if backend.kind=='isolated_array_backend' and not isolated_test:
            raise InputError("fixture backend forbidden in production")
        if not data_identity or not target_identity:
            raise InputError("data/target provenance required")
        if predictor.as_of>open_time or q_model.as_of>open_time:
            raise InputError("future frozen estimator")
        if predictor.q_model!=q_model.to_dict():
            raise InputError("planning and live q must have one frozen model")
        if q_model.to_dict()['kind']=='diagnostic_prior' and not calibration_only:
            raise InputError('diagnostic prior prohibited outside calibration_only')
        if calibration_only:
            from raven_mcs.control.calibration_identity import endpoint,ClockNamespace
            endpoint(experiment_end)
            if isolated_test or not probability_applicability or not clock_namespace or seed!=43001:
                raise InputError('first acquisition identity/seed required')
            ClockNamespace(**clock_namespace)
        self._frozen_config=ControlConfig.from_dict(config.to_dict())
        self.settings=settings;self.mu=tuple(float(x) for x in mu)
        self.debt=tuple(0. for _ in self.mu)
        self._predictor=FrozenServiceModel.from_dict(predictor.to_dict())
        self._q_model=q_model_from_dict(q_model.to_dict())
        self.backend=backend;self.seed=seed;self.experiment_end=experiment_end
        self.now=float(open_time);self.window_open=float(open_time);self.model_version=0
        self.window_id=0;self.revision=0;self.isolated_test=isolated_test
        self.calibration_only=bool(calibration_only)
        self.probability_applicability=copy.deepcopy(probability_applicability)
        self.clock_namespace=copy.deepcopy(clock_namespace)
        self.data_identity=data_identity;self.target_identity=target_identity
        self.pool={};self.in_flight={};self.attempts={};self.private_stage1={}
        self.consumed=set();self.last_release=None;self.variance={}
        self.events=[];self.closures=[];self.diagnostics=[];self.decisions=[]
        self.rng_state=dict(seed=seed,scheme='SeedSequence[seed,tick,scenario,94031]')
        self.snapshot()  # validates current input

    @property
    def config(self):return self._frozen_config

    @property
    def predictor(self):return self._predictor

    @property
    def q_model(self):return self._q_model

    def advance_time(self, now):
        if not np.isfinite(now) or now<self.now-1e-9 or now>self.experiment_end+1e-9:
            raise InputError("nonmonotone/invalid event time")
        if now>self.now:
            self.now=float(now);self.revision+=1
        self.expire()

    def _event(self, kind, key=None, **extra):
        self.events.append(dict(time=self.now,kind=kind,key=key,window=self.window_id,
                                model_version=self.model_version,**extra))

    def registration_features(self, registration):
        return RegistrationFeatures(self.model_version-registration.downloaded_version,
            registration.device_class,registration.network_class,
            max(0.,self.window_open+self.config.deadline-registration.registered_at),
            len(self.pool),len(self.in_flight),policy_context_hash(self.config,self.settings,self.mu,self.predictor.version,self.probability_applicability),registration.registered_at,
            clock_run_id=(self.clock_namespace or {}).get('run_id',''),service_parameters_hash=self.service_parameter_identity())

    def service_parameter_identity(self):
        from raven_mcs.control.calibration_identity import service_parameters_hash
        return service_parameters_hash(self.predictor)

    def on_register(self, registration: Registration, summary: Stage1Summary):
        self.advance_time(registration.registered_at)
        if registration.key in self.attempts or registration.downloaded_version>self.model_version or not self.backend.has_version(registration.downloaded_version):
            raise InputError("duplicate registration or unavailable/future checkpoint")
        if summary.frozen_at!=registration.registered_at or len(summary.masses)!=len(self.mu):
            raise InputError("stage1 must be frozen at this actual registration")
        if summary.design_enabled!=self.config.design.enabled or summary.design_source!=self.config.design.source:
            raise InputError("message uses different frozen window Design")
        features=self.registration_features(registration)
        q=self.q_model.predict_at_registration(features)
        if q.frozen_at!=registration.registered_at or q.model_version!=self.q_model.version:
            raise InputError("q registration freeze mismatch")
        if q.role=='isolated_test_input' and not self.isolated_test:
            raise InputError("isolated q cannot register in production")
        self.attempts[registration.key]=AttemptRecord(registration,features,q)
        self.private_stage1[registration.key]=summary
        self.in_flight[registration.key]=InFlight(registration,q)
        self.backend.prepare_work(registration,summary)
        self._event('registered',registration.key,downloaded_version=registration.downloaded_version,
                    stage1_hash=sha256_json(asdict(summary)),q_role=q.role,q_model=q.model_version)
        self.revision+=1
        if summary.total<=0:
            self.attempts[registration.key].mature('no_observations',self.now)
            self.in_flight.pop(registration.key)
        self.expire()
        return q

    def start_local_training(self, key, observed_records, *, authorization):
        if key not in self.private_stage1: raise InputError("unregistered training work")
        self.attempts[key].q.require(isolated_test=self.isolated_test,calibration_only=self.calibration_only)
        return self.backend.start_local_training(key,observed_records,authorization=authorization)

    def on_failure(self, key, now, *, reason):
        self.advance_time(now)
        if key not in self.attempts or reason not in {'compute_failure','network_failure'}:
            raise InputError("invalid failure notification")
        rec=self.attempts[key]
        if rec.physical_outcome!='pending':raise InputError("duplicate/conflicting physical outcome")
        rec.physical_outcome=reason;self.in_flight.pop(key,None)
        if rec.consumed is None:rec.mature(reason,self.now)
        self._event('notified_failure',key,reason=reason);self.revision+=1

    def on_completion(self, key, now, *, update):
        self.advance_time(now)
        if key not in self.attempts: raise InputError("unregistered completion")
        rec=self.attempts[key]
        if rec.physical_outcome!='pending':raise InputError("duplicate/conflicting completion")
        # Validate actual tensor before admitting any message. This field never
        # enters a snapshot or the planning subprocess.
        self.backend.complete(key,update)
        rec.physical_outcome='completion';rec.completed_at=self.now
        self.in_flight.pop(key,None)
        self._event('physically_completed',key);self.revision+=1
        if rec.consumed is not None:
            self._event('completed_after_terminal',key,terminal=rec.terminal_reason)
            return
        reg=rec.registration
        if self.model_version-reg.downloaded_version>self.config.age_max:
            rec.mature('expired',self.now);self._event('expired',key);return
        current=self.pool.get(reg.client)
        if current is not None:
            if (current.registration.registered_at,current.key)>(reg.registered_at,key):
                rec.mature('superseded',self.now);self._event('older_completion_rejected',key);return
            self.attempts[current.key].mature('superseded',self.now)
            self._event('superseded',current.key,replacement=key)
        msg=Delivered(reg,self.private_stage1[key],rec.q,self.now)
        self.pool[reg.client]=msg;rec.accepted_at=self.now
        self._event('accepted',key)

    def expire(self):
        for client,msg in list(self.pool.items()):
            if self.model_version-msg.registration.downloaded_version>self.config.age_max:
                del self.pool[client];self.attempts[msg.key].mature('expired',self.now)
                self._event('expired',msg.key);self.revision+=1
        for key,item in list(self.in_flight.items()):
            if self.model_version-item.registration.downloaded_version>self.config.age_max:
                self.in_flight.pop(key)
                if self.attempts[key].consumed is None:self.attempts[key].mature('expired',self.now)
                self._event('expired_in_flight',key);self.revision+=1

    def snapshot(self):
        return DecisionSnapshot(self.now,self.window_open,self.model_version,self.revision,self.config,
            self.settings,self.mu,self.debt,tuple(sorted(self.pool.values(),key=lambda m:m.registration.client)),
            tuple(self.in_flight[k] for k in sorted(self.in_flight)),self.last_release,
            tuple(sorted(self.variance.items())),self.predictor.version,self.seed,self.experiment_end,self.isolated_test,
            self.calibration_only,copy.deepcopy(self.probability_applicability),copy.deepcopy(self.clock_namespace),self.service_parameter_identity())

    def preview_release(self): return preview_release(self.snapshot())

    def apply_release(self, preview: ReleasePreview):
        snapshot=self.snapshot()
        if preview.fingerprint!=snapshot.fingerprint:
            raise InputError("STALE_PREVIEW: recompute for the current snapshot")
        if set(preview.keys)&self.consumed or tuple(m.key for m in snapshot.pool)!=preview.keys:
            raise InputError("duplicate consumption or preview key mismatch")
        from raven_mcs.control.preview import residual
        if residual(preview.alpha,self.settings)>1e-7:
            raise InputError("invalid applied weight feasibility")
        if preview.keys:
            for msg in snapshot.pool:msg.q.require(isolated_test=self.isolated_test,calibration_only=self.calibration_only)
            actual_M=np.asarray([msg.summary.composition for msg in snapshot.pool]).T
            actual_omega=actual_M@np.asarray(preview.alpha)
            if (not np.allclose(actual_M,np.asarray(preview.M),rtol=0,atol=1e-12) or
                    not np.allclose(actual_omega,preview.omega,rtol=0,atol=1e-12) or
                    abs(preview.ell-.5*np.abs(actual_omega-np.asarray(self.mu)).sum())>1e-12):
                raise InputError("preview mass/ell does not match actual input and weights")
        duration=self.now-self.window_open
        if preview.keys:
            # Backends validate all tensors and commit exactly once. State is
            # consumed only after a successful actual server update.
            variance=self.backend.apply(preview.keys,preview.alpha,self.settings.server_eta,self.model_version+1)
            self.debt=tuple(update_debt(np.asarray(self.debt),mu=np.asarray(self.mu),
                omega=np.asarray(preview.omega),eta=self.settings.server_eta))
            self.model_version+=1
            self.variance.update(variance)
            self.last_release=ReleaseSummary(self.now,preview.ell,preview.age,duration)
            for key in preview.keys:
                self.attempts[key].mature('consumed',self.now);self.consumed.add(key)
                self._event('consumed',key)
            self.pool.clear()
        record=dict(time=self.now,duration=duration,empty=not bool(preview.keys),
                    version=self.model_version,configured_design=int(self.config.design.enabled),
                    coverage_role='diagnostic_only',preview=preview.to_dict())
        self.closures.append(record)
        self.window_open=self.now;self.window_id+=1;self.revision+=1
        self._event('window_closed',empty=not bool(preview.keys))
        self.expire()
        if hasattr(self.backend,'sync_control_state'):self.backend.sync_control_state(self)
        return record

    def freeze_next_estimators(self, *, predictor, q_model):
        if self.now!=self.window_open:raise InputError("estimators may change only before the next window")
        if predictor.as_of>self.now or q_model.as_of>self.now or predictor.q_model!=q_model.to_dict():
            raise InputError("inconsistent/future next-window estimators")
        self._predictor=FrozenServiceModel.from_dict(predictor.to_dict())
        self._q_model=q_model_from_dict(q_model.to_dict());self.revision+=1

    def diagnostic(self, *, gate: int, state: str):
        if gate not in (0,1):raise InputError("invalid diagnostic Gate")
        self.diagnostics.append(dict(time=self.now,Gate=gate,state=state,
            configured_design=int(self.config.design.enabled),actual_design=int(self.config.design.enabled),
            role='diagnostic_only'))

    def mature_rows(self):
        return [r.to_dict() for r in self.attempts.values() if r.mature_label is not None]

    def finish_observation(self):
        for rec in self.attempts.values():rec.censor(self.now)

    def finish_finite_endpoint(self):
        """Only genuine T=100 termination supplies administrative nonconsumption."""
        if not self.calibration_only or self.now!=self.experiment_end:
            raise InputError('finite endpoint cannot be assigned to an interrupted prefix')
        if self.pool:self.apply_release(self.preview_release())
        for rec in self.attempts.values():
            if rec.consumed is None:rec.mature('horizon_unconsumed',self.now)
        self._event('administrative_endpoint',T=self.experiment_end)

    def to_dict(self):
        return dict(config=self.config.to_dict(),settings=asdict(self.settings),mu=self.mu,debt=self.debt,
            predictor=self.predictor.to_dict(),q_model=self.q_model.to_dict(),seed=self.seed,
            experiment_end=self.experiment_end,now=self.now,window_open=self.window_open,
            model_version=self.model_version,window_id=self.window_id,revision=self.revision,
            isolated_test=self.isolated_test,data_identity=self.data_identity,target_identity=self.target_identity,
            calibration_only=self.calibration_only,probability_applicability=self.probability_applicability,
            clock_namespace=self.clock_namespace,
            pool={k:asdict(v) for k,v in self.pool.items()},
            in_flight={k:asdict(v) for k,v in self.in_flight.items()},
            attempts={k:v.to_dict() for k,v in self.attempts.items()},
            private_stage1={k:asdict(v) for k,v in self.private_stage1.items()},
            consumed=sorted(self.consumed),last_release=asdict(self.last_release) if self.last_release else None,
            variance=self.variance,events=self.events,closures=self.closures,diagnostics=self.diagnostics,
            decisions=self.decisions,rng_state=self.rng_state,backend=self.backend.to_dict())

    @classmethod
    def from_dict(cls,obj,*,backend):
        obj=copy.deepcopy(obj)
        result=cls(config=ControlConfig.from_dict(obj['config']),settings=P2Settings(**obj['settings']),
            mu=obj['mu'],predictor=FrozenServiceModel.from_dict(obj['predictor']),
            q_model=q_model_from_dict(obj['q_model']),backend=backend,seed=obj['seed'],
            experiment_end=obj['experiment_end'],open_time=obj['window_open'],isolated_test=obj['isolated_test'],
            data_identity=obj['data_identity'],target_identity=obj['target_identity'],
            calibration_only=obj.get('calibration_only',False),probability_applicability=obj.get('probability_applicability'),
            clock_namespace=obj.get('clock_namespace'))
        for k in ('now','window_open','model_version','window_id','revision','events','closures','diagnostics','decisions','rng_state'):
            setattr(result,k,obj[k])
        result.debt=tuple(obj['debt']);result.variance=dict(obj['variance'])
        result.pool={k:delivered_from_dict(v) for k,v in obj['pool'].items()}
        result.in_flight={k:InFlight(Registration(**v['registration']),result_q(v['q'])) for k,v in obj['in_flight'].items()}
        result.attempts={k:AttemptRecord.from_dict(v) for k,v in obj['attempts'].items()}
        result.private_stage1={k:Stage1Summary.from_dict(v) for k,v in obj['private_stage1'].items()}
        result.consumed=set(obj['consumed'])
        result.last_release=ReleaseSummary(**obj['last_release']) if obj['last_release'] else None
        backend.restore(obj['backend'])
        result.snapshot()
        if any(result.attempts[m.key].consumed is not None for m in result.pool.values()):
            raise InputError("checkpoint pool already terminal")
        if not backend.has_version(result.model_version):raise InputError("checkpoint model version missing")
        return result


def result_q(obj):
    from raven_mcs.control.schema import QValue
    return QValue(**obj)
