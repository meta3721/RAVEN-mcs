"""Human-readable T-Drive protocol seal R1 report."""

from __future__ import annotations

from pathlib import Path
from typing import Any

from raven_mcs.paper_data_r1.io_util import write_text
from raven_mcs.tdrive_protocol_seal_r1.constants import FORMAL_SEEDS, METHODS, ROUND


def write_report(
    out: Path,
    ctx: dict[str, Any],
    *,
    status_code: str,
    status_name: str,
    gates: dict[str, Any] | None,
) -> Path:
    gtxt = "pending"
    if gates:
        lines = []
        for gid, payload in gates.get("gates", {}).items():
            mark = "PASS" if payload.get("pass") else "FAIL"
            lines.append(f"- {gid} {mark}: {payload.get('detail')}")
        gtxt = f"{gates.get('n_pass')}/{gates.get('n_total')} all_pass={gates.get('all_pass')}\n" + "\n".join(lines)
    fx = ctx["fixture"]
    md = f"""# T-Drive real-mobility protocol seal R1

Round: `{ROUND}`

## 1. Executive decision

**{status_code}. {status_name}**

This round is a protocol seal, not an experiment. Formal training runs = 0. Paper-result runs = 0. Canary = 0.

## 2. Zero-run attestation

training_started = false; formal_run_started = false; canary_started = false; raw/processed unmodified.

## 3. Raw T-Drive identity

MSR T-Drive trajectory sample under `data/raw/tdrive_speed`. Manifest data_hash `{ctx['manifest']['data_hash']}`. Status `{ctx['raw_identity']['status']}`.

## 4. Processed T-Drive identity

`atomic_units.parquet` rows={ctx['processed_identity']['atomic_units']['row_count']}; `client_measurements.parquet` rows={ctx['processed_identity']['client_measurements']['row_count']}. Status `{ctx['processed_identity']['status']}`. Files were not rewritten.

## 5. Speed-target semantics

Consecutive GPS haversine km / dt hours; keep 5–120 km/h; dt in (0, 0.25] h. Y = mean reference-fleet speed in 500 m × 30 min cell×slot.

## 6. Timezone

Naive T-Drive clocks are Beijing wall-clock. Adapter labels them UTC without converting. Paper timezone = Beijing local coinciding with processed timestamps. Do not apply +8.

## 7. Client identity

One client-fleet taxi = one federated client (`vehicle::{{id}}`). Reference fleet (30%, seed 26001) builds Y only. n_clients={ctx['sem']['n_clients']}.

## 8. Spatial grid

Regular 500 m cells over lon 116.0–116.8, lat 39.6–40.2. spatial_id = gXXXX_YYYY. n_cells={ctx['sem']['n_cells']}.

## 9. Time slots

30-minute floor of processed timestamps. n_slots={ctx['sem']['n_slots']}.

## 10. Atomic-unit definition

i = (spatial_id, time_slot); unit_id = `{{spatial_id}}_t{{time_index:05d}}`; Y_i = km/h speed.

## 11. Deployment target h(i)

`PRE_REGISTERED_PROTOCOL_FALLBACK`: H1–H4 Beijing-local time-of-day. Processed `target_group` (spatial×block) is recovered but is not paper h(i).

## 12. Target mu

Test-support frequency of atomic units over H1–H4. No speed labels. sum(mu)=1 within 1e-12.

## 13. Opportunity stratum s(i)

Processed `opportunity_stratum` = spatial_id × 4 TOD blocks × weekday/weekend. Distinct from h(i).

## 14. Real mobility opportunity R

R=1 iff processed client_measurements contains (k, i). REAL_FROM_TDRIVE. Independent of method and of seeds 30001–30010.

## 15. Observation O

Adapter valid-speed filter is DETERMINISTIC_DATA_QUALITY. EventTrace adds controlled p_obs=0.35. Label: REAL_MOBILITY_OPPORTUNITY + DETERMINISTIC_DATA_QUALITY + CONTROLLED_OBSERVATION. Not a recorded sensor-failure log.

## 16. Usable update U

E3 Complete-aligned compute/network/deadline/staleness (s_max=5). CONTROLLED_EXPERIMENTAL. T-Drive does not record these.

## 17. Real-vs-controlled selection-layer disclosure

Only R is guaranteed real-mobility-derived. O/U are controlled experimental layers after real opportunity.

## 18. Train/validation/test split

Recovered processed TemporalSplitConfig 60/20/20 by unique time slots. Not the chronological fallback. E9 yaml is not this protocol.

## 19. Leakage audit

Status: `{"PASS" if ctx["split"]["leakage_pass"] else "FAIL"}`. No unit or slot overlap; chronological partitions; train-only scaler; h/q do not use test outcomes.

## 20. Seed policy

Formal paired seeds: {", ".join(str(s) for s in FORMAL_SEEDS)}. All five methods share one exogenous EventTrace per seed.

## 21. EventTrace schema/generator

Generator `tdrive-complete-aligned-r1-v1`: R from client_measurements; O/U from E3 stage2 transfer. Method-independent. E3 station spatial_to_client generator is not used as-is.

## 22. EventTrace micro-fixture

Non-paper fixture seed {fx.get("seed")}: taxis={fx.get("n_taxis")}, cells={fx.get("n_spatial_cells")}, slots={fx.get("n_time_slots")}. Status `{fx.get("status")}`. No model fitting.

## 23. Five-method set

{chr(10).join(f"- {m['slot']} {m['display']} (`{m['canonical']}`)" for m in METHODS)}

No Local-Hajek, Inst-Cal, Debt-Cal, SimOracle, Central, or ablations.

## 24. RAVEN config

Transfer of E3/E4 full RAVEN: λ_group=1.0, λ_β=1.0, λ_v=0.1, λ_s=0.1, alpha_max=0.5, e_min/ESS=3.0. Not T-Drive test-tuned.

## 25. Baseline configs

Same backbone, split, preprocessing, and matched-seed EventTrace. TimeAlign canonical ID is `flamf_timealign_adapted`. Not intentionally weakened.

## 26. Primary/secondary metrics

Primary: Delta_group, Delta_c_s, RMSE_mu. RMSE_rho classified `NOT_REQUIRED_FOR_TDRIVE_PRIMARY_CLAIM`.

## 27. Statistical protocol

Paired Wilcoxon two-sided; Holm within each primary metric vs four baselines (m=4); α=0.05; EPS_ZERO=1e-12.

## 28. Pre-registered claim decision rules

Strong / partial / no-clear external consistency, or counterevidence. Success is not defined as an RMSE_mu win.

## 29. Future 1-seed Canary plan

5 methods × seed 30001. Every row `NOT_AUTHORIZED_YET`. Not executed.

## 30. Future 50-run formal matrix

5 methods × 10 seeds = 50 rows, all `NOT_AUTHORIZED_YET`. Not executed.

## 31. Method/data compatibility

Offline classification COMPATIBLE for all five methods. No training used.

## 32. External-validity wording

Allowed: real trajectories determine the opportunity process. Forbidden: claiming network/compute/federated-update traces are recorded T-Drive logs.

## 33. Protocol source freeze

See `13_freeze/TDRIVE_PROTOCOL_SOURCE_FREEZE.json` and the master JSON/MD.

## 34. Protocol diagnostics

See `14_diagnostics/`. Previews are `NOT_FOR_PAPER_USE`.

## 35. Gates

{gtxt}

## 36. Remaining blockers

{"None for protocol seal." if status_code == "A" else "See failed gates and status class B–F."}

## 37. Exact recommended next action

If status A: return this package. Do **not** start Canary until a separate instruction authorizes 5 methods × seed 30001.

If not A: do not start Canary; resolve the named blocker without running T-Drive experiments.
"""
    return write_text(out / "TDRIVE_REAL_MOBILITY_PROTOCOL_SEAL_R1_REPORT.md", md)
