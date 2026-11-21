# EXECUTION_ENTRY

工作目录：`C:\Cursor\raven.mcs`。解释器：`C:\Cursor\raven.mcs\.venv_new\Scripts\python.exe`。

当前：15 条已经完成。运行状态 THREE_SEED_RUN_COMPLETE，科学状态 FAIL_PREDICTION_GUARD，成本状态 COST_EVIDENCE_INCOMPLETE。三张冻结表、15 行 `RUN_MANIFEST.csv`、首批 `RESTORE_CHECK.json` 和 `DECISION_REPORT.md` 都在 `training_run_v1/`。新增训练已经停止。下面各节保留命令当时的记录。

只查看队列、不训练：

```text
C:\Cursor\raven.mcs\.venv_new\Scripts\python.exe results_zero_safe_buffer\round_v1\backend_pilot\run_pilot.py --plan
```

这条命令最近一次已经运行。状态是 RUNTIME_READY_UNRUN。计划进程没有加载 torch、numpy、pandas 或 cvxpy，也没有调用 `train_step`。

未带授权标志的训练入口：

```text
C:\Cursor\raven.mcs\.venv_new\Scripts\python.exe results_zero_safe_buffer\round_v1\backend_pilot\run_pilot.py --execute first-batch
```

这条命令已经运行，打印 `TRAINING_NOT_AUTHORIZED` 后退出，没有进入事件循环。

获准后的首种子五臂命令如下。这条命令已经执行，五臂都完成，退出码 0：

```text
C:\Cursor\raven.mcs\.venv_new\Scripts\python.exe results_zero_safe_buffer\round_v1\backend_pilot\run_pilot.py --execute first-batch --authorize-training
```

从某个断点继续一条臂的命令如下。本次没有执行它：

```text
C:\Cursor\raven.mcs\.venv_new\Scripts\python.exe results_zero_safe_buffer\round_v1\backend_pilot\run_pilot.py --execute resume --checkpoint <checkpoint.pkl> --authorize-training
```

后续种子的入口已经按证据放行，不再因为 I、TwoStage、FedAvg 的 `restore_pass` 为假而拒绝。当时 33002 和 33003 的冻结表还没有生成，那次准备的空闲内存是 `1737154560` bytes。两张表后来已经写成，剩余十条也已经执行并退出码 0。历史阻塞见 `training_run_v1/REFERENCE_PREPARATION_REPORT.md`。命令是：

```text
C:\Cursor\raven.mcs\.venv_new\Scripts\python.exe results_zero_safe_buffer\round_v1\backend_pilot\run_pilot.py --execute remaining --authorize-training
```

默认参数和 `--plan` 都不会把授权标志打开。

非训练复查：

```text
C:\Cursor\raven.mcs\.venv_new\Scripts\python.exe results_zero_safe_buffer\round_v1\backend_pilot\runtime_check.py
```

这条命令已经再次运行。进入门时的空闲内存是 `4809961472` bytes（4.480 GiB），没有等待。seed 33001 的 1637 条 U=1 attempt 与 `replay_seed` 一致，最大绝对误差门限是 1e-6，结果 PASS。状态写成 RUNTIME_READY_UNRUN。上一次内存不足的结果留在 `RUNTIME_CHECK_RESOURCE_BLOCKED_1735626752.json`。
