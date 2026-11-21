"""Direct new-version session. Never calls old connect_full_runner."""
from dataclasses import dataclass
from pathlib import Path
import numpy as np
from .schema import Stage1Summary,InputError
from .isolation import IsolatedController
from .persistence import save_checkpoint
from .training_backend import connect_development
from raven_mcs.correction.stage1 import reconstruct_stage1
from raven_mcs.sag.r1l_design import apply_configured_design_zeta

@dataclass
class DevelopmentSession:
    owner: object
    runner: object
    controller: object
    run_dir: Path
    def register_observations(self,registration,*,stratum_ids,p_pre_features,observation,group_ids,metadata_as_of,provenance):
        if metadata_as_of>registration.registered_at or metadata_as_of>self.runner.window_open:
            raise InputError('future metadata / stage1 context')
        if len(stratum_ids)!=len(observation) or len(p_pre_features)!=len(observation):raise InputError('risk-set dimensions')
        if any(set(row)-{'bias','hour_block','planned_workload_pre'} for row in p_pre_features):raise InputError('post-observation feature')
        context=self.runner.backend.stage1_context()
        if self.runner.backend.stage1_as_of>metadata_as_of:raise InputError('stage1 availability mismatch')
        ratio=apply_configured_design_zeta(context._compute_zeta(registration.client,list(stratum_ids)),int(self.runner.config.design.enabled))
        p=context._compute_p_hat(list(p_pre_features))
        stage=reconstruct_stage1(ratio,p,observation,group_ids,num_groups=self.owner.num_groups,a_max=context.a_max,p_min=context.p_min)
        summary=Stage1Summary(tuple(stage.groups),tuple(stage.weights),stage.effective_n,int(np.sum(observation)),
            self.runner.config.design.enabled,self.runner.config.design.source,registration.registered_at,
            f'lagged_p/{context.p_model_version}',tuple(ratio),tuple(p),provenance,tuple(int(i) for i in np.flatnonzero(observation)))
        return self.runner.on_register(registration,summary)
    def freeze_stage1_for_next_window(self,*,as_of):
        if self.runner.now!=self.runner.window_open or as_of>self.runner.window_open:raise InputError('stage1 must freeze before next window')
        self.runner.backend.freeze_stage1_context(as_of);self.runner.revision+=1
    def close(self):return self.runner.apply_release(self.runner.preview_release())
    def save(self,name):
        path=self.run_dir/name;save_checkpoint(path,self.runner);return path

def prepare_development(owner,**kwargs):
    run_dir=Path(kwargs.pop('run_dir'));run_dir.mkdir(exist_ok=False)
    runner=connect_development(owner,**kwargs);runner.backend.freeze_stage1_context(kwargs['open_time'])
    return DevelopmentSession(owner,runner,IsolatedController(),run_dir)
