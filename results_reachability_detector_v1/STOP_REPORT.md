# STOP_REPORT

日期：2026-10-12T19:46:57.450967+08:00。状态：STOP_METHOD_IDENTITY_MISMATCH。失败层：G0；G1–G5 全部 SKIPPED。

## 首个失败条件

用户协议0.2要求：“旧论文的 configured-Design 与代码的 aggregate_coverage 身份冲突若仍存在，涉及旧方法结果归属和下游核验的阶段不能启动”；1.4要求基线身份明确。本轮确认该冲突仍存在。状态名只是将该明确条件编码，不改变协议门槛。

论文预配置 Design 并仅诊断 coverage；实际 `raven_mcs` 注册为 aggregate_coverage，runner 以 Gate 驱动 Design，函数忽略静态配置。静态反例：预配置D=1、Gate=0，论文D=1，实际D=0。没有性能数值被伪装成新检测结果。

## 对应基线与影响

Traffic/41001 旧 Uniform 开发结果 RMSE_mu=253.1132 vehicles/h 的缓存继承冲突实现；它未确认跨种子及训练平台，不能作为 configured-Design 的已确认任务基线。Central-delivered 202.0554及47.01%是学习诊断，不是联邦或新RAVEN收益。B-exact须按真实组成和约束保留；B-anytime等尚未实现、核验或比较。coverage Gate对象不同，也不能将其缺陷当新检测器优势。

## 已花预算

新训练0条、GPU训练0秒、检测器实现0个、合成轨迹0条、真实检测回放0条、新增校准样本和消息均0。本次只读停止审计脚本CPU 0.015625秒、墙钟 0.014671秒；不含此前交互式读取的未计量CPU，不能称作全会话精确总CPU。未消耗8 CPU小时实验额度，也未启动旧112条训练。

## 已取消任务

- G0剩余可识别性、样本需求、成本估计、近邻来源和基线实现核验
- G1实际适用分支的T1/T1b/T2/T3/T4/T5/T6证明
- G2检测器接口实现及四条关键路径核验
- G3六类各200条合成轨迹，每条最多80次查看
- G4 Traffic 41001→41002→41003、SensorScope/U-Air条件回放
- G4正式确认42001–42020
- G5 H=1、H=8、最大半径替换、移除未来外集合消融与影子预测核验

## 错误性质与适用范围

这是方法身份/实现语义不一致，尚未评价新检测器的统计错误率、检测收益或成本；不能据此断言数学路线错误或所有可达性检测无效。统计假设仍未放行。发现后没有外部追加检索、换方法、调门槛、改代码或续跑。协议虽允许独立数学证明，但用户要求G0 PASS才进入G1，本轮没有启动独立证明。

旧实验、论文及旧STOP保留；旧状态仍为 STOP_P1_NO_VALID_UNIFIED_BACKBONE。新证据只写入 results_reachability_detector_v1。没有发布、推送或提交。

## 终点主张

- 检测收益：未评价。
- 任务性能不退步：未接入、未验证；不把纯诊断设想当实际配对证据。
- 预测收益/新RAVEN收益：没有对应证据，不作主张。

## 唯一协议修订候选（未执行）

另行授权一次 configured-Design 代码同步与身份核验，保留旧 coverage-controlled 路径和所有旧结果，产出窗口前D、独立Gate及缓存归属证据；通过后才可重新启动本协议G0，不自动恢复本停止状态。

## 失败来源定位

