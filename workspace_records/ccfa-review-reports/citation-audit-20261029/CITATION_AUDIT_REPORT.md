# RAVEN-MCS 引用与参考文献审计

审计日期：2026-10-29（核验自 2026-10-28 开始）。模式：citation-audit；真实性/元数据核验由 ccf-integrity-auditor 主导，核心基线时效性做 ccf-literature-searcher 范围内的定向检索。论文及实验未修改。

## 结论

尚未同时满足用户的四项要求。2026 年数量通过；2025 年数量不通过。核心对比覆盖了近期相关工作，但无法据此声称实验全面对比了最新方法。实际引用没有发现可确认的虚构论文，但存在明确元数据错误，且有两个细节未完全闭合，因此“所有引用规范且真实”暂不能整体判通过。

## 审计版本和可复核边界

- 对象：论文目录中现存 main.pdf、supplemental.pdf、reference.bib、两份 bbl/aux/log/blg。PDF 编译时间 2026-10-26 22:51；bbl 时间 2026-10-25 19:58；bib 时间 2026-10-18 20:55。
- 审计时 main.tex、appendix.tex、supplemental.tex 都为 0 字节，修改时间 2026-10-28 22:52:01。因此本报告描述现存已编译稿，不能证明当前源文件可重建该稿，也不能对当前 TeX 的每条 cite 命令作验收。本轮只读检查，没有清空、恢复或编译论文。
- 逐条身份核验使用出版商登记在 Crossref 的元数据、官方会议/作者/原始论文页及数据发布页。Crossref 模糊搜索出现限流、近似错配和早期在线元数据时，未自动认定为假文献，转用精确 DOI 或原始来源。
- 已对 47 个实际引用条目逐条建账：46 条定位到原始论文、出版商登记信息或官方数据页；Hájek 1971 定位到研究论文中的一致引证，原始书籍章节未直接核到。没有把“存在性已定位”扩大为全部作者/页码/引用语义均已复核。

## 年份数量：以实际引用去重计数

- 正文：47 条，2026 年 7 条，2025 年 5 条。2026 要求 ≥5：通过；2025 要求 ≥15：不足 10 条。
- 补充文件：5 条，全部与正文重叠；其中 2026 年 2 条、2025 年 0 条。正文与补充的去重并集仍为 47 条，7/5 的年份计数不变。
- 全部 bib：54 条，2026 年 9 条、2025 年 7 条；有 7 条未进入已编译正文/补充引用，不得用它们充当已引用数量。即使把整个 bib 都算上，2025 仍不满足 15 条。
- 此处按已编译书目的年份与已分配卷期年份统计，不将访问年份、预印本修订年份和 DOI 中的年份混用。当前 2026 七条含 6 条正式发表记录和 1 条 arXiv；若只认正式论文，2026 仍有 6 条，满足 5 条。

2026 七条：

- [4] Federated Learning-Based Distributed Data Completion in Sparse Mobile CrowdSensing。
- [5] Who Trains Matters: Federated Learning under Enrollment and Participation Selection Biases。
- [15] Spatio-Temporal Pyramid-Based Multi-Scale Data Completion in Sparse Crowdsensing。
- [16] MapT-STC: A One-Shot Spatiotemporal Data Completion Framework for Cold-Start Tasks in Sparse Crowdsensing。
- [17] Data Pricing via Uncertainty Quantification for Sparse Mobile CrowdSensing。
- [25] STDFL: A Spatio-Temporal-Aware Dynamic Federated Learning Framework for Spatial Crowdsourcing。
- [31] FedCure: Mitigating Participation Bias in Semi-Asynchronous Federated Learning with Non-IID Data。

2025 五条：

- [13] A New Data Completion Perspective on Sparse CrowdSensing: Spatiotemporal Evolutionary Inference Approach。
- [14] Rethinking the Effect of Sparse Data Completion on Sparse Mobile Crowdsensing Tasks。
- [24] SEAFL: Enhancing Efficiency in Semi-Asynchronous Federated Learning through Adaptive Aggregation and Selective Training。
- [30] Debiasing Federated Learning with Correlated Client Participation。
- [32] FLOSS: Federated Learning with Opt-Out and Straggler Support。

## 必须修复的书目错误

### [12] wang2024fewshot

