# G2 protocol — external endpoint + adapted strong baselines

Date: 2026-08-24  
Default method: Path B `raven_gated` (SensorScope=`raven`, U-Air=`raven_wo_design`).

## 6.1 External endpoint (pre-registered)

Four public UTC six-hour blocks \(g\in\{0,1,2,3\}\) from `RepeatableTimeOfDayMapper` on test `absolute_time`. This is the paper’s four-group deployment partition, not the 144/220 runtime \(h(i)\).

\[
\mathrm{RMSE}_g
=
\sqrt{
\frac{\sum_{i:h_4(i)=g}w_i(\hat Y_i-Y_i)^2}
{\sum_{i:h_4(i)=g}w_i}
},
\qquad
\mathrm{WorstGroupRMSE}
=
\max_g\mathrm{RMSE}_g.
\]

\(w_i\) are the same test \(\mu\)-weights used for RMSE\(_\mu\).  
Dispersion: \(\mathrm{RMSE}_{(3)}-\mathrm{RMSE}_{(1)}\) of the four blocks (max−min).  
Fine 144/220 worst-group from the earlier B1 audit is **not** reused as this gate’s primary (it is a different estimand).  
No new training: reload sealed `checkpoints/final.pt`.

## 6.2 Adapted baselines (same backbone / EventTrace / seeds)

| Slot | Method | Handbook class | Status |
|---|---|---|---|
| 1 | `fedau_window` | participation-rate debiasing | sealed, adapted |
| 2 | `obsuse_window` | observation+usable correction | sealed, adapted |
| 3 | `twostage_hajek` | target-risk IW / covariate-shift FL | sealed, adapted |
| diagnostic | `fedavg_window` | unweighted control | sealed |
| diagnostic | `local_hajek` | demote if it tracks FedAvg | sealed, not a strong-baseline slot |
| not run | FedCure-class | semi-async participation | **not implemented** (would need new training) |

All marked adapted, not official reproductions.

## Seeds and gate

- VAL: 30001–30010  
- TEST: 30011–30020, one look after VAL  
- Scenario: Complete-aligned only

Non-inferiority (fixed before TEST): for WorstGroupRMSE, mean paired relative change of **gated vs FedAU** and **gated vs ObsUse** is \(\le +0.5\%\) (positive = gated worse). Separate families per dataset. Report paired Wilcoxon + Holm on those two comparisons; NI is the mean-relative rule, not “p>0.05”.

VAL must also confirm every method has a finite 4-block worst-group on all 10 seeds.

If VAL NI fails: still write the TEST look as a **report**, but verdict is `G2_RECORDED_NEGATIVE` (endpoint exists; gated does not match participation baselines). Do not retune Design or invent a new IW method on TEST.
