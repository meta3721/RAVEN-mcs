# 当前实验阶段总结、资源限制与证据索引

归档日期：2026-10-15（北京时间）。项目：`C:/Cursor/raven.mcs`。本次按 ccf-pipeline-orchestrator 整理已有证据；不改变方法、实验门槛或历史状态。

**当前阶段：45011完整采集完成；45001四臂自主单种子预实验完成；完整P3之前的单种子效用预筛未通过。状态保持 `PILOT_UTILITY_NOT_ESTABLISHED / Q_STOP_CLAIM_UNSUPPORTED / WAITING_USER_REVIEW`。停止新增实验。**

本次只读取报告、直接引用的结果摘要、冻结文件与检查点指针，追溯已有硬件核验输出，并检查可见进程。未启动训练、重放、参数搜索、性能测试、压力测试或完整P3；未复制大体积模型，未修改旧失败报告、STOP状态、损坏文件或历史费用账。

## 1. 证据范围与状态沿革

读取的三组报告及其直接引用的机器摘要：

- [45011滚动续行报告目录](C:/Cursor/raven.mcs/ccf-review-report/observed_feedback_rolling_45011_20261014_s2/)：完整采集、恢复、机制与成本描述。
- [45001原自主预实验报告目录](C:/Cursor/raven.mcs/ccf-review-report/observed_feedback_autonomous_pilot_45001_20261014/)：原方法与配置冻结、OF完整结果、fixed.5中断前缀及当时取消的两臂。
- [45001限定恢复报告目录](C:/Cursor/raven.mcs/ccf-review-report/observed_feedback_autonomous_pilot_45001_recovery_20261015/)：设施修复、资源授权迁移、fixed.5恢复、fixed2与no-Q-stop完整结果及最终筛查。

旧45001报告的 `PAIRING_INCOMPLETE` 是当时正确的历史状态：OF完成，fixed.5仅到t75，fixed2与no-Q-stop尚未启动。经另行授权的恢复阶段，后三臂已经完成，最终四臂无缺项；不能将旧报告改写为当时已完成，也不能继续用旧缺臂状态描述当前科学结论。

发生报告快照差异时，具体恢复记录、各臂 `VALIDATION_AND_SUMMARY.json` 与已关闭的最终 `BUDGET.json` 优先于较早的文字快照。本次仅在此补充索引与解释，不回写旧报告。

### 已完成

- **45011完整T=100采集**：1000网格、4300注册、逻辑SGD 3281、147次关闭、1581个唯一消费key。实际物理工作范围3302—3303步，包含失败后缀21—22步。原10行前缀与成功990行后缀构成有效轨迹；模型、私有队列及随机状态恢复等值核验已有PASS。它提供接口、采集、机制描述与成本证据，不提供独立固定策略对照的效用证据。
- **45001四臂自主T=100采集**：OF、fixed_time_0.5、fixed_time_2、OF-no-Q-stop均为1000网格、4300注册、逻辑SGD 3354。四臂共同数值初值及每臂4300个外生key配对检查PASS；抽样hash与R无不匹配。模型、队列、消费、下载版本、实际CPU下界及到达等内生差异保留。
- **本次相关实施与恢复关键路径核验**：既有SGD0策略检查、限定持久化设施检查、恢复前实际状态和producer/RNG等值检查、终点消费/权重/数值检查及新会话外层PID终审均有既有记录。它们的通过范围限于这些具体路径。
- **45001预定单种子效用筛查已执行完毕**：完成筛查不等于通过；结论为未建立预定效用，Q停止项额外贡献未获支持。

### 部分完成

- **P1自主学习链证据**：已获得真实CommonNDMF/ClientTrainer、完整当前P2、实际聚合/消费/状态更新与成对保存证据；预测保存、物理单位重评分等完整要求尚未补齐，不能标记全部P1通过。
- **P2计算与证明证据**：已有完整当前预览/应用、约束残差和绑定检查；完整声明/证明账仍缺，不将这些实现检查等同于全部数学证明完成。
- **P3准备与预筛**：完成单种子四臂比较，但效用门槛未通过。完整P3全A层/三种子未开始，不以本预实验替代。
- **概率接口与支持记录**：已有采集、成熟/删失和策略身份记录；q=.5仍是 `diagnostic_prior`，不是拟合或已校准概率。概率依据与完整校准尚未建立。
- **运行稳定性与费用可追溯性**：恢复设施和新会话终审获得验证；旧失联段的实际CPU、确切退出时刻和系统根因仍未知，不能追认历史终审完整。

