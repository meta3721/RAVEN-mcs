# Evaluation内部重组完整源码差异

基于本轮编辑前归档，不相对于仓库HEAD。回退时保留后续用户改动。

## main.tex

```diff
--- main.tex before
+++ main.tex after
@@ -1141,7 +1141,7 @@
 \label{subsec:eval_methods}
 
 The following five principal schemes share the task backbone and window-close
-protocol; their local weighting, reference masses, and aggregation rules differ.
+protocol; local weights, positive-mass support, and aggregation constraints differ.
 Each experiment retains its stated comparison set.
 
 \noindent\textit{FedAvg-Window.}
@@ -1172,23 +1172,28 @@
 are defined in Appendix~\ref{app:adapted_baselines}.
 
 \noindent\textit{RAVEN-Design.}
-The complete comparison arm reconstructs a reference through opportunity,
-observation, and usability correction, then solves P2 under cap and
-effective-support constraints. It coordinates reference fidelity, deployment-group
-composition, and accumulated under-service, with Design fixed on as defined
-after \eqref{eq:design_factor}.
-
-\noindent\textit{Auxiliary comparisons.}
+This arm uses opportunity/observation-corrected local training and
+client masses, then usability correction to reconstruct the server reference.
+It solves P2 under cap and effective-support constraints, producing executable weights. Reference fidelity, deployment-group composition, and accumulated under-service
+are coordinated with Design fixed on before the run (\eqref{eq:design_factor}).
+
+\noindent\textit{Matched-support rules.}
+Count and Uniform share Design-on local correction and active clients.
+Count normalizes observed counts without enforcing $\mathcal C_r$;
+Uniform is feasible under the experimental configuration.
+Reference projection minimizes $\|\alpha-\widehat\beta_r\|_2^2$ on
+$\mathcal C_r$; projection and P2 enforce these constraints.
+Inst-Cal is debt-free P2, distinct from removing the Inst component.
+The $\kappa=1000$ projection-plus-debt rule is a separate sensitivity configuration.
+
+\noindent\textit{Other comparisons.}
 FedAsync-Window~\cite{xie2019asynchronous}, TimeAlign-Agg~\cite{wang2026federated},
-and Local-H\'ajek test staleness, temporal coverage, and local correction.
-Matched-support Count, Uniform, reference projection, and P2 share support
-and constraints; projection minimizes $\|\alpha-\widehat\beta_r\|_2^2$ on
-$\mathcal C_r$. Inst-Cal removes debt; RAVEN-NoDesign fixes Design off.
-Central-All/Delivered and RAVEN-SimOracle are reference-only. Debt-Cal and
-the tuning-selected $\kappa=1000$ projection-plus-debt rule have separate
-recursions. FedIPW/FedPALS are mechanism comparators, not run baselines
-(Supplementary Table~\ref{tab:nearest_neighbor}). Labels may omit Window;
-2S-H\'ajek abbreviates TwoStage-H\'ajek.
+and Local-H\'ajek examine timing and local correction. RAVEN-NoDesign fixes
+the opportunity ratio to one; other steps coincide without requiring identical support.
+Central-All/Delivered and RAVEN-SimOracle are reference-only; Debt-Cal retains
+its separate recursion. FedIPW/FedPALS are mechanism comparators, not run
+baselines (Supplementary Table~\ref{tab:nearest_neighbor}). Labels may omit
+Window; 2S-H\'ajek abbreviates TwoStage-H\'ajek.
 
 \noindent\textit{Deployment alignment.}
 Group mismatch measures the $L_1$ distance between aggregate group mass and
@@ -1320,171 +1325,8 @@
 comparisons miss the declared $\le-.5\%$ paired relative-error criterion.
 
 
-\paragraph{Risk semantics and external protocols.}
-
-The five-seed balanced control meets its $3\%$ no-harm margin: RAVEN versus
-TimeAlign degrades by $.0599\%$, with one-sided 95\% upper bound $.134\%$.
-Under complete-aligned NSW-Traffic, define target and arrival changes from
-balanced as $\Delta_\mu,\Delta_\rho$ and
-$D_{\mathrm{aligned}}=\Delta_\mu-\Delta_\rho$.
-Figure~\ref{fig:risk_noninterchangeability} gives mean $D$ from $-.0209$ to
-$-.0214$, 17--18 negative seeds per method, and paired
-$p=4.83\times10^{-4}$--$5.86\times10^{-4}$.  Target change is about
-$8\times10^{-4}$ versus $2.2\times10^{-2}$ arrival change, showing that
-selection affects the two risk views differently.
-The six-scenario matrix (Appendix~\ref{app:e2_layer_matrix}) finds Holm-significant
-arrival changes for all five methods under observation-only and complete-aligned
-selection, but target changes for zero and two methods respectively.  The other
-three non-balanced scenarios have no significant target contrast.  Compounding
-and cancellation depend on the construction.
-
-\begin{figure}[t]
-\raggedright
-\includegraphics[width=\columnwidth]{fig2_e2_risk_noninterchangeability.pdf}
-\caption{Target and arrival-risk changes on NSW-Traffic.
-Complete-aligned selection: (a)~mean $\pm$ sample SD over 20 paired seeds of
-$D_{\mathrm{aligned}}=\Delta\mathrm{RMSE}_{\mu}-\Delta\mathrm{RMSE}_{\rho}$;
-zero denotes equal changes. Negative $D$ means a larger arrival-risk change.
-(b)~Negative-seed counts; dotted line: 10/20. Counts describe direction,
-not significance or performance ranking.}
-\label{fig:risk_noninterchangeability}
-\end{figure}
-
-Real T-Drive opportunity is intermittent: active fraction $.425$, burstiness
-$+.38$, and cell coverage $.547$.  Four-block opportunity--target TV is $.142$
-versus $.192/ .278$ in protocol SensorScope/U-Air, all above $.05$
-(Fig.~\ref{fig:g3_tdrive}; Table~\ref{tab:tdrive_hybrid}).
-With controlled $O/U$, RAVEN-NoDesign fails the
-$+.5\%$ worst-group tolerance against FedAU/ObsUse: paired relative
-$+2.39\%/+2.43\%$ (versus FedAvg $+.32\%$).  Its group gap equals FedAvg's;
-Design on worsens prediction, worst-group risk, and group mismatch.  Delivery remains controlled.
-
-\begin{figure}[t]
-\raggedright
-\includegraphics[width=\columnwidth]{fig_g3_tdrive_h_mass.pdf}
-\caption{T-Drive opportunity and target mismatch.
-(a)~Deployment target $\boldsymbol\mu$, real taxi $R$, and unit-balanced
-reference. (b)~Four-block $\mathrm{TV}(\pi^{\mathrm{opp}},\boldsymbol\mu)$;
-SS/UA denote the Complete-aligned SensorScope/U-Air protocols. The dotted $0.05$
-line is the pre-specified mismatch-diagnostic threshold.}
-\label{fig:g3_tdrive}
-\end{figure}
-\begin{table}[!htbp]
-\centering
-\caption{T-Drive comparison under real sensing opportunities.
-Real taxi $R$, controlled $O/U$; mean $\pm$ SD over ten seeds; 178 windows;
-lower is better. WorstGroupRMSE uses UTC H1--H4.
-FedAvg, FedAU and ObsUse are Window variants.}
-\label{tab:tdrive_hybrid}
-\scriptsize
-\setlength{\tabcolsep}{1pt}
-\begin{tabular}{lcccc}
-\toprule
-Method & $\mathrm{RMSE}_{\mu}$ & WorstGroupRMSE &
-$\Delta_{\mathrm{group}}$ & $\Delta_{c\text{-}s}$\\
-\midrule
-FedAvg     & \shortstack{$1.1042$\\$\pm0.0022$} & \shortstack{$1.3064$\\$\pm0.0035$} & $0.5232$ & \shortstack{$1.9758$\\$\pm0.0004$}\\
-TwoStage-H\'ajek    & \shortstack{$1.1254$\\$\pm0.0142$} & \shortstack{$1.3373$\\$\pm0.0198$} & \shortstack{$0.5948$\\$\pm0.0124$} & \shortstack{$1.9642$\\$\pm0.0007$}\\
-FedAU      & \shortstack{$1.0898$\\$\pm0.0050$} & \shortstack{$1.2801$\\$\pm0.0109$} & $0.5232$ & \shortstack{$1.9915$\\$\pm0.0012$}\\
-ObsUse     & \shortstack{$1.0896$\\$\pm0.0049$} & \shortstack{$1.2796$\\$\pm0.0108$} & $0.5232$ & \shortstack{$1.9916$\\$\pm0.0012$}\\
-RAVEN-NoDesign & \shortstack{$1.1069$\\$\pm0.0028$} & \shortstack{$1.3106$\\$\pm0.0044$} & $0.5232$ & \shortstack{$1.9936$\\$\pm0.0003$}\\
-RAVEN-Design & \shortstack{$1.1242$\\$\pm0.0159$} & \shortstack{$1.3355$\\$\pm0.0225$} & \shortstack{$0.5948$\\$\pm0.0124$} & \shortstack{$1.9774$\\$\pm0.0006$}\\
-\bottomrule
-\end{tabular}
-\end{table}
-
-The separate NSW four-region protocol ranking
-(Appendix~\ref{app:traffic_four_region}) favors TwoStage-H\'ajek on prediction
-and worst-group RMSE and FedAU on group mismatch ($.0606$ versus RAVEN's
-$.1048$); RAVEN stays within the descriptive worst-group tolerance against
-FedAU/ObsUse under its local four-region target.
-
-Arrival-weighted validation shifts the reported risk by $-4.11\%$ to
-$-4.12\%$ on SensorScope and $+.27\%$ to $+.62\%$ on U-Air, yet selects
-the same configuration on all 20 seeds. In these comparisons, the scoring
-distortion changes reported error more than configuration selection.
-
-Both City Scanner protocols show group-alignment gains under real opportunities
-and controlled delivery; prediction and external-protocol rankings differ.
-
-\subsection{Mechanism Contributions (RQ2)}
-\label{subsec:rq2_mechanisms}
-\label{subsec:eval_rq2}
-\label{subsec:eval_rq3}
-
-\paragraph{Matched-support rules.}
-Table~\ref{tab:trained_rules} shares the Design-on correction pathway and
-RAVEN's active support across count weighting, Uniform, reference projection,
-Inst-Cal, and full P2.  Its U-Air count row is not the unrestricted FedAvg row
-of Table~\ref{tab:main_effectiveness}.  All paired rules use the same target and cap/ESS definitions;
-prediction follows the common saved-parameter scoring rule above.
-
-\begin{table*}[t]
-\centering
-\caption{Trained aggregation rules on matched Design-on support.
-Means over 20 paired seeds per dataset; lower is better.
-Wall is wall-clock seconds per run. U-Air Count uses RAVEN-Design support,
-unlike unrestricted FedAvg in Table~\ref{tab:main_effectiveness}.
-}
-\label{tab:trained_rules}
-\footnotesize
-\setlength{\tabcolsep}{5pt}
-\begin{tabular*}{\textwidth}{@{\extracolsep{\fill}}llrrrrr}
-\toprule
-Dataset & Server-weight rule & $\Delta_{\mathrm{group}}$ & $\Delta_{c\text{-}s}$ &
-$\mathrm{RMSE}_\mu$ & WorstGroupRMSE & Wall (s)\\
-\midrule
-SensorScope & Count / matched support & $1.05577$ & $1.29032$ & $7.93889$ & $8.67161$ & $20.5$\\
-SensorScope & Uniform & $1.02693$ & $1.27069$ & $7.93931$ & $8.67202$ & $20.0$\\
-SensorScope & Reference projection & $1.01158$ & $1.26903$ & $7.93725$ & $8.66989$ & $19.9$\\
-SensorScope & Projection with debt ($\kappa=1000$) & $0.98464$ & $1.26659$ & $7.93842$ & $8.67109$ & $18.5$\\
-SensorScope & Inst-Cal & $1.01409$ & $1.26443$ & $7.93799$ & $8.67066$ & $26.2$\\
-SensorScope & Full RAVEN-Design & $1.01394$ & $1.26438$ & $7.93799$ & $8.67066$ & $27.1$\\
-\midrule
-U-Air & Count / matched support & $1.12176$ & $1.26213$ & $1.19225$ & $1.25956$ & $12.0$\\
-U-Air & Uniform & $1.09734$ & $1.24065$ & $1.19349$ & $1.26094$ & $8.5$\\
-U-Air & Reference projection & $1.09162$ & $1.23265$ & $1.19691$ & $1.26474$ & $8.8$\\
-U-Air & Projection with debt ($\kappa=1000$) & $1.08001$ & $1.22623$ & $1.19470$ & $1.26231$ & $9.0$\\
-U-Air & Inst-Cal & $1.09241$ & $1.23342$ & $1.19537$ & $1.26304$ & $15.1$\\
-U-Air & Full RAVEN-Design & $1.09236$ & $1.23339$ & $1.19537$ & $1.26303$ & $15.3$\\
-\bottomrule
-\end{tabular*}
-\end{table*}
-
-Uniform accounts for $68.96\%$ of SensorScope's matched count-to-RAVEN group
-reduction: total $2.09$ pp ($[1.87,2.31]$), partitioned into $1.44$ pp
-count-to-Uniform and $.65$ pp remaining. U-Air gives $1.47$ pp
-($[1.18,1.75]$), partitioned into $1.22$ pp ($83.07\%$) and $.25$ pp.
-This isolates the effect of removing count weighting; the following contrasts
-measure the reference and calibration increments.
-The hindsight structural ruler has a group-TV gap from Uniform of
-$3.44/1.32$ pp on SensorScope/U-Air over 20 always-on seeds. U-Air FedAU/ObsUse use
-different supports and do not enter this attribution.
-
-Before feasible calibration, the direct corrected reference has group-mismatch
-readouts of $1.03533/1.11961$ on SensorScope/U-Air, above Uniform and
-potentially infeasible under caps/ESS. Projecting it improves these readouts by
-$1.188$ pp ($[.956,1.409]$) and $1.399$ pp ($[1.019,1.782]$), respectively.
-This fixed-support structural contrast quantifies the role of converting a
-reconstructed reference into a finite-window allocation; trained prediction
-and runtime are reported separately in Table~\ref{tab:trained_rules}.
-
-Relative to Uniform, corrected-reference projection improves group mismatch
-by $.768$ pp ($[.563,.970]$) on SensorScope and $.286$ pp ($[.098,.471]$)
-on U-Air. The $.5$ pp practical line is cleared stably only on SensorScope;
-U-Air changes from $.170$ on tuning seeds to $.402$ on report seeds.
-SensorScope's independent same-support projected Design-on/off contrast gives
-$.922$ pp ($[.721,1.141]$). This opportunity-correction effect is not additive
-with projection--Uniform;
-U-Air changes active support and cannot identify that contrast.
-
-Full P2 has $.118$ pp more group mismatch than projection on SensorScope
-($p_{\mathrm{Holm}}=.019$) but $.232$ pp less client--stratum mismatch.
-U-Air's group contrast is not significant.  Projection takes $19.9/8.8$ s
-versus RAVEN's $27.1/15.3$ s. The prediction contrasts are not
-Holm-significant (SensorScope $p=1$; U-Air minimum $.120$ using the saved model parameters).
-
-\paragraph{Fixed-configuration Design effects.}
+\paragraph{Controlled station comparisons.}
+
 
 Table~\ref{tab:main_effectiveness} compares controlled station mechanisms with both Design settings.  SensorScope
 Design reduces group/client--stratum mismatch versus FedAvg by $3.96\%/2.01\%$.
@@ -1550,22 +1392,186 @@
 TwoStage-H\'ajek by $2.46\%$ on TEST seeds, but its absolute $1.2630$ remains
 above FedAvg's $1.1690$.
 
-\paragraph{Under-served-block validation.}
+
+Under-served-block validation meets no-harm but misses the required improvement
+against FedAU/ObsUse (Supplementary Table~\ref{tab:underserved_block};
+Appendix~\ref{app:underserved_block}). INT-R retains U-Air's Design trade-off,
+while SensorScope's client--stratum advantage approaches zero (Appendix~\ref{app:int_r}).
 \label{subsec:eval_underserved}
-On validation only, aggregate target and opportunity mass to four UTC blocks
-and freeze $g^\star=\arg\max_b(\mu_b^{\mathrm{blk}}-
-\pi_b^{\mathrm{opp},4})$: block 2 on SensorScope and 3 on U-Air, with gaps
-$.114/.172$.  The required improvement against both FedAU and ObsUse is
-$-.5\%$.  Observed $+.05\%/+.15\%$ and $-.44\%/-.27\%$ miss that criterion
-while meeting no-harm (Supplementary Table~\ref{tab:underserved_block}).  INT-R preserves the direction of U-Air's Design trade-off, while
-the SensorScope client--stratum advantage approaches zero.
-
-\paragraph{Component removal.}
+
+\paragraph{Additional sensing protocols.}
+Real T-Drive opportunity is intermittent: active fraction $.425$, burstiness
+$+.38$, and cell coverage $.547$.  Four-block opportunity--target TV is $.142$
+versus $.192/ .278$ in protocol SensorScope/U-Air, all above $.05$
+(Fig.~\ref{fig:g3_tdrive}; Table~\ref{tab:tdrive_hybrid}).
+With controlled $O/U$, RAVEN-NoDesign fails the
+$+.5\%$ worst-group tolerance against FedAU/ObsUse: paired relative
+$+2.39\%/+2.43\%$ (versus FedAvg $+.32\%$).  Its group gap equals FedAvg's;
+Design on worsens prediction, worst-group risk, and group mismatch.  Delivery remains controlled.
+
+\begin{figure}[t]
+\raggedright
+\includegraphics[width=\columnwidth]{fig_g3_tdrive_h_mass.pdf}
+\caption{T-Drive opportunity and target mismatch.
+(a)~Deployment target $\boldsymbol\mu$, real taxi $R$, and unit-balanced
+reference. (b)~Four-block $\mathrm{TV}(\pi^{\mathrm{opp}},\boldsymbol\mu)$;
+SS/UA denote the Complete-aligned SensorScope/U-Air protocols. The dotted $0.05$
+line is the pre-specified mismatch-diagnostic threshold.}
+\label{fig:g3_tdrive}
+\end{figure}
+\begin{table}[!htbp]
+\centering
+\caption{T-Drive comparison under real sensing opportunities.
+Real taxi $R$, controlled $O/U$; mean $\pm$ SD over ten seeds; 178 windows;
+lower is better. WorstGroupRMSE uses UTC H1--H4.
+FedAvg, FedAU and ObsUse are Window variants.}
+\label{tab:tdrive_hybrid}
+\scriptsize
+\setlength{\tabcolsep}{1pt}
+\begin{tabular}{lcccc}
+\toprule
+Method & $\mathrm{RMSE}_{\mu}$ & WorstGroupRMSE &
+$\Delta_{\mathrm{group}}$ & $\Delta_{c\text{-}s}$\\
+\midrule
+FedAvg     & \shortstack{$1.1042$\\$\pm0.0022$} & \shortstack{$1.3064$\\$\pm0.0035$} & $0.5232$ & \shortstack{$1.9758$\\$\pm0.0004$}\\
+TwoStage-H\'ajek    & \shortstack{$1.1254$\\$\pm0.0142$} & \shortstack{$1.3373$\\$\pm0.0198$} & \shortstack{$0.5948$\\$\pm0.0124$} & \shortstack{$1.9642$\\$\pm0.0007$}\\
+FedAU      & \shortstack{$1.0898$\\$\pm0.0050$} & \shortstack{$1.2801$\\$\pm0.0109$} & $0.5232$ & \shortstack{$1.9915$\\$\pm0.0012$}\\
+ObsUse     & \shortstack{$1.0896$\\$\pm0.0049$} & \shortstack{$1.2796$\\$\pm0.0108$} & $0.5232$ & \shortstack{$1.9916$\\$\pm0.0012$}\\
+RAVEN-NoDesign & \shortstack{$1.1069$\\$\pm0.0028$} & \shortstack{$1.3106$\\$\pm0.0044$} & $0.5232$ & \shortstack{$1.9936$\\$\pm0.0003$}\\
+RAVEN-Design & \shortstack{$1.1242$\\$\pm0.0159$} & \shortstack{$1.3355$\\$\pm0.0225$} & \shortstack{$0.5948$\\$\pm0.0124$} & \shortstack{$1.9774$\\$\pm0.0006$}\\
+\bottomrule
+\end{tabular}
+\end{table}
+
+The separate NSW four-region protocol ranking
+(Appendix~\ref{app:traffic_four_region}) favors TwoStage-H\'ajek on prediction
+and worst-group RMSE and FedAU on group mismatch ($.0606$ versus RAVEN's
+$.1048$); RAVEN stays within the descriptive worst-group tolerance against
+FedAU/ObsUse under its local four-region target.
+
+\paragraph{Target-risk and arrival-risk comparison.}
+
+
+The five-seed balanced control meets its $3\%$ no-harm margin: RAVEN versus
+TimeAlign degrades by $.0599\%$, with one-sided 95\% upper bound $.134\%$ (Appendix~\ref{app:e1_balanced}).
+Under complete-aligned NSW-Traffic, define target and arrival changes from
+balanced as $\Delta_\mu,\Delta_\rho$ and
+$D_{\mathrm{aligned}}=\Delta_\mu-\Delta_\rho$.
+Figure~\ref{fig:risk_noninterchangeability} gives mean $D$ from $-.0209$ to
+$-.0214$, 17--18 negative seeds per method, and paired
+$p=4.83\times10^{-4}$--$5.86\times10^{-4}$.  Target change is about
+$8\times10^{-4}$ versus $2.2\times10^{-2}$ arrival change, showing that
+selection affects the two risk views differently.
+The six-scenario contrasts distinguish compounding and cancellation under
+the constructed layers (Appendix~\ref{app:e2_layer_matrix}).
+
+\begin{figure}[t]
+\raggedright
+\includegraphics[width=\columnwidth]{fig2_e2_risk_noninterchangeability.pdf}
+\caption{Target and arrival-risk changes on NSW-Traffic.
+Complete-aligned selection: (a)~mean $\pm$ sample SD over 20 paired seeds of
+$D_{\mathrm{aligned}}=\Delta\mathrm{RMSE}_{\mu}-\Delta\mathrm{RMSE}_{\rho}$;
+zero denotes equal changes. Negative $D$ means a larger arrival-risk change.
+(b)~Negative-seed counts; dotted line: 10/20. Counts describe direction,
+not significance or performance ranking.}
+\label{fig:risk_noninterchangeability}
+\end{figure}
+
+Arrival-weighted validation shifts the reported risk by $-4.11\%$ to
+$-4.12\%$ on SensorScope and $+.27\%$ to $+.62\%$ on U-Air, yet selects
+the same configuration on all 20 seeds. In these comparisons, the scoring
+distortion changes reported error more than configuration selection.
+
+
+Group alignment improves in the two City Scanner protocols, while station
+and external comparisons show protocol-specific prediction and alignment rankings.
+
+\subsection{Mechanism Contributions (RQ2)}
+\label{subsec:rq2_mechanisms}
+\label{subsec:eval_rq2}
+\label{subsec:eval_rq3}
+
+\paragraph{Matched-support comparison.}
+Table~\ref{tab:trained_rules} shares the Design-on correction pathway and
+RAVEN's active support across count weighting, Uniform, reference projection,
+Inst-Cal, and full P2.  Its U-Air count row is not the unrestricted FedAvg row
+of Table~\ref{tab:main_effectiveness}.  The target and cap/ESS definitions are common, but Count is uncalibrated;
+prediction follows the common saved-parameter scoring rule above.
+
+\begin{table*}[t]
+\centering
+\caption{Trained aggregation rules on matched Design-on support.
+Means over 20 paired seeds per dataset; lower is better.
+Wall is wall-clock seconds per run. U-Air Count uses RAVEN-Design support,
+unlike unrestricted FedAvg in Table~\ref{tab:main_effectiveness}.
+}
+\label{tab:trained_rules}
+\footnotesize
+\setlength{\tabcolsep}{5pt}
+\begin{tabular*}{\textwidth}{@{\extracolsep{\fill}}llrrrrr}
+\toprule
+Dataset & Server-weight rule & $\Delta_{\mathrm{group}}$ & $\Delta_{c\text{-}s}$ &
+$\mathrm{RMSE}_\mu$ & WorstGroupRMSE & Wall (s)\\
+\midrule
+SensorScope & Count / matched support & $1.05577$ & $1.29032$ & $7.93889$ & $8.67161$ & $20.5$\\
+SensorScope & Uniform & $1.02693$ & $1.27069$ & $7.93931$ & $8.67202$ & $20.0$\\
+SensorScope & Reference projection & $1.01158$ & $1.26903$ & $7.93725$ & $8.66989$ & $19.9$\\
+SensorScope & Projection with debt ($\kappa=1000$) & $0.98464$ & $1.26659$ & $7.93842$ & $8.67109$ & $18.5$\\
+SensorScope & Inst-Cal & $1.01409$ & $1.26443$ & $7.93799$ & $8.67066$ & $26.2$\\
+SensorScope & Full RAVEN-Design & $1.01394$ & $1.26438$ & $7.93799$ & $8.67066$ & $27.1$\\
+\midrule
+U-Air & Count / matched support & $1.12176$ & $1.26213$ & $1.19225$ & $1.25956$ & $12.0$\\
+U-Air & Uniform & $1.09734$ & $1.24065$ & $1.19349$ & $1.26094$ & $8.5$\\
+U-Air & Reference projection & $1.09162$ & $1.23265$ & $1.19691$ & $1.26474$ & $8.8$\\
+U-Air & Projection with debt ($\kappa=1000$) & $1.08001$ & $1.22623$ & $1.19470$ & $1.26231$ & $9.0$\\
+U-Air & Inst-Cal & $1.09241$ & $1.23342$ & $1.19537$ & $1.26304$ & $15.1$\\
+U-Air & Full RAVEN-Design & $1.09236$ & $1.23339$ & $1.19537$ & $1.26303$ & $15.3$\\
+\bottomrule
+\end{tabular*}
+\end{table*}
+
+\paragraph{Reference reconstruction and feasible calibration.}
+Before feasible calibration, the direct corrected reference has group-mismatch
+readouts of $1.03533/1.11961$ on SensorScope/U-Air, above Uniform and
+potentially infeasible under caps/ESS. Projecting it improves these readouts by
+$1.188$ pp ($[.956,1.409]$) and $1.399$ pp ($[1.019,1.782]$), respectively.
+This fixed-support structural contrast quantifies the role of converting a
+reconstructed reference into a finite-window allocation; trained prediction
+and runtime are reported separately in Table~\ref{tab:trained_rules}.
+
+Relative to Uniform, corrected-reference projection improves group mismatch
+by $.768$ pp ($[.563,.970]$) on SensorScope and $.286$ pp ($[.098,.471]$)
+on U-Air. The $.5$ pp practical line is cleared stably only on SensorScope;
+U-Air changes from $.170$ on tuning seeds to $.402$ on report seeds.
+SensorScope's independent same-support projected Design-on/off contrast gives
+$.922$ pp ($[.721,1.141]$). This opportunity-correction effect is not additive
+with projection--Uniform;
+U-Air changes active support and cannot identify that contrast.
+
+Full P2 has $.118$ pp more group mismatch than projection on SensorScope
+($p_{\mathrm{Holm}}=.019$) but $.232$ pp less client--stratum mismatch.
+U-Air's group contrast is not significant.  Projection takes $19.9/8.8$ s
+versus RAVEN's $27.1/15.3$ s. The prediction contrasts are not
+Holm-significant (SensorScope $p=1$; U-Air minimum $.120$ using the saved model parameters).
+
+Uniform accounts for $68.96\%$ of SensorScope's matched count-to-RAVEN group
+reduction: total $2.09$ pp ($[1.87,2.31]$), partitioned into $1.44$ pp
+count-to-Uniform and $.65$ pp remaining. U-Air gives $1.47$ pp
+($[1.18,1.75]$), partitioned into $1.22$ pp ($83.07\%$) and $.25$ pp.
+These mean-difference shares describe this shared pathway, not causal
+component contributions or additive gains across the following comparisons.
+The hindsight structural ruler has a group-TV gap from Uniform of
+$3.44/1.32$ pp on SensorScope/U-Air over 20 always-on seeds. U-Air FedAU/ObsUse use
+different supports and do not enter this attribution.
+
+\paragraph{Component contributions.}
+
 Table~\ref{tab:e4_ablation} removes one component from Design-on under paired
-Complete-aligned traces, reporting
+Complete-aligned traces, not universally fixed active support, reporting
 $100(M_{\mathrm{removed}}-M_{\mathrm{full}})/M_{\mathrm{full}}$.
-The Design row is the end-to-end trade-off above, not the same-support
-projection contrast. Inst contributes on specific structural and prediction
+The Design row includes the support changes described in
+Section~\ref{subsec:rq1_alignment}, not the fixed-support projection intervention.
+Inst removes instantaneous calibration, whereas Inst-Cal removes debt. Inst contributes on specific structural and prediction
 endpoints: its removal worsens SensorScope client--stratum mismatch by
 $.310\%$ and U-Air RMSE/tail by $.143\%/ .149\%$
 ($p_{\mathrm{Holm}}=.0194$), without significant U-Air structural changes.
@@ -1608,17 +1614,14 @@
 \end{tabular}
 \end{table}
 
-Constant within-client weights cancel in local normalization in the original
-station blocks (Appendix~\ref{app:local_hajek}).
+Constant within-client weights cancel in local normalization, while corrected
+client masses can still affect server weights in the original station blocks (Appendix~\ref{app:local_hajek}).
 The within-stratum heterogeneity experiment varies time-tercile covariates at fixed block observation means
 (Supplementary Table~\ref{tab:f1_mechanism}; Appendix~\ref{app:f1_mechanism}), providing within-stratum heterogeneous
 inputs to the correction pathway.
 
-\paragraph{Numerical accuracy.}
-The independent projection comparison has endpoint discrepancy up to
-$2.42\times10^{-5}$ in $\Delta$ units
-(Appendix~\ref{app:kappa_probe}, including residual and objective-gap diagnostics). Appendix~\ref{app:p2_diagnostics} assesses numerical feasibility and solver
-discrepancies separately from mathematical optimality.
+Numerical endpoint and feasibility diagnostics are reported in
+Appendices~\ref{app:kappa_probe} and~\ref{app:p2_diagnostics}.
 
 Count-to-Uniform and reference-projection increments are distinct; full P2
 coordinates endpoint and runtime trade-offs. Component effects are endpoint-specific,
@@ -1627,6 +1630,23 @@
 \subsection{Target Support and Feasible Adjustment (RQ3)}
 \label{subsec:rq3_adjustment}
 \label{subsec:ceiling}
+
+\paragraph{Support and constraint geometry.}
+
+With $E_{\min}=3$, $K_r\le3$ forces Uniform by the simplex norm bound.
+In the Complete-aligned station protocol this covers $78.6\%$ of 1877 SensorScope windows,
+$90.2\%$ of 1402 U-Air Design-on windows, and $79.0\%$ of 1515 Design-off
+windows.  Largest target groups carry only $.53\%/.79\%$.
+Across 3279 evaluated active windows the feasible L1 group-distance range has
+median $10^{-13}$; this does not make the squared L2 term in P2 constant.
+Appendix~\ref{app:arrival_support} separates missing, narrow-range, and
+adjustable target mass on nonempty arrival logs from these formal traces.
+
+For group range $W_{r,g}=\max_{\alpha\in\mathcal C_r}(M_r\alpha)_g-
+\min_{\alpha\in\mathcal C_r}(M_r\alpha)_g$, adjustable target mass sums
+$\mu_g$ where $W_{r,g}\ge.01$. Separate development trajectories exhibit
+weight directions with little adjustable target mass; their client subsets,
+targets, and cap/ESS scans are in Appendix~\ref{app:development_geometry}.
 
 \paragraph{Target-support variants.}
 \label{subsec:cityscanner_target_support}
@@ -1672,13 +1692,10 @@
 
 For floor/M1$\mu$/M2$\mu$ versus FedAvg, one-sided 95\% prediction upper bounds
 of $3.83/4.14/8.15\%$ exceed the $2\%$ non-inferiority margin;
-the gated superiority tests therefore remain untested. Separately, the primary trace-level
-ratio $\mathrm{RMSE}_{\mu}(\mathrm{ctrl})/\mathrm{RMSE}_{\mu}(\mathrm{floor})-1$
-has Hodges--Lehmann estimate $-.019\%$, 95\% percentile trace-cluster interval
-$[-1.89\%,+12.28\%]$, and $p=.922$. Deletion cost remains unresolved;
-floor changes group marginals as well as zero masses. The separate four-contrast
-secondary family has no Holm-significant member. Common-target alignment uses
-group mismatch; client--stratum gaps are arm-specific
+the gated superiority tests therefore remain untested. The control/floor paired prediction ratio remains inconclusive;
+floor changes group marginals as well as zero masses. The graphical primary
+chains and secondary Holm family retain separate identities
+(Appendix~\ref{app:cityscanner_sixarm}). Client--stratum targets are arm-specific
 (Supplementary Table~\ref{tab:cityscanner_sixarm_cs}).
 
 Target-map effects also depend on which groups the support represents.
@@ -1687,100 +1704,19 @@
 whereas U-Air costs $6.6\%$--$7.5\%$ at shares $.354$--$.466$.
 The zero-target share alone therefore does not predict cost.
 
-\paragraph{Support and constraint geometry.}
-With $E_{\min}=3$, $K_r\le3$ forces Uniform by the simplex norm bound.
-In the Complete-aligned station protocol this covers $78.6\%$ of 1877 SensorScope windows,
-$90.2\%$ of 1402 U-Air Design-on windows, and $79.0\%$ of 1515 Design-off
-windows.  Largest target groups carry only $.53\%/.79\%$.
-Across 3279 evaluated active windows the feasible L1 group-distance range has
-median $10^{-13}$; this does not make the squared L2 term in P2 constant.
-Appendix~\ref{app:arrival_support} separates missing, narrow-range, and
-adjustable target mass on nonempty arrival logs from these formal traces.
-
-Appendix~\ref{app:development_geometry} records three development trajectories
-(seeds 41001--41003, cap $.5$, ESS minimum 3). Their targets and client
-subsets differ from the formal arrival logs in
-Appendix~\ref{app:arrival_support}. For group range
-$W_{r,g}=\max_{\alpha\in\mathcal C_r}(M_r\alpha)_g-
-\min_{\alpha\in\mathcal C_r}(M_r\alpha)_g$, adjustable mass sums $\mu_g$
-where $W_{r,g}\ge.01$.
-Traffic's 183 sorted-client $K=8$ subsets (ESS 4, cap $.25$) all have a
-composition direction, but only $4.651\%$ mean adjustable target mass.
-References violate constraints in $59.02\%$, with mean projection distance
-$.067487$. The same appendix varies caps and ESS.
-
-\paragraph{Stabilization and reference sensitivity.}
-On observed SensorScope/U-Air client-windows, the $q_{\min}$ floor activates
-in $5.22\%/5.18\%$ and the inverse-usability ceiling in $24.22\%/23.75\%$.
-At true margins on active Design-on support, reference stabilization error
-has median zero and maximum $\ell_1$ values $.553/.680$
-(Supplementary Table~\ref{tab:app_a5_a6_audit}). The perturbation bound retains this error;
-A6a is sufficient for it to vanish. Shared support/state and A6b remain
-comparison conditions because the saved states omit active-set lists and
-estimated margins. The worst-case Design-on constant $L_\pi\le2\times10^{13}$
-is a loose envelope, rather than a tight numerical prediction of observed error
-(Proposition~\ref{prop:practical_plugin}; Appendix~\ref{app:a5_a6_audit}).
-
-Inside one calibrated member, replacing estimated observation/usability margins
-by truth changes RMSE by $-.008\%$ ($[-.041,+.025]\%$) on SensorScope and
-$+.040\%$ ($[-.090,+.171]\%$) on U-Air over 20 paired seeds.  Three U-Air
-members stay within $.3\%$, but TwoStage-H\'ajek lies $2.04\%$ above its
-oracle-margin counterpart ($[1.33,2.75]\%$). Reference perturbations
-(median $\ell_1=.077$, maximum $1.15$) can be appreciable even where prediction
-is insensitive.
-
-\paragraph{Prediction sensitivity.}
-For evaluated true-margin configurations, define
-$H=(\mathrm{RMSE}_{\mu}(\mathrm{FedAvg})-\mathrm{RMSE}_{\mu}(\mathrm{oracle}))/
-\mathrm{RMSE}_{\mu}(\mathrm{FedAvg})$.
-Varying opportunity tilt, tail observation, capacity, and target gives
-SensorScope estimates in $[-.03\%,+.08\%]$ with detectable effects
-$.17$--$.36$ percentage points.  U-Air's 270 runs/45 traces give
-$|H|\le.217\%$ with intervals containing zero; $.70$--$.80$ point detection
-leaves the $.5\%$ practical improvement unresolved.  These configurations
-are not optimal upper bounds over all feasible weights.
-
-\paragraph{Target concentration.}
-Table~\ref{tab:target_concentration} multiplies region1's prior mass by
-$\kappa_{\mathrm{tar}}$ and renormalizes, keeping the original backbone, two
-local steps, and server rule.  Local-H\'ajek is compared with RAVEN-SimOracle
-using generator observation probabilities and Monte Carlo usability
-probabilities through the full calibration path.  The baseline pair is reused;
-$5$ comes from the four-arm experiment; $10$ and the single-region limit are
-two further conditions, each with 20 paired seeds.  This target multiplier
-is unrelated to debt strength $\kappa$.
-
-\begin{table}[t]
-\centering
-\caption{Target-concentration sensitivity on NSW-Traffic.
-$D$ is control minus oracle test RMSE in the original standardized units;
-relative gain is $100\overline D/\overline{\mathrm{RMSE}}_{\mathrm{control}}$.
-Intervals and MDE use seed-paired analysis.}
-\label{tab:target_concentration}
-\scriptsize
-\setlength{\tabcolsep}{2.2pt}
-\begin{tabular}{lrrrr}
-\toprule
-$\kappa_{\mathrm{tar}}$ & Top region & $\overline D$ [95\% CI] & MDE$_{80}$ & Gain (\%)\\
-\midrule
-1 & $0.256$ & \shortstack{$0.000013$\\$[-0.000099,0.000148]$} & $0.000197$ & $0.0013$\\
-5 & $0.632$ & \shortstack{$0.000228$\\$[0.000055,0.000422]$} & $0.000289$ & $0.0225$\\
-10 & $0.775$ & \shortstack{$0.000462$\\$[0.000241,0.000708]$} & $0.000367$ & $0.0454$\\
-Single region & $1.000$ & \shortstack{$0.000994$\\$[0.000685,0.001337]$} & $0.000511$ & $0.0970$\\
-\bottomrule
-\end{tabular}
-\end{table}
-
-The oracle contrast increases to $.0970\%$ at the limit.  At $10$ and the
-limit its interval excludes zero and its mean exceeds MDE; at $5$ only the
-former holds.  All four effects remain below this experiment's $2\%$
-practical criterion.  Target dilution alone therefore does not explain the
-small gain of this oracle/update configuration.
-
-Appendix~\ref{app:learning_capacity} separates learning capacity from aggregation:
-formal station RMSE exceeds training-mean references, while independent development
+
+\paragraph{Reference sensitivity.}
+Stabilization contributes reference error in the conditional perturbation
+analysis: its median is zero but maxima reach $.553/.680$ in $\ell_1$ on
+SensorScope/U-Air. Replacing estimated margins can change reference mass
+appreciably while prediction remains insensitive (Appendix~\ref{app:a5_a6_audit}).
+Evaluated oracle configurations are sensitivity references, not predictive
+optima. Concentrating the Traffic target raises the observed oracle contrast
+to $.0970\%$, still below its $2\%$ practical criterion
+(Supplementary Table~\ref{tab:target_concentration}; Appendix~\ref{app:target_concentration}).
+Formal station RMSE exceeds training-mean references; separate development
 validation improves on simple baselines on Traffic/SensorScope, not U-Air.
-Update-rule sensitivities retain separate budgets (Appendix~\ref{app:update_rule_sensitivity}).
+Learning and update-rule budgets remain distinct (Appendix~\ref{app:learning_capacity}).
 
 Support determines represented group mass; cap and ESS bound its adjustment.
 Weight freedom, composition freedom, and prediction sensitivity remain distinct.

```

