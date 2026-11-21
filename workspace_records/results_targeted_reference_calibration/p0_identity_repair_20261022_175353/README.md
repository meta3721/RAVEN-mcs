# 身份修复 P0

目录：`p0_identity_repair_20261022_175353`。状态 `BLOCKED_METADATA`，P1 `NOT_RUN`。

旧失败目录 `p0_p1_20261022_161223` 只读。本目录没有覆盖它，也没有把冲突站点删掉后继续做面板。

## 命令

Python 使用旧目录里的虚拟环境。PowerShell 不使用 `&&`。

~~~powershell
$env:OMP_NUM_THREADS='1'
$env:MKL_NUM_THREADS='1'
$env:OPENBLAS_NUM_THREADS='1'
$env:NUMEXPR_NUM_THREADS='1'
$py = 'C:/Users/szr/Desktop/record/1/results_targeted_reference_calibration/p0_p1_20261022_161223/.venv/Scripts/python.exe'
$r = 'C:/Users/szr/Desktop/record/1/results_targeted_reference_calibration/p0_identity_repair_20261022_175353'
& $py -X utf8 "$r/extract_and_match_dfit.py"
& $py -X utf8 "$r/build_linkage.py"
~~~

日文件各下载一次，记录在 `download_log.json`。不要为了复现而反复下载。

## 应读的结果

- `IDENTITY_RULES.md`：事件键拟议规则和来源。
- `conflict_row_linkage.csv`：965 行冲突成员的联结。A/T 的 `pm25fm_exported` 为空。
- `conflict_key_status.csv`：381 个旧键的联结状态。
- `unresolved_reference_row.csv`：唯一不能联结的源行。
- `P0_DATA_AUDIT.md`：阻塞审计。
- `P0_status.json`：`BLOCKED_METADATA`。
- `NEXT_STAGE_REQUEST.md`：不进入 P1。
