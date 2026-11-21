# RAVEN-MCS training active-set repair (route A) — experiment report for independent verification

```text
Author of the executed work: the agent that ran this round (not the author of the plan).
Plan under execution:       ccfa-review-reports/raven-mcs-active-set-repair-design.md
                            (referred to below as "the plan"; section numbers are the plan's)
Executed:                   2026-09-27, ~11:50-12:25 local (03:50-04:25 UTC)
Audience:                   an independent verifier (Claude) who did not observe this round.
Purpose:                    let you CONFIRM OR REFUTE every numeric claim from stored artifacts
                            without re-running training, and re-run training if you want to.
```

**How to verify, in order of cost:**

```bash
# 1. re-derive every numeric claim from stored artifacts (no training, ~20 s)
.venv_new/Scripts/python.exe results_active_set_repair/round_v1/verify_report_claims.py
#    -> expect the final line "ALL CLAIMS RE-DERIVED FROM STORED ARTIFACTS"
# 2. add the pi^tar rebuild through the runner's own path (~2 min)
.venv_new/Scripts/python.exe results_active_set_repair/round_v1/verify_report_claims.py --deep
# 3. re-run any stage; every run is marker-cached, so G1/E1 become read-backs, not retraining
.venv_new/Scripts/python.exe scripts/run_active_set_repair.py --stage g0|g1|e2|e3|status
# 4. to retrain from scratch, delete results_active_set_repair/round_v1/repair/ and re-run e1
```

`verify_report_claims.py` only reads. It fails loudly with claim / expected / re-derived values.
Its S5 section contains **guards**: it first reproduces *both published* `tab:app_p2_coverage` rows
from the untouched frozen trees before it will validate the substituted row.

**Verification result recorded at hand-over** (2026-09-27, revision 2; artifacts per `MANIFEST.sha256`):

```text
verify_report_claims.py          ->  137/137 checks passed  "ALL CLAIMS RE-DERIVED FROM STORED ARTIFACTS"
verify_report_claims.py --deep   ->  139/139 checks passed  (adds a pi^tar rebuild via the runner path)
```

**Revision 2** incorporated an independent review of revision 1: it retracted two of the four
amendment grounds, retracted the `p2_cvxpy.py` drift lead on new evidence, retracted the claim that G2
was not executable (**G2 has now been run and the hybrid blocks are cleared**), fixed a transposed
quotation of the manuscript, and added four findings.

**Revision 3 is an erratum.** Two of revision 2's findings were wrong, and both were wrong the same way:
it treated a run directory under `artifacts/` as authoritative without first searching for a
supersession record. `artifacts/e4_ablation_semantic_integrity_repair_r1/E4_WO_INST_FINAL_DECISION.json`
had already declared the E4 `raven_wo_inst` arm **invalid** on 2026-08-12 and authorised 40 corrective
reruns. See SS0.2, SS0.3 and SS4.4. Everything else in revision 2 stands.

If you see fewer passes, the artifacts or the environment differ from what is described here —
SS1 pins the environment and SS11 pins the artifact hashes via `MANIFEST.sha256`.

---

## 0. TOLERANCE AMENDMENT — read this before R1-R4

**The plan's G1a gate failed as written and was executed under an amended tolerance, with the
user's explicit authorization. It is the only pass rule that was changed.**

| item | the plan | as executed |
|:---|:---|:---|
| G1a pass rule | "final metrics bit-equal to the frozen tree" | `abs_diff <= 1e-6` |
| G1a failure action | **stop** — "a rebuild would confound two changes" | not taken; user authorized continuation |
| authority | — | user, 2026-09-27, verbatim: *"放宽容错，执行E1，然后写进实验报告，特别将其注明"* |

The failing arm, the only one of 12 gates that is not bit-exact:

| | value | source |
|:---|:---|:---|
| frozen | `7.915297744846339` | `artifacts/e3_formal_runs_r1/runs/sensorscope/debt_cal/seed30001/final_metrics.json :: RMSE_mu` |
| current runner | `7.915297538076236` | `results_active_set_repair/round_v1/repair/C0_frozen/sensorscope/debt_cal/seed30001/final_metrics.json :: RMSE_mu` |
| \|diff\| | `2.0677010326153322e-07` (relative `2.61e-08`) | `G1_REPORT.json :: G1a[2].abs_diff` |

**Determinism evidence** (`G1_DEBT_CAL_DIAG.json`): three independent measurements return the
identical `7.915297538076236` — `debt_cal` as the **first** `run_arm` call in a fresh process
(`repair_solo`), a same-process repeat (`repair_again`), and the **third**-in-process call inside
the original G1a sequence. `self_consistent = true`, `ordering_effect = false`. So it is not
run-to-run noise and not in-process state leakage.

**Grounds offered for the amendment** — **revised 2026-09-27 after independent review**, which
found two of the four original grounds invalid. The amendment stands on the three grounds below.
The superseded grounds are kept so the change of reasoning is auditable.

1. **Magnitude.** The relative size `2.6e-08` is ~**1e6 times smaller** than the ~6.3 % active-set
   effect E1 measures (SS4). The reviewer reached the same bound independently by a stronger route:
   even a 100x amplification of the drift cannot reach the `9e-4` gap between rebuilt Debt-Cal and
   frozen RAVEN-NoDesign.
2. **The decisive comparator is bit-reproducible on U-Air.** The reviewer correctly observed that the
   original ground 4 was wrong — R1 compares rebuilt Debt-Cal against **frozen** RAVEN-NoDesign, so
   the comparison *is* cross-batch — and that `raven_wo_design` had never been bit-reproduction-
   checked on U-Air. That check has now been run (`C1_RAVEN_WO_DESIGN_REPRO.json`): the current code
   reproduces **frozen U-Air `raven_wo_design` bit-exactly**, `abs_diff = 0.0` on `RMSE_mu`,
   `Delta_group` and `Delta_c_s` at seeds 30001 and 30002. Together with `raven_simoracle`
   (`GATE_uair.json`, `abs_diff = 0.0`), **every U-Air arm that has been checked except `debt_cal`
   reproduces bit-exactly**, so R1's comparator is sound and the drift is confined to one arm.
3. **The drift cannot be filter-caused.** G1a's target block has **zero** `pi^tar` holes (SS2), so
   the filter the gate isolates is provably a no-op there. *Narrowed:* this does **not** bound the
   drift's magnitude on U-Air, and the original report implied that it did. Grounds 1-2 carry the
   amendment.

**Superseded grounds, retained for audit:**

- ~~`2.07e-07` is 5x below the `1e-6` used in the plan's E2 reference path, so the plan is internally
  inconsistent.~~ **Withdrawn.** The reviewer is right that these bound different things: E2's `1e-6`
  compares a recomputation against a stored value; G1a asks whether the code is the same. Citing one
  as precedent for the other was rhetoric, not a contradiction.
