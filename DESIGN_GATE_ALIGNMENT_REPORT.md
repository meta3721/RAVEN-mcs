# Design / coverage Gate 实现同步报告

日期：2026-10-12。规范来源：`TO_OVERLEAF_paper_tmc_r1_clean/main.tex` 的预配置 Design 定义。此次没有修改论文，也没有把论文改回 Design := Gate。

**身份验收：IMPLEMENTATION_ALIGNED。性能结果：RESULTS_NOT_REVALIDATED。**

本状态限定于显式配置、完整运行计算链和历史归属一致性。它不代表覆盖率合格、目标完全可识别、风险下降、任务性能不退步或预测改善，也不代表此前主实验重新成立。此前 G0 停止状态及取消任务保持原状；本次没有启动下一层科学实验或大规模训练。

## 1. 根因与实际修复

旧 `raven_mcs` 注册将 `gate_mode=aggregate_coverage` 同时用于方法身份、Design 开关和诊断。`_decide_g_r` 返回 Gate，随后 `_apply_zeta` 将它用于本地训练和参考质量重构。WARMUP、RESET 和低 coverage 因而把论文预配置的 Design 关闭。旧源码字符串测试又强制该等式，进一步固定了冲突。

当前方法注册是 `raven_mcs / configured-design-v1`；独立历史注册是 `raven_coverage_legacy / coverage-controlled-v1`。前者保留完整 observation IPW、usable-update IPW、Hájek、本地训练、即时校准、debt、参考惩罚、方差与时效项；on/off 只改变实际机会 Design 因子。

修复位置如下。精确文件和修复前后哈希见 `results_design_gate_alignment_v1/CODE_CHANGES.json`；逐行补丁见同目录 `DESIGN_GATE_ALIGNMENT.patch`，其基准是本次修复前快照，包含本任务实际修改，而非整个已有工作区的变化。

| 位置 | 修复职责 |
|---|---|
| `aggregation/method_policy.py`、`aggregation/methods.py` | 独立 design_control、coverage_diagnostic、method_version；注册完整新版和明确 legacy 聚合入口 |
| `sag/r1l_design.py` | 不可变 DesignConfiguration、显式 on/off 验证、独立 Gate/Design 决策与应用函数；旧等式留在命名明确的 legacy 函数 |
| `training/window_runner.py` | 进入窗口时先冻结配置；真实本地权重、参考质量及 P2 使用实际 Design；窗口日志和指标分开保存 configured Design、actual Design、coverage Gate、来源和版本 |
| `correction/design_ratio.py` | 检查有限性与合法非负输入，保留概率下界；缺输入明确报错，不以 Gate=0 替代 Design |
| `utils/config.py`、`utils/validation.py`、`configs/method/` | 序列化显式设置和版本，检查设置一致性；legacy 配置身份也单独记录，拒绝被忽略的 Design 参数 |
| `scripts/run_experiment.py` | 读取显式配置并传入真实 factory；持久化各窗口 Design/Gate 日志；传递设备和本地步数；拒绝覆盖已有 summary，拒绝把简化 SyntheticGateRunner 当作新版完整方法 |
| `experiments/e1_entry.py` | 接入相同配置并记录窗口字段和运行身份；未解冻旧 E1 方法名单 |
| `experiments/r1m_method_freeze.py`、`legacy_coverage_freeze.py` | 当前部署冻结与历史 coverage 冻结分离；旧 R1l/R1m 审计入口必须显式选择 legacy |
| `sag/r1m_spec.py`、`sag/r1l_theory.py` | 将历史 coverage-controlled 身份及理论文本明确归入 legacy；不修改数学常数和旧证据文件 |
| 四个历史 `_skip_unused_gate` 入口 | 对 configured 和 coverage legacy 交回真实 FullWindowRunner 决策路径，避免旁路诊断/配置 |
| `training/cache_identity.py` | 在读取 Design 依赖的 Torch 缓存前核验精确配置、版本、角色及计算依赖，拒绝无身份或旧身份缓存 |

