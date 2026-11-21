# 单窗可达性归因实验方案

日期：2026-10-18。对应大纲《五个候选方向的简要大纲》第 1 条。本文件是实验协议，不是论文段落，不包含本方案的测量结果。

```text
Mode: design
Venue and assumptions: IEEE TMC，方法加测量。当前稿件已经报告开发几何下的可调质量，以及正式协议里 K≤3 时可行集退化为均匀权重。本方案只在已发表正式窗口的已到达客户端上，把目标质量拆成支持缺失、约束钉死和可调三部分，并把到目标的可行距离拆到单纯形、cap 和 ESS。组成估计的位移只有在该窗已经存有投影前参考向量时才计算。诊断不改预测，不写成预测风险下界。
No-fabrication status: 没有运行本方案。结果格全部是 TBD。不得把开发几何表、P0 的可调质量、City Scanner 主表或 Adam 确认集填进结果格。
Next CCFA owner: 用户决定是否执行只读归因。数字出来之后由 ccf-integrity-auditor 核对分解恒等式。未经用户点名，不交给 ccf-paper-writer，不改 main.tex。
```

## 主张与证据

要回答的问题：某一关闭上目标难以匹配，质量落在当前没有客户端的组、落在已经出现但被 cap 或 ESS 钉住的组，还是落在参考向量相对冻结目标的位移上。

不回答的问题：下一窗会不会补上缺失的组。把未消费更新留到后一窗（方法三，已有消费规则下保留池与到达窗相同）。等待更久再关闭（方法二，维持停止）。向未到达的客户端发请求（方法四）。检测器是否该切换 Design。几何距离是不是 RMSE 的下界。

| 主张 | 审稿问题 | 需要的证据 | 数据 | 对照 | 指标 | 占位 | 状态 |
| --- | --- | --- | --- | --- | --- | --- | --- |
| 正式自然窗口上，正目标质量可以分成缺失、钉死、可调，三者相加等于该窗正目标质量 | 不可调是缺人，还是人在但权重动不了 | 只读分解，同一到达集合 | 已有 EventTrace 的正式块 | 同一 \(M,\mu,\mathcal C\) 上的三个互斥部分 | \(\mu_{\mathrm{miss}},\mu_{\mathrm{pin}},\mu_{\mathrm{adj}}\) | TBD | planned |
| 到 \(\mu\) 的 \(\ell_1\) 可行距离可以分成单纯形缺口和 cap、ESS 的增量 | 现有 \(K=8\) 子集上的 cap/ESS 表没有回答正式窗口上哪条约束在起作用 | 同一 \(M\) 上四个嵌套约束集 | 同上 | 单纯形、加 cap、加 ESS、完整 \(\mathcal C\) | \(d_{\mathrm{simplex}},d_{\mathrm{cap}},d_{\mathrm{ESS}},d_{\mathcal C}\) | TBD | planned |
| \(K\le 3\) 的退化单独成层，不把整块的均值当成新发现 | 站点上约八成窗口只有均匀权重，这是否吃掉了全部分解 | 预先分层 \(K\le 3\) 与 \(K>3\) | 同上 | 两层各自的质量份额 | 两层的三项质量 | TBD | planned |
| 参考向量相对 \(\mu\) 的位移可以和几何分开 | 配权点偏离目标，是因为 \(\mathcal C\) 到不了，还是因为送进去的参考就不是 \(\mu\) | 仅当该窗存有投影前参考 | 存有该向量的窗口 | \(\alpha(\widehat r)\) 对 \(\alpha(\mu)\) | \(\delta_{\mathrm{ref}},\delta_{\mathrm{dec}}\) | TBD | 缺向量则为 blocked，不阻断前三行 |

## 执行约束

