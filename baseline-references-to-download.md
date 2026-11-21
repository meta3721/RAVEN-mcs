# 对比方法的参考文献与下载来源

**用途**：为 RAVEN-MCS 的方法对比复现/引用取件。
**生成日期**：2026-09-19
**范围**：论文中实际作为 comparator 出现的方法（不是全部 54 条参考文献）。

> ⚠️ **重要前提**：论文里这些 baseline 写的都是 **"windowed adaptation / not an official reproduction"**。
> 也就是说**没有现成的 FedAU-Window / ObsUse-Window / TimeAlign-Agg 代码可以下载**，
> 只有它们赖以改编的**原始方法论文**可下载。下表把两者分开了。

---

## A. 有原始论文可下载的 comparator（4 个）

### A1. FedAvg — 对应论文中的 `FedAvg-Window`

- **标题**：Communication-Efficient Learning of Deep Networks from Decentralized Data
- **作者**：Brendan McMahan, Eider Moore, Daniel Ramage, Seth Hampson, Blaise Agüera y Arcas
- **出处**：AISTATS 2017, PMLR vol. 54, pp. 1273–1282
- **下载**：
  - 官方 PDF（PMLR，永久开放）：<http://proceedings.mlr.press/v54/mcmahan17a/mcmahan17a.pdf>
  - 预印本：<https://arxiv.org/abs/1602.05629>
  - DOI：10.48550/arXiv.1602.05629

### A2. FedAsync — 对应论文中的 `FedAsync-Window`

- **标题**：Asynchronous Federated Optimization
- **作者**：Cong Xie, Oluwasanmi Koyejo, Indranil Gupta
- **出处**：arXiv:1903.03934（论文中著录为 OPT 2020 workshop）
- **下载**：
  - arXiv 摘要页：<https://arxiv.org/abs/1903.03934>
  - arXiv PDF：<https://arxiv.org/pdf/1903.03934>
  - 参考实现（第三方，非作者官方）：<https://github.com/yuxuan18/fedAsync>

### A3. Local-Hàjek — 对应论文中的 `Local-Hàjek`（客户端内逆概率/Hàjek 归一化）

由两篇经典统计文献支撑，都不是机器学习论文：

- **Horvitz–Thompson 1952**
  - 标题：A Generalization of Sampling Without Replacement From a Finite Universe
  - 出处：JASA, vol. 47, no. 260, pp. 663–685, 1952
  - DOI：<https://doi.org/10.1080/01621459.1952.10483446>
  - 说明：JSTOR 付费；多数高校图书馆有权限。
- **Hájek 1971（比估计量）**
  - 标题：Comment on "An Essay on the Logical Foundations of Survey Sampling, Part One"
  - 出处：*Foundations of Statistical Inference*（Godambe & Sprott 编），Holt, Rinehart and Winston, 1971, pp. 236–242
  - 说明：**书籍章节，无公开 PDF**。需要图书馆或馆际互借；若只需引用 Hàjek 比估计量的标准性质，可改引更易获取的综述（见 D 节）。

### A4. 参与偏差方法 — 对应论文中的 `FedAU-Window`

- **标题**：A Lightweight Method for Tackling Unknown Participation Statistics in Federated Averaging
- **作者**：Shiqiang Wang, Mingyue Ji
- **出处**：ICLR 2024, pp. 854–893（论文中著录为 "FedAU"）
- **下载**：
  - OpenReview（开放获取）：<https://openreview.net/forum?id=7J4e5NPcEs>
  - 官方 PDF：<https://openreview.net/pdf?id=7J4e5NPcEs>
  - IBM 研究页：<https://research.ibm.com/publications/a-lightweight-method-for-tackling-unknown-participation-statistics-in-federated-averaging>

### A5. TimeAlign-Agg 所依据的联邦 MCS 补全工作

论文原文写的是 *"a windowed time-aware aggregator **in the spirit of** [wang2026federated], not an official reproduction"*。