### 本阶段未开展或未完成验收

- 完整P3全A层与45002/45003等扩种子。
- P4充分学习平台、预测重评分及训练均值/适用持久性和季节性预测基线的完整验收。
- P5完整外部方法比较及生产概率依据；本批未拟合q。
- P6独立正式确认；B1、扩大批次及39条正式轨迹。
- P7去L、去P2-Q等完整机制消融，以及完整新颖性核验。

此处状态依据三组交接报告；不将“本批没有证据”扩写为项目任何历史版本从未做过相关工作。根目录没有本项目有效 `ccfa.yaml`；检出的同名文件属于技能示例/模板，不据此登记项目通过状态。

## 2. 核心科学结果与可支持结论

证据：[最终比较](C:/Cursor/raven.mcs/results_observed_feedback_autonomous_pilot_45001_recovery_20261015/PILOT_COMPARISON.json)、[配对检查](C:/Cursor/raven.mcs/results_observed_feedback_autonomous_pilot_45001_recovery_20261015/PAIRING_RESULT.json)、[比较说明](C:/Cursor/raven.mcs/ccf-review-report/observed_feedback_autonomous_pilot_45001_recovery_20261015/PILOT_COMPARISON.md)。以下G、W均越小越好：

- OF：G=0.9452180232558112，W=0.6015037593984962。
- fixed_time_0.5：G=0.9588590116279057，W=0.5063291139240507。
- fixed_time_2：G=0.8430825786217807，W=2.0000000000000000。
- OF-no-Q-stop：G、W与OF相同。

G按20.1至100的800个网格上的既定最近实际非空发布质量记录计算。W取close_time>20的全部正时长关闭窗口，包括空关闭和终点关闭；四臂分母依次133、158、40、133。动作比较使用20<t<100的799个常规网格。t是受控服务时间单位，不能称为第t个聚合窗口，也不能当作实际墙钟。

事前主对照始终是fixed.5。原等待路线要求 `rW=(Wb−Wof)/Wb≥.05` 且 `dG=Gof−Gb≤.01`；原匹配路线要求 `rG=(Gb−Gof)/Gb≥.02` 且 `Wof≤1.05Wb`。本次未改变门槛、分母、主对照或用辅助J择优。

- **OF对fixed.5**：G改善1.422627%，W增加18.796992%，W比值1.187969925。等待路线未达5%收益；匹配路线未达2%质量收益且违反5%等待保护。质量保护dG≤.01本身通过，不能笼统写为所有保护均失败；总体预定收益及配套条件未满足。
- **OF对fixed2**：W减少69.924812%，G恶化12.114524%；绝对dG=0.102135445，超过.01质量保护。存在等待—质量权衡，不能据等待改善单独宣布通过，也不能称fixed2在两指标上同时支配OF。
- **去Q停止项对OF**：G/W、关闭序列相同，799格自主动作差异为0，动态Q和模型版本差异也为0。本种子未支持额外Q停止项贡献。该消融仅将停止式κ置0，完整P2-Q、Q更新及其他机制保留；不能解释成删除所有debt项，也不能替代去L或去P2-Q消融。

四臂是独立自主轨迹；同全局时间的不同池/模型不是同状态反事实。45011及OF内的同状态影子动作只支持机制描述，不能替代自主收益。上述都是Traffic/45001、冻结配置、诊断先验下的单种子结果；800格或多个窗口不是独立种子，不据此推断所有种子或整个方法家族均失败。

**结论边界分别保留：**

- 检测/停止或控制效用：本单种子预定G/W效用预筛未通过；没有新的可达性证书或风险保证。
- 任务性能不退步：fixed2比较中的既定G质量保护未通过；尚无完整预测任务不退步证据。
- 预测收益：未重新验证，标记 `RESULTS_NOT_REVALIDATED`；不声称RMSE收益、充分训练后的主实验成立或新版RAVEN收益。

运行故障与上述科学效用分别记录。没有证据表明G/W的未达标由电脑配置引起；反之，轨迹终点有效也不能否定用户观察到的卡顿。

## 3. 已有硬件核验及其时间边界