- 执行者不得修改 `src/`，不得修改 `TO_OVERLEAF_paper_tmc_r1_clean/` 下的论文、附录和 bib。
- 新脚本和新输出只进入 `results_m1_attribution/round_v1/`。不得写入 `results_reachability_detector_v1/`，也不得写入 `results_xw_pool/`。
- 需要已有的极值或投影函数时，从外层脚本导入。导入做不到就在本目录重写同一数学定义。不能改包内源文件，也不能改 `results_main_rebuild_r1/diagnose_geometry.py`。
- 不新增种子，不训练，不生成 EventTrace，不重采样 \(R/O/U\)。本方案不创建 `runs/`。
- 不恢复 OF-v1，不实现带证书的可达性检测器，不把 2026-10-12 停在方法身份冲突的那份检测器协议从 G1 接着跑。
- 不把已消费更新留到后一窗，不读 \(q^{\mathrm{use}}\)，不用 \(S_{\max}\) 构造候选池。
- 不取代已经授权的 City Scanner 完整 P2 对简单投影比较。
- 开发几何的种子 41001–41003、固定 \(K\in\{4,8,16\}\) 子集，以及该表使用的 cap 与 ESS 比例，不进入本方案。
- Python 使用 `.venv_new\Scripts\python.exe`。

## 对象

每一行是已发表正式轨迹上的一次关闭 \(r\)。客户端集合 \(A_r\) 是该关闭日志里已经交付、并在该关闭消费的客户端。一个客户端一行；若同一客户端有多条已交付尝试，保留版本 \(\sigma\) 最大的一条。这是日志里的到达窗集合，不是反事实保留池。

组标签从 `opportunity_features` 读取，规则与 `results_xw_pool/round_v1/p0_geometry.py` 的 `group_from_features` 相同。读不出唯一冻结 \(\mu\) 键的尝试，该块记为 blocked，不补标签。

冻结目标：

- NSW-Traffic：`configs/frozen/e3_multidataset_protocol_closure/traffic/public_target.json`
- SensorScope、U-Air：`artifacts/e3_semantic_alignment_and_runner_integration_closure_r1/` 下各自的 `E3_*_TARGET_SEMANTICS_R2.json`
- City Scanner 与 T-Drive：沿用 P0 的阻断。访问占用没有组字段；Pilot 2 没有四区域冻结 \(\mu\)；T-Drive 没有组字段。不把均匀 0.25 当作 \(\mu\)，不用微型夹具。

可行集与 P0 预注册相同，不重新选择：

\[
\overline\alpha_r=\min\{1,\max\{\alpha_{\max},1/K\}\},\qquad
\overline E_r=\min\{E_{\min},K\},
\]

\(\alpha_{\max}=0.5\)，\(E_{\min}=3\)。\(K\le 3\) 时 \(\overline E_r=K\)，可行集只有均匀权重。阈值 0.01 沿用正文：组区间宽度 \(W_g\ge 0.01\) 才算可调。看到分解之后不改这两个数，也不改阈值。

## 三项质量

记 \(n_g\) 为 \(A_r\) 中组 \(g\) 的客户端数。正目标质量的组分成互斥的三类：

- 缺失：\(n_g=0\)。质量 \(\mu_{\mathrm{miss}}\)。
- 钉死：\(n_g>0\) 且 \(W_g<0.01\)。质量 \(\mu_{\mathrm{pin}}\)。
- 可调：\(W_g\ge 0.01\)。质量 \(\mu_{\mathrm{adj}}\)。

\(W_g\) 是组 \(g\) 的组成行在 \(\mathcal C_r\) 上的最大值减最小值。三者之和必须等于该窗正 \(\mu\) 之和。容差 \(10^{-8}\)。超出容差的窗口作废，不删掉后重算阈值。

\(\mu_g=0\) 的组不进入三项。客户端落在这类组上时，记入列 `off_target_clients`，不把它算成缺失，也不把它算成可调。

## 四段距离

在同一组成矩阵 \(M\) 上计算到 \(\mu\) 的 \(\ell_1\) 距离。\(\alpha\) 始终在概率单纯形上。

| 记号 | 额外约束 | 含义 |
| --- | --- | --- |
| \(d_{\mathrm{simplex}}\) | 无 | 只换支持、不施加 cap 和 ESS 时还剩的距离 |
| \(d_{\mathrm{cap}}\) | \(\alpha_k\le\overline\alpha_r\) | cap 单独加上之后的距离 |
| \(d_{\mathrm{ESS}}\) | \(\sum_k\alpha_k^2\le 1/\overline E_r\) | ESS 单独加上之后的距离 |
| \(d_{\mathcal C}\) | cap 与 ESS 同时加上 | 正式可行集上的距离 |

