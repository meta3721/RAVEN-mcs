# 论文—实验利用情况审计

日期：2026-10-15。模式：ccf-integrity-auditor／claim-audit，聚焦已有结果在当前稿中的使用程度；不是新一轮全文科学评分或引用真实性核验。

## 核心结论

确有一批已完成结果未进入论文，另一些只被压缩成一句话。最值得优先整理的是：Traffic目标集中度梯度、外生人口/311目标评分、漂移场景、200遍学习能力与新几何诊断，以及F-1与W1的完整证据展示。它们主要补强适用边界、机制归因和研究可信度；不能因此改称已有RAVEN预测领先证据。

审计基准：[main.pdf](C:/Cursor/raven.mcs/TO_OVERLEAF_paper_tmc_r1_clean/main.pdf)（18页）、[supplemental.pdf](C:/Cursor/raven.mcs/TO_OVERLEAF_paper_tmc_r1_clean/supplemental.pdf)（16页），并对照main.tex、appendix.tex、supplemental.tex。采用你此前指定且近期更新的clean版（2026-10-12）；名称为final的另一目录仍是8月版本，未拿它当当前稿。10月12日下午至15日的新实验晚于本次PDF编译，未纳入有时间原因。

目录清点包含56个results根目录、35个artifacts一级实验/修复目录，另检查outputs、现有公开bundle与报告索引；本报告详细评价20组证据。目录清点不等于每个历史二进制/每行日志已重验。本轮通读正文及补充材料全部页面，只读取必要报告和小型指标，不加载训练模型、不执行训练/回放/凸求解/压力测试、不改论文和原始结果。

## 判定口径

- 未系统纳入：相应完整结果未出现，或仅吸收相关概念而没有报告该结果矩阵。
- 已写但压缩：核心数字已有，但实验条件、对照设计或结果关系被压缩，适合用已有数据展开。
- 独立或待修复：有资产，但方法身份、历史范围或复现问题阻止其直接并入主表。
- 已覆盖：补充材料也属于论文；不能将已有完整附录表误算成未利用。

不按目录数计算独立实验数。复评分、重复修复、共享模型、同一运行跨阶段汇总均不重复算训练；成功保存终点也不自动意味着通过了全部出版证据核验。

## 一、尚未系统纳入的结果


### A01 NSW-Traffic部署目标集中度梯度

**规模与完成程度：**Step 3为4臂×20种子=80条；Step 4为2臂×2新集中度×20种子=80条。κ=1基准复用已有运行，不另计新实验。

**已有结果：**目标由近均匀到单区域，oracle相对control的RMSE改善依次约0.0013%、0.0225%、0.0454%、0.0970%；单区域绝对差区间[0.000685,0.001337]，换成相对control量级约[0.067%,0.130%]。后两级有可检测差异，幅度仍小。

**当前稿体现：**正文VII-F/VII-G讨论目标稀释与headroom，却没有报告该集中度梯度；全文无single-region或0.097结果。附录也无对应表。

**可如何利用：**优先补一个“目标集中度—可检测预测增益”小表/曲线，服务于权重类的适用边界，解释即使目标集中、可行域有自由度，预测增益仍有限。

**适用限制：**不是RAVEN领先结果，也不是所有可行权重的严格最优上界。oracle是已评估的真概率配置；结论限于该骨干、原服务器更新和声明的目标。此处κ为目标集中度，非OF停止系数。

证据：[TE2_REPORT.md](C:/Cursor/raven.mcs/results_traffic_e2/round_v1/TE2_REPORT.md)；[TE2_STEP4_VERDICT.json](C:/Cursor/raven.mcs/results_traffic_e2/round_v1/TE2_STEP4_VERDICT.json)；[TE2_MAIN.csv](C:/Cursor/raven.mcs/results_traffic_e2/round_v1/tables/TE2_MAIN.csv)；[TE2_STEP4_MAIN.csv](C:/Cursor/raven.mcs/results_traffic_e2/round_v1/tables/TE2_STEP4_MAIN.csv)。


### A02 人口与311需求构成的外生部署目标

