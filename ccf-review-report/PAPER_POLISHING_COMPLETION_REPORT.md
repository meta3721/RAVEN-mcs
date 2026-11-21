# PAPER_POLISHING_COMPLETION_REPORT

日期：2026-10-29（Asia/Shanghai）。执行用户指定分步指令，使用ccf-humanization、ccf-paper-writer、ccf-submission-checker。状态分开记录：**定点润色完成；本次最终编译通过；正式提交信息尚不齐全**。没有启动实验。

## 第0步：基线与回退——完成

当前规范四份源码均非空，采用现工作树，没有回退到旧稿。main/supplemental通过xr互读aux并各自生成书目。本轮编辑前串行重建两份PDF，均14页。原有引用修复、City Scanner布局和图一保留。

备份：[stepwise_polish_20261029_212935](C:/Cursor/raven.mcs/TO_OVERLEAF_paper_tmc_r1_clean/revision_backups/stepwise_polish_20261029_212935)。包含三份TeX、reference.bib、两份原PDF及aux/bbl；本轮每份源码差异随备份保存。若没有后续改动可恢复本轮备份后重编译；若已有后续改动，只按差异合并还原本轮段落，不能覆盖用户新编辑。之前所有备份保留。未改Git索引，未reset/clean。

基线记录包括页数、原摘要空格分词169、图表/公式/定理标签编号和实际引用。最终逐标签比较原编号保持一致。图形未编辑，无需另备绘图代码。本轮未恢复上次的0字节故障：当前稿源本来已有效。

## 第1步：主线与保护事实——完成

主线固定为原子R/O/U选择、目标参考重构、窗口支持上的可行校准。内部核对后保留：

- City Scanner两项五方法比较：完整RAVEN平均组失配最低；25.8%/23.3%相对TwoStage-Hájek，按种子均值之比，未重算。真实R、受控U；O一项受控、一项实测。不是两个独立数据集或完整真实部署。
- 六臂比较：十轨迹×每轨迹三模型种子；保留2%预测非劣性未确认及其区间，未写成三十独立轨迹。
- 相同支持的计数→Uniform、Uniform→投影、投影→完整P2分别解释；.768pp与.922pp只从引言去重，原实验结果及区间原位保留，不相加。
- SensorScope完整P2改善客户端—分层对齐、但组失配和运行时不及投影的取舍保留在结果节。预测排序仍随协议变化。
- 理想恢复、固定状态扰动、条件债务与覆盖保证范围分开；Design仍为窗口前配置，Gate仅诊断。

## 第2步：证明格式——完成

[main.tex:692](C:/Cursor/raven.mcs/TO_OVERLEAF_paper_tmc_r1_clean/main.tex:692)及理论节：四处Proof sketch改为正式proof环境，保留原关键论证；三处延后推导明确给出完整证明的Appendix标签指向。债务界的坐标递推、零总质量及正部分论证保留。

[appendix.tex:131](C:/Cursor/raven.mcs/TO_OVERLEAF_paper_tmc_r1_clean/appendix.tex:131)起：正文四项Proposition、两项Theorem均重述原条件、对象、结论，原编号由ref调用，不推进计数器。正文已编号的结论公式通过引用重用，没有新公式编号。债务界另重述初始化、概率组成、非活跃窗口、S_R>0及次线性条件。

对应证明采用proof环境、空心结束框；另规范两个辅助推论的证明结束。保留原正式假设与主文定理原文。覆盖证明压缩了重复的反向推断解释，完整保留随机秩、事件包含、非负截断及历史信息边界；pairwise/drift证明合并重复结论，没有改定理或添加假设。

第一次补充编译遇到IEEEtran中proof内paragraph的prevdepth兼容错误；将该处段标题改为普通段落后修复，下一轮即通过。没有改科学定义或无限重试。此次是呈现与一致性核验，不宣称重新认证全部理论。

## 第3步：图表编号引用——完成

