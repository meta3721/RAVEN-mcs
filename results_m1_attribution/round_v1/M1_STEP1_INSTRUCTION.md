# 方法一 P0 第一步指令

日期：2026-10-18。协议：`ccfa-review-reports/raven-mcs-reachability-attribution-experiment-design.md` 执行顺序第 1 步。本文件是给执行者的指令。它不包含窗口组成，也不包含 \(\mu_{\mathrm{miss}}\)、\(\mu_{\mathrm{pin}}\)、\(\mu_{\mathrm{adj}}\) 或任何距离。

```text
Mode: design
Venue and assumptions: IEEE TMC。本步只把已经发表的目标向量和可行集常数抄进预注册。分解、冒烟、与跨窗 P0 的逐窗核对、估计位移都不在本步。
No-fabrication status: 本步不产生测量结果。M1_MU.json 里的和与键数是冻结目标文件的抄录，不是实验结果。结果表保持 TBD。
Next CCFA owner: 执行者只交 M1_PREREG.md 与 M1_MU.json。用户未点名时不进入第 2 步，不交给 ccf-paper-writer。
```

## 本步只交两份文件

写到 `results_m1_attribution/round_v1/`：

1. `M1_MU.json`：三个正式块的原始 \(\mu\) 抄本和核验计数。
2. `M1_PREREG.md`：引用这份抄本，并写死后面各步不得改的定义。

完成这两份文件之后停止。第 2 步到第 5 步不因本步完成而获得授权。

## 允许读取的文件

只打开下面这些：

- `ccfa-review-reports/raven-mcs-reachability-attribution-experiment-design.md`
- 本指令
- `configs/frozen/e3_multidataset_protocol_closure/traffic/public_target.json`
- `artifacts/e3_semantic_alignment_and_runner_integration_closure_r1/E3_SENSORSCOPE_TARGET_SEMANTICS_R2.json`
- `artifacts/e3_semantic_alignment_and_runner_integration_closure_r1/E3_UAIR_TARGET_SEMANTICS_R2.json`
- `results_xw_pool/round_v1/P0_GATE_PREREG.md`，只为引用其中已经写明的 \(\alpha_{\max}\) 与 \(E_{\min}\) 出处
- `artifacts/e4_wo_inst_reference_penalty_final_correction_r1/E4_WO_INST_FINAL_ONE_FACTOR_SPEC.json`，只读 `required_identities.alpha_bounds` 与 `required_identities.ESS_constraints`

Python 使用 `.venv_new\Scripts\python.exe`。抄录脚本如果需要，只放在 `results_m1_attribution/round_v1/`。脚本不得导入 pyarrow，不得打开 parquet。

## 禁止

- 不打开 `artifacts/e3_formal_runs_r1/eventtraces/` 下的任何文件，包括 `events.parquet`。不列出其中的种子目录来“核对组是否出现”。
- 不读 `opportunity_features`。
- 不打开 `results_xw_pool/round_v1/P0_WINDOWS.csv` 和 `P0_SUMMARY.csv`。逐窗核对是第 4 步。
- 不把跨窗 P0 的可调质量、\(K\le 3\) 份额或区间写进 `M1_PREREG.md`。
- 不读 \(q^{\mathrm{use}}\)，不读开发轨迹的 `beta`，不盘点投影前参考向量 \(\widehat r\)。
- 不写 `M1_WINDOWS.csv`、`M1_SUMMARY.csv`、`M1_ESTIMATE.csv`、`M1_STATUS.json`，不写冒烟记录，不创建 `runs/`。
- 不修改 `src/`，不修改 `TO_OVERLEAF_paper_tmc_r1_clean/`，不写入 `results_reachability_detector_v1/` 或 `results_xw_pool/`。
- 不把 City Scanner 或 T-Drive 的轨迹打开来推翻下面已经写定的阻断。

后面步骤才会用到、本步不得打开的轨迹位置是：

`artifacts/e3_formal_runs_r1/eventtraces/{traffic,sensorscope,uair}/seed*/training_eventtrace/events.parquet`

## 抄 \(\mu\)

对三个 JSON，只取顶层对象的 `mu`。键转成字符串，值转成浮点数，按原样写入 `M1_MU.json`。不删键，不合并 head 与 tail，不在抄本里除以总和。

每个块记录：

- `source`：上面的路径
- `mu`：原始映射
- `n_keys`
- `sum`：原始值之和
- `n_positive`：值 \(>0\) 的键数
- `n_nonpositive`：值 \(\le 0\) 的键数

归一规则现在写死，供第 2 步以后使用，本步不另存一份归一化映射：`sum>0` 时，几何计算使用 `值/sum`。`sum<=0`、文件缺失、`mu` 不是对象或含非数字时，该块在预注册里记为 `blocked`，并写明原因。其余块继续抄。

Traffic 的抄本必须来自该 JSON 的 `mu`，不得手写四个 0.25。若键集合不是 `"0"`,`"1"`,`"2"`,`"3"`，停止本步，把实际键写进预注册，不重命名，不改用 `group_names`。

## 写死的常数

这些数来自已有预注册，本步不重新选择。若 E4 规格文件里的对应字段与下表不一致，停止本步，不另取一个数。

