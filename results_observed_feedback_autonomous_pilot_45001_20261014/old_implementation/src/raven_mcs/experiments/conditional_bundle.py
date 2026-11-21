"""Official dynamic session API. The caller supplies causal events, not a trace."""
from __future__ import annotations
from dataclasses import dataclass
import json
from pathlib import Path
import numpy as np

from raven_mcs.control.schema import ControlConfig, Stage1Summary, InputError
from raven_mcs.control.isolation import IsolatedController
from raven_mcs.control.persistence import initialize_control_run, save_checkpoint,restore_checkpoint
from raven_mcs.correction.stage1 import reconstruct_stage1
from raven_mcs.sag.r1l_design import apply_configured_design_zeta


@dataclass
class ConditionalBundleSession:
    owner: object
    runner: object
    controller: IsolatedController
    run_dir: Path | None = None

    def register_observations(self,registration,*,stratum_ids,p_pre_features,observation,group_ids,
                              metadata_as_of,provenance):
        """Uses the full runner's lagged zeta/p and shared reconstruction.

        Observation outcomes are actual at registration. Pre-O features and
        public strata must already be known; future labels are not accepted.
        Model observations/labels, if later used for local work, go directly to
        start_local_training, never to this controller snapshot.
        """
        if metadata_as_of>registration.registered_at or metadata_as_of>self.runner.window_open:
            raise InputError("metadata/estimator snapshot not available before this window")
        if len(stratum_ids)!=len(observation) or len(p_pre_features)!=len(observation):
            raise InputError("registration risk-set dimensions mismatch")
        allowed={'bias','hour_block','planned_workload_pre'}
        if any(set(row)-allowed for row in p_pre_features):
            raise InputError("unrecognized or post-observation feature")
        context=self.runner.backend.stage1_context()
        if self.runner.backend.stage1_as_of>metadata_as_of:
            raise InputError('stage1 snapshot is newer than declared available metadata')
        zeta_d=context._compute_zeta(registration.client,list(stratum_ids))
        ratio=apply_configured_design_zeta(zeta_d,int(self.runner.config.design.enabled))
        p=context._compute_p_hat(list(p_pre_features))
        stage=reconstruct_stage1(ratio,p,observation,group_ids,num_groups=self.owner.num_groups,
                                 a_max=context.a_max,p_min=context.p_min)
        summary=Stage1Summary(tuple(stage.groups),tuple(stage.weights),stage.effective_n,
            int(np.sum(observation)),self.runner.config.design.enabled,self.runner.config.design.source,
            registration.registered_at,f'lagged_p/{context.p_model_version}',tuple(ratio),tuple(p),provenance,
            tuple(int(i) for i in np.flatnonzero(observation)))
        return self.runner.on_register(registration,summary)

    def freeze_stage1_for_next_window(self,*,as_of):
        if self.runner.now!=self.runner.window_open or as_of>self.runner.window_open:
            raise InputError('stage1 estimators may change only before the next window')
        self.runner.backend.freeze_stage1_context(as_of)
        self.runner.revision+=1

    def decide(self):
        decision=self.controller.decide(self.runner.snapshot(),self.runner.predictor)
        from dataclasses import asdict
        self.runner.decisions.append(asdict(decision))
        return decision

    def close(self):
        return self.runner.apply_release(self.runner.preview_release())

    def save(self,name):
        if self.run_dir is None:raise InputError("session has no initialized output")
        return save_checkpoint(self.runner,self.run_dir,name=name,controller=self.controller)


def prepare_conditional_bundle(full_runner,*,config:ControlConfig,predictor,q_model,seed,experiment_end,
                               open_time,data_identity,target_identity,run_dir=None,repo_root=None,
                               isolated_test=False,stage1_as_of=None,calibration_only=False,
                               probability_applicability=None,clock_namespace=None):
    if stage1_as_of is None:
        if not isolated_test:raise InputError('explicit lagged stage1 as_of required')
        stage1_as_of=open_time
    if stage1_as_of>open_time:raise InputError('future stage1 estimator')
    runner=full_runner.build_dynamic_control(config=config,predictor=predictor,q_model=q_model,
        seed=seed,experiment_end=experiment_end,open_time=open_time,data_identity=data_identity,
        target_identity=target_identity,isolated_test=isolated_test,calibration_only=calibration_only,
        probability_applicability=probability_applicability,clock_namespace=clock_namespace)
    runner.backend.freeze_stage1_context(stage1_as_of)
    session=ConditionalBundleSession(full_runner,runner,IsolatedController(),Path(run_dir) if run_dir else None)
    if run_dir is not None:
        if repo_root is None:raise InputError("repository provenance required")
        initialize_control_run(runner,run_dir,repo_root=Path(repo_root))
    return session


def restore_conditional_bundle(full_runner,checkpoint,*,repo_root,expected_config,
                               expected_data_identity,expected_target_identity):
    """Restore the official session without writing an old result or replaying."""
    from raven_mcs.control.predictor import FrozenServiceModel
    from raven_mcs.control.probability import q_model_from_dict
    state=json.loads(Path(checkpoint).read_text(encoding='utf-8'))['state']
    provisional=full_runner.build_dynamic_control(config=expected_config,
        predictor=FrozenServiceModel.from_dict(state['predictor']),q_model=q_model_from_dict(state['q_model']),
        seed=state['seed'],experiment_end=state['experiment_end'],open_time=state['window_open'],
        data_identity=expected_data_identity,target_identity=expected_target_identity,
        isolated_test=state['isolated_test'],calibration_only=state.get('calibration_only',False),
        probability_applicability=state.get('probability_applicability'),clock_namespace=state.get('clock_namespace'))
    runner,accounting=restore_checkpoint(checkpoint,backend=provisional.backend,repo_root=repo_root,
        expected_config=expected_config,expected_data_identity=expected_data_identity,
        expected_target_identity=expected_target_identity)
    if runner.backend.stage1_as_of is None:
        raise InputError('official session checkpoint lacks frozen stage1 inputs')
    controller=IsolatedController()
    if accounting is not None:controller.accounting=accounting['accounting']
    return ConditionalBundleSession(full_runner,runner,controller,Path(checkpoint).parent)
