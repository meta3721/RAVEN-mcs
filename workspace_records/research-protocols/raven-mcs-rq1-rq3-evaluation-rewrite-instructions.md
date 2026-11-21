# RAVEN-MCS：参照MapT-STC的RQ驱动评价重写指令

本指令于2026-11-01按最新讨论更新。正式采用“整体效果—机制作用—可调空间”三个RQ，覆盖此前以cost或stabilization conditions为问题标题的版本。后两者按相关性作为配套证据，不主导RQ措辞。

请使用 `ccf-paper-writer` 将最新论文的Evaluation重组为“先列研究问题—再介绍数据与比较设置—最后逐项回答RQ1–3”的结构。结合 `ccf-humanization`，依据既有图表与实验材料写英文LaTeX，不新增实验，不改变结果，不把内部审计语言写进论文。

## 1. 材料与本轮结构优先级

正文及补充：`C:/Cursor/raven.mcs/TO_OVERLEAF_paper_tmc_r1_clean/`下最新 `main.tex`、`appendix.tex`、`supplemental.tex`、`main.pdf`、`supplemental.pdf`。

结构范文：

`C:/Users/szr/Documents/xwechat_files/wxid_6u3gb5i5cvyq22_ceae/msg/file/2026-11/MapT-STC A One-Shot Spatiotemporal Data Completion Framework for Cold-Start Tasks in Sparse Crowdsensing (1).pdf`

重点阅读范文PDF第10–15页：Performance Evaluation先列五个RQ，随后Datasets、Baselines & Measures，后续C–G小节与RQ1–5对应。

本轮采用这一检索友好的组织方式，替代旧指令建议的五个主题小节结构。保留旧指令的证据保护、14页、图表核验和实验暂停要求。

不照搬范文的RQ内容、算法结论、数据集划分和方法。不要复制其冗长的泛化评价或“所有组件必然必要”的判断。

修改前保存拟改TeX及PDF备份；以当前已完成的标题、三项贡献、摘要、图表集成状态为准，不恢复旧版。

## 2. 先校正“贡献—预期实验—证据”表的用途

用户提供的三行表作为内部证据映射，不直接作为论文结果或正式统计结论：

1. 完整方法在City Scanner的组失配收益是整体证据，不等于机会、观测和可用性三层校正分别得到独立验证。
2. 目标风险与到达风险不同，是评价对象的区别，不是RAVEN优于其他方法的直接证据。
3. 完整校准是多项目标的协调，不能预设其group mismatch必然优于Uniform或reference projection。
4. 每项消融是否有实际重要收益应由现有结果回答，不能先写“每个组件都必要”。
5. 理论恢复与非扩张由证明及条件支撑。现有实验主要检查适用条件、支持几何和敏感性，不直接证明渐近恢复或误差界。
6. “中等”“中等偏强”是定性的证据匹配判断，不是统计置信度；不写进论文，不用它代替效应量、区间、检验或明确条件。

新结构的目的，是让实验问题与研究主张相符，不是事后修改阈值或让结果都变成成功。

## 3. Evaluation开头：研究目标与三个RQ

用一个简短英文段落说明评价考察三个层次：部署目标对齐效果、参考重构与可行校准的机制作用、目标支持及聚合约束决定的可调空间。不要一开头堆数据集名、结果数字或完整假设清单。

随后列三个简洁RQ，采用以下默认文本，可作语法微调但不能扩大范围：

**RQ1: How effectively does RAVEN-MCS align aggregated client contributions with deployment targets under sequential sensing and update selection?**

**RQ2: How do reference reconstruction and feasible calibration contribute to deployment-group alignment on matched client support?**

**RQ3: How do target support and aggregation constraints shape the feasible adjustment of deployment-group mass?**

三问分别关联：

- RQ1：完整框架是否达到应用目标，以及目标评价为何不同于到达评价。
- RQ2：通过匹配支持的对照识别参考重构与可执行校准的作用，预测与计算成本作为配套维度。
- RQ3：解释目标图、可用支持、cap与ESS如何决定可执行的组质量调整空间；稳定化与学习敏感性作为必要的辅助解释。

