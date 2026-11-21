# FIGURE_TABLE_PLACEMENT_REPORT

日期：2026-10-30（Asia/Shanghai）。状态：**结构迁移完成，最终PDF版面和语义检查通过**。

交付：[正文PDF](C:/Cursor/raven.mcs/TO_OVERLEAF_paper_tmc_r1_clean/main.pdf)；[补充PDF](C:/Cursor/raven.mcs/TO_OVERLEAF_paper_tmc_r1_clean/supplemental.pdf)；[规范源码](C:/Cursor/raven.mcs/TO_OVERLEAF_paper_tmc_r1_clean/main.tex)。

## 1. 实际版本和回退

以本轮开始时当前工作树的已润色main.tex及两份14页PDF为基线；保留10月29日引用修复、证明重述、City Scanner主表及语言修订，没有恢复旧稿。按用户最新指令，由ccf-paper-writer作位置调整、ccf-humanization检查衔接、ccf-submission-checker核验编译与PDF实际位置。

修改前一次备份：[figure_table_placement_20261030_084624](C:/Cursor/raven.mcs/TO_OVERLEAF_paper_tmc_r1_clean/revision_backups/figure_table_placement_20261030_084624)，保存main.tex、appendix.tex、supplemental.tex、reference.bib、两份PDF及aux/bbl。本轮只修改main.tex与编译产物；另外三份规范源码按字节与备份一致。

回退：没有后续编辑时可恢复备份main.tex并重编译两个PDF；已有后续编辑时，按[main.tex.diff](C:/Cursor/raven.mcs/TO_OVERLEAF_paper_tmc_r1_clean/revision_backups/figure_table_placement_20261030_084624/main.tex.diff)合并回退本轮修改，不用旧整篇文件覆盖后续工作。此前备份全部保留。

## 2. Figure 1迁入第三节：源码与PDF双重核验

- 整个figure*环境从Introduction移入第三节，只有一个实例；原文件名fig1_raven_problem_framework.pdf、图号1及fig:raven_overview标签保留，图形资产与绘图源码未改。
- 第三节标题：[main.tex:200](C:/Cursor/raven.mcs/TO_OVERLEAF_paper_tmc_r1_clean/main.tex:200)；首次框架导读/引用：[main.tex:203](C:/Cursor/raven.mcs/TO_OVERLEAF_paper_tmc_r1_clean/main.tex:203)；浮动体标签：[main.tex:220](C:/Cursor/raven.mcs/TO_OVERLEAF_paper_tmc_r1_clean/main.tex:220)。导读只说明本地更新、服务器参考重构及窗口关闭时的可行校准，没有复制后文公式。
- 最终PDF第三节从**第2页**开始，延续到**第4页**；第四节标题在第4页。完整图一及图注实际位于**第3页**，在第三节开始之后、第四节之前，未落回第一/二节或拖入第四节。
- 前两节均不引用图一；图一的首次编号引用在第三节标题之后。
- 第四节前使用已有placeins的FloatBarrier，确保图一在第三节内排出。Evaluation前另设FloatBarrier防止实验浮动体回漂。没有clearpage、负间距、字号或图形宽度调整。
- 图注保留Design窗口前配置、Gate诊断、聚合后债务更新、空窗口等通用身份说明。City Scanner栅格客户端身份从框架图注去重，Evaluation设置及Table II已有更精确的500m×30min定义，没有丢失。

## 3. 六处前置表格引用及实验内容去向

1. **引言City Scanner应用段 / tab:cityscanner_real**：删除前置重复。最低平均组失配、真实R/受控U、两协议O身份及预测排序均已在Evaluation的City Scanner段和Table II充分说明，现保留在 [main.tex:1285](C:/Cursor/raven.mcs/TO_OVERLEAF_paper_tmc_r1_clean/main.tex:1285)及相邻分析。25.8%/23.3%仍为对TwoStage-Hájek的组失配下降，按种子均值之比；未改为预测收益。
2. **引言匹配支持段 / tab:trained_rules**：删除前置重复。计数、Uniform、参考投影、完整P2及几何的结果解释仍在VII-E及VII-F；主表VI在 [main.tex:1556](C:/Cursor/raven.mcs/TO_OVERLEAF_paper_tmc_r1_clean/main.tex:1556)。没有把删掉编号后的经验结论留在引言。
3. **引言目标支持变体 / tab:cityscanner_sixarm**：删除编号与应用结果引导，现只保留评估设计概述。六臂目标支持/形状比较及其完整统计解释留在VII-B、Table III（[main.tex:1347](C:/Cursor/raven.mcs/TO_OVERLEAF_paper_tmc_r1_clean/main.tex:1347)），十轨迹×每轨迹三模型种子的层级、非劣性及不利结果不变。
4. **引言第三项贡献 / tab:cityscanner_real与tab:trained_rules**：改写为“Evaluation of alignment mechanisms”，说明评估的问题与设计，不再宣称最低失配或已发现的结构优势；不引用图、表或实验附录。前两项的原子建模、机制和理论贡献保留。
5. **Related Work / tab:nearest_neighbor**：保留FedIPW、FedPALS及RAVEN差异的准确独立文字，表格指向迁至Evaluation的Methods and pairing，[main.tex:1183](C:/Cursor/raven.mcs/TO_OVERLEAF_paper_tmc_r1_clean/main.tex:1183)。明确此表比较对象、信息与保证范围，不代表已运行这些方法作新基线。表本体仍在补充Table XVI。
6. **Section IV / tab:f1_mechanism**：方法只保留常数权重归一化相消的数学说明和Appendix D推导；观测异质性表的编号引用迁至VII-F原有局部权重解释，[main.tex:1700](C:/Cursor/raven.mcs/TO_OVERLEAF_paper_tmc_r1_clean/main.tex:1700)。没有恢复未闭合的预测结论。

