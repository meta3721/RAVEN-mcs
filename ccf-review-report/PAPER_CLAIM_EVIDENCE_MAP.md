# 创新主张—原始证据—论文位置

## 2026-10-18 六臂目标支持训练结果提升正文（当前定位）

VII-B第9页新增目标支持变体三段分析；完整六行主表为Table III第10页，保留标签`tab:cityscanner_sixarm`。字段为ρ百分比、Δgroup、RMSEμ及WorstGroupRMSE，均值/SD取十条轨迹内三模型种子均值。原City Scanner两块Table II第9页全部不变；摘要、贡献、概述及结论的“最低平均组失配”明确限定为每块原五方法比较，25.8%/23.3%原计算口径不变。

- `results_gatekeeping/round_v1/C1_RUNS.csv`全部180行复核：6臂×10轨迹×3模型种子，来源字段150 NEW/30 FROZEN，独立配对单位为10条轨迹。对`C1_ARM_SUMMARY.csv`逐项核对先轨迹内平均、再跨十轨迹计算mean/SD，主表四位小数、ρ两位小数。floor的最低组失配及FedAvg最低两预测端点正确加粗，NoDesign完整保留。
- `C1_A1_CHAINS.csv`及`C1_ANALYSIS_PROVENANCE.json`：floor、M1μ、M2μ相对FedAvg各10/10轨迹组失配更低；H1_p=0.0009765625、H1_reject=True。正文明确三个注册结构检验通过，p是单侧配对Wilcoxon原p值，不是Holm调整值。三链图式分配见PREREG有效修订和Appendix J-D。
- 同三链H2_reject=False，95%单侧上界3.83%/4.14%/8.15%未满足2%非劣；H3未检验。`C1_SECONDARY.csv`另一四成员Holm家族均未显著，与结构H1分开陈述。
- `C1_PRIMARY.json`的ctrl/floor−1仍为轨迹内三模型种子RMSE先平均再作比值；HL−0.019%、既存percentile trace-cluster区间[−1.89%,+12.28%]、p=.922及101.9%组增益保留率不变。floor同时改变群体边际，不写纯删除因果或预测无损。
- `C1_MAPS.json`有效字段、PREREG修订及EXECUTION_REPORT后续Part B确认1164控制键、812零键；M1μ/M2μ同键集且按区匹配μ。未采用顶层旧3568文字。它们是实际训练的目标形状变体，不与待决固定checkpoint外生目标重评分合并。
- 原附录六列结果表拆分：正文Table III提供可共同比较的端点，补充Table XXIX第13页仅保留全部Δc-s均值/SD，各臂自身目标不同，不加粗或横向排名。Appendix J-D第12—13页保留地图、主对比、H1→H2→H3及另一家族细节。

正文表号：I数据、II原双协议、III六臂、IV T-Drive、V站点、VI同支持、VII消融、VIII集中度、IX自然几何；补充X—XXXI。图号、公式和算法均未改，无需迁移Design图。两PDF仍14/14页。材料索引保留六臂local-only身份，未上传。见`CITYSCANNER_SIX_ARM_MAIN_TEXT_REPORT.md`及定向差异；下文历史定位保留。

## 2026-10-18 正文定义范围对齐（不改变证据结论）

当前规范稿保持完整RAVEN的City Scanner组优势及原数值。VII-A第8页现按协议区分WorstGroupRMSE的UTC块/空间群体、Tail RMSE范围和评分尺度，并分别列出20/10/5种子及六臂10轨迹×3模型种子的层级。Table I角色区分受控机制与应用，`City Scanner Pilot 2`显示名不再与优化程序(P2)混淆。

IV的β为估计且稳定化的参考，α为可执行权重；局部位移归一化仅去除显式学习率/步数尺度。图1和T-Drive表注明确NoDesign只省略机会—目标比率，其他校正与校准保留。V-E（第6页）为辅助机会覆盖诊断，VI-F（第7页）保留稳定区间条件界；VII-G覆盖结果现位于第13页，.959/.750明确属于另行评价的Design=Gate候选，不是当前预配置Design方法的新验证。

正文核心表号与位置保持：City Scanner II第9页，T-Drive III/站点IV第10页，规则V/消融VI第11页，集中度VII/几何VIII第12页。附录F第7页的固定Design说明同步；开发学习Table XXIX自然浮动至补充第13页。两PDF仍14/14页，公式、假设、证明、算法、结果表体与评分修复不变。详细A—I核验及差异见`PAPER_BODY_CLAIM_ALIGNMENT_REPORT.md`和`PAPER_BODY_CLAIM_ALIGNMENT_DIFF.md`。以下历史索引保留，位置冲突以本段和当前标签为准。

