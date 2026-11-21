# 正文补强与数据图润色报告

日期：2026-11-04。规范目录：`C:/Cursor/raven.mcs/TO_OVERLEAF_paper_tmc_r1_clean/`。

本轮已完成正式源码与图片替换、双文档编译及28页视觉检查。采用**路线A**：从附录F-A现有支持几何表生成一张正文图，保留附录完整表格、窗口数和L1推导。正文与补充材料仍为 **14/14页**，正文第14页原空白右栏已自然填入参考文献。

实验保持暂停。没有训练、预测、求解器调用、重评分、新检验或种子筛选；没有改变方法、实验数值或主张范围。

## 1. 起点、范例与视觉方案

修改起点已实测为正文14页、补充14页；正文第14页左栏有3781个PDF字符，右栏为空。当前小标题标点、C-D/表VIII关系和字体修复均作为受保护起点保留。

实际查看了指定范例，而非按文件名推断：

- **C-PRISM带批注版本第14页**：图5、7、8采用成组等尺寸面板，下方放置子图标题；导师批注强调图例不压数据、面板大小一致。采纳这些组织原则，没有复制其三维图、双纵轴或四图横排。
- **MapT-STC第11—13页Evaluation**：图9/10的等尺寸配对面板、图13/14的稳定方法编码、图15/16的统一任务分组。采纳面板对齐、稳定颜色/标记、轴标题与子图说明分离；没有复制实验内容或版式细节。
- 范例页渲染及批注定位保存在 `C:/Cursor/raven.mcs/tmp/page_fill_20261104/` 的 `examples.json`、`cprism_p14.png`、`mapt_p11.png`—`mapt_p13.png`。

统一方案先于篇幅整合确定：保留3.5英寸单栏最终尺寸，Times系普通文字与STIX数学字体；轴、图例和面板约9pt，刻度/数值/行标签约8pt。三张正文数据图采用开放式上/右边界和克制纹理，保留零线及诊断线。同种方法沿用原配色、标记和顺序，Estimated/Oracle保留独立的配置编码。

## 2. 逐图修改与数据核验

### 正文图2：Design敏感性

文件：`figures/fig_w1_design_gate.pdf`；label `fig:w1_design_gate`，最终正文第10页。

- 两面板、百分比方向、不同数值范围、零线和公共图例保留。
- 柱宽由0.32减为0.28，组内中心间距由0.34增为0.38；Estimated保留斜纹，Oracle使用实色，降低纹理干扰。
- 正负数值各有预留标注行；负值增加横向错位及引线。近零的−0.005、−0.013标签与零线、坐标刻度分开。包围框检查确认所有数值标签在轴内且互不重叠。
- 数据仍为 `figure_data/FIG_W1_DESIGN_GATE.csv` 的原4行。8个数值、三位小数显示、No-Design分母及“正值更差”含义不变。
- 保留原数值轴上下界计算，没有扩大或压缩效应数值。

### 正文图3：机会质量与TV

文件：`figures/fig_g3_tdrive_h_mass.pdf`；label `fig:g3_tdrive`，最终正文第11页。

- 两面板统一绘图区高度和零基线，微调左右边距及面板间距；共享图例在上方。
- 精简重复纹理，目标为实色，真实R与单位平衡参考用不同方向斜纹；灰度下仍可区分。
- 保留原零起点、质量/TV范围、0.05阈值、SS/UA协议缩写与0.142/0.192/0.278标签。
- 数据仍为 `FIG_G3_TDRIVE_H_MASS.csv` 与 `FIG_G3_TDRIVE_TV.csv`，目标、真实机会和单位平衡参考未混合。没有把诊断值写成预测收益。

### 正文图4：风险差与方向计数

文件：`figures/fig2_e2_risk_noninterchangeability.pdf`；label `fig:risk_noninterchangeability`，最终正文第11页。

- 左面板改为**均值点＋完整水平样本SD区间**，去掉近似重叠的填充柱。RAVEN保持深蓝和原标记体系，其他方法保留各自颜色/标记。
- 两面板方法顺序、纵向位置完全相同，方法名称只在左侧出现一次。
- 右侧计数柱及18/20、18/20、17/20、17/20、17/20保留；零线、10/20参考线、科学计数倍率和D定义不变。
- 图注相应明确均值点及SD区间；未改为置信区间，没有新增显著性或排名解释。
- 数据仍为 `figure_data/FIG_E1_E2_RISK_NONINTERCHANGEABILITY.csv` 的原5方法×20种子，均值、样本SD、种子范围与方向计数逐项相同，轴范围不变。

