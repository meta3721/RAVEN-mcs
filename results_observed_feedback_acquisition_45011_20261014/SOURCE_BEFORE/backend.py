"""OF-v1 adapter to actual CommonNDMF/ClientTrainer; no training approval here."""
from dataclasses import dataclass
from .schema import InputError,DependencyPending,P2Settings
from .lifecycle import DynamicWindowRunner
from . import METHOD_VERSION

@dataclass(frozen=True)
class FutureTrainingAuthorization:
    approved_stage:str
    source:str
    calibrated_q_evidence:str
    policy_version:str=METHOD_VERSION
    def require(self):
        if self.policy_version!=METHOD_VERSION or self.approved_stage not in {'P4','P5','P6','P7'} or not self.source or not self.calibrated_q_evidence:
            raise DependencyPending('OF-v1 training requires a separate approved stage and calibrated q')

def connect_full_runner(owner,*,config,q_model,seed,data_identity,target_identity,probability_applicability,clock_namespace,isolated_test=False,open_time=0.):
    # Imported only when the real backend is connected; never a fake predictor.
    from raven_mcs.training.dynamic_control import FullRunnerBackend,TrainingAuthorization
    class Adapter(FullRunnerBackend):
        def start_local_training(self,key,observed_records,*,authorization):
            if not isinstance(authorization,FutureTrainingAuthorization):raise DependencyPending('OF-v1 limited implementation has no SGD authorization')
            authorization.require()
            if self.isolated_input or q_model.to_dict()['kind']!='evidence_table':raise DependencyPending('full training requires production q evidence')
            return super().start_local_training(key,observed_records,authorization=TrainingAuthorization(authorization.approved_stage,authorization.source,authorization.calibrated_q_evidence))
        def to_dict(self):
            import torch,numpy as np,random
            value=super().to_dict();state=np.random.get_state()
            value.update(adapter_policy=METHOD_VERSION,torch_rng=torch.get_rng_state().tolist(),python_rng=random.getstate(),
                numpy_rng=[state[0],state[1].tolist(),state[2],state[3],state[4]],model_training=self.owner.model.training,
                optimizer_state='stateless_hajek_sgd_no_persistent_optimizer_slots')
            return value
        def restore(self,obj):
            import torch,numpy as np,random
            if obj.get('adapter_policy')!=METHOD_VERSION:raise InputError('backend adapter method mismatch')
            super().restore(obj)
            def tuple_tree(x):return tuple(tuple_tree(v) for v in x) if isinstance(x,(tuple,list)) else x
            torch.set_rng_state(torch.tensor(obj['torch_rng'],dtype=torch.uint8));random.setstate(tuple_tree(obj['python_rng']))
            nr=obj['numpy_rng'];np.random.set_state((nr[0],np.asarray(nr[1],dtype=np.uint32),nr[2],nr[3],nr[4]))
            self.owner.model.train(obj['model_training'])
        def _restore_stage1(self,packet):
            super()._restore_stage1(packet)
            if packet is not None and packet['observation']['weights'] is None:self._lagged_owner.obs_propensity.weights=None
    if owner.policy.design_control!='configured' or owner.policy.method_version!='configured-design-v1':raise InputError('legacy full backend not allowed')
    required=('uses_design_ratio','uses_observation_ipw','uses_usable_ipw','uses_hajek_local_loss','uses_instant_calibration',
        'uses_debt','uses_reference_penalty','uses_variance_penalty','uses_staleness_penalty')
    if not all(getattr(owner.policy,x) for x in required) or owner.design_configuration.to_dict()!=config.design.to_dict():raise InputError('complete configured aggregation identity required')
    if owner.clock.model_version or owner.variance_count or any(owner.debt):raise InputError('fresh owner required; use OF checkpoint for resume')
    agg=owner.aggregator
    settings=P2Settings(lambda_group=agg.lambda_group,lambda_beta=agg.lambda_beta,lambda_variance=agg.lambda_variance,
        lambda_staleness=agg.lambda_staleness,alpha_max=agg.alpha_max,e_min=agg.e_min,server_eta=owner.eta,
        max_server_learning_rate=agg.max_server_learning_rate,d_max=owner.d_max,q_min=owner.q_min,v_floor=owner.v_floor)
    backend=Adapter(owner);backend.isolated_input=isolated_test
    runner=DynamicWindowRunner(config=config,settings=settings,mu=owner.mu,q_model=q_model,backend=backend,seed=seed,
        open_time=open_time,isolated_test=isolated_test,data_identity=data_identity,target_identity=target_identity,
        probability_applicability=probability_applicability,clock_namespace=clock_namespace)
    owner._dynamic_control_owner=True
    return runner
