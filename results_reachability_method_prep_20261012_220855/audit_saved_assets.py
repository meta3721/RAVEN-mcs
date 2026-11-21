"""Read completed artefacts only. No imports from controllers, no trajectories."""
import bisect
import csv
import hashlib
import json
import statistics
import time
from collections import Counter
from pathlib import Path

START = time.process_time()
HERE = Path(__file__).resolve().parent
OLD = Path('C:/Users/szr/Desktop/record/1/results_reachability_stopping_v1')
ROOT = Path('C:/Cursor/raven.mcs')
P0 = ROOT / 'ccf-review-report/reachability_v2_p0_20261012_215621'
P0_DATA = ROOT / 'results_reachability_v2_p0_20261012_215621'

def read_json(path):
    return json.loads(path.read_text(encoding='utf-8-sig'))

def preserve_inventory():
    paths = [p for directory in (OLD, P0, P0_DATA) for p in directory.rglob('*')
             if p.is_file() and '__pycache__' not in p.parts]
    return {str(p): hashlib.sha256(p.read_bytes()).hexdigest() for p in paths}

def save(name, value):
    (HERE / name).write_text(json.dumps(value, ensure_ascii=False, indent=2,
                                      allow_nan=False), encoding='utf-8')

before = preserve_inventory()
rows = list(csv.DictReader((OLD/'MAIN_COMPARISON.csv').open(encoding='utf-8-sig', newline='')))
audits = []
for row in rows:
    policy = row['policy']
    closures = read_json(OLD/f'41001_{policy}_closures.json')
    timeline = list(csv.DictReader((OLD/f'41001_{policy}_timeline.csv').open(encoding='utf-8-sig', newline='')))
    times = [c['time'] for c in closures]
    used = set()
    residual = 0.0
    score_error = 0.0
    for i, c in enumerate(closures):
        assert c['version_before'] == i
        assert not used.intersection(c['keys'])
        used.update(c['keys'])
        assert len(c['keys']) == c['K'] == len(c['weights'])
        assert c['time'] > (times[i-1] if i else 0)
        assert abs(c['duration'] - (c['time'] - (times[i-1] if i else 0))) < 1e-8
        if c['K']:
            a = c['weights']
            residual = max(residual, abs(sum(a)-1), -min(a),
                           max(a)-max(.5,1/c['K']), sum(x*x for x in a)-1/min(3,c['K']))
        score_error = max(score_error, abs(c['score']-(c['distance']+.02*c['age']+.2*c['duration']/4)))
    reconstructed = [closures[bisect.bisect_right(times, float(r['time'])+1e-9)-1]['score']
                     if bisect.bisect_right(times,float(r['time'])+1e-9) else 1.0 for r in timeline]
    error = abs(statistics.mean(reconstructed)-float(row['J']))
    timeline_error = max(abs(a-float(r['score'])) for a,r in zip(reconstructed,timeline))
    assert error < 1e-10 and timeline_error < 1e-10 and score_error < 1e-10 and residual <= 1e-7
    post = [c for c in closures if c['time']>20]
    wait_component = statistics.mean(
        .2*closures[bisect.bisect_right(times,float(r['time'])+1e-9)-1]['duration']/4 for r in timeline)
    audits.append(dict(policy=policy, J=statistics.mean(reconstructed), grid_rows=len(timeline),
        grid_min=float(timeline[0]['time']), grid_max=float(timeline[-1]['time']),
        closure_score_error=score_error, timeline_error=timeline_error, J_error=error,
        weight_residual=residual, closures_total=len(closures), closures_postwarmup=len(post),
        unique_consumed=len(used), reasons=dict(Counter(c['reason'] for c in post)),
        K_counts=dict(Counter(c['K'] for c in post)),
        duration_under_1_count=sum(c['duration']<1-1e-9 for c in post),
        duration_mean=statistics.mean(c['duration'] for c in post),
        score_components=dict(geometry=float(row['geometry_distance']),
                              age=.02*float(row['age']), waiting=wait_component)))
