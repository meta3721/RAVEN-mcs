"""Results, Discussion, Limitations, Conclusion drafts (markdown + tex)."""

from __future__ import annotations

from pathlib import Path

from raven_mcs.paper_data_r1.io_util import write_text


RESULTS_MD = r"""# VII. Results (RQ-organized)

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
"""

RESULTS_TEX = r"""\section{Results}
\subsection{Experimental Setup}
We evaluate RAVEN-MCS on three sealed datasets with distinct paper roles. SensorScope and U-Air are the scientifically comparable E3/E4 effectiveness blocks. NSW Traffic is used for E2 risk-semantic evidence and is not mixed with E3 as a homogeneous performance block (Traffic E3 cross-vintage inference is \texttt{NOT\_COMPARABLE}).

For SensorScope and U-Air, the deployment-target grouping \(h(i)\) is four UTC time-of-day groups (H1: 00--06, H2: 06--12, H3: 12--18, H4: 18--24), constructed from train-split mass without test labels. The opportunity stratum \(s(i)\) is spatial identity \(\times\) four time blocks \(\times\) weekday/weekend, so \(h(i)\neq s(i)\). NSW Traffic uses the sealed E2 four-region public-target/stratum semantics.

Primary methods are FedAvg-Window, FedAsync-Window, TimeAlign-Agg, Local-Hajek, TwoStage-Hajek, and RAVEN-MCS. Inst-Cal and Debt-Cal are reported in the E3 table; Central-All, Central-Delivered, and RAVEN-SimOracle are reference-only. Primary metrics are \(\Delta_{\mathrm{group}}\), \(\Delta_{c,s}\), and RMSE\(_\mu\). E3/E4 use paired seeds 30001--30020 with the sealed Wilcoxon+Holm protocol. T-Drive is a protocol-only reserve and is not part of the current formal evidence.

\subsection{RQ1: Why Arrival Risk Is Not Deployment-Target Risk}
E1 is a balanced no-harm sanity check: statistical superiority is not established. E2 is the primary RQ1 evidence. On NSW Traffic complete-aligned traces, \(D_{\mathrm{aligned}}=\Delta\mathrm{RMSE}_\mu-\Delta\mathrm{RMSE}_\rho\) has a stable nonzero direction across five methods and 20 seeds (Fig.~\ref{fig:e2}). This supports risk non-interchangeability and is not a RAVEN ranking result.

\subsection{RQ2: Overall Effectiveness of RAVEN-MCS}
On SensorScope and U-Air, RAVEN reduces \(\Delta_{\mathrm{group}}\) and \(\Delta_{c,s}\) relative to the main window and Hajek baselines, with Holm-supported paired differences in the sealed structural families (Table~\ref{tab:e3}, Fig.~\ref{fig:e3}). RMSE\(_\mu\) remains competitive, with selective rather than uniform Holm-supported gains. We do not claim that RAVEN is superior to every baseline on every metric.

\subsection{RQ3: Where Do the Gains Come From?}
E4 one-factor ablations on the final 240-cell family (w/o-Inst Generation~2) yield endpoint-dependent roles (Fig.~\ref{fig:e4}): Design/Obs/Inst are \texttt{ENDPOINT\_TRADEOFF}; Use is \texttt{NO\_CLEAR\_EFFECT}; Debt is \texttt{STRUCTURAL\_ONLY\_SUPPORTED} and quantitatively small. RAVEN is a coupled architecture, not a sum of independently monotone boosters.

\subsection{Summary of Empirical Evidence}
E2 motivates target-aware correction; E3 shows structural alignment gains on comparable datasets; E4 shows heterogeneous component roles. No new quantitative claims are introduced here.
"""

DISCUSSION_MD = r"""# Discussion

## 1. Why structural target alignment is the primary empirical success criterion

The paper's problem is that usable-update distributions can differ from the intended deployment target. Reducing \(\Delta_{\mathrm{group}}\) and \(\Delta_{c,s}\) directly measures whether correction/calibration moved mass toward that public target. RMSE\(_\mu\) remains necessary as a deployment-risk companion, but it is not the sole success definition.

## 2. Why improved structural alignment need not yield universal RMSE gains

Target-weighted RMSE can stay similar when methods already fit the observed support well, when residual error is dominated by measurement noise, or when structural reweighting trades error across groups. Selective RMSE gains (and null RMSE Holm tests against window baselines on SensorScope) are therefore compatible with a structural success.

## 3. Why component trade-offs are expected

RAVEN couples design, observation, usability, instantaneous calibration, and debt. Removing one factor can help one endpoint while hurting another because the remaining modules re-equilibrate. Fig.~3 is intended to display mixed signs, not a uniform benefit story.

## 4. What Use = NO_CLEAR_EFFECT means and does not mean

It means that, in the sealed Complete-aligned E4 family, dropping usable-update IPW produced no Holm-significant robust marginal effect. It does **not** mean that usable updates are scientifically irrelevant, that \(U\) can be ignored in the generative model, or that Use is proven unnecessary in every MCS regime.

## 5. Why Debt can be statistically stable but practically small

Paired tests can detect a consistent direction whose magnitude is tiny relative to \(\Delta_{\mathrm{group}}\) level. The paper therefore reports Debt as structurally supported and quantitatively small, not as a large practical lever.

## 6. Traffic source-vintage limitation

E2 Traffic is valid for C1–C2. E3 reused-old versus new-current Traffic is `NOT_COMPARABLE`. No table or figure may treat them as one homogeneous performance block.

## 7. P2 feasibility versus exact optimality

Warning-affected windows were feasibility-audited. Exact post-hoc optimality is not reconstructable from sealed outputs (C10). Theoretical uniqueness under stated assumptions is a theory claim, not an experimental certificate.

## 8. External-validity limitation

Current core evidence does not contain a formal T-Drive performance block. Real taxi-mobility opportunity remains a protocol-sealed reserve, not a present result.
"""

