# 数据图局部重绘约定

本轮依据当前规范稿和封存CSV重新绘图，使用确定性脚本；图一、结果数据与统计结论保持不变。实验暂停。

备份：`TO_OVERLEAF_paper_tmc_r1_clean/figures/_backup/data_figures_before_revision_20261026_221941/`，已保存七图现有PDF/PNG、三个TeX、正文/补充PDF、make_figures.py、原学习曲线绘图脚本及figure_data。已验证副本字节一致，恢复规则随备份保存。

输出候选先写入 `figures/data_figures_revision_candidate/`；验收后再替换同名图片。新曲线输出PDF并改引用；City Scanner只提供候选，不与表II重复占用正文版面。

- 图2：原100行、五方法×种子30001—30020；保留风险差均值±样本SD和负差计数，不引入新检验。
- 图3：两个G3 CSV原值；阈值来自post_review/G3_mobility_replay/PROTOCOL.md的RQ1四时段TV>0.05规则，是失配诊断阈值。SS/UA为种子30001的既有协议风险集诊断，不是20种子性能均值。
- 图4：原四行Estimated/Oracle汇总、原比较方向及分母；采用统一3位小数和错位引线，保留全部近零值。
- 补充图5/6：严格沿用旧函数六方法、两数据集过滤及顺序；均值±样本SD，横向区间图，不换成表中不同支持集的行。RAVEN明确标为RAVEN-Design。
- 补充图7：原575窗中CERTIFIED子集和SensorScope a=.40原时间线；独立坐标标签/子图说明，保留误覆盖、阈值与状态。历史coverage-controlled候选仅作诊断审计，不改写当前Design身份。
- 补充图8：原3600行曲线，两个已选骨干×三数据集×三种子×200遍；保持log横轴、物理单位、均值/最小最大阴影及原验证基线算法。只读原曲线、选参汇总和基线CSV，不运行原finalize_execution.py。
- City Scanner：两CSV原五方法，32001—32010和33001—33010；组失配及两项预测均值±样本SD分别展示，独立标准化尺度，候选图不替代表II。

视觉：约3.5英寸单栏图，学习曲线7.16英寸通栏；低饱和稳定方法配色与不同标记；完整显示所有样本SD区间。坐标轴名与子图标题分开绘制。报告记录实际页面尺寸和未解决项，不用字号或模板调整凑页数。
