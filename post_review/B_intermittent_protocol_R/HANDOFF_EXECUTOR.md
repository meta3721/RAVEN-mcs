# HANDOFF: Option B intermittent protocol R (SensorScope / U-Air)

This file is a frozen executor brief for another AI. Do not invent results. Do not edit the TMC manuscript unless the human later asks. Do not treat this block as mobile-client MCS.

```text
Experiment ID: INT-R-E3
Round directory: results_int_r/round_v1/
Python: C:\Cursor\raven.mcs\.venv_new\Scripts\python.exe
Repo: C:\Cursor\raven.mcs
Paper method: support-conditional Design (SCD), NOT coverage Gate
Question answered: Does the published E3 ranking still hold when protocol R is intermittent instead of always-on?
Question NOT answered: SensorScope/U-Air traces contain mobile clients. They do not.
```

---

## 0. Role and stop conditions

You are the experiment executor. Implement the occupancy layer, generate shared EventTraces, run the listed methods, write audit CSVs, and stop.

Stop and ask the human if any of the following happens:

- You cannot generate traces without using labels, RMSE, or residuals.
- The occupancy calibrator cannot hit the active-fraction window without using test data.
- You would need to overlay T-Drive GPS onto SensorScope/U-Air stations.
- You would need to change SCD using INT-R RMSE.
- GPU budget is insufficient for the mandatory matrix.

Do not start SAG / certificate / T-Drive ranking / NSW-Traffic E3. Those are out of scope.

---

## 1. Scientific contract

### Claim under test

Published E3 ranks methods on SensorScope and U-Air under Complete-aligned selection whose protocol opportunity \(R\) is **always-on**: every mapped client gets an opportunity event in every window (`generate_complete_aligned_r3`, loop `for client_id in client_ids`).

This experiment keeps the same station arrays, same public \(\boldsymbol\mu\), same O/U layers, and makes **client-window occupancy** intermittent, calibrated to the already-published T-Drive **occupancy scalars** (not T-Drive trajectories).

Allowed later wording: "protocol MCS with intermittent protocol \(R\)."
Forbidden later wording: real mobility, taxi clients on SensorScope/U-Air, end-to-end MCS, T-Drive method ranking.

### Object difference vs T-Drive G3

| Layer | T-Drive G3 (already done) | This experiment |
| --- | --- | --- |
| \(R\) | real taxi occupancy | protocol occupancy process on station clients |
| \(O\) | controlled Bernoulli | existing Complete-aligned \(p_{\mathrm{obs}}\) |
| \(U\) | controlled device-tier | existing `compute_usable_r3` |
| Ranking | forbidden | required (E3 table) |

Do not copy T-Drive unit-level \(R\) onto these stations.

---

## 2. Frozen inputs (do not retune)

Copy these from the paper / public bundle. Do not change them to improve RMSE.

```text
Seeds E3/E4: 30001 .. 30020
Canary seed: 31001 (smoke only; not in the table)
Calibration seed: 29999 (occupancy parameters only; not in the table)
Datasets: sensorscope, uair
Not datasets: traffic, tdrive
O/U generator: src/raven_mcs/e3/real_runner/generator_r3.py generate_complete_aligned_r3
mean_observation_rate: 0.35 (existing default)
s_max: 5
window_duration: 1.0
theta_align: 1.25, tail blocks {2, 3} (existing pi_opp)
P2 lambdas: lambda_group=1.0, lambda_beta=1.0, lambda_v=0.1, lambda_s=0.1, alpha_max=0.5, ESS=3.0
TARGET_LAW_RULE_V1 hash: 86fd55f7e0bf8499944433de16324bd4687befd5568892613ee87acacad3ad07
```

**SCD freeze (paper, not Gate):**

```text
SensorScope: Design ON
U-Air: Design OFF
Reason: frozen public-target support (U-Air 25.5% zero-target mass). This is a property of π^tar, not of occupancy.
Coverage Gate (Algorithm 1 / aggregate_coverage / Design_t := Gate_t): OFF for all INT-R ranking runs.
U-Air full Design: diagnostic row only, same traces, Design ON, still not Gate.
```

Do not re-choose SCD after seeing INT-R RMSE. You may **report** as a diagnostic: fraction of target-supported units with at least one \(R=1\) under intermittent occupancy. That diagnostic must not flip Design.

Code note: `method_policy.py` still documents `raven_mcs` Gate as `aggregate_coverage`. For this round, **do not follow that Gate switch**. Implement SCD as:

- SensorScope SCD row: Design ratio ON (`uses_design_ratio=True`), Gate unused.
- U-Air SCD row: Design ratio OFF (same components as `raven_wo_design` / always_off Design), Gate unused.
- U-Air full-Design diagnostic: Design ratio ON, Gate unused.

