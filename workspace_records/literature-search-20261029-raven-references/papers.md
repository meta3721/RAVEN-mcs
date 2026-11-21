# RAVEN-MCS 引用补充文献检索

日期：2026-10-29。标准模式；目标是为现有论文补充真实、相关的 2025 文献，并检查近期机制进展。未修改论文、未恢复实验。

## 可直接使用的结果

筛选结果为 10 篇优先纳入的新增 2025 正式论文，以及 2 篇须有对应讨论才引用的备选。12 篇均与当前 54 条 reference.bib 按标题和已有 DOI 去重，未发现重复；标题、作者和正式发表信息已核至官方论文集、出版商登记或原始作者稿。

上轮审计的已引用 2025 文献为 5 篇。若后续作者在正文中实质引用这 10 篇，且编译后的计数核准，2025 可达到 15 篇。此处只是候选包，不宣称论文已经达到该数量。2026 数量已经满足要求，无需更改首发/卷期年份凑数。

交付：recommended_2025.bib（10 篇）、optional_2025.bib（2 篇）、papers.csv/json（来源、放置位置与边界）、insertion-plan.md（写作交接），sources/ 保存已获取的公开原文与注册元数据。

## 分组与优先级

- 参与与优化：FAST、FOCUS、PHP-FL。
- 异步与陈旧控制：MasFL/AdaMasFL、DeFedAvg。
- 缺失机制与联邦数据处理：Cafe、DARN。
- 稀疏移动群智补全：Non-Aligned Multi-Scale、StrucFormer。
- 偏差概念：Bias in Federated Learning 综述。
- 条件性备选：FedRényi（预测群体公平）、FedBack（主动参与控制）。

## 每篇文献与引用边界

### 1. FAST: A Lightweight Mechanism Unleashing Arbitrary Client Participation in Federated Learning

