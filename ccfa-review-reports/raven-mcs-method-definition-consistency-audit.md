# RAVEN-MCS 方法定义一致性修订记录

日期：2026-10-12。Owner：ccf-paper-writer；prose 修改前已读取 ccf-humanization、humanization-policy、experiment-discipline 和 prose-quality-guardrails。只处理方法身份、时序和归属，不全篇润色、不改代码、不启动实验。

## 结论分层

1. 论文核心配置定义已统一为窗口前配置 Design、窗口内固定、coverage Gate 仅诊断。没有把生产注释里的 formal 当成科学依据。
2. 固定配置下的既有重构、凸校准及稳定性论证可以保留；它们不证明 target-support 规则能在真实部署中提前执行，也不证明其选择最优。覆盖理论仍条件于稳定区域交换性。
3. 结果归属只能部分核实。固定臂与覆盖候选已在文字中分开，但完整历史源快照、部分表格重评分链及预配置时点仍有证据缺口。因此不报告“全部论文内部方法冲突已解决”，更不报告整个项目已同步。

## 输入及检查

已读用户列出的 main.pdf、main.tex、appendix.tex、supplemental.tex、method_policy.py、prepare_uniform.py、20261011 重建协议、EXECUTION_REPORT.md，以及桌面记录中的执行审计。额外只读追踪 window_runner.py、sag/r1l_design.py、compute_scd_phi.py、G1/C2/G3 历史记录及部分运行配置/结果。没有执行这些实验脚本。

初始 main.pdf 为 18 页，与源中的窗口前配置和“delivered units”规则一致；旧 main.log 记录的 17 页不能作为最新版 PDF 状态。

## 源文件改动

| 范围 | 处理 |
|---|---|
| 摘要、Introduction、Fig.1 图注 | 明确预配置机会 Design；删除零目标统计直接触发当前窗口开关的暗示；图中没有 Gate→Design 边，图文件保留 |
| 系统模型、机会校正、覆盖小节 | 明确窗口前记录、窗口内固定；Gate 与完成后 C_t 审计分开 |
| `alg:window_close` | REQUIRE 写明已经记录的配置，不加入新控制分支 |
| 理论导语、假设和结论 | 明确论证条件于配置，不把零目标规则当作正性证明；原定理、证明及结论公式保留 |
| 实验设置与 Design 消融 | 保留固定臂；消融从两块的 Design-on 开始；U-Air off 是报告臂，不是算法因数据集名字自动返回 off |
| `eq:design_gate` 周围 | 保留数学式；纠正 delivered 与完整训练目录的计数对象混淆，说明块索引及决策时点条件 |
| `eq:design_switch` 周围 | 保留原值与式子，归为端点事后权衡图，取消“两个在线步骤”的说法 |
| 部署条件、补充覆盖审计 | 区分默认配置方法与 Design_t=Gate_t 的覆盖候选证书记录 |
| 补充支持统计及表注 | 不再把离线统计无条件称为 pre-window，也不声称它产生了历史排名 |
| supplemental.tex | 更新算法说明注释；原计数器与输入结构保留 |

定义对象变更理由：正文说 n_r 是 delivered units，但 SensorScope/U-Air 的权威计数枚举完整 train split 的唯一 unit ID，且分母正好等于数据集 train 数。本轮按来源修正文字对象，没有改 rho 公式或将当前交付信息改写成已知未来信息。

## 结果与方法归属