报告四个数，以及三个增量 \(d_{\mathrm{cap}}-d_{\mathrm{simplex}}\)、\(d_{\mathrm{ESS}}-d_{\mathrm{simplex}}\)、\(d_{\mathcal C}-\max(d_{\mathrm{cap}},d_{\mathrm{ESS}})\)。四个距离都保留。不允许在看完结果后只留下增量最大的那一条当作原因。

数值要求：\(d_{\mathcal C}\ge d_{\mathrm{cap}}\ge d_{\mathrm{simplex}}\) 且 \(d_{\mathcal C}\ge d_{\mathrm{ESS}}\ge d_{\mathrm{simplex}}\)，容差 \(10^{-6}\)。求解器的可行性违约超过 \(10^{-7}\) 则该窗作废。不作 cap 或 ESS 的网格。

一行一个组的窗口另有恒等式：\(d_{\mathrm{simplex}}=2\mu_{\mathrm{miss}}\)。该窗不满足时，整块停止并写出偏离，不把恒等式改成拟合。组行不是独热向量时，这条恒等式不适用，距离四元组仍要计算，并在该窗标记 `row_type=mixed`。

## 估计位移

几何三项和四段距离只用组标签、\(\mu\) 和 \(\mathcal C\)。它们把组标签当成已经观测到的元数据。

估计位移只在该窗的存档里同时有这两样时计算：投影前的参考向量 \(\widehat r\)，以及它和当前客户端行的对齐。定义

\[
\delta_{\mathrm{ref}}=\lVert \widehat r-\mu\rVert_1,\qquad
\delta_{\mathrm{dec}}=\lVert \alpha(\widehat r)-\alpha(\mu)\rVert_1.
\]

\(\alpha(\cdot)\) 是投到同一个 \(\mathcal C_r\) 上的投影。\(\widehat r\) 与 \(\mu\) 都先归一到组和为 1 的单纯形上再算 \(\delta_{\mathrm{ref}}\)。

没有这对向量的窗口，两列写空，块状态在估计列上是 blocked。几何表照常完成。不重新拟合 \(q\)，不从旧运行读取 \(q^{\mathrm{use}}\) 来制造 \(\widehat r\)，不把开发轨迹里的 `beta` 拷到正式种子上。

## 分层

每一块先按窗口分成 \(K\le 3\) 和 \(K>3\)，再对种子取均值。全窗均值可以附在表外，不作为主行。\(K\le 3\) 层预期 \(\mu_{\mathrm{adj}}=0\)、可行集为均匀权重。这一层用来核对定义，不用来宣布新的约束发现。

同一窗口同时报告三个协变量，不另做实验：客户端数 \(K\)、出现的组数、\(d_{\mathcal C}\)。组出现率是 \(n_g/K\)，写进窗口文件，不单独立项。

## 与已有几何的关系

正文开发几何在另一套种子和另一套 cap 上计算可调质量与不可达质量。本方案不重算那张表，也不把它的均值写进结果格。

P0 已经在 NSW-Traffic、SensorScope、U-Air 的正式轨迹上算过逐窗 \(\mu_{\mathrm{adj}}\) 和 \(K\le 3\) 份额，并且在写成的消费规则下保留池与 \(A_r\) 逐窗相同。本方案的 \(\mu_{\mathrm{adj}}\) 必须与 `results_xw_pool/round_v1/P0_WINDOWS.csv` 里同一 `block,seed,window` 的 `adj_A` 一致，容差 \(10^{-8}\)。不一致则停止，不取平均，不改公式。P0 没有缺失质量和钉死质量，那两列不能从 P0 抄出。

`diagnose_geometry.py` 里的 `projection_distance` 是参考向量到其投影的距离，不是 \(d_{\mathcal C}\)。两列并列时必须分开命名。

## 数据

