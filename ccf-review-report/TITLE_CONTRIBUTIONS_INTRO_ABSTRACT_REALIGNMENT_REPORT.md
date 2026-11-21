# 标题、贡献、引言与摘要重新对齐报告

日期：2026-10-31。本报告对应用户本次明确重发的完整执行要求，以收到本次请求时的最新稿为基线，不回退上一轮已完成内容。上一份同名报告和差异已归入本次修改前归档。

采用ccf-paper-writer进行实际LaTeX修改，ccf-humanization进行语言检查。已读取完整指令、当前规范源文件与两份PDF、现有书目、导师材料及审查；重新核对范文第1–2页。实际执行顺序记录于`C:/Cursor/raven.mcs/tmp/title_realignment_recheck_20261031/execution_order.json`：先凝练贡献并保存第四段/贡献列表，再保存挑战段，最后核对标题、修改八句摘要。未执行实验、推理、重评分、统计检验或算法修改。

## 1. 标题与统一主线

**RAVEN-MCS: Target-Mass Calibration for Windowed Federated Data Completion in Mobile Crowdsensing**

当前标题已经是指令默认短标题，本轮核对后保留；补充标题与其一致，未为产生差异而再改名。Target-Mass Calibration为中心，Windowed限定实际协议，Federated Data Completion与Mobile Crowdsensing保留任务关系；未承诺普遍预测领先、精确目标实现或主动停止。源码和PDF没有显式/Title或pdftitle字段，不新增元数据依赖。结论已有相同对象关系，本轮保持。

中心主线：**重构感知单元上的统计目标参考，再在当前可用支持、cap及有效支持约束下，将其转为面向部署组对齐的可执行客户端混合。** 部署目标、重构参考和最终权重继续区分。

## 2. 三项贡献及证据

贡献一中文释义：按感知单元而非仅客户端频率刻画顺序校正；同一机会/观测校正量供给局部归一化训练及质量估计，可用性校正再重标定质量以形成服务器参考。依据III-B/C、IV-A/B/C和附录A-A的理想因子分解。VII-C的选择层实验、VII-E的同支持Design比较与直接参考读出提供机制解释；Local-Hájek抵消事实保留。没有把IPW/Hájek本身宣称原创，也没有把F1未闭合预测结果恢复为收益。

贡献二中文释义：把统计参考与可行聚合分开，通过当前支持、权重上限及客户端有效支持约束下的完整P2连接它们，协调参考锚、部署组组成及累计欠服务。依据V-A/B/C/D、定理1与附录A-D，以及VII-E的直接参考、Uniform、投影、完整P2比较。简单投影是独立比较规则，未冒充完整RAVEN；没有宣称所有正则项均有实际收益或债务自行稳定。

贡献三中文释义：理想汇总目标矩的恢复及固定共享状态下参考到权重/组成的扰动性质。依据命题2（A1–A3、正确比率/支持/顺序识别/簇正则）及命题3（A1/A4/A5/A6b、正质量、共享active support/M/C及其余状态固定）、附录A-C/A-E/A-H。本文表述的非扩张针对权重映射，组成另有算子范数界；估计误差与稳定化误差分别进入界。第三项不再以使用某数据集为创新主体，也没有新增定理或长期/预测保证。

### 贡献1（44词）

We reconstruct a deployment-target reference over atomic sensing units through sequential opportunity, observation, and usable-update correction. Shared opportunity and observation weights supply normalized local training and client-mass estimates; usability correction then rescales these masses into a server reference that retains relative representation across clients.

### 贡献2（42词）

We develop a window calibration program that converts the reconstructed reference into executable weights on available clients under weight caps and client-level effective-support constraints. Its reference anchor, group-composition term, and target-debt state coordinate statistical fidelity with current deployment service and accumulated under-service.

### 贡献3（50词）

We characterize ideal pooled target-moment recovery under compatible support, correct ratios, sequential identification, and cluster regularity. For anchored convex calibration on shared support with the remaining window state fixed, we establish reference non-expansion of weights and a composition perturbation bound, separating estimation and stabilization errors under positive-mass and bounded-error conditions.

## 3. 挑战—方法—证据对应

