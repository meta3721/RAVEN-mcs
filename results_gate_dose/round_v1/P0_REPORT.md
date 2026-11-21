# Gate-dose round — P0 report (no training)

Round: `results_gate_dose/round_v1/`
Instruction: `raven-mcs-gate-dose-execution-prompt.md`, sha256 `56607091…`, 11 275 B
Stage: **P0 only** (§7). No training has run. `授权门控剂量` has not been written, so
P1/P2 are not executed.

Artifacts produced (written before any run; `MANIFEST.sha256` records both the file hash
and a timestamp-free content hash):

| file | bytes | file sha256 | content sha256 |
| --- | --- | --- | --- |
| `MASKS.json` | 157 836 | `033d0cb7304b126c…` | `6b456bd378e92ead…` |
| `TARGET_WIRING.json` | 9 265 | `4fd05b8d3ecf8779…` | `b9de9d9b7d7e7823…` |
| `RHO.csv` | 5 266 | `302cd48c779e9a2a…` | (content-deterministic: file hash is stable) |

The JSON file hashes move with the `created_utc` stamp; the content hashes do not.
Re-running `p0` several times reproduced both content hashes and the `RHO.csv` file hash
exactly, so the masks, the wiring and the realized ρ are functions of the frozen inputs
alone. This report is deliberately not listed in `MANIFEST.sha256` — the manifest is
regenerated as the round progresses, so hashing a narrative that cites it would be
circular.

Driver: `scripts/gate_dose.py` (new; the only writer under `results_gate_dose/`).
`src/`, the manuscript, `artifacts/` and every existing `results_*` are untouched;
`TO_OVERLEAF_paper_tmc_r1_clean/main.tex` is still `02447bfe6256632b…`.

---

## 1 Masks (locked before any run)

Candidate rule, permutation, nesting and level sizes follow §1 exactly.

| dataset | keys with `pi_tar > 0` | permutation | level `m` | keys masked |
| --- | --- | --- | --- | --- |
| SensorScope | 440 | one draw, `default_rng(20261007)` | 0 / 0.10 / 0.25 / 0.40 | 0 / 44 / 110 / 176 |
| U-Air | 216 | one draw, `default_rng(20261007)` | 0 / 0.10 / 0.20 | 0 / 22 / 43 |

Nesting verified for both datasets (`MASKS.json → nested: true`). U-Air has 288 keys
of which 72 are zero under the production target, so 216 are maskable.

## 2 Target wiring (`TARGET_WIRING.json`)

Three consumers, all rebuilt from the same masked test split:

- **T1** `run_e3_real(pi_target_override=…)`, masked keys set to 0, renormalized.
- **T2** the group target `mu`, injected by patching `production_target_bundle`
  (`run_h_headroom.injected` technique), rebuilt as the masked test-unit group share.
- **T3** the `Delta_c-s` denominator, injected by patching
  `raven_mcs.e3.delta_cs_rho.delta_cs_v6.build_pi_tar_client_stratum`.

`accumulate_delta_cs_v6` rebuilds `pi_tar` from the atomic test split on its own
(`delta_cs_v6.py` L134); it has no override parameter, so T3 cannot be wired without a
patch. The patch is a monkeypatch at call time — no `src/` edit. The patched map sums to
1, which the builder asserts.

### Assertions

| dataset | T1 max &#124;Δ&#124; vs production | T2 max &#124;Δmu&#124; | T3 max &#124;Δ&#124; | Σ pi_tar | Σ mu | per-level mu vs masked test share |
| --- | --- | --- | --- | --- | --- | --- |
| SensorScope | 1.78e-17 | 0.0 | 1.78e-17 | 1 ± 3.1e-15 | 1 ± 1.1e-16 | 0.0 |
| U-Air | 2.60e-18 | 0.0 | 2.60e-18 | 1 ± 1.8e-15 | 1 ± 1.1e-16 | 0.0 |