- ~~E1's four rebuilt rows are compared against each other and against RAVEN-NoDesign from the new
  batch.~~ **Withdrawn as factually wrong.** RAVEN-NoDesign is the frozen E4 tree. See ground 2.

**Consequence a verifier must carry forward:** the `debt_cal` G1a arm is reproduced to `1e-6`,
not bit-exactly. Every other gate is bit-exact.

### 0.1 The drift is localised, and there is a concrete lead — please attack it

`runtime_manifest.json` hashes, frozen vs this round, SensorScope seed30001:

| method | EventTrace_hash | config_hash | metric_hash | **checkpoint_hash** | RMSE_μ reproduced? |
|:---|:--:|:--:|:--:|:--:|:---|
| `fedasync_window` | SAME | DIFF | DIFF | **SAME** | bit-exact `0.0` |
| `flamf_timealign_adapted` | SAME | DIFF | DIFF | **SAME** | bit-exact `0.0` |
| `debt_cal` | SAME | DIFF | DIFF | **DIFF** | `2.07e-07` |

Readings:

- The EventTrace is identical in all three, so the divergence is not in the data.
- `config_hash` and `metric_hash` differ for **all three**, including the two that reproduce
  bit-exactly — so they are **non-diagnostic** here (they embed the `source_identity` that
  `run_arm` writes). Do not read them as evidence of a metric change.
- **`checkpoint_hash` is the discriminator**: identical for the two arms that reproduce exactly,
  different for `debt_cal`. The trained weights are where the difference lives.

**Lead that was withdrawn, and the evidence that killed it.** The first version of this report
proposed `src/raven_mcs/aggregation/p2_cvxpy.py` (uncommitted, mtime 2026-08-28 > frozen 2026-08-11,
`git diff --stat` = `9 +++++`) as the cause. The reviewer gave three reasons why the diff is inert;
the third — that no one had checked whether the sanitisation ever fires — was testable, so it was
tested (`C2_VDIAG_SANITISATION.json`):

| check | result |
|:---|:---|
| `solve_p2` calls instrumented (U-Air + SensorScope `debt_cal` seed 30001) | **171** |
| calls whose `variance_diag` had a non-finite entry | **0** |
| calls whose `variance_diag` had a negative entry | **0** |
| smallest `variance_diag` seen | `0.011557` |

So the `v_diag` sanitisation **never fires** on these runs, and the added `instant_calibration`
parameter defaults to `True` while `DebtCalAggregator` (`methods.py:447-457`) does not pass it. The
diff cannot produce the drift on this path. **The lead is withdrawn.** (Incidental: the diff's own
`if np.any(v_diag < 0): raise` at `p2_cvxpy.py:94-95` is dead code, because `:80` clamps to `>= 0`
first.)