- 正式来源：IJCAI 2025；状态：正式发表；原始来源/出版登记已核。
- 原始/稳定链接：[FAST: A Lightweight Mechanism Unleashing Arbitrary Client Participation in Federated Learning](https://ijcai.org/proceedings/2025/628)。
- 类型/优先级：pure method；优先纳入。
- 原文支持的要点：FAST 使用偶发 snapshot 机制支持大部分训练阶段的任意客户端参与，并分析非凸及强凸收敛。
- 推荐位置（本次检索判断）：Section II participation-aware FL：与 FedAU、相关参与去偏并列，说明参与不规则可通过聚合之外的训练机制处理。
- 引用边界：它对 snapshot 轮有专门要求；没有证明本文 R/O/U 识别或硬约束下部署目标质量可达。
- 初评 I/C/N：4/4/4。已检查原文的收敛假设与 §5；Fashion-MNIST、CIFAR-10、Shakespeare，客户端参与和数据异质性实验。评分为检索阶段判断，未复现实验。
- BibTeX 键：`li2025fast`。

### 2. Exact and Linear Convergence for Federated Learning under Arbitrary Client Participation is Attainable

- 正式来源：NeurIPS 2025；状态：正式发表；原始来源/出版登记已核。
- 原始/稳定链接：[Exact and Linear Convergence for Federated Learning under Arbitrary Client Participation is Attainable](https://proceedings.neurips.cc/paper_files/paper/2025/hash/395409679270591fd2a70abc694cf5a1-Abstract-Conference.html)。
- 类型/优先级：theory/proof；优先纳入。
- 原文支持的要点：FOCUS 用时变图与 push-pull 策略处理客户端参与和漂移，分析不同目标条件下的收敛。
- 推荐位置（本次检索判断）：Section II participation-aware FL：补足 2025 年优化理论进展，避免将“处理未知参与”写成本文独有贡献。
- 引用边界：线性率有强凸或 PL 等条件；参与假设含正概率。不能引用为任意非凸、永久缺失支持下的无条件精确收敛。
- 初评 I/C/N：4/4/3。已检查 Assumption 1、Theorem 1 与附录 G；CIFAR-10 上包含 FedAU、MIFA、SCAFFOLD 参照。理论证据强，任务范围有限。
- BibTeX 键：`ying2025focus`。

### 3. A Fair Federated Learning Method for Handling Client Participation Probability Inconsistencies in Heterogeneous Environments

- 正式来源：NeurIPS 2025；状态：正式发表；原始来源/出版登记已核。
- 原始/稳定链接：[A Fair Federated Learning Method for Handling Client Participation Probability Inconsistencies in Heterogeneous Environments](https://proceedings.neurips.cc/paper_files/paper/2025/hash/dcc0ac74ac8b95dc1939804acce0317d-Abstract-Conference.html)。
- 类型/优先级：pure method；优先纳入。
- 原文支持的要点：PHP-FL 研究模型异质及参与概率不一致，通过双端对齐和重要性驱动参数更新改善准确率与客户端表现公平性。
- 推荐位置（本次检索判断）：Section II 参与偏差/公平性段：作为 2025 年直接相关工作，同时区分表现公平性与部署组质量对齐。
- 引用边界：其模型异质、知识对齐、客户端准确率公平性与本文同骨干及质量组成目标不同，不能直接等同。
- 初评 I/C/N：4/4/4。已检查 §5：Fashion-MNIST、CIFAR-10，三种参与模式、准确率/公平性指标及 DEAL/ISPU 消融。
- BibTeX 键：`wu2025phpfl`。

### 4. Momentum-Driven Adaptivity: Towards Tuning-Free Asynchronous Federated Learning

- 正式来源：ICML 2025；状态：正式发表；原始来源/出版登记已核。
- 原始/稳定链接：[Momentum-Driven Adaptivity: Towards Tuning-Free Asynchronous Federated Learning](https://proceedings.mlr.press/v267/yan25f.html)。
- 类型/优先级：pure method；优先纳入。
- 原文支持的要点：MasFL 通过历史下降方向减轻异步陈旧累积；AdaMasFL 进一步引入自适应归一化，分析收敛与调参依赖。
- 推荐位置（本次检索判断）：Section II asynchronous/staleness-aware FL：更新异步优化背景，明确本文聚合质量校准与优化加速的研究边界。
- 引用边界：它改变优化器和更新协议，不应未经适配和重训就当成本文现有实验的已比较基线。
- 初评 I/C/N：4/4/4。已检查原文实验：CIFAR-10、Fashion-MNIST，对照 CA2FL/FADAS，并评估异步程度和学习率条件。
- BibTeX 键：`yan2025momentum`。

### 5. Achieving Linear Speedup in Asynchronous Federated Learning With Heterogeneous Clients

- 正式来源：IEEE TMC 24(1), 2025；状态：正式发表；原始来源/出版登记已核。
- 原始/稳定链接：[Achieving Linear Speedup in Asynchronous Federated Learning With Heterogeneous Clients](https://doi.org/10.1109/tmc.2024.3461852)。
- 类型/优先级：pure method；优先纳入。
- 原文支持的要点：DeFedAvg 允许不同客户端基于陈旧全局模型异步本地训练，并分析异质客户端下的线性加速。
- 推荐位置（本次检索判断）：Section II 异步方法段：与 FedAsync、staleness control、MasFL 共同支撑异步优化现状。
- 引用边界：原始预印本为 2024，正式 TMC 卷期为 2025；此处按正式版本计数，不能把两个版本当两篇。
- 初评 I/C/N：4/4/3。正式元数据核至 24(1):435–448；原始作者预印本 HTML 已检查实验与 wall-clock 模型，含 Fashion-MNIST/CIFAR-10。未直接取得最终排版 PDF。
- BibTeX 键：`wang2025defedavg`。

### 6. Cafe: Improved Federated Data Imputation by Leveraging Missing Data Heterogeneity

- 正式来源：IEEE TKDE 37(5), 2025；状态：正式发表；原始来源/出版登记已核。
- 原始/稳定链接：[Cafe: Improved Federated Data Imputation by Leveraging Missing Data Heterogeneity](https://pmc.ncbi.nlm.nih.gov/articles/PMC12048026/)。
- 类型/优先级：pure method；优先纳入。
- 原文支持的要点：Cafe 根据客户端缺失机制的互补性与可观测样本量形成个性化聚合权重，研究异质缺失条件的联邦插补。
- 推荐位置（本次检索判断）：Section II 新增简短“联邦缺失数据处理”段：这是比泛泛 FL 背景更近的机制来源。
- 引用边界：不能写“既有联邦插补不考虑缺失机制或聚合权重”；本文应强调部署目标、顺序选择校正及窗口可执行约束。
- 初评 I/C/N：4/4/4。已检查原始作者稿的机制、MNAR 模拟、RMSE/分布距离/下游指标及五次随机重复；2026 PMC 开放时间不改变正式 2025 年份。
- BibTeX 键：`min2025cafe`。

### 7. Federated Incomplete Tabular Data Prediction with Missing Complementarity

- 正式来源：PVLDB 18(10), 2025；状态：正式发表；原始来源/出版登记已核。
- 原始/稳定链接：[Federated Incomplete Tabular Data Prediction with Missing Complementarity](https://www.vldb.org/pvldb/vol18/p3531-miao.pdf)。
- 类型/优先级：pure method；优先纳入。
- 原文支持的要点：DARN 直接对不完整表格进行联邦预测，利用缺失分布互补性和观测样本量确定个性化权重。
- 推荐位置（本次检索判断）：Section II 联邦缺失数据段，与 Cafe 并列；用于区分“补全后预测”和“直接不完整数据预测”。
- 引用边界：它包含分类和回归，但不依赖先插补；不能写成纯插补方法，也不能把个性化缺失互补性等同于本文部署组目标。
- 初评 I/C/N：4/4/4。已检查原文表 3–5 与实验设置：Bank/Higgs/Covertype/Gas，分类与回归、多缺失互补场景及消融。
- BibTeX 键：`zhang2025darn`。

### 8. Non-Aligned Multi-Scale Data Completion for Sparse Mobile CrowdSensing

- 正式来源：IEEE/ACM IWQoS 2025；状态：正式发表；原始来源/出版登记已核。
- 原始/稳定链接：[Non-Aligned Multi-Scale Data Completion for Sparse Mobile CrowdSensing](https://cis.temple.edu/~jiewu/research/publications/Publication_files/iwqos2025-final14.pdf)。
- 类型/优先级：pure method；优先纳入。
- 原文支持的要点：该文通过尺度对齐、双向处理及 ST-/Cross-Mamba 整合非对齐多尺度感知数据，用于稀疏 MCS 补全。
- 推荐位置（本次检索判断）：Section II Sparse MCS completion：补足 2025 多尺度与异构观测范围的进展。
- 引用边界：文中的 alignment 是空间/尺度组成关系，不是本文部署目标质量对齐；评估为三类数据源、六个变量/子数据集。
- 初评 I/C/N：3/4/4。已检查原文 §VI：空气质量 PM2.5/PM10、天气湿度/温度、TaxiBJ P1/P2，含不同尺度/采样率比较。
- BibTeX 键：`liu2025nonaligned`。

### 9. StrucFormer: Structural Prior Guided Transformer for Mobile Crowdsensing Data Inference

- 正式来源：ICASSP 2025；状态：正式发表；原始来源/出版登记已核。
- 原始/稳定链接：[StrucFormer: Structural Prior Guided Transformer for Mobile Crowdsensing Data Inference](https://ieeexplore.ieee.org/abstract/document/10890429/authors)。
- 类型/优先级：pure method；优先纳入。
- 原文支持的要点：StrucFormer 将低秩结构先验融入 Transformer 的嵌入、注意力和正则化，用于稀疏群智感知数据推断。
- 推荐位置（本次检索判断）：Section II Sparse MCS completion：代表结构先验与 Transformer 结合的 2025 方法，适合一句背景定位。
- 引用边界：目前仅核到出版登记和出版商摘要；不引用未经查验的性能提升数字，不预先认定为可直接复现的强基线。
- 初评 I/C/N：3/待全文核准/待全文核准。已核作者、正式会议、DOI、1–5 页与方法摘要；原文受访问限制，完整性与数字证据不强行打分。
- BibTeX 键：`kang2025strucformer`。

### 10. Bias in Federated Learning: A Comprehensive Survey

- 正式来源：ACM Computing Surveys 57(11), 2025；状态：正式发表；原始来源/出版登记已核。
- 原始/稳定链接：[Bias in Federated Learning: A Comprehensive Survey](https://doi.org/10.1145/3735125)。
- 类型/优先级：survey；优先纳入。
- 原文支持的要点：该综述区分人口统计偏差、表现相关偏差与贡献相关偏差，并整理缓解方法及其保证。
- 推荐位置（本次检索判断）：Introduction 背景或 Section II 开头：支撑偏差分类，帮助避免把质量组成对齐泛称为所有形式的公平。
- 引用边界：综述用于概念和文献覆盖；具体机制优先引原始论文。它不能证明本文的实验优势。
- 初评 I/C/N：4/4/N/A survey。已核正式元数据和出版商可检索正文的分类/综述范围；综述不评方法数值效果，数字证据记 N/A survey。
- BibTeX 键：`benarba2025bias`。

### 11. Federated Rényi Fair Inference in Federated Heterogeneous System

- 正式来源：UAI 2025；状态：正式发表；原始来源/出版登记已核。
- 原始/稳定链接：[Federated Rényi Fair Inference in Federated Heterogeneous System](https://proceedings.mlr.press/v286/ma25a.html)。
- 类型/优先级：pure method；条件性备选。
- 原文支持的要点：FedRényi 聚合本地公平性统计并近似缺失客户端更新，以研究异步、异质系统中的群体公平与准确率。
- 推荐位置（本次检索判断）：仅在正文明确讨论统计/预测群体公平时引用；可用于说明其与本文部署组成目标的差异。
- 引用边界：公平性统计指标不等于部署质量差；不能用它替本文证明预测公平。若正文不讨论该边界，可不加入。
- 初评 I/C/N：4/4/4。已检查原文数值表：ADULT、COMPAS、DRUG、DUTCH，准确率、公平性及综合指标，含系统异质分析。
- BibTeX 键：`ma2025fedrenyi`。

### 12. Controlling Participation in Federated Learning with Feedback

- 正式来源：L4DC 2025；状态：正式发表；原始来源/出版登记已核。
- 原始/稳定链接：[Controlling Participation in Federated Learning with Feedback](https://proceedings.mlr.press/v283/cummins25a.html)。
- 类型/优先级：pure method；条件性备选。
- 原文支持的要点：FedBack 用积分反馈控制每个客户端的参与率，基于 ADMM 联邦学习分析全局收敛。
- 推荐位置（本次检索判断）：仅在讨论参与控制/跨轮反馈与本文 debt 状态的关系时引用，适合 Related Work 的一句范围比较。
- 引用边界：其动作是主动控制客户端参与；本文主要在既有可用集合上校准权重，不能把两类方法写成相同协议。
- 初评 I/C/N：4/4/3。已检查原文 §5：MNIST/CIFAR-10、100 客户端和 ADMM/FedAvg/FedProx 参照；方法假设与本文不同。
- BibTeX 键：`cummins2025fedback`。

## 与本文定位最有关的三点

1. Cafe 与 DARN 表明“根据缺失机制/互补性确定联邦权重”已有直接工作。本文的差异应落在部署目标、原子感知单元上的 R/O/U 顺序选择以及当前窗口的硬可执行约束，不能仅声称“考虑非随机缺失并重新加权”。
2. FAST、FOCUS、PHP-FL 表明 2025 年处理任意/非均匀参与已有多种机制。本文宜区分参与优化、表现公平性与感知单位代表质量，而不笼统否定既有方法。
3. MasFL 与 DeFedAvg 处理异步优化和陈旧更新，不自动解决部署目标组成问题。本文可将两者写作互补技术。将其列为 Related Work 不等于已经完成相应实验比较。

## 近期更新：不混入 2025 补额

- [CoRe-Fed, AAAI 2026](https://ojs.aaai.org/index.php/AAAI/article/view/39628)：联合嵌入对齐与参与历史相关聚合，适合继续检查本文 debt/history 相关表述的边界。正式元数据为 40(29):24458–24466，DOI 10.1609/aaai.v40i29.39628。本轮核对到摘要和正式书目，未作完整方法评审。
- [Toward Efficient and Scalable Asynchronous Federated Learning via Stragglers Version Control, TMC 2026](https://cis.temple.edu/~jiewu/research/publications/Publication_files/Toward_Efficient_and_Scalable_Asynchronous_Federated_Learning_via_Stragglers_Version_Control.pdf)：DVAFL 通过版本控制处理慢客户端更新，正式 PDF 为 25(2):2627–2643，属于可补充的异步机制背景。DOI 10.1109/TMC.2025.3609568 中的 2025 不能取代正式卷期 2026。
- 上轮已核的 FedIPW 2026、FedPALS v2、SEAFL IPDPS 2025 和 FLOSS ACM 2025 仍应保留或更新，不重复算作新增文献。

## 质量评分口径与未完成项

I/C/N 分别为洞见、完整性、实验数字证据的检索阶段 1–5 初评；不是对论文录用概率的评分，也不表示复现成功。评分依据原始机制、可见证明和实验设计。综述的实验数字证据不适用。StrucFormer 只有元数据与摘要通过核验，完整性和数字证据保留待全文核准，不伪造评分。

公开原文重点阅读：FAST、FOCUS、PHP-FL、MasFL、Cafe、DARN、Non-Aligned、FedRényi、FedBack；DeFedAvg 阅读 2024 作者预印本 HTML，并以出版商登记的 2025 TMC 信息生成正式条目。StrucFormer 和综述未获得本地完整排版 PDF。

## 下一步写作交接

建议由 ccf-paper-writer 按 insertion-plan.md 做局部整合，由 ccf-integrity-auditor 再核对实际引用、年份计数及语境。不因本次检索自动启动实验或宣称新基线收益。

## 检索检查

公开关键词检索、来源过滤、标题/DOI 去重、发表年份核验、类型标注、引用位置和机制边界已完成。无新数据集检索任务；无实验数值填入本文；无未发表材料对外搜索。个别原文不可直接访问已逐条标明。