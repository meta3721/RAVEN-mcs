# Integrity audit — the two new passages (`numeric-audit`)

Skill: `CCFA-Skills/ccf-integrity-auditor` (`SKILL.md`; the skill is not in the session
catalog, read from disk as the handoff §15 records).
Mode: **`numeric-audit`** — numbers, sources, direction, and text/target agreement.
Artifact audited: `TO_OVERLEAF_paper_tmc_r1_clean/main.tex`
sha256 **`68D9B44F17A4E48D7D010C5BB83EFC4C0951B60BC3EED39A6529B56AC4FC700B`**
(the version the handoff names; confirmed independently).
Reconstruction script: `.rb_work/audit_new_paragraphs.py` (read-only).

Passages audited: `L2152–L2167` ("Why the weights leave the prediction endpoint flat")
and `L2199–L2215` (the second half of Limitations).

**No manuscript or ledger file was edited by this audit.**

---

## 1 Claim-evidence matrix

`OK` = the number is reproduced from the named primary source within its printed precision.
`FAIL` = reproduced but not within the printed claim as literally stated.

| # | location | claim | source I checked | recomputed | verdict |
| --- | --- | --- | --- | --- | --- |
| A | L2154 | frozen `E_min = 3` | `src/raven_mcs/aggregation/methods.py` L345/415/482 `e_min: float = 3.0`; L525 `e_min=min(self.e_min, n_active)`; caller passes no override; `FullWindowRunner` has no `e_min` field | default 3.0, no override anywhere on the `run_e3_real` path | **OK** |
| B | L2154–L2155 | `Ē_r = min(3, K_r)`; `‖α‖² ≥ 1/K_r` with equality only at `1/K_r` | `src/raven_mcs/aggregation/feasibility.py` L15–21 `ess_ball_bound = min(e_min, n_active)`; constrained `cp.sum_squares(alpha) <= 1/e_bar` (`p2_cvxpy.py` L113) | the bound is exactly as stated; by Cauchy–Schwarz on the simplex the minimum of `‖α‖²` is `1/K_r`, attained only at uniform | **OK** (theory) |
| C | L2156–L2160 | a window with `K_r ≤ 3` "admits the uniform weights alone"; "in those windows (P2) returns uniform weights whatever its objective" | frozen `window_metrics.json`, 60 runs | feasible set: **OK**. Returned weights: see **F1** below | **OK with caveat** |
| D | L2157–L2158 | `78.6 %` of the `1877` active windows on SensorScope have `K_r ≤ 3` | `artifacts/e3_formal_runs_r1/runs/sensorscope/raven/seed*/window_metrics.json`, seeds 30001–30020 | **1877** windows, share **0.7858 (78.58 %)**; `K_r` min 1 max 7 mean 2.58 | **OK** |
| E | L2158–L2159 | `90.2 %` of `1402` (U-Air, Design on) | same tree, `uair/raven` | **1402** windows, share **0.9016 (90.16 %)**; min 1 max 6 mean 2.08 | **OK** |
| F | L2159 | `79.0 %` of `1515` (U-Air, Design off) | `artifacts/e4_core_mechanism_ablation_r1/runs/uair/raven_wo_design/seed*` | **1515** windows, share **0.7901 (79.01 %)**; min 1 max 7 mean 2.59 | **OK** |
| G | L2163–L2165 | largest group `0.53 %` (220 groups, SS) / `0.79 %` (144 groups, UA) | `.rb_work/evidence_headroom/TARGET_CONCENTRATION.csv` + recomputation from the frozen target artifacts | max `μ` **0.00528 (0.528 %)** / **0.00786 (0.786 %)**; 220 / 144 groups | **OK** |
| H | L2162 | projection over uniform server weights `+0.768` and `+0.286` pp | pre-existing, `main.tex` L81, L1833–L1836, L2092–L2093 | not a new number; the sentence re-invokes the round's own established pair | **OK** (no new claim) |
| I | L2199–L2201 | arrival validation misstates risk by `−4.11` to `−4.12 %` (SS) and `+0.27` to `+0.62 %` (UA), nine configurations | `results_estimand_selection/round_v1/SELECTION_DECISION.json` → `method_b` | SS `−0.04117 … −0.04113`; UA `+0.00267 … +0.00620`; 9 configurations each | **OK** |
| J | L2202–L2204 | "selects the same configuration as the deployment target on all 20 seeds of both datasets" | same file | disagreement rate **0.0000** on both; median Kendall τ **1.000**; mean regret **0.000000** | **OK** |
| K | L2205–L2207 | masking up to `40 %` of positive target keys raises `ρ_r` from `0` to `0.388` | `results_gate_dose/round_v1/{RHO.csv,MASKS.json}` | `m = 0.40` masks **176 of 440** = **40.00 %**; `ρ = 0.388138`; `m = 0` gives `ρ = 0` | **OK** |
| L | L2207 | SS "without a prediction cost of Design above `0.17 %`" | `results_gate_dose/round_v2/tables/DOSE_SUMMARY.csv` | level means `−0.00005, +0.00142, +0.00175, +0.00059` → largest **+0.1747 %** | **FAIL** (see F2) |
| M | L2207–L2208 | UA cost stays `6.6 %–7.5 %` for `ρ_r` between `0.354` and `0.466` | same table | r_RMSE `+0.07457, +0.06995, +0.06638`; `ρ` `0.3544, 0.4188, 0.4662` | **OK** |
| N | L2210 | on NSW-Traffic a window carries `12.1` active clients on average | `results_new_block_traffic/round_v1/S0_FOLLOWUP.json` → `N1_debt_cal`, recomputed from `artifacts/e3_formal_runs_r1/runs/traffic/debt_cal/seed*/window_metrics.json` | **12.0809** over 1990 active windows (`≤2` share 0.0683) | **OK** |
| O | L2211–L2212 | four frozen federated members agree on `RMSE_μ` within `0.002 %` | `S0_FOLLOWUP.json` → `federated_arms_RMSE_mu_mean` | max−min = `1.5e-05`; `/mean` = **0.00149 %** | **OK** |
| P | L2213–L2214 | window FedAvg `2.8 %–3.0 %` above a centralized model for every budget `2`–`20` steps | `results_new_block_traffic/round_v1/S1_LADDER.csv` → `ratio_to_c` | `+2.96 %, +2.81 %, +2.78 %, +2.91 %` at `2, 5, 10, 20`; budgets correct | **OK** |

