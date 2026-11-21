# RAVEN-MCS 小标题、附录C-D与全文字体修复指令

请直接在现有LaTeX工程中完成以下局部修复，并编译、检查交付。使用 `ccf-paper-writer` 处理必要文字，使用 `ccf-visual-composer` 处理现有图表和浮动排版，最后用 `ccf-submission-checker` 验收；新增引导句按 `ccf-humanization` 保持直接、准确。

本指令的“第3、4项”指2026-11-04终检中的“小标题重复标点”和“附录C-D孤立标题/表VIII位置”，不是第三章、第四章的方法内容。

## 一、工程及本轮边界

工程目录：`C:/Cursor/raven.mcs/TO_OVERLEAF_paper_tmc_r1_clean/`。

必须读取：

- `main.tex`、`appendix.tex`、`supplemental.tex`，以及当前 `main.pdf`、`supplemental.pdf`。
- 当前8个实际插入的图PDF；需要修改图形字体时读取其生成源码，包括 `fig1_framework_vector.py`、`data_figures_revision.py`，其余图按实际调用追溯。
- 检查依据：`C:/Users/szr/Desktop/record/1/ccfa-review-reports/raven-final-submission-check.md`。

本轮仅处理上述两项局部排版，以及全文字体、图表文字的规范与可读性。保留论文主线、方法定义、章节结构、实验结果、全部数值、统计含义、公式符号、文献键、图表数据和证据边界。作者信息、摘要压缩等其他待办不在本轮修改范围。

实验继续暂停。只运行LaTeX编译、字体检查及使用现有数据的必要绘图导出。先查清绘图入口，避免调用包含训练、模型预测、统计重算或整个实验流水线的入口。

修改前，按工程已有备份约定，为实际要修改的TeX、绘图源码、图PDF/SVG及两份论文PDF保存可回退副本；不得覆盖已有备份。记录备份和恢复位置。完成后更新正式文件，不生成多个混淆的正文版本。

## 二、先复核当前字体事实，避免误修

截至本轮检查，当前文件仍是正文14页、补充材料14页。以下是实测事实，若文件已更新，应重新测量：

- 正文与补充材料的主要正文文字约9.96 PDF pt，属于Times系的Nimbus Roman；正常粗体与斜体均存在。
- 公式使用Computer Modern和STIX，图中文字以Times New Roman/STIX为主；补充材料少量代码采用等宽字体。这些有明确用途的多字体并存不构成错误。
- 图注、参考文献及表格常见约7.97pt；部分表格使用 `\scriptsize`，约6.97pt。不能把所有小字号都归为正文缩字。
- 两份PDF和全部8个实际插入图PDF未发现Type 3字体；日志未发现缺字或LaTeX Font Warning。
- 日志中的部分 `LaTeX Font Info` 是Times字体的bx→b或数学符号字体映射，不应误报为缺字、字体损坏或必须整体更换字体。
- 主PDF唯一未嵌入字体资源是图1带入的Helvetica。它没有执行任何文字绘制；图1实际绘制文字使用已嵌入的STIX。需要清理资源，不能把它描述为已发现的文字缺失。
- 图1普通辅助标签多约6—8pt；其他数据图普通标签多约7.4—8pt，确有提升最终尺寸可读性的空间。

输出按“正文/标题/图注与表题/表格/图内标签/公式/参考文献”分类的字体清单。以最终插入PDF的实际尺寸为准，区分普通文字与数学上下标，不以最小单个字形字号作全篇最小字号结论。

## 三、修复小标题的重复标点

1. 检查正文中全部 `\paragraph{...}`。当前以下10个标题把句点写入参数，IEEEtran又自动追加冒号，导致PDF出现 `.:`：
   - City Scanner protocols
   - Controlled station comparisons
   - Additional sensing protocols
   - Target-risk and arrival-risk comparison
   - Matched-support comparison
   - Reference reconstruction and feasible calibration
   - Component contributions
   - Support and constraint geometry
   - Target-support variants
   - Reference sensitivity
2. 补充材料另检查 `Feasible target image`、`Reference stability of P2` 两个同类标题。
3. 删除标题参数内手写的末尾句点，让IEEEtran提供默认终止标点。例如改成 `\paragraph{Matched-support comparison}`。若当前类文件已有不同处理，按实际PDF确认，不重复加冒号。
4. 仅改标题末尾标点，不改标题文字、编号层级、标签、正文标点、公式小数点或参考文献。
5. 不修改IEEEtran类文件，不全局重定义标题命令。