不使用“RQ3: Do experiments validate the theoretical guarantees?”，现有证据无法直接回答这一问题。也不新增样本量扫描、误差界覆盖实验或真实采集来补齐它。

正文允许使用定义清楚的RQ1–3作为正式研究问题，区别于内部实验任务号。只在开头、对应小节标题与必要回指处使用，普通行文不要反复以RQ编号代替问题名称。

## 4. 推荐章节结构

Evaluation开头的目标段与RQ列表后，按以下顺序：

### A. Datasets and Selection Protocols

说明数据、客户端定义、目标组与strata、时间划分、各协议R/O/U的来源。保留数据概况表。

### B. Baselines and Evaluation Measures

定义完整RAVEN、on/off配置、简单基线、matched-support规则、组件移除和oracle参考；说明主要/辅助指标与单位。

### C. Implementation and Statistical Settings

说明公平配对、backbone及预算、模型评分口径、seed与trace单位、统计家族和预先已有的阈值。内容较短时可以作为B节下的子段落，避免无意义碎片化。

### D. Deployment-Target Alignment (RQ1)

应用结果、风险度量语义与不同协议中的表现范围。

### E. Contributions of Reference Reconstruction and Calibration (RQ2)

匹配支持对比、组件效果及结构—预测—运行时间取舍。

### F. Target Support and Feasible Adjustment (RQ3)

目标支持变体与支持几何为主体；截断、参考扰动和学习敏感性仅保留解释所需的内容，其余详细诊断放附录。

未来工作仍在后续Conclusion and Future Work，不混入RQ答案。无需新增独立的内部证据评分或审计小节。

保留可复用label并同步引用，不硬编码最终罗马节号、表号和页码。

## 5. 数据、基线和指标怎么写

### 5.1 数据与协议

数据集介绍必须服务于RQ，不照搬一般背景百科：

- City Scanner两套协议：RQ1的主要应用对比；目标支持变体还用于RQ3。
- SensorScope/U-Air受控站点协议：RQ2的归因比较与RQ3的条件分析。
- NSW-Traffic：风险语义、不同目标/支持或更新规则的辅助分析，按实际协议分开。
- T-Drive：真实机会下的协议比较，不能归入全真实端到端交付验证。

说明受控与实测过程，不能统称real-world datasets就暗示真实R/O/U。occupied cells和station clients等身份保持准确。

### 5.2 比较对象

分清两种比较：

- 应用比较允许比较完整方案的实际表现，但不能将差异全归因于某一校正层。
- 归因比较必须说明共用的支持、目标、约束和评分规则；不能把支持改变的on/off差异冒充同支持权重干预。

FedIPW/FedPALS若仅为机制定位而未实际运行，应明确其身份，不能列为已完成性能基线。

### 5.3 指标与统计

group mismatch用于检验部署组质量对齐；client–stratum mismatch、RMSE、worst-group和运行时间各有不同作用。说明实际研究叙事的主次，不声称本轮重新组织后的主次是历史上重新注册的统计方案。

保留所有现有显著性家族、效应量、单位与阈值。尤其区分：

- 均值±SD与置信区间。
- seed-paired与trace-cluster分析。
- 比值的均值与均值的比值。
- 描述性+0.5%容差、正式2%非劣界和不同实验的实际效应标准。

不重新检验、不调整显著性阈值、不把“中等匹配”转成新统计结论。

## 6. RQ1的结果组织与答案边界

### 6.1 应用层主要结果

以 `tab:cityscanner_real` 及已经实际集成的对应图为核心，按两个协议分别说明：

- RAVEN在五种方法中的平均组失配排序。
- 相对TwoStage-Hájek的25.8%/23.3%变化口径。
- 辅助端点和预测端点的真实领先者。

使用“完整框架在两套城市感知协议中改善部署组质量对齐”的范围，不把它改写成三层校正独立有效、全数据集有效或普遍预测精度提升。

### 6.2 为什么不是只看误差

风险语义实验作为一个简短分析段，说明同一选择变化在deployment-target和arrival-weighted risk下反应不同。保留对应图表/附录直接引用。

明确该现象涉及评价分布，而非RAVEN独有的性能优势。不要把五种方法共同出现的风险差异称为RAVEN优于其他方法。

