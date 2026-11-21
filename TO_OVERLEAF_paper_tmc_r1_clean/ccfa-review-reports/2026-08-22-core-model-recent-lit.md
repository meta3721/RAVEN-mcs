# 核心模型文献近3年（2024-2026）联网检索报告

检索日期：2026-08-22
目的：核实论文引用的核心方法/模型是否有 2024-2026 更近的论文可以补充或替换
检索范围：异步联邦、参与偏差/部分参与、目标分布对齐、MCS 稀疏补全

---

## 一、论文当前核心引用年龄问题

论文 32 条方法/模型引用中，近3年（2024-2026）18 条（56%），**早于2024 的 14 条**集中在：

| 方向 | 当前引用（偏旧） | 近3年新工作？ |
|---|---|---|
| **异步联邦** | FedAsync 2019、liu2023adaptive 2023 | ✅ 大量 2024-2026 |
| **参与偏差/部分参与** | FedProx 2020、SCAFFOLD 2020、FedVARP 2022、unified 2022、anchor 2023 | ✅ 大量 2024-2026 |
| **目标对齐/选择偏差** | agnostic FL 2019 | ✅ 有 2026 直接相关 |
| **MCS 稀疏补全** | wang2023outlier/spatiotemporal 2023 | ✅ 部分（已引 2024-2026 若干） |

---

## 二、检索到的 2024-2026 候选新文献

### A. 异步联邦学习（可补充/替换 FedAsync 2019、liu2023adaptive 2023）

