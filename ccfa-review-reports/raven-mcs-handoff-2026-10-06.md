# RAVEN-MCS 交接记录 — 2026-10-06（round-12 之后，门控剂量轮之前）

> **修订提示（2026-10-07 19:40）**：§1–§9 是 10-06 的原版交接，保留作审计线索。另一 Agent 在 10-07
> 跑完了四轮实验、改动了手稿、并把记录写进了台账 Part VIII。全部新增事实、被推翻的假设、新发现的缺陷
> 与下一步（`ccf-integrity-auditor` + `ccf-paper-reviewer` 验收 Evidence 轴）见文末 **§10–§16**。
> **二者冲突时以 §10 起为准。**

用途：把本会话的可用信息交给新会话。读法：§1 是速览，§2 是**已确认事实**（有文件/数值/哈希支撑），
§3 是**关键决策与原因**，§4 是**失败尝试（不要重复）**，§5 是**假设**，§6 是**未决问题**，§7 是**下一步**，
§8 是路径与命令清单，§9 是约束（禁止事项）。凡我没有亲自验证、只是从早前记录继承的内容，一律标注
"未在本会话复验"。

---

## 1. 状态速览

| 项 | 值 |
| --- | --- |
| 手稿（当前） | `TO_OVERLEAF_paper_tmc_r1_clean/main.tex` sha256 **`02447bfe6256632b…`**，113 854 B |
| 手稿（round-12 评审时的"当前版"） | `59e4f4d5cffff4ff…`，113 345 B（round-11 文字修复产物） |
| 手稿（round-12 的历史版） | `88ecd743321e38e9…`，113 379 B = `snapshots/2026-10-04-pre-r11/main.tex` |
| 构建 | `main.pdf` **17 pp**，0 errors / 0 undefined / 0 multiply-defined / 0 overfull；`supplemental.pdf` 16 pp，1 个既有 Overfull |
| 冻结评审契约 | `TMC-J-R4`（8 维，权重 0.10/0.20/0.25/0.15/0.10/0.10/0.05/0.05；锚 1–5；总 1–10；`\|Δ\|<0.05` = unchanged） |
| round-12 记分 | 相对进步 **`improved` +0.05**（正好压在阈值上）；绝对就绪度 **3.30**；立场 **5/10（维持）** |
| 阻塞轴 | **Evidence（权重 0.25，锚在 3）** = E1；E2 在 Significance/Originality |
| 台账 | `ccfa-review-reports/raven-mcs-metric-definition-diagnosis.md` sha256 `142D3D42B9BEF39D…`，2858 行；更正条目已到 **52**；**Part VII = round-12 修订台账** |
| 当前未完成任务 | Claude 给的"门控剂量"实验指令：只应执行 **P0（无训练）**；P1/P2 训练需要用户写出 **`授权门控剂量`** |
| 本会话最后动作 | 我正要查看 `src/raven_mcs/training/window_runner.py` 是否有"只打分/学习率为 0"的路径，以实现 Δ_group/Δ_c-s 的 θ 重打分——**工具调用被中断**，`scripts/gate_dose.py` **尚未创建** |

---

## 2. 已确认事实

### 2.1 手稿与构建

- round-12 后我做了 3 处**纯文字**修改（3 hunks，+9/−1 行，+63 词，无任何数字/表/图/论断改动）：
  1. **M2** — Data and Code Availability 首段末新增一句，点名 `w1/` 子树、`w1/PAPER_NUMBERS.csv`（"indexing the printed values"）与 `verify.py`（"re-checking the payload against the manifest"）。
  2. **M4** — §"Structural Alignment Objective" 等价带段落末新增："The band and this reading rule were fixed before the ladder runs, and `w1/ladder\_v3/PREREG.md` in the released bundle states both."（我先核对了该文件 L97–98 确实以"等效：区间落在 [−0.10,+0.10]；必要：区间完全越过 +0.10"定义两者。）
  3. **CL-3** — 贡献列表在 "Target debt is an accounting recursion…" 前插入新 `\item \textbf{What the measurement does not attribute.}`，把"结论 + κ=1000 排除 + 预测端点指路"整段**逐字**移出贡献 3。
- 改前快照：`snapshots/2026-10-06-pre-r12-fix/`（`main.tex`、`supplemental.tex`、`PRE_EDIT_HASHES.txt`）。
- 其他源文件：`supplemental.tex` `e99e1058a3251c59…`（未改）；`appendix.tex` `29ADD10FB7F84247…`（2026-10-02）；`reference.bib` `3F0BE0112FA97126…`。
- 构建顺序**必须**先 `supplemental.tex` 再 `main.tex`（否则 main 读到过期 `supplemental.aux`，会出现 multiply-defined）。命令见 §8。
- 早前记录的仓库卫生问题（**未在本会话复验**）：review/evidence 树大量未入 git（2 676 文件 / 46.05 MB）；`src/` 相对 HEAD 有 12 个文件真实内容差异（`window_runner.py` +358/−67）；一次批量 touch 把若干文件截断为 2 B；`BUNDLE_SUMMARY.json` 的 `file_count 2117` 与实际 2 118 不符；`scripts/run_nodesign_supplement.py` 载入了错误的 City Scanner 数据集（`cityscanner_nyc_p2_measured_o` vs `cityscanner_nyc_pm25`）。

### 2.2 round-12 评审（`ccf-paper-reviewer`，version-comparison 模式）

- 证据链：`snapshots/2026-10-04-pre-r11/main.tex` = `88ecd743321e38e9…`（与上一份 canonical 报告记录的哈希一致）→ `59e4f4d5cffff4ff…`，**4 hunks / +5 / −6**：①⑷ `recoverable → closed by uniform server weights`（L1819、L2194）；② 删掉 `8.23`–`21.73`；③ 隐私句重排（L2172–2176）。`recoverable` 从 4 处（两义）降到 2 处（只剩 ceiling 义，现 L2103/L2106）。
- 机器校验：`CCFA-Skills/ccf-paper-reviewer/scripts/validate_version_comparison.py .rb_work/r12_contract.json` → **PASS: version comparison is internally consistent**。
- 相对进步：唯一变动 Terminology **3→4**（R5-16 已解决）→ 加权 Δ = **+0.05** → `improved`。**分类正好落在冻结阈值上**（`|0.05|` 不 < 0.05）；若 Terminology 保持 3 则为 `unchanged`。此刀锋已在报告中披露。
- 绝对就绪度：八维 2/5/3/4/2/2/3/4 → 加权 **3.30**，立场 **5/10 borderline negative（维持）**。
- 台账八行（r12）：R5-16 / M3 / A-8 = `resolved`；**M2 / M4 / CL-3 = `done`（本次落地）**；E1、E2 = `open`；NEW-r12-1 = `open (boundary)`；NEW-r12-2 = `partially_resolved`；NEW-r12-3 = `open (deferred)`。
- 产物哈希：canonical 报告 `ccfa-review-reports/raven-mcs-tmc-review.md` `32BA5AE2593AED22…`（257 行，已就地重写并加 "Post-review revision" 说明，指出新当前版是 `02447bfe…`）；上一份归档 `snapshots/2026-10-06-pre-round12-raven-mcs-tmc-review.md` `B569EBD96E8CC84E…`；回复函 `ccfa-review-reports/raven-mcs-r12-response-to-review.md` `7A2ABBE77BA660F0…`（90 行）；台账（诊断记录）`142D3D42B9BEF39D…`。
- 归属分工（技能契约强制）：评审方**不改正文、不维护台账**；`ccf-rebuttal-writer` 拥有台账与回复函、**把正文修改交给 `ccf-paper-writer`**；`ccf-experiment-designer` 拥有实验协议。

### 2.3 E1 与 E2 的内容（round-12 两条 major）

