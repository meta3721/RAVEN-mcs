"""Production connection to FullWindowRunner's real model and ClientTrainer.

B0 prepares work and may apply supplied deterministic tensors in isolated
tests. Training requires a separate authorization and calibration readiness.
There is no EventTrace replay loop in this module.
"""
from __future__ import annotations

from dataclasses import dataclass,asdict
import copy
import numpy as np
import torch

from raven_mcs.control.schema import InputError, DependencyPending, P2Settings
from raven_mcs.control.lifecycle import DynamicWindowRunner
from raven_mcs.training.client import _flatten_params, unflatten_params


@dataclass(frozen=True)
class TrainingAuthorization:
    approved_stage: str
    source: str
    q_calibration_evidence: str

    def require(self):
        if self.approved_stage not in {'B1','P4','P5','P6','P7'} or not self.source or not self.q_calibration_evidence:
            raise DependencyPending("training needs separately approved stage and q calibration")


@dataclass(frozen=True)
class CalibrationAuthorization:
    source: str
    seed: int = 43001
    max_steps: int = 5000
    def require(self):
        if not self.source or self.seed!=43001 or self.max_steps!=5000:
            raise DependencyPending('only the first approved calibration acquisition is authorized')


class FullRunnerBackend:
    kind='full_window_runner_common_ndmf'

    def __init__(self,owner):
        self.owner=owner;self.work={};self.updates={};self.local_optimizer_steps=0
        self._lagged_owner=None;self.stage1_as_of=None

    def freeze_stage1_context(self,as_of):
        """Capture full-runner inputs before a window; never fit an estimator."""
        if not np.isfinite(as_of):raise InputError('invalid stage1 estimator time')
        if self.owner.obs_propensity is None:
            raise InputError('missing observation propensity; no constant substitution')
        context=copy.copy(self.owner)
        context.pi_target=copy.deepcopy(self.owner.pi_target)
        context.pi_opp_joint=copy.deepcopy(self.owner.pi_opp_joint)
        if not context.pi_opp_joint and self.owner.opportunity_estimator is not None:
            context.pi_opp_joint=dict(self.owner.opportunity_estimator.pi_hat())
        context.opportunity_estimator=None
        context.obs_propensity=copy.deepcopy(self.owner.obs_propensity)
        self._lagged_owner=context;self.stage1_as_of=float(as_of)

    def stage1_context(self):
        if self._lagged_owner is None:raise InputError('stage1 snapshot not frozen before window')
        return self._lagged_owner

    def _pack_stage1(self):
        if self._lagged_owner is None:return None
        context=self._lagged_owner
        observation=asdict(context.obs_propensity)
        for name in ('weights','_previous_weights'):
            value=observation[name]
            observation[name]=None if value is None else value.tolist()
        observation['history_x']=[x.tolist() for x in observation['history_x']]
        return dict(as_of=self.stage1_as_of,p_model_version=context.p_model_version,
            pi_target=[[a,b,v] for (a,b),v in sorted(context.pi_target.items())],
            pi_opp_joint=[[a,b,float(v)] for (a,b),v in sorted(context.pi_opp_joint.items())],
            observation=observation,pi_min=context.pi_min,p_min=context.p_min,a_max=context.a_max)

    def _restore_stage1(self,packet):
        if packet is None:self._lagged_owner=None;self.stage1_as_of=None;return
        from raven_mcs.propensity.observation import ObservationPropensity
        context=copy.copy(self.owner)
        context.pi_target={(a,b):v for a,b,v in packet['pi_target']}
        context.pi_opp_joint={(a,b):v for a,b,v in packet['pi_opp_joint']}
        context.opportunity_estimator=None
        obs=copy.deepcopy(packet['observation'])
        weights=obs.pop('weights');previous=obs.pop('_previous_weights')
        obs['feature_names']=tuple(obs['feature_names'])
        obs['history_x']=[np.asarray(x,dtype=float) for x in obs['history_x']]
        context.obs_propensity=ObservationPropensity(**obs)
        context.obs_propensity.weights=np.asarray(weights,dtype=float)
        context.obs_propensity._previous_weights=None if previous is None else np.asarray(previous,dtype=float)
        for name in ('p_model_version','pi_min','p_min','a_max'):setattr(context,name,packet[name])
        self._lagged_owner=context;self.stage1_as_of=packet['as_of']

    def has_version(self,version):return version in self.owner.model_versions

    def prepare_work(self,registration,summary):
        self.work[registration.key]=dict(downloaded_version=registration.downloaded_version,
            client=registration.client,weights=list(summary.local_weights),positions=list(summary.observed_positions),training_started=False)

    def start_local_training(self,key,observed_records,*,authorization):
        if not isinstance(authorization,(TrainingAuthorization,CalibrationAuthorization)):
            raise DependencyPending("local training is not approved in B0")
        authorization.require()
        if isinstance(authorization,CalibrationAuthorization):
            if not getattr(self,'calibration_only',False) or self.owner.seed!=authorization.seed:
                raise DependencyPending('calibration authorization cannot start production training')
            if self.local_optimizer_steps+self.owner.local_steps>authorization.max_steps:
                raise DependencyPending('LOCAL_SGD_STEP_BUDGET_EXHAUSTED')
        work=self.work[key]
        if work['training_started']:raise InputError("local work already started")
        if len(observed_records)!=len(work['positions']):raise InputError("observed record alignment mismatch")
        state=self.owner._get_model_checkpoint(work['downloaded_version'])
        weights=np.asarray(work['weights'])[work['positions']]
        server_state=copy.deepcopy(self.owner.theta)
        try:
            update,loss=self.owner._trainer.train_step(model_state=state,observed_records=observed_records,
                a_bar_weights=weights,local_steps=self.owner.local_steps)
        finally:
            self.owner.model.load_state_dict(server_state)
        work['training_started']=True
        self.local_optimizer_steps+=self.owner.local_steps
        return update,loss

    def complete(self,key,update):
        reference=_flatten_params(self.owner.theta)
        update=np.asarray(update,dtype=np.float64)
        if key not in self.work or update.shape!=reference.shape or not np.all(np.isfinite(update)):
            raise InputError("invalid/missing completed update")
        self.updates[key]=update.copy()

    def apply(self,keys,alpha,eta,new_version):
        if any(k not in self.updates for k in keys):raise InputError("actual completed tensor missing")
        theta=_flatten_params(self.owner.theta)
        for key,a in zip(keys,alpha):theta-=eta*a*self.updates[key]
        if not np.all(np.isfinite(theta)):raise InputError("nonfinite applied model")
        new_state=unflatten_params(theta,self.owner.theta)
        old_state=copy.deepcopy(self.owner.theta)
        try:self.owner.model.load_state_dict(new_state)
        except Exception:
            self.owner.model.load_state_dict(old_state);raise
        self.owner.theta=new_state
        self.owner.model_versions[new_version]=copy.deepcopy(new_state)
        # The full runner's actual variance estimator is updated only after
        # consumption. Forecasts use its lagged snapshot, with zero increment.
        updates_by_client={self.work[k]['client']:self.updates[k] for k in keys}
        self.owner._update_variance_state(updates_by_client,list(updates_by_client))
        for key in keys:self.updates.pop(key)
        return dict(self.owner.variance_state)

    def sync_control_state(self,dynamic):
        self.owner.debt=np.asarray(dynamic.debt).copy()
        self.owner.clock.model_version=dynamic.model_version
        self.owner.clock.current_window=dynamic.window_id
        self.owner.scale+=dynamic.settings.server_eta if dynamic.closures[-1]['empty'] is False else 0.
        if not dynamic.closures[-1]['empty']:
            self.owner.omega_sum+=dynamic.settings.server_eta*np.asarray(dynamic.closures[-1]['preview']['omega'])

    def to_dict(self):
        def pack(state):
            return {k:dict(shape=list(v.shape),dtype=str(v.dtype),values=v.detach().cpu().numpy().tolist()) for k,v in state.items()}
        return dict(kind=self.kind,model_class=type(self.owner.model).__name__,theta=pack(self.owner.theta),
            versions={str(k):pack(v) for k,v in self.owner.model_versions.items()},work=copy.deepcopy(self.work),
            updates={k:v.tolist() for k,v in self.updates.items()},local_optimizer_steps=self.local_optimizer_steps,
            variance_state=self.owner.variance_state,variance_count=self.owner.variance_count,
            variance_mean={k:v.tolist() for k,v in self.owner.variance_mean.items()},
            debt=self.owner.debt.tolist(),scale=self.owner.scale,omega_sum=self.owner.omega_sum.tolist(),
            clock=dict(model_version=self.owner.clock.model_version,current_window=self.owner.clock.current_window),
            stage1_context=self._pack_stage1(),
            local_training_config=dict(optimizer='existing_hajek_sgd',local_steps=self.owner.local_steps,
                learning_rate=self.owner._trainer.learning_rate))

    def restore(self,obj):
        if obj['kind']!=self.kind or obj['model_class']!=type(self.owner.model).__name__:
            raise InputError("production backend/model mismatch")
        expected=dict(optimizer='existing_hajek_sgd',local_steps=self.owner.local_steps,
                      learning_rate=self.owner._trainer.learning_rate)
        if obj['local_training_config']!=expected:raise InputError('checkpoint local training configuration mismatch')
        reference=self.owner.theta
        def unpack(state):
            if set(state)!=set(reference):raise InputError("checkpoint parameter keys mismatch")
            values={}
            for k,data in state.items():
                if list(reference[k].shape)!=data['shape'] or str(reference[k].dtype)!=data['dtype']:
                    raise InputError("checkpoint tensor structure mismatch")
                value=torch.tensor(data['values'],dtype=reference[k].dtype)
                if not bool(torch.isfinite(value).all()):raise InputError("checkpoint tensor invalid")
                values[k]=value
            return values
        theta=unpack(obj['theta']);versions={int(k):unpack(v) for k,v in obj['versions'].items()}
        self.owner.model.load_state_dict(theta);self.owner.theta=theta;self.owner.model_versions=versions
        self.work=copy.deepcopy(obj['work']);self.updates={k:np.asarray(v,dtype=float) for k,v in obj['updates'].items()}
        self.local_optimizer_steps=obj['local_optimizer_steps']
        self.owner.variance_state=dict(obj['variance_state']);self.owner.variance_count=dict(obj['variance_count'])
        self.owner.variance_mean={k:np.asarray(v,dtype=float) for k,v in obj['variance_mean'].items()}
        self.owner.debt=np.asarray(obj['debt']);self.owner.scale=obj['scale'];self.owner.omega_sum=np.asarray(obj['omega_sum'])
        for k,v in obj['clock'].items():setattr(self.owner.clock,k,v)
        self._restore_stage1(obj['stage1_context'])


