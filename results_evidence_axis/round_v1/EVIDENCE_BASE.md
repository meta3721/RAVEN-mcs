# Evidence axis — evidence base (measured 2026-10-06)

Purpose: state what is measured, in numbers, before any new Evidence-axis experiment is
designed. Every value here is read from a named file or produced by a named read-only
probe; no training ran and no `src/`, manuscript, `artifacts/` or existing `results_*`
file was touched.

Probes: `.rb_work/evidence_headroom.py`, `evidence_concentration.py`,
`evidence_tdrive_conc.py`, `evidence_mask_concentration.py`,
`evidence_concentration_counterfactual.py`.
Outputs: `.rb_work/evidence_headroom/{HEADROOM,TARGET_CONCENTRATION,MASK_CONCENTRATION,CONCENTRATION_COUNTERFACTUAL}.csv`.

---

## 1 The deployment targets are nearly uniform, so stratifying by them barely moves a metric

Concentration of the frozen deployment target (1 − H/H_max; 0 = uniform, 1 = all mass on
one cell):

| dataset | level | n cells | top-1 share | top-5 share | cells for 50 % of mass | 1 − H/H_max |
| --- | --- | ---: | ---: | ---: | ---: | ---: |
| SensorScope | group `mu` | 220 | 0.53 % | 2.64 % | 95 | **0.0027** |
| SensorScope | client×stratum `pi_tar` | 440 | 0.35 % | 1.76 % | 159 | **0.0081** |
| U-Air | group `mu` | 144 | 0.79 % | 3.93 % | 66 | **0.0010** |
| U-Air | client×stratum `pi_tar` | 288 | 0.63 % | 3.14 % | 80 | **0.0791** |
| T-Drive | group `mu` | 4 | **51.44 %** | 100 % | 2 | **0.1407** |
| T-Drive | client×stratum `pi_tar` | 17 483 | 0.031 % | 0.154 % | 2 632 | **0.0502** |

T-Drive's real four-group target is genuinely concentrated — but its **stratum-level**
target, which is the support the method weights, is as diffuse as the other two. The
concentration that exists lives at the h-level, above the level the aggregation acts on.

## 1a Correction to the detectable-effect convention (audit EV-2)

The manuscript reports paired minimum detectable effects of 0.17–0.36 pp (SensorScope) and
0.70–0.80 "points" (U-Air). The evidence-axis audit (`ccfa-review-reports/
raven-mcs-evidence-axis-audit.md`, `EV-2`/`EV-3`) cross-checked those against
`results_gatekeeping/round_v1/A1_POWER.csv`, whose own `mde80` cell is 0.42–0.45 % on
SensorScope and **0.08–0.09 %** on U-Air, i.e. the printed U-Air range is on a different
scale from the rest of its paragraph. Using the audited convention, U-Air's detectable
effect is *below* the magnitudes the endpoint could carry, so the correct reading of the
U-Air null is **"the design can see this size and the effect is absent"**, not "the endpoint
cannot see it".

Own recomputation of the `mde80` column disagrees with it and is left unresolved
(`.rb_work/evidence_headroom/MDE_RECONCILIATION.csv`): $2.802\,s_d/\sqrt{20}$ gives 0.00618 pp
(SensorScope) and 0.0649 pp (U-Air) absolute, which as a share of the frozen `RMSE_μ` means
is 0.078 % and 5.4 %, against the column's 0.445 % and 0.075 %. One of the two conventions
is wrong and must be settled before any number from it is printed.

## 2 What a fixed-checkpoint evaluation re-weighting can move — and what it cannot

`(uniform − target-weighted) RMSE_μ`, same model, per seed
(`HEADROOM.csv`, 20 seeds, both arms):

| dataset | uniform − target | best-single-group − target | worst-single-group − target | group error spread (worst/best) |
| --- | ---: | ---: | ---: | ---: |
| SensorScope | **+0.8208 %** (sd 0.0041) | −12.2 % | +14.1 % | 1.30× |
| U-Air (Design on) | **+0.2660 %** (sd 0.0082) | −70.9 % | +42.7 % | 4.0–5.1× |
| U-Air (Design off) | +0.2583 % (sd 0.0112) | −68.6 % | +44.6 % | 3.6× |

**Scope of this measurement (corrected).** These figures hold the checkpoint fixed and change
only the *evaluation* weights. They show that `RMSE_μ` and the uniform-weighted RMSE are
nearly the same function of the same predictions. They do **not** bound what a re-weighting
during *training* could do to the per-group errors, so they cannot be quoted as "the bound
on any target-constrained re-weighting", and the earlier drafts of this file did exactly
that. The same limitation applies to the concentration counterfactual in §3.