decisions = read_json(OLD/'41001_target_gain_stop_decisions.json')
dec_stats = dict(count=len(decisions), stop_count=sum(d['close'] for d in decisions),
    wait_count=sum(not d['close'] for d in decisions),
    zero_gain_count=sum(abs(d['predicted_gain'])<1e-12 for d in decisions),
    nonpositive_gain_count=sum(d['predicted_gain']<=0 for d in decisions),
    cost_values=sorted(set(d['waiting_cost'] for d in decisions)),
    K_counts=dict(Counter(d['K'] for d in decisions)),
    gain_min=min(d['predicted_gain'] for d in decisions),
    gain_max=max(d['predicted_gain'] for d in decisions))
new = next(a for a in audits if a['policy']=='target_gain_stop')
base = min((a for a in audits if a['policy']!='target_gain_stop'),key=lambda a:a['J'])
save('SAVED_EVIDENCE_AUDIT.json', dict(scope='saved file arithmetic; no controller execution, no replay',
    policies=audits, decisions=dec_stats, comparison=dict(baseline=base['policy'],
    absolute_J_difference=new['J']-base['J'], relative_J_worsening=(new['J']-base['J'])/base['J'],
    component_differences={k:new['score_components'][k]-base['score_components'][k]
                           for k in new['score_components']}),
    limits=['No recomputation of atomic-unit Q or service events in this audit.',
            'Original COMPLETED_ARTEFACT_AUDIT covers those metadata checks; preserved as historical evidence.',
            'No neural predictions exist for v1.']))
save('SOURCE_INVENTORY.json', dict(assets=[dict(path=p,sha256=h) for p,h in before.items()],
    dependencies=[dict(path=str(ROOT/p),exists=(ROOT/p).exists()) for p in [
        Path('results_main_rebuild_r1/data/traffic/atomic_units.parquet'),
        Path('results_main_rebuild_r1/eventtraces/traffic/seed41001/training_eventtrace/events.parquet')]]))
after = preserve_inventory()
assert before == after
save('HISTORY_PRESERVATION.json', dict(all_unchanged=True, files=len(before),
    external_files=len([p for p in before if p.startswith(str(OLD))]),
    excluded=['__pycache__'], original_p0_state_changed=False, original_stop_changed=False))
save('PREPARATION_STATE.json', dict(status='WAITING_USER_REVIEW', phase='METHOD_DEFINITION_AND_DESIGN',
    proposed_method='reachability_stop/conditional-bundle-v2', implementation_started=False,
    old_method='target_gain_stop/v1', old_status=read_json(OLD/'EXECUTION_STATUS.json')['status'],
    candidate_specification='PROPOSED_NOT_IMPLEMENTED', implementation_aligned=False,
    results='RESULTS_NOT_REVALIDATED', resumed_old_tasks=False,
    neural_training_runs=0, optimizer_steps=0, new_synthetic_replays=0, new_real_control_replays=0))
elapsed = time.process_time()-START
save('BUDGET.json', dict(limit_cpu_device_seconds=1800, audit_process_cpu_seconds=elapsed,
    neural_training=0, synthetic_replay=0, real_control_replay=0,
    audit_scope='stdlib arithmetic and file hashing only',
    other_reads_cpu='interactive read/write processes not individually metered; not claimed as precise total',
    conservative_preparation_charge_seconds=180+elapsed,
    charge_basis='180 s reserved for lightweight read/write processes; accounting allowance, not measured CPU',
    future_implementation_budget_authorized=False))
print(json.dumps(dict(policies=len(audits), preserved_files=len(before), audit_cpu_seconds=elapsed,
    decisions=dec_stats, comparison=read_json(HERE/'SAVED_EVIDENCE_AUDIT.json')['comparison']),ensure_ascii=False))
