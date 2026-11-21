"""Causal current-pool runner, private registration work and fault quarantine."""
from dataclasses import asdict
import copy,json
import numpy as np
from . import METHOD_VERSION
from .schema import ControlConfig,P2Settings,InputError,DependencyPending,DecisionSnapshot,Registration,Stage1Summary,QValue,Delivered,InFlight,ReleaseSummary,delivered_from_dict
from .probability import AttemptRecord,RegistrationFeatures,q_model_from_dict,policy_context_hash
from .preview import P2Cache,P2NumericResult,bind_numeric,p2_dependency_hash
from raven_mcs.utils.hashing import sha256_json

class DynamicWindowRunner:
    def __init__(self,*,config,settings,mu,q_model,backend,seed,experiment_end=100.,open_time=0.,
                 isolated_test=False,data_identity,target_identity,probability_applicability=None,clock_namespace=None):
        if experiment_end!=100.:raise InputError('OF-v1 finite endpoint must be T100')
        if backend.kind=='isolated_array_backend' and not isolated_test:raise InputError('fixture backend forbidden in production')
        if not data_identity or not target_identity:raise InputError('data/target identity missing')
        self._config=ControlConfig.from_dict(config.to_dict());self.settings=settings;self.mu=tuple(float(x) for x in mu)
        self._q=q_model_from_dict(q_model.to_dict())
        if self._q.as_of>open_time:raise InputError('future q model')
        if self._q.to_dict()['kind']=='isolated_test' and not isolated_test:raise InputError('isolated q prohibited in production')
        self.probability_applicability=copy.deepcopy(probability_applicability)
        self.clock_namespace=copy.deepcopy(clock_namespace)
        if not self.probability_applicability or not self.clock_namespace:raise InputError('explicit q/clock applicability required')
        if self.probability_applicability.get('consumption_policy')!=METHOD_VERSION or self.probability_applicability.get('T')!=100:
            raise InputError('q policy/endpoint mismatch')
        if not isolated_test:
            required={'learning','service','stage1','data_identity','target_identity'}
            if not required.issubset(self.probability_applicability):raise DependencyPending('production q applicability incomplete')
            learning={'model','optimizer','local_steps','learning_rate','initial_model_hash','scaler','feature_schema'}
            if not learning.issubset(self.probability_applicability['learning']):raise DependencyPending('production learning applicability incomplete')
            if self.probability_applicability['data_identity']!=data_identity or self.probability_applicability['target_identity']!=target_identity:
                raise InputError('probability data/target identity mismatch')
        if not self.clock_namespace.get('run_id') or self.clock_namespace.get('unit')!='controlled_service_unit' or not self.clock_namespace.get('origin_utc'):
            raise InputError('run clock namespace missing')
        self.backend=backend;self.seed=seed;self.experiment_end=experiment_end;self.now=float(open_time);self.window_open=float(open_time)
        self.model_version=0;self.window_id=0;self.revision=0;self.isolated_test=isolated_test;self.calibration_only=False
        self.data_identity=data_identity;self.target_identity=target_identity
        self.debt=tuple(0. for _ in self.mu);self.variance={};self.last_release=None
        self.pool={};self.in_flight={};self.attempts={};self.private_stage1={};self.consumed=set()
        self.events=[];self.closures=[];self.decisions=[];self.diagnostics=[];self.fault=None;self.ended=False
        self.rng_state=dict(seed=seed,role='no_future_scenario_rng')
        self.cache=P2Cache();self.snapshot()
    @property
    def config(self):return self._config
    @property
    def q_model(self):return self._q
    def _healthy(self):
        if self.fault is not None:raise InputError('FAULT_QUARANTINED: no normal operation or checkpoint')
    def _event(self,kind,key=None,**extra):
        self.events.append(dict(time=self.now,kind=kind,key=key,window=self.window_id,model_version=self.model_version,**extra))
    def advance_time(self,now):
        self._healthy()
        if self.ended:raise InputError('finite endpoint already finished')
        if not np.isfinite(now) or now<self.now-1e-9 or now>100.+1e-9:raise InputError('invalid/nonmonotone clock')
        if now>min(self.window_open+4.,100.)+1e-9:raise InputError('MISSED_DEADLINE: process the closing grid before later events')
        if now>self.now:self.now=float(now);self.revision+=1
        self.expire()
    def service_parameter_identity(self):return sha256_json(self.probability_applicability.get('service',{}))
    def registration_features(self,reg):
        history=dict(debt=self.debt,variance=self.variance,last=asdict(self.last_release) if self.last_release else None,
            elapsed=self.now-self.window_open,pool=[asdict(m) for m in self.snapshot().pool],
            public_inflight=[asdict(m) for m in self.snapshot().in_flight])
        return RegistrationFeatures(self.model_version-reg.downloaded_version,reg.device_class,reg.network_class,
            max(0.,self.window_open+4-reg.registered_at),len(self.pool),len(self.in_flight),
            policy_context_hash(self.config,self.settings,self.mu,self.probability_applicability),reg.registered_at,
            sha256_json(history),json.dumps(history,sort_keys=True,allow_nan=False),self.clock_namespace['run_id'],self.service_parameter_identity())
    def on_register(self,registration,private_summary):
        self.advance_time(registration.registered_at)
        if registration.registered_at>=100.:raise InputError('registration outside [0,T)')
        if registration.key in self.attempts or registration.downloaded_version>self.model_version or not self.backend.has_version(registration.downloaded_version):
            raise InputError('duplicate key or unavailable/future model')
        if private_summary.frozen_at!=registration.registered_at or len(private_summary.masses)!=len(self.mu):raise InputError('registration stage1 clock/dimension mismatch')
        if private_summary.design_enabled!=self.config.design.enabled or private_summary.design_source!=self.config.design.source:raise InputError('stage1 configured Design mismatch')
        features=self.registration_features(registration);R=int(private_summary.total>0);E=int(features.model_age<=5)
        q=self.q_model.predict_at_registration(features) if R and E else QValue(0.,registration.registered_at,self.q_model.version,METHOD_VERSION,
            'outside_R' if not R else 'age_monotonicity','outside_R' if not R else 'structural_zero',sha256_json(asdict(features)))
        if q.frozen_at!=registration.registered_at or q.model_version!=self.q_model.version:raise InputError('registration q freeze mismatch')
        if q.role=='isolated_test_input' and not self.isolated_test:raise InputError('isolated q cannot register in production')
        self.backend.prepare_work(registration,private_summary)
        self.private_stage1[registration.key]=private_summary
        self.attempts[registration.key]=AttemptRecord(registration,features,q,R,E,sha256_json(asdict(private_summary)))
        self.in_flight[registration.key]=InFlight(registration,q,R,E);self.revision+=1
        self._event('registered',registration.key,R=R,E=E,q_role=q.role)
        if not R:
            self.attempts[registration.key].mature('no_observations',self.now);self.in_flight.pop(registration.key)
        self.expire();return q
    def start_local_training(self,key,observed_records,*,authorization):
        self._healthy()
        if key not in self.private_stage1 or not self.attempts[key].R:raise InputError('unregistered or R0 training attempt')
        if self.attempts[key].E:self.attempts[key].q.require(isolated_test=self.isolated_test)
        return self.backend.start_local_training(key,observed_records,authorization=authorization)
    def on_failure(self,key,now,*,reason):
        self.advance_time(now)
        if key not in self.attempts or reason not in {'compute_failure','network_failure'}:raise InputError('invalid failure notification')
        rec=self.attempts[key]
        if rec.physical_outcome!='pending':raise InputError('duplicate/conflicting physical notification')
        rec.physical_outcome=reason;self.in_flight.pop(key,None)
        if rec.consumed is None:rec.mature(reason,self.now)
        self.revision+=1;self._event('notified_failure',key,reason=reason)
    def on_completion(self,key,now,*,update):
        self.advance_time(now)
        if key not in self.attempts:raise InputError('unregistered completion')
        rec=self.attempts[key]
        if rec.physical_outcome!='pending':raise InputError('duplicate/conflicting completion')
        if sha256_json(asdict(self.private_stage1[key]))!=rec.stage1_hash:raise InputError('REGISTRATION_STAGE1_CHANGED')
        self.backend.complete(key,update);rec.physical_outcome='completion';rec.completed_at=self.now;self.in_flight.pop(key,None)
        self.revision+=1;self._event('physically_completed',key)
        if rec.consumed is not None:return
        reg=rec.registration
        if not rec.R or not rec.E or self.model_version-reg.downloaded_version>5:
            rec.mature('expired',self.now);return
        summary=self.private_stage1[key]
        if summary.frozen_at!=reg.registered_at:raise InputError('private registration payload changed clock')
        previous=self.pool.get(reg.client)
        if previous and (previous.registration.registered_at,previous.key)>(reg.registered_at,key):rec.mature('superseded',self.now);return
        if previous:self.attempts[previous.key].mature('superseded',self.now)
        self.pool[reg.client]=Delivered(reg,summary,rec.q,self.now);rec.accepted_at=self.now;self._event('accepted',key)
    def expire(self):
        self._healthy()
        for cid,msg in list(self.pool.items()):
            if self.model_version-msg.registration.downloaded_version>5:
                self.pool.pop(cid);self.attempts[msg.key].mature('expired',self.now);self.revision+=1;self._event('expired',msg.key)
        for key,msg in list(self.in_flight.items()):
            if self.model_version-msg.registration.downloaded_version>5:
                self.in_flight.pop(key)
                if self.attempts[key].consumed is None:self.attempts[key].mature('expired',self.now)
                self.revision+=1;self._event('expired_inflight',key)
    def snapshot(self):
        self._healthy()
        return DecisionSnapshot(self.now,self.window_open,self.model_version,self.revision,self.config,self.settings,self.mu,self.debt,
            tuple(sorted(self.pool.values(),key=lambda m:m.registration.client)),tuple(self.in_flight[k] for k in sorted(self.in_flight)),
            self.last_release,tuple(sorted(self.variance.items())),self.seed,100.,self.isolated_test,False,
            copy.deepcopy(self.probability_applicability),copy.deepcopy(self.clock_namespace),self.service_parameter_identity(),self.q_model.version)
    def preview_release(self,*,use_cache=True):
        s=self.snapshot()
        if not s.pool:
            numeric=P2NumericResult(p2_dependency_hash(s),(),(),(),(),tuple(() for _ in s.mu),tuple(0. for _ in s.mu),1.,0.,json.dumps(dict(status='empty_no_release')))
            return bind_numeric(s,numeric)
        return self.cache.get(s,use_cache=use_cache)
    def apply_release(self,preview,*,reason='EXPLICIT_INTERFACE_COMMIT'):
        self._healthy();s=self.snapshot()
        if preview.fingerprint!=s.fingerprint:raise InputError('STALE_PREVIEW')
        if preview.dependency_hash!=p2_dependency_hash(s):raise InputError('P2_DEPENDENCY_CHANGED')
        keys=tuple(m.key for m in s.pool)
        if keys!=preview.keys or set(keys)&self.consumed:raise InputError('duplicate consumption or key mismatch')
        if self.now==100 and self.window_open==100:raise InputError('terminal window already closed')
        if keys:
            from .preview import residual
            if residual(preview.alpha,self.settings)>1e-7:raise InputError('applied weight feasibility')
            M=np.asarray([m.summary.composition for m in s.pool]).T;omega=M@np.asarray(preview.alpha)
            for msg in s.pool:msg.q.require(isolated_test=self.isolated_test)
            if not np.allclose(M,preview.M,rtol=0,atol=1e-12) or not np.allclose(omega,preview.omega,rtol=0,atol=1e-12) or abs(preview.ell-.5*np.abs(omega-np.asarray(self.mu)).sum())>1e-12:
                raise InputError('actual P2 payload mismatch')
        duration=self.now-self.window_open
        phase='backend_apply'
        try:
            if keys:
                from raven_mcs.aggregation.debt import update_debt
                variance=self.backend.apply(keys,preview.alpha,.01,self.model_version+1)
                phase='lifecycle_commit'
                self.debt=tuple(float(x) for x in update_debt(np.asarray(self.debt),mu=np.asarray(self.mu),omega=np.asarray(preview.omega),eta=.01))
                self.model_version+=1;self.variance.update(variance)
                self.last_release=ReleaseSummary(self.now,preview.ell,preview.age,duration,tuple(preview.omega))
                for key in keys:self.attempts[key].mature('consumed',self.now);self.consumed.add(key)
                self.pool.clear()
            record=dict(time=self.now,duration=duration,empty=not bool(keys),version=self.model_version,reason=reason,
                configured_design=int(self.config.design.enabled),actual_design=int(self.config.design.enabled),coverage_role='diagnostic_only',preview=preview.to_dict())
            self.closures.append(record);self.window_open=self.now;self.window_id+=1;self.revision+=1
            self.expire();phase='backend_control_sync'
            if hasattr(self.backend,'sync_control_state'):self.backend.sync_control_state(self)
            self._event('window_closed',empty=not bool(keys))
            return record
        except Exception as exc:
            self.fault=dict(time=self.now,phase=phase,error=repr(exc),state='UNCOMMITTED_OR_PARTIAL_MODEL_QUARANTINED')
            self._event('transaction_fault',phase=phase);raise
    def diagnostic(self,*,gate,state):
        self._healthy()
        if gate not in (0,1):raise InputError('invalid diagnostic Gate')
        self.diagnostics.append(dict(time=self.now,Gate=gate,state=state,configured_design=int(self.config.design.enabled),actual_design=int(self.config.design.enabled),role='diagnostic_only'))
    def freeze_next_q(self,q_model):
        self._healthy()
        if self.now!=self.window_open or q_model.as_of>self.now:raise InputError('q may change only at next window boundary')
        model=q_model_from_dict(q_model.to_dict())
        if model.to_dict()['kind']=='isolated_test' and not self.isolated_test:raise InputError('isolated q in production')
        self._q=model;self.revision+=1
    def finish_observation(self):
        for rec in self.attempts.values():rec.censor(self.now)
    def finish_finite_endpoint(self):
        self._healthy()
        if self.now!=100. or self.ended:raise InputError('cannot assign full endpoint to prefix or twice')
        if self.window_open<100:self.apply_release(self.preview_release(),reason='TERMINAL')
        for rec in self.attempts.values():
            if rec.consumed is None:rec.mature('horizon_unconsumed',self.now)
        self.ended=True;self._event('administrative_endpoint',T=100.)
    def on_grid(self,now,controller):
        self.advance_time(now);decision=controller.decide(self);self.decisions.append(decision.to_dict())
        if decision.action=='CLOSE' and self.window_open<now:self.apply_release(decision.preview or self.preview_release(),reason=decision.reason)
        if now==100:self.finish_finite_endpoint()
        return decision
    def to_dict(self):
        return dict(method=METHOD_VERSION,config=self.config.to_dict(),settings=asdict(self.settings),mu=self.mu,debt=self.debt,
            q_model=self.q_model.to_dict(),seed=self.seed,experiment_end=100.,now=self.now,window_open=self.window_open,
            model_version=self.model_version,window_id=self.window_id,revision=self.revision,isolated_test=self.isolated_test,
            data_identity=self.data_identity,target_identity=self.target_identity,probability_applicability=self.probability_applicability,
            clock_namespace=self.clock_namespace,pool={k:asdict(v) for k,v in self.pool.items()},in_flight={k:asdict(v) for k,v in self.in_flight.items()},
            attempts={k:v.to_dict() for k,v in self.attempts.items()},private_stage1={k:asdict(v) for k,v in self.private_stage1.items()},
            consumed=sorted(self.consumed),last_release=asdict(self.last_release) if self.last_release else None,variance=self.variance,
            events=self.events,closures=self.closures,decisions=self.decisions,diagnostics=self.diagnostics,rng_state=self.rng_state,
            backend=self.backend.to_dict(),fault=self.fault,ended=self.ended)
    def checkpoint_state(self):
        self._healthy()
        if any(sha256_json(asdict(self.private_stage1[k]))!=rec.stage1_hash for k,rec in self.attempts.items()):raise InputError('REGISTRATION_STAGE1_CHANGED')
        return self.to_dict()
    @classmethod
    def from_dict(cls,obj,*,backend):
        obj=copy.deepcopy(obj)
        if obj.get('method')!=METHOD_VERSION or obj.get('fault'):raise InputError('checkpoint method/fault mismatch')
        r=cls(config=ControlConfig.from_dict(obj['config']),settings=P2Settings(**obj['settings']),mu=obj['mu'],
            q_model=q_model_from_dict(obj['q_model']),backend=backend,seed=obj['seed'],open_time=obj['window_open'],
            isolated_test=obj['isolated_test'],data_identity=obj['data_identity'],target_identity=obj['target_identity'],
            probability_applicability=obj['probability_applicability'],clock_namespace=obj['clock_namespace'])
        for name in ('now','window_open','model_version','window_id','revision','variance','events','closures','decisions','diagnostics','rng_state','ended'):setattr(r,name,obj[name])
        r.debt=tuple(obj['debt']);r.pool={k:delivered_from_dict(v) for k,v in obj['pool'].items()}
        r.in_flight={k:InFlight(Registration(**v['registration']),QValue(**v['q']),v['R'],v['E']) for k,v in obj['in_flight'].items()}
        r.attempts={k:AttemptRecord.from_dict(v) for k,v in obj['attempts'].items()};r.private_stage1={k:Stage1Summary.from_dict(v) for k,v in obj['private_stage1'].items()}
        r.consumed=set(obj['consumed']);r.last_release=ReleaseSummary(**dict(obj['last_release'],omega=tuple(obj['last_release']['omega']))) if obj['last_release'] else None
        backend.restore(obj['backend']);r.snapshot()
        r.checkpoint_state()
        if not backend.has_version(r.model_version) or any(r.attempts[m.key].consumed is not None for m in r.pool.values()):raise InputError('restored lifecycle/model inconsistent')
        return r
