# 三项方法修改的合理性评估与小规模实验设计

日期：2026-09-23

更正：2026-09-24 —— `RAVEN-SimOracle` 是 `p`、`q` 的**联合** oracle，不是“真 q”。下文“收益上限”的表格表头、该表 U-Air 行与“十问应答”第 7 条的读数已相应改为 −0.028%（sd 0.265%）；同一句里 U-Air 的最小可检测效应按配对公式重算为约 0.17%（原写 0.22%）。结论未变。同步见 `raven-mcs-metric-definition-diagnosis.md` §3 T3。

对象：RAVEN-MCS（窗口化异步联邦移动群智感知数据补全）

输入：`ccfa-review-reports/raven-mcs-metric-definition-diagnosis.md`，以及用户提出的三项方法修改

契约：`CCFA-Skills/ccf-idea-optimizer`（标准模式，合理性）与 `CCFA-Skills/ccf-experiment-designer`（`design` 模式，实验设计）

本文件只记录分析与设计，没有改任何实验配置、结果或论文源文件。

## 结论

三项修改里，没有一项能在现有协议块上带来超过 1% 的 `RMSE_μ` 收益。

- 修改 1 需要改写后才成立。它是三者中最强的，但检验的是“P2 是否有用”，不是“RAVEN 能否赢过外部方法”。
- 修改 2 的前提在数学上不成立：Shimodaira 的幂平滑和 Yamada 的相对密度比，在 `π^tar = 0` 处都给不出下限权重。
- 修改 3 与 P2 的组项高度重叠，而且它瞄准的“权重估计误差”已被 oracle 结果排除（该 oracle 同时替换 `p` 与 `q`，见“收益上限”）。

下面的新数字都来自已冻结产物，是本轮重新计算的。四篇文献都已核实存在。

## 文献核实

四篇文献都存在，但适用条件与原先用法有出入。

