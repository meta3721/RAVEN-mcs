# 检索记录

目的：补充与既有 RAVEN-MCS 主张匹配的正式文献，优先填补 2025 年缺口；不是新实验设计或方法改写。

## 使用的公开检索式

- 2025 crowdsensing data completion / data inference
- federated learning biased client participation 2025 ICML ICLR NeurIPS
- asynchronous federated learning 2025 staleness / client heterogeneity
- federated missing not at random / missing complementarity / federated imputation
- FAST / FOCUS / PHP-FL / Momentum-Driven Adaptivity / DeFedAvg 公开题名
- Cafe / DARN / StrucFormer / Non-Aligned Multi-Scale 公开题名
- Bias in Federated Learning: A Comprehensive Survey

## 来源与处理

检索发现优先用论文题名与公开关键词；核验使用 NeurIPS/IJCAI/PMLR/PVLDB 官方论文集、IEEE/ACM 出版商、作者公开原文、PMC 作者稿和 Crossref 精确 DOI 登记。排除 MDPI、mdpi-res 及低质量/不相关来源；搜索命中这些域未进入推荐和评分。

Crossref 原始元数据保存至 sources/*.json；公开原文保存八份 PDF 及其抽取文本。DeFedAvg PDF 下载因证书校验失败，没有关闭校验绕过，改读 arXiv 原始 HTML。StrucFormer 正文访问受限，未假定读过全文。

## 集中筛选的 28 条记录

- FAST: A Lightweight Mechanism Unleashing Arbitrary Client Participation in Federated Learning：保留：优先纳入
- Exact and Linear Convergence for Federated Learning under Arbitrary Client Participation is Attainable：保留：优先纳入
- A Fair Federated Learning Method for Handling Client Participation Probability Inconsistencies in Heterogeneous Environments：保留：优先纳入
- Momentum-Driven Adaptivity: Towards Tuning-Free Asynchronous Federated Learning：保留：优先纳入
- Achieving Linear Speedup in Asynchronous Federated Learning With Heterogeneous Clients：保留：优先纳入
- Cafe: Improved Federated Data Imputation by Leveraging Missing Data Heterogeneity：保留：优先纳入
- Federated Incomplete Tabular Data Prediction with Missing Complementarity：保留：优先纳入
- Non-Aligned Multi-Scale Data Completion for Sparse Mobile CrowdSensing：保留：优先纳入
- StrucFormer: Structural Prior Guided Transformer for Mobile Crowdsensing Data Inference：保留：优先纳入
- Bias in Federated Learning: A Comprehensive Survey：保留：优先纳入
- Federated Rényi Fair Inference in Federated Heterogeneous System：保留：条件性备选
- Controlling Participation in Federated Learning with Feedback：保留：条件性备选
- FedImpute: Personalized federated learning for data imputation with clusterer and auxiliary classifier：真实 ESWA 2025；未进优先包，Cafe/DARN 更接近缺失机制加权和更强定位需要。
- Indirect-Communication Federated Learning via Mobile Transporters：真实 TMC 2025；未进优先包，本文无 transporter 路由机制，关系较间接。
- CoRe-Fed: Bridging Collaborative and Representation Fairness via Federated Embedding Distillation：保留 2026 更新提示；不计入 2025。
- Toward Efficient and Scalable Asynchronous Federated Learning via Stragglers Version Control：保留 2026 更新提示；DOI 含 2025，不按 DOI 改年份。
- A New Data Completion Perspective on Sparse CrowdSensing: Spatiotemporal Evolutionary Inference Approach：已引用 2025，去重不新增。
- Rethinking the Effect of Sparse Data Completion on Sparse Mobile Crowdsensing Tasks：已引用 2025，去重不新增。
- Debiasing Federated Learning with Correlated Client Participation：已引用 2025，去重不新增。
- SEAFL: Enhancing Efficiency in Semi-Asynchronous Federated Learning through Adaptive Aggregation and Selective Training：已引用，更新为正式 IPDPS 2025 不增加去重数量。
- FLOSS: Federated Learning with Opt-Out and Straggler Support：已引用正式 2025，arXiv 2026 修订不新增。
- Who Trains Matters: Federated Learning under Enrollment and Participation Selection Biases：已引用 2026，不新增。
- Overcoming Label Shift with Target-Aware Federated Learning：已引用 2024/v2 2025，不能假定已录用或算独立新增。
- Federated Multiple Imputation for Variables that Are Missing Not At Random in Distributed Electronic Health Records：医学任务较远；PMC 标 2025 上网但会刊 2024，不能直接用于 2025 补额。
- FedHAN: A Cache-Based Semi-Asynchronous Federated Learning Framework Defending Against Poisoning Attacks in Heterogeneous Clients：安全攻击是主要任务，与当前论文范围偏离，未选。
- The Power of Bias: Optimizing Client Selection in Federated Learning With Heterogeneous Differential Privacy：主要约束来自隐私预算，本论文无此机制，未选。
- Federated causal discovery with missing data in a multicentric study on endometrial cancer：因果发现及医疗目标不同，未选。
- AFBS: buffer gradient selection in semi-asynchronous federated learning：与异步相关，但发表状态/正文机制未完整核验，未纳入已核候选。

## 未知与清理

- StrucFormer 的完整数字证据和复现细节待原文；推荐范围限已核摘要。
- 综述有正式元数据与出版商可检索内容，未取得完整本地 PDF，不将它用于方法数值证明。
- 搜索曾将某篇材料邻近的 arXiv:2412.12837 与综述混在结果中；打开原始 arXiv 后发现是另一篇隐私攻击论文，已排除该链接映射，未写入候选 BibTeX。
- 部分模糊搜索或网页保护导致不可直接打开时，不据“无全文”判论文虚假；只记录实际核到的层级。
- 该检索未重跑任一实验，论文文件未编辑。

## 写作交接

以 insertion-plan.md 将每篇来源对应到具体语义位置；严格区分原文事实与本文差异判断。候选包中的对比属于文献机制比较，不表示完成其模型复现。