**E1＝对齐没有被证明能买到准确度**（Evidence 0.25，决定性拒绝轴）。论文自身证据：
- 预测家族无 Holm 存活项：SensorScope `p_Holm = 1.000`；U-Air 最佳 raw `0.027` → Holm `0.133`；**RMSE_μ 的 arm 排序不跟随结构排序**（L2100-2105）。
- 天花板：GO 规则（`H ≥ 0.5%` 且区间下界 > 0）预注册后**未触发**；SS MDE 0.17–0.36 pp，六个估计全在 `[−0.03%, +0.08%]`；UA 20 seeds / 270 runs / 45 轨迹，全部 `|H| ≤ 0.217%`，CI 含零，实际可检测效应 **0.70–0.80 pp**；把观测倾向层内加硬只把 oracle gap 抬到 0.104%（SS）/0.251%（UA）。
- 估计代价不是原因：换真值边际只动 `−0.008%`（SS）/`+0.040%`（UA），四成员中三个对自身聚合权重巨大变化不敏感。
- 均匀权重已闭合 FedAvg→RAVEN 群组差距的 **68.96%（SS）/ 83.07%（UA）**。
- City Scanner 非劣性在声明边界**不可检验**（power ≈ 0.15）；删除问题 `n=10, r=3` **未决**。
- **本轮新增（NEW-r12-1）**：在论文自己的 checkpoint 上，U-Air 超标决策端点（35 µg/m³）在两侧都**饱和**——宽支撑 regime 只保留 **0.00–2.48 %** 的超标质量，窄支撑 **17.5–33.9 %**；`{25,35,50,75}` 四个阈值都无法体现决策能力。**论文未被反驳**（它不声称决策技能；main.tex L1573 明说决策是 "reported rather than made by the method"），但 round-9 给 E1 开的修复路线（"a decision quantity"）在此 block 上被**关闭**。
- 现在的 E1 修复条件（三条同时）：(i) headroom 高于自身可检测效应；(ii) 决策量 base rate 不饱和；(iii) 跑之前预注册。**加 seed、重跑该端点、改措辞都不算。** 分数移动条件：Evidence 3→4、立场 5→6。

**E2＝冠名的程序不是推动端点的那部分**（Significance/Originality；venue fit，不是正确性错误）。论文自身证据：
- L968-984：3 279 个活跃窗口上 `‖M_rα−μ‖₁` 在 `C_r` 上的极差中位数 **1e-13** → ℓ₁ 面平坦、最小值不唯一；端点只经 tie-break 移动，tie-broken 规则只比均匀权重多 **0.0107 pp**（1.05140 vs 1.06213，per-seed max 0.0337）；原话 "The constraint is thus the load-bearing part of (P2), and the group objective alone is not."；并留了方向："where a window's active clients do cover the target's groups, the group term regains its effect."（L982-984）。
- L1830-1860：投影值 `+0.768 pp [0.563,0.970]`（SS，越过 0.5 pp 线、跨半稳定）、`+0.286 pp [0.098,0.471]`（UA，低于线且不稳）；ζ 是唯一既必要又实践显著的进一步成分 `+0.922 pp [0.721,1.141]`（UA 不可识别）；群组匹配 / 方差 / 陈旧与 debt（`+0.0073 pp [0.0064,0.0083]` SS、`+0.0024 pp` UA）**全部落在 ±0.10 带内**；群组匹配单独把 Δ_c-s 推向错误方向 0.135 pp；锚项的作用是让问题严格凸。
- 摘要 L83-85 已自认："The other terms of the calibration program, including debt at the frozen strength, stay inside a pre-registered equivalence band."
- 修复路线：(a) **纸面**——让贡献列表以"投影 + Design 因子"领衔，(P2) 其余项作为唯一性装置（评审明写单靠它 **不动分数**）；(b) **实验**——找一个 setting 让那些项移动端点（论文自指的"活跃客户端覆盖目标组"情形）。E2 的 Significance 修复被明确挂在 **"only together with the Evidence repair"**。
- **注意**：本会话我**独立复验了 Design 侧**（见 2.4），但**没有**重新推导 1e-13 平坦性与 0.0107 pp（继承自 `MYOPIC_DIAG.json` 与 round-9/10 的核对）。

### 2.4 H / regime 线（round 3 + 修复）

- 关掉 FedAvg 复现缺陷的规则：**`m_total = 0` 当 `pi_tar = 0`**，轨迹保持字节不变。门：20/20 seed 在 `RMSE_mu`、`Tail_RMSE`、`RMSE_rho`、`Delta_group` 上 `0.000e+00`，活跃集逐窗相同；240/240 轨迹配对一致。此前 round_v1 在 seed 30001 差 `3.958590311060117e-02`（−3.27 %）、seed 30006 差 `1.353623714159775e-01`（−10.53 %），且被记为 `known_nonrepro: true` + `"pass": "True"`。
- 修正臂上的 H 表（U-Air，n=20，6 条件）：Design-on oracle 全为负（−0.27 %…−0.68 %，C4/C5 CI 排除零）；Design-off oracle（`raven_simoracle_nodesign`，`uses_design_ratio=False`；`gate_mode="policy"` → `G_r=0`、`ζ≡1`）**+5.21 %…+6.17 %，CI 下界 > 0.04** → 预注册规则给出 **`decision = go`**（`go_bar = 0.005` 未动）。**这个 `go` 必须读作"支撑成本效应"，不是 oracle 余量。**
- 2×2 分解：regime 因子 ≈ 6 %，权重/信息因子 ≤ 0.3 %（regime 内：A −0.27 % [−0.80,+0.26]；B −0.22 % [−0.72,+0.28]）。regime A（66/80 窗、2.32 客户端）与 B（74/80、2.81）；**A ⊂ B 在 20/20 seed 上成立**；A/B 两次 FedAvg 的 `EventTrace_hash` **与** `config_hash` 20/20 完全相同；中位 145 vs 192 个 client-window（A 保留 74.6 %，≈25 % = 72/288 pairs）。
- 支撑成本：旧分母 +6.98/+6.99/+6.32/+6.99/+7.00/+6.31 %（C0…C5）↔ §3A H4 的 θ 重算值 +6.968/+6.989/−/+6.980/+6.991/−；修正分母 +6.45/+6.51/+5.88/+6.46/+6.49/+5.89 %（CI 下界 +5.13/+5.48/+4.49/+5.14/+5.16/+4.49 %）。→ **H4 被复现，只改水平。**
- 更正条目 **49**（round-3 的 C4/C5 A 侧不是 block-uniform）：`round_v3/runs/C4_block_uniform/.../fedavg_window` 与 C0 **在除 `runtime_seconds` 外每个数值字段、20/20 seed 上相同**，`pi_tar_hash` 同为 `8bab153a707d1267`。原因：`r3_p1p2.train_fedavg` 用 `gc = dict(H.CONDITIONS["C0_frozen"])` 只覆盖 theta/tail/model → `target` 仍 `test_share` → `H.injected` 跳过 block_uniform 的 `_bundle` 补丁；单传 `pi_target_override` 不改变零质量集合。
- 修复（条目 **50**）：`results_h_headroom/round_v3_fix/runs/` 40 个 run（条件字典原样传入）。ΔRMSE **+0.003157**（C4）/ **+0.003102**（C5），20/20 同向；ΔΔ_group ≤ 0.015；**ΔΔ_c-s 恰好 0**（Δ_c-s 是 client×stratum 上的 `Σ|Π̂−π^tar|`，组质量的严格正缩放动不了它）。重推 H：C4 `1.188238→1.191394`、`H_best 0.059330→0.061820 [0.047162,0.076477]`；C5 `1.179322→1.182424`、`0.052110→0.054595 [0.040396,0.068793]`；**两者仍 `go`，轮次决策仍 `go`**；C0–C3 不变（≤4.4e-16）。

### 2.5 端点轮 P0–P2D（`results_regime_b_endpoints/round_v1/`）

