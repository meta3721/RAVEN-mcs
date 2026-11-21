# City Scanner本轮规范源差异

以当前工作树为起点，不回退其他AI修复。

## main.tex

```diff
--- current-start/main.tex
+++ current/main.tex
@@ -86,8 +86,9 @@
 reduces group mismatch by $0.768$ percentage points relative to Uniform.
 Structural alignment does not consistently improve prediction, and projection
 can achieve lower group mismatch and runtime than the full RAVEN criterion.
-These findings separate the roles of population reconstruction and finite-window
-calibration in federated completion.
+City Scanner comparisons with real opportunities and, separately, measured
+observation likewise show group-alignment advantages with protocol-dependent
+prediction trade-offs; delivery remains controlled.
 \end{abstract}
 
 \begin{IEEEkeywords}
@@ -188,8 +189,11 @@
     every improvement to the full objective.
 \end{itemize}
 
-The main comparison (Table~\ref{tab:main_effectiveness}) and matched-support
-rules (Table~\ref{tab:trained_rules}) address different contrasts.  On
+City Scanner provides real-opportunity and measured-observation evidence
+(Table~\ref{tab:cityscanner_real}), with different prediction leaders across
+protocols despite RAVEN's group-alignment advantage. Controlled station
+comparisons (Tables~\ref{tab:main_effectiveness} and~\ref{tab:trained_rules})
+identify the roles of reference reconstruction and feasible calibration.  On
 SensorScope, projection improves group mismatch by $0.768$ pp versus Uniform.
 A separate same-support projected Design-on/off comparison gives $0.922$ pp.
 These effects are not additive.  Six selection scenarios test risk semantics,
@@ -1271,6 +1275,68 @@
 prose; Holm tests use all 20.  It is not a non-inferiority proof.
 Balanced-control, oracle-sensitivity, and concentration criteria retain their
 distinct thresholds below.
+
+\subsection{Real Sensing Opportunities and Measured Observation}
+\label{subsec:cityscanner_real}
+
+Table~\ref{tab:cityscanner_real} compares completion under real sensing
+opportunities. Both blocks predict {PM}$_{2.5}$, but use different data,
+targets, and sensing protocols.
+Their clients are occupied grid cells. Design is fixed on and the coverage
+Gate is unused. Usable-update delivery remains controlled in both blocks.
+Appendices~\ref{app:cityscanner_nyc}--\ref{app:cityscanner_p2_measured_o}
+give construction, filtering, and splits.
+
+\begin{table*}[t]
+\centering
+\caption{City Scanner {PM}$_{2.5}$ completion under two distinct sensing protocols
+(mean $\pm$ SD, ten paired seeds and 100 windows per block; lower is better).
+Clients are occupied $500$\,m $\times$ $30$\,min grid cells, not vehicles.
+Prediction errors use each block's own training-only $z$-score scale, not
+$\mu$g/m$^3$ or a shared cross-block scale. WorstGroupRMSE is the maximum over
+four coordinate quadrants. Bold marks each block's endpoint minimum.}
+\label{tab:cityscanner_real}
+\label{tab:cityscanner_hybrid}
+\label{tab:cityscanner_p2_measured_o}
+\footnotesize
+\begin{tabular*}{\textwidth}{@{\extracolsep{\fill}}lcccc@{}}
+\toprule
+Protocol / method & $\mathrm{RMSE}_{\mu}$ & WorstGroupRMSE & $\Delta_{\mathrm{group}}$ & $\Delta_{c\text{-}s}$\\
+\midrule
+\multicolumn{5}{l}{(a) New York visit occupancy: real $R$, controlled $O/U$}\\
+FedAvg-Window & $\mathbf{0.2379}{\pm}0.0839$ & $\mathbf{0.2489}{\pm}0.0856$ & $0.1953{\pm}0.0342$ & $0.8123{\pm}0.0191$\\
+TwoStage-H\'ajek & $0.2510{\pm}0.1044$ & $0.2629{\pm}0.1068$ & $0.0952{\pm}0.0307$ & $\mathbf{0.5305}{\pm}0.0286$\\
+FedAU-Window & $0.2582{\pm}0.1028$ & $0.2700{\pm}0.1048$ & $0.3216{\pm}0.0412$ & $1.1403{\pm}0.0538$\\
+ObsUse-Window & $0.2566{\pm}0.1004$ & $0.2685{\pm}0.1023$ & $0.3187{\pm}0.0414$ & $1.1369{\pm}0.0547$\\
+RAVEN-Design & $0.2549{\pm}0.1057$ & $0.2671{\pm}0.1079$ & $\mathbf{0.0706}{\pm}0.0266$ & $0.5676{\pm}0.0311$\\
+\midrule
+\multicolumn{5}{l}{(b) New York Pilot 2: union-GPS $R$, measured $O$, controlled $U$}\\
+FedAvg-Window & $0.7182{\pm}0.0208$ & $0.7359{\pm}0.0204$ & $0.0769{\pm}0.0231$ & $0.7066{\pm}0.0162$\\
+TwoStage-H\'ajek & $\mathbf{0.7097}{\pm}0.0204$ & $\mathbf{0.7273}{\pm}0.0200$ & $0.0607{\pm}0.0206$ & $\mathbf{0.3893}{\pm}0.0265$\\
+FedAU-Window & $0.7173{\pm}0.0289$ & $0.7351{\pm}0.0291$ & $0.2283{\pm}0.0433$ & $1.0034{\pm}0.0383$\\
+ObsUse-Window & $0.7175{\pm}0.0288$ & $0.7352{\pm}0.0290$ & $0.2314{\pm}0.0429$ & $1.0059{\pm}0.0380$\\
+RAVEN-Design & $0.7135{\pm}0.0206$ & $0.7311{\pm}0.0200$ & $\mathbf{0.0465}{\pm}0.0119$ & $0.4172{\pm}0.0214$\\
+\bottomrule
+\end{tabular*}
+\end{table*}
+
+With real visit occupancy and controlled observation, RAVEN minimizes group
+mismatch ($.0706$), while TwoStage-H\'ajek minimizes client--stratum mismatch.
+RAVEN's seed-paired mean relative RMSE is
+$1.71\%/1.34\%$ lower than FedAU/ObsUse, with worst-group reductions
+$1.56\%/1.23\%$. FedAvg predicts best on both endpoints.
+Against this count-weighted baseline, RAVEN's $5.59\%$ higher paired RMSE
+shows that improved group alignment can carry a prediction cost.
+
+Pilot~2 measures observation from finite {PM}$_{2.5}$ on union GPS occupancy,
+where {NO}$_2$ contributes locations without supplying prediction labels.
+RAVEN again has
+the smallest group mismatch ($.0465$), and its paired RMSE is
+$.43\%/ .45\%/ .65\%$ lower than FedAU/ObsUse/FedAvg. TwoStage-H\'ajek
+predicts best on both endpoints. It also minimizes client--stratum mismatch.
+The declared $-.5\%$ improvement criterion against both FedAU and ObsUse
+is not met. The cross-block differences cannot be attributed solely to
+measuring $O$, because the data and targets also change.
 
 \subsection{Risk Semantics and External Protocols}
 \label{subsec:eval_rq1}
@@ -1355,25 +1421,10 @@
 $.1048$); RAVEN stays within the descriptive worst-group tolerance against
 FedAU/ObsUse.  It does not validate a transferred station lookup.
 
-City Scanner visit occupancy (Appendix~\ref{app:cityscanner_nyc}) gives RAVEN
-relative RMSE gains of $1.71\%/1.34\%$ and worst-group gains of
-$1.56\%/1.23\%$ against FedAU/ObsUse, yet FedAvg is best on both prediction
-endpoints ($.2379/.2489$).  RAVEN has lowest group mismatch ($.0706$).
-With measured $O$ in Pilot~2 (Appendix~\ref{app:cityscanner_p2_measured_o}),
-TwoStage-H\'ajek remains best on both prediction endpoints; RAVEN has lowest
-group mismatch and beats FedAU/ObsUse/FedAvg in RMSE by
-$.43\%/.45\%/.65\%$.  These cell-client protocols are distinct from taxi-client
-T-Drive and from each other.  A trace dominating City Scanner's paired spread
-is retained: its recurrence over five model seeds identifies trace variability,
-not a model-training failure.  Power at the declared margin is only about $.15$
-over ten traces; the no-trace calculation is sensitivity only.
-The separate Design-cost analysis uses ten traces and three model seeds; its
-deletion-effect contrast remains unresolved.
-
-\subsection{Design and Main-Comparison Outcomes}
+\subsection{Design Effects in Controlled Station Protocols}
 \label{subsec:eval_rq2}
 
-Table~\ref{tab:main_effectiveness} keeps both Design settings.  SensorScope
+Table~\ref{tab:main_effectiveness} compares controlled station mechanisms with both Design settings.  SensorScope
 Design reduces group/client--stratum mismatch versus FedAvg by $3.96\%/2.01\%$,
 with no Holm-significant prediction improvement.  Removing Design worsens the structural endpoints by $1.237\%/.597\%$,
 measured relative to the Design-on arm.
@@ -1574,38 +1625,25 @@
 \end{table}
 
 \paragraph{Configuration and support.}
-For a specified training-unit catalogue, $r$ indexes the experimental block,
-$n_r$ counts units and $n_r^{\mathrm{zero}}$ counts those with an attached
-zero-target client--stratum.  The offline check is
-\begin{equation}
-\rho_r=\frac{n^{\mathrm{zero}}_r}{n_r},
-\qquad
-D_r=\mathrm{on}\iff\rho_r=0 .
-\label{eq:design_gate}
-\end{equation}
-It returns on for SensorScope and off for U-Air/T-Drive (zero shares
-$35.4\%/47.4\%$).  NSW and City Scanner's all-positive region lookups return
-on, but are different objects.  Because configuration is frozen before opening, its catalogue and public lookup
-must already exist; neither current outcomes nor the coverage Gate switches it.  The 774-window
-audit holds R/O/U and registration fixed; differences begin at positive-mass
-support.  U-Air's $25.5\%$ occurrence share and $51.6\%$ active-set overlap
-describe that trace, not a configuration input.
-For measured endpoint values $M_{e,r}(D)$,
-$e\in\mathcal E=\{\Delta_{\mathrm{group}},\Delta_{c\text{-}s},
-\mathrm{RMSE}_{\mu},\mathrm{Tail}\}$, and nonnegative weights $w_e$, the
-retrospective chart
-\begin{equation}
-\begin{aligned}
-\widehat J_r(D)&=\sum_{e\in\mathcal{E}}w_e\,\frac{M_{e,r}(D)}{M_{e,r}(\mathrm{on})},\\
-D_r^{\star}&=\arg\min_{D\in\{\mathrm{on},\mathrm{off}\}}\widehat J_r(D),
-\end{aligned}
-\label{eq:design_switch}
-\end{equation}
-has U-Air structural indifference at $w_c/w_g=1.39$ when only structural terms
-are weighted.  It is not the online rule used in the experiments.
-Zero-target share is not a Design-cost predictor: masking SensorScope target
-keys raises it to $.388$ with cost at most $.175\%$, while U-Air costs
-$6.6\%$--$7.5\%$ over shares $.354$--$.466$.
+The offline support rule and retrospective cost chart are in
+Appendix~\ref{app:cityscanner_phi}. Their catalogue and target lookup must
+exist before window opening; the coverage Gate does not select Design.
+The 774-window U-Air audit holds R/O/U fixed, but Design changes positive-mass
+support (active-set overlap $51.6\%$). Zero-target share is not a cost predictor:
+masking SensorScope keys gives at most $.175\%$ cost at share $.388$, whereas
+U-Air costs $6.6\%$--$7.5\%$ at shares $.354$--$.466$.
+
+\paragraph{City Scanner target support.}
+A separate six-arm experiment uses ten visit-occupancy traces, each with three
+model seeds (Appendix~\ref{app:cityscanner_sixarm}). Replacing zero control-map
+masses with a positive floor retains $101.9\%$ of the FedAvg-to-control
+group-alignment gain. For the trace-level ratio
+$\mathrm{RMSE}_{\mu}(\mathrm{ctrl})/\mathrm{RMSE}_{\mu}(\mathrm{floor})-1$,
+the Hodges--Lehmann estimate is $-.019\%$, with 95\% trace-cluster interval
+$[-1.89\%,+12.28\%]$ ($p=.922$). The deletion-cost contrast is inconclusive,
+not equivalent. Flooring also changes target group marginals, so the contrast
+does not isolate deletion alone. All traces, including the high-variation
+trace, remain in this primary result.
 
 \subsection{Prediction Sensitivity and Adjustment Geometry}
 \label{subsec:ceiling}
@@ -1757,7 +1795,9 @@
 selection to the constrained client mixtures available in an asynchronous
 window.  Ideal moment recovery and fixed-window calibration stability address
 different parts of this connection, with long-run alignment conditional on
-debt growth.  The experiments separate structural changes already explained by
+debt growth.  City Scanner shows group-alignment advantages alongside protocol-dependent
+prediction trade-offs under real opportunities and measured observation, with
+controlled delivery. Station comparisons separate changes explained by
 Uniform from reference projection and independent Design effects.  Simple
 projection is faster and can improve group alignment over full RAVEN, while
 the full criterion improves another structural endpoint.  These differences do
@@ -1772,8 +1812,11 @@
 CC BY 4.0.  \texttt{RAVEN\_MCS\_PUBLIC\_REPRO\_R1} contains EventTraces,
 frozen targets, paired results, and figure/table sources for its indexed
 comparisons.  Later corrected W1 scores, concentration, Adam, learning, and
-geometry diagnostics are indexed, with file paths and scoring identities, in
-\texttt{submission\_evidence/}\allowbreak\texttt{SUBMISSION\_EVIDENCE\_INDEX.md} beside the bundle.
+geometry diagnostics, City Scanner's two protocols, and its separate six-arm
+target-support comparison are indexed with relative paths and scoring
+identities in \texttt{submission\_evidence/}\allowbreak\texttt{SUBMISSION\_EVIDENCE\_INDEX.md}
+inside the bundle. The index distinguishes packaged records from local-only
+sources.
 
 \bibliographystyle{IEEEtran}
 \bibliography{reference}
```

