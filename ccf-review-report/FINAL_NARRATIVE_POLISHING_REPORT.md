# 最终叙事打磨与验收报告

日期：2026-10-31。规范目录：`C:/Cursor/raven.mcs/TO_OVERLEAF_paper_tmc_r1_clean/`。

已实际修改 `main.tex` 与 `appendix.tex`，编译更新 `main.pdf`、`supplemental.pdf`。`supplemental.tex` 和 `reference.bib` 与备份逐字节一致。训练、推理、重评分、重放、调参和统计检验均未执行；已有实验与停止状态未改动。

已阅读本轮完整指令、当前两份论文和全部规范 TeX、导师 DOCX 四百一十段正文与四张截图、`raven-final-narrative-review.md`。截图只用于理解写作要求，未引入 CLOAK/CS 内容。采用 ccf-paper-writer 修改文字、ccf-humanization 检查表述、ccf-integrity-auditor 核对字段与条件、ccf-submission-checker 完成本地编译验收。

## 逐项执行结果

1. **已修改、字段已核对：触发比例。** `appendix.tex:1456–1478`、表XXV。改为 `q_min floor activation`、`d_max ceiling activation`；保留 5.22/5.18% 和 24.22/23.75%。依据 `results_prop3_audit/round_v1/compute_a5a6_eps_stab.py:161–182` 与 `A5A6_EPS_STAB.json` 的 `released_audit_recheck`：先筛选 `O=True`，分别统计 `q_use_true < Q_MIN` 和 `q_use_true < 1/D_MAX`。分母为12346/9760个 observed client-windows，不是全部记录或active P2窗口。本轮没有重新执行统计脚本。

2. **已修改；完整经验验证仍待核实：A5范围。** `appendix.tex:1483–1532`。去掉“A5 holds”及“Proposition 3 therefore applies”的无条件推断。正边际、共享支持/组成矩阵/可行集、正参考总质量分别陈述。额外发现：`tools/a5_a6_support_audit.py` 的质量计算使用 `n_obs / max(p,p_min)` 乘截断可用性因子，未包含机会Design因子；保存的 `artifacts/a5_a6_audit/audit_summary.csv` 中5.521/16.89因此不能当作完整Design-on参考的归一化质量下界。保留数值，将行名改为“Obs./use mass minimum”，并明确它省略机会校正。共享A/M/C及完整参考正质量仍是扰动比较条件；日志缺少active-set列表和估计边际，不声称验证全部A5或A6b。

3. **已修改：A6a充分性。** `appendix.tex:1433–1438`。A6a充分保证稳定化误差为零，但归一化可能抵消失真，故不是必要条件。正文命题3、附录重述与完整证明原已采用这一方向，保持原文；一般误差项、A6b、共享固定状态和正质量条件未删。

4. **已修改：实验与策略名称。** `appendix.tex:1440–1446,1718–1724,1936–1990`。直接给出站点实验实际常数p_min=q_min=.05、pi_min=10^-6、a_max=20、d_max=10，删除runner覆盖过程。六臂名称与主表统一；停止规则采用机制名称，保留全部五行及G/W/J、停止系数和P2债务。旧键映射见下。

5. **已修改：分析标题与对象。** `appendix.tex:845,966,1313,1430`，以及正文VII-E/F。以“Within-client weight constancy”“Numerical feasibility of warning-affected P2 allocations”“Design-Induced Support Changes”“Support and Stabilization Conditions”组织内容；Frozen result改为Result。774窗口改为paired analysis，3279窗口改为evaluated active windows；realized coverage在窗口完成后评价下界并更新诊断状态。正式数学对象和label保留。

6. **已修改：三个Design/Gate对象。** `main.tex:1752–1756`；`appendix.tex:1535–1588`。将旧候选命名为coverage-controlled Design variant，首次出现明确Design=Gate，与主方法预配置Design、诊断Gate分开。保留pooled CERTIFIED validity .959、U-Air a=1时.750，以及表XXVI全部n、n_cert、分母与其他结果。图7未重绘，图内为数据集、状态和坐标标签，不含旧候选身份；新图注明确变体。交换性条件和CERTIFIED操作状态的区别保留。