硬件信息未保存在本轮三目录的资源摘要中。本次追溯了此前项目核验的原始工具输出，未重新做硬件/性能测量。来源为[历史核验会话记录](C:/Users/szr/.codex/sessions/2026/10/11/rollout-2026-10-11T21-49-44-01a12b3a-025f-7c00-9765-41825e4e13ed.jsonl:1686)，以及[内存/卷容量/PyTorch核验输出](C:/Users/szr/.codex/sessions/2026/10/11/rollout-2026-10-11T21-49-44-01a12b3a-025f-7c00-9765-41825e4e13ed.jsonl:1696)。会话文件名为创建日期，实际采样时间如下，均为北京时间：

- **CPU，2026-10-14 15:49:00.838输出**：注册表输出Intel(R) Core(TM) 7 245HX；逻辑处理器数14。15:50:01.695的 `os.cpu_count()`再次输出14。该次注册表命令同时有类型转换报错，成功输出的型号/逻辑数与报错分别保留；不由此推断物理核数或持续可用算力。
- **内存，2026-10-14 15:50:01.695输出**：Windows GlobalMemoryStatusEx查询成功；可见物理总量16,551,960,576字节，约15.42 GiB。**当时**可用801,460,224字节，约0.7464 GiB。此可用内存只描述当时瞬时状态，既不是2026-10-15当前状态，也不是fixed.5中断时读数；没有同期进程峰值、提交内存、分页或OOM证据可据以诊断中断。
- **GPU，2026-10-14 15:49:00.838输出**：nvidia-smi识别NVIDIA GeForce RTX 5060 Laptop GPU，总显存8151 MiB、当时空闲7899 MiB，驱动616.56、当时利用率0%。15:50:01.695的PyTorch输出CUDA可用、CUDA runtime 13.0、Torch 2.13.0+cu130，设备可见显存8,518,041,600字节。两种接口口径原样保留，不拼成同一个数值。
- **存储卷，2026-10-14 15:50:01.695输出**：C盘总510,628,196,352字节（475.56 GiB），当时空闲138,621,853,696字节（129.10 GiB）；D盘总60,186,161,152字节（56.05 GiB），当时空闲47,953,399,808字节（44.66 GiB）。这是逻辑卷容量，不能据此认定SSD型号、物理盘数量、健康或当前余量；上述信息均未核验。

**本轮涉及的45011与45001实验账/执行记录均为GPU用量0，q拟合0。** 本机能识别GPU、安装CUDA构建，不代表这些采集已经使用GPU，也不能据此推断GPU加速可解决当前问题。

## 4. 运行稳定性：事实、原因与未知

### 用户观察

用户在本次请求中报告：实验期间电脑多次卡顿，甚至出现“熄火”。这是需要保留的运行稳定性问题。各次发生时间、持续时间、应用是否退出、是否系统异常关机/重启或其他现象，尚无足够对应证据，均为**未知**；不自动等同于旧fixed.5进程失联事件。

### 日志确认的事实

- **45011发布异常与失败后缀**：既有记录含root发布/替换权限异常；S1没有可用的新完整模型后缀，额外21—22个物理SGD未进入有效模型。S2成功使用独立工作区反馈路径后完成采集；成功轨迹只拼接原10行和成功990行。详见[45011恢复报告](C:/Cursor/raven.mcs/ccf-review-report/observed_feedback_rolling_45011_20261014_s2/RESUMPTION_REPORT.md)及[费用说明](C:/Cursor/raven.mcs/ccf-review-report/observed_feedback_rolling_45011_20261014_s2/RESOURCE_AND_BUDGET.md)。
- **45001 OF可捕获暂停**：首段在t33.29因根预算读数过期，在新注册前拒绝操作并保存；保持1秒样本有效期，修复等候新样本的设施路径后从原状态恢复并完成。这有明确程序错误/保护路径证据，不属于已确认的系统关机。
- **45001旧fixed.5失联**：原PID16640最后完整点为2026-10-14 21:28:10的t75；CATEGORY_LIVE与root反馈文件mtime为21:29:13且内容全NULL；22:46:22首次观察进程不存在。最终meter、charge、EXECUTION_RESULT缺失；部分运行日志也不可读。退出确切时间、退出码及系统根因未知。6671.2秒仅启动至首次发现失联的保守包络。
- **fixed.5恢复**：旧t75模型/private与producer/RNG仍有效，恢复前等值检查PASS；只迁移资源授权，原750行与成功250行拼接成T100。旧失联后缀不用日志补造，旧损坏文件保留。
- **fixed2普通设施暂停**：在t8.11已训练待queue帧，等候根新样本2秒超时，未获准执行下一操作；异常被捕获、完整点和费用终审已保存，无新NULL记录。此前t5的170逻辑步具备完整恢复上下文，采用它恢复；原266物理步不退账，明确重做96步。接受的根样本仍须小于1秒，等候上限改为10秒不改变样本有效期。详见[具体恢复说明](C:/Cursor/raven.mcs/ccf-review-report/observed_feedback_autonomous_pilot_45001_recovery_20261015/FIXED2_RESUMPTION_REPORT.md)。
- **持久化设施已有修复与限定检查**：原子发布、同步写入、上个有效记录、检查点SESSION_DURABLE、周期根样本与独立退出审计，已有唯一固定输入SGD0检查PASS；不代表实际断电实验或任意中断零丢失保证。详见[设施说明](C:/Cursor/raven.mcs/ccf-review-report/observed_feedback_autonomous_pilot_45001_recovery_20261015/FACILITY_FIX.md)与[检查记录](C:/Cursor/raven.mcs/results_observed_feedback_autonomous_pilot_45001_recovery_20261015/FACILITY_CHECK.json)。