## 2026-10-18 核心应用优势主张更新（当前定位）

摘要（第1页）、引言贡献/概述（第1—2页）、VII-B/Table II（第9页）和结论（第13页）以完整RAVEN的City Scanner最低平均组失配贯通。两块各五个已报告方法、十种子；不是两个独立城市或全实测R/O/U。

- 新强调的25.8%/23.3%：分别从`results_c1_cityscanner/round_v1/tables/CS_E3.csv`和`results_joint_ou/round_v1/tables/JO_E3.csv`，按`method`汇总全部种子的`Delta_group`。RAVEN/TwoStage-Hájek均值依次为0.07064401934314223/0.0952010655099507及0.046539837752587646/0.060700754903925284。两块TwoStage均为最佳组对照；`100*(1-mean_RAVEN/mean_TwoStage)`=25.7949278564%/23.3290626678%。这是描述性均值之比；不赋予新显著性、不与配对预测相对差混用。
- City Scanner预测仍使用各自`*_E3_PAIRED.csv`已保存的`RMSE_mu_paired_rel_mean`等字段：访问占用FedAvg预测领先，RAVEN对其+5.59%；Pilot 2为TwoStage-Hájek领先，RAVEN对FedAU/ObsUse/FedAvg为−0.43%/−0.45%/−0.65%，前两者未达到原−0.5%条件。
- VII-E/Table V（第10—11页）：`results_w1_ladder/round_v4/FULL_SEED_DECISIONS.csv`与`FULL_SEED_LADDER.csv`核对直接参考→投影1.188/1.399 pp、投影相对Uniform0.768/0.286 pp及SensorScope独立投影Design对照0.922 pp，沿用原区间、支持集与比较身份。训练预测/时间采用`round_v5_1/TRADEOFF_V51.csv`，与离线直接参考读出分开；不归并为完整P2的增量。
- VII-E（第11—12页）、Appendix J-D（第13页）：`results_gatekeeping/round_v1/C1_PRIMARY.json`、`C1_ARM_SUMMARY.csv`核对101.9%仅为特定floor变体的组改善保留率；既存预测主区间与floor改变群体边际的含义不变。
- VII-F（第12页）：`results_main_rebuild_r1/P2_GEOMETRY_WINDOWS.csv`的183个Traffic固定K=8子集，最小`composition_rank=7`、平均`adjustable_target_mass=0.046511627906976744`，分别支撑“均有组成方向”和“仅4.651%目标质量可调整”。不与旧主实验窗口合并。

正文/补充均14页。II—VI、附录、公式、算法、全部表图及书目未改；当前未闭合证据状态不变。完整计算口径、保留取舍及验收见`PAPER_CORE_ADVANTAGE_REVISION_REPORT.md`，定向差异见`PAPER_CORE_ADVANTAGE_REVISION_DIFF.md`。下文历史定位保留，不覆盖原报告。

叙述压缩定位更新（2026-10-17）：表号、字段及原始证据对应不变。City Scanner仍为第9页Table II；VII-E现位于第10—11页，六臂主比值与区间在第11页；VII-F位于第11—12页，承接验证评分与支持审计；VII-G及覆盖0.750在第12页。其余科学状态不变。改动及词数见`PAPER_NARRATIVE_COMPRESSION_REPORT.md`，以下历史定位据此读取。


## 2026-10-17 City Scanner重组后的当前定位（优先于下文历史表号）

本次以中断后重新读取、与本轮快照逐文件一致的当前工作树为起点，保留既有S1—S4修复。只整理已有结果，实验保持暂停。正文与补充均为14页。

