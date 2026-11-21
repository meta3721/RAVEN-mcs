# Diagnostic record — consolidated: correctness defects, the measured gain ceiling, layer provenance, and the RAVEN-MCS evidence base

```text
Date: 2026-09-23 (supersedes the 2026-09-20 metric-definition record)
Added: 2026-09-24 — D-6, §2 L6–L9, §3 T8: the constructed regime as a bound on the achievable gain
Implemented: 2026-09-24 — F-3 in `main.tex` §VII-A.2 and `appendix.tex` (A5/A6 audit); §7 items 16–17
Corrected: 2026-09-24 — T3 restated: `RAVEN-SimOracle` is a joint p/q oracle, so the null cannot be
           attributed to `q`; the U-Air readings are re-derived as −0.028% (sd 0.265%). Touches
           §0 D-6, §2 L7, §3 T3, §3 T8, §8 F-2. The same correction was applied to
           `raven-mcs-method-revision-evaluation.md`. No manuscript file changed.
Implemented (paper): 2026-09-25 — D-1 as Option 1: φ removed from all three `.tex` files, the Design
           factor restated as an explicit configuration, and Table III plus the appendix four-block
           table completed into a within-dataset Design factorial (§7 items 18–21). Main 16 pp.,
           supplement 15 pp., equation labels 41, 0 undefined, 0 overfull > 2 pt.
Executed:  2026-09-24 — F-1 and the ceiling map. The ceiling map is read from the frozen artifacts
           (**T9**); F-1 ran 160 new cells and returns Δ_oracle = +0.104% / −0.251%, inside the
           pre-registered bound, so **H-A is refuted** (§3 T8 item 2, §3 T8's H-A outcome, §8 item 8).
           Standalone write-up: `ccfa-review-reports/raven-mcs-f1-experiment-summary.md`.
           Anchor correction the same day: the `raven` cell is the forced-Design row on U-Air, not
           the deployed method (T9); the U-Air columns of T9 and F-1 carry that caveat.
Executed (H/U1): 2026-09-24/25 — the H headroom grid (180 runs, pre-registered STOP on 5 seeds) and
           its U-Air extension **U1** (270 new runs, 45 new traces, 20 seeds): the pre-registered GO
           rule never fired, all six |H| ≤ 0.217 %, and the Design support cost settled at
           **+6.31…+6.99 %** with every CI lower bound above **+4.75 %**. §3A;
           `results_h_headroom/round_v1/` and `round_u1/`.
Audited:   2026-09-25 — the main comparison's U-Air `FedAvg-Window` cell traced to a 2026-08-11
           runner that dropped the zero-target-mass pairs. §2A N1; `results_table2_audit/`.
Corrected: 2026-09-27 — **four corrections to §2A** (N3 rewritten, N4 downgraded to a disclosed
           redundancy, N7 added, N2 given its metric attribution). The `−6.17 %` / `−9.11 %` sentence
           is `WorstGroupRMSE` **paired TEST**, and on that metric against equal-delivery comparators
           it is `+0.48 %` / `+0.44 %`; on `RMSE_μ` the win is `+0.54 %` (TEST) / `+0.09 %` (ALL20),
           not `+0.55 %`. The earlier claimed "0.35 % printed-versus-recomputed gap" **was wrong** and
           is withdrawn. See §7 items 22–25.
Reviewed:  2026-09-25 — full review after Option 1: absolute **4/10 weak reject**, progress
           **+0.40**. `ccfa-review-reports/raven-mcs-tmc-review.md`; the prior version is kept at
           `snapshots/raven-mcs-tmc-review-2026-09-20-pre-option1.md`.
Manuscript: TO_OVERLEAF_paper_tmc_r1_clean (main.pdf 16 pp. + supplemental.pdf 15 pp.)
Inputs: this record; ccfa-review-reports/raven-mcs-method-revision-evaluation.md (2026-09-23)
Status: assessment and decision record. This record itself changed no manuscript file.
        The P0 edits in §7 items 12-15 were applied separately, on explicit instruction.
Boundary: changes listed in §7 are those made after the previous review round (2026-09-12).
Purpose: **consolidated 2026-09-25.** Part I orders every finding by class and weight and points into
         the evidence below; Part II holds the evidence and the ledger.
         Structure note: section numbers 0–11 and every item label (R, L, T, S, E, G, D) are
         unchanged, because other documents cite them. New material is inserted as §2A and §3A
         rather than renumbering anything.
Contents: Part I — consolidated diagnosis, ordered by importance
          Part II — §0 decisions; §1–§2 root defects 1–2; §2A correctness defect (U-Air baseline);
                    §3 root defect 3 (ceiling); §3A the headroom experiments; §4 scenarios;
                    §5 earlier problems; §6 degeneration; §7 changelog; §8 next actions;
                    §9 incident log; §10 reproduce; §11 boundaries
```

---

# Part I — Consolidated diagnosis, ordered by importance

## I.1 The verdict in one paragraph

The manuscript is an honest, well-scoped paper whose central empirical claim cannot be supported on
the blocks it reports, and which additionally contains one comparison that its own artifacts
contradict. Five classes of finding are now established. **Tier 1** is correctness: the U-Air
`FedAvg-Window` and `Local-Hájek` rows of the main comparison were produced by a runner that dropped
the zero-target-mass training pairs, so one stated win is an artifact of an unequal-information
baseline. **Tier 2** is the evidence ceiling: the correction family cannot move the primary endpoint
by 0.5 %, and two independent pre-registered experiments now show this is a property of the
endpoints, not of the testbed being too easy. **Tier 3** is provenance: the deployment target is
evaluation-derived and `U` is measured nowhere, so the objects are not what they are named.
**Tier 4** is a ledger of what has been repaired. **Tier 5** is the repair routes that remain, ranked
by what they can still buy. Absolute readiness on the frozen rubric is **4/10 weak reject**; the last
revision measured **+0.40** on the progress scale without moving either defect that sets the verdict.

## I.2 Tier 1 — correctness: the paper states what its artifacts contradict

A wrong number outranks a weak claim, because it is the one class of defect that invalidates work
built on top of it.

| # | finding | where | status |
|:--|:---|:---|:---|
| **N1** | The main comparison's U-Air `FedAvg-Window` cell came from a runner that removed the 72 of 288 `(client, stratum)` pairs with `π^tar = 0`; `RAVEN-NoDesign` keeps them, and `FedAU`/`ObsUse` were run later and keep them too | §2A | measured, reproducible |
| **N2** | The paper's `−6.17 %` / `−9.11 %` are **`WorstGroupRMSE`, paired, TEST** relatives measured against the contaminated batch — a metric attribution the source report left implicit. On that same metric against equal-delivery same-family comparators they become **+0.48 %** (`FedAU`) and **+0.44 %** (`ObsUse`); on `RMSE_μ` the win becomes **+0.54 %** (TEST) / **+0.09 %** (ALL20). `FedAU` and `ObsUse` show the *same* −6.2 %/−6.6 % gap against the frozen row, so the anomaly is the FedAvg row and not a RAVEN result | §2A | measured |
| **N3** | The U-Air `FedAvg-Window` row is **assembled from two frozen batches that disagree**. `RMSE_μ`, `Δ_group` and `Δ_c-s` come from the E3 run tree; `WorstGroupRMSE` comes from the public-repro per-seed CSV. The two artifacts differ at **3 of 20 seeds** — 30007 +4.23 %, 30016 −2.00 %, 30018 +4.91 % — and the last two are inside the TEST window | §2A | root cause located; the printed `1.1882` **is** the stored ALL20 mean `1.188238` |
| **N4** | `Local-Hájek` is **bit-identical** to the frozen `FedAvg` on both datasets, so it inherits the same restriction and must be corrected with the same row. The manuscript already discloses the coincidence and its cause | §2A | measured; disclosed in the main text beside Table III |
| **N5** | What survives: after equalising delivery, U-Air prediction is a four-way tie (1.1119–1.1131) and the claim must move to `Δ_group` (`RAVEN-NoDesign` 1.0165 versus 1.0446 / 1.0557 / 1.0413) | §2A | measured |
| **N6** | The `raven` cell is the **forced-Design** row on U-Air, not the deployed method; Table III's U-Air method is `raven_wo_design` = 1.1131. Any analysis calling `1.1911` "the published method" compares against the wrong run | §3 T9 | corrected in T9 and both F-1 documents |
| **N7** | Table III's `RMSE_μ` column **mixes metric scales across datasets**. SensorScope is raw physical (`IDENTITY_RAW_PHYSICAL`, no sigma); U-Air is z-scored by `sigma = 17.36325121670317` (`OFFLINE_LINEAR_CONVERSION`). Neither sigma nor the standardization is disclosed in the paper, and the sealed table source stores U-Air in the **opposite** (physical) domain | §2A | measured; **new this round** |

What survives from the U-Air comparison: `RAVEN-NoDesign` `Δ_group` = **1.0165** against current
FedAvg `1.0446`, `FedAU` `1.0557` and `ObsUse` `1.0413`. On prediction the four are within ±0.15 %.

## I.3 Tier 2 — the evidence ceiling: the central claim cannot be supported on these blocks

| # | finding | where |
|:--|:---|:---|
| **T-a** | Every propensity route moves `RMSE_μ` by **≤0.03 %** in either direction; exact `p` and `q` together are worth +0.008 %/−0.028 % | §3 T1–T9 |
| **T-b** | The best any reweighting reaches is 0.112 % on SensorScope; on U-Air, re-anchored to the deployed method, the uncorrected central reference is **5.85 % worse** | §3 T9 |
| **T-c** | **The ceiling is not a testbed artifact.** F-1 hardened the observation propensity inside the stratum (Δ_oracle **+0.104 %/−0.251 %**); H/U1 stressed six conditions with a pre-registered 0.5 % bar and no cell exceeded 0.217 % in magnitude and none fired GO. Two independent manipulations, one verdict | §3 T8, §3A |
| **T-d** | **H-A is refuted**; what remains is H-B, endpoint weight-blindness | §3 T8 item 2 |
| **T-e** | The structural endpoint the paper wins on is decoupled from prediction by the paper's own ablations | §3 T4, §6 |
| **T-f** | `U` is measured in no block, so the layer carrying most of the machinery is simultaneously unmeasured and worth ≤0.03 % | §2 L1, §2A |

## I.4 Tier 3 — provenance and scope: the objects are not what they are named

| # | finding | where | moved? |
|:--|:---|:---|:---|
| **P-a** | The deployment target is evaluation-derived (`RMSE_μ` against a test-split share) | §1 R1–R4 | **no** |
| **P-b** | Both selection margins are stratum-constant by construction, so the reported regime is the easy one; now disclosed with its dispersion | §2 L6–L9 | disclosed only |
| **P-c** | The six-scenario family is complete and never enumerated; `complete_counteracting` is invisible | §4 S1–S7 | **no** |
| **P-d** | Equal-weight problems that survive independently of the above | §5 E1–E6, §6 G1–G7 | **no** |

## I.5 Tier 4 — what has been repaired (ledger)

| decision | what it fixed | evidence |
|:---|:---|:---|
| **D-4** | Layer provenance and construction constants stated; abstract, Table III caption and limitations scoped | §7 items 12–15 |
| **D-6** | The dispersion of the two margins stated beside the constants | §7 items 16–17 |
| **D-1** | φ removed from all three `.tex` files; the Design factor restated as an explicit configuration; Table III completed into a within-dataset 2×2 factorial; the appendix statistic demoted to descriptive provenance | §7 items 18–21 |
| **D-6 / T8** | F-1 executed; H-A refuted | §3 T8, `raven-mcs-f1-experiment-summary.md` |

## I.6 Tier 5 — repair routes, ranked by what they can still buy

| rank | route | what it buys | status |
|:--|:---|:---|:---|
| 1 | **Restate and rebuild the U-Air comparison**: equal delivery, one frozen batch per row, and a stated metric scale (N1, N2, N3, N4, N7) | removes a wrong comparison and a mixed-provenance row; the only Tier-1 repair available without new data | numbers in hand |
| 2 | **Report the endpoint-keyed Design rule** (Design helps `Δ_c-s` in 3 of 4 blocks, hurts `Δ_group` in 3 of 4; mechanism = the **+6.31…+6.99 %** support cost, all CI lower bounds above +4.75 %) | closes review M1 and M4 at zero compute | numbers in hand |
| 3 | **State the ceiling** using F-1 + H/U1 | converts "we are competitive" into a measured bound; +0.5 on Evidence | numbers in hand |
| 4 | **Obtain an exogenous target map** (D-2/D-3) | the only route that addresses P-a; nothing else substitutes | external, open |
| 5 | **Measure `U` somewhere** | converts T-f from "unmeasured" to "measured but small" | no block exists |
| — | ~~Make the construction harder~~ | **closed** — F-1 and U1 both ran; it does not raise the ceiling | §3 T8, §3A |
| — | ~~Use a positivity gate as the Design rule~~ | **closed** — A5 holds on U-Air, so such a gate would switch Design *on* there, into the 6.55 %-worse branch | §7 open defects |

## I.7 Action list in priority order

