# 指令：写 City Scanner 驱动并生成共享 EventTrace（不训练）

把下面整段交给执行 AI。本轮 **只写 script + 生成 traces**。  
**禁止 `--stage train`。禁止改 \(\phi\)。禁止改 Table II。禁止提交。**

人已冻结：ingest + \(\phi=0\) + `GO.json`（Design ON，`scd_method=raven`）。  
T-Drive spatial C1 训练已停，本机可写 traces。

## 0. 给人口径：预计耗时

| 阶段 | 墙钟 | 说明 |
|---|---|---|
| 读合同 + 写生成器/驱动 | **45–90 min** | 复制 T-Drive 生成逻辑到**新文件**，加上 1666→100 窗口装箱 |
| seed 32001 canary（含方法名无关核对） | **1–3 min** | 约 3.6k 事件行；T-Drive 同机约 44 万行 / 5–10 min |
| 其余 9 个种子 | **5–15 min** | 顺序生成即可，不必并行 |
| **本指令合计** | **约 1.0–2.0 h**（多数是写代码） | 生成 traces 本身通常 **<20 min** |
| 不在本指令 | 训练矩阵 | 10 seed × 5 方法 × 100 窗；Hájek 在 T-Drive 上曾到数小时/种子。**本轮不要跑。** |

依据：T-Drive spatial traces 为 178 窗、每种子 441898 行，第一颗（双跑 canary）约 10 min，其后约 5 min/种子。City Scanner 装箱后约 **100 窗、每种子 ~3556 行**（约 T-Drive 的 1/124），生成应是分钟级。

---

```text
You are the City Scanner EventTrace executor for repo C:\Cursor\raven.mcs.
Read this entire file before editing.
Canonical manuscript: TO_OVERLEAF_paper_tmc_r1_clean/main.tex
Python: C:\Cursor\raven.mcs\.venv_new\Scripts\python.exe
Paper method: SCD via phi=0, NOT coverage Gate.
Do not train. Do not call --stage train / smoke / all.
Do not recompute or overwrite phi / GO.json / CS_PHI_DECISION.json.
Do not overwrite tdrive_protocol_seal_r1/.
Do not edit generate_tdrive_complete_aligned_eventtrace.
Do not call materialize_r3_trace or generate_complete_aligned_r3
  (those are protocol-R, not real City Scanner visits).
Do not reuse T-Drive / P2 / SensorScope / U-Air EventTraces.
Do not use vehicle / SensorID as FL clients.
Do not use build_pi_target_support_compatible.
Do not retune phi, p_obs, s_max, grid, slot, windows, or lambdas.
Do not change Table II / tab:tdrive_hybrid / tab:traffic_four_region.
Do not restore formal non-inferior.
Do not edit the manuscript.
Do not commit unless the human asks.
```

---

## 1. 写前核对（不通过则停）

1. `post_review/C1_kill_cityscanner/TARGET_SPEC.json`：`status=LOCKED`，`chosen_option=CS_NYC_PM25_CELL_500M`。
2. `results_c1_cityscanner/round_v1/INGEST_REPORT.json`：`status=INGEST_FROZEN`，`data_hash=22896ed585d50da8e55cc3bfe96b0e07eab790e7f9aaadb36c25e0a85c03d556`，`clients=spatial_id`，`phi_run=true`，`train_run=false`。
3. `results_c1_cityscanner/round_v1/GO.json` 必须已经存在，且与 `CS_PHI_DECISION.json` 一致：

```text
phi_train_unit = 0.0
n_train_units = 9343
n_train_zero = 0
design_on = true
scd_method = raven
train_full_design_extra = false
used_y_or_rmse = false
```

若 `GO` 缺失或与 DECISION 不一致：**停，问人。不要重跑 phi。**

4. Processed 可读：`data/processed/cityscanner_nyc_pm25/atomic_units.parquet` 与 `client_measurements.parquet`。  
   期望：atomic 14723 行；train unique `unit_id` = 9343；train unique `time_index` = **1666**；`client_id == spatial_id`；无 `NYCP*` client。
5. Python 为 `.venv_new\Scripts\python.exe`。
6. 本机没有 `results_c1_kill/` 正在训练的进程（用户已停 T-Drive C1）。