The paper's own measurements land at the same order: the recoverable-gain ceiling (fixed
class, true margins) is **H = −0.27 % to −0.68 %** on U-Air at every condition, with
`H_best_oracle` +5.2 % to +6.2 % coming from the Design-off/support contrast rather than from
evaluation reweighting (`results_h_headroom/round_v3/tables/H_SUMMARY.csv`); replacing the
two estimated margins with their true values moves `RMSE_μ` by −0.008 % (SensorScope) and
+0.040 % (U-Air) at 20 seeds. On the audited convention the paired minimum detectable effect
is 0.42–0.45 % (SensorScope) and 0.08–0.09 % (U-Air) — see §1a; the manuscript's printed
0.17–0.36 pp / 0.70–0.80 pp is the pair `EV-2` flags.

**Consequence (corrected).** On U-Air the whole evaluation-reweighting term (0.26 %) is
*larger* than the audited detectable effect (0.08–0.09 %), so the design can see effects of
that size; the measured member spread is 0.357 pp against a 0.08–0.09 % resolution, i.e. the
effect is visible and absent. On SensorScope the same statement holds a fortiori: the member
spread is 0.026 pp against a 0.42–0.45 % resolution, which is the familiar null. Neither is
a statement about training-time reweighting (see the scope note above).

## 3 Target concentration does not rescue the weighting term (evaluation-layer result)

Counterfactual on the 20 paired seeds, frozen checkpoints, no rule re-solved and **no
retraining under the concentrated target**. `w(C) = (1−C)·mu + C·mu_C`, where `mu_C` puts 5 %
of the groups' worth of mass on selected groups. Two selection rules: `label_free` (the
Design-on model's own worst-error groups — uses no arm comparison) and `disagreement` (an
upper bound that uses the arm difference).
`gap = 100·(RMSE_wo_design − RMSE_raven)/RMSE_raven`; negative = Design on better.

SensorScope (n = 20, cells mass in top 5):

| rule | C = 0 | 0.25 | 0.50 | 0.75 | 1.00 |
| --- | ---: | ---: | ---: | ---: | ---: |
| `label_free` | +0.005 % | +0.005 % | +0.004 % | +0.004 % | +0.004 % |
| `disagreement` | +0.005 % | +0.006 % | +0.007 % | +0.008 % | +0.009 % |

U-Air:

| rule | C = 0 | 0.25 | 0.50 | 0.75 | 1.00 |
| --- | ---: | ---: | ---: | ---: | ---: |
| `label_free` | −6.875 % | −6.551 % | −6.329 % | −6.167 % | −6.044 % |
| `disagreement` | −6.875 % | −7.161 % | −7.403 % | −7.614 % | −7.801 % |

**Scope (corrected).** Only the evaluation weights change here; neither arm is retrained
under the concentrated target, so the per-group errors are held fixed by construction. The
tables therefore speak about the evaluation layer only. The `C = 0` column is *not* a
"composition effect": it is the Design-on/Design-off difference, i.e. the alignment factor
itself, and the two arms differ in their active sets as `round_v3` established, not only in
their weights.

Reading: the ~6.9 % U-Air gap is present at `C = 0` and is **not** produced by
concentration; the most favourable concentration rule multiplies it by 1.13×, and the
label-free rule makes it slightly *smaller*. On SensorScope concentration changes the gap
by +0.004 pp across the whole range, and the label-free rule makes it slightly smaller. Within
the evaluation layer, concentrating the target does not reveal a weighting effect. This does
**not** cover training under a concentrated target, which was not run; see §3 scope note.

## 4 Masking did not test concentration, and the gate-dose driver's ρ is a support statistic

`MASK_CONCENTRATION.csv`: the instruction's mask removes positive keys and renormalizes.

| dataset | m | ρ | positive keys | top-1 share | top-5 share | 1 − H/H_max |
| --- | ---: | ---: | ---: | ---: | ---: | ---: |
| SensorScope | 0 | 0.0000 | 440 | 0.35 % | 1.76 % | 0.0081 |
| SensorScope | 0.40 | 0.3881 | 264 | 0.58 % | 2.88 % | 0.0921 |
| U-Air | 0 | 0.3544 | 216 | 0.63 % | 3.14 % | 0.0791 |
| U-Air | 0.20 | 0.4662 | 173 | 0.82 % | 4.09 % | 0.1214 |

The rise in 1 − H/H_max is an artefact of the shrinking support (220 → 264 cells), not mass
concentration: the top-5 share never exceeds 4 %. The masked target stays flat. Separately,
masking removes mass from cells that carry *zero* mass under the production target, so the
factor ρ (share of delivered units on non-positive keys) changes the **reachable** support,
it does not concentrate the target.

## 5 What the endpoint responds to: the support factor, at many times the detectable effect

The largest reproducible movements of `RMSE_μ` are all support/reachability changes:

| quantity | movement | source |
| --- | ---: | --- |
| regime A → B (support factor, n = 20, 6 conditions) | `RMSE_μ` −5.2 … −6.4 %, `Δ_group` −5.9 … −9.2 %, `Δ_c-s` **+3.1 … +4.8 %** | `results_regime_b_endpoints/round_v1/P0_REPORT.md` |
| U-Air Design-removal ablation (Holm-significant) | `RMSE_μ` −6.885 %, `Δ_group` −6.943 %, `Δ_c-s` +4.990 % | manuscript §ablation |
| the arms' own paired gap at `C = 0` | −6.875 % | `CONCENTRATION_COUNTERFACTUAL.csv` |
| replacing estimated margins with true ones, one member | `RMSE_μ` −0.008 % / +0.040 % | manuscript ceiling subsection |

