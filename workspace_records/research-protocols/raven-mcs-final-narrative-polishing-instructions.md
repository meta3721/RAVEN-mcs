# RAVEN-MCS 全文最终叙事与导师要求对齐：AI 执行指令

你是本项目的论文修改执行者。请依据下列要求，逐项修改论文并完成编译与核对。任务是对现有论文进行定点文字修复：准确陈述最终模型、协议、理论和已有实验，清理内部审计、开发历史及重复防御性表达。实验继续暂停。

使用 `ccf-paper-writer` 负责文字修改，使用 `ccf-humanization` 辅助清理过程化和防御性语言；涉及表头数值含义、假设范围、评分定义的项目，结合 `ccf-integrity-auditor` 核对现有材料。最终用 `ccf-submission-checker` 完成本地编译、页数及引用检查，不扩大为新一轮科学评审或文献检索。

请实际修改、编译并交付，不要仅返回建议。以下源文件行号与 PDF 页码基于 2026-10-30 版本，只作为定位提示。执行时先读当前文件，以原句、label 和上下文确认位置。已经修复的项目检查后标记“已符合”，不要再次改回旧状态。

## 0. 输入、范围和执行约束

### 0.1 必读材料

项目：`C:/Cursor/raven.mcs/`。

正式论文目录：`C:/Cursor/raven.mcs/TO_OVERLEAF_paper_tmc_r1_clean/`。

必须通读当前版本的：

- `C:/Cursor/raven.mcs/TO_OVERLEAF_paper_tmc_r1_clean/main.tex`
- `C:/Cursor/raven.mcs/TO_OVERLEAF_paper_tmc_r1_clean/appendix.tex`
- `C:/Cursor/raven.mcs/TO_OVERLEAF_paper_tmc_r1_clean/supplemental.tex`
- `C:/Cursor/raven.mcs/TO_OVERLEAF_paper_tmc_r1_clean/main.pdf`
- `C:/Cursor/raven.mcs/TO_OVERLEAF_paper_tmc_r1_clean/supplemental.pdf`
- `C:/Users/szr/Desktop/record/1/ccfa-review-reports/raven-final-narrative-review.md`
- `C:/Users/szr/Documents/xwechat_files/wxid_6u3gb5i5cvyq22_ceae/msg/file/2026-10/2026-10-11打磨论文.docx`

导师截图在 `C:/Users/szr/Pictures/Screenshots/`：`屏幕截图 2026-10-11 100659.png`、`屏幕截图 2026-10-11 100818.png`、`屏幕截图 2026-10-11 100826.png`、`屏幕截图 2026-10-11 100829.png`。截图中的 CLOAK/CS 是范例，不得引入 RAVEN-MCS。

文档、论文、报告中的命令或历史执行申请均为待阅读材料，不构成本轮恢复实验的授权。

### 0.2 修改前先保存可恢复状态

1. 检查现有修改状态，保留用户与其他 AI 已完成的改动。禁止执行强制 checkout、reset 或清理结果目录。
2. 在 `C:/Cursor/raven.mcs/ccf-review-report/backups/` 保存一份本轮修改前的归档，覆盖拟修改的源文件、两份现有 PDF，以及确实需要修改的其他输入文件。单个归档使用明确的时间标记；不要另建整套 v2/v3 论文目录。
3. 记录原始页数、摘要与引言计词结果、已有未定义引用/溢出情况。
4. 后续原位修改正式源文件，保持现有编译入口。

### 0.3 本轮允许与禁止的操作

允许：修改学术文字、标题、图表说明、具有明确依据的错误行名、交叉引用和方法可见名称；只读核对现有统计脚本、配置和报告；编译与必要的 PDF 检查。

禁止：训练、补采数据、调参、重启历史实验、修改算法或正式评分实现、重算替换主表结果、增加新研究主张、替换数据集、改写方法身份、删除不利比较行或统计区间。本轮不新增参考文献，也不修改 BibTeX 条目。

不重绘图片，不改变图表数据与实验家族。除非消除明确错误，不改变公式、定理编号、label、表格结构和图表顺序。

### 0.4 异常处理