- 协议：`DESIGN.md` `cd2db441…`（含量表声明 σ = **17.36325121670317** = A 侧 policy = `dataset._scaler_std`，逐格断言；`T_DEC = 35.0` 物理单位；`go_bar`/标签规则/AM-5 词表/±0.10 带）。
- **P0**（`P0_REPORT.md` `80df1a80…`）：240 格、0 未配对；支撑 288 两侧；复现 `0.000e+00`。Δ_c-s 在 regime B **更差**：FedAvg `+3.121…+4.094 %`、oracle `+3.752…+4.751 %`，CI 全排除 0、240/240 seed 对同号。伴随：FedAvg `Δ_group −5.87…−8.20 %`、`RMSE −5.18…−6.38 %`、tail `−5.24…−6.70 %`。
- **P1**（`P1_REPORT.md` `6fa89510…`）：对照 40 格 `max|Δ| = 2.220e-16`；FedAvg C0 `E_dec` A `0.336755` → B `0.087341`，r `−38.91 %` CI `[−59.99, −17.84]`，真阳性保留 A **33.8 %** vs B **0.1 %**。扫描：T=25 两侧全过预测、T=50/75 两侧全漏、T=35 唯一不对称来自 A 的误报 vs B 丢掉全部真阳性。
- **P2 被自己的门停住（2/12）**，两个原因：(a) 回放缺逐条件注入（θ / `diurnal_blind` / block-uniform 的 μ）；(b) C4/C5 A 侧条件无效（条目 49）。
- **P2B**（`P2B_REPORT.md` `c0c7e5ad…`）：忠实回放（`H.injected` + 重标定 μ + 条件匹配的 oracle A 侧）→ **7/12**；`P2B_ADDENDUM.md` 的 A4 只用"审计 θ 值"豁免 oracle C1 30014。
- **P2C**（`P2C_REPORT.md` `851c67a9…`）：判据 C1 = **该 run 自己的末窗 `active == False` 且 `a_r_size == 0`**（即 2026-09-29 审计 `A1_INACTIVE_FINAL_SWEEP.csv: last_active` 的字段，只对冻结树穷举过）。**用前先验区分度**：6/6 失败 A 侧格命中、0/198 通过 A 侧格命中、0/204 B 侧格命中。扩到 C2/C5 → **11/12**。
- **P2D**（`P2D_REPORT.md` `00b759e2…`）：扩到 C1 → **12/12**，6 个豁免格（`C1 30014`、`C2 30002`、`C5 30002` × 两臂对），每个受影响集合**两报**（主 n=16 / 声明式敏感性 n=17）。
- 最终读数（12 集合、6 条件、2 臂族）：`E_dec` 在 regime B 低 **20.1–39.1 %**（CI 全排除 0），**全部来自误报抑制**（A 0.20–0.28 → B 0.001–0.006），B 的超标质量保留 **0.00–2.48 %** vs A **17.5–33.9 %**。**没有任何集合支持"某一侧决策更好"。**
- 全程守住：容差 `1e-12` 未动、判据用前验证、豁免逐格披露并用敏感性对冲、触发 seed 始终排除、端点/带/标签/量表一致。`round_v1/MANIFEST.sha256` 43 项；`round_v3_fix/MANIFEST.sha256` 另有。

### 2.6 门控剂量轮（Claude 指令；**只到侦察，未写驱动**）

- 指令文件（只读副本）：`C:\Users\szr\.dsh\attachments\v1\files\56\56607091831dbaff735061019b6c82cb5a89d2b09c465083cac70c967ee2b59b\raven-mcs-gate-dose-execution-prompt.md`，sha256 `56607091…`，11 275 B。要点：
  - 输出**仅** `results_gate_dose/round_v1/`；驱动**新** `scripts/gate_dose.py`；**不得改 `src/`**。
  - 禁止：改 `src/`、手稿、`artifacts/`、任何既有 `results_*`；跑后再选掩码键/加水平/加 seed/加臂；改端点、估计量、bootstrap seed、判定规则；为决策合并两个数据集；git commit/push。
  - **训练只在用户写出 `授权门控剂量` 之后开始**；§2 的 m=0 门（8 次训练）也属于该授权；门失败则其余全不跑。
  - 因子：掩码**正** π^tar 键的比例 m（掩码键 π^tar = 0）。掩码构造已锁：候选=生产 test-split 下 `pi_tar > 0` 的键按字典序排序；顺序由 `numpy.random.default_rng(20261007)` 每数据集抽一个置换，抽一次；水平 m 掩掉该顺序前 `round(m·n_positive)` 个键；**嵌套**。写 `MASKS.json`（置换、`n_positive`、每水平键表）并把其 sha256 放进 `MANIFEST.sha256`，**在任何训练之前**。
  - 水平：SS `m = 0, 0.10, 0.25, 0.40`；UA `m = 0, 0.10, 0.20`（m=0 用存储产物，放在 §2 门之后）。臂：`raven`（Design on）与 `raven_wo_design`（Design off）；`local_steps = 2`；seed 30001–30020；不重生成轨迹。总数 **208** 次训练（8 门 + 120 + 80）。
  - 三个目标消费者必须一致：`pi_target_override`、`μ`（用于 Δ_group 与 RMSE_μ 权重，按掩码 test split 重建，"the same way `run_h_headroom.injected` patches `production_target_bundle`"）、Δ_c-s 用的 client×stratum 目标。训练前写 `TARGET_WIRING.json`，并断言：m=0 时每个消费者与生产对象**哈希相等**；任意 m 时 `μ_g` == 掩码 test 单元的组份额（1e-12）；`Σμ = 1`、`Σπ^tar = 1`（1e-12）。
  - m=0 门（seed 30001–30002、双臂、双数据集 = 8 run）：对 `artifacts/e3_formal_runs_r1/runs/<ds>/raven/seed<seed>/final_metrics.json` 与 `artifacts/e4_core_mechanism_ablation_r1/runs/<ds>/raven_wo_design/seed<seed>/final_metrics.json`，要求 `|ΔRMSE_μ| ≤ 1e-9`、`|ΔΔ_group| ≤ 1e-9`、`|ΔΔ_c-s| ≤ 1e-9`、逐窗 `active_clients` 相同。任何未过写 `GATE.json`（`pass: false`，JSON 布尔）并停；**无豁免名单**。
  - 打分：从各 run 的 `final_metrics.json` 读四个端点；**末窗 inactive 的 run 用保存的 θ checkpoint 重打分**（"the paper's canonical rule (the `P2C_ADDENDUM.md` §C1 criterion)"）；末窗 active 的 run 须"stored vs θ re-score ≤ 1e-8"，未过即停；所有 θ 打分的 run 列入 `THETA_SCORED.csv`，主分析含它们、敏感性排除。
  - 实现化的 ρ：`scripts/c1_deletion_driver.py::rho_for` 语义（导入或逐字复制）= **非 test split 上 U=1 已投递风险单元中 `pi_tar ≤ 0` 的份额**；不依赖模型输出；训练前算好写 `RHO.csv`；m=0 必须复现 SS `0` 与 UA 的 `≈0.354`，偏差超 **1e-6** 即停。
  - 估计量与判定（已锁）：每 (dataset, level, seed) 的配对相对 Design 代价 `r_e = (M_e(raven) − M_e(raven_wo_design)) / M_e(raven_wo_design)`，`e ∈ {RMSE_μ, Δ_group, Δ_c-s, Tail}`。**H1（主）**：按数据集把 `r_RMSE` 对实现 ρ 做 OLS 得斜率 `b`；区间 = seed-cluster bootstrap（重抽 20 个 seed 连同其所有水平，10 000 次，`numpy` seed `20261007`，percentile 95 %）。标签：SS 主 → CI 下界 > 0 = `open`；CI 上界 < 0 = `harm`；否则 `null`；UA 同三标签。**`gate_law = supported` 当且仅当 SS `open` 且 UA 非 `harm`**；不得重测 `harm`；不得给 `null` 加水平或 seed。**H2**（仅当 H1 支持时）：SS m=0 上 Design on 的非劣性——`r_RMSE` 的 95 % t 上界 < `+0.5 %`。描述性（不决策）：`r_Δc-s`、`r_Δgroup`、`r_Tail` 的同款斜率/区间、各水平均值 t 区间，以及 H1 拟合的交叉点 `ρ* = −a/b`（含 bootstrap 区间，仅当 H1 为 `open` 时报告；它是拟合值不是新门）。
  - 结果表：`tables/DOSE_CELLS.csv`（每 (dataset, level, seed) 一行：`rho`、双臂四端点、四个 `r_e`、`theta_scored`、来源路径）、`tables/DOSE_SUMMARY.csv`、`tables/DOSE_SLOPES.csv`、`DOSE_DECISION.json`（门、H1 标签、`gate_law`、H2 或 `not_tested`、`ρ*` 或 `null`）。
  - 已声明的局限：水平同时改变 ρ 与部署目标（但同一水平内两臂看同一目标，故 `r_e` 是水平内对比）；掩码是随机的、非结构化的（整块时间掩码是另一个实验）；两个数据集、无 City Scanner（其 ρ 无法同法剂量化）。