- [TO_OVERLEAF_paper_tmc_r1_clean/main.tex:171](C:/Cursor/raven.mcs/TO_OVERLEAF_paper_tmc_r1_clean/main.tex:171)：`the coverage Gate is a separate diagnostic.`
- [TO_OVERLEAF_paper_tmc_r1_clean/main.tex:207](C:/Cursor/raven.mcs/TO_OVERLEAF_paper_tmc_r1_clean/main.tex:207)：`configuration that the deployment fixes before the window opens and holds`
- [TO_OVERLEAF_paper_tmc_r1_clean/main.tex:210](C:/Cursor/raven.mcs/TO_OVERLEAF_paper_tmc_r1_clean/main.tex:210)：`empirical diagnostic in the supplemental material.`
- [TO_OVERLEAF_paper_tmc_r1_clean/main.tex:259](C:/Cursor/raven.mcs/TO_OVERLEAF_paper_tmc_r1_clean/main.tex:259)：`station clients, and a coverage Gate is audited only as a diagnostic that does not`
- [TO_OVERLEAF_paper_tmc_r1_clean/main.tex:284](C:/Cursor/raven.mcs/TO_OVERLEAF_paper_tmc_r1_clean/main.tex:284)：`\cite{lu2023federated,plassier2023conformal}; the diagnostic Gate in`
- [TO_OVERLEAF_paper_tmc_r1_clean/main.tex:999](C:/Cursor/raven.mcs/TO_OVERLEAF_paper_tmc_r1_clean/main.tex:999)：`diagnostic Gate, detailed as the aggregate coverage certificate algorithm of the`
- [TO_OVERLEAF_paper_tmc_r1_clean/main.tex:1016](C:/Cursor/raven.mcs/TO_OVERLEAF_paper_tmc_r1_clean/main.tex:1016)：`audit the bound and update the diagnostic state for subsequent windows.`
- [TO_OVERLEAF_paper_tmc_r1_clean/main.tex:1042](C:/Cursor/raven.mcs/TO_OVERLEAF_paper_tmc_r1_clean/main.tex:1042)：`separately from the coverage diagnostic.`
- [TO_OVERLEAF_paper_tmc_r1_clean/main.tex:1383](C:/Cursor/raven.mcs/TO_OVERLEAF_paper_tmc_r1_clean/main.tex:1383)：`false-safe probability of an empirical diagnostic Gate is bounded by`
- [TO_OVERLEAF_paper_tmc_r1_clean/main.tex:1433](C:/Cursor/raven.mcs/TO_OVERLEAF_paper_tmc_r1_clean/main.tex:1433)：`\item \textbf{Component roles:} which terms move structural diagnostics`
- [TO_OVERLEAF_paper_tmc_r1_clean/main.tex:1563](C:/Cursor/raven.mcs/TO_OVERLEAF_paper_tmc_r1_clean/main.tex:1563)：`decision.  The support-compatible mixture-target diagnostic on SensorScope`
- [TO_OVERLEAF_paper_tmc_r1_clean/main.tex:2199](C:/Cursor/raven.mcs/TO_OVERLEAF_paper_tmc_r1_clean/main.tex:2199)：`evaluated as a diagnostic.  Equation~\eqref{eq:design_gate} reports the`
- [src/raven_mcs/aggregation/method_policy.py:42](C:/Cursor/raven.mcs/src/raven_mcs/aggregation/method_policy.py:42)：`FORMAL_GATE_MODE = "aggregate_coverage"`
- [src/raven_mcs/aggregation/method_policy.py:122](C:/Cursor/raven.mcs/src/raven_mcs/aggregation/method_policy.py:122)：`"raven_mcs": MethodPolicy(`
- [src/raven_mcs/aggregation/method_policy.py:124](C:/Cursor/raven.mcs/src/raven_mcs/aggregation/method_policy.py:124)：`gate_mode="aggregate_coverage",`
- [src/raven_mcs/sag/r1l_design.py:57](C:/Cursor/raven.mcs/src/raven_mcs/sag/r1l_design.py:57)：`def design_from_gate(gate_t: int | bool) -> int:`
- [src/raven_mcs/sag/r1l_design.py:121](C:/Cursor/raven.mcs/src/raven_mcs/sag/r1l_design.py:121)：`del oracle_safe, current_C, current_mask, dataset_design_flag, design_enabled`
- [src/raven_mcs/sag/r1l_design.py:138](C:/Cursor/raven.mcs/src/raven_mcs/sag/r1l_design.py:138)：`design_t = design_from_gate(gate_t)`
- [src/raven_mcs/sag/r1l_design.py:170](C:/Cursor/raven.mcs/src/raven_mcs/sag/r1l_design.py:170)：`raise RuntimeError("Design_t must equal Gate_t")`
- [src/raven_mcs/training/window_runner.py:367](C:/Cursor/raven.mcs/src/raven_mcs/training/window_runner.py:367)：`Formal RAVEN-MCS (gate_mode=aggregate_coverage): Design_t := Gate_t`
- [src/raven_mcs/training/window_runner.py:393](C:/Cursor/raven.mcs/src/raven_mcs/training/window_runner.py:393)：`return int(rec["Gate_t"]), certs, rec.get("fallback_reason"), passed`
- [results_main_rebuild_r1/prepare_uniform.py:63](C:/Cursor/raven.mcs/results_main_rebuild_r1/prepare_uniform.py:63)：`policy=dataclasses.replace(POLICY_MAP['raven_mcs'],uses_debt=False,`
- [results_main_rebuild_r1/prepare_uniform.py:97](C:/Cursor/raven.mcs/results_main_rebuild_r1/prepare_uniform.py:97)：`gate_mode='aggregate_coverage',loss_policy=dataclasses.asdict(policy)),dest)`
