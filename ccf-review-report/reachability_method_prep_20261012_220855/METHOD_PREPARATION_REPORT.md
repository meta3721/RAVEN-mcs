# 方法准备交付

状态：**WAITING_USER_REVIEW**。候选规格已形成，尚未实施；新实验 **RESULTS_NOT_REVALIDATED**。本轮仅准备方法，训练、合成回放、真实控制回放均0，旧取消实验未恢复。

## 可审查材料

1. [P0_LOCATION_ADDENDUM.md](C:/Cursor/raven.mcs/ccf-review-report/reachability_method_prep_20261012_220855/P0_LOCATION_ADDENDUM.md)：定位补正、检索范围、历史归属。
2. [LEGACY_V1_SOURCE_AND_FAILURE.md](C:/Cursor/raven.mcs/ccf-review-report/reachability_method_prep_20261012_220855/LEGACY_V1_SOURCE_AND_FAILURE.md)：实际v1计算链、信息接口及六策略失败证据。
3. [CANDIDATE_SPEC.md](C:/Cursor/raven.mcs/ccf-review-report/reachability_method_prep_20261012_220855/CANDIDATE_SPEC.md)：单一新候选的机制、规则、必要假设、接口、成本和最小验证。
4. [REVISED_PROTOCOL.md](C:/Cursor/raven.mcs/ccf-review-report/reachability_method_prep_20261012_220855/REVISED_PROTOCOL.md)：方法设计A、实施后B0身份验收、B1及P2–P7实验验收分开。

## 结论及依赖

已定位旧target_gain_stop/v1。此前P0在live目录未找到它，并不说明Desktop归档不存在；补正文档新增，原报告不覆盖。六策略保存分数复算一致，v1相对fixed_time_2的J仍恶化3.7144%。这是单步简化几何代理失败，不是RMSE失败，也不是所有多步方法无效的证明。

新候选采用条件消息束、多首次关闭计划、跨窗状态传播和完整P2释放质量预览，保留原评分系数与实验门槛。它有可编码规格，但没有运行证据。尚需证明公共目标/资源信息在使用前可用、完成动态q的选择事件定义及校准来源、分离真实注册训练与关窗消费、核验生产manifest/恢复路径，以及测量规划开销。

动态q依赖不阻断独立P2/消息状态模块实施或条件数学命题整理；缺少合法概率证据时不能运行完整训练链或继承完整RAVEN风险保证。阶段A完成并等待审查，不因尚未实施而再记录“候选没有通过真实16窗”的循环失败。

## 历史及缓存处置

| 资产 | 本轮操作 | 后续依赖处置 |
|---|---|---|
| Desktop旧源码、协议、STOP、所有结果 | 只读保留；25文件内容前后一致 | 永久归属target_gain_stop/v1；若重现须独立输出及重新批准，不运行写原OUT的入口 |
| 原P0的4个Markdown与8个结构化文件 | 原样保留；新增定位补正 | 当时定位状态保留，引用时同时引用补正，不改candidate_frozen或历史状态 |
| 原始数据、合法train/val/test划分、公共目录 | 可保留；本轮只检查v1依赖路径存在 | 重查μ公开时间及任务单位，不能用测试标签定策略 |
| 注册机会与物理服务随机原语 | 可在外生假设成立时复用 | 实际训练影响时长时按本策略重算服务，不能盲用旧完成表 |
| v1原始Q、warmup经验批次 | 保留作旧方法诊断 | 新校正组成/风险集预测需新版本生成；不得当成完整RAVEN摘要 |
| Design/p训练权重、校正质量 | 仅相同注册前快照/版本/输入且可证明依赖一致时可复用 | 动态注册或Design/估计器不同必须重算；名称相同不构成复用依据 |
| 旧U、tau、下载版本、q、消费与过期、beta/debt、P2权重 | 隔离为旧身份 | 新策略全部重新产生；固定基线也按新共同系统生成 |
| 旧模型、训练位移、预测及RMSE | 不改名、不当作新版对照 | 动态下载/消费改变后须重新训练与预测；原结果可作明确身份的历史学习诊断 |
| 已有Design/Gate专项证据 | 保留、按适用范围引用 | 不等于新动态身份通过；只补新增快照/计算路径，不重跑112条历史训练 |

可直接使用的对照证据：旧v1与其五个旧控制的共同代理比较；冻结且与新任务/单位/划分完全相同的简单预测器，在评价目录与权重相同后可直接重评分。当前未执行后者，所以列为待核验，不声称直接可比已确认。新A层基线、完整外部方法、新策略q/模型/预测必须新生成，现有中央学习结果仅作原身份参考。

## 本轮验证与预算

已有文件算术审计脚本CPU0.046875秒，最终交付检查CPU0.03125秒，合计实测0.078125秒。早期交互读取CPU未逐进程计量，不把它伪装成精确总耗时；为全部轻量读取/写入预留180秒记账，当前保守记账180.078125秒（0.050022设备小时），低于0.5小时上限。预留额是记账额度而非实测CPU。无依赖安装、求解、拟合、训练或控制回放；仅新建本轮审计工具及交付文档，生产方法源码未改动。

六策略各800评分点，保存分数/版本/唯一消费/权重核验通过；未重建Q或真实服务链，不宣称新的实现验收。保护清单37文件前后相同，最后完成交付检查见 [DELIVERY_CHECK.json](C:/Cursor/raven.mcs/results_reachability_method_prep_20261012_220855/DELIVERY_CHECK.json)。结构化状态与预算见 [PREPARATION_STATE.json](C:/Cursor/raven.mcs/results_reachability_method_prep_20261012_220855/PREPARATION_STATE.json)、[BUDGET.json](C:/Cursor/raven.mcs/results_reachability_method_prep_20261012_220855/BUDGET.json)、[HISTORY_PRESERVATION.json](C:/Cursor/raven.mcs/results_reachability_method_prep_20261012_220855/HISTORY_PRESERVATION.json)。交付文件夹仅含.md；工具与JSON在独立results目录。

## 待审决定

建议审查上述单一候选后，再决定是否批准B0代码实施及限定验证，或修订/终止。B0建议设备预算与50–82人时工作量均未获授权；也没有拟定任何自动恢复命令。当前保持WAITING_USER_REVIEW，不标IMPLEMENTATION_ALIGNED，不报告新RAVEN检测或预测收益。