def connect_full_runner(owner, *, config, predictor, q_model, seed, experiment_end, open_time,
                        data_identity,target_identity,isolated_test=False,calibration_only=False,
                        probability_applicability=None,clock_namespace=None):
    if owner.policy.design_control!='configured' or owner.policy.method_version!='configured-design-v1':
        raise InputError("dynamic control requires configured-design-v1, never legacy")
    required=('uses_design_ratio','uses_observation_ipw','uses_usable_ipw','uses_hajek_local_loss',
              'uses_instant_calibration','uses_debt','uses_reference_penalty','uses_variance_penalty','uses_staleness_penalty')
    if not all(getattr(owner.policy,key) for key in required):
        raise InputError("dynamic control requires the complete configured RAVEN method")
    if owner.design_configuration!=config.design:
        raise InputError("full and dynamic configured Design mismatch")
    if (owner.clock.model_version!=0 or np.any(owner.debt) or owner.variance_count):
        raise InputError('dynamic entry requires a fresh owner; resume from a dynamic checkpoint')
    agg=owner.aggregator
    settings=P2Settings(lambda_group=agg.lambda_group,lambda_beta=agg.lambda_beta,
        lambda_variance=agg.lambda_variance,lambda_staleness=agg.lambda_staleness,
        alpha_max=agg.alpha_max,e_min=agg.e_min,server_eta=owner.eta,
        max_server_learning_rate=agg.max_server_learning_rate,d_max=owner.d_max,q_min=owner.q_min,v_floor=owner.v_floor)
    backend=FullRunnerBackend(owner)
    backend.calibration_only=calibration_only
    result=DynamicWindowRunner(config=config,settings=settings,mu=owner.mu,predictor=predictor,
        q_model=q_model,backend=backend,seed=seed,experiment_end=experiment_end,open_time=open_time,
        data_identity=data_identity,target_identity=target_identity,isolated_test=isolated_test,
        calibration_only=calibration_only,probability_applicability=probability_applicability,clock_namespace=clock_namespace)
    owner._dynamic_control_owner=True
    return result
