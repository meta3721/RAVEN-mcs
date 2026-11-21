"""Read-only real-prefix planner check; no training or trajectory advance."""
if __name__=='__main__':
    import json,time
    from pathlib import Path
    from raven_mcs.control.schema import DecisionSnapshot
    from raven_mcs.control.predictor import FrozenServiceModel
    from raven_mcs.control.isolation import IsolatedController
    from raven_mcs.control.lifecycle import DynamicWindowRunner
    from raven_mcs.experiments.calibration_first import load_inputs,owner_for
    from raven_mcs.experiments.conditional_bundle import restore_conditional_bundle
    from raven_mcs.control.schema import ControlConfig
    out=Path('results_calibration_first_20261013');path=out/'trajectory/FAILED_tick0201.json'
    obj=json.loads(path.read_text(encoding='utf-8'))['state'];inputs=load_inputs(Path.cwd(),out)
    owner=owner_for(inputs,ControlConfig.from_dict(obj['config']))
    session=restore_conditional_bundle(owner,path,repo_root=Path.cwd(),expected_config=ControlConfig.from_dict(obj['config']),
        expected_data_identity=inputs.data_id,expected_target_identity=inputs.target_id)
    before=session.runner.to_dict()
    decision=session.decide()
    from dataclasses import asdict
    result=dict(decision=asdict(decision),accounting=session.controller.accounting[-1],
        restored_now=session.runner.now,T_target=100.,SGD_executed=0,
        no_model_or_lifecycle_change=all(session.runner.to_dict()[k]==before[k] for k in before if k!='decisions'))
    (out/'PREFIX_PLANNER_CHECK.json').write_text(json.dumps(result,ensure_ascii=False,indent=2),encoding='utf-8')
    print(json.dumps(result,ensure_ascii=False))
