# CODE_DIFF

本轮没有修改 `src`。新增文件都在 `results_zero_safe_buffer/round_v1/`。

工作区里原有的 src 差异不是本轮写入的：

```
src/raven_mcs/aggregation/feasibility.py   |  21 +-
 src/raven_mcs/aggregation/method_policy.py | 164 ++++++---
 src/raven_mcs/aggregation/methods.py       |   8 +
 src/raven_mcs/aggregation/p2_cvxpy.py      |   9 +
 src/raven_mcs/correction/design_ratio.py   |   4 +-
 src/raven_mcs/correction/pi_target.py      | 125 +++++--
 src/raven_mcs/data/window_dataset.py       |  41 ++-
 src/raven_mcs/experiments/e1_entry.py      |  12 +
 src/raven_mcs/experiments/sag_runtime.py   |  50 ++-
 src/raven_mcs/sag/__init__.py              |   2 +
 src/raven_mcs/sag/certificates.py          | 517 ++++++++++++++++++++++++++--
 src/raven_mcs/sag/counterfactual_audit.py  | 305 +++++++++++++++--
 src/raven_mcs/training/window_runner.py    | 527 ++++++++++++++++++++++++-----
 src/raven_mcs/utils/config.py              |  16 +
 src/raven_mcs/utils/manifest.py            |  43 ++-
 src/raven_mcs/utils/validation.py          |  17 +-
 16 files changed, 1612 insertions(+), 249 deletions(-)
```
