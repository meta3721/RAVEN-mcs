"""Specific 44001 authorization, unchanged real Hájek trainer and tensor backend."""
from dataclasses import dataclass
import copy
import numpy as np
from raven_mcs.training.dynamic_control import FullRunnerBackend
from . import METHOD_VERSION
from .schema import DependencyPending,InputError,P2Settings
from .lifecycle import DynamicWindowRunner

@dataclass(frozen=True)
class DevelopmentAuthorization:
    source: str
    seed: int = 44001
    method: str = METHOD_VERSION
    role: str = 'development_activation_cost_only'
    max_steps: int = 5000
    def require(self):
        if (self.source!='user_20261013_RE_interval_v3_single_development' or self.seed!=44001 or
            self.method!=METHOD_VERSION or self.role!='development_activation_cost_only' or self.max_steps!=5000):
            raise DependencyPending('only the explicitly authorized 44001 revision development acquisition is allowed')

class DevelopmentBackend(FullRunnerBackend):
    def __init__(self,owner):
        super().__init__(owner)
        self.calibration_only=True;self.method_version=METHOD_VERSION
    def restore(self,obj):
        super().restore(obj)
        if self._lagged_owner is not None:
            # Live observation fitting changes only at a closed window and is
            # immediately frozen, so these are also the current live estimator.
            self.owner.obs_propensity=copy.deepcopy(self._lagged_owner.obs_propensity)
            self.owner.p_model_version=self._lagged_owner.p_model_version
    def start_local_training(self,key,observed_records,*,authorization):
        if not isinstance(authorization,DevelopmentAuthorization):raise DependencyPending('revision requires its own development authorization')
        authorization.require()
        if not getattr(self,'calibration_only',False) or self.owner.seed!=44001 or getattr(self,'method_version',None)!=METHOD_VERSION:
            raise DependencyPending('development authorization backend identity mismatch')
        if self.local_optimizer_steps+self.owner.local_steps>5000:raise DependencyPending('LOCAL_SGD_STEP_BUDGET_EXHAUSTED')
        work=self.work[key]
        if work['training_started'] or len(observed_records)!=len(work['positions']):raise InputError('training work alignment / repeated execution')
        state=self.owner._get_model_checkpoint(work['downloaded_version'])
        weights=np.asarray(work['weights'])[work['positions']]
        server_state=copy.deepcopy(self.owner.theta)
        try:
            update,loss=self.owner._trainer.train_step(model_state=state,observed_records=observed_records,
                a_bar_weights=weights,local_steps=self.owner.local_steps)
        finally:self.owner.model.load_state_dict(server_state)
        work['training_started']=True;self.local_optimizer_steps+=self.owner.local_steps
        return update,loss

def connect_development(owner,*,config,predictor,q_model,seed,experiment_end,open_time,
                        data_identity,target_identity,probability_applicability,clock_namespace):
    required=('uses_design_ratio','uses_observation_ipw','uses_usable_ipw','uses_hajek_local_loss',
        'uses_instant_calibration','uses_debt','uses_reference_penalty','uses_variance_penalty','uses_staleness_penalty')
    if owner.seed!=seed or seed!=44001 or config.method_version!=METHOD_VERSION:
        raise InputError('revision owner/config/seed identity mismatch')
    if owner.policy.design_control!='configured' or not all(getattr(owner.policy,k) for k in required):
        raise InputError('complete configured RAVEN required')
    if owner.design_configuration!=config.design or owner.clock.model_version!=0 or np.any(owner.debt) or owner.variance_count:
        raise InputError('fresh configured owner required')
    agg=owner.aggregator
    settings=P2Settings(lambda_group=agg.lambda_group,lambda_beta=agg.lambda_beta,lambda_variance=agg.lambda_variance,
        lambda_staleness=agg.lambda_staleness,alpha_max=agg.alpha_max,e_min=agg.e_min,server_eta=owner.eta,
        max_server_learning_rate=agg.max_server_learning_rate,d_max=owner.d_max,q_min=owner.q_min,v_floor=owner.v_floor)
    backend=DevelopmentBackend(owner);backend.calibration_only=True;backend.method_version=METHOD_VERSION
    runner=DynamicWindowRunner(config=config,settings=settings,mu=owner.mu,predictor=predictor,q_model=q_model,
        backend=backend,seed=seed,experiment_end=experiment_end,open_time=open_time,data_identity=data_identity,
        target_identity=target_identity,calibration_only=True,probability_applicability=probability_applicability,
        clock_namespace=clock_namespace)
    owner._dynamic_control_owner=True
    return runner
