import pathlib
p = pathlib.Path("ccfa-review-reports/raven-mcs-metric-definition-diagnosis.md")
L = p.read_text(encoding="utf-8").replace("\r\n","\n").split("\n")
s = next(i for i,l in enumerate(L) if l.startswith("# Part I"))
e = next(i for i in range(s+1, len(L)) if L[i].startswith("---"))
print("replacing lines %d..%d (%d lines)" % (s+1, e, e-s))
new = r"""# Part I — Consolidated diagnosis, ordered by importance

## I.1 The verdict in one paragraph

The manuscript is an honest, well-scoped paper whose central empirical claim cannot be supported on
the blocks it reports. Four classes of finding stand. **Tier 1** was a correctness defect: the U-Air
`FedAvg-Window` baseline had been produced by a runner that dropped the 72 of 288 zero-target-mass
training pairs, so one stated win was an artifact of an unequal-information baseline. It is **closed**,
repaired under route A on 2026-09-27 and written into the manuscript. **Tier 2** is the evidence
ceiling, and it now sets the verdict on its own: no correction in the family moves the primary endpoint
by 0.5 %, two independent pre-registered experiments show this is a property of the endpoints rather
than of a testbed that was made too easy, and until 2026-09-27 the paper stated neither the bound nor
the experiment that measured it. **Tier 3** is provenance: the deployment target is evaluation-derived
and `U` is measured nowhere, so the objects are not what they are named. **Tier 4** is a ledger of what
has been repaired. **Tier 5** is the repair routes that remain, ranked by what they can still buy.

Absolute readiness on the frozen rubric is **4 / 10 weak reject**. Round 2 measured **+0.40** on the
progress scale and round 3 **+0.10**: the route-A repair bought soundness (+1) and cost reproducibility
(−1) by leaving the shipped bundle stale, and it did not create the evidence the contribution needs. A
third-round erratum dated 2026-09-27 withdrew one review concern and the mechanism attribution of
another. See §7 items 26–34 and `results_active_set_repair/round_v1/`.

## I.2 Tier 1 — correctness: closed 2026-09-27

**Closed.** The U-Air active-set defect was repaired under route A on 2026-09-27 and written into the
manuscript. The item anchors `N1`–`N7` are retained so that external citations still resolve; their
subjects and outcomes are in §2A below. Evidence lives in `results_active_set_repair/round_v1/`
(187-check verifier, manifest, worktree hashes, and the independent review of the review). There is no
open Tier-1 correctness item in this record.

One residual, carried in §7's open-defect table rather than here: the `wo_inst` ablation repair of
2026-08-12 is unfinished at `counterfactual_audit._solve_alpha`, so that arm cannot be re-run. No
manuscript value depends on it.

## I.3 Tier 2 — the evidence ceiling: the central claim cannot be supported on these blocks

| # | finding | where |
|:--|:---|:---|
| **T-a** | Every propensity route moves `RMSE_μ` by **≤0.03 %** in either direction; exact `p` and `q` together are worth +0.008 %/−0.028 % | §3 T1–T9 |
| **T-b** | The best any reweighting reaches is 0.112 % on SensorScope; on U-Air, re-anchored to the deployed method, the uncorrected central reference is **5.85 % worse** | §3 T9 |
| **T-c** | **The ceiling is not a testbed artifact.** F-1 hardened the observation propensity inside the stratum (Δ_oracle **+0.104 %/−0.251 %**); H/U1 stressed six conditions against a pre-registered 0.5 % bar, no cell reached 0.217 % and none fired GO. **Stated in the paper** as of §7 item 33 | §3 T8, §3A |
| **T-d** | **H-A is refuted**; what remains is H-B, endpoint weight-blindness | §3 T8 item 2 |
| **T-e** | The structural endpoint the paper wins on is decoupled from prediction by the paper's own ablations. The 2026-09-27 erratum sharpens this: with the corrected `wo_inst` reruns, **the Design factor is the only component that moves `Δ_group` materially**, and every other component moves it by at most 0.26 % | §3 T4, §6 |
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
| **D-1** | φ removed from all three `.tex` files; the Design factor restated as an explicit configuration; Table III completed into a within-dataset factorial; the appendix statistic demoted to descriptive provenance | §7 items 18–21 |
| **D-6 / T8** | F-1 executed; H-A refuted | §3 T8, `raven-mcs-f1-experiment-summary.md` |
| **Route A** | **The U-Air correctness defect written out of the manuscript**: the `FedAvg-Window` row and three appendix no-Design rows rebuilt on the licensed set, `tab:app_block_rmse` and `tab:app_p2_coverage` updated, the `−9.11 % / −6.17 %` sentence replaced by a within-Design-family statement plus the six-comparator qualification, the Local-Hájek coincidence reattributed, and the metric scale disclosed (closing `N7`). **Tier 1 closed** | §7 items 26–32 |
| **T-c** | **The ceiling stated**: §VII-F "Recoverable-Gain Ceiling" now carries the frozen GO rule, the negative result on both blocks, the U-Air MDE caveat, and the F-1 hardening test | §7 item 33 |

## I.6 Tier 5 — repair routes, ranked by what they can still buy

| rank | route | what it buys | status |
|:--|:---|:---|:---|
| — | ~~Restate and rebuild the U-Air comparison~~ (N1–N4, N7) | **done 2026-09-27**; Tier 1 closed | §7 items 26–32 |
| — | ~~State the ceiling using F-1 + H/U1~~ | **done 2026-09-27**; §VII-F, 220 words, no page added | §7 item 33 |
| 1 | **Report the endpoint-keyed Design rule** (Design helps `Δ_c-s` in 3 of 4 blocks, hurts `Δ_group` in 3 of 4; mechanism is the **+6.31…+6.99 %** U-Air support cost, all CI lower bounds above +4.75 %) | closes review M1 and M4 at zero compute | numbers in hand |
| 2 | **State the attribution gap**: that the U-Air structural effect is carried by the Design factor and that the ablation family does not separate Debt-Cal's route to the same endpoint | closes the repair condition of review M8 | numbers in hand |
| 3 | **Refresh the shipped bundle** `RAVEN_MCS_PUBLIC_REPRO_R1` so it matches the corrected tables | removes review M7, the only traceable score decrease | mechanical |
| 4 | **Obtain an exogenous target map** (D-2/D-3) | the only route that addresses P-a; nothing else substitutes | external, open |
| 5 | **Measure `U` somewhere** | converts T-f from "unmeasured" to "measured but small" | no block exists |
| — | ~~Make the construction harder~~ | **closed**: F-1 and U1 both ran; it does not raise the ceiling | §3 T8, §3A |
| — | ~~Use a positivity gate as the Design rule~~ | **closed**: A5 holds on U-Air, so such a gate would switch Design *on* there, into the 6.55 %-worse branch | §7 open defects |

## I.7 Action list in priority order

| # | action | owner | why now |
|:--|:---|:---|:---|
| 1 | Add the endpoint-keyed Design rule and the support-cost mechanism | `ccf-paper-writer` | closes the "no rule for Design" gap the φ removal opened, at zero compute |
| 2 | State the attribution gap beside the U-Air structural claim | `ccf-paper-writer` | one paragraph; closes review M8's repair condition |
| 3 | Refresh the reproduction bundle so it matches the corrected tables | `ccf-integrity-auditor` | review M7 is the only traceable score decrease in the last round |
| 4 | Enumerate the six scenarios and report `complete_counteracting` | `ccf-paper-writer` | read-only, already computed |
| 5 | Pursue an exogenous target map | external | the only route to P-a |
| 6 | Finish the bibliography verification (24 of 54 entries) and settle the desk items | `ccf-integrity-auditor`, `ccf-submission-checker` | packaging |
"""
L[s:e] = new.split("\n")
p.write_bytes("\n".join(L).encode("utf-8"))
raw = p.read_bytes()
print("Part I rewritten: %d lines; record now %d lines, CRLF=%d, %dB" % (len(new.split("\n")), len(L), raw.count(b"\r\n"), len(raw)))