**规模与完成程度：**2张外生图（ACS人口、NYC 311）+原评估派生图；50个固定checkpoint，各按三套权重重评分；无新训练。

**已有结果：**三套权重下五方法均值排序一致，RMSE移动不超过约0.21%；原键级ρ_delivered约14.35%，人口/311图约1.00%/0.98%。区域级零检查与键级零检查并非同一对象。

**当前稿体现：**正文VII-E(b)及附录J已吸收“目标查找对象不同”的限定；没有系统呈现ACS/311来源、三图端点重评分与排序稳定性。

**可如何利用：**可补“公共目标来源敏感性”表，给出外生需求与评估组成的区分；使用固定预测的重新加权结果支持评分敏感性讨论。

**适用限制：**不能声称在外生目标下重新训练成功。后续endpoint-screen另一路径出现City Scanner重评分不一致，引用前须确认这50个权威checkpoint及正确loader；不能忽略争议或把两种ρ分母混合。当前论文对查找对象的限定已部分修复，旧报告首段“门不一致”不应不加区分照搬。

证据：[EXECUTION_REPORT.md](C:/Cursor/raven.mcs/results_exogenous_target/round_v1/EXECUTION_REPORT.md)；[ENDPOINT_TABLE.csv](C:/Cursor/raven.mcs/results_exogenous_target/round_v1/ENDPOINT_TABLE.csv)；[MAP_SUMMARY.csv](C:/Cursor/raven.mcs/results_exogenous_target/round_v1/MAP_SUMMARY.csv)；[EXECUTION_REPORT.md](C:/Cursor/raven.mcs/results_endpoint_screen/round_v1/EXECUTION_REPORT.md)。


### A03 机会过程漂移的完整五方法对比

**规模与完成程度：**2数据集×5方法×20种子=200个final_metrics，200个对应final checkpoint均存在；另有现成summary/holm文件。

**已有结果：**drift_period=50、drift_magnitude=.1。SensorScope的RAVEN Δgroup约1.0331，FedAU约1.0889；U-Air的RAVEN Δc-s约1.2291，FedAU约1.3303。原汇总显示结构对比3/4有利，U-Air预测仍显著落后于FedAU。

**当前稿体现：**正文与补充材料没有该漂移实验表。理论中的任意漂移不可能性边界、RESET压力审计、INT-R均不是这200条运行的替代。

**可如何利用：**可加入专门的漂移鲁棒性小表：同时展示结构收益和U-Air预测代价，使“随时间变化的机会”有实证对应。

**适用限制：**200个保存终点存在不等于本次已重新认证全部运行；沿用其冻结旧版本，核对Design和终点评分身份。不把有限构造漂移说成任意漂移保证；有限Q/S亦不证明债务次线性。

证据：[run_ledger.json](C:/Cursor/raven.mcs/artifacts/e3_drifting_r1/run_ledger.json)；[trace_ledger.json](C:/Cursor/raven.mcs/artifacts/e3_drifting_r1/trace_ledger.json)；[conclusion.txt](C:/Cursor/raven.mcs/_paper_work/drifting_window_results/conclusion.txt)；[summary.csv](C:/Cursor/raven.mcs/_paper_work/drifting_window_results/summary.csv)；[holm.csv](C:/Cursor/raven.mcs/_paper_work/drifting_window_results/holm.csv)。


### A04 200遍训练的学习能力与简单基线

**规模与完成程度：**112条真实训练：108条Central-delivered、1条Traffic均匀联邦、3条U-Air Central-all；每条达到200有效遍历。

**已有结果：**Common-NDMF验证集相对最强适用简单基线：Traffic +47.01%、SensorScope +10.16%、U-Air −0.96%；历史残差升级未解决U-Air。Traffic单条Uniform改善33.70%，但100→200仍改善0.914%，未达预算平台。

**当前稿体现：**正文VII-F/G讨论旧短预算学习弱与两个常数参考；没有这些200遍曲线、强简单基线、物理单位验证结果。

**可如何利用：**可单列新的学习能力审计/附录，展示训练与验证曲线、简单基线、平台与失败数据集；帮助区分骨干能力、训练协议和聚合收益。