- **本会话已完成的侦察（只读，`\u200b.rb_work/gate_dose_recon.py`）**：
  - π^tar 支撑：SS **440** 键全正；UA **288** 键、**216** 正 / **72** 零。
  - **μ == test 单元组份额，逐元素完全相同**（`max|share − μ| = 0.000e+00`；SS 220 组、UA 144 组；两组 μ 之和 = 1.000000000000000，无零元）。→ 掩码后 μ 的构造就是"未掩码 test 单元的组份额"。
  - 训练原子（`split == "train"`）数：SS **10 285** / UA **5 688**；ρ(m=0) = **0.000000**（SS）/ **0.354430**（UA），与 `post_review/C2_scd_phi/tables/SCD_PHI.csv` 的 `phi_train_unit`（0 / 0.35443）**完全一致**，也与 `appendix.tex` L2436-2437 的 `tab:scd_phi_freeze`（0 / 35.4 %）一致。
  - 掩码键数（Python `round(m·n_positive)`）：SS **44 / 110 / 176**（m=0.10/0.25/0.40）；UA **22 / 43**（m=0.10/0.20；`round(21.6)=22`、`round(43.2)=43`）。
  - 生产目标工件：`artifacts/e3_semantic_alignment_and_runner_integration_closure_r1/E3_{SENSORSCOPE,UAIR}_TARGET_SEMANTICS_R2.json`（`n_groups` 220/144，`mu` 长度与之相等，SS/UA `uses_e1_time_only_target` 非真，`uses_repeatable_time_of_day_mapper = False`）。
  - 门所需的存储产物**都存在**：`artifacts/e3_formal_runs_r1/runs/{sensorscope,uair}/raven/seed*`（各 20）与 `artifacts/e4_core_mechanism_ablation_r1/runs/{sensorscope,uair}/raven_wo_design/seed*`（各 20）；轨迹目录 `artifacts/e3_formal_runs_r1/eventtraces/<ds>/seed<seed>/training_eventtrace`；冻结 config 的 `local_steps = 2`、`scenario = complete_aligned`。
  - `raven_wo_design` 已在 UA seed 30001–30002 验证**逐位复现**（`results_active_set_repair/round_v1/C1_RAVEN_WO_DESIGN_REPRO.json`，2026-09-27，"all_bit_equal": true，三指标 `abs_diff = 0.0`）。
  - 代码事实：`run_e3_real(...)` 接受 `pi_target_override`（会写进 `config_snapshot.json` 的 `pi_target_mode = "override"`），并把 `pi_target` 与 `target_mu` 传给 `build_full_runner`；**μ 只能经 `production_target_bundle` 注入**（该函数从冻结工件取 μ，SS/UA 走 `load_frozen_target_artifact`），所以掩码 μ 必须靠 monkeypatch（与 `run_h_headroom.injected` 同法），**不改 `src/`**。
  - θ 重打分的**已有规范实现只覆盖 RMSE_μ**：`results_seed_path_audit_r1/c9_h_theta_recheck.py`（`predict()` 遍历 test 单元 + `rmse_mu()` 按组质量加权；`CommonNDMF`/`DiurnalBlindNDMF`、`torch.load(..., weights_only=False)`、取 `state_dict`）。Δ_group/Δ_c-s 的 θ 重打分路径**尚未建立**。

---

## 3. 关键决策与原因

1. **round-12 用 version-comparison 模式**：手稿在上一轮评审后确实变过（r11 的 4 hunks），所以必须把"相对进步"与"绝对就绪度"分开报，不能合成一个数。
2. **Terminology 3→4，导致 `improved` +0.05**：历史条目自己写的修复条件是"one sentence that renames one of the two uses"，两处都改了、只剩一义 → 扣除项消失。分类正好压在阈值上已披露；**没有**为了好看四舍五入成 `unchanged`。
3. **只做 M2 / M4 / CL-3 三处正文修改**：纯文字、零数字改动、17 pp 未涨；E2 的"以投影领衔"重排与 NEW-r12-3 的命名统一**没做**（前者评审明说单靠它不动分、后者评审未扣分），记录为 open 而不是偷偷改。
4. **C4/C5 修复写进新树 `round_v3_fix/` 而非覆盖**：条目 49 引用有缺陷的旧 run，覆盖会毁掉审计线索。
5. **豁免必须"先验证判据再使用"**：P2C/P2D 的豁免建立在"末窗 inactive"这一**既有字段**上，用前先做区分度检验（6/6 vs 0/198），且**不撤回**任何既有豁免路线（P2C 打分器第一次跑时漏了 P2B 的 A4 路线，导致 oracle C1 从通过退回失败，已改为并集后重跑）。
6. **端点轮的 `go` 不等于"有 oracle 余量"**：2×2 显示 regime ≈6 %、权重/信息 ≤0.3 %，且论文自己已列 Design-removal 行（−6.885 % RMSE、+4.990 % Δ_c-s），所以 `go` 读作"支撑成本效应/regime 开关"，不授权任何新论断。
7. **两套技能角色不越界**：评审不改正文/台账；rebuttal-writer 出回复函与台账、把正文改动交 paper-writer；experiment-designer 出协议。本会话就是按这个顺序执行的。
8. **门控剂量轮先只做 P0**：指令自己把训练锁在用户写出 `授权门控剂量` 之后，用户本次没写，所以即便用户说"请执行之"，也只能执行到 P0 与驱动编写。

---

## 4. 失败尝试（不要重复）

| 失败 | 现象 | 结论/替代 |
| --- | --- | --- |
| round-2 用改轨迹 `U` 来修 FedAvg 复现 | 差 0.145–0.170 % | 错对象；正确是 `m_total = 0`（round-3，精确 0.0） |
| 给 `supplemental.bbl` 的 `\bibitem` 加前缀 / 抑制 `\citation` | 仍 warning（冲突来自 `\bibitem` 写 `\bibcite`） | 采用 `\makeatletter\@fileswfalse\makeatother` 包住 supplemental 的 `\bibliography`，且**先构建 supplemental 再 main** |
| 把 A 侧一律指向冻结目录（P0 首跑） | 60 个 oracle 格被判 `trace_hash` 不配对 | 冻结集只有 C0 轨迹；改为"取与 B 侧同轨迹的 Design-on oracle" |
| P2 首跑的回放缺逐条件注入 | 门失败（A 侧最大 `9.09e-02`，B 侧 `3.26e-03`） | 在 `H.injected(CONDITIONS[cond], block_factor=factor)` 内建 runner + 传重标定 μ + 条件匹配 A 侧 |
| `r3_p1p2.train_fedavg` 的 `gc = dict(H.CONDITIONS["C0_frozen"])` | C4 与 C0 数值完全相同（block-uniform 无效） | 用 `dict(H.CONDITIONS[cond])` 原样传，方能让 `_bundle` 补丁生效 |
| P2C 打分器首版 | oracle C1 从 pass 退回 fail（漏掉 P2B A4 豁免） | 豁免取并集；扩展不得撤回既有路线 |
| 早前的 `E_floor` LP / "顶点扫描" | LP 给 0.74–13.1（错）；顶点理由也错（凸函数在 polytope 上的最小值一般不在顶点） | 正确闭式：`floor = 0 if min_g m_g ≤ K ≤ max_g m_g else min(|min−K|,|max−K|)`；20 000 次随机搜索佐证；40/40 轨迹 floor = 0 |
| `h_response_shift.py --tables` | 空 seed 集在 `slope_ci` 崩溃 | 加长度/ptp 守卫 |
| `r3_masszero.py` 补丁生成器 | 两次 `IndentationError: unexpected indent` | 用 `textwrap.dedent` + 逐行锚点 + 只缩进函数体 |
| `rb_p1.py` 两次路径错 | `FileNotFoundError: ...\seed%d\training_eventtrace\seed30001\trace_identity.json`；随后 `...round_v1\runs\...\seed30006\config_snapshot.json` | 轨迹路径按 seed 格式化；seed ≥ 30006 在 `round_u1` |
| `rb_p1.py` sweep 收集 | 第一次完整 P1b 产出空 `P1_SWEEP.csv`（行字典已被裁剪） | 在训练循环内收集 sweep 行 |
| S1 screen 的 City Scanner 回放 | 与 `CS_ACCEPTED.json` 最大差 `3.68` → 门 fail、`weighting_path = closed` | CS 被预注册规则排除（不是设置问题，是 runner/checkpoint 接线）；端点轮不碰 CS |
| R0.3 初版无来源限定 | 在新的 `rshift_grid` run 上 STOP | 限定到 `h_round`/`h_gate`，门槛不变；8/8 过 |
| `r0_rescope.py` 输出一句假话 | "seed 30001 reproduces exactly" | 事实是 seed 30001 在两处都差 `−3.959e-02`，已改 |
| 我自己的日期笔误 | 把 2026-10-06 的 H/regime 工作写成 2026-10-05 | 台账 5 处已改为 2026-10-06 |
| 台账编辑事故（更早） | 一个脚本假设 `### MODERATE` 紧跟 M-1，切片删掉了 M-2/M-3/M-4 | 从 `.sync_diag/round10-before-m1-fix.md` 恢复，用三条断言重写并核对 356 行 |
| 本会话最后一步 | 正准备查 `window_runner.py` 的"只打分"路径，**工具调用被中断** | 见 §6 未决问题 2；`scripts/gate_dose.py` 未创建 |

