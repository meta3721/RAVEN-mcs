# 字体与局部排版修复报告

日期：2026-11-04。规范工程：`C:/Cursor/raven.mcs/TO_OVERLEAF_paper_tmc_r1_clean/`。

本轮指定范围验收通过：正文 **14页**、补充材料 **14页**。完成12处段内标题标点、C-D/表VIII关联、8张插入图的字体与局部布局、原7pt表格的字号提升。实验、模型、协议和统计结论没有改动。该结论仅覆盖本轮排版任务，不代表其他投稿待办已完成。

使用 ccf-paper-writer、ccf-visual-composer、ccf-humanization；最后按 ccf-submission-checker 的 package-check 模式检查编译、字体、编号和页面。

## 1. 已修复

### 12处段内标题

删除 `\paragraph{...}` 参数内的末尾句点，保留 IEEEtran 自动生成的冒号；没有更改标题名称、层级或类文件。

- 正文10处：City Scanner protocols；Controlled station comparisons；Additional sensing protocols；Target-risk and arrival-risk comparison；Matched-support comparison；Reference reconstruction and feasible calibration；Component contributions；Support and constraint geometry；Target-support variants；Reference sensitivity。
- 补充2处：Feasible target image；Reference stability of P2。

源码和最终PDF均未再检出标题末尾 `.:`。

### C-D与表VIII

- 修改前：C-D标题与表VIII均在补充第6页，但表先出现在页顶，标题在其后且没有解释文字。
- 修改后：仍在补充第6页，实际顺序为 **C-D标题 → 实质引导句 → 表VIII → Appendix D**。
- 引导句说明比较 selection units、available information、target objects 和 guarantee scopes，保留FedIPW、FedPALS、RAVEN-MCS的机制比较身份。
- 局部将标题、正常10pt引导句和表格组合在同一个 `table*` 排版块，表后设置 `\FloatBarrier`。此前仅在表后加边界仍会使表浮到标题之前，因此采用此局部组合。标题和引导在宽表上方，读者无需跨越下一附录寻找归属；未使用 `[H]`、负间距或缩字。
- `app:mechanism_comparison`、`tab:nearest_neighbor`、表内容和引用均保留。标题/引导不是另一个性能实验。

### 图1

修改 `fig1_framework_vector.py`，保留现有矢量对象、计算流程和反馈关系：仅对字体、节点宽度、换行、节点边缘连接位置进行适配。`Sensing and usable updates` 面板短语中的 and 用 `+` 表示，含义不变。

- 最终插入正文的主要标签约 **8.91pt（约9pt）**，普通辅助标签约 **8.23pt**；原先许多辅助标签约6—7pt。
- 选择/滞后状态、陈旧度、P2正则说明等换行；适度扩大局部节点，未删除模块或核心输入。
- 实际检查 ReportLab `Canvas` 的构造接口后，设置 `initialFontName='F1'`，使用已注册STIX初始化。原先没有文字绘制调用的Helvetica资源已消失；这属于资源清理，修改前并非已经发生文字缺失。
- 从同一源代码导出正式PDF、带嵌入STIX字体的活文字SVG及PNG预览。PDF可选择文字，无整图栅格化或全文转轮廓。

### 七张数据图

仅调用 `data_figures_revision.py` 的7个指定函数；未执行 `make_figures.py` 的整体入口。候选先输出到 `figures/font_polish_candidate/`，检查后替换原文件名。

- 正文图2 `fig_w1_design_gate`：轴标题、面板和共享图例层级提高；数值标签约8pt，原符号、精度、分母、零线及正负方向不变。数值标签完整落在轴内，包围框互不重叠。
- 正文图3 `fig_g3_tdrive_h_mass`：共享横排图例约9pt，轴标题约9pt，刻度和数值约8pt；目标、真实R、单位平衡参考及0.05线均保留。
- 正文图4 `fig2_e2_risk_noninterchangeability`：轴/面板约9pt，方法与方向计数约8pt；均值、样本SD和18/20、18/20、17/20、17/20、17/20均保持。
- 补充图5/6：横向均值±样本SD区间图、方法顺序和完整误差线保持；面板约9pt，方法/刻度约8pt。
- 补充图7：普通轴/面板约9pt、图例/刻度约8pt。共享图例分两行，增大面板间留白；轴标签与子图说明仍是不同对象。保留上图0、0.1、0.2刻度、y=x、阈值、误覆盖点和下图WARMUP/RESET。
- 补充图8：单位标签约8.5pt，列/行/面板和共享图例约9pt，刻度约8pt；保持物理单位、对数横轴、三种子min–max阴影及基线。未将其改称置信区间。