### 有证据支持的局部原因

部分45011失败调用可定位到 `os.replace` 权限/发布路径问题；OF和fixed2的可捕获暂停可定位到根样本新鲜度/等待设施。fixed2回退至t5是因为活动帧未保存完整抽样审计上下文，96步重做有计数依据。这些局部原因不能推广为所有中断或用户“熄火”的原因。

旧fixed.5全NULL、进程消失和终审缺失是故障事实，不能单凭它们证明断电、过热、内存不足、磁盘故障、应用崩溃或配置不足。[既有中断审查](C:/Cursor/raven.mcs/ccf-review-report/observed_feedback_autonomous_pilot_45001_recovery_20261015/INTERRUPTION_REVIEW.md)记录：对应窄时间段System事件41/6008/7/51/55/153查询曾被访问控制拒绝，未获得因果证据。本次不重复被拒查询、不扫描全盘、不做压力测试。

### 状态文件增长与成本负担

45011成对模型/private字节从初始 `[6,301,614, 4,134,777]`、首个滚动点 `[32,700,682, 4,593,467]` 增长到终点 `[179,560,368, 7,493,086]`。45001终点依次为OF `[174,821,982, 5,678,396]`、fixed.5 `[165,745,680, 5,706,787]`、fixed2 `[229,256,810, 5,713,223]`、no-Q `[174,966,952, 5,677,926]`。这些是保存文件字节，不能当作进程RSS或峰值内存。

既有实测显示保存与事件处理占据明显CPU费用。例如45011成功续行根433.468750 CPU秒中，save为131.421875、events为219.593750、training为45.796875；它们已包含在根总量，不能再累加计费。45001 no-Q保存最大完整根上界10.457500 CPU秒。状态增长与保存负担有事实依据；它们对用户卡顿或失联的具体因果贡献仍未知。当前内存余量、磁盘余量/健康、温度、电源状态、并发负载及故障时峰值资源均未知。

### 当前可见运行状态

2026-10-15 23:35:40（北京时间）的只读检查未发现可见 `python`/`pythonw` 进程；恢复阶段既有账中各计量worker均记为exited，活动区间已关闭。当前CIM进程命令行枚举受访问控制限制，不能把此快照表述成已排除所有解释器别名、后台任务或不可见进程。本次没有发现可报告的仍运行项目作业，未启动作业，也未终止任何进程。

## 5. 费用与物理工作口径

所有CPU单位为秒。**审计实际CPU、保守预算占用、墙钟和未知实耗分开**；不把额度写成测量，不重复加入PID、内层训练/监视或同一历史账。

### 45011连续采集账

- 最终占用757.375000 / 授权3600；其中已知审计实际622.187500，保守135.187500；未计量实际缺口UNKNOWN。
- 成功续行根433.468750（tree345.390625 + driver88.078125）已包含在上项。
- 成功续行实际墙钟2410.307449；含前段与失败续行的轨迹累计实际执行墙钟2477.795585。交付检查等其他调用墙钟另列；`BUDGET.wall_measured=2423.2142044`是该账所列调用范围，不替代跨会话轨迹墙钟。
- 原5小时口径的累计历史占用5522.609375 **已经包含这757.375000**，不能再相加。该历史累计含保守/未知部分，不能称为全实测CPU。

