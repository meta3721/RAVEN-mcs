# FIGURE_TABLE_CAPTION_CONCISION_REPORT

日期：2026-10-30。按用户指定 raven-mcs-concise-figure-table-captions-instructions.md 完成 ccf-paper-writer compress 与 ccf-humanization 检查。实验保持暂停。

## 交付与总体结果

- 已原位修改 [main.tex](<C:/Cursor/raven.mcs/TO_OVERLEAF_paper_tmc_r1_clean/main.tex>) 和 [appendix.tex](<C:/Cursor/raven.mcs/TO_OVERLEAF_paper_tmc_r1_clean/appendix.tex>)；成功编译 [正文PDF](<C:/Cursor/raven.mcs/TO_OVERLEAF_paper_tmc_r1_clean/main.pdf>) 与 [补充PDF](<C:/Cursor/raven.mcs/TO_OVERLEAF_paper_tmc_r1_clean/supplemental.pdf>)。
- 共检查 **41个图表**：正文4图8表，补充4图25表。**33个caption修改，8个完整保留**。所有改写以短标题起句，后接必要统计与辨识信息；少于目标词数且仍明确的标题未强行扩写，也未强制一行。
- 所有caption合计 **1375→1004词元，减少371**。其中正文 534→383，补充 841→621。正文/附录的说明迁移及合并分别净增加16/47词元，合计63；两份源码总体按同一近似口径 **净减少308词元**，没有把迁移当作净删除。
- 无新增表下注释；既有NSW四区域表下注释原样保留，行列、字号、间距不变。caption统计包含标题及其后的完整说明；表下注释总量变化为0。
- **正文14→14页，补充14→14页，完整页数净减少0**。未修改模板、字号、页边距或浮动体参数。
- 图1仍在正文第3页、Section III内（第三节起于第2页，第四节起于第4页）。摘要和引言逐字不变；引言仍为481词元，没有把说明搬入引言。

词数口径：去除TeX注释、引用/label参数、行内数学及命令名，以英文字母或数字及其内部连字符/撇号为词元；是透明的近似编辑计数，不是按原TeX空格计数。全文净变化用同一程序测量，并与caption变化及所有正文迁移的净增量核对相等。公式与数字的保真另行按源块逐字核对，未靠词数替代。

## 必要说明的实际落点

1. **City Scanner客户端身份**：从主表caption归入VII-A数据与选择协议设置，明确occupied 500m×30min cells，而非车辆。100窗设置在既有Appendix J-B/J-C构造中完整保留。主表caption保留十配对种子的mean±SD、每协议独立训练z-score尺度、非物理浓度/非共享尺度、WG四象限及端点最小值。
2. **同支持规则评分**：保存模型参数及末窗校正说明迁至VII-E的Matched-support rules段末，紧邻表VI；κ=1000的独立敏感性规则定义、调参种子身份和与默认Debt效果的区别在VII-E及Appendix E-A已有原文，caption不再重复。U-Air Count与不受该支持限制的FedAvg区别仍在caption及正文。
3. **T-Drive定位**：图3caption的表IV指引并入VII-C紧邻T-Drive机会/结果段；真实R、受控O/U、178窗、十种子SD、单位平衡参考及0.05诊断线均可查。SS/UA简称展开为对应Complete-aligned协议，不将机会诊断写成预测收益。
4. **四区域真实排名**：原补充表XX caption中的TwoStage-Hájek领先预测及client–stratum、FedAU领先组对齐，合并入Appendix F-C现有结果段；已存在的描述性+0.5%阈值及Holm p>0.05注释保留。
5. **覆盖候选结果**：SensorScope a=0.40与U-Air a=0.20因LCB低于阈值保持Gate off、U-Air a=1.00未达95%经验有效性，归入Appendix I表后结果段，未隐藏失格结果。caption继续标明historical candidate，并保留Validity/FSR/Gate ON定义，补清Duty为CERTIFIED占比；图7保留真实误覆盖、阈值、WARMUP/RESET、次窗RESET及与configured Design分离的身份。
6. **学习曲线设置**：图8的模型特定优化器/LR移入Appendix K设置段，逐种子最佳验证checkpoint合并到已有validation selects说明；曲线caption仍说明三开发种子、物理单位、行/列、均值/种子min–max（不是CI）、基线均值和log有效遍历。
7. **只删除重复的细节**：图1债务/空窗/Design职责在V-B/V-D/V-E已完整定义；数据表的目标来源在III-C/VII-A；离线零目标表的支持及输入时序边界在Appendix J-A；A5/A6审计的ζ公式和a_max=20在Appendix H。这些权威定义没有删除或变更。

