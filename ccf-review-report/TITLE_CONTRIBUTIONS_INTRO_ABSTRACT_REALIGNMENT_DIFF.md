# 本次重新对齐：前后差异

日期：2026-10-31。本次以收到最新完整执行请求时的规范稿为基线。不是回退到481词旧引言；上一轮的详细差异已经归档保留。

## 标题与补充标题

修改前后均为：**RAVEN-MCS: Target-Mass Calibration for Windowed Federated Data Completion in Mobile Crowdsensing**。该默认短标题已符合要求，本次保留并核对两份PDF一致。补充源码无改动，PDF按本次主稿重新编译。

## 本次执行顺序

先完成第四段和三项贡献，再完成第二、三段，最后核对标题并修改八句摘要。阶段保存记录在`C:/Cursor/raven.mcs/tmp/title_realignment_recheck_20261031/execution_order.json`。

## 摘要：修改前（186词）

Mobile crowdsensing completion reconstructs urban and environmental fields from sparse distributed observations to support sensing services. However, sequential selection distorts their represented population, and finite windows can prevent a corrected target reference from being directly aggregated. Existing approaches address completion, participation bias, and target-aware aggregation, leaving the connection between sensing-unit reconstruction and constrained window execution to be specified. To bridge this gap, we propose RAVEN-MCS (Reference Alignment Via Exposure-aware Normalization for Mobile CrowdSensing), an integrated framework that converts reconstructed target references into executable client mixtures. Specifically, opportunity and observation correction jointly supply normalized local training weights and client reference masses. The framework then applies usability correction and calibrates group composition under weight caps and effective-support constraints while accounting for accumulated under-service. Rigorous theoretical analysis validates ideal pooled moment recovery under stated ratio, support, identification, and cluster conditions, and reference non-expansion at a shared fixed window state. Extensive experiments on real-world datasets demonstrate that RAVEN reduces group mismatch by 23.3\%--25.8\% versus TwoStage-H\'ajek in two City Scanner protocols with controlled delivery, while matched-support station comparisons and geometry diagnostics distinguish correction, projection, and adjustment limits.

## 摘要：修改后（202词，严格八句）

Mobile crowdsensing completion reconstructs urban and environmental fields from sparse distributed observations to support sensing services. However, sequential selection distorts their represented population, and finite windows can make the corrected reference infeasible under the available support and aggregation constraints. Existing approaches address completion, participation bias, and target-aware aggregation, whereas this setting requires an explicit link between sensing-unit reference reconstruction and constrained window execution. To bridge this gap, we propose RAVEN-MCS (Reference Alignment Via Exposure-aware Normalization for Mobile CrowdSensing), an integrated framework that converts reconstructed target references into executable client mixtures. Specifically, opportunity and observation correction jointly supply normalized local training weights and client reference masses. The framework then applies usability correction to form the server reference and calibrates executable weights under caps and effective-support constraints, coordinating reference fidelity, group targets, and accumulated under-service. Rigorous theoretical analysis validates ideal pooled moment recovery under stated ratio, support, identification, and cluster conditions, and reference non-expansion for anchored convex calibration at a shared fixed window state. Extensive experiments on real-world datasets demonstrate that RAVEN reduces group mismatch by 23.3\%--25.8\% versus TwoStage-H\'ajek in two City Scanner protocols with controlled delivery, while matched-support station comparisons and geometry diagnostics distinguish correction, projection, and adjustment limits.

## Introduction：修改前（612词）