| 块 | 角色 | 种子 | 几何分解 | 估计位移 |
| --- | --- | --- | --- | --- |
| NSW-Traffic | 正式自然窗口。P0 上逐窗可调质量为 0 | 该块正式轨迹已有种子 | 必做 | 有 \(\widehat r\) 才做 |
| SensorScope | 正式自然窗口。\(K\le 3\) 份额高 | 同上 | 必做 | 同上 |
| U-Air | 同上 | 同上 | 必做 | 同上 |
| City Scanner 访问占用 | 应用块 | 已发表配对种子 | 组字段和冻结 \(\mu\) 到齐才做；当前按 P0 为 blocked | 同左 |
| City Scanner Pilot 2 | 应用块 | 同上 | 同上 | 同左 |
| T-Drive | 真实 \(R\) | 已发表种子 | 同上；不用微型夹具 | 同左 |
| 种子 41001–41003 | 开发几何 | 不进入 | 不做 | 不做 |

## 完成与停止

本方案没有训练闸门。一块几何完成，是指每个未作废窗口满足质量分解恒等式和距离单调性。一块可以在估计列上 blocked 而几何列完成。

出现任一条即停，不改定义后重跑：

- 质量三项之和偏离正 \(\mu\) 之和，超过 \(10^{-8}\)。
- 距离违反单调性，超过 \(10^{-6}\)。
- 独热窗口上 \(d_{\mathrm{simplex}}\) 偏离 \(2\mu_{\mathrm{miss}}\)，超过 \(10^{-6}\)。
- \(K\le 3\) 的窗口出现非零 \(\mu_{\mathrm{adj}}\)。
- 与 P0 同一窗口的 \(\mu_{\mathrm{adj}}\) 不一致。
- 为了填估计列而拟合新的 \(q\)，或读取了 \(q^{\mathrm{use}}\)。
- 使用了保留池、\(S_{\max}\) 或开发几何的 cap。
- 需要修改 `src/` 或论文才能继续。

全部正式块的窗口都落在同一类里，仍然是完成。写出该类。不因此放宽阈值，也不因此进入决策实验。

## 决策

本文件不定义、不执行任何由诊断驱动的配权或关闭规则。诊断数字不得写成 RMSE、最差组误差或组失配的下界。

若以后要把诊断接进决策，另写预注册：规则在打开验证预测之前定死，对照是同一到达集合上始终做简单投影，终点是该块已发表的预测与组失配。那份预注册不由本文件自动生效。

## 冒烟

保留一次，不作为证据。取 NSW-Traffic 正式轨迹的一个已有窗口：三项质量之和等于正 \(\mu\)，\(d_{\mathcal C}\ge d_{\mathrm{simplex}}\)，若该窗 \(K\le 3\) 则 \(\mu_{\mathrm{adj}}=0\)。通过只说明脚本读进了轨迹。不报告该窗的距离数值作为结果，不报告 RMSE。

## 结果表

未跑。质量是目标质量份额，距离是 \(\ell_1\)。主表按块和 \(K\) 层给出种子均值。区间若要写，用种子级百分位、10000 次、随机种子 20261019，只描述均值的离散程度，不作为通过线。不复用 20261018、20261007 或 20261002。

### 质量分解

| 块 | 层 | 种子数 | 窗口数 | \(\mu_{\mathrm{miss}}\) | \(\mu_{\mathrm{pin}}\) | \(\mu_{\mathrm{adj}}\) | 组数均值 | 状态 |
| --- | --- | --- | --- | --- | --- | --- | --- | --- |
| NSW-Traffic | \(K\le 3\) | TBD | TBD | TBD | TBD | TBD | TBD | TBD |
| NSW-Traffic | \(K>3\) | TBD | TBD | TBD | TBD | TBD | TBD | TBD |
| SensorScope | \(K\le 3\) | TBD | TBD | TBD | TBD | TBD | TBD | TBD |
| SensorScope | \(K>3\) | TBD | TBD | TBD | TBD | TBD | TBD | TBD |
| U-Air | \(K\le 3\) | TBD | TBD | TBD | TBD | TBD | TBD | TBD |
| U-Air | \(K>3\) | TBD | TBD | TBD | TBD | TBD | TBD | TBD |
| City Scanner 访问占用 | — | — | — | — | — | — | — | blocked 或 TBD |
| City Scanner Pilot 2 | — | — | — | — | — | — | — | blocked 或 TBD |
| T-Drive | — | — | — | — | — | — | — | blocked 或 TBD |

