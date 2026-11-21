# Section IV本轮局部差异

基准为本轮开始的当前工作树。

```diff
--- this-round-start/main.tex
+++ current/main.tex
@@ -494,18 +494,14 @@
 \section{Selection-Layer-Aware Target Reconstruction}
 \label{sec:reconstruction}
 
-RAVEN-MCS (Reference Alignment Via Exposure-aware Normalization) first forms a
-selection-corrected reference for the mass the usable data represent.
-Opportunity, observation, and usable-update selection have different
-conditioning histories.  Their probabilities can be multiplied into a joint
-inclusion probability by the chain rule; retaining the factors specifies when
-their covariates and outcomes become available and permits layer-specific
-estimation and diagnosis.
+RAVEN connects sensing-unit correction to a window's client reference using
+sequential IPW and H\'ajek normalization.  Local weights determine training
+within clients, while corrected masses determine their relative server reference.
 
 \subsection{Opportunity/Design Correction}
 \label{subsec:design_correction}
 
-For a target-supported client--atomic pair, the ideal opportunity/design ratio is
+The ideal opportunity ratio on target-supported client--atomic pairs is
 \begin{equation}
  \zeta^{o}_{k,r,i}
  =
@@ -518,8 +514,10 @@
       {P_r^{\mathrm{opp}}(k,i)}.
  \label{eq:design_ratio_general}
 \end{equation}
-Under within-stratum exchangeability,
-$\nu^{\mathrm{opp}}_{k,r}(i\mid s)=\nu^{\mathrm{tar}}_{i\mid s}$, this reduces to
+Within-stratum exchangeability,
+$\nu^{\mathrm{opp}}_{k,r}(i\mid s)=\nu^{\mathrm{tar}}_{i\mid s}$,
+cancels the conditional atomic ratio.  The implementation estimates the
+remaining opportunity mass from lagged history and floors its denominator:
 \begin{equation}
  \widehat\zeta^{o}_{k,r,s}
  =
@@ -527,8 +525,7 @@
  {\max\{\widehat\pi^{\mathrm{opp}}_{k,s,r},\pi_{\min}\}}.
  \label{eq:design_ratio_simple}
 \end{equation}
-The opportunity estimate is lagged: current-window outcomes cannot alter the
-weight applied to that same window.  One admissible implementation uses
+One admissible smoothed count estimator is
 \begin{align*}
  C^{\mathrm{opp}}_{k,s,r}
  &=
@@ -540,24 +537,17 @@
  {\sum_{j,u}
  (C^{\mathrm{opp}}_{j,u,r}+\epsilon_{\mathrm{opp}})}.
 \end{align*}
-Other pre-outcome estimators are compatible with the framework if they preserve
-the same support and information boundary.
-
-The Design factor $D_t\in\{\mathrm{on},\mathrm{off}\}$ of
-\eqref{eq:design_factor} applies \eqref{eq:design_ratio_simple} when it is on,
-which is RAVEN-Design; with the factor off,
-Algorithm~\ref{alg:window_close} runs RAVEN-NoDesign and sets
-$\widehat\zeta^{o}_{k,r,i}=1$ on observed pairs.  The factor is a configuration of
-the deployment, supplied before the window opens and held fixed within it.
-The off setting retains the opportunity layer's arrival law
-$\pi^{\mathrm{opp}}$.
+Under \eqref{eq:design_factor}, Design on uses this ratio.  Off sets it to one
+and retains the opportunity arrival law.  Both are configured before opening
+and fixed within the window.
+Same-support Design contrasts and Obs/Use ablations assess endpoint-specific
+layer effects, not universal necessity (Section~\ref{subsec:eval_rq3}).
 
 \subsection{Observation Correction and Local H\'ajek Normalization}
 \label{subsec:observation_hajek}
 
-The ideal first-stage weight for a realized opportunity is
-$a^\star_{k,r,i}=\zeta^{o}_{k,r,i}/p^{\mathrm{obs}}_{k,r,i}$.
-The implemented plug-in weight is stabilized as
+For ideal weight $a^\star_{k,r,i}=\zeta^o_{k,r,i}/p^{\mathrm{obs}}_{k,r,i}$,
+the stabilized plug-in and corrected masses are
 \begin{equation}
  a_{k,r,i}
  =
@@ -568,43 +558,30 @@
  \right\}.
  \label{eq:a_stabilized}
 \end{equation}
-Define the corrected total mass
-\begin{equation}
-    m_{k,r}
-    =
+\begin{align}
+m_{k,r}
+    &=
     \sum_i
     R_{k,r,i}O_{k,r,i}a_{k,r,i},
-    \label{eq:m_total}
-\end{equation}
-the corrected deployment-group mass
-\begin{equation}
- m^{g}_{k,r,g}
- =
+    \label{eq:m_total}\\
+m^{g}_{k,r,g}
+ &=
  \sum_i
  R_{k,r,i}O_{k,r,i}a_{k,r,i}
  \mathbf{1}\{h(i)=g\},
- \label{eq:m_group}
-\end{equation}
-and the corrected opportunity-stratum mass
-\begin{equation}
- m^{s}_{k,r,s}
- =
+ \label{eq:m_group}\\
+m^{s}_{k,r,s}
+ &=
  \sum_i
  R_{k,r,i}O_{k,r,i}a_{k,r,i}
  \mathbf{1}\{s(i)=s\}.
  \label{eq:m_stratum}
-\end{equation}
-RAVEN aggregates only target-relevant usable clients:
-$\mathcal{A}_r\triangleq\{k\in\mathcal{U}_r:m_{k,r}>0\}$.
-Every $k\in\mathcal{A}_r$ has well-defined normalized record weights
-$\overline a_{k,r,i}=\frac{R_{k,r,i}O_{k,r,i}a_{k,r,i}}{m_{k,r}}$.
-Its deployment-group composition is
-$c^{g}_{k,r,g}=\frac{m^{g}_{k,r,g}}{m_{k,r}}$, and its
-opportunity-stratum composition is
-$c^{s}_{k,r,s}=\frac{m^{s}_{k,r,s}}{m_{k,r}}$.
-Both composition vectors sum to one for $k\in\mathcal{A}_r$.
-
-The local effective sample size is
+\end{align}
+Only $\mathcal A_r=\{k\in\mathcal U_r:m_{k,r}>0\}$ is aggregated.  Define
+$\overline a_{k,r,i}=R_{k,r,i}O_{k,r,i}a_{k,r,i}/m_{k,r}$,
+$c^g_{k,r,g}=m^g_{k,r,g}/m_{k,r}$, and
+$c^s_{k,r,s}=m^s_{k,r,s}/m_{k,r}$.  These record weights and compositions
+normalize within each active client.  Local ESS,
 \begin{equation}
  n^{\mathrm{eff}}_{k,r}
  =
@@ -615,10 +592,8 @@
  \frac{1}{\sum_i\overline a_{k,r,i}^2}.
  \label{eq:neff}
 \end{equation}
-It measures weight concentration and is deliberately distinct from the
-target-equivalent corrected mass $m_{k,r}$.
-
-The local completion objective is
+measures concentration, not corrected target mass $m_{k,r}$.
+Training uses the normalized objective
 \begin{equation}
  \widehat F^{H}_{k,r}(\theta)
  =
@@ -632,10 +607,9 @@
  \right)^2.
  \label{eq:local_hajek_objective}
 \end{equation}
-Starting from $\theta_{\sigma_{k,r}}$, client $k$ performs
-$E_{\mathrm{loc}}$ local steps of $\ell$ with step size $\gamma_r>0$, reaching
-$\theta^{(E_{\mathrm{loc}})}_{k,r}$.  Its normalized model
-displacement is
+Starting at $\theta_{\sigma_{k,r}}$, the client takes $E_{\mathrm{loc}}$ steps
+on $\widehat F^H_{k,r}$ with step size $\gamma_r>0$, producing normalized
+displacement
 \begin{equation}
  \mathbf{u}_{k,r}
  =
@@ -646,13 +620,18 @@
  }{\gamma_r E_{\mathrm{loc}}}.
  \label{eq:normalized_update}
 \end{equation}
+The displacement divides out the local learning rate and step count, preserving
+the server update scale.  Constant within-client correction cancels during
+normalization.  Heterogeneous propensities supply different inputs, although
+clipping can still equalize realized weights.
+Local-weight audits and F1 examine constant-weight cancellation and heterogeneous
+inputs without establishing prediction gains
+(Appendix~\ref{app:local_hajek} and Table~\ref{tab:f1_mechanism}).
 
 \subsection{Usable-Update Correction and Reference Aggregation Mass}
 \label{subsec:usable_correction}
 
-For a registered attempt, $\widehat q^{\mathrm{use}}_{k,r}$ is estimated only
-from variables measurable before $U_{k,r}$ is realized.  For
-$k\in\mathcal{A}_r$, define
+For $k\in\mathcal A_r$, the pre-$U$ estimate gives
 \begin{equation}
  d_{k,r}
  =
@@ -663,8 +642,7 @@
  \right\},
  \label{eq:d_use}
 \end{equation}
-and $b_{k,r}=m_{k,r}d_{k,r}$.
-The selection-corrected reference aggregation vector is
+Set $b_{k,r}=m_{k,r}d_{k,r}$ and normalize:
 \begin{equation}
  \widehat\beta_{k,r}
  =
@@ -674,39 +652,30 @@
  k\in\mathcal{A}_r.
  \label{eq:beta_ref}
 \end{equation}
-Thus $\widehat{\boldsymbol\beta}_r$ is a probability vector on
-$\mathcal{A}_r$.  The ideal untruncated factorization of
-$\beta^\star\overline a^\star$ is in the supplemental material; the implemented
-$\widehat{\boldsymbol\beta}_r$ is a stabilized plug-in whose clipping controls
-the finite-sample bias--variance trade-off.  The corrected
-deployment-group composition represented by the usable data before server
-calibration is $\boldsymbol\omega_r^{\mathrm{ref}}=M_r\widehat{\boldsymbol\beta}_r$,
-which a finite mobile window need not make equal to $\boldsymbol\mu$, since the
-current feasible client set can lack target support.
+Local H\'ajek normalization removes the client's total scale from training.
+$m_{k,r}d_{k,r}$ restores relative corrected mass between usable clients.
+The ideal untruncated factorization of $\beta^\star\overline a^\star$ is
+given in the supplemental material.  This factorization concerns ideal event
+weights rather than a prediction guarantee for multi-step updates from stale
+models.  The implemented
+$\widehat{\boldsymbol\beta}_r$ is instead an estimated, stabilized reference,
+not the feasible decision $\boldsymbol\alpha_r$.
+Its composition $M_r\widehat{\boldsymbol\beta}_r$ need not equal
+$\boldsymbol\mu$ when current support is incomplete.  Section~\ref{sec:calibration}
+maps the reference to executable aggregation weights.
+W1 compares direct-reference structural readouts, Uniform, projection, and
+RAVEN to assess this calibration step (Section~\ref{subsec:eval_rq3}).
 
 \subsection{Information Boundary and Stabilization}
 \label{subsec:information_boundary}
 
-Every correction applied in window $r$ is measurable before its own random
-outcome: lagged opportunity history, observation propensities excluding the
-current sensing outcome and label, and usable-update propensities excluding the
-realized $U$ outcome and future events.  The server determines $\boldsymbol\alpha_r$ without
-inspecting the coordinates, norm, or direction of a current random
-update for the purpose of assigning that update's weight.  The clipping
-constants in \eqref{eq:a_stabilized} and \eqref{eq:d_use} are
-finite-sample bias--variance stabilizers.  Exact identification in
-Section~\ref{sec:theory} concerns the ideal ratios, or equivalently
-regimes in which the stabilizing bounds are inactive on target support.
-
-\subsection{Why Pairwise Positive Lower Bounds Are Not the Formal Certificate}
-\label{subsec:pairwise_barrier}
-
-A deterministic pre-window pairwise lower bound is structurally vacuous under
-hidden zero-opportunity events by the positive pairwise lower-bound barrier
-proposition in the supplemental material, whose availability-induced barrier
-corollary places the frozen stress levels $a\in\{0.80,0.60,0.40,0.20\}$ in that
-region.  Pairwise positive LCBs are not the aggregate object \eqref{eq:agg_Ct}.
-
+Opportunity estimates are lagged, observation models exclude current responses,
+and usable-update models exclude $U$ outcomes and future information.  Current
+update coordinates, norms, or directions never determine that update's weight.
+Clipping stabilizes finite samples but introduces error distinct from
+estimation error.  Ideal recovery requires support, correct ratios, and
+sequential identification (Section~\ref{sec:theory}).  Inactive clipping alone
+does not establish these conditions.
 
 \section{Feasibility-Aware Target Calibration}
 \label{sec:calibration}
@@ -1250,12 +1219,13 @@
 
 \subsection{Aggregate Coverage Guarantees}
 \label{subsec:agg_coverage_theory}
+\label{subsec:pairwise_barrier}
 
 The reconstruction results above do not by themselves yield a finite-sample
 coverage certificate.  Deterministic pre-window pairwise LCBs are vacuous
 under hidden zero-opportunity events, and the frozen stress levels
 $a\in\{0.80,0.60,0.40,0.20\}$ fall in that region
-(Section~\ref{subsec:pairwise_barrier}).  In a certified regime the
+by the availability-induced barrier corollary in the supplemental material.  In a certified regime the
 false-safe probability of an empirical diagnostic Gate is bounded by
 $\alpha$, by the false-safe Gate corollary in the supplemental material; and
 no method can simultaneously provide nontrivial per-window certification and
```