| 论文 | 年份/venue | 核心贡献 | 相关性 |
|---|---|---|---|
| [Taming Staleness in Asynchronous Federated Learning With System Heterogeneity](https://www.computer.org/csdl/journal/td/5555/01/11659786/2j6urT98PRK) | IEEE TD（2026） | 系统异构下的 staleness 控制 | **高**：直接对应论文的 staleness 维度 |
| [Toward Efficient and Scalable Asynchronous Federated Learning via Stragglers Version Control](https://xplorestaging.ieee.org/document/11162622) | IEEE（2026） | 落后客户端版本控制，可扩展异步 FL | **高**：异步 FL 效率 |
| [ASMAFL: Adaptive Staleness-Aware Momentum Asynchronous FL in Edge Computing](https://ieeexplore.ieee.org/document/10772339) | IEEE（2024） | 自适应 staleness 感知动量异步 FL | **高**：异步+staleness+边缘 |
| [FedSTEP: Asynchronous and Staleness-Aware Personalization](https://dl.acm.org/doi/epdf/10.1145/3746252.3761166) | ACM（2025） | 异步+staleness 个性化 | 中 |
| [Staleness-Aware Semi-Asynchronous FL With Adaptive Learning Rates and Non-IID](https://cd.nstl.gov.cn/paper_detail.html?id=696295e8834474dec33ef6283a6a159b) | IEEE（2026） | 半异步+自适应学习率 | **高**：半异步与本论文接近 |
| [SEAFL: Enhancing Efficiency in Semi-Asynchronous FL Through Adaptive Aggregation](https://ieeexplore.ieee.org/abstract/document/11078406) | IEEE（2025） | 半异步自适应聚合 | **高** |
| [Asynchronous FL With Nonconvex Client Objectives and Heterogeneous Dataset](https://ieeexplore.ieee.org/abstract/document/11202971) | IEEE（2026） | 非凸+异构数据的异步 FL 理论 | **高**：理论+异步 |
| [A Byzantine-robust asynchronous FL method on Non-IID data](https://www.sciencedirect.com/science/article/abs/pii/S0925231226016991) | Neurocomputing（2026） | 拜占庭鲁棒异步 | 中 |

### B. 参与偏差/部分参与（可补充/替换 FedProx/SCAFFOLD/FedVARP/anchor 2020-2023）

| 论文 | 年份/venue | 核心贡献 | 相关性 |
|---|---|---|---|
| [FedCure: Mitigating Participation Bias in Semi-Asynchronous FL with Non-IID Data](https://ojs.aaai.org/index.php/AAAI/article/view/39176) | AAAI 2026 | 半异步参与偏差 | **已引用** ✅（chen2026fedcure） |
| [Who Trains Matters: Federated Learning under Enrollment and Participation Selection Biases](https://ar5iv.labs.arxiv.org/html/2604.26604) | arXiv 2026 | 注册偏差+参与选择偏差（形式化 π^part） | **极高**：与论文"两层三阶段非随机选择"几乎同框架 |
| [Debiasing FL with Correlated Client Participation](https://mlanthology.org/iclr/2025/sun2025iclr-debiasing/) | ICLR 2025 | 相关参与偏差去偏 | **已引用** ✅（sun2025debiasing） |
| [Addressing Data Quality Decompensation via Dynamic Client Selection](https://arxiv.org/html/2505.21219v1) | arXiv 2025 | 动态客户端选择减轻过采样偏差 | 中 |
| [GC-Fed: Gradient centralized FL with partial client participation](https://www.sciencedirect.com/science/article/abs/pii/S1566253526000278) | ISJ（2026） | 梯度集中化+部分参与 | 中 |
| [Server-Proximal Aggregation for FL under Partial Participation](https://icml.cc/virtual/2026/poster/63720) | ICML 2026 | 部分参与下的服务器近端聚合 | **高**：部分参与理论 |
| [A Grouping-based FL Framework with Fairness Guarantee](https://ieeexplore.ieee.org/document/11272699) | IEEE（2026） | 分组+公平 | 中 |

### C. 目标分布对齐/非随机选择（可补充/对比 agnostic FL 2019）

| 论文 | 年份/venue | 核心贡献 | 相关性 |
|---|---|---|---|
| [Who Trains Matters (同上)](https://chatpaper.com/chatpaper/paper/273521) | arXiv 2026 | 注册+参与选择偏差 | **极高**：最接近的相关工作 |
| [Distribution Alignment for One-Shot FL via Optimal Transport](https://icml.cc/virtual/2026/poster/64658) | ICML 2026 | 最优传输分布对齐 | 中：对齐方法 |
| [Dual debiasing learning for single-source federated domain generalization](https://www.sciencedirect.com/science/article/abs/pii/S0925231226016498) | Neurocomputing（2026） | 双重去偏+域泛化 | 中 |

### D. MCS 稀疏补全（部分已引，可补充）

| 论文 | 年份/venue | 核心贡献 | 相关性 |
|---|---|---|---|
| [Privacy-Preserving Federated Active Learning for Data Completion in Sparse Crowdsensing](https://ieeexplore.ieee.org/document/11587349) | IEEE（2026） | 隐私保护联邦主动学习补全 | **高**：联邦补全新方向（比 wang2026federated 更新） |
| [Probabilistic Spatio-Temporal Data Inference with Conditional Diffusion Model](https://ieeexplore.ieee.org/document/11359234) | IEEE（2026） | 条件扩散模型概率推断 | **中-高**：补全新方法范式 |

---

## 三、建议（供你人工核实后决策）

### 优先级最高（强烈建议考虑）

1. **"Who Trains Matters: FL under Enrollment and Participation Selection Biases"（arXiv 2026）**
   - **风险最高**：它形式化了"注册偏差 + 参与选择偏差"（π^part 公式），与论文强调的"两层三阶段非随机选择"框架非常接近
   - **必须人工核实**：若该工作与论文的核心区别不足，新颖性定位可能需要调整；即使不同，也应在 Related Work 中明确讨论
   - [查看原文](https://ar5iv.labs.arxiv.org/html/2604.26604)

2. **异步 FL 的 staleness/半异步新工作（2024-2026）**
   - 当前只引 FedAsync 2019 + liu2023adaptive 2023，**缺 2024-2026 的 staleness 研究**
   - 候选：[Taming Staleness (TD 2026)](https://www.computer.org/csdl/journal/td/5555/01/11659786/2j6urT98PRK)、[ASMAFL (2024)](https://ieeexplore.ieee.org/document/10772339)、[SEAFL (2025)](https://ieeexplore.ieee.org/document/11078406)

### 补充性建议

3. **MCS 补全**：补引 [Privacy-Preserving FL Active Learning (2026)](https://ieeexplore.ieee.org/document/11587349)（比 wang2026federated 更新的联邦补全）

4. **参与偏差**：补引 [Server-Proximal Aggregation (ICML 2026)](https://icml.cc/virtual/2026/poster/63720)（部分参与理论）

---

## 四、审稿风险提示

| 风险 | 等级 | 说明 |
|---|---|---|
| "Who Trains Matters" 可能构成直接竞争/重叠 | 🔴 高 | 需人工核实其与论文"三层选择"的区别 |
| 异步 FL 引用偏旧（2019/2023） | 🟡 中 | 补 2024-2026 staleness 文献可显著提升定位 |
| 参与偏差引用偏旧（2020-2023） | 🟡 中 | FedCure 2026/sun2025debiasing 已引，但可补 ICML 2026 |

## 需要你决策

以上候选均为网络检索结果，**未经过认证的真实性与内容深读**。建议：
1. 先人工核实 "Who Trains Matters" 与论文的区别（最重要）
2. 选择 2-3 篇异步 FL 新文献补入 Related Work
3. 让 `ccf-literature-searcher` 做标准模式深检索（含论文聚类、机会图谱）或 `ccf-integrity-auditor` 核实候选条目真实性