## 逐图表标题前后对照

下列“标题”指caption原/新首句；旧稿首句尚未分离说明时，原样列出其统计或公式部分。词数为**完整caption**，不只计算标题。所有label（含别名）及编号与备份一致。

### 正文

#### 图 1 — `fig:raven_overview`

- 状态：修改；main.pdf第3页。
- 原标题：RAVEN-MCS in an active window.
- 新标题：RAVEN-MCS workflow.
- 完整caption词数：**94→60**。
- 说明处理：保留三子图、β→可行α、原始记录留本地及跨窗线型；债务依据/顺序和空窗处理已完整载于V-B/V-D，Design/Gate载于V-D/V-E，删去重复。

#### 表 I — `tab:datasets`

- 状态：修改；main.pdf第8页。
- 原标题：Datasets and roles.
- 新标题：Datasets and their evaluation protocols.
- 完整caption词数：**22→5**。
- 说明处理：目标信息来源已在III-C及VII-A明示；T-Drive的真实R/受控O/U已在同一设置段和表中Role列说明，删除重复。

#### 表 II — `tab:cityscanner_real`

- 状态：修改；main.pdf第9页。
- 原标题：City Scanner {PM}$_{2.5}$ completion under two distinct sensing protocols (mean $\pm$ SD, ten paired seeds and 100 windows per block; lower is better).
- 新标题：City Scanner completion under two sensing protocols.
- 完整caption词数：**62→43**。
- 说明处理：保留十配对种子、mean±SD、各协议独立训练标准化、方向、四象限WG和粗体；500m×30min客户端身份并入VII-A数据设置，100窗已在Appendix J两协议构造明确。

#### 表 III — `tab:cityscanner_sixarm`

- 状态：修改；main.pdf第9页。
- 原标题：City Scanner visit-occupancy target-map variants (mean $\pm$ SD over ten trace means, three model seeds per trace; a different aggregation level from Table~\ref{tab:cityscanner_real}).
- 新标题：City Scanner visit-occupancy target-map variants.
- 完整caption词数：**57→50**。
- 说明处理：保留十条轨迹均值/每轨迹三模型种子、rho、共同组目标及预测尺度；与主表的统计层级差异由两表明确的单位直接体现，删去重复表号提醒。

#### 图 2 — `fig:risk_noninterchangeability`

- 状态：修改；main.pdf第10页。
- 原标题：Complete-aligned NSW-Traffic risk differences.
- 新标题：Target and arrival-risk changes on NSW-Traffic.
- 完整caption词数：**44→42**。
- 说明处理：保留Complete-aligned、D定义、20种子样本SD、零线/负值、10/20线与方向计数边界，仅重组标题和压缩措辞。

#### 图 3 — `fig:g3_tdrive`

- 状态：修改；main.pdf第10页。
- 原标题：T-Drive opportunity.
- 新标题：T-Drive opportunity and target mismatch.
- 完整caption词数：**31→31**。
- 说明处理：保留目标/真实R/单位平衡三对象、SS/UA协议简称、TV和.05阈值；Design-off表引用迁到VII-C紧邻T-Drive结果段。

#### 表 IV — `tab:tdrive_hybrid`