## appendix.tex

```diff
--- appendix.tex before
+++ appendix.tex after
@@ -748,7 +748,7 @@
 upper bound is $0.134\%$, below the pre-specified $3\%$ no-harm margin.
 The balanced experiment evaluates this criterion under aligned selection.
 
-\begin{table}[!t]
+\begin{table}[!htbp]
 \centering
 \caption{Balanced control over the five pre-specified paired seeds.}
 \label{tab:app_e1_balanced}
@@ -778,7 +778,7 @@
 risk-semantic premise that arrival-weighted and deployment-target-weighted
 views react differently to the same structured selection shift.
 
-\begin{table}[!t]
+\begin{table}[!htbp]
 \centering
 \caption{Complete-aligned risk non-interchangeability statistics.
 CI denotes the 95\% interval; $p$ is the paired Wilcoxon test of
@@ -840,7 +840,7 @@
 3596 on U-Air.  In every audited effective client-window, the realized
 within-client correction-weight range is 0.
 
-\begin{table}[!t]
+\begin{table}[!htbp]
 \centering
 \caption{Within-client weight constancy.}
 \label{tab:app_local_hajek}
@@ -905,7 +905,7 @@
 original construction; at $\theta_O=1$ they are regenerated with the same
 opportunity, delivery process, seeds, splits, and target maps.
 
-\begin{table}[t]
+\begin{table}[!htbp]
 \centering
 \caption{Within-stratum observation-probability diversity. Distinct probabilities are
 counted per opportunity stratum; entries are stratum means. The block marginal
@@ -936,7 +936,7 @@
 constraints whenever the necessary state is available.  Table~\ref{tab:app_p2_coverage}
 summarizes the dataset-level certificate coverage.
 
-\begin{table}[!t]
+\begin{table}[!htbp]
 \centering
 \caption{P2 feasibility-certificate coverage in the formal protocol blocks.}
 \label{tab:app_p2_coverage}
@@ -961,7 +961,7 @@
 The pre-specified solver-discrepancy rule uses $10^{-4}/10^{-3}$ thresholds.
 Stored P2 outputs were not re-solved.
 
-\begin{table}[!t]
+\begin{table}[!htbp]
 \centering
 \caption{Numerical feasibility of warning-affected P2 allocations.}
 \label{tab:app_p2_warning_audit}
@@ -998,23 +998,17 @@
 with maximum $9.64\times10^{-12}$. These diagnostics separate numerical
 feasibility and endpoint agreement from exact optimality.
 
-\FloatBarrier
+
 
 \section{Supplementary Experimental Comparisons}
 \label{app:additional_context}
 
-This section reports reference methods, baseline specifications, and additional
-target and selection protocols.  Prediction and oracle references carry
-$^\dagger$; the main inferential family consists of the deployable methods.
-
-The same-backbone family below uses Design on for both station blocks.
-Table~\ref{tab:main_effectiveness} separately reports both fixed Design settings
-on each dataset.
+Reference-only rows carry $^\dagger$; inference uses deployable methods.
+These station comparisons fix Design on; Table~\ref{tab:main_effectiveness}
+reports both configurations.
 
 \subsection{Windowed adaptations of FedAU, ObsUse, and TimeAlign}
 \label{app:adapted_baselines}
-FedAU-Window, ObsUse-Window, and TimeAlign-Agg adapt their weighting principles
-to the shared backbone and window-close protocol specified below.
 FedAU~\cite{wang2024lightweight} targets the original federated averaging
 objective under unknown participation; these rules reweight usable clients
 and do not recover that objective.
@@ -1072,7 +1066,16 @@
 \end{tabular}
 \end{table*}
 
-\begin{table}[t]
+\paragraph{Under-served-block validation.}
+\label{app:underserved_block}
+On validation only, aggregate target and opportunity mass to four UTC blocks
+and freeze $g^\star=\arg\max_b(\mu_b^{\mathrm{blk}}-
+\pi_b^{\mathrm{opp},4})$: block 2 on SensorScope and 3 on U-Air, with gaps
+$.114/.172$.  The required improvement against both FedAU and ObsUse is
+$-.5\%$.  Observed $+.05\%/+.15\%$ and $-.44\%/-.27\%$ miss that criterion
+while meeting no-harm (Supplementary Table~\ref{tab:underserved_block}).  
+
+\begin{table}[!htbp]
 \centering
 \caption{Validation RMSE in under-served UTC blocks.
 Relative changes (\%) over ten paired validation seeds versus
@@ -1120,9 +1123,6 @@
 
 \subsection{Full Method Context on the Comparable Datasets}
 \label{app:e3_full_context}
-
-Table~\ref{tab:app_e3_sensorscope} reports the full SensorScope
-prediction and structural endpoints.
 
 \begin{table}[!htbp]
 \centering
@@ -1205,7 +1205,7 @@
 The block applies the named heuristic to a local map; it does not transfer
 the SensorScope/U-Air support statistic.
 
-\begin{table}[t]
+\begin{table}[!htbp]
 \centering
 \caption{NSW-Traffic comparison under a four-region target.
 Mean $\pm$ SD over ten seeds; 100 windows; lower is better.
@@ -1282,8 +1282,7 @@
 \subsection{Runtime Diagnostic from Existing Risk-Semantic Logs}
 \label{app:runtime}
 
-Table~\ref{tab:app_runtime} reports wall-clock runtime for the evaluated
-workloads.  The ``all scenarios'' column aggregates six
+In Table~\ref{tab:app_runtime}, the ``all scenarios'' column aggregates six
 risk-semantic scenarios and 20 seeds (120 runs per method); the Complete-aligned column
 contains 20 runs per method.
 
@@ -1313,7 +1312,7 @@
 \subsection{Design-Induced Support Changes}
 \label{app:design_provenance}
 
-The Design ablation in Section~\ref{subsec:eval_rq3} exhibits an endpoint
+The end-to-end Design comparison in Section~\ref{subsec:rq1_alignment} exhibits an endpoint
 trade-off on U-Air. Across 774 paired windows, full RAVEN and w/o-Design share
 opportunity, observation, usable-update, and registration events. Removing the
 Design ratio changes positive-mass P2 support, so the end-to-end contrast
@@ -1429,29 +1428,15 @@
 
 \section{Support and Stabilization Conditions}
 \label{app:a5_a6_audit}
-
-A5, A6a, and A6b are separate. Proposition~\ref{prop:reconstruction} uses
-A1--A3. The perturbation form of Proposition~\ref{prop:practical_plugin} uses
-A1, A4, A5, and A6b with the shared-state and positive-mass conditions stated
-there. A6a is sufficient for $\varepsilon_{\mathrm{stab},r}=0$, but is not
-necessary when normalization cancels distortions. The statistics below use
-recorded margins on the selection traces.
-
-Twenty formal seeds give 16000 SensorScope and 12800 U-Air client-window
-records, of which 12346 and 9760 are observed.
-Table~\ref{tab:app_a5_a6_audit} substitutes the logged selection margins for
-the unlogged plug-ins $\widehat\pi^{\mathrm{opp}}$, $\widehat p^{\mathrm{obs}}$,
-and $\widehat q^{\mathrm{use}}$, at the constants these runs resolved:
-$p_{\min}=q_{\min}=0.05$, $\pi_{\min}=10^{-6}$, $a_{\max}=20$, and
-$d_{\max}=10$. These constants define the station-trace comparison analyzed here.
-
-Over all $28800$ records the observation rate takes only the block values
-$0.1925$ and $0.35$, so it is constant inside each opportunity stratum. The
-usable-update rate is drawn once per client-window and shared by at most four
-risk units, so it does not tilt a risk set. Neither margin varies by unit or
-by label on these traces.
-
-\begin{table}[!t]
+Proposition~\ref{prop:practical_plugin} uses A1, A4, A5, A6b and shared-state,
+positive-mass conditions; A6a suffices for zero stabilization error but is not required by the bound. Twenty seeds yield 16000/12800 SensorScope/U-Air
+client-windows (12346/9760 observed), with
+$p_{\min}=q_{\min}=.05$, $\pi_{\min}=10^{-6}$, $a_{\max}=20$, $d_{\max}=10$.
+The table uses true rather than unavailable estimated margins. Across 28800
+records, observation probabilities are block-constant $.1925/.35$;
+usable probability is shared by at most four risk units, without label dependence.
+
+\begin{table}[!htbp]
 \centering
 \caption{Support and stabilization on station traces.
 Floor/ceiling activation percentages use observed client-windows.
@@ -1480,57 +1465,71 @@
 \end{tabular*}
 \end{table}
 
-\noindent\textbf{Positive margins and recorded mass.} Opportunity and observation
-margins are positive throughout the traces; the smallest observed usable margin
-is $5.5\times10^{-3}$. The recorded observation/usability-weighted window mass
-has minima $5.521$ on SensorScope and $16.89$ on U-Air. This statistic precedes
-opportunity correction and therefore describes a different normalization mass
-from the full Design-on reference in \eqref{eq:beta_ref}.
-
-The one qualification is structural rather than numerical.  A usable-update
-margin of exactly zero occurs for $22.84\%$ of SensorScope and $23.75\%$ of
-U-Air client-windows.  Those cells are never observed and never usable, so
-they contribute neither to a corrected mass nor to any ratio: the count of
-zero-margin cells among observed client-windows is $0$ out of $12346$ and $0$
-out of $9760$.  Accordingly, A5's positivity condition is evaluated on the
-active support used by the estimator.
-
-\noindent\textbf{Active stabilization under A6a.}  The
-true usable margin falls below the floor $q_{\min}=0.05$ on $5.22\%$ of
-observed SensorScope and $5.18\%$ of observed U-Air client-windows, so the
-floor is active.  Similarly,
-$1/q^{\mathrm{use}}$ exceeds the ceiling $d_{\max}=10$ on $24.22\%$ and
-$23.75\%$ of observed client-windows; over all records, including the
-never-observed cells, the share with $q^{\mathrm{use}}<1/d_{\max}$ is
-$41.52\%$ and $41.86\%$.
-
-The observation-side clause bounds the composite weight and depends on the
-Design setting.  With Design off the composite
-equals $1/p^{\mathrm{obs}}$, whose largest value is $5.195$ because the
-observation rate takes only the block-level values $0.1925$ and $0.35$, so the
-clause holds on both datasets.  With Design on the composite is
-$\zeta/p^{\mathrm{obs}}$ with $\zeta=\pi^{\mathrm{tar}}/\pi^{\mathrm{opp}}$, and
-because the opportunity margin ranges down to $6.33\times10^{-4}$ it reaches
-$19.26$ on SensorScope and $23.47$ on U-Air, against the ceiling
-$a_{\max}=20$ used in these runs.  On U-Air, $2.74\%$ of active
-client-windows exceed this ceiling; SensorScope remains below it.  The
-Design-on condition is threshold-dependent: a ceiling of $40$ would contain
-both maxima, while the reported blocks use $20$.
-
-The stabilization error $\varepsilon_{\mathrm{stab}}$ in \eqref{eq:eps_stab}
-has median $0$, but is positive on $10.7\%$ (SensorScope) and $11.1\%$ (U-Air)
-of active windows, reaching $0.553$ and $0.680$ in reference $\ell_1$ distance.
-These errors enter Proposition~\ref{prop:practical_plugin} under its shared-state,
-positive-mass, and A6b conditions. Usability stabilization contributes most of
-the error; with Design on, the opportunity composite ceiling also contributes.
-
-\noindent\textbf{Analysis inputs and conditions.} The statistics use true margins
-over 20 fixed seeds. Shared $\mathcal A_r$, $M_r$, and $\mathcal C_r$, and
-positive full-reference normalization mass remain conditions of the perturbation
-comparison. Stored P2 states omit active-set lists, and the estimated margins
-needed to evaluate A6b and realized plug-in error are unavailable. The reported
-$\varepsilon_{\mathrm{stab}}$ is evaluated at the true margins.
-
+\noindent\textbf{Support and mass.}
+Minimum observed usable margin is $.0055$. Pre-opportunity mass minima
+$5.521/16.89$ differ from full-reference mass. Zero usable margins occur
+in $22.84\%/23.75\%$ of all client-windows but none of 12346/9760 observed
+records: never-observed/usable cells are outside estimator support.
+
+\noindent\textbf{Stabilization and conditions.}
+Including unobserved cells, $q^{\mathrm{use}}<1/d_{\max}$ occurs in
+$41.52\%/41.86\%$. Table maxima $19.26/23.47$ exceed ceiling $20$ only for
+$2.74\%$ of active U-Air client-windows; ceiling $40$ would contain both.
+True-margin stabilization error is positive on $10.7\%/11.1\%$ of active
+windows (median $0$, maximum $.553/.680$), mainly from usability with an
+additional Design-on opportunity contribution. The worst-case
+$L_\pi\le2\times10^{13}$ is loose. Shared $\mathcal A_r,M_r,\mathcal C_r$,
+positive reference mass and A6b remain conditions: saved states omit
+active-set lists and estimated margins, preventing A6b and plug-in-error checks.
+
+\paragraph{Reference and Prediction Sensitivity.}
+\label{app:reference_sensitivity}
+On 20 paired seeds, true observation/usability margins change calibrated
+RMSE by $-.008\%$ ($[-.041,+.025]\%$) on SensorScope and $+.040\%$
+($[-.090,+.171]\%$) on U-Air. Three U-Air members stay within $.3\%$;
+TwoStage-H\'ajek is $2.04\%$ above its oracle counterpart ($[1.33,2.75]\%$).
+Reference $\ell_1$ perturbations have median $.077$, maximum $1.15$.
+For $H=(\mathrm{RMSE}_{\mu}(\mathrm{FedAvg})-\mathrm{RMSE}_{\mu}(\mathrm{oracle}))/
+\mathrm{RMSE}_{\mu}(\mathrm{FedAvg})$, varying opportunity tilt, tail observation,
+capacity and target yields SensorScope effects $[-.03\%,+.08\%]$ (detectable
+$.17$--$.36$ pp). U-Air's 270 runs/45 traces give $|H|\le.217\%$ with
+zero-containing intervals; $.70$--$.80$ pp detection leaves $.5\%$ improvement
+unresolved. These are evaluated configurations, not predictive optima.
+
+\paragraph{Target-Concentration Sensitivity.}
+\label{app:target_concentration}
+
+Table~\ref{tab:target_concentration} multiplies region1's prior mass by
+$\kappa_{\mathrm{tar}}$ then renormalizes, retaining backbone, two local steps
+and server rule. Local-H\'ajek versus full-path RAVEN-SimOracle uses generator
+observation and Monte Carlo usability probabilities. Baseline runs are reused;
+$5$ uses the four-arm experiment; $10$ and single-region conditions each add
+20 paired seeds. This multiplier differs from debt strength $\kappa$.
+
+\begin{table}[!htbp]
+\centering
+\caption{Target-concentration sensitivity on NSW-Traffic.
+$D$ is control minus oracle test RMSE in the original standardized units;
+relative gain is $100\overline D/\overline{\mathrm{RMSE}}_{\mathrm{control}}$.
+Intervals and MDE use seed-paired analysis.}
+\label{tab:target_concentration}
+\scriptsize
+\setlength{\tabcolsep}{2.2pt}
+\begin{tabular}{lrrrr}
+\toprule
+$\kappa_{\mathrm{tar}}$ & Top region & $\overline D$ [95\% CI] & MDE$_{80}$ & Gain (\%)\\
+\midrule
+1 & $0.256$ & \shortstack{$0.000013$\\$[-0.000099,0.000148]$} & $0.000197$ & $0.0013$\\
+5 & $0.632$ & \shortstack{$0.000228$\\$[0.000055,0.000422]$} & $0.000289$ & $0.0225$\\
+10 & $0.775$ & \shortstack{$0.000462$\\$[0.000241,0.000708]$} & $0.000367$ & $0.0454$\\
+Single region & $1.000$ & \shortstack{$0.000994$\\$[0.000685,0.001337]$} & $0.000511$ & $0.0970$\\
+\bottomrule
+\end{tabular}
+\end{table}
+
+At $10$ and the single-region limit, intervals exclude zero and means exceed
+MDE; at $5$ only intervals exclude zero. All effects remain below the $2\%$
+criterion, so target dilution alone does not explain this configuration's small gain.
 
 \section{Coverage Diagnostics under Availability Stress}
 \label{app:certificate_audit}
@@ -1621,7 +1620,7 @@
 This chart is not the experiments' online rule. Both fixed Design settings
 remain reported where their trade-off matters.
 
-\begin{table}[t]
+\begin{table}[!htbp]
 \centering
 \caption{Offline zero-target counts for attached clients.
 Frozen $\pi^{\mathrm{tar}}(k(i),s(i))$; missing keys count as zero.
@@ -1696,7 +1695,7 @@
 training, without responses/errors. Table~\ref{tab:cityscanner_sixarm}
 summarizes ten within-trace model-seed means.
 
-\begin{table}[t]
+\begin{table}[!htbp]
 \centering
 \caption{Client--stratum gaps across City Scanner target maps.
 Mean $\pm$ SD over ten trace means, each using three model seeds.
@@ -1747,17 +1746,15 @@
 \section{Learning Capacity and Update-Rule Sensitivity}
 \label{app:learning_capacity}
 
-Development validation uses seeds 41001--41003, separate from the main test
-comparisons. Central-delivered pools supply the training observations. Both
-backbones run 200 effective passes with Adam rates $.0003,.001,.003$ or
-momentum-SGD rates $.001,.01,.03$, batch size 64, and factor-.3 decay after
-passes 50, 100, and 150; validation selects each seed's best checkpoint. HistoryResidual
-adds a 64/32 history network and a training-statistic residual to
-Common-NDMF: 108 central runs, one Traffic Uniform run, and three U-Air
-Central-all diagnostics. In Fig.~\ref{fig:learning_capacity}, Common-NDMF
-uses Adam $.003$ on Traffic/SensorScope and SGD $.03$ on U-Air;
-HistoryResidual uses Adam $.003/.001/.003$ on Traffic/SensorScope/U-Air,
-respectively.
+Development seeds 41001--41003 use central-delivered training pools,
+separate from main TEST. Both backbones run 200 effective passes, batch 64,
+with Adam rates $.0003/.001/.003$ or momentum-SGD $.001/.01/.03$;
+factor-.3 decay occurs at passes 50/100/150, and validation selects checkpoints.
+HistoryResidual adds a 64/32 history network and training-statistic residual
+to Common-NDMF. Counts are 108 central runs, one Traffic Uniform run and
+three U-Air Central-all diagnostics. Figure~\ref{fig:learning_capacity} uses
+Common-NDMF Adam $.003$ on Traffic/SensorScope, SGD $.03$ on U-Air;
+HistoryResidual Adam $.003/.001/.003$, respectively.
 
 \begin{table*}[t]
 \centering
@@ -1788,17 +1785,13 @@
 \label{fig:learning_capacity}
 \end{figure*}
 
-Figure~\ref{fig:learning_capacity} separates training and validation trajectories.
-Training, spatial, and seasonal means, persistence, and seasonal-naive
-predictors use delivered training labels only. Persistence repeats the latest
-legal observation; seasonal naive repeats the latest phase, and a weekly
-comparison needs two training weeks. Validation labels stay out of history.
-Scores are inverse-scaled to float64 physical targets.
-HistoryResidual gains are $7.33\%$ on Traffic and $-0.34\%/-4.45\%$ on
-SensorScope/U-Air. U-Air Central-all averages $19.5427$ against the spatial
-reference $18.4567$. Traffic Uniform reaches $253.1132$ vehicles/h ($33.70\%$
-improvement) and is still improving $0.914\%$ from passes 100 to 200.
-
+Baselines use delivered training labels: means (training/spatial/seasonal),
+persistence (latest legal observation) and seasonal naive (latest phase;
+weekly needs two training weeks). Validation never enters history; scores
+are inverse-scaled to float64 physical targets. HistoryResidual gains are
+$7.33\%/-0.34\%/-4.45\%$ on Traffic/SensorScope/U-Air. U-Air Central-all
+scores $19.5427$ versus spatial reference $18.4567$. Traffic Uniform reaches
+$253.1132$ vehicles/h ($33.70\%$ improvement), improving $.914\%$ over passes 100--200.
 
 \subsection{Formal-Protocol Prediction References}
 \label{app:formal_prediction_references}
@@ -1873,7 +1866,7 @@
 $[2.220\%,2.283\%]$ on SensorScope and $[2.938\%,3.020\%]$ on U-Air
 ($10{,}000$ resamples, seed $20261019$).
 
-\begin{table}[t]
+\begin{table}[!htbp]
 \centering
 \caption{Arrival-log geometry. Masses are percentages of positive target
 mass. L1 is the shared minimum $\ell_1$ distance on $M^{\mathrm{arr}}$.}
@@ -1916,7 +1909,7 @@
 renormalized reference. Feasible ranges separate weight freedom from mass
 adjustable by at least .01, without prediction re-evaluation.
 
-\begin{table}[t]
+\begin{table}[!htbp]
 \centering
 \caption{Natural-window geometry under the separate development protocol.
 Seeds 41001--41003, cap .5, ESS minimum 3.}
@@ -1934,7 +1927,7 @@
 \end{tabular}
 \end{table}
 
-\begin{table}[t]
+\begin{table}[!htbp]
 \centering
 \caption{NSW-Traffic geometry under cap and ESS changes.
 183 fixed-$K=8$ subsets. $E$: minimum ESS; cap: maximum weight;
@@ -1990,7 +1983,7 @@
 Rolling reference and the fixed reference use $\kappa_{\mathrm{stop}}=0$; Rolling + stop debt uses $.1$.
 All retain P2's $\mathbf Q$ and its updates.
 
-\begin{table}[t]
+\begin{table}[!htbp]
 \centering
 \caption{Traffic release-control diagnostics.
 One development seed; $G$, $W$, and $J$: lower is better.}

```

## supplemental.tex

```diff
--- supplemental.tex before
+++ supplemental.tex after
@@ -74,12 +74,12 @@
 and provides its proofs and supporting analyses.}
 
 % Continue figure/table/equation numbers from the companion main paper.
-% Main has 4 figures, 8 tables, 1 algorithm and 41 numbered equations.
+% Main has 4 figures, 7 tables, 1 algorithm and 41 numbered equations.
 % The development-geometry summary now lives in this file.
 % Offline support and retrospective switch equations are in Appendix J.
 % Numbered statements in main: four propositions, two theorems, one assumption.
 \setcounter{figure}{4}
-\setcounter{table}{8}
+\setcounter{table}{7}
 \setcounter{algorithm}{1}
 \setcounter{equation}{41}
 \setcounter{proposition}{4}

```

