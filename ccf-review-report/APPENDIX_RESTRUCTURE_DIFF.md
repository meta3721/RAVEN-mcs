# 附录结构重组完整源码差异

以本轮备份为基准；回退需合并保留后续用户改动。

## main.tex

`diff
--- main.tex before
+++ main.tex after
@@ -574,7 +574,7 @@
 \end{equation}
 Local H\'ajek removes total scale from training; $m_{k,r}d_{k,r}$ carries it
 and usable-update correction into relative server mass.
-Appendix~\ref{app:deferred_constructions} gives the ideal untruncated
+Appendix~\ref{app:ideal_factorization} gives the ideal untruncated
 $\beta^\star\overline a^\star$ factorization. The stabilized reference
 $\widehat{\boldsymbol\beta}_r$ is distinct from the feasible decision
 $\boldsymbol\alpha_r$: incomplete support can prevent
@@ -615,7 +615,7 @@
 \end{equation}
 The cap $\overline\alpha_r=\min\{1,\max\{\alpha_{\max},1/K_r\}\}$ and
 support bound $\overline E_r=\min\{E_{\min},K_r\}$ use frozen
-$0<\alpha_{\max}\le1$, $E_{\min}\ge1$ (Appendix~\ref{app:deferred_constructions}).
+$0<\alpha_{\max}\le1$, $E_{\min}\ge1$ (Appendix~\ref{app:correction_constraints}).
 These definitions make Uniform feasible while controlling single-client
 dominance and minimum effective support.  The reconstructed reference need not
 satisfy these constraints.  The lagged variance proxy is
@@ -1716,7 +1716,8 @@
 (Supplementary Table~\ref{tab:target_concentration}; Appendix~\ref{app:target_concentration}).
 Formal station RMSE exceeds training-mean references; separate development
 validation improves on simple baselines on Traffic/SensorScope, not U-Air.
-Learning and update-rule budgets remain distinct (Appendix~\ref{app:learning_capacity}).
+Learning and update-rule budgets remain distinct
+(Appendices~\ref{app:learning_capacity} and~\ref{app:update_rule_sensitivity}).
 
 Support determines represented group mass; cap and ESS bound its adjustment.
 Weight freedom, composition freedom, and prediction sensitivity remain distinct.

`

## appendix.tex

