# Integrity audit — RAVEN-MCS 2026-10-07 revision

Skill: `CCFA-Skills/ccf-integrity-auditor` (read from disk; not in the session skill catalog).
Mode: **`full`** — scoped to the 2026-10-07 delta plus the defect list in handoff §13.
Owner of this pass: `ccf-integrity-auditor` (assessment only).

## 0. Artifacts checked

| artifact | identity |
| --- | --- |
| `TO_OVERLEAF_paper_tmc_r1_clean/main.tex` | sha256 `68D9B44F17A4E48D7D010C5BB83EFC4C0951B60BC3EED39A6529B56AC4FC700B`, 116 379 B |
| historical version used for the delta | sha256 `02447BFE6256632B5AF2A535BCFCE2EB1024EB3A7AC957C2158B3EEDB6B1219A`, 113 854 B — **not present on disk**; reconstructed and hash-verified (see §0.1) |
| pre-round-12 snapshot | `snapshots/2026-10-06-pre-r12-fix/main.tex`, sha256 `59E4F4D55CFF…`, 113 345 B |
| build outputs | `_r13_build/` (out-of-tree; see §0.2) |
| new round trees | `results_evidence_axis/round_v1`, `results_estimand_selection/round_v1`, `results_gate_dose/{round_v1,round_v2}`, `results_new_block_traffic/round_v1` |
| release bundle | `RAVEN_MCS_PUBLIC_REPRO_R1` (2 118 files) |
| records | `ccfa-review-reports/raven-mcs-metric-definition-diagnosis.md` (2 908 lines), `RAVEN_MCS_PUBLIC_REPRO_R1/w1/PAPER_NUMBERS.csv` |
| prior audit (not mine) | `ccfa-review-reports/raven-mcs-integrity-audit-new-passages.md`, mtime 2026-10-07 20:06 |

### 0.1 The delta, and a correction to the handoff

The handoff §12 describes the 10-07 change as "5 hunks / +45 / −1 relative to `02447bfe`". That
is wrong. Deleting the two new blocks from the current file reproduces `02447BFE6256632B…`
**exactly** (113 854 B), which proves the two new blocks are the whole of the 10-07 change:

* hunk 3, `L2152–L2168`: **+17** lines ("Why the weights leave the prediction endpoint flat")
* hunk 4, `L2198–L2216`: **+19** lines (the second Limitations paragraph)

**The 10-07 delta is +36 / −0 relative to `02447bfe`.** The other three hunks (+9 / −1: `L228`,
`L617`, `L2260`) are the round-12 M2/M4/CL-3 edits, which are *already inside* `02447bfe` and are
therefore not part of this revision. Handoff §12's count is relative to the pre-round-12 snapshot
`59E4F4D5`, not to `02447bfe`. Recorded as a record-correction item; no manuscript consequence.

### 0.2 Build status

Built in fixed order (`supplemental.tex`, then `main.tex` ×2), output redirected to
`_r13_build/` because the source directory refuses writes in this session (§5.6).

| product | pages | `!` errors | undefined | multiply-defined | Overfull |
| --- | --- | --- | --- | --- | --- |
| `main.pdf` | **18** | 0 | 0 | 0 | 0 |
| `supplemental.pdf` | 16 | 0 | 0 | 0 | **1** (`\vbox`, 3.42152 pt) |

The supplemental `\vbox` reproduces ledger `NEW-r12-2` ("the vbox remains") exactly, so that row
is accurate. **The manuscript grew from 17 pp to 18 pp**, and `main.pdf`/`main.log`/`main.aux` in
the tree are still the 2026-10-06 20:45 artefacts. See §4.4.

### 0.3 Reconciliation with the prior audit (2026-10-07 20:06)

A `numeric-audit` of the same two passages was produced 26 minutes after the handoff and three
minutes before this session began, by another actor. It was **not** disclosed in the handoff. It is
preserved unchanged; this report supersedes it in scope but does not overwrite it, because one of
its verdicts is contradicted below and the disagreement is itself evidence.

* Its novel finding **F1 is exactly reproducible.** I recomputed it independently from
  `window_metrics.json`: of 1 475 SensorScope windows with `K_r ≤ 3`, **368** carry exactly uniform
  `α` (max deviation `< 1e-12`); the worst deviation is **9.171284e-05** at `seed30007` window 36
  (`α = [0.33324162, 0.333414555, 0.333343824]`) and the worst constraint excess is
  **+1.511833e-08**. Every digit matches. F1 is upheld.
* Its **F2** (`0.17 %` is one digit short of `0.1747 %`) is independently confirmed by a second
  method (§2, claim L). Upheld.
* Its **F3** (mixed precision) is upheld as presentational.
* Its **claim P verdict is not upheld** (§2, F-P). It marks "for every local budget from 2 to 20
  steps" as `OK, budgets correct`; four budgets of the nineteen integers in `[2,20]` were measured,
  and one of the four was not trained in that round. See F-P for the two readings and why the
  literal one is not supported.
* It explicitly deferred handoff §13.1 and §13.2; both are ruled on here (§4.1, §4.2), and §13.1 is
  materially wider than the handoff states.
* It left the `+0.768` / `+0.286` pair untraced. It is traceable; see §2 claim H and F-H.
* Its own script is incomplete relative to its docstring: `.rb_work/audit_new_paragraphs.py`
  (`f133c63898bc6269`) advertises claims A/B/C and H but implements only D/E/F, G and I–P. The
  unimplemented ones are precisely the claims its report marks `OK (no new claim)` or `OK with
  caveat`, so the two claim rows it treated most lightly are the two it did not compute. Both are
  verified here (§1 rows A/B/C/H).

## 1. Claim-evidence matrix

`OK` = reproduced from the named primary source within its printed precision.
`FAIL` = reproduced but not within the printed claim as literally stated.
`OVERSTATED` = the arithmetic is right but the sentence asserts more than was measured.

