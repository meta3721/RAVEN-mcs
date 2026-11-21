# 预算、历史保留与原始证据

日期：2026-10-13；最终状态WAITING_USER_REVIEW。原始目录：`C:/Cursor/raven.mcs/results_revision_feasibility_20261013_125348/`。

## 本批计量

| 项目 | 秒 | 含义 |
|---|---:|---|
| 11次命令完整Job进程树CPU | 35.515625 | 包含求解器、规划子进程及退出 |
| 驱动/监视进程CPU | 1.640625 | 与Job成本不相交 |
| 已计量CPU合计 | 37.156250 | 上两项相加 |
| 交互、文件写入和计量尾部预留 | 30.000000 | 保守计费，不冒充逐进程实测 |
| 最终本批计费 | **67.156250** | 上限240；剩余172.843750 |
| 命令墙钟合计 | 43.821972 | 11次命令，含失败与重验；非整个会话时长 |

原逐次charge字段合计37.140625秒；一条驱动记录在稍后采样多出一个0.015625秒CPU计量刻度。本次以每行 `max(charged_CPU, job_CPU+driver_CPU)` 保守核账，最终采用37.15625秒。原记录不覆盖；预算脚本已改为一次采样写入对应字段。报告没有把Job、PID复核和内层控制器CPU重复相加。

原申请账1862.296875秒，加本批后为1929.453125秒；原5小时申请名义余额16070.546875秒。历史计量缺口仍为未知，不能把名义余额解释成已恢复准确历史账，更不能解释成继续执行授权。

训练=0，局部SGD=0，q拟合=0，GPU=0，新真实采集=0，随机合成回放=0。手写有限分支是已批准的机制检查；全支持预测器测试只调用固定小用例接口，不生成新控制轨迹。

## 保留与隔离

- 原v2源码闭包437项逐项一致；旧v2没有被重命名或替换。新包位于其闭包之外，单独记录方法和源码身份。
- 上一批保护清单中的101个文件校验一致，包括首条原轨迹/失败记录、历史报告及相应资料。S1规格及S2脚本与首次计算前记录一致。
- 原43001仅保留为旧策略开发资料。其q、模型、消费标签、动作轨迹和性能指标不归属新版；不能自动进入新q拟合/验证。
- 原数据、TRAIN划分、公共目录、与控制策略无关的元数据可以在身份核对后复用。本批只读了冻结μ与合法开发快照；没有重算模型。
- 新版未来轨迹必须重新生成所有依赖新消费策略的模型/预测、消费记录、动态q拟合标签及服务历史。不能直接读取旧v2模型缓存后声称新版结果。
- `S3_*FAIL*`、首次失败日志及旧检查点全部保留。新保存接口独占创建；旧检查点和代码已变化的新版检查点均不能被静默恢复。

## 证据位置

| 证据 | 原始文件 |
|---|---|
| 事前冻结 | `S1_FROZEN_INPUTS.json` |
| S2输入 | `S2_INPUT_SNAPSHOT.json` |
| 18个完整分支、状态闭合/消费/debt与区间 | `S2_late_unknown.json`、`S2_early_unknown.json`、`S2_RESULT.json` |
| R/E与身份最终检查 | `S3_RE_PASS_clock_final.json`、`S3_RE_clock_final.log` |
| 保存恢复 | `S3_new_identity_checkpoint_clock_final.json` |
| 未知与动作最终检查 | `S3_unknown_PASS_final.json`、`S3_unknown_final.log` |
| 全支持与实际P2最终检查 | `S3_supported_PASS_final.json`、`S3_supported_final.log` |
| 每决策CPU/逐PID及独立复核 | `S3_late_unknown_decision_final.json`、`S3_early_unknown_decision_final.json`、`S3_supported_decision_final.json` |
| 普通开发失败原证据 | `S3_RE_attempt1.log`、`S3_RE_FAIL_1.json` |
| 最终保留/语法/证据核验 | `FINAL_VERIFICATION.json`、`final_verification.log` |
| 最终预算 | `FINAL_BUDGET.json`及全部`charge_*.json`、`*.meter.json` |

最终核验只做本批语法、原始证据与保留检查，没有重复旧全套计量压力测试或全项目科学实验。没有修改论文，没有改写旧STOP_REPORT，没有恢复43002–43008、B1或正式确认。
