"""Same saved failed input, normal limited planner, explicit numerical bridge."""
import json
from dataclasses import asdict
from re_interval_development_budget import ROOT,OUT
from raven_mcs_re_interval.schema import DecisionSnapshot
from raven_mcs_re_interval.predictor import FrozenServiceModel
from raven_mcs_re_interval.persistence import source_identity
from raven_mcs_re_interval.isolation import IsolatedController
from raven_mcs.control.persistence import exclusive_json
from raven_mcs.utils.hashing import sha256_file
if __name__=='__main__':
    packet=json.loads((OUT/'trajectory/FAILED_tick0202.json').read_text());before=packet['sources'];after=source_identity()
    changed=[k for k in before if before[k]!=after[k]]
    assert changed==['src/raven_mcs_re_interval/predictor.py']
    diagnosis=json.loads((OUT/'CLOCK_FAILURE_DIAGNOSIS.json').read_text())
    assert all(0<x['clock_delta']<1e-10 and x['version_delta']<=0 for c in diagnosis['captured'] for x in c['invalid'])
    snap=DecisionSnapshot.from_dict(json.loads((OUT/'snapshots/tick0202.json').read_text())['snapshot'])
    model=FrozenServiceModel.from_dict(json.loads((OUT/'trajectory/SERVICE_FROZEN_AT_20.json').read_text())['model'])
    scenarios=model.sample_scenarios(snap)
    assert all(e.time==round(e.time,10) for s in scenarios for e in s.events)
    assert all(e.registration.registered_at==round(e.registration.registered_at,10) for s in scenarios for e in s.events if e.registration.key.startswith('hist::'))
    ctrl=IsolatedController();decision=ctrl.decide(snap,model)
    # Timeout remains the original valid policy outcome, not a clock repair
    # failure or a mechanism success. Canonical event clocks are checked above.
    assert decision.control_cpu_seconds<=2
    exclusive_json(OUT/'ENGINEERING_PATCH_01.json',dict(reason='canonical ten-decimal resampled opportunity clock; observed 3.55e-15 future-time artifact',
        before_sources=before,after_sources=after,same_method_no_threshold_change=True,
        edit='t=clock+phase -> t=round(clock+phase,10); no validation or scientific tolerance relaxed',
        approved_scope='ordinary engineering error repair within same authorized batch',
        original_frozen_plan_sha256=sha256_file(OUT/'ACQUISITION_FROZEN_PLAN.json'),
        saved_failure=str(OUT/'trajectory/FAILED_tick0202.json'),verification=asdict(decision),accounting=ctrl.to_dict()))
    print(json.dumps(dict(reason=decision.reason,CPU=decision.control_cpu_seconds,proven=decision.proven)))