- 状态：修改；main.pdf第10页。
- 原标题：T-Drive hybrid ranking: real taxi $R$, controlled $O/U$ (mean $\pm$ SD, 10 seeds, $178$ windows; lower is better).
- 新标题：T-Drive comparison under real sensing opportunities.
- 完整caption词数：**35→31**。
- 说明处理：保留真实R/受控O/U、十种子178窗、SD、方向、UTC组和Window简称；NoDesign比率定义已在V-D明示。

#### 表 V — `tab:main_effectiveness`

- 状态：修改；main.pdf第10页。
- 原标题：Always-on station protocol $R$, constructed $O/U$ (20 seeds, mean $\pm$ SD; lower is better).
- 新标题：Controlled station-protocol comparison.
- 完整caption词数：**44→29**。
- 说明处理：保留always-on/构造O/U、20配对种子SD、方向及Window身份；UTC组/简单基线/描述性容忍度已在VII-A，INT-R独立身份已在VII-A及Appendix F。

#### 图 4 — `fig:w1_design_gate`

- 状态：修改；main.pdf第11页。
- 原标题：Design versus No-Design with estimated/oracle propensities (20 seeds): $100(M_{\mathrm{Design}}-M_{\mathrm{NoDesign}})/M_{\mathrm{NoDesign}}$; positive means Design is worse.
- 新标题：Design sensitivity under estimated and oracle propensities.
- 完整caption词数：**34→23**。
- 说明处理：保留估计/oracle、两端点对应、20种子、相对变化公式及正值为更差；结果解释由图中数值和VII-D已有论述承担，D=off见V-D。

#### 表 VI — `tab:trained_rules`

- 状态：修改；main.pdf第11页。
- 原标题：Trained server-weight rules on matched Design-on support (20 paired seeds per dataset; means; lower is better).
- 新标题：Trained aggregation rules on matched Design-on support.
- 完整caption词数：**57→33**。
- 说明处理：保留matched Design-on支持、20配对均值、秒/运行及U-Air Count支持区别；保存参数和末窗校正迁至VII-E；κ=1000独立敏感性身份在VII-E首段及组件移除段已明确，caption去重。

#### 表 VII — `tab:e4_ablation`

- 状态：修改；main.pdf第12页。
- 原标题：Component-removal ablation: relative change (\%) after removing one RAVEN component.
- 新标题：Component-removal effects.
- 完整caption词数：**24→12**。
- 说明处理：保留百分比、正负方向和Holm星号，完整分母公式已在VII-E紧邻正文。

#### 表 VIII — `tab:target_concentration`

- 状态：修改；main.pdf第12页。
- 原标题：Traffic target concentration and the evaluated oracle-margin contrast.
- 新标题：Target-concentration sensitivity on NSW-Traffic.
- 完整caption词数：**30→24**。
- 说明处理：保留D/原标准单位、种子均值比公式与seed-paired区间/MDE口径；只精简标题和内部existing措辞。

### 补充材料

#### 表 IX — `tab:app_e1_balanced`

- 状态：完整保留；supplemental.pdf第5页。
- 原标题：Balanced control over the five pre-specified paired seeds.
- 新标题：Balanced control over the five pre-specified paired seeds.
- 完整caption词数：**8→8**。
- 说明处理：原caption已简短明确，全文保留。

#### 表 X — `tab:app_e2_daligned`

- 状态：完整保留；supplemental.pdf第5页。
- 原标题：Complete-aligned risk non-interchangeability statistics.
- 新标题：Complete-aligned risk non-interchangeability statistics.
- 完整caption词数：**17→17**。
- 说明处理：原caption已简短明确，全文保留。

#### 表 XI — `tab:e2_layer_matrix`

- 状态：完整保留；supplemental.pdf第6页。
- 原标题：Risk responses to controlled selection layers on NSW-Traffic.
- 新标题：Risk responses to controlled selection layers on NSW-Traffic.
- 完整caption词数：**27→27**。
- 说明处理：原caption已简短明确，全文保留。

