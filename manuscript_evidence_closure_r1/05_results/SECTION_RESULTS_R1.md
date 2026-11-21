# VII. Results (RQ-organized)

## VII-A. Experimental Setup

We evaluate RAVEN-MCS on three sealed datasets with distinct paper roles. SensorScope and U-Air are the scientifically comparable E3/E4 effectiveness blocks. NSW Traffic is used for E2 risk-semantic evidence and is **not** mixed with E3 as a homogeneous performance block (Traffic E3 cross-vintage inference is `NOT_COMPARABLE`).

For SensorScope and U-Air, the deployment-target grouping \(h(i)\) is four UTC time-of-day groups (H1: 00–06, H2: 06–12, H3: 12–18, H4: 18–24), constructed from train-split mass without test labels. The opportunity stratum \(s(i)\) is spatial identity \(\times\) four time blocks \(\times\) weekday/weekend. Thus \(h(i)\neq s(i)\). NSW Traffic uses the sealed E2 four-region public-target / stratum semantics.

Primary methods are FedAvg-Window, FedAsync-Window, TimeAlign-Agg (`flamf_timealign_adapted`), Local-Hajek, TwoStage-Hajek, and RAVEN-MCS, with Inst-Cal and Debt-Cal reported in the E3 table. Central-All, Central-Delivered, and RAVEN-SimOracle are reference-only. Primary metrics are \(\Delta_{\mathrm{group}}\), \(\Delta_{c,s}\), and RMSE\(_\mu\); Tail RMSE is a companion predictive metric. E3/E4 use paired seeds 30001–30020. Inference uses the sealed paired Wilcoxon family with Holm adjustment; EPS\(_0=10^{-12}\). Implementation environment is the sealed E3/E4 runners (P2 via cvxpy; warning-affected windows are feasibility-audited, not retrospectively certified optimal).

T-Drive is a protocol-only reserve and is **not** part of the current formal evidence.

## VII-B. RQ1: Why Arrival Risk Is Not Deployment-Target Risk

E1 provides balanced/no-harm context: under balanced selection, RAVEN does not significantly degrade RMSE\(_\mu\) relative to the window baselines (seeds 28001–28005). Statistical superiority is **not** established in E1, and E1 is not used as a ranking result.

E2 is the primary RQ1 evidence. On NSW Traffic complete-aligned traces, \(D_{\mathrm{aligned}}=\Delta\mathrm{RMSE}_\mu-\Delta\mathrm{RMSE}_\rho\) has a stable nonzero (negative) direction across the five formal methods and 20 paired seeds (Fig.~1). The visual message is risk non-interchangeability: the distribution that produces usable updates is not generally interchangeable with the intended deployment-target risk. Fig.~1 is **not** a RAVEN-versus-baselines superiority plot.

This mismatch motivates target-aware correction rather than arrival-risk matching alone.

## VII-C. RQ2: Overall Effectiveness of RAVEN-MCS

On SensorScope, RAVEN reduces \(\Delta_{\mathrm{group}}\) and \(\Delta_{c,s}\) relative to the main window and Hajek baselines, with Holm-supported paired differences in the sealed structural families (Table~II, Fig.~2). On U-Air the same structural direction holds: RAVEN attains lower \(\Delta_{\mathrm{group}}\) and \(\Delta_{c,s}\) than the main baselines, again Holm-supported.

Prediction is competitive rather than uniformly dominant. RMSE\(_\mu\) and Tail RMSE remain close to the window baselines on SensorScope (no Holm-supported RMSE superiority vs those baselines). On U-Air, RMSE\(_\mu\) shows a Holm-supported improvement versus TwoStage-Hajek but not versus the window methods. RAVEN therefore maintains competitive deployment-target prediction risk with **selective** significant gains.

RAVEN consistently reduces structural mismatch on the two scientifically comparable datasets while maintaining competitive prediction performance, with selective significant gains. We do **not** claim that RAVEN is superior to every baseline on every metric.

## VII-D. RQ3: Where Do the Gains Come From?

E4 removes one RAVEN component at a time on the final 240-cell family (w/o-Inst Generation 2 only). Relative change \(100\times(\mathrm{Metric}_{w/o X}-\mathrm{Metric}_{\mathrm{RAVEN}})/\mathrm{Metric}_{\mathrm{RAVEN}}\) is shown in Fig.~3: positive bars mean removal worsens a lower-is-better metric.

- **Design:** `ENDPOINT_TRADEOFF` — mixed structural/predictive directions across datasets.
- **Obs:** `ENDPOINT_TRADEOFF` — endpoint-specific structural directions.
- **Use:** `NO_CLEAR_EFFECT` in the tested Complete-aligned family. This does **not** prove that usable-update modeling is conceptually irrelevant; it means no robust marginal sealed effect was detected here.
- **Inst:** `ENDPOINT_TRADEOFF` — mixed significant directions across structural and predictive endpoints (not the superseded one-sided `STRUCTURAL_ONLY_SUPPORTED` Inst label).
- **Debt:** `STRUCTURAL_ONLY_SUPPORTED`, statistically consistent but **quantitatively small**.

RAVEN behaves as a coupled correction/calibration architecture rather than a sum of independently monotone boosters.

## VII-E. Summary of Empirical Evidence

E2 shows why target-aware correction is needed. E3 shows that the full architecture improves structural alignment on comparable SensorScope/U-Air evidence while remaining competitively predictive. E4 shows that component roles are heterogeneous and interacting. No new quantitative claims are introduced in this summary.