18 of 20 claims reproduce. Two do not, in the same way and with the same cause.

## 2 Numeric consistency findings

### F1 — L2156/L2160: the returned weights are not exactly uniform (low severity, disclosed, wording)

The mechanism claim is sound but the verb is stronger than the artifacts. On the frozen runs,
of **1475** SensorScope windows with `K_r ≤ 3`, only **368** carry exactly uniform `α`
(max deviation `< 1e-12`); the remaining **1107** differ from uniform by up to **9.17e-5**
(`seed30007` window 36: `α = [0.3332416, 0.3334146, 0.3333438]`).

I checked whether this falsifies the mechanism, and **it does not**: the same window satisfies
the binding constraint, `‖α‖² = 0.333333348` against the limit `1/K_r = 0.333333333`, a
violation of **+1.5e-8**, inside the solver's own acceptance gate (`≤ 1e-7`, `p2_cvxpy.py`
L193). So the feasible set really is the uniform point and the solver returns a point
*beside* it by interior-point tolerance — the very inaccuracy CLARABEL warns about on this
problem.

Consequence: `(P2) returns uniform weights whatever its objective` is true of the **feasible
set** and approximately true of the **output**. A reader who takes it literally could believe
the stored weights are exactly uniform. Low severity because the deviation (9e-5) is four
orders below the `+0.768` pp effect the sentence is explaining, and because the paper does not
claim all windows are exactly uniform anywhere else.

