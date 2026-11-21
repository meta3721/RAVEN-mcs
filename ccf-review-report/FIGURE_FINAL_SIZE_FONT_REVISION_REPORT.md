# 图内字体最终尺寸修订记录

日期：2026-11-06。使用 ccf-visual-composer，在现有矢量绘图源码上做局部修订；没有调用生成式图像工具、重设计图形、启动训练/推理/求解或改动实验数据。

## 交付与最终尺寸

已更新实际引用的9组 PDF/SVG/PNG 和3个绘图脚本，顺序编译 [正文PDF](../TO_OVERLEAF_paper_tmc_r1_clean/main.pdf) 与 [补充PDF](../TO_OVERLEAF_paper_tmc_r1_clean/supplemental.pdf)。两份均为 **14页**，含参考文献。

TeX正文、图注、表题、插入宽度及附录导航文件与本轮备份逐字节一致；保留此前语言润色和其他未提交改动。正式图仍使用原文件名，PNG仅作预览。

测量以导出PDF实际页面宽度和成稿中该PDF Form的变换矩阵为准，再在成稿图形区域提取普通标签验证。不是按代码fontsize或最小字符大小判定：

- 单栏图导出宽252.000 bp，成稿宽251.065 bp，缩放0.996290；9.1 pt导出普通字实测为 **9.066 pt**，9.6 pt轴标题约 **9.564 pt**，9.3 pt子图名约9.265 pt。
- 通栏图导出宽515.520 bp，成稿宽514.082 bp，缩放0.997210。学习曲线普通字实测 **9.075 pt**，轴/列标题约 **9.573 pt**。
- 图1使用1500坐标宽，坐标字号还须先乘内部scale，不能把代码26.5误当PDF字号。普通字由原约8.23提升到 **9.082 pt**；模块标题由约8.91提升到 **9.596 pt**。普通文字最小导出字号约9.108 pt，经实际插入后为9.082 pt。
- 数学上下标、指数保留原相对字号层级，不要求统一9 pt。旋转数学字形的包围框高度也不等于标称字号。逐图实际标签、位置、缩放和测量值保存在 `final_font_audit.json`。

## 逐图修改及同尺寸对照

下列对照均按相同的最终插入宽度生成：96dpi用于常规阅读尺度，180dpi用于细节；各自高宽比保留，没有将新旧图强行拉伸成同高。页码为最终成稿。

- **fig1_raven_problem_framework.pdf**（正文第3页）：普通文字及模块标题放大；扩展记录/R-O/参考质量/支持及约束文本框，微调相邻连线；将债务公式放到账本下方。当前/下一窗口反馈、全部文字和语义分组保留。图高仅增加约3.43导出pt。 普通标签约9.08 pt。[常规同宽对照](../tmp/figure_font_20261106/comparison_fig1_raven_problem_framework_96dpi.png)，[细节对照](../tmp/figure_font_20261106/comparison_fig1_raven_problem_framework_180dpi.png)。
- **fig_w1_design_gate.pdf**（正文第10页）：刻度、图例及全部数值标签放大；正负数值分别留两排标注，避免零线和柱顶；数据集标签向外对齐。图高由2.05增至2.30英寸，坐标范围完全保留。 普通标签约9.07 pt。[常规同宽对照](../tmp/figure_font_20261106/comparison_fig_w1_design_gate_96dpi.png)，[细节对照](../tmp/figure_font_20261106/comparison_fig_w1_design_gate_180dpi.png)。
- **fig_g3_tdrive_h_mass.pdf**（正文第10页）：放大轴名、刻度、图例、数值及子图名，保留原双面板、柱、阈值和全部标注。 普通标签约9.07 pt。[常规同宽对照](../tmp/figure_font_20261106/comparison_fig_g3_tdrive_h_mass_96dpi.png)，[细节对照](../tmp/figure_font_20261106/comparison_fig_g3_tdrive_h_mass_180dpi.png)。
- **fig2_e2_risk_noninterchangeability.pdf**（正文第11页）：放大方法名、刻度和方向计数；同一科学计数倍率移至左面板上方，与横轴名分开，保留全部种子计数。 普通标签约9.07 pt。[常规同宽对照](../tmp/figure_font_20261106/comparison_fig2_e2_risk_noninterchangeability_96dpi.png)，[细节对照](../tmp/figure_font_20261106/comparison_fig2_e2_risk_noninterchangeability_180dpi.png)。
- **fig_arrival_support_geometry.pdf**（正文第12页）：放大六行标签、数值、图例及轴名；加宽左侧标签留白，保留所有区间比例与外部引线数值。 普通标签约9.07 pt。[常规同宽对照](../tmp/figure_font_20261106/comparison_fig_arrival_support_geometry_96dpi.png)，[细节对照](../tmp/figure_font_20261106/comparison_fig_arrival_support_geometry_180dpi.png)。
- **fig3_e3_structural_mismatch.pdf**（补充第6页）：放大方法名、刻度和子图名；四面板的均值、SD区间及局部坐标范围不变。 普通标签约9.07 pt。[常规同宽对照](../tmp/figure_font_20261106/comparison_fig3_e3_structural_mismatch_96dpi.png)，[细节对照](../tmp/figure_font_20261106/comparison_fig3_e3_structural_mismatch_180dpi.png)。
- **fig4_e3_prediction_risk.pdf**（补充第7页）：同结构区间图的稳定字号层级，保留四个指标面板及完整误差线。 普通标签约9.07 pt。[常规同宽对照](../tmp/figure_font_20261106/comparison_fig4_e3_prediction_risk_96dpi.png)，[细节对照](../tmp/figure_font_20261106/comparison_fig4_e3_prediction_risk_180dpi.png)。
- **fig_certificate_audit.pdf**（补充第13页）：放大坐标、图例、状态说明和子图名；上图图例移到绘图区上方，下图共享图例与子图说明保持分离。y=x、阈值、WARMUP/RESET及误覆盖点不变。 普通标签约9.07 pt。[常规同宽对照](../tmp/figure_font_20261106/comparison_fig_certificate_audit_96dpi.png)，[细节对照](../tmp/figure_font_20261106/comparison_fig_certificate_audit_180dpi.png)。
- **fig_learning_capacity_r2.pdf**（补充第14页）：放大单位、刻度、行/列标题、图例及面板编号；微调右侧留白并将100/200末端刻度向外分开，所有刻度值及对数尺度保留。六面板、基线及三种子范围阴影不变。 普通标签约9.07 pt。[常规同宽对照](../tmp/figure_font_20261106/comparison_fig_learning_capacity_r2_96dpi.png)，[细节对照](../tmp/figure_font_20261106/comparison_fig_learning_capacity_r2_180dpi.png)。