All level assertions pass. **Disclosure:** the instruction asks for *hash* equality of
each consumer against the production object at `m = 0`. That holds only after
renormalization; the renormalized map differs from the production map by 1.8e-17
(SensorScope) / 2.6e-18 (U-Air), so the hashes differ. The report records both the hash
comparison and the value comparison, and passes the assertion on the values (≤ 1e-12).
The production `pi_tar` itself sums to 0.999999999999995 (SensorScope) and
1.0000000000000004 (U-Air) before renormalization.

## 3 Realized rho (`RHO.csv`)

### 3.1 Which frame

The instruction fixes "the share of U = 1 delivered risk units on non-test splits whose
`(client, stratum)` has `pi_tar ≤ 0`" (the `c1_deletion_driver.py::rho_for` semantics) and
pins `m = 0` to SensorScope `0` and U-Air `≈ 0.354`. On these datasets those two
requirements select different frames:

| frame | SensorScope | U-Air | reproduces the pin? |
| --- | --- | --- | --- |
| **train atoms** (`split == "train"`), keyed by `(client, stratum)` | **0** | **0.35443037974683544** | **yes, exactly** |
| U = 1 delivered risk units on non-test splits, frozen traces | 0 | 0.2543367346938776 | no |
| every risk-set unit of every trace, non-test | 0 | 0.2546875 | no |
| `(client, stratum)` pairs present in train (`SCD_PHI phi_train_pair`) | 0 | 0.25 | no |

The pinned U-Air value is `post_review/C2_scd_phi/tables/SCD_PHI.csv::phi_train_unit`
(0.35443037974683544, and `appendix.tex` L2436-2437 prints 35.4 %). The primary frame is
therefore the train-atom frame; the event-trace frame is computed anyway and reported in
`RHO.csv` as `rho_alt_*` columns. Both are static — no model output — so the
train-atom frame carries **no seed dimension** (the instruction's "per (dataset, level,
seed)" is nominal for it, which is what lets the `m = 0` pin be exact).

**ρ tolerance.** Only the unrounded stored value (`0.35443037974683544`) is within the
instruction's 1e-6; the printed `0.354` is off by 4.3e-4. `TARGET_WIRING.json`
(`m0_rho_check`) records both differences:

| dataset | measured ρ at m=0 | vs unrounded | vs printed 0.354 | verdict |
| --- | --- | --- | --- | --- |
| SensorScope | 0.0 | 0.0 | 0.0 | pass |
| U-Air | 0.35443037974683544 | 0.0 | 4.304e-4 | pass vs unrounded, fail vs printed |

### 3.2 Realized levels

| dataset | `m` | keys masked | mass removed | **ρ (primary)** | ρ (trace frame) |
| --- | --- | --- | --- | --- | --- |
| SensorScope | 0 | 0 | 0 | 0.000000 | 0.000000 |
| SensorScope | 0.10 | 44 | 10.03 % | 0.097423 | 0.115282 |
| SensorScope | 0.25 | 110 | 24.81 % | 0.245309 | 0.302330 |
| SensorScope | 0.40 | 176 | 39.00 % | 0.388138 | 0.441947 |
| U-Air | 0 | 0 | 0 | 0.354430 | 0.254337 |
| U-Air | 0.10 | 22 | 10.38 % | 0.418776 | 0.326276 |
| U-Air | 0.20 | 43 | 23.06 % | 0.466245 | 0.393112 |

The dose is monotone in `m` and the levels move ρ by 0.10–0.35 — far more than the
≈0.097 (SensorScope) / ≈0.11 (U-Air) spread the trace frame would show per seed.

## 4 θ re-scoring (§3 of the instruction) — reconnaissance result

§3 requires every run to be scored from its saved θ checkpoint when its last window is
inactive, and requires stored vs θ re-score agreement to ≤ 1e-8 for runs whose last
window is active. A frozen-θ replay was built and measured (scratch only,
`.rb_work/gate_dose_scratch`): the production entry point `run_e3_real` is called with the
saved `state_dict` pre-loaded and `ClientTrainer.train_step` neutralized to return an
empty update, so server θ never moves while every downstream quantity (P2 weights, debt,
`omega`, `Delta_c_s`) is recomputed by the production code path.