**适用限制：**全部是新重建协议的开发验证结果，不是旧表III测试成绩，也不是RAVEN收益。不能用47.01%替换摘要算法收益或混入旧测试表。R2 CSV才是权威；旧seasonal-naive/float32汇总已被修正。

证据：[EXECUTION_REPORT.md](C:/Cursor/raven.mcs/results_main_rebuild_r1/EXECUTION_REPORT.md)；[P1_CENTRAL_SELECTED_R2.csv](C:/Cursor/raven.mcs/results_main_rebuild_r1/P1_CENTRAL_SELECTED_R2.csv)；[P0_VALIDATION_BASELINES_R2.csv](C:/Cursor/raven.mcs/results_main_rebuild_r1/P0_VALIDATION_BASELINES_R2.csv)；[P1_SELECTED_TRAIN_VALIDATION_CURVES_R2.csv](C:/Cursor/raven.mcs/results_main_rebuild_r1/P1_SELECTED_TRAIN_VALIDATION_CURVES_R2.csv)；[EXECUTION_QA.json](C:/Cursor/raven.mcs/results_main_rebuild_r1/EXECUTION_QA.json)。


### A05 K/ESS/cap与实际可调组质量的几何诊断

**规模与完成程度：**同一重建批次9条开发轨迹及多组K/ESS/cap诊断；与A04共用实验资产，不能重复计入训练总数。

**已有结果：**新自然轨迹单点可行域比例：SensorScope80.57%、U-Air82.46%、Traffic4.33%。Traffic有183个K=8且rank≥1的筛选窗口，但平均可调整目标质量约4.65%；参考违反约束59.02%，纯投影L2修复距离均值约.067487。

**当前稿体现：**正文VII-F已有旧种子的K≤3比例和稀释解释；没有这批新K/ESS/cap、rank、逐组min/max与可调质量证据。

**可如何利用：**可将“客户端数足够”进一步分解为“权重有自由度、组成有自由度、可调目标质量足够”，补一组几何图支撑可实现性主题。

**适用限制：**无标签几何诊断不是训练性能实验。K截取不是新的受控参与调度；不能据183窗口推出预测收益。旧Gate/Design接线身份另列，不能把其开启比例当作修复后方法证据。

证据：[EXECUTION_REPORT.md](C:/Cursor/raven.mcs/results_main_rebuild_r1/EXECUTION_REPORT.md)；[P2_GEOMETRY_AUDIT.json](C:/Cursor/raven.mcs/results_main_rebuild_r1/P2_GEOMETRY_AUDIT.json)；[P2_GEOMETRY_SUMMARY.csv](C:/Cursor/raven.mcs/results_main_rebuild_r1/P2_GEOMETRY_SUMMARY.csv)；[P2_GEOMETRY_WINDOWS.csv](C:/Cursor/raven.mcs/results_main_rebuild_r1/P2_GEOMETRY_WINDOWS.csv)；[P2_GEOMETRY_GROUP_RANGES.csv](C:/Cursor/raven.mcs/results_main_rebuild_r1/P2_GEOMETRY_GROUP_RANGES.csv)。


### A06 E2六场景的完整风险语义矩阵

**规模与完成程度：**6场景×5方法×20种子=600条formal_results：balanced、R-only、O-only、U-only、complete-aligned、complete-counteracting。

**已有结果：**当前稿突出complete-aligned的风险不互换；其余单层干预和counteracting的风险响应没有系统展示。最终claim矩阵明确：一些场景改变arrival risk，但不支持所有场景均恶化target risk、counteracting方向事件或RAVEN统一领先。

**当前稿体现：**正文Fig.2/附录表VI为complete-aligned；附录表XVI对六场景仅汇总runtime，不能算科学结果矩阵已充分利用。

**可如何利用：**可从已封存修正统计中整理“选择层×风险变化”的简表，直接回答R/O/U分别改变了什么，避免动机只靠一个同向场景。

**适用限制：**使用numerical-tolerance最终修订统计；signed Gap_mis不能当绝对失配程度。该数据不提供RAVEN预测或公平性领先证据。

