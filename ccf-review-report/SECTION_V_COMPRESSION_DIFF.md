# Section V本轮局部差异

基准为本轮开始的当前工作树，不回退前轮修订。

## main.tex

```diff
--- this-round-start/main.tex
+++ current/main.tex
@@ -680,17 +680,15 @@
 \section{Feasibility-Aware Target Calibration}
 \label{sec:calibration}
 
-Selection reconstruction determines what the usable data statistically
-represent; the clients available at window closure determine which mixtures are
-realizable.  RAVEN calibrates the corrected reference
-$\widehat{\boldsymbol\beta}_r$ within this current support.
+Section~\ref{sec:reconstruction} supplies the corrected reference
+$\widehat{\boldsymbol\beta}_r$.  Available support and aggregation constraints
+determine its executable mixtures.  P2 connects reference fidelity, target
+composition, and accumulated under-service.
 
 \subsection{Feasible Aggregation Set}
 \label{subsec:feasible_set}
 
-Let $K_r=|\mathcal{A}_r|$ in an active window and retain
-$M_r=[\mathbf{c}^{g}_{k,r}]_{k\in\mathcal{A}_r}$.  The server chooses
-$\boldsymbol\alpha_r\in\mathbb{R}^{K_r}$ from
+For $K_r=|\mathcal A_r|>0$, choose $\boldsymbol\alpha_r\in\mathbb R^{K_r}$ in
 \begin{equation}
  \mathcal{C}_r
  =
@@ -702,15 +700,12 @@
  \right\},
  \label{eq:Cr}
 \end{equation}
-where the coordinate cap $\overline\alpha_r$ and $\ell_2$ support bound
-$\overline E_r$ are frozen functions of $K_r$, the effective-support cap of the
-supplemental material, with $0<\alpha_{\max}\le1$ and $E_{\min}\ge1$ as frozen
-design parameters.  The cap controls single-client dominance and the $\ell_2$
-constraint imposes a minimum effective aggregation support; the uniform vector
-$\mathbf{1}/K_r$ belongs to $\mathcal{C}_r$, so every active window has at least
-one feasible aggregation vector.
-
-RAVEN also uses pre-aggregation uncertainty only.  A lagged variance proxy is
+The cap $\overline\alpha_r=\min\{1,\max\{\alpha_{\max},1/K_r\}\}$ and
+support bound $\overline E_r=\min\{E_{\min},K_r\}$ use frozen
+$0<\alpha_{\max}\le1$, $E_{\min}\ge1$ (Appendix~\ref{app:deferred_constructions}).
+These definitions make Uniform feasible while controlling single-client
+dominance and minimum effective support.  The reconstructed reference need not
+satisfy these constraints.  The lagged variance proxy is
 \begin{equation}
  v_{k,r}
  =
@@ -725,24 +720,22 @@
  V_r=\operatorname{diag}(v_{k,r})\succeq0,
  \label{eq:variance_proxy}
 \end{equation}
-where $\overline S_{k,r^-}^{\,2}$ is available before the current random update
-is weighted.  Let $\overline{\boldsymbol\tau}_r\ge0$ denote the frozen
-pre-aggregation staleness vector.
+This proxy and frozen staleness vector $\overline{\boldsymbol\tau}_r\ge0$
+are available before weighting, without inspecting the current update vector.
+The variance proxy is not the true current-update variance.  Its lag prevents
+the weighting rule from adapting to the current random vector.
 
 \subsection{Long-Term Target Debt}
 \label{subsec:debt}
 
-Finite-window feasibility can make
-$M_r\boldsymbol\alpha=\boldsymbol\mu$ impossible.  RAVEN maintains a
-nonnegative target-debt vector
-$\mathbf{Q}_r\in\mathbb{R}^{|\mathcal{G}|}_+$, initialized by
-$\mathbf{Q}_0=\mathbf{0}$, updated in an active window by
-$\mathbf{Q}_{r+1}=\left[\mathbf{Q}_r+\eta_r(\boldsymbol\mu-\boldsymbol\omega_r)\right]_+$
-with $\boldsymbol\omega_r=M_r\boldsymbol\alpha_r$, and left unchanged in an
-inactive one.  A positive $Q_{r,g}$ records accumulated under-service of
-deployment group $g$ without pretending that unavailable target mass can be
-synthesized in the current window.  For every prefix with $S_R>0$, the recursion
-implies the deterministic accounting relation
+Initialize $\mathbf Q_0=\mathbf0$.  In active windows, accumulated group
+under-service follows
+$\mathbf Q_{r+1}=[\mathbf Q_r+\eta_r(\boldsymbol\mu-\boldsymbol\omega_r)]_+$,
+where $\boldsymbol\omega_r=M_r\boldsymbol\alpha_r$.  Inactive windows leave
+debt unchanged.  Positive coordinates record accumulated group under-service
+when the feasible mixture cannot match the target within a window.
+For effective step mass $S_R=\sum_{r<R}\eta_r I_r>0$,
+the deterministic accounting bound is
 \begin{equation}
  \left\|
  \overline{\boldsymbol\omega}_R-\boldsymbol\mu
@@ -753,17 +746,14 @@
  }{S_R}.
  \label{eq:debt_bound}
 \end{equation}
-The full derivation is in the target-debt accounting proof of the supplemental
-material.  Vanishing long-run mismatch follows if
-$\|\mathbf Q_R\|_1=o(S_R)$; the recursion alone does not establish that growth
-condition.
+Only $\|\mathbf Q_R\|_1=o(S_R)$ makes this bound vanish.  The recursion does
+not establish debt stability.  The derivation is in the supplemental material.
 
 \subsection{Feasibility-Aware Calibration Program}
 \label{subsec:P2}
 
-For every active window, RAVEN solves
-$\text{(P2)}\ \min_{\boldsymbol\alpha\in\mathcal{C}_r}J_r(\boldsymbol\alpha)$.
-The objective is
+Each active window solves
+$\text{(P2)}\ \min_{\boldsymbol\alpha\in\mathcal C_r}J_r(\boldsymbol\alpha)$:
 \begin{align}
  J_r(\boldsymbol\alpha)
  ={}&-\mathbf{Q}_r^{\top}M_r\boldsymbol\alpha
@@ -778,28 +768,24 @@
  +\lambda_s\overline{\boldsymbol\tau}_r^{\top}\boldsymbol\alpha.
 \label{eq:P2_objective}
 \end{align}
-The debt term prioritizes accumulated under-served groups; the group,
-reference, variance, and staleness terms are coordinated terms of one
-program.  The reference anchor penalizes departures from the reconstructed
-client mass, while the group term penalizes departures of the resulting
-composition from the deployment target.  These are different distances:
-projection of $\widehat{\boldsymbol\beta}_r$ in client-weight space minimizes
-$\|\boldsymbol\alpha-\widehat{\boldsymbol\beta}_r\|_2^2$, whereas group matching
-minimizes $\|M_r\boldsymbol\alpha-\boldsymbol\mu\|_2^2$.
-Over the $3279$ audited active windows, the feasible range of the evaluation
-quantity $\|M_r\boldsymbol\alpha-\boldsymbol\mu\|_1$ has median $10^{-13}$.
-This describes the $\ell_1$ evaluation geometry, not constancy of the squared
-$\ell_2$ term in (P2).  Limited group support can restrict observable alignment
-even when feasible weights differ; the rule comparisons in
-Section~\ref{subsec:eval_rq3} measure the consequences of the separate terms.
-$\widehat{\boldsymbol\beta}_r$ is the selection-corrected reference;
-$\boldsymbol\alpha_r$ is the feasible aggregation decision.
+The anchor controls departures from the reconstructed client reference, whereas
+the group term controls the resulting deployment composition.  Client-weight
+projection and composition matching therefore measure different distances.
+Debt prioritizes accumulated under-service.  Variance and staleness regularize
+using their defined proxies.  Section~\ref{subsec:theorem_calibration}
+establishes uniqueness under its stated conditions, separately from numerical
+solver accuracy.
+W1 compares direct-reference structural readouts, Uniform, projection, and
+full RAVEN under their respective rules (Section~\ref{subsec:eval_rq3}).
+On SensorScope, projection has lower group mismatch and runtime than full
+RAVEN, while RAVEN has lower client--stratum mismatch.  Structural ordering
+does not establish prediction ordering.
 
 \subsection{Global Update and Window Logic}
 \label{subsec:global_update}
 
-Let $\boldsymbol\alpha_r^\star$ denote the solution of (P2).  The server update
-is
+With P2 solution $\boldsymbol\alpha_r^\star$, aggregate the normalized updates
+of \eqref{eq:normalized_update}:
 \begin{equation}
  \theta_{r+1}
  =
@@ -810,59 +796,13 @@
  \alpha^\star_{k,r}\mathbf{u}_{k,r}.
  \label{eq:server_update}
 \end{equation}
-After aggregation, the server updates the debt via
-$\mathbf{Q}_{r+1}=\left[\mathbf{Q}_r+\eta_r(\boldsymbol\mu-\boldsymbol\omega_r)\right]_+$,
-where $\boldsymbol\omega_r=M_r\boldsymbol\alpha_r$, and advances lagged
-selection and variance states.  If $\mathcal{A}_r=\varnothing$, the
-window is inactive: $\theta_{r+1}=\theta_r$, $\mathbf{Q}_{r+1}=\mathbf{Q}_r$,
-and the window does not enter $S_R$.  Algorithm~\ref{alg:window_close}
-records this order: reconstruct $\widehat{\boldsymbol\beta}_r$, solve (P2) for
-$\boldsymbol\alpha_r^\star$, then aggregate and update debt.
-
-\subsection{Finite-Sample Aggregate Coverage Certificate}
-\label{subsec:agg_certificate_alg}
-\label{subsec:agg_coverage_object}
-
-The auxiliary coverage diagnostic uses target-positive pairs
-$I_{\mathrm{tar}}=\{(k,s):\pi^{\mathrm{tar}}_{k,s}>0\}$ and realized coverage
-\begin{equation}
- C_t
- =
- \sum_{(k,s)\in I_{\mathrm{tar}}}
- \pi^{\mathrm{tar}}_{k,s}
- \,
- \mathbf{1}\!\left\{\pi^{\mathrm{opp}}_{k,s,t}\ge\pi_{\mathrm{safe}}\right\},
- \label{eq:agg_Ct}
-\end{equation}
-Here $\pi^{\mathrm{opp}}_{k,s,t}$ is lagged opportunity mass and
-$\pi_{\mathrm{safe}}$ is a frozen threshold.  The pair masses and unit lookup
-are specified in Appendix~\ref{app:itar_lookup}.  Unlike federated conformal
-prediction sets~\cite{lu2023federated,plassier2023conformal}, this diagnostic
-assesses aggregate opportunity coverage.
-
-The Design factor $\eqref{eq:design_factor}$ is configured on or off.  A
-diagnostic Gate, detailed as the aggregate coverage certificate algorithm of the
-supplemental material, uses only pre-window information $F_{t-}$ with
-\begin{equation}
- k_n=\lceil(n+1)(1-\alpha)\rceil,
- \qquad
- \alpha=0.05,
- \label{eq:agg_kn}
-\end{equation}
-and
-\begin{equation}
- C^{\mathrm{LCB}}_t=\max\{0,\widehat C_t-q_t\},
- \label{eq:agg_CLCB}
-\end{equation}
-so $\mathrm{Gate}_t=\mathbf{1}\{C^{\mathrm{LCB}}_t\ge\tau_{\mathrm{cov}}\}$ with
-$\tau_{\mathrm{cov}}=0.05$.  WARMUP and RESET force the Gate off.  It does
-not switch Design.  The predictor and calibration scores use completed past
-windows; the current window's realized $C_t$ is used after completion to
-audit the bound and update the diagnostic state for subsequent windows.
-
-Let $D_t\in\{\mathrm{on},\mathrm{off}\}$ be the Design factor of window $t$:
-a configuration of the deployment, fixed before the window opens, recorded
-with it, and held constant through its close.  The opportunity/design factor is
+The order is reference reconstruction, P2, aggregation, then debt
+(Section~\ref{subsec:debt}) and lagged-state updates.
+If $\mathcal A_r=\varnothing$, carry forward model and debt without adding
+the window to $S_R$.
+
+The recorded configuration $D_t\in\{\mathrm{on},\mathrm{off}\}$ is fixed before
+opening and throughout window $t$:
 \begin{equation}
 \widehat\zeta^{o}_{k,t,i}
 =
@@ -873,57 +813,78 @@
 \end{cases}
 \label{eq:design_factor}
 \end{equation}
-With $D_t=\mathrm{on}$ this is the lagged ratio
-\eqref{eq:design_ratio_simple}, the setting called RAVEN-Design; with
-$D_t=\mathrm{off}$ it is the uncorrected factor one, called RAVEN-NoDesign,
-and the result is not target-mass reconstruction.
-\eqref{eq:design_factor} is the only place the two settings differ: the
-observation, usable-update, calibration, and debt steps are identical.
-The Design-on/off experiments fix $D_t$ to on/off, respectively, for the
-entire run.  Equation~\eqref{eq:design_gate} describes a block-level support
-check on a specified training-unit catalogue.  It can supply a pre-window
-configuration only when that catalogue and its public target lookup are
-already available.  The supplemental material reports the catalogue counts
-separately from the coverage diagnostic.
+RAVEN-Design uses the lagged ratio.  RAVEN-NoDesign retains the opportunity
+arrival law.  All other correction, calibration, and debt steps coincide.
+On/off comparison arms fix the setting throughout a run.  The catalogue check
+\eqref{eq:design_gate} can inform configuration only when its catalogue and
+public lookup already exist before opening, independently of coverage.
 
 \begin{algorithm}[t]
-\caption{Window-close RAVEN-MCS with the Design factor as an explicit configuration}
+\caption{Window-close RAVEN-MCS with configured Design}
 \label{alg:window_close}
 \begin{algorithmic}[1]
-\REQUIRE window $t$; recorded $R_{k,t,i}$, $O_{k,t,i}$, $U_{k,t}$;
-public $\boldsymbol\mu$; debt $\mathbf{Q}_t$; model $\theta_t$;
-frozen public $\pi^{\mathrm{tar}}$; Design factor $D_t\in\{\mathrm{on},\mathrm{off}\}$
-recorded before window opening and held fixed within the window
-\ENSURE $\theta_{t+1}$, $\mathbf{Q}_{t+1}$
-\STATE Form $\mathcal{E}_t$ and
-$\mathcal{U}_t=\{k\in\mathcal{E}_t:U_{k,t}=1\}$.
-\IF{$D_t=\mathrm{on}$}
-\STATE Compute lagged opportunity/design ratios
-$\widehat\zeta^{o}_{k,t,i}$ \COMMENT{RAVEN-Design}
+\REQUIRE window $t$; recorded $R,O,U$; model $\theta_t$ and debt $\mathbf Q_t$;
+public $\boldsymbol\mu,\pi^{\mathrm{tar}}$; pre-window $D_t$ and frozen
+correction/constraint parameters, $\eta_t$, and lagged states
+\ENSURE $\theta_{t+1}$, $\mathbf Q_{t+1}$
+\STATE Form $\mathcal E_t$ and $\mathcal U_t=\{k\in\mathcal E_t:U_{k,t}=1\}$.
+\STATE Apply configured Design via \eqref{eq:design_factor}.
+\STATE Compute $a_{k,t,i}$ and $m_{k,t}$ via \eqref{eq:a_stabilized}--\eqref{eq:m_total};
+set $\mathcal A_t=\{k\in\mathcal U_t:m_{k,t}>0\}$.
+\IF{$\mathcal A_t=\varnothing$}
+\STATE Carry forward $\theta_t,\mathbf Q_t$; exclude this window from $S_R$; stop this window.
 \ELSE
-\STATE Set $\widehat\zeta^{o}_{k,t,i}\leftarrow 1$ on observed pairs \COMMENT{RAVEN-NoDesign}
-\ENDIF
-\STATE Compute observation weights $a_{k,t,i}$ and masses $m_{k,t}$;
-set $\mathcal{A}_t=\{k\in\mathcal{U}_t:m_{k,t}>0\}$.
-\IF{$\mathcal{A}_t=\varnothing$}
-\STATE Set $\theta_{t+1}\leftarrow\theta_t$,
-$\mathbf{Q}_{t+1}\leftarrow\mathbf{Q}_t$, and stop.
-\ELSE
-\STATE Compute usable-update factors $d_{k,t}$ and reference
-$\widehat{\boldsymbol\beta}_t$.
-\STATE Form $\mathcal{C}_t$ and lagged $V_t$,
-$\overline{\boldsymbol\tau}_t$; solve (P2) for
-$\boldsymbol\alpha_t^\star$.
-\STATE $\theta_{t+1}\leftarrow\theta_t
--\eta_t\sum_{k\in\mathcal{A}_t}\alpha^\star_{k,t}\mathbf{u}_{k,t}$.
-\STATE $\boldsymbol\omega_t\leftarrow M_t\boldsymbol\alpha_t^\star$,
-$\mathbf{Q}_{t+1}\leftarrow
-[\mathbf{Q}_t+\eta_t(\boldsymbol\mu-\boldsymbol\omega_t)]_+$.
+\STATE Reconstruct $d_{k,t}$ and $\widehat{\boldsymbol\beta}_t$ via
+\eqref{eq:d_use}--\eqref{eq:beta_ref}.
+\STATE Form $\mathcal C_t$ and lagged $V_t,\overline{\boldsymbol\tau}_t$;
+solve P2 for $\boldsymbol\alpha_t^\star$.
+\STATE Update $\theta_{t+1}$ by \eqref{eq:server_update}.
+\STATE Set $\boldsymbol\omega_t=M_t\boldsymbol\alpha_t^\star$;
+apply the debt recursion of Section~\ref{subsec:debt}.
 \STATE Advance lagged selection and variance states.
 \ENDIF
 \end{algorithmic}
 \end{algorithm}
 
+\subsection{Finite-Sample Aggregate Coverage Certificate}
+\label{subsec:agg_certificate_alg}
+\label{subsec:agg_coverage_object}
+
+For target-positive pairs $I_{\mathrm{tar}}=\{(k,s):\pi^{\mathrm{tar}}_{k,s}>0\}$,
+diagnose realized coverage
+\begin{equation}
+ C_t
+ =
+ \sum_{(k,s)\in I_{\mathrm{tar}}}
+ \pi^{\mathrm{tar}}_{k,s}
+ \,
+ \mathbf{1}\!\left\{\pi^{\mathrm{opp}}_{k,s,t}\ge\pi_{\mathrm{safe}}\right\},
+ \label{eq:agg_Ct}
+\end{equation}
+Here $\pi^{\mathrm{opp}}_{k,s,t}$ is lagged opportunity mass and
+$\pi_{\mathrm{safe}}$ is frozen.  Lookup construction is in
+Appendix~\ref{app:itar_lookup}.  Unlike conformal prediction
+sets~\cite{lu2023federated,plassier2023conformal}, this is aggregate opportunity
+coverage.  The diagnostic uses pre-window information $F_{t-}$ and
+\begin{equation}
+ k_n=\lceil(n+1)(1-\alpha)\rceil,
+ \qquad
+ \alpha=0.05,
+ \label{eq:agg_kn}
+\end{equation}
+Use the historical same-block quantile $q_t=S^{\mathrm{cal}}_{(k_n)}$ in
+\begin{equation}
+ C^{\mathrm{LCB}}_t=\max\{0,\widehat C_t-q_t\},
+ \label{eq:agg_CLCB}
+\end{equation}
+with $\mathrm{Gate}_t=\mathbf1\{C_t^{\mathrm{LCB}}\ge\tau_{\mathrm{cov}}\}$,
+$\tau_{\mathrm{cov}}=0.05$.  WARMUP/RESET set Gate to zero without switching
+Design.  Prediction and calibration use completed past windows.  Realized $C_t$
+audits the bound and updates diagnostic state only after completion.
+Section~\ref{subsec:agg_coverage_theory} gives conditional guarantees.  The
+supplemental algorithm specifies the historical quantile construction.
+The CERTIFIED state does not establish exchangeability, and the stable-regime
+guarantee does not extend to arbitrary unannounced drift.
 
 \section{Theoretical Analysis}
 \label{sec:theory}
@@ -1725,7 +1686,7 @@
 and debt accounts for accumulated group under-service through the one-sided
 bound \eqref{eq:debt_bound}.  The anchor term is
 what makes the problem strictly convex, so the flat $\ell_1$ surface of
-Section~\ref{subsec:P2} does not make the solved point arbitrary.
+Section~\ref{subsec:ceiling} does not make the solved point arbitrary.
 
 \begin{table}[!htbp]
 \centering
@@ -2091,6 +2052,12 @@
 ($144$ groups).  The factor that moves $\mathrm{RMSE}_{\mu}$ by several points
 on U-Air is Design, and it acts on which client windows are active, as the two
 window counts show, rather than on the weights inside a window.
+Over the $3279$ audited active windows, the feasible range of
+$\|M_r\boldsymbol\alpha-\boldsymbol\mu\|_1$ has median $10^{-13}$.
+This is the $\ell_1$ evaluation geometry, not constancy of the squared
+$\ell_2$ term in P2.  Limited group support can restrict observable alignment
+even when feasible weights differ.  This main-comparison audit is separate
+from the development geometry below.
 NSW-Traffic is the block on which most windows have $K_r>3$; its prediction
 measurement is in Section~\ref{subsec:limitations}.
 
```

## appendix.tex

```diff
--- this-round-start/appendix.tex
+++ current/appendix.tex
@@ -72,7 +72,7 @@
 fraction of those zeros, not $\#\{i:\varpi_i^{\mathrm{tar}}=0\}$, and
 not a positivity check on target-positive pairs.  It is the input of the
 block-level support rule (42).  This catalogue statistic can inform the
-Design configuration of (32) only if its inputs are available before the
+Design configuration of \eqref{eq:design_factor} only if its inputs are available before the
 window opens; both fixed on/off settings are reported.
 The pair opportunity mass $\pi^{\mathrm{opp}}_{k,s,t}$ is
 $F_{t-}$-measurable on the same client--stratum key.
@@ -234,7 +234,7 @@
 
 \begin{proposition*}[Normalized target reconstruction]
 Under A1--A3, for any bounded test function $\psi(k,i)$, distinct from
-the Design factor of (32), the H\'ajek ratio in
+the Design factor of \eqref{eq:design_factor}, the H\'ajek ratio in
 (35) converges in probability to
 \begin{equation}
     \Phi^{\mathrm{tar}}
```

