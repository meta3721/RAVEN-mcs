# RAVEN-MCS：模板化与过程性语言检测

日期：2026-11-05。当前main.tex为17:44版本，appendix.tex为17:42版本。使用ccf-humanization的warning-only规则，沿用ccf-paper-reviewer的语言评估方式；只检测，不修改稿件，不判断作者身份，不使用外部AI检测器，不输出AI生成概率。

## 判断

整稿有少量模板化与核验报告式表达，但不足以据此判断“由AI写成”。从阅读观感看，更突出的是高度技术化和多轮压缩后的简略表达，而非泛化套话或空泛宣传。没有必要为降低所谓AI率进行全文改写。保留目前框架和清楚的机制解释，只在必要处修短句与名词堆叠即可。

## 本地规则检查及其限度

分别运行check_prose_quality.py于正文和附录。两者均无error，均没有标出opening_filler、precision_terms、formulaic_structure；正文与附录的prose-only处理结果中em dash均为0。剩余均为uniform_sentence_run和semicolon_density两种信号。该脚本是有限词表与规则扫描，不是训练的作者身份分类器；“未命中”不等于保证没有模板表达。

- 正文有两组近似句长序列，分别涉及系统模型定义，以及City Scanner统计说明/表题。后者跨越正文到table caption，不能当作同一段落语气机械的证据。
- 附录一组序列也跨越结果说明和表题，属于必须人工过滤的结构性提示。
- 分号提示来自处理后的TeX文本（正文100、附录91），尚非按可见自然语言人工标注的标点统计。统计和符号定义中的分隔不能直接视作病句或AI特征。本轮检查中该处理结果未含`\\;`数学间距命令，因此不将本次分号计数归因于该命令。

## 具体观察与处理建议

### H1 摘要/引言指定模板：保留，轻量精修

main.tex:74及105—109使用“However”“Existing approaches”“To bridge this gap”“Specifically”“Rigorous theoretical analysis”“Extensive experiments”，以及“To address the above challenges”“Furthermore”“In this way”。连续读来有一定模板感，但这与导师明确要求的句式一致，不能自动归为写作缺陷，更不是作者身份的证据。

必要调整仅是降低单句信息密度。特别是摘要结尾同时出现收益数字、基线定义、协议范围和诊断结论；不必为去模板改掉指定句首，也不要增加宣传形容词。

### H2 结果尾部有记录式短句：可以局部改

main.tex:1644—1649：“Numerical endpoint and feasibility diagnostics: …”及紧接的“Count-to-Uniform and reference-projection increments are distinct; full P2 coordinates endpoint and runtime trade-offs.”

前一句主要承担导航，却采用“标签+冒号+引用”；后一句紧接抽象总结，连贯性弱。可以在后续文字修改中明确这些诊断检验什么，再接相关发现。本轮不改写。

### H3 少量措辞生硬：可以局部改

main.tex:337—339的“the legal pre-U model”更像程序/约束语境，未立即说明合法性是指何种信息可用条件；后半句关于不得对交付结果条件化的含义是必要的。应明确是使用交付前信息的模型，不删科学限制。

main.tex:1649的“standard-strength debt contribution”压缩了系数设置与结果解释，未来可用明确的预设债务系数说法。不是所有frozen、formal、development都要替换，这些词有时承担有效的协议区分。

### H4 方法与结论存在核心词重复：以清楚为先

reference、target、mass、support、calibration在方法、实验和结论中反复出现，部分名词串偏重，但它们对应不同科学对象。不能为显得自然随意换同义词，否则会破坏术语稳定。main.tex:578—586的本地归一化—质量—服务器参考解释具体而连贯，应保留。

### H5 看起来“防御性”的限定中，很多应保留

main.tex:1077：“CERTIFIED is an operational state, not evidence for exchangeability.” 这是防止把运行状态当作概率假设成立证据的必要说明，保留。

main.tex:1749：“Evaluated oracle configurations are sensitivity references, not predictive optima.” 区分敏感性参考和预测最优性，保留。

main.tex:1753—1758区分正式实验与开发学习、训练预算和更新规则预算，影响证据解释，保留；可以减少重复解释，但不合并不同协议。

main.tex:1784材料仅本地保留的说明属于可获得性事实，保留，不因语气不够积极而删掉。

附录中数学最小值与存储数值解的区分、次线性债务条件和稳定状态假设同样不是无意义免责声明。

### H6 未发现的典型问题

本轮关键词扫描没有发现论文可见叙述使用“we found a flaw”“we revise”“previous version”“internal verification”“approved configuration”“publication-ready method”等内部修订叙事。标签/引用键中的audit不是可见正文用词，不能据此计作AI味。没有发现应为“去AI化”而立即清理的大面积空泛套话。

## 建议

若还做最后一轮，只处理H2—H3及摘要结尾的密度问题，限于几个局部段落；其余优先保留。此判断与此前“无需再全面润色”一致。改写不以外部检测器分数为目标，不删除影响结论的结果、理论假设和协议身份。

范围：全文规则扫描，结合已完成语言审查并核读本轮所有正文命中及关键附录上下文；不是本轮重新逐式验证证明。没有上传外部检测平台，没有修改源文件或编译PDF，没有增加实验或投稿声明。
