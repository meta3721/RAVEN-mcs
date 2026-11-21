"""No-overwrite manifests/checkpoints for the production dynamic entry."""
from __future__ import annotations

from dataclasses import asdict
import json
import os
from pathlib import Path

from raven_mcs.control import METHOD_VERSION
from raven_mcs.control.lifecycle import DynamicWindowRunner
from raven_mcs.control.schema import InputError
from raven_mcs.utils.hashing import sha256_file, sha256_json, is_sha256
from raven_mcs.utils.manifest import build_manifest, write_manifest, write_resolved_config
from raven_mcs.utils.seed import SeedBundle


def computational_sources(repo_root: Path):
    """Explicit full packages used by control/model/training plus infrastructure.

    Including the packages rather than a hand-picked solver file covers import
    dependencies, while avoiding historical datasets/models and result trees.
    """
    root=Path(repo_root)/'src/raven_mcs'
    # FullWindowRunner imports additional metric/experiment helpers. Freeze the
    # entire source package to avoid omitting a transitive computational input.
    paths=set(root.rglob('*.py'))
    paths.add(Path(repo_root)/'configs/control/conditional_bundle_v2.json')
    paths.add(Path(repo_root)/'configs/config.yaml')
    return tuple(sorted(paths,key=lambda p:str(p)))


def source_inventory(repo_root):
    return {str(p.relative_to(repo_root).as_posix()):sha256_file(p) for p in computational_sources(repo_root)}


def exclusive_json(path,obj):
    path=Path(path)
    data=json.dumps(obj,ensure_ascii=False,sort_keys=True,indent=2,allow_nan=False)
    # Exclusive creation preserves every previous checkpoint/result. Partial
    # files on write failure remain evidence and fail JSON/hash validation.
    with path.open('x',encoding='utf-8') as f:
        f.write(data);f.flush();os.fsync(f.fileno())


def initialize_control_run(runner,run_dir,*,repo_root):
    run_dir=Path(run_dir);repo_root=Path(repo_root).resolve()
    if run_dir.exists():raise InputError("output directory exists; refusing overwrite")
    if not is_sha256(runner.data_identity) or not is_sha256(runner.target_identity):
        raise InputError("real data/target content identities required")
    config=dict(experiment='conditional_bundle_control',dataset='explicit_data_identity',
        method=METHOD_VERSION,scenario='isolated_deterministic_B0' if runner.isolated_test else 'dynamic_production',
        seed=runner.seed,device='cpu',solver=dict(backend='CLARABEL'),control=runner.config.to_dict(),
        settings=asdict(runner.settings),mu=list(runner.mu),target_identity=runner.target_identity,
        training_executed=False,q_status='DEPENDENCY_PENDING' if runner.q_model.version=='q-calibration-pending' else 'EVIDENCE_REQUIRED',
        evidence_role='B0_interface_only' if runner.isolated_test else 'unvalidated_dynamic_entry')
    if runner.calibration_only:
        config.update(scenario='calibration_only/pi_boot',evidence_role='first_fit_acquisition_cost_interface_only',
            q_status='DIAGNOSTIC_PRIOR_NOT_CALIBRATED',probability_applicability=runner.probability_applicability,
            clock_namespace=runner.clock_namespace,experiment_end=runner.experiment_end)
    sources=computational_sources(repo_root)
    manifest=build_manifest(run_id=run_dir.name,config=config,
        seed_bundle=SeedBundle.from_config(runner.seed,None),data_hash=runner.data_identity,
        event_trace_hash=sha256_json({'dynamic_events_at_save':runner.events,'scope':'current_visible_only'}),
        repo_root=repo_root,require_git=True,source_paths=sources)
    inventory=source_inventory(repo_root)
    run_dir.mkdir(parents=True,exist_ok=False)
    write_manifest(manifest,run_dir);write_resolved_config(config,run_dir)
    exclusive_json(run_dir/'SOURCE_CLOSURE.json',inventory)
    exclusive_json(run_dir/'METHOD_IDENTITY.json',dict(method=METHOD_VERSION,base_method='raven_mcs/configured-design-v1',
        configured_design=int(runner.config.design.enabled),coverage_role='diagnostic_only',
        status='CALIBRATION_ONLY_DIAGNOSTIC_PRIOR' if runner.calibration_only else ('ISOLATED_TEST_ONLY' if runner.isolated_test else 'IMPLEMENTATION_READY_PENDING_CALIBRATION'),
        calibration_only=runner.calibration_only,clock_namespace=runner.clock_namespace,
        probability_applicability=runner.probability_applicability,
        results='RESULTS_NOT_REVALIDATED',q_registration_freeze=True,source_scope=manifest.git_state_scope))
    return manifest


def save_checkpoint(runner,run_dir,*,name,controller=None):
    run_dir=Path(run_dir)
    if not (run_dir/'manifest.json').is_file():raise InputError("production manifest required before checkpoint")
    if Path(name).name!=name or not name.endswith('.json'):raise InputError("checkpoint must be a local .json name")
    state=runner.to_dict()
    packet=dict(schema='conditional_bundle_checkpoint_v1',method=METHOD_VERSION,state=state,
        state_hash=sha256_json(state),source_closure=json.loads((run_dir/'SOURCE_CLOSURE.json').read_text(encoding='utf-8')),
        controller=controller.to_dict() if controller is not None else None)
    exclusive_json(run_dir/name,packet)
    return run_dir/name


def restore_checkpoint(path,*,backend,repo_root,expected_config=None,expected_data_identity=None,expected_target_identity=None):
    packet=json.loads(Path(path).read_text(encoding='utf-8'))
    if packet['method']!=METHOD_VERSION or packet['schema']!='conditional_bundle_checkpoint_v1':
        raise InputError("checkpoint method/schema mismatch")
    if packet['state_hash']!=sha256_json(packet['state']):raise InputError("checkpoint content mismatch")
    if packet['source_closure']!=source_inventory(Path(repo_root).resolve()):
        raise InputError("checkpoint computational source changed")
    state=packet['state']
    if expected_config is not None and state['config']!=expected_config.to_dict():raise InputError("checkpoint config mismatch")
    for field,expected in (('data_identity',expected_data_identity),('target_identity',expected_target_identity)):
        if expected is not None and state[field]!=expected:raise InputError(f"checkpoint {field} mismatch")
    result=DynamicWindowRunner.from_dict(state,backend=backend)
    return result,packet['controller']