If you must add a method key, name it `raven_mcs_scd` and keep `paper_method` wiring explicit in the run manifest. Do not silently run `Design_t := Gate_t`.

---

## 3. Occupancy process (the only new mechanism)

### 3.1 Placement

In `generate_complete_aligned_r3`, **before** sampling stratum / risk set / O / U for a client-window \((k,t)\):

1. Draw occupancy \(A_{k,t} \in \{0,1\}\) from the frozen occupancy process (Section 3.3).
2. If \(A_{k,t}=0\): write no opportunity event for that client-window (empty risk set, no O, no U). This is \(R_{k,t,i}=0\) for all units \(i\) in that window.
3. If \(A_{k,t}=1\): keep the existing r3 path unchanged (joint \(\pi^{\mathrm{opp}}\), risk-set size `min(4, len(support))`, \(p_{\mathrm{obs}}\), `compute_usable_r3`).

Occupancy is a **client-window** bit, not a per-unit independent mask on top of always-on events. Always-on is exactly \(A_{k,t}=1\) for all \(k,t\).

### 3.2 Legal information

\(A_{k,t}\) may depend only on:

- client id, window id, dataset id
- occupancy RNG (seeded; see 3.4)
- previously realized \(A_{k,0},\ldots,A_{k,t-1}\) for the same client (Markov memory)

\(A_{k,t}\) must **not** depend on:

- \(Y\), predictions, residuals, RMSE, test split labels
- method identity
- O/U outcomes of the current window
- T-Drive GPS / cell ids

### 3.3 Process family (required)

Use a **per-client two-state Markov chain** on \(\{0,1\}\) (off/on), independent across clients.

```text
P(A_{t}=1 | A_{t-1}=1) = alpha      # stay on
P(A_{t}=0 | A_{t-1}=0) = beta       # stay off
Initialize A_{k,0} ~ Bern(rho_star) independently
```

Independent Bernoulli occupancy is **not** the primary process. Bernoulli gaps are not bursty enough versus T-Drive. Use Bernoulli \(A_{k,t}\sim\mathrm{Bern}(0.425)\) only as a documented fallback if the Markov search in 3.5 cannot hit the active-fraction window. If fallback is used, set `occupancy_family=bernoulli_iid` in the manifest and do not claim T-Drive burstiness matching.

### 3.4 RNG

```text
occupancy_rng(dataset, seed) = numpy Generator(seed + 10007 * dataset_id + 17)
dataset_id: sensorscope=0, uair=1
This RNG is independent of the existing r3 rng: default_rng(seed + 13)
Do not consume occupancy draws from the r3 rng. That would shift O/U bits for A=1 clients relative to always-on.
```

When \(A=1\), the existing r3 rng sequence for that client-window must match always-on r3 **conditional on reaching that client**. Because always-on iterates all clients, skipping \(A=0\) clients **will** shift later clients' r3 draws if you skip `rng` calls.

**Required invariance:** for every \((k,t)\) with \(A_{k,t}=1\), the r3 draws (stratum, risk set, O, U) must be identical to always-on r3 for that \((k,t)\). Implement by **always advancing** the r3 rng through the full always-on client loop, then **dropping** the event row when \(A_{k,t}=0\). Alternatively, use a per-client-window `default_rng(hash(seed, dataset, client, window, "r3"))` for r3 draws so skipped clients cannot shift others. Pick one, write it in the manifest, and unit-test it.

### 3.5 Calibrate (alpha, beta) without labels

Public calibration targets (already in the manuscript / G3; do not re-estimate from T-Drive unit CSV):

```text
rho_star = 0.425     # mean client active fraction
B_star   = 0.38      # Goh–Barabási burstiness (sd-mean)/(sd+mean) on inter-active gaps
rho_window = [0.40, 0.45]
B_window   = [0.30, 0.45]
```

Burstiness definition (must match `post_review/G3_mobility_replay/run_g3.py::_burstiness`):

- For each client, take sorted window ids with \(A=1\), gaps = `np.diff(slots)`.
- Pool gaps with `len(slots) >= 3` per client, or report both pooled-all-gaps and per-client mean. Primary number: **pooled gaps**, `ddof=1` std.
- \(B=(\sigma-\mu)/(\sigma+\mu)\). Always-on has no gaps (G3 reports \(-1\)).

Calibration procedure:

1. Use seed **29999**, dataset **sensorscope** train **window count only** (no atomic \(Y\)).
2. Simulate occupancy for all SensorScope clients × that window count on a grid of `(alpha, beta)` in `(0.50, 0.99)^2`.
3. Accept the pair that minimizes \((\hat\rho-\rho_\star)^2 + 0.25(\hat B-B_\star)^2\) among pairs with \(\hat\rho \in [0.40,0.45]\).
4. If no pair has \(\hat\rho\) in window, stop and ask the human.
5. If \(\hat\rho\) is in window but \(\hat B\) is not, **keep the \(\hat\rho\)-feasible pair** and record `burstiness_miss=true`. Do not retune using RMSE.
6. Freeze `(alpha, beta)` once. Reuse the **same** `(alpha, beta)` on U-Air. Do not fit a second pair on U-Air.