### 6.3 跨协议范围

T-Drive和NSW四区域实际比较可用一个紧凑段落给出结果及差异条件，完整表若在附录则直接引用。保留关键不利排序，不能只有有利协议出现在RQ1。

### 6.4 小节结尾

用1–2句直接回答RQ1：已观察到哪些协议上的部署组对齐收益，预测排序是否一致，证据覆盖哪些真实/受控过程。

不用“RQ1: PASS”“中等置信”“全部验证”等内部状态词。

## 7. RQ2的结果组织与答案边界

以 `tab:trained_rules` 为核心，围绕以下隔离比较推进：

1. Count→Uniform：计数权重在结构差距中的作用。
2. 校正参考→可行投影：从统计参考转为当前窗口可执行分配的变化。
3. Uniform→校正参考投影：超出Uniform的参考增量。
4. 简单投影→完整P2：额外校准目标的结构、预测与时间取舍。

使用原有数字与区间，特别保留SensorScope的0.768 pp与U-Air的0.286 pp，但明确它们属于projection相对Uniform；不能把它们写成full P2相对projection的收益。

SensorScope独立projected Design on/off对比可辅助解释机会校正，不能与另一条路径增量直接相加。U-Air支持变化的比较不承担同样的纯归因解释。

随后用组件移除表回答哪些机制在哪些端点有作用：

- 不要求每项都显著，更不预先宣布所有组件必要。
- 债务显著但量级小的结果按原口径说明，不能夸大为关键收益来源。
- 正式强度与kappa=1000敏感性变体保持分开。
- 不显著预测差异不等于等效或无代价。

运行时间与结构/预测取舍放在同一语境，不另散落到未来工作。保留简单投影在部分端点优于full的事实。

小节末用1–2句回答：哪些增量已识别，哪些是多目标取舍，哪些组件的实际必要性仍未确立。不要用一句“校准全面有效”覆盖所有差异。

## 8. RQ3的结果组织与答案边界

理论贡献由证明承担，RQ不必与三项贡献机械地一一对应。本小节首先回答目标支持和约束决定的可调空间，继而说明必要的经验条件。按下列顺序组织：

### 8.1 目标支持与目标形状

用既有六臂目标图实验比较控制图、floor处理、外部形状与Design配置。说明每种变体改变了什么、共同部署目标如何保持、哪些client–stratum指标属于不同目标因而不能直接排名。

以组对齐的已有结果为主体，完整预测结果与区间保留在相应表和解释中。不能把floor同时改变目标边际的干预说成纯粹支持恢复，也不能把十条trace各三model seeds写成三十条独立trace。

### 8.2 支持与可调空间

用正式窗口的forced-Uniform比例、可行组组成范围和可调目标质量说明为什么部分窗口几乎没有权重或组成调节自由。

分别标明formal traces、arrival logs和development protocol；不能混用分母。L1组成距离范围很小，不意味着P2中的平方L2项恒定。

### 8.3 稳定化与参考敏感性

准确写成截断/概率下限被触发，不能称“稳定器失效”。保留实际触发比例、稳定化误差及现有估计/真实边际对照结果。

理论的一般扰动界包含稳定化误差项；A6a是该项为零的充分条件，不能误写为必要条件。现有日志不能核验的A6b或共享状态，不写成已验证成立。

若理论常数过宽，准确说明该最坏界不提供紧的数值预测；不由此推导全部理论无效，也不忽略这一事实来宣称界与实测吻合。

### 8.4 补充敏感性

目标集中度、oracle/优化器敏感性等已有结果只选与本问直接相关的内容；详细开发配置和学习曲线继续留附录，不在正文形成第四个零散问题轴。

结构对齐不自动转成RMSE改善，现有误差不敏感也不等于证明任何算法都没有收益。保留未建立的非劣、检测能力与控制条件，集中说明而不反复自我辩解。

本小节不虚构误差随样本量收敛的实验，不写“实验证实了渐近恢复”“验证了误差界覆盖率”或“证明了全轨迹稳定性”。

小节结尾先直接回答：目标支持、cap与ESS如何决定可行组质量的调整空间；仅在解释必需时简述稳定化或学习条件。不要用一段假设核验日志代替RQ3的答案。

