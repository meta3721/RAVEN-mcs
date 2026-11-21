# Regime-B endpoint experiment — design and pre-registration

Authored with the `ccf-experiment-designer` contract (mode `design`), then overlaid with this record's
pre-registration discipline (rules fixed before computation, stop rules, forbidden-claim list).
Written **before** any value of the confirmatory cells was computed.

Owner of this document: `ccf-experiment-designer`. Executor to be written at `.rb_work/rb_endpoints.py`.
Round directory: `results_regime_b_endpoints/round_v1/`.

---

## Mode

`design` (protocol + pre-registration + result-table schema). Not `result-presentation`: no
confirmatory value exists yet.

**`ccf-humanization` preflight: not loaded, deliberately.** The skill requires it only when the artifact
is publication-facing prose, a final manuscript table/caption, or a publication method description.
This document is an internal protocol and preregistration; nothing here is manuscript text. If any cell
of it is later proposed for the paper, the humanization preflight runs at that point.

---

## Question

Regime A excludes client-windows whose `(client, stratum)` carries `pi_tar = 0`; regime B keeps them
(the old rule, and the Design-off setting). On U-Air, regime B buys `RMSE_mu −6.4 %` and
`Delta_group −6.9 %` at C0 (round-3 finding). The manuscript's own Design-removal row prices the same
trade: `Delta_group −6.943 %`, `RMSE_mu −6.885 %`, **`Delta_c-s +4.990 %`** and tail `−7.221 %`
(`tab:e4_ablation`, Holm-adjusted).