#### 表 XII — `tab:app_local_hajek`

- 状态：完整保留；supplemental.pdf第6页。
- 原标题：Local-Hajek provenance audit.
- 新标题：Local-Hajek provenance audit.
- 完整caption词数：**3→3**。
- 说明处理：原caption已简短明确，全文保留。

#### 表 XIII — `tab:f1_mechanism`

- 状态：完整保留；supplemental.pdf第6页。
- 原标题：Within-stratum observation-probability diversity.
- 新标题：Within-stratum observation-probability diversity.
- 完整caption词数：**21→21**。
- 说明处理：原caption已简短明确，全文保留。

#### 表 XIV — `tab:app_p2_coverage`

- 状态：完整保留；supplemental.pdf第6页。
- 原标题：P2 feasibility-certificate coverage in the formal protocol blocks.
- 新标题：P2 feasibility-certificate coverage in the formal protocol blocks.
- 完整caption词数：**8→8**。
- 说明处理：原caption已简短明确，全文保留。

#### 表 XV — `tab:app_p2_warning_audit`

- 状态：完整保留；supplemental.pdf第6页。
- 原标题：Numerical feasibility audit of warning-affected P2 allocations.
- 新标题：Numerical feasibility audit of warning-affected P2 allocations.
- 完整caption词数：**7→7**。
- 说明处理：原caption已简短明确，全文保留。

#### 表 XVI — `tab:nearest_neighbor`

- 状态：修改；supplemental.pdf第7页。
- 原标题：Closest mechanisms and their information requirements.
- 新标题：Selection mechanisms and their information requirements.
- 完整caption词数：**26→6**。
- 说明处理：比较维度与机制已在表体、II及VII-A有明确说明，删除caption重复机制宣传。

#### 表 XVII — `tab:underserved_block`

- 状态：修改；supplemental.pdf第7页。
- 原标题：Validation-only under-served-block RMSE of the Table~\ref{tab:main_effectiveness} RAVEN configuration relative to FedAU-Window and ObsUse-Window (ten paired seeds; negative means the RAVEN row is better).
- 新标题：Validation RMSE in under-served UTC blocks.
- 完整caption词数：**59→32**。
- 说明处理：保留validation、十配对种子的均值相对百分比、比较对象、正负方向、Design配置及双阈值；结果未达改善/达到no-harm已在VII-D和表Win/no-harm列。

#### 图 5 — `fig:e3_structural`

- 状态：修改；supplemental.pdf第7页。
- 原标题：Frozen same-backbone structural results: means $\pm$ sample SD, 20 paired seeds, lower is better.
- 新标题：Structural mismatch under the frozen station protocols.
- 完整caption词数：**49→44**。
- 说明处理：保留样本SD/20配对种子、四面板、Design-on及不同支持集；两种Design配置在Appendix F开头及主表已有说明。

#### 图 6 — `fig:e3_prediction`

- 状态：修改；supplemental.pdf第8页。
- 原标题：Frozen prediction results: means $\pm$ sample SD, 20 paired seeds, lower is better.
- 新标题：Prediction error under the frozen station protocols.
- 完整caption词数：**34→34**。
- 说明处理：保留样本SD/20配对种子、四面板、Design-on和结构图的支持身份引用；U-Air off=1.1131保留主表，删去重复数字。

#### 表 XVIII — `tab:app_e3_sensorscope`

- 状态：修改；supplemental.pdf第8页。
- 原标题：SensorScope full method context (mean $\pm$ std over 20 seeds).
- 新标题：SensorScope method comparison.
- 完整caption词数：**20→14**。
- 说明处理：保留SD/20种子、方向、dagger参考身份；RAVEN-Design与主表对应关系已在Appendix F开头及两表同名行清楚呈现。

#### 表 XIX — `tab:app_e3_uair`