证据：[formal_results.csv](C:/Cursor/raven.mcs/artifacts/e2_traffic_formal_runs_r1/formal_results.csv)；[E2_CLAIM_MATRIX_FINAL.md](C:/Cursor/raven.mcs/artifacts/e2_traffic_numerical_tolerance_and_final_claim_seal_r1/E2_CLAIM_MATRIX_FINAL.md)；[TABLE_E2_2_FINAL.csv](C:/Cursor/raven.mcs/artifacts/e2_traffic_numerical_tolerance_and_final_claim_seal_r1/paper_tables/TABLE_E2_2_FINAL.csv)。


### A07 U-Air活跃支持A/B的跨条件机制与告警代价

**规模与完成程度：**6条件×2规则家族×20种子=240个成对比较单元；主要复用H轮运行，不把240对误称新增240次训练。另有12组决策端点重评分。

**已有结果：**扩大支持的B方案在预测/组端点改善约5%—9%，同时Δc-s恶化约3.1%—4.8%，240/240对同方向。告警误差降低主要来自压掉假阳性，超标质量保留率下降到约0%—2.48%，不是更好的检测。

**当前稿体现：**正文已报告U-Air Design-off取舍及774窗口溯源；未展示六条件、两家族支持干预，也没有对应告警TP/FP/FN证据。

**可如何利用：**作为支持变化机制的补充表或应用边界：解释RMSE改善为何不自动等于告警效用改善。

**适用限制：**规则家族并非当前RAVEN同一行；必须标明实际A/B语义。P2D含终窗inactive导致的重评分豁免和敏感性分析，需保留。协议equivalent_zero标签较粗，不能拿它抹去实测差异，也不能事后换带宽。

证据：[P0_REPORT.md](C:/Cursor/raven.mcs/results_regime_b_endpoints/round_v1/P0_REPORT.md)；[P1_REPORT.md](C:/Cursor/raven.mcs/results_regime_b_endpoints/round_v1/P1_REPORT.md)；[P2D_REPORT.md](C:/Cursor/raven.mcs/results_regime_b_endpoints/round_v1/P2D_REPORT.md)；[EXECUTION_REPORT.md](C:/Cursor/raven.mcs/results_h_headroom/round_v3/EXECUTION_REPORT.md)。


### A08 部署总量误差与结构失配的直接联系

**规模与完成程度：**200次已有组成重建、40个闭式总量匹配floor；无神经训练，不使用预测ŷ。

**已有结果：**SensorScope上结构差与标签总量误差的斜率约+.366，区间[.266,.472]；U-Air区间跨0。两数据集总量floor均为0；预注册aggregate_path因此仍closed。

**当前稿体现：**正文讨论结构指标与预测敏感性；没有E=|(ω̄−μ)·m|这一标签总量端点的完整结果。

**可如何利用：**可作为结构指标能否关联另一任务量的条件性诊断，说明只在SensorScope观察到联系。

**适用限制：**m取测试组标签均值，仅离线分析，不能进入控制器；E不含ŷ，不是补全预测误差。先前两个错误floor已撤回，只能用最终闭式版本。不能称跨数据集任务收益成立。

证据：[EXECUTION_REPORT.md](C:/Cursor/raven.mcs/results_aggregate_total/round_v1/EXECUTION_REPORT.md)；[TOTAL_DOSE.csv](C:/Cursor/raven.mcs/results_aggregate_total/round_v1/TOTAL_DOSE.csv)；[TOTAL_DECISION.json](C:/Cursor/raven.mcs/results_aggregate_total/round_v1/TOTAL_DECISION.json)。


## 二、已有文字但值得展开


### C01 层内异质观测概率F-1试验

**规模与完成程度：**2种观测构造×2概率配置×2数据集×20种子=160个新保存终点。

**已有结果：**保持块均值的θO=1构造将每stratum的不同p值由1提升到约2.8个；oracle-p相对估计p的预测差为SensorScope +.104%、U-Air −.251%，总体幅度未达.5%。

**当前稿体现：**正文VII-F只有“15—21倍、.104%/.251%”一句；无独立表，没有完整区分θO=0/1、oracle-p仅改p及U-Air为Design-on的身份。