7图的输入身份、所有统计字段、均值/SD、方向计数、窗口、曲线、阴影和基线记录，与上一正式绘图记录逐项完全一致。比较结果在 `tmp/font_local_20261104/plot_data_comparison.json`。没有新增检验、模型计算或实验统计结论。

### 表格

正文表I、III、IV由 `\scriptsize` 改为 `\footnotesize`。补充表IX、X、XII、XIV、XVI、XVIII、XXIV、XXVI、XXVIII、XXIX、XXXI及表XII表注同样提升。

- 约7pt → 约8pt；其余已清楚的8pt或更大文字保持。
- 局部将 WorstGroupRMSE 表头换行；表III将数据集组名旋转，增加可用列间空间；小范围调整表III、IX、XIV、XXVI列间距，XIV的 Neg. seeds 表头换行。
- 不改变行列、有效数字、SD、标记、粗体最优值、样本量或单位；没有用 `resizebox` 抵消字号提升。
- **保留的约7pt密集表例外：无。** 正文3处、附录12处（含1处表注）scriptsize命令均已替换。数学上下标和模板小型大写字形另按用途判断，不计为表内普通文字缩字。

## 2. 字体实测与本来符合的项目

以下是最终PDF中的近似PDF point。插图按实际正文/补充版面检查，而非按放大预览的视觉大小判定。

- **正文**：Nimbus Roman，主要普通正文约9.96pt；摘要约8.97pt粗体为IEEEtran既有层级。
- **标题**：主标题约23.91pt；章节/小节使用模板约10pt及其小型大写、斜体层级。未更改字号或字体包。
- **图注与表题**：模板普通文字约7.97pt；其小型大写中的较小字形约6.38pt，属于模板形态。
- **表格**：普通文字约7.97pt或更大；上下标按数学层级保留。
- **图内标签**：图1为STIX，主要约8.91pt、辅助约8.23pt；数据图为Times New Roman与STIX，轴/面板等约8.97pt、细节约7.97pt，学习曲线单位约8.47pt。小图覆盖诊断图例维持约8pt，以保留数据空间；不声称所有图例或字形都达到9pt。
- **公式**：保留Computer Modern/STIX，主体随环境约8/10pt，上下标常见约5—7pt。图1下标约5.92pt，未机械放大到普通标签字号。
- **参考文献**：Nimbus Roman，模板约7.97pt；补充少量代码等宽字体保留。

原稿正文/标题/图注/公式/参考文献的这些角色层级本来符合本轮要求，并非多字体错误。PDF字符提取器对旋转字符的包围框高度可能给出较小“size”；旋转轴标签同时核对生成器的字号与实际页面，不把单个字形高度解释为字体字号。