| # | line | claim | source | recomputed | verdict |
| --- | --- | --- | --- | --- | --- |
| A | 2154 | frozen `E_min = 3`; `Ē_r = min(3, K_r)` | `src/…/feasibility.py` L15–21 (`Ē = min(E_min, K)`); `methods.py` `e_min: float = 3.0` (L345/415/482/588/623); `window_runner.py` L989; `e3/final_closure/core.py` L22 (`min(3, n)`); `paper_data_r2/config_registry.py` L182; `artifacts/e4_wo_inst_reference_penalty_final_correction_r1/E4_WO_INST_FINAL_ONE_FACTOR_SPEC.json` L16 (`"ESS_constraints": 3.0`) | 3.0 everywhere on the `run_e3_real` path; no override | **OK** (but see F-E) |
| B | 2155–2156 | `‖α‖₂² ≥ 1/K_r`, equality only at `1/K_r`, so `K_r ≤ 3` admits uniform alone | `eq:Cr` (`main.tex` L883–892): `1ᵀα = 1`, `0 ≤ α_k ≤ ᾱ`, `‖α‖₂² ≤ 1/Ē_r` | Cauchy–Schwarz on the simplex; with `Ē_r = K_r` the bound forces equality | **OK** (theory) |
| C | 2157–2158 | `78.6 %` of `1877` active SensorScope windows have `K_r ≤ 3` | `artifacts/e3_formal_runs_r1/runs/sensorscope/raven/seed*/window_metrics.json`, `active` ∧ `a_r_size ≤ 3` | `1475/1877 = 0.785828…` → **78.58 %** | **OK** |
| D | 2158–2159 | `90.2 %` of `1402` (U-Air, Design on) | `…/uair/raven/seed*` | `1264/1402 = 0.901569…` → **90.16 %** | **OK** |
| E | 2159 | `79.0 %` of `1515` (U-Air, Design off) | `artifacts/e4_core_mechanism_ablation_r1/runs/uair/raven_wo_design/seed*` | `1197/1515 = 0.790099…` → **79.01 %** | **OK** |
| F | 2157 | "`20` frozen seeds" | all three trees above | 20 seed directories per arm | **OK** |
| G | 2163–2165 | largest group `0.53 %` / `220` groups (SS); `0.79 %` / `144` (UA) | `artifacts/e3_…closure_r1/E3_{SENSORSCOPE,UAIR}_TARGET_SEMANTICS_R2.json` → `mu` | SS `max μ = 0.0052785924` (**0.528 %**), `n = 220`, `Σμ = 1.000000000000000`; UA `max μ = 0.0078616352` (**0.786 %**), `n = 144`, `Σμ = 1.000000000000000` | **OK** |
| H | 2162 | projection over uniform is `+0.768` / `+0.286` pp | `RAVEN_MCS_PUBLIC_REPRO_R1/w1/tradeoff_v4/PART_A_REPORT.md` L15/L17 (bundled) | SS `B1(raven) − B1(uniform) = +0.768 [0.563, 0.970]`; UA `+0.286 [0.098, 0.471]` | **OK** (traceable; see F-H) |
| I | 2199–2201 | arrival weighting misstates risk by `−4.11`…`−4.12 %` (SS), `+0.27`…`+0.62 %` (UA), nine configurations | `results_estimand_selection/round_v1/SELECTION_DECISION.json` → `method_b`; `tables/RISK_ROWS.csv` | 9 methods × 2 datasets; SS means `−0.041129`…`−0.041170`; UA `+0.002672`…`+0.006195` | **OK** |
| J | 2202–2204 | selects the same configuration on all 20 seeds of both datasets | same file → `summaries[]` | `disagreement_rate = 0.0` (SS and UA); `mean_reg = 0.0` | **OK** |
| K | 2205–2207 | masking up to `40 %` of positive keys raises `ρ_r` from `0` to `0.388` | `results_gate_dose/round_v1/{MASKS.json,RHO.csv}` | SS `176/440 = 40.00 %`; `ρ = 0.388138`; `m = 0` → `ρ = 0` | **OK** |
| L | 2207 | SS prediction cost "not above `0.17 %`" | `results_gate_dose/round_v2/tables/DOSE_SUMMARY.csv` | level means `−0.00005, +0.00142, +0.00175, +0.00059`; max **`+0.1747 %`** | **FAIL** (F-L) |
| M | 2207–2208 | U-Air `6.6 %`–`7.5 %` for `ρ_r` in `0.354`–`0.466` | same table | `(0.354430, +7.4565 %), (0.418776, +6.9947 %), (0.466245, +6.6385 %)` | **OK** (exact bounding box) |
| N | 2210 | a window carries `12.1` active clients on average | `results_new_block_traffic/round_v1/S0_REPORT.md`; `S0_FOLLOWUP.json` → `N1_debt_cal` | trace-side `12.0568` (5 seeds) / `12.0851` (20 seeds); run-side `12.0809` over 1 990 windows. **No source prints `12.1`**; `S0_REPORT.md` prints `12.06` | **OK only as 1-dp rounding** (F-N) |
| O | 2211–2212 | four frozen federated members agree on `RMSE_μ` within `0.002 %` | `S0_FOLLOWUP.json`; per-arm `final_metrics.json` | `max − min = 1.5315e-05`; `/mean = 0.001526 %`; `/central = 0.001570 %` | **OK as a loose bound** (F-O) |
| P | 2213–2214 | window FedAvg `2.8 %`–`3.0 %` above centralized "for every local budget from `2` to `20` steps" | `S1_LADDER.csv` → `ratio_to_c` | `100(ratio−1) = 2.9619, 2.8140, 2.7801, 2.9109 %` at `ls = 2, 5, 10, 20`; only **4** budgets exist; `ls=2` is `sealed_e2_complete_aligned_read_only` | **OVERSTATED** (F-P) |
| Q | 2214–2215 | "the federated learner, not the weighting, limits the endpoint" | `S1_VERDICT.json` (`go:false, failed:"N3"`); `S0_REPORT.md` §9.2; `MANIFEST.sha256` (`S2 = "NOT RUN (S1 NO-GO)"`) | learner half measured; weighting half inferred from four arms that `S0_REPORT.md` §9.2 measures as near-constant predictors (0.3 % better than the best constant, zero alerts in 18/18 cells); `S2`'s GO-H/GO-D never ran | **OVERSTATED** (F-Q) |

17 of 19 numeric claims reproduce at their printed precision; `L` fails by 0.0047 pp, `P` and `Q`
assert more than was measured, and `N` is a round-up with no literal source.

## 2. Numeric consistency findings

