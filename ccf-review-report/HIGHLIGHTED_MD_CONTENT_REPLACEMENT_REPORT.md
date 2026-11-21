# 标黄MD引用的实质内容替换

日期：2026-10-18。已直接修改规范`main.tex`，完成正文及补充材料顺序编译。最终均为14页，未改变模板、字号或页边距。使用ccf-paper-writer修订、ccf-humanization检查表述、ccf-integrity-auditor核对证据。

## 标注与当前稿

用户`main-1018.pdf`共14页，与修改前规范PDF逐页提取的正文文本一致，存在第8页一处、第13页两处Highlight。以当前工作树为修改起点，用户标注PDF保留，未覆盖。

## 三处替换

### 1. 第8页：结构比较的预注册路径

原句：`The released w1/ladder_v3/PREREG.md fixes both rules.`

最终位置：正文VII-A3a，标签`subsec:equivalence_band`，第8页右栏，最后两句续至第9页Table II下方。整合原段后直接交代：

- Hindsight在相同活跃集、M及可行域上预知全部窗口，是离线结构参照；保留20种子下3.44/1.32 pp的组TV余量。
- 归一化为`〈Δa−Δb〉/〈ΔUniform−Δ*〉`，分子、分母先在同一批种子上取均值；既有95%成对区间共同重抽分子和分母，不用每种子比值均值。
- 区间完全落入[−.10,+.10]才满足注册实际意义带；removed−full区间完全高于+.10才达到该协议的组件必要性幅度标准。
- 独立组TV实践线为95%下界≥0.5 pp，按论文既有`pp=50Δ`换算，与RMSE百分比和Wilcoxon/Holm显著性分开。
- 无超参数主对比使用全部20种子，调参/报告半集仅检查稳定性，并引用VII-E已有具体结果。

依据：完整读取封装的v3 `PREREG.md`、v4 `PREREG.md`及`PART_A_REPORT.md`；核对`FULL_SEED_DECISIONS.csv`中20种子、`.768 [.563,.970]`、`.286 [.098,.471]`及独立`.922 [.721,1.141]`的现成字段。沿用v4主判定，没有把v3报告半口径套回正文。

**3.44/1.32 pp仅核到已有历史报告级来源。** 已读取封装`W1_PHASE3_REPORT_round_v2.md`，其同支持解释和数值与原文一致；未执行原始最优值复算，未改写`PAPER_NUMBERS.csv`中的UNLOCATED，也未宣称完成独立原始重建。

### 2. 第13页：复现目录名

原句起始：`RAVEN_MCS_PUBLIC_REPRO_R1 contains EventTraces, frozen targets, paired results, and figure/table sources ...`

最终位置：正文第13页右栏“Data and Code Availability”。改为说明**本地保存的复现档案**实际内容：冻结目标、选择配置、事件轨迹、配对结果、图表输入及评分身份；具体包括City Scanner两套原五方法协议、修正后的保存参数同支持权重评分、目标集中度及Adam敏感性记录。保留数据正式引用、City Scanner DOI及CC BY 4.0、T-Drive使用条件。

依据：完整读取封装README和证据索引，逐项确认表中17个packaged路径存在；另核对City Scanner两套汇总和同支持240行评分记录。没有以目录名称代替实质内容，也没有称其已公开下载或已随稿上传。

### 3. 第13页：证据索引MD路径

原句：`... are indexed with relative paths and scoring identities in submission_evidence/SUBMISSION_EVIDENCE_INDEX.md inside the bundle. The index distinguishes packaged records from local-only sources.`

最终位置：与上一处合并成第13页同一自足段落，直接区分六臂档案内已有运行记录、目标地图及注册检验，与档案外的六臂聚合汇总、分析溯源及独立学习/几何记录。

核查发现索引将六臂整组写成local-only不准确：本地封装`w1/gatekeeping/`已有`C1_RUNS.csv`、`C1_A1_CHAINS.csv`、`C1_PRIMARY.json`、`C1_SECONDARY.csv`、`C1_MAPS.json`及注册/执行报告；`C1_ARM_SUMMARY.csv`和`C1_ANALYSIS_PROVENANCE.json`未在该封装中。正文按实际文件分开陈述，**“本地档案已有”不等于“公开上线”或“已随稿附送”**。未改动旧索引、历史报告或原始结果。

