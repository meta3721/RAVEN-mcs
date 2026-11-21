# Round-v3 execution report — P1 (C0 reproduction, 20 seeds) + P2 (H table on the corrected FedAvg)

Pre-registration: `PREREG_P2.md` in this directory, written before any H value of this round was
computed. Rule unchanged: the frozen trace keeps its `U`; FedAvg gets `m_total = 0` for a
client-window whose `(client_id, opportunity_stratum)` carries `pi_tar = 0`; the gate is the
same three items as Stage B.

## 1. What ran

| item | value |
| --- | --- |
| driver | `.r3_work/r3_p1p2.py` (sha256 `00BFEDAE33C7BA27…`), rule in `.r3_work/r3_masszero.py` (`36F560138FDC5321…`) |
| trace pairing source | frozen E3 trace for C0/C3/C4, round-v1/u1 condition traces for C1/C2/C5 |
| P1 | 18 new C0 FedAvg runs (Stage B had 30001, 30006) + gate against the stored artifacts |
| P2 | 120 FedAvg runs = 6 conditions × 20 seeds (30001–30020) |
| oracle metrics | copied verbatim from `results_h_headroom/round_v1/runs` (seeds ≤ 30005) and `round_u1/runs` (≥ 30006); no oracle was trained |
| H table | `.r3_work/r3_htable.py`, `tables/H_SUMMARY.csv`, `H_DECISION.json` |
| verification | `.r3_work/r3_pairing_check.py` (trace pairing), `.r3_work/r3_verify_oracle_arms.py` (oracle-arm re-measurement), `.r3_work/r3_active_sets.py` (active-set identity) |

## 2. P1 — the FedAvg arm reproduces the stored artifact on all 20 seeds

`|ΔRMSE_μ| = |ΔΔ_group| = 0.000e+00` and identical active-client sets on every window, on all
20 seeds (`tables/C0_REPRO.csv`, `pass = True` for 20/20). Beyond the three gate items, the two
metrics the gate did **not** assert also match exactly (`tables/C0_REPRO_extra_metrics.csv`):

| metric | max abs diff over 20 seeds |
| --- | --- |
| `RMSE_mu` | 0.000e+00 |
| `Tail_RMSE` | 0.000e+00 |
| `RMSE_rho` | 0.000e+00 |
| `Delta_group` | 0.000e+00 |

So the `m_total` rule is not an approximation of the stored behaviour (the earlier attempts landed
0.15 %–3.3 % short of it): on the C0 condition it *is* the stored behaviour, exactly, on 20/20
seeds.

## 3. P2 — pairing and oracle-arm verification

* Trace pairing: for all 240 (condition, seed, arm) triples the round-v3 FedAvg run's
  `EventTrace_hash` equals the stored oracle run's. **0 mismatches.**
* Both oracle arms used by the H table were re-measured on the frozen trace
  (`tables/ORACLE_ARM_VERIFY.csv`):
  * `raven_simoracle` → `1.196856` (seed 30001) and `1.283674` (30006) = the frozen artifacts,
    `|Δ| = 0.0`. Positive control passed, so the re-run environment matches the frozen one.
  * `raven_simoracle_nodesign` → `1.154653` / `1.142415` = the stored h_round values,
    `|Δ| = 0.0`. The round-1 gate had only recorded a *finite* smoke value for this arm; it is
    now equality-verified, which the H cells below depend on.

## 4. The H table (U-Air, n = 20, corrected FedAvg)

`H = (RMSE_μ(fedavg_window) − RMSE_μ(oracle)) / RMSE_μ(fedavg_window)`; positive ⇒ the oracle is
better. CI = Student-t, df = 19.