- City Scanner是正文主要实证之一：VII-B、Table II，第9页。两个独立面板各5方法、10配对种子：访问占用R且受控O/U；Pilot 2为union-GPS R、实测PM观测O及受控U。客户端为500m×30min占用网格。RMSE采用各块训练集z-score，不是物理PM浓度或跨块统一尺度。
- Table II(a)来源：`results_c1_cityscanner/round_v1/tables/CS_E3.csv`、`CS_E3_SUMMARY.csv`、`CS_E3_PAIRED.csv`。原始逐种子字段`RMSE_mu/WorstGroupRMSE/Delta_group/Delta_c_s`，均值及样本SD保留4位小数。RAVEN组失配0.0706最小；FedAvg预测0.2379/0.2489最小。配对相对RMSE对FedAU/ObsUse为−1.71%/−1.34%，对FedAvg为+5.59%，不是显示均值的比值。
- Table II(b)来源：`results_joint_ou/round_v1/tables/JO_E3.csv`、`JO_E3_SUMMARY.csv`、`JO_E3_PAIRED.csv`，同字段与打印口径。TwoStage-Hájek预测0.7097/0.7273及client–stratum失配0.3893最小；RAVEN组失配0.0465最小。RAVEN对FedAU/ObsUse/FedAvg配对RMSE为−0.43%/−0.45%/−0.65%。对前两者的原−0.5%门槛未通过。NO₂只提供GPS，不是NO₂预测。两块变化不是只改变O的因果效应。
- 六臂训练变体：正文VII-E（第11—12页）、补充Appendix J-D和Table XXVIII（第13页）。来源`results_gatekeeping/round_v1/C1_RUNS.csv`、`C1_ARM_SUMMARY.csv`、`C1_PRIMARY.json`、`C1_SECONDARY.csv`、`C1_MAPS.json`及`PREREG.md`修订与`EXECUTION_REPORT.md` Part B。六臂×10轨迹×3模型种子=180单元，其中150新增、30复用；SD在10条轨迹均值之间计算。
- 六臂机制范围：floor在1164键上替换812个零键并归一，改变群体边际；M1mu/M2mu在相同键集上按区匹配μ，剩余70/33零键。不能将floor改称原方法或删除单因素；不能将M1/M2训练等同于有争议的固定预测重评分。共用群体目标及预测评分；Δc-s相对各臂目标，不是共同目标横向排名。
- 六臂主对比：先轨迹内平均三模型种子RMSE，再作`ctrl/floor−1`；保存的HL=−0.000192186241、95% percentile trace-cluster CI=[−0.018930121494,+0.122753847247]、Wilcoxon p=0.921875。正文显示−0.019%、[−1.89%,+12.28%]及.922。保留率1.019406194为FedAvg→ctrl组对齐改善的保留率，不是预测收益。全部10轨迹为主分析；去32005只属原敏感性。未重新抽样或计算显著性。
- 受控站点角色：VII-D、Table IV，第10页保留全部Design两臂；VII-E、Table V，第11页保留Count/Uniform/投影/投影加债务/Inst-Cal/完整RAVEN的结构、预测和时间；Table VI完整消融。旧主模型与训练均值差距仍在VII-A。0.768 pp和0.922 pp的独立比较、Use不显著、默认Debt微小及U-Air代价继续可见。
- 其他最终表号：I数据，III T-Drive，VII集中度，VIII开发几何；补充IX—XXX。原City Scanner两张附表合成Table II，原标签保留为新表兼容别名。Appendix J-B/C保留过滤、划分与复现定义，J-A承载离线配置及回顾性图；原正文两式移至补充(71)/(72)，标签保持。正文核心(1)—(41)、II—VI文字和已有证明未改。
- 材料入口：`RAVEN_MCS_PUBLIC_REPRO_R1/submission_evidence/SUBMISSION_EVIDENCE_INDEX.md`已更新当前表号。`cityscanner/`和`cityscanner_p2/`已有封装CSV与本地原始结果逐行一致；六臂材料明确为working-tree local-only，未宣称上传或公开。


## 2026-10-16剩余章节压缩后的最终位置索引

以下为本轮已编译的14页正文、14页补充材料的定位。下文保留此前整合时的历史定位；若表号或分节位置不同，以本段及当前标签为准。原始文件名称不随论文编号改变。

