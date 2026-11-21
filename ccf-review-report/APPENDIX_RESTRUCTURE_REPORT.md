# 附录A—H结构重组报告

## 当前状态

已实际重组规范源码、建立A—H八个一级附录、修正引用层级并编译两份PDF。内容保留检查通过，交叉引用稳定；**本轮整体验收尚未通过：正文14页、补充15页，补充超限1页；另有一项掩蔽代价证据对应未闭合。** 未将这两项记为通过。

交付：[正文PDF](C:/Cursor/raven.mcs/TO_OVERLEAF_paper_tmc_r1_clean/main.pdf)、[补充PDF](C:/Cursor/raven.mcs/TO_OVERLEAF_paper_tmc_r1_clean/supplemental.pdf)、[完整源码差异](C:/Cursor/raven.mcs/ccf-review-report/APPENDIX_RESTRUCTURE_DIFF.md)。规范main.tex、appendix.tex、supplemental.tex已原位更新。实验继续暂停；没有训练、推理、重评分、求解或统计检验。

## 新目录及归属

- **A. Supplementary Model Definitions and Main Proofs**：旧A的目标测度、约束与理想因子分解、主要证明、债务和校准几何，对应正文III—VI。
- **B. Aggregate Coverage Diagnostic and Its Proofs**：旧A的覆盖lookup与旧B的诊断算法、成对障碍、样本量、稳定覆盖及false-safe/漂移证明。
- **C. Experimental Protocols and Baseline Specifications**：旧J-B/J-C两套City Scanner协议、旧F-A窗口基线公式、独立的信息机制比较表。
- **D. Additional Results for Deployment-Target Alignment**：旧F的完整站点结果与结构/预测图、四UTC块、NSW四区域；旧C三组风险语义控制；欠服务块；旧G间歇机会结果。
- **E. Mechanism Analysis and Numerical Calibration Details**：旧D局部归一化与层内异质；旧F-F支持变化；旧E数值可行性、投影加债务；旧F-E运行时间。
- **F. Target Support, Target Maps, and Reference Sensitivity**：旧L正式到达日志几何；旧J-D六臂目标图；旧J-A离线配置；旧H的稳定化、参考/预测与集中度敏感性，分别设六个子节。
- **G. Coverage-Controlled Variant under Availability Stress**：旧I经验压力结果，仍明确Design=Gate的辅助变体身份。数学诊断证明在B，不将二者混同。
- **H. Development Learning and Implementation Sensitivity**：旧K集中学习、正式协议预测参照与更新规则，以及旧M开发几何和释放时机，分别为五个子节。

补充开头新增紧凑导览，主题、附录号和页码均由ref/pageref生成，没有手写A—H页码。各一级附录只增加简短用途说明；没有建立空设置节或重复正文City Scanner主表。

## 关键迁移和引用修复

1. **拆开旧A-A。** `app:deferred_constructions`现在只承载兼容目标。覆盖lookup整体迁入B-A，`app:itar_lookup`随定义移动。A2均值条件、cap/ESS与理想权重分解归A-B，入口为`app:correction_constraints`及`app:ideal_factorization`。C1及其说明移至A-F的扰动证明旁，`app:perturbation_constants`为精确入口；原公式不变。
2. **主要证明标签随完整证明移动。** `app:proof_prop1`、`app:proof_prop2`、`app:proof_theorem1`、`app:proof_prop3`、`app:proof_prop4`、`app:proof_debt_bound`保持语义；restated、Proof、QED与推导原样保留。未使用的`app:proof_summary`改绑A的有效一级入口，避免挂在旧计数器上。
3. **B的次序。** 先lookup，再历史分位数/状态和算法2，再成对障碍及可用性推论、n_min、稳定覆盖、false-safe与漂移。障碍及可用性证明仍各有精确标签；算法不控制Design。
4. **C/D分离定义与结果。** `app:adapted_baselines`仅承载定义；`tab:nearest_neighbor`为C的独立机制/信息需求子节。`app:underserved_block`整段和原表归D-G，正式编号不再为F-A0a。
5. **RQ1结果归D。** `app:e3_full_context`、`app:block_rmse`、`app:traffic_four_region`、`app:e1_balanced`、`app:e2_full_stats`、`app:e2_layer_matrix`、`app:int_r`各自保留；没有用旧F的“全部Design on”作为新D总述。
6. **RQ2材料归E。** `app:local_hajek`、`app:f1_mechanism`、`app:design_provenance`、`app:p2_diagnostics`、`app:kappa_probe`和`app:runtime`均随原块迁移。数值诊断仍是实现可行性及差异，不改称最优性证明；没有把所有比较改称固定支持。
7. **RQ3材料归F。** 正式到达日志是`app:arrival_support`；六臂是`app:cityscanner_sixarm`；离线配置是F-C的`app:cityscanner_phi`；支持条件为`app:a5_a6_audit`；参考及集中度分别为F-E/F-F的`app:reference_sensitivity`、`app:target_concentration`，消除原H-0a/H-0b编号。
8. **H入口粒度。** `app:learning_capacity`只指H-A集中学习；`app:formal_prediction_references`、`app:update_rule_sensitivity`、`app:development_geometry`、`app:release_timing`分别指其独立子节。正文涉及更新规则的句子已另指更新规则入口。
9. 原`app:additional_context`是旧F混合内容的无人引用总标签，内容现分属C/D/E。已确认规范源码没有引用后退役该标签，避免把一个片段伪装成全部旧内容。其它原label均保留且无重复。