覆盖 Gate 的分支检查发现：新版只将 Gate 用于诊断记录及诊断状态；传播到实际计算的兼容变量 `G_r` 在新版中是冻结 Design。旧 `gate_mode` 仅在 legacy 决策分支解释，在新版中不决定方法身份、Design 或诊断方式。概率下界、输入有效性、P2 可行约束及旧阈值均保留。新版诊断模式按独立 policy 声明固定为 aggregate coverage，旧 sag_cov_mode 覆盖参数仅在 legacy 生效，其隔离行为也已验证。

没有添加按数据集名称、测试标签、当前窗口结果或未来信息选择 Design 的规则，也没有新增 catalogue 自动选择。公开目标和机会输入仍须在窗口前合法可用；本次支持的选择方式是明确的 on/off。

## 2. 四种组合的真实执行证据

证据：`FOUR_COMBINATIONS.json` 和 `tests/integration/test_configured_design_runner.py`。测试实际执行 CommonNDMF、ClientTrainer 的一个本地 SGD 步、完整 RavenAggregator/P2 与服务器更新；捕获的是实际传给训练器的权重和实际聚合输入，不是仅检查日志。为隔离两个变量，只控制 certificate 输出，训练、修正、重构和求解均使用生产实现。

两个客户端每窗各有四条有效观测；合法冻结机会质量均为 1/8，公共目标质量分别为 `[.04,.08,.16,.32]`、`[.02,.06,.12,.20]`，总和为 1。因此非恒等设计比率是 `[.32,.64,1.28,2.56]`、`[.16,.48,.96,1.60]`。实际 observation 预测冷启动概率为 .2。

| configured Design | coverage Gate | 实际 Design 因子（客户端 0 / 1） | 实际本地归一化权重（客户端 0 / 1） | 重构质量 | beta |
|---|---|---|---|---|---|
| 1 | 0 | `.32,.64,1.28,2.56` / `.16,.48,.96,1.60` | `1/15,2/15,4/15,8/15` / `.05,.15,.30,.50` | `24,16` | `.60,.40` |
| 1 | 1 | 同上非恒等比率 | 同上 | `24,16` | `.60,.40` |
| 0 | 0 | `1,1,1,1` / `1,1,1,1` | `.25,.25,.25,.25` / 同左 | `20,20` | `.50,.50` |
| 0 | 1 | 全 1 | 均匀本地权重 | `20,20` | `.50,.50` |

实际组成矩阵也与上述本地质量归一化结果逐项一致。固定 Design、仅改变 Gate 时，训练损失、服务器 alpha、参考组成、beta、debt、方差状态和所有模型张量相同；运行两窗的配对条件恢复了相同 Torch/NumPy/Python 随机状态。Design-on 的模型哈希为 `face86f3a47eaf20865e8a27666a58e373c6f09897338fd923befd073f3ea54a`，Design-off 为 `dac99ab31e9acd1a9be8de303b971d10cd7c2712c8ca418cb63cb6f5b43c4ce2`，各自不随 Gate 改变。这同时证明 Design 改变确实进入模型计算。

该小型样例的可行聚合接近均匀（on 约 `.500000000033,.499999999967`，off 为 `.5,.5`）。本验收没有借此声称优化自由度充分或聚合性能改善；它验证因子和参考质量确实作用于真实计算链。

## 3. 冻结、诊断状态、入口与 legacy

