# 本轮未采用的证据与待决事项

## 2026-10-18 六臂训练证据的范围澄清

已完成的City Scanner六臂训练现列正文Table III（VII-B），其floor/M1μ/M2μ相对FedAvg的三项注册结构H1均通过：每项10/10轨迹组失配更低、单侧原p=0.0009765625。原H2非劣未建立、H3未检验、另一四成员Holm家族不显著及ctrl/floor宽区间均保留。Δc-s明细在补充Table XXIX，统计细节仍在Appendix J-D。

这些是1164控制键上的实际训练变体，不能被固定checkpoint人口/311加载与尺度争议一并否定，也不据此追认该旧重评分。下文其他待决和历史记录不撤销；本轮只核对已有指标，没有训练、推理、重评分或新检验。

## 2026-10-17 City Scanner重组：本轮范围与仍待解决事项

City Scanner两套PM₂.₅排名已有来源核定，现为正文Table II；历史“仅附录展示”限制已由本次用户授权更新，不能再据此阻止正文使用。两块已有逐种子、均值/样本SD、配对相对差与现有包内CSV一致；后来的外生目标评分争议不撤销这两套原始排名。

六臂训练实验确已完成，采用EXECUTION_REPORT后续Part B而非早段“未开始”状态。C1_MAPS顶层`key_universe`文本仍提及M1/M2全3568键，但其实际`checks.key_counts`、`map_meta`、`arms`及注册修订和源码均为1164个控制键；3568是已拒绝的替代方案。本轮按实际1164键呈现，未修改原始JSON或历史报告。报告B.10个别句子写RMSE差，正式主定义及C1_PRIMARY.json明确为轨迹内模型种子均值的RMSE比减1；论文采用后者。

尚未解决的科学问题：主删除成本对比宽区间[−1.89%,+12.28%]不建立预测收益或等价，floor同时改变零质量与群体边际，不能当作纯删除干预；M1/M2与floor变体的2%预测非劣链均未通过；4成员次对比家族未显著。City Scanner未因此被证明超过训练均值、学习充分或端到端实测R/O/U。真实U仍未测量。

交付可访问性：两套5方法排名CSV已在现有包内；六臂原始小型结果仍为`results_gatekeeping/round_v1/`本地工作树资产，索引已明确local-only，没有虚称加入封存包或公开发布。正式投稿如需独立下载的全部六臂材料，仍需作者完成交付安排；本轮未上传、加载模型或启动新实验。

以下既有F1、漂移、外生目标评分及S1未闭合方法支持身份继续有效；本轮保留先前图表、假设及术语修复，没有将旧待决重新宣布全部解决。


## 2026-10-16压缩核验新增记录：结构图来源差异

`TO_OVERLEAF_paper_tmc_r1_clean/figure_data/FIG_E2_E3_STRUCTURAL_ALIGNMENT.csv`中U-Air FedAsync的组失配为1.1223±0.0416，而现有完整方法表相应行显示1.0451±0.0397。仅凭现成展示不能确认二者支持集、汇总对象或评分身份相同，原因未知。本轮未运行模型或重评分，也未将其中一值替换另一值。

因此撤销将结构图视为重复图的删减，保留补充Fig. 5及原完整表，保留原CSV和图资产。该图不能作为同支持重复验证。正文机制归因继续依据已核定的W1 Table IV，不依赖上述差异单元。此项需已有运行身份记录闭合后才能统一展示口径。

理论文字方面，VI的A3已在本轮澄清正确总体比率与理想未截断估计的关系；不再使用“截断未激活即正确识别”的措辞。此项是条件表达修复，不是新增实验或预测结论。以下F1、漂移和外生目标待决事项继续有效。


日期：2026-10-16。对应规范稿：`C:/Cursor/raven.mcs/TO_OVERLEAF_paper_tmc_r1_clean`。本文件属于内部证据记录，不进入学术正文；不授权追加实验、推理或重评分。

## F1预测端点：保留原始方向，暂不新增预测结论

生成器源码已核定：`src/raven_mcs/e3/real_runner/generator_r3_score.py` 中的z为机会层内time_index排序三分位，不是目标标签。其block intercept保持边际观测率。论文补充材料只纳入该机制和层内概率多样性，删去原文“label-correlated”及把U-Air负效应写成正收益的表述。

本轮读取两套F1目录、两个数据集、两方法、20种子的全部160份小型 `final_metrics.json`，没有加载checkpoint或重新预测。由原始导出计算 `100×(mean RMSE_est−mean RMSE_oracle_p)/mean RMSE_est`：

- SensorScope θO=0：7.9379888489 对7.9384078665，−0.0052786%。
- SensorScope θO=1：7.9809386092 对7.9726206420，+0.1042229%。
- U-Air θO=0：1.1911139246 对1.1909160655，+0.0166113%。
- U-Air θO=1：1.1880318220 对1.1910144554，**−0.2510567%**。若改为逐种子相对差的均值则为−0.2569922%，不能混用两个分母口径。

这些是历史导出值的复核，不是本轮重新验收的预测结果。`results_w1_ladder/round_v5_1/ERRATA_FOR_PAPER.md`说明：同一旧评分路径在U-Air终窗不活跃时可读取内存module而非保存θ；W1的18行已另行修正。F1原始window_metrics中：θO=0的raven与oracle-p均有30007/30016/30018终窗不活跃；θO=1两方法均有30018/30020终窗不活跃。θO=0的导出均值1.1911139也与旧评分值一致，而W1保存参数路径的RAVEN均值为1.1953656。

