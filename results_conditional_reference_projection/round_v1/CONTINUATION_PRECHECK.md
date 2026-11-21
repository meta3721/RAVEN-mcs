# CONTINUATION_PRECHECK

用户消息“请执行之”授权 33002 与 33003，各五臂、各 100 窗。seed 33001 的预测结果保留，不重跑。

## 状态

S0 的 `training_authorized=false` 和 `conversation_scope=plan_only` 是当时的历史。首批实际由“完成S1，成功后进行五臂训练”以及“现在再试一下训练，内存应该够了”授权，并且已经训练完成。早期 743211008 与 1280335872 字节是那次暂停时的可用内存，不是本次入口的内存。

`training_authorized` 仍保持 false，避免把旧字段当成总开关。本次范围写在 `continuation_authorized`。分支 B 仍是 `NOT_REGISTERED_NO_DEPLOYMENT_CONTRACT`。

## 运行守卫

首批只在臂的前后看内存，不能当作完整运行的最小值，峰值记为 `UNMEASURED_FULL_RUN`。

本次在每个窗口前后检查预算、可用内存和 RSS，并用一个采样线程记录连续低于 2 GiB 的时间。连续 30 秒才停止。守卫测试已通过：29 秒不触发、满 30 秒触发、中途恢复后重新计时；预算崩溃进程只计入一次。测试没有训练模型。

导入 torch 之前仍要求大约 4 GiB 可用内存。单进程、单线程、低优先级。

## F 的数值清理

冻结可行性是 1e-8，不再把 -1e-6 当成同一条标准。只有不超过 1e-8 的负值可以清掉；清完以后的 simplex、负值、cap、ESS 都必须不超过 1e-8。更大的越界直接停止。

首批 F 只记录了两次约 -4.4e-11 的清理，没有每个窗口的残差。那一批的审计覆盖不足，不推断其余窗口都已检查，也不为补日志重跑。

## 源码

首批源码在 `implementation/snapshot_first_seed/`。新入口是 `implementation/run_remaining_seeds.py`。五条臂都克隆服务器参数。`src/` 没有修改。