`diff
--- appendix.tex before
+++ appendix.tex after
@@ -1,11 +1,10 @@
 \appendices
-\section{Complete Proofs for Sections III--VI}
+\section{Supplementary Model Definitions and Main Proofs}
 \label{app:complete_proofs}
-
-This appendix gives the deferred proofs for Sections~III--VI, using their
-notation, targets, sequential probabilities, and P2 feasible set.
-
-\subsection{Deferred Constructions from the Main Text}
+\label{app:proof_summary}
+Definitions and proofs supplement the model, reconstruction, and calibration analysis.
+
+\subsection{Compatible Target Measures}
 \label{app:deferred_constructions}
 
 The compatible client--stratum target used for opportunity correction is
@@ -49,22 +48,9 @@
  \label{eq:target_ki_mass}
 \end{equation}
 
-\subsubsection{Target-Positive Pairs, Coverage, and the Heuristic Lookup}
-\label{app:itar_lookup}
-$I_{\mathrm{tar}}=\{(k,s):\pi^{\mathrm{tar}}_{k,s}>0\}$ and $C_t$ in
-\eqref{eq:agg_Ct} use $\pi^{\mathrm{tar}}_{k,s}$ from \eqref{eq:target_ks_mass}.
-For unit $i$, $k(i)$ is the unique client on the frozen occupancy map
-(stations on SensorScope and U-Air, occupied cells on T-Drive and City
-Scanner). The lookup is $\pi^{\mathrm{tar}}(k(i),s(i))$; a missing key is $0$,
-including when several clients meet the same unit. Table~\ref{tab:scd_phi_freeze}
-is the train-unit fraction of those zeros. It is not
-$\#\{i:\varpi_i^{\mathrm{tar}}=0\}$ and not a target-positive-pair check. It
-enters \eqref{eq:design_gate}, and can set \eqref{eq:design_factor} only when
-its inputs exist before the window; both fixed settings are reported.
-$\pi^{\mathrm{opp}}_{k,s,t}$ is $F_{t-}$-measurable on the same key. Since
-$\sum_{k,s}\pi^{\mathrm{tar}}_{k,s}=1$, \eqref{eq:agg_Ct} is certified mass over
-positive target mass.
-
+\subsection{Correction, Constraints, and Ideal Weights}
+\label{app:correction_constraints}
+\label{app:ideal_factorization}
 A2's usable-update mean-ignorability display is
 \begin{equation}
  \mathbb{E}\!\left[
@@ -95,22 +81,6 @@
 \end{aligned}
  \label{eq:cap_ess}
 \end{equation}
-The Lipschitz constant in \eqref{eq:g4_beta} is
-\begin{multline}
-C_1
-=
-\frac{2K_r n_r}{B_{\min}}
-\Bigl(
-d_{\max}\max\{L_\pi,L_p\}+a_{\max}L_q
-\Bigr),\\
-L_\pi=\frac{\pi^{\mathrm{tar}}_{\max}}{\pi_{\min}^2 p_{\min}},\quad
-L_p=\frac{\pi^{\mathrm{tar}}_{\max}}{\pi_{\min}p_{\min}^2},\\
-L_q=\min\Bigl\{\frac{1}{q_{\min}^2},\,d_{\max}^2\Bigr\},
-\label{eq:g4_c1}
-\end{multline}
-with $L_\pi=0$ and $L_p=1/p_{\min}^2$ under Design off. These constants bound
-the implemented map's sensitivity to the opportunity, observation, and usable
-margins. They are worst-case envelopes, not numerical certificates.
 The ideal untruncated factorization of the sequential weight is
 \begin{equation}
  \beta^\star_{k,r}\overline a^\star_{k,r,i}
@@ -233,6 +203,24 @@
 
 \subsection{Proof of Proposition~\ref{prop:practical_plugin}}
 \label{app:proof_prop3}
+\label{app:perturbation_constants}
+The Lipschitz constant in \eqref{eq:g4_beta} is
+\begin{multline}
+C_1
+=
+\frac{2K_r n_r}{B_{\min}}
+\Bigl(
+d_{\max}\max\{L_\pi,L_p\}+a_{\max}L_q
+\Bigr),\\
+L_\pi=\frac{\pi^{\mathrm{tar}}_{\max}}{\pi_{\min}^2 p_{\min}},\quad
+L_p=\frac{\pi^{\mathrm{tar}}_{\max}}{\pi_{\min}p_{\min}^2},\\
+L_q=\min\Bigl\{\frac{1}{q_{\min}^2},\,d_{\max}^2\Bigr\},
+\label{eq:g4_c1}
+\end{multline}
+with $L_\pi=0$ and $L_p=1/p_{\min}^2$ under Design off. These constants bound
+the implemented map's sensitivity to the opportunity, observation, and usable
+margins. They are worst-case envelopes, not numerical certificates.
+
 \begin{restated}{Proposition}{prop:practical_plugin}
 Assume A1, A4, A5, and A6b.  Let the stabilized window mass obey
 $\mathbf{1}^{\top}b_r^{\mathcal T}\ge B_{\min}>0$ at the true margins, and let
@@ -539,17 +527,32 @@
 \eqref{eq:app_reference_nonexpansive}.
 \qed
 
-\label{app:proof_summary}
 Reconstruction concerns pooled population moments; reference stability fixes
 the entire window state. Neither supplies unconditional long-run alignment or
 a prediction guarantee.
 
-\section{Complete Proofs for Aggregate Coverage Certification}
+\section{Aggregate Coverage Diagnostic and Its Proofs}
 \label{app:agg_coverage_proofs}
-
-This section gives the deferred coverage proofs for
-Sections~\ref{subsec:agg_certificate_alg} and~\ref{subsec:agg_coverage_theory}.
-
+Definitions and proofs supplement the aggregate coverage diagnostic.
+
+\subsection{Target-Positive Coverage and Lookup}
+\label{app:itar_lookup}
+$I_{\mathrm{tar}}=\{(k,s):\pi^{\mathrm{tar}}_{k,s}>0\}$ and $C_t$ in
+\eqref{eq:agg_Ct} use $\pi^{\mathrm{tar}}_{k,s}$ from \eqref{eq:target_ks_mass}.
+For unit $i$, $k(i)$ is the unique client on the frozen occupancy map
+(stations on SensorScope and U-Air, occupied cells on T-Drive and City
+Scanner). The lookup is $\pi^{\mathrm{tar}}(k(i),s(i))$; a missing key is $0$,
+including when several clients meet the same unit. Table~\ref{tab:scd_phi_freeze}
+is the train-unit fraction of those zeros. It is not
+$\#\{i:\varpi_i^{\mathrm{tar}}=0\}$ and not a target-positive-pair check. It
+enters \eqref{eq:design_gate}, and can set \eqref{eq:design_factor} only when
+its inputs exist before the window; both fixed settings are reported.
+$\pi^{\mathrm{opp}}_{k,s,t}$ is $F_{t-}$-measurable on the same key. Since
+$\sum_{k,s}\pi^{\mathrm{tar}}_{k,s}=1$, \eqref{eq:agg_Ct} is certified mass over
+positive target mass.
+
+\subsection{Historical Quantiles and Diagnostic States}
+\label{app:coverage_algorithm}
 \begin{algorithm}[t]
 \caption{Aggregate coverage certificate (diagnostic Gate)}
 \label{alg:agg_certificate}
@@ -579,6 +582,7 @@
 \end{algorithmic}
 \end{algorithm}
 
+\subsection{Pairwise Opportunity Barriers}
 \begin{proposition}[Positive pairwise LCB barrier]
 \label{prop:pairwise-lcb-barrier}
 Let $X_t\ge 0$ denote the realized opportunity of one target pair in window
@@ -599,31 +603,7 @@
 obeying the designated-entity necessary condition.
 \end{corollary}
 
-\begin{corollary}[False-safe Gate bound]
-\label{cor:false-safe-gate}
-Under the conditions of Theorem~2,
-\begin{equation}
- P\bigl(\mathrm{Gate}_t=1\text{ and }C_t<\tau_{\mathrm{cov}}\mid g\bigr)
- \le\alpha.
- \label{eq:agg_cor2}
-\end{equation}
-\end{corollary}
-
-\begin{proposition}[Arbitrary-drift applicability boundary]
-\label{prop:drift-boundary}
-Suppose two data-generating worlds share the same legal $F_{t-}$ but have
-$C_t=c_{\mathrm{high}}$ and $C_t=c_{\mathrm{low}}$ with
-$c_{\mathrm{low}}<\tau_{\mathrm{cov}}<c_{\mathrm{high}}$.  Any deterministic
-pre-window certificate outputs the same $C^{\mathrm{LCB}}_t$ in both worlds.
-If that output is at least $\tau_{\mathrm{cov}}$, the certificate is
-false-safe in the low world; if it is below $\tau_{\mathrm{cov}}$, it cannot
-certify the high world.  Without an assumption linking the current window to
-observable pre-window information, no method can simultaneously provide
-nontrivial per-window certification and universal protection against
-arbitrary unannounced regime shifts.
-\end{proposition}
-
-\subsection{Proof of Proposition~\ref{prop:pairwise-lcb-barrier}}
+\subsubsection{Proof of Proposition~\ref{prop:pairwise-lcb-barrier}}
 \label{app:proof_pairwise_lcb}
 \begin{proof}
 Fix a regular conditional probability given $F_{t-}$. On $\{L_t>0\}$,
@@ -636,7 +616,7 @@
 be zero wherever the stated zero-opportunity condition holds.
 \end{proof}
 
-\subsection{Proof of Corollary~\ref{cor:availability-barrier}}
+\subsubsection{Proof of Corollary~\ref{cor:availability-barrier}}
 \label{app:proof_availability_barrier}
 \begin{proof}
 Let $i=(k,s)$ and $e(i)=k$ be the designated stressed entity of the pair.
@@ -705,6 +685,16 @@
 
 \subsection{Proof of Corollary~\ref{cor:false-safe-gate}}
 \label{app:proof_false_safe}
+\begin{corollary}[False-safe Gate bound]
+\label{cor:false-safe-gate}
+Under the conditions of Theorem~2,
+\begin{equation}
+ P\bigl(\mathrm{Gate}_t=1\text{ and }C_t<\tau_{\mathrm{cov}}\mid g\bigr)
+ \le\alpha.
+ \label{eq:agg_cor2}
+\end{equation}
+\end{corollary}
+
 \begin{proof}
 On the event $\{\mathrm{Gate}_t=1,\,C_t<\tau_{\mathrm{cov}}\}$ one has
 $C^{\mathrm{LCB}}_t\ge\tau_{\mathrm{cov}}>C_t$, hence
@@ -722,6 +712,20 @@
 
 \subsection{Proof of Proposition~\ref{prop:drift-boundary}}
 \label{app:proof_drift_boundary}
+\begin{proposition}[Arbitrary-drift applicability boundary]
+\label{prop:drift-boundary}
+Suppose two data-generating worlds share the same legal $F_{t-}$ but have
+$C_t=c_{\mathrm{high}}$ and $C_t=c_{\mathrm{low}}$ with
+$c_{\mathrm{low}}<\tau_{\mathrm{cov}}<c_{\mathrm{high}}$.  Any deterministic
+pre-window certificate outputs the same $C^{\mathrm{LCB}}_t$ in both worlds.
+If that output is at least $\tau_{\mathrm{cov}}$, the certificate is
+false-safe in the low world; if it is below $\tau_{\mathrm{cov}}$, it cannot
+certify the high world.  Without an assumption linking the current window to
+observable pre-window information, no method can simultaneously provide
+nontrivial per-window certification and universal protection against
+arbitrary unannounced regime shifts.
+\end{proposition}
+
 \begin{proof}
 The two worlds share $F_{t-}$, hence the pre-window rule has the same output
 $L$ in both. If $L\ge\tau_{\mathrm{cov}}$, it exceeds $c_{\mathrm{low}}$
@@ -732,280 +736,46 @@
 history; it does not restore Theorem~\ref{thm:agg-lcb} on an undetected first-shift window.
 \end{proof}
 
-\section{Supplementary Risk-Semantic Evidence}
-\label{app:risk_semantic_evidence}
-
-This appendix gives the balanced control and full selection-scenario statistics
-for interpreting target and arrival risk.
-
-\subsection{Balanced No-Harm Control}
-\label{app:e1_balanced}
-
-Table~\ref{tab:app_e1_balanced} reports all five paired methods under the balanced
-control.  The selected TimeAlign reference has mean
-$\mathrm{RMSE}_\mu=7.7108$, while RAVEN-MCS obtains $7.7154$.  RAVEN's
-pre-specified mean relative degradation is $0.0599\%$; the one-sided 95\%
-upper bound is $0.134\%$, below the pre-specified $3\%$ no-harm margin.
-The balanced experiment evaluates this criterion under aligned selection.
-
-\begin{table}[!htbp]
-\centering
-\caption{Balanced control over the five pre-specified paired seeds.}
-\label{tab:app_e1_balanced}
-\footnotesize
-\setlength{\tabcolsep}{5pt}
-\begin{tabular*}{\columnwidth}{@{\extracolsep{\fill}}lcc}
-\toprule
-Method & $\mathrm{RMSE}_\mu$ & Seeds\\
-\midrule
-FedAvg-Window & $7.7220\pm0.0289$ & 5 \\
-FedAsync-Window & $7.7222\pm0.0287$ & 5 \\
-TimeAlign-Agg & $7.7108\pm0.0272$ & 5 \\
-TwoStage-H\'ajek & $7.7262\pm0.0291$ & 5 \\
-RAVEN-MCS & $7.7154\pm0.0337$ & 5 \\
-\bottomrule
-\end{tabular*}
-\end{table}
-
-\subsection{Complete Risk Non-Interchangeability Statistics}
-\label{app:e2_full_stats}
-
-Table~\ref{tab:app_e2_daligned} gives the complete method-level risk-interchangeability summary for
-the pre-specified difference-of-differences
-$D_{\mathrm{aligned}}=\Delta\mathrm{RMSE}_{\mu}
--\Delta\mathrm{RMSE}_{\rho}$.  The negative mean is stable across all five
-methods, and 17--18 of 20 paired seeds are negative.  This supports the
-risk-semantic premise that arrival-weighted and deployment-target-weighted
-views react differently to the same structured selection shift.
-
-\begin{table}[!htbp]
-\centering
-\caption{Complete-aligned risk non-interchangeability statistics.
-CI denotes the 95\% interval; $p$ is the paired Wilcoxon test of
-$D_{\mathrm{aligned}}$ against zero.}
-\label{tab:app_e2_daligned}
-\scriptsize
-\setlength{\tabcolsep}{2.5pt}
-\begin{tabular*}{\columnwidth}{@{\extracolsep{\fill}}lcccc}
-\toprule
-Method & $D_{\mathrm{aligned}}$ & 95\% CI & Neg. seeds & $p$\\
-\midrule
-FedAsync-Window & $-0.02115$ & $[-0.03158,-0.01073]$ & 18/20 & $4.83e-04$ \\
-FedAvg-Window & $-0.02115$ & $[-0.03158,-0.01071]$ & 18/20 & $4.83e-04$ \\
-TimeAlign-Agg & $-0.02137$ & $[-0.03185,-0.01090]$ & 17/20 & $4.83e-04$ \\
-RAVEN-MCS & $-0.02088$ & $[-0.03132,-0.01043]$ & 17/20 & $5.86e-04$ \\
-TwoStage-H\'ajek & $-0.02120$ & $[-0.03169,-0.01072]$ & 17/20 & $5.86e-04$ \\
-\bottomrule
-\end{tabular*}
-\end{table}
-
-
-\subsection{Response to Each Selection Layer}
-\label{app:e2_layer_matrix}
-
-The six scenarios use five methods and 20 paired seeds each (600 existing
-runs).  Table~\ref{tab:e2_layer_matrix} summarizes the final numerical-tie-aware
-analysis.  Each range spans the five method-specific mean changes from balanced;
-the significant counts retain the existing within-method, within-metric Holm
-families over the five non-balanced scenarios.  Signed arrival--target gaps distinguish risk direction from absolute mismatch.
-
-\begin{table*}[t]
-\centering
-\caption{Risk responses to controlled selection layers on NSW-Traffic.
-Changes use the original standardized RMSE units; $\times10^{-3}$ applies to
-both range columns. Counts are Holm-significant methods out of five.}
-\label{tab:e2_layer_matrix}
-\footnotesize
-\begin{tabular*}{\textwidth}{@{\extracolsep{\fill}}lrrrr}
-\toprule
-Scenario & Target change range & Arrival change range & Target significant & Arrival significant\\
-\midrule
-Balanced & 0 & 0 & -- & --\\
-Opportunity only & $[0.057,0.114]$ & $[5.699,5.990]$ & 0/5 & 0/5\\
-Observation only & $[0.108,0.157]$ & $[11.018,11.145]$ & 0/5 & 5/5\\
-Usable update only & $[0.193,0.245]$ & $[5.472,5.607]$ & 0/5 & 0/5\\
-Complete aligned & $[0.757,0.820]$ & $[21.660,22.130]$ & 2/5 & 5/5\\
-Complete counteracting & $[0.030,0.059]$ & $[12.447,12.639]$ & 0/5 & 0/5\\
-\bottomrule
-\end{tabular*}
-\end{table*}
-
-\section{Local-H\'ajek Degeneracy Analysis}
-\label{app:local_hajek}
-
-The equality between Local-Hajek and FedAvg in the formal SensorScope/U-Air
-blocks is protocol-specific and should not be interpreted as a general
-equivalence.  Table~\ref{tab:app_local_hajek} covers
-9666 effective client-windows: 6070 on SensorScope and
-3596 on U-Air.  In every audited effective client-window, the realized
-within-client correction-weight range is 0.
-
-\begin{table}[!htbp]
-\centering
-\caption{Within-client weight constancy.}
-\label{tab:app_local_hajek}
-\footnotesize
-\setlength{\tabcolsep}{5pt}
-\begin{tabular*}{\columnwidth}{@{\extracolsep{\fill}}lcc}
-\toprule
-Dataset & Effective client-windows & Weight range\\
-\midrule
-SensorScope & 6070 & $0$\\
-U-Air & 3596 & $0$\\
-\midrule
-Total & 9666 & $0$\\
-\bottomrule
-\end{tabular*}
-\end{table}
-
-The collapse follows directly from the normalized local objective.  Let
-$\mathcal I_{k,r}^{+}$ be the records retained by an effective client-window
-and let $N_{k,r}^{+}=|\mathcal I_{k,r}^{+}|$.  If the realized first-stage
-weight is constant over that set, i.e.,
-$a_{k,r,i}=a_{k,r}>0$ for all $i\in\mathcal I_{k,r}^{+}$, then
-\begin{equation}
- \overline a_{k,r,i}
- =
- \frac{a_{k,r}}
- {N_{k,r}^{+}a_{k,r}}
- =
- \frac{1}{N_{k,r}^{+}}.
- \label{eq:app_local_hajek_uniform}
-\end{equation}
-Consequently,
-\begin{equation}
- \widehat F^H_{k,r}(\theta)
- =
- \frac{1}{N_{k,r}^{+}}
- \sum_{i\in\mathcal I_{k,r}^{+}}
- \frac{1}{2}
- \left(
- f_\theta(i;C_i^{\mathrm{dep}})-Z_{k,r,i}
- \right)^2,
- \label{eq:app_local_hajek_collapse}
-\end{equation}
-which is exactly the uniform local objective used by the matched FedAvg
-backbone in these realized windows.
-\qed
-
-The derivation accounts for the observed numerical equality when within-window
-correction weights are constant. Heterogeneous weights are a different case.
-
-
-\subsection{Within-Stratum Observation Heterogeneity}
-\label{app:f1_mechanism}
-
-The within-stratum heterogeneity construction changes the observation probability to
-$p_i=\operatorname{clip}(\operatorname{sigmoid}(b_{0,b}+\theta_O z_i),.05,.95)$,
-where $z_i\in\{-1,0,1\}$ is the time-index tercile of a training unit within
-its opportunity stratum.  The block intercept $b_{0,b}$ preserves the original
-block mean, .35 or .1925.  It uses no current response value.  Thus the
-intervention introduces within-stratum covariate dependence, not general MNAR
-selection.  At $\theta_O=0$ the copied selection traces coincide with the
-original construction; at $\theta_O=1$ they are regenerated with the same
-opportunity, delivery process, seeds, splits, and target maps.
-
-\begin{table}[!htbp]
-\centering
-\caption{Within-stratum observation-probability diversity. Distinct probabilities are
-counted per opportunity stratum; entries are stratum means. The block marginal
-is preserved by construction.}
-\label{tab:f1_mechanism}
-\footnotesize
-\begin{tabular*}{\columnwidth}{@{\extracolsep{\fill}}lrr}
-\toprule
-Dataset & $\theta_O=0$ & $\theta_O=1$\\
-\midrule
-SensorScope & 1.00 & 2.76\\
-U-Air & 1.00 & 2.83\\
-\bottomrule
-\end{tabular*}
-\end{table}
-
-The estimated-propensity arm keeps the original covariates. The true-$p$ arm
-replaces only the atomic observation propensity, retaining estimated $q$ and
-Design on. Its local inverse weights can vary across time terciles, while a
-stratum-constant factor cancels under local H\'ajek normalization. Block
-observation means stay at .35 or .1925.
-
-\section{P2 Feasibility Diagnostics}
-\label{app:p2_diagnostics}
-
-Theorem~1 concerns the mathematical program.  Separately, the
-experimental audit reconstructs whether logged allocations satisfy the P2
-constraints whenever the necessary state is available.  Table~\ref{tab:app_p2_coverage}
-summarizes the dataset-level certificate coverage.
-
-\begin{table}[!htbp]
-\centering
-\caption{P2 feasibility-certificate coverage in the formal protocol blocks.}
-\label{tab:app_p2_coverage}
-\footnotesize
-\setlength{\tabcolsep}{4pt}
-\begin{tabular*}{\columnwidth}{@{\extracolsep{\fill}}lcccc}
-\toprule
-Dataset & Runs & Mean windows & Range & Status\\
-\midrule
-SensorScope & 180 & 93.85 & 88--98 & Certified \\
-U-Air & 180 & 72.61 & 63--79 & Certified \\
-\bottomrule
-\end{tabular*}
-\end{table}
-
-The solver log contains 778 numerical-inaccuracy warnings on 85 formal runs.
-Table~\ref{tab:app_p2_warning_audit} covers 6438 active P2 windows; the maximum constraint
-residual is $2.686\times10^{-8}<10^{-7}$, which certifies feasibility.
-Where the invocation state is reconstructable, CLARABEL and SCS typically
-match to $10^{-8}$ in $\ell_1$; the worst window differs by $0.0056$ in
-allocation.
-The pre-specified solver-discrepancy rule uses $10^{-4}/10^{-3}$ thresholds.
-Stored P2 outputs were not re-solved.
-
-\begin{table}[!htbp]
-\centering
-\caption{Numerical feasibility of warning-affected P2 allocations.}
-\label{tab:app_p2_warning_audit}
-\footnotesize
-\setlength{\tabcolsep}{5pt}
-\begin{tabular*}{\columnwidth}{@{\extracolsep{\fill}}lc}
-\toprule
-Quantity & Result\\
-\midrule
-Numerical-inaccuracy warnings & 778\\
-Affected formal runs & 85\\
-Evaluated active windows & 6438\\
-Maximum constraint residual & $2.686\times10^{-8}$\\
-Feasibility & Certified\\
-Optimality certificate in stored logs & Unavailable\\
-\bottomrule
-\end{tabular*}
-\end{table}
-
-
-\subsection{Projection-with-Debt Sensitivity}
-\label{app:trained_rule_probe}
-\label{app:kappa_probe}
-
-At tuned $\kappa=1000$, projection-with-debt gains $1.347/.580$ pp on
-SensorScope/U-Air over projection (Holm $\approx10^{-5}$), versus the
-frozen-strength $.0073$ pp SensorScope gain inside the practical band.
-Projection's maximum endpoint discrepancy across 240 runs is
-$\varepsilon_{\mathrm{impl}}=2.42\times10^{-5}$ in $\Delta$ units ($.00121$ pp):
-17\% of the frozen-strength debt effect, $.13\%/.16\%$ of Design/projection
-contrasts. Primal residuals reach $6.66\times10^{-16}$ against tolerance
-$10^{-13}$, while stationarity residuals reach $.667$ against $10^{-12}$.
-Comparator objective gaps exceed $10^{-12}$ in 7 of 200 sampled windows,
-with maximum $9.64\times10^{-12}$. These diagnostics separate numerical
-feasibility and endpoint agreement from exact optimality.
-
-
-
-\section{Supplementary Experimental Comparisons}
-\label{app:additional_context}
-
-Reference-only rows carry $^\dagger$; inference uses deployable methods.
-These station comparisons fix Design on; Table~\ref{tab:main_effectiveness}
-reports both configurations.
+\section{Experimental Protocols and Baseline Specifications}
+\label{app:experimental_protocols}
+Protocols and baseline definitions complement the evaluation settings.
+
+\subsection{City Scanner New York {PM}$_{2.5}$}
+\label{app:cityscanner_nyc}
+
+New York Pilot~1/2 {PM} CSVs (Zenodo 10.5281/zenodo.7961851, {CC BY}
+4.0)~\cite{wang2023cityscanner} exclude Boston, Beirut, and {NO}$_2$.
+Non-finite GPS, time, or {PM}$_{2.5}$, and values outside
+$[0,1000]$\,$\mu$g/m$^3$, are removed. Occupied $500$\,m $\times$ $30$\,min
+cells average calibrated measurements into $Y$; empty slots are absent.
+Cells are clients and GPS supplies $R$. Median cell indices define four
+quadrants without $Y$; $\boldsymbol\mu$ is their test share. Strata are
+$\mathrm{region}{::}\mathrm{block}{::}\mathrm{weekday}$ (at most 32).
+Complete-aligned $O/U$ use $p_{\mathrm{obs}}=.35$ and $S_{\max}=5$.
+
+The 14723 units, 446 cells, and 2776 slots split chronologically into
+$9343/3290/2090$ train/validation/test units (test regions $496/992/148/454$).
+Seeds $32001$--$32010$ share 100 equal-count windows of 1666 training slots.
+Design is on and Gate is unused (Table~\ref{tab:scd_phi_freeze}).
+Table~\ref{tab:cityscanner_real}(a) uses training-standardized errors. One
+seed-32006 window clipped and renormalized tiny negative solver weights.
+
+\subsection{City Scanner Pilot~2 with Measured Observation}
+\label{app:cityscanner_p2_measured_o}
+
+Pilot~2 uses {PM}/{NO}$_2$ CSVs from the same source, excluding Pilot~1,
+Boston, and Beirut, on the same client/$Y$ grid. Union GPS supplies $R$;
+finite {PM}$_{2.5}$ in $[0,1000]$ supplies $O=1$; {NO}$_2$ contributes
+locations only. $U$ stays Complete-aligned ($S_{\max}=5$). The frozen regional
+target, Design-on, and unused Gate keep their roles at different target values.
+
+The 14960 cell-slots, 416 cells, and 2402 slots split into
+$10141/2835/1984$ train/validation/test units: 1931 unobserved ($12.9\%$) and
+13029 labeled, with test-region occupancy $1289/268/144/283$. Seeds
+$33001$--$33010$ use 100 windows from 1441 training slots.
+Table~\ref{tab:cityscanner_real}(b) uses this block's training standardization.
+Section~\ref{subsec:cityscanner_real} gives the rankings and the missed
+improvement criterion.
 
 \subsection{Windowed adaptations of FedAU, ObsUse, and TimeAlign}
 \label{app:adapted_baselines}
@@ -1045,6 +815,10 @@
 trace (seeds \(30001\)--\(30020\)).  Existing tables already report
 these adaptations.
 
+
+
+\subsection{Selection Mechanisms and Information Requirements}
+\label{app:mechanism_comparison}
 \begin{table*}[t]
 \centering
 \caption{Selection mechanisms and their information requirements.}
@@ -1066,60 +840,11 @@
 \end{tabular}
 \end{table*}
 
-\paragraph{Under-served-block validation.}
-\label{app:underserved_block}
-On validation only, aggregate target and opportunity mass to four UTC blocks
-and freeze $g^\star=\arg\max_b(\mu_b^{\mathrm{blk}}-
-\pi_b^{\mathrm{opp},4})$: block 2 on SensorScope and 3 on U-Air, with gaps
-$.114/.172$.  The required improvement against both FedAU and ObsUse is
-$-.5\%$.  Observed $+.05\%/+.15\%$ and $-.44\%/-.27\%$ miss that criterion
-while meeting no-harm (Supplementary Table~\ref{tab:underserved_block}).  
-
-\begin{table}[!htbp]
-\centering
-\caption{Validation RMSE in under-served UTC blocks.
-Relative changes (\%) over ten paired validation seeds versus
-FedAU-Window/ObsUse-Window; negative favors RAVEN.
-Design is on for SensorScope and off for U-Air.
-Improvement/no-harm thresholds are $\le-0.5\%$/$\le+0.5\%$.}
-\label{tab:underserved_block}
-\setlength{\tabcolsep}{3.5pt}
-\begin{tabular}{lcccc}
-\toprule
-Dataset & $g^{\star}$ (UTC) & vs FedAU & vs ObsUse & Win / no-harm\\
-\midrule
-SensorScope & 2 (12--18) & $+0.05\%$ & $+0.15\%$ & No / Yes\\
-U-Air & 3 (18--24) & $-0.44\%$ & $-0.27\%$ & No / Yes\\
-\bottomrule
-\end{tabular}
-\end{table}
-
-
-
-\begin{figure}[t]
-\centering
-\includegraphics[width=\columnwidth]{fig3_e3_structural_mismatch.pdf}
-\caption{Structural mismatch under the frozen station protocols.
-Mean $\pm$ sample SD over 20 paired seeds; lower is better.
-(a)(b)~SensorScope group/client--stratum mismatch; (c)(d)~U-Air counterparts.
-RAVEN-Design is on in both datasets; some active sets differ from
-Table~\ref{tab:app_e3_uair}, precluding a matched-support comparison.}
-\label{fig:e3_structural}
-\end{figure}
-
-\begin{figure}[t]
-\centering
-\includegraphics[width=\columnwidth]{fig4_e3_prediction_risk.pdf}
-\caption{Prediction error under the frozen station protocols.
-Mean $\pm$ sample SD over 20 paired seeds; lower is better.
-(a)(b)~SensorScope target/Tail RMSE; (c)(d)~U-Air counterparts.
-RAVEN-Design is on; support identities follow Fig.~\ref{fig:e3_structural}.}
-\label{fig:e3_prediction}
-\end{figure}
-
-
-
-
+\section{Additional Results for Deployment-Target Alignment}
+\label{app:rq1_results}
+
+\label{app:risk_semantic_evidence}
+These supplementary results address deployment alignment in RQ1.
 
 \subsection{Full Method Context on the Comparable Datasets}
 \label{app:e3_full_context}
@@ -1185,6 +910,70 @@
 have prediction-only entries.  RAVEN-SimOracle supplies a controlled oracle
 reference.  NSW-Traffic uses its own data-processing and target specification
 in the four-region comparison below.
+
+\begin{figure}[!htbp]
+\centering
+\includegraphics[width=\columnwidth]{fig3_e3_structural_mismatch.pdf}
+\caption{Structural mismatch under the frozen station protocols.
+Mean $\pm$ sample SD over 20 paired seeds; lower is better.
+(a)(b)~SensorScope group/client--stratum mismatch; (c)(d)~U-Air counterparts.
+RAVEN-Design is on in both datasets; some active sets differ from
+Table~\ref{tab:app_e3_uair}, precluding a matched-support comparison.}
+\label{fig:e3_structural}
+\end{figure}
+
+\begin{figure}[!htbp]
+\centering
+\includegraphics[width=\columnwidth]{fig4_e3_prediction_risk.pdf}
+\caption{Prediction error under the frozen station protocols.
+Mean $\pm$ sample SD over 20 paired seeds; lower is better.
+(a)(b)~SensorScope target/Tail RMSE; (c)(d)~U-Air counterparts.
+RAVEN-Design is on; support identities follow Fig.~\ref{fig:e3_structural}.}
+\label{fig:e3_prediction}
+\end{figure}
+
+\subsection{Four-Block Per-Group RMSE}
+\label{app:block_rmse}
+
+Table~\ref{tab:app_block_rmse} reports the four UTC-block scores whose
+maximum is $\mathrm{WorstGroupRMSE}$ in
+Table~\ref{tab:main_effectiveness}.  The blocks are the public
+deployment groups $00$--$06$, $06$--$12$, $12$--$18$, and $18$--$24$~UTC.
+The table decomposes the existing prediction endpoint by group.  On both datasets the
+worst block is $g=2$ ($12$--$18$~UTC).  The pre-registered under-served
+block $g^{\star}$ coincides with that worst block on SensorScope and
+does not on U-Air.
+
+\begin{table*}[t]
+\centering
+\caption{Per-group RMSE across four UTC blocks.
+Mean $\pm$ SD over 20 paired seeds; lower is better.
+WG denotes $\max_g\mathrm{RMSE}_g$. Both fixed Design settings are shown.}
+\label{tab:app_block_rmse}
+\footnotesize
+\setlength{\tabcolsep}{4pt}
+\begin{tabular*}{\textwidth}{@{\extracolsep{\fill}}llccccc}
+\toprule
+Dataset & Method & $g{=}0$ & $g{=}1$ & $g{=}2$ & $g{=}3$ & WG\\
+\midrule
+\multirow{6}{*}{SS}
+& FedAvg-Window & $7.4912{\pm}0.0464$ & $7.5873{\pm}0.0444$ & $8.6716{\pm}0.0471$ & $8.2084{\pm}0.0460$ & $8.6716{\pm}0.0471$\\
+& TwoStage-H\'ajek & $7.4831{\pm}0.0549$ & $7.5795{\pm}0.0523$ & $8.6633{\pm}0.0556$ & $8.2004{\pm}0.0549$ & $8.6633{\pm}0.0556$\\
+& FedAU-Window & $7.4887{\pm}0.0512$ & $7.5848{\pm}0.0491$ & $8.6691{\pm}0.0522$ & $8.2059{\pm}0.0510$ & $8.6691{\pm}0.0522$\\
+& ObsUse-Window & $7.4815{\pm}0.0517$ & $7.5780{\pm}0.0496$ & $8.6618{\pm}0.0528$ & $8.1988{\pm}0.0516$ & $8.6618{\pm}0.0528$\\
+& RAVEN-Design & $7.4903{\pm}0.0479$ & $7.5864{\pm}0.0457$ & $8.6707{\pm}0.0486$ & $8.2075{\pm}0.0476$ & $8.6707{\pm}0.0486$\\
+& RAVEN-NoDesign & $7.4907{\pm}0.0474$ & $7.5868{\pm}0.0452$ & $8.6711{\pm}0.0481$ & $8.2079{\pm}0.0470$ & $8.6711{\pm}0.0481$\\
+\midrule
+\multirow{6}{*}{UA}
+& FedAvg-Window & $1.1015{\pm}0.0546$ & $1.1144{\pm}0.0578$ & $1.1690{\pm}0.0692$ & $1.0721{\pm}0.0601$ & $1.1690{\pm}0.0692$\\
+& TwoStage-H\'ajek & $1.2009{\pm}0.0623$ & $1.2194{\pm}0.0649$ & $1.2907{\pm}0.0753$ & $1.1800{\pm}0.0670$ & $1.2907{\pm}0.0753$\\
+& FedAU-Window & $1.1023{\pm}0.0545$ & $1.1153{\pm}0.0576$ & $1.1701{\pm}0.0689$ & $1.0729{\pm}0.0598$ & $1.1701{\pm}0.0689$\\
+& ObsUse-Window & $1.1016{\pm}0.0544$ & $1.1145{\pm}0.0576$ & $1.1692{\pm}0.0689$ & $1.0721{\pm}0.0598$ & $1.1692{\pm}0.0689$\\
+& RAVEN-Design & $1.1779{\pm}0.0583$ & $1.1953{\pm}0.0611$ & $1.2630{\pm}0.0716$ & $1.1552{\pm}0.0633$ & $1.2630{\pm}0.0716$\\
+& RAVEN-NoDesign & $1.1025{\pm}0.0578$ & $1.1155{\pm}0.0611$ & $1.1703{\pm}0.0734$ & $1.0732{\pm}0.0636$ & $1.1703{\pm}0.0734$\\
+\bottomrule
+\end{tabular*}
+\end{table*}
 
 \subsection{NSW-Traffic Four-Region Protocol Ranking}
 \label{app:traffic_four_region}
@@ -1236,89 +1025,137 @@
 \end{minipage}
 \end{table}
 
-\subsection{Four-Block Per-Group RMSE}
-\label{app:block_rmse}
-
-Table~\ref{tab:app_block_rmse} reports the four UTC-block scores whose
-maximum is $\mathrm{WorstGroupRMSE}$ in
-Table~\ref{tab:main_effectiveness}.  The blocks are the public
-deployment groups $00$--$06$, $06$--$12$, $12$--$18$, and $18$--$24$~UTC.
-The table decomposes the existing prediction endpoint by group.  On both datasets the
-worst block is $g=2$ ($12$--$18$~UTC).  The pre-registered under-served
-block $g^{\star}$ coincides with that worst block on SensorScope and
-does not on U-Air.
+\subsection{Balanced No-Harm Control}
+\label{app:e1_balanced}
+
+Table~\ref{tab:app_e1_balanced} reports all five paired methods under the balanced
+control.  The selected TimeAlign reference has mean
+$\mathrm{RMSE}_\mu=7.7108$, while RAVEN-MCS obtains $7.7154$.  RAVEN's
+pre-specified mean relative degradation is $0.0599\%$; the one-sided 95\%
+upper bound is $0.134\%$, below the pre-specified $3\%$ no-harm margin.
+The balanced experiment evaluates this criterion under aligned selection.
+
+\begin{table}[!htbp]
+\centering
+\caption{Balanced control over the five pre-specified paired seeds.}
+\label{tab:app_e1_balanced}
+\footnotesize
+\setlength{\tabcolsep}{5pt}
+\begin{tabular*}{\columnwidth}{@{\extracolsep{\fill}}lcc}
+\toprule
+Method & $\mathrm{RMSE}_\mu$ & Seeds\\
+\midrule
+FedAvg-Window & $7.7220\pm0.0289$ & 5 \\
+FedAsync-Window & $7.7222\pm0.0287$ & 5 \\
+TimeAlign-Agg & $7.7108\pm0.0272$ & 5 \\
+TwoStage-H\'ajek & $7.7262\pm0.0291$ & 5 \\
+RAVEN-MCS & $7.7154\pm0.0337$ & 5 \\
+\bottomrule
+\end{tabular*}
+\end{table}
+
+\subsection{Complete Risk Non-Interchangeability Statistics}
+\label{app:e2_full_stats}
+
+Table~\ref{tab:app_e2_daligned} gives the complete method-level risk-interchangeability summary for
+the pre-specified difference-of-differences
+$D_{\mathrm{aligned}}=\Delta\mathrm{RMSE}_{\mu}
+-\Delta\mathrm{RMSE}_{\rho}$.  The negative mean is stable across all five
+methods, and 17--18 of 20 paired seeds are negative.  This supports the
+risk-semantic premise that arrival-weighted and deployment-target-weighted
+views react differently to the same structured selection shift.
+
+\begin{table}[!htbp]
+\centering
+\caption{Complete-aligned risk non-interchangeability statistics.
+CI denotes the 95\% interval; $p$ is the paired Wilcoxon test of
+$D_{\mathrm{aligned}}$ against zero.}
+\label{tab:app_e2_daligned}
+\scriptsize
+\setlength{\tabcolsep}{2.5pt}
+\begin{tabular*}{\columnwidth}{@{\extracolsep{\fill}}lcccc}
+\toprule
+Method & $D_{\mathrm{aligned}}$ & 95\% CI & Neg. seeds & $p$\\
+\midrule
+FedAsync-Window & $-0.02115$ & $[-0.03158,-0.01073]$ & 18/20 & $4.83e-04$ \\
+FedAvg-Window & $-0.02115$ & $[-0.03158,-0.01071]$ & 18/20 & $4.83e-04$ \\
+TimeAlign-Agg & $-0.02137$ & $[-0.03185,-0.01090]$ & 17/20 & $4.83e-04$ \\
+RAVEN-MCS & $-0.02088$ & $[-0.03132,-0.01043]$ & 17/20 & $5.86e-04$ \\
+TwoStage-H\'ajek & $-0.02120$ & $[-0.03169,-0.01072]$ & 17/20 & $5.86e-04$ \\
+\bottomrule
+\end{tabular*}
+\end{table}
+
+
+\subsection{Response to Each Selection Layer}
+\label{app:e2_layer_matrix}
+
+The six scenarios use five methods and 20 paired seeds each (600 existing
+runs).  Table~\ref{tab:e2_layer_matrix} summarizes the final numerical-tie-aware
+analysis.  Each range spans the five method-specific mean changes from balanced;
+the significant counts retain the existing within-method, within-metric Holm
+families over the five non-balanced scenarios.  Signed arrival--target gaps distinguish risk direction from absolute mismatch.
 
 \begin{table*}[t]
 \centering
-\caption{Per-group RMSE across four UTC blocks.
-Mean $\pm$ SD over 20 paired seeds; lower is better.
-WG denotes $\max_g\mathrm{RMSE}_g$. Both fixed Design settings are shown.}
-\label{tab:app_block_rmse}
+\caption{Risk responses to controlled selection layers on NSW-Traffic.
+Changes use the original standardized RMSE units; $\times10^{-3}$ applies to
+both range columns. Counts are Holm-significant methods out of five.}
+\label{tab:e2_layer_matrix}
 \footnotesize
-\setlength{\tabcolsep}{4pt}
-\begin{tabular*}{\textwidth}{@{\extracolsep{\fill}}llccccc}
-\toprule
-Dataset & Method & $g{=}0$ & $g{=}1$ & $g{=}2$ & $g{=}3$ & WG\\
-\midrule
-\multirow{6}{*}{SS}
-& FedAvg-Window & $7.4912{\pm}0.0464$ & $7.5873{\pm}0.0444$ & $8.6716{\pm}0.0471$ & $8.2084{\pm}0.0460$ & $8.6716{\pm}0.0471$\\
-& TwoStage-H\'ajek & $7.4831{\pm}0.0549$ & $7.5795{\pm}0.0523$ & $8.6633{\pm}0.0556$ & $8.2004{\pm}0.0549$ & $8.6633{\pm}0.0556$\\
-& FedAU-Window & $7.4887{\pm}0.0512$ & $7.5848{\pm}0.0491$ & $8.6691{\pm}0.0522$ & $8.2059{\pm}0.0510$ & $8.6691{\pm}0.0522$\\
-& ObsUse-Window & $7.4815{\pm}0.0517$ & $7.5780{\pm}0.0496$ & $8.6618{\pm}0.0528$ & $8.1988{\pm}0.0516$ & $8.6618{\pm}0.0528$\\
-& RAVEN-Design & $7.4903{\pm}0.0479$ & $7.5864{\pm}0.0457$ & $8.6707{\pm}0.0486$ & $8.2075{\pm}0.0476$ & $8.6707{\pm}0.0486$\\
-& RAVEN-NoDesign & $7.4907{\pm}0.0474$ & $7.5868{\pm}0.0452$ & $8.6711{\pm}0.0481$ & $8.2079{\pm}0.0470$ & $8.6711{\pm}0.0481$\\
-\midrule
-\multirow{6}{*}{UA}
-& FedAvg-Window & $1.1015{\pm}0.0546$ & $1.1144{\pm}0.0578$ & $1.1690{\pm}0.0692$ & $1.0721{\pm}0.0601$ & $1.1690{\pm}0.0692$\\
-& TwoStage-H\'ajek & $1.2009{\pm}0.0623$ & $1.2194{\pm}0.0649$ & $1.2907{\pm}0.0753$ & $1.1800{\pm}0.0670$ & $1.2907{\pm}0.0753$\\
-& FedAU-Window & $1.1023{\pm}0.0545$ & $1.1153{\pm}0.0576$ & $1.1701{\pm}0.0689$ & $1.0729{\pm}0.0598$ & $1.1701{\pm}0.0689$\\
-& ObsUse-Window & $1.1016{\pm}0.0544$ & $1.1145{\pm}0.0576$ & $1.1692{\pm}0.0689$ & $1.0721{\pm}0.0598$ & $1.1692{\pm}0.0689$\\
-& RAVEN-Design & $1.1779{\pm}0.0583$ & $1.1953{\pm}0.0611$ & $1.2630{\pm}0.0716$ & $1.1552{\pm}0.0633$ & $1.2630{\pm}0.0716$\\
-& RAVEN-NoDesign & $1.1025{\pm}0.0578$ & $1.1155{\pm}0.0611$ & $1.1703{\pm}0.0734$ & $1.0732{\pm}0.0636$ & $1.1703{\pm}0.0734$\\
+\begin{tabular*}{\textwidth}{@{\extracolsep{\fill}}lrrrr}
+\toprule
+Scenario & Target change range & Arrival change range & Target significant & Arrival significant\\
+\midrule
+Balanced & 0 & 0 & -- & --\\
+Opportunity only & $[0.057,0.114]$ & $[5.699,5.990]$ & 0/5 & 0/5\\
+Observation only & $[0.108,0.157]$ & $[11.018,11.145]$ & 0/5 & 5/5\\
+Usable update only & $[0.193,0.245]$ & $[5.472,5.607]$ & 0/5 & 0/5\\
+Complete aligned & $[0.757,0.820]$ & $[21.660,22.130]$ & 2/5 & 5/5\\
+Complete counteracting & $[0.030,0.059]$ & $[12.447,12.639]$ & 0/5 & 0/5\\
 \bottomrule
 \end{tabular*}
 \end{table*}
 
-\subsection{Runtime Diagnostic from Existing Risk-Semantic Logs}
-\label{app:runtime}
-
-In Table~\ref{tab:app_runtime}, the ``all scenarios'' column aggregates six
-risk-semantic scenarios and 20 seeds (120 runs per method); the Complete-aligned column
-contains 20 runs per method.
+\subsection{Under-Served-Block Validation}
+\label{app:underserved_block}
+On validation only, aggregate target and opportunity mass to four UTC blocks
+and freeze $g^\star=\arg\max_b(\mu_b^{\mathrm{blk}}-
+\pi_b^{\mathrm{opp},4})$: block 2 on SensorScope and 3 on U-Air, with gaps
+$.114/.172$.  The required improvement against both FedAU and ObsUse is
+$-.5\%$.  Observed $+.05\%/+.15\%$ and $-.44\%/-.27\%$ miss that criterion
+while meeting no-harm (Supplementary Table~\ref{tab:underserved_block}).  
 
 \begin{table}[!htbp]
 \centering
-\caption{Runtime on the risk-semantic workloads.
-Wall-clock seconds per run, mean $\pm$ SD.}
-\label{tab:app_runtime}
-\footnotesize
+\caption{Validation RMSE in under-served UTC blocks.
+Relative changes (\%) over ten paired validation seeds versus
+FedAU-Window/ObsUse-Window; negative favors RAVEN.
+Design is on for SensorScope and off for U-Air.
+Improvement/no-harm thresholds are $\le-0.5\%$/$\le+0.5\%$.}
+\label{tab:underserved_block}
 \setlength{\tabcolsep}{3.5pt}
-\begin{tabular*}{\columnwidth}{@{\extracolsep{\fill}}lcc}
-\toprule
-Method & All scenarios & Complete-aligned\\
-\midrule
-FedAvg-Window & $71.426\pm5.105$ & $69.278\pm2.287$ \\
-FedAsync-Window & $71.418\pm4.863$ & $70.186\pm3.531$ \\
-TimeAlign-Agg & $71.244\pm5.225$ & $69.217\pm2.554$ \\
-TwoStage-H\'ajek & $71.781\pm8.017$ & $69.829\pm3.670$ \\
-RAVEN-MCS & $72.669\pm4.243$ & $71.070\pm1.292$ \\
-\bottomrule
-\end{tabular*}
+\begin{tabular}{lcccc}
+\toprule
+Dataset & $g^{\star}$ (UTC) & vs FedAU & vs ObsUse & Win / no-harm\\
+\midrule
+SensorScope & 2 (12--18) & $+0.05\%$ & $+0.15\%$ & No / Yes\\
+U-Air & 3 (18--24) & $-0.44\%$ & $-0.27\%$ & No / Yes\\
+\bottomrule
+\end{tabular}
 \end{table}
 
-The runtime rows in Table~\ref{tab:app_runtime} summarize completed runs on the
-specified workload sizes and selection scenarios.
-
-\subsection{Design-Induced Support Changes}
-\label{app:design_provenance}
-
-The end-to-end Design comparison in Section~\ref{subsec:rq1_alignment} exhibits an endpoint
-trade-off on U-Air. Across 774 paired windows, full RAVEN and w/o-Design share
-opportunity, observation, usable-update, and registration events. Removing the
-Design ratio changes positive-mass P2 support, so the end-to-end contrast
-includes support changes as well as weight changes.
-
-\section{Intermittent Protocol Opportunity (INT-R)}
+
+
+
+
+
+
+
+
+
+
+\subsection{Intermittent Opportunity Protocol}
 \label{app:int_r}
 
 Table~\ref{tab:main_effectiveness} uses always-on Complete-aligned opportunity.
@@ -1426,7 +1263,420 @@
 Table~\ref{tab:main_effectiveness} with intermittent protocol opportunities, isolating sensitivity to
 the opportunity process on the same sensing data.
 
-\section{Support and Stabilization Conditions}
+
+\section{Mechanism Analysis and Numerical Calibration Details}
+\label{app:rq2_details}
+Mechanism conditions and numerical calibration details support RQ2.
+
+\subsection{Local-H\'ajek Weight Cancellation}
+\label{app:local_hajek}
+
+The equality between Local-Hajek and FedAvg in the formal SensorScope/U-Air
+blocks is protocol-specific and should not be interpreted as a general
+equivalence.  Table~\ref{tab:app_local_hajek} covers
+9666 effective client-windows: 6070 on SensorScope and
+3596 on U-Air.  In every audited effective client-window, the realized
+within-client correction-weight range is 0.
+
+\begin{table}[!t]
+\centering
+\caption{Within-client weight constancy.}
+\label{tab:app_local_hajek}
+\footnotesize
+\setlength{\tabcolsep}{5pt}
+\begin{tabular*}{\columnwidth}{@{\extracolsep{\fill}}lcc}
+\toprule
+Dataset & Effective client-windows & Weight range\\
+\midrule
+SensorScope & 6070 & $0$\\
+U-Air & 3596 & $0$\\
+\midrule
+Total & 9666 & $0$\\
+\bottomrule
+\end{tabular*}
+\end{table}
+
+The collapse follows directly from the normalized local objective.  Let
+$\mathcal I_{k,r}^{+}$ be the records retained by an effective client-window
+and let $N_{k,r}^{+}=|\mathcal I_{k,r}^{+}|$.  If the realized first-stage
+weight is constant over that set, i.e.,
+$a_{k,r,i}=a_{k,r}>0$ for all $i\in\mathcal I_{k,r}^{+}$, then
+\begin{equation}
+ \overline a_{k,r,i}
+ =
+ \frac{a_{k,r}}
+ {N_{k,r}^{+}a_{k,r}}
+ =
+ \frac{1}{N_{k,r}^{+}}.
+ \label{eq:app_local_hajek_uniform}
+\end{equation}
+Consequently,
+\begin{equation}
+ \widehat F^H_{k,r}(\theta)
+ =
+ \frac{1}{N_{k,r}^{+}}
+ \sum_{i\in\mathcal I_{k,r}^{+}}
+ \frac{1}{2}
+ \left(
+ f_\theta(i;C_i^{\mathrm{dep}})-Z_{k,r,i}
+ \right)^2,
+ \label{eq:app_local_hajek_collapse}
+\end{equation}
+which is exactly the uniform local objective used by the matched FedAvg
+backbone in these realized windows.
+\qed
+
+The derivation accounts for the observed numerical equality when within-window
+correction weights are constant. Heterogeneous weights are a different case.
+
+
+\subsection{Within-Stratum Observation Heterogeneity}
+\label{app:f1_mechanism}
+
+The within-stratum heterogeneity construction changes the observation probability to
+$p_i=\operatorname{clip}(\operatorname{sigmoid}(b_{0,b}+\theta_O z_i),.05,.95)$,
+where $z_i\in\{-1,0,1\}$ is the time-index tercile of a training unit within
+its opportunity stratum.  The block intercept $b_{0,b}$ preserves the original
+block mean, .35 or .1925.  It uses no current response value.  Thus the
+intervention introduces within-stratum covariate dependence, not general MNAR
+selection.  At $\theta_O=0$ the copied selection traces coincide with the
+original construction; at $\theta_O=1$ they are regenerated with the same
+opportunity, delivery process, seeds, splits, and target maps.
+
+\begin{table}[!t]
+\centering
+\caption{Within-stratum observation-probability diversity. Distinct probabilities are
+counted per opportunity stratum; entries are stratum means. The block marginal
+is preserved by construction.}
+\label{tab:f1_mechanism}
+\footnotesize
+\begin{tabular*}{\columnwidth}{@{\extracolsep{\fill}}lrr}
+\toprule
+Dataset & $\theta_O=0$ & $\theta_O=1$\\
+\midrule
+SensorScope & 1.00 & 2.76\\
+U-Air & 1.00 & 2.83\\
+\bottomrule
+\end{tabular*}
+\end{table}
+
+The estimated-propensity arm keeps the original covariates. The true-$p$ arm
+replaces only the atomic observation propensity, retaining estimated $q$ and
+Design on. Its local inverse weights can vary across time terciles, while a
+stratum-constant factor cancels under local H\'ajek normalization. Block
+observation means stay at .35 or .1925.
+
+\subsection{Design-Induced Support Changes}
+\label{app:design_provenance}
+
+The end-to-end Design comparison in Section~\ref{subsec:rq1_alignment} exhibits an endpoint
+trade-off on U-Air. Across 774 paired windows, full RAVEN and w/o-Design share
+opportunity, observation, usable-update, and registration events. Removing the
+Design ratio changes positive-mass P2 support, so the end-to-end contrast
+includes support changes as well as weight changes.
+
+
+\FloatBarrier
+\subsection{Numerical Feasibility of P2}
+\label{app:p2_diagnostics}
+
+Theorem~1 concerns the mathematical program.  Separately, the
+experimental audit reconstructs whether logged allocations satisfy the P2
+constraints whenever the necessary state is available.  Table~\ref{tab:app_p2_coverage}
+summarizes the dataset-level certificate coverage.
+
+\begin{table}[!t]
+\centering
+\caption{P2 feasibility-certificate coverage in the formal protocol blocks.}
+\label{tab:app_p2_coverage}
+\footnotesize
+\setlength{\tabcolsep}{4pt}
+\begin{tabular*}{\columnwidth}{@{\extracolsep{\fill}}lcccc}
+\toprule
+Dataset & Runs & Mean windows & Range & Status\\
+\midrule
+SensorScope & 180 & 93.85 & 88--98 & Certified \\
+U-Air & 180 & 72.61 & 63--79 & Certified \\
+\bottomrule
+\end{tabular*}
+\end{table}
+
+The solver log contains 778 numerical-inaccuracy warnings on 85 formal runs.
+Table~\ref{tab:app_p2_warning_audit} covers 6438 active P2 windows; the maximum constraint
+residual is $2.686\times10^{-8}<10^{-7}$, which certifies feasibility.
+Where the invocation state is reconstructable, CLARABEL and SCS typically
+match to $10^{-8}$ in $\ell_1$; the worst window differs by $0.0056$ in
+allocation.
+The pre-specified solver-discrepancy rule uses $10^{-4}/10^{-3}$ thresholds.
+Stored P2 outputs were not re-solved.
+
+\begin{table}[!t]
+\centering
+\caption{Numerical feasibility of warning-affected P2 allocations.}
+\label{tab:app_p2_warning_audit}
+\footnotesize
+\setlength{\tabcolsep}{5pt}
+\begin{tabular*}{\columnwidth}{@{\extracolsep{\fill}}lc}
+\toprule
+Quantity & Result\\
+\midrule
+Numerical-inaccuracy warnings & 778\\
+Affected formal runs & 85\\
+Evaluated active windows & 6438\\
+Maximum constraint residual & $2.686\times10^{-8}$\\
+Feasibility & Certified\\
+Optimality certificate in stored logs & Unavailable\\
+\bottomrule
+\end{tabular*}
+\end{table}
+
+
+\subsection{Projection-with-Debt Sensitivity}
+\label{app:trained_rule_probe}
+\label{app:kappa_probe}
+
+At tuned $\kappa=1000$, projection-with-debt gains $1.347/.580$ pp on
+SensorScope/U-Air over projection (Holm $\approx10^{-5}$), versus the
+frozen-strength $.0073$ pp SensorScope gain inside the practical band.
+Projection's maximum endpoint discrepancy across 240 runs is
+$\varepsilon_{\mathrm{impl}}=2.42\times10^{-5}$ in $\Delta$ units ($.00121$ pp):
+17\% of the frozen-strength debt effect, $.13\%/.16\%$ of Design/projection
+contrasts. Primal residuals reach $6.66\times10^{-16}$ against tolerance
+$10^{-13}$, while stationarity residuals reach $.667$ against $10^{-12}$.
+Comparator objective gaps exceed $10^{-12}$ in 7 of 200 sampled windows,
+with maximum $9.64\times10^{-12}$. These diagnostics separate numerical
+feasibility and endpoint agreement from exact optimality.
+
+
+
+\subsection{Runtime under Risk-Semantic Workloads}
+\label{app:runtime}
+
+In Table~\ref{tab:app_runtime}, the ``all scenarios'' column aggregates six
+risk-semantic scenarios and 20 seeds (120 runs per method); the Complete-aligned column
+contains 20 runs per method.
+
+\begin{table}[!t]
+\centering
+\caption{Runtime on the risk-semantic workloads.
+Wall-clock seconds per run, mean $\pm$ SD.}
+\label{tab:app_runtime}
+\footnotesize
+\setlength{\tabcolsep}{3.5pt}
+\begin{tabular*}{\columnwidth}{@{\extracolsep{\fill}}lcc}
+\toprule
+Method & All scenarios & Complete-aligned\\
+\midrule
+FedAvg-Window & $71.426\pm5.105$ & $69.278\pm2.287$ \\
+FedAsync-Window & $71.418\pm4.863$ & $70.186\pm3.531$ \\
+TimeAlign-Agg & $71.244\pm5.225$ & $69.217\pm2.554$ \\
+TwoStage-H\'ajek & $71.781\pm8.017$ & $69.829\pm3.670$ \\
+RAVEN-MCS & $72.669\pm4.243$ & $71.070\pm1.292$ \\
+\bottomrule
+\end{tabular*}
+\end{table}
+
+The runtime rows in Table~\ref{tab:app_runtime} summarize completed runs on the
+specified workload sizes and selection scenarios.
+
+\section{Target Support, Target Maps, and Reference Sensitivity}
+\label{app:rq3_details}
+Support geometry, target maps, and reference sensitivity address RQ3.
+
+\subsection{Instantaneous Arrival-Support Geometry}
+\label{app:arrival_support}
+
+The rows use the formal complete-aligned logs for NSW-Traffic, SensorScope,
+and U-Air, seeds $30001$--$30020$. A nonempty close keeps $U=1$ attempts;
+one client keeps the largest downloaded version. That attempt is one column
+of $M^{\mathrm{arr}}$: the frozen UTC block of its observed units on Traffic,
+and the spatial-and-block group named by its opportunity stratum on
+SensorScope and U-Air. Empty closes are dropped ($5382$ remain). U-Air
+contributes $1515$ closes; the $1402$ Design-on active windows in the main
+text are a different set.
+
+Positive target mass splits into missing mass ($n_g=0$), narrow-range mass
+($n_g>0$, $W_g<.01$), and adjustable mass ($W_g\ge.01$), with
+$\overline\alpha=\min\{1,\max\{.5,1/K\}\}$ and $\overline E=\min\{3,K\}$.
+For $K\le 3$ the feasible set is uniform, so adjustable mass is $0$.
+$d_{\mathrm{simplex}}$, $d_{\mathrm{cap}}$, $d_{\mathrm{ESS}}$, and
+$d_{\mathcal C}$ minimize $\|M^{\mathrm{arr}}\alpha-\mu\|_1$ on the simplex,
+under the cap, under $\sum_k\alpha_k^2\le 1/\overline E$, and under both.
+These are $\ell_1$ distances, separate from the squared $\ell_2$ gap
+$d_r^{\mathrm{feas}}$ in Appendix~\ref{app:supp_calibration_geometry}.
+
+\begin{proposition}[Arrival-support simplex distance]
+\label{prop:arrival_simplex}
+If every column of $M$ is a basis vector, $\mu_g\ge 0$, and $\sum_g\mu_g=1$,
+then on the simplex
+$\min_{\alpha}\|M\alpha-\mu\|_1=2\mu_{\mathrm{miss}}$,
+where $\mu_{\mathrm{miss}}$ is the target mass on groups with no column.
+\end{proposition}
+
+\begin{proof}
+Absent groups contribute $\mu_{\mathrm{miss}}$, and present groups must carry
+total mass $1$, so they sit at least $\mu_{\mathrm{miss}}$ above their combined
+target. Matching each present target and placing the residual on one present
+client attains the bound. The same value under the cap and the ESS bound is
+measured in Table~\ref{tab:arrival_support}; it is not claimed for arbitrary caps.
+\end{proof}
+
+The four minima agree through $10^{-11}$, and all $2966$ closes with
+$K\le 3$ have adjustable mass $0$. Table~\ref{tab:arrival_support} gives the
+common distance. Seeds are averaged inside a stratum, then averaged with
+equal weight. For $K>3$, adjustable mass has descriptive interval
+$[2.220\%,2.283\%]$ on SensorScope and $[2.938\%,3.020\%]$ on U-Air
+($10{,}000$ resamples, seed $20261019$).
+
+\begin{table}[!htbp]
+\centering
+\caption{Arrival-log geometry. Masses are percentages of positive target
+mass. L1 is the shared minimum $\ell_1$ distance on $M^{\mathrm{arr}}$.}
+\label{tab:arrival_support}
+\scriptsize
+\setlength{\tabcolsep}{2.5pt}
+\begin{tabular}{llrrrrr}
+\toprule
+Dataset & $K$ & Windows & Miss. & Narrow & Adj. & L1\\
+\midrule
+Traffic & $\le 3$ & 294 & 75.000 & 25.000 & 0 & 1.5000\\
+Traffic & $>3$ & 1696 & 75.000 & 25.000 & 0 & 1.5000\\
+SensorScope & $\le 3$ & 1475 & 98.916 & 1.084 & 0 & 1.9783\\
+SensorScope & $>3$ & 402 & 97.748 & 0 & 2.252 & 1.9550\\
+U-Air & $\le 3$ & 1197 & 98.551 & 1.449 & 0 & 1.9710\\
+U-Air & $>3$ & 318 & 97.024 & 0 & 2.976 & 1.9405\\
+\bottomrule
+\end{tabular}
+\end{table}
+
+Every Traffic close covers one UTC block, so $75\%$ of the target is absent,
+the present block has range zero, and the minimum distance is $1.5$. For
+$K>3$, SensorScope and U-Air leave $2.252\%$ and $2.976\%$ adjustable. The cap
+and ESS bound do not raise that one-close minimum. Cross-window mismatch and
+RMSE are separate questions.
+
+Under arrival-time consumption, an attempt still inside the staleness bound
+at its arrival close is consumed there. On these three traces the hold set
+matches the arrival set in every nonempty window, so the adjustable-mass
+difference is zero. Retaining an update past that close is a different rule,
+and this comparison did not train it.
+
+\subsection{City Scanner Target Maps and Zero-Mass Handling}
+\label{app:cityscanner_sixarm}
+
+The six-arm visit-occupancy comparison uses controlled $O/U$ and ten traces
+with model seeds $s,s+100000,s+200000$: 150 newly trained and 30 reused runs.
+Maps use public locations, calendar strata and test-region shares before
+training, without responses/errors. Table~\ref{tab:cityscanner_sixarm}
+summarizes ten within-trace model-seed means.
+
+\begin{table}[!htbp]
+\centering
+\caption{Client--stratum gaps across City Scanner target maps.
+Mean $\pm$ SD over ten trace means, each using three model seeds.
+Targets are arm-specific, so gaps do not rank common-target alignment.}
+\label{tab:cityscanner_sixarm_cs}
+\footnotesize
+\begin{tabular}{lr}
+\toprule
+Method / target map & $\Delta_{c\text{-}s}$\\
+\midrule
+FedAvg / count & $0.8123{\pm}0.0191$\\
+RAVEN-NoDesign & $0.7880{\pm}0.0254$\\
+RAVEN-control & $0.5676{\pm}0.0311$\\
+RAVEN-floor & $0.7892{\pm}0.0235$\\
+RAVEN-M1$\mu$ & $1.4060{\pm}0.0168$\\
+RAVEN-M2$\mu$ & $1.4348{\pm}0.0147$\\
+\bottomrule
+\end{tabular}
+\end{table}
+
+Count-weighted FedAvg and RAVEN-NoDesign omit the target ratio.
+RAVEN-control has 1164 keys, 812 zero; RAVEN-floor replaces zeros with
+$4.78469\times10^{-4}$, the smallest positive mass, and renormalizes,
+changing group marginals. RAVEN-M1$\mu$/RAVEN-M2$\mu$ use ACS population/NYC~311
+shapes on these keys, rescaled within region to the common target (70/33 zeros).
+All maps cover the 959 risk-set keys.
+
+For $d_t=R_{\mathrm{ctrl},t}/R_{\mathrm{floor},t}-1$ on within-trace mean RMSE,
+Hodges--Lehmann gives $-.019\%$ (paired Wilcoxon $p=.922$).
+Hierarchical resampling of traces and their model seeds gives the 95\%
+percentile interval $[-1.89\%,+12.28\%]$, including zero but extending above
+the $2\%$ equivalence band. Group-gain retention is
+$(\overline\Delta_{\mathrm{FedAvg}}-\overline\Delta_{\mathrm{floor}})/
+(\overline\Delta_{\mathrm{FedAvg}}-\overline\Delta_{\mathrm{ctrl}})=1.0194$.
+
+Registered floor/M1$\mu$/M2$\mu$ versus FedAvg chains use one-sided paired
+Wilcoxon tests of within-trace three-seed mean group differences (H1). All
+ten traces improve (individual $p=.0009765625$) and reject at family-level
+$.05$ (initial weights $1/3$, Holm redistribution $1/2$). Prediction
+non-inferiority (H2) needs a Wilcoxon-inverted one-sided upper bound below
+$2\%$; the bounds $3.83/4.14/8.15\%$ fail, so superiority (H3) is untested.
+The secondary Holm family (M1/control, M2/control, floor/NoDesign, six-arm
+dose-response slope) has no significant member. All traces stay in the
+primary analysis. Trace 32005's control/NoDesign cost recurs on five model
+seeds; dropping it only in a sensitivity pass gives $[-2.32\%,+3.53\%]$,
+still inconclusive. All-trace diagnostic power at $2\%$ is $.151$.
+
+\subsection{Offline Configuration and Retrospective Trade-offs}
+\label{app:cityscanner_phi}
+For block $r$, $n_r$ counts unique training units and $n_r^{\mathrm{zero}}$
+those with a zero-target attached client--stratum key. The offline rule is
+\begin{equation}
+\rho_r=\frac{n^{\mathrm{zero}}_r}{n_r},
+\qquad
+D_r=\mathrm{on}\iff\rho_r=0 .
+\label{eq:design_gate}
+\end{equation}
+Table~\ref{tab:scd_phi_freeze} distinguishes its lookup objects. A pre-window
+configuration requires the catalogue and public lookup to exist then;
+current outcomes and the coverage Gate do not select Design. The counts
+use no $Y$ or RMSE, establish neither target-positive support nor input
+availability timing, and differ from U-Air's $25.5\%$ EventTrace occurrence.
+For measured endpoints $M_{e,r}(D)$,
+$e\in\{\Delta_{\mathrm{group}},\Delta_{c\text{-}s},\mathrm{RMSE}_{\mu},\mathrm{Tail}\}$,
+and nonnegative weights $w_e$, the retrospective chart is
+\begin{equation}
+\begin{aligned}
+\widehat J_r(D)&=\sum_{e\in\mathcal{E}}w_e\,\frac{M_{e,r}(D)}{M_{e,r}(\mathrm{on})},\\
+D_r^{\star}&=\arg\min_{D\in\{\mathrm{on},\mathrm{off}\}}\widehat J_r(D),
+\end{aligned}
+\label{eq:design_switch}
+\end{equation}
+Using structural terms alone gives U-Air indifference at $w_c/w_g=1.39$.
+This chart is not the experiments' online rule. Both fixed Design settings
+remain reported where their trade-off matters.
+
+\begin{table}[!htbp]
+\centering
+\caption{Offline zero-target counts for attached clients.
+Frozen $\pi^{\mathrm{tar}}(k(i),s(i))$; missing keys count as zero.
+Design uses rule~\eqref{eq:design_gate}.}
+\label{tab:scd_phi_freeze}
+\scriptsize
+\setlength{\tabcolsep}{2.5pt}
+\begin{tabular*}{\columnwidth}{@{\extracolsep{\fill}}lcccc}
+\toprule
+Block & $n_{\mathrm{train}}$ & $n_{\mathrm{zero}}$ & coverage & Design \eqref{eq:design_gate}\\
+\midrule
+SensorScope (Table~\ref{tab:main_effectiveness}) & $10285$ & $0$ & $0$ & on\\
+U-Air (Table~\ref{tab:main_effectiveness}) & $5688$ & $2016$ & $35.4\%$ & off\\
+T-Drive hybrid (Table~\ref{tab:tdrive_hybrid}) & $285659$ & $135268$ & $47.4\%$ & off\\
+NSW-Traffic four-region (Table~\ref{tab:traffic_four_region}) & $18576$ & $0$ & $0$ & on\\
+City Scanner NYC {PM}$_{2.5}$ (Table~\ref{tab:cityscanner_hybrid}) & $9343$ & $0$ & $0$ & on\\
+City Scanner P2 meas.\ $O$ (Table~\ref{tab:cityscanner_p2_measured_o}) & $10141$ & $0$ & $0$ & on\\
+\bottomrule
+\end{tabular*}
+\end{table}
+
+Lookup objects differ: test-split client--stratum mass
+$\pi^{\mathrm{tar}}_{k,s}$ on SensorScope/U-Air, test-stratum frequency on
+T-Drive, and a four-region freeze on NSW-Traffic. City Scanner assigns
+positive test-group shares $\mu_{h(i)}$ to training atoms, rather than
+checking target-positive pairs; its zero count is not the SensorScope/U-Air
+support check.
+
+\subsection{Support and Stabilization Conditions}
 \label{app:a5_a6_audit}
 Proposition~\ref{prop:practical_plugin} uses A1, A4, A5, A6b and shared-state,
 positive-mass conditions; A6a suffices for zero stabilization error but is not required by the bound. Twenty seeds yield 16000/12800 SensorScope/U-Air
@@ -1482,7 +1732,7 @@
 positive reference mass and A6b remain conditions: saved states omit
 active-set lists and estimated margins, preventing A6b and plug-in-error checks.
 
-\paragraph{Reference and Prediction Sensitivity.}
+\subsection{Reference and Prediction Sensitivity}
 \label{app:reference_sensitivity}
 On 20 paired seeds, true observation/usability margins change calibrated
 RMSE by $-.008\%$ ($[-.041,+.025]\%$) on SensorScope and $+.040\%$
@@ -1496,7 +1746,7 @@
 zero-containing intervals; $.70$--$.80$ pp detection leaves $.5\%$ improvement
 unresolved. These are evaluated configurations, not predictive optima.
 
-\paragraph{Target-Concentration Sensitivity.}
+\subsection{Target-Concentration Sensitivity}
 \label{app:target_concentration}
 
 Table~\ref{tab:target_concentration} multiplies region1's prior mass by
@@ -1531,8 +1781,10 @@
 MDE; at $5$ only intervals exclude zero. All effects remain below the $2\%$
 criterion, so target dilution alone does not explain this configuration's small gain.
 
-\section{Coverage Diagnostics under Availability Stress}
+\section{Coverage-Controlled Variant under Availability Stress}
 \label{app:certificate_audit}
+Conditional diagnostic proofs are in Appendix~\ref{app:agg_coverage_proofs}.
+
 \label{subsec:limitations}
 
 Table~\ref{tab:certificate_stress} and Fig.~\ref{fig:certificate_audit}
@@ -1578,7 +1830,7 @@
 keep Gate off because the LCB stays below $\tau_{\mathrm{cov}}$.
 U-Air $a=1.00$ misses the nominal $95\%$ empirical validity.
 
-\begin{figure}[t]
+\begin{figure}[!htbp]
 \raggedright
 \includegraphics[width=\columnwidth]{fig_certificate_audit.pdf}
 \caption{Coverage-controlled Design diagnostics.
@@ -1589,161 +1841,11 @@
 \label{fig:certificate_audit}
 \end{figure}
 
-\section{Target Support and City Scanner Protocols}
-\label{app:cityscanner_phi}
-
-\subsection{Offline Configuration and Retrospective Trade-offs}
-For block $r$, $n_r$ counts unique training units and $n_r^{\mathrm{zero}}$
-those with a zero-target attached client--stratum key. The offline rule is
-\begin{equation}
-\rho_r=\frac{n^{\mathrm{zero}}_r}{n_r},
-\qquad
-D_r=\mathrm{on}\iff\rho_r=0 .
-\label{eq:design_gate}
-\end{equation}
-Table~\ref{tab:scd_phi_freeze} distinguishes its lookup objects. A pre-window
-configuration requires the catalogue and public lookup to exist then;
-current outcomes and the coverage Gate do not select Design. The counts
-use no $Y$ or RMSE, establish neither target-positive support nor input
-availability timing, and differ from U-Air's $25.5\%$ EventTrace occurrence.
-For measured endpoints $M_{e,r}(D)$,
-$e\in\{\Delta_{\mathrm{group}},\Delta_{c\text{-}s},\mathrm{RMSE}_{\mu},\mathrm{Tail}\}$,
-and nonnegative weights $w_e$, the retrospective chart is
-\begin{equation}
-\begin{aligned}
-\widehat J_r(D)&=\sum_{e\in\mathcal{E}}w_e\,\frac{M_{e,r}(D)}{M_{e,r}(\mathrm{on})},\\
-D_r^{\star}&=\arg\min_{D\in\{\mathrm{on},\mathrm{off}\}}\widehat J_r(D),
-\end{aligned}
-\label{eq:design_switch}
-\end{equation}
-Using structural terms alone gives U-Air indifference at $w_c/w_g=1.39$.
-This chart is not the experiments' online rule. Both fixed Design settings
-remain reported where their trade-off matters.
-
-\begin{table}[!htbp]
-\centering
-\caption{Offline zero-target counts for attached clients.
-Frozen $\pi^{\mathrm{tar}}(k(i),s(i))$; missing keys count as zero.
-Design uses rule~\eqref{eq:design_gate}.}
-\label{tab:scd_phi_freeze}
-\scriptsize
-\setlength{\tabcolsep}{2.5pt}
-\begin{tabular*}{\columnwidth}{@{\extracolsep{\fill}}lcccc}
-\toprule
-Block & $n_{\mathrm{train}}$ & $n_{\mathrm{zero}}$ & coverage & Design \eqref{eq:design_gate}\\
-\midrule
-SensorScope (Table~\ref{tab:main_effectiveness}) & $10285$ & $0$ & $0$ & on\\
-U-Air (Table~\ref{tab:main_effectiveness}) & $5688$ & $2016$ & $35.4\%$ & off\\
-T-Drive hybrid (Table~\ref{tab:tdrive_hybrid}) & $285659$ & $135268$ & $47.4\%$ & off\\
-NSW-Traffic four-region (Table~\ref{tab:traffic_four_region}) & $18576$ & $0$ & $0$ & on\\
-City Scanner NYC {PM}$_{2.5}$ (Table~\ref{tab:cityscanner_hybrid}) & $9343$ & $0$ & $0$ & on\\
-City Scanner P2 meas.\ $O$ (Table~\ref{tab:cityscanner_p2_measured_o}) & $10141$ & $0$ & $0$ & on\\
-\bottomrule
-\end{tabular*}
-\end{table}
-
-Lookup objects differ: test-split client--stratum mass
-$\pi^{\mathrm{tar}}_{k,s}$ on SensorScope/U-Air, test-stratum frequency on
-T-Drive, and a four-region freeze on NSW-Traffic. City Scanner assigns
-positive test-group shares $\mu_{h(i)}$ to training atoms, rather than
-checking target-positive pairs; its zero count is not the SensorScope/U-Air
-support check.
-
-\subsection{City Scanner New York {PM}$_{2.5}$}
-\label{app:cityscanner_nyc}
-
-New York Pilot~1/2 {PM} CSVs (Zenodo 10.5281/zenodo.7961851, {CC BY}
-4.0)~\cite{wang2023cityscanner} exclude Boston, Beirut, and {NO}$_2$.
-Non-finite GPS, time, or {PM}$_{2.5}$, and values outside
-$[0,1000]$\,$\mu$g/m$^3$, are removed. Occupied $500$\,m $\times$ $30$\,min
-cells average calibrated measurements into $Y$; empty slots are absent.
-Cells are clients and GPS supplies $R$. Median cell indices define four
-quadrants without $Y$; $\boldsymbol\mu$ is their test share. Strata are
-$\mathrm{region}{::}\mathrm{block}{::}\mathrm{weekday}$ (at most 32).
-Complete-aligned $O/U$ use $p_{\mathrm{obs}}=.35$ and $S_{\max}=5$.
-
-The 14723 units, 446 cells, and 2776 slots split chronologically into
-$9343/3290/2090$ train/validation/test units (test regions $496/992/148/454$).
-Seeds $32001$--$32010$ share 100 equal-count windows of 1666 training slots.
-Design is on and Gate is unused (Table~\ref{tab:scd_phi_freeze}).
-Table~\ref{tab:cityscanner_real}(a) uses training-standardized errors. One
-seed-32006 window clipped and renormalized tiny negative solver weights.
-
-\subsection{City Scanner Pilot~2 with Measured Observation}
-\label{app:cityscanner_p2_measured_o}
-
-Pilot~2 uses {PM}/{NO}$_2$ CSVs from the same source, excluding Pilot~1,
-Boston, and Beirut, on the same client/$Y$ grid. Union GPS supplies $R$;
-finite {PM}$_{2.5}$ in $[0,1000]$ supplies $O=1$; {NO}$_2$ contributes
-locations only. $U$ stays Complete-aligned ($S_{\max}=5$). The frozen regional
-target, Design-on, and unused Gate keep their roles at different target values.
-
-The 14960 cell-slots, 416 cells, and 2402 slots split into
-$10141/2835/1984$ train/validation/test units: 1931 unobserved ($12.9\%$) and
-13029 labeled, with test-region occupancy $1289/268/144/283$. Seeds
-$33001$--$33010$ use 100 windows from 1441 training slots.
-Table~\ref{tab:cityscanner_real}(b) uses this block's training standardization.
-Section~\ref{subsec:cityscanner_real} gives the rankings and the missed
-improvement criterion.
-
-\subsection{City Scanner Target Maps and Zero-Mass Handling}
-\label{app:cityscanner_sixarm}
-
-The six-arm visit-occupancy comparison uses controlled $O/U$ and ten traces
-with model seeds $s,s+100000,s+200000$: 150 newly trained and 30 reused runs.
-Maps use public locations, calendar strata and test-region shares before
-training, without responses/errors. Table~\ref{tab:cityscanner_sixarm}
-summarizes ten within-trace model-seed means.
-
-\begin{table}[!htbp]
-\centering
-\caption{Client--stratum gaps across City Scanner target maps.
-Mean $\pm$ SD over ten trace means, each using three model seeds.
-Targets are arm-specific, so gaps do not rank common-target alignment.}
-\label{tab:cityscanner_sixarm_cs}
-\footnotesize
-\begin{tabular}{lr}
-\toprule
-Method / target map & $\Delta_{c\text{-}s}$\\
-\midrule
-FedAvg / count & $0.8123{\pm}0.0191$\\
-RAVEN-NoDesign & $0.7880{\pm}0.0254$\\
-RAVEN-control & $0.5676{\pm}0.0311$\\
-RAVEN-floor & $0.7892{\pm}0.0235$\\
-RAVEN-M1$\mu$ & $1.4060{\pm}0.0168$\\
-RAVEN-M2$\mu$ & $1.4348{\pm}0.0147$\\
-\bottomrule
-\end{tabular}
-\end{table}
-
-Count-weighted FedAvg and RAVEN-NoDesign omit the target ratio.
-RAVEN-control has 1164 keys, 812 zero; RAVEN-floor replaces zeros with
-$4.78469\times10^{-4}$, the smallest positive mass, and renormalizes,
-changing group marginals. RAVEN-M1$\mu$/RAVEN-M2$\mu$ use ACS population/NYC~311
-shapes on these keys, rescaled within region to the common target (70/33 zeros).
-All maps cover the 959 risk-set keys.
-
-For $d_t=R_{\mathrm{ctrl},t}/R_{\mathrm{floor},t}-1$ on within-trace mean RMSE,
-Hodges--Lehmann gives $-.019\%$ (paired Wilcoxon $p=.922$).
-Hierarchical resampling of traces and their model seeds gives the 95\%
-percentile interval $[-1.89\%,+12.28\%]$, including zero but extending above
-the $2\%$ equivalence band. Group-gain retention is
-$(\overline\Delta_{\mathrm{FedAvg}}-\overline\Delta_{\mathrm{floor}})/
-(\overline\Delta_{\mathrm{FedAvg}}-\overline\Delta_{\mathrm{ctrl}})=1.0194$.
-
-Registered floor/M1$\mu$/M2$\mu$ versus FedAvg chains use one-sided paired
-Wilcoxon tests of within-trace three-seed mean group differences (H1). All
-ten traces improve (individual $p=.0009765625$) and reject at family-level
-$.05$ (initial weights $1/3$, Holm redistribution $1/2$). Prediction
-non-inferiority (H2) needs a Wilcoxon-inverted one-sided upper bound below
-$2\%$; the bounds $3.83/4.14/8.15\%$ fail, so superiority (H3) is untested.
-The secondary Holm family (M1/control, M2/control, floor/NoDesign, six-arm
-dose-response slope) has no significant member. All traces stay in the
-primary analysis. Trace 32005's control/NoDesign cost recurs on five model
-seeds; dropping it only in a sensitivity pass gives $[-2.32\%,+3.53\%]$,
-still inconclusive. All-trace diagnostic power at $2\%$ is $.151$.
-
-\section{Learning Capacity and Update-Rule Sensitivity}
+\section{Development Learning and Implementation Sensitivity}
+\label{app:development_details}
+Independent development protocols retain their own targets and budgets.
+
+\subsection{Centralized Learning Capacity and Baselines}
 \label{app:learning_capacity}
 
 Development seeds 41001--41003 use central-delivered training pools,
@@ -1821,85 +1923,7 @@
 reference. Oracle weights reduce group/client--stratum mismatch by
 $.0079$ ($[.0051,.0110]$) and $.0099$ ($[.0067,.0132]$) on these runs.
 
-\section{Instantaneous Arrival-Support Geometry}
-\label{app:arrival_support}
-
-The rows use the formal complete-aligned logs for NSW-Traffic, SensorScope,
-and U-Air, seeds $30001$--$30020$. A nonempty close keeps $U=1$ attempts;
-one client keeps the largest downloaded version. That attempt is one column
-of $M^{\mathrm{arr}}$: the frozen UTC block of its observed units on Traffic,
-and the spatial-and-block group named by its opportunity stratum on
-SensorScope and U-Air. Empty closes are dropped ($5382$ remain). U-Air
-contributes $1515$ closes; the $1402$ Design-on active windows in the main
-text are a different set.
-
-Positive target mass splits into missing mass ($n_g=0$), narrow-range mass
-($n_g>0$, $W_g<.01$), and adjustable mass ($W_g\ge.01$), with
-$\overline\alpha=\min\{1,\max\{.5,1/K\}\}$ and $\overline E=\min\{3,K\}$.
-For $K\le 3$ the feasible set is uniform, so adjustable mass is $0$.
-$d_{\mathrm{simplex}}$, $d_{\mathrm{cap}}$, $d_{\mathrm{ESS}}$, and
-$d_{\mathcal C}$ minimize $\|M^{\mathrm{arr}}\alpha-\mu\|_1$ on the simplex,
-under the cap, under $\sum_k\alpha_k^2\le 1/\overline E$, and under both.
-These are $\ell_1$ distances, separate from the squared $\ell_2$ gap
-$d_r^{\mathrm{feas}}$ in Appendix~\ref{app:supp_calibration_geometry}.
-
-\begin{proposition}[Arrival-support simplex distance]
-\label{prop:arrival_simplex}
-If every column of $M$ is a basis vector, $\mu_g\ge 0$, and $\sum_g\mu_g=1$,
-then on the simplex
-$\min_{\alpha}\|M\alpha-\mu\|_1=2\mu_{\mathrm{miss}}$,
-where $\mu_{\mathrm{miss}}$ is the target mass on groups with no column.
-\end{proposition}
-
-\begin{proof}
-Absent groups contribute $\mu_{\mathrm{miss}}$, and present groups must carry
-total mass $1$, so they sit at least $\mu_{\mathrm{miss}}$ above their combined
-target. Matching each present target and placing the residual on one present
-client attains the bound. The same value under the cap and the ESS bound is
-measured in Table~\ref{tab:arrival_support}; it is not claimed for arbitrary caps.
-\end{proof}
-
-The four minima agree through $10^{-11}$, and all $2966$ closes with
-$K\le 3$ have adjustable mass $0$. Table~\ref{tab:arrival_support} gives the
-common distance. Seeds are averaged inside a stratum, then averaged with
-equal weight. For $K>3$, adjustable mass has descriptive interval
-$[2.220\%,2.283\%]$ on SensorScope and $[2.938\%,3.020\%]$ on U-Air
-($10{,}000$ resamples, seed $20261019$).
-
-\begin{table}[!htbp]
-\centering
-\caption{Arrival-log geometry. Masses are percentages of positive target
-mass. L1 is the shared minimum $\ell_1$ distance on $M^{\mathrm{arr}}$.}
-\label{tab:arrival_support}
-\scriptsize
-\setlength{\tabcolsep}{2.5pt}
-\begin{tabular}{llrrrrr}
-\toprule
-Dataset & $K$ & Windows & Miss. & Narrow & Adj. & L1\\
-\midrule
-Traffic & $\le 3$ & 294 & 75.000 & 25.000 & 0 & 1.5000\\
-Traffic & $>3$ & 1696 & 75.000 & 25.000 & 0 & 1.5000\\
-SensorScope & $\le 3$ & 1475 & 98.916 & 1.084 & 0 & 1.9783\\
-SensorScope & $>3$ & 402 & 97.748 & 0 & 2.252 & 1.9550\\
-U-Air & $\le 3$ & 1197 & 98.551 & 1.449 & 0 & 1.9710\\
-U-Air & $>3$ & 318 & 97.024 & 0 & 2.976 & 1.9405\\
-\bottomrule
-\end{tabular}
-\end{table}
-
-Every Traffic close covers one UTC block, so $75\%$ of the target is absent,
-the present block has range zero, and the minimum distance is $1.5$. For
-$K>3$, SensorScope and U-Air leave $2.252\%$ and $2.976\%$ adjustable. The cap
-and ESS bound do not raise that one-close minimum. Cross-window mismatch and
-RMSE are separate questions.
-
-Under arrival-time consumption, an attempt still inside the staleness bound
-at its arrival close is consumed there. On these three traces the hold set
-matches the arrival set in every nonempty window, so the adjustable-mass
-difference is zero. Retaining an update past that close is a different rule,
-and this comparison did not train it.
-
-\section{Development Geometry and Release Timing}
+\subsection{Development Constraint Geometry}
 \label{app:development_geometry}
 
 Table~\ref{tab:development_geometry} reports natural-window geometry;
@@ -2011,3 +2035,4 @@
 Rolling minus fixed averages $.0395584$ (median $.0405236$). Rolling reference
 lowers $W$ by $30.0752\%$ and raises $G$ by $.0258430$ versus the fixed reference, so neither
 improves both. Rolling + stop debt matches it on this seed.
+

`