**可如何利用：**一张小表即可说明：原观测机制过于简单是否隐藏聚合增益，以及硬化选择为何仍未建立实质预测收益。

**适用限制：**不能把U-Air负号删去或称oracle普遍更好；不是无偏性保证，也不是真实MNAR实测。原汇总的部分旧Design措辞已过时，引用时以当前配置定义为准。

证据：[raven-mcs-f1-experiment-summary.md](C:/Cursor/raven.mcs/ccfa-review-reports/raven-mcs-f1-experiment-summary.md)；[f1_run_status.jsonl](C:/Cursor/raven.mcs/artifacts/e3_f1_score_dependent_r1/f1_run_status.jsonl)；[f1_run_status.jsonl](C:/Cursor/raven.mcs/artifacts/e3_f1_theta1_r1/f1_run_status.jsonl)。


### C02 实际训练的服务器权重规则与W1前沿

**规模与完成程度：**论文已声明240条规则运行；另有离线同支持ladder/frontier/分解，不能把这些重建全部当新训练。

**已有结果：**有uniform、投影、投影加债务等完整训练规则；SensorScope投影较uniform改善组质量+.768pp，而预测对比Holm后不显著。κ=1000为单独敏感性，不是标准配置。

**当前稿体现：**正文VII-C/VII-E已有大量定量文字，补充K有κ=1000及εimpl；但主表III没有Uniform/Projection行，没有清晰的结构—预测—时间联合展示。

**可如何利用：**优先整理现有规则的比较表或二维结构/预测图，让校正、约束投影、债务强度各自作用一眼可见。

**适用限制：**此类证据已进入摘要和贡献，不能称完全未利用。W1各轮有修订/近似oracle判定，勿回收失败的“exact”声明或混用不同active-set标尺。

证据：[PART_B_REPORT.md](C:/Cursor/raven.mcs/results_w1_ladder/round_v4/PART_B_REPORT.md)；[EXECUTION_REPORT.md](C:/Cursor/raven.mcs/results_w1_ladder/round_v5_1/EXECUTION_REPORT.md)；[EXECUTION_REPORT.md](C:/Cursor/raven.mcs/results_w1_ladder/round_v5_1a/EXECUTION_REPORT.md)；[PAPER_NUMBERS.csv](C:/Cursor/raven.mcs/RAVEN_MCS_PUBLIC_REPRO_R1/w1/PAPER_NUMBERS.csv)。


### C03 训练更新、参数位移与Adam替换诊断链

**规模与完成程度：**旧checkpoint位移审计、Traffic局部2/5/10/20步、服务器优化器筛选、15种子两臂确认及结构只读读出。

**已有结果：**旧参数位移约.26%—.40%；单纯多本地步效果有限。Adam确认的oracle预测headroom −1.49%，区间[−5.42%,1.76%]，MDE约5.80%；同批结构差可分离。

**当前稿体现：**正文VII-G已有数段文字和全部关键数字，缺少贯穿“本地预算—更新归一化—服务器更新—预测/结构”关系的表或曲线。

**可如何利用：**作为学习协议诊断图，帮助解释结构改变但预测不变；同A04的200遍训练独立标识。

**适用限制：**Adam仍未证明oracle预测领先，也不能把宽区间当成.5%效果已排除。短步中央参考与联邦的优化器/样本预算不完全相同。

证据：[S1_REPORT.md](C:/Cursor/raven.mcs/results_new_block_traffic/round_v1/S1_REPORT.md)；[S1P_REPORT.md](C:/Cursor/raven.mcs/results_server_optimizer/round_v1/S1P_REPORT.md)；[TE1_REPORT.md](C:/Cursor/raven.mcs/results_traffic_e1/round_v1/TE1_REPORT.md)；[TS1_REPORT.md](C:/Cursor/raven.mcs/results_traffic_struct/round_v1/TS1_REPORT.md)。


### C04 零目标支持比例ρ的剂量反应

**规模与完成程度：**v2已完成多剂量Design on/off对比；v1只做准备后停止，不能重复计为已执行同一实验。

