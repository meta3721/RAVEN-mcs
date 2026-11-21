# 数据图重绘与论文集成报告

状态：七张现有数据图已修复并集成；City Scanner图已完成，作为独立候选交付。正文与补充材料均成功编译为 **14页**。本轮未训练、加载模型、推理、重评分、运行求解器或新增统计检验。

## 逐图结果与来源

1. **正文图2，第10页。** 原五方法及种子30001—30020保留；改为两幅横向柱图，方法直接横排。风险差为20种子均值±样本SD，负差计数从同一100行CSV算得 **18/20、18/20、17/20、17/20、17/20**。零参考线和10/20参考线保留；图注明确计数描述方向。来源：`figure_data/FIG_E1_E2_RISK_NONINTERCHANGEABILITY.csv`。

2. **正文图3，第10页。** 两幅零起点柱图保留，放大图例与刻度并精简子图标签。来源：`FIG_G3_TDRIVE_H_MASS.csv`、`FIG_G3_TDRIVE_TV.csv`。四块TV仍为0.141577、0.191855、0.278184。0.05线依据 `post_review/G3_mobility_replay/PROTOCOL.md` RQ1，是预设机会失配诊断阈值。SS/UA分别为Complete-aligned SensorScope/U-Air协议；G3汇总记载这两份协议风险集诊断使用种子30001，并非20种子性能均值。

3. **正文图4，第11页。** 沿用 `FIG_W1_DESIGN_GATE.csv` 四行数据，没有用表格均值重新计算或替换CSV百分比。Estimated/Oracle用固定错位标注行与引线，统一三位小数，保留−0.005、−0.013等近零值。实际文字包围盒核验：所有数字在轴框内且互不重叠。分母仍为No-Design，正值仍表示Design更差。该汇总CSV没有种子列；20种子说明沿用当前稿，未假称从四行汇总恢复了种子清单。

4. **补充图5，第7页。** 改为横向均值点±样本SD，六方法顺序不变，RAVEN明确显示为RAVEN-Design。来源为原 `FIG_E2_E3_STRUCTURAL_ALIGNMENT.csv` 的240行，两个数据集各六方法×20种子，30001—30020。所有区间完整显示；保留与其他表格活跃支持不同的身份说明。

5. **补充图6，第8页。** 同样改为均值点±样本SD。严格沿用旧函数对 `FIG_E3_E3_PREDICTION_RISK.csv` 的过滤：原440行中选原六方法、两数据集的240行，方法/种子顺序与图5一致。没有混入Central、Oracle或其他不同支持集行，也没有以表中相近数字替换。Tail与目标RMSE划分保留。

6. **补充图7，第11页。** 改为按真实单栏尺寸生成的上下两面板，分别保留 `C_t` / `C_t^{LCB}` 与 Window / Coverage；标题使用独立文字对象。保留575窗CSV中的原243个CERTIFIED窗口、10个实际误覆盖点，以及原SensorScope a=.40的62窗时间线；RESET触发窗为42，下一窗RESET。图例移到轴外，最终页面检查后再次修复其与子图说明的间距。数据仍归旧coverage-controlled候选的诊断审计，未将其重新标为配置式Design性能证据。CSV没有种子键，该层身份未知。

7. **补充图8，第13页。** 从 `results_main_rebuild_r1/P1_SELECTED_TRAIN_VALIDATION_CURVES_R2.csv` 的3600行重新绘制为通栏PDF，保留2×3、对数横轴1—200有效训练遍历、三种子均值与最小—最大阴影。列标题、训练/验证行标题、(a)—(f)与共享图例已补齐。物理单位保留vehicles/h、°C、μg/m³。选中配置由 `P1_CENTRAL_SELECTED_R2.csv` 核对，基线按原脚本从 `P0_VALIDATION_BASELINES_R2.csv` 为各种子选最强适用基线后求均值；未运行原 `finalize_execution.py`。原PNG保留于备份。