## 9. 每个RQ内部采用问题—设计—结果—解释—回答

小节开头一两句说明比较怎样回答问题，不重抄setup。随后以图表和决定性效应组织结果，再给现有机制/控制比较支持的解释，最后直接回答RQ。

结构可以自然变化，不要求每段固定四句。避免按数据集连续罗列数字后才补一句总结。

使用现有图表，不因采用RQ就新增一套重复图。图应服务于相应问题：

- 城市感知主结果图/表→RQ1。
- matched-support、Design机制、组件移除和成本→RQ2。
- 目标支持变体、几何、稳定化与学习敏感性→RQ3。

若旧段落同时涉及多个RQ，拆分或保留主归属并短引用另一小节，不复制整段。

## 10. 不把评价结构当作证据升级

改写后必须保留以下区别：

- 重构参考的理论性质、完整方法的应用表现、单模块独立增量。
- 可执行性、目标对齐、预测价值与计算成本。
- 现有对照支持的机制解释与尚未隔离的因果贡献。
- 已证明的条件结论与实际日志能够检查的条件。

明确RQ有助于评审定位证据、识别结论和理解边界；不能承诺因此消除新颖性、简单基线或实用价值方面的质疑。论文不能用清晰结构取代缺失的关键证据。

## 11. 验收与交付

编译正文与补充至xref稳定；若图表在主文/附录间移动，更新counter和所有引用，不留重复label、重号或只在md文件里的证据。

正文不超过14页，补充不长于正文。优先精简setup重复、内部过程与开发细节；不得缩小模板字体/页边距或删关键不利比较凑页。

逐项验收：

1. RQ1–3先列出，dataset与baseline/metrics紧随其后，后续三个小节逐一回答。
2. 每个RQ都有可追踪图表、实际比较设计与明确回答。
3. 没有将定性匹配程度写成统计置信度。
4. RQ2没有预设完整校准胜过简单投影，RQ3没有冒充实验验证定理。
5. 实验数值、检验家族、阈值、方法身份和支持集条件保持准确。
6. 数据表、简单投影、成本、未建立非劣等关键证据仍可见。
7. 未来工作保持独立，不将已完成诊断改为计划。
8. 备份与本轮改动可恢复；实验没有启动。

交付正式源文件和两份PDF，并写：

- `C:/Cursor/raven.mcs/ccf-review-report/RQ_DRIVEN_EVALUATION_REVISION_REPORT.md`
- `C:/Cursor/raven.mcs/ccf-review-report/RQ_DRIVEN_EVALUATION_REVISION_DIFF.md`

报告列出新结构、各RQ最终回答及证据位置、旧段落/图表去向、保留的不确定性和实际页数/编译状态。内部“贡献—证据—匹配”表留在报告，不进入论文。

## 12. 本轮特别要求：围绕贡献写结果，清除自我否定式叙述

论文以“目标对齐效果—机制作用—可调空间”为叙事主线。开篇、RQ列表和各小节主题句不提前列出不足，不使用内部证据评级，不把论文写成问题检查记录。

执行以下文字处理：

1. 删除无关开发失败、退役方案与实验审批过程；这些记录留在项目材料，不写进正文。
2. 合并重复的 `we do not claim`、`does not establish`、`not a guarantee` 等告诫。必要范围通过明确的对象、协议、条件和实际统计结果表达，不另加一段自我辩护。
3. 每段先给研究问题或已有证据支持的发现，再用图表解释；不要以“未达到门槛”“无法验证”作为所有段落的开头。
4. 结果解释强调可识别的作用与科学发现：例如校正参考与可执行分配的区别、可行投影的作用、支持与cap/ESS决定的调整空间。
5. 预测和成本放在相关比较中简洁说明，不用它们替代目标对齐评价，也不让它们成为全文反复出现的自我评价。
6. 不删除会改变比较结论的表格行、区间、方法身份或观察事实；不把不显著写成等效，不把不同端点概括成全面领先。
7. 可以减少重复披露的篇幅，不能通过省略关键比较制造错误印象。全文已有精确结果时，不在每个RQ总结里再次复述同一限制。