Do **not** target T-Drive cell coverage \(0.547\). Different geometry. Report unit/cell coverage as a diagnostic only.

### 3.6 Mandatory occupancy audit (before any training)

For each of `{sensorscope, uair}` × seeds `{30001, 30010, 30020}` write:

```text
mean_client_active_fraction
burstiness_pooled_gaps
fraction_windows_all_clients_off   # must be 0, or skip those windows consistently
mean_active_clients_per_window
TV(pi_opp_H, mu) on four UTC blocks using A=1 risk sets, train units only
```

Gate to start training:

```text
INT-R-OCC-1: mean active fraction in [0.35, 0.50] on both datasets, seed 30001
INT-R-OCC-2: burstiness > 0 on both datasets, seed 30001 (unless bernoulli fallback)
INT-R-OCC-3: TV(pi_opp, mu) > 0.05 on both datasets, seed 30001 (same 0.05 threshold as G3)
INT-R-OCC-4: no Y/RMSE in occupancy code path (grep gate)
INT-R-OCC-5: A=0 client-windows have empty risk_set_unit_ids
```

If INT-R-OCC-3 fails, occupancy destroyed the mismatch the paper is about. Stop; do not train.

---

## 4. What stays Complete-aligned

When \(A_{k,t}=1\):

- Keep Complete-aligned **direction**: tail blocks \(\{2,3\}\) still under-sampled in \(\pi^{\mathrm{opp}}\) and still have lower \(p_{\mathrm{obs}}\) (`scale=0.55`).
- Do not flatten \(\pi^{\mathrm{opp}}\) to uniform to "look more like taxis."
- Do not change `spatial_to_client` (station identity remains the client). That is why this still is not mobile MCS.

---

## 5. Mandatory run matrix

Shared EventTrace per `(dataset, seed)`. All methods in a cell consume that trace.

### 5.1 E3 ranking (mandatory)

Datasets: SensorScope, U-Air.
Seeds: 30001–30020.
Methods:

| Paper name | Implementation key (suggested) | Notes |
| --- | --- | --- |
| FedAvg-Window | `fedavg_window` | |
| TwoStage-Hajek | `twostage_hajek` | |
| FedAU-Window | `fedau_window` | windowed adaptation, not official FedAU |
| ObsUse-Window | `obsuse_window` | O+U, no Design/P2/debt |
| RAVEN-MCS (SCD) | SCD as in §2 | SS Design ON, UA Design OFF |
| RAVEN (full Design) | Design ON, U-Air only | diagnostic row; omit on SensorScope |

Do not add FedCure. Do not rank on Traffic. Local-Hájek may be run as a sanity check; omit from the main table if it again coincides with FedAvg.

### 5.2 E4 Design-only (mandatory, cheap relative to full E4)

Same INT-R traces. One factor: remove Design (compare SCD stack vs Design-off on SensorScope; on U-Air SCD is already Design-off, so compare SCD vs full Design — that row already exists in 5.1).

Minimum:

- SensorScope: SCD (Design on) vs `raven_wo_design` on the **same** INT-R traces, 20 seeds, same four metrics as E4.
- U-Air: already covered by SCD vs full Design in 5.1.

Skip Use / Inst / Debt one-factor unless the human expands budget. Those are not what Option B is for.

### 5.3 Out of scope

- E1 balanced no-harm
- E2 NSW-Traffic
- Certificate / R1m / availability grid
- T-Drive RMSE
- Full always-on retrain (use published Table II as the always-on reference)
- Promoting INT-R into `main.tex`

---

## 6. Metrics and statistics (copy the paper)

Metrics (lower better): \(\mathrm{RMSE}_\mu\), \(\mathrm{WorstGroupRMSE}\) (max over four UTC groups), \(\Delta_{\mathrm{group}}\), \(\Delta_{c\text{-}s}\).

Report `mean ± std` over 20 paired seeds.

Pre-registered tests (do not open extra looks):

1. SensorScope structural: paired relative change of SCD vs FedAvg on \(\Delta_{\mathrm{group}}\) and \(\Delta_{c\text{-}s}\). Direction of interest: SCD lower.
2. Worst-group non-inferiority vs FedAU-Window and vs ObsUse-Window: mean paired relative change \(\le +0.5\%\). Holm vs those two is **reported**, not a win claim unless both Holm-adjusted \(p<0.05\) **and** the \(0.5\%\) win rule used in the paper (beat **both** by \(\ge 0.5\%\)).
3. U-Air: full Design vs SCD on primaries. Published always-on story is that full Design **worsens** primaries by about \(7\%\). INT-R may agree or disagree. Record either way. Do not switch SCD.
4. Under-served-block: **do not open**. Not in this round.