Measured on 7 active runs (both datasets, both arms; seeds 30001/30002/30003):

| endpoint | stored vs θ re-score |
| --- | --- |
| `RMSE_mu` | **exactly 0.0 in all 14 comparisons across 7 runs** (bit-equal) |
| `Tail_RMSE` | **exactly 0.0** |
| `Delta_group` | 2.4e-6 … 4.7e-4 absolute (2.3e-6 … 4.3e-4 relative) |
| `Delta_c_s` | 1.5e-5 … 5.9e-4 absolute (1.2e-5 … 4.8e-4 relative) |

`active_clients` is identical on every window in all of them.

Interpretation: `RMSE_mu` and `Tail_RMSE` are functions of the final θ over the test
split, and the replay reproduces them exactly — the mechanism is faithful. `Delta_group`
and `Delta_c_s` are **trajectory functionals** (time sums over per-window α, which depend
on θ at each window), so a final-θ replay cannot reproduce them to 1e-8; it differs by
1e-5…6e-4. Consequence for the driver:

- the ≤ 1e-8 stored-vs-replay check is applied to `RMSE_mu` and `Tail_RMSE` (the
  endpoints it can legitimately gate), and the `Delta_group`/`Delta_c_s` movement is
  recorded next to every cell for disclosure;
- the three runs with an inactive last window — `uair/raven` seeds **30007, 30016,
  30018** (the only ones in the 80 frozen runs; 77/80 have an active last window) — do
  change materially under the replay, so §3's exception matters here:

| run | `RMSE_mu` stored | `RMSE_mu` θ | `Tail_RMSE` stored | `Tail_RMSE` θ | `Delta_group` Δ | `Delta_c_s` Δ |
| --- | --- | --- | --- | --- | --- | --- |
| uair/raven 30007 | 1.142487 | 1.189413 (+4.11 %) | 1.148485 | 1.197865 (+4.30 %) | 5.95e-5 | 7.66e-9 |
| uair/raven 30016 | 1.170926 | 1.152670 (−1.56 %) | 1.177715 | 1.158593 (−1.62 %) | 1.05e-4 | 1.31e-4 |
| uair/raven 30018 | 1.125360 | 1.181723 (+5.01 %) | 1.129562 | 1.188798 (+5.24 %) | 7.28e-5 | 7.30e-5 |

## 5 m = 0 reproducibility (the round's main technical risk)

The handoff lists "`raven` reproduces at m = 0" as an unverified assumption; only
`raven_wo_design` had written bit-exact evidence. A rehearsal (scratch only, **not** the
P1 gate; no result is claimed from it) re-ran seed 30001 for both arms and both datasets
with the masked target at `m = 0` and compared against the stored artifacts:

| dataset / arm | `RMSE_mu` stored | re-run | &#124;Δ&#124; | `Delta_group` | `Delta_c_s` | `Tail_RMSE` | `active_clients` |
| --- | --- | --- | --- | --- | --- | --- | --- |
| ss / raven | 7.913791224193 | 7.913790804121 | **4.20e-7** | 9.8e-11 | 4.6e-9 | 4.3e-7 | identical |
| ua / raven | 1.201716880706 | 1.201716881084 | **3.78e-10** | 4.3e-9 | 8.3e-9 | 4.8e-10 | identical |
| ss / raven_wo_design | 7.916851248043 | 7.916851248043 | **0.0** | 0.0 | 2.0e-15 | 0.0 | identical |
| ua / raven_wo_design | 1.160743090966 | 1.160743090966 | **0.0** | 0.0 | 2.2e-16 | 0.0 | identical |

So §2's `|ΔRMSE_μ| ≤ 1e-9` holds for `raven_wo_design` bit-exactly and **fails for
`raven`** on both datasets (4.2e-7 SensorScope, 3.8e-10 U-Air). Two further measurements
narrow the cause:

1. **Not run-to-run noise.** The same invocation twice in the same process is
   bit-identical: θ bit-equal, `alpha` bit-equal across all 66 P2 invocations, and all
   four endpoints at `|Δ| = 0` (`.rb_work/gate_dose_repeat.py`). The path is
   deterministic *within* an environment; the miss is a property of the stored
   artifacts, not of a single run.