---

## 5. 假设（未证实，需验证）

1. **`raven`（e3 冻结）在 m=0 可复现到 1e-9** —— 只有 `raven_wo_design` 有逐位复现的书面证据（UA 30001–30002）。这是 P1 门的主要风险。
2. **ρ 与 seed 无关**：我的 ρ 帧是静态训练原子集（无模型输出），故 ρ 在每个 (dataset, level) 上对所有 seed 同值；指令说"per (dataset, level, seed)"，且 m=0 的钉值只能由静态变体满足。若要求逐 seed，需要另找逐 seed 的投递帧（未决问题 4）。
3. **掩码后 π^tar 与 μ 需要重新归一化**：因为指令断言任意 m 下两者都 = 1（1e-12）。我据此实现（掩码键置 0 后除以剩余质量之和）。
4. **臂不需要注入 `m_total` 规则**：`raven`（Design on，ζ 使零质量对权重为 0）与 `raven_wo_design`（Design off）在 m=0 应能直接复现；若不成立，门会给 `pass: false` 并停。
5. **`round_v3_fix` 的修复不影响论文任何数字** —— 已验证其 Δ_c-s 逐位不变、H 判决不变；但"论文不需要因条目 49/50 修改"这一点是判断，不是测量。
6. 早前提到的仓库卫生问题（未跟踪文件、`src/` 漂移、截断文件、bundle 计数、nodesign 数据集错配）均**未在本会话复验**。

---

## 6. 未决问题

1. **`raven` 的 m=0 复现性**（见假设 1）——P1 一跑即知；失败则整轮停在门。
2. **Δ_group / Δ_c-s 的 θ 重打分怎么实现**：现有规范只覆盖 RMSE_μ；需要 `window_runner.py` 的窗口循环在 θ 冻结下重跑（例如 `local_steps = 0` 或学习率为 0），或改写为"加载 θ 后重算窗口结构指标"。这是我被中断时正在查的问题。
3. **ρ 的容差解读**：指令写"复现 SS 0 与 UA ≈0.354，偏差 > 1e-6 即停"。打印值是 35.4 %（= 0.354，3 位有效），未取整的存储值是 **0.35443**；只有用后者才能满足 1e-6。我按"对照 `SCD_PHI.csv` 的 0.35443"实现，并同时报告与 0.354 的差。**需要用户确认这一解读。**
4. ρ 的 seed 维度（假设 2）。
5. 门通过后是否允许把 `raven`/`raven_wo_design` 之外的臂纳入后续轮次（指令明确禁止，仅确认理解）。
6. 早前授权但**未做**的收尾事项（来自更早的轮次，未在本会话处理）：`PAPER_NUMBERS.csv` 的两行假 `UNLOCATED`、6 行换算来源、4 行"存了但未印"；递归/H 轮的记录更正（H `H9(a)` 撤回、`R5-6`/`F1`/`F8` 的过期引文标签、21-vs-20 闭合计数）；`EV-1` 的 `0.027 → 0.024`；U1 与 H 的 C1–C5 对冻结基线重算；Part C 的 SS/U-Air 确证；W4 的 FedIPW/FedPALS 映射；公开 bundle 的完整复验；`.m7_work/`、`.sync_diag/`、`.r11_work/` 的清理。
7. City Scanner 的 ρ 无法同法剂量化（指令已声明排除）——若将来要覆盖，需要单独设计。

---

## 7. 下一步（建议顺序）

1. **回复用户的两个确认点**：ρ 容差解读（未取整 0.35443）、ρ 的 seed 维度。若用户不接受，改的是驱动实现而不是结果。
2. **写 `scripts/gate_dose.py` 的 P0**（无训练）：MASKS.json（rng `20261007`、每数据集一个置换、字典序候选、嵌套、写 sha256）、TARGET_WIRING.json（三消费者 + 三条断言；μ 由未掩码 test 单元的组份额重建，π^tar 掩码后重新归一化）、RHO.csv（`rho_for` 语义逐字复制并注明来源与哈希）、MANIFEST.sha256。跑 P0，把 m=0 的 ρ 钉值（0 / 0.35443）与三条 wiring 断言结果写进报告。
3. **补齐 θ 重打分**（未决问题 2），并在驱动里内置 §2 门；**但不要跑 P1/P2**，直到用户写出 **`授权门控剂量`**。
4. 用户授权后再按 P1（8 run 门）→ P2（200 run）→ P3（表与判定）执行；`gate_law`、H1/H2 标签、`ρ*` 全部按 §2.6 的锁定规则报，任何 `harm` 都按测得报、`null` 不加水平/seed。
5. 之后的写作（若用户要求）：只有 `gate_law = supported` 才允许写"一个事前结构统计量预测对齐因子的预测代价的符号与大小"；**不得**写"对齐改善了预测"；任何手稿改动另开请求，并先走 `ccf-humanization` 预检。

---

## 8. 路径与命令清单

**环境**
- Python：`C:\Cursor\raven.mcs\.venv_new\Scripts\python.exe`（3.11）；PowerShell 控制台是 GBK：**不要**用 `python -c` 带中文/引号，写 `.py` 文件跑；文本文件用 `[System.IO.File]::WriteAllText($p,$t,(New-Object System.Text.UTF8Encoding($false)))`。
- 构建（在 `TO_OVERLEAF_paper_tmc_r1_clean/` 内，顺序固定）：
  `pdflatex -interaction=nonstopmode -halt-on-error supplemental.tex` → `pdflatex ... main.tex` ×2；检查 `main.log` 的 `Output written on ... (17 pages`、`^!` 计数、`undefined`、`multiply defined`、`Overfull`。
- 技能在磁盘上（**不在**会话的 skill 目录里，需要直接读 SKILL.md）：`CCFA-Skills/{ccf-paper-reviewer,ccf-paper-writer,ccf-experiment-designer,ccf-rebuttal-writer,ccf-common,...}`；评审校验器 `CCFA-Skills/ccf-paper-reviewer/scripts/validate_version_comparison.py <json>`。

**本会话产物**
- 手稿与快照：`TO_OVERLEAF_paper_tmc_r1_clean/main.tex`（`02447bfe…`）、`snapshots/2026-10-06-pre-r12-fix/`、`snapshots/2026-10-06-pre-round12-raven-mcs-tmc-review.md`、`snapshots/2026-10-04-pre-r11/`。
- 评审与台账：`ccfa-review-reports/raven-mcs-tmc-review.md`（r12 canonical）、`raven-mcs-r12-response-to-review.md`、`raven-mcs-metric-definition-diagnosis.md`（Part VII + 条目 45–52）。
- 端点轮：`results_regime_b_endpoints/round_v1/`（`DESIGN.md`、`P0_REPORT.md`、`P1_REPORT.md`、`P2_REPORT.md`、`P2B_ADDENDUM.md`/`P2B_REPORT.md`、`P2C_ADDENDUM.md`/`P2C_REPORT.md`、`P2D_ADDENDUM.md`/`P2D_REPORT.md`、`tables/P*_*.csv`、`MANIFEST.sha256` 43 项）；执行器 `.rb_work/{rb_endpoints.py,rb_p1.py,rb_p2.py,rb_p2b.py,rb_p2_gate.py,p2c_score.py,p2d_score.py,repair_c45.py,rederive_h_fix.py,...}`。
- H/regime：`results_h_headroom/round_v3/`（`PREREG_P2.md`、`EXECUTION_REPORT.md`、`H_DECISION.json`、`tables/*`、120 个 run）、`results_h_headroom/round_v3_fix/`（40 个修复 run、`tables/H_SUMMARY_fix.csv`、`H_FIX_DIFF.csv`、`H_DECISION_fix.json`、`MANIFEST.sha256`）。
- 门控剂量：**只有** `.rb_work/gate_dose_recon.py`；指令只读副本见 §2.6；`scripts/gate_dose.py` 与 `results_gate_dose/` **尚不存在**。