- 状态：修改；supplemental.pdf第9页。
- 原标题：U-Air full method context (mean $\pm$ std over 20 seeds).
- 新标题：U-Air method comparison.
- 完整caption词数：**79→36**。
- 说明处理：保留20种子SD、方向/参考标识、读取目标者的支持限制、全交付FedAvg与两图不同的支持、Design-on；删内部runner再运行叙述，不改变数据版本。

#### 表 XX — `tab:traffic_four_region`

- 状态：修改；supplemental.pdf第9页。
- 原标题：NSW-Traffic ranking under a four-region public target map (mean $\pm$ std, 10 seeds, $100$ windows).
- 新标题：NSW-Traffic comparison under a four-region target.
- 完整caption词数：**38→20**。
- 说明处理：保留十种子100窗SD、方向及粗体；TwoStage/FedAU真实排名归入Appendix F四区域正文，描述性容忍度和现有表下注释保留。

#### 表 XXI — `tab:app_block_rmse`

- 状态：修改；supplemental.pdf第10页。
- 原标题：Four-block $\mathrm{RMSE}_g$ (mean $\pm$ std over 20 paired seeds).
- 新标题：Per-group RMSE across four UTC blocks.
- 完整caption词数：**24→23**。
- 说明处理：保留20配对种子SD、方向、WG定义及双Design配置；UTC区间和最差组已在该小节正文，删除G2过程标签。

#### 表 XXII — `tab:app_runtime`

- 状态：修改；supplemental.pdf第10页。
- 原标题：Wall-clock runtime on the risk-semantic workloads in seconds (mean $\pm$ std).
- 新标题：Runtime on the risk-semantic workloads.
- 完整caption词数：**10→11**。
- 说明处理：保留wall-clock秒/运行及SD；各列120/20运行的统计单位仍在相邻正文。

#### 表 XXIII — `tab:int_r_occ`

- 状态：修改；supplemental.pdf第10页。
- 原标题：INT-R occupancy audit on the shared EventTraces (eight logical clients).
- 新标题：INT-R occupancy on shared event traces.
- 完整caption词数：**26→25**。
- 说明处理：保留八客户端、Goh–Barabási间隔定义及训练A=1风险集，标题与说明分开。

#### 表 XXIV — `tab:int_r_e3`

- 状态：修改；supplemental.pdf第11页。
- 原标题：INT-R robustness ranking under intermittent protocol $R$ (mean $\pm$ std over 20 seeds).
- 新标题：Station-protocol comparison under intermittent opportunities.
- 完整caption词数：**39→22**。
- 说明处理：保留20配对种子SD、方向及各行固定Design身份；去掉含混的same settings说明，intermittent与station范围保留标题和正文。

#### 表 XXV — `tab:app_a5_a6_audit`

- 状态：修改；supplemental.pdf第11页。
- 原标题：Support-hypothesis audit on the formal-protocol traces.
- 新标题：Support-hypothesis audit on formal station traces.
- 完整caption词数：**52→30**。
- 说明处理：保留active含义、真边际/20 Design-on支持集及med/p95/max；decisive解释、ζ比与a_max=20已在相邻审计正文。

#### 表 XXVI — `tab:certificate_stress`

- 状态：修改；supplemental.pdf第12页。
- 原标题：Coverage-stress audit of a candidate aggregate coverage Gate.
- 新标题：Historical coverage candidate under controlled stress.
- 完整caption词数：**51→35**。
- 说明处理：保留历史候选、Validity/FSR/Gate分母；补清Duty含义，既有Gate-off和U-Air未达95%结果迁到同节表后结果段。

#### 图 7 — `fig:certificate_audit`

- 状态：修改；supplemental.pdf第10页。
- 原标题：Coverage-diagnostic audit of the historical candidate (separate from configured Design).
- 新标题：Coverage diagnostics for the historical candidate.
- 完整caption词数：**54→33**。
- 说明处理：保留历史候选/配置Design分离、CERTIFIED子图、真实误覆盖、y=x/阈值、WARMUP/RESET及次窗RESET；Gate-off阈值原因与表后结果段合并。