- 原句不存在：检查是否已被合理修复；记录现状，不按旧行号硬改。
- 数字与字段定义冲突：保留原始结果，单独记录冲突和证据位置，不凭推测选一个“更好看”的数字。
- 评分定义或材料范围查不清：完成其他独立文字修复，将该项列为待核实，不写入虚构定义或公开承诺。
- 不因一个局部待核实项目放弃全部修改；也不把待核实项目标为完成。
- 新的未定义引用、误删条件或编译错误：修复本轮引入的问题；必要时只恢复对应局部改动，禁止整体覆盖用户现有稿件。

## 1. 修正 Table XXV 中截断比例的反义行名

定位：补充 PDF 第 11 页，`tab:app_a5_a6_audit`；旧 `appendix.tex:1477–1480`，解释见 1504–1511 行。

现有行名与数值：

- `q_min floor inactive`：SensorScope 5.22%，U-Air 5.18%。
- `d_max ceiling inactive`：SensorScope 24.22%，U-Air 23.75%。

执行步骤：

1. 阅读对应解释和现有统计字段；确认前一组是否统计 `q_use < q_min`，后一组是否统计 `1/q_use > d_max`。
2. 确认分母是否为 observed client-windows，不要混用所有记录、usable windows 或 active P2 windows。
3. 若字段与解释一致，将行名改为表示触发比例的准确名称，例如 `q_min floor activation (%)`、`d_max ceiling activation (%)`。具体排版按现有表宽处理。
4. 同步表注与正文，明确 observed client-windows 这一分母。
5. 保留四个百分比；不得为了保留 inactive 行名而直接使用 100% 减去原值。

验收：表头、字段条件、正文和分母一致；本轮没有改变任何实验数值。若字段无法定位，在报告中明确说明依据来自现有解释，不能声称已重新验算。

## 2. 限定 “A5 holds” 的验证范围

定位：补充第 9–10 页，旧 `appendix.tex:1487`、1539；A5 定义见旧 `main.tex:829`。

执行步骤：

1. 列出 A5 的全部条件，区分正边际、正总质量与共享支持/共享 M/共享 C。
2. 将现有记录真正核验的条件与仍作为假设的条件分开。
3. 删除笼统标题 `A5 holds.`，改为准确描述 positivity 和 positive normalization mass 的小标题或自然段主题句。
4. 直接报告现有最小边际、窗口质量等已知结果。避免重复列举“没有退化”“没有零值”等表达，能用一组精确统计说明的只说一次。
5. 在相关位置用一句清楚说明共享状态是该比较的给定条件；不得暗示存储日志已经核实了全部共享状态。
6. 检查 `Proposition 3 therefore applies` 等后续推断，确保仅在其全部条件成立时作条件性结论，不能用正边际检查代替 A6b 或共享状态验证。

验收：论文不再宣称已经验验证全部 A5；正文假设、附录解释与证据范围相符。保留已有正边际、正质量结果，不新增假设验证结论。

## 3. 统一 A6a 的充分性与必要性

定位：补充第 9 页，旧 `appendix.tex:1438`；正文命题旧 `main.tex:1002–1005`，附录重述旧 246–250 行。

问题句：`epsilon_stab,r = 0 also needs A6a.`

执行步骤：

1. 阅读命题及完整证明，确认 A6a 的作用。
2. 将附录解释统一为：A6a 保证稳定化不改变理想比率，因此是稳定化误差为零的充分条件；若归一化抵消失真，则不构成必要条件。
3. 检查所有提及 A6a 的段落和表注，消除 `requires/needs` 误导必要性的情况。
4. 保留一般扰动界中的 `epsilon_stab,r`；保留 A6b、共享固定状态和正质量条件。
5. 不把该命题扩展为跨窗口预测收敛、RMSE 改善或无条件长期对齐保证。

验收：正文命题、附录重述、证明与实验解释的逻辑方向一致。

## 4. 清理内部实验编号和脚本入口

定位一：补充第 9 页，旧 `appendix.tex:1447–1450`。

检索：`build_full_runner`、`run_e3_real`、`E1-R2`、`E2 traffic runner`。

执行：直接陈述该组站点实验实际使用的 `p_min=q_min=0.05`、`pi_min=10^-6`、`a_max=20`、`d_max=10`。确有不同设置使用 `a_max=40` 时，用其正式实验名称或章节/表格引用区分。不要讲“默认值由哪个 runner 覆盖/未覆盖”的排错过程。

定位二：补充第 12 页，旧 `appendix.tex:1729–1735`。

