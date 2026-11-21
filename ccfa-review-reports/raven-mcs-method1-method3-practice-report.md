# 方法一与方法三实践总报告

日期：2026-10-18。用途：交给另一个 AI 审查。本文件是执行记录，不是论文段落，不新算几何，不授权改 `main.tex` 或 `src/`。

审查时以本文件点名的 CSV 和 JSON 为准。叙述与这些文件不一致时，以文件为准。

## 审查范围

本轮只做了两件离线测量。

| 大纲条目 | 问题 | 实践范围 | 结局 |
| --- | --- | --- | --- |
| 方法三：固定窗口下的跨窗口联合聚合 | 相邻窗口里尚未消费、年龄合格的更新，并入当前关闭后，可调质量是否提高 | 只做了 P0 几何闸门。三臂训练没有做 | NSW-Traffic、SensorScope、U-Air 为 fail。City Scanner 两块和 T-Drive 为 blocked。没有训练 |
| 方法一：可达性检测 | 单窗对不齐目标，质量落在缺席组、被约束钉住的组，还是落在参考向量相对冻结目标的位移 | 第 1 步到第 5 步都写完。只分解到达窗集合，不构造保留池 | 三个正式块几何为 complete。估计列为 blocked。同上三块应用块为 blocked |

没有做的条目：方法二（目标驱动停止，OF-v1 维持停止）、方法四（主动探测）、方法五（何时更强校准值得其代价）、已另行授权的 City Scanner 完整 P2 对简单投影、2026-10-12 停在方法身份冲突的检测器协议 `results_reachability_detector_v1/`。

两轮都没有创建 `runs/`，没有修改 `src/` 或 `TO_OVERLEAF_paper_tmc_r1_clean/`。

## 两边共用的对象

正式轨迹：

- `artifacts/e3_formal_runs_r1/eventtraces/traffic`
- `artifacts/e3_formal_runs_r1/eventtraces/sensorscope`
- `artifacts/e3_formal_runs_r1/eventtraces/uair`

每块种子 `seed30001`–`seed30020`，共 20 个。目录里本来就有 `seed30005`。没有另加种子。

冻结目标：

| 块 | 文件 | 抄本计数 |
| --- | --- | --- |
| NSW-Traffic | `configs/frozen/e3_multidataset_protocol_closure/traffic/public_target.json` | 4 键 `"0"`–`"3"`，各 0.25，`sum=1` |
| SensorScope | `artifacts/e3_semantic_alignment_and_runner_integration_closure_r1/E3_SENSORSCOPE_TARGET_SEMANTICS_R2.json` | 220 键，`sum=0.9999999999999997`，全部为正 |
| U-Air | `artifacts/e3_semantic_alignment_and_runner_integration_closure_r1/E3_UAIR_TARGET_SEMANTICS_R2.json` | 144 键，`sum=1.0000000000000002`，全部为正 |

可行集：\(\alpha_{\max}=0.5\)，\(E_{\min}=3\)，来自 `artifacts/e4_wo_inst_reference_penalty_final_correction_r1/E4_WO_INST_FINAL_ONE_FACTOR_SPEC.json` 的 `required_identities.alpha_bounds` 与 `required_identities.ESS_constraints`。窗口界是 \(\overline\alpha_r=\min\{1,\max\{0.5,1/K\}\}\)，\(\overline E_r=\min\{3,K\}\)。可调阈值 0.01。\(K\le 3\) 时可行集只有均匀权重，可调质量为 0。

组标签规则在 `results_xw_pool/round_v1/p0_geometry.py` 的 `group_from_features`。方法一的脚本抄了同一规则。到达窗集合是 `U=1` 且 `window_id` 等于该关闭的尝试，每个客户端留 `downloaded_version` 最大的一条。

开发几何不在本轮：种子 41001–41003、45001，固定 \(K\in\{4,8,16\}\) 的子集，以及附录里的 cap 0.25、0.1875、0.50。正式 NSW 的可调质量是 0，不能与那张表里约 4.6% 的可调质量当成同一次测量。

## 方法三

### 协议与指令