验收：正文与补充材料不再出现标题末尾的 `.:`；原有分级和交叉引用不变。

## 四、修复附录C-D及表VIII的关系

当前源位置：`appendix.tex` 的 `\subsection{Selection Mechanisms and Information Requirements}` 与 `app:mechanism_comparison` 附近。当前PDF位置为补充材料第6页。该小节只有一个浮动表，表VIII被放到标题上方，标题后立即进入Appendix D。

1. 保留C-D小节、`app:mechanism_comparison` 及 `tab:nearest_neighbor` 标签。
2. 在小节标题与表格声明之间增加一句实质性引导。可直接使用以下内容，并依当前术语微调：

```latex
Table~\ref{tab:nearest_neighbor} compares the selection units, available
information, target objects, and guarantee scopes of FedIPW, FedPALS,
and RAVEN-MCS.
```

3. 调整局部声明位置或分页，使读者能清楚按“小节标题—引导—对应表格”阅读。优先将标题和引导保留在表格前方的正文中，使表VIII随后或紧邻出现。不要只按源码顺序认定问题解决，必须检查实际PDF。
4. 保持表VIII的全部技术比较内容和引用。它仍是信息条件与机制范围的比较，不能被改写成实际运行的性能基线结果。
5. 避免把标题孤立在页/栏末，避免让Appendix D标题插入C-D解释与表VIII的关联之中。必要时仅局部调整附近冗余措辞或浮动位置。
6. 不用全局 `[H]`、大段负间距、修改页边距或缩字解决；不重排A—H的大框架。

验收：C-D有实际内容，表VIII归属清楚；正文原有Supplementary Table VIII引用和阅读导引仍正确；后续附录编号不误变。

## 五、按角色规范字体与字号

### 5.1 正文、标题、图注、公式与参考文献

- 保留 `\documentclass[letterpaper,journal]{IEEEtran}` 及模板默认的标题、正文、摘要、图注、表题和参考文献层级。正文维持约10pt的模板字号。
- 保留模板产生的标题/表题小型大写、粗体、斜体和正常段落缩进，不把模板默认形态误当成不统一。
- 不全局改为其他文档类，不引入字体包强制覆盖全部正文/数学字体，不改变全局行距、页边距或正文宽度。
- 变量斜体、运算符及单位正体按现有数学语义保留；上下标、帽符号、希腊字母、负号、百分号、µg/m³和°C必须清晰且含义不变。
- 不把数学下标或指数强行放到与普通文字相同大小，不全局替换数学字母字体，也不把正文/公式转成图片。
- 图注、表题及参考文献优先保持IEEEtran默认字号，不为追求“全文一个字号”放大或缩小。

### 5.2 图1：小字与未使用字体资源

- 修改现有 `fig1_framework_vector.py` 的矢量布局及文字参数，保持现有计算流程、连接方向、模块名称和符号。局部维护现有图，不开启新一轮生成式草图。
- 普通主标签以最终版面约9—10pt为目标，辅助普通文字尽量达到8pt以上；数学上下标不受这一普通文字目标机械约束。目标源于IEEE图形可读性建议，不宣称它是所有字形的统一硬性下限。
- 优先增大当前6—8pt辅助文字；通过节点留白、合理换行和少量压缩重复说明腾出空间。关键方法标签、概率/质量/权重含义以及当前窗口与反馈箭头不能删改。
- 图1已有嵌入STIX可保留；无需为改字体名称而破坏数学字形。提高文字层级一致性和最终尺寸可读性。
- 清理未使用Helvetica资源：优先在生成器初始化时使用已注册且可嵌入的字体；或验证资源没有文字调用后移除未使用资源。须查验实际运行库接口，不靠猜测参数修改。
- 从同一矢量源码同步导出可编辑SVG与插入论文的PDF，保留可选择文字。使用嵌入字体，避免整图栅格化或把全部文字转轮廓来掩盖问题。

### 5.3 数据图：统一普通文字层级