- 目标、到达分布与可行组成的区分：摘要、I、III—V；理想矩重建及固定窗口性质在VI、补充Appendix A。I—V与本轮开始时逐字一致。
- 原主实验：Table III；T-Drive外部协议：Table II；数据定义：Table I。VII-B说明风险语义及外部协议，VII-C说明Design对照和主结果。不能将旧端到端支持变化等同于W1同支持机制。
- C02/W1实际训练规则：VII-D、Table IV（`tab:trained_rules`）；直接参考结构读出紧邻该表，不补造预测或时间；组件消融为Table V。0.768 pp是投影对Uniform，0.922 pp是独立同支持Design-on/off，不相加。完整P2、投影、Inst-Cal、κ=1000投影加债务身份分别保留。原始来源与字段继续使用下文C02记录。
- A01集中度：VII-E、Table VI（`tab:target_concentration`），沿用TE2原始判定及原检验，不把所评估oracle称为全类上界。
- A05开发几何：VII-E、Table VII及补充Table XXX。旧主实验退化比例另行陈述，不与开发轨迹合并；有组成自由度不等于预测改善。
- A06六场景、C01/F1机制及Local-Hájek退化：VII-B/E及补充原矩阵/机制表。F1仍不新增预测收益。
- A04骨干学习能力：VII-E末及补充学习能力表、Fig. 8；属于独立开发验证，非RAVEN收益。
- 服务器更新规则和覆盖范围：VII-F；补充覆盖表及Fig. 7。候选Gate审计保持旧coverage-controlled身份，U-Air失效单元可见。
- 补充保留Table VIII—XXX共23表；结构Fig. 5、预测Fig. 6、覆盖Fig. 7、学习Fig. 8。两幅重复消融图删除展示，源资产保留；结构图未被删除，其来源差异见待决记录。
- VI的A3表述已澄清：理想估计使用正确总体比率且无截断；截断未激活本身不建立正确识别。A6a只是稳定化误差为零的充分条件，不是必要条件。未新增预测保证。
- 理论证明压缩不改变正文43个编号数学表达；跨PDF引用改用有效标签，完整证明仍在补充Appendix A/B。


日期：2026-10-16。本记录先于本轮论文编辑建立，随原始证据核验与编译补全。规范源目录：`C:/Cursor/raven.mcs/TO_OVERLEAF_paper_tmc_r1_clean`。仅使用既有结果，不运行训练、推理、重放或求解。

## 主张与使用范围

- 问题与对象：部署目标、R/O/U选择后的到达分布和有限窗口可实现组成是不同对象。正文摘要、引言、系统模型及方法衔接；原有公式与定理编号保持。
- C02/W1：同支持计数、Uniform、参考投影、Inst-Cal、完整RAVEN及独立κ=1000投影加债务规则。原始训练记录 `results_w1_ladder/round_v4/TRADEOFF.csv`；预测采用修正的 `round_v5_1/TRADEOFF_V51.csv`；结构与数值误差以 `round_v5_1a/` 后续核验为准。正文联合表；U-Air匹配支持计数对照独立于原主表。直接参考只有离线结构证据时不补造其预测或训练代价。
- W1 Design：`round_v4/PART_A_REPORT.md`及相应逐种子表。0.922 pp是投影参考Design-on对no-Design的同活跃集比较；0.768 pp是投影对Uniform，不能顺序相加。摘要/引言/结论统一标明。
- A01：`results_traffic_e2/round_v1/TE2_STEP4_VERDICT.json`、`tables/TE2_MAIN.csv`、`tables/TE2_STEP4_MAIN.csv`及原配置。正文集中度小表；κ是目标质量倍率；oracle是所评估真概率配置，不是全类最优上界。
- A06：`artifacts/e2_traffic_formal_runs_r1/formal_results.csv`与最终数值容忍修订的 `paper_tables/TABLE_E2_2_FINAL.csv`。正文解释选择层；补充材料完整六场景风险响应，沿用已有检验，不新增显著性筛选。
- C01/F1：两目录的 `f1_run_status.jsonl`与逐run `final_metrics.json`、生成器 `generator_r3_score.py`。原计划核对层内异质选择及真p单因素替换；实际核验后，仅将机制与概率多样性写入补充材料并由正文引用。全组带符号预测效应因评分身份未闭合留在独立待决记录，不新增为论文结论。
- A05：`results_main_rebuild_r1/P2_GEOMETRY_SUMMARY.csv`、`P2_GEOMETRY_AUDIT.json`与诊断源码。正文/补充材料区分K、权重自由度、组成方向、可调整目标质量；为新开发轨迹的无标签几何，不替换旧窗口比例或宣称性能。
- A04：`P1_CENTRAL_SELECTED_R2.csv`、`P0_VALIDATION_BASELINES_R2.csv`与 `P1_SELECTED_TRAIN_VALIDATION_CURVES_R2.csv`。补充材料验证集学习能力表/曲线；47.01%与10.16%归Central-delivered骨干，不归RAVEN。
- A03：先检查200条漂移运行的源码/Design/划分/指标身份；无法解决的身份冲突仅阻止该项新增结论，独立记录，不阻断其余修订。
- 最近邻：公开FedIPW与FedPALS原文核验；相关工作及附录机制表涵盖选择单位、信息、目标、校准/ESS、状态与保证。已有BibTeX按原文核实，不从记忆新增书目信息。