8. **City Scanner候选。** 从 `results_c1_cityscanner/round_v1/tables/CS_E3.csv`、`results_joint_ou/round_v1/tables/JO_E3.csv` 绘制两协议×三个端点：组失配、目标RMSE、最差组RMSE；保留各五方法、十种子及均值±样本SD。种子为32001—32010、33001—33010。预测使用协议各自的标准化尺度，未跨协议合并。核对组失配均值比降幅为25.7949%和23.3291%，图中未另加百分比标注。**未集成正文**：表II完整保留，新增同端点图会明显重复。推荐作为VII-B表II配套的独立讲解/审阅图；日后若调整正文证据载体，再另行确定是否替换，不能直接删除表II。

## 文件、复现和边界

规范目录中的 `data_figures_revision.py` 是本轮可复现绘图源，仅读取已有CSV。`make_figures.py` 六个获授权函数委托该源；公共 `_panel_caption()` 改用独立文字绘制。其剩余调用者只有未重新生成的 `fig5_ablation()`、`fig6_uair_excl_design()`；源码检查和运行核验确认标题函数保留已设置横轴名。真实图4入口也已执行，所得数据与标签检查和候选一致。没有执行 `make_figures.py` 的整个 `main()`。

原虚拟环境Python入口失效。本轮将Matplotlib 3.11.2、NumPy 2.5.4、Pandas 3.1.0的预编译包隔离安装在 `tmp/data_figures_revision_20261026/site-packages/`，未更改实验环境。绘图与编译顺序执行，绘图线程限制为1。

从项目根目录复现全部候选（使用已具备上述包的Python）：

```powershell
python TO_OVERLEAF_paper_tmc_r1_clean/data_figures_revision.py
```

也可用 `--only fig_w1_design_gate` 等参数逐图生成；`--out`指定独立目录。完整统计/来源记录为候选目录中的 `PLOT_STATISTICS_AND_SOURCES.json`。

## 编译与一致性检查

- 正文14页、补充14页；图号仍为正文2—4、补充5—8。初次集成一度15＋15页，最终通过本轮图内留白与图注去重恢复，没有缩小模板或文字字号、删除结果或其他章节证据。
- 已查看最终正文10—11页、补充7—8、11、13页及独立候选。无可见裁切、缺字、数值遮挡、悬空图例；覆盖图标题与轴名及图例的包围盒检查通过。
- 最终日志没有Overfull、未定义或重复引用、待重编译提示。保留原有Underfull等普通排版提示，不声称日志完全无警告。
- 八个候选PDF均没有嵌入位图。学习曲线为曲线数据生成的矢量路径，不是描摹PNG。
- 均值和样本SD已独立复核，原过滤行与方法顺序一致；学习曲线每模型/数据集均为200遍×3种子，阴影没有改称置信区间。
- 输入CSV逐字节不变；图一PDF/PNG/SVG、图一源代码不变；未授权图片、三个TeX中的非本轮图注/图格式区域和其他绘图函数均通过未改动核验。`supplemental.tex`保持原字节。
- 科学结论和已知支持身份差异保留。本轮未补齐的来源信息仅为上列汇总/窗口文件缺少种子键；没有为此编造身份或启动实验。

最终核验文件位于 `tmp/data_figures_revision_20261026/`，包括 `verification.json`、`source_scope_verification.json`、`entrypoint_verification.json` 与编译日志。源码差异见 `DATA_FIGURES_REVISION_DIFF.md`；前后图像见 `DATA_FIGURES_BEFORE_AFTER.md`。

## 备份与恢复

备份目录：`TO_OVERLEAF_paper_tmc_r1_clean/figures/_backup/data_figures_before_revision_20261026_221941/`。其中保留原数据图PDF/PNG、make_figures.py、原学习曲线脚本、main/appendix/supplemental.tex、正文/补充PDF、figure_data及result_sources小型来源副本；恢复说明已保存。所有初始副本已核验可读取且字节相同，原图一备份未触动。

恢复时，将本轮数据图PDF/PNG恢复原位置；仅合并恢复本轮图注、学习图PNG引用与原宽度、六个绘图函数和公共标题函数。若之后论文已有修改，**不能整体覆盖旧TeX或旧脚本**。重新编译当前论文；备份PDF仅代表备份时间点。新绘图源和候选可作为未启用资产保留，不删除任何备份。
