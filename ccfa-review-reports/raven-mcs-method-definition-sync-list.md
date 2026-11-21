# RAVEN-MCS 代码／实验协议同步清单

日期：2026-10-12。仅列后续改动，本轮未修改下列实现、测试、协议或历史结果。

采用定义见 `raven-mcs-method-definition-card.md`。默认方法必须消费窗口前显式配置；coverage Gate 与 Design 独立。不得仅改 formal/legacy 名字。

| 文件/位置 | 当前冲突行为 | 后续应同步的行为 | 受影响实验 |
|---|---|---|---|
| `src/raven_mcs/aggregation/method_policy.py`：FORMAL_GATE_MODE、POLICY_MAP、aliases | raven_mcs及formal别名解析为aggregate_coverage，注释规定Design:=Gate | 显式配置D的论文路径，与coverage-controlled候选分开注册；保留历史路径可追溯 | 未来完整RAVEN、B/P/R共享损失、Design消融；历史数据不可改名 |
| `src/raven_mcs/training/window_runner.py`：_decide_g_r、_apply_zeta、_process_window | 读取证书并把返回Gate用于本地机会因子；formal路径忽略静态Design配置 | 窗口前冻结并记录D；因子由D驱动；证书独立记录；当前R/O/U和窗口末数据不得反写本窗配置 | 所有端到端固定臂及活跃集/缓存；保持Obs/Use/P2/debt等完整组件 |
| `src/raven_mcs/sag/r1l_design.py`：design_from_gate、formal_decide_gate_and_design、apply_formal_design_zeta | 独占Design权限，等式硬编码；静态配置列为禁止控制 | coverage候选函数保留其身份；默认方法脱离此强制关联，允许合法窗口前配置；证书公式不因改名而改变 | coverage stress仅保留候选归属，不能复用为固定臂实验确认 |
| `results_main_rebuild_r1/prepare_uniform.py`：policy、record、cache | 继承raven_mcs的aggregate_coverage并捕获其本地损失，g_r同时当Design；重放和校准语义未完全闭合 | 新缓存需记录D、Gate、定义版本和输入时点；固定臂损失不能继承动态开关；旧缓存保持原身份 | 现有9条开发准备轨迹、Traffic单条Uniform开发结果；未来U/B/P/R共享缓存 |
| `ccfa-review-reports/raven-mcs-main-experiment-rebuild-design-20261011.md`：输入清单、四臂R、共同状态和消融 | 把aggregate-coverage称论文完整方法并要求其Design-on/off | 改为配置D的完整R；四臂本地校正/配置匹配；coverage是共同诊断，不是收益机制；先冻结方法身份再运行 | 尚未启动的42001–42020确认及机制轨道；不能把P1称已通过完整方法确认 |
| `results_main_rebuild_r1/EXECUTION_REPORT.md`及准备目录元数据 | gate-on比例是生产Design开关，不是独立诊断；Uniform路径沿旧定义 | 历史执行事实保留，补版本归属；集中式门槛不重解释；若将来更换定义，旧Uniform数字不转移 | 108 Central-delivered、3 Central-all不依赖此开关；1 Uniform诊断及几何/缓存依赖 |
| `scripts/compute_scd_phi.py`、`scripts/gate_dose.py`、相关冻结目录 | 前者枚举完整train目录；部分脚本使用delivered集合，统计框架不同 | 明确rho对象、唯一单位/事件分母、冻结时点；作者未决定前不统一成在线规则 | C2支持统计、gate-dose、外生目标及混合移动块配置；原数值保留 |
| `TO_OVERLEAF_paper_tmc_r1_clean/make_figures.py`：fig_certificate_audit docstring及来源命名 | 图生成描述Design:=Gate；方法显示名RAVEN-MCS不区分历史版本 | 后续只同步元数据/变体归属，不修改本次数值；当前图注已区分候选诊断 | 补充certificate表/图、历史E3/E4图；图的Gate量不改名为Design量 |
| `tests/unit/test_raven_mcs_resolves_to_aggregate_coverage.py`、`test_raven_mcs_not_always_on.py`、`test_window_close_receives_gate_t.py`及R1l/R1m身份测试 | 测试把旧等式和排除静态配置当正确性条件 | 后续按默认配置路径与coverage候选分别验证；加入窗口内固定、Gate不改变D、当前交付信息不前用的检查 | 防止实现同步后被旧身份测试回退；本轮不运行或改这些测试 |

后续实施前的阻塞项：作者确定target-support输入与可得时间、空目录行为，以及默认部署是否真的应用该规则。不能擅自新增滞后统计或自动选择机制。

同步后的证据要求：新方法运行保存完整policy、窗口前D和独立Gate日志；旧覆盖候选、固定臂与新缓存逐项对照。现有结果仅在行为及评分链一致时可支持对应配置；未来实验需另获授权，本清单不授权启动训练。