- **标题**：Federated Learning-Based Distributed Data Completion in Sparse Mobile CrowdSensing
- **作者**：En Wang, Baoju Li, Wenbin Liu, Zengyi Han, Cong Wang, Ximing Li, Jie Wu
- **出处**：IEEE Transactions on Mobile Computing, vol. 25, no. 5, pp. 6784–6800, 2026
- **下载**：
  - 作者自存 PDF（吴杰教授主页，公开）：<https://cis.temple.edu/~wu/research/publications/Publication_files/Federated_Learning-Based_Distributed_Data_Completion_in_Sparse_Mobile_CrowdSensing.pdf>
  - IEEE Xplore：<https://ieeexplore.ieee.org/document/10848376>
  - （注意：这条在上一轮核实中确认存在且著录正确。）

---

## B. 论文自建、无外部文献的 comparator（不必下载）

| 方法名 | 论文中的定义 | 说明 |
| --- | --- | --- |
| `ObsUse-Window` | 应用本文的观测与可用更新校正，去掉 Design/P2/debt | **本文自己的消融式基线**，无外部出处 |
| `TwoStage-Hàjek` | 同一 Hàjek 族顺序应用于机会层与观测层 | 本文组合，出处即 A3 两条 |
| `Inst-Cal` | P2 保留当前组校准与参考项，不用债务 | 本文组件消融 |
| `Debt-Cal` | 用债务与当前组校准，但 ζ=p=q=1 | 本文组件消融 |
| `Central-All` | 集中使用全部有效观测 | 参照上界，非文献方法 |
| `Central-Delivered` | 集中使用可用更新对应的观测 | 参照量 |
| `RAVEN-SimOracle` | 用生成的真值 ζ、真实 p 与 Monte-Carlo q | 受控场景下的校正参照 |

---

## C. 想直接拿可用代码的话（工程捷径）

这些是维护良好的开源联邦学习库，内含 FedAvg 等标准 baseline 实现，可以用来对齐/校验你自己的窗口化改编：

- **AFL-Lib**（MobiCom'25 Poster，异步 FL 库与 benchmark）：<https://github.com/boyi-liu/AFL-Lib>
- **FedML**（研究型 FL 库）：<https://github.com/FedML-AI/FedML>
- **federated-learning-lab**（含 FedAvg / FedProx / SCAFFOLD 从零实现 + CI）：<https://github.com/waynehacking8/federated-learning-lab>
- **SCAFFOLD baseline**：<https://github.com/FabioTur-dev/SCAFFOLD_baseline>

> 这些是**第三方实现**。若用于论文，必须像现在这样标注"windowed adaptation, not an official reproduction"，不要写成官方复现。

---

## D. 如果 Hàjek 1971 拿不到（替代引用）

Hàjek 比估计量的标准性质在下面这些开放来源中有完整陈述，可在正文引用时替换或补充：

- Särndal, Swensson & Wretman, *Model Assisted Survey Sampling*, Springer, 1992（第 5–6 章）——经典教材。
- 综述型开放材料：搜索 "Hajek ratio estimator consistency" 可找到多份公开讲义。
- 你论文的 `reference.bib` 里已有 `shimodaira2000covariate` 与 `robins1994estimation`，这两篇都可公开获取，可作为逆概率加权的可引来源。

---

## E. 取件清单（按优先级）

| 优先级 | 文献 | 链接 | 可得性 |
| --- | --- | --- | --- |
| P0 | FedAvg (McMahan 2017) | <http://proceedings.mlr.press/v54/mcmahan17a/mcmahan17a.pdf> | 开放 |
| P0 | FedAsync (Xie 2019) | <https://arxiv.org/pdf/1903.03934> | 开放 |
| P0 | FedAU (Wang & Ji, ICLR 2024) | <https://openreview.net/pdf?id=7J4e5NPcEs> | 开放 |
| P0 | FL-based completion (Wang 2026, TimeAlign 依据) | <https://cis.temple.edu/~wu/research/publications/Publication_files/Federated_Learning-Based_Distributed_Data_Completion_in_Sparse_Mobile_CrowdSensing.pdf> | 开放 |
| P1 | Horvitz–Thompson 1952 | <https://doi.org/10.1080/01621459.1952.10483446> | 机构订阅 |
| P1 | Hájek 1971 | 书籍章节，无公开 PDF | 图书馆 / 馆际互借 |