官方[IEEE图形指南](https://journals.ieeeauthorcenter.ieee.org/create-your-ieee-journal-article/create-graphics-for-your-article/file-formatting/)的最终尺寸约9–10pt是可读性建议。本轮保持约9pt主标签与约8pt细节层级，没有把该建议当作所有上下标的硬性下限。

## 3. 编译、完整性与视觉验收

- 最终编译顺序：正文LaTeX → 补充LaTeX → 两份BibTeX → 交替两轮正文/补充LaTeX。8次调用均退出0；两份aux哈希稳定。最后一次完整构建墙钟约4.91秒，不将其当作整项任务CPU用量。
- 页数：修改前14/14，修改后 **14/14**，均含各自参考文献。未缩小模板或正文。
- `pdffonts`检查两份成稿和8个实际插入图：**所有字体资源嵌入，Type 3为0，未嵌入资源为0**；图1无Helvetica资源。正常Font Info映射不计为错误。
- 最终日志：Overfull、缺字、LaTeX Font Warning、未定义引用/文献、重复标签均为0。剩余 `epstopdf` 提示仅为shell escape被禁用，全部插图已是PDF，无需EPS转换。
- 正文aux图1–4、表I–VII；补充aux图5–8、表VIII–XXXII，编号和标签不变。PDF按双栏几何提取文字时可能把左右栏表题读成非编号顺序，因此同时核对aux、实际表题和页面。
- 32张表的数值标记逐表比较相同；显示公式、所有label及cite键与备份相同。`supplemental.tex`与本轮备份逐字相同，保留了此前工作树修改。
- 两份PDF共28页全部渲染并逐页查看100dpi完整页面；另以170dpi放大检查图1、正文表III/IV、C-D/表VIII、表IX/XIV/XXVI、覆盖诊断及学习曲线。检查了其余字体变更图的独立预览和正文实际尺寸。未见裁切、遮挡、缺字或坐标/子图标题覆盖。
- 新增文字仅C-D引导句，按humanization检查为直接的比较内容说明；未新增防御性总结或扩大方法主张。

## 4. 交付与证据位置

- [正文PDF](C:/Cursor/raven.mcs/TO_OVERLEAF_paper_tmc_r1_clean/main.pdf)、[补充PDF](C:/Cursor/raven.mcs/TO_OVERLEAF_paper_tmc_r1_clean/supplemental.pdf)。
- 修改的规范源文件：`main.tex`、`appendix.tex`、`fig1_framework_vector.py`、`data_figures_revision.py`，以及 `figures/` 下8组同名PDF/SVG/PNG。其他图没有重新生成。
- 候选与统计记录：`TO_OVERLEAF_paper_tmc_r1_clean/figures/font_polish_candidate/`。
- 逐文件源码差异、前后字体输出、完整性检查、构建记录和逐页渲染：`C:/Cursor/raven.mcs/tmp/font_local_20261104/`。其中 `checks.json`、`citation_build_status.json` 和 `table_page_index.json`记录最终检查。
- [图1前后对照](C:/Cursor/raven.mcs/tmp/font_local_20261104/comparison_fig1_raven_problem_framework.png)、[覆盖诊断图前后对照](C:/Cursor/raven.mcs/tmp/font_local_20261104/comparison_fig_certificate_audit.png)。对照图按同宽缩放供定位，字号结论依据最终PDF实测。
- C-D前后位置证据：`before_supplemental_6.png`与`zoom_supplemental_6.png`；最后一次覆盖刻度核对以正式补充PDF第13页为准。

## 5. 回退

已验证可读且逐文件哈希一致的修改前备份：

`C:/Cursor/raven.mcs/ccf-review-report/backups/font_local_20261104_132021.zip`

包含3份TeX、2个绘图源、8组原PDF/SVG/PNG、两份原论文PDF、`MANIFEST.json`及 `BACKUP_AND_RESTORE.md`。未覆盖或删除此前备份。

恢复时先把ZIP解压到独立临时目录。若此后无其他修改，可按清单恢复本轮4份已改源码及8组图文件，并顺序重编译两份PDF；`supplemental.tex`本轮没有改动，无需替换。若已有后续修改，应按差异合并回退标题标点、表格字体/布局、C-D排版和绘图参数，不能直接用旧main.tex覆盖后续工作。只需查看原样PDF时，从备份独立打开即可，不必改动规范源文件。

## 6. 保留与未解决项

本轮范围内没有尚未解决的溢出、字体资源或C-D归属问题；没有保留7pt密集表例外。约9pt图标签是分层优化目标，8pt细节及更小数学上下标已如实列出，并非所有字形统一9pt。

作者信息、摘要长度和终检中其他事项不在本轮范围，未改动、未宣称通过。实验保持暂停；没有运行训练、预测、重评分、求解器或新的统计检验。