- **记录内与更新层的顺序选择 → 参考重构。** 第二段解释机会/观测作用于记录、可用性交付作用于客户端窗口，以及局部归一化与跨客户端质量的区别。其结尾明确要重构local training weights和server reference mass；第四段Specifically句及贡献一给出共享校正量与质量重标定机制。依据III–IV节定义、命题2、附录A-C，以及现有六场景和同支持比较。
- **重构参考与可执行混合之间的缺口 → 窗口校准。** 第三段解释当窗客户端、组组成、cap/有效支持及累计欠服务。其结尾直接落在reference fidelity、feasible group service与cumulative deficits；第四段Furthermore句及贡献二回应。依据V节可行集/P2、定理1、VII-E同支持规则比较与VII-F/附录L/M几何诊断。
- **参考误差如何传播 → 条件性理论刻画。** 第三个贡献分析上述连接的扰动，不另造一个未实现的挑战。非扩张针对共享支持及剩余窗口状态固定的带锚凸程序；组成界与稳定化误差保留。依据命题3与附录A-E/A-H，附录H的经验支持范围仍有限定。

第四段最终四个方法句承担提出、过程、协调特色、对象转换与服务作用；其后只有指定贡献引导句和三项We贡献。已将旧“mass reconstruction becomes an executable decision”改成明确的“turns the reconstructed reference into a feasible client mixture”，补足组对齐目的。没有重新加入独立理论段或实验总结段。

## 4. 引文与范文使用

范文只借鉴四部分功能、第二挑战递进展开及To address/Specifically/Furthermore/In this way模板。未挪用其隐私、激励、模块、数据、独特措辞或引文；贡献仍为三项。

背景5篇：ganti2011mobile；wang2025evolutionary、xu2025rethinking、liu2025nonaligned；mcmahan2017communication，分别支撑场景、补全和联邦更新。

挑战一6篇：wang2024fewshot、liu2025nonaligned支撑补全表示；xie2019asynchronous支撑异步更新；wang2024lightweight、sun2025debiasing支撑参与纠偏；morishita2026who支撑FedIPW的enrollment/participation和population summaries。

挑战二5篇：wang2022unified、chen2026fedcure支撑参与分析/半异步纠偏；wang2024lightweight支撑参与权重估计；morishita2026who、listozec2024overcoming支撑FedIPW与FedPALS的具体能力。保留FedPALS的凸目标标签匹配、sample-ESS及凸包外目标，不把本文交汇处的研究对象扩大为竞品能力否定。

未新增或修改书目条目，现有引用键和段内次序保留；未进行额外文献新颖性认定。

## 5. 八句摘要及主张依据

1. **背景：稀疏分布式观测的补全任务，对应III节问题定义。**

   Mobile crowdsensing completion reconstructs urban and environmental fields from sparse distributed observations to support sensing services.

2. **问题：顺序选择改变代表总体；有限支持/约束使参考未必可执行，对应III-B/D/E、IV-C和V-A。**

   However, sequential selection distorts their represented population, and finite windows can make the corrected reference infeasible under the available support and aggregation constraints.

3. **研究状况：承认已有补全、参与纠偏和目标聚合，正向界定本文连接对象；对应II节及补充表XVI，不声称前作均无校准或ESS。**

   Existing approaches address completion, participation bias, and target-aware aggregation, whereas this setting requires an explicit link between sensing-unit reference reconstruction and constrained window execution.

4. **提出框架：保留既有英文展开，连接感知单元参考与可执行混合，对应IV–V节。**

   To bridge this gap, we propose RAVEN-MCS (Reference Alignment Via Exposure-aware Normalization for Mobile CrowdSensing), an integrated framework that converts reconstructed target references into executable client mixtures.

5. **机制一：机会/观测共享校正量供给本地归一化训练及客户端质量，对应IV-A/B及式(15)–(20)。**

   Specifically, opportunity and observation correction jointly supply normalized local training weights and client reference masses.

6. **机制二：可用性校正形成服务器参考，校准权重而非只匹配参考组成，对应IV-C与V-A/B/C，保留cap、有效支持、参考锚及目标债务。**

   The framework then applies usability correction to form the server reference and calibrates executable weights under caps and effective-support constraints, coordinating reference fidelity, group targets, and accumulated under-service.