The one quantity that tracks that lever is whether a window's contributing clients actually
cover the target's positive cells. Section 2.3 of the handoff records the manuscript's own
pointer to it ("where a window's active clients do cover the target's groups, the group
term regains its effect"), and the regime-B overlap rises from 83–98 keys (A) to 107–130
(B) while the calibration price is paid (`P0_REPORT.md` §2).

The two arms of that lever also differ in their active sets, not only in their weights
(`round_v3`: Design on and off do not select the same client–windows). So the 5–9 % is a
support/set difference, and any design that doses support is measuring the Design factor
itself — which is the alignment factor, not a proxy for it.

## 6 The decision-quantity route is closed on U-Air

At the 35 µg/m³ endpoint the base rate is 0.086 and neither arm has decision skill: the
frozen rule retains 33.8 % of the exceedance mass, the Design-off rule 0.1 %, and the
threshold sweep is degenerate at 25 (both over-predict), 50 and 75 (both miss everything).
No declared threshold gives either arm skill, so the endpoint cannot adjudicate the
trade-off (`P1_REPORT.md` §2, `P2D_REPORT.md`).

## 6a How much of the deployment target the estimator can even see (measured)

Per-window exposure = the target-positive mass covered by that window's contributing
clients, computed from the frozen traces alone. Labels are the processed
`opportunity_stratum` (`window_dataset.py` L118 — the space the runner's own client→stratum
map is built in), not the trace's `opportunity_features` label, which is a different space
on SensorScope.

| dataset | windows | R_mass mean (active windows) | R_mass max (best window) | covered target cells / window | contributing clients / window |
| --- | ---: | ---: | ---: | ---: | ---: |
| SensorScope | 100 | **0.666 %** | 1.70 % | 2.58 | 2.58 |
| U-Air | 80 | **0.885 %** | 2.57 % | 1.93 | 2.59 |

Between-seed spread of that exposure is ±0.0004 (SensorScope) / ±0.0006 (U-Air) — across 20
frozen traces the factor barely moves, while the within-run window spread is 0.0034 / 0.0061.
The ceiling is not the problem: the client population's training-atom repertoire covers
**100 %** of the target-positive mass on both datasets (SensorScope 440/440 cells; U-Air
216/216, with 25 % of training cells off-target). A dosed design could therefore span
exposure from ~0 to 100 % if traces were regenerated; the frozen traces span almost none of
it (`REACHABILITY.csv`, `REACHABILITY_CEILING.csv`).

U-Air's windows additionally cover 0.66 off-target cells per window on average: about a
quarter of what its clients touch carries no target mass. That is the situation the Design
gate exists for, and it is a property of the client↔support overlap, not of the target.

## 6b The 6.9 % is the Design factor itself, and it is not explained away

The Design-on / Design-off contrast at `C = 0`, same model classes, same traces, same target,
same 288-key `Δ_c-s` support (20 paired seeds): **−6.875 %** on `RMSE_μ`
(`CONCENTRATION_COUNTERFACTUAL.csv`). Round_v3 established that the two arms' **active sets
differ**, so this is not a pure weighting contrast either: the sets and the weights move
together, and that is what turning the Design gate off does.

**Withdrawn.** An earlier draft of this file called that movement "aggregate composition, not
alignment". That is a relabel: Design *is* the alignment factor, and a reviewer will say so.
The measurement supports a narrower statement:

* the *evaluation-layer* reweighting term is 0.26 % (U-Air) / 0.82 % (SensorScope) with the
  checkpoint fixed (§2), and it does not grow when the target is concentrated (§3);
* the *Design factor* moves `RMSE_μ` by 6.875 % and `Δ_c-s` by 3–5 % by changing which
  client–windows enter the aggregate and with what weights (§5).

Which of those two — the weight vector or the participating set — carries the 6.9 % is **not
identified** by the measurements on disk. Identifying it needs an intervention that changes
one while holding the other, and that experiment has not been run.

## 7 What this means for the E1 repair condition

The round-12 condition is: headroom above the run's own detectable effect, a decision
quantity whose base rate is not saturated, and pre-registration before running. What the
measurements establish:

* the prediction endpoint's response to aggregation weights is small and, at the audited
  resolution, **measured to be absent** (§1a, §2) — not unresolved;
* the decision endpoint is saturated on U-Air at every declared threshold (§6), so it cannot
  adjudicate;
* the largest effect on the endpoint is the Design factor itself, at 6.875 % / `+3–5 %`,
  which changes the participating set together with the weights (§6b).

So the honest Evidence-axis statement is the measured null plus its resolution, and the open
identification question of §6b — not a claim that alignment buys accuracy, and not a claim
that the endpoint is blind. No claim is made here about any unrun experiment's outcome.
