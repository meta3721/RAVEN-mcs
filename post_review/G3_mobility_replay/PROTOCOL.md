# G3 protocol — real-mobility opportunity replay (evidence level A)

Date: 2026-08-24  
Gate: W3 / handbook §7.1–7.4  
Default paper method (unchanged): Path B `raven_gated`.

## What this gate is

TMC needs mobility that is not a decorative protocol variable. The sealed T-Drive package already binds **R = REAL_FROM_TDRIVE**. This gate **measures** that opportunity layer and compares it to protocol-generated Complete-aligned opportunity on SensorScope / U-Air.

This is **not** a new prediction bake-off, not an end-to-end system, and not a formal 10-seed T-Drive ranking.

## Evidence level (handbook 7.3)

| Layer | Source | Label |
|---|---|---|
| R | Processed T-Drive `client_measurements` (trajectory presence after bbox/gap/speed filters) | **real** |
| O | Complete-aligned Bernoulli \(p_{\mathrm{obs}}=0.35\) on \(R=1\) | controlled |
| U | `compute_usable_r3`, \(s_{\max}=5\), same E3 device/network/deadline/staleness | controlled |

Allowed wording: **real-mobility opportunity replay** / **hybrid evidence, level A**.  
Forbidden: “original MCS datasets have mobile clients”, “T-Drive supplies real federated updates”, “end-to-end mobile system”, energy claims, evidence B or C.

## What is frozen / read-only

- `tdrive_protocol_seal_r1/` — protocol seal only. Do not write, regenerate, or unzip over it.
- `data/processed/tdrive_speed/` — hash-bound. Read only.
- Sealed E3 EventTraces — read only, used as **protocol-generated** opportunity.
- No change to `POLICY_MAP["raven"]` or Path B.

Formal T-Drive training (seal canary seed 30001, methods in the seal matrix) stays a **separate instruction**. This gate does not start it.

## Estimands (pre-registered)

All T-Drive opportunity masses use **train-split** \(R\) rows joined to atomic units. Target \(\mu\) is the sealed H1–H4 test-unit frequency (`TDRIVE_TARGET_H_SEAL.json`). \(h(i)\) is `fallback_h_id` (processed wall-clock hour labeled UTC; do not apply +8).

\[
\mathrm{TV}(p,q)=\tfrac12\sum_g |p_g-q_g|.
\]

1. **Real-trace** \(\pi^{\mathrm{opp}}_{\mathrm{real}}\): frequency of train \(R\) events over H1–H4.
2. **Balanced-unit** \(\pi^{\mathrm{opp}}_{\mathrm{bal}}\): uniform over train atomic units, then H-marginal. This is the “Balanced opportunity” foil.
3. **Protocol-generated** \(\pi^{\mathrm{opp}}_{\mathrm{prot}}\): SensorScope / U-Air seed-30001 EventTrace risk sets, marginalized to UTC six-hour blocks; \(\mu\) is that dataset’s test-unit H-frequency.

### 7.1 mobility metrics (T-Drive \(R\))

Coverage, client active fraction per slot, opportunity-stratum visitation (entropy / Gini / top-decile share), inter-arrival gaps (slots), Goh–Barabási burstiness \((\sigma-\mu)/(\sigma+\mu)\).

### 7.4 system metrics

Dropout (active in the first 50% of train slots, absent from the last 20%).  
Usable-update / deadline / staleness / compute / network rates: Monte Carlo of the frozen U-layer on \(R=1\) client-windows (\(N=20000\), seed 30001). Label every U number **controlled experimental**.  
Expected update count \(= n_{\mathrm{client\times window}}\times \widehat{\Pr}(U=1\mid R=1)\). No energy.

### RQ1 / RQ2 direction (no T-Drive training)

**RQ1 (mismatch exists):** \(\mathrm{TV}(\pi^{\mathrm{opp}},\mu)>0.05\) on the same 4-block partition. Direction is consistent if protocol SS, protocol U-Air, **and** real T-Drive all clear this threshold. Also report stratum-level mismatch and spatial opportunity CV (seal already has 2.27).

**RQ2 (Design / structural alignment):** no method ranking on T-Drive. Reuse the G1 support diagnostic: fraction of train-\(R\) units (and client-windows) with \(\pi^{\mathrm{tar}}(s)=0\).  
Predict: T-Drive behaves like SensorScope (keep Design) if H-level and a material stratum-level zero-target fraction stay near 0; like U-Air (gate Design off) if a large train-only support appears.

## Gate

| Verdict | Rule |
|---|---|
| `G3_ACCEPTED` | Level-A labels in place; all 7.1 metrics from real \(R\); 7.4 U rates labeled controlled; RQ1 threshold holds on T-Drive **and** both protocol datasets; RQ2 diagnostic written; seal dir untouched. |
| `G3_RQ1_WEAK` | Metrics complete, but T-Drive 4-block TV \(\le 0.05\). Then RQ1 may still hold at stratum/spatial layer — say so explicitly; do not claim 4-block mismatch. |
| `G3_FAIL` | Real \(R\) cannot be reconstructed, or real-trace mismatch is absent at **both** H and stratum layers. |

Success is **structural direction**, not RMSE. Do not open T-Drive TEST. Do not retune \(p_{\mathrm{obs}}\), \(s_{\max}\), or Design.

## Outputs

Only under `post_review/G3_mobility_replay/`.