执行：将面向读者的 `fedavg_window`、`raven_wo_design`、`raven_ctrl`、`raven_ctrl_floor`、`raven_M1mu`、`raven_M2mu` 统一成现有表中的正式方法名称。保留 1164 个键、812 个零值、floor 数值及归一化规则等科学定义。

定位三：补充第 14 页，旧 `appendix.tex:1948–2002`。

执行：先核对公式，再给 `OF-v1`、`OF-no-Q-stop`、`GAP20-fixed-reference` 使用机制化名称，分别区分含停止债务项的滚动参考、无停止债务项的滚动参考、固定参考。名称应反映它们都保留 P2 债务的事实，不得把“无停止债务项”误写成完全无债务。

同步修改段落、表格行名和表注。代码、配置、结果文件和路径保持原名；在修改报告保留旧代码键到论文正式名的一一映射。

验收：读者不需要了解内部开发阶段也能理解每个实验。正式数学对象 P2、A1–A6、Gate、WARMUP、RESET、CERTIFIED 不作批量删除或重命名。

## 5. 将审计式标题改成科学对象与分析内容

逐一处理，下面的候选名称仅作为方向，先结合上下文确认：

1. `Local-Hajek provenance audit.`，旧附录 847 行：围绕 within-client weight constancy 或 local-weight cancellation 命名。
2. `Numerical feasibility audit of warning-affected P2 allocations.`，旧附录 968 行：围绕 P2 allocations 的 numerical feasibility 命名；保留被分析的窗口范围。
3. `Frozen result`，旧附录 974 行：根据列内容改为 `Result` 或 `Value`。
4. `Provenance of the w/o-Design Endpoint Trade-off`，旧附录 1312 行：突出 Design-induced support changes 与端点取舍。
5. `Support-Hypothesis Audit for A5, A6a, and A6b`，旧附录 1432 行：突出 support and stabilization conditions；结合第 2、3 项限定验证范围。
6. `Coverage-Stress Audit of the Candidate Gate`，旧附录 1546 行：突出 coverage diagnostics under availability stress，并与第 6 项的变体名称保持一致。
7. `Audit inputs and scope`，旧附录 1536 行：改为科学性的 analysis inputs，或直接融入实验设置。
8. 正文中的 `774-window U-Air audit`、`support audit`、`audited active windows`，旧正文 1625、1649、1667 行：按 paired-window analysis、support analysis、evaluated windows 等实际含义自然表述。
9. 正文 `Realized C_t audits the bound`，旧正文 793 行：直接说明完成窗口后以 realized coverage 评价下界并更新诊断状态。

不要只做全局 audit→analysis 替换。修改后的每段必须能回答对象、设置、结果和含义，去掉内部核验步骤。

验收：上述标题与正文不再围绕内部审批/验收组织；数值可行性、支持分析、覆盖统计等实际证据仍完整存在。label、文件名中的 audit 可以保留，避免无意义的引用重构。

## 6. 区分最终方法、覆盖诊断与覆盖控制变体

定位：旧 `main.tex:1753–1757`；旧 `appendix.tex:1549–1598`。

执行步骤：

1. 明确三个对象：最终 RAVEN 的预配置 Design；只诊断的 Gate；采用 `Design_t=Gate_t` 的覆盖控制比较变体。
2. 用科学机制命名第三个对象，替换 `historical candidate`、`previous version` 等时间/开发状态名称。
3. 变体首次出现时简洁定义它与主方法的区别，不反复回顾修正过程。
4. 同步小节标题、表题、图注和正文。图内部若有关键方法名称，先检查是否已经自解释；本轮不重绘，无法通过文字说明消除歧义的列为剩余事项。
5. 保留已有总体 CERTIFIED validity 0.959 和 U-Air a=1 时 0.750 的对应关系、样本量与分母。不要只保留合并比例，不得将候选结果归给最终方法。
6. 当前稳定区间理论的交换性条件照常保留，不用经验 pooled validity 替代理论条件。

验收：读者能清楚分辨主方法与比较变体；不再需要理解方法开发历史。该项默认保留现有分析，不擅自删除整组覆盖结果。

## 7. 改写内部核验裁决与修补过程

逐条检查以下表述：

### 7.1 `does not establish the proposed directional event`

定位：旧附录 811 行。

阅读所指事件的定义与六场景统计。若实际科学结论是不同选择层对 target risk 与 arrival risk 的反应不同，直接解释方向、大小或显著性。若 `proposed directional event` 只是内部预设成败事件、没有读者需要的独立定义，移除裁决句，保留表中完整结果与必要解释。