7. **已修改：内部裁决改为分析事实。** 删除“proposed directional event”的内部判定，六场景全表和风险方向解释保留。保留求解器最坏分配差.0056，删除无法据现有材料证明的全体“headlines不变”。`appendix.tex:992–999`补充现有残差：primal最大6.66×10^-16（容差10^-13），stationarity最大.667（容差10^-12），200个比较窗口中7个objective gap超过10^-12，最大9.64×10^-12；不写精确最优认证。依据 `results_w1_ladder/round_v5_1a/O_GATES_RERUN.json` 与 `EXECUTION_REPORT.md`，未重求解。保留最大结构端点差2.42×10^-5 Δ。774窗口说明共享R/O/U及注册事件，差异来自正质量支持，不再叙述hash或leakage排查。

8. **已修改：集中边界。** 引言将支持边界融入可达组成；A1–A3和IV-D集中保留理想识别与稳定化区别。统计设置区分描述性+.5%容差、Wilcoxon/Holm和六臂2%非劣门槛。结果仍给3.83/4.14/8.15%单侧上界、非劣门槛未满足及后续superiority未测试，保留[-1.89%,+12.28%]、p=.922的不确定性。NSW直接说明本地四区域目标。结论聚焦参考到可执行混合、固定状态分析、次线性债务条件与City Scanner组对齐，不重复实验中已有预测排名提醒。

9. **已修改可核实部分；模型保存时点待核实。** `main.tex:1218–1221,1501`。用统一saved-parameter TEST评分口径替代“terminal-window correction”。只读确认 `scripts/w1_v51_a2.py` 对六臂分别加载各自保存参数，使用相同TEST目标权重直接评分；`results_w1_ladder/round_v5_1/ERRATA_FOR_PAPER.md`、`A2P_RESCORE.csv`、`TRADEOFF_V51.csv`、`A2P_G0B_TRIGGER.csv`说明U-Air 30007/30016/30018六臂共18行末记录窗口为空，其余222行与既有分数一致到既定精度。现存 `src/raven_mcs/e3/real_runner/runner.py` 为0字节，`scripts/run_h_headroom.py` 为2字节，无法复核原训练后端checkpoint写入时点与完整调用链。当前window_runner空窗口不更新模型，但不能代替历史后端证明。论文没有声称已查明最后/最佳/平均checkpoint保存规则；本项不标为完整解决。本轮未加载模型、重新预测或修改评分代码。

10. **已修改：摘要顺序和篇幅。** `main.tex:71–73`。一个段落八句，依次为背景、问题、已有研究、提出方法、两句机制、理论、实验。169→169词。理论保留正确比率、兼容支持、顺序识别、簇正则及固定状态/强凸范围；实验句明确真实机会、受控交付及受控/实测观测，25.8/23.3%均为相对TwoStage-Hájek的组失配seed-mean比值降低。没有改成RMSE或百分点。

11. **已修改并保留已有结构：引言。** `main.tex:89,102`。把并列研究方向的Although改为Asynchronous… and participation…。支持边界改为当前感知支持上的可达组成。481→481词，前三段仍157词，占32.6%；引用数仍5/6/6，键和顺序未改。第四部分指定首句、理论一句、实验概括一句、三项首词为We的编号贡献均保留。无图表编号引用。

12. **已修改可核实材料描述；完整复现与访问机制待核实。** `main.tex:1771–1777`。保留公开数据、Zenodo/CC BY4.0、T-Drive条款原引用；改为本地作者材料的实际范围，不承诺公开完整包或available upon request。核对到非空配置、target maps、EventTrace索引/文件、`cityscanner/CS_E3_SUMMARY.csv`（601字节）、`cityscanner_p2/JO_E3_SUMMARY.csv`（646字节）及`submission_evidence/W1_TRADEOFF_V51.csv`（54413字节）。但 `RAVEN_MCS_PUBLIC_REPRO_R1/README.md` 和 `BUNDLE_SUMMARY.json` 均为空，manifest对应的summary大小与当前文件不符；`PROTOCOL.json`仍描述旧support-conditional Design身份，不能充作当前完整configured-Design方法复现规格。未发现可确认的本轮授权公开地址，未发布/上传任何材料。

13. **已修改：引用、重复词和显示精度。** `main.tex:306`将预配置Design指向实际窗口更新节`subsec:global_update`；Gate仍指向诊断节。去除balanced Balanced。`appendix.tex:1955–1956`用近似号显示c_ref≈.916837、ell≈.906977、age≈.492992；精确执行值仍保留在 `results_of_v1_small_scope_20261018_190539/FREEZE.json` 的c_ref/reference_ell/reference_age及A/B结果中，没有修改配置。所有编号公式和标签保持。