**Safe edit (wording, not numbers):** "a window with `K_r ≤ 3` admits the uniform weights
alone, and (P2) returns weights within solver tolerance of uniform there whatever its
objective".

### F2 — L2207: `0.17 %` is one digit short of its own source (low severity, correctness)

The source's largest SensorScope level mean is **0.1747 %** (`m = 0.25`, 20 seeds,
`r_RMSE_mean = 0.001747`, interval `[0.000139, 0.003355]`). Printed to two decimals that is
`0.17 %`, and the manuscript writes "not above `0.17 %`" — but the value **is above** `0.17 %`
by `0.0047` pp. The claim as literally stated is false by one unit in the last printed place;
the underlying measurement is not in question.

This is a rounding-boundary defect, and it matters slightly more than cosmetics because the
same sentence uses `0.17` in the *ceiling* sense ("above"), so the reader is told a bound that
the data crosses.

**Safe edit (numbers):** write the level mean or a bound that contains it, e.g. "not above
`0.175 %`" or "at most `0.17`–`0.18 %`". Any of these is supported by the same table; none
changes a conclusion.

### F3 — L2199–L2201: mixed precision across two parallel ranges (presentational)

The SensorScope range prints to 4 significant figures (`4.11`, `4.12`) and the U-Air range to
2 (`0.27`, `0.62`), inside one sentence listing two versions of the same kind of quantity.
Both endpoints do round correctly from the source (`+0.267 → 0.27`, `+0.620 → 0.62`). No
number is wrong; the two ranges simply need not be quoted at different precisions.

**Safe edit (wording):** give both to 2 dp, or both to the precision of their intervals.

## 3 Citation metadata and context

No citation is added or changed by either passage, so `citation-audit` returns nothing new: the
sentences reference the paper's own tables, equations and earlier sections. This is recorded
rather than skipped because the mode was `numeric-audit`.

## 4 Severity

| finding | severity | reason |
| --- | --- | --- |
| F2 (`0.17 %` vs `0.1747 %`) | **low, but a factual overstatement** | a bound the data crosses by 0.005 pp; one token to fix |
| F3 (mixed precision) | **presentational** | both endpoints round correctly |
| F1 (uniform-weights verb) | **low** | feasible-set claim sound; returned point within solver tolerance |
| all other 17 claims | none | reproduced at the printed precision |

**Nothing in either passage is unsupported, invented, or directionally wrong.** No claim
depends on a source that does not exist, and no source contradicts a printed number except the
two rounding cases above.

## 5 What this audit does not settle

1. **The `eval_rq2`-sourced pair** (`+0.768` / `+0.286` pp, L2092–L2093) is pre-existing and I
   confirmed only that the new sentence repeats it, not that the pair itself is current. The
   `results_h_headroom/round_v3/tables/` tree does not carry a `+0.768`/`+0.286` label I could
   trace directly, so **those two numbers remain the round's, not this audit's**.
2. **The MDE pair at L2120** (`0.17`–`0.36` pp) is untouched by these passages and is the
   subject of audit item `EV-2`. This audit does not re-open it, but note that `0.17` now
   appears twice on the same page in two unrelated senses.
3. **The bundle-lag question** (handoff §13.1) and the **truncated scripts** (§13.2) are outside
   `numeric-audit`; they were not examined here.

## 6 No-invention status

Every recomputed value above was produced from the named artifact in this session
(`.rb_work/audit_new_paragraphs.py`), not copied from another round's summary. Where a source
could not be traced (H above) I said so instead of asserting the number. No manuscript,
ledger, or results file was modified by this audit.

## 7 Next CCFA owner

`ccf-paper-writer` for the two wording/rounding edits in §2 (F1, F2, F3) — all three are
one-token or one-clause changes that need the writing authorization the manuscript's own
policy requires. `ccf-paper-reviewer` remains the owner of the Evidence score, and per the
handoff §15 neither skill's conclusion may be merged into the other.