**The question this round answers:** in regime B, what happens to the two endpoints the RMSE/group
result does **not** cover — the calibration endpoint `Delta_c-s` (a paper metric) and the decision
endpoint `E_dec` (the screen's decision endpoint)? Is the ~6 % prediction+group gain paid for on the
calibration and decision side, and by how much?

---

## Claim-evidence matrix

| Claim under test | Reviewer question | Evidence needed | Dataset | Arms | Metrics | Result | Status |
| --- | --- | --- | --- | --- | --- | --- | --- |
| Regime B costs calibration alignment | is the RMSE gain free? | paired A/B contrast, 20 seeds | U-Air | FedAvg A vs FedAvg B | `Delta_c-s` (↓) | TBD | planned |
| The same holds for the oracle pair | does it depend on the weighting? | paired A/B, 20 seeds | U-Air | oracle Design-on vs Design-off | `Delta_c-s` (↓) | TBD | planned |
| Regime B costs decision quality | is the gain free at the decision endpoint? | checkpoint replay, gated | U-Air | FedAvg A vs FedAvg B | `E_dec` (↓), `E_mix`, `E_group` | TBD | planned |
| The trade-off is not a C0 accident | does it hold under all six conditions? | 6 conditions × 20 seeds | U-Air | both pairs | all four | TBD | planned |

---

## Dataset / benchmark needs

U-Air (the block where the support loss exists and where `E_dec` is defined). No new data, no new
traces, no training. SensorScope is **out of scope**: its support cost is ≈0 and `E_dec` is not defined
there (`want_dec = ds in {"uair"}`).

Everything needed already exists, verified read-only before this document
(`tables/RECON_AVAILABILITY.csv`): 24 cells (2 arm pairs × 6 conditions) × 20 seeds = **480 runs**, each
with `final_metrics.json`, `delta_c_s_summary.json` and `checkpoints/final.pt`.

---

## Confirmed method / baseline versions

| side | arm pairing | source | rule |
| --- | --- | --- | --- |
| A | `fedavg_window` | `results_h_headroom/round_v3/runs/<cond>/uair/fedavg_window/seed*` | `m_total = 0` when `pi_tar = 0`; reproduces the frozen artifact exactly on 20/20 seeds |
| B | `fedavg_window` | `results_h_headroom/round_v1|round_u1/runs/<cond>/uair/fedavg_window/seed*` | keeps the same client-windows |
| A | `raven_simoracle` | `artifacts/e3_formal_runs_r1/runs/uair/raven_simoracle/seed*` | Design on (frozen artifact) |
| B | `raven_simoracle_nodesign` | `results_h_headroom/round_v1|round_u1/runs/<cond>/uair/raven_simoracle_nodesign/seed*` | `uses_design_ratio=False` |

The A/B FedAvg pair is a **proven single-variable contrast**: identical `EventTrace_hash` *and*
identical `config_hash` on 20/20 seeds (round-3 `tables/REGIME_AB_FEDAVG.csv`).

---

## Baseline matrix

```text
Baseline: regime A itself (the frozen/manuscript rule) — the reference side of a paired contrast.
Why included: a level without a reference cannot be read; the manuscript prints A-side numbers.
Source: frozen 2026-08-11 artifacts + round_v3 re-runs (exact reproduction, 20/20).
Implementation source: same runner, same trace, same config; only the m_total rule differs.
Fairness constraints: identical seeds, identical traces (hash-checked), identical config hashes.
Expected metric: Delta_c-s, E_dec, E_mix, E_group, plus RMSE_mu and Delta_group as the already-known side.
Can run? yes — read-only for Delta_c-s; checkpoint replay for the E-* endpoints.
If missing, reason: n/a.
```

Secondary reference, not a baseline: the screen's stored `E_dec` values for 40 frozen U-Air cells are
used as a **positive control** for the replay code, never as a comparison arm.

---

## Main experiments

### P0 — calibration endpoint (`Delta_c-s`), read-only

`Delta_c-s = sum_{k,s} |Pi_hat_ks - pi_tar_ks|` on the `client × opportunity_stratum` support
(`src/raven_mcs/e3/delta_cs_rho/delta_cs_v6.py`), read from each run's `final_metrics.json` and
cross-checked against `delta_c_s_summary.json` (must agree to 1e-12; the summary also supplies
`pair_support_size` and `overlap_size`).

* **Primary cells:** the FedAvg pair, all six conditions, 20 seeds. C0 is reported as *reconnaissance*
  (see the disclosure below) and the five other conditions as confirmatory.
* **Secondary cells:** the oracle pair, all six conditions (Design-on vs Design-off). Unseen.
* **Support guard:** `pair_support_size` must be 288 in every cell, in both regimes. If any cell's
  support differs, that cell is `unpaired` and is excluded (it is not averaged over).
* **Reproduction guard:** the A-side FedAvg `Delta_c-s` must equal the frozen artifact's exactly
  (20/20 at C0, already verified in reconnaissance).

### P1 — decision endpoint (`E_dec`) and its decomposition, checkpoint replay

For each cell: rebuild the runner from the stored checkpoint with the cell's **own trace**, predict on
the test split, and compute the endpoints with the screen's own function
(`.s1_work/s1_screen.py::_endpoints_from_pred`, imported, not re-implemented) at the screen's threshold
`T_DEC = 35.0`:

* `E_dec = sum_u w_u * 1{(y_pred_phys > T_DEC) != (y_true_phys > T_DEC)}`, `y_phys = y * sigma + mean`;
* decomposition (new, pre-declared): `missed = sum w * 1{true > T, pred <= T}`,
  `false_alarm = sum w * 1{pred > T, true <= T}`, so `E_dec = missed + false_alarm`;
* `E_mix`, `E_group`, `base_rate` as the screen defines them.
* **Scale declaration.** Regime-B runs carry no `metric_scale_policy.json`. The experiment declares the
  physical scale from the A side: `sigma = 17.36325121670317`, `conversion = OFFLINE_LINEAR_CONVERSION`,
  `dataset = uair` — the value the frozen artifacts declare in 20/20 cells per condition, and which the
  screen itself asserts must equal `dataset.target_std`. The executor must (i) assert that equality on
  every A-side cell, and (ii) apply that single declared sigma to **both** sides. No per-cell scale and
  no fitted scale.
* **Replay gate (the screen's rule, unchanged):** `|RMSE_mu_recomputed - RMSE_mu_stored| <= 1e-12` on
  non-trigger cells. Cells on `TRIGGER_SEEDS = {30007, 30016, 30018}` are recorded with their offset
  (the screen pre-declared exactly this) and are **excluded from the primary contrast**; a sensitivity
  that includes them is reported separately.
* **Positive control:** the executor must reproduce the screen's stored `E_dec`, `E_mix`, `E_group` and
  `base_rate` for the 40 evaluable frozen U-Air cells (`SCREEN_RUNS.csv`) to 1e-12 before any regime-B
  cell is read. This validates the replay path against the only stored endpoint values that exist.
* **Primary cells:** FedAvg pair, C0, the 17 non-trigger seeds. Then the other five conditions.

---

## Ablations

| Variant | Component changed | Mechanism tested | Metric | Interpretation rule (fixed now) |
| --- | --- | --- | --- | --- |
| FedAvg A → B | the `m_total` rule | the support/aggregation regime | all four | the primary single-variable contrast |
| oracle Design-on → off | `uses_design_ratio` | whether the price depends on the weighting | all four | if the two pairs agree in sign and size, the price is a regime property; if they disagree, it is arm-specific |
| threshold sweep `T ∈ {25, 35, 50, 75}` µg/m³ | the decision threshold | whether the decision endpoint is saturated | `E_dec`, `missed`, `false_alarm`, true-exceedance share | **descriptive only, no per-threshold inference, no best-threshold selection**; a threshold with zero correct positives in both regimes is labelled `degenerate_at_T` |

---

## Robustness / failure / efficiency

* Robustness = the six conditions (tilt strength, tail scale, backbone, target law) and the two arm
  families. No new stress axes are invented.
* Failure mode already observed and handled: the S1 screen's City Scanner replay failed and closed its
  round. This round does not touch City Scanner, and its gate is `Delta_c-s` + replay exactness on
  U-Air only.
* Efficiency: no training. `Delta_c-s` is a file read; `E_dec` is one forward prediction per run
  (the screen's own per-row wall time was 0.8–6 s). No compute claim is made from this round.

---

## Smoke scope and deduplication

Two non-duplicative checks only, each on a unique changed critical path:
1. the 40-cell positive control against stored `E_dec` (validates the replay path);
2. two seeds × one condition end-to-end for the B side (validates that the B-side path resolves run
   dirs, trace dirs and the declared scale).
No repeated smoke grid, no defensive cases, and neither check is reported as evidence.

---

## Decision rule (fixed before computation)

For each endpoint and each cell set, the per-seed paired relative change is
`r_s = (M_B,s - M_A,s) / M_A,s`, positive = regime B worse. Report `n`, mean, sd, Student-t CI
(df = n-1), and the number of seeds with `r_s > 0`. Labels (AM-5 vocabulary), fixed now:

| condition on the CI | label |
| --- | --- |
| CI entirely inside `(-0.10, +0.10)` | `equivalent_zero` |
| CI entirely above `+0.10` | `harm` |
| CI entirely below `-0.10` | `benefit` |
| CI excludes 0 but spans a band edge | `directional, below band` (reported with the CI, not as harm/benefit) |
| CI contains 0 and spans a band edge | `inconclusive` |

Band = `±0.10` relative, the record's practical-significance convention, **not a hypothesis test**. The
band, the endpoints and the cell sets are not adjusted after values are seen. `E_dec` cells whose
`missed` component equals `base_rate` in **both** regimes are additionally labelled
`degenerate_at_T`: the contrast then lives entirely in the false-alarm part and is reported as a
false-alarm contrast, never as "decision quality".

---

## Stop rules

1. Replay gate failure (`> 1e-12` on a non-trigger cell) stops the round for that cell set; no waiver,
   no tolerance loosening.
2. Positive-control mismatch (`> 1e-12` on any of the 40 stored cells) stops P1 entirely.
3. A-side `metric_scale_policy.sigma != dataset.target_std` (screen's own assertion) stops P1.
4. Any cell whose `pair_support_size != 288`, or whose A/B trace hashes disagree, is reported `unpaired`
   and excluded — not averaged over, not repaired.
5. Missing checkpoint or missing `final_metrics.json` in a primary cell stops that cell set.
6. The round computes no new training run and edits no manuscript file.

---

## Forbidden claims

* No claim that regime B is "better" or "worse" overall: the result is a **trade-off vector**, and the
  endpoints move in opposite directions by construction of the question.
* No decision-quality claim from a saturated `E_dec`; the `missed`/`false_alarm` split must be printed
  next to every `E_dec` number.
* No equivalence claim from a CI that merely contains zero, and no significance claim from a CI that
  excludes zero but spans the band (`directional, below band`).
* No pooling of conditions into a single number, no pooling across datasets, no SensorScope extension.
* No use of the threshold sweep to pick a favourable threshold, and no re-labelling of a degenerate
  threshold as a result.
* No claim that the calibration price *causes* the prediction gain, or the reverse; the round measures
  co-movement of endpoints along one rule change.
* No manuscript change and no scorecard claim from this round.

---

## Result tables (schema; all cells TBD until executed)

**T1 — calibration endpoint, paired**

| Cell set | regime A `Delta_c-s` (mean ± sd) | regime B | paired change (mean [95 % CI]) | seeds `r>0` | label |
| --- | --- | --- | --- | --- | --- |
| FedAvg, C0, 20 seeds | TBD | TBD | TBD | TBD | TBD |
| FedAvg, C1–C5, 20 seeds each | TBD | TBD | TBD | TBD | TBD |
| oracle Design-on vs off, C0–C5 | TBD | TBD | TBD | TBD | TBD |

**T2 — decision endpoint, paired (non-trigger seeds)**

| Cell set | `base_rate` | A `E_dec` | B `E_dec` | A missed / false-alarm | B missed / false-alarm | paired change [95 % CI] | label |
| --- | --- | --- | --- | --- | --- | --- | --- |
| FedAvg, C0, 17 seeds | TBD | TBD | TBD | TBD | TBD | TBD | TBD |
| FedAvg, C1–C5 | TBD | TBD | TBD | TBD | TBD | TBD | TBD |
| oracle pair, C0–C5 | TBD | TBD | TBD | TBD | TBD | TBD | TBD |

**T3 — companion endpoints (context, same pairs)**

| Cell set | `RMSE_mu` A→B | `Delta_group` A→B | tail RMSE A→B | `E_mix` A→B | `E_group` A→B |
| --- | --- | --- | --- | --- | --- |
| FedAvg, C0–C5 | TBD | TBD | TBD | TBD | TBD |
| oracle pair, C0–C5 | TBD | TBD | TBD | TBD | TBD |

**T4 — threshold sweep (descriptive)**

| threshold µg/m³ | true exceedance share | A `E_dec` (mean) | B `E_dec` (mean) | A missed/false-alarm | B missed/false-alarm | degenerate? |
| --- | --- | --- | --- | --- | --- | --- |
| 25 / 35 / 50 / 75 | TBD | TBD | TBD | TBD | TBD | TBD |

---

## Missing values

Explicit and never substituted: `not evaluable` (no scale), `unpaired` (support/hash), `replay-inexact`
(trigger seeds), `degenerate_at_T` (no correct positives), `missing` (absent run). No cell is filled by
a simplified run, by a proxy metric, or by interpolation. A cell with `n < 20` is printed as `n < 20`.

## Pinned inputs

`INPUTS.sha256` pins every input this design reads: the screen executor
(`.s1_work/s1_screen.py`, `19958a13…`), the screen's own preregistration (`.s1_work/PREREG_S1.md`,
`e9ab6f1e…`), the `Delta_c-s` implementation (`delta_cs_v6.py`, `580bd1d6…`), an A-side scale policy
(`b63547f9…`), the stored screen results (`SCREEN_RUNS.csv`, `a7291d3e…`), and the round-3 pairing
tables. Cross-check that comes for free: the pinned `PREREG_S1.md` hash equals the `prereg_sha256` that
`SCREEN_DECISION.json` records, so the screen's pre-registration is intact and this design cites the same
file the screen pinned.

---

## Reconnaissance disclosure (pre-registered honesty item)

Before this document, one read-only extraction was performed to confirm the metric is well-posed:
`tables/RECON_DELTA_CS_AB.csv`, FedAvg C0, 20 seeds. It found `pair_support_size = 288` in both regimes
(so the contrast is apples-to-apples), exact A-side reproduction of the frozen artifact, and
`Delta_c-s` worse in regime B on 20/20 seeds (mean 1.262132 → 1.313777, +4.09 % by ratio of means).
It also established the availability matrix and revealed that `E_dec` is (i) evaluable on only 40 of the
100 stored U-Air cells, and (ii) **saturated** at `T_DEC = 35` on those 40: `base_rate = 0.085954` in
every row, `E_dec >= base_rate` in 40/40, and `E_dec == base_rate` exactly in 18/40 — i.e. no stored run
predicts a single exceedance correctly, and the whole variation lives in the false-alarm part.

Consequences, fixed now: C0 FedAvg `Delta_c-s` is **reconnaissance, not confirmatory**; the
`missed`/`false_alarm` decomposition and the `degenerate_at_T` label are mandatory rather than optional;
the sweep is added as a declared diagnostic so that a saturated primary threshold cannot silently
produce a null; and the five other conditions plus the whole oracle pair remain genuinely unseen and
carry the confirmatory weight.

---

## Execution priority

| Priority | Experiment | Claim defended | Cost | Dependency | Where | Stop condition |
| --- | --- | --- | --- | --- | --- | --- |
| P0 | `Delta_c-s` paired A/B, FedAvg C1–C5 + oracle pair C0–C5 (read-only) | the trade-off is price-side real and general | very low (file reads) | none | this round | support ≠ 288, hash mismatch |
| P1a | replay positive control, 40 stored cells | the replay path is the screen's | low | none | this round | any mismatch > 1e-12 |
| P1b | `E_dec` + decomposition, FedAvg C0 non-trigger (34 runs) | decision-side price at the screen's threshold | low (one forward pass per run) | P1a | this round | replay gate |
| P2 | `E_dec` for C1–C5 and the oracle pair (440 runs) | generality of the decision-side price | medium (minutes) | P1b | appendix | replay gate |
| P3 | threshold sweep (descriptive) | saturation is a threshold artefact or not | low | P1b | appendix | none (descriptive) |

No item in this table requires training, GPU time, new traces, or a manuscript edit.

---

## No-fabrication status

```text
No confirmatory experimental result has been generated by this design. Every cell in T1-T4 is TBD.
The only values quoted above are (a) stored values from files named in the text and (b) the labelled
reconnaissance extraction, whose file and provenance are given. No placeholder is filled by a
simplified run, and no threshold, scale, band or cell set will be changed after values are seen.
```

---

## Next CCFA owner

* `ccf-experiment-designer` — this document (design + preregistration).
* Executor `.rb_work/rb_endpoints.py` (P0/P1), then results under `results_regime_b_endpoints/round_v1/`.
* `ccf-integrity-auditor` — after execution, for number/claim consistency against the result tables.
* `ccf-paper-writer` — only if the user later asks for manuscript text, and only after the
  `ccf-humanization` preflight; nothing in this design is manuscript text today.
