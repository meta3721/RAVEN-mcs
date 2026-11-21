# HANDOFF: compute SensorScope / U-Air \(\phi\) (zero-target mass)

Paste this to the executor AI:

```text
You are the SCD-PHI-SS-UA executor for repo C:\Cursor\raven.mcs.
Read this entire file and post_review/C2_scd_phi/PROTOCOL.json.
Execute §6 in order. Do not invent numbers. Do not edit the manuscript.
Do not train. Do not change SCD flags. Do not use RMSE / Y / residuals.
Do not call build_pi_target_support_compatible.
Do not read INT-R traces. If SensorScope phi > 0, stop.
Python: C:\Cursor\raven.mcs\.venv_new\Scripts\python.exe
```

```text
Experiment ID: SCD-PHI-SS-UA
Round directory: post_review/C2_scd_phi/
Python: C:\Cursor\raven.mcs\.venv_new\Scripts\python.exe
Paper method: support-conditional Design (SCD), NOT coverage Gate
This round only MEASURES phi. It does not rewrite Algorithm 2.
```

---

## 0. Role and stop conditions

Compute the frozen public-target zero-mass fraction \(\phi\) on SensorScope and U-Air, using the same \(\pi^{\mathrm{tar}}\) wiring as production Design (`build_pi_target`, `split="test"`). Write CSV/JSON under `post_review/C2_scd_phi/`. Then stop.

Stop and ask the human if any of the following happens:

- Processed `atomic_units.parquet` is missing, or frozen hashes do not match `FROZEN_DATASET_HASHES`.
- Always-on formal EventTraces `artifacts/e3_formal_runs_r1/eventtraces/{dataset}/seed{seed}/training_eventtrace/` are missing for any seed in 30001–30020.
- You would need RMSE, labels \(Y\), or E3 metrics to choose a denominator or a threshold \(\tau\).
- You would need `build_pi_target_support_compatible` (that is the failed G1 repair, not the SCD statistic).
- SensorScope \(\phi>0\) on **either** `phi_train_unit` or `phi_et_occ` (current table puts Design ON because SS zero-target mass is 0).
- U-Air `phi_et_occ` does not match G1 `0.2546875` within `1e-12` (wrong \(\pi^{\mathrm{tar}}\) wiring).
- You would need to edit `TO_OVERLEAF_paper_tmc_r1_clean/` or change method keys.

Do not start training, SAG, Gate, T-Drive ranking, NSW-Traffic E3, or INT-R. Do not `git push`. Do not commit unless the human asks.

---

## 1. Why this exists

Reviewer C2: SCD is currently a two-dataset flag, not a reusable online rule. The intended rule (not applied in this round) is