十个指定对象均在结果/机制解释中加入直接引用：Local-Hájek、数值P2、最近邻表、SensorScope完整端点、coverage stress及其图、学习曲线、开发几何、约束敏感性、释放时机表。最近邻比较在Related Work直接指向Table XVI。核验所有保留图表，定义/注释/caption自引不计为正文使用；每组别名label以该对象至少一次有效引用验收。

## 第4步：摘要与引言——完成

[main.tex:71](C:/Cursor/raven.mcs/TO_OVERLEAF_paper_tmc_r1_clean/main.tex:71)：单段组织任务、参考不可执行缺口、两步机制、准确理论范围和City Scanner组对齐证据；25.8%/23.3%、比较对象及协议身份保留。无摘要引用或公式；百分比为普通文本。

[main.tex:159](C:/Cursor/raven.mcs/TO_OVERLEAF_paper_tmc_r1_clean/main.tex:159)：三项编号贡献分别承担“原子目标与选择重构”“可行校准及分析”“应用与机制归因”。引言中的.768/.922和具体SensorScope投影代价去重，实验原处保留。

最终摘要近似167词（空格分词166），引言556词。计数排除图注、数学和引用命令；摘要与原基线169空格词元的差异仅作粗略比较。

创新内容口径：摘要选“Selection correction…”至“In two City…”之前的缺口/方法/理论句，以及最后Matched-support机制句，共103/167≈61.7%；两组City Scanner数字句不计。引言选“An atomic…”到“Existing target-aware…”前的原子选择/对象缺口、We develop起的方法与分析段、三个贡献条目，共367/556≈66.0%。既有工作综述和应用数字罗列不计。这是透明写作分配检查，不是新颖性或期刊评分。

## 第5步：相关工作与方法——完成

保留上一轮所有引用和BibTeX。用“记录内部的选择信息”串联Cafe/DARN与参与层方法，保持其插补/直接预测用途；最近邻比较有明确表指向。F1在方法/结果/图注改为有语义的层内观测异质性实验名称，引用键和正式数学标识保留。常数局部权重的归一化相消解释保留。

P2数值说明改为数值可行性和求解差异的具体指向。更新注册、预先固定目标和时间信息边界中的registered/frozen保留；G5_SOLVER_DIVERGE从学术正文移除，10^-4/10^-3阈值与未重求解事实保留。

## 第6步：实验解释——完成

City Scanner段首明确检验真实机会下的组对齐。六臂段仍先交代支持/形状变化，再报告结构结果与预测区间；其多重性、非劣性及删除代价边界未改。相同支持三类比较的原组织已符合要求，保留所有端点、区间和计数归因。将少量工程状态措辞改为saved model parameters/pre-specified等具体身份。

Obs/Use、Debt、投影数值精度、U-Air反向变化、oracle局限、覆盖候选身份和释放时机代价均保留；没有将不显著改为等效或将结构改进写成预测改进。已充分组织的结果不为“润色”再重写。

## 第7步：图表说明与结论——完成；密表可读性保留待办

图一仅缩短caption中的重复解释，图PDF/PNG及绘图源码完全未编辑。Table IV/V缩短重复Window方法后缀并在caption明确对应，未改方法身份。Table II/III仍跨栏，Table II/III/VI未移出正文。表内全部数值逐项一致；误差线、统计单位、比较方向不变。

Table VIII、补充Table XVIII仍较密，本轮没有继续缩字号或重绘。已记录，不能把“未发现裁切”当成小字密度已完全解决。

[main.tex:1812](C:/Cursor/raven.mcs/TO_OVERLEAF_paper_tmc_r1_clean/main.tex:1812)：结论以参考—可行混合和两个City Scanner组对齐结果收束，合并重复的具体SensorScope取舍；该事实留在实验节。保留固定状态/长期条件及预测排序依协议变化。

## 第8步：提交说明和篇幅——可执行修改完成，正式提交材料部分未闭合

补充首页移除上传操作指令，保留伴随论文身份。Data and Code Availability保留公共数据来源与许可证，改为与核验范围相称的本地材料说明，没有虚构公开入口或完整复现承诺。