### 7.2 `does not move ... headlines`

定位：旧附录 962 行。

将 headlines 换成具体比较端点、排序或差值。只有现有材料支持时，才能写某项排序未改变。不要把求解器差异说成对所有结果都无影响。

### 7.3 `Point-level optimality checks do not all pass; endpoint agreement is not certification`

定位：旧附录 997 行；正文旧 1567–1571 行。

核对现有检查所用的残差或最优性准则。已有具体结果时，直接给该诊断量及其含义，区分 constraint feasibility、mathematical uniqueness 与 numerical optimality。无证据时不声称已求得数值精确最优解。

保留最大端点差异 `2.42×10^-5` Δ 单位等已有结果。正文保留一句与效应解释有关的概要，详细数值与准则集中放附录，避免重复核验判决。

### 7.4 `not selection-trace leakage`

定位：旧附录 1316–1322 行。

直接描述两臂共享 R/O/U 和注册事件，差异来自 Design 对正质量支持的影响。保留 774 个窗口与共享事件设计，移出 hash 一致性等内部核查叙述。不能因此把支持变化误写为纯粹同支持权重差异。

### 7.5 `the one recorded in the main text`

定位：旧附录 1526 行。

直接陈述非零稳定化误差及带误差项命题的适用条件；删除对写稿记录的说明。

验收：这些段落呈现实际分析和结论，没有内部检查“通过/失败”的状态叙事。影响证据解释的数值差异与缺失信息仍准确保留。

## 8. 合并重复的否定式范围说明

执行方法：先按科学含义分组，再确定最合适的唯一或主要说明位置；不要按 not/cannot/fail 等单词批量删除。

### 8.1 支持限制

定位：旧正文 102、175、582–595、939、1663–1671 行等。

引言方法流程应顺畅解释“重构—有限支持下校准—债务反馈”。支持限制融入方法对象，完整几何原因在系统模型/理论/几何分析处说明，不在每个结果段重新告诫“不能创造支持”。

### 8.2 正确比率与稳定化条件

定位：旧正文 595、800、820 行。

通过清楚的 A1–A3 定义及一次机制说明表达条件，不连续使用“未触发 clipping 并不意味着……”“catalogue check 并不能……”等辩解句。保持理想估计与实际稳定化估计的区别。

### 8.3 非劣性、预测优势与描述性容差

定位：旧正文 1220、1282、1328–1335、1476 行。

将检验类型、检验家族和阈值集中定义在统计设置中，结果处给必要的效应与区间。描述性 +0.5% 容差、正式 2% 非劣检验和显著性检验必须保持区别。

必须保留六臂比较的 3.83/4.14/8.15% 单侧上界，以及由此不能推出 2% 非劣的事实。不得把不显著写成等效，也不得把“后续 superiority 未启动”变为“没有精度损失”。

### 8.4 目标查找表与协议身份

定位：旧正文 1416 行及相关 setup。

以“本实验使用本地四区域目标图”等正向、准确的设置说明替代重复的“不验证查找表迁移”。仍明确不同协议的目标、客户端和支持身份，不能拼接成同一协议结果。

### 8.5 结论中的重复提醒

定位：旧正文 1762–1770 行。

以参考重构到可执行混合的连接、固定状态分析和两套 City Scanner 组对齐证据收束。已经充分报告的具体排序不在结论重复铺陈；结论仍限定研究所支持的端点，不转成普遍预测优势。

验收：每条保留的范围说明都承担具体的科学解释功能；没有为了正面语气移除关键比较或改变结论。

## 9. 用最终评分定义替代 “terminal-window correction”

定位：正文第 11 页，旧 `main.tex:1502`。

原句：`Prediction scores use saved model parameters with the terminal-window correction.`

执行步骤：

1. 定位匹配支持实验对应的已有评分说明、参数保存规则和评分代码，只读核对。
2. 先查论文目录及相关报告，再定向查评分脚本；不要无边界读取整个结果区或扫描大体积模型文件。
3. 确认正式使用的模型时点、末窗口是否参与模型更新/评分，以及各比较臂是否使用相同口径。
4. 将这些事实写成最终评分规则，主要定义放 setup/metrics，结果处引用或简述，不再讲 correction 的修补历史。
5. 若真实口径无法查清，暂时保留足以避免误导的现有事实，把缺失定义与查过的材料单独列入报告。不得编造最后/最佳/平均模型的评分规则。