\[
\phi=\frac{\#\{i\in\mathcal{I}_{\mathrm{risk}}^{\mathrm{train}}:\pi_i^{\mathrm{tar}}=0\}}{\#\mathcal{I}_{\mathrm{risk}}^{\mathrm{train}}},\qquad \mathrm{Design}=\mathrm{ON}\iff\phi=0.
\]

Motivated by positivity (A5), **not** by RMSE. This round only computes \(\phi\). It does not pick \(\tau\) from a grid, and it does not set `Design_t := Gate_t`.

The manuscript number **25.5%** is already measured. G1 `three_layer_panel.csv` has

| dataset | `frac_pi_tar_zero` | `n_units` |
| --- | ---: | ---: |
| sensorscope | `0.0` | 64000 |
| uair | `0.2546875` | 51200 |

`0.2546875 = 25.46875%`, reported as 25.5%. Your EventTrace occurrence statistic **must** recover these two numbers. That is the wiring check. The transferable SCD statistic is the EventTrace-free train-unit version below.

---

## 2. Frozen inputs (do not retune)

```text
ROOT = C:\Cursor\raven.mcs
Python = ROOT\.venv_new\Scripts\python.exe
Datasets = sensorscope, uair
Seeds = 30001 .. 30020
EventTrace root = artifacts/e3_formal_runs_r1/eventtraces
Atomic = data/processed/{dataset}/atomic_units.parquet
pi_target = build_pi_target(atomic_sealed, spatial_to_client, split="test")
Zero test = (pi <= 0.0)
K = 8 clients (existing mapping; do not rebuild a new mapping)
```

Copy G1 dataset prep from `post_review/G1_propensity_design/run_g1_diagnosis.py` function `_prepare_dataset`. Do not invent a new stratum or client map.

Forbidden traces:

```text
artifacts/e3_int_r_eventtraces/
artifacts/e3_int_r_eventtraces_v2/
```

Occupancy changes the realized risk set. Paper \(\phi\) is always-on.

---

## 3. Definitions (compute all four; freeze one)

For unit \(i\), client \(k(i)\) from `load_spatial_to_client`, stratum \(s(i)=\) sealed `opportunity_stratum`,

\[
\pi_i^{\mathrm{tar}} := \pi^{\mathrm{tar}}\bigl(k(i),s(i)\bigr)
=\texttt{pi\_target.get((client\_id, opportunity\_stratum), 0.0)}.
\]

Missing keys count as 0.

### 3.1 `phi_train_unit` (primary SCD candidate; no EventTrace)

\(\mathcal{I}_{\mathrm{risk}}^{\mathrm{train}}\) = unique `unit_id` with `split=="train"` on the sealed atomic table.

\[
\phi_{\mathrm{train}}=\mathrm{mean}_i\bigl[\pi_i^{\mathrm{tar}}\le 0\bigr].
\]

This is the transferable rule: public \(\pi^{\mathrm{tar}}\) vs the train support. It does not depend on seed, occupancy, or \(Y\).

### 3.2 `phi_train_pair` (diagnostic)

Unique `(client_id, opportunity_stratum)` that appear in train. Fraction with \(\pi^{\mathrm{tar}}\le 0\).

Not the paper number. Report it. Do not use it to replace 3.1 unless 3.1 is undefined.

### 3.3 `phi_et_occ` (paper-number check; G1)

Load always-on `training_eventtrace` for seeds 30001–30020. For every event row, every `uid` in `risk_set_unit_ids`:

```text
cid = str(client_id)
s = unit_stratum[str(uid)]
pi = pi_target.get((cid, s), 0.0)
```

Pool all appearances. \(\phi_{\mathrm{et,occ}}=\mathrm{mean}(\pi\le 0)\).

Must match G1:

```text
sensorscope phi_et_occ == 0.0
uair       phi_et_occ == 0.2546875
```

Absolute tolerance `1e-12`. Also record `n_appearances` (G1: SS 64000, UA 51200).

### 3.4 `phi_et_unique` (diagnostic)

Same EventTraces, but unique `unit_id` that appear in any risk set (pool 20 seeds, then also per seed). Fraction with \(\pi^{\mathrm{tar}}\le 0\).

Report min/max across seeds. Do not average RMSE. Do not drop seeds.

---

## 4. What you must not do

- Do not use `pi_target_mode="support_compatible"` or `build_pi_target_support_compatible`.
- Do not use frozen \(\mu\) group ids as a substitute unless you also compute 3.1–3.3. Group-level \(\mu=0\) is a different denominator.
- Do not set a threshold \(\tau>0\) after seeing U-Air. The preview rule is \(\phi=0\) vs \(\phi>0\).
- Do not read `final_metrics.json`, E3 CSV, or Table II.
- Do not write \(\phi\) into `main.tex` / `appendix.tex`.
- Do not change `raven` / `raven_wo_design` assignment.

Grep gate on your new script:

```text
must not contain: rmse, y_i, test_error, support_compatible, Gate_t, aggregate_coverage
```

---

## 5. Decision after numbers exist (report only; do not apply)

Write `SCD_PHI_DECISION.json` with `status` in `{PASS, STOP}`.

| Check | Pass condition |
| --- | --- |
| Wiring | `phi_et_occ` matches G1 within `1e-12` on both datasets |
| SS positivity | `phi_train_unit[sensorscope] == 0` and `phi_et_occ[sensorscope] == 0` |
| UA signal | `phi_train_unit[uair] > 0` |
| Rule recovers table | SS \(\phi=0\) (Design ON) and UA \(\phi>0\) (Design OFF) |

If wiring fails: `STOP`, `reason=PHI_WIRING_MISMATCH`. Do not pick another denominator to force 25.5%.

If SS \(\phi>0\): `STOP`, `reason=SENSORSCOPE_PHI_POSITIVE`. The positivity rule cannot recover the current SensorScope assignment.

If UA `phi_train_unit==0` while `phi_et_occ==0.2546875`: `STOP`, `reason=TRAIN_UNIT_PHI_ZERO_BUT_ET_NOT`. Ask the human. Do not silently switch to EventTrace \(\phi\) as the SCD rule (that rule is not transferable without traces).

If all pass: `PASS`. Freeze

```text
phi_scd := phi_train_unit
Design_ON iff phi_scd == 0
```

Record U-Air exact fraction and one-decimal percent. If `round(100*phi_train_unit_uair, 1) != 25.5`, say so in the report. The manuscript 25.5% stays tied to `phi_et_occ` until a later writing pass. This round does not edit the paper.

---

## 6. Execution order

1. Confirm Python: `C:\Cursor\raven.mcs\.venv_new\Scripts\python.exe`.
2. Write `scripts/compute_scd_phi.py` (new file). Keep it small. Reuse G1 `_prepare_dataset` wiring; do not copy the propensity replay.
3. Hash-check atomics via `raven_mcs.e3.canary.dataset_load.verify_dataset_hash`.
4. Compute 3.1 and 3.2 (no traces).
5. Compute 3.3 and 3.4 from always-on traces 30001–30020.
6. Write outputs in §7.
7. Fill `SCD_PHI_DECISION.json`. If `STOP`, do not invent a fix. Ask the human.
8. Stop. No manuscript. No training. No commit unless asked.

---

## 7. Required outputs

All under `post_review/C2_scd_phi/`:

| File | Content |
| --- | --- |
| `tables/SCD_PHI.csv` | one row per dataset; columns in §7.1 |
| `tables/SCD_PHI_BY_SEED.csv` | one row per dataset×seed for `phi_et_occ_seed` and `phi_et_unique_seed` |
| `SCD_PHI.json` | machine-readable copy of the CSV plus hashes |
| `SCD_PHI_DECISION.json` | PASS/STOP and frozen `phi_scd` if PASS |
| `REPORT.md` | short; numbers from JSON; no claim that Algorithm 2 is already rewritten |

### 7.1 `SCD_PHI.csv` columns

```text
dataset
n_train_units
n_train_zero
phi_train_unit
n_train_pairs
n_train_pairs_zero
phi_train_pair
n_et_appearances
n_et_appearances_zero
phi_et_occ
n_et_unique_units
n_et_unique_zero
phi_et_unique
g1_phi_et_occ_expected
phi_et_occ_matches_g1
atomic_hash_ok
```

Percents in REPORT only. CSV/JSON keep exact floats.

---

## 8. Implementation sketch (do not “improve”)

```python
from pathlib import Path
import json
import numpy as np
import pandas as pd

from raven_mcs.correction.pi_target import build_pi_target
from raven_mcs.e3.canary.dataset_load import load_spatial_to_client, verify_dataset_hash
from raven_mcs.e3.real_runner.generator_r3 import build_joint_pi_opp  # optional; not needed for phi
from raven_mcs.e3.stratum_seal.remap import apply_sealed_opportunity_stratum
from raven_mcs.simulation.event_trace import load_event_trace

ROOT = Path(r"C:\Cursor\raven.mcs")
ET = ROOT / "artifacts" / "e3_formal_runs_r1" / "eventtraces"
SEEDS = list(range(30001, 30021))
G1 = {"sensorscope": 0.0, "uair": 0.2546875}

def prepare(dataset: str):
    atomic = pd.read_parquet(ROOT / "data" / "processed" / dataset / "atomic_units.parquet")
    atomic_sealed, _ = apply_sealed_opportunity_stratum(atomic, dataset=dataset, root=ROOT)
    spatial_to_client = load_spatial_to_client(ROOT, dataset)
    atomic_for_pi = atomic_sealed.copy()
    if "target_group_main" not in atomic_for_pi.columns:
        atomic_for_pi["target_group_main"] = atomic_for_pi["target_group"].astype(str)
    pi_frame = build_pi_target(atomic_for_pi, spatial_to_client, split="test")
    pi_target = {
        (str(r.client_id), str(r.opportunity_stratum)): float(r.pi_k_s_tar)
        for r in pi_frame.itertuples()
    }
    unit_stratum = {
        str(r.unit_id): str(r.opportunity_stratum) for r in atomic_sealed.itertuples(index=False)
    }
    unit_client = {}
    for r in atomic_sealed.itertuples(index=False):
        unit_client[str(r.unit_id)] = str(spatial_to_client[str(r.spatial_id)])
    train = atomic_sealed.loc[atomic_sealed["split"].astype(str) == "train"]
    return pi_target, unit_stratum, unit_client, train

def phi_train_unit(train, pi_target, unit_stratum, unit_client):
    uids = train["unit_id"].astype(str).unique()
    zeros = 0
    for uid in uids:
        pi = pi_target.get((unit_client[uid], unit_stratum[uid]), 0.0)
        zeros += int(pi <= 0.0)
    n = int(len(uids))
    return n, zeros, zeros / n if n else float("nan")
```

EventTrace loop: `load_event_trace(ET / dataset / f"seed{seed}" / "training_eventtrace")`. Use `risk_set_unit_ids` only. Do not need \(O\), \(p\), or weights.

`load_event_trace` JSON-decodes `risk_set_unit_ids`. Treat entries as `str`.

---

## 9. Claim ceiling for REPORT.md

Allowed:

- SensorScope / U-Air \(\phi\) under the definitions above.
- Whether G1 25.5% is recovered by `phi_et_occ`.
- Whether `phi_train_unit` has the same ON/OFF sign as the current table.

Forbidden:

- “SCD is now an online rule” (Algorithm 2 is not rewritten in this round).
- Any RMSE, ranking, or “Design would improve if…”.
- Mobile clients, T-Drive burstiness, Gate as method.
- Lab-round names in a manuscript draft (this REPORT may name G1 as the source of 25.5%).

---

## 10. Done when

- `tables/SCD_PHI.csv` and `SCD_PHI_DECISION.json` exist.
- G1 wiring check is recorded.
- No manuscript diff.
- No training artifacts.

If `PASS`, the next human task is a **separate** Algorithm 2 / E3 wording pass. Do not start it here.