结果段不需要展示内部“成功/失败/中等匹配”标签。每个RQ的结尾直接陈述该问题的已有答案，能用准确的范围和数字完成的，不再追加套话。

## 13. 从现有混合章节迁移到RQ结构

以源文件中的当前小节、label与内容定位，不按旧行号覆盖。

- `Experimental Setup`：拆分/整理为数据协议、基线指标、实现统计；设置中提前出现的结果分析归入对应RQ。
- `Real Sensing Opportunities and Measured Observation`：主结果归RQ1；其目标支持六臂段落及对应表归RQ3。
- `Risk Semantics and External Protocols`：风险语义与外部协议的总体比较归RQ1，均明确其解释角色；不要混成完整方案的统一获胜证据。
- `Design Effects in Controlled Station Protocols`：机制对照归RQ2；on/off导致支持改变的必要解释紧随该比较。外部占据协议的完整敏感性细节可留附录。
- `Attributing Structural Gains and Component Trade-offs`：matched-support、组件移除、预测/成本比较归RQ2；数值诊断简述并指向附录。
- `Prediction Sensitivity and Adjustment Geometry`：目标支持、约束几何和必要参考敏感性归RQ3；开发训练预算、独立backbone探索、完整优化器诊断留附录。
- `Update-Rule Sensitivity and Coverage Scope`：只将直接回答新RQ的必要内容融入对应部分；窗口释放单种子研究、独立coverage-controlled变体的完整轨迹留对应附录。不得将其改名为主方法实验。

每个图表保留唯一正式位置，所有主张有直接引用。已经完成的图片集成与批注修复保持，不恢复旧版。

若旧label名称中带rq1/rq2/rq3但语义已改变，保留label并重新检查所有引用指向；如重命名，则全文同步。不得因字符串名称相似，把旧的“风险语义RQ1”直接当作新的应用对齐RQ1。

## 14. 可直接替换的开头与标题骨架

下面是结构骨架，不是完整交付。执行者必须填入根据当前图表改写后的实质结果，最终稿不允许保留占位文字。

```latex
\section{Evaluation}
\label{sec:evaluation}

We evaluate RAVEN-MCS from three complementary perspectives:
deployment-target alignment, the contributions of reference
reconstruction and feasible calibration, and the adjustment space
induced by target support and aggregation constraints.
Specifically, we address the following research questions.

\begin{itemize}
\item \textbf{RQ1:} How effectively does RAVEN-MCS align aggregated
client contributions with deployment targets under sequential
sensing and update selection?
\item \textbf{RQ2:} How do reference reconstruction and feasible
calibration contribute to deployment-group alignment on matched
client support?
\item \textbf{RQ3:} How do target support and aggregation constraints
shape the feasible adjustment of deployment-group mass?
\end{itemize}

\subsection{Datasets and Selection Protocols}

\subsection{Baselines and Evaluation Measures}

\subsection{Implementation and Statistical Settings}

\subsection{Deployment-Target Alignment (RQ1)}

\subsection{Contributions of Reference Reconstruction and Calibration (RQ2)}

\subsection{Target Support and Feasible Adjustment (RQ3)}
```

如果RQ2标题在双栏中太长，可缩短为 `Mechanism Contributions (RQ2)`；完整问题已在开头定义，不影响含义。实现/统计设置若过短，可合并到B节形成自然段，不必为了骨架保留空壳小节。

只在开头列一次RQ。后续用自然语言回答，避免多层item、内部编号、同一句结果反复出现。

## 15. 修改范围与最终回复补充要求

本轮主要修改Evaluation及其对应附录中的内容位置和引用。最新摘要、引言、三项贡献、标题和结论不作无必要的重写；只有因小节移动造成的引用或一两句重复需要调整时才同步修正并说明。

不要声称“实验已达到中等置信程度”或“已经验证全部三项贡献”；报告用实际证据对应解释完成情况。

最终回复提供可点击的两份正式PDF及修改报告，并简洁说明：三个RQ最终是什么、主要图表分别回答哪个RQ、哪些冗余段落已合并或移附录、编译与页数情况。文件名和输出路径沿用第11项，实验继续暂停。
