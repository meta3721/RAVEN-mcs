# G5 decision

**Window-level rule: `G5_SOLVER_DIVERGE`.**  
**Main conclusions: not affected. Sealed formal rerun is not authorized.**

The pre-registered \(10^{-4}\) allocation / \(10^{-3}\) composition rule is missed on a tail of windows. Typical windows and the objectives agree. Debt and the Path B / G2 contrasts are classified against the locked 0.5% MPID. 20 seeds stay algorithmic randomness.

## 9.1 P2 warnings

Frozen E3 audit (read-only): **778 warnings, 85 runs, 6438 windows**, max residual \(2.686\times10^{-8}<10^{-7}\). Feasibility certified. Exact optimality still not reconstructable from sealed E3.

New check: 779 reconstructable windows (179 warning) from G1 `raven_sc_target` and drifting `raven` seeds 30001–30005. Second solver = **raw SCS** (OSQP cannot encode the ESS ball). Agreement is CLARABEL-raw vs SCS-raw.

| | median | p90 | max |
|---|---:|---:|---:|
| \(\|\alpha^{\mathrm{C}}-\alpha^{\mathrm{S}}\|_1\) | \(2.5\times10^{-8}\) | 0.0013 | **0.0056** |
| \(\|M\Delta\alpha\|_1\) | \(2.5\times10^{-8}\) | 0.0013 | **0.0056** |
| \(\|J_{\mathrm{C}}-J_{\mathrm{S}}\|/(1+\|J_{\mathrm{C}}\|)\) | \(5\times10^{-9}\) | \(1.5\times10^{-4}\) | \(1.6\times10^{-4}\) |
| logged vs CLARABEL (repair) \(\|M\Delta\alpha\|_1\) | 0 | \(2.2\times10^{-4}\) | \(6.0\times10^{-4}\) |

475 / 779 windows meet the tight \(10^{-4}\) rule. 122 exceed the \(10^{-3}\) composition flag. Warning windows are the harder tail (median 0.0006; 9 / 179 meet \(10^{-4}\)).

That is why the pre-registered **window** rule is `G5_SOLVER_DIVERGE`. It is **not** a paper-endpoint failure:

- One window at 0.0056, averaged over ~90 active windows, moves run-level \(\Delta_{\mathrm{group}}\) by \(\sim 6\times10^{-5}\).
- Path B U-Air Design-off is **−6.7%** \(\Delta_{\mathrm{group}}\) (CI about −8.1 to −5.4). Solver tail noise cannot invent that.
- Repair displacement (max \(6\times10^{-4}\)) is smaller than the CLARABEL–SCS tail.

Do not retune \(\lambda\). Do not overwrite sealed E3/E4. A solver-config + formal rerun needs a **separate** instruction; this gate does not start it.

The 778 warnings stay: feasibility-certified, optimality not reconstructable, typical-window solver agreement at machine precision, tail allocation disagreement \(\le 0.0056\) L1 and **below MPID at run level**.

## 9.2 Practical significance (MPID = 0.5%, locked)

| Contrast | Split | Result vs MPID |
|---|---|---|
| E4 remove Debt (all four endpoints, both datasets) | formal 20 | **quantitatively small** (0.002%–0.014%; some \(p<0.05\)) |
| E4 remove Design on U-Air | formal 20 | **practically meaningful** (primaries about −6.5% to −6.9%) |
| Path B TEST U-Air gated vs full Design | test 10 | **practically meaningful** (\(\Delta_{\mathrm{group}}\) −6.73% [−8.09, −5.36]) |
| Path B TEST SensorScope Design vs No-Design \(\Delta_{\mathrm{group}}\) | test 10 | **practically meaningful** (−1.07% [−1.40, −0.74]); RMSE below MPID |
| G2 TEST gated vs FedAU / ObsUse WorstGroup | test 10 | **below MPID** (U-Air +0.48% / +0.44%; SS ~0) |

Debt remains a statistically detectable but **quantitatively small** structural term. It is not a headline component.

**Seed scope:** 20 formal seeds (and the 10+10 VAL/TEST split) are EventTrace / algorithmic randomness. They do not replace independent cities, calendar windows, or a T-Drive method ranking.

## Claim ceiling

See `CLAIM_ADDON.md`. Writing is still a separate pass. G0–G5 are now all gated.