---

## 2. 冻结科学合同（生成 traces 用）

| 层 | 本轮锁定 | 禁止 |
|---|---|---|
| \(R\) | 真实到访：该格子在该 30 min 有保留样本 \(\iff\) 该 `unit_id` 存在且 `client_id=spatial_id` | `generate_complete_aligned_r3` 的协议抽样占用；OccupancySpec 模拟占用 |
| \(O\) | 受控 Bernoulli \(p_{\mathrm{obs}}=0.35\)（常数，不要按 block 乘 0.55） | 声称实测传感器日志 |
| \(U\) | `compute_usable_r3`，\(s_{\max}=5\) | 改 s_max |
| 窗口 | **恰好 100**（见 §3 装箱） | 改成 50 / 178 / 1666；看完 RMSE 再改 |
| 种子 | `32001–32010`；canary=`32001` | 复用 30001 / 31001 |
| RNG | `np.random.default_rng(seed + 13)`，与 T-Drive 生成器相同偏移 | 另起盐值 |
| \(h(i)\) | `target_group` = region0..3 | UTC H1–H4（T-Drive `fallback_h_id` 不要抄进本块） |
| \(s(i)\) | `opportunity_stratum` = `region::block::weekday` | 改 stratum |
| Client | `spatial_id` | 车辆 / SensorID |
| 方法名 | 生成器必须忽略 `method`；同一 seed 两条 trace 的 events 必须相等 | 按方法各写一条不同 hash 的 trace |

Hybrid 标签：真实 \(R\) + 受控 \(O/U\)。不是端到端 MCS。

---

## 3. 窗口装箱（必须按此式，禁止另发明）

Train 有 **1666** 个 unique `time_index`（0..1665）。TARGET_SPEC 预注册 **100** 窗。  
不要把 1666 个 30 min 槽各当一窗（那会违反 100 窗冻，也不是 RMSE 理由）。

无 \(Y\)、确定性：

```text
times = sorted unique train time_index          # length n=1666
rank[t] = 0 .. n-1
W = 100
window_id(t) = min(W-1, rank[t] * W // n)
```

核对：`window_id` 恰好覆盖 `0..99`。  
本机预计算（不要为对不上而改公式）：约 **3556** 个 client×window 事件行/种子；每窗平均约 36 个 client、93 个 unit。

每个 `(window_id, client_id)` 一行 EventTrace：

- `risk_set_unit_ids` = 该 client 在该窗内所有 train `unit_id`（该格子落在该箱的全部 30 min 槽）。
- \(R=1\) 当且仅当该 unit 在 processed 中存在。

不要丢掉箱外的 train 质量：1666 槽全部进入某窗。不要按 RMSE 改装箱。

---

## 4. 写哪些文件

**新建**（不要改 seal）：

1. `src/raven_mcs/data/cityscanner_eventtrace.py`  
   从 `src/raven_mcs/tdrive_protocol_seal_r1/eventtrace_generator.py` **抄结构**，但：
   - `dataset="cityscanner_nyc_pm25"`
   - `num_windows=100` via §3
   - `mean_observation_rate=0.35`，`s_max=5`
   - `del method`
   - `h` 用 `target_group`，禁止 `fallback_h_id`
   - `EventTraceMetadata.generator` 用新名字，例如 `cityscanner-real-r-complete-aligned-ou-v1`
   - `metadata.num_windows == 100`
   - 返回 `(trace, long_df, audit)`；`trace.validate()`
   - **不要 import / 改** `tdrive_protocol_seal_r1`

2. `scripts/run_c1_cityscanner.py`  
   模板：`scripts/run_c1_tdrive_spatial.py` 的 `stage_generate` + argparse。  
   本轮 **只实现** `--stage generate`。  
   `--stage train` / `smoke` / `all`：打印错误并 `return 2`（“this round is generate-only”）。  
   `--stage phi`：只 **读取** 已有 GO；若缺失则停；**禁止重算 phi**。

路径：