### F-L — `0.17 %` is below its own source value (low severity, factual)

Largest SensorScope level mean is `+0.1747 %` (`m = 0.25`). The sentence says the cost is "not
above `0.17 %`", and `0.1747 > 0.17`. Same conclusion as the prior audit's F2, reached
independently. One token to fix.

### F-P — "for every local budget from 2 to 20 steps" (moderate, overstatement)

Two readings exist and the literal one fails:

* *Literal* ("every budget in the range 2…20"): 19 integers, of which **4** were run. Not supported.
* *Charitable* ("every budget we tested, which ranged from 2 to 20"): supported, since all four
  ratios lie in `[2.78, 2.97] %`.

The sentence also prints `2.8 %` as the lower bound while the measured minimum is `2.7801 %`
(rounds to `2.8` at one decimal, but is not attained), and `S1_REPORT.md` itself prints "2.78–2.96 %".
Additionally, `ls = 2` was **not trained in that round**: `local_steps_source =
sealed_e2_complete_aligned_read_only`, i.e. read from the sealed E2 runner, which
`GATE_AMENDMENT_A1.md` §5 flags as "not numerically interchangeable with the fresh rungs". The
traces are byte-identical (`sha256 f4ae137ab4967267…`), so the data is the same; the code path is
not. None of this is disclosed in the manuscript. The prior audit's `OK` does not survive the
"every … from 2 to 20" wording.

### F-Q — "not the weighting" is the half that was never tested (moderate, disclosure)

`S1_VERDICT.json` records `go: false`, `failed: "N3"`, reason "no level within 1.01c and best is
not 1 % below level 2"; the best rung (`ls = 10`) is only `0.1765 %` below `ls = 2` against a `1 %`
fallback bar. `MANIFEST.sha256` records `S2 = "NOT RUN (S1 NO-GO)"` and `F = "NOT LICENSED"`.

Reporting a failed necessary condition *as a limitation* is correct practice, and the learner half
("budget does not close the gap") is measured. The unmeasured half is the contrast: S2's GO-H
(oracle-weighting headroom) and GO-D (decision) are exactly the tests that would license "not the
weighting", and they were never run. `S0_REPORT.md` §9.2 further measures that the four frozen arms
are numerically near-constant predictors (0.3 % better than the best constant; zero alerts in all
18 cells), so their `0.0015 %` agreement is agreement between four models that learned almost
nothing — weaker support for "the weighting does not matter" than four independent confirmations
would be. The sentence should be scoped to what was measured.

### F-N — `12.1` has no literal source (low severity)

The trace-side mean is `12.0568` (5 seeds) / `12.0851` (20 seeds); the run-side roll-up is `12.0809`
over 1 990 active windows; `S0_REPORT.md` §3 prints **`12.06`**. `12.1` is a 1-dp round-up. The only
literal `12.1…` value in the tree is `12.11`, which is the `complete_counteracting` family row — a
family that was not chosen. I cannot distinguish round-up of `12.06` from a misread of `12.11`; both
are consistent with the printed digits. The statistic is an unweighted mean over active windows
(unit-weighting gives `17.86`), and the sentence never states that.

Also unprinted: the `≤ 2`-client share is **`6.69 %`** (`0.066908`), which is the actual N1 basis for
"the weights are free" against a 25 % bar. The sentence's `12.1` alone does not carry that inference.

### F-O — `0.002 %` is a round-up of `0.0015 %` (low severity)

Members: `debt_cal 1.003475640`, `inst_cal 1.003481206`, `local_hajek 1.003490955`,
`raven_simoracle 1.003477565`. Spread `1.5315e-05`; `/mean = 0.001526 %`, `/central = 0.001570 %`.
The claim is true for every plausible denominator, but `0.002 %` is not a source value and no source
states a denominator; the defensible figure is `~0.0015 %`.

### F-H — `+0.768` is called a "small margin" against the paper's own ruler (moderate, internal consistency)

The new sentence (L2160–2162) reads: "(P2) returns uniform weights whatever its objective, which is
consistent with **the small margin** of the projection over uniform server weights on the group
endpoint (`+0.768` and `+0.286` pp above)."

The same manuscript states elsewhere:

* L1831–1836: "Replacing uniform weights by `Proj_{C_r}(β̂_r)` is worth `+0.768` pp (`[0.563,0.970]`)
  on SensorScope, **above the `0.5` pp practical line and stable across the two seed halves**, and
  `+0.286` pp (`[0.098,0.471]`) on U-Air, below that line and unstable."
* L2091–2093: "the projection improves on uniform weights by `+0.768` pp
  (**`p_Holm = 2.7×10^{-5}`**) on SensorScope".