作者 Yang Xu 应写为 Xu, Yang；当前 Yang, Xu 导致 PDF 显示 Y. Yang。INFOCOM 官方日程确认姓名。DOI 10.1109/INFOCOM52122.2024.10621156。
核验来源：[Few-Shot Data Completion for New Tasks in Sparse Crowdsensing](https://infocom.info/infocom24/day/3)。

### [21] xie2019asynchronous

会议名称为 OPT 2020，但 year=2019。应选 2020 workshop 条目，或独立采用 2019 arXiv 预印本条目，不混写。
核验来源：[Asynchronous Federated Optimization](https://opt-ml.org/oldopt/opt20/papers.html)。

### [24] islam2025seafl

已有 IPDPS 2025 正式版本，509–519，DOI 10.1109/IPDPS64566.2025.00052。应更新 @misc 为 @inproceedings，并录入六位作者；不增加 2025 去重计数。
核验来源：[SEAFL: Enhancing Efficiency in Semi-Asynchronous Federated Learning through Adaptive Aggregation and Selective Training](https://doi.org/10.1109/ipdps64566.2025.00052)。

### [29] wang2024lightweight

当前页码 854–893 与印刷论文集目录不符；目录起页 29653。建议按 ICLR 官方 BibTeX 去除未经核准页码，或核准完整印刷范围。补充文件同样受影响。
核验来源：[A Lightweight Method for Tackling Unknown Participation Statistics in Federated Averaging](https://proceedings.iclr.cc/paper_files/paper/2024/hash/03a9a9c1e15850439653bb971a4ad4b3-Abstract-Conference.html)。

### [30] sun2025debiasing

当前页码 28564–28595 与印刷论文集目录不符；目录起页 16492。建议按 ICLR 官方 BibTeX 去除未经核准页码，或核准完整印刷范围。
核验来源：[Debiasing Federated Learning with Correlated Client Participation](https://proceedings.iclr.cc/paper_files/paper/2025/hash/464917b6103e074e1f9df7a2bf3bf6ba-Abstract-Conference.html)。

### [31] chen2026fedcure

Shuqing Cao 应为 Shuqin Cao；Dawei Wang 应为 Wei Wang。AAAI 官网作者名单及正式 PDF 一致。DOI 10.1609/aaai.v40i25.39176。
核验来源：[FedCure: Mitigating Participation Bias in Semi-Asynchronous Federated Learning with Non-IID Data](https://doi.org/10.1609/aaai.v40i25.39176)。

页码交叉证据：ICLR 2024 印刷论文集目录将 FedAU 列于 29653 起，下一篇为 29693；ICLR 2025 目录将相关参与去偏论文列于 16492 起，下一篇为 16524。当前两组页码不能保留。最小修复可直接采用官方导出的无页码条目，而非猜测页码。

- [ICLR 2024 论文集目录](https://www.proceedings.com/content/074/074958webtoc.pdf)
- [ICLR 2025 论文集目录](https://www.proceedings.com/content/080/080508webtoc.pdf)

## 核心方法是否最新

1. FedAvg 2017、FedAsync 2019/2020 是基础参照，保留原始来源合理，不应为凑年份替换它们。FedAsync 的会议/年份必须先统一。
2. TimeAlign 所依托的联邦稀疏数据补全工作 [4] 已引到 TMC 25(5), 2026 正式版本，属于近期且任务直接相关的来源；论文应继续明确它是本文采用的 windowed adaptation。
3. FedAU [29] 已引用 ICLR 2024 正式版本；该原方法的出处没有过时，但它不能独自代表全部参与去偏新进展。现有相关工作已列 ICLR 2025 相关参与去偏、FLOSS 2025、FedCure 2026。
4. 最近的概念竞争工作 FedIPW [5] 已引用 arXiv 2026-04-29 v1；FedPALS [6] 已注明 arXiv v2, 2025-08-26。本轮没有核到可替代这两个条目的更晚正式出版记录，不应凭搜索聚合页将其升级为已录用论文。FedPALS 的 2025 修订不能被另算一篇论文。
5. SEAFL [24] 已有 IPDPS 2025 正式版本，应更新条目。FLOSS 已引 ACM 2025 版本，但 arXiv 于 2026-04-21 更新 v2；若论文使用 v2 特有内容，应清楚标注版本，不能把同一论文重复计入两个年份。
6. “引用了新论文”和“实验比较了新方法”需要分开。正文核心表的实际外部参照主要为 FedAvg-Window、FedAU-Window、TimeAlign 等；FedIPW、FedPALS、FedCure 主要用于定位/范围比较，不是已经完成的完整数值基线。当前可以说采用近期相关方法和同骨干适配比较；不能说全面胜过最新 SOTA。
7. 本轮定位到但现有书目缺失的直接机制背景是 FedBuff（AISTATS 2022）：缓冲异步聚合与本文窗口聚合相关。建议在相关工作解释区别；这是机制覆盖问题，不是 2025/2026 数量补额。它不自动要求恢复训练。

相关原始来源：
- [FedAU，ICLR 2024](https://proceedings.iclr.cc/paper_files/paper/2024/hash/03a9a9c1e15850439653bb971a4ad4b3-Abstract-Conference.html)
- [相关参与去偏，ICLR 2025](https://proceedings.iclr.cc/paper_files/paper/2025/hash/464917b6103e074e1f9df7a2bf3bf6ba-Abstract-Conference.html)
- [FedIPW 原始预印本](https://arxiv.org/abs/2604.26604)
- [FedPALS v2](https://arxiv.org/abs/2411.03799v2)
- [SEAFL 正式记录](https://doi.org/10.1109/IPDPS64566.2025.00052)
- [FLOSS 正式记录](https://doi.org/10.1145/3766882.3767180)
- [FLOSS 版本记录](https://arxiv.org/abs/2507.23115)
- [FedBuff，AISTATS 2022](https://proceedings.mlr.press/v151/nguyen22b.html)

## 引用格式、语境与待核项

- 现存两份 PDF 未检出 [3]–[7] 式区间压缩；可见正文以独立方括号列出引用。
- main.aux 的 47 个引用键与 main.bbl 一一对应；无缺失或多余正文条目。补充的五条全部能在 bib 中定位。54 个 bib 条目无重复键。现存日志无未定义引用警告，BibTeX 日志 warning$=0。以上是保存的编译结果，不是对零字节源文件的新编译验收。
- 相关工作前两句分别聚集 13 条和 10 条引用，主题关联大致合理，但一条概述句很难清楚说明各方法差异。建议按数据补全、联邦补全、异步/陈旧控制拆成短句，每个具体判断紧邻其适当引文；不要为满足数量把新论文全部堆入这两句。
- 对 FedIPW、FedPALS、FedAU 的核心机制概述，和可见原始摘要/版本记录未发现明显错引；本轮未做 47 篇全文的逐命题证明审查。引用某篇文献不证明对应方法已在本文实验实现。
- 两篇联邦 conformal prediction 文献 [38]/[39] 在正文中用于与机会覆盖诊断区分；它们的存在性和主题已核实，不宜据此把本文 Gate 叙述成已有 conformal 覆盖保证。
- Hájek [34] 的原始章节信息待直接核准；目前不据不一致的二次引证擅改其页码。NSW [43] 的数据发布年份 2024 待核准，官方动态数据页的访问日期与数据版本需区分。
- T-Drive 原始论文 [44] 与所链接的微软数据页都真实；微软页明确建议引用该 2010 论文。可补论文 DOI，并将实际下载的数据页作为数据来源单列/说明，避免把论文年份与数据页 2011 年日期混淆。
- DOI/稳定 URL 建议补齐；并非据“没有 DOI 字段”就判定某条虚假。文章号（City Scanner 的 524）、品牌/方法缩写（FedVARP 等）的展示可统一，属于次要规范修正。

## 建议处理顺序

1. 先确认三份零字节 TeX 的原因及当前有效稿源，从已知备份恢复有效源文件由论文维护者执行；本轮没有覆盖任何文件。
2. 修复 6 个问题条目，闭合 2 项待核细节，重编译后复核 47 条编号、链接和去压缩格式。
3. 如坚持 2025 ≥15，再按论文具体论断检索并实质引用至少 10 篇相关 2025 工作；避免修改年份凑数、重复预印本/正式版本、引入无关隐私交易论文。已有 bib 中两篇未引用的 2025 隐私/交易论文不能自动视为合适补额。
4. 更新相关工作中的发表状态，说明最新概念竞争工作的比较范围，保持现有实验暂停。增加引用不等于已经补做实验。

## 逐条核验清单

### [1] Mobile Crowdsensing: Current State and Future Challenges (2011)

- 键：`ganti2011mobile`；状态：已定位，未见硬错误。
- 证据：[Mobile Crowdsensing: Current State and Future Challenges](https://doi.org/10.1109/mcom.2011.6069707)。
- 核验说明：已定位公开原始论文、出版商登记元数据或数据发布页；不等同于逐页全文复核全部引文语义。

### [2] Robust Data Inference and Cost-Effective Cell Selection for Sparse Mobile Crowdsensing (2024)

- 键：`li2024robust`；状态：已定位，未见硬错误。
- 证据：[Robust Data Inference and Cost-Effective Cell Selection for Sparse Mobile Crowdsensing](https://doi.org/10.1109/tnet.2024.3397309)。
- 核验说明：已定位公开原始论文、出版商登记元数据或数据发布页；不等同于逐页全文复核全部引文语义。

### [3] Communication-Efficient Learning of Deep Networks from Decentralized Data (2017)

- 键：`mcmahan2017communication`；状态：已定位，未见硬错误。
- 证据：[Communication-Efficient Learning of Deep Networks from Decentralized Data](https://proceedings.mlr.press/v54/mcmahan17a.html)。
- 核验说明：已定位公开原始论文、出版商登记元数据或数据发布页；不等同于逐页全文复核全部引文语义。

### [4] Federated Learning-Based Distributed Data Completion in Sparse Mobile CrowdSensing (2026)

- 键：`wang2026federated`；状态：已定位，未见硬错误。
- 证据：[Federated Learning-Based Distributed Data Completion in Sparse Mobile CrowdSensing](https://doi.org/10.1109/tmc.2025.3640170)。
- 核验说明：已定位公开原始论文、出版商登记元数据或数据发布页；不等同于逐页全文复核全部引文语义。

### [5] Who Trains Matters: Federated Learning under Enrollment and Participation Selection Biases (2026)

- 键：`morishita2026who`；状态：已定位，未见硬错误。
- 证据：[Who Trains Matters: Federated Learning under Enrollment and Participation Selection Biases](https://arxiv.org/abs/2604.26604)。
- 核验说明：已定位公开原始论文、出版商登记元数据或数据发布页；不等同于逐页全文复核全部引文语义。 已核到 2026-04-29 arXiv v1，未核到正式录用版本。

### [6] Overcoming Label Shift with Target-Aware Federated Learning (2024)

- 键：`listozec2024overcoming`；状态：已定位，未见硬错误。
- 证据：[Overcoming Label Shift with Target-Aware Federated Learning](https://arxiv.org/abs/2411.03799v2)。
- 核验说明：已定位公开原始论文、出版商登记元数据或数据发布页；不等同于逐页全文复核全部引文语义。 当前引用已注明 2025-08-26 v2；arXiv 首发 2024，不据修订日期冒称正式 2025 会议或期刊文章。

### [7] Mobile Crowd Sensing and Computing: The Review of an Emerging Human-Powered Sensing Paradigm (2015)

- 键：`guo2015mobile`；状态：已定位，未见硬错误。
- 证据：[Mobile Crowd Sensing and Computing: The Review of an Emerging Human-Powered Sensing Paradigm](https://doi.org/10.1145/2794400)。
- 核验说明：已定位公开原始论文、出版商登记元数据或数据发布页；不等同于逐页全文复核全部引文语义。

### [8] Opportunities in Mobile Crowd Sensing (2014)

- 键：`ma2014opportunities`；状态：已定位，未见硬错误。
- 证据：[Opportunities in Mobile Crowd Sensing](https://doi.org/10.1109/mcom.2014.6871666)。
- 核验说明：已定位公开原始论文、出版商登记元数据或数据发布页；不等同于逐页全文复核全部引文语义。

### [9] Spatiotemporal Urban Inference and Prediction in Sparse Mobile CrowdSensing: A Graph Neural Network Approach (2023)

- 键：`wang2023spatiotemporal`；状态：已定位，未见硬错误。
- 证据：[Spatiotemporal Urban Inference and Prediction in Sparse Mobile CrowdSensing: A Graph Neural Network Approach](https://doi.org/10.1109/tmc.2022.3195706)。
- 核验说明：已定位公开原始论文、出版商登记元数据或数据发布页；不等同于逐页全文复核全部引文语义。 Crossref 直查保留早期在线 2022 年信息；作者正式发表清单列 22(11):6784–6799, 2023，不应误改为早期在线版本。

### [10] Outlier-Concerned Data Completion Exploiting Intra- and Inter-Data Correlations in Sparse CrowdSensing (2023)

- 键：`wang2023outlier`；状态：已定位，未见硬错误。
- 证据：[Outlier-Concerned Data Completion Exploiting Intra- and Inter-Data Correlations in Sparse CrowdSensing](https://doi.org/10.1109/tnet.2022.3201545)。
- 核验说明：已定位公开原始论文、出版商登记元数据或数据发布页；不等同于逐页全文复核全部引文语义。

### [11] Spatiotemporal Transformer for Data Inference and Long Prediction in Sparse Mobile CrowdSensing (2023)

- 键：`wang2023transformer`；状态：已定位，未见硬错误。
- 证据：[Spatiotemporal Transformer for Data Inference and Long Prediction in Sparse Mobile CrowdSensing](https://doi.org/10.1109/infocom53939.2023.10228982)。
- 核验说明：已定位公开原始论文、出版商登记元数据或数据发布页；不等同于逐页全文复核全部引文语义。

### [12] Few-Shot Data Completion for New Tasks in Sparse Crowdsensing (2024)

- 键：`wang2024fewshot`；状态：需修复。
- 证据：[Few-Shot Data Completion for New Tasks in Sparse Crowdsensing](https://infocom.info/infocom24/day/3)。
- 核验说明：作者 Yang Xu 应写为 Xu, Yang；当前 Yang, Xu 导致 PDF 显示 Y. Yang。INFOCOM 官方日程确认姓名。DOI 10.1109/INFOCOM52122.2024.10621156。

### [13] A New Data Completion Perspective on Sparse CrowdSensing: Spatiotemporal Evolutionary Inference Approach (2025)

- 键：`wang2025evolutionary`；状态：已定位，未见硬错误。
- 证据：[A New Data Completion Perspective on Sparse CrowdSensing: Spatiotemporal Evolutionary Inference Approach](https://doi.org/10.1109/tmc.2024.3480983)。
- 核验说明：已定位公开原始论文、出版商登记元数据或数据发布页；不等同于逐页全文复核全部引文语义。

### [14] Rethinking the Effect of Sparse Data Completion on Sparse Mobile Crowdsensing Tasks (2025)

- 键：`xu2025rethinking`；状态：已定位，未见硬错误。
- 证据：[Rethinking the Effect of Sparse Data Completion on Sparse Mobile Crowdsensing Tasks](https://doi.org/10.1109/tmc.2025.3531362)。
- 核验说明：已定位公开原始论文、出版商登记元数据或数据发布页；不等同于逐页全文复核全部引文语义。

### [15] Spatio-Temporal Pyramid-Based Multi-Scale Data Completion in Sparse Crowdsensing (2026)

- 键：`liu2026pyramid`；状态：已定位，未见硬错误。
- 证据：[Spatio-Temporal Pyramid-Based Multi-Scale Data Completion in Sparse Crowdsensing](https://doi.org/10.1109/tmc.2025.3599322)。
- 核验说明：已定位公开原始论文、出版商登记元数据或数据发布页；不等同于逐页全文复核全部引文语义。

### [16] MapT-STC: A One-Shot Spatiotemporal Data Completion Framework for Cold-Start Tasks in Sparse Crowdsensing (2026)

- 键：`zhang2026mapt`；状态：已定位，未见硬错误。
- 证据：[MapT-STC: A One-Shot Spatiotemporal Data Completion Framework for Cold-Start Tasks in Sparse Crowdsensing](https://doi.org/10.1109/tmc.2026.3678980)。
- 核验说明：已定位公开原始论文、出版商登记元数据或数据发布页；不等同于逐页全文复核全部引文语义。

### [17] Data Pricing via Uncertainty Quantification for Sparse Mobile CrowdSensing (2026)

- 键：`liu2026pricing`；状态：已定位，未见硬错误。
- 证据：[Data Pricing via Uncertainty Quantification for Sparse Mobile CrowdSensing](https://doi.org/10.1109/tsc.2026.3664086)。
- 核验说明：已定位公开原始论文、出版商登记元数据或数据发布页；不等同于逐页全文复核全部引文语义。

### [18] Federated Machine Learning: Concept and Applications (2019)

- 键：`yang2019federated`；状态：已定位，未见硬错误。
- 证据：[Federated Machine Learning: Concept and Applications](https://doi.org/10.1145/3298981)。
- 核验说明：已定位公开原始论文、出版商登记元数据或数据发布页；不等同于逐页全文复核全部引文语义。

### [19] Advances and Open Problems in Federated Learning (2021)

- 键：`kairouz2021advances`；状态：已定位，未见硬错误。
- 证据：[Advances and Open Problems in Federated Learning](https://doi.org/10.1561/2200000083)。
- 核验说明：已定位公开原始论文、出版商登记元数据或数据发布页；不等同于逐页全文复核全部引文语义。

### [20] Federated Learning: Challenges, Methods, and Future Directions (2020)

- 键：`li2020federated`；状态：已定位，未见硬错误。
- 证据：[Federated Learning: Challenges, Methods, and Future Directions](https://doi.org/10.1109/msp.2020.2975749)。
- 核验说明：已定位公开原始论文、出版商登记元数据或数据发布页；不等同于逐页全文复核全部引文语义。

### [21] Asynchronous Federated Optimization (2019)

- 键：`xie2019asynchronous`；状态：需修复。
- 证据：[Asynchronous Federated Optimization](https://opt-ml.org/oldopt/opt20/papers.html)。
- 核验说明：会议名称为 OPT 2020，但 year=2019。应选 2020 workshop 条目，或独立采用 2019 arXiv 预印本条目，不混写。

### [22] Adaptive Asynchronous Federated Learning in Resource-Constrained Edge Computing (2023)

- 键：`liu2023adaptive`；状态：已定位，未见硬错误。
- 证据：[Adaptive Asynchronous Federated Learning in Resource-Constrained Edge Computing](https://doi.org/10.1109/tmc.2021.3096846)。
- 核验说明：已定位公开原始论文、出版商登记元数据或数据发布页；不等同于逐页全文复核全部引文语义。

### [23] Staleness-Controlled Asynchronous Federated Learning: Accuracy and Efficiency Tradeoff (2024)

- 键：`sun2024staleness`；状态：已定位，未见硬错误。
- 证据：[Staleness-Controlled Asynchronous Federated Learning: Accuracy and Efficiency Tradeoff](https://doi.org/10.1109/tmc.2024.3416216)。
- 核验说明：已定位公开原始论文、出版商登记元数据或数据发布页；不等同于逐页全文复核全部引文语义。

### [24] SEAFL: Enhancing Efficiency in Semi-Asynchronous Federated Learning through Adaptive Aggregation and Selective Training (2025)

- 键：`islam2025seafl`；状态：需修复。
- 证据：[SEAFL: Enhancing Efficiency in Semi-Asynchronous Federated Learning through Adaptive Aggregation and Selective Training](https://doi.org/10.1109/ipdps64566.2025.00052)。
- 核验说明：已有 IPDPS 2025 正式版本，509–519，DOI 10.1109/IPDPS64566.2025.00052。应更新 @misc 为 @inproceedings，并录入六位作者；不增加 2025 去重计数。

### [25] STDFL: A Spatio-Temporal-Aware Dynamic Federated Learning Framework for Spatial Crowdsourcing (2026)

- 键：`li2026stdfl`；状态：已定位，未见硬错误。
- 证据：[STDFL: A Spatio-Temporal-Aware Dynamic Federated Learning Framework for Spatial Crowdsourcing](https://doi.org/10.1109/tmc.2026.3673177)。
- 核验说明：已定位公开原始论文、出版商登记元数据或数据发布页；不等同于逐页全文复核全部引文语义。

### [26] A Unified Analysis of Federated Learning with Arbitrary Client Participation (2022)

- 键：`wang2022unified`；状态：已定位，未见硬错误。
- 证据：[A Unified Analysis of Federated Learning with Arbitrary Client Participation](https://doi.org/10.52202/068431-1390)。
- 核验说明：已定位公开原始论文、出版商登记元数据或数据发布页；不等同于逐页全文复核全部引文语义。

### [27] FedVARP: Tackling the Variance Due to Partial Client Participation in Federated Learning (2022)

- 键：`jhunjhunwala2022fedvarp`；状态：已定位，未见硬错误。
- 证据：[FedVARP: Tackling the Variance Due to Partial Client Participation in Federated Learning](https://proceedings.mlr.press/v180/jhunjhunwala22a.html)。
- 核验说明：已定位公开原始论文、出版商登记元数据或数据发布页；不等同于逐页全文复核全部引文语义。

### [28] Anchor Sampling for Federated Learning with Partial Client Participation (2023)

- 键：`wu2023anchor`；状态：已定位，未见硬错误。
- 证据：[Anchor Sampling for Federated Learning with Partial Client Participation](https://proceedings.mlr.press/v202/wu23e.html)。
- 核验说明：已定位公开原始论文、出版商登记元数据或数据发布页；不等同于逐页全文复核全部引文语义。

### [29] A Lightweight Method for Tackling Unknown Participation Statistics in Federated Averaging (2024)

- 键：`wang2024lightweight`；状态：需修复。
- 证据：[A Lightweight Method for Tackling Unknown Participation Statistics in Federated Averaging](https://proceedings.iclr.cc/paper_files/paper/2024/hash/03a9a9c1e15850439653bb971a4ad4b3-Abstract-Conference.html)。
- 核验说明：当前页码 854–893 与印刷论文集目录不符；目录起页 29653。建议按 ICLR 官方 BibTeX 去除未经核准页码，或核准完整印刷范围。补充文件同样受影响。

### [30] Debiasing Federated Learning with Correlated Client Participation (2025)

- 键：`sun2025debiasing`；状态：需修复。
- 证据：[Debiasing Federated Learning with Correlated Client Participation](https://proceedings.iclr.cc/paper_files/paper/2025/hash/464917b6103e074e1f9df7a2bf3bf6ba-Abstract-Conference.html)。
- 核验说明：当前页码 28564–28595 与印刷论文集目录不符；目录起页 16492。建议按 ICLR 官方 BibTeX 去除未经核准页码，或核准完整印刷范围。

### [31] FedCure: Mitigating Participation Bias in Semi-Asynchronous Federated Learning with Non-IID Data (2026)

- 键：`chen2026fedcure`；状态：需修复。
- 证据：[FedCure: Mitigating Participation Bias in Semi-Asynchronous Federated Learning with Non-IID Data](https://doi.org/10.1609/aaai.v40i25.39176)。
- 核验说明：Shuqing Cao 应为 Shuqin Cao；Dawei Wang 应为 Wei Wang。AAAI 官网作者名单及正式 PDF 一致。DOI 10.1609/aaai.v40i25.39176。

### [32] FLOSS: Federated Learning with Opt-Out and Straggler Support (2025)

- 键：`goetze2025floss`；状态：已定位，未见硬错误。
- 证据：[FLOSS: Federated Learning with Opt-Out and Straggler Support](https://doi.org/10.1145/3766882.3767180)。
- 核验说明：已定位公开原始论文、出版商登记元数据或数据发布页；不等同于逐页全文复核全部引文语义。 已引用 2025 ACM 正式版本；arXiv 有 2026-04-21 v2，使用新内容时需明确版本。

### [33] A Generalization of Sampling Without Replacement From a Finite Universe (1952)

- 键：`horvitz1952generalization`；状态：已定位，未见硬错误。
- 证据：[A Generalization of Sampling Without Replacement From a Finite Universe](https://doi.org/10.1080/01621459.1952.10483446)。
- 核验说明：已定位公开原始论文、出版商登记元数据或数据发布页；不等同于逐页全文复核全部引文语义。

### [34] Comment on ``An Essay on the Logical Foundations of Survey Sampling, Part One'' (1971)

- 键：`hajek1971comment`；状态：待核。
- 证据：[Comment on ``An Essay on the Logical Foundations of Survey Sampling, Part One''](https://nejsds.nestat.org/journal/NEJSDS/article/114/file/pdf)。
- 核验说明：书籍评论条目可由统计学研究论文的参考文献追溯，包含 236–242 的一致引证；本次未获得原始章节，未逐页核准页码和原始章节标题，不判为虚构。

### [35] Improving Predictive Inference under Covariate Shift by Weighting the Log-Likelihood Function (2000)

- 键：`shimodaira2000covariate`；状态：已定位，未见硬错误。
- 证据：[Improving Predictive Inference under Covariate Shift by Weighting the Log-Likelihood Function](https://doi.org/10.1016/s0378-3758(00)00115-4)。
- 核验说明：已定位公开原始论文、出版商登记元数据或数据发布页；不等同于逐页全文复核全部引文语义。

### [36] Estimation of Regression Coefficients When Some Regressors are not Always Observed (1994)

- 键：`robins1994estimation`；状态：已定位，未见硬错误。
- 证据：[Estimation of Regression Coefficients When Some Regressors are not Always Observed](https://doi.org/10.1080/01621459.1994.10476818)。
- 核验说明：已定位公开原始论文、出版商登记元数据或数据发布页；不等同于逐页全文复核全部引文语义。

### [37] What is the Effect of Importance Weighting in Deep Learning? (2019)

- 键：`byrd2019importance`；状态：已定位，未见硬错误。
- 证据：[What is the Effect of Importance Weighting in Deep Learning?](https://proceedings.mlr.press/v97/byrd19a.html)。
- 核验说明：已定位公开原始论文、出版商登记元数据或数据发布页；不等同于逐页全文复核全部引文语义。

### [38] Federated Conformal Predictors for Distributed Uncertainty Quantification (2023)

- 键：`lu2023federated`；状态：已定位，未见硬错误。
- 证据：[Federated Conformal Predictors for Distributed Uncertainty Quantification](https://proceedings.mlr.press/v202/lu23i.html)。
- 核验说明：已定位公开原始论文、出版商登记元数据或数据发布页；不等同于逐页全文复核全部引文语义。

### [39] Conformal Prediction for Federated Uncertainty Quantification Under Label Shift (2023)

- 键：`plassier2023conformal`；状态：已定位，未见硬错误。
- 证据：[Conformal Prediction for Federated Uncertainty Quantification Under Label Shift](https://proceedings.mlr.press/v202/plassier23a.html)。
- 核验说明：已定位公开原始论文、出版商登记元数据或数据发布页；不等同于逐页全文复核全部引文语义。

### [40] SensorScope: Application-Specific Sensor Network for Environmental Monitoring (2010)

- 键：`ingelrest2010sensorscope`；状态：已定位，未见硬错误。
- 证据：[SensorScope: Application-Specific Sensor Network for Environmental Monitoring](https://doi.org/10.1145/1689239.1689247)。
- 核验说明：已定位公开原始论文、出版商登记元数据或数据发布页；不等同于逐页全文复核全部引文语义。

### [41] SensorScope Data (2019)

- 键：`barrenetxea2019sensorscope`；状态：已定位，未见硬错误。
- 证据：[SensorScope Data](https://zenodo.org/records/2654726)。
- 核验说明：已定位公开原始论文、出版商登记元数据或数据发布页；不等同于逐页全文复核全部引文语义。

### [42] U-Air: When Urban Air Quality Inference Meets Big Data (2013)

- 键：`zheng2013uair`；状态：已定位，未见硬错误。
- 证据：[U-Air: When Urban Air Quality Inference Meets Big Data](https://www.microsoft.com/en-us/research/publication/u-air-when-urban-air-quality-inference-meets-big-data/)。
- 核验说明：已定位公开原始论文、出版商登记元数据或数据发布页；不等同于逐页全文复核全部引文语义。

### [43] NSW Roads Traffic Volume Counts (2024)

- 键：`tfnsw2024traffic`；状态：待核。
- 证据：[NSW Roads Traffic Volume Counts](https://opendata.transport.nsw.gov.au/data/dataset/nsw-roads-traffic-volume-counts-api)。
- 核验说明：官方数据集真实、链接可定位；year=2024 的发布依据本次未核准。访问日期不能替代数据版本年份；保留真实下载/访问记录，核对具体资源。

### [44] T-Drive: Driving Directions Based on Taxi Trajectories (2010)

- 键：`yuan2010tdrive`；状态：已定位，未见硬错误。
- 证据：[T-Drive: Driving Directions Based on Taxi Trajectories](https://www.microsoft.com/en-us/research/publication/t-drive-trajectory-data-sample/)。
- 核验说明：已定位公开原始论文、出版商登记元数据或数据发布页；不等同于逐页全文复核全部引文语义。

### [45] Hyperlocal environmental data with a mobile platform in urban environments (2023)

- 键：`wang2023cityscanner`；状态：已定位，未见硬错误。
- 证据：[Hyperlocal environmental data with a mobile platform in urban environments](https://doi.org/10.1038/s41597-023-02425-3)。
- 核验说明：已定位公开原始论文、出版商登记元数据或数据发布页；不等同于逐页全文复核全部引文语义。

### [46] Individual Comparisons by Ranking Methods (1945)

- 键：`wilcoxon1945individual`；状态：已定位，未见硬错误。
- 证据：[Individual Comparisons by Ranking Methods](https://doi.org/10.2307/3001968)。
- 核验说明：已定位公开原始论文、出版商登记元数据或数据发布页；不等同于逐页全文复核全部引文语义。

### [47] A Simple Sequentially Rejective Multiple Test Procedure (1979)

- 键：`holm1979simple`；状态：已定位，未见硬错误。
- 证据：[A Simple Sequentially Rejective Multiple Test Procedure](https://www.ime.usp.br/~abe/lista/pdf4R8xPVzCnX.pdf)。
- 核验说明：已定位公开原始论文、出版商登记元数据或数据发布页；不等同于逐页全文复核全部引文语义。
