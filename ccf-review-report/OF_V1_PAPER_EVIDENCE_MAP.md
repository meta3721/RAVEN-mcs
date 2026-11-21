# OF-v1新增论文内容的证据对应

## 使用范围与核验方式

规范稿为 [main.tex](C:/Cursor/raven.mcs/TO_OVERLEAF_paper_tmc_r1_clean/main.tex)、[appendix.tex](C:/Cursor/raven.mcs/TO_OVERLEAF_paper_tmc_r1_clean/appendix.tex) 和 [supplemental.tex](C:/Cursor/raven.mcs/TO_OVERLEAF_paper_tmc_r1_clean/supplemental.tex)。正文控制段在第13页，附录L-A从补充第13页开始，五臂表XXXII在补充第14页。

仅纳入已完成的Traffic开发种子45001控制诊断。没有将网格、窗口或动作视为独立种子，没有新增统计检验，没有预测效果结论。q=.5的诊断先验身份保留。本次从既有CLOSURES重算简单均值以核对入稿数字；未运行原验证脚本的训练/模型加载路径。

轻量核验输出：[final_evidence_audit.json](C:/Cursor/raven.mcs/tmp/of_stop_paper/final_evidence_audit.json)。核验脚本：[audit_existing_evidence.py](C:/Cursor/raven.mcs/tmp/of_stop_paper/audit_existing_evidence.py)。这些文件位于临时工作目录；正式交付索引仅使用本目录中的MD。

## 五臂表：app:release_timing / tab:release_timing

统一原表：[SMALL_VALIDATION_COMPARISON.csv](C:/Cursor/raven.mcs/results_of_v1_small_scope_20261018_190539/SMALL_VALIDATION_COMPARISON.csv)，字段为strategy、seed、T_actual、q_role、G、W、J、G_n、W_n、J_n。论文按六位小数显示，G/W/J均越低越好。

- **OF-v1**：G=0.9452180232558112，W=0.6015037593984962，J=0.9898797986022612；分母800/133/133。原始关闭记录：[CLOSURES.json](C:/Cursor/raven.mcs/results_observed_feedback_autonomous_pilot_45001_20261014/of_resume1/CLOSURES.json)。原摘要字段G_800、W_mean_post20_including_empty、J_mean_nonempty_post20位于同目录VALIDATION_AND_SUMMARY.json。
- **OF-no-Q-stop**：G=0.9452180232558112，W=0.6015037593984962，J=0.9898797986022612；分母800/133/133。原始记录：[CLOSURES.json](C:/Cursor/raven.mcs/results_observed_feedback_autonomous_pilot_45001_recovery_20261015/noqstop/CLOSURES.json)，摘要为同目录VALIDATION_AND_SUMMARY.json中的上述三字段。
- **GAP20-fixed-reference**：G=0.9193750000000022，W=0.8602150537634409，J=0.9741633395843979；分母800/93/93。原始记录：[CLOSURES.json](C:/Cursor/raven.mcs/results_of_v1_small_scope_20261018_190539/gap/CLOSURES.json)；[C_VALIDATION.json](C:/Cursor/raven.mcs/results_of_v1_small_scope_20261018_190539/C_VALIDATION.json)字段G、W、J、G_denominator、W_denominator、J_denominator、full_T100。
- **fixed_time_0.5**：G=0.9588590116279057，W=0.5063291139240507，J=0.9973086359124509；分母800/158/158。原始记录：[CLOSURES.json](C:/Cursor/raven.mcs/results_observed_feedback_autonomous_pilot_45001_recovery_20261015/fixed05_resume1/CLOSURES.json)，摘要为同目录VALIDATION_AND_SUMMARY.json。
- **fixed_time_2**：G=0.8430825786217807，W=2.0，J=0.9493079462553562；分母800/40/40。原始记录：[CLOSURES.json](C:/Cursor/raven.mcs/results_observed_feedback_autonomous_pilot_45001_recovery_20261015/fixed2_resume1/CLOSURES.json)，摘要为同目录VALIDATION_AND_SUMMARY.json。

**指标定义**直接对应 [verify_observed_feedback_recovery_arm_v2.py:93](C:/Cursor/raven.mcs/scripts/verify_observed_feedback_recovery_arm_v2.py:93) 至其后原指标块：