**门控剂量要用的既有输入**
- 目标工件：`artifacts/e3_semantic_alignment_and_runner_integration_closure_r1/E3_{SENSORSCOPE,UAIR}_TARGET_SEMANTICS_R2.json`
- 冻结 run：`artifacts/e3_formal_runs_r1/runs/<ds>/raven/seed*`、`artifacts/e4_core_mechanism_ablation_r1/runs/<ds>/raven_wo_design/seed*`
- 轨迹：`artifacts/e3_formal_runs_r1/eventtraces/<ds>/seed<seed>/training_eventtrace`
- ρ 的既有对照：`post_review/C2_scd_phi/tables/SCD_PHI.csv`（`phi_train_unit` 0 / 0.35443）、`scripts/compute_scd_phi.py`、`appendix.tex` L2436-2437
- 待逐字复制的函数：`scripts/c1_deletion_driver.py::rho_for`
- θ 重打分参考：`results_seed_path_audit_r1/c9_h_theta_recheck.py`
- 掩码 μ 的注入参考：`scripts/run_h_headroom.py::injected`（patch `production_target_bundle`）
- 未掩码/掩码断电开关：`src/raven_mcs/e3/real_runner/runner.py::run_e3_real`（`pi_target_override` 生效；μ 经 bundle）

---

## 9. 约束（不要违反）

- **训练授权**：门控剂量轮必须等用户写出 `授权门控剂量`；P0 可以跑。
- **不改**：`src/`、手稿、`artifacts/`、任何既有 `results_*`（门控剂量轮的禁止清单）；不回改论文数字；不 git commit/push。
- **预注册纪律**：先写规则再算；不因看到数值而放宽门槛、加豁免、换端点、换 seed/水平/臂、改 bootstrap seed 或判定规则；不为决策合并两个数据集。
- **停止规则**：门失败就停并如实写 `pass: false`+原因；没有豁免名单；`harm`/`null` 按测得报，不给 `null` 加料。
- **披露纪律**：任何执行缺陷（路径、解析器、收集顺序）都要在报告里写明并给出修法；豁免格要逐格披露并用敏感性对冲。
- **归属纪律**：评审不改正文/台账；正文改动由 `ccf-paper-writer` 执行且需明确授权；台账由 `ccf-rebuttal-writer` 维护。
- **语言**：与用户交流用中文；报告与产物用英文（沿用既有文件风格）。

---

# Part 2 — 2026-10-07 修订（另一 Agent 的四轮 + 手稿改动）

## 10. 修订后的状态速览（以本节为准）

| 项 | 10-06 原版 | **10-07 现状** |
| --- | --- | --- |
| `main.tex` | `02447bfe6256632b…`，113 854 B | **`68D9B44F17A4E48D…`**，116 379 B，mtime **10-07 17:05**（+45/−1 行，相对 `02447bfe`） |
| 构建产物 | 17 pp | **过期**：`main.pdf`/`main.log`/`main.aux` 仍是 **10-06 20:45** 的 17 pp 版本，**新段落尚未编译** |
| 台账 | 条目到 52，Part VII | 新增 **Part VIII**（`items 53–62`，10-07 15:28），但 **§VIII.3 已过期**（它写 "`main.tex` `02447bfe…` unchanged, 17 pp" 与 "NSW-Traffic … has not been run and no number from it exists"——两者现在都不成立） |
| 新的实验轮 | 无 | **四轮**：`results_evidence_axis/round_v1`（写作提案）、`results_estimand_selection/round_v1`、`results_gate_dose/{round_v1 STOPPED, round_v2 执行}`、`results_new_block_traffic/round_v1`（S0+S1） |
| 门控剂量轮 | 我等 `授权门控剂量` | **另一 Agent 已执行到底**（round_v2，246 runs / 200 dose cells），但经 **G3 门槛修正 1e-6→1e-5**（用户授权 "修正G3"） |
| Evidence 轴 | 未修复（r12：Evidence 3） | **四条路线的必要条件的全部测量**：权重自由度、估计量选择、gate 定律、交通新块——**全部为负**（详见 §11）；手稿 17:05 写入了"bound"叙述 |
| 新发现的缺陷 | — | **发布 bundle 与工作树不一致**（E4 ablation 10/40 行，见 §13.1）；**三个脚本被截断为 2 字节且不可恢复**（§13.2） |
| 评审/审计 | r12 canonical（`32BA5AE2…`） | **尚未**为 10-07 的改动跑过 `ccf-integrity-auditor` 或 `ccf-paper-reviewer`（＝下一步） |

## 11. 10-07 新增的四轮（事实）

### 11.1 round 13 — `results_evidence_axis/round_v1`（08:29–08:48，无训练）
三份文档：`EVIDENCE_BASE.md`（约束图）、`DESIGN_BRIEF.md`（方向选择）、`WRITING_PROPOSAL.md`（C1 路线：写出测得的 bound）。
- 结论：SensorScope/U-Air 上**没有任何** Evidence 正向路线；建议只写 bound。
- 关键数：目标近均匀——最大组份额 **0.53 %**（SS，220 组）/ **0.79 %**（UA，144 组）；`1 − H/H_max` = **0.0027 / 0.0010**；窗口贡献客户端只触及目标正质量的 **0.67 %（SS）/ 0.89 %（UA）**（最好窗口 1.70 % / 2.57 %）；六条规则间 `RMSE_μ` 跨度 **0.026 pp（SS）/ 0.357 pp（UA）**；固定 checkpoint、只改**评估**权重时 `RMSE_μ` 与均匀加权差 **0.8208 %（SS）/ 0.2660 %（UA）**（**仅评估层**，不得用来 bound 训练）。
- 提案自带四项"防错"更正（MDE 方向、固定 checkpoint 的范围、被撤回的 "composition" 改名、跨数据集复制）与"deliberately does not claim"清单（**不**声称"对齐改善预测"）。

### 11.2 round 14 — `results_estimand_selection/round_v1`（09:12–09:54）
标签：SS/UA **均 `saturated`**（`d̄ = 0`，Wilson [0.000, 0.161]；regret 0.000000；Kendall τ = 1.000；符号翻转率 0.0000）。
- 到达律加权的验证**误报**部署风险：**−4.11 % 到 −4.12 %**（SS，九条候选全部，t 区间排除零）/ **+0.27 % 到 +0.62 %**（UA），但**排序完全不变** → 水平位移，不是排序变化。
- `TV(π_arr, μ)` 组级 **0.3548（SS）/ 0.4255（UA）**；`WEIGHTS.csv` 在其自身阶段先写（已注册）。