来源：[45011最终账](C:/Cursor/raven.mcs/results_observed_feedback_rolling_45011_20261014_s2/BUDGET.json)、[口径解释](C:/Cursor/raven.mcs/ccf-review-report/observed_feedback_rolling_45011_20261014_s2/RESOURCE_AND_BUDGET.md)。

### 45001原阶段与限定恢复阶段

- 原阶段最终占用2983.859375：审计实际563.703125；保守2420.156250；未知实际CPU不补0。其中fixed.5旧失联调用2388由2380分配额加8安全余量形成，**不是实测消耗，也不是已证明的实际消耗上界**。
- 恢复阶段已关闭最终占用1423.875000 / 阶段1800：审计实际1333.875000；保守90.000000（30准备/交付及60外部辅助）；这些未审计辅助的实际值UNKNOWN，90也不是经证明的实际上界。
- 45001连续占用4407.734375 / 修订4800 = 原2983.859375 + 恢复1423.875000。其中审计实际1897.578125，保守2510.156250；不能把4407.734375称为算法实际CPU。
- 本次涉及的历史累计口径为9930.343750 = **5522.609375 + 4407.734375**。不要再加入45011的757.375、45001原阶段2983.859375或恢复1423.875。更早历史内部实际/保守的完整拆分未在本轮重建；它不是全项目穷尽费用。
- 恢复目录部分MD/DELIVERY_CHECK保留交付前快照1423.515625、连续4407.375000；最终账补入report_delivery的0.359375后是上述关闭值。原45001部分早期文段为2983.687500，最终补正为2983.859375。历史快照保留，不混用。

来源：[原最终账](C:/Cursor/raven.mcs/results_observed_feedback_autonomous_pilot_45001_20261014/BUDGET.json)、[恢复最终账](C:/Cursor/raven.mcs/results_observed_feedback_autonomous_pilot_45001_recovery_20261015/BUDGET.json)。

### 墙钟单列

- 原45001阶段留账14373.550642 / 14400，含前期600秒保守项、开发/等待与未审计包络；不是全部训练实测时长。旧 `job_wall_measured` 名称下也混入fixed.5的6671.2秒包络，依已有补正不能整体视为实测。
- 恢复阶段最终活动墙钟8944.252982 / 9000，含337秒初始化前保守活动留额；计量作业实际墙钟合计6839.089439。两者范围不同，不能相加。
- 连续留账23317.803624 / 23400 = 旧14373.550642 + 恢复8944.252982。已证据化的审批等待单列排除；关闭后不再按目录年龄增长。本次归档没有重新打开该活动区间。
- 各臂执行会话墙钟：OF 2689.562009；fixed.5本次恢复实测750.707479，旧运行精确值UNKNOWN，6671.2包络单列；fixed2两会话合计2975.833990（含被丢弃的96步）；no-Q 2995.480840。各臂数值是阶段总账的组成/审计说明，不再加入阶段墙钟。

来源：[关闭活动区间](C:/Cursor/raven.mcs/results_observed_feedback_autonomous_pilot_45001_recovery_20261015/ACTIVITY_INTERVAL.json)、[等待口径补正](C:/Cursor/raven.mcs/results_observed_feedback_autonomous_pilot_45001_recovery_20261015/PREINITIALIZE_APPROVAL_CORRECTION.json)与最终账。

### 有效训练与丢失物理工作

- 45011：有效逻辑3281；实际物理范围3302—3303，包含旧失败21—22步；丢失步不构成有效模型证据。
- 45001：四臂有效逻辑均3354；OF物理3354，fixed.5物理3354—4429（旧失联后缀0—1075未知），fixed2物理3450（3354+已知重做96），no-Q物理3354。合计13512—14587；该区间含未知工作，不能取下界当精确实测。
- fixed.5的1075来自有限4300注册、旧t75已3225注册、单次执行及local_steps=1等已审计结构条件；不是CPU推导，也不消除未知退出时长。恢复前更松5000上界留在旧报告，现按[有限工作审查](C:/Cursor/raven.mcs/results_observed_feedback_autonomous_pilot_45001_recovery_20261015/FINITE_WORK_AUDIT.json)解释。fixed2新增96后全批规划结构上界16693，不是实际工作量。

