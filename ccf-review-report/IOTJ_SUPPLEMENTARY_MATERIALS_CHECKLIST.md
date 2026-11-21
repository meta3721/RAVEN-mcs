# IoTJ补充材料清单与工作区盘点

核验日期：2026-11-11。规范稿：`C:/Cursor/raven.mcs/TO_OVERLEAF_paper_tmc_r1_clean/`。

## 结论

**本次初投最小审稿补充文件是当前14页 supplemental.pdf，随14页 main.pdf 一起提交。**附录已包含证明、协议、附加结果及必要边界。更详细的CSV/代码可作为可选复现附件整理，但目前工作区没有一份可以不经清理、直接宣称完整对应现稿的复现ZIP。

本清单定位了117个材料条目：116个现存文件和1项拟新增README。存在性不等于科学数值全部复核或已获再分发许可；每行有核验深度和提交前处理。CSV为作者用核对单，不应把全部列出的内部材料直接上传。

## 盘点范围与执行边界

- 项目目录枚举127731个文件路径；桌面工作区枚举602个；另一个授权可视化根目录未检出文件。
- 枚举排除了.git、虚拟环境、node_modules、site-packages、__pycache__及聊天附件缓存；未逐个阅读128333个文件的内容。对规范论文、现有复现包、代表性归档、对应结果摘要及来源索引做定向核验。
- 不扫描项目外其他个人目录。只读检查和撰写清单；没有训练、推理、重评分、求解、新统计检验、上传或发布；没有修改论文与原始结果，也没有修复旧包后假称其原本有效。
- 机器清单包含源路径、存在性、字节数、论文锚点、状态和下一步。小于5MB的已选文件记录SHA-256，供本轮取材核对。

## 一、可以随稿提交的内容

1. **supplemental.pdf**：741156字节，14页。作为 `Supplementary Material for Review` 或门户对应的可供评审补充材料类别上传；不选Not for Review。
2. **main.pdf**：4459254字节，14页。它是配套Main Manuscript，不是另一个补充附件。当前AI内容披露及作者声明仍须按既有准备度报告落实。
3. **面向评审的简短README**：建议准备，当前没有针对本次IoTJ提交的完整说明。拟用文件名 `README.md`，说明补充PDF目录、指标、数据获取、可选证据文件的组织；这不是已被证明的IoTJ统一必交文件。

