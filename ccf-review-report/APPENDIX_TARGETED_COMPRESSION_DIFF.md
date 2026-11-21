# 附录定点修复与压缩：完整源码差异

相对于本轮当前稿备份，保留此前用户修改。

## main.tex

`diff
--- main.tex before
+++ main.tex after
@@ -1698,24 +1698,20 @@
 (Appendix~\ref{app:cityscanner_sixarm}). Client--stratum targets are arm-specific
 (Supplementary Table~\ref{tab:cityscanner_sixarm_cs}).
 
-Target-map effects also depend on which groups the support represents.
-In the retrospective comparison (Appendix~\ref{app:cityscanner_phi}), masking
-SensorScope keys gives at most $.175\%$ cost at zero-target share $.388$,
-whereas U-Air costs $6.6\%$--$7.5\%$ at shares $.354$--$.466$.
-The zero-target share alone therefore does not predict cost.
-
-
 \paragraph{Reference sensitivity.}
 Stabilization contributes reference error in the conditional perturbation
 analysis: its median is zero but maxima reach $.553/.680$ in $\ell_1$ on
-SensorScope/U-Air. Replacing estimated margins can change reference mass
-appreciably while prediction remains insensitive (Appendix~\ref{app:a5_a6_audit}).
+SensorScope/U-Air (Appendix~\ref{app:a5_a6_audit}). Replacing estimated margins
+can change reference mass appreciably while prediction remains insensitive
+(Appendix~\ref{app:reference_sensitivity}).
 Evaluated oracle configurations are sensitivity references, not predictive
 optima. Concentrating the Traffic target raises the observed oracle contrast
 to $.0970\%$, still below its $2\%$ practical criterion
 (Supplementary Table~\ref{tab:target_concentration}; Appendix~\ref{app:target_concentration}).
-Formal station RMSE exceeds training-mean references; separate development
-validation improves on simple baselines on Traffic/SensorScope, not U-Air.
+Formal station RMSE exceeds training-mean references
+(Appendix~\ref{app:formal_prediction_references}); separate development validation
+improves on simple baselines on Traffic/SensorScope, not U-Air
+(Appendix~\ref{app:learning_capacity}).
 Learning and update-rule budgets remain distinct
 (Appendices~\ref{app:learning_capacity} and~\ref{app:update_rule_sensitivity}).
 

`

## appendix.tex