引言现在仅以一句话概述评估设计，贡献第三条说明科学问题；人工逐句检查未留下定量或定性实验发现，也没有用“results below”等含糊转述绕过迁移。理论结论与其Proposition/Theorem指向仍保留。摘要不属本次迁移范围，按原文完全保留核心结果。

## 4. 相关方法旁注的合并

- Section IV的同支持Design、Obs/Use实验旁注和Section V的数值可行性、规则比较旁注，从前置方法解释去重；相应结果原已在VII-E的规则比较/消融及Numerical accuracy段。数值可行性与数学最优解的区别现在在该结果段明确指向Appendix E。
- 主文Proposition 3中的“reported traces发生clipping”经验旁注去重；VII-F原有active-clipping说明保留。正式假设、下界、固定状态和不截断条件未变，所有编号公式原样。
- 理论覆盖段的“实验stress levels位于pairwise障碍区”移至VII-G覆盖候选解释。pairwise障碍的数学说明和证明指向仍在理论节，未把诊断结果当作主方法保证。
- 没有新增实验分析段落目录，也没有将后文已充分报告的事实再次复制成结果清单。

## 5. 全局结构及内容保护检查

- Introduction：figure/table/figure*/table*/wrapfigure/subfigure/图片调用及input/include引入均为零；无Fig./Figure/Table/Tables编号表述，无图表自动引用，无实验附录指向。
- Evaluation开始前：表格编号引用**0**、table浮动体**0**；同时检查ref/eqref/autoref/cref/Cref目标与实际图表label映射，以及PDF中“Table”输出，不仅搜索单个关键词。
- 图一首次引用属于III；其他图2–4及表I–VIII均在VII及以后。PDF Evaluation在**第7页**开始，第一张表I在**第8页**，没有实验表格回漂到该标题之前。
- 图表数量、顺序和编号不变：正文4图、8表；补充4图（5–8）、25表（IX–XXXIII）。主表II、III、VI继续为正文Evaluation中的跨栏表。
- 所有保留图表均有有意义的文字解释及直接编号引用；没有把label定义或caption自引算作完成。原有label的数字逐一与备份aux对比一致，补充setcounter无需改动。
- 表格tabular内容逐块相同；所有编号公式、算法块逐块相同。没有更改约束、系数、统计阈值、结果数字、误差线、方法身份或比较尺度。
- appendix.tex、supplemental.tex、reference.bib未改；引用键集合仍46个来源，2025年15篇、2026年7篇；独立方括号引用保留。未运行实验、模型、重新评分或统计检验。

## 6. 编译与页面验收

使用现有MiKTeX/IEEEtran工具链，单进程、低优先级顺序编译。最后一轮main/supplemental各LaTeX→BibTeX→两轮LaTeX均退出0，双向xr的aux稳定。正文**14页**，补充**14页**，与基线页数一致。

无未定义引用、重复标签或Overfull警告；仅保留既有epstopdf未开启shell escape提醒，不影响PDF/PNG资源。未手写编号修补引用。

已渲染并逐页检查28页，重点查看引言、Related Work、第三节第2–4页、III/IV交界、VII开头及全部图表页。图一第3页完整显示；文字、图注、公式、跨栏主表没有裁切、重叠或异常空白。原有密表字号和图形均未改变，本轮不将位置调整扩大为视觉重设计。

结构迁移无未满足项。作者信息、公开复现入口和其他历史待办均未填写或修改，不属于本轮结构验收范围。

核验记录保存在tmp/placement_20261030/：baseline.json、PLACEMENT_VERIFICATION.json、顺序编译日志及逐页预览；本轮关键记录亦随回退备份保存。