**The leading candidate now, from the reviewer.** `DebtCalAggregator` calls `solve_p2` with
`lambda_beta=1e-8` (`methods.py:455-457`, comment: "P2 uniqueness requires lambda_beta > 0; keep
negligible so Debt-Cal"), whereas every other P2 user in the RAVEN family takes `lambda_beta=1.0`
(`RavenAggregator`/`RavenSimOracleAggregator`, `methods.py:478/619`). **`lambda_beta=1e-8` is the one
property unique to `debt_cal` among all P2 users, and `debt_cal` is the one G1a arm that does not
reproduce.** A near-singular reference term makes the P2 optimum sensitive to solver version and to
tiny input perturbations, which is consistent with a deterministic `2e-07` difference in the weights.

Supporting evidence assembled this round: every **other** checked arm reproduces bit-exactly —
`fedasync_window` and `flamf_timealign_adapted` (G1a, 0.0), `central_delivered` (G1b, 0.0),
`raven`/`twostage_hajek` at the three divergent seeds (G1c, 0.0), `raven_simoracle` on both datasets
(`GATE_*.json`, 0.0), and `raven_wo_design` on U-Air (`C1_RAVEN_WO_DESIGN_REPRO.json`, 0.0). So P2
per se is reproducible here; the `lambda_beta=1e-8` arm is the untested-in-isolation one.

Open falsification route: run `RavenAggregator`-family `debt_cal` with `lambda_beta=1.0` instead of
`1e-8` and see whether the frozen value returns. That is a method change, so it needs authorization
outside route A.

### 0.2 The `wo_inst` repair is unfinished at one call site

Looking for the missing 2x2 arm (SS4.3) turned up a code-state problem. **Revision 2 called it
"a half-applied uncommitted diff" and implied an unexplained regression. It is not unexplained: it is
the residue of a documented repair whose own record describes it.**

`artifacts/e4_ablation_semantic_integrity_repair_r1/E4_WO_INST_SEMANTIC_FIX.json` (2026-08-12) records
that the pre-repair `window_runner` gated `aggregator.compute_server_weights` on
`policy.uses_instant_calibration`; `raven_wo_inst` has that flag `False`, so `alpha` was set to
normalised `beta` and **P2 never ran** for that arm. The repair added an `instant_calibration` flag,
threaded through `p2_cvxpy.solve_p2` into `validate_p2_lambdas`, so that `lambda_group = 0` is legal for
the ablation only, and made the runner always call the aggregator.

One call site was not covered. `RavenWoInstAggregator.__init__` (`methods.py:581-600`) hardcodes
`lambda_group = 0.0` and `instant_calibration = False`, while
`src/raven_mcs/sag/counterfactual_audit.py:106` (`_solve_alpha` -> `solve_p2`) calls `solve_p2` without
passing the flag, so the default `True` applies. With `window_runner.py:1016/1252` running
`_run_counterfactual()` whenever `lowmem` is false:

```text
ValueError: lambda_group must be >= max_server_learning_rate (got 0.0 < 1.0)
```

A plain `run_arm("C0_frozen", "uair", "raven_wo_inst", 30001)` raises, so the arm cannot be re-run until
that site is covered; nine lines of the repair also remain uncommitted. Recorded in
`C3_TWO_BY_TWO.json :: status = BLOCKED`. **No manuscript value depends on it**: Table IV's `Inst` rows
use the corrective reruns (SS0.3).

This still supports the reviewer's SS6(c) point on code-version traceability, though more narrowly than
revision 2 claimed. The working tree does not carry a general breakage; it carries one unfinished repair.

### 0.3 Erratum: the `Inst` rows are right, and revision 2 said otherwise

Revision 2 reported that Table IV's U-Air `Inst` row contradicted the E4 arm it names, quoting a tree
mean of `1.119606` against the printed `-0.089`, and concluded that "if the tree is authoritative the
published row is wrong". **Both statements are withdrawn.**

The primary record, `artifacts/e4_ablation_semantic_integrity_repair_r1/E4_WO_INST_FINAL_DECISION.json`:

```json
{ "decision": "WO_INST_EXISTING_40_RUNS_INVALID_TARGETED_RERUN_REQUIRED",
  "proven_invalid": true, "authorized_corrective_reruns": 40,
  "reason": "Parent raven_wo_inst skipped P2 by setting alpha=beta when
             uses_instant_calibration=False, violating preserve-P2-machinery semantics." }
```

The invalidated arm is visible in the run data: every sibling E4 U-Air arm carries a
`p2_invocation_states.json` of `0.87`-`1.23` MB, while `raven_wo_inst` carries **`3` bytes**, an empty
list. The 40 corrective reruns live in `artifacts/e4_wo_inst_reference_penalty_final_correction_r1/`,
and their `E4_WO_INST_FINAL_CLAIM.json` reproduces the table to four decimals:

| cell | `mean_paired_diff` | implied relative | Table IV prints |
|:---|:---|:---|:---|
| U-Air `Delta_group` | `-0.00097708` | **`-0.0894 %`** | `-0.089` |
| U-Air `Delta_c_s` | `-0.00176200` | `-0.1429 %` | `-0.143` |
| U-Air `RMSE_mu` | `+0.00155659` | `+0.1307 %` | `+0.131` |
| SensorScope `Delta_group` | `-0.00264030` | `-0.2604 %` | `-0.260` |
| SensorScope `RMSE_mu` | `-0.00013938` | `-0.0018 %` | `-0.002` |

**Table IV is correct. The tree directory `artifacts/e4_core_mechanism_ablation_r1/runs/uair/raven_wo_inst`
is the superseded artifact, and the paper never used it.** The consequence for SS4.4 is in that section;
the consequence for the third review round is recorded there as a withdrawn concern.

Testable prediction: patch `counterfactual_audit._solve_alpha` to pass `instant_calibration=False`
when `lambda_group == 0` — i.e. finish the diff the docstring already describes — and
`raven_wo_inst` should run again.

---

## 1. Scope, boundary and environment

**Executed:** G0 inventory; G1a-G1d gates (12 gate entries, 10 distinct runs — the two G1d
`fedavg_window` seeds 30001/30006 are re-used by E1 through the shared run marker); E1 rebuild
(80 runs, 2 of them the G1d pair); E2 re-evaluation; E3 downstream recomputation.
**Distinct training runs: 92** = 90 under `repair/C0_frozen/` + 2 in `repair_solo/` and
`repair_again/` (the SS0.1 determinism measurements). **~35 min on CPU.**

**Boundary as executed (§14 of the plan):**

| the plan forbids | status |
|:---|:---|
| writing outside `results_active_set_repair/round_v1/` and `scripts/run_active_set_repair.py` | honoured; `status` stage lists the write set |
| overwriting a frozen tree | honoured; frozen trees are read-only in this round |
| changing `src/` | **no change made this round.** See the caveat below |
| editing `.tex` | honoured; nothing written into `TO_OVERLEAF_paper_tmc_r1_clean/` this round |
| replacing a table cell | honoured; R4 is a proposal only |
| commit or push | honoured |

**Caveat a verifier must not miss.** `git status` shows `src/` as modified relative to HEAD
(`method_policy.py`, `methods.py`, `window_runner.py`, `p2_cvxpy.py`, `pi_target.py`,
`feasibility.py`, `window_dataset.py`, `sag_runtime.py`, `sag/*`, plus many untracked paths).
Those diffs are from **earlier, separately authorized rounds of the same session** (the `uses_oracle_p`
field, the `raven_oracle_p` aggregator, the p-gate in `window_runner.py`, the F-1 generator), **not
from route A**. Evidence that route A itself added no `src/` change: the modified `src/` *sources*
carry mtimes of 2026-08-28, 2026-08-30, 2026-09-11 and 2026-09-23, all **before** this round's first
artifact (2026-09-27 11:50:13); only `src/**/__pycache__/*.pyc` files carry this round's mtime, and
those are interpreter bytecode, regenerated by importing modules. A verifier who wants a stronger
check should diff `scripts/run_active_set_repair.py` for any `src/` write path — there is none.

**Environment fingerprint** (asserted by the verifier):

```text
python 3.11.9 | pandas 3.0.5 | numpy 2.4.6 | torch 2.13.0+cu130 | scipy 1.17.1 | cvxpy 1.9.2
solvers: CLARABEL, SCS, SCIPY, HIGHS, OSQP
interpreter: .venv_new/Scripts/python.exe   (requirements-lock.txt pins cvxpy==1.9.2, clarabel==0.11.1)
```

`requirements-lock.txt` pins `clarabel==0.11.1`; the installed `cvxpy` matches the lock. The frozen
runs' `runtime_manifest.json` records **no** dependency versions, so a solver-version drift between
2026-08-11 and now can be neither confirmed nor excluded from stored metadata alone.

---

## 2. G0 — inventory: `ACTIVE_SET_INVENTORY.csv`, `PI_TAR_HOLES.csv`, `G0_SUMMARY.json`

`pi^tar` rebuilt through the runner's own path
(`apply_sealed_opportunity_stratum` -> `build_pi_target(atomic_for_pi, spatial_to_client, split="test")`,
`src/raven_mcs/e3/real_runner/runner.py:326-387`) over the `pi^opp` (client x stratum) support.

| block | strata | support pairs | zero `pi^tar` | share | the plan's SS2 figure | match |
|:---|--:|--:|--:|--:|:---|:--:|
| `uair` | 288 | 288 | **72** | **25.0 %** | "72 of 288" | ✓ |
| `sensorscope` | 440 | 440 | 0 | 0 % | "0/440" | ✓ |
| `traffic` | 32 | 344 | 0 | 0 % | "0/344" | ✓ |
| `tdrive_speed` | — | — | — | — | "not counted" | **NOT_COUNTED** |

Realized active sets vs frozen `fedau_window` (full delivery), same seed and window, over all 640
stored `window_metrics.json`:

| block | licensed class | methods | windows identical to FedAU | mean active clients |
|:---|:---|:---|--:|--:|
| SensorScope | all 16 | full + design | **2000 / 2000** | 2.4245 |
| U-Air | `full` | `fedavg_window`, `fedasync_window`, `flamf_timealign_adapted`, `debt_cal` | **826 / 1600** | **1.8269** |
| U-Air | `full`, clean batch | `fedau_window`, `obsuse_window`, `raven_wo_design` | **1600 / 1600** | **2.4500** |
| U-Air | `design_support` | `local_hajek`, `twostage_hajek`, `inst_cal`, `raven`, `raven_simoracle`, 4 E4 arms | 826 / 1600 = licensed | 1.8269 |

**Verdict: 80 violations = 4 no-Design methods x 20 seeds, all on U-Air**, exactly the set the plan
predicted in its SS2 item 1 — which went beyond the diagnosis record's N1/N4 in naming four methods
rather than one. Verified: `fedavg_window`, `fedasync_window`, `flamf_timealign_adapted`, `debt_cal`
all have `uses_design_ratio=False` in `src/raven_mcs/aggregation/method_policy.py` (lines 65, 73,
79, 103), so their licensed `A_r` is full delivery and the restriction was unlicensed.

SensorScope Design-on rows also read 2000/2000 because with zero holes the restriction is a no-op
there — consistent, not a contradiction.

---

## 3. G1 — gates: `G1_REPORT.json`, `G1_DEBT_CAL_DIAG.json`

| gate | runs | the plan's rule | result |
|:---|--:|:---|:---|
| G1a | 3 | reproduce the frozen tree | `fedasync_window` **0.0** ✓, `flamf_timealign_adapted` **0.0** ✓, `debt_cal` **2.07e-07** → **pass under the SS0 amendment** |
| G1b | 1 | bit-equal | `central_delivered` U-Air **0.0** ✓ |
| G1c | 6 | match tree or CSV, per seed | **6/6 match the E3 tree; 0/6 match the repro CSV** |
| G1d | 2 | bit-equal to `results_table2_audit` | both ✓ (seed 30001: 1.1712625825964957 vs audit ...955, 2e-16) |
| G2 | 6 | hybrid active-set logging | **0 executed** — see SS7 |

### 3.1 G1c resolves diagnosis-record item N3

| method | seed | E3 tree | this round's rerun | repro CSV | reproduces |
|:---|--:|:---|:---|:---|:---|
| `raven` | 30007 | 1.1424870864095478 | **1.1424870864095478** | 1.18941261605731 | tree |
| `raven` | 30016 | 1.1709258951551238 | **1.1709258951551238** | 1.1526704437327764 | tree |
| `raven` | 30018 | 1.125360082508588 | **1.125360082508588** | 1.1817229910128095 | tree |
| `twostage_hajek` | 30007 | 1.1441802550200664 | **1.1441802550200664** | 1.1868478786334546 | tree |
| `twostage_hajek` | 30016 | 1.2242075631780656 | **1.2242075631780656** | 1.2085144491379751 | tree |
| `twostage_hajek` | 30018 | 1.1286332988862726 | **1.1286332988862726** | 1.186397524006943 | tree |

All six `abs_diff = 0.0`. Per the plan's G1c rule the **E3 run tree is the single source for every
Design-on U-Air row**, and it is what E2 used. Since Table III's printed `1.1882` is *also* the
tree's ALL20 mean `1.188238`, the conclusion is that the **public-repro per-seed CSV is the outlier
artifact at those three seeds**, not the manuscript. Source:
`RAVEN_MCS_PUBLIC_REPRO_R1/tables/TABLE_II_WORSTGROUP_PER_SEED.csv`.

---

## 4. E1 — rebuild on the licensed set: `E1_RUNS.csv`, `E1_ASSERTIONS.csv`

Per-run assertion, evaluated **before** metrics were read: realized `active_clients` equals frozen
`fedau_window`'s for every window of the same seed.

| method | windows compared | identical |
|:---|--:|--:|
| `fedavg_window` | 1600 | **1600** |
| `fedasync_window` | 1600 | **1600** |
| `flamf_timealign_adapted` | 1600 | **1600** |
| `debt_cal` | 1600 | **1600** |

No assertion fired. All four now train on exactly FedAU's full-delivery set.

**Cell movement — the four affected U-Air rows, 20-seed `RMSE_mu` means:**

| method | old (Design-filtered) | new (licensed) | abs | relative |
|:---|:---|:---|:---|--:|
| FedAvg-Window | 1.188238 | **1.111932** | −0.076305 | **−6.4217 %** |
| FedAsync-Window | 1.188279 | **1.111924** | −0.076356 | **−6.4257 %** |
| TimeAlign-Agg | 1.188435 | **1.112002** | −0.076433 | **−6.4314 %** |
| Debt-Cal | 1.189318 | **1.114378** | −0.074940 | **−6.3011 %** |

The claim this supports: **four different aggregation rules shift by the same amount
(−6.30 % to −6.43 %, spread 0.13 pp).** A method-independent shift of that uniformity is evidence
that the cause is the active set rather than any method's behaviour. `verify_report_claims.py`
asserts the whole range lies in `[-6.44, -6.29]`.

**Independent cross-check.** E1's rebuilt FedAvg `1.111932` reproduces the earlier, separately
produced `results_table2_audit/uair_fedavg_current_per_seed.csv` 20-seed mean to four decimals.
Two independent rebuilds agree.

### 4.3 The measure-zero-control arm (2x2) — attempted, blocked, and why it matters

SS5 below attributes RAVEN-NoDesign's `Δ_group` structure to P2 components, but the comparable
`raven_wo_inst` arm is **design-ON**, so the design factor and the active set move together. The arm
that separates them is `design off x instant calibration off`. It was built at runtime with no `src/`
change (`POLICY_MAP[arm] = replace(POLICY_MAP["raven_wo_inst"], uses_design_ratio=False)` plus the
family's aggregator, mirroring the pattern `run_h_headroom` already uses for
`raven_simoracle_nodesign`), and it **cannot run**: `instant_calibration=False` is a constructor
argument of `RavenWoInstAggregator`, not a policy field, and that class is currently unrunnable
(SS0.2). Recorded as `C3_TWO_BY_TWO.json :: status = BLOCKED`, with three unblocking options.

The intellectual content of the arm is unchanged and remains the sharpest open question in this
round: **is instant calibration still decisive once the design factor is off?** SS5's licensed-set
association (§6.2, Debt-Cal 1.0175 and NoDesign 1.0165 against 1.0413-1.0557 for the five arms
without P2 calibration) is evidence *for* it, but it is not the controlled 2x2.

### 4.4 Why two E4 arms are bitwise identical, and a corrected reading of the ablation

Found this round. Comparing stored trees at full precision:

| arm A | arm B | relationship |
|:---|:---|:---|
| `raven_wo_inst` (E4 tree) | `twostage_hajek` (E3 tree) | **bit-identical per seed** on `RMSE_mu`, `Delta_group`, `Delta_c_s` |
| `inst_cal` (E3 tree) | `raven_wo_debt` (E4 tree) | **bit-identical per seed** (`Delta_c_s` differs by `2.2e-16`) |

**Revision 2 read the first identity as "TwoStage-Hajek *is* RAVEN without instant calibration" and
called the family's arms duplicates. That reading is wrong.** `E4_WO_INST_FINAL_DECISION.json`
(2026-08-12) records `proven_invalid: true` and `authorized_corrective_reruns: 40` for that arm, because
it skipped P2 through the gate described in SS0.2. Every sibling E4 U-Air arm carries a
`p2_invocation_states.json` of 0.87-1.23 MB; `raven_wo_inst` carries **3 bytes, an empty list**.
TwoStage-Hajek takes the same `alpha = beta` branch for its own reasons, since its policy has no
instant-calibration flag either, so the two coincide **through a shared control-flow path, not by being
the same method**. The corrective reruns give `Delta_group` `1.0914` on U-Air, not `1.1196`, and they are
what Table IV reports (SS0.3).

The second identity does carry a finding: `inst_cal` and `raven_wo_debt` differ only in
`uses_hajek_local_loss`, so **the Hajek local loss is numerically inert on U-Air**. `inst_cal` is a row
of `tab:app_e3_uair` while `raven_wo_debt` is not, so this coincidence does not create a duplicate row.

**Corrected statement of the levers.** With P2 preserved, the corrected ablation moves `Delta_group` by
`-0.089 %` on U-Air and `-0.260 %` on SensorScope when instant calibration is removed, and by at most
`0.26 %` for any other single component, against `-6.943 %` for the Design factor on U-Air. On U-Air the
Design factor is the only component that moves `Delta_group` materially, and **instant calibration is
not a lever**. Revision 2's claim that the effective levers are "{design factor, P2 instant calibration}"
is withdrawn. What survives is the weaker and better-supported statement that the manuscript's stored
ablation family shows one dominant component and five inert ones.

---

## 5. E2 / Table R1 — single-batch re-evaluation: `E2_UAIR_CELLS.csv`, `E2_UAIR_SUMMARY.csv`

One checkpoint source per row; `RMSE_mu` and the four block RMSEs recomputed from
`checkpoints/final.pt`; `WorstGroupRMSE = max` of the four blocks; both domains stored.
`Δ_group` and `Δ_c-s` are read from that same run's `final_metrics.json` (the plan's SS7 E2 named
`RMSE_μ` and block RMSEs as the recomputation targets).