```latex
Mobile crowdsensing (MCS) uses distributed mobile sensors to observe urban and environmental fields for applications including traffic and air-quality monitoring~\cite{ganti2011mobile}.
Uneven sampling leaves spatial and temporal gaps, motivating data completion for wider coverage and downstream sensing tasks~\cite{wang2025evolutionary,xu2025rethinking,liu2025nonaligned}.
Federated learning shares model updates while keeping the underlying sensing records distributed~\cite{mcmahan2017communication}.
In windowed asynchronous training, deployment-target service depends on both the representation of received information and its aggregation.

Deployment-oriented completion needs a clear account of which sensing population its training information represents and how that population differs from the intended target.
Visit opportunities and valid observations select records within clients according to where devices travel and what they can measure, whereas computation and transmission determine which trained updates are usable before window closure.
Received counts therefore need not follow deployment-target mass, even when client participation frequencies are known.
Completion representations exploit cross-task and non-aligned sensing structure~\cite{wang2024fewshot,liu2025nonaligned}, and asynchronous learning accommodates irregular updates~\cite{xie2019asynchronous}.
Participation correction adjusts unequal client contributions~\cite{wang2024lightweight,sun2025debiasing}; FedIPW additionally calibrates enrollment and participation using population summaries~\cite{morishita2026who}.
However, normalizing each client's training weights removes the total mass scale that the server needs to represent relative client contributions after sequential selection.
The challenge is to link these local and between-client quantities to the same sensing-unit target using only information available before the corresponding selection outcomes.

Beyond statistical reconstruction, a finite window can aggregate only the client updates that are usable at closure, so a corrected reference need not itself be an executable allocation.
Available group compositions, per-client weight caps, and effective-support constraints jointly delimit the mixtures that can be formed, even with accurate selection ratios.
Participation analyses and semi-asynchronous bias correction address unequal or irregular update contributions~\cite{wang2022unified,chen2026fedcure}; participation-weight estimation supplies an additional adjustment mechanism~\cite{wang2024lightweight}.
FedIPW calibrates population summaries under limited information~\cite{morishita2026who}, while FedPALS uses convex target-label matching and sample-ESS regularization, including targets outside the client convex hull~\cite{listozec2024overcoming}.
The task here is to connect a sequentially reconstructed sensing-unit reference to the constrained mixture available in the current window.
Group under-service can also accumulate across windows, motivating a state that records service deficits alongside instantaneous reference matching.
This connection calls for feasible allocation together with an account of how reference errors affect weights and group composition on shared support.

To address the above challenges, we propose RAVEN-MCS (Reference Alignment Via Exposure-aware Normalization for Mobile CrowdSensing), a framework linking sensing-unit target-reference reconstruction to executable aggregation for windowed federated completion.
Specifically, opportunity and observation correction generate weights shared by normalized local training and client-mass estimation, and pre-outcome usability correction then rescales those masses to form the server reference for constrained calibration at window close.
Furthermore, the calibration program coordinates fidelity to the reference in client-weight space with deployment-group alignment and accumulated under-service, under weight caps and client-level effective-support constraints on current clients.
In this way, deployment-target mass reconstruction becomes an executable aggregation decision on the window's available support.
The major contributions of this work are summarized as follows:
\begin{enumerate}
\item We reconstruct deployment-target mass over atomic sensing units by linking sequential opportunity, observation, and usable-update correction. Opportunity/observation weights jointly determine normalized local training and client masses; server-side usability correction carries their relative mass into the reference, reconnecting local normalization with between-client representation.
\item We develop a window calibration program that converts the reconstructed reference into executable weights on available clients under weight caps and client-level effective-support constraints. Its reference anchor, group-composition term, and target-debt state coordinate statistical fidelity with current deployment service and accumulated under-service.
\item We characterize ideal pooled target-moment recovery under compatible support, correct ratios, sequential identification, and cluster regularity. For a shared fixed window state, we establish reference non-expansion of calibrated weights and a composition perturbation bound, separating estimation error from stabilization error under convexity, positive-mass, and bounded-error conditions.
\end{enumerate}
```

## Introduction：修改后（632词）

