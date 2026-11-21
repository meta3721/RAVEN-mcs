"""Read-only identity audit of the authorized first trajectory (no replay)."""
import hashlib
import json
from pathlib import Path
import time
import sys

ROOT = Path(__file__).resolve().parents[1]
OLD = ROOT / 'results_calibration_first_20261013'
OUT = ROOT / 'results_calibration_diagnostic_20261013_122013'

def read(path):
    return json.loads(Path(path).read_text(encoding='utf-8'))

def digest(path):
    with Path(path).open('rb') as f:
        return hashlib.file_digest(f, 'sha256').hexdigest()

def jd(obj):
    return hashlib.sha256(json.dumps(obj, sort_keys=True, separators=(',', ':'), ensure_ascii=False, default=str).encode()).hexdigest()

def save(name, obj):
    with (OUT/name).open('x', encoding='utf-8') as f:
        json.dump(obj, f, ensure_ascii=False, indent=2, allow_nan=False)

if __name__ == '__main__':
    start=time.perf_counter(); cpu=time.process_time()
    OUT.mkdir(exist_ok=False)
    reports=ROOT/'ccf-review-report/calibration_diagnostic_20261013_122013'
    reports.mkdir(exist_ok=False)
    # Only this round's directly dependent sources, evidence and seven reports.
    source=read(OLD/'trajectory/SOURCE_CLOSURE.json')
    paths=[p for p in OLD.rglob('*') if p.is_file() and not any(x.endswith('-tmp') for x in p.parts)]
    paths += list((ROOT/'ccf-review-report/calibration_first_20261013').glob('*.md'))
    paths += [ROOT/'ccf-review-report/reachability_method_prep_20261012_220855'/s for s in ('CANDIDATE_SPEC.md','REVISED_PROTOCOL.md')]
    save('PROTECTED_BEFORE.json', {str(p):digest(p) for p in paths})
    end=read(OLD/'trajectory/COMPLETE_T100_tick1000.json'); failed=read(OLD/'trajectory/FAILED_tick0201.json')
    ep=read(OLD/'trajectory/COMPLETE_T100_producer.json'); fp=read(OLD/'trajectory/FAILED_producer.json')
    r=read(OLD/'RESUME_IDENTITY.json'); f=failed['state']; e=end['state']
    checks={
        'failed_content_hash':jd(f)==failed['state_hash'],
        'final_content_hash':jd(e)==end['state_hash'],
        'failed_private_pair':fp['checkpoint_hash']==digest(OLD/'trajectory/FAILED_tick0201.json'),
        'final_private_pair':ep['checkpoint_hash']==digest(OLD/'trajectory/COMPLETE_T100_tick1000.json'),
        'resume_parent':r['parent_hash']==fp['checkpoint_hash'],
        'same_sources':failed['source_closure']==end['source_closure']==source,
        'current_sources_match':all(digest(ROOT/p)==h for p,h in source.items()),
        'same_core_identity':all(f[k]==e[k] for k in ('config','settings','data_identity','target_identity','mu','clock_namespace','probability_applicability','experiment_end','seed','q_model')),
        'failed_clock_and_steps':f['now']==20.1 and f['backend']['local_optimizer_steps']==686,
        'complete_T100_steps':e['now']==100 and e['backend']['local_optimizer_steps']==3305,
        'no_repeat_registrations':len(e['attempts'])==4300 and len({a['registration']['key'] for a in e['attempts'].values()})==4300,
        'immutable_prefix_attempt_inputs':all(all(e['attempts'][k][field]==a[field] for field in ('registration','q','features')) for k,a in f['attempts'].items()),
        'mature_prefix_labels_preserved':all(e['attempts'][k]['consumed']==a['consumed'] for k,a in f['attempts'].items() if a['consumed'] is not None),
        'prefix_decisions_unchanged':e['decisions'][:len(f['decisions'])]==f['decisions'],
        'prefix_events_unchanged':e['events'][:len(f['events'])]==f['events'],
        'prefix_stage1_unchanged':all(e['private_stage1'][k]==v for k,v in f['private_stage1'].items()),
        'steps_equal_R1':sum(a['terminal_reason']!='no_observations' for a in e['attempts'].values())==e['backend']['local_optimizer_steps'],
        'consumption_endpoint_mature':all(a['consumed'] in (0,1) for a in e['attempts'].values()),
    }
    report=dict(status='PASS' if all(checks.values()) else 'FAIL',checks=checks,
        evidence_role='observed_development_diagnostic_and_original_pi_boot_fit_candidate_only',
        resume_evidence=dict(failed_model_hash=jd(f['backend']['theta']),failed_producer_rng_hash=jd(fp['state']),
            failed_torch_rng_hash=jd(fp['torch_rng']),driver_hash=digest(ROOT/'scripts/resume_calibration_first.py'),
            limitations='No separately saved immediate-after-restore snapshot; continuity supported by verified checkpoints, restore source and immutable prefix. No counterfactual uninterrupted numerical equivalence claim.'),
        original_budget=read(OLD/'FINAL_BUDGET.json'), bootstrap_process_cpu=time.process_time()-cpu,
        bootstrap_wall=time.perf_counter()-start, seed=43001, training_steps=0, q_fits=0)
    save('D0_IDENTITY.json',report)
    save('AUTHORIZATION.json',dict(limit_CPU_seconds=900,unmetered_shell_and_bootstrap_reserve=90,
        prior_charged_seconds=1760.640625,local_SGD=0,GPU=0,new_trajectories=0,q_fit=0,
        tolerance_predeclared='Job total vs retained PID GetProcessTimes sum: 0.03125*N + 0.01 seconds. Full lifecycle sum, no double addition. Poll reserve 0.15s, single CPU affinity.',
        next_batch_authorized=False))
    print(json.dumps(report,ensure_ascii=False))
    if not all(checks.values()):sys.exit(2)
