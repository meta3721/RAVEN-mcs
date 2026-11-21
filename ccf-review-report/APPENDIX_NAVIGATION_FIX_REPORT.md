# 正文与补充材料导航修改报告

日期：2026-11-04。使用 ccf-paper-writer、ccf-submission-checker。实验继续暂停；本轮没有训练、推理、重评分、统计检验或实验配置修改。

## 交付与验收状态

已修改规范源文件并成功顺序编译：[正文 PDF](../TO_OVERLEAF_paper_tmc_r1_clean/main.pdf) **14页**，[补充 PDF](../TO_OVERLEAF_paper_tmc_r1_clean/supplemental.pdf) **14页**，均含参考文献，与修改前页数相同。

源码、编译、标签身份、书签和链接目标的结构核验通过；**实际阅读器点击验收尚未完成，不能标记全部验收通过**。完整层级实页标题改用了下述模板标题回退方案。两份 PDF 应保留相同目录、原文件名共同交付。

## 1. 引用样式与实现

- 首次引用：`Appendix A, subsection A of the separate Supplementary Material`；后续采用 `App. E, subsec. D` 等短式。第三层完整表达为 `App. B, subsec. C, subsubsec. 1`，不会误读为页码。整个附录的导航宏分支仍显示 `Appendix A`，不补不存在的子节。
- 同父附录的成对引用采用 `App. E, subsecs. E and D`，各子节分别链接；已检查每一对的父附录一致。
- 新增 [appendix-navigation.tex](../TO_OVERLEAF_paper_tmc_r1_clean/appendix-navigation.tex)：在原 label 所在位置从附录、子节、三级节计数器分别记录导航元数据。原 label、原值和目标锚点保留。未解析或截断 IEEEtran 的 `\mbox` 复合引用字符串，未修改类文件。
- 两份入口保留当前 `xr`。核对其 v6.00 的 externaldocument URL 接口后，结合 hyperref 生成相对文件名的 GoToR 链接，未凭猜测换成另一套引用工具。导航元数据与参考文献 nocite 处理保持独立。
- 附录数学标题提供仅用于 PDF 字符串的文字替代（n-min、PM2.5），印刷数学含义不变。

## 2. 标题、首页索引和书签的取舍

尝试用 IEEEtran 的本地显示钩子将子节标题印为 `E-D.`，不改变底层计数。该方案可编译，但长标题重排引起浮动表顺延，补充材料变成15页，未满足本轮14页预算。最终保留模板的实页 `D.` 标题；**没有完成首选的实页完整前缀方案**。此处是页数与排版回退，并非声称引用工具不兼容。

补偿措施：正文明确父级与子级；补充材料有完整层级 PDF 书签；首页 Reading guide 采用正常10pt正文大小，保留 A—H 全部8个入口及7个重点子节 E-D、E-E、F-D、F-E、H-A、H-B、H-C，各带自动页码和内部链接。纸面没有展开全部二级目录，以免挤出证明或实验。别名只对应一个物理位置。

补充材料55条书签覆盖所有附录、所有二级小节、B-C1/B-C2及参考文献。E-A至E-F完整列出本地权重抵消、观测异质性、Design支持变化、P2数值可行性、带债务投影与运行时间；F、H的支持/稳定化、敏感性、开发学习、正式参照和更新规则均明确分开。正文35条章节书签。未缩小全局字号、改变模板或删除科学内容腾空间。

## 3. 正文—附录完整映射及最终页码

以下是正文35个目标标签对应的34个物理位置；页码为最终补充 PDF 的页码，由 aux 与 PDF named destination 交叉核验。正文引用从稳定 label 生成，报告中的快照不作为源码硬编码。A-B两个标签合列。