- 方案：`ccfa-review-reports/raven-mcs-cross-window-pool-experiment-design.md`
- 预注册：`results_xw_pool/round_v1/P0_GATE_PREREG.md`
- 执行脚本：`results_xw_pool/round_v1/p0_geometry.py`
- 结果：`P0_GATE.json`、`P0_SUMMARY.csv`、`P0_WINDOWS.csv`、`P0_BLOCKED.md`、`P0_SMOKE.md`

预注册写在打开组成之前。通过要同时满足：配对可调质量差的 95% 区间整个在 0 以上，且点估计至少 0.005；每一块的 \(K\le 3\) 份额从到达窗集合 \(A\) 降到保留池 \(H\)。区间是种子级百分位，10000 次，随机种子 20261018。SensorScope 或 U-Air 若通过，整轮停止且不训练。本执行即使有块通过也不训练，因为当时只要求 P0。

保留规则写在方案里：关闭 \(r\) 上，已交付、尚未消费、\(r-\sigma\le S_{\max}=5\) 的尝试可以进入；每个客户端只留最大 \(\sigma\)；进入该关闭求和的尝试视为消费。\(S_{\max}\) 没有重选。

### 闸门结果

| 块 | 种子 | \(\mathrm{adj}(A)\) | \(\mathrm{adj}(H)\) | \(\Delta\) | 区间 | \(K\le 3\) 份额 \(A\) 与 \(H\) | 新客户端 | 更换组成行 | 状态 |
| --- | ---: | ---: | ---: | ---: | --- | --- | ---: | ---: | --- |
| NSW-Traffic | 20 | 0 | 0 | 0 | [0, 0] | 0.1477506699649557 | 0 | 0 | fail |
| SensorScope | 20 | 0.004826495233338324 | 同左 | 0 | [0, 0] | 0.7855329299449888 | 0 | 0 | fail |
| U-Air | 20 | 0.006223665992967439 | 同左 | 0 | [0, 0] | 0.7897209615031388 | 0 | 0 | fail |

上表的份额是各种子份额的平均，不是窗口池化比例。方法一的窗口计数是 NSW 294/1990、SensorScope 1475/1877、U-Air 1197/1515。池化比例与上表差在第四位以后。审查时不要把这两种算法当成互相矛盾。

`P0_WINDOWS.csv` 有 5382 个数据行。方法一第 4 步按 `block,seed,window` 连接后，两边键集合相同。

冒烟只检查了 NSW-Traffic 种子 30001 的折叠、双重消费和年龄。`P0_SMOKE.md` 写明这不是结果。

City Scanner 访问占用、Pilot 2、T-Drive 在 `P0_BLOCKED.md`。状态是 blocked，不是 fail，也不是 pass。脚本把这三块的原因写死，没有打开它们的轨迹来补 \(\mu\)。均匀 0.25 没有被假定。T-Drive 微型夹具没有被使用。

`P0_GATE.json` 的 `_stop.training` 是 `not started`。`negative_control_passed` 是 false：SensorScope 和 U-Air 失败，符合预注册里的负对照预期，所以没有因为“意外通过”而停整轮。NSW-Traffic 也失败。没有任何一块 pass。

### 零差的记录原因

`P0_GATE.json` 的 `why_delta_is_zero` 写的是：一条尝试在到达关闭上已经满足年龄界，写成的规则就在那个关闭把它消费掉。后面的关闭看不到它。三个块上保留池 \(H_r\) 与到达窗集合 \(A_r\) 在每个有记录的窗口相同，新客户端和更换组成行都是 0，配对区间是 [0, 0]。看到这个零之后没有改规则。

因此这次 P0 测量的是这条“到达即可消费”的规则。它没有测量另一条把更新留过到达窗的规则。

NSW 的逐窗可调质量本身是 0。方法一在全部 1990 个窗口上看到每个窗口只有一个组。四个 UTC 块的目标里有三个缺席，出现的那一块可行区间宽度为 0。这与“保留池没有带来新客户端”是两件分开的事。

## 方法一

### 协议与指令

