"""Compare the pre-edit runner snapshot with explicit legacy, same inputs and RNG."""
from pathlib import Path
import importlib.util
import sys
import json
import random
import numpy as np
import torch
from unittest.mock import patch

ROOT=Path(__file__).resolve().parents[1]
sys.path.insert(0,str(ROOT/'src'))
OUT=Path(__file__).resolve().parent


def load(name,path):
    spec=importlib.util.spec_from_file_location(name,path)
    module=importlib.util.module_from_spec(spec)
    sys.modules[name]=module
    spec.loader.exec_module(module)
    return module


def main():
    helpers=load('alignment_fixture',ROOT/'tests/integration/test_configured_design_runner.py')
    class Factory:
        def mktemp(self,name):
            p=OUT/('parity_'+name)
            p.mkdir(exist_ok=True)
            return p
    context=helpers.context.__wrapped__(Factory())
    before=load('raven_before_alignment',OUT/'before/src/raven_mcs/training/window_runner.py')
    results=[]
    for gate in (0,1):
        current=helpers.make_runner(context,legacy=True)
        old=before.FullWindowRunner(trace=current.trace,dataset=current.dataset,
            model=helpers.deterministic_common_ndmf(current.dataset.num_spatial,seed=26001),
            aggregator=helpers.ObservedRaven(),policy=current.policy,mu=current.mu,
            num_groups=current.num_groups,pi_target=current.pi_target,
            pi_opp_joint=current.pi_opp_joint,local_steps=1)
        state=torch.get_rng_state(),np.random.get_state(),random.getstate()
        with patch.object(before,'compute_certificates',side_effect=helpers.diagnostic(gate)):
            om=old._process_window(0,old.trace.events)
        torch.set_rng_state(state[0]);np.random.set_state(state[1]);random.setstate(state[2])
        with patch('raven_mcs.training.window_runner.compute_certificates',side_effect=helpers.diagnostic(gate)):
            nm=current._process_window(0,current.trace.events)
        assert om.theta_hash_after==nm.theta_hash_after, (om.theta_hash_after,nm.theta_hash_after)
        assert om.alpha==nm.alpha
        for a,b in zip(old.diagnostics,current.diagnostics):
            for key in ('zeta_hat','applied_local_weights','beta_hat','alpha','update_vector_hash'):
                assert a[key]==b[key],key
        op,np_=old.aggregator.payloads[0],current.aggregator.payloads[0]
        for key in ('total_masses','compositions','beta_hat','debt','variance_diag'):
            np.testing.assert_array_equal(getattr(op,key),getattr(np_,key))
        results.append(dict(gate=gate,exact_theta_hash_parity=True,theta_hash=nm.theta_hash_after,
            weight_reference_solver_parity=True,shared_RNG_restored=True))
    (OUT/'LEGACY_BEFORE_AFTER_PARITY.json').write_text(json.dumps(results,indent=2),encoding='utf-8')
    print(json.dumps(results))


if __name__=='__main__':
    main()
