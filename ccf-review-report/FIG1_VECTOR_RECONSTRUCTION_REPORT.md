# 图一连线修正、矢量重建与集成报告

状态：已完成重建、图一集成、编译和页面检查。原始图与生成式草图均保留。实验继续暂停。

## 本轮落实的六项修改

| 用户意见 | 最终处理 |
|---|---|
| 权重接入服务器 | 只保留一组 α 输出；P2→权重向量→服务器为连续实线，与下方可用模型更新流在服务器汇合。 |
| 反馈来源分清 | 暖色虚线从组债务输出返回当前债务输入位置，注明下一窗口；蓝色虚线从更新历史输出分别返回重建所用历史和滞后状态输入。交叉处没有连接点。 |
| 共享校正量先分支 | R/O记录权重分成归一化本地训练权重和校正质量m两路；m与pre-U信息给出的d形成参考，不再从已重建参考反向决定训练。 |
| 债务不由模型参数计算 | 从α引出显式组成计算ω=Mα，再输入组债务台账；不从更新模型拉债务数据箭头。台账及历史更新置于“After aggregation”，图注说明执行顺序。 |
| 场景针对性 | 删除无人机、摄像头、手机组合，只保留网格、移动载体和车载传感器。图注说明City Scanner客户端为占用的时空网格单元。 |
| 精简与排版 | 合并权重输出、缩短可用性标签；记录/台账只留两行示意；删去长通道说明和P2发光。详细准入、空窗口及Design/Gate说明集中在图注。 |

新增物件均承担具体语义：网格与车载传感器表示机会；本地表表示观测记录；包表示归一化模型更新；时间轴区分按时/迟到；柱形向量表示参考与权重；矩阵表示客户端组组成；可行域形状表示约束；按组台账表示欠服务。所有高度、记录和台账均为示意，不是实验数字或精度提升证据。

## 交付与修改范围

规范目录：`TO_OVERLEAF_paper_tmc_r1_clean/`。

- `main.tex`：仅修改 `fig:raven_overview` 图注，标签和引用文件名不变。
- `make_figures.py`：仅替换 `fig1_framework()`，委托独立图一渲染模块；其他图函数逐字保持不变。
- `fig1_framework_vector.py`：新增独立矢量绘图源，使用同一组原生几何对象输出SVG/PDF，仅生成图一。
- `figures/fig1_raven_problem_framework.pdf`、`.png`：替换为检查后的新图；新增同名 `.svg`。
- `figures/fig1_redesign_candidate/`：保留生成式草图、最终候选PDF/PNG/SVG、源代码副本及字体资源。

SVG包含 **14个语义分组、117个活文字节点**，支持继续编辑；PDF包含 **0个嵌入位图对象**，不是草图截图或自动描摹。数学帽符为独立矢量线段，上下标为可编辑文字对象。字体使用STIX并随SVG嵌入，PDF使用的STIX正体/粗体已嵌入；图中图标全部为本轮原生几何绘制，无外部图标素材。STIX字体及原许可保存在候选目录 `assets/fonts/`，许可文件为 `LICENSE_STIX`。

独立再生成方式（从论文目录运行，需已有ReportLab和Poppler）：

```powershell
python fig1_framework_vector.py --out figures/fig1_redesign_candidate --poppler <pdftoppm可执行文件路径>
```

本轮使用现有文档Python运行时。原项目 `.venv_new` 的Python入口已失效，未擅自重建环境或安装依赖。实际 `make_figures.py` 中图一函数已单独提取执行验证，与候选SVG输出一致；没有调用整个 `main()` 或运行其他图函数。

## 编译与验收

- 使用现有MiKTeX，低优先级单进程顺序编译。正文 **14页**，补充材料 **14页**，无新增完整页。
- 正文图一位于第2页，通栏约180毫米宽；已查看最终页面、单图和彩色/灰度输出，未发现图文重叠、裁切、缺字或悬空主链。普通标签约6.2—8.2pt，上下标按比例缩小。
- 最终日志没有Overfull、未定义引用、重复定义或待重编译提示；既有Underfull提示正文26处、补充21处，未将其表述为“所有警告清零”。
- 修改范围验证通过：正文图注之外一致；其他图函数一致；17个其他图片文件、appendix.tex、supplemental.tex、reference.bib均保持原始字节。补充PDF仅随交叉引用重新编译。
- 矢量文件无位图嵌入；SVG结构可解析；绘制时逐字检查字体字形可用性；可执行图一入口重现相同SVG。
- 检查中修复了两个会造成误读的走线问题：支持输入绕开Q框，约束输入绕开V框；避免表现为依次经过这些无关状态。

本轮未发现仍无法由正文确认的机制。图一是活跃窗口机制总览，不承诺精确目标匹配或预测提升；空活跃窗口处理在图注中保留。没有修改算法定义、参数、公式、实验数值或统计结论。

机器检查和最终页面预览：`tmp/fig1_redesign_20261026/final_verification.json`、`main-vector-final-02.png`；局部源码差异：`ccf-review-report/FIG1_VECTOR_REVISION_DIFF.md`。

## 旧图与最终图对照

旧图的环形箭头将P2、债务和聚合顺序混淆，并有两个校准模块；最终图保留三部分构图，以连续数据流及分开的反馈线表达同一个方法。

**备份旧图：**

![备份旧图](C:/Cursor/raven.mcs/TO_OVERLEAF_paper_tmc_r1_clean/figures/_backup/fig1_before_redesign_20261026_094256/fig1_raven_problem_framework.png)

**最终矢量图的PNG预览：**

![最终图一](C:/Cursor/raven.mcs/TO_OVERLEAF_paper_tmc_r1_clean/figures/fig1_raven_problem_framework.png)

## 回退

备份目录：`TO_OVERLEAF_paper_tmc_r1_clean/figures/_backup/fig1_before_redesign_20261026_094256/`，完整保留，未覆盖或删除；恢复原始位置见其中 `BACKUP_AND_RESTORE.md`。

1. 恢复备份图一PDF/PNG到 `figures/` 的原同名文件。
2. 只合并恢复备份 `make_figures.py` 中的 `fig1_framework()`；若脚本后续有其他修改，不整体覆盖。
3. 只恢复备份 `main.tex` 中 `fig:raven_overview` 的旧图注。不能用旧全文覆盖后续论文修改。
4. 重新编译当前论文。备份main.pdf只代表备份时间点，不代表后续修改后的全文。
5. 新增SVG、独立渲染源和候选目录可以保留作为未启用资产，不需删除；旧函数恢复后不再使用新模块。不得清理备份目录。