- 方案：`ccfa-review-reports/raven-mcs-reachability-attribution-experiment-design.md`
- 第 1 步指令：`results_m1_attribution/round_v1/M1_STEP1_INSTRUCTION.md`
- 第 1 步产物：`M1_PREREG.md`、`M1_MU.json`、`m1_copy_mu.py`
- 第 2–5 步指令：`results_m1_attribution/round_v1/M1_STEPS_2_TO_5_INSTRUCTION.md`
- 执行：`m1_run.py`、`m1_distance.py`、`m1_solver_check.py`
- 执行自述：`M1_FIVE_STEP_REPORT.md`
- 结果：`M1_SMOKE.md`、`M1_WINDOWS.csv`、`M1_SUMMARY.csv`、`M1_ESTIMATE.csv`、`M1_STATUS.json`

第 1 步在打开 EventTrace 组成之前完成。E4 的两个字段与 0.5 和 3.0 一致，所以没有停步。归一规则是 `sum>0` 时用 `值/sum`。三个正式块都满足。抄本本身没有预先除以总和。

求解器是执行前已经安装的 Clarabel 0.11.1。本轮没有新装包。`m1_solver_check.py` 用组列表 `["0","0","1"]` 和四个 0.25 做了玩具自检，不是正式窗口。

### 第 2 步到第 5 步

冒烟只读 traffic 种子 30001，第一个 \(K\ge 1\) 的关闭是窗口 0。`M1_SMOKE.md` 不写该窗的质量或距离。该窗的数字在 `M1_WINDOWS.csv`：\(K=23\)，组数 1，缺失 0.75，钉死 0.25，可调 0，四段距离都在 1.5 附近。

冒烟文件把“\(K\le 3\) 则可调质量为 0”列进了窗口 0 的成立项。窗口 0 的 \(K\) 是 23，这条在冒烟窗口上没有被用到。它的实际检查在第 3 步：\(K\le 3\) 的 2966 个窗口可调质量都是 0。

第 3 步写出 5382 行：NSW-Traffic 1990，SensorScope 1877，U-Air 1515。\(K=0\) 的关闭没有写行。`row_type` 全部是 `onehot`。`off_target_clients` 全部是 0。作废窗口数是 0。

从 `M1_WINDOWS.csv` 重算的最大偏差：

| 检查 | 容差 | 5382 行上的最大值 |
| --- | --- | --- |
| 三项质量之和相对正 \(\mu\) | \(10^{-8}\) | \(3.3306690738754696\times 10^{-16}\) |
| 独热：\(d_{\mathrm{simplex}}-2\mu_{\mathrm{miss}}\) | \(10^{-6}\) | \(3.9968028886505635\times 10^{-15}\) |
| 单调性被违反的量 | \(10^{-6}\) | \(1.0317968701656355\times 10^{-11}\) |
| 三个增量的绝对值 | 无单独通过线 | 同上 |
| \(K\le 3\) 时 \(\mu_{\mathrm{adj}}\) | 必须为 0 | 0 |

第 4 步与 `P0_WINDOWS.csv` 的 `adj_A` 对齐。5382 个键两边相同，最大绝对差是 \(6.938893903907228\times 10^{-18}\)，与 `M1_STATUS.json` 的 `align_max_abs` 相同。通过之后才写 `M1_SUMMARY.csv`。主行只有块 \(\times\) 层，六行的 `n_seeds` 都是 20。没有全窗均值行。种子等权：先在种子内对窗口取均值，再对种子取均值。

描述性区间用 `numpy.random.default_rng(20261019)`，10000 次，顺序是块 NSW-Traffic、SensorScope、U-Air，每块先 `K<=3` 再 `K>3`，每层按 `mu_miss`、`mu_pin`、`mu_adj`、`d_simplex`、`d_cap`、`d_ess`、`d_C`。这不是通过线。换抽样顺序，端点会变。Traffic 各种子的层内均值相同，质量区间退化为点。

第 5 步没有找到与窗口客户端行对齐的组向量。`M1_ESTIMATE.csv` 只有表头 `block,seed,window,delta_ref,delta_dec`。估计列是 blocked。Traffic 种子 30001 的 `oracle_p` 与 `oracle_q` 是标量，第一格被看过，没有进入 \(\delta_{\mathrm{ref}}\) 或 \(\delta_{\mathrm{dec}}\)。`e2_reuse_provenance.json` 的 `source` 指向另一条轨迹目录，脚本没有打开它。没有拟合 \(q\)，没有读 \(q^{\mathrm{use}}\)。