- 全面检查当前正文图2—4与补充图5—8，而非只看独立图文件。优先沿用已有Times New Roman正文图字体与STIX数学字体。
- 普通轴标签、图例、面板说明以最终版面约9pt为优化目标，细节标签一般争取至少8pt；已有清楚、统一的图不必为了凑字号而重画。
- 同类图的轴标签、刻度、图例与面板标签分别保持一致层级。特别关注补充图7约7pt普通标注以及学习曲线中的单位/指数。
- 字体变大时调整图内留白与面板间距，必要时合理换行；不能通过裁切、减少必要坐标信息或把导出图再缩小抵消字号增益。
- 仅更改视觉参数，保持输入CSV、方法顺序、坐标变换、轴范围含义、数据点、误差线/阴影统计量、图例含义与所有数值标签不变。
- 从实际生成器导出矢量PDF，Matplotlib设置合适的TrueType嵌入，例如 `pdf.fonttype=42`；若输出SVG，保留文字编辑能力。核验导出结果，不只检查rcParams。

### 5.4 表格：优先提高普通表内文字

- 重点检查正文表I、III、IV的 `\scriptsize`，以及补充材料中所有使用 `\scriptsize` 的表。
- 表内普通文字优先约8pt，已有更大而清楚的文字保持。将约7pt的表能局部改为 `\footnotesize` 的先改；这是本轮可读性目标，不把7pt统一宣称为期刊违规。
- 优先通过表头换行、列宽、适度列间距、长方法名称换行处理宽度，保持booktabs结构；不要用整表 `\resizebox` 把字体再次压小。
- 个别密集补充表若必须保留约7pt，应逐项说明实际位置与原因，并检查100%版面/打印尺寸可读性；不把这当成全篇缩字许可。
- 全部数值、有效位数、±SD、显著性标记、最佳值粗体、单位、样本量与必要表注保持不变。必要时只在局部优化重复文字，不删行、删列或删证据。

## 六、编译和实际版面验收

1. 完成修改后重新生成受影响图，替换正式图文件，再编译两份文档。
2. 两份TeX通过 `xr` 互引，按工程实际依赖先生成正文aux，编译补充材料与各自BibTeX，然后交替编译正文/补充直至引用稳定。不能只编译main一次就认定完成。
3. 使用 `pdffonts` 检查两份成稿与8个插入图PDF：实际文字字体均嵌入，无Type 3，无未说明的未嵌入资源；图1的Helvetica资源清理应有明确结果。
4. 检查日志：缺字、LaTeX Font Warning、Overfull、未定义引用/文献、重复标签均应为0或有明确可核查解释；不要把正常Font Info算错误。
5. 渲染两份PDF共全部页面，检查100%阅读尺寸，并放大查看图1、表VIII、约7pt的表和所有改过字体的图。检查字符、单位、公式上下标、图例、坐标、图表题和表注无裁切、遮挡或重叠。
6. 检查修改后的页数目标：正文不超过14页、补充不大于正文；当前基线为14/14。优先局部排版和减少重复措辞保住篇幅，不以缩正文、改模板或删关键证据换页数。若暂不能兼顾，明确报告具体冲突和已完成部分，保留可回退文件，不标记全部完成。
7. 检查图表序列仍为正文图1—4、表I—VII，补充图5—8、表VIII—XXXII；阅读导引及正文到附录的引用均与新页码一致。
8. 对改动前后实验表格数值和绘图数据作内容比较，确认只改排版/视觉与指定引导句。无需启动训练或重算统计。

## 七、交付

- 更新后的正式 `main.pdf`、`supplemental.pdf` 和相应源文件。
- 更新过的图PDF、SVG及其绘图源码，保留回退副本。
- 一份简短的 `FONT_AND_LOCAL_FORMAT_FIX_REPORT.md`：列出12个标题的处理、C-D/表VIII前后页码、按角色的实际字体字号、未嵌入资源清理情况、图表视觉检查、页数/编译结果，以及修改和回退路径。
- 报告区分“已修复”“本来符合”“保留的密集表字号例外”“尚未解决”。不要把未执行的项目或单次成功编译写成全部验收通过。

规范来源：

- [IEEE Graphics File Formatting](https://journals.ieeeauthorcenter.ieee.org/create-your-ieee-journal-article/create-graphics-for-your-article/file-formatting/)：图形字体嵌入与最终尺寸约9—10pt建议。
- [IEEE Computer Society Author Guidelines](https://www.computer.org/publications/author-resources)：采用期刊模板，图表按最终尺寸放置并尽量接近首次实质说明。

本指令只要求执行指定范围的修复，不代表作者占位符、摘要长度或投稿账户信息等其他终检待办已完成。