- **A-A，第1页**：Compatible Target Measures。标签：`app:deferred_constructions`。
- **A-B，第1页**：Correction, Constraints, and Ideal Weights。标签：`app:ideal_factorization`, `app:correction_constraints`。
- **A-C，第1页**：Proof of Proposition 1。标签：`app:proof_prop1`。
- **A-D，第1页**：Proof of Proposition 2。标签：`app:proof_prop2`。
- **A-E，第2页**：Proof of Theorem 1。标签：`app:proof_theorem1`。
- **A-F，第2页**：Proof of Proposition 3。标签：`app:proof_prop3`。
- **A-G，第3页**：Proof of Proposition 4。标签：`app:proof_prop4`。
- **A-H，第3页**：Proof of the Target-Debt Accounting Bound。标签：`app:proof_debt_bound`。
- **B-A，第4页**：Target-Positive Coverage and Lookup。标签：`app:itar_lookup`。
- **B-C1，第4页**：Proof of Proposition 5。标签：`app:proof_pairwise_lcb`。
- **B-E，第4页**：Proof of Theorem 2。标签：`app:proof_agg_lcb`。
- **B-F，第5页**：Proof of Corollary 2。标签：`app:proof_false_safe`。
- **B-G，第5页**：Proof of Proposition 6。标签：`app:proof_drift_boundary`。
- **C-A，第5页**：City Scanner New York PM2.5。标签：`app:cityscanner_nyc`。
- **C-B，第5页**：City Scanner Pilot 2 with Measured Observation。标签：`app:cityscanner_p2_measured_o`。
- **C-C，第5页**：Windowed adaptations of FedAU, ObsUse, and TimeAlign。标签：`app:adapted_baselines`。
- **D-C，第6页**：NSW-Traffic Four-Region Protocol Ranking。标签：`app:traffic_four_region`。
- **D-D，第7页**：Balanced No-Harm Control。标签：`app:e1_balanced`。
- **D-F，第8页**：Response to Each Selection Layer。标签：`app:e2_layer_matrix`。
- **D-G，第8页**：Under-Served-Block Validation。标签：`app:underserved_block`。
- **D-H，第8页**：Intermittent Opportunity Protocol。标签：`app:int_r`。
- **E-A，第8页**：Local-Hájek Weight Cancellation。标签：`app:local_hajek`。
- **E-B，第9页**：Within-Stratum Observation Heterogeneity。标签：`app:f1_mechanism`。
- **E-D，第10页**：Numerical Feasibility of P2。标签：`app:p2_diagnostics`。
- **E-E，第10页**：Projection-with-Debt Sensitivity。标签：`app:kappa_probe`。
- **F-A，第10页**：Instantaneous Arrival-Support Geometry。标签：`app:arrival_support`。
- **F-B，第11页**：City Scanner Target Maps and Zero-Mass Handling。标签：`app:cityscanner_sixarm`。
- **F-D，第12页**：Support and Stabilization Conditions。标签：`app:a5_a6_audit`。
- **F-E，第12页**：Reference and Prediction Sensitivity。标签：`app:reference_sensitivity`。
- **F-F，第12页**：Target-Concentration Sensitivity。标签：`app:target_concentration`。
- **H-A，第13页**：Centralized Learning Capacity and Baselines。标签：`app:learning_capacity`。
- **H-B，第13页**：Formal-Protocol Prediction References。标签：`app:formal_prediction_references`。
- **H-C，第13页**：Update-Rule Sensitivity。标签：`app:update_rule_sensitivity`。
- **H-D，第14页**：Development Constraint Geometry。标签：`app:development_geometry`。

## 4. 链接核验与阅读器边界

结构核验逐一解析所有书签的页面对象、全部正文附录目标的完整层级/目标标题/页码，以及所有链接注释的精确目的地：

- 正文130个内部链接、58个跨 PDF 链接；补充76个内部链接、60个跨 PDF 链接。内部共206个、跨文件共118个，均能在 PDF 结构中解析到目标。
- 跨文件 `/F` 只使用 `main.pdf` 或 `supplemental.pdf`；`/D` 指向具体小节、公式、定理或表格的 named destination，不是对方首页。没有写死 C:/ 路径。
- 将两份 PDF 复制到独立目录后，按相对文件名重新解析118个目的地，全部存在。该测试验证文件结构可搬移，**不等同阅读器已实际执行跳转**。
- Reading guide 的层级、页码、内部目标及各级书签均检查目标位置；重点 E-D/E-E、D-D/D-F、F-D/F-E、H-A/B/C 和主要证明锚点也包含在完整35目标核验中。
- 已启用 hidelinks，打印无彩色框。未定义引用、重复 label、重复 destination、PDF字符串数学警告均未出现。