```text
SPEC     post_review/C1_kill_cityscanner/TARGET_SPEC.json
OUT      results_c1_cityscanner/round_v1/
TRACE    artifacts/e3_c1_cityscanner_eventtraces_v1/cityscanner_nyc_pm25/seed{SEED}/training_eventtrace/
PYTHON   C:\Cursor\raven.mcs\.venv_new\Scripts\python.exe
```

`_device()` 可写但本轮不调用。若写了，固定 `"cpu"`。不要改全局 `training/client.py`。

---

## 5. `stage_generate` 行为

1. `load_go()`：读 `GO.json` + `CS_PHI_DECISION.json`，核对 §1.3。不一致则停。
2. 读 atomic + measurements。断言 `client_id` 集合 == `spatial_id` 集合；无车辆前缀。
3. 对每个 seed in `32001–32010`（可用 `--seeds` 覆盖）：
   - 若 `training_eventtrace/trace_identity.json` 已存在且无 `--force`：REUSE，记录 hash。
   - `--force`：删该 seed 目录后重建。
   - **32001 canary：** 同一 seed 调生成器两次，`method="raven"` 与 `method="fedavg_window"`。`trace_a.events` 必须 equals `trace_b.events`。失败则停。然后 `freeze_event_trace(trace_a, out)`。
   - 其他种子：`method=None` 一次即可。
4. 每个 seed 写 `generation_meta.json`（可放 `out.parent`）。
5. 写 `results_c1_cityscanner/round_v1/CS_TRACE_MANIFEST.json`：

```text
experiment_id = C1-KILL-CITYSCANNER-NYC
r_layer = REAL_FROM_CITYSCANNER_VISITS
o_layer = CONTROLLED_EXPERIMENTAL p_obs=0.35
u_layer = CONTROLLED_EXPERIMENTAL compute_usable_r3 s_max=5
num_windows = 100
window_map = rank(time_index)*100//1666
hybrid = true
gate_unused = true
method_independent = true
rows = [{seed, status, trace_hash, n_windows, n_event_rows, n_clients, elapsed_sec}]
```

6. 更新 `INGEST_REPORT.json`：`eventtrace_run=true`，`train_run` 仍为 `false`。不要改 `data_hash` / `phi_*`。

CLI（本轮只跑这两条）：

```powershell
cd C:\Cursor\raven.mcs
.\.venv_new\Scripts\python.exe scripts\run_c1_cityscanner.py --stage generate --seeds 32001
.\.venv_new\Scripts\python.exe scripts\run_c1_cityscanner.py --stage generate
```

第一行必须先成功（canary + 方法名无关）。再铺满 10 种子。不要一上来 `--stage all`。

---

## 6. 成功条件

1. 10 个目录均有 `events.parquet` + `trace_identity.json`。
2. 每个 `metadata.num_windows == 100`。
3. 32001 方法名无关核对通过（记入 manifest / generation_meta）。
4. 不同 seed 的 `trace_hash` **不同**；同一 seed 不因方法名改变。
5. `client_id` 看起来像格子（如 `gXXXX_YYYY`），不是 `NYCP...`。
6. `GO.json` 字节级语义未变（`phi_train_unit` 仍为 0.0，`design_on` 仍为 true）。
7. 无 `NT_ACCEPTED.json` / `C1_ACCEPTED.json` / checkpoints / RMSE 文件出现在 `results_c1_cityscanner/`。
8. 报告：`post_review/C1_kill_cityscanner/EVENTTRACE_REPORT.md`（canary 耗时、10 种子墙钟、每种子行数、hashes）。

---

## 7. 明确不要做

- 训练；smoke；打开 Table II。
- 改 `scripts/compute_cityscanner_phi.py` 的输出。
- 改 `tdrive_protocol_seal_r1/` 或 `scripts/run_c1_tdrive_spatial.py`。
- 用 P2 的 `materialize_r3_trace` 图省事。
- 为“窗口太少/太多”或空窗去改 \(W\) 或网格。
- 提交 / push。

训练矩阵（以后另一份指令）：mandatory = `fedavg_window`, `twostage_hajek`, `fedau_window`, `obsuse_window`, `raven`。因为 \(\phi=0\)，不要再加 `raven_wo_design`，也不要再加一条 full-Design 诊断行。Kill bar 已冻，本轮不执行。