## 不纳入核心证据

OF/可达性/停止分支、NO₂分支、撤回或未完成结果均不纳入。人口/311重评分若权威加载和尺度争议未被已有证据解决，暂不新增结论。几何与200遍验证不混入旧测试性能排名。

## 修改保护

当前四个源文件已有大量未提交改动，作为本轮起点保留，不回退至HEAD。临时编辑前文本仅位于 `tmp/paper_evidence_revision/before/`；最终本轮差异单独保存为MD中的统一差异，避免把用户原有改动算成本轮新增。不创建另一套final论文，不修改算法、协议、冻结参数和旧停止状态。

## 完成后的字段、分母与位置

### 摘要、引言与结论的两组结构数字

- 0.768 pp：`results_w1_ladder/round_v4/FULL_SEED_DECISIONS.csv`，ds=sensorscope、contrast=`B1:raven - B1:uniform`，字段pp_all20=0.7675383247515095，区间pp_all20_ci=[0.5629155207,0.9700230086]。这是固定支持结构读出；实际训练规则的相应均值差在打印精度上相同，不能借此将两套数值精度/区间混为同一记录。
- 0.922 pp：同文件ds=sensorscope、contrast=`B1:raven - B1:raven_wo_design`的pp_all20及区间；对应 `FULL_SEED_LADDER.csv` 的d_group：projected Design-on=1.0115773653447282、projected no-Design=1.0300230300411375。公式为50×(no-Design−Design)，不是在0.768上继续叠加。
- pp统一为50×Δ；相对百分比、Δ绝对差和closable-gap归一化单位分别保留。
- 位置：main.tex摘要、Introduction第三条贡献、Section VII-C与Conclusion。原端到端Design on/off仍在Table IV；新表中的W1同支持Design比较不替代它。

### C02：正文Table V，标签tab:trained_rules

- 原始训练：`results_w1_ladder/round_v4/TRADEOFF.csv`。权威修正预测：[`TRADEOFF_V51.csv`](C:/Cursor/raven.mcs/results_w1_ladder/round_v5_1/TRADEOFF_V51.csv)。按ds、arm分组，各20行，取算术均值；字段Delta_group、Delta_c_s、RMSE_mu、WorstGroupRMSE、runtime_seconds；正文打印结构/预测5位小数，墙钟1位小数。12行逐项核对通过。
- 六规则：fedavg_window（在本比较支持上按计数）、uniform_window、proj_beta、proj_beta_debt、inst_cal、raven。新三规则实现与目标在[`w1_v4_train.py`](C:/Cursor/raven.mcs/scripts/w1_v4_train.py)，ALPHA_MAX=.5、E_MIN=3、ETA=.01；proj_beta_debt的κ=1000单列，绝不记为完整RAVEN。
- U-Air匹配支持计数行RMSE=1.1922509224，不是旧主表不受该支持限制的FedAvg=1.1119；新表与旧主表分开。完整RAVEN的U-Air修正RMSE=1.1953655741。
- 校正参考直接读出：[`FULL_SEED_LADDER.csv`](C:/Cursor/raven.mcs/results_w1_ladder/round_v4/FULL_SEED_LADDER.csv)，block=all20、rule=B0:raven，d_group为SensorScope 1.0353336565、U-Air 1.1196064720。它是离线固定支持结构记录，没有新增直接参考的预测或训练耗时，故以紧邻段落列示而不拼成训练性能行。
- 训练预测检验：SensorScope采用原[`TRADEOFF_PAIRED.csv`](C:/Cursor/raven.mcs/results_w1_ladder/round_v4/TRADEOFF_PAIRED.csv)；U-Air采用[`A3P_RESOURCE_UPAIR.csv`](C:/Cursor/raven.mcs/results_w1_ladder/round_v5_1/A3P_RESOURCE_UPAIR.csv)字段p_holm_v51，最小.1197528839，正文舍入.120；不再沿用旧.133。没有重选检验或重新bootstrap。
- 数值精度：[`A1P_IMPL_RERUN.csv`](C:/Cursor/raven.mcs/results_w1_ladder/round_v5_1a/A1P_IMPL_RERUN.csv)的eps_impl_group/eps_impl_cs最大2.42e−5，单位为Δ。保留比较器最优性检查未全通过的事实；不恢复“exact oracle”认证主张。补充材料将εimpl明确为结构端点差，而不是服务器权重距离。
- 方法身份：W1明确复制旧raven静态always-on科学配置，仅换服务器权重，且有已有闭环/支持检查和后续评分修正；这里沿用这套固定on比较，不把它改记为2026-10-12之后configured-design-v1实现的新结果。新实现性能未因本次写作获得重新验证。

