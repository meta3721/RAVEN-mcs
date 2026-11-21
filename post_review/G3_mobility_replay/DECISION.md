# G3 decision

**G3_ACCEPTED** at evidence level **A**.  
T-Drive supplies a real-mobility opportunity process. RQ1 mismatch is present under that process and under protocol-generated SensorScope / U-Air opportunity. RQ2 method ranking on T-Drive was **not** run. The sealed protocol directory was not written.

## Evidence boundary

| Layer | What it is | What it is not |
|---|---|---|
| R | 1,751,641 train client×unit presence rows from processed T-Drive trajectories (hash-bound) | not a new sensing task |
| O | Complete-aligned \(p_{\mathrm{obs}}=0.35\) | not recorded sensor failures |
| U | E3 `compute_usable_r3`, \(s_{\max}=5\) | not T-Drive device / network logs |

Allowed: **real-mobility opportunity replay**. Forbidden: end-to-end system, original MCS datasets “have mobile clients”, energy, evidence B/C.

Processed hashes match `TDRIVE_PROCESSED_DATA_IDENTITY.json`.

## 7.1 / 7.4 — real \(R\) vs protocol \(R\)

| | T-Drive real trace | SensorScope protocol | U-Air protocol |
|---|---:|---:|---:|
| Clients | 5,837 taxis | 8 | 8 |
| Mean client active fraction | **0.425** | **1.00** | **1.00** |
| Inter-arrival | median 0.5 h (burstiness +0.38) | every window (burstiness −1) | every window (burstiness −1) |
| Cell coverage vs train atomic | 0.547 | 1.00 | 1.00 |
| Dropout (early, not late) | 7.8% of early clients | — | — |
| 4-block \(\mathrm{TV}(\pi^{\mathrm{opp}},\mu)\) | **0.142** | **0.192** | **0.278** |

Protocol Complete-aligned \(R\) is always-on and spatially complete. Real taxi \(R\) is intermittent, bursty, and covers 54.7% of train cells. That is the TMC-relevant contrast.

Other T-Drive \(R\) facts: 178 train slots × 30 min; mean 6.13 visitors per train unit; stratum visit Gini 0.75; top decile of strata holds 57.4% of \(R\); spatial CV 2.14.

Controlled U-layer (20,000 draws, seed 30001): \(\widehat{\Pr}(U=1\mid R)\approx 0.147\), \(\widehat{\Pr}(U=1\mid O)\approx 0.423\). Deadline miss \(|O\) 0.288; staleness fail \(|O\) 0.177; \(\Pr(\tau>5)\approx 0.178\). Expected usable updates \(\approx 6.5\times 10^4\). These are **not** T-Drive logs.

## RQ1 — direction holds

Pre-registered: 4-block TV \(> 0.05\).

- Real T-Drive: 0.142  
- Protocol SensorScope: 0.192  
- Protocol U-Air: 0.278  

G1’s finer `opp_tv_realized_vs_target` (0.289 / 0.424) is a different estimand and stays on the G1 record.

Real-trace TV is **smaller** than balanced-unit TV (0.207): afternoon target mass is partly shared by taxi presence. Mobility does not invent a larger H-mismatch than uniform-over-units; it still leaves a clear H3 vs H4 gap (target H3 0.514 vs real \(R\) 0.384; target H4 0.235 vs real \(R\) 0.367).

## RQ2 — diagnostic only

No raven / FedAvg ranking on T-Drive. Formal canary remains a separate instruction (seal seeds 30001–30010; this gate did not start it).

Support split:

- Paper \(h(i)=\) H1–H4: **0** zero-support groups on test (SensorScope-like).  
- Design \(s(i)=\) spatial × block × weekday: **44.3%** of train-\(R\) units sit on train-only strata (U-Air-like in size; U-Air G1 was 25.5% at its Design support).

If a future T-Drive Design keys on \(s\)-level test mass, expect an \(A_r\) support shift. That is **not** a license to change Path B from this file. Path B stays the paper default.

## Claim ceiling add-on

See `CLAIM_ADDON.md`. Do not start G4 until asked. Do not rewrite the paper in this step.