Seeds are algorithmic / EventTrace randomness, not cities.

---

## 7. Result tables (fill with real numbers only)

Write CSV, not LaTeX, under `results_int_r/round_v1/tables/`.

### Table INT-R-OCC (occupancy)

`dataset, seed, mean_active_frac, burstiness_pooled, tv_opp_mu, n_clients, n_windows`

### Table INT-R-E3 (same columns as paper Table II)

`dataset, method, rmse_mu_mean, rmse_mu_std, worstgroup_mean, worstgroup_std, delta_group_mean, delta_group_std, delta_cs_mean, delta_cs_std`

Methods as in §5.1. Use `TBD` only before the run finishes. Never invent a finished number.

### Table INT-R-E4-Design

`dataset, removed, delta_group_pct, delta_cs_pct, rmse_mu_pct, tail_rmse_pct, holm_star_flags`

SensorScope Design removal; U-Air covered by E3 full-Design row.

### Table INT-R-VS-ALWAYS-ON (optional diagnostic)

If always-on tabulated numbers are read from the **published** Table II (do not retype from memory; parse the sealed CSV used by the paper):

`dataset, method, metric, always_on_mean, int_r_mean, relative_pct`

This is a robustness comparison, not a new ranking family.

---

## 8. Implementation map

Primary code:

```text
src/raven_mcs/e3/real_runner/generator_r3.py   # occupancy gate; rng isolation
src/raven_mcs/e3/real_runner/runner.py         # consume new traces; SCD wiring
src/raven_mcs/aggregation/method_policy.py     # do not turn Gate back on for ranking
src/raven_mcs/aggregation/methods.py           # method keys
```

Reuse E3 real-runner for training. New traces must not overwrite existing always-on EventTraces.

```text
Write traces to: artifacts/e3_int_r_eventtraces/{dataset}/{seed}/complete_aligned_int_r/
Keep old traces: artifacts/e3_formal_runs_r1/ and public bundle eventtraces/ untouched
```

Manifest JSON at `results_int_r/round_v1/INT_R_MANIFEST.json`:

```text
occupancy_family, alpha, beta, rho_star, B_star, calibration_seed,
rng_scheme, scd_rule, gate_used=false, generator_version, git_commit
```

---

## 9. Smoke tests (not evidence)

Run before the 20-seed matrix. Do not put smoke numbers in tables.

1. Seed 31001, SensorScope, 3 windows, occupancy on. Assert \(A=0\) rows have empty risk sets.
2. Same seed, occupancy forced \(A=1\) for all (debug flag). Assert EventTrace hashes match always-on r3 for those 3 windows under the chosen rng scheme, **or** document why hash equality is impossible and instead assert per-(k,t) r3 draws match.
3. Occupancy code path grep: no `rmse`, `Y_i`, `test_error` in the occupancy function.
4. One-window SCD SensorScope Design ON and U-Air Design OFF both launch without calling Gate.

---

## 10. Execution order

1. Implement occupancy + rng isolation + unit tests.
2. Calibrate `(alpha, beta)` on seed 29999; freeze.
3. Generate traces for 30001–30020 × {sensorscope, uair}.
4. Occupancy audit gates INT-R-OCC-1..5.
5. Train mandatory E3 matrix.
6. Train SensorScope Design-off on same traces.
7. Write CSVs + manifest + a short `EXECUTION_LOG.md` (commands, git hash, failures). No manuscript edits.

Priority if budget is cut: occupancy audit + SensorScope E3 20 seeds (FedAvg, FedAU, ObsUse, SCD) first; then U-Air; then Design-off.

---

## 11. Claim ceiling after results exist

When (and only when) the human asks to write the paper:

- INT-R is a **robustness** block unless they explicitly promote it to the main table.
- Do not drop the sentence that original traces are not mobile clients.
- Do not call occupancy "T-Drive \(R\)" or "real mobility."
- If INT-R ranking **disagrees** with always-on (sign flip on U-Air Design reversal, or SCD loses non-inferiority), report it. Do not hide it. Do not retune occupancy.

---

## 12. No-fabrication / integrity

- Do not fill Table INT-R-E3 until runs finish.
- Do not reuse always-on RMSE as INT-R RMSE.
- Do not change seeds, \(\boldsymbol\mu\), or SCD after seeing metrics.
- Do not commit GPU checkpoints into the public bundle unless asked.
- Do not run `git push`.
- Python 3.11 from `.venv_new`.

```text
No-fabrication status: this brief contains no experimental results.
Next owner after CSVs exist: ccf-integrity-auditor (numbers vs claims), then ccf-paper-writer only if the human asks to add a supplemental paragraph.
```
