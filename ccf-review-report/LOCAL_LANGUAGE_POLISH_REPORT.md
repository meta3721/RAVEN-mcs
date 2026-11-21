# RAVEN-MCS 局部英文细节润色记录

日期：2026-11-05。主技能：ccf-paper-writer，polish模式；辅助：ccf-humanization。依据当前规范稿及用户提供的 paper-language-review.md，先读上下文，再做局部修改。没有章节重构、新增文献或实验。

## 交付与范围

已就地修改 [main.tex](../TO_OVERLEAF_paper_tmc_r1_clean/main.tex)、[appendix.tex](../TO_OVERLEAF_paper_tmc_r1_clean/appendix.tex)，并编译 [正文PDF](../TO_OVERLEAF_paper_tmc_r1_clean/main.pdf)、[补充PDF](../TO_OVERLEAF_paper_tmc_r1_clean/supplemental.pdf)。两份均为14页（含参考文献），与修改前相同。其他用户改动没有回退。

- 方法/理论：明确 R 指标的复数主语；明确零和的是累计有符号欠服务向量，保留债务界及次线性增长条件。IV-C本地归一化—客户端质量—服务器参考解释与V-C组成映射解释原样保留。
- Evaluation：展开多重斜杠数字配对，明确指标、数据集和对照；保留比例均值与配对相对变化的区别、全部关键有利/不利结果、描述性容差、正式非劣性和各统计家族。不把投影或调节债务规则的结果转给完整RAVEN。
- 摘要、引言、相关工作：八句摘要及全部原句首保持；同一英文词数口径由203词变为211词（约+3.9%，英文词、连字符词算一词，去除引用命令）。引言仍为四段安排和三条以We开头的编号贡献，没有引入图表、数字或新贡献。相关工作只改局部衔接，保留FedIPW/FedPALS等近邻能力、引用及顺序。
- 术语与附录：Uniform称为structural benchmark；readouts改为具体group mismatch指标；practical line改为预设实际意义阈值；明确原frozen-strength固定的是债务系数。没有猜填该系数的新数值。数值检查、理论唯一解和最优性认证仍分开。

## 关键原句—改后句—理由

### 1. 指标主语

原：The realized $R_{k,r,i}$ record events from this process, not mutually independent Bernoulli draws.

改：The realized indicators $R_{k,r,i}$ record events from this process; they are not mutually independent Bernoulli draws.

理由：明确主语是指标集合；不增加独立性假设。

### 2. 欠服务界指代

原：Zero total mass makes its $\ell_1$ norm twice its positive mass.

改：The signed under-service vector sums to zero, so its $\ell_1$ norm equals twice its positive mass.

理由：排除将its读成非负债务向量的可能；公式与附录推导不变。

### 3. 引言重复挑战句

原：The challenge is to reconstruct local training weights and server reference mass for the same sensing-unit target, using only the information available before each selection outcome.

改：Local training weights and server reference mass must therefore represent the same sensing-unit target using information available before each selection outcome.

理由：第二段聚焦统一目标参考；第三段聚焦有限窗口执行，删去重复任务归纳。

### 4. 采样层级

原：usability is drawn once/client-window

改：usability is sampled once per client in each window

理由：完整说明每客户端、每窗口的一次随机采样。

### 5. City Scanner预测对照

原：RAVEN's paired RMSE improves on FedAU/ObsUse by $1.71\%/1.34\%$, with worst-group reductions of $1.56\%/1.23\%$.

改：RAVEN reduces paired RMSE by $1.71\%$ relative to FedAU and $1.34\%$ relative to ObsUse; the corresponding worst-group RMSE reductions are $1.56\%$ and $1.23\%$, respectively.

理由：就近给出两个比较对象及两个指标；保留FedAvg预测领先和RAVEN的5.59%代价。

### 6. 投影实际意义

原：The $.5$ pp practical line is cleared stably only on SensorScope; U-Air changes from $.170$ on tuning seeds to $.402$ on report seeds.

改：Only SensorScope consistently meets the pre-specified $.5$ pp practical threshold; U-Air's improvement is $.170$ pp on tuning seeds and $.402$ pp on report seeds.

理由：明确阈值身份、单位和分半稳定性；没有将统计显著替代实际意义。

### 7. Inst消融

原：Inst contributes on specific structural and prediction endpoints: its removal worsens SensorScope client--stratum mismatch by $.310\%$ and U-Air RMSE/tail by $.143\%/ .149\%$.