### 六行主表

点估计来自 `M1_SUMMARY.csv`。四段 \(\ell_1\) 距离在表里相同到求解残差，所以距离只放 \(d_{\mathrm{simplex}}\)。缺失、钉死、可调是目标质量份额。

| 块 | 层 | 窗口 | 缺失 | 钉死 | 可调 | 距离 | 组数 |
| --- | --- | ---: | ---: | ---: | ---: | ---: | ---: |
| NSW-Traffic | \(K\le 3\) | 294 | 0.75 | 0.25 | 0 | 1.5 | 1 |
| NSW-Traffic | \(K>3\) | 1696 | 0.75 | 0.25 | 0 | 1.5 | 1 |
| SensorScope | \(K\le 3\) | 1475 | 0.9891584060276133 | 0.010841593972387837 | 0 | 1.978316812055228 | 2.101390738348231 |
| SensorScope | \(K>3\) | 402 | 0.9774759675556238 | 0 | 0.022524032444377305 | 1.9549519351112488 | 4.365293424132939 |
| U-Air | \(K\le 3\) | 1197 | 0.9855073643767707 | 0.014492635623227676 | 0 | 1.971014728753542 | 2.1191046279416605 |
| U-Air | \(K>3\) | 318 | 0.9702387128882476 | 0 | 0.02976128711175053 | 1.9404774257764958 | 4.368911768056504 |

层内窗口极值，来自 `M1_WINDOWS.csv`，不是种子均值：

- NSW 的 1990 行都是组数 1、缺失 0.75、钉死 0.25、可调 0。
- SensorScope \(K\le 3\)：组数 1–3，钉死落在 [0.003519061583577714, 0.015835777126099713]，可调为 0。\(K>3\)：组数 4–7，钉死为 0，可调落在 [0.017008797653958952, 0.036950146627565995]。
- U-Air \(K\le 3\)：组数 1–3，钉死落在 [0.0062893081761006275, 0.023060796645702302]，可调为 0。\(K>3\)：组数 4–7，钉死为 0，可调落在 [0.02515723270440251, 0.04874213836477986]。

若干描述性区间端点：SensorScope \(K\le 3\) 缺失 [0.9889653534323972, 0.9893469335602714]；SensorScope \(K>3\) 可调 [0.022196304789500493, 0.022828952966498346]；U-Air \(K\le 3\) 缺失 [0.985181322904435, 0.985817619941481]；U-Air \(K>3\) 可调 [0.029383829372418353, 0.03019555950209604]。其余端点在 `M1_SUMMARY.csv`。

### 质量名称和距离各回答什么

三项质量按预注册互斥：缺席组、出现但区间宽度 \(<0.01\) 的组、宽度 \(\ge 0.01\) 的组。\(W_g\) 用的是 cap 与 ESS 同时生效的闭式，与方法三的 `adjustable` 相同。\(K\le 3\) 不调用这个闭式，直接把出现组的正质量记入钉死。

四段距离才把单纯形、cap、ESS 拆开。5382 行上，四段距离都等于缺席质量的两倍，cap 与 ESS 的增量不超过 \(1.03\times 10^{-11}\)。

NSW 上，钉死的 0.25 是窗口里唯一那个 UTC 块的目标质量。该组的可行质量只能是 1，区间宽度是 0。单纯形上同样不能把质量移出这个唯一的组。cap 和 ESS 没有在这段 \(\ell_1\) 距离上再加一截。

站点 \(K>3\) 上，钉死为 0。已经出现的组都达到 0.01 的宽度，可调质量就是这些组的目标质量，种子均值约 0.0225 和 0.0298。缺席组仍约占 0.97。距离仍等于缺席质量的两倍。

## 两套结果怎样放在一起

两边用的是同一批正式轨迹、同一冻结 \(\mu\)、同一可行集和同一到达窗集合。方法一的 \(\mu_{\mathrm{adj}}\) 与方法三的 `adj_A` 对齐到 \(10^{-18}\) 量级，可调质量的定义没有在两轮之间换掉。

方法三问的是保留池是否比到达窗更大。在写成的消费规则下，三个块的答案是池与到达窗相同，可调质量差为 0，闸门 fail。