共同的新可用性内容为：

> The locally held reproduction archive contains frozen targets, selection configurations, EventTraces, paired results, figure/table inputs, and scoring identities. It includes both five-method City Scanner protocols, corrected saved-parameter scores for the matched-support weight rules, target-concentration results, and Adam sensitivity records. For the separate six-arm target-map comparison, run records, maps, and registered tests are archived; aggregate summaries and analysis provenance remain outside the archive, as do the independent learning and geometry records.

## 实验实质覆盖检查

已完整读取当前`PAPER_CLAIM_EVIDENCE_MAP.md`、`PAPER_EVIDENCE_PENDING_ITEMS.md`，核对底层小型CSV/JSON。以下均已有实质结果，没有重复加表：

- 同支持规则：VII-E/Table VI，48个结构/预测均值单元与修正评分记录的5位小数一致，保留Uniform、投影、Inst-Cal、完整方法和独立κ=1000规则。
- 集中度：VII-F/Table VIII，四级0.0013%/0.0225%/0.0454%/0.0970%及原区间/MDE，核对`TE2_CONCENTRATION_STEP4.json`；仍是所评估oracle配置。
- Adam：VII-G，15种子H=−1.49%、区间[−5.42%,+1.76%]、MDE=5.80%，核对`TE1_ADAM_VERDICT.json`。结构读出取`TS1_STRUCT_SUMMARY.json`，正文保持Δ单位，未机械采用索引该行的pp标签。
- City Scanner：VII-B/Tables II–III保留完整排名、三项结构H1通过、各10/10方向一致及H2非劣未建立，核对两套原汇总与保存的检验链。六臂表没有再次搬运。
- 学习/几何：VII-F、附录K/L及相关表，核对`P1_CENTRAL_SELECTED_R2.csv`、`P2_GEOMETRY_SUMMARY.csv`。47.01%/10.16%/−0.96%仍属于开发骨干；183个K=8和4.651%仍属于独立几何。

## 编译、语言与修改范围验收

- 仅修改`main.tex`的结构判据和可用性两段。其他正文、所有表体、编号数学环境、算法、标签、附录、补充源文件及书目内容与本轮起点一致。没有改参数、协议、种子或结果。
- 使用现有MiKTeX工具链，单进程顺序执行正文→补充→正文→补充，四次均成功；书目及引用键未改，已有两份bbl保持一致，无需重新生成书目。
- 正文14→14页，补充14→14页，均包含各自参考文献。补充逐页提取文本与修改前一致；正文第8—14页因自然重排发生页面文本变化，表号不变。
- 渲染并查看正文第8—14页，判据、City Scanner双协议/六臂表及后续图表无新增超宽、遮挡或异常空白。可用性仍在第13页右栏。现有第8页判据自然续至第9页。
- 最终两份日志无未定义引用、重复标签、overfull或待重跑提示；保留环境原有epstopdf shell-escape提示和MiKTeX更新提示，不影响生成。
- 三个源文件及两份PDF均不再出现此次检查的`.md`、`PREREG`、`SUBMISSION_EVIDENCE_INDEX`、复现目录名。没有把路径转移至附录。
- 新判据/可用性分别约158/100英文词（语言工具排除数学后的口径）；ccf-humanization检查无error/warning，新增破折号为0。仅有分号密度advisory，人工核对其分别连接同一判据或材料范围，保留。

## 尚缺事项与交付

未找到可核验的正式公开发布入口，本轮没有编造URL、DOI、上传状态或“应要求提供”的承诺。索引的六臂可访问性描述与实际封装不一致，报告已按文件列明；未擅改封存记录。公开发布、完整封装及历史报告级余量的原始值复算，均不能由文字替换自动完成。

新增训练=0，模型加载/推理=0，重评分=0，回放/求解=0，新统计检验/bootstrap=0。仅读取已有指标并作确定性一致性核对。实验继续暂停。

交付：[规范源码](C:/Cursor/raven.mcs/TO_OVERLEAF_paper_tmc_r1_clean/main.tex)、[正文PDF](C:/Cursor/raven.mcs/TO_OVERLEAF_paper_tmc_r1_clean/main.pdf)、[补充PDF](C:/Cursor/raven.mcs/TO_OVERLEAF_paper_tmc_r1_clean/supplemental.pdf)。