## appendix.tex

```diff
--- current-start/appendix.tex
+++ current/appendix.tex
@@ -1642,22 +1642,36 @@
 \label{fig:certificate_audit}
 \end{figure}
 
-\section{Target-Coverage Statistic and City Scanner Hybrid Rankings}
+\section{Target Support and City Scanner Protocols}
 \label{app:cityscanner_phi}
 
-Table~\ref{tab:scd_phi_freeze} collects the offline train-unit zero-target
-fraction of each block, together with the setting returned by the support
-rule \eqref{eq:design_gate}.  The SensorScope/U-Air counts enumerate unique units in the full
-training split, not the current window's delivered updates.  The rule outputs
-coincide with the settings displayed in the rankings.  Use as a pre-window
-configuration requires this catalogue and the frozen target lookup to be
-available at that time.  Both fixed Design settings are reported on the
-blocks where the trade-off is material.
-The statistic does not verify positivity on
-target-positive pairs, and none of these counts uses $Y$ or RMSE.
-The U-Air EventTrace occurrence share
-$13040/51200=25.5\%$ is not a row in this table.
-The coverage Gate does not switch Design.
+\subsection{Offline Configuration and Retrospective Trade-offs}
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
 
 \begin{table}[t]
 \centering
@@ -1699,156 +1713,109 @@
 \subsection{City Scanner New York {PM}$_{2.5}$}
 \label{app:cityscanner_nyc}
 
-This block uses Design on with a locally constructed
-public drive-by
-{PM}$_{2.5}$ map~\cite{wang2023cityscanner}.
-The source files are the New York Pilot~1 and Pilot~2 {PM} CSVs on
-Zenodo~\footnote{\url{https://doi.org/10.5281/zenodo.7961851}}
-({CC BY} 4.0).  Boston, Beirut, and {NO}$_2$ files are not used.
-$Y$ is the mean of finite calibrated {PM}$_{2.5}$ ($\mu$g/m$^3$) inside
-an occupied $500$\,m $\times$ $30$\,min cell.
-GPS places visits only.
-Federated clients are occupied grid cells, not vehicles.
-Physical filters drop non-finite latitude, longitude, time, or
-\texttt{pm25}, and drop $\texttt{pm25}<0$ or $\texttt{pm25}>1000$.
-Empty cell-slots are absent, not imputed.
-
-The public target $h(i)$ is four quadrants from the median cell indices
-$(g_x,g_y)$ over all occupied cells, without $Y$.
-$\boldsymbol\mu$ is the test-split region share, without $Y$.
-Opportunity strata are $\mathrm{region}{::}\mathrm{block}{::}\mathrm{weekday}$
-(at most $32$).
-$R$ is real visit occupancy: a client occupies a unit if and only if
-that cell has at least one kept sample in that slot.
-$O$ and $U$ remain Complete-aligned controls
-($p_{\mathrm{obs}}=0.35$, $S_{\max}=5$).
-The ranking family is therefore hybrid, not end-to-end MCS.
-
-Processed counts: $14723$ atomic units, $446$ occupied cells, $2776$
-occupied slots, and train/validation/test $9343/3290/2090$.
-All four regions have test units
-($496$, $992$, $148$, $454$).
-Table~\ref{tab:scd_phi_freeze} records the target-coverage statistic
-($0$ of $9343$); Design is on for this block.
-Shared EventTraces use seeds $32001$--$32010$ and $100$ windows obtained
-by chronological equal-count bins of the $1666$ train $30$\,min slots.
-The coverage Gate is unused.
-
-Table~\ref{tab:cityscanner_hybrid} ranks the same windowed family.
-$\mathrm{WorstGroupRMSE}$ is the maximum error over the four quadrants.
-RAVEN-Design is lower than FedAU-Window and ObsUse-Window on
-paired $\mathrm{RMSE}_{\mu}$ (mean relative $-1.71\%$ and $-1.34\%$)
-and on worst-group RMSE ($-1.56\%$ and $-1.23\%$).
-FedAvg-Window remains lowest on both prediction endpoints.
-RAVEN-Design is smallest on $\Delta_{\mathrm{group}}$.
-The block uses the City Scanner visit-occupancy protocol and its quadrant target.
-A separate Pilot~2 ranking with measured observation is
-Table~\ref{tab:cityscanner_p2_measured_o}.
-
-\begin{table}[t]
-\centering
-\caption{City Scanner New York {PM}$_{2.5}$ hybrid ranking
-(mean $\pm$ std, 10 seeds, $100$ windows).  Lower is better.
-FedAvg-Window is lowest on $\mathrm{RMSE}_{\mu}$ and WorstGroupRMSE;
-RAVEN-Design is lower than FedAU-Window and ObsUse-Window on
-those two and smallest on $\Delta_{\mathrm{group}}$.}
-\label{tab:cityscanner_hybrid}
-\scriptsize
-\setlength{\tabcolsep}{2.5pt}
-\begin{tabular}{@{}lcccc@{}}
-\toprule
-Method & $\mathrm{RMSE}_{\mu}$ & WorstGroupRMSE &
-$\Delta_{\mathrm{group}}$ & $\Delta_{c\text{-}s}$\\
-\midrule
-FedAvg-Window & \shortstack{$\mathbf{0.2379}$\\$\pm0.0839$} & \shortstack{$\mathbf{0.2489}$\\$\pm0.0856$} & \shortstack{$0.1953$\\$\pm0.0342$} & \shortstack{$0.8123$\\$\pm0.0191$}\\
-TwoStage-H\'ajek & \shortstack{$0.2510$\\$\pm0.1044$} & \shortstack{$0.2629$\\$\pm0.1068$} & \shortstack{$0.0952$\\$\pm0.0307$} & \shortstack{$\mathbf{0.5305}$\\$\pm0.0286$}\\
-FedAU-Window & \shortstack{$0.2582$\\$\pm0.1028$} & \shortstack{$0.2700$\\$\pm0.1048$} & \shortstack{$0.3216$\\$\pm0.0412$} & \shortstack{$1.1403$\\$\pm0.0538$}\\
-ObsUse-Window & \shortstack{$0.2566$\\$\pm0.1004$} & \shortstack{$0.2685$\\$\pm0.1023$} & \shortstack{$0.3187$\\$\pm0.0414$} & \shortstack{$1.1369$\\$\pm0.0547$}\\
-RAVEN-Design & \shortstack{$0.2549$\\$\pm0.1057$} & \shortstack{$0.2671$\\$\pm0.1079$} & \shortstack{$\mathbf{0.0706}$\\$\pm0.0266$} & \shortstack{$0.5676$\\$\pm0.0311$}\\
-\bottomrule
-\end{tabular}
-
-\begin{minipage}{\columnwidth}
-\raggedright\scriptsize
-$R$ is real visit occupancy; $O$/$U$ are Complete-aligned
-($p_{\mathrm{obs}}=0.35$, $S_{\max}=5$).
-WorstGroupRMSE is the maximum over four coordinate quadrants.
-RAVEN-Design is used (Design on).
-Clients are occupied cells, not vehicles.
-The target consists of four coordinate quadrants on the occupancy grid.
-\end{minipage}
-\end{table}
-
-\subsection{City Scanner Pilot~2 with measured observation}
+The visit-occupancy block uses New York Pilot~1/2 {PM} CSVs from
+Zenodo 10.5281/zenodo.7961851 ({CC BY} 4.0)~\cite{wang2023cityscanner},
+excluding Boston, Beirut, and {NO}$_2$. Non-finite GPS, time, or {PM}$_{2.5}$
+and concentrations outside $[0,1000]$\,$\mu$g/m$^3$ are removed.
+$Y$ averages the remaining calibrated measurements in occupied
+$500$\,m $\times$ $30$\,min cells; empty slots are absent, not imputed.
+Clients are cells, with GPS determining real occupancy $R$.
+The four-quadrant target uses median cell indices without $Y$;
+$\boldsymbol\mu$ is the test-region share. Strata are
+$\mathrm{region}{::}\mathrm{block}{::}\mathrm{weekday}$ (at most 32).
+$O/U$ are Complete-aligned controls ($p_{\mathrm{obs}}=.35$, $S_{\max}=5$).
+
+There are 14723 units, 446 cells and 2776 slots; chronological
+train/validation/test counts are $9343/3290/2090$, with test-region counts
+$496/992/148/454$. Seeds $32001$--$32010$ share 100 windows formed by
+equal-count bins of the 1666 training slots. Design is on and Gate unused
+(Table~\ref{tab:scd_phi_freeze}). Table~\ref{tab:cityscanner_real}(a)
+reports training-standardized errors. The driver clips tiny negative solver
+weights and renormalizes; one seed-32006 window required this correction.
+
+\subsection{City Scanner Pilot~2 with Measured Observation}
 \label{app:cityscanner_p2_measured_o}
 
-This block keeps the same Design setting and the same windowed family, but
-changes how observation is realized.
-The source files are the New York Pilot~2 {PM} and {NO}$_2$ CSVs on
-Zenodo~\footnote{\url{https://doi.org/10.5281/zenodo.7961851}}
-({CC BY} 4.0).  Pilot~1, Boston, and Beirut are not used.
-$Y$ is the mean of finite calibrated {PM}$_{2.5}$ ($\mu$g/m$^3$) inside
-an occupied $500$\,m $\times$ $30$\,min cell.
-Federated clients are occupied grid cells, not vehicles.
-
-$R$ is real visit occupancy on the union of kept-{PM} GPS and {NO}$_2$ GPS
-at the same grid: a client occupies a unit if and only if that cell has at
-least one kept GPS sample in that slot.
-$O=1$ if and only if the cell-slot contains finite {PM}$_{2.5}$ in
-$[0,1000]$, giving a measured observation indicator.
-{NO}$_2$ contributes GPS occupancy only and is not the completion target.
-$U$ remains a Complete-aligned control ($S_{\max}=5$).
-The hybrid protocol combines measured occupancy and observation with controlled
-usable-update delivery.
-
-Occupancy is $14960$ cell-slots, $416$ cells, and $2402$ slots
-($10141/2835/1984$ train/val/test), with measured $O=0$ on $1931$ slots
-($12.9\%$) and $13029$ labeled $O=1$ units.
-Region test occupancy is $1289$, $268$, $144$, and $283$.
-RAVEN-Design is used (Design on); seeds $33001$--$33010$ and
-$100$ windows from $1441$ train slots.
-Paired relative RMSE versus FedAU-Window, ObsUse-Window, and FedAvg-Window is
-$-0.43\%$, $-0.45\%$, and $-0.65\%$ (worst-group $-0.44\%$, $-0.47\%$,
-$-0.65\%$).
-Pilot~2 evaluates measured observation on the City Scanner occupancy grid;
-its protocol differs from the visit-occupancy comparison in
-Table~\ref{tab:cityscanner_hybrid}.
+This block uses New York Pilot~2 {PM} and {NO}$_2$ CSVs from the same
+licensed source, excluding Pilot~1, Boston and Beirut. Clients and $Y$ use
+the same grid-cell definitions. Union GPS defines $R$; finite {PM}$_{2.5}$
+in $[0,1000]$ defines $O=1$. {NO}$_2$ contributes locations only.
+$U$ remains Complete-aligned ($S_{\max}=5$). The frozen region target,
+Design-on setting and unused Gate are unchanged in role, not in numerical
+target values.
+
+Occupancy comprises 14960 cell-slots, 416 cells and 2402 slots:
+$10141/2835/1984$ train/validation/test. There are 1931 unobserved units
+($12.9\%$) and 13029 labeled units; test-region occupancy is
+$1289/268/144/283$. Seeds $33001$--$33010$ use 100 windows from 1441
+training slots. Table~\ref{tab:cityscanner_real}(b) reports errors in this
+block's own training-standardized scale. Section~\ref{subsec:cityscanner_real}
+gives both rankings, paired comparisons and the missed improvement criterion.
+
+\subsection{City Scanner Target Maps and Zero-Mass Handling}
+\label{app:cityscanner_sixarm}
+
+This trained six-arm comparison uses the visit-occupancy protocol with
+controlled $O/U$: ten traces, each with model seeds $s,s+100000,s+200000$.
+The 180 cells comprise 150 newly trained and 30 reused cells. Maps are fixed
+before training from public locations, calendar strata and test-region shares,
+without responses or model errors. Table~\ref{tab:cityscanner_sixarm}
+reports mean and SD over ten within-trace model-seed means.
 
 \begin{table*}[t]
 \centering
-\caption{City Scanner New York Pilot~2 ranking with measured observation
-(mean $\pm$ std, 10 seeds, $100$ windows).  Lower is better.
-TwoStage-H\'ajek is lowest on $\mathrm{RMSE}_{\mu}$ and WorstGroupRMSE;
-RAVEN-Design is smallest on $\Delta_{\mathrm{group}}$ and
-lower than FedAU-Window, ObsUse-Window, and FedAvg-Window on the two prediction
-endpoints.}
-\label{tab:cityscanner_p2_measured_o}
-\scriptsize
-\setlength{\tabcolsep}{2.5pt}
-\begin{tabular*}{\textwidth}{@{\extracolsep{\fill}}lcccc}
-\toprule
-Method & $\mathrm{RMSE}_{\mu}$ & WorstGroupRMSE &
-$\Delta_{\mathrm{group}}$ & $\Delta_{c\text{-}s}$\\
-\midrule
-FedAvg-Window & $0.7182{\pm}0.0208$ & $0.7359{\pm}0.0204$ & $0.0769{\pm}0.0231$ & $0.7066{\pm}0.0162$\\
-TwoStage-H\'ajek & $\mathbf{0.7097}{\pm}0.0204$ & $\mathbf{0.7273}{\pm}0.0200$ & $0.0607{\pm}0.0206$ & $\mathbf{0.3893}{\pm}0.0265$\\
-FedAU-Window & $0.7173{\pm}0.0289$ & $0.7351{\pm}0.0291$ & $0.2283{\pm}0.0433$ & $1.0034{\pm}0.0383$\\
-ObsUse-Window & $0.7175{\pm}0.0288$ & $0.7352{\pm}0.0290$ & $0.2314{\pm}0.0429$ & $1.0059{\pm}0.0380$\\
-RAVEN-Design & $0.7135{\pm}0.0206$ & $0.7311{\pm}0.0200$ & $\mathbf{0.0465}{\pm}0.0119$ & $0.4172{\pm}0.0214$\\
+\caption{Six-arm City Scanner comparison (ten traces, three model seeds per
+trace; mean $\pm$ SD across trace means). Prediction uses common region weights
+and the training-standardized scale. $\rho$: percentage of non-test delivered
+units assigned zero mass (zero for Design off). Group gaps share a region
+target; client--stratum gaps use arm-specific maps and cannot rank alignment
+to a common target. Lower errors are better.}
+\label{tab:cityscanner_sixarm}
+\footnotesize
+\begin{tabular*}{\textwidth}{@{\extracolsep{\fill}}lccccc@{}}
+\toprule
+Arm & $\rho$ (\%) & $\mathrm{RMSE}_{\mu}$ & WorstGroupRMSE & $\Delta_{\mathrm{group}}$ & $\Delta_{c\text{-}s}$\\
+\midrule
+\texttt{fedavg\_window} & 0.00 & $0.2409{\pm}0.0832$ & $0.2529{\pm}0.0903$ & $0.1953{\pm}0.0342$ & $0.8123{\pm}0.0191$\\
+\texttt{raven\_wo\_design} & 0.00 & $0.2439{\pm}0.0835$ & $0.2575{\pm}0.0905$ & $0.0736{\pm}0.0264$ & $0.7880{\pm}0.0254$\\
+\texttt{raven\_ctrl} & 14.35 & $0.2561{\pm}0.1031$ & $0.2695{\pm}0.1095$ & $0.0706{\pm}0.0266$ & $0.5676{\pm}0.0311$\\
+\texttt{raven\_ctrl\_floor} & 0.00 & $0.2442{\pm}0.0842$ & $0.2576{\pm}0.0908$ & $0.0682{\pm}0.0313$ & $0.7892{\pm}0.0235$\\
+\texttt{raven\_M1mu} & 1.01 & $0.2467{\pm}0.0889$ & $0.2609{\pm}0.0971$ & $0.0771{\pm}0.0338$ & $1.4060{\pm}0.0168$\\
+\texttt{raven\_M2mu} & 0.98 & $0.2508{\pm}0.0907$ & $0.2661{\pm}0.1003$ & $0.0813{\pm}0.0301$ & $1.4348{\pm}0.0147$\\
 \bottomrule
 \end{tabular*}
-
-\par\vspace{2pt}
-\noindent\raggedright\scriptsize
-$R$ is real visit occupancy on union GPS; $O$ is measured from finite
-{PM}$_{2.5}$; $U$ is Complete-aligned ($S_{\max}=5$).
-WorstGroupRMSE is the maximum over four coordinate quadrants.
-RAVEN-Design is used (Design on).
-Clients are occupied cells, not vehicles.
-This protocol uses the measured observation indicator defined above.
 \end{table*}
 
-
+\texttt{fedavg\_window} uses count weights and \texttt{raven\_wo\_design}
+fixes Design off, so neither applies the target ratio.
+\texttt{raven\_ctrl} uses the test-location control map (1164 keys,
+812 zeros). \texttt{raven\_ctrl\_floor} fills these zeros with the smallest
+positive mass ($4.78469\times10^{-4}$) and renormalizes, changing group
+marginals. \texttt{raven\_M1mu}/\texttt{raven\_M2mu} use ACS population/NYC~311
+shapes on the same keys, rescaled within region to the common target;
+70/33 zero keys remain. All maps cover the 959 recorded risk-set keys.
+These trained variants differ from control RAVEN and disputed fixed-prediction
+re-scorings. Flooring changes both zeros and marginals.
+
+The primary $d_t=R_{\mathrm{ctrl},t}/R_{\mathrm{floor},t}-1$ uses within-trace
+model-seed mean RMSE, giving a Hodges--Lehmann estimate of $-.019\%$
+(paired Wilcoxon $p=.922$). Resampling traces and model seeds within trace
+gives the recorded 95\% percentile interval $[-1.89\%,+12.28\%]$,
+which establishes neither deletion cost nor $2\%$ equivalence.
+The group-gain retention is
+$(\overline\Delta_{\mathrm{FedAvg}}-\overline\Delta_{\mathrm{floor}})/
+(\overline\Delta_{\mathrm{FedAvg}}-\overline\Delta_{\mathrm{ctrl}})=1.0194$,
+not prediction improvement.
+
+No member of the four-contrast secondary Holm family (M1/control,
+M2/control, floor/NoDesign, six-arm dose-response slope) is significant.
+The separate floor/M1/M2 versus FedAvg non-inferiority chains miss the
+$2\%$ margin: one-sided 95\% upper bounds are $3.83/4.14/8.15\%$,
+so superiority is not tested. All traces enter the primary analysis.
+Trace 32005's control/NoDesign cost recurs across five model seeds.
+Its registered exclusion is sensitivity only: the primary-contrast interval
+narrows to $[-2.32\%,+3.53\%]$ and remains inconclusive.
+Recorded diagnostic power at the $2\%$ margin is $.151$ with all traces.
 
 \section{Learning Capacity under a Separate Development Protocol}
 \label{app:learning_capacity}
@@ -1883,7 +1850,7 @@
 \end{tabular*}
 \end{table*}
 
-\begin{figure*}[t]
+\begin{figure*}[!b]
 \centering
 \includegraphics[width=\textwidth]{fig_learning_capacity_r2.png}
 \caption{Longer-budget development learning curves, with physical training
@@ -1918,14 +1885,12 @@
 \section{Constraint Sensitivity of the Development Geometry}
 \label{app:development_geometry}
 
-The geometry uses first-cycle payloads from the separate development traces,
-with their recorded correction settings.  It does not re-evaluate the main
-fixed-Design performance experiment.  For each natural window with at least
-eight distinct clients, the diagnostic takes the first eight in sorted client
-order and renormalizes their reference.  Rank is measured from the centered
-composition matrix; group ranges are extrema over the constrained feasible
-set.  Therefore $K-1$, composition rank, and mass with a group range of at least
-.01 describe different kinds of freedom.
+This separate development diagnostic uses first-cycle payloads and their
+recorded correction settings. For each natural window with at least eight
+clients, it takes the first eight in sorted order and renormalizes their
+reference. Centered composition rank and feasible group ranges distinguish
+weight freedom from mass adjustable by at least .01; they do not re-evaluate
+fixed-Design prediction performance.
 
 \begin{table}[t]
 \centering
@@ -1949,8 +1914,7 @@
 \end{tabular*}
 \end{table}
 
-The natural data contain no $K=16$ payload.  Tightening caps increases reference
-infeasibility and projection distance without changing the .01-threshold
-adjustable mass in these subsets.  This illustrates why a single count of active
-clients is insufficient to characterize the target adjustment available to a
-server.  No forecasts or label-dependent choices enter this geometry audit.
+No natural payload has $K=16$. Tighter caps increase infeasibility and
+projection distance while leaving .01-threshold adjustable mass unchanged.
+Client count alone therefore does not characterize adjustment capacity.
+No forecasts or label-dependent choices enter this audit.
```

## supplemental.tex

```diff
--- current-start/supplemental.tex
+++ current/supplemental.tex
@@ -70,13 +70,13 @@
 and must be uploaded as a separate PDF. It is not a standalone submission.}
 
 % Continue figure/table/equation numbers from the companion main paper.
-% Main has 4 figures, 7 tables, 1 algorithm (window-close configured Design) and
-% the support-gate / switch-point equations (42)-(43).
+% Main has 4 figures, 8 tables, 1 algorithm and 41 numbered equations.
+% Offline support and retrospective switch equations are in Appendix J.
 % Numbered statements in main: four propositions, two theorems, one assumption.
 \setcounter{figure}{4}
-\setcounter{table}{7}
+\setcounter{table}{8}
 \setcounter{algorithm}{1}
-\setcounter{equation}{43}
+\setcounter{equation}{41}
 \setcounter{proposition}{4}
 \setcounter{theorem}{2}
 \setcounter{corollary}{0}
```