**已有结果：**SensorScope的ρ可增至.388而预测代价仍不足.175%；U-Air的ρ约.354—.466时代价约6.6%—7.5%。主剂量斜率区间跨0，gate_law不支持。

**当前稿体现：**正文VII-G以一小段吸收结论；没有跨剂量的预测/结构并列图，附录也没有完整剂量表。

**可如何利用：**可作适用性图，明确零支持检查不能当预测代价大小的经验定律。

**适用限制：**不包装成成功门控策略；保留G3授权修订和敏感性，不能回收未通过H1后不应报告的ρ*。

证据：[PART_II_REPORT.md](C:/Cursor/raven.mcs/results_gate_dose/round_v2/PART_II_REPORT.md)；[DOSE_SUMMARY.csv](C:/Cursor/raven.mcs/results_gate_dose/round_v2/tables/DOSE_SUMMARY.csv)；[STOPPED.md](C:/Cursor/raven.mcs/results_gate_dose/round_v1/STOPPED.md)。


## 三、独立分支或需先解决适用问题


### B01 City Scanner Pilot2 NO₂实测观测对比

**规模与完成程度：**5方法×10种子=50条；不同于稿内PM₂.₅实测O的50条。

**已有结果：**RAVEN RMSE约.9597、WG约1.0837，TwoStage-Hajek约.9602/1.0862；FedAU约.9555/1.0693，更好。通过的是预定“至少一个端点胜Hajek”条件，不是最强方法领先。

**当前稿体现：**正文和附录没有NO₂预测目标结果；稿内NO₂只用于PM₂.₅任务的GPS并集，不能算NO₂结果已报告。

**可如何利用：**保留为跨污染物候选或独立补充资产，可解释与PM₂.₅结论的差异。

**适用限制：**多份历史handoff明确“不摄入PATH_A NO2”；本轮审计不解除该边界。纳入前需核验污染物物理尺度、冻结目标和授权范围；不能改名并入PM₂.₅表。U仍为受控，非全实测R/O/U。

证据：[PATH_A_HAJEK_REPORT.md](C:/Cursor/raven.mcs/results_path_a_hajek/round_v1/PATH_A_HAJEK_REPORT.md)；[PA_E3_SUMMARY.csv](C:/Cursor/raven.mcs/results_path_a_hajek/round_v1/tables/PA_E3_SUMMARY.csv)；[DATA_GAP.md](C:/Cursor/raven.mcs/post_review/PATH_A_HAJEK/DATA_GAP.md)；[next-ai-handoff.md](C:/Cursor/raven.mcs/ccfa-review-reports/next-ai-handoff.md)。


### B02 可达性／OF新分支及完整自主负结果

**规模与完成程度：**10月12—15日新方法分支；含完整45011成本采集和45001四臂自主T100，以及旧reachability/44001前缀和诊断。

**已有结果：**OF对fixed.5的G改善1.42%但W增加18.80%；对fixed2等待缩短但质量保护失败；OF与no-Q-stop的最终G/W及关闭序列相同。当前状态为单种子效用未建立。

**当前稿体现：**论文PDF/正文截止10月12日中午，未出现OF/B触发式、45011、45001或新四臂结果。

**可如何利用：**适合独立研究记录、方法演进与未成功扩展说明；可提炼未来研究限制，不作为旧RAVEN正文的新增收益证据。

**适用限制：**控制目标、事件语义和诊断q身份与原论文不同；不是原五组件消融。工程检查、SGD0和前缀不能计作完整比较，q=.5不构成校准概率。

证据：[DEVELOPMENT_ACQUISITION_REPORT.md](C:/Cursor/raven.mcs/ccf-review-report/observed_feedback_rolling_45011_20261014_s2/DEVELOPMENT_ACQUISITION_REPORT.md)；[PILOT_COMPARISON.md](C:/Cursor/raven.mcs/ccf-review-report/observed_feedback_autonomous_pilot_45001_recovery_20261015/PILOT_COMPARISON.md)；[NEXT_STAGE_READINESS.md](C:/Cursor/raven.mcs/ccf-review-report/observed_feedback_autonomous_pilot_45001_recovery_20261015/NEXT_STAGE_READINESS.md)；[STOP_REPORT.md](C:/Cursor/raven.mcs/results_reachability_detector_v1/STOP_REPORT.md)。