DISCUSSION_TEX = r"""\section{Discussion}
Structural metrics are the primary empirical success criterion because they measure whether usable-update mass matches the public deployment target. Improved alignment need not imply RMSE gains on every dataset and baseline: prediction can remain competitive while group composition improves.

Component trade-offs are expected in a coupled correction/calibration system. Use \(=\) \texttt{NO\_CLEAR\_EFFECT} means no robust sealed E4 marginal effect, not that usability is conceptually irrelevant. Debt is statistically consistent but quantitatively small.

E2 Traffic supports the risk-semantic claim; E3 Traffic cross-vintage inference is \texttt{NOT\_COMPARABLE}. P2 warning windows are feasibility-audited; exact experimental optimality is not reconstructable. Formal real-mobility performance is not part of the current evidence.
"""

LIMITATIONS_MD = r"""# Limitations

- No universal RMSE superiority is claimed or shown.
- Component effects are endpoint- and dataset-dependent.
- Use has no robust marginal effect in the current Complete-aligned E4 family.
- Debt's sealed structural effect is statistically consistent but small.
- Traffic E3 cross-vintage comparison is excluded (`NOT_COMPARABLE`).
- P2 warning windows lack retrospective exact optimality reconstruction.
- Propensity quality remains a modeling dependence of IPW-style correction.
- Real mobility external validation is not yet part of the current formal evidence (T-Drive protocol reserved).
"""

LIMITATIONS_TEX = r"""\section{Limitations}
We do not claim universal RMSE superiority. Component effects are endpoint-dependent. Use has no robust marginal sealed E4 effect. Debt's structural effect is small. Traffic E3 cross-vintage comparison is excluded. P2 warning windows are not retrospectively certified optimal. IPW correction depends on propensity quality. Formal real-mobility performance is not part of the current evidence.
"""

CONCLUSION_MD = r"""# Conclusion (claim-safe draft)

Mobile crowdsensing under two-stage non-random selection can make the distribution of usable federated updates differ from the intended deployment target, so arrival/usable-update risk is not generally interchangeable with deployment-target risk.

RAVEN-MCS coordinates selection-aware correction with instantaneous and long-term target calibration. On scientifically comparable SensorScope and U-Air evidence, the architecture consistently reduces structural target mismatch while remaining competitively predictive, with selective rather than universal RMSE gains.

Component ablations show endpoint-dependent roles and trade-offs: Design, Obs, and Inst are endpoint trade-offs; Use has no clear sealed marginal effect in the tested family; Debt is statistically consistent but quantitatively small. RAVEN is therefore a coupled system, not a set of independently indispensable boosters.

We do not claim universal dominance, three-dataset homogeneous E3 superiority, empirical necessity of every module, or experimentally certified exact P2 optimality. External real-mobility performance remains outside the present formal block.
"""

CONCLUSION_TEX = r"""\section{Conclusion}
Two-stage non-random selection can induce a mismatch between usable-update and deployment-target distributions. RAVEN-MCS coordinates selection-aware correction with target calibration. On SensorScope and U-Air, it consistently reduces structural mismatch while remaining competitively predictive, with selective RMSE gains. Component roles are heterogeneous: Design/Obs/Inst exhibit endpoint trade-offs, Use has no clear sealed marginal effect in the tested family, and Debt is statistically consistent but small. We do not claim universal dominance.
"""


def write_prose(out: Path) -> None:
    write_text(out / "05_results/SECTION_RESULTS_R1.md", RESULTS_MD)
    write_text(out / "05_results/SECTION_RESULTS_R1.tex", RESULTS_TEX)
    write_text(out / "06_discussion/DISCUSSION_R1.md", DISCUSSION_MD)
    write_text(out / "06_discussion/DISCUSSION_R1.tex", DISCUSSION_TEX)
    write_text(out / "06_discussion/LIMITATIONS_R1.md", LIMITATIONS_MD)
    write_text(out / "06_discussion/LIMITATIONS_R1.tex", LIMITATIONS_TEX)
    write_text(out / "07_claim_alignment/CONCLUSION_R1.md", CONCLUSION_MD)
    write_text(out / "07_claim_alignment/CONCLUSION_R1.tex", CONCLUSION_TEX)