本次归档本身的实验训练/重放/GPU/q拟合增量为0。读取与文字整理未纳入新的实验根计量，精确辅助CPU未知；不写为总CPU实耗0，不挪用历史名义余额授权下一批，也不修改已经关闭的历史账。

## 6. 有效资产索引与历史隔离

以下仅建立位置索引。此次轻量核对了终点/指定恢复点marker及其指向model/private文件的存在；未重新读取或重算大模型hash。原有成对校验、等值及数值PASS以对应既有核验为依据，不冒充本次全量重新验收。

### 45011完整采集

- 有效终点：[tick1000.complete.json](C:/Cursor/raven.mcs/results_observed_feedback_rolling_45011_20261014_s2/trajectory/tick1000.complete.json)，指向同目录 `tick1000.model.json` 与 `tick1000.private.json`。
- 汇总：[VALIDATION_AND_SUMMARY.json](C:/Cursor/raven.mcs/results_observed_feedback_rolling_45011_20261014_s2/VALIDATION_AND_SUMMARY.json)；[机制/成本摘要](C:/Cursor/raven.mcs/results_observed_feedback_rolling_45011_20261014_s2/DESCRIPTIVE_MECHANISM_AND_COST.json)；[完整段成本](C:/Cursor/raven.mcs/results_observed_feedback_rolling_45011_20261014_s2/ENRICHED_ROLLING_COST_SEGMENTS.json)；[保存计量](C:/Cursor/raven.mcs/results_observed_feedback_rolling_45011_20261014_s2/SAVE_MEASUREMENTS.jsonl)。
- 冻结：[原采集计划](C:/Cursor/raven.mcs/results_observed_feedback_continuation_45011_20261014/ACQUISITION_FROZEN_PLAN.json)。恢复来源：[原t1.07成对点](C:/Cursor/raven.mcs/results_observed_feedback_continuation_45011_20261014/trajectory/stopped_0011_0206.complete.json)；[恢复等值检查](C:/Cursor/raven.mcs/results_observed_feedback_rolling_45011_20261014_s2/RESUMPTION_CHECK.json)。
- 有效范围：本轨迹采集、成本、标签/删失与同状态影子；失败S1后缀及发布失败只作故障/费用记录，不与成功后缀同时拼接。

### 45001 OF与共同冻结

- OF有效终点：[tick1000.complete.json](C:/Cursor/raven.mcs/results_observed_feedback_autonomous_pilot_45001_20261014/of_resume1/trajectory/tick1000.complete.json)；[完整摘要](C:/Cursor/raven.mcs/results_observed_feedback_autonomous_pilot_45001_20261014/of_resume1/VALIDATION_AND_SUMMARY.json)。恢复阶段直接复用，未重跑。
- OF历史暂停点：[stopped_0333_07272.complete.json](C:/Cursor/raven.mcs/results_observed_feedback_autonomous_pilot_45001_20261014/of/trajectory/stopped_0333_07272.complete.json)；[恢复检查](C:/Cursor/raven.mcs/results_observed_feedback_autonomous_pilot_45001_20261014/of_resume1/RESUMPTION_CHECK.json)。历史前缀不单独充当T100结果。
- 共同冻结：[PILOT_FROZEN_PLAN.json](C:/Cursor/raven.mcs/results_observed_feedback_autonomous_pilot_45001_20261014/PILOT_FROZEN_PLAN.json)、[INITIAL_BACKEND.json](C:/Cursor/raven.mcs/results_observed_feedback_autonomous_pilot_45001_20261014/INITIAL_BACKEND.json)、[冻结说明](C:/Cursor/raven.mcs/ccf-review-report/observed_feedback_autonomous_pilot_45001_20261014/PILOT_FREEZE.md)。科学配置θ=.02、κ=.10、ν=.20；no-Q-stop仅κ=0。T100、Δ=.1、warmup20、deadline4、age5、minimum_clients3；Design全程显式on、coverage Gate仅诊断；真实local_steps1、LR.01、server_eta.01；q=.5 diagnostic_prior。
- 源码/入口身份：[原实现冻结](C:/Cursor/raven.mcs/results_observed_feedback_autonomous_pilot_45001_20261014/IMPLEMENTATION_SCRIPT_FREEZE.json)、[修复脚本v2冻结](C:/Cursor/raven.mcs/results_observed_feedback_autonomous_pilot_45001_20261014/IMPLEMENTATION_SCRIPT_FREEZE_v2.json)、[旧实现档案](C:/Cursor/raven.mcs/results_observed_feedback_autonomous_pilot_45001_20261014/old_implementation/ARCHIVE_CHECK.json)。各运行/概率策略身份保存在相应臂的ARM_FROZEN_PLAN及结果配置中。