## 四、已充分体现，不应算作遗漏


### D01 City Scanner PM₂.₅与Pilot2实测O

**规模与完成程度：**两块各5方法×10种子；现有附录表XXII、XXIII。

**已有结果：**真实占用R，Pilot2有实测O；RAVEN有结构优势及有限预测相对改善，但不同块最优预测方法分别仍为FedAvg/TwoStage。

**当前稿体现：**正文VII-A/B/G明确介绍；附录J有数据构建与完整表。属于放在补充材料，不是遗漏实验。

**可如何利用：**若强调真实数据适用性，可从现有附录提升一张表至正文；不需要以“新增实验”名义重做。

**适用限制：**U仍受控，客户端是occupied cell而非车辆；不能升级为端到端实测移动联邦系统。

证据：[C1_KILL_REPORT.md](C:/Cursor/raven.mcs/results_c1_cityscanner/round_v1/C1_KILL_REPORT.md)；[JO_KILL_REPORT.md](C:/Cursor/raven.mcs/results_joint_ou/round_v1/JO_KILL_REPORT.md)。


### D02 INT-R间歇参与鲁棒性

**规模与完成程度：**SensorScope/U-Air的20配对种子，同站点数据，协议参与Markov稀疏化。

**已有结果：**T-Drive活跃率.425作为标量匹配；实际burstiness约.20，非.38。部分结构优势削弱，Design取舍方向仍在。

**当前稿体现：**附录G及表XVII/XVIII已经完整解释，正文VII-C明确概括。

**可如何利用：**保留现有呈现即可；需要版面调整时可提炼一幅小图。

**适用限制：**不是实际GPS叠加，也不是独立移动数据集，不能重复计入跨城市泛化。

证据：[EXECUTION_LOG.md](C:/Cursor/raven.mcs/results_int_r/round_v2/EXECUTION_LOG.md)。


### D03 E3/E4主对比、五组件消融与Uniform归因

**规模与完成程度：**正文表III/IV、Fig.4、附录完整方法表与消融图。

**已有结果：**Uniform解释大部分FedAvg差异，投影/Design的结构贡献、U-Air端点取舍和债务微小作用均已明确。

**当前稿体现：**摘要、引言贡献、方法、正文VII-C/E和结论重复使用，是当前稿最充分利用的证据。

**可如何利用：**避免再把相同数据换图重复占版面；可用C02的新排布提升清晰度。

**适用限制：**不能把统计显著但很小的Debt效应扩大成预测收益。

证据：[EXPERIMENT_ROLE_REGISTRY.md](C:/Cursor/raven.mcs/manuscript_evidence_closure_r1/00_audit/EXPERIMENT_ROLE_REGISTRY.md)；[E4_INST_FINAL_STATS.csv](C:/Cursor/raven.mcs/artifacts/e4_wo_inst_reference_penalty_final_correction_r1/E4_INST_FINAL_STATS.csv)。


### D04 覆盖Gate压力、稳定区间理论与支持审计

**规模与完成程度：**sag多个版本的修复轨迹；最终R1M等审计，附录表XIX/XX及Fig.9。

**已有结果：**pooled CERTIFIED validity约.959，U-Air a=1为.750；A6a稳定器实际激活，保留εstab。

**当前稿体现：**正文III/IV/V/VI及VII-G、附录H/I已有充分覆盖。

**可如何利用：**保留诊断角色和失败单元，不把每次修复报告当独立实验增加数量。

**适用限制：**旧候选Design:=Gate的数据不证明当前预配置Design方法收益；稳定区间定理也不证明任意自适应切换有效。

证据：[RAVEN_MCS_R1M_AGGREGATE_CERTIFICATE_FORMAL_AUDIT_REPORT.md](C:/Cursor/raven.mcs/results_sag_g1/round_r1m/summary/RAVEN_MCS_R1M_AGGREGATE_CERTIFICATE_FORMAL_AUDIT_REPORT.md)；[README.md](C:/Cursor/raven.mcs/artifacts/a5_a6_audit/README.md)。