### 11.3 round 15 — `results_gate_dose/round_v2`（10:21–13:00；246 runs，200 dose cells）
- **`gate_law = not supported`**；H1 斜率 **+0.001365**（SS，CI [−0.003556, +0.006356]）与 **−0.073079**（UA，CI [−0.165370, +0.022770]），**两者 `null`**；H2 `not_tested`；`ρ*` 不报。
- 描述性：`r_Δc-s` 斜率 **−0.1331（SS）/ −0.3565（UA）**，区间**严格为负**（SS −0.6 %→−5.8 %；UA −4.8 %→−8.8 %）；`r_Δgroup` 在两个数据集**变号**（+0.0568 / −0.1523）；SS 预测端点的剂量响应**最多 +0.17 %**（对 δ = 0.5 %），UA 为 **+6.6 %–7.5 %** 且**随 ρ 递减**。
- **H3**：`gate_decision = null`，且**结构上不可达**——ρ = 0 时 gate 的规则**就是** `always_on`（20/20 seed 差恒为 0），协议要求两个比较的 CI 上界都 < 0，故 `open` 不可能出现。（记录以免将来重复提议该比较。）
- **G3 修正**：原门（相对 1e-6）**未过**，40 格中 3 格失败（SS `Δ_group` seed 30019 = **1.516e-06**；UA `RMSE_mu` seed 30002 = **2.229e-06**；中位 ~5e-9）；`GATE_AMENDMENT.md` 记录原判保留、修正为 **1e-5**（用户授权），并加 **p95 ≤ 2e-6** 的合取条件；替代确认规则的初版（新 seed 30021–30025）**被书面撤回**，因为冻结产物与轨迹只到 seed 30020。
- `round_v1` 的 **P0 只跑了 P0 就按用户指令 STOP**（`STOPPED.md`）：无训练、无 `GATE.json`；保留下 masks/wiring/RHO 作为预注册线索（内容哈希 `masks 6b456bd378e92ead…`、`wiring b9de9d9b7d7e7823…`、`RHO.csv 302cd48c779e9a2a…`）。

### 11.4 round 16 — `results_new_block_traffic/round_v1`（15:19–16:27）
- **S0（只读）`go: true`**：`e3_complete_aligned` 族 20/20 seed；**N1 成立**（窗口均值 **12.06** 客户端，`≤2` 的窗口占 **6.69 %**，最大 28）；**N2 成立**（`TV(π_arr, μ)` 均值 **0.35638**；冻结目标 **172 组**、μ **精确均匀**，top-1 0.581 %）；轨迹侧的 `debt_cal` 交叉核对给出 12.08 / 6.83 %。
- **S1（阶梯）`go: false`，`failed: "N3"`**：`c = central_delivered` 均值 **0.977673231150311**，阈值 `1.01c = 0.9874499634618141`；四个 `local_steps` 水平（2/5/10/20）比值 **1.02962 / 1.02814 / 1.02780 / 1.02911**——**没有一个**落在 1.01c 内，最好的（10 步）只比 2 步低 **0.1765 %**（回退条件要求 ≥1 %）；即"2.8–3.0 % 的差距不是优化预算"。
- **S2 从未运行**（`F` seed 30006–30020 未被读取/训练/评分）。S0 的预测性分析显示该块联邦臂**数值上接近常数预测器**（比最优常数只好 0.3 %，测试集 z-score 化：均值 0.00000、sd 1.0、范围 −0.96…+7.95），**没有任何臂发出告警**（最大告警份额 0.00000），base rate 0.0990 但 recall 0.00 → GO-D 失败、`mean ΔF1 = 0.0000` 失败；作者标注这是"**预测，不是判决**"，并指出这是 `NEW-r12-1` 的镜像（那边因告警过多饱和，这边因没有告警饱和）。
- 披露：S1 的 level-2 是**继承**自 E2 冻结产物（`GATE_AMENDMENT_A1.md`），不与新跑的 rung 数值互换；`S1_BLOCKED.md`（修正前的拒绝）被保留。

## 12. 手稿 17:05 的新改动（相对 `02447bfe`：5 hunks / +45 / −1）

其中 3 个 hunk 是我 10-06 的 M2/M4/CL-3（未被改动）。**新增两段**：

1. **机制段**（`\noindent\textbf{Why the weights leave the prediction endpoint flat.}`，插在天花板小节末尾、Limitations 之前）：冻结 `E_min = 3` 时 `Ē_r = min(3, K_r)`，单纯形上 `‖α‖₂² ≥ 1/K_r` 且等号仅在 `1/K_r`，故 `K_r ≤ 3` 的窗口**只容许均匀权重**；20 个冻结 seed 上 **78.6 %**（SS，1877 个活跃窗口）/ **90.2 %**（UA，Design on，1402 个）/ **79.0 %**（UA，Design off，1515 个）；目标最大组份额 0.53 % / 0.79 %；结论"移动 `RMSE_μ` 的是 Design，它改变**哪些窗口活跃**，而不是窗口内部的权重"。
2. **Limitations 新增段**（三条测量）：到达律加权验证的误报（**−4.11 % 到 −4.12 %** SS、**+0.27 % 到 +0.62 %** UA，但 20/20 seed 选出同一配置）；掩码最多 **40 %** 正目标键使 `ρ_r` 从 0 升到 **0.388** 而 Design 的预测代价不超过 **0.17 %**，UA 在 `ρ_r` 0.354–0.466 之间代价保持 **6.6 %–7.5 %** → "**该统计量是门控的支撑条件，不是其代价大小的预测器**"；NSW-Traffic 上窗口平均 **12.1** 个活跃客户端、四个冻结联邦成员（含 oracle-margin）`RMSE_μ` 相差 **0.002 %** 以内、window FedAvg 在 `local_steps` 2–20 全程比同投递数据的集中式模型高 **2.8 %–3.0 %** → "**是该块的联邦学习器、而非加权，限制了这个端点**"。

**这些数字的可追溯性（我抽查过的）**：`12.1 / 6.69 %` → `results_new_block_traffic/round_v1/{S0_REPORT.md,S0_FOLLOWUP.json}`（N1）；`0.002 %` → 同处四臂 `RMSE_μ` 1.003476–1.003491 与 `S0_FOLLOWUP.json:crosschecks_section_0/federated_arms_RMSE_mu_mean`；`2.8 %–3.0 %` → `S1_LADDER.csv` 的 `ratio_to_c` 1.0278–1.0296；`78.6 % / 90.2 % / 79.0 % / 1877 / 1402 / 1515` → `.rb_work/evidence_headroom/{HEADROOM.csv,MASK_CONCENTRATION.csv,CONCENTRATION_COUNTERFACTUAL.csv}`（存在，但列到句子的映射**尚待逐格核验**）；`−4.11…−4.12 % / +0.27…+0.62 %` → round 14；`0.17 % / 6.6–7.5 % / 0.388 / 0.354–0.466` → round 15（`DOSE_SUMMARY.csv` / `DOSE_DECISION.json`）。

## 13. 我在本轮新发现、必须上报的问题

**13.1（Reproducibility，最重）发布 bundle 的 E4 ablation 图数据与工作树/论文不一致。**
- 工作树 `TO_OVERLEAF_paper_tmc_r1_clean/figure_data/FIG_E4_E4_COMPONENT_ABLATION.csv`（sha256 `998CDAC5982C…`）：U-Air Design `RMSE_mu = −6.885464`、`Tail_RMSE = −7.221249` → **正是论文印的 6.885 % 与 7.221 %**。
- 发布 bundle `RAVEN_MCS_PUBLIC_REPRO_R1/figures/FIG_E4_E4_COMPONENT_ABLATION.csv`（sha256 `C80F6DDDABD7…`）：同两格为 **−6.553094 / −6.875243**（θ 重采样之前的值）。
- 两文件 **40 行中有 10 行不同**（全部是 U-Air 的 `RMSE_mu`/`Tail_RMSE`，组件 Design/Obs/Use/Inst/Debt）。
- 结论：(a) 另一 Agent 在 `WRITING_PROPOSAL.md` 里提出的 "6.885 匹配不上任何列" 的疑虑 **可以用来源选择解释**——它对照的是 **pre-θ** 的 `RAVEN_MCS_PUBLIC_REPRO_R1/tables/E4_ABLATION_RELATIVE_CHANGE.csv`，而论文用的是 **θ 重采样后**的 `figure_data`（台账 items 47/48 记录了 `6.553→6.886`、`6.875→7.221`）；(b) 但**真正的缺陷是 bundle 落后于论文**：bundle 里那份 figure_data 仍是 θ 前的值，`verify.py` 只做哈希核对、发现不了这个不一致。**必须由 integrity 审计定案**（我未检查 bundle 的 `MANIFEST.csv` 是否声明了这两个文件）。

