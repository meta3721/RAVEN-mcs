# 正文短证明与附录入口整合

日期：2026-10-18。已修改规范`main.tex`并编译正文、补充PDF；最终均为14页。采用ccf-paper-writer修订、ccf-humanization语言检查及ccf-integrity-auditor条件/引用核对，没有新增实验。

## 逐项结果

| 理论项 | 正文实际位置 | 形式 | 正文论证 | 对应完整附录 |
| --- | --- | --- | --- | --- |
| 债务界(26)，`eq:debt_bound` | V-B，第5页右栏 | Proof sketch | 逐坐标累加控制累计欠配正部；零总质量使L1等于正部质量的两倍 | A-G，`app:proof_debt_bound`，补充第3页 |
| Proposition 1，`prop:risk` | VI-B，第6页右栏 | Proof | 在分布差的正坐标集合取指示函数，再以坐标指示函数得到逆向结论 | A-B，`app:proof_prop1`，补充第2页 |
| Proposition 2，`prop:reconstruction` | VI-C，第7页左栏 | Proof sketch | 顺序条件期望消去O/U，机会积分抵消比率分母，簇弱律及正分母给汇总比值极限 | A-C，`app:proof_prop2`，补充第2页 |
| Theorem 1，`thm:calibration` | VI-D，第7页左栏 | Proof | 当前cap/ESS下Uniform可行；紧致性、连续性和A4下正定Hessian给存在唯一 | A-D，`app:proof_theorem1`，补充第2页 |
| Proposition 3，`prop:practical_plugin` | VI-E，第7页左栏至右栏 | Proof sketch | 稳定化Lipschitz与正质量归一化控制估计误差，三角不等式加入稳定化误差；固定共享状态上的变分不等式、单调性和算子范数给后两界 | A-E，`app:proof_prop3`，补充第2页起 |
| Proposition 4，`prop:group_decomposition` | 第7页右栏 | Proof | 固定预测和群体内权重后，按组归并平方误差并代入组RMSE | A-F，`app:proof_prop4`，补充第3页 |
| Theorem 2，`thm:agg-lcb` | VI-F，第7页右栏 | Proof sketch | 条件交换性及独立连续破平局给均匀秩；秩事件蕴含分位点事件，分数代换及非负截断保留覆盖 | B-D，`app:proof_agg_lcb`，补充第4页 |

共3个完整短Proof、4个Proof sketch，均采用原有amsthm环境。每项末尾使用具体标签引用；未硬编码定理号或附录页号。债务界没有升级为新定理。Proposition 4的敏感性/排名指引由命题内移至证明末尾，数学陈述不变。

## 条件与结论保留

- 七项均完整读取对应附录后提炼；Proposition 3还核对附录A-H中固定状态的非扩张推导。
- 四个命题、两个定理和交换性假设的数学陈述、全部编号数学环境、算法、标签及结果表保持。命题4仅移出上述说明性附录指引。
- 保留固定预测器风险可以相等、A1—A3下理想汇总一致性、有限窗口不可实现、共享固定支持/M/可行域/其他状态、正质量、稳定化误差和债务次线性条件。
- 数值解审计入口保留在V-C，未将数学唯一性写成数值最优性认证。覆盖定理仍以交换性为假设，保留其不验证自适应切换的范围。
- 没有新增有限样本比值无偏、预测改进、任意漂移覆盖、日志A6b已核验或无条件长期对齐结论。本轮提炼未发现需要改变原命题才能完成的实质缺口。

## 篇幅与保护范围

首次完整加入短证明后正文为15页。通过精简证明措辞，并合并III-E的可行组成/更新尺度重复解释、IV的重建总览和参考衔接、V的代理/校准总览、VI的总览和范围重复说明，回到14页。没有改变字号、边距、行距或模板，也未删实验、移动结果表或增加附录篇幅。

同一语言工具近似口径下，新增证明约279词，全文净增约85词；约194词通过上述重复说明和指引归并抵消。此口径仅用于比较改动，不是净减少声明。

摘要、Introduction、Related Work及Evaluation至文末与本轮起点一致，保留City Scanner六臂正文表、标黄MD替换和已有评分修复。`appendix.tex`、`supplemental.tex`、书目及两份bbl未变；附录完整推导全部保留。

## 编译与页面验收

- 使用现有MiKTeX单进程顺序编译，最终正文→补充→正文→补充均成功，跨PDF引用稳定；书目未改，无需重新生成。
- 正文14页（含参考文献），补充14页；相对起点均未增加整页。补充逐页提取文本与起点一致。
- 七个具体证明入口均由aux核对为A-B/A-C/A-D/A-E/A-F/B-D及债务A-G，没有`Appendix ??`、重复标签、未定义引用、overfull或待重跑提示。
- 渲染查看正文第5—8页及第14页。七个证明段及各自单一结束方框清晰，未见公式、标题或算法遮挡、截断及异常空白。使用proof环境自动结束标记，没有手动追加qed。
- 语言检查无error/warning、新增破折号为0；分号密度仅为advisory，经人工核对用于紧凑论证。没有将内部执行记录写入正文。

新增训练、推理、重评分、回放、求解、统计检验均为0；仅作源码一致性、引用和编译检查。原实验暂停状态不变。

交付：[规范源码](C:/Cursor/raven.mcs/TO_OVERLEAF_paper_tmc_r1_clean/main.tex)、[正文PDF](C:/Cursor/raven.mcs/TO_OVERLEAF_paper_tmc_r1_clean/main.pdf)、[补充PDF](C:/Cursor/raven.mcs/TO_OVERLEAF_paper_tmc_r1_clean/supplemental.pdf)。