改：The Inst ablation removes instantaneous calibration, whereas Inst-Cal removes debt. Removing instantaneous calibration worsens SensorScope client--stratum mismatch by $.310\%$. On U-Air it worsens RMSE by $.143\%$ and tail RMSE by $.149\%$.

理由：明确被移除组件及U-Air两个指标；原Holm p值和结构不显著结论保留。

### 8. Debt消融

原：Debt's significant structural effects are $.0141\%/.0040\%$ on SensorScope and $.0043\%/.0024\%$ on U-Air.

改：Removing Debt significantly increases group and client--stratum mismatch by $.0141\%$ and $.0040\%$ on SensorScope, and by $.0043\%$ and $.0024\%$ on U-Air, respectively.

理由：明确完整方法为分母、移除方向、指标顺序和数据集；随后仍说明效应在实际意义带内。

### 9. 附录数值检查

原：the experimental audit reconstructs whether logged allocations satisfy the P2 constraints whenever the necessary state is available

改：Numerical checks test stored allocations against P2 constraints where the required state is logged.

理由：直接说明数值检查对象和所需日志状态；求解器警告、可行性与未获最优性证书均保留。

### 10. 附录开发更新

原：First-cycle development payloads retain their correction settings.

改：Initial development updates retain their correction settings.

理由：用实际研究对象代替内部载荷表述，保持开发协议身份。

## 核验结果

1. 对本轮备份逐文件比较：正文和附录的所有数值词元及其出现次数不变（因斜杠展开允许顺序调整）；全部32个表格、所有图形环境、equation/align、算法和定理环境内容不变。引用键、label、附录导航调用与章节/RQ顺序不变。定理外的证明说明仅澄清原有对象，没有新增数学结论。
2. supplemental.tex、appendix-navigation.tex、reference.bib的文本未变，两份bbl内容未变；现有图形与figure_data文件未修改。未改变方法实现、参数、阈值、支持集、统计检验或实验记录。
3. 顺序执行正文LaTeX、补充LaTeX、两份BibTeX，再交替编译两轮；最后8条命令全部成功，aux稳定。最终没有Overfull、缺字、字体警告、未定义引用/文献、重复label/destination或PDF字符串警告。日志仍有窄栏数学、表格及部分段落的Underfull提示；已结合最终页面检查，不宣称日志零提示。epstopdf的禁用shell-escape提示沿用现有工具链，不影响现成PDF图片。
4. 两份PDF全部字体嵌入，无Type 3。渲染全部28页并逐页联系图检查，重点复看正文第5页的证明和第11页的结果段；未发现新增裁切、重叠、缺字、图例丢失或异常空白。图1仍在系统模型部分、PDF第3页。
5. 35个原正文附录目标及所有原label的编号值保持；书签和内部/跨文件链接的精确PDF目的地解析通过。此项为结构回归检查，本轮未重新进行阅读器实点验证，不扩大上轮跨PDF可用性结论。
6. 运行check_prose_quality.py前后检查：两份源文件均无硬错误，新增润色无em dash。剩余提示为句长节奏和分号密度；正文系统模型的并列定义以及图表说明具有技术用途，附录提示还跨入表格。已人工审读，未为降低计数机械改写定义或表题，也未将辅助脚本的词数当作纯正文词数。

## 需单列的问题与回退

没有发现必须改变数学含义、实验解释或主张强度才能解决的新语言冲突。既有预测基线、P2各项必要性和未闭合证据问题不由本轮润色重新判定，仍按原有范围保留；没有新增保证。

原版本保存在 [language_polish_20261105_173149.zip](backups/language_polish_20261105_173149.zip)，修改前已验证每个备份条目可读并与实际文件逐字节一致，包含当时的源码、两份PDF、aux和书目输出。该备份没有覆盖旧导航备份。

完整本轮差异：[LOCAL_LANGUAGE_POLISH_DIFF.md](LOCAL_LANGUAGE_POLISH_DIFF.md)。恢复时仅逆向合并本轮main.tex及appendix.tex的语言差异，然后交替重编译；若已有后续工作，不直接用旧整份源码覆盖。恢复当时PDF可从ZIP提取两份原PDF；aux需与对应源码重建，不混用旧新编号。

构建命令、源码断言、前后语言脚本结果、字体与链接核验、最终28页预览保存在 [本轮核验目录](../tmp/language_polish_20261105/)。报告和完整差异为Markdown；规范源码及PDF仍在原论文目录。实验保持暂停。