- G：tick201…1000共800个网格，对当时最近非空真实释放的preview.ell取均值。ell为实际P2组成与目标的半L1距离，不是RMSE，也不借用其他协议的Delta_group尺度。
- W：time>20且duration>0的全部关闭记录的duration均值，定义包含空关闭和终点；本批五臂实际空关闭均为0。单位为受控逻辑服务时间，不是墙钟或注册到消费延迟。
- J：上述post20非空关闭的preview.ell+.02*preview.age+.20*duration/4均值，仅为辅助端点。

## 新增比较和机制数值

### 正文第13页及附录L-A：滚动参考与固定参考的取舍

H=OF-no-Q-stop，S=GAP20-fixed-reference。按CSV原值计算：

- 100*(1-W_H/W_S)=30.0751879699248%，正文显示30.08%，附录显示30.0752%。
- G_H-G_S=0.0258430232558090，正文显示0.02584，附录显示0.0258430，属于G的绝对差，不是百分点或RMSE。
- 反方向为S相对H的G下降约2.734081%、W上升约43.010753%；没有将该分母与前方向混用。

来源为上述两行原始指标，以及 [DECISION_REPORT.md](C:/Cursor/raven.mcs/ccf-review-report/of_v1_small_scope_20261018_190539/DECISION_REPORT.md) 的主要机制比较。独立按原关闭记录重新求和时，浮点累加使G差有约5e-15差异；在1e-12核对容差内，论文显示完全一致。这不是重新评分或统计检验。

正文和附录均同时保留等待缩短与失配上升，结论限于该种子的自主运行；没有写成两策略统计等价、普遍控制优势或窗内RAVEN效果检验。

### 129/799、129/582及参考值变化

来源：[A_RESULT.json](C:/Cursor/raven.mcs/results_of_v1_small_scope_20261018_190539/A_RESULT.json) 与 [A_PER_GRID.csv](C:/Cursor/raven.mcs/results_of_v1_small_scope_20261018_190539/A_PER_GRID.csv)。本次逐行复核CSV的forced、different、original_action、shadow_action和reference_difference：

- total_regular_grids=799，free_grids=582，differences=129。
- fraction_all=129/799=16.145181476846…%，显示16.1452%；fraction_free=129/582=22.164948453608…%，显示22.1649%。
- CLOSE_to_WAIT=129、WAIT_to_CLOSE=0。这里是原轨迹的同状态影子读出，与自主G/W分开，不另生成影子效用。
- 自由状态reference_difference（动态c_minus减固定c_ref）均值0.03955844053383594、中位数0.04052363581218976，附录显示0.0395584/0.0405236。最小值为负，因此只写该轨迹中通常放宽释放条件，没有写成所有状态或普遍定理。

论文位置：正文第13页只保留129/799，完整比例与参考差异在补充第13–14页。

### OF-v1与OF-no-Q-stop相同

来源为两臂原始CLOSURES及原VALIDATION_AND_SUMMARY.json；本次核对关闭time、duration、empty序列相同，G/W/J相同。附录末句明确只限本种子。该对照移除的是额外kappa_stop项；P2中Q及其更新仍保留。

## 规则、配置与信息边界

### 实际控制公式

- 原滚动规则：[controller.py:41](C:/Cursor/raven.mcs/src/raven_mcs_observed_feedback/controller.py:41) 及后续：c_minus=last_release.ell+.02*last_release.age；c=preview.ell+.02*preview.age；B=c_minus-c+kappa_stop*b+.20*clip(elapsed/4,0,1)。保存后的age不重新老化。OF-v1的额外停止系数为.1。
- 固定规则：[gap_local.py:75](C:/Cursor/raven.mcs/results_of_v1_small_scope_20261018_190539/gap_local.py:75) 附近的GapController.decide，以及 [FREEZE.json](C:/Cursor/raven.mcs/results_of_v1_small_scope_20261018_190539/FREEZE.json) 的formula、threshold、scientific_change：只将参考换为c_ref，额外停止系数为0；OF-no-Q-stop也为0。
- b为Q与实际组成减目标的内积，除以1+sum(Q)。Q非负时等于附录所写1+L1范数。它与正文P2中的Q项分别说明，没有更改原P2目标。
- [preview.py:38](C:/Cursor/raven.mcs/src/raven_mcs_observed_feedback/preview.py:38) 的compute_numeric使用完整RavenAggregator或同一完整目标的精确单点可行集分支；omega=M@alpha、ell=.5*abs(omega-mu).sum()、age=alpha@((version-downloaded_version)/5)。没有用另一几何距离代替实际组成。
- 原控制器与GapController的优先级同为终点、暖启动、deadline、K<3、自由控制；阈值.02+1e-7。论文公式不编号，不改变已有公式/定理编号。