## 核验

- 对8幅数据图重绘前后的绘图对象逐项比较：数据线、柱/区间、误差线、范围阴影、颜色、标记和坐标范围完全一致。各源CSV的大小与修改时间不变；到达支持图继续逐行匹配既有附录表。没有新的统计检验、重评分或结论。
- 图1新旧SVG文本序列和语义分组序列完全相同；只改变字号、框体尺寸、局部连接位置和留白。未把可行校准拆成新模块，未改变权重到聚合、组成到债务及两类跨窗口反馈的关系。
- 9幅PDF均为矢量，未含光栅图；SVG均有可编辑text、无整张位图嵌入。所有9幅图及两份论文字体均嵌入，Type 3为0。
- 最后一次构建按正文LaTeX→补充LaTeX→两份BibTeX→交替两轮执行，8次均成功，aux稳定。未定义引用/文献、重复label/destination、Overfull、缺字、字体警告和PDF字符串警告为0。仍有原有窄栏/数学的Underfull提示及禁用shell-escape提示，未将其写成零警告。
- 最终28页均渲染并逐页联系图查看，另查看9图独立预览、常规同宽对照及学习曲线最终第14页全页。未见标签裁切、文字越框、箭头穿字、重叠或图题/表题位置错误。图1仍在第三节、正文第3页。实际成稿的9个普通标签样本均与缩放计算值相符。
- 全部原label编号和35个正文附录目标核验通过，书签和精确链接目的地可解析。本轮为结构回归检查，没有另作阅读器跨文件实点测试。

## 源码、复现及回退

修改的源码：

- [fig1_framework_vector.py](../TO_OVERLEAF_paper_tmc_r1_clean/fig1_framework_vector.py)
- [data_figures_revision.py](../TO_OVERLEAF_paper_tmc_r1_clean/data_figures_revision.py)
- [arrival_support_figure.py](../TO_OVERLEAF_paper_tmc_r1_clean/arrival_support_figure.py)

候选及相应来源记录保留在 [figures/font_size_candidate](../TO_OVERLEAF_paper_tmc_r1_clean/figures/font_size_candidate/)，通过检查后才复制到正式figures。没有运行make_figures.py的整套main，也没有生成未引用的City Scanner候选或其他旧图。绘图库运行依赖本机Matplotlib 3.11.2、已有NumPy/Pandas及ReportLab；本轮补齐了当前运行时缺少的Matplotlib及其小型依赖。输入仍是脚本原先指定的CSV，没有换结果版本。

只重生成本轮图形的调用方式（从论文目录，使用已有Python环境）：

```powershell
python fig1_framework_vector.py --out figures/font_size_candidate
python data_figures_revision.py --out figures/font_size_candidate --only fig2_e2 fig_g3_tdrive fig_w1_design_gate fig3_structural fig4_prediction fig_certificate fig_learning_capacity
python arrival_support_figure.py --out figures/font_size_candidate
```

PDF/SVG始终输出；图1PNG预览需要给脚本传入可用的`--poppler`或让pdftoppm位于PATH。图1原有STIX字体素材及其许可沿用；未引入外部图标。

修改前已保存并逐条验证 [备份目录](../TO_OVERLEAF_paper_tmc_r1_clean/figures/_backup/figure_fonts_before_20261106_091202/)，含`before.zip`和`BACKUP_AND_RESTORE.md`。归档保留3个绘图脚本、9组原图、两份原论文PDF、TeX/aux及图1实际依赖字体。旧备份未覆盖或删除。

恢复时先解压到独立临时目录，仅还原3个脚本和9组图，再交替编译两份论文。TeX本轮没有修改，无需用旧源码覆盖当前稿；若后续脚本或图形已有改动，应依据本轮源码差异合并恢复。只查看旧版时直接打开备份PDF，不必修改规范源。

完整源码差异见 [FIGURE_FONT_SOURCE_DIFF.md](FIGURE_FONT_SOURCE_DIFF.md)。实际字号、数据对象比较、字体清单、标签身份、构建日志及28页渲染保存在 [本轮核验目录](../tmp/figure_font_20261106/)。未发现需要改变数据、科学含义或放宽14页约束才能解决的剩余字号冲突。