### Table R1 — U-Air no-Design family on the licensed set (20 seeds, standardized domain)

| method | `RMSE_μ` | `WorstGroupRMSE` | `Δ_group` | `Δ_c-s` | source |
|:---|:---|:---|:---|:---|:---|
| FedAvg-Window | 1.111932 ± 0.0603 | 1.169045 ± 0.0692 | 1.044620 | 1.313777 | E1 |
| FedAsync-Window | 1.111924 ± 0.0599 | 1.169044 ± 0.0688 | 1.045149 | 1.313666 | E1 |
| TimeAlign-Agg | 1.112002 ± 0.0597 | 1.169134 ± 0.0685 | 1.044768 | 1.314519 | E1 |
| Debt-Cal | 1.114378 ± 0.0645 | 1.171764 ± 0.0741 | **1.017533** | **1.294779** | E1 |
| FedAU-Window | 1.112813 ± 0.0600 | 1.170075 ± 0.0689 | 1.055671 | 1.329103 | frozen tree |
| ObsUse-Window | 1.112034 ± 0.0600 | 1.169211 ± 0.0689 | 1.041296 | 1.323475 | frozen tree |
| **RAVEN-NoDesign** | **1.113059** ± 0.0638 | **1.170275** ± 0.0734 | **1.016515** | **1.294934** | E4 tree |

