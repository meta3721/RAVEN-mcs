# 引用显示格式修改报告

日期：2026-10-25。状态：**源码修改、正文/补充编译及新PDF显示验收通过**。本轮使用ccf-submission-checker的局部package-check；没有扩展为全文审稿或论证修订。

## 修改范围

仅原位修改规范目录两个配置：

- `main.tex:17`：`\usepackage[nocompress]{cite}`。
- `supplemental.tex:18`：相同设置；其实际包含的`appendix.tex`继承该配置。

现有IEEEtran.cls第4402行已定义`\citepunct{], [}`，无需新宏或额外括号。保留排序，只关闭连续数字压缩。配置依据：[CTAN cite文档](https://mirrors.mit.edu/CTAN/macros/latex/contrib/cite/cite.pdf)。没有拆分多键调用、手写静态编号或仅替换范围连接号。

检查了三个实际tex文件及包含关系，未发现natbib/biblatex、重复加载或自定义引用宏覆盖；剔除注释后未发现手写文献范围或两个cite间手写连接号，无需恢复引用键。

## 身份与内容保持

正文31次cite调用，其中9次多键；补充入口无直接cite，附录5次均单键。逐调用命令、键顺序、键集合、文件和行号与修改前完全一致。参考库54项逐字未变；实际正文书目47项，补充5项。详见[CITATION_KEY_POSITION_RECORD.md](C:/Cursor/raven.mcs/ccf-review-report/CITATION_KEY_POSITION_RECORD.md)。

按本轮编辑前字节记录核验：反向去除新增nocompress选项后，两个入口与原始字节完全一致；appendix.tex及reference.bib完全一致。保留已有工作树修改，没有回退历史稿；正文论证、实验数字、公式、图表及书目内容不变。旧PDF为10月18日，不能充当当前源码基线的布局验收。

## 构建与显示检查

使用现有MiKTeX25.12、IEEEtran及BibTeX，单进程、低优先级、禁用自动安装和shell escape。顺序：正文→补充→两入口各自BibTeX→正文/补充两轮，共8次调用全部退出码0，两份aux稳定。编译子命令累计墙钟约7.28秒，非完整编辑任务CPU计量。

2026-10-25重新生成规范main.pdf和supplemental.pdf；正文14页、补充14页（均含参考文献），相对旧PDF没有整页变化。

- 全文扫描新PDF，包括附录、表格、图注、脚注及换行，文献区间候选 **正文0、补充0**。
- 正文全部9个多键簇按新aux编号逐项核验，完整独立方括号；例如原[7]–[17]现逐条显示[7]到[17]，没有丢失中间文献。
- 实际阅读正文第2、3页及补充第7页渲染。逗号、引用换行和表头引用正常，无引用簇遮挡、截断或明显越界。补充没有多键调用，未人为新增演示引用。
- 扫描命中的[0,2]与[0,1000]逐处核定为数学/数据取值区间，未修改；参考文献页码连接号未修改。
- 无未定义引用、[?]、重复方括号、重复标签、Overfull、待重编提示或引用宏错误；两份BibTeX无warning。原工程没有hyperref，旧/新PDF均无链接注解，故超链接保持检查不适用，未擅自新增。

仍有正文25条、补充21条Underfull提示，以及原有epstopdf禁用shell-escape提示和MiKTeX未检查更新提示；未阻断编译，未为消除这些提示越界改内容、模板或更新环境。没有需要用户解决的阻塞构建问题。

## 产物

- [main.tex](C:/Cursor/raven.mcs/TO_OVERLEAF_paper_tmc_r1_clean/main.tex) / [main.pdf](C:/Cursor/raven.mcs/TO_OVERLEAF_paper_tmc_r1_clean/main.pdf)
- [supplemental.tex](C:/Cursor/raven.mcs/TO_OVERLEAF_paper_tmc_r1_clean/supplemental.tex) / [supplemental.pdf](C:/Cursor/raven.mcs/TO_OVERLEAF_paper_tmc_r1_clean/supplemental.pdf)

小型审计JSON、构建日志和页面渲染位于tmp/citation_format_20261025；未复制整份论文或创建另一套final稿。ccf-review-report中只新增MD记录。没有启动实验、训练、推理、重评分或统计检验，原实验暂停状态保持。