**实际阅读器验证：未完成。** 尝试连接当前 Microsoft Edge 阅读器时，Computer Use 返回：`Computer Use has been stopped for this turn because it could not determine the current browser URL on Windows with enough confidence to enforce policy.` 已立即停止界面操作，未绕过该限制。因此本轮没有成功实点内部链接或跨 PDF 链接，不能声称某一阅读器已通过，亦不宣称所有浏览器/投稿系统支持 GoToR。其余编译及结构核验独立完成。清楚的正文层级、自动页码和完整内部书签仍可用于人工定位。

## 5. 编译、页面与内容保全核验

- 顺序执行正文 LaTeX、补充 LaTeX、两份 BibTeX，再交替编译两轮；最后一轮 aux 稳定，全部8条命令退出码0。编译日志和命令记录见下面证据目录。
- 本轮补齐现有 MiKTeX 缺失的5个小型依赖：pdfescape、hycolor、refcount、gettitlestring、uniquecounter；未执行全局更新或更换模板。
- 最终日志无 Overfull、Missing character、LaTeX Font Warning、未定义引用/文献、重复 label/destination 或 PDF-string token 警告。原有 epstopdf shell escape disabled 提示不影响本轮现成 PDF 图的编译。
- pdffonts 核验两份 PDF 字体均嵌入，无 Type 3 字体。保留此前图形及字体修复。
- 已渲染最终全部28页，逐页联系图检查阅读顺序、图表/标题边界、导引换行和空白；另检查首页导引及正文理论页的全页预览。未观察到新增裁切、重叠、异常空白或链接框遮挡。此项是静态渲染检查，不代替阅读器点击。
- 所有原有 label 的编号值与备份 aux 逐一一致；页码允许随导航排版变化。35个正文 app 目标集合不变，A—H结构不变。
- 三份源文件的全部表格、equation/align、algorithm/algorithmic环境及引用键序列比较通过；32个表格内容保留。附录修改以 label 包装和PDF标题文字替代为主；正文只改导航措辞，压短了重复的“完整证明见”引导句。实验数字、理论条件、算法及图形文件未修改。

## 6. 修改文件、证据与回退

规范修改文件：

- [main.tex](../TO_OVERLEAF_paper_tmc_r1_clean/main.tex)：导航设置、正文附录引用及简短引导语。
- [supplemental.tex](../TO_OVERLEAF_paper_tmc_r1_clean/supplemental.tex)：同一链接设置与紧凑 Reading guide。
- [appendix.tex](../TO_OVERLEAF_paper_tmc_r1_clean/appendix.tex)：保留原标签并记录导航层级、PDF书签数学替代。
- [appendix-navigation.tex](../TO_OVERLEAF_paper_tmc_r1_clean/appendix-navigation.tex)：共享导航宏，新文件；随源文件共同交付。
- 两份规范 PDF 及正常编译产物已更新；未改 bibliography 内容、绘图脚本或图形素材。

回退包：[appendix_navigation_20261104_180447.zip](backups/appendix_navigation_20261104_180447.zip)。修改前已校验归档可读及条目与原文件一致；内含原始三份 TeX、两份 PDF、两份 aux 和恢复说明。旧备份未覆盖。

恢复方法：先将 ZIP 解到临时目录；没有后续修改时，可还原本轮三份 TeX 与两份 PDF，移除对新增导航文件的引用，并重新交替编译。有后续修改时，依据本轮 diff 仅逆向合并导航设置、app引用、Reading guide、label包装和两处PDF字符串替代，不用旧 main.tex 覆盖后续工作；新增导航文件在无引用后才可移除。aux应由对应源码重建，不能混用新旧 aux。保留回退包。

机器核验、逐文件前后差异、编译日志、字体清单及页面预览位于 [本轮证据目录](../tmp/appendix_navigation_20261104/)：`checks.json`、`baseline.json`、`citation_build_records.json`、`citation_build_status.json`、三份 `*.tex.diff`、`*_fonts.txt`、`renders/`。恢复前可用 diff 核对局部范围。候选试排截图和旧15页试排图不是交付PDF。

## 7. 尚未完成的验收项

实际阅读器中的内部链接与跨PDF链接实点仍待完成；当前仅通过精确目标结构检查及相对路径搬移检查。首选的 E-D 实页标题因15页重排而回退，最终使用正常模板标题、明确正文层级、重点纸面索引和完整书签。没有将上述两项写成完全通过，也没有因它们恢复实验或改动科学内容。