```latex
Mobile crowdsensing (MCS) uses distributed mobile sensors to observe urban and environmental fields for applications including traffic and air-quality monitoring~\cite{ganti2011mobile}.
Uneven sampling leaves spatial and temporal gaps, motivating data completion for wider coverage and downstream sensing tasks~\cite{wang2025evolutionary,xu2025rethinking,liu2025nonaligned}.
Federated learning shares model updates while keeping the underlying sensing records distributed~\cite{mcmahan2017communication}.
In windowed asynchronous training, deployment-target service depends on both the representation of received information and its aggregation.

Deployment-oriented completion needs a clear account of which sensing population its training information represents and how that population differs from the intended target.
Visit opportunities and valid observations select records within clients according to where devices travel and what they can measure, whereas computation and transmission determine which trained updates are usable before window closure.
Received counts therefore need not follow deployment-target mass, even when client participation frequencies are known.
Completion representations exploit cross-task and non-aligned sensing structure~\cite{wang2024fewshot,liu2025nonaligned}, and asynchronous learning accommodates irregular updates~\cite{xie2019asynchronous}.
Participation correction adjusts unequal client contributions~\cite{wang2024lightweight,sun2025debiasing}; FedIPW additionally calibrates enrollment and participation using population summaries~\cite{morishita2026who}.
However, normalizing each client's training weights removes the total mass scale that the server needs to represent relative client contributions after sequential selection.
The challenge is to reconstruct local training weights and server reference mass for the same sensing-unit target, using only the information available before each selection outcome.

Beyond statistical reconstruction, a finite window can aggregate only the client updates that are usable at closure, so a corrected reference need not itself be an executable allocation.
Available group compositions, per-client weight caps, and effective-support constraints jointly delimit the mixtures that can be formed, even with accurate selection ratios.
Participation analyses and semi-asynchronous bias correction address unequal or irregular update contributions~\cite{wang2022unified,chen2026fedcure}; estimating participation weights provides a correction for these contribution imbalances~\cite{wang2024lightweight}.
FedIPW calibrates population summaries under limited information~\cite{morishita2026who}, while FedPALS uses convex target-label matching and sample-ESS regularization, including targets outside the client convex hull~\cite{listozec2024overcoming}.
The task here is to connect a sequentially reconstructed sensing-unit reference to the constrained mixture available in the current window.
Group under-service can also accumulate across windows, motivating a state that records service deficits alongside instantaneous reference matching.
The challenge is to coordinate fidelity to the reconstructed reference with feasible deployment-group service and cumulative deficits, while characterizing how reference errors propagate through this allocation.

To address the above challenges, we propose RAVEN-MCS (Reference Alignment Via Exposure-aware Normalization for Mobile CrowdSensing), a framework linking sensing-unit target-reference reconstruction to executable aggregation for windowed federated completion.
Specifically, opportunity and observation correction generate weights shared by normalized local training and client-mass estimation, and pre-outcome usability correction then rescales those masses to form the server reference for constrained calibration at window close.
Furthermore, the calibration program coordinates fidelity to the reference in client-weight space with deployment-group alignment and accumulated under-service, under weight caps and client-level effective-support constraints on current clients.
In this way, RAVEN-MCS turns the reconstructed reference into a feasible client mixture that targets deployment-group alignment within the available sensing support.
The major contributions of this work are summarized as follows:
\begin{enumerate}
\item We reconstruct a deployment-target reference over atomic sensing units through sequential opportunity, observation, and usable-update correction. Shared opportunity and observation weights supply normalized local training and client-mass estimates; usability correction then rescales these masses into a server reference that retains relative representation across clients.
\item We develop a window calibration program that converts the reconstructed reference into executable weights on available clients under weight caps and client-level effective-support constraints. Its reference anchor, group-composition term, and target-debt state coordinate statistical fidelity with current deployment service and accumulated under-service.
\item We characterize ideal pooled target-moment recovery under compatible support, correct ratios, sequential identification, and cluster regularity. For anchored convex calibration on shared support with the remaining window state fixed, we establish reference non-expansion of weights and a composition perturbation bound, separating estimation and stabilization errors under positive-mass and bounded-error conditions.
\end{enumerate}
```

## 主要实质调整

- 贡献一将质量对象写为reference及mass estimates，并明确可用性校正重标定客户端质量。
- 第四段的效果句明确参考→可行客户端混合→部署组对齐的对象连接。
- 两个挑战段分别明确本地训练/服务器参考重构、参考保真/可行服务/累计欠服务及误差传播。
- 理论贡献明确anchored convex calibration、shared support及remaining window state fixed，非扩张针对weights，组成另有perturbation bound。
- 摘要补足参考不可行的支持/约束原因、可用性校正形成服务器参考以及校准对参考保真和组目标的协调；实验句和全部数字保持。

## 保护范围与恢复

除main.tex摘要与引言外的规范内容未改；II节及之后文本、所有数学与实验数字、附录、补充源码、书目和图片保持。完整局部diff：`C:/Cursor/raven.mcs/tmp/title_realignment_recheck_20261031/main.tex.diff`。

回退归档：`C:\Cursor\raven.mcs\ccf-review-report\backups\title_contributions_realignment_20261031_204903.zip`。本轮只需逆向合并main.tex中摘要/引言；无后续修改时可恢复归档main.tex和原两份PDF。有后续修改时按块合并，不整文件覆盖。归档`reports/`保留上一轮报告与差异。