正文仅三处必要引用更改：理想因子分解→`app:ideal_factorization`；cap/ESS→`app:correction_constraints`；学习与更新预算→两个精确子节。Evaluation内容、标题、摘要、引言、贡献、方法、理论和结论没有实质改写。其它表图/证明引用沿语义label自动更新，没有按字母全局替换。

## 内容保留与编译核验

- 编辑前归档可读取，按当前工作树建立，没有恢复HEAD或覆盖用户此前修改。
- 合并main/appendix对照：所有表和图的内容块保留；改变的仅为表图位置及合法浮动参数。equation、align、multline、proof、restated、algorithmic、proposition和corollary逐块多重集相同，保证迁移和重排没有漏掉重复出现的对象。
- 原label除上列未使用混合总标签外均保留；无重复label、未定义引用/文献或缺字。书目不变，图资产和绘图源码未改。
- 主文计数仍为4图、7表、1算法、41编号公式及原理论计数；补充连续编号沿用实际主文终点。新章节与公式的位置变化通过自动编号反映。
- 使用既有MiKTeX单进程顺序构建，更新书目并交替编译至aux稳定。最终正文14页、补充15页；最终日志没有Overfull、LaTeX错误、未定义或重复引用。普通Underfull提示仍存在，不声称日志完全无警告。
- 查看补充所有重排页面的分页预览并放大检查入口、公式、表图与页边界。数值校准处增加一处FloatBarrier，避免前面跨主题浮动表与数值表叠放导致的纵向越界。没有每节换页、负间距、缩小字体/边距、图像压缩或拼接PDF。
- 写作检查用于标题与新导航：无em dash；等长句与分号提示主要涉及原证明/技术陈述，未据提示更改数学或统计符号。

可复核记录位于`C:/Cursor/raven.mcs/tmp/appendix_structure_20261104/`：baseline.json、checks.json、citation_build_status.json、prose_quality.json、三个源码差异和分页预览。checks.json的`page_budget_passed`为false。

## 尚未通过的两项

### 1. 补充篇幅

修改前14/14页，修改后14/15页。导览、精确子节入口和分组后的浮动体使补充增加1页。已压紧新增导览、合并相邻定义和重复用途说明，并尝试合法浮动位置；当前尚未满足“补充不超过实际正文”的要求。没有为压页删除证明、结果、条件、配置或越界压缩既有技术论述。仍需解决补充最后一页的释放时机末段与参考文献布局；本报告不标记整体验收通过。

### 2. 掩蔽代价的具体证据入口

正文main.tex第1702行附近原句仍为：

> In the retrospective comparison (Appendix~\ref{app:cityscanner_phi}), masking SensorScope keys gives at most $.175\%$ cost at zero-target share $.388$, whereas U-Air costs $6.6\%$--$7.5\%$ at shares $.354$--$.466$.

旧J-A及现F-C确实包含零目标查找对象、计数、离线配置和回顾性权衡公式，但**没有承载这组掩蔽结果的具体表、分母/比较配置或数值分析**。已检查当前源、相关旧备份的appendix.tex、C2_scd_phi资料、G1诊断、已有结果说明和相关修订报告；找到的是35.4%计数、25.5%EventTrace诊断等不同对象，不能当作该组掩蔽代价的证明。未从正文倒推实验或生成新的结果。

该原句和实质结论依授权保留；其引用现在技术上解析为F-C，但内容对应未闭合。缺少的是该组数字的可信原始结果/报告、mask定义、评分端点和成本比较分母。因而不能声称所有正文—附录对应均已通过。此缺口不影响其它独立内容已完成的结构迁移。

## 修改文件和回退

修改文件仅为规范目录的main.tex、appendix.tex、supplemental.tex及其编译产物，另新增本报告和差异记录。实验、配置、模型、CSV及历史停止报告未动。

备份位置见本轮baseline.json记录，并在下方给出直接链接。安全回退时先解压到独立目录；若之后没有新修改，可只恢复这三个TeX后重新编译。若有后续修改，以本轮差异反向合并附录块、标题、导览和三处正文引用，保留用户后续内容；不得整树reset或用旧main覆盖新稿。备份PDF仅代表回退时点。

[本轮修改前归档](C:/Cursor/raven.mcs/ccf-review-report/backups/appendix_structure_20261104_085238.zip)