- WARMUP、RESET 均产生 Gate=0；预配置 Design=on 仍实际使用非恒等比率。
- 窗口开始、计算诊断之前冻结不可变配置。测试在诊断计算中将外部配置替换为 off：已打开的第一个窗口仍为 on，第二个允许开始的窗口才使用 off，来源也分别正确。
- 固定 on/off 的两窗运行保持设置不变；相反的 Gate 序列没有改变诊断之外的计算结果。
- 在线机会估计路径也实际执行：所有 Design 比率计算都早于当前窗口历史更新，且历史仅更新一次。
- 缺目标、NaN、负值在 Gate=0 时仍明确报输入错误，未退回 off。
- 实际命令行 main → build_full_runner → FullWindowRunner → 本地训练 → 聚合执行了两个小型窗口，并将配置和逐窗口身份写入 summary。测试提供冻结的目标/机会样例输入，替代外部数据读取；不是实际数据集性能运行。再次使用相同输出路径会报错，保留原结果。
- legacy 实际 Gate=0 使用全 1；Gate=1 使用设计比率。进一步加载修复前 runner 快照，在相同输入及随机状态下与当前 explicit legacy 比较，两种 Gate 下模型哈希、实际训练权重、更新向量、参考质量、组成、beta、alpha、debt 和方差输入完全一致，见 `LEGACY_BEFORE_AFTER_PARITY.json`。

历史兼容名 `formal_decide_gate_and_design` 仍导出旧函数，供旧快照/审计兼容；当前 runner 的正式分支调用的是 `configured_decide_gate_and_design`。历史理论审计中 Design := Gate 的检查只对应旧论文快照，不能作为当前 configured 实现的身份或证明门槛；这些历史审计未在本次启动。

## 4. 结果归属与缓存清单

`PRESERVATION_CHECK.json` 核验了 1,424 个已登记历史文件，变化数为 0，包含旧实验、旧 STOP_REPORT 和当前论文。没有删除缓存、覆盖模型、重新标注旧数值，或解冻被取消的 112 条训练。

`CACHE_DISPOSITION.json` 逐文件登记 905 个历史数值/模型文件的保留及复用限制；这份清单不是重跑清单。是否重算按实际依赖判断，不能按路径里出现 uniform 或同名方法判断。

| 对象 | 保留与处置 |
|---|---|
| 原始数据、合法预处理、Design 无关划分、原子记录、公共目标元数据 | 保留；数据内容/划分/归一化来源一致时可复用 |
| 固定 EventTrace 的 R/O/U 和公共机会信息 | 保留；作为配对共同输入时还须核验时间可用性、调度及生成规则，不从测试标签选配置 |
| 纯训练均值、适用的持久性/季节性预测器 | 若拟合只用相同训练划分，且预测目标、窗口、评价质量和缺失协议完全匹配，可作为独立基线比较；本次未重新计算性能 |
| central-all / central-delivered 等与 Design 无关模型 | 保留；只有数据、目标、输入可用性、预算、模型和指标相同才可比较；其存在不能证明新版 RAVEN 收益 |
| `results_main_rebuild_r1/prepared/**/uniform_cache.pt` 及相应参考/几何记录 | 旧 prepared 程序使用旧 raven_mcs 的 coverage-controlled Design，本地权重和重构质量依赖 Design，不能因为服务器均匀就复用；选定的新 on/off 比较须重新生成这些依赖 |
| Design 依赖的权重、裁剪/Hájek统计、M、beta、组成、debt/方差轨迹 | 新版本选择了不同因子或轨迹时重算；不能仅重新求服务器权重就当作新方法的全链结果 |
| 相应模型检查点、预测、RMSE、任务不退步统计及收益表 | 源模型或训练轨迹依赖旧 Design 时，选定的新比较须重训、重新预测和评价；旧文件仅以旧方法身份保留 |
| 输入依赖不明的历史数值缓存 | 隔离于 configured 复用；先恢复依赖信息再判断，不无差别重算全部历史文件 |

新通用正式入口从新模型开始，没有从旧模型缓存恢复的路径；已有结果目录被拒绝覆盖。`load_configured_artifact` 在 Torch 读取前要求 `.identity.json`，精确比较 DesignConfiguration、方法版本、coverage 角色和非空计算依赖，相关测试包含真实文件读取及旧/缺失身份拒绝。使用者须提供目标、trace、模型/优化器/训练配置等实际依赖标识；该工具不会自动为旧文件补身份。原 checkpoint 恢复机制的配置哈希也保留，新 resolved 配置包含 Design 和版本，因此不能按同名方法恢复旧配置。