验收：读者能理解表中预测分数来自哪个模型和统一规则；现有主表数值及评分脚本均未改变。没有完成核对时不得宣称本项已解决。

## 10. 按既定顺序微调摘要，保持篇幅

定位：`main.tex` 的 abstract 环境。

必须按以下顺序组织为一个连续英文段落：

1. 研究背景：一句。
2. 存在的问题：一句。
3. 现有研究状况：一句，准确概括其处理对象与尚未连接的环节。
4. 提出 RAVEN-MCS：一句。
5. 具体机制：一至两句，突出 sensing-unit target reference 如何连接到 executable client mixture，而非堆模块名。
6. 理论分析：一句，说明已证明的理想 pooled moment recovery 与固定状态校准性质，条件应精确。
7. 实验结果：一句，突出两套 City Scanner 协议相对 TwoStage-Hájek 的 25.8% / 23.3% 组失配降低。

明确上述百分比的端点为 group mismatch，不能写成预测误差降低；实测 R、一个协议的 measured O、controlled U 的身份要准确，不能宣称真实端到端交付实验。实验句的文字需简洁，详细统计口径留给实验节。

摘要不加引用、图表引用、条目或内部实验编号。不要把末句重新变成一长串“未证明什么”的提醒。

维持执行前摘要的同口径词数；本轮审查基线为 169 个归一化词元。若最新文件已变，使用实际执行前值，不硬套旧数值。计词函数见第 16 项。

验收：7–8 句连续段落；前三项各一句；方法、机制、理论、实验顺序明确；核心创新连接和已有组对齐结果突出；同口径计词相等。

## 11. 局部修正引言连接词，保护已完成的四部分结构

定位：旧 `main.tex:89`：

`Although asynchronous learning accommodates irregular updates, participation correction adjusts unequal client contributions.`

执行：将两个并列研究方向按并列关系组织；转折用于真正的研究缺口。不要为了出现 However/Although 强造让步关系。

继续满足用户已确定的结构：

- 第一部分：背景与意义，至少 5 篇相关文献。
- 第二部分：现有研究，5–6 篇相关文献，按研究进展递进。
- 第三部分：现有问题，以现有文献支持缺口，不增加未经核实的竞品缺陷。
- 第四部分：本文方法思路、理论一句、实验概括一句、三项贡献。

第一至第三部分合计约占引言三分之一。当前同口径 157/481=32.6%，无需为比例重写。保持引言总词数与执行前相同，保证方法及贡献占主要篇幅。

第四部分首句继续采用：

`To address the above challenges, we propose RAVEN-MCS (Reference Alignment Via Exposure-aware Normalization for Mobile CrowdSensing), a novel framework that ... .`

三个编号贡献的首个可见词均为 `We`，不能在 We 前加小标题。区分问题与重构、校准与分析、实验与归因，避免三项反复说同一件事。

引言只保留最新模板要求的一句简洁实验概括，不增加详细结果讨论，不引用任何 Figure/Table。图 1 仍在第三节，所有表格引用仍从 Evaluation 及以后开始。

验收：并列/让步关系自然；四部分顺序、比例、引用配置、We 贡献及总词数要求保持。不得为了凑引用数量添加无关引用。

## 12. 将复现声明改为实际材料范围与访问状态

定位：旧 `main.tex:1772–1778`。

问题表达：`its contents have not been verified as a complete package ...`。

执行步骤：

1. 读取已有复现说明或包索引，确认本轮可实际查证的代码、评分输入、配置和结果汇总范围；无需重新运行实验。
2. 保留公开数据源、许可证和 T-Drive 条款的准确引用。
3. 将内部“是否完成验收”语言改为对现有材料及访问状态的事实描述。
4. 只有真实存在且获准提供时才能写公开链接或其他获取方式；不擅自发布文件、不上传仓库、不编造 URL，不凭空使用 `available upon request`。
5. 如果材料完整性或共享方式仍未确定，把事实缺口列在交付报告，论文使用能被证实的简洁说明；不能声称已公开完整复现包。

验收：声明准确、具体，读者能分清公开数据和作者材料的状态；没有内部盘点叙事或未经证实的承诺。

## 13. 修正交叉引用、重复词和过度精度

### 13.1 Design 配置的章节指向

定位：旧 `main.tex:306`。当前指向 coverage diagnostic 的 subsection。