2. **The θ itself differs.** Max `|Δθ|` against the stored checkpoint: `raven`
   3.09e-7 (SensorScope) / 1.49e-8 (U-Air); `raven_wo_design` exactly 0 with every
   parameter bit-equal.
3. **The frozen artifacts predate the current working tree.** Their ledger START records
   `git_commit b01db69e8554a33446c438c060ac464dcfadac24` (2026-08-11); the working `src/`
   differs from that commit by 22 files, +4173/−176 lines (e.g. `window_runner.py`
   +900, `p2_cvxpy.py` +9). The artefacts also lack `p2_invocation_states.json`, an audit
   file the current runner writes, so they were produced by an older runner. The
   `raven` arm is the one whose weights come from the CVXPY/CLARABEL P2 solve, which
   emits "Solution may be inaccurate" warnings in this environment; `raven_wo_design`
   bypasses that solve and is bit-exact.

This is a pre-registered boundary, not a permission slip: **if P1 were run now it would
write `GATE.json` with `pass: false`** and the round would stop there. §2 forbids a
waiver list and a second rule, so the decision to run under that gate, to amend the
tolerance, or to stop the round is the user's, not the driver's.

## 6 What is ready and what is not

Ready: `p0` (above). Implemented but **not run**: the §2 gate, the frozen-θ re-scoring
path, the plateau of §4's estimand (paired `r_e`), the seed-cluster bootstrap
(`default_rng(20261007)`, 10 000 draws, percentile 95 %), H1/H2 labelling.

Not implemented pending a decision: whether `m = 0` cells should be read from the stored
artifacts (as §1 says) when all other cells come from runs produced by the current tree —
a ~1e-7 relative difference in `RMSE_mu` between the two conventions for `raven`. The
driver already carries a per-cell fresh θ re-score column so the difference is visible
either way.

## 7 Interpretation decisions (confirmed by the user on 2026-10-06, before any run)

Item 1 is **not** confirmed: the user is reviewing the rules first, so training stays
locked. Items 2–4 are confirmed and are frozen into `scripts/gate_dose.py::CONFIRMED`.

1. **Training authorization — NOT GIVEN.** `授权门控剂量` has not been written. P1/P2
   remain unexecuted; P0 is complete.
2. **The `raven` m = 0 gate miss** (§5) — **confirmed: run under the written rule and, if
   it misses, write `GATE.json` with `pass: false` and stop the round.** No tolerance
   amendment, no waiver list, no continuation into P2 on a failed gate
   (`CONFIRMED["gate_failure_action"] = "stop_round"`). Disclosed consequence: the round
   would then close with the P1 miss as its result, and §5's evidence stands as the
   reason.
3. **ρ frame and tolerance** (§3.1) — **confirmed: primary frame = train atoms, and the
   1e-6 tolerance is read against the unrounded `0.35443037974683544`.** The printed
   `0.354` is 4.3e-4 away and fails either way; the trace frame is retained only as
   `rho_alt_*` cross-checks.
4. **θ re-scoring scope** (§4) — **confirmed: the ≤ 1e-8 stored-vs-replay check applies
   to `RMSE_mu` and `Tail_RMSE` only** (both reproduce at exactly 0.0); the
   `Delta_group`/`Delta_c_s` replay movement is recorded and disclosed next to every
   cell, not used as a gate. For the three inactive-last-window runs (uair/raven 30007,
   30016, 30018) all four endpoints come from the replay.

Open, not decided here: whether the `m = 0` cells are read from the stored artifacts
(§1's wording) or from fresh replays, given that all other cells are produced by the
current tree. P0 does not need it; the driver carries both columns so the ~1e-7 relative
`RMSE_mu` difference is visible when P2 is written.

## 8 No-fabrication status

Every number above is written by `scripts/gate_dose.py` or by the read-only probes named
in the text, from the named inputs. §4/§6 of the instruction remain `TBD`. No endpoint for
any dose cell exists yet. No claim is made about `gate_law`, H1 or H2.