### 新正文图5：到达支持与可调质量

文件：`figures/fig_arrival_support_geometry.pdf`；label `fig:arrival_support_geometry`，最终正文第13页、结论前。

- 采用路线A，不再迁移路线B结构失配图；补充四幅图均保留原位置。
- 六条100%堆叠条从当前 `appendix.tex` 的 `tab:arrival_support` 读取身份并逐行核验。独立生成器 `arrival_support_figure.py` 明确内置六行已发表表值，执行时断言与表格完全一致，不伪造窗口级数据。
- 按缺失/窄范围/可调质量绘制，百分数依次为：Traffic两行75.000/25.000/0；SensorScope两行98.916/1.084/0及97.748/0/2.252；U-Air两行98.551/1.449/0及97.024/0/2.976。
- 完整0—100%坐标，无断轴；约1%—3%的细段保留真实宽度，使用外侧数值和短引线。没有新增误差线。
- 正文与图注均说明：来源是正式轨迹的非空到达日志、使用到达组成映射；不等同于完整P2有效支持或跨窗口累计服务。U-Air的1515个到达窗口与1402个Design-on有效窗口明确分开。
- 完整窗口数、共同L1距离、种子汇总规则和推导仍在附录F-A/表XXIV；新图只解释支持与可调整性，不产生预测提升结论。

三张旧图的新旧数据记录逐项相同，见 `figure_data_comparison.json`。新图六行验证及来源见候选目录的 `ARRIVAL_SUPPORT_FIGURE_SOURCES.json`。

## 3. 正文补充位置与净增词数

采用同一近似英文计数口径：连字符/撇号词计一个词，排除数学表达及ref/label/cite命令。不是用页数反推词数。

- **IV-C，正文第5页**：原16词改为77词，净增 **61词**。解释归一化记录权重和为1后，客户端总校正质量为何仍需在服务器保留，以及m、d、参考β与后续α的连接。已有支持与识别条件保持。
- **V-C，正文第5页**：新增 **50词**。区分客户端权重的变化与经M映射后的群体组成变化，衔接RQ3，没有新增公式或理论保证。
- **VII-F/RQ3，正文第12页**：原16词引导改为84词解释，净增 **68词**。解释三类目标质量、0.01范围阈值、到达映射与有效支持的不同口径。
- 新图注 **39词**；既有风险图图注表达调整净增 **2词**。

正文说明净增 **179词**；计入全部图注变化，全文净增 **220词**。没有追加可选VI理论段，因为既有唯一性和固定状态稳定性说明已足够。没有扩写引言、摘要、结论或泛化背景。

humanization与prose-quality检查：新增/对应段落零em dash，最终检查零提示；局部消除两处分号连接，保持条件和不利结果。最终记录为 `prose_quality.json`。

## 4. 编号、布局与末页利用

- 正文图 **1—5**：新增5，其余label不变。原补充图5—8自然顺延为 **6—9**。
- `supplemental.tex` 的起始figure计数4→5，并同步说明性注释。所有相关正文/补充引用自动更新；表号仍为正文 **I—VII**、补充 **VIII—XXXII**。
- 图1保持在第三节/正文第3页，图1文件和生成器逐字节未变。C-D与表VIII保持补充第6页的“标题—引导—表格”顺序，12处标题标点及表格8pt修复未回退。
- 新图在RQ3的首次实质说明之后，于第13页排出；没有放到参考文献之后。参考文献自然顺延。
- 正文与补充材料修改前后均为 **14/14页**，包括各自参考文献。
- 正文第14页右栏从0个PDF字符变为3662个；左栏4024个。右栏文字下缘约684.84pt，左栏约747.60pt，保留约62.8pt（0.87英寸）的自然高度差。末栏已大体充实，没有拉大行距、缩小正文或改变模板。
- 三张既有数据图的最终物理尺寸不变：Design图3.5×2.05英寸，机会图3.5×2.02英寸，风险图3.5×1.85英寸；新图3.5×2.05英寸。没有先放大字号再缩小整图。

## 5. 验收结果