| # | action | owner | why now |
|:--|:---|:---|:---|
| 1 | Fix N1–N2 and N4 in the manuscript: rerun/relabel the U-Air `FedAvg` and `Local-Hájek` rows on equal delivery; state the `Δ_group` claim | `ccf-paper-writer` | a contradicted comparison invalidates everything downstream |
| 2 | Add the ceiling section with F-1 and H/U1 | `ccf-paper-writer` | it is the paper's own pre-registered outcome |
| 3 | Add the endpoint-keyed Design rule and the support-cost mechanism | `ccf-paper-writer` | closes the "no rule for Design" gap the φ removal opened |
| 4 | Rebuild the U-Air `FedAvg-Window` row from **one** frozen batch and state the U-Air metric scale `sigma` (N3, N7) | `ccf-paper-writer` + `ccf-integrity-auditor` | root cause now located; both are provenance defects with known fixes |
| 5 | Enumerate the six scenarios and report `complete_counteracting` | `ccf-paper-writer` | read-only, already computed |
| 6 | Pursue an exogenous target map | external | the only route to P-a |
| 7 | Ship the recomputed per-block scores and finish the bibliography verification | `ccf-submission-checker`, `ccf-integrity-auditor` | packaging |
```

---

# Part II — Evidence, ledger, and boundaries

Section numbers 0–11 below are unchanged from the 2026-09-23 record so that other documents'
citations (`§3 T8`, `§2 L6`, `§4 S2`, `D-1`, `§7 items 18–21`, …) still resolve. The two new
sections are §2A and §3A.

## 0. Decision register

### D-1 — φ is withdrawn from the Design-switch role — DECIDED AND IMPLEMENTED

**Decided 2026-09-21. Implemented in the manuscript 2026-09-25 as Option 1 (§7 items 18–21).**
`φ` no longer appears anywhere in `main.tex`, `appendix.tex`, or `supplemental.tex`; the Design
factor is an explicit configuration and both settings are reported on both blocks.

`φ` currently decides, per block, whether the opportunity/design ratio is applied
(Algorithm 1: `Design_t ← ON` iff `φ = 0`). That role is withdrawn because φ is not a
deployment-target statistic. It measures **the overlap between the training pair set and the
test-split pair set**:

| block | what determines φ | verified? |
|:---|:---|:---|
| SensorScope | test-split pair set contains all 440 training pairs → φ = 0 | **verified numerically** |
| U-Air | 72 of 288 training pairs have no test unit → φ = 35.4% | **verified numerically** |
| T-Drive | supplement states the lookup is **test-split stratum frequency** | stated by the paper |
| City Scanner ×2 | φ = 0 **by construction** ("follows from positive regional μ, not from checking target-positive pairs") | stated by the paper |
| NSW-Traffic four-region | "four-region freeze"; provenance not established | **unverified** |

At least four of six blocks therefore set the switch by evaluation-split coverage or by
construction. Consequences: the Design/NoDesign assignment of every block loses its stated
justification; the U-Air forced-Design diagnostic now reads as "Design removes 35.4% of
training units because those cells are absent from the test split"; and any target-mass claim
that depends on φ must be suspended until an exogenous target map exists. The *observation*
that arriving data need not match a deployment target does not depend on φ.

### D-2 — the "public deployment target" must be re-sourced

`π^tar_{k,s}` is a **test-split** client–stratum mass, and the vector that weights `RMSE_μ` is
the **supported-test-unit count share**. Until an exogenous public target map exists,
target-mass claims should be restricted to blocks that have one, or restated as "target on the
reachable evaluation support".

### D-3 — the dataset search requirement was over-specified; the object needed is a target map

**Refined 2026-09-21.** A search for a single dataset that both records `O`/`U` **and** carries
data on `π^tar = 0` cells returned nothing, and it cannot succeed as posed:

1. **`π^tar` is a construct, not a dataset field.** No released dataset ships a deployment
   target, so "a dataset with `π^tar = 0` cells" is unsatisfiable by construction.
2. **Genuine zero target mass combined with arriving data is the normal case** under selection
   bias, not a rare commodity. It appears automatically once an exogenous target map is chosen.
3. **Measured `O` and `U` are platform operation logs.** Released research datasets publish
   sensor values, not task/upload logs, so the conjunction is structurally rare.

Recommended path, in order of cost: (i) keep the disclosed protocol-constructed `O`/`U`;
(ii) obtain an **exogenous public target map** for the two blocks that already have real `R`
(T-Drive, City Scanner) from a geographic or statistical source (population, POI/land use,
official monitoring objective) defined on the same cells; (iii) restrict target-mass claims on
SensorScope and U-Air to nothing, leaving them as protocol development tables. This needs no
new sensing data. It is a recommendation, not a decision.

### D-4 — layer provenance and construction parameters must be stated — DECIDED AND IMPLEMENTED

**Decided and implemented 2026-09-21 as P0.** The paper now states which layer is measured in
which block, that the four protocol blocks are semi-synthetic, and the construction constants;
and the abstract, the main-table caption and the limitations are scoped accordingly. See §2
L1–L5 and §7 items 12–15.

### D-5 — which revision route to pursue, if any

**Open.** The method-revision evaluation (2026-09-23) concluded that none of the three proposed
revisions can yield more than 1% on `RMSE_μ` on the existing protocol blocks, and reduced the
strongest of them to a **necessity test for P2** rather than a gain route. The one experiment
worth running is V1 on City Scanner Pilot 2 (see §3 T6 and §8 item 1).

### D-6 — the *difficulty* of the constructed regime must be declared, not only its provenance

**Decided 2026-09-24.** D-4 fixed *where the layers come from*. It does not fix *how much the
regime leaves to correct*. Because `p_obs` is two-valued and block-level (§2 L6), and because the
endpoint is nearly indifferent to the propensity pair even when both members are exact (§3 T3), the
protocol blocks pin the correction problem close to its easiest identifiable point. Publishing the
constants without
publishing the dispersion invites the reader to read the `+0.5%` tolerance as a property of the
method rather than of the generator — exactly the inference §3 T8 records as unsupported.

Consequence for the manuscript: wherever the construction constants appear, the **within-stratum
dispersion of the true propensities** must appear beside them, together with one sentence that the
reported predictive gains are therefore not bounds on realistic regimes. The dispersion is a
zero-cost number: for `O` it is 0, for `U` it is one value per client-window (§3 T8, F-3).

Status: **implemented for the dispersion, open for the mechanism.** F-3 was written into the paper
on 2026-09-24 (§7 items 16–17): the main text now states that both construction parameters are
constant within a stratum rather than varying per unit, and the A5/A6 audit section now reports the
two-valued observation rate and the per-client-window usable-update rate beside the constants.
F-1 and F-2, the re-runs that would test whether the regime *causes* the flat gains, are not run.

---

## 1. Root defect 1 — the deployment target is evaluation-derived

**R1 — φ is a train/test pair-coverage statistic.** On U-Air the target map has 288 keys: 216
carry `π^tar > 0` and equal the 216 test pairs exactly, while 72 carry an explicit 0 and equal
the 72 train-only pairs exactly. Of 5688 training risk units, 3672 (64.56%) are positive and
2016 (35.44%) are "present but zero"; **missing keys: 0**. On SensorScope the map has 440 keys,
all positive, equal to both pair sets, so φ = 0 by coverage coincidence.

**R2 — `RMSE_μ` degenerates to the unweighted pooled RMSE on SensorScope and U-Air.** The
per-unit weight is `μ^eval_{h(i)}/n_{h(i)}` and `μ^eval_g = n_g/N` exactly (all `μ_g × N` are
integers summing to N), so `w_i = 1/N`. Verified: the weight vector is uniform to 1e-12 on both
blocks, and `sqrt(Σ_g (n_g/N) RMSE_g²) = 7.9389` equals the published value to four decimals.
On the two main blocks the primary metric is not target-weighted at all.

**R3 — `Δ_group` uses the same count-share vector**, over 220 groups (SensorScope) and 144
(U-Air) rather than four.

**R4 — the manuscript claim versus the artifacts.** §VII-A.1 said the masses are "constructed
from the training split without test-label values" while the vector weighting `RMSE_μ` and
`Δ_group` is the supported-**test**-unit share. The clause was softened to "label-free masses";
the substance is unresolved and is D-2.

**Disclosure status.** The supplement does state that SensorScope and U-Air "look up test-split
client–stratum mass" and that T-Drive looks up test-split stratum frequency, and the current
§VII-A.3 states the `RMSE_μ` degeneration. What the paper never draws is the consequence: φ is
a coverage statistic, and the two main blocks' target weighting is vacuous.

---

## 2. Root defect 2 — the selection layers are constructed, and the compounding direction is designed in

Ranked second only because it is the same kind of defect as §1: the label does not match the
artifact. Its practical weight is comparable, because it supplies the *inputs* to every block.

**L1 — O and U are constructed in the four protocol blocks, and U is measured nowhere.**
Verified in `src/raven_mcs/e3/real_runner/generator_r3.py` (generator
`e3-complete-aligned-r3-v1`):

- **R**: every client receives exactly one opportunity event per window, so no client is ever
  opportunity-censored; the stratum is drawn from a **constructed** joint law
  (`build_joint_pi_opp`: equal client mass `1/|K|` times `exp(-1.25)` against time blocks
  {2,3}).
- **O**: designed Bernoulli, `p = clip(0.35 × scale, 0.05, 0.95)` with `scale = 0.55` on
  blocks {2,3}, giving 0.1925 there and 0.35 elsewhere.
- **U**: designed device-tier compute and network success (`compute_usable_r3`) with
  `align_disadvantage = True` on blocks {2,3} and staleness capped at `s_max = 5`.
- Each client-window draws at most four risk units.

| block | R | O | U |
|:---|:---|:---|:---|
| SensorScope, U-Air, NSW-Traffic | always-on, stratum from a constructed law | constructed | constructed |
| T-Drive | **real** (taxi trajectories) | constructed | constructed |
| City Scanner NYC PM2.5 | **real** (visit occupancy) | constructed | constructed |
| City Scanner Pilot 2 | **real** (visit occupancy) | **measured** (finite PM2.5) | constructed |
| INT-R (supplement) | **simulated** occupancy thinned to 0.425 | constructed | constructed |

Counts: R real in 3 blocks, O measured in 1, **U measured in 0**.

**L2 — what the paper says and does not say.** It says: Complete-aligned means "R, O, and U are
all active and non-random in the same direction" (§VII-A.2); "Original SensorScope and U-Air
traces are not claimed to contain mobile clients" (§VII-A.1, about R); "O and U stay controlled
except Pilot 2 measured O" (§VII-G); "not a jointly measured observation-and-network process"
(supplement). It does not say: that the four protocol blocks are semi-synthetic; the
construction constants; that the alignment direction is designed in; or that the scenario
family has six members (the supplement mentions "six risk-semantic scenarios" once and never
lists them, so `complete_counteracting`, in which U opposes R and O, is invisible).

**L3 — consequence: the mismatch that `Δ_group` measures is partly designed.** All three layers
are tilted against the same two time blocks, so the compounding misalignment is built rather
than observed, and `Δ_group ≈ 1.0` out of a maximum of 2 is largely a property of that
construction. Since `Δ_group` is one of the two endpoints the paper wins on, that win is doubly
qualified: self-referential (E1) and construction-driven (L3). **§4 partly answers this.**

**L4 — correction to this record's own earlier audit.** The A5/A6 audit's readings were
generator constants: `min p_obs_true = 0.1925 = 0.35 × 0.55` exactly, `min π^opp = 6.33e-4` is
the closed form of `build_joint_pi_opp`, and `q_use_true` is a Monte Carlo over a synthetic
prestate. The audit remains a valid statement about the released traces, but it carries **no**
information about any real sensing process, and my earlier review statement that "the
observation-side clause is satisfied" gave that evidence more weight than it has.

**L5 — the plan had it right, and the paper dropped the label.** The earliest design document
(`参考文件/RAVEN-MCS_V2.3_实验设计方案.docx`) declares the experiment nature as
**半合成受控实验 + 真实轨迹一致性实验**, places `p_obs` and `q_use` under `selection/` as
constructed objects, and states that short gaps are used only for the public reference and
"不作为客户端已观测". The provenance was therefore documented at plan level; the manuscript
carried over only the word "controlled". This is scope and labelling drift, not concealment,
and it is why the remedy is specification rather than a new dataset.

**L6 — the observation propensity is two-valued, and the release proves it.** In the released
audit (`artifacts/a5_a6_audit/audit_records.csv`, 28 800 rows, SensorScope + U-Air), `p_obs_true`
takes **exactly two values**, `0.1925` and `0.35`, and no others. The code explains why:
`generator_r3.py` lines 152–156 set `p_obs = clip(0.35 × scale, 0.05, 0.95)` with
`scale = 0.55 if block in {2,3} else 1.0`, where `block` is parsed from the unit's **target-group**
label. So `p_obs` is a function of the UTC block alone: it carries no client, no unit and no label
information.

The two-valuedness proves more than it first appears, because the recorded field is a **risk-set
mean**: `generator_r3.py` line 231 sets `p_mean = mean(p_obs_by_unit.values())` and line 240 stores
`p_obs_true = p_mean`, while the per-unit dict goes to a separate field,
`p_obs_true_by_unit` (line 241), which the audit does not read. Had any risk set ever mixed UTC
blocks, `p_mean` would have taken intermediate values strictly between `0.1925` and `0.35`. Over
28 800 events on two datasets it takes only the two extremes. **Every risk set is therefore
block-pure, so `p_obs` is exactly constant within every risk set and every opportunity stratum —
verified, not inferred.**

Two consequences the paper does not currently draw:

- **The Design and observation branch reduces to a two-parameter affine rescale** of the observed
  mass. `a = ζ̂^o / max{p̂^obs, p_min}` can take only two distinct values up to sampling noise in
  `p̂^obs`, so there is no high-dimensional propensity field to estimate and no propensity–label
  interaction to undo.
- **Within any opportunity stratum the propensity is constant**, because the UTC block is a
  component of the stratum label (`region::block::weekday`) as well as of the group label. The
  paper's stated assumption, "The main blocks assume within-stratum exchangeability,
  `ν^opp_{k,r}(i|s) = ν^tar_{i|s}`" (`main.tex` lines 1496–1499), is therefore **not at risk from
  the observation layer anywhere in the main tables**: the `O` layer contributes zero
  within-stratum tilt by construction. The only within-stratum discrepancy the generator can still
  create is the uniform-over-pool risk-set draw (`rng.choice(support, k = min(4, |support|))`)
  against the test-split target share. Prop. 2 and the design-ratio simplification are thus
  exercised only in the regime where their key assumption holds by fiat, not approximately.

**L7 — the usable-update propensity is a per-client-window quantity, and it is not label-dependent.**
Same file: `q_use_true` takes 1105 distinct values on `[0, 0.9815]`, at most **8 within any single
`(dataset, seed, window)`** — one per client. This is by construction: `U` is decided once per
client-window (`compute_usable_r3` is called once per client, `generator_r3.py` lines 161–172, and
all risk units in that client-window share the decision), the event row stores a single
`q_use_true` value per event (line 242), and `align_disadvantage` is again a
block-level flag. So the `U` layer does vary across clients and windows — it is not degenerate —
but it is driven by device tier, registration time and staleness, none of which depends on the
label. Against that, T3 shows that substituting true propensities for both estimated ones moves
`RMSE_μ` by **+0.008%** (SensorScope) and **−0.028%** (U-Air). That contrast is a joint oracle and
does not isolate `q`.

**L8 — the one real `O` measurement disagrees with the construction by 2.5×–4.5×, and the constant
moved without a record.** The only measured observation layer in the repository is City Scanner NYC
Pilot 2 (`o_layer = MEASURED_FINITE_PM25`, `p_obs_bernoulli = false`):

| quantity | value | source |
|:---|:---|:---|
| measured `O=1` share, joint O/U round | **0.871** (`measured_o0_fraction = 0.12908`) | `results_joint_ou/round_v1/INGEST_REPORT.json` |
| measured `O=1` share, path-A round | **0.859** (`measured_o0_fraction = 0.14071`) | `results_path_a_hajek/round_v1/INGEST_REPORT.json` |
| constructed `p_obs`, blocks {0,1} | **0.35** | `generator_r3.py` line 61 |
| constructed `p_obs`, blocks {2,3} | **0.1925** | `generator_r3.py` lines 155–156 |
| E1 balanced `O` | [0.15, 0.25] | `experiments/e1_entry.py` |
| E2 balanced `O` | 0.20, constant | `e2/generators.py` line 151 |

The denominators differ — the measured figure is the share of PM∪NO₂ union GPS cell-slots that
carry a finite PM₂.₅ value, whereas the constructed figure is a per-risk-unit Bernoulli
probability — so this is not a calibration error. It is the **absence** of a calibration: had the
constructed value ever been anchored to the only measurement the repository has, a one-directional
factor of 2.5–4.5 could not have survived unreported. The same repository also carries this
constant at three different values — `0.20` in `configs/scenario/*.yaml` and in
`semantic_alignment/complete_aligned_r2.py` line 87 / `protocol_closure/complete_aligned.py` line
102, `0.35` in the E3 runner that actually produces Table III, and `0.85` as the
`delivery_mode="high"` floor — and the `0.85` floor is the value closest to the measurement, in the
one configuration explicitly labelled "for non-degenerate correctness fixtures only"
(`generator_r3.py` lines 69–78).

**L9 — even the measured-`O` block runs on a controlled `U`, in the repository's own words.**
`scripts/ingest_joint_ou_cs_p2.py` (driven by `post_review/JOINT_MEASURED_OU_RANK/TARGET_SPEC.json`)
writes `results_joint_ou/round_v1/INGEST_REPORT.json`, which declares provenance per layer:
`r_layer = REAL_FROM_UNION_PM_NO2_GPS`, `o_layer = MEASURED_FINITE_PM25`,
`u_layer = CONTROLLED_EXPERIMENTAL compute_usable_r3 s_max=5`. The claim "`U` is measured in no
block" (§VII-A.2; §2 L1 above) is therefore not an inference from absence — it is the literal
content of that field, and the controlled substitute is the **same function** used in every
synthetic block. `sample_tau`'s docstring adds "P(age > S_max) ≈ 0.20 under this **controlled
design (not performance-tuned)**", and `q_true` has no closed form: it is estimated by
`estimate_q_true_mc(m=2000)`. A layer with no closed form and no measurement cannot have been
fitted to anything.

---

## 2A. Correctness defect — the main comparison's U-Air baseline

Placed here, before §3, because it is a correctness class defect and outranks the ceiling discussion:
a wrong comparison invalidates work built on it. Discovered on 2026-09-24 during the H gate check and
audited on 2026-09-25. Evidence: `results_table2_audit/**`, `results_h_headroom/round_v1/GATE_uair.json`,
`results_h_headroom/round_u1/GATE_uair.json`.

**N1 — the frozen U-Air `FedAvg-Window` cell came from a runner that dropped the zero-target pairs.**
The 2026-08-11 runner removed every `(client, stratum)` pair with `π^tar = 0` from the active set, and
`FedAvg-Window` was not exempt. U-Air has **72 of 288** such pairs (SensorScope 0/440, Traffic 0/344);
window 0's `client-005` is dropped in the frozen `FedAvg`, `RAVEN` and `TwoStage`, and retained in the
frozen `FedAU` and `ObsUse`, which were produced by the later runner. The gate confirms it at two
seeds: seed 30001 frozen `1.210848` versus rerun `1.171263` (`abs_diff` 0.0396), and seed 30006 frozen
`1.285611` versus rerun `1.150249` (`abs_diff` 0.1354). Both are recorded as `known_nonrepro`.

**N2 — the stated win is an artifact of the unequal baseline, and it is not a RAVEN result.**

| method | versus **frozen** FedAvg (TEST / ALL20) | versus **equal-delivery** FedAvg (TEST / ALL20) |
|:---|:---|:---|
| `RAVEN-NoDesign` | **−5.80 %** (9/10) / **−6.62 %** (19/20) | **+0.54 %** (3/10) / **+0.09 %** (7/20) |
| `FedAU-Window` | **−6.24 %** (10/10) / **−6.63 %** (20/20) | +0.10 % (5/10) / +0.08 % (10/10) |
| `ObsUse-Window` | **−6.21 %** (10/10) / **−6.70 %** (20/20) | +0.12 % (5/10) / +0.01 % (11/20) |
| `RAVEN-Design` | — | +7.49 % (0/10) / +7.54 % (0/20) |

Three unrelated methods therefore show the **same** 6.2–6.7 % gap against the frozen row. The anomaly
is the frozen `FedAvg` row, not an advantage of `RAVEN-NoDesign`. The manuscript's sentence
"RAVEN-NoDesign improves on TwoStage-Hájek and FedAvg (TEST −9.11 % and −6.17 %)" does not hold
against equal delivery.

**N3 — the printed value is correct; the row is assembled from two frozen batches that disagree.**
Resolved 2026-09-27, and the earlier wording of this item was wrong. Table III prints `1.1882` for
this cell, and the E3 run tree's ALL20 mean over the same 20 seeds is **`1.188238`** — the printed value
**is** the stored value (|diff| 0.000038, 0.003 %). The `1.1923` that this item previously set against
it is not an independent recomputation but the mean of a **different artifact**:
`RAVEN_MCS_PUBLIC_REPRO_R1/tables/TABLE_II_WORSTGROUP_PER_SEED.csv`, byte-identical to
`post_review/P0_ni_artifact/tables/TABLE_II_WORSTGROUP_PER_SEED.csv` (sha256 `cb91220557d6…`).

The real defect is that Table III's U-Air block draws its columns from **two sources**:

| Table III U-Air column | frozen source | check against the printed cell |
|:---|:---|:---|
| `RMSE_μ`, `Δ_group`, `Δ_c-s` | `artifacts/e3_formal_runs_r1/runs/uair/*` (2026-08-11 batch, 4 methods) | tree means reproduce the printed cells exactly: `1.188238`→`1.1882`, `1.121762`→`1.1218`, `1.262132`→`1.2621` |
| `WorstGroupRMSE` | the public-repro per-seed CSV (7 methods, incl. the 2026-08-17 batch) | `1.259556`→`1.2596`, `1.290654`→`1.2907`, `1.263029`→`1.2630` |

The two artifacts agree on 17 of 20 seeds and disagree on three:

| seed | repro CSV | E3 tree | relative |
|:---|:---|:---|:---|
| 30007 | 1.193597 | 1.145170 | **+4.23 %** |
| 30016 | 1.144226 | 1.167526 | **−2.00 %** |
| 30018 | 1.178757 | 1.123620 | **+4.91 %** |
| the other 17 | — | — | 0.0000 % |

Means are `1.192251` (CSV) against `1.188238` (tree), i.e. **0.34 %** over ALL20 and 0.27 % over
TEST10. Because seeds 30016 and 30018 lie inside the TEST window `30011`–`30020`, the printed row pairs
an `RMSE_μ` from one batch with a `WorstGroupRMSE` from another **on the very seeds that carry the TEST
claims**. The divergence is not specific to `FedAvg`: it hits all four methods that have tree
directories (`fedavg_window`, `local_hajek`, `raven`, `twostage_hajek`) at the same three seeds, so it
is a batch-level offset rather than a per-method error. **This is a provenance defect, not a
reproducibility one**, and the column-level fix is to source the whole row from a single batch.

**N4 — `Local-Hájek` inherits the restriction, and the coincidence is already disclosed.** Its 20-seed
U-Air values are **bit-identical** to the frozen `FedAvg-Window` — not merely equal to four decimals —
on both sources (per-seed identical in the repro CSV and in the E3 tree), and the sealed SensorScope
source likewise carries `7.93889340278565` for both rows. It therefore carries the same 72 dropped pairs
and must be corrected with the same row. This is **not** a hidden defect: the manuscript states the
coincidence and its cause (the realized within-client Hájek weights are uniform) in the paragraph
following Table III, and `appendix.tex` prints the same `1.1882` for both rows. What is new here is only
the consequence — the two-row redundancy in the U-Air block is real, not a rendering artifact.

**N5 — what survives, and it is on the other endpoint.** After equalising delivery, U-Air prediction
is a **four-way tie** (`RAVEN-NoDesign` 1.1131, equal-delivery `FedAvg` 1.1119, `FedAU` 1.1128,
`ObsUse` 1.1120 — spread 0.11 %), with `TwoStage` 1.2202 paying 9 % for its own restriction. But
`RAVEN-NoDesign` keeps `Δ_group = 1.0165` against `FedAvg` 1.0446 (−2.69 %), `FedAU` 1.0557
(−3.71 %) and `ObsUse` 1.0413 (−2.38 %). The U-Air claim must therefore be moved from prediction to
structure, which is also where §3 T9 shows the only reachable gains live.

**N6 — `raven` is the forced-Design row.** Moved here from Part I, which previously used N4 for this
finding while §2A used N4 for `Local-Hájek`; the two numbering schemes now agree. Table III's U-Air
RAVEN row is `raven` (Design on, 20-seed mean `1.191114`) whereas the deployed configuration is
`raven_wo_design` (`1.113059`). Any analysis that calls `1.1911` "the published method" compares
against the wrong run. Anchor correction already applied in §3 T9 and in both F-1 documents.

**N7 — Table III's `RMSE_μ` column mixes metric scales across datasets. NEW this round.**
`artifacts/e3_formal_runs_r1/runs/*/*/metric_scale_policy.json` records a per-dataset metric-scale
policy, and the three blocks do not share one:

| dataset | runs | `zscore_applied` | `conversion` | `status` | `sigma` |
|:---|--:|:---|:---|:---|:---|
| `sensorscope` | 220 | **false** | `IDENTITY_RAW_PHYSICAL` | `RAW_PHYSICAL` | `null` |
| `uair` | 220 | **true** | `OFFLINE_LINEAR_CONVERSION` | `OFFLINE_LINEAR_CONVERSION` | **17.36325121670317** |
| `traffic` | 120 | **true** | `OFFLINE_LINEAR_CONVERSION` | `OFFLINE_LINEAR_CONVERSION` | 575.7755968885956 |

SensorScope's `RMSE_μ` is therefore in raw physical units while U-Air's is z-scored, and the two sit in
one column of one table with no note. The scale is recoverable and exact:
`1.188238 × 17.36325121670317 = 20.631670`, which is precisely the U-Air `FedAvg-Window` value in the
sealed table source `manuscript_evidence_closure_r1/01_table_sources/TABLE_II_E3_MAIN_EFFECTIVENESS_FINAL.csv`
(sha256 `1aa0706f…`). That source is therefore **not** 17× wrong — it stores the **physical** domain
while the manuscript prints the **standardized** one, and the earlier framing of this item as a sealed
-source scale error is withdrawn. Three consequences stand:

1. **Undisclosed quantity.** Grepping both `.tex` files for `sigma`, `metric.scale`, `normaliz` and
   `17.36` returns no disclosure of the scale; every `normaliz` hit concerns the estimator's Hájek
   normalization, not `RMSE_μ` units. A reader cannot tell that the U-Air prediction column is
   dimensionless while SensorScope's is not, nor compare the two columns against each other.
2. **Regeneration hazard.** Rebuilding Table III from the sealed source would shift the U-Air `RMSE_μ`
   and tail columns by 17.36× relative to what is printed, while that source's own metadata asserts
   `scientific_semantics_changed: false`. `Δ_group` and `Δ_c-s` are scale-invariant (sealed-versus-tree
   ratio 1.0000 to ten digits) and would be unaffected.
3. **Broken store contract.** All three policies declare
   `store_fields: [RMSE_mu_std, RMSE_mu_phys, MAE_mu_std, MAE_mu_phys]`, but **no** `final_metrics.json`
   in the tree carries any `*_std` or `*_phys` field — only the un-suffixed `RMSE_mu` / `MAE_mu`. The
   declared offline conversion was never materialized, and the stored field name does not record which
   domain it holds.

**Numbering caution for anyone acting on the source report.** `ccfa-review-reports/raven-mcs-experiment-report-20260924.md`
calls this table "Table II". In the current manuscript the `1.1882` cell is in **Table III**
(`tab:main_effectiveness`); the current Table II is the T-Drive hybrid table. Fixing "Table II" as
written would edit the wrong table. The appendix four-block table `tab:app_block_rmse` carries the
same U-Air rows and needs the same correction.

---

## 3. Root defect 3 — the recoverable gain is capped, and the machinery is already near-oracle

This is the finding that explains why no endpoint separates the methods: the quantity the
correction family can act on is a small fraction of the observed gap. Sources:
`artifacts/e3_formal_runs_r1/runs/*/final_metrics.json` (20 seeds per block) and
`ccfa-review-reports/raven-mcs-method-revision-evaluation.md`.

**T1 — the two central references already differ by most of the gap.**

| block | Central-All | Central-Delivered | federal methods | RAVEN vs Central-All |
|:---|:---|:---|:---|:---|
| SensorScope | 7.6004 | 7.9291 | 7.9309–7.9399 | +4.45% |
| U-Air | 1.0556 | 1.1782 | 1.1882–1.2160 | +13.3% |
| traffic | 0.9538 | 0.9754 | ≈1.0035 | — |

`Central-All` trains on all valid observations with no `U` restriction; `Central-Delivered`
trains centrally on the delivered data with no correction. **They already differ by 4.3% and
11.6%**, i.e. the distance from the federal family to `Central-All` is dominated by **which
samples were delivered**, not by how they were weighted.

**T2 — no reweighting can recover a sample that was never delivered.** This is a structural cap
on the entire correction family (Design, O, U, P2, debt) taken together, not a defect in any one
of them. It is the same fact as E4's null `U` ablation seen from the other side.

**T3 — the plug-in propensity pair is not the bottleneck, and the null cannot be attributed to
either member.** `RAVEN-SimOracle` replaces **both** estimated propensities by their true values: a
single flag, `uses_oracle_propensity`, gates the usable map (`rec.oracle_q`, `window_runner.py`
lines 426–430) and the atomic observation map (`p_obs_true_by_unit`, lines 707–727). Against the
reference `RAVEN` the contrast on `RMSE_μ` is **+0.008%** (SensorScope, sd 0.070% of the baseline
mean) and **−0.028%** (U-Air, sd 0.265%), re-derived over the same 20 paired seeds from
`artifacts/e3_formal_runs_r1/runs/*/*/final_metrics.json`. Nothing measurable follows from exact
propensities, which is a stronger statement than the earlier `q`-only reading and is the one the
evidence supports. What it does **not** support is naming the usable-update layer as the irrelevant
one: no arm in the repository separates `p` from `q`, so the null may be carried by either or by
both, and settling that needs an oracle-`p`-only and an oracle-`q`-only arm
(`raven-mcs-f1-experiment-design.md` §4.1). The rest of T3's role in this record is unchanged.
F-1 measured the split directly rather than leaving it open: on `RMSE_μ` under the published
construction the observation member alone is worth **−0.005%** (SensorScope) and **+0.017%** (U-Air),
so the usable member accounts for roughly **+0.013%** and **−0.045%**. Neither carries the null.

**T4 — prediction is insensitive to the aggregation weights.** On U-Air seed 30001 over 80
windows, P2 moves `α` away from `β̂` by a mean L1 distance of **0.337** (max 1.256), while
`RMSE_μ` barely moves. A large change in the aggregation composition produces a negligible
change in prediction.

**T5 — the scenario family agrees.** Across all six risk-semantic scenarios (§4 S2), `RMSE_μ`
spans 1.0042–1.0050 (**+0.08%**) while `RMSE_ρ` spans 1.0085–1.0304 (**+2.2%**). The whole
designed selection shift is worth 0.08% of target risk.

**T6 — P2's own off-switch already beats it, inside the paper's own baseline list.**
`TwoStageHajekAggregator.compute_server_weights` returns `_normalize(payload.beta_hat)`
(`src/raven_mcs/aggregation/methods.py` lines 314–320). It is therefore **exactly RAVEN's
reference with P2 switched off**, sharing the identical `β̂`, so the only difference from RAVEN
is the P2 projection plus debt. On **City Scanner Pilot 2**, the one block with measured `O`:

| method | `RMSE_μ` | `Δ_group` |
|:---|:---|:---|
| TwoStage-Hájek (= `β̂`, no P2) | **0.7097 ± 0.0204** | 0.0607 ± 0.0206 |
| RAVEN-Design | 0.7135 ± 0.0206 | **0.0465 ± 0.0119** |

The P2-off member is **0.54% better on prediction** (sd 0.45%; RAVEN wins 2 of 10 seeds). In the
other direction, Table IV's Inst row **is** `λ_g = 0` with P2 retained (Gen2): on U-Air it makes
`RMSE_μ` significantly worse by `+0.131%` and `Tail_RMSE` by `+0.136%`; on SensorScope it is not
significant. **So both available "P2 off" and "P2 weakened" configurations have already been
run, and neither supports a predictive value for P2.**

**T7 — the ceiling and what would raise it.** The honest expected gain from any reweighting-based
revision on these blocks is under 1%, below the paper's own 0.5% practical threshold. A larger
gain would require one of: (i) model misspecification in the direction of the shift, since with a
correctly specified model equal weighting is asymptotically optimal; (ii) a target law whose
total-variation distance from the arrival law is large **and** an evaluation weighted by that law
rather than by unit counts; or (iii) a downstream decision that depends on group-level error. On
the existing blocks, method-to-method gaps above 1% occur only where `R` is real (T-Drive: 1.6%;
Pilot 2: about 1.2%).

**T8 — the construction regime is a candidate *cause* of the flat gains in T1–T7, and that claim is
testable.** T1–T7 measure the ceiling; §2 L6–L9 describe the generator. The link between them is a
hypothesis, recorded here with its mechanism and its falsification test rather than as a finding.

The mechanism splits into three claims that can fail independently:

- **H-A (identifiability is built in).** With `p_obs` two-valued, block-level and constant within
  stratum (L6), the observation-side correction has two parameters to estimate and no
  propensity–label interaction to remove. Under a correctly specified constant propensity, inverse
  probability weighting is unbiased and equal weighting is asymptotically optimal — this is exactly
  T7(i). A sub-1% separation between the corrected and the uncorrected families is therefore what
  theory predicts *for this generator*, independently of whether RAVEN would separate on a
  realistic one.
- **H-B (the endpoint is insensitive to the axis the method acts on).** `RMSE_μ` responds to the
  residual mass error, which is at the `10^-3` level, not to the designed tilt magnitude (0.55).
  T4 (P2 moves `α` by mean L1 0.337 with `RMSE_μ` flat) and T3 (exact propensities move `RMSE_μ` by ≤0.03%)
  are two instances. The reported gain is thus dominated by terms the construction does not manage.
- **H-C (real propensities are harder on both axes at once).** A real `O`/`U` would plausibly have
  many distinct, label-correlated, occasionally-zero propensities (device and NIC heterogeneity,
  missing-not-at-random connectivity or battery, scheduled sampling). That raises the *achievable*
  gain above 0.5% while simultaneously raising the risk that a plug-in propensity is misspecified.
  The constructed regime pins the first axis at its easiest point and does not control the second.

**Consequence for how the headline may be read.** If H-A–H-C hold, the `+0.5%` tolerance is
**neither a lower nor an upper bound** on the gain in a realistic regime: the protocol blocks are
too easy to falsify the method and too insensitive to confirm it. That is weaker, and more
defensible, than either "the method works" or "the construction inflated the gain".

**Outcome, 2026-09-24: H-A is refuted, H-B stands.** F-1 ran. Making the selection law harder on the
axis the observation correction acts on raised the value of an exact propensity by 15–21×, from
0.005%/0.017% to +0.104%/−0.251%, which confirms H-A's mechanism. The amplified figure is still
2–5× below the paper's own 0.5% practical threshold, and on U-Air it carries the wrong sign, so the
constructed regime is not what caps the gain. What remains is H-B: the endpoint is close to
indifferent to the weights, which is also what the Stage A ceiling map shows from the other side
(every propensity route ≤0.03%; the only large route on U-Air is deletion, −6.55%).

**Falsification, at near-zero data cost.** Three tests, in increasing cost, all on existing code:

1. **F-3 (one number, available now).** Report the within-stratum dispersion of the true
   propensities beside the construction constants. For `O` it is **0** by L6; for `U` it is one
   value per client-window by L7. Published next to `0.35` and `0.55`, this lets the reader see the
   difficulty directly. No re-run. **Done 2026-09-24** in `main.tex` §VII-A.2 and the `appendix.tex`
   A5/A6 audit (§7 items 16–17).
2. **F-1 (re-run the aligned arm; one experiment). — RUN 2026-09-24, H-A REFUTED.** The test as
   first written here could not work, for a structural reason established in
   `raven-mcs-f1-experiment-design.md` §0: in E3 the opportunity stratum is nested inside the target
   group (`h(i) = s93::block0`, `s(i) = s93::block0::weekend`), and E3's `tail_score` analogue *is*
   the block, so an E2-style block-indexed score would be stratum-constant and would reproduce the
   existing construction under a new name. The executed manipulation therefore moves the propensity
   inside the stratum, on the unit's `time_index` tercile, at a per-block marginal held to machine
   precision (`|Δ| ≤ 5.6e-17`). The decisive endpoint is the within-trace contrast
   `RMSE_μ(plug-in) − RMSE_μ(exact p)`, which removes the model-capacity confound that the
   originally stated RAVEN-vs-baseline criterion carries.

   Result, 160 runs over 20 paired seeds, harness reproducing the `raven` cell to 0.0000%:
   `Δ_oracle` is **+0.104%** (SensorScope, 4.7 σ) and **−0.251%** (U-Air, 2.1 σ) on the harder trace,
   against −0.005% and +0.017% on the published one. Both are inside the pre-registered 0.5% bound,
   and U-Air carries the wrong sign, so **H-A is refuted**: the constructed regime is not what caps
   the gain. The mechanism is nevertheless confirmed in direction, since making the selection law
   harder raised the value of an exact propensity by 15–21×. Full readout in
   `raven-mcs-f1-experiment-design.md` §5.4; artifacts `artifacts/e3_f1_theta1_r1` (harder trace)
   and `artifacts/e3_f1_score_dependent_r1` (published trace).

   **Anchor caveat (added 2026-09-24, see T9).** Both arms ran the `raven` policy. That is the
   paper's table method on SensorScope, but on U-Air `raven` is the *forced-Design* diagnostic row
   (1.1911) while Table III's U-Air method is `RAVEN-NoDesign` (1.1131). The U-Air column of F-1
   therefore describes the forced-Design configuration, not the deployed one. The E1 verdict is
   unaffected, because the contrast is within a single trace and a single policy with only the
   propensity map varying, but the U-Air figure must not be read as a statement about the paper's
   U-Air method. Re-running the U-Air arm against a design-removed base needs a
   `raven_wo_design_oracle_p` policy and is not done.
3. **F-2 (the same, for `U`).** Add a unit-level component to `q` plus an occasional true zero, and
   compare it against a new **oracle-`q`-only** arm: T3's existing contrast is a joint oracle and
   cannot serve as the baseline. If exact `q` still does not matter, the `U` branch has no
   predictive role under either regime and T6's conclusion strengthens. The flag split this needs
   is the one F-1 already requires (`raven-mcs-f1-experiment-design.md` §4.1).

With F-1 executed, the only proposed experiment left in this record that could **raise** the observed
gain is F-2, and §8 item 8 records why it is now low value.

**T9 — the ceiling map, measured (Stage A, executed 2026-09-24; U-Air anchor corrected 2026-09-24).**
Before F-1 was implemented, every improvement route the existing artifacts can price was read off
them: the `raven` cell (`artifacts/e3_formal_runs_r1/runs`) against the E4 one-factor ablations
(`artifacts/e4_core_mechanism_ablation_r1/runs`), paired on the 20 formal seeds. `delta%` is
(ablated − reference)/reference; σ is |mean| over the standard error of the paired difference.

**Anchor correction.** The first version of this table used `raven` as the reference on *both*
datasets. That is wrong for U-Air. `method_policy.py` defines `raven` = `_RAVEN_CORE` +
`gate_mode="always_on"`, so its design ratio is applied unconditionally; a repository-wide search
finds **no φ in the E3 runner path at all**, and the published `config_snapshot.json` for the two
datasets differs only in `n_groups_frozen` (220 vs 144) and the target artifact. Table III is
explicit: on U-Air it reports `RAVEN-NoDesign` = **1.1131** as the table method and labels
`raven`'s 1.1911 as `RAVEN-Design (forced)`, a diagnostic row (`main.tex` lines 1754–1757,
1821–1822). 1.1131 is exactly `runs/uair/raven_wo_design`. So on U-Air the reference for anything
called "the paper's method" is the design-removed run, and the column below is a **forced-Design
factorial**, not a price list against the deployed configuration.

| module changed | SensorScope `RMSE_μ` | U-Air `RMSE_μ` (forced-Design factorial) | SensorScope `Δ_group` | U-Air `Δ_group` | σ (`RMSE_μ`, SS / UA) |
|:---|---:|---:|---:|---:|:---|
| remove design (ζ̂ + Gate) | +0.005% | −6.553% | +1.237% | −6.943% | 0.3 / 10.0 |
| remove observation IPW | +0.012% | −0.010% | +0.096% | +0.123% | 2.5 / 1.0 |
| remove usable IPW | +0.012% | +0.024% | +0.026% | +0.014% | 2.5 / 1.1 |
| remove Inst (P2 group term) | **−0.090%** | **+2.086%** | +2.110% | +2.494% | 1.6 / 6.4 |
| remove debt | +0.000% | +0.001% | +0.014% | +0.004% | 0.1 / 0.7 |
| exact `p` and `q` (joint oracle) | −0.008% | +0.028% | +0.200% | −0.017% | 0.5 / 0.5 |

**Two claims from the first version are withdrawn.**

1. *"On U-Air the largest available move is deletion: dropping the design branch buys 6.55%."* This
   is not headroom. The paper **already deploys that branch on U-Air**, and Table III already
   reports both rows side by side with the reversal explained (`main.tex` lines 1757–1760, 1933).
   It is a branch assignment the φ rule makes, not an unexploited improvement. The row stays in the
   table because it is the correct price of *forcing* Design on U-Air, which is what the `raven`
   cell is.
2. *The U-Air reference bounds.* Against the actual table method (1.1131) rather than the forced row,
   `Central-Delivered` (1.1782) is **5.85% worse**, not 1.10% better, and `Central-All` (1.0556) is
   **5.17% better** and unreachable by reweighting. On U-Air the deployed method therefore already
   beats uncorrected central training and every federal baseline in the tree (1.1882–1.2160).

**What survives.** The SensorScope column is anchored correctly: the table method there is
`RAVEN-Design` = the `raven` cell = 7.9380, and every module is worth at most 0.09%, the only
non-trivial one negative. The propensity family is ≤0.03% on both datasets, which on U-Air is now a
statement about the design-removed base. Note that the E4 tree carries **no** design-removed module
factorial, so the four other U-Air rows cannot be re-anchored from existing artifacts; they must be
read as a forced-Design factorial or re-run. `remove Inst` matches `twostage_hajek` to four decimals
on U-Air (both 1.2160, in the forced factorial), which is where the "the whole RAVEN-versus-`β̂`
gap is the P2 group term" reading came from, and that reading inherits the same anchor caveat.

Overlap: the Design-removal and Inst rows restate Table IV's existing rows. What is new is placing
all five modules and three endpoints in one σ-annotated frame.

---

## 3A. The headroom experiments — H (round_v1) and its U-Air extension U1

Placed here because it is the decisive evidence for §3: two pre-registered experiments that separate
"the estimator is lazy" from "the space does not exist". Pre-registration:
`ccfa-review-reports/raven-mcs-h-headroom-preregistration.md` (revisions 1 and 2 frozen before the
runs they govern). Design of the extension: `ccfa-review-reports/raven-mcs-uair-headroom-design.md`.
Artifacts: `results_h_headroom/round_v1/` (180 runs) and `round_u1/` (270 new runs, 45 new traces).

**H1 — the question and the rule.** `H = (RMSE_μ(FedAvg) − RMSE_μ(oracle)) / RMSE_μ(FedAvg)` on
paired arms and the same EventTrace. Six conditions move one knob at a time plus one combination:
opportunity tilt `θ ∈ {1.25, 2.5, 4.0}`, tail observation scale `∈ {0.55, 0.25, 0.10}`, a
diurnal-blind backbone, and a block-uniform target law. The arms are `fedavg_window`,
`raven_simoracle` (true `p`, true `q`, Design on) and a NoDesign oracle added by revision 1. The rule
was frozen before any stress run: **GO** iff some `c ∈ {C1…C5}` has `H ≥ 0.5 %` **and** CI lower
bound `> 0`; otherwise **STOP**, which the pre-registration states formally withdraws the claim that
the correction family can improve prediction on these protocols.

**H2 — round_v1, 5 seeds, 180 runs: STOP, with one conclusive half.** `H_DECISION.json` records
`decision = STOP`, `go_cells = []`. SensorScope is conclusive: all six point estimates lie in
[−0.03 %, +0.08 %] with a paired-difference MDE of **0.17–0.36 pp**. U-Air is not: its MDE is
**1.38–1.91 pp**, which cannot exclude a 1 % effect, and U-Air is the only block with an effect whose
CI excludes zero.

**H3 — U1, U-Air extended to 20 seeds: the rule could fire and did not.** 270 new runs, 45 new
traces, seeds 30006–30020, the five original seeds reused bit-identically (`|diff| = 0.000e+00` on
all three metrics). Revision 2 froze the U-Air oracle arm to the NoDesign arm, which is inert
(`H ≡ H_nodesign` in every cell). The gate was re-run at the new seed 30006 and `raven_simoracle`
reproduced the frozen value at `abs_diff = 0.00e+00`.

| condition | `H_nodesign` at 20 seeds [95 % CI] | at 5 seeds | shift | MDE | GO threshold | GO |
|:---|---:|---:|---:|---:|---:|:---|
| C0 frozen | **−0.2166 %** [−0.7154, +0.2822] | +0.22 % | −0.44 pp | 0.70 pp | 0.50 % | no |
| C1 strong tilt | **−0.0044 %** [−0.5378, +0.5291] | **+0.77 %** | **−0.78 pp** | 0.75 pp | 0.53 % | no |
| C2 extreme tilt | **+0.0371 %** [−0.5281, +0.6023] | −0.07 % | +0.11 pp | 0.80 pp | 0.57 % | no |
| C3 low capacity | **−0.2107 %** [−0.7094, +0.2881] | +0.24 % | −0.45 pp | 0.70 pp | 0.50 % | no |
| C4 block-uniform | **−0.2161 %** [−0.7155, +0.2833] | +0.22 % | −0.44 pp | 0.70 pp | 0.50 % | no |
| C5 combined | **+0.0283 %** [−0.5360, +0.5926] | −0.09 % | +0.12 pp | 0.80 pp | 0.56 % | no |

Every point estimate satisfies `|H| ≤ 0.2166 %`, an order of magnitude below the bar, and all six sit
below revision 2's 0.30 % band floor, so the pre-registered escalation to 45 seeds is **not run**.
**C1 is the headline: the cell the source report flagged as closest to GO collapses from +0.77 % to
−0.0044 %.** The apparent near-breach was small-sample noise. SensorScope stays at 5 seeds because
its MDE is already 0.17–0.36 pp.

**H4 — the one stable effect is a support loss, not a weighting gain.** Design carries the target-mass
ratio `ζ̂ = π^tar/π^opp`, which drives the weight of any `(client, stratum)` with `π^tar = 0` to zero;
on U-Air that discards 72 of 288 pairs. Measured on the *oracle* arms, so it is not estimator failure:

| condition | U-Air support cost [95 % CI] | SensorScope |
|:---|---:|---:|
| C0 | **+6.968 %** [+5.462, +8.474] | −0.020 % |
| C1 | **+6.989 %** [+5.834, +8.143] | +0.022 % |
| C2 | **+6.317 %** [+4.769, +7.865] | +0.011 % |
| C3 | **+6.980 %** [+5.473, +8.488] | −0.018 % |
| C4 | **+6.991 %** [+5.482, +8.500] | −0.023 % |
| C5 | **+6.308 %** [+4.751, +7.865] | +0.011 % |

All six U-Air lower bounds exceed **+4.75 %**; SensorScope is ≈0. The cost is invariant to the tilt
strength, the backbone and the target law (C0 ≈ C3 ≈ C4 ≈ +6.98 %; C2 ≈ C5 ≈ +6.31 %), i.e. it is
driven by the dropped support alone. This supplies the mechanism §7's open-defect list said was
missing, and it is the fact behind the endpoint-keyed Design rule in Part I, Tier 5 rank 2.

**H5 — what this establishes.** The ceiling in §3 is **not** an artifact of an easy testbed. Two
independent manipulations reach the same verdict: F-1 (§3 T8) hardened the observation propensity
*inside* the stratum, at a marginal held to 5.6×10⁻¹⁷, and got `Δ_oracle` = +0.104 %/−0.251 %; H/U1
stressed the opportunity tilt, the observation level, the backbone capacity and the target law under
a pre-registered bar and got no GO anywhere. H-A (the construction is the cause) is refuted; H-B (the
endpoints are nearly blind to the weights) is what remains.

**H6 — the caveat, and what is still open.** The realized U-Air sd (1.07–1.21 pp) landed at the top of
the projected range, so the realized MDE is **0.70–0.80 pp**, slightly worse than the projected
0.55–0.76 pp. The correct statement is: 80 % power excludes true effects of ≈0.75 pp or more, and C2
and C5 have 95 % upper bounds at +0.60 %, so those two cells do not yet exclude a true effect of about
0.5 % at 95 %. The source report's sentence "±0.03 % is the spatial ceiling" should therefore be
scoped to SensorScope or restated as "at 20 seeds every point estimate has `|H| ≤ 0.22 %` and the
pre-registered GO rule did not fire". Not run: revision 2's U2 (45 seeds), and no `U` measurement.

---

## 4. The scenario family is already complete, and it partly answers §2

**S1 — Verdict: the six scenarios are fully tabulatable from existing results, with no re-run.**
`artifacts/e2_traffic_formal_runs_r1/` holds 600 result cells = **6 scenarios × 5 methods × 20
seeds**, `status = PASS` for all 600, with no duplicates.

| column needed | file | field |
|:---|:---|:---|
| per (scenario, method, seed) RMSE_μ / RMSE_ρ / gap | `formal_results.csv` | `RMSE_mu`, `RMSE_rho`, `Gap_mis` |
| pre-aggregated mean/std/median/IQR/CI95 | `formal_statistics.csv` | 4 metrics × 30 cells |
| per-group RMSE → WorstGroupRMSE | `formal_group_metrics.csv` | `group`, `RMSE` (6×5×20×4) |
| per-scenario paired tests (Raven vs 4 baselines × 3 metrics) | `paired_comparisons.csv` | Wilcoxon + CI + wins/losses + p |
| solver and denominator diagnostics | `formal_runtime_metrics.csv` | `P2_solver_failure_count`, `denominator_zero_count` |

`Gap_mis = RMSE_μ − RMSE_ρ` is pre-computed per row, so Δ_μ, Δ_ρ and the generalised
difference-of-differences `D(S) = Δ_μ(S) − Δ_ρ(S)` (paired by seed, reference = `balanced`) are
available for every scenario.

**S2 — the computed family table** (means over 5 methods × 20 seeds; `D` over 100 paired values):

| scenario | RMSE_μ | RMSE_ρ | Gap_mis | **D(S)** | seeds with D < 0 |
|:---|:---|:---|:---|:---|:---|
| balanced | 1.0042 | 1.0085 | −0.0042 | — | — |
| opportunity_only | 1.0043 | 1.0142 | −0.0099 | −0.00572 | 60/100 |
| observation_only | 1.0044 | 1.0196 | −0.0152 | −0.01096 | 81/100 |
| usable_only | 1.0044 | 1.0140 | −0.0095 | −0.00531 | 65/100 |
| **complete_aligned** | 1.0050 | 1.0304 | −0.0254 | **−0.02115** | 87/100 |
| complete_counteracting | 1.0043 | 1.0210 | −0.0167 | −0.01249 | 74/100 |

The reproduced `complete_aligned` value **−0.02115 matches the manuscript exactly**, which
validates the read path against the published number.

**S3 — the three layers add up, which supplies the control that §2 L2/L3 said was missing.**
Single-layer ΔGap is −0.0057 (opportunity), −0.0110 (observation) and −0.0053 (usable), summing
to −0.0220, against the measured aligned ΔGap of −0.0212, i.e. **96% additivity**. The
counteracting scenario is predicted by `opp + obs − usable = −0.0114` against a measured
−0.0125. So the compounding misalignment is not a black box: it is the sum of three separately
controllable layers, and `usable_only` contributes the least, consistent with T2 and E4.

**S4 — the core claim is robust across the family, but the reported magnitude is the maximum.**
`D < 0` in all five non-reference scenarios, so the arrival-versus-target distinction is
directionally robust beyond the single aligned arm, which is a genuine strengthening of the
Prop. 1 premise. However `|D|` spans −0.0053 to −0.0212, a factor of four, and **the paper
reports the largest value**. Power also varies sharply: `opportunity_only` is negative in only
60/100 seeds, which is barely above chance, while `complete_aligned` reaches 87/100.

**S5 — the headline tolerance endpoint carries no scenario information.** WorstGroupRMSE across
the six scenarios spans 1.1740–1.1767 (range 0.0027) while the per-scenario seed standard
deviation is 0.010–0.017, so the scenario effect is **four to six times below the noise**.

**S6 — two prerequisites before any scenario table is published.**
First, `paired_comparisons.csv` carries `multiple_comparison_policy = none_familywise…`, i.e.
**no family correction**; the paper's existing Holm discipline must be applied. Second,
**`Δ_group` and `Δ_c-s` are absent from the E2 tree**, which holds only RMSE_μ, RMSE_ρ,
`Gap_mis` and per-group RMSE.

**S7 — relation to E5.** E5 shows `D ≈ −Δ_ρ` with method-invariance; S4 adds
scenario-dependence of magnitude and the maximum-selection problem. Both critiques stand.

---

## 5. Earlier problems of equal weight, independent of §1–§4

IDs are stable labels, not a rank. E1, E2 and E6 bear most on the verdict.

**E1 — the two endpoints that carry the wins are the functional the method minimizes.**
`Δ_group(R) = ‖ω̄_R − μ‖₁` is the time average of the quantity whose instantaneous squared form
enters P2 with the debt term on the same μ; `Δ_c-s` measures distance to the same `π^tar` the
reconstruction factor reproduces. The one non-self-referential endpoint, `RMSE_μ`, shows no
separation on any block (SensorScope spans 7.9293–7.9389 across five methods; U-Air
1.1120–1.2160, RAVEN-NoDesign third of six). S5 adds that the whole scenario family moves
`RMSE_μ` by only 0.08%.

**E2 — the comparator set contains no external method, and two of its members are RAVEN
constructions.** `TwoStage-Hájek` is `_normalize(β̂)` (T6), i.e. RAVEN's reference with the
calibration removed. `ObsUse-Window` is the authors' own ablated variant: its aggregator docstring
says "no design ratio, Hajek local loss, (P2), or debt", and with observation rates equal to one
it coincides with `FedAU-Window` to 1e-12. These two are the comparators for the headline `+0.5%`
worst-group tolerance (`+0.44%`, `+0.48%`). `TimeAlign-Agg` is "in the spirit of" a 2026 TMC paper
that uses **the same three datasets** (SensorScope, U-Air, NSW-Traffic) and is explicitly not an
official reproduction. `FedAU-Window` adapts a method whose original evidence is CIFAR/SVHN/CINIC
image classification.

**E3 — the sharp theory does not cover the evaluated system.** Prop. 3 needs A6, and the
supplement's own audit reports A6 failing on both datasets (the `q_min` floor active on
5.22%/5.18% of observed windows; `1/q^use > d_max` on 24.22%/23.75%). Prop. 2 covers the ideal
pooled estimator under A1–A3 only.

**E4 — the deployed-configuration ablation shows no practically meaningful positive effect.**
Excluding the U-Air Design row, which ablates a configuration the paper does not deploy, the
remaining rows give: Obs `+0.123%*` on `Δ_group` and not significant elsewhere; Use
`+0.014 / −0.014 / +0.024 / +0.025`, all non-significant; Inst `−0.089 / −0.143` on the
structural endpoints with `+0.131%* / +0.136%*` on prediction; Debt `+0.004%* / +0.002%*`.
Nothing clears the paper's own 0.5% minimum-practical-effect bar. On SensorScope, Design
`+1.237%* / +0.597%*` is the only component above that bar and it moves prediction by `+0.005%`;
Obs is significantly **harmful** on `Δ_c-s` (`−0.070%*`).

**E5 — `D_aligned` collapses to its own second term.** `corr(D, Δ_ρ) = −0.9988`,
`sd(D)/sd(Δ_ρ) = 0.975`, `sign(D) = −sign(Δ_ρ)` in 98/100 seeds, and the statistic cannot vary
with the method (all five give `−0.02115 … −0.02137`). The stated null is not the theory's null:
the target law is fixed across the two arms while the arrival law moves by scenario design.

**E6 — the P2 component's predictive value is already contradicted by the paper's own numbers.**
See T6: the P2-off member (`TwoStage-Hájek`) is 0.54% better than RAVEN on the measured-`O`
block, and the P2-weakened member (`λ_g = 0`) is significantly worse on U-Air. The clean
attribution (identical `β̂`, difference is exactly P2 plus debt) makes this hard to explain away
by any other component.

---

## 6. Degeneration and component removal: what the derivation covers

**G1 — the assumption class already admits partial degeneration.** A4 requires `λ_β > 0` and
permits `λ_g, λ_v, λ_s ≥ 0`. Thm. 1's strong convexity comes only from the reference-penalty
term ("`J_r` is `λ_β`-strongly convex"), so zeroing an aggregate weight leaves existence and
uniqueness intact. Prop. 3's P2 step uses the reference non-expansion, whose inequality chain
contains only `λ_β`. Code agrees: `aggregation/feasibility.py` requires
`λ_group ≥ max_server_learning_rate` when instantaneous calibration is on and only `λ_group ≥ 0`
when it is off. So the Inst / Debt / variance / staleness degenerations are **inside** the
analysed class.

**G2 — O-off and U-off are outside the theory.** They change the estimator, not the program.
Prop. 2 presumes the ideal ratios at all three layers, so nothing states what `β̂` estimates once
a factor is deleted; and Prop. 3 is a small-perturbation result of order `ε`, whereas deleting
an inverse-propensity factor is an `O(1)` change.

**G3 — no rule for when to degenerate.** The only switch is φ, now withdrawn (D-1). No result
selects a degenerate variant.

**G4 — what the removal data actually shows.**

| removal | endpoints (relative %) | significant? | φ branch? | covered by theory? |
|:---|:---|:---|:---|:---|
| U-Air Design | Δ_group −6.943, RMSE −6.553, Tail −6.875 improve; Δ_c-s +4.990 worsens | yes | **yes** (U-Air deploys NoDesign), so not a new degeneration | yes, as a rule branch |
| U-Air Inst | Δ_group −0.089, Δ_c-s −0.143 improve; RMSE +0.131, Tail +0.136 worsen | gains **not** significant, costs significant | no | G1 only; no selection result |
| U-Air Use | Δ_c-s −0.014, rest positive | none | no | no |
| **SensorScope Obs** | Δ_c-s **−0.070** improves, Δ_group +0.096 | **significant** | no | **no** |
| SensorScope Inst | Δ_group −0.260 improves (ns), Δ_c-s +0.310 worsens | mixed | no | G1 only |
| both Debt | both endpoints +0.014 / +0.004 worsen | significant but tiny | no | G1 |

The only **significant, non-φ** degeneration benefit is SensorScope Obs removal improving
`Δ_c-s` by 0.070%, and Obs has opposite signs across blocks.

**G5 — ablation-definition drift, which must be settled before any degeneration claim.**
`e4/wo_inst_final/evidence.py` records: Gen0 — "original E4 wo_inst **skipped P2**"; Gen1 — "used
`lambda_beta=1e-8` != E3 full-RAVEN `lambda_beta=1.0`"; Gen2, the one behind Table IV — keeps P2
with `λ_group = 0` and `λ_β` matched to full RAVEN. "Removing Inst" therefore names two different
experiments across generations.

**G6 — warning for any future automatic degeneration rule.** Keying such a rule on the reported
endpoints would deepen the circularity of E1. Any such mechanism needs pre-registration, a
held-out selection criterion, and family correction.

**G7 — the proposed revision routes, as evaluated.** The method-revision evaluation (2026-09-23)
examined three proposals: (i) shrink P2's group term toward the arrival law by `μ_λ = (1−λ)ρ + λμ`;
(ii) replace the φ switch by a continuous Design factor; (iii) estimate composite balancing
weights directly instead of multiplying three inverse factors. Conclusions:

- **Route (i)** remains the strongest but must be rewritten: only the `λ_g`-shrinkage version keeps
  the estimand; the `μ_λ` version changes it and needs a new assumption (frozen, split-independent
  mixing law) and a bias–variance proposition that does not yet exist. Its `λ = 0` endpoint is
  **not** `ObsUse-Window`, and `λ_g ∈ (0,1)` with instant calibration on violates the shipped
  feasibility constraint. **It is already partly run**: `λ_g = 0` is Table IV's Inst row.
- **Route (ii) does not work as stated.** `0^γ = 0` for `γ > 0`, and Yamada's
  `r_α = p/(αp + (1−α)p')` gives `r_α = 0` when `p = 0`. Neither literature supplies a floor at
  `π^tar = 0`; Yamada bounds the ratio **above** by `1/α`. A floor requires replacing the target
  law by a mixture `π_κ = (1−κ)π^tar + κ π^opp`, which changes the estimand, and it necessarily
  keys on test-split coverage (R1), so it does not resolve D-1.
- **Route (iii)** overlaps P2's own group term, degenerates to post-stratification
  (`w_s = π^tar_s/ρ̂_s`) when the moments are strata indicators, would drive `Δ_group` toward zero
  by construction (E6/E1), and aims at weight-estimation error that T3 has already ruled out as
  the bottleneck.
- **Internal-consistency constraint discovered:** routes (i) and (ii) are the same "target
  mixing" operation applied at different layers. If both are used, `κ` and `λ` must be bound to a
  single mixing law, otherwise `β̂` and P2 chase different estimands.

---

## 7. Changelog — paper modifications since the previous review round

Boundary: after the 2026-09-12 review. All in `TO_OVERLEAF_paper_tmc_r1_clean/`.

| # | change | where | basis | status |
|:--|:---|:---|:---|:---|
| 1 | A5 split into **A5 (positivity and shared support)** and **A6 (inactive stabilization and bounded plug-in error)**; Prop. 3 restated under A1 and A4–A6; scope sentence that `ε_clip` is retained; U-Air reversal attributed to A6 | `main.tex` §VI-A/E, §VII-G; `appendix.tex` | the old A5 mixed qualitative positivity with quantitative bound-inactivity, and only the latter is empirically false | done |
| 2 | New supplement section **"Support-Hypothesis Audit for A5 and A6"** with the per-dataset table and a limits paragraph | `appendix.tex` | reports A5 holding and A6 failing on the released traces | done |
| 3 | §IV-E and §VI-F **splice grammar** repaired; §VI-F first two clauses back-reference §IV-E; "can be false-safe at rate α" corrected to a bound | `main.tex` | ungrammatical where appendix pointers had replaced citations | done |
| 4 | **Assumption 1** trimmed: the "not assumed globally" sentence deleted as entailed | `main.tex` §VI-F | added no condition beyond the `g`-conditioning | done |
| 5 | `\COMMENT{scope; does not prove Assumption A}` → `Assumption~1` | `appendix.tex` algorithm | placeholder name in a shipped algorithm | done |
| 6 | **§VII-A.1 group map corrected**: `h(i)` = spatial unit × four UTC time blocks, 220 / 144 groups, label-free masses | `main.tex` | manuscript said four groups; the runs used the spatial×time map | done |
| 7 | **§VII-A.3 metric definitions added**: `RMSE_μ` display with weight law; three distinct vectors `μ`, `μ^eval`, `μ^blk`; the SensorScope/U-Air degeneration; `WorstGroupRMSE` as the max of four UTC-block scores; `Tail_RMSE` as the frozen late-day blocks 2–3; `RMSE_ρ` as the same functional with arrival weights | `main.tex` §VII-A.3 | none of these were defined | done |
| 8 | Table I column header `\|G\|` → `WG blocks` | `main.tex` | the four UTC blocks are the aggregation level of `WorstGroupRMSE`, not the dataset's group count | done |
| 9 | §VII-D under-served check uses `μ^blk_b` instead of `μ_g` | `main.tex` | separates the four-block marginal from the group marginal | done |
| 10 | **`Δ_group` definition made readable**, including the ℓ1 reading and `0 ≤ Δ_group ≤ 2` | `main.tex` §IV-D | it was an unnumbered inline formula whose prose name did not match the symbol | done |
| 11 | `reference.bib` restored (54 entries, ICLR/INFOCOM attribution intact) | `reference.bib` | truncated to 0 bytes; see §9 | done |
| 12 | **§VII-A.2 new paragraph (P0)**: which layer is measured in which block; the four protocol blocks are semi-synthetic; construction constants; and the scoping sentence that the Table III structural-alignment results are conditional on the construction | `main.tex` §VII-A.2 | L1–L3; the paper disclosed "controlled" but never the construction | done |
| 13 | Abstract: "a Complete-aligned protocol" → "a **protocol-constructed** Complete-aligned selection" | `main.tex` abstract | D-4 | done |
| 14 | Table III caption: "This is a protocol development table on station traces, not a real-mobility ranking." → "…station traces **whose `O` and `U` layers are protocol-constructed**…" | `main.tex` | D-4 | done |
| 15 | §VII-G: "`O` and `U` **stay controlled** except Pilot 2 measured `O`." → "`O` and `U` **are protocol-constructed** except Pilot 2 measured `O`." | `main.tex` | D-4 | done |
| 16 | §VII-A.2 (the P0 paragraph): added that **both construction parameters are constant within a stratum** rather than varying per unit, naming the two mechanisms (observation rate set by the UTC block that the stratum already fixes; usable-update rate drawn once per client-window), and the scoping sentence that the reported predictive gains describe this construction rather than the range attainable when selection varies at the unit level | `main.tex` §VII-A.2 | D-6, L6–L7, T8 F-3 | done |
| 17 | A5/A6 audit section: new paragraph reporting the **dispersion** of the two selection margins on the released traces — the observation rate takes only `0.1925` and `0.35` over all `28800` records and is therefore stratum-constant, and the usable-update rate is drawn once per client-window and shared by that window's at most four risk units | `appendix.tex` §"Support-Hypothesis Audit" | D-6, L6–L7, T8 F-3 | done |
| 18 | **D-1 implemented (Option 1). Method restated without a data-derived switch.** Equation (32) is retained in its slot but now defines the **Design factor** `ζ̂^o = π^tar / max{π̂^opp, π_min}` when `D_t = on` and `= 1` when `D_t = off`, with `D_t ∈ {on, off}` a configuration supplied to Algorithm 1. Algorithm 1's φ line and its `IF φ = 0` branch are replaced by `IF D_t = on`; the algorithm now produces only `θ_{t+1}` and `Q_{t+1}`. §V-E and the §V-C preamble state that the factor is configured before the window opens, that the two settings differ nowhere else, that both are reported, and that a data-derived selector would have to be justified on the evaluation it changes. The zero-target statistic survives only as a descriptive number in the supplemental material | `main.tex` §V-C, §V-E, Algorithm 1, eq. (32) | D-1, Option 1 | done |
| 19 | **Table III completed into a within-dataset Design factorial.** One row added: SensorScope `RAVEN-NoDesign` `RMSE_μ` 7.9384 ± 0.0468, `WorstGroupRMSE` 8.6711 ± 0.0481, `Δ_group` 1.0265 ± 0.0278, `Δ_c-s` 1.2719 ± 0.0308. `WorstGroupRMSE` is not stored in `final_metrics.json`; it was recomputed from the saved checkpoints with the `run_int_r_v2.py` path, and the recomputation **reproduces the published `RAVEN-Design` four-block row to 4×10⁻⁵** (7.4903 / 7.5864 / 8.6707 / 8.2075, WG 8.6707) before being applied to the new row. The U-Air `RAVEN-Design (forced)` label becomes `RAVEN-Design`. Caption rewritten to report the trade: Design is worth +1.237% `Δ_group` and +0.597% `Δ_c-s` on SensorScope at unchanged prediction, and costs 6.553% `RMSE_μ` / 6.943% `Δ_group` / 6.875% tail on U-Air while improving `Δ_c-s` by 4.990% (17.1σ) | `main.tex` Table III | D-1, §3 T9 anchor correction | done |
| 20 | The same factorial added to the appendix four-block table: SensorScope `RAVEN-NoDesign` = 7.4907 / 7.5868 / 8.6711 / 8.2079, WG 8.6711 ± 0.0481; U-Air `RAVEN-Design (forced)` relabelled `RAVEN-Design`; caption and the surrounding assignment sentences rewritten as reported settings rather than a rule | `appendix.tex` `tab:app_block_rmse` | D-1 | done |
| 21 | **Abstract, contributions, §I, §VII, limitations and the whole appendix de-φ'd.** The abstract states the two settings trade off across endpoints with the measured numbers; contributions and §I report the factor as an explicit configuration; the appendix section `Frozen φ Assignments…` becomes `Target-Coverage Statistic and City Scanner Hybrid Rankings`, its table caption and column header demote the statistic to descriptive provenance and record the Design setting *used* rather than *selected*; every "RAVEN-Design if and only if φ = 0", "Design is withheld (φ = 47.4%)" and "forced RAVEN-Design" is replaced by the corresponding configuration statement | `main.tex`, `appendix.tex` | D-1, Option 1 | done |

Side effects of the whole change set: main text **15 → 16 pages** (page 15 saturated; page 16
holds roughly nine reference lines, and the P0 paragraph did not add a page). Equation numbering
unchanged at 41, so the 67 frozen literals in `appendix.tex` remain valid;
`tools/freeze_appendix_refs.py --check` reports 0 to freeze and 0 unresolvable. Supplement clean
(0 overfull, 0 undefined). Main carries only the pre-existing 5.6 pt log-only overfull. Em
dashes: 2, both pre-existing.

Items 16–17 left every one of those invariants where it was: main **16 pages**, supplement
**15 pages**, equation labels **41**, `tools/freeze_appendix_refs.py --check` reports 0 to freeze
and 0 unresolvable (56 appendix-internal references kept), 0 undefined references or citations, em
dashes still 2, and the only overfull box is the same pre-existing 5.63672 pt one. The 144 added
words return `PASS: 144 words; em dashes 0/3; 0 issue(s)` from
`CCFA-Skills/ccf-paper-writer/scripts/check_prose_quality.py`; both added passages were verified
present in the built PDFs by text extraction, not only in source.

Items 18–21 (Option 1) left the build invariants where they were: main **16 pages**, supplement
**15 pages**, equation labels **41**, 0 LaTeX errors, 0 undefined references or citations,
`tools/freeze_appendix_refs.py --check` reports **0 to freeze and 0 unresolvable** (57
appendix-internal references kept), 0 overfull boxes above 2 pt, em dashes in `main.tex` still 2 and
in `appendix.tex` 0. Equation (32) kept its number, which is why the frozen literals in
`appendix.tex` did not move; the freeze tool's only conversion was `\eqref{eq:design_factor} → 32`.
A source-level ripgrep over all three `.tex` files returns **no `\phi`**, and a text extraction of
both built PDFs returns **no** `forced RAVEN-Design`, `RAVEN-Design (forced)`, `frozen heuristic`,
or `Design fraction`.

### Record corrections — 2026-09-27 (this file only; no manuscript change)

Four corrections from the N-forensics round. **Nothing in `TO_OVERLEAF_paper_tmc_r1_clean/` was
edited**, so every build invariant in items 18–21 still holds.

| # | correction | evidence |
|:--|:---|:---|
| 22 | **§2A N3 rewritten, and its status changed from `open` to root-cause located.** The item previously claimed a 0.35 % printed-versus-recomputed gap. The printed `1.1882` **is** the E3 tree's ALL20 mean `1.188238` (0.003 %). The real defect is mixed sourcing: `RMSE_μ`/`Δ_group`/`Δ_c-s` from the E3 run tree, `WorstGroupRMSE` from `RAVEN_MCS_PUBLIC_REPRO_R1/tables/TABLE_II_WORSTGROUP_PER_SEED.csv`, the two disagreeing at seeds 30007 / 30016 / 30018 by 2–5 %, with 30016 and 30018 inside the TEST window | `artifacts/e3_formal_runs_r1/runs/uair/*/final_metrics.json`; the repro CSV; per-seed diff in §2A N3 |
| 23 | **§2A N4 corrected from a hidden defect to a disclosed redundancy.** `Local-Hájek` is **bit-identical** to frozen `FedAvg` on both datasets (not merely equal to four decimals), and the manuscript already states the coincidence and its cause in the paragraph following Table III | per-seed identity in both frozen sources; `appendix.tex` prints `1.1882` for both rows |
| 24 | **New §2A N7: the `RMSE_μ` column mixes metric scales across datasets.** SensorScope is `IDENTITY_RAW_PHYSICAL` / `zscore_applied: false` / no sigma; U-Air is `OFFLINE_LINEAR_CONVERSION` / `zscore_applied: true` / `sigma = 17.36325121670317`. Exact recovery: `1.188238 × 17.36325121670317 = 20.631670`, the U-Air `FedAvg-Window` value in the sealed source, so the sealed source stores the **physical** domain and is not itself wrong. Also: all three policies declare `store_fields: [RMSE_mu_std, RMSE_mu_phys, MAE_mu_std, MAE_mu_phys]` but **no** `final_metrics.json` carries any `*_std`/`*_phys` field | `artifacts/e3_formal_runs_r1/runs/*/*/metric_scale_policy.json` (220/220 sensorscope, 220/220 uair, 120/120 traffic); key census over every `final_metrics.json`; `manuscript_evidence_closure_r1/01_table_sources/TABLE_II_E3_MAIN_EFFECTIVENESS_FINAL.csv` |
| 25 | **§2A N2 given its metric attribution; N1–N7 renumbered to one scheme.** The `−6.17 %` / `−9.11 %` sentence is `WorstGroupRMSE`, **paired**, **TEST**, measured against the contaminated batch; on that metric against equal-delivery comparators it is `+0.48 %` (`FedAU`) / `+0.44 %` (`ObsUse`). Separately, Part I had used N4 for the forced-Design finding while §2A used N4 for `Local-Hájek`; the forced-Design item is now **N6** in both places | exhaustive match over {metric} × {reference} × {source} × {window} × {aggregation} reproduces −9.11 %/−6.17 % to 0.002 pp as WG-paired-TEST10 on the repro source |

Also carried forward, unchanged in substance but no longer "unlocated": the `RAVEN-Design` row is the
**forced-Design** run, and its equal-delivery gap to a clean FedAvg (`1.1119`) is **+7.12 %**, so the
printed same-batch comparison `1.2630` versus `1.2596` **understates** the U-Air Design cost.

### Open manuscript defects NOT changed

| item | where | note |
|:---|:---|:---|
| **the U-Air `FedAvg-Window` and `Local-Hájek` rows rest on a weakened baseline** | Table III; `tab:app_block_rmse`; §VII-C.1 | **§2A N1, N2, N4**: the stated `−6.17 %` / `−9.11 %` are `WorstGroupRMSE` paired TEST relatives; against equal-delivery comparators the same metric gives `+0.48 %` / `+0.44 %`, and on `RMSE_μ` `+0.54 %` (TEST) / `+0.09 %` (ALL20). The U-Air claim must move to `Δ_group` (1.0165 versus 1.0446). Highest priority: a contradicted comparison invalidates what depends on it |
| **the U-Air `FedAvg-Window` row is sourced from two frozen batches that disagree at 3 of 20 seeds** | Table III, U-Air `FedAvg-Window` | **§2A N3**, root cause **located** 2026-09-27: `RMSE_μ`/`Δ_group`/`Δ_c-s` from the E3 run tree, `WorstGroupRMSE` from the public-repro CSV; seeds 30016 and 30018 are inside the TEST window. The earlier "0.35 % printed-versus-recomputed" framing is withdrawn — the printed `1.1882` *is* the stored ALL20 mean |
| **Table III's `RMSE_μ` column mixes metric scales across datasets and discloses neither** | Table III; `metric_scale_policy.json`; the sealed Table II source | **§2A N7** (new): SensorScope raw physical, U-Air z-scored by `sigma = 17.36325121670317`; the sealed source stores the opposite domain; the declared `*_std`/`*_phys` store fields are materialized nowhere |
| **the recoverable-gain ceiling is nowhere stated** | §VII | **T1–T10, §3A**: two pre-registered experiments. Stating it is +0.5 on Evidence and is the paper's own recorded outcome |
| **the endpoint-keyed Design rule is not written** | §V-E, Table III | Design helps `Δ_c-s` in 3 of 4 blocks and hurts `Δ_group` in 3 of 4; mechanism is the **+6.31…+6.99 %** U-Air support cost with all CI lower bounds above +4.75 % (§3A H4). Closes the gap the φ removal opened, at zero compute |
| ~~φ still drives the Design switch~~ **closed by items 18–21** | Algorithm 1; §V-E; eq. (32); the appendix φ table | D-1 implemented as Option 1: the switch is now an explicit configuration and both settings are reported. Residual: the *choice* of setting per block is still a deployment decision with no derived rule — see the new row below |
| no derived rule replaces φ for choosing a Design setting | §V-E, Table III, §VII-G | Option 1 deliberately reports the factorial instead of selecting. Option 2 (an A5/positivity gate) is **refuted**: A5 holds on U-Air, so such a gate would switch Design *on* there, i.e. into the 6.55%-worse branch. The only causally aligned successor is an exogenous target map (D-2/D-3), which is not yet obtained |
| the `μ` identity and target provenance | §VII-A.1, §VII-A.3, supplement | D-2 open; §VII-A.2's wording deliberately stays neutral |
| six scenarios never enumerated; `complete_counteracting` never reported | §VII-A.2; supplement runtime table | **feasible today, see §4**; not yet written up |
| the recoverable-gain ceiling is nowhere stated | §VII | **T1–T7**; stating it would reframe the contribution honestly |
| **the F-1 result is in no manuscript** | §VII | H-A was tested and refuted: an exact observation propensity is worth 0.10% / −0.25% even under a construction built to be hard, and every propensity route is ≤0.03%. The paper neither states that its construction was probed this way nor that the probe came back empty. This is the strongest available support for the §8 item 6 reframing, and it is not in the paper |
| the *difficulty* of the constructed regime is nowhere stated | §VII-A.2 (the P0 paragraph) | **closed by items 16–17**: the constants now appear with their dispersion, so `+0.5%` no longer reads as a property of the method; what stays open is the causal question of T8, not the disclosure |
| "forced" never defined | §VII-A.2, Table II/III/IV captions, §VII-G and six more places | means overriding the φ branch; two surface forms coexist |
| `g` never defined | Assumption 1; Thm. 2 | the conditioning object of the coverage guarantee |
| Availability names `TABLE_II_MAIN_EFFECTIVENESS.csv` as "canonical Table II" | Data and Code Availability | the main comparison is Table **III** |
| remaining spliced appendix pointers | §I evaluation paragraph, §VII-A.1 City Scanner paragraphs, Table I caption, §VII-C.2, §VII-G | ungrammatical |
| table captions say "controlled" while the body now says "protocol-constructed" | Table I/II captions | bridged by one sentence in §VII-A.2 |
| `tab:app_e2_daligned` presents one measurement as five method rows | supplement | see E5 |
| Table IV's U-Air Design row duplicates Table III's two RAVEN rows | main | one experiment presented twice |
| 24 of 54 bibliography entries unverified | `reference.bib` | one misattribution already found and fixed |
| author masking inconsistent; TMC page policy unverified | title page / format | desk-level hygiene |

---

## 8. Next actions

Reordered 2026-09-25 to match Part I. The order is by class and weight: correctness first, then the
ceiling, then the rule that the φ removal left open, then external evidence, then packaging.
Superseded items are kept at the end for the record.

1. **Repair the U-Air baseline (§2A N1, N2, N4).** Re-run `fedavg_window` and `local_hajek` on U-Air
   with the current runner (equal delivery), relabel both rows, and move the U-Air claim from prediction
   to `Δ_group` (1.0165 versus 1.0446). Numbers are already in `results_table2_audit/`. Any further
   analysis on the old row is void. Note the metric: the `−6.17 %` / `−9.11 %` sentence is
   `WorstGroupRMSE`, not `RMSE_μ`.
2. **Rebuild the U-Air `FedAvg-Window` row from a single frozen batch and disclose the metric scale
   (§2A N3, N7).** Both root causes are now located, so this is an edit rather than an investigation:
   take `RMSE_μ`, `Δ_group`, `Δ_c-s` **and** `WorstGroupRMSE` from one artifact, and state that the
   U-Air `RMSE_μ` column is z-scored by `sigma = 17.36325121670317` while SensorScope's is raw. Also
   decide whether Table III should print the physical U-Air values, which is what the sealed source and
   `metric_scale_policy.json`'s `primary_domain: "physical"` both imply.
3. **Add the ceiling to the paper** using T1–T10 and §3A. This is the paper's own pre-registered
   outcome (H's STOP, U1's confirmation), not an outside criticism, and it is worth about +0.5 on
   Evidence. Scope the sentence: SensorScope conclusive at MDE 0.17–0.36 pp; U-Air "every point
   estimate `|H| ≤ 0.22 %`, GO rule not fired", with the 0.70–0.80 pp MDE caveat (§3A H6).
4. **Write the endpoint-keyed Design rule** (§3A H4): Design helps `Δ_c-s` in 3 of 4 blocks and hurts
   `Δ_group` in 3 of 4, the mechanism is the +6.31…+6.99 % U-Air support cost, and no uniform setting
   works — Pilot 2 favours Design on two endpoints while City Scanner contradicts the support
   statistic. This closes review M1 and M4 at zero compute.
5. **Write up the scenario family** (§4). Read-only; the numbers are computed. Prerequisites: fix the
   Holm family for the per-scenario tests, and note that `Δ_group` cannot be included from the E2
   tree (S6).
6. **Obtain an exogenous public target map** for the blocks that already have real `R` (T-Drive,
   City Scanner) — see D-2/D-3. The only route that addresses §1, and nothing else substitutes.
7. **Do not switch datasets.** PEMS-BAY is a fixed-loop-detector traffic speed series (325 sensors,
   5 min, roughly six months), so it supplies neither a mobility-derived `R` nor any `U`; at best it
   could make `O` measured, and it duplicates the fixed-sensor type already used in NSW-Traffic.
8. **Decide the fate of the Design branch** once D-2 resolves, and **settle G5** before any
   degeneration claim.
9. **Reframe the contribution.** With H-A refuted and the ceiling measured twice, the honest
   positioning is: RAVEN is a target-composition *diagnostic and accounting* framework, the
   predictive payoff is not demonstrated on these protocols, and the reachable range is capped (T1–T2,
   §3A). Items 3 and 4 supply the evidence for that framing; the paper should be written to it rather
   than to a predictive claim.
10. **Ship the recomputed per-block scores** (the new `WorstGroupRMSE` cell in §7 item 19) and finish
    the bibliography verification.
11. **Score-change conditions**: one endpoint whose target is external to the method with a corrected
    gain → +1 overall; a measured-`U` block → +0.5 to +1; clarity and consistency fixes alone →
    about +0.5. §4 S3 raises the middle item's value, since the counteracting control already exists.

**Superseded or completed, kept for the record.**

- **V1 on City Scanner Pilot 2** (previously item 1) — no longer first. Its purpose was to test
  whether P2 is beneficial; §3 T6 already shows `TwoStage-Hájek = _normalize(β̂)` scores better, and
  §3A removes the headroom it would have measured. Run it only if the predictive claim is revived.
- **Record the difficulty of the constructed regime, and test it** (D-6, T8) — **both stages done.**
  F-3 put the dispersion in the paper (§7 items 16–17); F-1 ran 160 cells with the harness reproducing
  the published `raven` to 0.0000 % and returned `Δ_oracle` = +0.104 % (SensorScope, 4.7 σ) and
  −0.251 % (U-Air, 2.1 σ), inside the bound, so **H-A is refuted**. F-2 was not run and is now
  low-value. The headroom question was then re-asked under five stress conditions by H and U1 (§3A)
  with the same verdict.

---

## 9. Incident log — repository file corruption

At **2026-09-21 07:24:52**, 56 tracked files share one modification timestamp; **16 of them were
truncated**. Damage and recovery:

| file | was | restored to |
|:---|:---|:---|
| `TO_OVERLEAF_paper_tmc_r1_clean/reference.bib` | 0 B | 19520 B (54 entries) |
| `src/raven_mcs/data/registry.py` | 0 B | 1226 B |
| `src/raven_mcs/data/cityscanner.py` | 2 B | 14330 B |
| `scripts/run_c1_tdrive_spatial.py` | 0 B | 47177 B |
| `RAVEN_MCS_PUBLIC_REPRO_R1/scripts/build_public_repro_bundle.py` | 0 B | 14814 B |
| `RAVEN_MCS_PUBLIC_REPRO_R1/configs/design_rule.json` | 0 B | 122 B |
| `configs/dataset/cityscanner_nyc_pm25.yaml` | 2 B | 950 B |
| `post_review/C1_kill_cityscanner/C1_KILL_INSTRUCTION.md` | 2 B | 5208 B |
| `post_review/C1_kill_cityscanner/TARGET_SPEC.json` | 2 B | 3718 B |
| `post_review/C1_kill_tdrive_spatial/C1_KILL_INSTRUCTION.md` | 2 B | 3366 B |
| `post_review/C1_kill_tdrive_spatial/DRIVER_HAJEK_SLOWDOWN_PATCH_INSTRUCTION.md` | 2 B | 6976 B |
| `post_review/C1_kill_tdrive_spatial/TARGET_SPEC.json` | 2 B | 1260 B |
| `post_review/C1_tdrive_rank/REMOTE_AGENT_PROMPT.md` | 2 B | 2705 B |
| `post_review/C1_tdrive_rank/REMOTE_SYNC.md` | 2 B | 1470 B |
| `results_c1_cityscanner/round_v1/INGEST_REPORT.json` | 2 B | 884 B |
| `results_tdrive_rank/TD_R_ZIP_INGEST_AUDIT.json` | 2 B | 1618 B |
| `results_tdrive_rank/round_v1/TD_R_HARDWARE_STOP.json` | 2 B | 1500 B |

Consequences before recovery: the whole `raven_mcs.data` import chain failed, taking down
`raven_mcs.correction.pi_target`, `raven_mcs.e3.*`, and `scripts/compute_scd_phi.py`. That is
why the φ readings in §1 were recomputed after recovery rather than read from that script.

Recovery method: `git checkout --` for 15 files; `reference.bib` from the reproduction package
`_tmp_pack/7.26-vs-current-verification/current_paper/reference.bib`, the only backup whose key
set matches the compiled `main.bbl` exactly (54/54, no missing, no extra, INFOCOM attribution
present). `git HEAD` was not usable for it: 51 keys and the uncorrected venue attribution.
Verified afterwards: five key modules import, `bibtex` regenerates 54 `\bibitem`, `main.log`
reports 0 undefined citations and 0 undefined references, both PDFs rebuild.

Cause: unknown. The damaged set clusters on `C1_tdrive_rank`, `C1_kill_*` and the reproduction
bundle, which looks like an interrupted bulk write or checkout. An earlier edit in the same
session failed with `ReplaceFileW EIO (Win32 1175)` on `main.tex`. Content written to those 15
files after their last commit is unrecoverable.

Prevention: run `_tmp_ref/damage_scan_full.py` before any commit or package build.

---

## 10. Reproduce

```text
_tmp_ref/phi_zero_decompose.py     φ zero-set partition (missing key vs explicit zero) and
                                   test/train pair coverage; §1 R1
_tmp_ref/a4_mu_check.py            μ_g × N integrality → μ is the unit-count share; R2
_tmp_ref/a4_final_verify.py        weight-vector uniformity and the four-block identity; R2/R3
_tmp_ref/confirm_metric_lineage.py Table III == 20-seed means of the E3 run metrics
_tmp_ref/analyse_daligned.py       D vs Δ_ρ / Δ_μ statistics; E5
_tmp_ref/rank_interchange.py       method rankings under both risks and the power check
_tmp_ref/scenario_inventory.py     six-scenario completeness and per-scenario aggregates; §4 S1
_tmp_ref/scenario_table.py         family table, generalised D(S), additivity and
                                   WorstGroupRMSE sensitivity; §4 S2–S5
_tmp_ref/verify_p0_rendered.py     confirms each P0 edit in the built PDF (§7 items 12–15)
_tmp_ref/bib_verify.py             bibliography entry count and undefined-citation count
_tmp_ref/damage_scan_full.py       repository truncation scan; §9
_tmp_ref/check_stratum_constant_layers.py  distinct values of p_obs_true / q_use_true and their
                                   per-client-window structure, from the released audit; L6/L7
_tmp_ref/f1_stage_a_ceilings.py    the ceiling map: full RAVEN vs published references, per endpoint
                                   and dataset, with paired sds; T9
_tmp_ref/f1_ablation_ceilings.py   full RAVEN vs the E4 one-factor ablations, five modules x three
                                   endpoints, with sigma; T9
_tmp_ref/f1_compare.py             F-1 pairing and MDE helper
_tmp_ref/f1_readout.py             the F-1 verdict readout: gate 1 reproduction, E1 on both arms,
                                   manipulation gate; T8 item 2
_tmp_ref/f1_generator_check.py     theta_O generator validation: theta=0 bit-identity against the
                                   published trace, marginal preservation, within-stratum dispersion
_tmp_ref/audit_nodesign_pairing.py reconciles the NoDesign supplement's paired relative means against
                                   ratio-of-means: the Delta_group paired column carries an unstable
                                   sign on City Scanner (6/10 wins, 31 pp dispersion); §3A H4
_tmp_ref/u1_readout.py             the U1 verdict readout: decision file, 20-seed H and support cost,
                                   5-seed comparison, reuse bit-identity, arm-freeze check
_tmp_ref/u1_precise.py             precise U1 sd / MDE / GO-threshold table; §3A H3
```

Findings without a script: T1–T3 (central references and the oracle comparison) come from
`artifacts/e3_formal_runs_r1/runs/*/final_metrics.json`, and T6 from
`src/raven_mcs/aggregation/methods.py` lines 314–320 plus `appendix.tex` lines 2446–2449. §2A N1–N5
come from `results_table2_audit/{uair_table2_summary_with_current_fedavg.csv,uair_paired_vs_fedavg.csv,AUDIT_META.json}`
and `results_h_headroom/round_{v1,u1}/GATE_uair.json`, produced by `scripts/audit_table2_uair_fedavg.py`.
§3A comes from `scripts/run_h_headroom.py` (extended 2026-09-25 with `--round`, `--seeds`,
`--reuse-from`, `--freeze-arm-dataset`, `--full-seed-dataset`, `--decision-name`; defaults unchanged
and regression-verified against `round_v1` to 0.000e+00) plus
`results_h_headroom/{round_v1,round_u1,round_v1_verify}/`. Route
evaluations in §6 G7 and the literature verification are in
`ccfa-review-reports/raven-mcs-method-revision-evaluation.md`.

Other key inputs: `data/processed/{sensorscope,uair}/atomic_units.parquet`,
`artifacts/e3_semantic_alignment_and_runner_integration_closure_r1/E3_*_TARGET_SEMANTICS_R2.json`,
`artifacts/e2_traffic_formal_runs_r1/formal_*.csv` and `paired_comparisons.csv`,
`artifacts/e2_traffic_formal_results_analysis_r1/COMPLETE_ALIGNED_DOD.csv`,
`configs/e2_numeric/scenario_direction_registry.yaml`, and for L6–L9
`artifacts/a5_a6_audit/audit_records.csv` (28 800 rows),
`results_joint_ou/round_v1/INGEST_REPORT.json`,
`results_path_a_hajek/round_v1/INGEST_REPORT.json`, `configs/scenario/*.yaml`, and for T9 and T8
item 2 the two F-1 arms `artifacts/e3_f1_score_dependent_r1/` (published trace, θ = 0) and
`artifacts/e3_f1_theta1_r1/` (F-1-O trace, θ = 1.0), 160 cells over 20 paired seeds, with the
driver `scripts/run_e3_f1.py` and the θ_O generator
`src/raven_mcs/e3/real_runner/generator_r3_score.py`.

---

## 11. What this record does not do

It does not implement D-2 or D-3, and it does not edit the manuscript: D-1 was implemented as Option 1
on explicit instruction (§7 items 18–21), and §2A's repairs are specified but not applied. D-6 and its
F-1 test are complete, as is the H/U1 headroom work. It does not run revision 2's U2 (45 seeds), V1, or
T8's remaining F-2; does not rescore the paper beyond the review cited in the header; does not produce
the LaTeX versions of the scenario or gain-ceiling tables; ~~does not locate the root cause of §2A N3~~
(**superseded 2026-09-27**: N3's root cause is located — mixed sourcing across two frozen batches —
and N7 records the undisclosed U-Air metric scale); does not settle the NSW-Traffic target-map
provenance or the 0.34 % residual between the U-Air four-block identity and the published `RMSE_μ`
(**note: this is a distinct item from N3's 0.34 % ALL20 gap between the repro CSV and the run tree; the
two share a magnitude and have not been shown to share a cause**); and does not re-verify the 24
unverified bibliography entries.

Two claims it explicitly declines to make. First, it does **not** claim that the constructed regime
caused the flat gains: T8 recorded that as a hypothesis with a stated falsification test, F-1 ran it,
H-A was refuted, and H-B is what survives. Second, it does **not** claim the ceiling is zero: §3A H6
records that U-Air's realized MDE is 0.70–0.80 pp and that two cells still admit a true effect of
about 0.5 % at 95 %.
