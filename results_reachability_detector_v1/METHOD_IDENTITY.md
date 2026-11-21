# G0 方法身份核验：未通过

论文定义是窗口前显式配置 Design，并在窗口内保持；coverage Gate 仅诊断。当前注册表仍将 `raven_mcs` 指向 aggregate_coverage；runner 返回 Gate 驱动机会校正；r1l_design 明确丢弃静态配置并要求 Design=Gate。

静态语义反例：预配置 Design=1、Gate=0 时，论文路径应保持 Design=1；实现路径给出 Design=0。这是控制行为差异，不是标签或别名差异，也不是一次实验失败率。

对应任务基线是旧 Traffic/41001 Uniform 开发轨迹，它的缓存继承该实现路径，不能转归 configured-Design。历史固定 on/off 臂、覆盖候选和本协议纯检测器保持分别归属。未修改任何代码以解除冲突。

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