检查语义，预配置 Design 的窗口逻辑应指向其实际定义处，如 `subsec:global_update`；诊断的引用留在解释 Gate 的位置。使用 label，不能手写固定节号。

### 13.2 重复词

定位：旧 `appendix.tex:744–745`：`under the balanced Balanced control`。

删除重复词，并扫描相邻段落是否有同类拼接或残留的 `existing/final/confirmed` 状态提示。

### 13.3 过长小数

定位：旧 `appendix.tex:1967–1968` 的固定参考常数。

论文可用恰当有效位和近似号，精确值保留在现有正式配置/复现材料中。不得修改执行值；不能在缺少精确值出处时以舍入值冒充完整复现定义。

### 13.4 表达密度与术语一致性

逐段检查长句是否混合多个不相关判断，短段落和小标题是否只有内部状态说明。仅合并无独立科学功能的片段。

不要机械删除有意义的小节，不批量改动公式。被引用的关键公式、优化程序和正式假设必须保留。短常数若确实无需独立编号且无引用，可局部内联，但应优先避免无必要的编号变化。

验收：交叉引用准确；没有重复词；显示精度与配置精度的职责清楚；术语在正文、图注和附录一致。

## 14. 全文检索回归检查：必须按上下文分类

对实际会编译进入两份 PDF 的文字检查，不把注释、label、citation key、图片文件名误判成论文叙事。

### 14.1 应清理的过程叙述

搜索：`we found a flaw`、`we revise`、`previous version`、`patch`、`failed experiment`、`internal verification`、`publication-ready`、`approved`、`confirmed version`、`provenance audit`、`Frozen result`、`historical candidate`。

逐处判断，删除内部历史或改写成最终学术事实。不能把原来的过程句仅换几个同义词。

### 14.2 应检查重复和逻辑的否定式表达

搜索：`we do not claim`、`not claim`、`not the only`、`does not establish`、`cannot`、`not a guarantee`、`not a non-inferiority proof`。

去掉主动自我评价和重复告诫，将必要含义放到明确的对象、条件、区间或比较中。数学不可能性结果和实际未通过统计条件的结论可以保留，避免改错含义。

### 14.3 应保留其科学含义的词与编号

- `frozen` 若表示预先固定或防止时序泄漏，可自然保留；若只是“冻结结果”，改为结果本身。
- `historical calibration scores` 表示严格历史信息，不属于版本历史。
- `development protocol` 若区分不同数据/预算/目标，必须保留必要身份。
- P2、A1–A6、Theorem/Proposition 和已定义的状态名是正式对象。
- 正式种子编号属于可复现信息，不等于内部研究阶段编号；无需将每个 seed 全部删掉。

验收：每个残留的高风险表达都有明确科学用途；报告仅记录关键保留理由，不把检索日志放入论文。

## 15. 关键证据与主张保护检查

逐项核对修改前后：

1. City Scanner 的 25.8% / 23.3% 仍是相对 TwoStage-Hájek、按 seed means 比值计算的组失配降低，不是 RMSE 收益。
2. 两个协议均未实测真实 usable-update delivery；其中一个使用 measured O。不得统称全真实 R/O/U。
3. 六臂实验是十条 trace、每条三个 model seeds；不能写成 30 个独立 trace。
4. 六臂非劣区间、控制/floor 比较的不确定性及实际检验路径仍准确。
5. 完整方法与简单 reference projection 的 group、client–stratum、预测与 wall-clock 比较仍存在；不能只留下有利端点。
6. U-Air Design on/off 的排序翻转、支持变化与 matched-support 比较边界仍存在。
7. `kappa=1000` 投影加债务敏感性规则仍独立于正式强度的 full RAVEN，不能拿其收益代替主方法收益。
8. 理想 pooled recovery、固定状态扰动界、有限窗口可行性、次线性债务条件保持区别。
9. 覆盖控制比较变体、诊断 Gate 与预配置 Design 不混同。
10. 不同实验设置、目标图、尺度与种子家族不合并；SD/SE/CI、物理单位与标准化单位不混用。

这些检查只防止改写改变证据含义，不要求给正文增加新的限制清单。

## 16. 计词与编译验收

### 16.1 计词

摘要与引言分别提取环境/章节内容，用同一函数比较执行前后。沿用以下项目口径；不把结果宣称为期刊官方计词：