### A01：正文Table VI，标签tab:target_concentration

- [`TE2_STEP4_VERDICT.json`](C:/Cursor/raven.mcs/results_traffic_e2/round_v1/TE2_STEP4_VERDICT.json)的ceiling_ladder四行：mean_gap、boot_lo/hi、MDE80、control_mean、pct_of_control。最后一列=100×mean_gap/control_mean；不是逐种子相对差均值。未新增任何检验。
- 相对改善依次0.0013343795%、0.0224665957%、0.0453986256%、0.0970086052%；区间是原标准化RMSE绝对差，不是百分比或pp。
- 原逐种子表：[`TE2_MAIN.csv`](C:/Cursor/raven.mcs/results_traffic_e2/round_v1/tables/TE2_MAIN.csv)及[`TE2_STEP4_MAIN.csv`](C:/Cursor/raven.mcs/results_traffic_e2/round_v1/tables/TE2_STEP4_MAIN.csv)。κ=1复用；κ=5来自4臂×20种子；κ=10和single-region来自2臂×2条件×20种子。没有把复用算新训练。
- 配置：[`TE2_FROZEN_PREREG.json`](C:/Cursor/raven.mcs/results_traffic_e2/round_v1/TE2_FROZEN_PREREG.json)，原服务器步、local_steps=2、172个station×time组；priority region1。κtar对该区域原质量乘倍后重归一；区域质量.255814、.632184、.774648、1。oracle为raven_simoracle，替换生成器p及MC q，并保留校准路径；不是对所有可行权重优化的严格上界。

### A06：正文VII-B，补充Table X，标签tab:e2_layer_matrix

- [`TABLE_E2_2_FINAL.csv`](C:/Cursor/raven.mcs/artifacts/e2_traffic_numerical_tolerance_and_final_claim_seal_r1/paper_tables/TABLE_E2_2_FINAL.csv)：对每scenario和metric=RMSE_mu/RMSE_rho，读取五方法mean_diff的min/max及significant_holm_0.05计数。范围乘1000后打印3位，caption标明×10−3。零控制行是与自身之差，不补造balanced检验。
- 五非平衡场景target显著方法数0/0/0/2/0；arrival为0/5/0/5/0，顺序为R-only、O-only、U-only、complete-aligned、complete-counteracting。
- 原始600行[`formal_results.csv`](C:/Cursor/raven.mcs/artifacts/e2_traffic_formal_runs_r1/formal_results.csv)，采用最终容忍修订的既有检验，保持原Holm家族。signed Gap_mis不作绝对失配。

### C01：正文VII-F，补充Table XII，标签tab:f1_mechanism

- 原生成器、generation_meta与[`F1总结`](C:/Cursor/raven.mcs/ccfa-review-reports/raven-mcs-f1-experiment-summary.md)的既有机制核验：θO=0/1保持block观测边际，层内不同p数均值1→2.76/2.83。
- 新稿把time-index tercile与观测前信息界限写清，不称一般MNAR纠偏。只对满足“观察集合含不同时间三分位”的记录集合解释非恒定逆权重，未由概率多样性冒充预测收益。
- 全组预测数字因U-Air原评分路径冲突暂缓，原始正负方向与具体运行在[`待决记录`](C:/Cursor/raven.mcs/ccf-review-report/PAPER_EVIDENCE_PENDING_ITEMS.md)完整保留，不能以正文未纳入误称没有负结果。

### A05：正文Table VII与补充Table XXX

