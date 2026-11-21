# G2 decision

**G2_ACCEPTED.**  
4-block WorstGroupRMSE is now a real external endpoint. Path B `raven_gated` is non-inferior to the two participation baselines on the pre-registered +0.5% rule. TEST was opened once. No retuning.

## What was measured

- Groups: UTC six-hour blocks 0–3 (`RepeatableTimeOfDayMapper`), not the 144/220 runtime \(h(i)\).
- Earlier B1 fine-group worst-group remains a **different, already-negative** estimand. It is not this gate.
- Methods: gated default + `raven` / `raven_wo_design` + adapted FedAU, ObsUse, TwoStage-Hajek. FedAvg and Local-Hajek are diagnostics.
- FedCure-class was **not** implemented.

Local-Hajek RMSE\(_\mu\) matches FedAvg to 0.00% on both datasets. It is demoted from the strong-baseline list.

## VAL (30001–30010) — NI passed

| Dataset | Gated WG | vs FedAU | vs ObsUse | vs TwoStage | vs FedAvg |
|---|---:|---:|---:|---:|---:|
| SensorScope | 8.657 | +0.05% | +0.15% | +0.03% | 0.00% |
| U-Air | 1.153 | **−0.47%** | **−0.29%** | **−9.49%** | **−7.98%** |

All NI checks vs FedAU/ObsUse pass. Holm p-values vs those two are not significant; the gate is the mean-relative rule, not “p>0.05”.

## TEST (30011–30020) — one look, same rule

| Dataset | Gated WG | vs FedAU | vs ObsUse | vs TwoStage | vs FedAvg |
|---|---:|---:|---:|---:|---:|
| SensorScope | 8.685 | −0.01% | +0.05% | +0.14% | −0.02% |
| U-Air | 1.187 | **+0.48%** | **+0.44%** | **−9.11%** | **−6.17%** |

U-Air vs FedAU/ObsUse stays inside +0.5% (CI crosses 0). SensorScope remains a tie.

U-Air **full Design** TEST WorstGroupRMSE = 1.275 vs gated 1.187. The Path B drop of Design also helps this external endpoint.

## Claim ceiling add-on

Allowed:

- Report 4-block worst-group + overall RMSE\(_\mu\) in the main text; per-block table in supplement.
- Say gated RAVEN is **non-inferior** to adapted FedAU/ObsUse on that endpoint, and better than FedAvg and TwoStage-Hajek on U-Air.
- Say TwoStage-Hajek (adapted target IW) does **not** explain the U-Air gated result.

Forbidden:

- “Best worst-group” or Holm-significant win over FedAU.
- Using the old 144-d B1 numbers as if they were this 4-block endpoint.
- Calling Local-Hajek a strong baseline.
- Claiming an official FedAU/ObsUse reproduction.
- Starting G3 or rewriting the paper in this step.