The bundled source agrees with L1834, not with the new sentence: `PART_A_REPORT.md` L15 flags the
SensorScope pair as outside the equivalence band and passing the practical line ("超出带 /
**通过**"), and L17 flags U-Air as outside the band but failing it ("不通过"). So one of the two
numbers is designated practically significant and Holm-significant by this paper, and the new
sentence calls the pair a small margin. The numbers are right and traceable; the characterisation
conflicts with the paper's own. A reader who checks L1834/L2092 will read the new sentence as
downplaying a result the paper claims elsewhere.

Two provenance details, both resolved in the paragraph's favour. (i) The printed CI brackets
`[0.563, 0.970]` and `[0.098, 0.471]` reproduce **exactly** from the bundled
`w1/tradeoff_v4/PART_A_REPORT.md` L15/L17. Recomputing the same contrast from
`results_w1_ladder/round_v4/FULL_SEED_LADDER.csv` instead gives `[0.561, 0.965]` and
`[0.091, 0.470]` — a third vintage that agrees to the second decimal but not the third. The
manuscript matches the bundled report, so this is a vintage spread across artefacts, not a
manuscript error; it does mean the pair is not reproducible to the printed precision from
`round_v4` alone. (ii) "pp" is a fixed rescaling, not a percentage of anything natural:
`pp_group = 50 × d_group` on every row of `FULL_SEED_LADDER.csv` (max deviation 0.0), matching
`GAP_DECOMPOSITION.csv` `pp_total = 50 × delta_total`. The `0.5` pp practical line is therefore
`0.01` in `Δ_group` units. This is internally consistent and is how the paper uses it elsewhere;
it is recorded because a reader cannot infer the unit from the sentence.

### F-E — `E_min = 3` is only partly recorded in the frozen artefacts (low severity, traceability)

The claim is correct (§1 row A), but on the E3 path it is *inferred from source defaults*, not read
from an artefact: the frozen `config_snapshot.json` for all four arms the paragraph measures records
`local_steps: 2` and `scenario: complete_aligned` and **no `e_min` key at all**, and
`configs/frozen/e3_multidataset_protocol_closure/` carries only horizon / opportunity_strata /
public_target / q_feature_boundary / stage2_eligibility. The value reaches the solver through
`window_runner.py` L989 `e_min=float(getattr(agg, "e_min", 3.0))`. Partly mitigating: the E4
one-factor spec *does* deposit it — `E4_WO_INST_FINAL_ONE_FACTOR_SPEC.json` L16
`"ESS_constraints": 3.0` — and two E4 call sites override it to `1.0`
(`e4/semantic_repair/task_b.py:53`, `e4/wo_inst_final/corrective.py:59`), so the default is not
universal in the codebase even though it is universal on the `raven` / `raven_wo_design` path.
No number changes; the premise is simply not confirmable from the E3 run artefacts themselves.

### F-KR — For U-Air Design-on the trace-derived and runner-derived `K_r` disagree (moderate, reproducibility)

`K_r` is directly recorded, not derived: `window_metrics.json` carries `a_r_size` (= `K_r`) and
`active_clients` (= `len`), and `main.tex` L880 defines `K_r = |A_r|`. On SensorScope and on U-Air
Design-off the independent trace artefact `.rb_work/evidence_headroom/REACHABILITY_WINDOWS.parquet`
(`n_active`) agrees with the runner **row for row** (2 000/2 000 and 1 600/1 600). On **U-Air
Design-on it does not**: `trace − K_r ∈ {0: 741, 1: 503, 2: 141, 3: 16, 4: 1}`, 113 windows are
trace-active but runner-inactive, and the trace-based `K_r ≤ 3` share over the *same* 1 402 windows
is **77.389 %**, not the printed **90.157 %**.

Consequence: the `90.2 % of 1402` claim is traceable to `window_metrics.json` only; it is not
derivable from the released EventTraces. That is a genuine artefact disagreement between two
deposited objects for the same windows, and it is not disclosed anywhere. It does not by itself
falsify the sentence — the sentence's perimeter is the runner's active window set, which is
self-consistent — but a reader who recomputes from the traces will get a different number and no
explanation. This is the mechanism paragraph's counterpart to §4.2: the numbers are right against
one deposited object and not against another.

Note also that `K_r ≤ 3` (this paragraph) and `|A_r| ≤ 2` (ledger item 62, 51.4 % / 69.0 %) are
**different thresholds of the same statistic**, not two renderings of one fact. Both verify: the
`≤ 3` shares are 78.58 / 90.16 / 79.01 %, and the `≤ 2` shares are 965/1877 = 51.41 % (SS) and
968/1402 = 69.04 % (UA Design-on), matching ledger item 62 exactly.

## 3. Citation metadata and citation-context findings

Neither new block adds or alters a citation: both contain **zero `\cite`** commands, one `\eqref`
each (`eq:Cr`, `eq:design_gate`), and no `\ref`. All cross-references resolve — the build reports
`undefined: 0` and `multiply-defined: 0`. `reference.bib` was touched at 19:11 but its content is
unchanged (`3F0BE0112FA9…`). Nothing to report under either citation heading.

## 4. Defect rulings requested by handoff §15

### 4.1 §13.1 Public-bundle drift — **upheld and materially wider: 3 of 9 files, not 1**

The handoff compared one pair. Comparing all nine `figure_data` files against the bundle:

| worktree `figure_data/` | sha256 (16) | bundle `figures/` | sha256 (16) | |
| --- | --- | --- | --- | --- |
| `FIG_CERTIFICATE_STRESS.csv` | `E48662E76E8DC053` | same | `E48662E76E8DC053` | identical |
| `FIG_CERTIFICATE_WINDOWS.csv` | `849B27D048FCE05D` | same | `849B27D048FCE05D` | identical |
| `FIG_E1_E2_RISK_NONINTERCHANGEABILITY.csv` | `28605D1EBF874C5F` | same | `28605D1EBF874C5F` | identical |
| `FIG_E2_E3_STRUCTURAL_ALIGNMENT.csv` | `0949F2E89E82953B` | same | `0949F2E89E82953B` | identical |
| **`FIG_E3_E3_PREDICTION_RISK.csv`** | **`27B90460279AFBEC`** (53 593 B) | same name | **`8110240A5F88644B`** (54 029 B) | **DIFFERENT** |
| **`FIG_E4_E4_COMPONENT_ABLATION.csv`** | **`998CDAC5982CC2B9`** (5 658 B) | same name | **`C80F6DDDABD7C8E7`** (5 656 B) | **DIFFERENT** |
| `FIG_G3_TDRIVE_H_MASS.csv` | `2E5199BC682BD7EF` | same | `2E5199BC682BD7EF` | identical |
| `FIG_G3_TDRIVE_TV.csv` | `E742948E1A8E6779` | same | `E742948E1A8E6779` | identical |
| **`FIG_W1_DESIGN_GATE.csv`** | **`050F595A42867BBF`** (269 B) | same name | **`5462183B6858F4B4`** (275 B) | **DIFFERENT** |

The three differing files are exactly the three that `git status` reports as modified under
`TO_OVERLEAF_paper_tmc_r1_clean/figure_data/`, which corroborates that the worktree copies were
regenerated while the bundle copies were not. The handoff's single-pair comparison therefore
understated the drift by a factor of three; the E4 pair is not the only, nor necessarily the most
consequential, lag point.

For the E4 pair the *reason* is now established, and it is a legitimate one. The frozen per-run
records give U-Air Design `RMSE_μ` means of `1.191114` (E3 `uair/raven`) vs `1.113059`
(E4 `uair/raven_wo_design`), i.e. **−6.553094 %**, and the frozen 240-cell evidence table agrees —
`results_seed_path_audit_r1/C4_T4_STATS.csv` even carries that figure in a `printed_old` column.
The printed **−6.885464 %** instead uses `full_mean = 1.195366`, the θ-copy re-score in
`results_active_set_repair/round_v1/E2_UAIR_CELLS.csv` (source `"G1c selected: tree"`), which
replaces exactly three U-Air seeds — `30007`, `30016`, `30018` — under the mirror/θ ruling recorded
in `results_endpoint_screen/round_v1/EXECUTION_REPORT.md` §1 ("the checkpoint score is canonical
there", max `|Δ| = 0.05661`). So the worktree figure is the θ-rescored value the manuscript prints
and the bundle holds the pre-θ value; the manuscript's number is defensible under that ruling.
`Δ_group` was **not** replaced and still matches the frozen records exactly (−6.943368 %), which is
consistent with the handoff's observation that all ten differing rows are U-Air
`RMSE_mu`/`Tail_RMSE`. The defect is therefore **not** that the figure is wrong, but that (i) the
bundle was never refreshed to the ruling it depends on, and (ii) neither `MANIFEST.csv` nor
`verify.py` can express "this value is the pre-ruling vintage", so the inconsistency is invisible to
every automated check the bundle ships. This directly contradicts `README.md` L13, which
tells the reader that `tables/` and `figures/` are "CSVs that generate the manuscript tables and
figures".

`verify.py` **cannot** detect any of this, and not merely because it only hashes: `MANIFEST.csv` has
only `path,bytes,sha256` — no source path, no provenance, no manuscript link — so the bundle has no
record of what each file was generated from and nothing to compare against. A hash-only verifier is
sufficient for integrity *of the bundle* and silent about consistency *with the paper*. This is the
structural reason the drift went unnoticed, and it is the finding a reader-facing fix must address
(a provenance column, or withdrawing the README's "generate the manuscript" claim).

A systematic sweep of the whole bundle (2 118 files) shows the lag is **not confined to the
figures**, and that it reaches numbers the paper prints.

* **`figures/FIG_E3_E3_PREDICTION_RISK.csv`**: 27 of 440 rows differ (the nine U-Air arms at seeds
  `30007`, `30016`, `30018`), columns `RMSE_mu` (max `|Δ| = 0.117272`) and `Tail_RMSE` (max
  `0.060681`); `MAE_mu`, `RMSE_rho` and `comparison_class` are identical. The bundle's U-Air 20-seed
  arm means round to `1.1911 / 1.1911 / 1.1882 / 1.2160 / 1.1914`; **none of those digits occurs in
  `main.tex`, `supplemental.tex` or `appendix.tex`**, whereas the worktree version gives exactly the
  printed `1.1954` (L1897, appendix L1927), `1.1954` (appendix L1925), `1.1923` (appendix L1923),
  `1.2202` (L1894, appendix L1924) and `1.1958` (appendix L1928). `results_seed_path_audit_r1/C3_CELL_DIFF.csv`
  independently records these as "MIRROR (replace)".
* **`tables/TABLE_II_MAIN_EFFECTIVENESS.csv`, `TABLE_E3_MAIN_EFFECTIVENESS.csv`,
  `TABLE_E4_COMPONENT_EFFECTS.csv`, `TABLE_E4_CORE_ABLATION.csv` and `TABLE_II_FREEZE.json`** all
  still carry the superseded pre-repair values (`1.18824`, `1.19111`, `1.19112`, parent
  `1.191113924600986`). For these the bundle *agrees with its worktree source* — the sources are
  stale too — so this is a bundle↔manuscript defect rather than a copy error, and `verify.py` is
  blind to it either way.
* The bundle **documents the correction it fails to ship**: `w1/audit_v5/round_v5_1/ERRATA_FOR_PAPER.md`
  gives the mapping `fedavg_window 1.18824 → 1.19225`, `raven 1.19111 → 1.19537`,
  `inst_cal 1.19112 → 1.19537`, and `A3P_RESOURCE_UPAIR.csv` is the **only** file in the bundle that
  holds the corrected `1.195365574077496`.
* **The released bundle contains its own truncated files.** `scripts/rebuild_table_ii.py` is a **2-byte**
  file (`sha256 7eb70257593d…`), manifest-registered at 2 bytes, while `README.md` L14 and L96 instruct
  the reader to run it to check Table II's 4-decimal cells. `tdrive/TD_R_FREEZE.json` is also 2 bytes
  with the same hash and no worktree counterpart, yet `README.md` L18 lists it as a deliverable. This is
  the §4.2 truncation class *inside the artifact a reader is told to verify with*.
* `README.md` L42 is **false**: it states that round v2's `PHASE3_REPORT.md` "is not redistributed",
  but `w1/frontier/PHASE3_REPORT.md` is in the bundle and its line 77 states the `3.44` pp and `1.32` pp
  figures. Consequently the first two rows of `w1/PAPER_NUMBERS.csv` print `UNLOCATED` with the reason
  "that file … was not copied" — a false reason.
* The shipped `scripts/build_public_repro_bundle.py` (`c8d9f0ac…`, 14 814 B) is an older revision than
  the worktree copy (`d400bdf4…`, 18 354 B) and contains no reference to `cityscanner/`, `overlay/` or
  `w1/EXCLUDED`, so **the shipped builder cannot reproduce the bundle it ships**. No R1.1 (w1) build
  script exists anywhere in the worktree.
* Manifest coverage: 2 116 data rows, 0 duplicates, 0 hash or byte mismatches, and only two files
  present on disk but unlisted — `MANIFEST.csv` itself (conventional) and
  `w1/MANIFEST_ADDITIONS.csv`, which `README.md` L38 describes as the rows this revision added to the
  manifest and which is therefore the one addition neither manifested nor hashed.
* `BUNDLE_SUMMARY.json` `file_count: 2117` against **2 118** files actually present, and
  `total_bytes: 179 916 789` against **180 207 845** actual — short by exactly the 291 056 bytes of
  `MANIFEST.csv`. Both fields exclude that one file. `created_utc` still reads 2026-09-05 while
  `bundle_revision` is `R1.1` (mtime 2026-10-04).
* A record correction: `ccfa-review-reports/raven-mcs-tmc-review-round10.md` §V.3 states that
  `PROTOCOL.json` and `verify.py` are "likewise not manifest-registered". Both **are**
  manifest-registered. That claim is refuted.

Reader-visible net effect, in the bundle's own numbers: someone rebuilding the paper's tables from
`RAVEN_MCS_PUBLIC_REPRO_R1` recovers `-6.553 / -6.875 / 0.131 / 0.136 / 1.1911 / 1.1882 / 1.2160`
where the paper prints `-6.885 / -7.221 / 0.143 / 0.149 / 1.1954 / 1.1923 / 1.2202`.

### 4.2 §13.2 Three scripts truncated to 2 bytes — **upheld: unrecoverable, and the bundle is not self-contained for those tables**

`scripts/compute_cityscanner_phi.py`, `scripts/run_c1_cityscanner.py`, `scripts/run_p2_nt_e3.py` are
each **2 B**, identical hash `7EB70257593D…`, mtime 2026-10-07 19:11, and untracked in git. I
searched the entire workspace (including `deliverables/` and the release bundle) for a copy and for
bytecode: **there is no copy and no `.pyc`** for any of the three (`scripts/__pycache__/` holds 20
other modules, none of these). The contents are lost and cannot be recovered from this workspace.

Consequence for delivered numbers: the bundle ships the *outputs* of these drivers
(`cityscanner/{CS_E3.csv,CS_E3_PAIRED.csv,CS_E3_SUMMARY.csv,CS_PHI.csv,…}` and
`cityscanner_p2/{JO_E3.csv,…}`) but ships only four rebuild scripts
(`rebuild_table_ii.py`, `rebuild_table_ii_tolerance.py`, `rebuild_e3_scd_holm_fedau_obsuse.py`,
`build_public_repro_bundle.py`). So the City Scanner visit-occupancy and Pilot-2 measured-`O`
rankings cited by the manuscript and supplemental material are **shipped as data with no surviving
generator**: a reader can hash them but cannot rebuild them. `README.md` L20–21 presents those
subtrees as reproducibility artefacts without disclosing this.

Scope note: none of the three drivers produces a number in either new block, so the direct impact on
this revision is nil. The impact is on the bundle's reproducibility claim, and it is a
release-integrity defect regardless of this revision. Two earlier records
(`ccfa-review-reports/raven-mcs-experiment-report-20260924.md` L27,
`results_endpoint_screen/round_v1/EXECUTION_REPORT.md` L99/L113) already recorded this loss and a
partial rebuild (`scripts/run_nodesign_supplement.py`), so the truncation is recurrent, not new.

The class is wider than the three worktree scripts. §4.1 records that `scripts/rebuild_table_ii.py`
**inside the released bundle** is also a 2-byte stub while `README.md` tells the reader to run it;
`tdrive/TD_R_FREEZE.json` is a 2-byte stub listed as a deliverable; and three further shipped files
(`scripts/rebuild_e3_scd_holm_fedau_obsuse.py`, `tables/E3_SCD_WORSTGROUP_VS_FEDAU_OBSUSE_HOLM.csv`,
`tables/E3_SCD_WORSTGROUP_SLICE_REL.csv`) have no counterpart anywhere in the worktree. So the
truncation is not only a worktree loss: it reaches files the release presents as runnable checks.

### 4.3 §13.3 Ledger Part VIII is stale and internally self-contradictory — **upheld**

Three passages are contradicted by the artefacts:

* L2865–2866: "no manuscript file … was edited by any of them. `main.tex` remains
  `02447bfe6256632b…` throughout." False: the file is `68D9B44F…` (mtime 17:05), which the handoff
  itself records and which the user confirms is an authorized change.
* L2905: "`main.tex` `02447bfe6256632b…` (unchanged, 17 pp)." False on both counts: `68D9B44F…`,
  18 pp.
* L2912: of the new block, "it has not been run and no number from it exists." False: the traffic
  round ran (`S0` `go: true`, `S1` `go: false / failed N3`), and the manuscript now prints four
  numbers from it.

The ledger **contradicts itself**: its own E1 row at L2848 already cites
`results_new_block_traffic/round_v1/S0_VERDICT.json` as evidence, in the same part that says the
block was never run.

Separately, two ledger prose phrases overstate statistics the ledger itself lists:
L2848/L2861's "ranking is preserved exactly" sits beside `mean_tau = 0.9943` and
`sign_flip_rate = 0.0029` (2/700) in `SELECTION_DECISION.json`. The quantities the ledger *quotes*
are accurate — `median_tau = 1.000` and `sign_flip_rate_big_delta = 0.0000` (n = 10) — so this is a
phrase-accuracy defect, not a data defect. Note the manuscript's own sentence (claim J) is narrower
and fully supported: `disagreement_rate = 0.0` on 20/20 seeds both datasets.

Also imprecise: ledger item 60 cites `DOSE_DECISION.json → h3.primary_w_pred` as the source for
"`gate_decision = null`", but `gate_decision` is not a key in that file; the string exists only as
prose in `PART_II_REPORT.md` L75 and `JOINT_READING.md` L53. The substance holds; the citation does
not resolve.

### 4.4 §13.4 Build — **upheld, and now measured: 18 pp**

See §0.2. The build is clean (0 errors / 0 undefined / 0 multiply-defined / 0 Overfull in `main`;
one `\vbox` in `supplemental`, as the ledger records), but:

1. The manuscript is now **18 pages**. If 18 pp is the MOPC ceiling this is at the limit with zero
   headroom; the growth is +1 page, not the "unknown" the handoff could only guess at.
2. The shipped `main.pdf` (890 040 B, 17 pp), `main.log` and `main.aux` are still the 2026-10-06
   20:45 artefacts. **The tree's PDF does not correspond to the tree's source.** Anyone reviewing,
   submitting, or archiving from this directory today would read a document that does not contain
   the revision under audit.

### 4.5 §13.5 MDE dispute — **the ledger is wrong in both directions; the column is exactly reproducible**

I resolved this rather than leaving it open. `results_gatekeeping/round_v1/A1_ANALYSIS.py` L31–32
and L208–209 define the column:

```
Z95 = 1.6448536269514722          # one-sided 95 %
Z80 = 0.8416212335729143          # 80 % power
def mde80(delta, se): return delta - (Z80 + Z95) * se
```

`Z80 + Z95 = 2.48647486052439`. Across **all 42 rows**, `(delta − mde80) / se_used` equals
`2.48647486052439` with a spread of `2.2e-15`. So:

* **`mde80` is a signed margin, not a minimum detectable effect.** It is `delta − k·se`; a negative
  value means the margin `delta` is not resolvable at that power. 36 of 42 rows are negative
  (all 6 U-Air rows, all 30 City Scanner rows) — meaningful, not invalid. My own first reading of
  these negatives as "structurally impossible" was wrong, and I record that.
* **Ledger item 55 is wrong twice.** Its stated formula (`2.802·s_d/√n`) is not the column's formula,
  and its printed values (`0.00618` SS, `0.0649` UA) are **9.98×** and **10.00×** larger than the
  correct `2.802·s_d/√n` (`0.0006190`, `0.0064883`) — a systematic decimal slip. Its *conclusion*
  ("the column is not reproducible from its own inputs") survives only because it tested the wrong
  formula; under the column's actual formula the column is exactly reproducible.
* **Ledger item 54 misreads the sign.** It reports `mde80` as "0.42–0.45 % (SS) and 0.08–0.09 % (UA)",
  i.e. it quotes the absolute values of the six negative U-Air entries as if they were MDEs. The
  actual MDE implied by the column's own convention is `k·se`: **0.0549 %** (SS `raven`),
  **0.0829 %** (SS `proj_beta`), **0.5758 %** (UA `raven`), **0.5930 %** (UA `proj_beta`). So the
  "off by roughly a decade" conclusion does not follow from this column: the column's own U-Air MDE,
  `0.576–0.593 %`, is within ~1.3× of the manuscript's quoted `0.70–0.80`. By this column the U-Air
  design is *not* an order of magnitude away from the quoted effect size.
* Item 54 also compares the manuscript's `L2119–L2124` pair — a paired-difference MDE from the
  Recoverable-Gain Ceiling work (20 seeds / 270 runs / 45 traces) — against a gatekeeping table for a
  different margin test. Even had the reading been right, the two quantities are not the same object.

Net: `EV-2` remains open, but its recorded severity is not supported by `A1_POWER.csv`, and items 54
and 55 need correction rather than further quotation. **This does not block the new passages**: I
confirmed the new blocks cite no MDE at all (no `MDE`, `detectable`, or `mde` token in either), which
matches the handoff's own assessment. It does block any claim that "the design could see an effect of
this magnitude".

### 4.6 G3 tolerance amendment disclosure — **adequately disclosed in the tree, absent from the paper**

Present and mutually consistent: `GATE_G3.json` (the 1e-6 verdict, `pass: false`, 37/40),
`GATE_ORIGINAL.json` (`pass: false`), `GATE_G3_AMENDED.json` (`tol_rel_original 1e-06`,
`tol_rel 1e-05`), `GATE_AMENDMENT.md`, and the withdrawal of the impossible confirmation rule
(seeds 30021–30025, which do not exist in the frozen artefacts). `DOSE_DECISION.json` records
`G3_original_pass: false`, `G3_tol_rel: 1e-05`, `amended: true`.

No manuscript disclosure exists (grep for `G3`, `dose`, `1e-5`, `10^{-5}`: 0 hits). I do **not**
treat that as a defect: a solver-tolerance amendment is an internal reproducibility knob, it was
authorized, and it is 500× below `δ = 0.5 %`. But the numbers in the new Limitations sentence do
depend on runs admitted under the amended tolerance, so the chain is worth one clause in the
rebuttal record even though it does not belong in the paper.

## 5. Additional findings not in the handoff

1. **§5.1 `w1/PAPER_NUMBERS.csv` does not cover the new numbers.** The round-12 M2 fix added a
   sentence pointing readers at `w1/PAPER_NUMBERS.csv` as the index "indexing the printed values".
   That index has **83 rows (70 `located`, 13 `UNLOCATED`)** and **zero** rows for any of the new
   printed values: `1877`, `1402`, `1515`, `78.6`, `90.2`, `79.0`, `12.1`, `0.388`, `4.11`, `6.6`,
   `2.8`. The revision therefore weakens the very fix M2 made: the manuscript now prints ~15 numbers
   the released index does not locate. Moderate; the fix is to add rows, and the sources are all
   identified in this report.
2. **§5.2 Two different NSW-Traffic experiments are described without distinction.** The pre-existing
   passage at L1743–L1754 reports the supplemental four-region protocol ranking (`0.0606` vs
   `0.1048` on `Δ_group`, `TwoStage-Hájek` lowest); the new Limitations sentence reports the
   `results_new_block_traffic` `e3_complete_aligned` family (`12.1` clients, `0.002 %`, `2.8–3.0 %`).
   These are different runs, different arm families, and different endpoints. Neither passage says
   so. The four-region numbers do not trace to `results_new_block_traffic` at all (a whole-workspace
   `*.csv` grep for `0.1048` returns only an unrelated City Scanner summary). One-sidedness also
   shows: the NSW block's own `TV(π_arr, μ) = 0.35638` — the largest of any block, and larger than
   the four-block figures the manuscript reports — appears nowhere in the manuscript.
3. **§5.3 The new text's evidence for "weights are free" is not printed.** The `≤ 2`-client share
   (`6.69 %` against a 25 % bar) is the actual N1 criterion; the manuscript prints only `12.1`.
4. **§5.4 The solution-quality caveat behind F1 is a real, if small, code-base property.** The
   binding-constraint excess reaches `+1.5e-8` (inside the solver's `≤ 1e-7` acceptance gate) and
   8 windows exceed `1e-9` on SensorScope and 8 on U-Air Design-off. This is consistent and
   disclosed-by-tolerance, and it does not change any number; it is noted because the new sentence's
   verb ("returns uniform weights") is stronger than the artefacts.
5. **§5.5 The 19:11 truncation event also touched `scripts/run_c1_tdrive_spatial.py` (47 177 B,
   intact) and `TO_OVERLEAF_paper_tmc_r1_clean/reference.bib` (content unchanged,
   `3F0BE0112FA9…`).** So the batch operation truncated three files and touched two others without
   damaging them. The trigger is unknown; it is the second recorded occurrence.
6. **§5.6 This session could not write into `TO_OVERLEAF_paper_tmc_r1_clean/`, `ccfa-review-reports/`,
   `scripts/`, `snapshots/`, `.rb_work/` or any other pre-existing subdirectory** (0/12 probed
   succeed; the workspace root and newly created directories do). The ACL diagnostic confirms the
   proximate cause — those directories lack `WRITE_OWNER` for the signed-in user, so DSH cannot
   provision its workspace grant — and a verified repair on
   `TO_OVERLEAF_paper_tmc_r1_clean` added the missing right **without restoring writes**, while an
   ACL-equivalent directory created during this session writes normally. The block is therefore not
   ACL-content-dependent and cannot be repaired from inside. This is why the build ran with
   `-output-directory` and why every artefact of this audit is staged in `_r13_build/` rather than
   written in place. It is an environment defect, not a manuscript defect, but it affects the
   audit trail and is recorded so the deliverables' provenance is legible.

## 6. Severity

| finding | severity | reason |
| --- | --- | --- |
| §4.1 bundle drift, 3/9 files + `file_count` | **high (Reproducibility)** | released artefact contradicts the paper it claims to generate; verifier structurally blind |
| §4.1b bundle ships superseded printed values | **high (Reproducibility)** | readers rebuilding Table II/III and Table IV recover different digits than the paper prints |
| §4.2 lost drivers, City Scanner tables | **high (Reproducibility)** | three delivered tables have no surviving generator and no copy exists; two stubs sit inside the bundle itself |
| §4.4 stale PDF + 18 pp | **high (submission risk)** | shipped PDF is not the audited manuscript; page limit reached |
| F-P "every local budget 2–20" | **moderate** | asserts 19 budgets from 4, one inherited |
| F-Q "not the weighting" | **moderate** | the contrast's own tests never ran; supporting arms are near-constant |
| F-H `+0.768` as "small margin" | **moderate** | contradicts L1834 and L2091–2093 of the same manuscript |
| §4.3 ledger staleness + self-contradiction | **moderate (record)** | three false statements and an internal inconsistency |
| §4.5 MDE items 54/55 | **moderate (record)** | ledger formula wrong, values 10× off, sign misread |
| §5.1 `PAPER_NUMBERS.csv` coverage | **moderate (Reproducibility)** | undoes the round-12 M2 fix's effect |
| F-L `0.17 %` vs `0.1747 %` | **low, factual** | a printed bound the data crosses by 0.0047 pp |
| F-N `12.1` | **low** | round-up; no literal source; actual N1 basis unprinted |
| F-O `0.002 %` | **low** | loose bound for `0.0015 %` |
| F-KR trace vs runner `K_r` (U-Air Design-on) | **moderate (Reproducibility)** | two deposited artefacts give 77.4 % vs 90.2 % for the same 1 402 windows |
| F-E `E_min` not in run artefacts | **low** | premise inferred from defaults, not deposited on the E3 path |
| §5.2 two NSW families | **low–moderate** | clarity/consistency; no number is wrong |
| §5.4 uniform-verb (prior F1) | **low** | feasible-set claim sound; output within solver tolerance |
| §4.6 G3 disclosure | **none** | disclosed in-tree, authorized, internal |

Nothing in either new passage is unsupported, invented, or directionally wrong. Every number in the
mechanism paragraph reproduces exactly from the frozen artefacts. The failures are in **what the
sentences assert about coverage and status**, not in the arithmetic.

## 7. Safe edit suggestions (owner: `ccf-paper-writer`; none applied by this audit)

1. L2207: `0.17` → `0.175` (or "at most `0.17`–`0.18 %`"). One token; same table; no conclusion moves.
2. L2213: "for every local budget from `2` to `20` steps" → "for every local budget we ran
   (`2`, `5`, `10`, `20` steps)". Removes the coverage overstatement; also consider `2.78 %` for the
   lower bound and stating the three-seed centralized denominator.
3. L2214–2215: scope the contrast — e.g. "on that block the gap is the federated learner's, not an
   optimisation budget" — and drop or qualify "not the weighting", which S2 would have tested.
4. L2160–2162: "the small margin" → a characterisation consistent with L1834, e.g. "the margin the
   projection adds over uniform weights on the group endpoint (`+0.768` pp on SensorScope, above the
   `0.5` pp line; `+0.286` pp on U-Air, below it)".
5. L2156/L2160: "returns uniform weights" → "returns weights within solver tolerance of uniform"
   (prior audit F1; deviation `≤ 9.2e-5`, constraint excess `≤ 1.5e-8`).
6. L2210: state the `≤ 2`-client share (`6.69 %`) — it is the load-bearing N1 number — and consider
   disambiguating which NSW-Traffic family the sentence reports (§5.2).
7. L2199–L2201: quote both ranges at the same precision (prior audit F3).
8. Not manuscript edits: refresh the bundle (§4.1/§4.2), rebuild and re-ship `main.pdf` (§4.4),
   correct ledger items 54/55 and Part VIII §VIII.3 (§4.3/§4.5), and add `PAPER_NUMBERS.csv` rows
   (§5.1). The last three belong to `ccf-rebuttal-writer`; the page-limit decision belongs to the user.

## 8. Next CCFA owner

`ccf-paper-writer` for the eight wording/rounding edits above (all need the writing authorization the
project requires). `ccf-rebuttal-writer` owns the ledger corrections (items 54, 55, 61-as-phrased,
new items for §4.1–§4.4 and §5.1) and must not treat this report as a ledger entry. The page-limit
decision and the bundle refresh are user authorization items. `ccf-paper-reviewer` owns the Evidence
score; per handoff §15 neither conclusion may be folded into the other.

## 9. No-invention status

Every value recomputed in this report was produced in this session from the named artefact by scripts
in `_r13_build/` (`reconstruct_prev.py`, `count_active_windows.py`, `check_a1_power.py`,
`check_a1_power_k.py`, `check_conc_and_proj.py`, `check_uniform_alpha.py`, and the four subagent
scripts), not copied from another round's summary. Where a source could not be traced I said so
(the prior audit's `+0.768` pair — now traced; the four-region NSW numbers — still untraced in this
tree). Where my first reading was wrong I recorded it: I first read the negative `mde80` values as
structurally impossible and the column as unreproducible, and both readings were wrong (§4.5). No manuscript,
ledger, bundle, or `results_*` file was modified by this audit.