### fixed.5恢复与旧故障

- 原有效恢复点：[t75 marker](C:/Cursor/raven.mcs/results_observed_feedback_autonomous_pilot_45001_20261014/fixed05/trajectory/tick0750.complete.json)；[旧前缀检查](C:/Cursor/raven.mcs/results_observed_feedback_autonomous_pilot_45001_20261014/INTERRUPTED_PREFIX_CHECK.json)。它仍是有效前缀和恢复依据，不是旧运行完整终点。
- 新有效终点：[tick1000.complete.json](C:/Cursor/raven.mcs/results_observed_feedback_autonomous_pilot_45001_recovery_20261015/fixed05_resume1/trajectory/tick1000.complete.json)；[完整摘要](C:/Cursor/raven.mcs/results_observed_feedback_autonomous_pilot_45001_recovery_20261015/fixed05_resume1/VALIDATION_AND_SUMMARY.json)；[恢复等值检查](C:/Cursor/raven.mcs/results_observed_feedback_autonomous_pilot_45001_recovery_20261015/fixed05_resume1/RESUMPTION_CHECK.json)。有效归属为原750行+新250行。
- 原损坏证据：[CATEGORY_LIVE.json](C:/Cursor/raven.mcs/results_observed_feedback_autonomous_pilot_45001_20261014/fixed05/CATEGORY_LIVE.json)、[root.json](C:/Cursor/raven.mcs/results_observed_feedback_autonomous_pilot_45001_20261014/fixed05/root_feedback_lgdpze5u/root.json)、[运行日志](C:/Cursor/raven.mcs/results_observed_feedback_autonomous_pilot_45001_20261014/fixed05_run1.log)、[启动记录](C:/Cursor/raven.mcs/results_observed_feedback_autonomous_pilot_45001_20261014/fixed05_run1.process.json)。NULL与缺终审说明历史故障，不提供有效后缀/消费/费用终审。

### fixed2与no-Q-stop

- fixed2原t8.11停止点：[stopped_0082_01732.complete.json](C:/Cursor/raven.mcs/results_observed_feedback_autonomous_pilot_45001_recovery_20261015/fixed2/trajectory/stopped_0082_01732.complete.json)。模型/状态与故障记录保留；因完整抽样审计上下文不足，没有用它续行。
- 实际恢复来源：[t5 marker](C:/Cursor/raven.mcs/results_observed_feedback_autonomous_pilot_45001_recovery_20261015/fixed2/trajectory/tick0050.complete.json)；[修复计划](C:/Cursor/raven.mcs/results_observed_feedback_autonomous_pilot_45001_recovery_20261015/FIXED2_REPAIR_PLAN.json)；[恢复等值检查](C:/Cursor/raven.mcs/results_observed_feedback_autonomous_pilot_45001_recovery_20261015/fixed2_resume1/RESUMPTION_CHECK.json)。
- fixed2有效终点：[tick1000.complete.json](C:/Cursor/raven.mcs/results_observed_feedback_autonomous_pilot_45001_recovery_20261015/fixed2_resume1/trajectory/tick1000.complete.json)；[完整摘要](C:/Cursor/raven.mcs/results_observed_feedback_autonomous_pilot_45001_recovery_20261015/fixed2_resume1/VALIDATION_AND_SUMMARY.json)。有效归属为原50行+成功950行，96重做步计物理成本。
- no-Q有效终点：[tick1000.complete.json](C:/Cursor/raven.mcs/results_observed_feedback_autonomous_pilot_45001_recovery_20261015/noqstop/trajectory/tick1000.complete.json)；[完整摘要](C:/Cursor/raven.mcs/results_observed_feedback_autonomous_pilot_45001_recovery_20261015/noqstop/VALIDATION_AND_SUMMARY.json)。

