"""The one authorized integration check, deterministic and zero SGD."""
from dataclasses import replace,asdict
import json
import sys
import numpy as np
import torch
from re_interval_development_budget import ROOT,OUT
from raven_mcs_re_interval.development_acquisition import build_session,SOURCE
from raven_mcs_re_interval.training_backend import DevelopmentAuthorization,DevelopmentBackend
from raven_mcs_re_interval.schema import Registration,InputError
from raven_mcs_re_interval.lifecycle import DynamicWindowRunner
from raven_mcs_re_interval.persistence import restore_checkpoint
from raven_mcs_re_interval.probability import DiagnosticPriorQ
from raven_mcs.control.persistence import exclusive_json,source_inventory
from raven_mcs.training.dynamic_control import CalibrationAuthorization
from raven_mcs.training.client import ClientTrainer,_flatten_params
from raven_mcs.utils.hashing import sha256_json

def rejects(fn):
    try:fn()
    except Exception:return True
    raise AssertionError('expected explicit rejection')

if __name__=='__main__':
    torch.set_num_threads(1);torch.set_num_interop_threads(1)
    tag=sys.argv[1] if len(sys.argv)>1 else ''
    i,s=build_session(ROOT,OUT,integration=True,integration_tag=tag);r=s.runner
    assert type(r) is DynamicWindowRunner and type(r.backend) is DevelopmentBackend
    assert isinstance(s.owner._trainer,ClientTrainer) and s.owner.seed==44001
    DevelopmentAuthorization(SOURCE).require()
    rejects(lambda:CalibrationAuthorization(SOURCE,seed=44001).require())
    rejects(lambda:DevelopmentAuthorization(SOURCE,seed=43001).require())
    rejects(lambda:DevelopmentAuthorization(SOURCE,role='formal').require())
    # No training and no RNG service draw: prepare real stage1 and actual tensor
    # submission plumbing using deterministic zero tensors, integration only.
    cid=i.clients[0];st=i.strata[cid][0];gid=i.meta[i.pools[(cid,st)][0]]['group']
    for key,flag in [('R1',1),('R0',0)]:
        s.register_observations(Registration(key,cid,0.,0,'tier-0','net-tier-0'),stratum_ids=[st],
            p_pre_features=[dict(bias=1.,hour_block=0.,planned_workload_pre=1.)],observation=[flag],group_ids=[gid],
            metadata_as_of=0.,provenance='deterministic_entry_integration_NO_TRAINING')
    assert r.attempts['R1'].q.role=='diagnostic_prior' and r.attempts['R0'].q.role=='outside_R'
    assert r.backend.work['R1']['positions']==[0] and r.backend.work['R0']['positions']==[]
    rejects(lambda:r.attempts['R0'].q.require(isolated_test=False,calibration_only=True))
    rejects(lambda:r.attempts['R1'].q.require(isolated_test=False,calibration_only=False))
    # Structural age-zero record: deterministic checkpoint versions, no optimizer.
    for v in range(1,7):s.owner.model_versions[v]={k:t.clone() for k,t in s.owner.theta.items()}
    r.model_version=6;s.owner.clock.model_version=6;r.expire()
    s.register_observations(Registration('E0',cid,0.,0,'tier-0','net-tier-0'),stratum_ids=[st],
        p_pre_features=[dict(bias=1.,hour_block=0.,planned_workload_pre=1.)],observation=[1],group_ids=[gid],
        metadata_as_of=0.,provenance='deterministic_entry_integration_NO_TRAINING')
    assert r.attempts['E0'].q.role=='structural_zero' and 'E0' in r.backend.work
    # Verify exact trainer argument forwarding while intercepting before SGD.
    calls=[];original=s.owner._trainer.train_step
    def intercept(**kwargs):calls.append(dict(weights=kwargs['a_bar_weights'].tolist(),steps=kwargs['local_steps']));raise RuntimeError('NO_SGD_IN_INTEGRATION')
    s.owner._trainer.train_step=intercept
    rejects(lambda:r.start_local_training('E0',[{}],authorization=DevelopmentAuthorization(SOURCE)))
    s.owner._trainer.train_step=original
    assert len(calls)==1 and calls[0]['steps']==1 and r.backend.local_optimizer_steps==0
    # Real tensor backend accepts/completes/consumes a current eligible message.
    s.register_observations(Registration('current',cid,0.,6,'tier-0','net-tier-0'),stratum_ids=[st],
        p_pre_features=[dict(bias=1.,hour_block=0.,planned_workload_pre=1.)],observation=[1],group_ids=[gid],
        metadata_as_of=0.,provenance='deterministic_entry_integration_NO_TRAINING')
    r.on_completion('current',0.,update=np.zeros_like(_flatten_params(s.owner.theta)))
    before=sha256_json(r.to_dict());preview=r.preview_release();assert sha256_json(r.to_dict())==before
    s.close();assert r.attempts['current'].consumed==1
    path=s.save('ENTRY_CHECKPOINT.json')
    restored=restore_checkpoint(path,backend=DevelopmentBackend(s.owner))
    assert sha256_json(restored.to_dict())==sha256_json(r.to_dict())
    assert restored.backend.calibration_only and restored.backend.method_version==r.config.method_version
    assert sha256_json(asdict(restored.backend.owner.obs_propensity))==sha256_json(asdict(restored.backend.stage1_context().obs_propensity))
    assert r.backend.local_optimizer_steps==0
    old=json.loads((ROOT/'results_calibration_first_20261013/trajectory/SOURCE_CLOSURE.json').read_text())
    assert old==source_inventory(ROOT)
    exclusive_json(OUT/('ENTRY_INTEGRATION_PASS'+tag+'.json'),dict(status='PASS',SGD=0,synthetic_or_real_replay=0,
        new_runner_type=type(r).__module__,new_controller_type=type(s.controller).__module__,backend_type=type(r.backend).__module__,
        real_trainer_type=type(s.owner._trainer).__module__,authorization=asdict(DevelopmentAuthorization(SOURCE)),
        original_43001_guard_preserved=True,TRAIN_reader_only=True,R0_role='outside_R',E0_role='structural_zero',
        intercept_at_real_trainer_before_SGD=calls,diagnostic_prior_production_rejected=True,save_restore_identical=True,
        actual_tensor_submission_consumed=True,old_source_closure_unchanged=True))
    print('ENTRY_INTEGRATION_PASS; zero SGD, one deterministic integration check')