```python
import re

def manuscript_word_count(text):
    text = re.sub(r'(?m)(?<!\\)%.*$', '', text)
    text = re.sub(
        r'\\(?:label|cite[a-zA-Z]*|ref|eqref|autoref|cref|Cref)\*?'
        r'(?:\[[^\]]*\])*\{[^{}]*\}', ' ', text)
    text = re.sub(r'\$[^$]*\$', ' ', text)
    text = re.sub(r'\\(?:begin|end)\{[^{}]*\}', ' ', text)
    text = re.sub(r'\\[A-Za-z]+\*?(?:\[[^\]]*\])?', ' ', text)
    text = text.replace('\\', ' ').replace('{', ' ').replace('}', ' ').replace('~', ' ')
    return len(re.findall(r"[A-Za-z0-9]+(?:[-’'][A-Za-z0-9]+)*", text))
```

只比较摘要内容与引言正文；不要把标题、其他章节或自动生成的数字混入基线。原则为 `W_after = W_before`，通过准确压缩或补足科学内容实现，禁止套话填充。

### 16.2 编译

1. 沿用项目实际可用的 LaTeX 工具链。
2. 正文与补充通过 xr 互引，按实际依赖交替编译到引用和编号稳定，必要时运行 BibTeX。
3. 检查两份日志，不得新增 undefined references/citations、重复 label、缺图或编译错误。
4. 不能仅凭日志判断排版；打开修改涉及的 PDF 页，检查表头、标题、公式、Proof 和附录引用。
5. 正文不超过 14 页，补充不超过正文。以最终 PDF 实测页数为准。
6. 如超页，优先删改重复过程叙述和冗余句，不缩小正文/图表字号、压缩页边距或全局堆叠负间距，不删除关键结果来凑页。
7. 正式 Proof、结束方框及附录完整命题/定理重述保持；不得恢复 `Proof sketch`。
8. 引用继续逐个显示，不能恢复 `[3]–[7]` 式范围压缩。图 1 留第三节，表格引用留 Evaluation 及之后；摘要与引言均不引图表。
9. 如果 `ccf-paper-writer` 的非修改式 prose checker 可用，可运行一次定位剩余写作问题。结果是人工判断线索，不作为机械改词指标；不为清零牺牲术语与科学含义。

验收：真实编译成功；页数符合现有约束；交叉引用稳定；受影响页面无新遮挡/越界；词数约束通过。

## 17. 最终交付

正式产物保持原路径：

- `C:/Cursor/raven.mcs/TO_OVERLEAF_paper_tmc_r1_clean/main.tex`
- `C:/Cursor/raven.mcs/TO_OVERLEAF_paper_tmc_r1_clean/appendix.tex`
- `C:/Cursor/raven.mcs/TO_OVERLEAF_paper_tmc_r1_clean/supplemental.tex`，仅在需要时修改。
- `C:/Cursor/raven.mcs/TO_OVERLEAF_paper_tmc_r1_clean/main.pdf`
- `C:/Cursor/raven.mcs/TO_OVERLEAF_paper_tmc_r1_clean/supplemental.pdf`

另交付两份简洁文档：

1. `C:/Cursor/raven.mcs/ccf-review-report/FINAL_NARRATIVE_POLISHING_REPORT.md`
2. `C:/Cursor/raven.mcs/ccf-review-report/FINAL_NARRATIVE_POLISHING_DIFF.md`

报告逐项对应本指令第 1–16 项，给出“已修改 / 已符合 / 待核实 / 不适用”、当前文件定位、修改理由及必要证据。允许报告使用内部任务编号；编号不得写进论文。

必须单独记录：

- 第 1 项触发率字段与分母的核对依据。
- 第 2、3 项假设范围与逻辑方向的修复。
- 正式名称与旧代码键的对应关系。
- terminal-window 评分定义核对到了什么、还有什么未确认。
- 复现材料真实范围和访问状态。
- 摘要/引言词数前后值、最终页数、编译状态和剩余问题。
- 备份入口及仅恢复本轮改动的具体办法。

差异文档展示有代表性的前后句子，不复制整篇论文。不要把本报告、内部检查编号或修改说明插入论文正文、脚注、图注及附录。

最终回复先给修改后的 PDF 和报告链接，再用简短文字说明完成范围、未解决项目及其确切原因。没有完成字段核对、评分定义确认或真实编译时，必须如实写出；不以“全部通过”概括。实验保持暂停。