## supplemental.tex

`diff
--- supplemental.tex before
+++ supplemental.tex after
@@ -63,6 +63,7 @@
 
 \begin{document}
 
+
 \title{Supplemental Material for\\
 RAVEN-MCS: Target-Mass Calibration for Windowed Federated Data Completion in Mobile Crowdsensing}
 
@@ -76,7 +77,7 @@
 % Continue figure/table/equation numbers from the companion main paper.
 % Main has 4 figures, 7 tables, 1 algorithm and 41 numbered equations.
 % The development-geometry summary now lives in this file.
-% Offline support and retrospective switch equations are in Appendix J.
+% Offline configuration and retrospective results are in Appendix F.
 % Numbered statements in main: four propositions, two theorems, one assumption.
 \setcounter{figure}{4}
 \setcounter{table}{7}
@@ -87,6 +88,16 @@
 \setcounter{corollary}{0}
 \setcounter{assumption}{1}
 
+\noindent\textbf{Reading guide.}
+Model/proofs: Appendix~\ref{app:complete_proofs}, p.~\pageref{app:complete_proofs};
+coverage: \ref{app:agg_coverage_proofs}, p.~\pageref{app:agg_coverage_proofs};
+protocols/baselines: \ref{app:experimental_protocols}, p.~\pageref{app:experimental_protocols};
+RQ1 results: \ref{app:rq1_results}, p.~\pageref{app:rq1_results};
+RQ2 mechanisms: \ref{app:rq2_details}, p.~\pageref{app:rq2_details};
+RQ3 support/sensitivity: \ref{app:rq3_details}, p.~\pageref{app:rq3_details};
+coverage variant: \ref{app:certificate_audit}, p.~\pageref{app:certificate_audit};
+development: \ref{app:development_details}, p.~\pageref{app:development_details}.
+
 \input{appendix}
 
 % Each PDF has its own bibliography. xr imports cross-references without bibcite.

`