### D05 Local-Hajek退化、774窗口与求解器核验

**规模与完成程度：**9666有效client-window、774窗口层级溯源、6438窗口数值可行性审计等。

**已有结果：**协议内局部权重归一化消除常数，Design差异起于正质量/P2支持；可行性核验与最优性证明不同。

**当前稿体现：**附录D/E/F和正文VII均有明确文字与表VII—IX。

**可如何利用：**作为现有结果可信度的支撑，不另包装成性能增益。

**适用限制：**778警告/85运行等计数描述旧封存人群，不能套到后续修复运行集合。

证据：[E3_LOCAL_HAJEK_FINAL_DECISION.md](C:/Cursor/raven.mcs/artifacts/e3_local_hajek_weight_and_p2_certificate_final_closure_r1/E3_LOCAL_HAJEK_FINAL_DECISION.md)；[E4_WO_DESIGN_774_WINDOW_LAYER_SUMMARY.md](C:/Cursor/raven.mcs/artifacts/e4_wo_inst_reference_penalty_final_correction_r1/E4_WO_DESIGN_774_WINDOW_LAYER_SUMMARY.md)。


### D06 arrival与target验证选择的360格复核

**规模与完成程度：**2数据集×9配置×20种子=360格的已有checkpoint重评分，无新训练。

**已有结果：**arrival评分有偏移，但两种权重在全部20种子选择同配置；选择后悔量为0，诊断saturated。

**当前稿体现：**正文VII-G已直接给出−4.11%至−4.12%及+.27%至+.62%、20种子选择一致。

**可如何利用：**若补充材料有空间可留索引；核心发现已经被利用，不是新的正效用。

**适用限制：**不能把风险数值不一致说成已造成模型选择损失。终窗checkpoint/内存镜像例外须保留。

证据：[PART_I_REPORT.md](C:/Cursor/raven.mcs/results_estimand_selection/round_v1/PART_I_REPORT.md)。


## 五、不应回收成论文“新收益”的材料

- results_endpoint_screen/round_v1/SCREEN_DOSE_provisional_WITHDRAWN.csv明确撤回，不使用其斜率作为结果。
- H响应偏移80条及早期oracle根因报告存在U-Air FedAvg来源/支持语义争议；后续round_v3已说明较大约6%效果主要来自支持规则变化，不是oracle信息收益。不能回收旧“oracle损失6.8%”结论。
- W1某些轮次的exact oracle门槛未通过；其数据只能按已给出的approximate及误差量级陈述，不能改成严格最优证书。
- T-Drive spatial-h C1只有一条FedAvg摘要，其余方法为TBD；不是完整50条对比。
- gate-dose v1只有P0准备，v2才有实际剂量结果；各种SGD0、导入/保存检查、重复审计不是正式预测实验。
- 新重建的验证RMSE、旧测试RMSE和OF的G/W属于不同协议/指标，不能拼入一张主表制造统一领先。

## 六、最值得先做的整理

当前素材足以支持一次不新增训练的证据整理：优先将A01的集中度梯度、A03的漂移结果、C01的F-1设计与结果、C02的规则比较排成简明表/图；A02保留固定预测评分身份并处理既有重评分路径争议；A04/A05单列新开发诊断，不替换旧主表测试值。City Scanner、INT-R和覆盖证书已有完整附录，调整正文权重比重复新增表更有价值。

这份清单不是把所有负结果塞入论文的要求。按当前主题选择能回答读者关键问题的证据，保留效应方向、单位、种子、条件与失败单元；无法支持主张的结果用于限定或独立研究记录。

当前空缺仍然存在：新方法完整P3未通过；没有补齐当前新方案的完整强外部方法、充分联邦学习、生产q依据和独立确认。已有大量运行不等于这些特定问题已经得到回答。

本次未修改论文、未生成新实验结果、未启动任何实验队列。新增数字仅为已有小型记录的只读汇总，没有新增显著性检验。版本化细节见evidence-utilization.json／csv、audit-scope.json及目录清单。