#### 表 XXVII — `tab:scd_phi_freeze`

- 状态：修改；supplemental.pdf第12页。
- 原标题：Offline zero-target counts for occupancy-attached clients using frozen $\pi^{\mathrm{tar}}(k(i),s(i))$ (missing keys: $0$).
- 新标题：Offline zero-target counts for attached clients.
- 完整caption词数：**33→15**。
- 说明处理：保留lookup对象、missing=0和离线规则；支持/输入时序边界及不同25.5%统计在紧邻正文已逐字保留。

#### 表 XXVIII — `tab:cityscanner_sixarm_cs`

- 状态：修改；supplemental.pdf第12页。
- 原标题：Client--stratum gaps for Table~\ref{tab:cityscanner_sixarm} (mean $\pm$ SD, ten trace means of three model seeds).
- 新标题：Client--stratum gaps across City Scanner target maps.
- 完整caption词数：**25→29**。
- 说明处理：保留十轨迹均值/每轨迹三种子SD及目标不共用的排名边界；主表引用在同节开头已存在。

#### 表 XXIX — `tab:learning_capacity`

- 状态：修改；supplemental.pdf第13页。
- 原标题：Common-NDMF Central-delivered validation (three development seeds; physical units).
- 新标题：Central-delivered Common-NDMF validation against simple baselines.
- 完整caption词数：**20→23**。
- 说明处理：保留三开发种子、物理单位及gain是种子配对相对强基线的均值，标题点明对照对象。

#### 图 8 — `fig:learning_capacity`

- 状态：修改；supplemental.pdf第13页。
- 原标题：Central-delivered development curves (seeds 41001--41003): training/validation RMSE by row, physical units by column.
- 新标题：Centralized learning curves across datasets.
- 完整caption词数：**50→37**。
- 说明处理：保留开发种子、训练/验证行、物理单位列、均值/三种子min–max、基线种子均值及log有效遍历；选定优化器及逐种子最佳checkpoint归到Appendix K设置段。

#### 表 XXX — `tab:arrival_support`

- 状态：完整保留；supplemental.pdf第13页。
- 原标题：Arrival-log geometry.
- 新标题：Arrival-log geometry.
- 完整caption词数：**16→16**。
- 说明处理：原caption已简短明确，全文保留。

#### 表 XXXI — `tab:development_geometry`

- 状态：修改；supplemental.pdf第14页。
- 原标题：Natural-window geometry in the separate development protocol (seeds 41001--41003, cap .5 and ESS minimum 3).
- 新标题：Natural-window geometry under the separate development protocol.
- 完整caption词数：**16→15**。
- 说明处理：保留独立开发协议和原种子/cap/ESS，仅分开短标题与设置。

#### 表 XXXII — `tab:geometry_sensitivity`

- 状态：修改；supplemental.pdf第14页。
- 原标题：Traffic geometry on 183 fixed-$K=8$ subsets.
- 新标题：NSW-Traffic geometry under cap and ESS changes.
- 完整caption词数：**18→20**。
- 说明处理：保留183个固定K=8子集、E/cap/repair定义和不变可调整质量，明确题名为cap/ESS比较。

#### 表 XXXIII — `tab:release_timing`

- 状态：修改；supplemental.pdf第14页。
- 原标题：Traffic release-control diagnostics on one development seed ($G$, $W$, and $J$: lower is better).
- 新标题：Traffic release-control diagnostics.
- 完整caption词数：**11→10**。
- 说明处理：保留单开发种子和G/W/J方向，详细方法/单位已在Appendix M-A正文。

## 数字、身份与范围核验

所有tabular/tabular*、equation/align/multline及algorithm环境与备份逐字一致，所有includegraphics文件名和宽度参数一致；图形文件和绘图脚本未写入、未执行，实验资产未处理。33处caption及记录在案的正文说明迁移之外，main.tex/appendix.tex余文完全一致；supplemental.tex和reference.bib按字节不变。全文各label及生成编号集合一致，无孤立新增对象；引用逐项编号格式保留，表格编号引用仍限Evaluation及其后或补充材料。