| 文献 | 记录 | 与本修改相关的条件 |
| --- | --- | --- |
| Shimodaira 2000 | *Journal of Statistical Planning and Inference* 90(2):227–244，[doi:10.1016/S0378-3758(00)00115-4](https://doi.org/10.1016/S0378-3758(00)00115-4) | 最优权重是密度比 `w = q1/q0` 这一结论，只在模型设定错误时成立。模型设定正确时，等权 MLE 渐近最优。中等样本量用 ICw 在 `w^λ`（`λ ∈ [0,1]`）之间选择。 |
| Yamada, Suzuki, Kanamori, Hachiya, Sugiyama | NIPS 2011；*Neural Computation* 25(5), 2013，[doi:10.1162/NECO_a_00442](https://doi.org/10.1162/NECO_a_00442) | `r_α = p / (αp + (1−α)p')`。作用是把比值上界压到 `1/α`。它处理比值过大的一端，不负责给零点托底。 |
| Hainmueller 2012 | *Political Analysis* 20(1):25–46，[doi:10.1093/pan/mpr025](https://doi.org/10.1093/pan/mpr025) | 精确匹配预先指定的矩，权重取指数形式，恒为正。目标矩必须落在样本矩的凸包内（overlap）。 |
| Zubizarreta 2015 | *JASA* 110(511):910–922，[doi:10.1080/01621459.2015.1023805](https://doi.org/10.1080/01621459.2015.1023805) | 求满足平衡容差的最小方差权重。场景明确包含 incomplete outcome data，这一点对应 O 层。 |

推论：两种“平滑”在 `π^tar = 0` 处都给不出下限。`0^γ = 0`（对 `γ > 0`），而 `r_α = 0 / (0 + (1−α)π^opp) = 0`。修改 2 所说的“留下限权重”，这两篇文献都实现不了。

## 收益上限

来源：`artifacts/e3_formal_runs_r1/runs/*/final_metrics.json`，每块 20 个种子。`traffic` 是目录名，按上下文推断为 NSW-Traffic。

| 块 | Central-All | Central-Delivered | 各联邦方法区间 | RAVEN 对 SimOracle（真 `p`、真 `q` 联合） |
| --- | --- | --- | --- | --- |
| SensorScope | 7.6004 | 7.9291 | 7.9309–7.9399 | +0.008%（sd 0.070%） |
| U-Air | 1.0556 | 1.1782 | 1.1882–1.2160 | −0.028%（sd 0.265%） |
| traffic | 0.9538 | 0.9754 | ≈1.0035 | — |

`Central-Delivered` 是在已交付数据上做集中训练、不加任何校正（`src/raven_mcs/aggregation/methods.py` 第 70–83 行）。`Central-All` 使用全部有效观测，不受 U 限制（同文件第 48–63 行）。`RAVEN-SimOracle` 同时使用真 `p` 与真 `q`，其余与 RAVEN 相同。真实开关是 `uses_oracle_propensity`，它一并门控 `q` 映射（`src/raven_mcs/training/window_runner.py` 第 426–430 行）与逐原子 `p` 映射（同文件第 707–727 行）；`methods.py` 第 607–611 行只是聚合器 docstring，其中“oracle q”的说法不完整。仓库里没有任何一条臂把 `p` 与 `q` 分开，所以上表末列是联合 oracle 的读数，不能单独归因给 `q`。

读法：

- 到 Central-All 的差距（SensorScope +4.45%，U-Air +13.3%），主要是 U 层丢数据造成的。两个 Central 之间已经差了 4.3% 和 11.6%。任何重加权都拿不回没交付的样本。
- 用真 `p`、真 `q` 也几乎不变，说明倾向性估计（两者合起来）不是瓶颈。单看 `q` 是不是瓶颈，现有产物回答不了。
- U-Air 上，RAVEN 在种子 30001 的 80 个窗口里，P2 把 `α` 从 `β̂` 平均推开的 L1 距离是 0.337（最大 1.256），但 `RMSE_μ` 几乎不动。预测对聚合权重不敏感。

配对功效：

- E2（`artifacts/e2_traffic_formal_runs_r1/formal_results.csv`）六个场景里，RAVEN 对 TwoStage / FedAvg 的配对相对差，种子 sd 只有 0.02%–0.05%。
- Pilot 2（`results_joint_ou/round_v1/tables/JO_E3.csv`）上，RAVEN 对 TwoStage 为 **+0.54%**（sd 0.45%），10 个种子里 RAVEN 只赢 2 个。

代码事实：

- TwoStage-Hájek 就是 `α = β̂`，不跑 P2（`methods.py` 第 314–320 行）。
- ObsUse-Window 的权重是按客户端的 `raw_counts / (p_obs · q_use)`，不含 unit 级 Hájek，也不含 P2（第 154–160 行）。
- `validate_p2_lambdas` 规定：instant calibration 打开时，必须 `λ_group ≥ max_server_learning_rate`，后者默认 1.0（`src/raven_mcs/aggregation/feasibility.py` 第 37–46 行；`RavenAggregator` 默认值在 `methods.py` 第 474–484 行）。

## 第一部分：合理性

### 修改 1

```text
修改：P2 可收缩配平。
一句话机制：削弱或改写 P2 把聚合组成 Mα 推向 μ 的力度，让 α 回到参考 β̂ 附近。
数学陈述：
  原式 J_r(α) = −Q_rᵀ M α + (λ_g/2)‖Mα − μ‖² + (λ_β/2)‖α − β̂_r‖²
              + (λ_v/2) αᵀ V_r α + λ_s τ̄_rᵀ α，α ∈ C_r。
  (1a) 目标混合：用 μ_λ = (1−λ)ρ_r + λμ 替换 μ。
       ρ_r 为本窗到达组成（count-proportional α 下的 Mα）。
  (1b) 强度收缩：μ 不变，λ_g 取自预先写死的网格，并可置 Q ≡ 0。
估计对象：
  (1b) 不改变 β̂ 的 estimand，只改变 P2 的极小点 α*(λ_g)。
  (1a) 改变 P2 的目标组成，由 μ 变成 μ_λ，estimand 随之改变。
是否落在现有假设类 A1–A6 内：
  (1b) 是。λ_g = 0 在 A4 类内（诊断 E8）。
       但 λ_g ∈ (0, 1) 与 instant calibration 同时出现，违反代码里的可行性约束。
  (1a) 形式上是（μ_λ 仍是概率向量），但需要新增假设 A7：
       μ_λ 在选择前冻结，且与 test split 无关。
现有定理的适用性：
  Thm. 1：对 (1a)(1b) 都成立，强凸只依赖 λ_β。
  Prop. 2：对两者都不受影响，它讲的是 β̂ 的池化 estimand，不涉及 P2。
  Prop. 3：对任何固定的 μ_λ 或 λ_g 都成立。
           但在 (1a) 下，α* 对齐的是 μ_λ 而不是 π^tar。
  需要的替代命题（(1a) 专用，needs-mechanism）：
    若损失有界于 B，则
      R_tar(θ_λ) − R_tar(θ_1) ≤ (1−λ)·B·TV(ρ, μ) + 方差项差。
    这个命题要给出偏差–方差折中，现在没有。
它改变了什么：P2 从硬配平变成可调的配平；端点之一是 α ≈ Proj_{C_r}(β̂)。
它破坏了什么：
  (1a) 削弱“对齐部署目标”的主张（问 2）。
  E6：Δ_group 必然随 λ 变小而变差，不能再用作赢的证据。
  E9：λ_g < 1 必须关掉 instant calibration，也就是进入 Gen2 wo_inst 的配置。
  E7：λ = 0 退回的不是 ObsUse（见问 1）。
可伪证条件：
  若验证集在多数块或种子上选中 λ_g = 0（或 λ = 0），
  且测试端相对 TwoStage 不显著更好，
  那么 P2 对预测没有价值。这同时是对 P2 这个贡献的证伪。
新颖性不确定度：needs-search。
  “用准则在加权与不加权之间选插值”在原理上已被 Shimodaira 覆盖。
```

### 修改 2

```text
修改：用连续 Design 替换 φ 硬开关。
一句话机制：让 Design 因子在完全校正与不校正之间连续变化，不再按 φ 二选一。
数学陈述：
  (2a) 用户版：ζ^γ（Shimodaira），
       或 r_α = π^tar / (α π^tar + (1−α) π^opp)（Yamada）。
  (2b) 能真正托底的版本：
       ζ_κ = (1−κ)·π^tar/π^opp + κ
            = [(1−κ)π^tar + κ π^opp] / π^opp。
       即把目标换成混合律 π_κ = (1−κ)π^tar + κ π^opp。
估计对象：
  (2a) estimand 不变，但零质量单元仍是零，托不了底。
  (2b) estimand 由 π^tar 变成 π_κ。
是否落在现有假设类 A1–A6 内：
  (2b) 需要 A5 在 π_κ 上成立（κ > 0 时自然成立），
       以及与 A7 同类的冻结与独立条件。
现有定理的适用性：
  Thm. 1 成立。
  Prop. 2 只对 κ = 0 成立；κ > 0 时它恢复的是 π_κ 的矩，
          要把命题的对象从 π^tar 改写为 π_κ。
  Prop. 3 在固定 κ 下成立。
它改变了什么：
  (2a) 当 γ ∈ (0, 1) 时改变 ζ 在 strata 之间的形状，
       对正质量单元不是空操作；零质量单元不变。
  (2b) 零质量单元获得 κ 的权重。
它破坏了什么：
  E3/E2：零质量集合恰好是“测试中不存在的对”，
         托底规则是以 test 覆盖为条件的。
  φ 开关虽然消失，但 test 派生的目标仍在（问 5），
  所以并没有“顺带解决 φ”。
  内部一致性：(2b) 与修改 (1a) 是同一种“目标混合”操作，只是作用在不同层。
  两者同时用时，κ 与 λ 必须绑定为同一个混合律，
  否则 β̂ 和 P2 追的是两个不同的 estimand。
可伪证条件：
  U-Air 上，冻结的 κ（例如 0.5）对 NoDesign（κ = 1 端）
  不能在 Holm 下显著改善；或者验证集总是选中 κ ≈ 1。
  两种情况都说明连续 Design 没有价值。
新颖性不确定度：needs-mechanism。
  托底必须来自目标混合，而不是比值平滑；混合目标的合法来源也未解决。
```

### 修改 3

```text
修改：直接估计复合权重（balancing weights）。
一句话机制：不再估三层倾向性再相乘，而是直接在到达单元上求一组权重，
           使其 strata 或特征矩等于目标矩。
数学陈述：
  EB：min Σ_i w_i log(w_i / w_i^0)，
      s.t. Σ_i w_i c(x_i) = m^tar，Σ w_i = 1。
  SBW：min ‖w − w̄‖²，
       s.t. |Σ_i w_i c_j(x_i) − m_j^tar| ≤ δ_j，w ≥ 0。
  若 c 只取 strata 指示，两者都退化为 post-stratification：
      w_s = π^tar_s / ρ̂_s。
  也就是用一个经验比值替换 π̂^opp · p̂ · q̂ 的连乘。
估计对象：与 m^tar 同源。m^tar 仍取 test-split 的 π^tar 时，estimand 不变。
是否落在现有假设类 A1–A6 内：
  否。A6 讲的是 q̂ 与截断，这里已不适用。
  需要新假设 A6'：目标矩落在每窗到达矩的凸包内（EB），或落在容差 δ 内（SBW）。
现有定理的适用性：
  Thm. 1 成立，前提是 β̂ 改由平衡权重构造、P2 不变。
  Prop. 2 需改写为：在 A6' 和结果对 c 线性（或误差可控）时，
          平衡权重的池化估计量是 m^tar 的无偏或一致估计。
  Prop. 3 的“剪切插件的 O(ε) 扰动”不再对应，
          需要换成“平衡容差 δ → 偏差”的界。
它改变了什么：去掉 p_min、q_min、d_max 的截断机制，也去掉三层误差的累积。
它破坏了什么：
  与 P2 重叠：P2 的组项本身就是客户端粒度上的二次软平衡，加上方差惩罚 λ_v。
  E6：平衡会按构造把 Δ_group 压到接近 0。
  E1：U 是构造的，“解决 A6 失败”只是关于构造协议的陈述。
  联邦声称不完全成立：只有 strata 指示约束时“只要计数”才成立；
  连续矩下 EB 对偶梯度需要 Σ_i exp(θᵀ x_i) x_i，必须多轮迭代。
  逐客户端上报 strata 计数会暴露到访位置模式，这是一个隐私面。
可伪证条件：
  Pilot 2 上，平衡权重配 P2 关闭，对 TwoStage 不能显著更好。
  或者可行性审计显示“正目标质量但本窗零到达”的 (窗口, stratum)
  超过预注册阈值（例如 10%），迫使大量回退。
新颖性不确定度：needs-search。
  联邦场景下的 balancing weights 这轮没有检索。
```

## 十问应答

### 1. 修改 1 的安全论证是否成立

不成立，分两层。

第一层，`λ = 0` 退回的不是 ObsUse。ObsUse 是按客户端的 `raw_counts / (p · q)`，不含 unit 级 Hájek，不含截断下限，不含 P2。`μ_λ = ρ` 时，组项会把 `Mα` 拉向计数比例组成（近似 FedAvg），同时 `λ_β` 项把它拉向 `β̂`，再叠上 `λ_v`、`λ_s` 和 `C_r`。三者都不是 ObsUse。

第二层，即使能嵌套，被嵌套的也是作者自己的子集（E7）。

修正后的安全陈述：在 `λ_g = 0`、`Q ≡ 0`、`C_r` 不起作用时，(1b) 的端点是 `α = Proj_{C_r}(β̂)`，近似 TwoStage-Hájek。按验证集选中的成员，其测试风险不超过“候选集内测试最优成员 + 选择误差”。这个保证只对候选集内的作者内部方法成立，对 FedAvg、FedAU 以及任何外部方法都没有保证。要对外部方法有保证，只能把外部方法显式放进候选集，而那就变成了按验证集选方法的元方法。

### 2. `μ_λ` 改变的是估计量还是估计对象

(1b) 只改估计量。(1a) 改估计对象。`λ < 1` 时，论文只能声称“对齐到以 `λ` 混合的目标”。Prop. 2 不受影响，因为它针对 `β̂`；但“对齐部署目标”这句要加限定。需要 A7，以及修改 1 中写出的偏差–方差命题。

### 3. 在验证集上按风险选 `λ` 是什么性质的决策

对 (1a) 是在选 estimand，对 (1b) 是超参选择。纪律要求：

- 网格事先写死；
- 验证划分完全落在训练时段内（U-Air 已有冻结划分：验证在第 158–210 时刻，测试在第 211–263 时刻，见 `configs/frozen/e3_multidataset_protocol_closure/uair/horizon.json`）；
- 验证风险的加权律事先声明；
- 每块只选一次，选定后连同 hash 一起冻结，测试只跑一次；
- 报告被选中 `λ` 的跨种子稳定性。

这与“测试只在冻结后运行一次”相容。但现有 `final_metrics.json` 没有记录验证集指标，E3 目录里也没有看到 checkpoint。按验证集选择需要重新评估（needs-evidence）。

### 4. 修改 2 与 Hájek 抵消（E4）

全局缩放是空操作。`ζ^γ` 在 `γ ∈ (0, 1)` 时改变 strata 间的相对比值，对正质量单元不是空操作。按客户端的常数缩放也不是空操作，因为 `β̂_k` 是跨客户端归一化的。

要托底，必须改结构：让零质量单元获得正质量，也就是改分子（目标律），而不是改指数或比值形状。

### 5. 托底权重与评测泄漏

因为 `π^tar = 0` 当且仅当该对不在 test split 中，任何“对零质量单元特别处理”的规则，都在用 test 的协变量覆盖。它不碰 test 标签，属于 transductive 的目标设定，离标签泄漏有一步距离，但与“公开部署目标”的主张不相容。

与切分无关的下限来源有两个：一是外部冻结的质量（WorldPop 一类、或事先声明的部署规格）；二是只由训练期估计的 `π^opp`，也就是 (2b) 中的 `ν = π^opp`。后者只让托底项与切分无关，`ζ` 的主项仍然来自 test。根治靠诊断中的 D-2：换成外部目标后，U-Air 那 35.4% 的训练单元自然获得正质量，连托底都不需要。

### 6. 修改 3 是否继承 E2

继承。`m^tar` 取 test 派生的质量，就等于把训练组成匹配到测试组成。而 `RMSE_μ` 恰好是测试单元等权，这种匹配对该指标几乎是量身定做的，基线却拿不到这份信息，比较不公平。

前置条件有二：一是 `m^tar` 外部冻结，或者只用训练期信息；二是 A6'（overlap）通过可行性审计。

### 7. 效应量

三项修改要修的量，在现有协议块上都在 0.1% 量级以下。

- E2：选择效应的全部只有 0.08%。即使完全校正，也低于论文自己 0.5% 的实际意义门槛。配对最小可检测效应（Holm 族 4 个比较里最严的一步，20 个种子，功效 0.8）约为 0.017%–0.036%。统计上能测出来，实践上没有意义。
- E3：真 `p`、真 `q` 相对估计值的差异是 +0.008% 和 −0.028%（联合 oracle，不区分 `p` 与 `q`）。所以修改 3 瞄准的“权重估计误差”没有空间。两块上 4.45% 和 13.3% 的差距来自 U 层丢数据，重加权拿不回来。
- Pilot 2：按实测 sd 0.45%，最小可检测效应在 10 个种子时约 0.6%，20 个种子时约 0.37%（用 t 近似）。

可能出现大于 1% 收益的条件：

- 模型设定错误的方向与偏移同向。按 Shimodaira 的结论，模型正确时等权最优。可以用更弱的骨干，或更强的偏移，把现在的 `exp(−1.25)` 做成一条扫描。
- 目标律与到达律的总变差距离大，并且评测按该目标加权，不再是计数份额。
- 下游决策依赖组级误差，例如按区域定位热点。

现有数据里，方法间差距已超过 1% 的只有真实 R 的块：T-Drive 上 ObsUse 对 NoDesign 是 1.6%；Pilot 2 上 TwoStage 对 FedAvg 约 1.2%。

### 8. 端点选择

只用 `Δ_group` 或 `Δ_c-s` 必然重演 E6。修改 3 甚至会按构造把 `Δ_group` 压到约 0。

两个目标不来自本方法流水线、泛函也不在 `J_r` 中的端点：

- Gap-closure 比例 `G_m = (RMSE_FedAvg − RMSE_m) / (RMSE_FedAvg − RMSE_Central-All)`。参照是集中训练全部数据，与流水线无关。SensorScope、U-Air 和 traffic 已有全部取值，可以直接算。Pilot 2 没有 Central 参照，需要补跑。
- `Tail_RMSE`，即冻结的第 2–3 时间块，已在 `final_metrics.json` 中。这两个块正是构造偏置所在的块，只能算半独立。

外部质量加权的 RMSE（例如 WorldPop）是最干净的端点，现在还没有取值。

### 9. U 从未实测时，哪些主张可以做

可以说：在构造的 U 协议下，平衡权重消除了截断机制（`clip_rate_stage1` 与 `clip_rate_stage2` 已在 `final_metrics.json` 里，可以直接对比），并且权重有界、离散度下降。

不可以说：对真实网络可用性稳健；“修复了 A6”（A6 失败本身就是构造 q 的性质）；部署收益。Pilot 2 的 U 同样是构造的（Complete-aligned，`s_max = 5`，见 `appendix.tex` 表注）。

### 10. 配置一致性

| 参数 | 取值 | 来源 | 状态 |
| --- | --- | --- | --- |
| `λ_β` | 1.0 | `RavenAggregator` 默认值（`methods.py` 第 474–484 行）；`configs/sag_g0/thresholds.json` | E3 的 `config_snapshot.json` 没有记录 λ，是否用的默认值 needs-evidence |
| `λ_group` | 1.0；变体为 0 | 同上；instant on 时要求 ≥ 1.0（`feasibility.py`） | 变体 0 必须关 instant，也就是 Gen2 |
| `λ_v` | 0.1 | 同上 | 同上 |
| `λ_s` | 0.1 | `methods.py` 默认值 | 同上 |
| `α_max` | 0.5 | 默认值；`src/raven_mcs/e3/final_closure/core.py` | — |
| `E_min` | 3.0，取 `min(E_min, n_active)` | 默认值 | — |
| `s_max` | 5 | `configs/frozen/e3_multidataset_protocol_closure/*/stage2_eligibility.json`；E2 的 `FORMAL_RUN_CONFIG.json` | 已核实 |
| `d_max` / `q_min` / `p_min` | 10 / 0.05 / 0.05 | `configs/frozen/e1_r2_weight_safety.yaml` | 已核实 |
| `π_min` | 1e-6 与 1e-8 冲突 | 前者见 `e1_r2_weight_safety.yaml`，后者见 `configs/config.yaml` | needs-evidence |
| `a_max` | 40 | E2 的 `FORMAL_RUN_CONFIG.json` | E3 与 Pilot 2 needs-evidence |

所有变体一律采用 Gen2 约定：保留 P2，`λ_β` 与全 RAVEN 对齐。

修改 (1b) 的 `λ_g = 0` 在 SensorScope / U-Air 上已经跑过，就是表 IV 的 Inst 行。U-Air 上 RMSE 显著变差 +0.131%，SensorScope 不显著。所以修改 1 在协议块上已有负面证据。Gen2 是否保留 debt 仍是 needs-evidence。

## 最强路线与两次挑战

最强路线是修改 (1b)。它是三者中唯一瞄准已测到的损失的。

- Pilot 2 上，TwoStage（`α = β̂`）比 RAVEN 好 0.54%。两者共用 `β̂`，差别正是 P2 和 debt，归因干净。
- T-Drive 上，NoDesign 比 ObsUse 差 1.6%，但这里混入了 unit 级 Hájek 和截断的差异，归因不干净。

Overlap 挑战：“用准则在等权与全重要性加权之间选插值”就是 Shimodaira 的 `w^λ` 加 ICw，机制本身不新。需要进一步检索的是有没有“联邦服务器端组质量校准加收缩”的先例（needs-search）。结论：修改 1 不能当贡献写，只能当诊断或修复。

Evidence 挑战：修改 1 在 Pilot 2 上的最好结果，就是退回 TwoStage，也就是作者自己的方法。这相对 FedAvg 约好 1.2%，但这是已有数字，不是新收益。在协议块上，`λ_g = 0` 已经显示无益甚至有害。

挑战后的修订：

- 把修改 1 从“收益路线”改写为“P2 必要性检验”。
- 主变体用 (1b)，不改 estimand；(1a) 降为敏感性分析。
- 预注册两种可能结论。若 P2 关闭后不劣，论文把 P2 定位为 `Δ_group` 工具，不再声称预测收益。若 P2 在某个真实 R 块上带来显著预测收益，才保留“P2 改善预测”的主张。

## 第二部分：小规模实验设计

### Mode

`design`。

### Venue and assumptions

IEEE TMC。不做全量重跑。新运行只在已冻结的 EventTrace 上补跑变体，并复用已有基线结果做配对，要求 trace hash 相同。不修改 `tdrive_protocol_seal_r1/`。新结果写入新目录。

### Claim-evidence matrix

| 主张 | 证据 | 端点 | 块 |
| --- | --- | --- | --- |
| C1：P2 对预测有益 | V1 对 TwoStage 与全 RAVEN | 配对 `RMSE_μ`（主）；`G`、`Tail_RMSE`（次） | Pilot 2（主），T-Drive（次） |
| C2：连续 Design 优于二选一 | V2 对 NoDesign | 同上 | U-Air |
| C3：复合平衡权重优于三层连乘 | V3 对 TwoStage | 同上，另加截断率与权重离散度 | Pilot 2 |
| C0：收益上限 | T0.1（零训练） | `G`、Central 参照 | SensorScope / U-Air / traffic |

### Dataset and benchmark needs

- Pilot 2：`results_joint_ou/round_v1/`，10 个种子 33001–33010，5 个方法。
- U-Air 与 SensorScope：`artifacts/e3_formal_runs_r1/runs/`，20 个种子。
- E2 traffic：`artifacts/e2_traffic_formal_runs_r1/`，只用于 T0 的上限论证。
- 外部目标：暂无，只作为 D-2 后续。

### Confirmed method and baseline versions

以 E3 和 Pilot 2 已冻结的 RAVEN、TwoStage-Hájek、FedAvg-Window、FedAU-Window、ObsUse-Window 为准。每个新变体只改一个开关，配置见问 10 的表。Pilot 2 的超参实例化路径待核（needs-evidence，看 `scripts/run_joint_ou_cs_p2.py`）。

### Baseline matrix

外部方法只有 FedAvg-Window。FedAU-Window 是跨域适配。ObsUse-Window 和 TwoStage-Hájek 是作者内部方法，表中必须标出。

### Main experiments

- **V1（修改 1b）。** Pilot 2 上跑 RAVEN，设 `λ_group = 0`、`instant_calibration = False`、`Q ≡ 0`，其余冻结。10 次运行。若它接近 TwoStage，说明损失来自组项和 debt；否则来自 `λ_v`、`λ_s` 或 `C_r`。
- **V1-TD。** T-Drive 上跑 NoDesign 版的同一变体，10 或 20 次（按冻结 trace 的种子数）。
- **V2（修改 2b）。** U-Air 上用 `ζ_κ`，`κ = 0.5`，固定、预注册，不做选择。20 次运行。两个端点 `κ = 0`（Design）和 `κ = 1`（NoDesign）复用已有结果。
- **V3（修改 3，只做离散版）。** Pilot 2 上用 strata post-stratification 权重，P2 关闭，Hájek 归一后作为 `α`。10 次运行。

### Ablations

V1 本身就是 P2 的消融。V3 加一个“P2 开”的对照，只在 V3 通过后才做。

### Robustness, failure, efficiency

- T0.3 可行性审计：统计“正目标质量但零到达”的 (窗口, stratum) 比例。这是 V3 的前置条件。
- 截断率对比：用已有的 `clip_rate_stage1` 与 `clip_rate_stage2`。
- 被选 `λ` 的稳定性：只有在验证指标可得时才做。
- 运行时间：沿用已有的 runtime 字段。

### Smoke scope and deduplication

每个新变体只在 1 个种子上验证能跑通、trace hash 一致、其他方法未受影响。不做额外的防御性用例。smoke 结果不进入论文。

### Result tables or figure specs

表 A，收益上限（T0.1，零训练，可立即填）：

| 块 | FedAvg | 最优联邦方法 | RAVEN | SimOracle | Central-Delivered | Central-All | G_RAVEN |
| --- | --- | --- | --- | --- | --- | --- | --- |
| SensorScope | TBD | TBD | TBD | TBD | TBD | TBD | TBD |
| U-Air | TBD | TBD | TBD | TBD | TBD | TBD | TBD |
| traffic | TBD | TBD | — | TBD | TBD | TBD | — |

表 B，变体主结果（配对相对差，负值为改善）：

| 变体 | 块 | 对照 | n | mean Δ% | sd Δ% | 95% CI | Holm-adj p | wins/ties/losses | 判定 |
| --- | --- | --- | --- | --- | --- | --- | --- | --- | --- |
| V1 | Pilot 2 | TwoStage | 10 | TBD | TBD | TBD | TBD | TBD | TBD |
| V1 | Pilot 2 | 全 RAVEN | 10 | TBD | TBD | TBD | TBD | TBD | TBD |
| V1-TD | T-Drive | ObsUse / FedAU | TBD | TBD | TBD | TBD | TBD | TBD | TBD |
| V2 | U-Air | NoDesign | 20 | TBD | TBD | TBD | TBD | TBD | TBD |
| V3 | Pilot 2 | TwoStage | 10 | TBD | TBD | TBD | TBD | TBD | TBD |

表 C，机制诊断。列为截断率 stage1/stage2、权重最大值、ESS、可行性违例率、`‖α − β̂‖₁`。各行变体的取值全部为 TBD。

统计：

- 种子：Pilot 2 用 10 个（与已有基线配对，最小可检测效应约 0.6%）。若结论处在边界，再加到 20 个，此时基线也要补跑，最小可检测效应约 0.37%。U-Air 用 20 个，以 RAVEN 对 SimOracle 的配对 sd 0.265% 作噪声代理，按配对公式（20 个种子、功效 0.8、双侧 0.05）算最小可检测效应约 0.17%。
- 配对：同种子、同 trace hash，用 Wilcoxon signed-rank，与 E2 已用检验一致。
- Holm 族：{V1 在 Pilot 2 对 TwoStage，V1-TD 对 ObsUse，V2 对 NoDesign，V3 对 TwoStage}，共 4 个，沿用论文“family of four”的纪律。次要端点只描述，不下结论。

预注册判定规则：

- 成功：Holm 校正后 p < 0.05，并且平均改善 ≥ 0.5%，并且 95% CI 上界 < 0。
- 非劣：CI 上界 < +0.5%。
- 其余一律判失败。`Δ_group` 不参与判定。

终止与放弃条件：

- V1：若对全 RAVEN 没有改善，就放弃“P2 有害”这个假设。若接近 TwoStage，结论是 P2 对预测无益，论文据此改定位，不再展开 λ 网格。
- V2：若 T0.4 表明没有与切分无关的托底来源，V2 只能作为披露后的敏感性分析。若不优于 NoDesign，就放弃。
- V3：若 T0.3 的违例率 > 10% 就不跑。若不优于 TwoStage，就放弃。

### Missing values

- Pilot 2 的 Central 参照。
- 验证集指标（`final_metrics.json` 未记录）。
- E3 与 Pilot 2 实际使用的 λ、`π_min`、`a_max`。
- Gen2 是否保留 debt。
- 外部目标质量。

### Execution priority

1. T0.1–T0.4，零训练，只读已冻结产物。
2. V1（Pilot 2）。
3. V1-TD。
4. V3，前提是 T0.3 通过。
5. V2。

若只能做一件事，做 V1（Pilot 2）。它只要 10 次运行，是观测实测的块，基线已经配好对。TwoStage 恰好就是“P2 关闭”的端点，归因最干净。它直接决定 P2 这个核心组件在预测上是有益、中性还是有害，其余路线的定位都取决于这个结论。

### No-fabrication status

表中所有 TBD 都未填。文中出现的具体数字，出处都已写明：E3 与 E2 的冻结产物、`JO_E3.csv`、`appendix.tex` 第 2446–2449 行、诊断文件中的 E4 与 E5。四篇文献都已核实，没有新增其他引用。

### Next CCFA owner

结果回来后交给 `ccf-integrity-auditor` 核对数字与主张。只有 C1 或 C3 通过时，才交 `ccf-paper-writer` 改写。

## Checklist

idea-optimizer 的 13 项里，第 1–12 项已覆盖。第 4、11 项的联邦平衡权重先例标为 needs-search。第 13 项没有触发任何模块交接。