14. **已检查、定点清理：上下文回归。** 内部候选历史、provenance audit、Frozen result、runner与过程修补叙述已清理。保留合法历史、预固定状态、formal development protocol和数学不可达性。剩余cannot用于不同测度不可替换、同支持对照不能由改变支持的比较识别、以及不可达性证明；CERTIFIED不证明交换性的说明承担理论范围限定。非修改式prose checker结果：0个em dash，无套话或夸张词提示；两组等长句提示分别来自集合/映射定义、统计说明及图注，人工检查后保留；分号密度提示包含数学与表格分隔，不为清零改写公式。

15. **已符合：关键事实保护。** 两个City Scanner协议与25.8/23.3%组失配口径、十条trace×三model seeds、六臂全部结果与非劣区间、投影/完整P2的组与client–stratum差别和运行时间、U-Air支持变化与排序翻转、独立κ=1000规则、理想/稳定/长期条件、Gate职责与SD/CI单位均保留。自动比对所有表格数值单元一致；仅明确有误的行名更正。正文36、附录27个编号equation/align块逐段一致；全部Proof、algorithmic、定理/命题/推论/重述环境逐段一致。未重绘或改写图片引用。

16. **已完成本地验收；不等于科学缺口全部闭合。** 使用现有MiKTeX低优先级单进程顺序运行pdflatex与BibTeX，交替编译到两份aux稳定。最终正文14页、补充14页；修改前亦14/14，无完整页数减少。两份最终日志无undefined references/citations、重复label、缺字、缺图、Overfull或编译错误。全部28页已渲染检查，表XXV/停止规则表另放大检查；最后访问状态措辞校正后重新编译并检查受影响的正文13–14页。图1仍位于第三节、PDF第3页；表引用均从Evaluation开始；引用保留nocompress逐项显示；未恢复Proof sketch，结束方框保留。标签数正文103、附录111均不变，引用命令及顺序不变。

## 正式名称与旧键

- `fedavg_window` → FedAvg（六臂表显示FedAvg / count）。
- `raven_wo_design` → RAVEN-NoDesign。
- `raven_ctrl` → RAVEN-control。
- `raven_ctrl_floor` → RAVEN-floor。
- `raven_M1mu` / `raven_M2mu` → RAVEN-M1μ / RAVEN-M2μ。
- `OF-v1` → Rolling + stop debt（滚动参考，κ_stop=.1）。
- `OF-no-Q-stop` → Rolling reference（滚动参考，κ_stop=0）。
- `GAP20-fixed-reference` / `GAP20` → Fixed reference（t=20固定参考，κ_stop=0）。

后三种均保留P2目标债务Q及其更新；“无停止债务项”不等于无P2债务。代码键、配置和结果文件未更名。

## 未闭合事项及边界

- 完整Design-on参考的窗口质量下界：现有5.521/16.89属于省略机会因子的统计量，不能代替；本轮仅修正对象，未重算。
- 共享A/M/C和A6b：存储状态与估计边际不足，仍为比较条件，不能由正边际推出。
- checkpoint保存时点：原后端源文件为空，已核实评分读取但未核实历史保存顺序。
- 当前方法的完整复现包：空文件、陈旧protocol、材料覆盖与访问状态尚不闭合。已有材料不据此全部失效，也不据此声称完整复现。
- 这些问题不以新增实验、重评分或虚构定义解决。本轮保留实验暂停状态。

## 回退

完整修改前归档：`C:/Cursor/raven.mcs/ccf-review-report/backups/final_narrative_20261031_090533.zip`。归档已检查可读并逐字节核对，包含原main.tex、appendix.tex、supplemental.tex、reference.bib、两份PDF以及当时aux/bbl/log；不覆盖旧备份。

若规范稿自本轮结束后没有其他改动，只从归档恢复`main.tex`和`appendix.tex`；可同时恢复原main.pdf/supplemental.pdf，或按现有工具链重编译。不要恢复未修改的BibTeX、supplemental.tex或整目录。若后续已有其他修改，先解压至临时目录，根据差异报告及`tmp/final_narrative_20261031/main.tex.diff`、`appendix.tex.diff`逐块逆向合并，仅撤回本轮修改，禁止用旧main.tex覆盖后续工作。

审查证据和编译记录：`C:/Cursor/raven.mcs/tmp/final_narrative_20261031/`，含baseline、checks、protected_checks、prose_quality、changes和逐次编译输出；这里不是实验结果目录。修改前后代表性句子见同目录外的`ccf-review-report/FINAL_NARRATIVE_POLISHING_DIFF.md`。