特别核对：City Scanner两协议各自尺度和统计单位；六臂十轨迹均值而非三十独立重复；W1的Design-on支持及独立κ变体；U-Air表XIX与图5/6的FedAvg支持不同；样本SD与种子范围不互换；消融百分比分母、正负方向、Holm星号；覆盖候选和configured Design不混同。实验优劣排名、不利数值及理论条件未变。

## 编译及逐页版式验收

现有MiKTeX pdflatex/BibTeX工具链，关闭自动安装及shell escape，低优先级、数值库线程1、单进程顺序构建。最终8次调用均退出0，正文/补充aux稳定；没有未定义引用、重复标签、Overfull，BibTeX无warning。保留既有epstopdf的shell-escape禁用提示，不为消除提示开启shell命令。

已实际渲染并阅读所有16个含图表页面：

- 正文第3页：图1流程、三子图标记和图注换行正常，位置在III内。
- 正文第8页：表I标题及多列宽度正常。
- 正文第9页：表II/III，独立尺度、统计层级及rho注释清楚，无压线。
- 正文第10页：图2/3、表IV/V；方向/阈值、方法标签和表格没有遮挡。
- 正文第11页：表VI及图4；时间单位、支持差异和正负方向清楚。
- 正文第12页：表VII/VIII；星号、公式及CI/MDE列完整。
- 补充第5页：表IX/X；统计量与区间完整。
- 补充第6页：表XI–XV；矩阵、短表和说明未碰线。
- 补充第7页：表XVI/XVII及图5；方法机制长单元格、验证方向、误差线正常。
- 补充第8页：图6及表XVIII；RAVEN-Design身份及参考dagger清楚。
- 补充第9页：表XIX/XX；支持差异仍可直接读到，既有表下注释未裁切。
- 补充第10页：表XXI–XXIII及图7；图例、轴名、状态标记、候选身份正常。
- 补充第11页：表XXIV/XXV；双Design行和审计真边际说明正常。
- 补充第12页：表XXVI–XXVIII；候选诊断分母、离线lookup及目标差异说明正常。
- 补充第13页：表XXIX/XXX及图8；六面板、物理单位、阴影和说明正常。
- 补充第14页：表XXXI–XXXIII；开发协议及单种子诊断边界保留，书目正常。

最后一次去重及缩写展开后，重编译并再次阅读受影响正文第10–12页；两PDF页数与图表所在页不变。未见裁切、重叠、缺字、caption压线或新增异常空白。既有图内文字、表下注释和基础字号没有缩小。新caption逐项运行本地表达检查，无error/warning、em dash为0；若干紧凑统计说明触发分号密度advisory，人工按其定义/单位分隔用途核对保留，没有为此拉长caption。

## 回退与核验记录

备份：[caption_concision_20261030_164954](<C:/Cursor/raven.mcs/TO_OVERLEAF_paper_tmc_r1_clean/revision_backups/caption_concision_20261030_164954>)。包含修改前main.tex、appendix.tex、supplemental.tex、reference.bib、两PDF及辅助文件；已附最终main.tex.diff、appendix.tex.diff和BACKUP_AND_RESTORE.md。没有覆盖历史备份。

若无后续编辑，可还原备份main.tex/appendix.tex后重建两PDF；若已有后续修改，仅按差异合并恢复本轮caption及七处正文归位，不能整份覆盖后续工作。补充入口和书目从未改动；不需要恢复或重跑任何实验。

结构核验、完整caption旧/新文本、迁移文本及编译记录保存在 tmp/caption_concision_20261030/，报告使用的核验记录也已复制到备份。源码和PDF为唯一规范稿，没有创建另一套final稿。

未解决项：本轮标题/说明及版式验收无遗留阻断；页数仍为14/14，不宣称减少了完整页面或新增研究证据。