- 最终构建：正文/补充LaTeX、两份BibTeX、交替两轮LaTeX，共8次调用退出0，跨文件aux稳定；最后完整构建墙钟约3.89秒。编辑、绘图及编译均按单进程顺序执行，数值库线程设为1。
- 正文、补充及全部9个实际插入图PDF经 `pdffonts` 检查：字体均嵌入，Type 3为0；保留上轮图1无Helvetica残留的状态。
- 日志中的Overfull、缺字、Font Warning、未定义引用/文献和重复label均为0。仅有禁用shell escape的epstopdf提示，当前插图均为PDF，不需要EPS转换。
- 修改的四张图均输出活文字SVG和矢量PDF，未嵌入整图位图；PNG仅供预览。
- 三张旧图的数据、方法身份、顺序、种子和统计量与修改前记录完全相同；六行支持数据与附录逐项一致。
- 32张表的源码内容、所有编号公式、算法与文献引用键保持。`appendix.tex`与本轮备份逐字节一致；标题、摘要、引言、相关工作、系统模型也保持原文。全部绘图CSV、图1及四张补充图文件未改动。
- 28页全部按100dpi完整页面逐页检查，并核验图的最终单栏尺寸、灰度版本和单图放大预览。未见裁切、遮挡、缺字、误差线截断、图例压数据或子图标题覆盖轴标签。
- 本轮范围无未解决的证据、字体或页数冲突。该结论是本次局部编辑验收，不包括作者信息等其他投稿待办。

## 6. 正式文件与前后对照

- [正文PDF](C:/Cursor/raven.mcs/TO_OVERLEAF_paper_tmc_r1_clean/main.pdf)、[补充PDF](C:/Cursor/raven.mcs/TO_OVERLEAF_paper_tmc_r1_clean/supplemental.pdf)。
- [正文源码](C:/Cursor/raven.mcs/TO_OVERLEAF_paper_tmc_r1_clean/main.tex)、[补充入口](C:/Cursor/raven.mcs/TO_OVERLEAF_paper_tmc_r1_clean/supplemental.tex)。附录源码未改。
- [三图生成器](C:/Cursor/raven.mcs/TO_OVERLEAF_paper_tmc_r1_clean/data_figures_revision.py)、[新增支持图生成器](C:/Cursor/raven.mcs/TO_OVERLEAF_paper_tmc_r1_clean/arrival_support_figure.py)。只运行指定三个数据图函数及新支持图，未调用make_figures.main。
- [新支持图PDF](C:/Cursor/raven.mcs/TO_OVERLEAF_paper_tmc_r1_clean/figures/fig_arrival_support_geometry.pdf)、[可编辑SVG](C:/Cursor/raven.mcs/TO_OVERLEAF_paper_tmc_r1_clean/figures/fig_arrival_support_geometry.svg)。其余正式图沿用原文件名。
- 同最终尺寸对照：[Design对照](C:/Cursor/raven.mcs/tmp/page_fill_20261104/comparison_fig_w1_design_gate.png)、[机会/TV](C:/Cursor/raven.mcs/tmp/page_fill_20261104/comparison_fig_g3_tdrive_h_mass.png)、[风险差](C:/Cursor/raven.mcs/tmp/page_fill_20261104/comparison_fig2_e2_risk_noninterchangeability.png)、[第14页](C:/Cursor/raven.mcs/tmp/page_fill_20261104/comparison_main_last_page.png)。
- 候选、来源记录：`C:/Cursor/raven.mcs/TO_OVERLEAF_paper_tmc_r1_clean/figures/page_fill_candidate/`。
- 源码前后差异、视觉方案、灰度预览、逐页渲染和验收记录：`C:/Cursor/raven.mcs/tmp/page_fill_20261104/`，重点为 `checks.json`、`word_changes.json`、`citation_build_status.json` 与 `VISUAL_CONTRACT.md`。

## 7. 回退入口

已验证可读取、逐文件与起点一致的备份：

[page_fill_20261104_142650.zip](C:/Cursor/raven.mcs/ccf-review-report/backups/page_fill_20261104_142650.zip)

备份包含3份TeX、两份原PDF、原绘图源码、正式8组图PDF/SVG/PNG、绘图CSV及来源记录；旧备份未覆盖。

恢复时先解压到独立临时目录。无后续编辑时，恢复main.tex、supplemental.tex、data_figures_revision.py及三组修改过的数据图，然后交替编译两份文档；新增加的arrival_support_figure.py和fig_arrival_support_geometry三种格式可在确认没有后续依赖后移出正式目录。appendix.tex和图1本轮未变，无需替换。若已有后续改动，应合并回退本轮局部差异，不能用整个旧main.tex覆盖后续工作。原PDF可以直接从备份独立查看。