Physical domain (`RMSE_mu_phys = *_std x 17.36325121670317`), 20-seed means: FedAvg 19.306761,
FedAsync 19.306615, TimeAlign 19.307969, Debt-Cal 19.349231, FedAU 19.322047, ObsUse 19.308533,
RAVEN-NoDesign **19.326325**.

**On prediction the licensed no-Design family is a six-way tie**: FedAvg / FedAsync / TimeAlign /
FedAU / ObsUse / RAVEN-NoDesign span `1.1119`-`1.1131`, i.e. **0.11 %**. Debt-Cal is the only row
that separates, at `1.1144` (+0.22 %).

### 5.1 Two exact confirmations of the σ arithmetic (record item N7)

| row | E2 physical domain | sealed `TABLE_II_E3_MAIN_EFFECTIVENESS_FINAL.csv :: RMSE_mu_mean` | match |
|:---|:---|:---|:--:|
| U-Air Central-All | **18.328143** | 18.328143 | ✓ |
| U-Air Central-Delivered | **20.456610** | 20.456610 | ✓ |

These are independent rows, not the one σ was derived from. They establish that the sealed table
source is the **physical** domain of the same quantities the manuscript prints in the
**standardized** domain: `metric_scale_policy.json` for `uair` records `zscore_applied: true`,
`sigma = 17.36325121670317`, `conversion: OFFLINE_LINEAR_CONVERSION`, while `sensorscope` records
`zscore_applied: false`, `sigma: null`, `IDENTITY_RAW_PHYSICAL`. `Σ` and `Δ` columns are
scale-invariant.

---

## 6. E3 / Table R2 — downstream recomputation: `P2_COVERAGE.csv`, `PAIRED_STATS.csv`

### 6.1 `tab:app_p2_coverage`, U-Air row, four rebuilt methods substituted

The published row was built from the 180-run U-Air windowed set (9 methods x 20 seeds; central
methods have no `window_metrics.json`). "Active windows" = windows with `active == true`; the
definition was validated by reproducing **both** published rows exactly from untouched trees:

| row | recomputed from frozen trees | published in `appendix.tex` |
|:---|:---|:---|
| U-Air | 180 runs / **70.1000** / **63-75** | 180 / 70.10 / 63-75 |
| SensorScope | 180 runs / **93.8500** / **88-98** | 180 / 93.85 / 88-98 |

Substituted row:

| set | per-method mean active windows | aggregate |
|:---|:---|:---|
| 4 rebuilt methods | **75.75** each (min 73, max 79) | — |
| 5 unchanged methods | 70.10 each (min 63, max 75) | — |
| **substituted** | — | **180 runs / 72.6111 / 63-79** |

The four rebuilt methods each gain 5.65 active windows per run, because on the licensed set they
see the full delivered client set.

### 4.5 G2 executed — the hybrid blocks are cleared