实际发现：RAVEN_MCS_PUBLIC_REPRO_R1/README.md与BUNDLE_SUMMARY.json均0字节；MANIFEST.csv非空，且其BUNDLE_SUMMARY登记大小811字节与当前0不符。submission_evidence/SUBMISSION_EVIDENCE_INDEX.md可读，但含旧表号，不能直接充当当前完整包验收。

轻量检查确认CS_E3_SUMMARY.csv（601字节）、JO_E3_SUMMARY.csv（646字节）、W1_TRADEOFF_V51.csv（54413字节）存在且非空；未据此声称全部主表/模型/评分输入齐全。索引将六臂汇总、学习与几何列为local-only，与旧稿“六臂已归档”的泛述存在覆盖口径差异，故只收窄可用性声明，不修包、不复制大资产、不覆盖历史材料。

作者仍含****、***及占位邮箱，未猜填；标题未换；未编造简介或公共链接。正式提交前需作者提供真实资料、核定包目录/可获取入口及适用规则。本轮没有修复空README或把其缺失写成数据结论不成立。

篇幅：添加重述后补充曾15页；通过精简重复证明解释、重复符号介绍与诊断说明恢复14页。正文/补充最终14/14，无模板、基础字号、页边距、行距或负间距修改。

## 第9步：最终验收——通过本轮文稿检查，未签发全面投稿合规

- 最终顺序构建8次调用均退出0，main/supplemental的aux稳定，分别14页。两份PDF均来自本轮最终源码及BibTeX输出。
- 无未定义引用、重复标签或Overfull警告；已有epstopdf“shell escape关闭”提醒不影响现用PDF/PNG。Underfull结合逐页观察，不当作自动内容错误。
- 正文4图8表、补充4图25表、主文4命题2定理、主文41个编号公式及后续编号保持；所有原有label对应数字不变。表格数值及主文/附录编号公式逐块核对相同；主文正式命题/定理/假设原文相同；算法与约束未更改。
- 实际引用键与基线集合一致：正文46个来源，2025=15（正式），2026=7（6正式+1预印本）；补充5个、2025=0/2026=2，并集46。数量通过；cite nocompress保留，未检出压缩引用区间。
- 全部28页渲染目视检查：标题/作者占位、证明/结束框、跨栏表、图注、书目、末页均已查看，未发现裁切、遮挡或悬空图例。小表密度问题如第7步记录，不虚报完全消除。
- 实际绘制字体均嵌入：正文38种、补充39种。资源字典另有一个未绘制的Helvetica基础字体；内容流未使用它，不能将资源枚举误报为可见文字缺失嵌入。图一未因此被改写。
- 已运行指定check_prose_quality.py：两稿em dash均0。正文有一个5句近似长度提示，涉及注册/可用/正质量集合及group/stratum职责定义，人工核对后保留其独立科学含义；分号密度为提示，含公式和技术并列，不机械改写。没有将脚本当AI检测器或消除所有提示的目标。
- IEEE CS官方作者资源2026-10-29检索内容支持regular摘要100–200词：[官方作者指南](https://www.computer.org/publications/author-resources)。TMC专属当前页数/费用/身份规则未独立核准；14页是项目约束，不宣称所有投稿规则已满足。当地技能目录无已核TMC专属指南，不套用其他会议规则。

## 回退与核验记录

本次修改限main.tex、appendix.tex、supplemental.tex及其编译产物；reference.bib按字节保持，实验资产/配置/脚本未改。备份保存关键原文件和每份源码diff；本轮记录在tmp/polish_20261029/（baseline.json、FINAL_QA.json、FONT_USAGE.json、构建日志、逐页预览）。不新增通用校验和材料。

关键前后对照：[PAPER_POLISHING_DIFF.md](C:/Cursor/raven.mcs/ccf-review-report/PAPER_POLISHING_DIFF.md)。剩余事项是提交身份、复现包覆盖/空文件及小表可读性，不是自动启动新实验的理由。