| 证据块 | 已核对来源/行为 | 可支持内容与缺口 |
|---|---|---|
| 主比较 SensorScope/U-Air、Design 图与消融 | G1 DIAGNOSIS_REPORT 明确 Estimated=`raven`(E3)、Oracle=`raven_simoracle`、off=`raven_wo_design`(E4)；两块各20个配置和结果文件存在；G1 Path B 是按数据集选取已封存臂的后处理 | 支持固定臂对比；不是新 target-support 自动选择算法的前瞻确认。旧 window_metrics 未保存 g_r，不能用其不存在的字段确认开关历史 |
| 主表结构量 | 80个已有 final_metrics 的 Delta_group/Delta_c_s 均值重算，与四个 RAVEN 表项四位值相符 | 数值保留；没有重训 |
| 主表预测量 | SensorScope RMSE_mu 7.9380/7.9384、U-Air off 1.1131 对上上述原始文件；U-Air on 原始均值为1.1911，正文为1.1954；WorstGroup来自另一个四块重评分链 | 不改数值；本轮未闭合 U-Air on 1.1954 的重评分来源和历史脚本链。缺口不是 coverage-controlled 等价性的证据 |
| T-Drive、City Scanner rankings | 空间T-Drive和measured-O City Scanner runner 有显式跳过 coverage Gate 的固定因子路径；冻结统计/设置文件可读 | 与固定臂方向一致；这些 runner 不能代替全部 hybrid/NYC 历史运行源快照，逐版本完整追溯待补 |
| NSW-Traffic 主块、四区域、Adam确认 | 稿件说明各自目标、选择和配置不同 | 不转归新定义的新实验；本轮未重新执行全部15/20种子的源闭包，归属缺口保留 |
| INT-R、projection/weight replay、kappa=1000 probe | 文中固定设置与事后/探索性边界保留 | 不转成动态 coverage 切换收益；未重新核验全部历史源和本地训练缓存，保留为已有协议下的分析 |
| coverage stress 表/图 | FIG_CERTIFICATE_WINDOWS.csv 共575行，每行 Design_t=Gate_t；图只画 C、LCB、预测及状态 | 明确 coverage-controlled candidate 的证书诊断；不能据此说 configured-Design 训练获得同样有效性或预测收益 |
| 重建 P1 | prepare_uniform 继承生产 aggregate_coverage；执行报告与审计说未完成四臂、Uniform仅开发诊断 | 集中式学习门槛不受 Design 身份影响；Uniform 的损失/轨迹不可重新标成固定配置结果 |

表内所有数值原样保留。结果来源未闭合处只记在本独立审计中；正文不新增全流程确认、收益或自动选择有效性主张。

## 作者待决事项

1. target-support 的输入究竟是事先冻结的训练单位目录，还是在线已交付集合？本轮已按已有计数解释离线表。若采用在线集合，当前窗口开启前无法计算其最终 rho；需要另行方法设计，不能本次偷偷引入 lagged rho。
2. 若要把目录规则用于部署，需提供目录/映射/公共目标冻结时间和可得信息条件；读取完整离线原子表且不读取 Y，不能单独证明在线可得。空目录 n_r=0 原式未定义，须作者决定适用范围或行为。
3. 历史 G1 Path B 是基于数据集身份和已有支持诊断选取臂；是否要提出可迁移的 target-support 配置规则，及如何前瞻验证，是后续科学决定。本轮不把历史排名重写为该规则的实验结果。
4. 补全 U-Air on 1.1954 与各附加结果的重评分/源版本链。保留当前值，不能因不能确认就更换或虚构来源。

## 验证

- 修订前临时基线与修订后比对：三个文件的全部 equation/align 块、tabular 块、label 和 citation keys 不变；原交叉引用保留，新增少量已有标签引用。
- 使用项目已安装 MiKTeX pdflatex，main/supplemental 交替编译，主文18页，补充16页。最终无 undefined reference/citation、multiply-defined label 或需重跑标签警告。
- 主文无 overfull；补充材料既有图组附近有2.4194pt overfull vbox，已目视检查页面无重叠/裁切；underfull 提示保留，不扩大为排版重写。
- 已渲染查看总览图、配置规则、算法及补充审计页面。prose checker 无 em dash 超限/硬错误；分号密度和补充材料既有句长警告属于范围外风格提示。
- 没有执行训练、测试预测、调参、四臂确认、代码修改或提交。
- `raven-mcs-method-definition-consistency.patch` 仅包含本轮相对编辑前源文件的85行新增/56行删除（主文63/41、附录21/14、supplemental注释1/1）。项目已有大量未提交修改，未用整个Git差异冒充本轮修改。