7. **理论：正确比率、支持、识别及簇条件下的理想汇总矩恢复；共享固定状态下带锚凸校准的参考非扩张，对应命题2/3及附录A-C/A-E/A-H。**

   Rigorous theoretical analysis validates ideal pooled moment recovery under stated ratio, support, identification, and cluster conditions, and reference non-expansion for anchored convex calibration at a shared fixed window state.

8. **综合证据：City Scanner两套协议的组对齐收益，加上站点同支持比较及几何诊断的机制解释；对应VII-B/E/F、表II/VI和附录H/L/M。**

   Extensive experiments on real-world datasets demonstrate that RAVEN reduces group mismatch by 23.3\%--25.8\% versus TwoStage-H\'ajek in two City Scanner protocols with controlled delivery, while matched-support station comparisons and geometry diagnostics distinguish correction, projection, and adjustment limits.

第8句保持既有结果不变：23.3%–25.8%只是两个City Scanner协议相对TwoStage-Hájek、按seed means比值计算的组失配降幅，不是百分点或预测误差改进。两协议真实机会、其中一个实测观测、全部交付受控的精确定义仍在setup和表II。while分句综合matched-support与支持几何的机制解释，不把SensorScope投影收益转记给完整P2，也不概括U-Air/T-Drive全面优胜。不显著不改成等效，六臂未确立2%非劣的事实保留。

## 6. 前后词数、实际范围与编译验收

采用项目既有归一化计词函数，不作为期刊官方词数。此次基线是最新稿，摘要186→202词，引言612→632词。四段分别66/146/152/107→66/148/159/113词；贡献引导句10词不变，三项贡献43/42/46→44/42/50词（合计131→136）。四个方法句113词，加引导句后第四段123词。旧481/169固定词数及前三段三分之一要求已由本指令覆盖，本轮不恢复这些旧约束。

正文和补充修改前14/14页，最终仍14/14页。现有MiKTeX低优先级、单进程顺序编译，正文/补充互引至aux稳定；最终日志无undefined references/citations、重复label、缺字/缺图、Overfull或编译错误。全部28页已渲染检查，正文1–2页单独放大核对；无新增遮挡、裁切或异常空白。图1仍在第三节/PDF第3页；所有表引用仍在Evaluation及以后，引用继续逐项显示。

实际规范源码仅main.tex的摘要及引言发生文字修改；标题、第一段及第二项贡献等已符合部分保留。Related Work及之后正文文本与本轮备份完全一致；appendix.tex、supplemental.tex、reference.bib逐字节一致。源码数字词元的完整序列一致；正式公式、定理、Proof、算法、label和结果表未变。未重绘图片、调整字体、页边距或间距。

ccf-humanization检查：本轮文本0个em dash，未检出套话或等长句堆叠提示；余下分号密度为advisory，人工核对为已有工作衔接及局部/服务器质量关系。全文剩余等长句提示位于未改的正式定义和统计图注，未为消除提示而改写技术事实。

## 7. 回退入口与未闭合事项

本轮修改前归档：`C:\Cursor\raven.mcs\ccf-review-report\backups\title_contributions_realignment_20261031_204903.zip`。包含原规范源文件、两份PDF、aux/bbl/log，以及`reports/`下上一份同名报告和差异；归档已确认可读且与归档时文件一致。没有覆盖早前归档。

若本轮结束后没有其他改动，仅恢复归档中的main.tex以及需要回退的main.pdf/supplemental.pdf；也可恢复main.tex后按原链编译。supplemental.tex本轮未改，不需恢复。若随后有其他修改，在临时目录解压，根据`C:/Cursor/raven.mcs/tmp/title_realignment_recheck_20261031/main.tex.diff`逐块逆向合并摘要及引言，不用整份旧稿覆盖后续改动。上一份报告可从归档`reports/`读取；实验目录和历史停止状态保持原样。

本轮没有新增需要实验才能解决的主张。此前完整Design质量字段、A5共享状态/A6b经验核验、历史checkpoint保存时点及完整复现包缺口继续保持待核实，未因写作调整而标为解决；见`FINAL_NARRATIVE_POLISHING_REPORT.md`。本轮贡献三仅陈述已证明的条件性性质，不声称这些假设已在所有轨迹上经验成立。实验继续暂停。