### 距离分解

| 块 | 层 | \(d_{\mathrm{simplex}}\) | \(d_{\mathrm{cap}}-d_{\mathrm{simplex}}\) | \(d_{\mathrm{ESS}}-d_{\mathrm{simplex}}\) | \(d_{\mathcal C}\) | 独热窗份额 |
| --- | --- | --- | --- | --- | --- | --- |
| NSW-Traffic | \(K\le 3\) | TBD | TBD | TBD | TBD | TBD |
| NSW-Traffic | \(K>3\) | TBD | TBD | TBD | TBD | TBD |
| SensorScope | \(K\le 3\) | TBD | TBD | TBD | TBD | TBD |
| SensorScope | \(K>3\) | TBD | TBD | TBD | TBD | TBD |
| U-Air | \(K\le 3\) | TBD | TBD | TBD | TBD | TBD |
| U-Air | \(K>3\) | TBD | TBD | TBD | TBD | TBD |

### 估计位移

| 块 | 有 \(\widehat r\) 的窗口份额 | \(\delta_{\mathrm{ref}}\) | \(\delta_{\mathrm{dec}}\) | 状态 |
| --- | --- | --- | --- | --- |
| NSW-Traffic | TBD | TBD | TBD | TBD 或 blocked |
| SensorScope | TBD | TBD | TBD | TBD 或 blocked |
| U-Air | TBD | TBD | TBD | TBD 或 blocked |

### 图

不在本方案里画。若以后要图，每个正式块一组叠柱，柱是 \(\mu_{\mathrm{miss}}\)、\(\mu_{\mathrm{pin}}\)、\(\mu_{\mathrm{adj}}\)，并排 \(K\le 3\) 与 \(K>3\)。没有数值之前不交给视觉排版。

## 执行顺序

| 顺序 | 实验 | 保卫的主张 | 代价 | 依赖 | 位置 | 停止 |
| --- | --- | --- | --- | --- | --- | --- |
| 1 | 抄冻结 \(\mu\)、\(\alpha_{\max}\)、\(E_{\min}\)、0.01 | 定义不看分解结果 | 低 | P0 预注册与目标文件 | `M1_PREREG.md` | 目标文件缺失则该块 blocked |
| 2 | 一次冒烟 | 恒等式接得上 | 低 | 一条正式轨迹 | 不进论文 | 恒等式失败则停 |
| 3 | 三块正式轨迹的质量与距离 | 缺失和钉死能否分开 | 低，不训练 | 已有轨迹 | 独立结果目录 | 见停止条 |
| 4 | 与 P0 的 \(\mu_{\mathrm{adj}}\) 逐窗核对 | 可调质量没有换定义 | 低 | `P0_WINDOWS.csv` | 同上 | 不一致则停 |
| 5 | 估计位移 | 参考是否偏离 \(\mu\) | 低 | 窗级 \(\widehat r\) | 同上 | 无向量则该列 blocked |

## 输出

`results_m1_attribution/round_v1/` 至少包含：

- `M1_PREREG.md`：计算前写定的目标路径、\(\alpha_{\max}\)、\(E_{\min}\)、阈值和容差。
- `M1_WINDOWS.csv`：每一种子、每一窗的三项质量、四个距离、\(K\)、组数、`row_type`。
- `M1_SUMMARY.csv`：上表各层的种子均值。
- `M1_ESTIMATE.csv`：有参考向量的窗口；没有则文件可以只有表头，并在状态里写 blocked。
- `M1_STATUS.json`：每块 `complete`、`blocked` 或 `stopped`，以及作废窗口数。

## 缺失

- 正式轨迹的窗级记录里有没有投影前参考向量，尚未盘点。没有则估计列 blocked。
- City Scanner 与 T-Drive 的组字段和冻结 \(\mu\) 仍缺，与 P0 相同。
- 质量、距离和估计位移的数值全部是 TBD。
- 本方案不估计审稿分数会不会变化。