| condition | FedAvg RMSE_μ | `raven_simoracle` | H | 95 % CI | go | `…_nodesign` | H | 95 % CI | go |
| --- | --- | --- | --- | --- | --- | --- | --- | --- | --- |
| C0_frozen | 1.188238 | 1.191447 | −0.0027 | [−0.0080, +0.0026] | no | 1.114401 | **+0.0617** | [+0.0471, +0.0764] | **yes** |
| C1_tilt_strong | 1.175616 | 1.180165 | −0.0039 | [−0.0085, +0.0008] | no | 1.103798 | **+0.0612** | [+0.0503, +0.0722] | **yes** |
| C2_tilt_extreme | 1.179738 | 1.184399 | −0.0041 | [−0.0095, +0.0014] | no | 1.114360 | **+0.0548** | [+0.0406, +0.0690] | **yes** |
| C3_low_capacity | 1.188034 | 1.191298 | −0.0028 | [−0.0080, +0.0024] | no | 1.114124 | **+0.0618** | [+0.0472, +0.0764] | **yes** |
| C4_block_uniform | 1.188238 | 1.194778 | −0.0055 | [−0.0108, −0.0003] | no | 1.117278 | **+0.0593** | [+0.0446, +0.0740] | **yes** |
| C5_combined | 1.179322 | 1.187190 | −0.0068 | [−0.0123, −0.0013] | no | 1.117102 | **+0.0521** | [+0.0379, +0.0663] | **yes** |

`H_DECISION.json`: `go_bar = 0.005` (unchanged from the 2026-09-24 round), `go_cells` = the six
`raven_simoracle_nodesign` cells, **`decision = "go"`** by the pre-registered rule
(cell `go` ⇔ `H_ci_lo > go_bar`; round `go` ⇔ at least one cell). The rule is reported as it
stands; nothing below revises it, and no cell was waived.

## 5. What the `go` is — and what it is not

1. **The manuscript's own oracle arm shows no headroom.** For `raven_simoracle`, |H| ≤ 0.68 %,
   and on C4/C5 the interval excludes zero on the *negative* side: FedAvg is marginally better
   (0.55 %, 0.68 %). On C0–C3 the interval contains zero. By the AM-5 vocabulary these cells are
   `equivalent_zero`, not `benefit`.
2. **All six `go` cells come from one arm**, `raven_simoracle_nodesign`, which is a
   review-loop diagnostic: `dataclasses.replace(POLICY_MAP["raven_simoracle"],
   uses_design_ratio=False)`. That policy keeps the default `gate_mode = "policy"`
   (`method_policy.py:35,165`), so with the flag false `_decide_g_r` returns `G_r = 0`
   (`OFF_MODE_NO_DESIGN`, `window_runner.py:403-405`) and `_apply_zeta` returns ζ ≡ 1
   (`window_runner.py:413-415`), i.e. **oracle propensity with the Design factor forced off**.
   Its nearest manuscript counterparts are `raven_wo_design` (the E4 Design-removal ablation,
   `gate_mode="always_off"`) and the Design-off setting the manuscript's own U-Air ranking
   already uses.
3. **The effect is the manuscript's own U-Air Design-removal row.** `tab:e4_ablation` reports,
   for U-Air, removing Design: `Δ_group −6.943 %*`, `Δ_c-s +4.990 %*`, `RMSE_μ −6.885 %*`,
   tail `−7.221 %*` (Holm-adjusted). Measured here on a different arm (oracle propensity instead
   of estimated): `RMSE_μ −6.44 %` and `Δ_group −7.51 %` versus the frozen `raven` arm. Same
   sign, comparable magnitude, no contradiction; the round-3 H frame therefore *corroborates*
   the U-Air Design gate (`ρ_r = 35.4 % ⇒ D = off`) from the RMSE side. It does **not** uncover
   untapped headroom, and it licenses no new manuscript claim.
4. **The frozen federated family is tied.** At C0 over 20 seeds: `fedavg_window` 1.188238,
   `local_hajek` 1.188238, `fedasync_window` 1.188279, `flamf_timealign_adapted` 1.188435,
   `debt_cal` 1.189318, `raven` 1.191114, `inst_cal` 1.191123, `raven_simoracle` 1.191447,
   `twostage_hajek` 1.215961, with `central_delivered` 1.178155 and `central_all` 1.055571
   (`tables/UAIR_ARM_CONTEXT.csv`). The corrected FedAvg does not overturn the manuscript's
   U-Air statement; on the corrected arm the oracle gains nothing measurable.