### 固定参考及合法分叉

[FREEZE.json](C:/Cursor/raven.mcs/results_of_v1_small_scope_20261018_190539/FREEZE.json)字段c_ref、reference_time、reference_ell、reference_age、frozen_UTC：

- c_ref=0.9168365859958755。
- 来自旧noqstop/CLOSURES.json中time=20的非空释放，ell=0.9069767441860466、age=0.49299209049144466；ell+.02*age精确对应冻结值。
- 冻结时间2026-10-18T11:05:14.147624+00:00；没有利用post20结果选择参考。
- 合法父点：[tick0200.complete.json](C:/Cursor/raven.mcs/results_observed_feedback_autonomous_pilot_45001_recovery_20261015/noqstop/trajectory/tick0200.complete.json)。新臂终点：[tick1000.complete.json](C:/Cursor/raven.mcs/results_of_v1_small_scope_20261018_190539/gap/trajectory/tick1000.complete.json)。

[ARM_FROZEN_PLAN.json](C:/Cursor/raven.mcs/results_of_v1_small_scope_20261018_190539/gap/ARM_FROZEN_PLAN.json)的branch记录restored_scientific_and_RNG_equal、registered_messages_unchanged及合法父点。旧注册保留原概率与时钟身份；新注册另有scope/clock_namespace。三臂暖启动20条关闭的科学字段相同，策略相关fingerprint/dependency_hash不要求相同。本文不把此种共同暖启动当成全程相同状态。

### 论文设置段的实际参数

ARM_FROZEN_PLAN.json：config记录T对应scope.T=100、grid=.1、warmup=20、deadline=4、age_max=5、minimum_clients=3、Design.enabled=True；settings记录lambda_group/lambda_beta=1/1、lambda_variance/lambda_staleness=.1/.1、alpha_max=.5、e_min=3、server_eta=.01、max_server_learning_rate=1、d_max=10、q_min=.05、v_floor=.0001；scope.learning记录CommonNDMF、existing_hajek_sgd、local_steps=1、learning_rate=.01；scope.stage1记录a_max=20、p_min=.05、pi_min=1e-6。

论文按真实K写cap=max(.5,1/K)、有效支持最低min(3,K)。q_role=diagnostic_prior_not_calibrated、q=.5、calibration_only=True。覆盖Gate只诊断，闭窗记录configured_design=actual_design=1。新臂从合法父点后自主训练和消费，不从B阶段SGD0验证点出发，也不回放旧最终载荷。

## 保留但未作论文效果主张的证据

- [DECISION.json](C:/Cursor/raven.mcs/results_of_v1_small_scope_20261018_190539/DECISION.json) 的L_MECHANISM_UTILITY_NOT_ESTABLISHED保持。原开发门槛属于投入决策，未移入学术正文。
- [C_VALIDATION.json](C:/Cursor/raven.mcs/results_of_v1_small_scope_20261018_190539/C_VALIDATION.json) 表明full_T100=True、full_P3=False、finite_model=True。它不能替代概率校准、充分训练、预测保护或多种子证据。
- [RESOURCE_AND_BUDGET.md](C:/Cursor/raven.mcs/ccf-review-report/of_v1_small_scope_20261018_190539/RESOURCE_AND_BUDGET.md) 与BUDGET_FINAL.json只用于停止与保留资产记录；没有形成CPU加速比。新臂复用暖启动，旧臂恢复费用口径不同。
- 实现/采集入口仅索引：[gap_local.py](C:/Cursor/raven.mcs/results_of_v1_small_scope_20261018_190539/gap_local.py)、[stage_c.py](C:/Cursor/raven.mcs/results_of_v1_small_scope_20261018_190539/stage_c.py)、[IMPLEMENTATION_NOTE.md](C:/Cursor/raven.mcs/ccf-review-report/of_v1_small_scope_20261018_190539/IMPLEMENTATION_NOTE.md)。本轮没有执行这些入口，没有复制模型资产或声明公开发布。