- [`P2_GEOMETRY_SUMMARY.csv`](C:/Cursor/raven.mcs/results_main_rebuild_r1/P2_GEOMETRY_SUMMARY.csv)，natural_original三行的windows、K_min/K_max、singleton_share×100、mean_adjustable_mass×100。0.433%等是目标概率质量百分比，不是Δ的pp换算。
- fixedK8_ESS0.5_cap2K：183窗口、mean_adjustable_mass=.0465116279、beta_violation_share=.5901639344、mean_projection_distance=.0674868983。其余四条件用相同行对应字段；没有新增求解。
- [`diagnose_geometry.py`](C:/Cursor/raven.mcs/results_main_rebuild_r1/diagnose_geometry.py)定义composition_rank=rank(M−column mean)，Wg为可行组质量最大−最小；adjustable mass为正目标组且Wg≥.01的μ之和。geometry不是预测指标。
- [`P2_GEOMETRY_AUDIT.json`](C:/Cursor/raven.mcs/results_main_rebuild_r1/P2_GEOMETRY_AUDIT.json)：已有投影848次核验，最大可行残差4.44e−16；本次不重复求解。新开发轨迹仍含旧coverage-controlled接线，因此不刊其gate_on_share、不把参考违反比例当作新configured方法表现，也不替换旧主协议78.6%/90.2%/79.0%。

### A04：补充Table XXIX与Fig.10，标签app:learning_capacity

- [`P1_CENTRAL_SELECTED_R2.csv`](C:/Cursor/raven.mcs/results_main_rebuild_r1/P1_CENTRAL_SELECTED_R2.csv)：ndmf三行mean_RMSE、sd_RMSE、baseline_RMSE、mean_relative_gain×100；均为验证集物理单位。Traffic 202.0554/+47.01%，SensorScope 2.6675/+10.16%，U-Air 20.5015/−0.96%。三行逐项核对通过。
- [`P0_VALIDATION_BASELINES_R2.csv`](C:/Cursor/raven.mcs/results_main_rebuild_r1/P0_VALIDATION_BASELINES_R2.csv)：按dataset/seed、applicable=True筛选，最小RMSE_mu分别来自Traffic weekly seasonal naive、SensorScope train_mean、U-Air spatial_mean；平均基线381.6185/2.9687/20.3060。三开发种子41001–41003，非旧测试种子。
- 曲线数据[`P1_SELECTED_TRAIN_VALIDATION_CURVES_R2.csv`](C:/Cursor/raven.mcs/results_main_rebuild_r1/P1_SELECTED_TRAIN_VALIDATION_CURVES_R2.csv)的pass_id/train_RMSE_physical/validation_RMSE_mu；复用原[`R2图`](C:/Cursor/raven.mcs/results_main_rebuild_r1/P1_TRAIN_VALIDATION_CURVES_R2.png)，保存到规范稿figures/fig_learning_capacity_r2.png，未运行模型或重新绘制轨迹。
- 优化器/预算来自train_central.py及逐run config：200遍、batch64、6配置、调度50/100/150乘.3。真实训练、验证曲线与R2评分已有[`EXECUTION_QA.json`](C:/Cursor/raven.mcs/results_main_rebuild_r1/EXECUTION_QA.json)核验，本次只读其结果。
- HistoryResidual的7.33%、−.34%、−4.45%取相同R2汇总。U-Air Central-all 19.5427对18.4567、单条Traffic Uniform 253.1132/+33.70%与100→200的.914%来自[`EXECUTION_REPORT.md`](C:/Cursor/raven.mcs/results_main_rebuild_r1/EXECUTION_REPORT.md)及其R2汇总，不作聚合方法排名。

### 相关工作与表述范围

- [FedIPW原文](https://arxiv.org/html/2604.26604v1)：Sections 3–6核定client enrollment/participation、population-summary calibration与条件性优化分析。现有key morishita2026who保留并增加公开URL。
- [FedPALS原文](https://arxiv.org/html/2411.03799v2)：Section 3、式8/9核定composition-space目标匹配与Σα²/n的软ESS惩罚；Proposition 1限label shift与target coverage下单步更新。现有key listozec2024overcoming保留，标题修正为with，补URL和v2日期，撤去未核定的TMLR状态注记。
- 正文Related Work及补充Table XV不再把FedIPW写成“没有总体校准”，也不把FedPALS与client-weight-space参考投影写成同一操作。
- 理论公式/编号及数学环境顺序保持。修正A6a解释为稳定误差消失的充分条件，避免把比例共同缩放后参考仍相等的情形错误排除；未新增定理或改算法。

本记录仅说明证据及其入稿范围。未采用项与不能靠写作补齐的创新缺口见独立待决记录；编译、页面与语言检查见修改报告。