5. **The ~6 % is an active-set regime, shared by methods — not oracle information.**
   `tables/ACTIVE_SET_REGIME.csv` compares the window→`active_clients` maps (with `a_r_size`),
   not just their sizes, over all 20 seeds:

   | pairing | result |
   | --- | --- |
   | frozen-rule FedAvg vs `raven_simoracle` (Design on) | **identical, 20/20 seeds** (66/80 windows, 2.32 clients) |
   | old-rule FedAvg vs `raven_simoracle_nodesign` (Design off) | **identical, 20/20 seeds** (74/80 windows, 2.81 clients) |
   | frozen-rule FedAvg vs `raven_simoracle_nodesign` | different windows, 20/20 seeds |

   Two regimes exist, they are exactly the same sets for a FedAvg arm and an oracle arm, and the
   arms inside a regime differ only in their weights. Within regime A the oracle's H is
   −0.27 % (C0, CI [−0.80 %, +0.26 %]); within regime B the same comparison is −0.22 %
   (CI [−0.72 %, +0.28 %], `tables/H_SUMMARY_oldfedavg_by_condition.csv`). These four arms form
   a complete 2 × 2 (regime A/B × weighting family): the regime factor moves `RMSE_μ` by ~6 %,
   the weighting/information factor by ≤ 0.3 %. So *given* the active set the oracle adds nothing
   measurable, in either regime, and the entire +5–6 % is the regime switch (which client-windows
   enter `e_r`). That switch is the Design/`m_total` bookkeeping, and the manuscript already
   reports its size and price in `tab:e4_ablation` and already sets it per dataset through the
   `ρ_r` gate.

   On the FedAvg side the two regimes are a clean single-variable contrast: the regime-A and
   regime-B runs carry the **same `EventTrace_hash` and the same `config_hash` on 20/20 seeds**, so
   the `m_total` rule is the only difference (`tables/REGIME_AB_FEDAVG.csv`). Measured there: A's
   active-client set is a **subset** of B's in every shared window (20/20 seeds), A never holds a
   window B lacks, and the medians are 145 vs 192 client-windows — A keeps **74.6 %** of B's, i.e.
   drops ~25 %, which is the `72 of 288` pairs (25.0 %) that §3A `H4` records as the Design support
   loss, seen as client-windows. So the two regimes differ in the aggregation rule alone, not in the
   data delivered or the environment.
6. **Unresolved.** Whether the wider regime's RMSE gain is legitimate estimation or a
   side-effect of relaxing the delivery/design bookkeeping is not settled here, and this round
   measured `RMSE_μ` and `Δ_group` only. The manuscript's own price side (`Δ_c-s +4.990 %`) is
   the trade-off the design gate is built on.

## 6. Forbidden-claim compliance

* No claim that the FedAvg defect caused any part of the old H magnitude: the contrast is
  reported descriptively in `tables/H_SUMMARY_oldfedavg*.csv` and nothing is inferred from it.
* No equivalence-to-zero claim from a CI containing zero; the vocabulary is the AM-5 one.
* No claim that the Design-off oracle is deployable, nor that its advantage is attainable by the
  estimated-propensity method. It is an oracle arm.
* No pooling across conditions or datasets; SensorScope was not re-run.
* C1–C5 FedAvg cells have no 2026-08-11 counterpart and are **not** claimed to reproduce a
  stored artifact; their only validation is the C0 exact match on 20/20 seeds, stated with them.
* The `H_DECISION.json:STOP` of `results_h_response_shift/round_v1` is untouched and not
  revisited by this round.

## 7. Consequence for the manuscript

None required. Round-v3 closes the FedAvg arm's reproducibility defect (M7-adjacent) across all
six conditions and confirms, on a FedAvg arm that reproduces the stored artifacts exactly, that
the U-Air oracle statement of the manuscript stands: the paper's own oracle arm has no headroom
over FedAvg, and the ~6 % effect that does exist is the Design-removal trade-off the manuscript
already tabulates and already encodes in its U-Air design gate. No file under
`TO_OVERLEAF_paper_tmc_r1_clean/` was modified by this round.

## 8. Outputs

`PREREG_P2.md`, `tables/C0_REPRO.csv`, `tables/C0_REPRO_extra_metrics.csv`,
`H_seed_rows.csv`, `tables/H_SUMMARY.csv`, `tables/H_SUMMARY_oldfedavg.csv`,
`tables/H_SUMMARY_oldfedavg_by_condition.csv`, `tables/ORACLE_ARM_VERIFY.csv`,
`tables/UAIR_ARM_CONTEXT.csv`, `tables/ACTIVE_SET_REGIME.csv`, `tables/REGIME_AB_FEDAVG.csv`,
`tables/SUPPORT_COST_CORRECTED.csv`, `H_DECISION.json`,
`GATE_C0.json`, `runs/` (120 FedAvg runs), `verify_nodesign/` (4 verification runs).