**13.2（不可恢复）三个脚本被截断为 2 字节且未被 git 跟踪。**
- `scripts/compute_cityscanner_phi.py`、`scripts/run_c1_cityscanner.py`、`scripts/run_p2_nt_e3.py`：大小 **2 B**，同一个哈希 `7EB70257593D…`，mtime **10-07 19:11**；`git status` 显示三者均为 **`??`（untracked）**；我在整个工作区（含 `deliverables/`、`RAVEN_MCS_PUBLIC_REPRO_R1/`）**找不到任何有内容的副本**。→ **内容已丢失**，只能由写过它们的 Agent 重写或从别处恢复。
- 同一时刻（19:11）`scripts/run_c1_tdrive_spatial.py`（47 177 B，有内容）与 `TO_OVERLEAF_paper_tmc_r1_clean/reference.bib` 也被 touch；`reference.bib` 内容**未变**（哈希仍 `3F0BE0112FA9…`）。

**13.3（记录过期）** 台账 `Part VIII` §VIII.3 与 10-07 之后的两次事件矛盾（手稿已被改、交通轮已运行并给出 `go: false`）；`Part VIII` 正文也自述 "no manuscript file … was edited by any of them"，这在 17:05 之后不再成立。

**13.4（构建）** 手稿改了但**没有重编译**：`main.pdf`/`main.log`/`main.aux` 都是 10-06 20:45；新段 +45 行，页数未知（很可能从 17 pp 增至 18 pp，而 18 pp 是 MOPC 上限）。

**13.5（数字争议未决）** `A1_POWER.csv` 的 `mde80` 列**无法由本列输入复现**（item 55：列自报 0.00445 / −0.000758，而 `2.802·s_d/√n` 给 0.00618 / 0.0649），且 `EV-2`（U-Air MDE 尺度错一个数量级）仍 **open**。手稿 17:05 的新段**没有**引用 MDE（改用机制 + `K_r` 计数），所以这个争议暂不阻塞新段，但它阻塞任何"设计能看见这个量级"的表述。

## 14. 对 Evidence 轴的初步判断（**我的判断，待两个技能裁定**）

- 四条路线的**必要条件**都已测完，且都为负：权重自由度（`K_r ≤ 3` 占 78.6 %/90.2 %，`|A_r| ≤ 2` 占 51.4 %/69.0 %）→ 权重被约束钉住；估计量（到达律加权误报 4 % 但不改排序）；gate 定律（两条斜率 `null`）；gate 决策（ρ=0 时 gate ≡ always_on，`open` 结构上不可达）；交通新块（N3 失败，联邦学习器离集中式 2.8–3.0 %）。
- 冻结的 r12 判据要求 "**一个预注册端点，其 headroom 高于可检测效应，且对齐改变预测或某个部署决策**"。这些轮次**没有**提供这样的正例，它们提供的是"**为什么在此不可能**"的测量。因此我的先验是：**Evidence 仍为 3**（轴未修复），但论文的**叙述质量**显著提升——从"未解释的 null"变成"有分辨率、有机制的 bound"；这可能影响 Clarity/Soundness 的读法，**不**影响立场（venue 的决策量仍未移动）。
- 反向可能性（需评审裁定，不要预设）：如果 `ccf-paper-reviewer` 认为"测得的分辨率 + 机制 + 四条封闭路线"本身构成 Evidence 的实质进展（把 null 从"未解决"变成"已解释的界"），Evidence 可能 3→4 并推动立场。**这必须由评审按 `TMC-J-R4` 独立判断，不得由执行方预先决定。**

## 15. 下一步：给另一个 Agent 的验收清单（`ccf-integrity-auditor` → `ccf-paper-reviewer`）

**顺序与输入**
1. **先跑 `ccf-integrity-auditor`**（技能在 `CCFA-Skills/ccf-integrity-auditor/`，不在会话 skill 目录，直接读其 `SKILL.md`）。审计对象 = `main.tex` **`68D9B44F17A4E48D…`** 相对 10-07 之前的手稿新增的**每一个数字**，逐格对照来源：
   - `78.6 % / 90.2 % / 79.0 % / 1877 / 1402 / 1515` → `.rb_work/evidence_headroom/{HEADROOM.csv,MASK_CONCENTRATION.csv}`（**列到句子的映射必须逐格核验**，这是我最没把握的一组）；
   - `0.53 % / 0.79 %`（最大组份额）→ 同目录 `TARGET_CONCENTRATION.csv`（并注意 round 13 文档里的 0.53/0.79 与 S0 的 172 组均匀 μ 是**不同块**）；
   - `−4.11…−4.12 % / +0.27…+0.62 %` → `results_estimand_selection/round_v1/{SELECTION_DECISION.json,tables/RISK_ROWS.csv}`；
   - `0.388 / 0.17 % / 6.6–7.5 % / 0.354–0.466` → `results_gate_dose/round_v2/{DOSE_DECISION.json,tables/DOSE_SUMMARY.csv,tables/DOSE_SLOPES.csv}`；
   - `12.1 / 0.002 % / 2.8–3.0 %` → `results_new_block_traffic/round_v1/{S0_REPORT.md,S0_FOLLOWUP.json,S1_LADDER.csv,S1_VERDICT.json}`；
   - 并要求它判定 **§13.1 的 bundle 落后问题**（10 行差异）与 **§13.5 的 MDE 争议**（item 54/55）是否阻塞新段。
2. **再跑 `ccf-paper-reviewer`（version-comparison 模式，契约 `TMC-J-R4` 不变）**，历史版 = **`02447bfe6256632b…`**（r12 评审的 "current"），当前版 = **`68D9B44F…`**；要求给出两张记分卡（相对进步 / 绝对就绪度）+ 独立置信度，并**明确回答"Evidence 轴是否得到修复"**，逐条对照 r12 的修复条件（预注册端点、headroom 高于 MDE、决策量不饱和、对齐改变预测或决策）。
3. **`ccf-integrity-auditor` 的补充检查项**（我建议直接写进它的任务）：truncated 三脚本（§13.2）是否影响任何已交付数字的可复现性；台账 Part VIII 的过期句（§13.3）；构建状态（§13.4：重编译 + 页数 + 0 errors/undefined/multiply-defined/overfull）；round 15 的 **G3 修正**是否被正确披露（原判文件是否齐备：`GATE_G3.json`（1e-6, pass:false）、`GATE_REPORT.md`、`GATE_G3_AMENDED.json`、`GATE_AMENDMENT.md`）。
4. **禁止**：不要因为"应该修好了"而调高 Evidence；不要在审计/评审里改正文或台账；两项技能的结论必须各自独立，不得合并成一个数。

**判定标准（预先固定，供两个技能使用）**
- `Evidence` 升到 4 **当且仅当**存在一个**预注册**端点，其 headroom 高于自身可检测效应，且**对齐/结构量改变了预测或某个部署决策**；仅仅"把 null 解释清楚"不满足该条件（但可作为 Clarity/Soundness 的依据）。
- 若 Evidence 不动，需明确写出**剩下的唯一正例路线**（round 13 指出的：目标在聚合层面真正集中的块，例如 T-Drive 的四组 μ 最大组 51.44 %，或一个带声明监测权重的 campaign）——这是一个**新实验**，需要自己的预注册。

## 16. 我未能验证 / 不确定的项（诚实清单）

1. §13.1 的两份 figure_data 差异是否为**唯一**的 bundle-落后点——我只比了这一对文件，没有做全 bundle 对工作树的系统比对。
2. 手稿机制段里 `K_r ≤ 3` 的 78.6 %/90.2 %/79.0 % 与 `1877/1402/1515` 是否与 `.rb_work/evidence_headroom/*` 的**同一口径**（计数的是活跃窗口？Design on/off 分别？我未逐格复算）。
3. 交通段 "四个冻结联邦成员相差 0.002 % 以内" 的分母口径（我按 S0 表里的 1.003476–1.003491 与均值 1.00348 推算得 0.0015 %，与 0.002 % 相容，但未核对 S0_REPORT 的原始表述）。
4. `6.885` 与台账记的 `6.886` 差 0.001（四舍五入 vs 不同重采样），未定案。
5. 三个被截断脚本在被截断前的用途与内容（我只能从名字与 19:11 的时间点推断与 City Scanner / 交通 e3 跑有关）。
6. `main.tex` 17:05 的改动**是否有书面授权**（用户是否对某一具体提案点头）——我在工作区里没有找到对应的授权记录或 writing-pass 报告；这一条必须由另一 Agent 或用户确认。