`results_main_rebuild_r1` 中的历史执行脚本保持原样，仍只属于历史结果包，不能作为新版正式入口；其仅按文件存在返回 CACHED 的逻辑不得用于 configured 结果生成。复现旧结果应使用旧快照或明确的 legacy policy；若需要适配旧 prepared 脚本，应在新目录复制并显式接入 legacy 身份，不能覆盖原脚本/结果。本次未执行这些历史训练脚本。

## 5. 使用方式

配置核验，无训练：

```powershell
.venv_new/Scripts/python.exe scripts/check_design_gate_configuration.py --method raven_mcs --design on
.venv_new/Scripts/python.exe scripts/check_design_gate_configuration.py --method raven_mcs --design off
.venv_new/Scripts/python.exe scripts/check_design_gate_configuration.py --method raven_coverage_legacy
```

正式完整 factory：

```python
runner = build_full_runner(trace, dataset, method="raven_mcs",
                           design="on", design_source="explicit_run_config", ...)
# 配对 off 运行使用同样输入及其他参数，只将 design 改为 "off"。
legacy = build_full_runner(trace, dataset, method="raven_coverage_legacy", ...)
# legacy 不接受被忽略的 design 参数。
```

通用实验入口使用 `--method raven_mcs --design on/off --design-source ...`，提供合法冻结输入及新的 `--output-dir`。这些是后续获准的小型/正式运行用法，本报告没有启动新的性能实验。Design=on 不带 coverage 合格或风险降低的含义。

旧 R1l/R1m 审计入口需 `--method raven_coverage_legacy`，并使用相应历史输入/论文快照和新的输出目录；不能把历史证明审计直接作用于当前论文。旧 E1 冻结名单尚未添加新版方法，故不应使用其旧性能协议直接生成 configured 主结果；将来实验需单独定义新的冻结配置与输出归属。

## 6. 验证结果与未解决依赖

- 最终相关单元/集成测试：**226 passed，0 failed，0 skipped，23.20 秒**，见 `related-tests-final.xml/.log`。按实际导入依赖与迁移清单选择，文件范围见 `RELATED_TEST_FILES.json`。
- 最终 legacy 修复前后真实执行一致性：PASS，见 `legacy-parity-final.log`。
- Python 源文件编译：PASS。
- 项目要求的 `verify_run.py --check-environment --check-repository`：环境 PASS、仓库基础设施 PASS，见 `repository-check-unsandboxed.log`。该命令本身不验证数据、模型或 G0–G7。
- 全项目 pytest 收集 1,592 项，运行到约 80% 时 Windows 原生访问异常退出，退出码 `-1073741819`；堆栈位于 `manifest._git_info → sha256_file` 扫描仓库文件。**全项目测试未完成，不能标为通过**；根因未定位，见 `all-tests.log`。未通过跳过此测试制造全绿。
- 全项目运行曾发现的旧论文/Gate定义断言、历史快照符号和滞后计算子串断言，已逐项迁移并在上述 226 项中重验通过。诊断历史测试原来缺 event-count 输入，NaN 相等断言无效，已补齐合法历史计数，保留诊断机制及阈值。
- 两项历史 E1_R2 审计仍失败：`outputs/runs/E1_R2` 下没有审计器所需的 RAVEN formal runs。修复前快照和当前相同审计源码均复现相同缺失，见 `HISTORY_AUDIT_BASELINE.json`、`history-audit.log`。没有生成或冒充缺失运行来满足测试。这仅影响历史 E1_R2 审计，不能阻止已完成的新方法身份验收。
- 相关回归中的 4 条已有 P2 求解器准确性警告已保留；没有改变约束或接受标准来消除它们。

初始失败日志也保留：包括沙箱临时原子写权限、测试错误的冷启动概率预期、配置 schema 及入口样例依赖。实现/测试修正后只对相关范围重验，最终证据以 final 命名文件为准。

## 7. 预算与后续门槛