`diff
--- appendix.tex before
+++ appendix.tex after
@@ -1117,6 +1117,37 @@
 \end{tabular*}
 \end{table*}
 
+\begin{table*}[t]
+\centering
+\caption{Station-protocol comparison under intermittent opportunities.
+Mean $\pm$ SD over 20 paired seeds; lower is better.
+RAVEN's fixed Design settings are listed per row.}
+\label{tab:int_r_e3}
+\scriptsize
+\setlength{\tabcolsep}{1pt}
+\begin{tabular*}{\textwidth}{@{\extracolsep{\fill}}llcccc}
+\toprule
+Dataset & Method & $\mathrm{RMSE}_{\mu}$ & WorstGroupRMSE &
+$\Delta_{\mathrm{group}}$ & $\Delta_{c\text{-}s}$\\
+\midrule
+\multirow{5}{*}{SensorScope}
+& FedAvg-Window     & \shortstack{$7.9373$\\$\pm0.0960$} & \shortstack{$8.6716$\\$\pm0.0976$} & \shortstack{$1.3411$\\$\pm0.0580$} & \shortstack{$1.5866$\\$\pm0.0445$}\\
+& TwoStage-H\'ajek    & \shortstack{$7.9362$\\$\pm0.0956$} & \shortstack{$8.6696$\\$\pm0.0957$} & \shortstack{$1.3558$\\$\pm0.0545$} & \shortstack{$1.5941$\\$\pm0.0415$}\\
+& FedAU-Window      & \shortstack{$7.9335$\\$\pm0.1036$} & \shortstack{$8.6678$\\$\pm0.1044$} & \shortstack{$1.3540$\\$\pm0.0541$} & \shortstack{$1.5978$\\$\pm0.0425$}\\
+& ObsUse-Window     & \shortstack{$7.9305$\\$\pm0.1047$} & \shortstack{$8.6647$\\$\pm0.1054$} & \shortstack{$1.3560$\\$\pm0.0534$} & \shortstack{$1.5983$\\$\pm0.0421$}\\
+& RAVEN-Design & \shortstack{$7.9407$\\$\pm0.0957$} & \shortstack{$8.6746$\\$\pm0.0972$} & \shortstack{$\mathbf{1.3272}$\\$\pm0.0607$} & \shortstack{$1.5859$\\$\pm0.0443$}\\
+\midrule
+\multirow{6}{*}{U-Air}
+& FedAvg-Window     & \shortstack{$1.1121$\\$\pm0.0873$} & \shortstack{$1.1682$\\$\pm0.1022$} & \shortstack{$1.3141$\\$\pm0.0679$} & \shortstack{$1.5786$\\$\pm0.0602$}\\
+& TwoStage-H\'ajek    & \shortstack{$1.1555$\\$\pm0.1027$} & \shortstack{$1.2179$\\$\pm0.1079$} & \shortstack{$1.4393$\\$\pm0.0613$} & \shortstack{$1.5694$\\$\pm0.0631$}\\
+& FedAU-Window      & \shortstack{$1.1126$\\$\pm0.0845$} & \shortstack{$1.1689$\\$\pm0.0985$} & \shortstack{$1.3319$\\$\pm0.0690$} & \shortstack{$1.5951$\\$\pm0.0597$}\\
+& ObsUse-Window     & \shortstack{$1.1126$\\$\pm0.0853$} & \shortstack{$1.1689$\\$\pm0.0995$} & \shortstack{$1.3304$\\$\pm0.0693$} & \shortstack{$1.5947$\\$\pm0.0604$}\\
+& RAVEN-Design & \shortstack{$1.1528$\\$\pm0.1005$} & \shortstack{$1.2148$\\$\pm0.1040$} & \shortstack{$1.4134$\\$\pm0.0725$} & \shortstack{$\mathbf{1.5632}$\\$\pm0.0663$}\\
+& RAVEN-NoDesign & \shortstack{$1.1120$\\$\pm0.0880$} & \shortstack{$1.1680$\\$\pm0.1031$} & \shortstack{$\mathbf{1.2959}$\\$\pm0.0746$} & \shortstack{$1.5672$\\$\pm0.0638$}\\
+\bottomrule
+\end{tabular*}
+\end{table*}
+
 \subsection{Under-Served-Block Validation}
 \label{app:underserved_block}
 On validation only, aggregate target and opportunity mass to four UTC blocks
@@ -1157,6 +1188,9 @@
 
 \subsection{Intermittent Opportunity Protocol}
 \label{app:int_r}
+
+
+
 
 Table~\ref{tab:main_effectiveness} uses always-on Complete-aligned opportunity.
 This ranking keeps the SensorScope and U-Air station arrays, the public
@@ -1227,41 +1261,6 @@
 Every method also has higher absolute $\Delta_{\mathrm{group}}$ than in
 Table~\ref{tab:main_effectiveness}, about $1.33$ versus $1.01$ on SensorScope.
 
-\begin{table*}[t]
-\centering
-\caption{Station-protocol comparison under intermittent opportunities.
-Mean $\pm$ SD over 20 paired seeds; lower is better.
-RAVEN's fixed Design settings are listed per row.}
-\label{tab:int_r_e3}
-\scriptsize
-\setlength{\tabcolsep}{1pt}
-\begin{tabular*}{\textwidth}{@{\extracolsep{\fill}}llcccc}
-\toprule
-Dataset & Method & $\mathrm{RMSE}_{\mu}$ & WorstGroupRMSE &
-$\Delta_{\mathrm{group}}$ & $\Delta_{c\text{-}s}$\\
-\midrule
-\multirow{5}{*}{SensorScope}
-& FedAvg-Window     & \shortstack{$7.9373$\\$\pm0.0960$} & \shortstack{$8.6716$\\$\pm0.0976$} & \shortstack{$1.3411$\\$\pm0.0580$} & \shortstack{$1.5866$\\$\pm0.0445$}\\
-& TwoStage-H\'ajek    & \shortstack{$7.9362$\\$\pm0.0956$} & \shortstack{$8.6696$\\$\pm0.0957$} & \shortstack{$1.3558$\\$\pm0.0545$} & \shortstack{$1.5941$\\$\pm0.0415$}\\
-& FedAU-Window      & \shortstack{$7.9335$\\$\pm0.1036$} & \shortstack{$8.6678$\\$\pm0.1044$} & \shortstack{$1.3540$\\$\pm0.0541$} & \shortstack{$1.5978$\\$\pm0.0425$}\\
-& ObsUse-Window     & \shortstack{$7.9305$\\$\pm0.1047$} & \shortstack{$8.6647$\\$\pm0.1054$} & \shortstack{$1.3560$\\$\pm0.0534$} & \shortstack{$1.5983$\\$\pm0.0421$}\\
-& RAVEN-Design & \shortstack{$7.9407$\\$\pm0.0957$} & \shortstack{$8.6746$\\$\pm0.0972$} & \shortstack{$\mathbf{1.3272}$\\$\pm0.0607$} & \shortstack{$1.5859$\\$\pm0.0443$}\\
-\midrule
-\multirow{6}{*}{U-Air}
-& FedAvg-Window     & \shortstack{$1.1121$\\$\pm0.0873$} & \shortstack{$1.1682$\\$\pm0.1022$} & \shortstack{$1.3141$\\$\pm0.0679$} & \shortstack{$1.5786$\\$\pm0.0602$}\\
-& TwoStage-H\'ajek    & \shortstack{$1.1555$\\$\pm0.1027$} & \shortstack{$1.2179$\\$\pm0.1079$} & \shortstack{$1.4393$\\$\pm0.0613$} & \shortstack{$1.5694$\\$\pm0.0631$}\\
-& FedAU-Window      & \shortstack{$1.1126$\\$\pm0.0845$} & \shortstack{$1.1689$\\$\pm0.0985$} & \shortstack{$1.3319$\\$\pm0.0690$} & \shortstack{$1.5951$\\$\pm0.0597$}\\
-& ObsUse-Window     & \shortstack{$1.1126$\\$\pm0.0853$} & \shortstack{$1.1689$\\$\pm0.0995$} & \shortstack{$1.3304$\\$\pm0.0693$} & \shortstack{$1.5947$\\$\pm0.0604$}\\
-& RAVEN-Design & \shortstack{$1.1528$\\$\pm0.1005$} & \shortstack{$1.2148$\\$\pm0.1040$} & \shortstack{$1.4134$\\$\pm0.0725$} & \shortstack{$\mathbf{1.5632}$\\$\pm0.0663$}\\
-& RAVEN-NoDesign & \shortstack{$1.1120$\\$\pm0.0880$} & \shortstack{$1.1680$\\$\pm0.1031$} & \shortstack{$\mathbf{1.2959}$\\$\pm0.0746$} & \shortstack{$1.5672$\\$\pm0.0638$}\\
-\bottomrule
-\end{tabular*}
-\end{table*}
-
-\paragraph{Scope of the supplementary evidence.}
-The INT-R block uses the same two station datasets as
-Table~\ref{tab:main_effectiveness} with intermittent protocol opportunities, isolating sensitivity to
-the opportunity process on the same sensing data.
 
 
 \section{Mechanism Analysis and Numerical Calibration Details}
@@ -1270,6 +1269,25 @@
 
 \subsection{Local-H\'ajek Weight Cancellation}
 \label{app:local_hajek}
+
+\begin{table}[!htbp]
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
 
 The equality between Local-Hajek and FedAvg in the formal SensorScope/U-Air
 blocks is protocol-specific and should not be interpreted as a general
@@ -1278,23 +1296,7 @@
 3596 on U-Air.  In every audited effective client-window, the realized
 within-client correction-weight range is 0.
 
-\begin{table}[!t]
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
+
 
 The collapse follows directly from the normalized local objective.  Let
 $\mathcal I_{k,r}^{+}$ be the records retained by an effective client-window
@@ -1343,7 +1345,7 @@
 original construction; at $\theta_O=1$ they are regenerated with the same
 opportunity, delivery process, seeds, splits, and target maps.
 
-\begin{table}[!t]
+\begin{table}[!htbp]
 \centering
 \caption{Within-stratum observation-probability diversity. Distinct probabilities are
 counted per opportunity stratum; entries are stratum means. The block marginal
@@ -1977,62 +1979,3 @@
 distance, not .01-threshold adjustable mass. No forecasts or label-dependent
 choices enter this diagnostic.
 
-\subsection{Release-Timing Reference Study}
-\label{app:release_timing}
-
-Table~\ref{tab:release_timing} compares release rules on Traffic TRAIN, development seed 45001, and Common-NDMF
-with normalized local SGD. Policies share $T=100$, a $.1$ grid, fixed-time-1 warm-up
-through $t=20$, maximum window 4, version-age limit 5, and three clients for
-non-forced closure. Design is on; Gate is diagnostic. Fixed reference
-branches from the common $t=20$ model, message pool, and random streams.
-Local H\'ajek-SGD (one step) and the server rate are $.01$. P2 uses
-group/reference coefficients $1/1$, variance/staleness coefficients $.1/.1$,
-cap $\max(.5,1/K)$, ESS minimum $\min(3,K)$, $d_{\max}=10$, $q_{\min}=.05$,
-variance floor $10^{-4}$, and maximum server rate 1. Observation stabilization
-uses $a_{\max}=20$, $p_{\min}=.05$, and $\pi_{\min}=10^{-6}$. Here $q=.5$ is a
-diagnostic prior. Predictive accuracy is not evaluated.
-
-With actual P2 weights, $\ell_t=\tfrac12\|M_t\boldsymbol\alpha_t-\boldsymbol\mu\|_1$,
-$a_t$ is weighted version age divided by 5, and $c_t=\ell_t+.02a_t$.
-With $u_t=\operatorname{clip}((t-o_t)/4,0,1)$ and
-$b_t=\mathbf Q_t^\top(M_t\boldsymbol\alpha_t-\boldsymbol\mu)/(1+\|\mathbf Q_t\|_1)$,
-$B_t^{\mathrm{roll}}=c_{L_t}-c_t+\kappa_{\mathrm{stop}}b_t+.20u_t$ and
-$B_t^{\mathrm{fix}}=c_{\mathrm{ref}}-c_t+.20u_t$.
-The rolling reference $c_{L_t}$ uses the last nonempty release.
-The fixed reference $c_{\mathrm{ref}}\approx.916837$ uses the $t=20$
-release's $\ell\approx.906977$ and $a\approx.492992$.
-Saved releases do not re-age.
-Both rules close when $B_t\ge.02+10^{-7}$, subject to terminal, warm-up,
-deadline, and minimum-client priorities in that order.
-Rolling reference and the fixed reference use $\kappa_{\mathrm{stop}}=0$; Rolling + stop debt uses $.1$.
-All retain P2's $\mathbf Q$ and its updates.
-
-\begin{table}[!htbp]
-\centering
-\caption{Traffic release-control diagnostics.
-One development seed; $G$, $W$, and $J$: lower is better.}
-\label{tab:release_timing}
-\footnotesize
-\setlength{\tabcolsep}{3pt}
-\begin{tabular*}{\columnwidth}{@{\extracolsep{\fill}}lrrr}
-\toprule
-Policy & $G$ & $W$ & $J$\\
-\midrule
-Rolling + stop debt & .945218 & .601504 & .989880\\
-Rolling reference & .945218 & .601504 & .989880\\
-Fixed reference & .919375 & .860215 & .974163\\
-Fixed time 0.5 & .958859 & .506329 & .997309\\
-Fixed time 2 & .843083 & 2.000000 & .949308\\
-\bottomrule
-\end{tabular*}
-\end{table}
-
-$G$ is the last nonempty release's $\ell$ over 800 grids (20.1--100). $W$ is
-mean positive post-20 duration, including empty and terminal closures, in
-logical window time. $J$ averages $\ell+.02a+.20\,\mathrm{duration}/4$ on
-nonempty post-20 releases. Fixed-reference shadows flip 129/799 actions
-(16.1452\%), all rolling CLOSE to fixed WAIT (129/582 free states, 22.1649\%).
-Rolling minus fixed averages $.0395584$ (median $.0405236$). Rolling reference
-lowers $W$ by $30.0752\%$ and raises $G$ by $.0258430$ versus the fixed reference, so neither
-improves both. Rolling + stop debt matches it on this seed.
-

`

## supplemental.tex

没有修改。