| 常数 | 值 | 出处 |
| --- | --- | --- |
| \(\alpha_{\max}\) | 0.5 | `E4_WO_INST_FINAL_ONE_FACTOR_SPEC.json` 的 `required_identities.alpha_bounds`；`P0_GATE_PREREG.md` 已引用 |
| \(E_{\min}\) | 3 | 同文件 `required_identities.ESS_constraints` |
| 可调阈值 | 0.01 | 协议正文，与开发几何所用阈值相同；开发几何的 cap 与种子不随之进入 |
| 质量恒等式容差 | \(10^{-8}\) | 协议 |
| 距离单调与独热恒等式容差 | \(10^{-6}\) | 协议 |
| 求解器可行性容差 | \(10^{-7}\) | 协议 |

窗口上的可行集保持

\[
\overline\alpha_r=\min\{1,\max\{0.5,1/K\}\},\qquad
\overline E_r=\min\{3,K\}.
\]

\(K\le 3\) 时可行集只有均匀权重，\(\mu_{\mathrm{adj}}\) 必须为 0。这个句子是定义，本步不拿窗口去验。

种子 41001–41003、固定 \(K\in\{4,8,16\}\) 的子集、附录几何表里的 cap 0.25、0.1875、0.50，以及种子 45001，不进入本方案。

描述性区间若在以后的步骤使用：种子级百分位，10000 次，随机种子 20261019。它不是通过线。本步不抽样。不使用 20261018、20261007、20261002。

## 预注册里要写上的定义

`M1_PREREG.md` 用文字写上下面的定义，使第 2 步不必再解释协议。定义不是测量。

客户端集合是该关闭日志里已交付并在该关闭消费的客户端，一人一行，同一客户端保留最大 \(\sigma\)。不构造保留池，不使用 \(S_{\max}\)。

正目标质量分成三项，互斥，和必须等于该窗正 \(\mu\) 之和：

- \(\mu_{\mathrm{miss}}\)：\(n_g=0\)
- \(\mu_{\mathrm{pin}}\)：\(n_g>0\) 且 \(W_g<0.01\)
- \(\mu_{\mathrm{adj}}\)：\(W_g\ge 0.01\)

\(\mu_g=0\) 的组不进入三项。落在这些组上的客户端以后记入 `off_target_clients`。

四个 \(\ell_1\) 距离在同一 \(M\) 上计算，\(\alpha\) 在单纯形上：\(d_{\mathrm{simplex}}\) 无 cap 无 ESS；\(d_{\mathrm{cap}}\) 只加 \(\alpha_k\le\overline\alpha_r\)；\(d_{\mathrm{ESS}}\) 只加 \(\sum_k\alpha_k^2\le 1/\overline E_r\)；\(d_{\mathcal C}\) 两条都加。三个增量都保留。独热组行上 \(d_{\mathrm{simplex}}=2\mu_{\mathrm{miss}}\)。混合组行标记 `row_type=mixed`，不套这条恒等式。

估计位移 \(\delta_{\mathrm{ref}}\)、\(\delta_{\mathrm{dec}}\) 本步不计算。预注册只写：没有与客户端行对齐的投影前 \(\widehat r\) 时，该列为 blocked，几何列仍可在以后完成。

主表以后按 \(K\le 3\) 与 \(K>3\) 分层。全窗均值不作为主行。

## 本步就写定的块状态

| 块 | 本步状态 | 原因 |
| --- | --- | --- |
| NSW-Traffic | 待抄 \(\mu\)；`sum>0` 则几何块留到以后 | 目标文件已指定 |
| SensorScope | 同上 | 同上 |
| U-Air | 同上 | 同上 |
| City Scanner 访问占用 | blocked | `opportunity_features` 没有组字段（没有 stratum、hour_block 或 target_group）。`s_max=5` 在 generation_meta 里。没有使用冻结 \(\mu\) 文件 |
| City Scanner Pilot 2 | blocked | 存在 `target_group_by_unit`，元数据里有 `s_max=5`，但没有 region0–3 的冻结 \(\mu\)。没有假定均匀 0.25 |
| T-Drive | blocked | `opportunity_features` 没有组字段。没有使用微型夹具。没有套用冻结 \(\mu\) 文件 |

这三句阻断从跨窗 P0 的记录原样保留。本步不追加搜索。

## 预注册的必写句子

`M1_PREREG.md` 开头写明：本文件在本协议的任何 EventTrace 组成被打开之前写成；其中没有客户端集合，没有窗口行，没有三项质量和四段距离。

文末写明本步没有打开的路径，并写上 `M1_MU.json` 里每个块的 `n_keys`、`sum`、`n_positive`、`n_nonpositive`。

## 本步完成的判定

同时满足才算完成：

- `M1_MU.json` 含 NSW-Traffic、SensorScope、U-Air 三个条目，或某个条目被明确标成 `blocked` 且带原因。
- `M1_PREREG.md` 含常数表、归一规则、三项定义、四段距离、分层、三块阻断句，以及抄本的四个计数。
- 目录里没有 `M1_WINDOWS.csv`、`M1_SUMMARY.csv`、`M1_ESTIMATE.csv`、`M1_STATUS.json`、`runs/`。

## 本步即停的条件

- E4 规格与 \(\alpha_{\max}=0.5\) 或 \(E_{\min}=3\) 不一致。
- Traffic 的 `mu` 读不出来。
- 为了确认组标签而需要打开 parquet。
- 需要修改 `src/` 或论文才能继续。

SensorScope 或 U-Air 的目标文件缺失时，只阻断该块，不改阈值，不换另一个 \(\mu\)。