IEEE要求补充文件单独标记并随投稿上传：[补充材料说明](https://journals.ieeeauthorcenter.ieee.org/create-your-ieee-journal-article/prepare-supplementary-materials/)。具体文件类别、数量与大小限制，以门户当前页面为准，本轮没有登录检查。

### 当前补充PDF的实际内容

- **附录A，第1页起**：兼容目标、理想权重与校正约束；风险区分、目标重建、唯一性、参考扰动、分组分解及债务界证明。
- **附录B，第3页起**：覆盖诊断的目标与算法、两类可用性障碍、n-min推导、稳定区间保证及漂移边界。与主方法的配置机制分开阅读。
- **附录C，第5页起**：City Scanner两协议的构造及筛选、窗口基线适配、选择机制与信息要求比较。
- **附录D，第6页起**：完整站点上下文、分组RMSE、NSW四区域、平衡控制、六场景风险及欠服务/间歇机会结果。
- **附录E，第8页起**：局部权重抵消、层内异质性、Design支持变化、数值可行性、匹配支持置信区间和债务敏感性、耗时。
- **附录F，第10页起**：到达支持几何、City Scanner六臂目标图、离线配置、稳定化、参考与目标集中度敏感性。
- **附录G，第12页起**：历史Design=Gate覆盖控制变体的压力评价，不是正文预配置Design方法的收益证明。
- **附录H，第13页起**：集中式骨干开发学习曲线、简单预测参考、更新规则和开发约束几何。

补充图为5—8、补充表为VIII—XXXII。页码来自本轮当前supplemental.aux，不沿用旧报告编号。

## 二、值得组成可选结果证据包的内容

这些源文件已定位，但没有在本轮新建ZIP或宣称完整可重训。优先选择小型逐种子表、汇总、冻结配置和必要分析代码，不整包复制runs/日志/checkpoint。

### 优先级一：支撑现稿主表

- **表II：City Scanner双协议**。`results_c1_cityscanner/round_v1/tables/CS_E3*.csv` 与 `results_joint_ou/round_v1/tables/JO_E3*.csv`，配合各自INGEST_REPORT、TRACE_MANIFEST及TRAIN_SETUP。6份结果CSV与旧复现包的对应副本逐字节一致。尺度和真实/受控层必须保留。
- **表VII及附录F-B：六臂目标支持**。`results_gatekeeping/round_v1/` 下 C1_RUNS、C1_PER_SEED、C1_ARM_SUMMARY、C1_A1_CHAINS、C1_PRIMARY、C1_SECONDARY、C1_MAPS、C1_ANALYSIS_PROVENANCE 和PREREG。配对单位是10条轨迹，每轨迹3个模型种子；不能写成180个独立样本。旧提交索引明确标为local-only，原始完整材料尚不在旧包内。
- **表III：站点比较**。必须结合 `results_table2_audit/` 的当前FedAvg重评分和旧正式轨迹，而非照搬旧包汇总表。该目录中已定位三个对应CSV。SensorScope/NoDesign等仍应逐行按原索引拼合；本轮未声称已完成所有表III单元重建。
- **表IV：T-Drive**。使用 `results_tdrive_rank/round_v1/tables/TD_R_E3*.csv` 和 `TD_R_PHI.csv`；不要纳入micro_fixture、OOM/停止日志。
- **表V及RQ2：匹配支持规则**。`results_w1_ladder/round_v5_1/TRADEOFF_V51.csv` 是修正预测表；V4的FULL_SEED_LADDER、FULL_SEED_DECISIONS、TRADEOFF_PAIRED等保留结构/区间来源，v5_1a的A1P_IMPL_RERUN保留实现误差。版本用途要写明，不能用旧TRADEOFF替代修正预测。
- **表VI：组件消融**。旧包中的TABLE_E4_CORE_ABLATION、相对变化与Holm表可作取材来源；按当前Design开关、支持与评分身份核对后选入，不能仅凭文件名是FINAL即认定完全适配。

### 优先级二：解释主结果与理论边界

- 图2/3/4及补充图5/6/7的CSV：规范论文 `figure_data/` 中9个CSV；其中消融CSV并非当前单独插入的图，作为证据输入即可。
- 到达支持：`results_m1_attribution/round_v1/M1_SUMMARY.csv`、M1_WINDOWS与PREREG，对应附录F-A。
- 稳定化：`results_prop3_audit/round_v1/A5A6_EPS_STAB.json`、eps_stab_windows.csv，对应附录F-D/F-E。
- 集中度：`results_traffic_e2/round_v1/TE2_STEP4_VERDICT.json`、tables/TE2_MAIN和TE2_STEP4_MAIN，对应附录F-F。
- 间歇机会：`results_int_r/round_v2/tables/INT_R_*.csv`，不与always-on协议合并。
- 开发学习：`results_main_rebuild_r1/` 的P0_VALIDATION_BASELINES_R2、P1_CENTRAL_SELECTED_R2、P1_SELECTED_TRAIN_VALIDATION_CURVES_R2，以及P2_GEOMETRY_SUMMARY/CONFIG/AUDIT。其结果归集中式骨干及独立开发几何，不归完整RAVEN的端到端收益。

小型包建议采用 `results/cityscanner/`、`results/station/`、`results/matched_support/`、`results/support_maps/`、`configs/`、`scripts/` 和README。所有路径应改成包内相对路径；仅有本地文件的条目不得描述为已公开或已上传。

## 三、源码与复现附件的可用范围

### LaTeX源包

已定位 main.tex、supplemental.tex、appendix.tex、appendix-navigation.tex、reference.bib 和两份bbl。编译资源为8个实际插入的图PDF及4位作者肖像。源码在系统要求时提供；初投是否要求源码以门户为准。

不要整包上传规范目录中的revision_backups、ai_detection、_check.txt、main.txt、旧候选图、PNG预览及日志。源码包应采用必要文件白名单；图形PDF已有嵌入字体。

### 绘图代码

`fig1_framework_vector.py`、`data_figures_revision.py`、`make_figures.py`已定位。图1重绘依赖STIX字体；学习能力图依赖论文目录外的三个结果CSV。data_figures_revision.py默认运行范围包括未集成候选图，应使用--only，输出至候选目录后核验，不能用默认调用覆盖正式图。

### 训练代码和环境

已定位src/raven_mcs、City Scanner两个入口、正式E3/E4入口及pyproject/requirements-lock/environment/config。当前实现支持显式Design配置，但工作区也保留历史入口和配置；不能把整个src/scripts目录未经选择直接当作与所有已封存轨迹完全同版本的实现。

这部分尚需：依赖闭包、明确当前方法配置、英文运行说明、结果复核命令和授权许可。requirements-lock没有单独锁定matplotlib/reportlab，不能声称仅该文件就覆盖全部绘图环境。本轮没有安装环境或运行训练，因此不出具端到端可重训认证。

## 四、明确不宜原样提交的旧包

### RAVEN_MCS_PUBLIC_REPRO_R1

只读执行verify.py，检查2116个清单项，发现3项哈希不符：

- README.md：清单10699字节，实际0字节。
- BUNDLE_SUMMARY.json：清单811字节，实际0字节。
- scripts/rebuild_e3_scd_holm_fedau_obsuse.py：清单5785字节，实际2字节，仅换行。

另一个rebuild_table_ii.py也仅2字节换行；该项虽然符合旧清单大小，也无法完成重建。**哈希通过不等于脚本可执行或材料完整。**

除此之外：

- PROTOCOL.json仍将paper_method写为support-conditional Design，并以SCD决定U-Air OFF；现稿报告明确的固定Design-on/off比较，两者不能不说明就等同。
- 旧TABLE_II_MAIN_EFFECTIVENESS.csv的U-Air FedAvg RMSE为1.18824；当前正文表III为1.1119，更正来源已定位到results_table2_audit及submission_evidence。旧表仍可能适用于其原始评分身份，但不能作为当前表III直接提交。
- submission_evidence索引仍使用旧Table III六臂/Appendix J-D等定位；现稿是表VII与附录F-B。
- City Scanner双协议6个结果CSV已在旧包中，六臂主材料及开发学习材料仍有local-only缺口。
- w1/PAPER_NUMBERS.csv对3.44/1.32 pp仍标UNLOCATED；后来有报告级来源补入，但本轮未找到并核验对应原始重建行，不应升级为原始数据可复算。
- LICENSE.txt是通用研究验证和上游许可保留说明，不是一份已明确赋予训练代码开放许可的完整声明。不能据“PUBLIC”目录名声称已获得全部数据再分发权。

### deliverables中三个代表性旧归档

已查看FINAL_PAPER_DATA_CORE_R1（202个成员）、FINAL_PAPER_DATA_FULL_R1（5022个成员）、PAPER_DATA_CORE_R2（140个成员）的成员目录；均未检出City Scanner或C1_RUNS/C1_ARM命名文件。它们可以内部取材，但未证明覆盖现稿，不应原样当作现稿完整附件。其他历史压缩包只做文件名盘点，没有逐个解包认证。

## 五、不应作为评审附件整体上传的材料

- 内部审查、改稿diff、停止报告、聊天截图和“下一阶段指令”；不把评审工作流当作科学补充。
- 未进入当前论文的主动参与、跨窗口停止、缓冲消费、PurpleAir校准等探索目录。若其中某结果已明确在现稿使用，按具体锚点单独抽取，不能按正负结果筛选。
- .git、虚拟环境、临时安装包、依赖缓存、个人工具配置及所有历史备份。
- 原始第三方数据和大规模checkpoint：不是一概禁止，而是仅在权限、需要、门户限制确认后选取。尤其T-Drive不应默认由作者二次分发。
- 导师资料、作者原始肖像文件夹及无关个人文档。论文源包所需的4张肖像可以保留，不能据此把整个个人资料目录上传。

## 六、仍待完成的事项

1. 写入准确的AI内容披露并由作者确认最终稿；ORCID、署名同意、无并投/会议前身按事实处理。
2. 编写一份对应本稿的英文README和当前标签—文件—字段索引，避免旧表号。
3. 如选择提交可选证据包，补入六臂及开发结果，并将旧包中更正前评分、SCD、coverage-controlled变体明确分层；不要只重算MANIFEST掩盖空文件。
4. 若要提交源码复现包，修复2份空重建脚本、明确环境与许可；选择低成本结果复核命令后另行核验。本轮不启动任何训练。
5. 在投稿系统上传PDF并检查预览、审稿可见性、手工附录导航；不能保证跨PDF链接在系统改名后仍可跳转。

材料齐备度与论文科学录用概率是不同判断。本清单未改变研究结论，也没有以新实验填补历史缺失日志。

## 输出与证据

- 详细CSV：`C:/Cursor/raven.mcs/ccf-review-report/IOTJ_SUPPLEMENTARY_MATERIALS_CHECKLIST.csv`。
- 文件名盘点、旧包verify输出、字节核对及当前目录页码：`C:/Cursor/raven.mcs/tmp/submission_supplement_inventory/`。
- 现稿准备度报告：`C:/Cursor/raven.mcs/ccf-review-report/IOTJ_SUBMISSION_READINESS_20261111.md`。

本轮只产出清单与核查记录，没有创建实际上传ZIP、公开仓库或发送任何文件。