### 恢复设施、费用、历史停止状态

- [资源授权](C:/Cursor/raven.mcs/results_observed_feedback_autonomous_pilot_45001_recovery_20261015/RESOURCE_AUTHORITY.json)、[源码/资源迁移](C:/Cursor/raven.mcs/results_observed_feedback_autonomous_pilot_45001_recovery_20261015/SOURCE_RESOURCE_MIGRATION.json)、[恢复脚本冻结](C:/Cursor/raven.mcs/results_observed_feedback_autonomous_pilot_45001_recovery_20261015/RECOVERY_SCRIPT_FREEZE.json)、[v1](C:/Cursor/raven.mcs/results_observed_feedback_autonomous_pilot_45001_recovery_20261015/RECOVERY_SCRIPT_FREEZE_v1.json)与[v2](C:/Cursor/raven.mcs/results_observed_feedback_autonomous_pilot_45001_recovery_20261015/RECOVERY_SCRIPT_FREEZE_v2.json)分别保留。
- 恢复目录中 `charge_*.json`、`*.meter.json`、`*.worker_exit.json`、`EXIT_*.json`与各会话的SESSION_DURABLE/previous是根费用、退出、最后完整点的对应证据；不由实时root文件单独替代终审。各臂 `EXECUTION_RESULT.json`记录真实完成/暂停及归属，`SAVE_MEASUREMENTS.jsonl`记录保存费用。
- [原失败报告](C:/Cursor/raven.mcs/ccf-review-report/observed_feedback_autonomous_pilot_45001_20261014/FAILURE_REPORT.md)、[恢复阶段科学失败报告](C:/Cursor/raven.mcs/ccf-review-report/observed_feedback_autonomous_pilot_45001_recovery_20261015/FAILURE_REPORT.md)、[当前交接状态](C:/Cursor/raven.mcs/ccf-review-report/observed_feedback_autonomous_pilot_45001_recovery_20261015/NEXT_STAGE_READINESS.md)都保留。旧STOP报告与更早方法结果不覆盖、不重新标为本方法证据。
- 旧结果报告存在模板复用措辞：部分非fixed.5报告仍提fixed.5的750格；fixed2摘要文字把偏移泛称为未知，而具体恢复记录证明96步是已知重做。本归档按实际臂marker、数值摘要和具体恢复记录区分，没有删除原文或沿用错误归属。

原始数据、与Design无关的划分和基础记录继续保留；这不授予复用任意旧模型/预测的资格。上述结果归属OF-v1、configured Design和其冻结配置；不得与旧coverage-controlled Design、其他候选或不同概率身份互相重标。

## 7. 未解决问题与交接边界

### 方法效用依据

单种子预筛已完整执行但未达原收益/保护条件；Q停止项额外贡献未获支持。其余种子、完整P3、概率校准、完整外部基线、充分训练后的任务不退步与预测收益仍缺相应证据。未来若继续，必须由用户决定如何处理当前效用依据并明确授权；身份/设施通过不替代效用，科学未通过也不抹去有效实现和独立证明资产。本次不设计新实验、不修订算法或阈值。

### 运行稳定性与资源条件

需要区分用户“熄火”的具体事件类型与时间、旧失联根因、当时及未来运行的资源余量、峰值与可持续落盘/终审条件。现有历史硬件容量和一次较低可用内存读数不足以判断配置是否根本不足；窄范围系统日志曾不可访问，缺口保持未知。已完成的设施改进只证明其限定检查与随后会话的行为，不证明系统长期稳定或任意断电可恢复。任何进一步诊断、设施修改或资源申请均需明确范围与授权；本次不做硬件购买建议。

### 当前暂停范围

停止所有新增实验；不自动进入完整P3，不扩种子，不调θ/κ/ν，不拟合q，不启动B1/独立确认，不重跑已完成45011或45001任何臂，不用名义剩余额度恢复旧取消任务。不进行训练、重放、参数搜索、压力测试。保留现有科学门槛、冻结配置、失败结果、故障原件及费用未知项。

后续交接以本索引、最终四臂比较和已关闭账为起点，分别处理“方法效用依据”和“运行稳定性/资源条件”，由用户批准具体后续范围或终止。本次交付维持 **WAITING_USER_REVIEW**，不将归档完成标记为实验验收通过。