Run through `run_nodesign_supplement.train_one`, the routine the plan names (`rns.OUT` redirected to
this report's write root so the SS14 boundary holds). One seed per block, three methods each; metrics
compared against the frozen ledgers `CS_TRAIN_LEDGER.json` / `JO_TRAIN_LEDGER.json`:

| block | method | result |
|:---|:---|:---|
| `cityscanner_nyc_pm25` | `fedavg_window`, `fedau_window`, `obsuse_window` | **BIT-IDENTICAL** |
| `cityscanner_nyc_p2_measured_o` | `fedavg_window`, `fedau_window`, `obsuse_window` | **BIT-IDENTICAL** |

Decision rule (the reviewer's, and it is the right one): the current `fedavg_window` is `ζ≡1`, i.e.
full delivery. If it reproduces a frozen ledger bit-exactly on a block where roughly 70 % of `π^opp`
pairs have `π^tar = 0` (plan SS2 item 4: 673/959 for City Scanner, 613/942 for Pilot 2), then the
frozen run **cannot** have dropped those pairs — a restricted run would have produced a different
model. All six cells reproduce, so **City Scanner and Pilot 2 used the licensed set**, and route A's
correctness damage is confined to U-Air. `G2_RUN_REPORT.json`.

Note the frozen ledgers carry `design_on: true` on the `fedau_window` rows, which is why the plan
flagged these blocks; the bit-identical reproduction shows that flag did not affect the active set.

### 6.2 Table R2 — paired RAVEN-NoDesign minus comparator, relative

t-intervals on n-1 df; Holm across the six comparators within each metric and slice. Bold =
interval excludes 0 and the ALL20 point estimate agrees in sign.

| comparator | `RMSE_μ` (TEST / ALL20) | `WorstGroupRMSE` | `Δ_group` | `Δ_c-s` |
|:---|:---|:---|:---|:---|
| FedAvg-Window | +0.545 % (3/10) / +0.089 % (7/20) | +0.581 % / +0.090 % | **−3.078 % / −2.711 %** (20/20) | **−1.360 % / −1.424 %** |
| FedAsync-Window | +0.604 % (3/10) / +0.089 % (8/20) | +0.644 % / +0.088 % | **−3.117 % / −2.760 %** (20/20) | **−1.348 % / −1.416 %** |
| TimeAlign-Agg | +0.560 % (3/10) / +0.080 % (8/20) | +0.596 % / +0.079 % | **−3.091 % / −2.722 %** (20/20) | **−1.405 % / −1.480 %** |
| **Debt-Cal** | −0.124 % (6/10) / −0.115 % (12/20) | −0.134 % / −0.124 % | **−0.052 % / −0.089 %** (10/20) — **not significant** | −0.055 % / +0.015 % — tie |
| FedAU-Window | +0.449 % (3/10) / +0.011 % (10/20) | +0.478 % / +0.002 % | **−3.942 % / −3.733 %** (20/20) | **−2.662 % / −2.553 %** |
| ObsUse-Window | +0.422 % (3/10) / +0.080 % (9/20) | +0.443 % / +0.075 % | **−2.532 % / −2.403 %** (20/20) | **−2.296 % / −2.143 %** |

Holm: `RMSE_μ` and `WorstGroupRMSE` are **non-significant against every comparator** (min Holm p
0.69 and 0.72, TEST). `Δ_group` and `Δ_c-s` are significant against **five of six** — Holm p
`1.9e-5`-`7.5e-4` for `Δ_group`, `3.5e-4`-`6.5e-4` for `Δ_c-s` (TEST), `≤1.7e-6` (ALL20) — and
**not against Debt-Cal** (Holm p 0.71 and 0.67 TEST; 0.41 and 0.90 ALL20).

### 6.3 The pre-registered analysis outcome

The plan's SS8 rule: *"The `Δ_group` claim is stated as unqualified only if it holds against all
six comparators. Otherwise the text names the comparators it holds against and the ones it does
not."*

**It does not hold against all six.** Debt-Cal ties RAVEN-NoDesign on `Δ_group` (`1.017533` vs
`1.016515`, relative −0.089 %, interval spanning zero). **The plan pre-registered this exact risk in
its SS8** ("Debt-Cal is the open risk … the row most able to remove the `Δ_group` advantage"), naming
its frozen restricted `Δ_group` of 1.0976 against NoDesign's 1.0165. It materialised.

Consequences for the manuscript, which the plan's wording rule already dictates:

- `Δ_group` must be **qualified**: RAVEN-NoDesign beats FedAvg, FedAsync, TimeAlign, FedAU and
  ObsUse by 2.4-3.7 % (20/20 seeds each) and **ties Debt-Cal**.
- `Δ_c-s` has the same shape: significant against five, tie against Debt-Cal.
- Prediction and `WorstGroupRMSE`: **ties against all six** (point estimates −0.12 % to +0.64 %, no
  significant difference in either direction).
- The manuscript sentence "improves on TwoStage-Hájek and FedAvg (TEST $-9.11\%$ and $-6.17\%$)" —
  **quoted here in the manuscript's own order; an earlier version of this report transposed the two
  percentages, which the reviewer caught** — splits into two halves:
  - the **FedAvg half (−6.17 %)** is superseded. It was measured against the contaminated batch; the
    rebuilt comparison on the same metric is **+0.581 %**.
  - the **TwoStage-Hájek half (−9.11 %)** is **not** overturned by the active-set repair. TwoStage's
    policy sets `uses_design_ratio=True`, so its restricted active set is licensed, and G1c confirmed
    its numbers come from the E3 tree. The reviewer is right that it should be restated as a
    within-Design-family comparison rather than dropped — and SS5.2 sharpens that further: on U-Air,
    TwoStage-Hájek *is* RAVEN without instant calibration, so this is a comparison against an
    ablation arm of the same method, not against an external baseline.

### 6.4 A downstream manuscript dependency the substitution invalidates

Flagged by the reviewer and verified: `appendix.tex` states, in the prose after
`tab:app_p2_coverage` (lines 1584-1588) and again in a table (lines 1607-1610):

> "The solver log contains 778 numerical-inaccuracy warnings across 85 affected formal runs. The
> reconstruction audit covers 6438 active P2 windows and certifies feasibility; the maximum
> reconstructed constraint residual is $2.686\times10^{-8}<10^{-7}$."

Those three numbers describe **the pre-repair U-Air + SensorScope solver batch**. E3 replaces four of
the nine U-Air windowed methods, and `debt_cal` is one of them — its P2 solves change. So the three
sentences no longer have support on the substituted batch and must be re-audited when R4 is applied.
The `tab:app_p2_coverage` cells themselves are fine (SS6.1); it is the surrounding feasibility audit
that is now unstaked. This dependency was **not** identified in the first version of this report.

---

## 7. Table R3 — gates, and Table R4 — replacement proposal

### R3

| gate | runs | result |
|:---|--:|:---|
| G1a | 3 | 2 bit-exact `0.0`; `debt_cal` `2.0677e-07` → pass under the SS0 amendment |
| G1b | 1 | bit-exact `0.0` |
| G1c | 6 | **6/6 reproduce the E3 tree, 0/6 the repro CSV** |
| G1d | 2 | both match `results_table2_audit` |
| **G2** | **6** | **all six hybrid cells BIT-IDENTICAL to the frozen ledgers → City Scanner and Pilot 2 cleared** (SS4.5) |
| C1 | 2 | frozen U-Air `raven_wo_design` reproduces **bit-exactly** (`abs_diff = 0.0`) |
| C2 | 2 | 171 `solve_p2` calls; **0** non-finite / **0** negative `variance_diag` → the sanitisation never fires (SS0.1) |
| C3 | 0 | **BLOCKED** by the unfinished call site in the `wo_inst` repair (SS0.2, SS4.3) |

### R4 — proposal only; nothing has been changed

| manuscript location | cell(s) | old | replaced by | new |
|:---|:---|:---|:---|:---|
| Table III, U-Air FedAvg-Window | 4 | 1.1882 / 1.2596 / 1.1218 / 1.2621 | R1 FedAvg | **1.1119 / 1.1690 / 1.0446 / 1.3138** |
| `tab:app_e3_uair` | FedAvg, FedAsync, TimeAlign, Debt-Cal | 1.1882-1.1893 | R1 | **1.1119-1.1144** |
| `tab:app_e3_uair` | Design-on rows | — | unchanged (G1c selected the tree) | — |
| `tab:app_block_rmse`, UA FedAvg-Window | 5 | tree values | E2 | `E2_UAIR_CELLS.csv` |
| `tab:app_p2_coverage`, U-Air | 3 | 180 / 70.10 / 63-75 | E3 | **180 / 72.6111 / 63-79** |
| prose: the `−6.17 %` sentence; the Local-Hájek coincidence sentence | prose | — | R2 wording rule; "coincides with FedAvg restricted to the Design support" | — |

`local_hajek` is **unchanged** by the rebuild (`1.192251 / 1.1218 / 1.2621`), because its policy sets
`uses_design_ratio=True` and its restricted active set is therefore licensed. Its identity with the
old `fedavg_window` is an identity with *FedAvg restricted to the Design support*; only the
explanatory sentence changes.

---

## 8. Plan versus measurement: where the plan held, and four defects

**Where the plan held.** Its SS2 inventory figures reproduce exactly (SS2 above). Its SS8 arithmetic
expectations reproduce: "FedAsync and TimeAlign coincide with the frozen FedAvg to 0.02 %" — measured
on the licensed set they sit `−0.0007 %` and `+0.0063 %` from rebuilt FedAvg; "expected to land near
the rebuilt FedAvg (1.1119)" — they landed at 1.1119 and 1.1120. And its SS8 risk statement about
Debt-Cal was **correct and pre-registered** (SS6.3).

**Four defects, each documented rather than worked around:**

1. **G1a's pass rule is internally inconsistent with the plan's own E2 tolerance.** G1a demands bit
   equality while SS7 E2 relies on `1e-6`. That inconsistency is what forced the SS0 amendment.
2. ~~**G2 is not executable as written.**~~ **RETRACTED — this was my error, and the reviewer
   caught it.** The plan's SS14 explicitly names `run_nodesign_supplement.train_one` as one of the
   three routines to reuse; I looked for a `load_paper_dataset` path instead, concluded the hybrids
   needed a `src/` change, and never read the routine the plan named. `train_one`
   (`scripts/run_nodesign_supplement.py:169`) monkeypatches `runner._process_window` at `:200/225`
   and returns per-window metrics from `runner.run()` at `:227`; the module also carries
   `_load_cityscanner` / `_load_pilot2` and `build_setup`. **G2 was therefore executed via exactly
   that path** (SS4.5 below), at a cost of a few minutes, and it produced a stronger result than the
   feasibility note I had proposed: **all six frozen hybrid rows reproduce bit-identically under full
   delivery, so City Scanner and Pilot 2 are cleared on those cells**, and route A's damage is
   confined to U-Air. This was the most consequential of my errors: I had declared a plan stage
   impossible that the plan had already solved.
3. **The T-Drive `pi^tar` hole count is not derivable.** `load_spatial_to_client` has no `tdrive`
   branch (`src/raven_mcs/e3/canary/dataset_load.py:76-85`), and no stored hybrid `pi^tar` exists
   under `results_tdrive_rank/` or `manuscript_evidence_closure_r1/09_tdrive_decision/`. Recorded as
   `NOT_COUNTED` with the reason rather than estimated.
4. **The plan's E2 note about `store_fields` is factually wrong.** SS7 E2 says `*_std`/`*_phys`
   "fills the `store_fields` contract that `metric_scale_policy.json` declares and **no run currently
   honours**". Every run already honours it, in `final_metrics_dual_domain.json` — e.g. U-Air
   `fedavg_window` seed 30001: `RMSE_mu_std = 1.210848`, `RMSE_mu_phys = 21.024266`,
   `MAE_mu_std/phys`, `Tail_RMSE_std/phys`, `Head_RMSE_std/phys`, `RMSE_rho_std/phys`. E2's physical
   column is therefore an arithmetic cross-check, not a contract repair.
   **Provenance of the error, stated plainly:** this claim was inherited from an earlier record of
   mine (`raven-mcs-metric-definition-diagnosis.md`, item N7, clause 3), which asserted the declared
   store fields were materialized nowhere. That clause was wrong and has since been corrected. If
   you are auditing the plan, treat this item as my error propagating into it, not the plan author's.

---

## 9. Falsification targets — what I most want challenged

Revised after review: two of the original five were answered by evidence gathered this round, one was
withdrawn, and one new one replaced it.

1. **The SS0 amendment.** Still the reviewer's call, but the grounds changed: the "E2 tolerance
   precedent" argument is withdrawn, and the case now rests on magnitude plus the fact that C1 shows
   the decisive comparator to be bit-reproducible on U-Air. If you judge that `2.07e-07` on an
   unaffected block still confounds E1, E1's numbers should be withdrawn — the plan's literal
   instruction was to stop.
2. **The `debt_cal` drift attribution. Replaced.** My `p2_cvxpy.py` lead is dead (C2: the
   sanitisation never fires; the new parameter defaults to `True`). The leading candidate is now the
   reviewer's own: `lambda_beta=1e-8`, the one property unique to `debt_cal` among P2 users. Note this
   is *now a case where I would like the reviewer to be wrong*, because if `lambda_beta=1e-8` is the
   cause then the arm is genuinely ill-conditioned and the drift is a property of Debt-Cal's
   configuration rather than of the code state.
3. **The unfinished `wo_inst` repair (SS0.2).** I claim the current working tree cannot run
   `raven_wo_inst` at all. This is directly reproducible in one command, so it is the cheapest thing
   here to falsify.
4. **P2 coverage substitution.** The reading is now guard-backed (both published rows reproduce
   exactly), and the reviewer's reliability judgement matches mine. What is *new* and worth
   challenging is the downstream claim in SS6.4: that the appendix's 778/85/6438/`2.686e-8` sentences
   lose their basis on the substituted batch. If those numbers were computed over a different run set
   than the 180 windowed runs, my claim is wrong.
5. **`WorstGroupRMSE` provenance.** Unchanged: recomputed from checkpoints via
   `audit_table2_uair_fedavg.block_rmse`, itself only verified at `1e-6`; the Central rows need a
   checkpoint unwrap that the plan's routine lacks.
6. **SS5's attribution, and the blocked 2x2.** No single component explains Debt-Cal's route to the
   same structural endpoint. On the corrected ablation the Design factor moves `Delta_group` by
   `-6.943 %` on U-Air, while debt moves it by `0.004 %`, observation IPW by `0.123 %`, usable IPW by
   `0.014 %` and instant calibration by `-0.089 %`. The family therefore isolates the Design factor and
   leaves the rest unattributed. An earlier version of this item claimed instant calibration was
   decisive, quoting `raven_wo_inst` at `1.119606`; that arm is invalidated (SS0.3). Neither of us has
   the controlled 2x2 (SS4.3, blocked). Attack the attribution, not the direction.

## 10. What this round does not establish

- No manuscript file was touched and no table cell replaced. R4 awaits authorization.
- City Scanner, Pilot 2 and T-Drive active sets remain **unverified** (SS8 items 2-3). No claim here
  covers the hybrid blocks.
- `debt_cal`'s G1a arm is reproduced to `1e-6`, not bit-exactly, and the residual is deterministic
  but not causally pinned (SS0.1).
- `Δ_group` and `Δ_c-s` for the rebuilt rows come from each run's own `final_metrics.json`, not
  recomputed from checkpoints.
- No Holm correction **across metrics**; Holm was applied across the six comparators within each
  metric and slice, as the plan's SS8 specifies.
- The `uair` physical domain depends on `sigma = 17.36325121670317` from
  `metric_scale_policy.json`; the paper prints the standardized domain and discloses neither.
  SS5.1 confirms the arithmetic on two independent rows but does not adjudicate which domain the
  manuscript *should* print.

---

## 11. Artifact manifest and write set

All paths below are relative to `results_active_set_repair/round_v1/`. `MANIFEST.sha256` covers this
directory plus `scripts/run_active_set_repair.py`; `verify_report_claims.py` section S7 checks it.

| artifact | size | what it evidences |
|:---|--:|:---|
| `ACTIVE_SET_INVENTORY.csv` | 52 500 B | 640 run-window comparisons, 80 violations (G0) |
| `PI_TAR_HOLES.csv` | 511 B | `pi^tar` support and holes per block (G0) |
| `HYBRID_PHI_DECISIONS.json` | 2 854 B | stored City Scanner / Pilot 2 zero-target decisions |
| `G0_SUMMARY.json` | 1 194 B | G0 roll-up |
| `G1_REPORT.json` | 4 582 B | G1a-G1d values, incl. the `amendment` block |
| `G1_DEBT_CAL_DIAG.json` | 737 B | the three determinism measurements |
| `E1_RUNS.csv` / `E1_ASSERTIONS.csv` | 4 807 / 3 730 B | 80 runs and 80 per-run active-set assertions |
| `E2_UAIR_CELLS.csv` | 81 864 B | per-seed, per-row, std + phys domains |
| `E2_UAIR_SUMMARY.csv` | 5 842 B | R1 aggregates and TEST/ALL20 slices |
| `P2_COVERAGE.csv` / `P2_COVERAGE_PER_RUN.csv` | 224 / 4 796 B | substituted `tab:app_p2_coverage` row |
| `PAIRED_STATS.csv` | 6 036 B | R2: paired relatives, t-intervals, wins, Holm p |
| `G2_REPORT.json` | 1 727 B | **superseded** — G2 feasibility note from revision 1; G2 was executed, see below |
| `C1_RAVEN_WO_DESIGN_REPRO.json` | rev 2 | frozen U-Air `raven_wo_design` bit-reproduction (SS0 ground 2) |
| `C2_VDIAG_SANITISATION.json` | rev 2 | 171 `solve_p2` calls instrumented; the sanitisation never fires (SS0.1) |
| `C3_TWO_BY_TWO.json` | rev 2 | the 2x2 arm, recorded `BLOCKED`, with root cause and unblocking options (SS0.2, SS4.3) |
| `G2_RUN_REPORT.json` | rev 2 | the six executed hybrid cells, all BIT-IDENTICAL (SS4.5) |
| `WORKTREE_DIFF.sha256` | rev 2 | sha256 of every uncommitted `src/` diff at hand-over, plus `git HEAD` |
| `EXECUTION_LOG.md` | 1 702 B | stage log |
| `ACTIVE_SET_REPAIR_REPORT.md` | 20 696 B | the earlier execution-facing report (superseded by this file for verification) |
| `verify_report_claims.py` | this round | the runnable verifier |
| `../scripts/run_active_set_repair.py` | this round | the driver; `--stage status` lists the write set |

Run trees produced this round: `repair/C0_frozen/{uair,sensorscope}/{method}/seed{seed}/` (90 runs)
and `repair_solo/`, `repair_again/` (2 diagnostic runs).

---

## 12. Manuscript write — 2026-09-27, separately authorized after R4

The user authorized the R4 cell replacements and the accompanying prose on 2026-09-27, after the
experiment round above had finished. **The boundary statements in SS1 describe the experiment round
only**; the manuscript edit is a distinct, later action recorded here.

| # | change | where |
|:--|:---|:---|
| 26 | U-Air `FedAvg-Window` row: `1.1882→1.1119`, `1.2596→1.1690`, `1.1218→1.0446`, `1.2621→1.3138` | `main.tex` Table III |
| 27 | `tab:app_e3_uair`: FedAvg / FedAsync / TimeAlign / Debt-Cal rows replaced; caption states each row uses the active set its own definition licenses | `appendix.tex` |
| 28 | `tab:app_block_rmse` UA `FedAvg-Window`: `1.1015 / 1.1144 / 1.1690 / 1.0721`, WG `1.1690` | `appendix.tex` |
| 29 | `tab:app_p2_coverage` U-Air: `70.10 / 63--75 → 72.61 / 63--79` | `appendix.tex` |
| 30 | the `TEST $-$9.11 % / $-$6.17 %` sentence replaced by the within-Design-family statement and the six-comparator `Δ_group` qualification | `main.tex` §V |
| 31 | Local-Hájek coincidence attributed to the shared Design-support restriction | `main.tex` §V |
| 32 | metric scale disclosed (U-Air and NSW-Traffic standardized, SensorScope physical, ratio columns invariant), closing record item N7 | `main.tex` §VII-A |

Build invariants after the write: main **16 pages**, supplement **15 pages**, equation labels **41**,
0 undefined references or citations, 0 overfull boxes above 2 pt,
`tools/freeze_appendix_refs.py --check` reports 0 to freeze and 0 unresolvable (57 kept), em dashes
2 in `main.tex` and 0 in `appendix.tex`. Verifier section S11 re-checks every replaced cell against
the artifacts in this directory and asserts the old values are gone.

**Deliberately not written.** The three feasibility-audit counts (778 warnings / 85 runs / 6438
windows / $2.686\times10^{-8}$) still describe the pre-repair batch. Their population is not the
180-run set that `tab:app_p2_coverage` covers, so the effect of substituting the rebuilt methods
cannot be determined without a solver-log re-audit; the numbers were left untouched rather than
replaced by estimates. This is the one R4-adjacent item still open.

**Next owner.** `ccf-integrity-auditor` to check R1-R4 and the SS12 cells against the run trees; the
prose in SS12 items 30-32 is `ccf-paper-writer` territory and has not had a second review.