方法一问的是到达窗内部的差距从哪来。三个块的 \(\ell_1\) 距离等于缺席质量的两倍。cap 和 ESS 没有再抬高这段距离。参考向量的位移没有测到。

方法一没有把更新留到下一窗，所以它不能推翻或补做方法三的闸门。方法三没有拆缺失质量和钉死质量，所以它的 fail 不能单独写成“差距来自 cap”。两套结果放在一起，只覆盖已经到达并在到达窗消费的客户端。

## 记录支持的结论

- 方法三 P0：NSW-Traffic、SensorScope、U-Air 未通过预注册的两条通过线。差是恒等零，不是区间擦到零。
- 方法三：City Scanner 两块和 T-Drive 是字段或冻结 \(\mu\) 缺失，不是几何失败。
- 方法三：W-Proj、B-Proj、B-P2 没有训练。
- 方法一：三个正式块的质量分解和四段距离满足预注册恒等式，与方法三的到达窗可调质量一致。
- 方法一：估计位移没有数值。几何 complete 不填上这个空列。
- 两边都没有把距离写成 RMSE、最差组误差或组失配的下界。

## 记录不支持的结论

- 不支持改消费规则后再把本轮的 0 当成新规则的结果。
- 不支持用开发几何的可调质量替换正式 NSW 的 0。
- 不支持把 `oracle_p`、`oracle_q` 或旧的 \(q^{\mathrm{use}}\) 补成 \(\widehat r\)。
- 不支持把 City Scanner 或 T-Drive 写成与上面六行同类的分解。
- 不支持启动方法三的训练、方法一的决策实验、OF-v1，或把本轮数字写入论文。
- 不支持用本轮结果估计审稿分数会怎样变化。

## 建议的核查顺序

1. 读 `M1_MU.json` 的四个计数和 Traffic 键 `"0"`–`"3"`，对照 `M1_PREREG.md`。
2. 用 `M1_WINDOWS.csv` 重算质量缺口、独热缺口、单调性缺口，以及 \(K\le 3\) 的 `mu_adj`。容差见上表。
3. 用 `P0_WINDOWS.csv` 按 `block,seed,window` 连接三个正式块。键集合应相同。`mu_adj` 与 `adj_A` 的最大绝对差应不超过 \(10^{-8}\)。再确认 `K_A=K_H`、`n_new=0`、`n_changed=0`、`adj_A=adj_H`。
4. 确认 `M1_SUMMARY.csv` 只有六行主行，且是种子等权。区间只在上文的 `default_rng(20261019)` 顺序下逐位比较。
5. 确认 `M1_ESTIMATE.csv` 只有表头。`M1_STATUS.json` 里三个正式块的 `geometry` 是 complete、`estimate` 是 blocked。三块应用块是 blocked。
6. 确认 `P0_GATE.json` 里三个正式块是 fail、三块应用块是 blocked、`training` 是 `not started`。确认两个结果目录都没有 `runs/`。
7. 若重解距离，用已安装的 Clarabel，保持 \(\alpha_{\max}\)、\(E_{\min}\) 和 0.01。恒等式失败时按协议停止，不要改容差后再报通过。

## 文件索引

方法三：`ccfa-review-reports/raven-mcs-cross-window-pool-experiment-design.md`，`results_xw_pool/round_v1/` 下的 `P0_GATE_PREREG.md`、`p0_geometry.py`、`P0_GATE.json`、`P0_SUMMARY.csv`、`P0_WINDOWS.csv`、`P0_BLOCKED.md`、`P0_SMOKE.md`。

方法一：`ccfa-review-reports/raven-mcs-reachability-attribution-experiment-design.md`，`results_m1_attribution/round_v1/` 下的 `M1_STEP1_INSTRUCTION.md`、`M1_STEPS_2_TO_5_INSTRUCTION.md`、`M1_PREREG.md`、`M1_MU.json`、`M1_FIVE_STEP_REPORT.md`、`M1_SMOKE.md`、`M1_WINDOWS.csv`、`M1_SUMMARY.csv`、`M1_ESTIMATE.csv`、`M1_STATUS.json`、`m1_run.py`、`m1_distance.py`。