本次 GPU 正式训练预算为 0；没有启动真实数据集的大规模训练，没有恢复取消任务。最终专项集成样例执行 21 个有效小窗口、每窗两个客户端各一个本地步，共 42 个本地 SGD 步；legacy 前后复核另执行 4 个小窗口。测试迭代和其他回归样例的累计本地步没有逐项计量，不将其冒称正式训练预算。最终相关回归耗时 23.20 秒；整个修复/诊断会话墙钟耗时记录于 `BUDGET.json`，包括广泛测试、仓库哈希扫描和代码检查。

后续检测收益、任务性能不退步、预测收益须分别有对应的检测比较、预先规定的不退步检验和预测基线/区间证据。**本报告三者均不作收益结论。** 方法身份验收允许独立数学证明及不依赖旧缓存的实现工作继续被评估，但不自动续跑此前协议或更改其停止状态。

## 8. 测试逐项调整理由

以下每项保留原覆盖意图，归入 legacy 或改为当前规范/实际行为验证，没有单纯删除或跳过失败测试。详见 `TEST_MIGRATION.json`：

- `tests/unit/test_formal_policy_unique.py`：新版方法身份由design_control/configured版本核验，独立legacy注册保留；原别名及唯一paper断言保留。
- `tests/unit/test_legacy_raven_isolated.py`：新版方法身份由design_control/configured版本核验，独立legacy注册保留；原别名及唯一paper断言保留。
- `tests/unit/test_r1m_no_legacy_gate_bypass.py`：新版方法身份由design_control/configured版本核验，独立legacy注册保留；原别名及唯一paper断言保留。
- `tests/unit/test_raven_mcs_resolves_to_formal_policy.py`：新版方法身份由design_control/configured版本核验，独立legacy注册保留；原别名及唯一paper断言保留。
- `tests/unit/test_raven_mcs_not_legacy_static_gate.py`：新版方法身份由design_control/configured版本核验，独立legacy注册保留；原别名及唯一paper断言保留。
- `tests/unit/test_raven_mcs_resolves_to_aggregate_coverage.py`：新版方法身份由design_control/configured版本核验，独立legacy注册保留；原别名及唯一paper断言保留。
- `tests/unit/test_r1m_raven_mcs_formal_alias.py`：新版方法身份由design_control/configured版本核验，独立legacy注册保留；原别名及唯一paper断言保留。
- `tests/unit/test_certified_above_tau_design_on.py`：Gate强制Design、忽略静态配置及WARMUP/RESET关闭Design只属于legacy；断言保留并使用显式legacy函数/注册。
- `tests/unit/test_certified_below_tau_design_off.py`：Gate强制Design、忽略静态配置及WARMUP/RESET关闭Design只属于legacy；断言保留并使用显式legacy函数/注册。
- `tests/unit/test_current_mask_cannot_control_design.py`：Gate强制Design、忽略静态配置及WARMUP/RESET关闭Design只属于legacy；断言保留并使用显式legacy函数/注册。
- `tests/unit/test_dataset_name_cannot_control_design.py`：Gate强制Design、忽略静态配置及WARMUP/RESET关闭Design只属于legacy；断言保留并使用显式legacy函数/注册。
- `tests/unit/test_design_t_equals_gate_t.py`：Gate强制Design、忽略静态配置及WARMUP/RESET关闭Design只属于legacy；断言保留并使用显式legacy函数/注册。
- `tests/unit/test_formal_runner_no_static_gate_lookup.py`：Gate强制Design、忽略静态配置及WARMUP/RESET关闭Design只属于legacy；断言保留并使用显式legacy函数/注册。
- `tests/unit/test_gate_t_controls_design_t.py`：Gate强制Design、忽略静态配置及WARMUP/RESET关闭Design只属于legacy；断言保留并使用显式legacy函数/注册。
- `tests/unit/test_gate_t_is_unique_design_authority.py`：Gate强制Design、忽略静态配置及WARMUP/RESET关闭Design只属于legacy；断言保留并使用显式legacy函数/注册。
- `tests/unit/test_no_dataset_gate_override.py`：Gate强制Design、忽略静态配置及WARMUP/RESET关闭Design只属于legacy；断言保留并使用显式legacy函数/注册。
- `tests/unit/test_no_static_gate_override.py`：Gate强制Design、忽略静态配置及WARMUP/RESET关闭Design只属于legacy；断言保留并使用显式legacy函数/注册。
- `tests/unit/test_oracle_cannot_control_current_design.py`：Gate强制Design、忽略静态配置及WARMUP/RESET关闭Design只属于legacy；断言保留并使用显式legacy函数/注册。
- `tests/unit/test_r1l_v12_mock_gate_design_cases.py`：Gate强制Design、忽略静态配置及WARMUP/RESET关闭Design只属于legacy；断言保留并使用显式legacy函数/注册。
- `tests/unit/test_r1l_v13_mock_raven_mcs_cases.py`：Gate强制Design、忽略静态配置及WARMUP/RESET关闭Design只属于legacy；断言保留并使用显式legacy函数/注册。
- `tests/unit/test_reset_design_off.py`：Gate强制Design、忽略静态配置及WARMUP/RESET关闭Design只属于legacy；断言保留并使用显式legacy函数/注册。
- `tests/unit/test_source_snapshot_contains_window_runner.py`：保留历史快照存在性及旧formal_decide符号断言；历史文件不随新legacy符号重命名，不修改快照。
- `tests/unit/test_warmup_design_off.py`：Gate强制Design、忽略静态配置及WARMUP/RESET关闭Design只属于legacy；断言保留并使用显式legacy函数/注册。
- `tests/unit/test_window_close_receives_gate_t.py`：Gate强制Design、忽略静态配置及WARMUP/RESET关闭Design只属于legacy；断言保留并使用显式legacy函数/注册。
- `tests/unit/test_window_runner_calls_compute_certificates.py`：Gate强制Design、忽略静态配置及WARMUP/RESET关闭Design只属于legacy；断言保留并使用显式legacy函数/注册。
- `tests/unit/test_design_t_controls_window_close.py`：旧论文源码字符串断言与当前规范冲突，替换为冻结Design消费和独立Gate的行为断言；真实计算链另由集成测试覆盖。
- `tests/unit/test_window_close_receives_gate_t.py`：旧论文源码字符串断言与当前规范冲突，替换为冻结Design消费和独立Gate的行为断言；真实计算链另由集成测试覆盖。
- `tests/unit/test_no_oracle_current_gate_leakage.py`：保留特征无oracle检查，将Design=Gate源码字符串断言改为配置不受当前/隐藏结果影响的行为断言。
- `tests/unit/test_abstract_has_no_old_dataset_gate_claim.py`：保留禁止数据集硬编码的断言；移除要求论文随Gate关闭Design的旧规范断言，核验当前论文明确的预配置定义；论文原文未修改。
- `tests/unit/test_intro_has_no_old_dataset_gate_claim.py`：保留禁止数据集硬编码的断言；移除要求论文随Gate关闭Design的旧规范断言，核验当前论文明确的预配置定义；论文原文未修改。
- `tests/unit/test_conclusion_has_no_old_dataset_gate_claim.py`：保留禁止数据集硬编码的断言；移除要求论文随Gate关闭Design的旧规范断言，核验当前论文明确的预配置定义；论文原文未修改。
- `tests/unit/test_gate_uses_lcb_only.py`：以实际Gate阈值及诊断状态行为替换旧理论文件源码子串要求；阈值保持0.05。
- `tests/unit/test_e1_entry_r3_opportunity.py`：调整因预计算全部客户端比率而改变的赋值变量名；保留计算必须先于lagged estimator更新的顺序检查，并增加真实runner行为测试。
- `tests/unit/test_raven_mcs_formal_alias_same_policy.py`：旧aggregate gate_mode断言迁移为configured Design身份；保留别名与规范键完全相同policy断言。
- `tests/unit/test_c_cov_semantics.py`：原诊断测试没有event_count_cp所需的历史事件计数，NaN相等断言错误；补充真实格式历史计数并断言有限诊断，不改变阈值或诊断规则。