**未找到F1覆盖这些运行的权威θ重评分汇总，故不能借W1修正证明F1已修正。** 不删除这些种子、不拿其余种子另算有利子集、不借本次权限运行推理。为避免只保留SensorScope的有利值，整组F1 oracle预测比较暂不新增入稿；原负方向在本文件完整保留。后续若取得已有、可核验的全组参数评分，再决定是否采用。当前论文只陈述生成机制、信息边界与输入异质性，不据此声称预测收益。

来源：[F1原总结](C:/Cursor/raven.mcs/ccfa-review-reports/raven-mcs-f1-experiment-summary.md)、[原构造目录](C:/Cursor/raven.mcs/artifacts/e3_f1_score_dependent_r1/)、[异质构造目录](C:/Cursor/raven.mcs/artifacts/e3_f1_theta1_r1/)、[W1评分勘误](C:/Cursor/raven.mcs/results_w1_ladder/round_v5_1/ERRATA_FOR_PAPER.md)。

## A03漂移：200个终点存在，冻结方法身份尚不能闭合

已按固定2数据集×5方法×20种子路径，核对200份final_metrics与200份final.pt存在；只读小型配置及汇总，未加载模型。`run_ledger.json`现存rows只覆盖20个SensorScope/raven单元，不能把该局部账当作完整200条的身份证明。

trace_ledger记载生成器e3-complete-aligned-r3-v1、drift_period=50、drift_magnitude=.1。运行的config_snapshot有method=raven、local_steps=2、空间×时间target及指标schema，但没有显式Design配置、实际Design/Gate职责和可解析的执行源码版本。runtime_manifest也未给出可用于核定这些职责的源码闭包；当前入口脚本的source_identity使用e3_drifting_r1标签，不能代替历史执行源码。当前注册表明确将raven归入legacy always-on，与新raven_mcs的configured路径分开。**不能仅因名称相同就追认200条均为新配置路径，也不能仅因legacy名称就断言科学计算必然不同；目前缺的是可闭合的运行身份依据。**

既有汇总保留有利与不利结果：相对FedAU，四个数据集×结构端点中3个有利，U-Air组端点不利；U-Air RMSE/Tail也落后。有限Q/S不证明债务次线性。本轮未将这些数字作为当前版本新增漂移结论入稿，没有覆盖原结果。

来源：[运行账](C:/Cursor/raven.mcs/artifacts/e3_drifting_r1/run_ledger.json)、[轨迹账](C:/Cursor/raven.mcs/artifacts/e3_drifting_r1/trace_ledger.json)、[既有结论](C:/Cursor/raven.mcs/_paper_work/drifting_window_results/conclusion.txt)、[SensorScope配置例](C:/Cursor/raven.mcs/artifacts/e3_drifting_r1/runs/sensorscope/raven/seed30001/config_snapshot.json)、[对应运行清单](C:/Cursor/raven.mcs/artifacts/e3_drifting_r1/runs/sensorscope/raven/seed30001/runtime_manifest.json)。

## A02外生目标：未解决的加载/尺度争议不纳入新结论

提供的实验利用审计指出人口/311固定checkpoint重评分与后续endpoint-screen的加载/评分路径存在争议。本轮没有用模型推理处理该争议，也没有找到能直接闭合争议的已有证据链，因此不新增外生目标排名或预测数字。保留原稿关于不同target lookup对象的必要说明，不将固定预测重评分写成外生目标下重训练。

## 文字与现有结果仍不能补齐的创新缺口

- IPW、Hájek、凸校准、凸包及ESS已有最近邻。本轮核验FedIPW的总体摘要校准与FedPALS的目标匹配/ESS，并修正比较，不能据此宣称重大独立算法突破。
- 完整P2各项的独立必要性仍未建立。已有投影更快、SensorScope组端点更好的事实保留，κ=1000独立规则不记为标准RAVEN收益。
- 理想矩重建、固定状态稳定性与条件性债务界仍不等于异步学习预测保证或无条件长期对齐；没有新增定理。
- 200遍新协议验证未建立三数据集均有效、充分训练的联邦主实验。Traffic/SensorScope的集中式改善不归入RAVEN，U-Air未超过简单基线的事实保留。

OF/可达性/停止、NO₂历史分支、已撤回数据及未完成实验均未并入本文。实验继续保持暂停；本文件不是下一批实验方案或执行申请。

## 2026-10-17 repair-round update on the structural figure source difference (S1)

Status change, appended without deleting the 2026-10-16 entry above. The difference is now resolved into two
separate causes. (a) **Scoring:** the four affected arms' `RMSE_mu` in
`figure_data/FIG_E3_E3_PREDICTION_RISK.csv` was still pre-theta on seeds 30007/30016/30018; substituting the
certified theta values moves `FedAvg-Window` from `1.178988` to `1.192251`, identical to Local-Hajek's theta
mean and consistent with `results_w1_ladder/round_v5_1/ERRATA_FOR_PAPER.md` E-v51-4. The 12 cells were
corrected from existing certified CSVs and the figure was regenerated; no inference was run. (b) **Support
identity:** `scripts/audit_table2_uair_fedavg.py` records that the frozen U-Air FedAvg runs dropped
`pi_tar = 0` clients while FedAU/ObsUse/RAVEN-NoDesign kept them, and that `fedavg_window_current` is a
current-runner re-run keeping every delivered client (`results_table2_audit`). The two exhibits are therefore
different comparisons and are now labelled as such in Table XVIII and in both figure captions. **Still
open:** no saved record states which active set `fedasync_window`, `flamf_timealign_adapted` and `debt_cal`
used in their frozen runs, so the exhibits cannot be unified without a re-run, which this round was not
authorized to perform. The figure no longer carries the U-Air comparative conclusion.
