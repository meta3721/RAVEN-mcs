# REFERENCE_PREPARATION_REPORT

日期：2026-10-19。当前状态：**REFERENCE_READY**。

## 当前

三张只读表都在 `training_run_v1/`：

| seed | 文件 | U=1 条数 | trace_hash |
| --- | --- | ---: | --- |
| 33001 | `frozen_reference_seed33001.json` | 1637 | `213a7f5a4512f36369434652dfd3fd220d681488f0490e003d7c051477d9cb57` |
| 33002 | `frozen_reference_seed33002.json` | 1661 | `3f7be3fa580dc9475073ae80643e9f0f98a02ff565cf1f25d37902a03add9e36` |
| 33003 | `frozen_reference_seed33003.json` | 1630 | `4cc2b1b9f34d2b9e0d44a6eca31c729034551b2d2cdcd154a92f0a8fd5979d5c` |

33002 和 33003 由 `reference_replay.replay_seed` 提供数值，并由驱动的 U=1 attempt 编号做一对一核对，最大绝对误差不超过 1e-6。seed 33001 的原文件没有被这次准备重写。机器记录在 `REFERENCE_PREPARATION.json`，状态 REFERENCE_READY。进入那次准备时的空闲内存是 6417756160 bytes（5.980 GiB），等待 0 秒。这个读数只属于该次准备，不是全部运行的最小空闲内存。

## 历史：第一次准备被内存拦住

当时状态是 RESOURCE_BLOCKED，33002 和 33003 还是 UNRUN。准备进程在加载参考之前检查内存。空闲内存在一次 30.016 秒等待之后是 1737154560 bytes（1.618 GiB）。2 GiB 门槛是 2147483648 bytes，2.5 GiB 启动门槛是 2684354560 bytes。等待后仍差 410329088 bytes 才到 2 GiB，差 947200000 bytes 才到 2.5 GiB。进程 RSS 是 16183296 bytes。那一次没有调用 `replay_seed`，也没有写出新表。

这次阻塞后来被解除。上面的当前表就是解除之后写出的。历史读数保留，不改成当时已经成功。
