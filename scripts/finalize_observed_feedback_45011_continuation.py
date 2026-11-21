"""Report existing evidence only. Does not create/advance an experiment."""
import csv,json,hashlib
from pathlib import Path
ROOT=Path(__file__).resolve().parents[1];OUT=ROOT/'results_observed_feedback_continuation_45011_20261014';REPORT=ROOT/'ccf-review-report/observed_feedback_continuation_45011_20261014'
def read(name):return json.loads((OUT/name).read_text())
e=read('EXECUTION_RESULT.json');v=read('PREFIX_RESTORE_CHECK.json');b=read('BUDGET.json');plan=read('PILOT_COST_PLAN.json');seed=read('SEED_REVIEW.json');f=read('ACQUISITION_FROZEN_PLAN.json')
rows=[json.loads(line) for line in (OUT/'DECISION_METRICS.jsonl').read_text().splitlines()]
with (OUT/'DECISION_METRICS.csv').open('w',newline='',encoding='utf-8-sig') as dest:
 writer=csv.DictWriter(dest,fieldnames=list(rows[0]));writer.writeheader()
 for row in rows:writer.writerow({k:json.dumps(x,ensure_ascii=False) if isinstance(x,(dict,list)) else x for k,x in row.items()})
protected=json.loads((ROOT/'results_observed_feedback_acquisition_45011_20261014/PROTECTED_HISTORY.json').read_text())
changed=[path for path,h in protected.items() if hashlib.sha256(Path(path).read_bytes()).hexdigest()!=h];assert not changed
meter=read('acquire.meter.json');process=read('acquire.process.json')
origin='C:/Cursor/raven.mcs/results_observed_feedback_continuation_45011_20261014/'
def link(name):return '['+name+']('+origin+name+')'
def md(name,text):
 path=REPORT/name
 with path.open('x',encoding='utf-8') as dest:dest.write(text)
estimated=sum(plan['estimated_remaining_CPU'].values());available=plan['available_root_CPU'];required=estimated+plan['save_reserve']
md('ACQUISITION_FREEZE.md',f'''# 45011真实成本run冻结

状态：**已启动但前缀未完整**。新初始化CommonNDMF（43空间实体、原骨干），仅TRAIN值及事前公共目录/目标，完整P2、configured Design=on、Gate仅诊断；OF-v1/T100/Δ.1/D4/age5/warmup20/θ.02/κ.10/ν.20，local_steps1/LR.01/server_eta.01，GPU0、最多5000局部步、诊断Beta(1,1)均值.5。未读取TEST值用于学习或控制，不加载43001/44001终态，不拟合q。

实际run_id：`{f['clock_namespace']['run_id']}`。UTC原点{f['clock_namespace']['origin_utc']}（北京时间2026-10-14 16:49:32.778907）；逻辑服务单位与墙钟分开，逐注册/通知实际UTC桥已归档。实际worker PID {f['worker_PID']}，常驻root `{f['root_id']}`，从创建前覆盖后代，PID仅核对不另计费。

四流由SeedSequence(45011)分别派生模型初值、局部dropout、机会/观察、服务；映射、scaler、公共μ/π、数据身份、初始模型数值身份、概率适用身份和源码保存在{link('ACQUISITION_FROZEN_PLAN.json')}。模型构造和初始数值已经执行；不是旧SGD0数学点。初始完整点`tick0000_initial.complete.json`已发布。

45011在列明的可访问身份资产中没有既往执行/拟合/选择冲突；当前批、计划、授权、固定SGD0归类分开。审计不覆盖任意外部历史或二进制内容。如今45011已用于本条成本前缀，不能再作为未使用的独立确认种子。{link('SEED_REVIEW.json')}和{link('AUDIT_SCOPE.json')}。
''')
md('DEVELOPMENT_ACQUISITION_REPORT.md',f'''# 真实首步采集与停止

**STARTED_PREFIX_INCOMPLETE / ACQUISITION_INCOMPLETE / WAITING_USER_REVIEW**。定向身份审计与唯一新增驱动SGD0通过后，实际初始化并进入唯一45011 Traffic轨迹。逻辑时间{v['now']}达到32个实际局部SGD，46次注册、10次实际网格决策、一次非空真实提交，模型版本1。目标仍T100，没有缩短目标或少训练来标完整。

实际修改：`acquisition.py`将注册/已训练/已排队活动帧存入私有producer，保留R0/E0工作和原服务源，推进因果游标，窗口后更新lagged p；仅回收不再允许下载的旧版本和已终止更新张量，保留所有证据。`backend.py`限定诊断授权下真实1步/.01/.01/Design on参数。`accounting.py`以根账含准入与监视计实际请求，分项转为计划预警。新增`execution.py`/`run_observed_feedback_45011.py`完成真实注册→训练→服务→到时通知→决策/提交→后窗p更新→成对保存。没有替代P2、future predictor或新q模型。

原SGD0结果直接复用。新增固定算术SGD0只检查变更链：实际trainer在真正SGD前返回固定零更新，实际SGD0，单元后端计数1仅记录一次截获。非恒等设计比率2与2/3、E0有工作/R0无工作、私有队列/游标/RNG恢复、后窗p更新及只读影子通过，未消耗Traffic或45011真实四流。{link('DRIVER_SGD0_RESULT.json')}。

真实prefix的成对恢复只读核验通过，模型状态hash、producer状态hash及源码一致，SGD32、now1.07、next_grid_tick11、next_clock1/client3、无未完成注册活动帧；检查未交付新通知、未决策或训练。{link('PREFIX_RESTORE_CHECK.json')}。当前证据验证到了首32步/暖启动，未验全T100、后续队列增长或常规反馈机制。

停止原因是首步续行计划不足，不是身份或性能失败。{link('EXECUTION_RESULT.json')}、{link('PILOT_COST_PLAN.json')}。旧NOT_STARTED报告原样保留，代表前一停止时刻；本文件记录新状态。
''')
md('FAILURE_REPORT.md',f'''# 首步续行费用计划未通过

实际状态：**已启动但前缀未完整**，等待用户决定。不是NOT_STARTED，也不是T100完成。没有信息/关键数值/消费冲突或实际请求2秒超限证据；方法性能仍未评估。

阻塞步骤：同一真实run首32步后的续行费用准入。预期是在原剩余额度内证明计划可继续；计划还需{estimated:.6f} CPU秒，另留保存{plan['save_reserve']:.6f}秒，共{required:.6f}；当时有效剩余{available:.6f}秒，差额{required-available:.6f}。实际总预算没有耗尽。

根训练最大请求上界.254375秒、实际局部步最大CPU.078125秒。当前实现更保守地用2×根训练最大值规划2164.222500秒，其中已包含2×局部最大CPU的664.687500秒，额外1499.535000秒来自监视/准入/测量余量的最大值外推；并非都是真正SGD时间。第一训练边界根差.234375=worker .078125+监视 .156250，墙钟约2.696359秒。对这个首次较长请求按所有剩余注册外推，是计划未过的主要原因之一，不证明后续实际一定耗这么多；不删掉该样本来强行通过。

其余计划：在线534.600000（参考已有K43 .27与剩余990格），事件1839.330000（观察最大上界与注册规模），保存124.275000（两倍实测并留3倍增长计划）。只有暖启动样本，后续费用、服务队列尾部和状态增长仍UNKNOWN。这些是保守规划选择，不能宣称统计保证或不可改变的物理下界。事件计数的规划近似没有覆盖所有未来状态，不足以单凭本前缀证明T100费用可行。当前停止按原“首步计划不足保存并等待”处理，不更改算法/阈值或自动恢复。

完整真实恢复点：{link('trajectory/stopped_0011_0206.complete.json')}。model6301614字节、private4134777字节；原数据身份、真实模型及版本、32步工作账、16个私有未来通知、producer游标、lagged p/q、Q/V/L、四流状态/映射、时钟和源码都绑定。保存恢复验证通过。next_grid_tick=11，须先处理到1.1的剩余注册/通知，不能跳过或重新抽样。没有此点之后未持久化的SGD/模型/服务抽样工作；退出仅补证据和计费。

私有账是保存前的预算快照；该次保存/最终归档/退出费用以最终BUDGET和charge行补齐。续行不得从检查点中的较小费用清零。后续恢复必须保持源码身份或提出明确迁移；不能由日志拼出私有模型。

旧加新费用{b['charged_CPU']:.6f}/3600，余额{3600-b['charged_CPU']:.6f}，实际SGD32、GPU0、q-fit0。旧失败和保守费用全保留。仍有效：审计、最小接线/SGD0、真实首步采集、一次完整P2与提交、根费用及真实成对恢复。取消后续T100采集，不拟合q、不开始39条、B1或确认。

继续所需决定：批准对费用外推/计量粒度做限定修订并核验，或接受当前计划不足而暂停；如需扩大总额度须另批。未经决定，不实施修订或恢复本前缀。
''')
md('MECHANISM_AND_SUPPORT_ANALYSIS.md',f'''# 前缀机制与两类删失

46条注册：R1=32、R0=14；实际E0=0（E0保留工作由固定SGD0另证）。R1中消费8、已通知失败5、消费尚未成熟19；另有16个R1物理服务仍pending。前缀右删失时间1.07，消费19条保留None，物理16条单独右删失；不行政补0，不当T100标签或校准通过。

决策仅0.1—1.0的10个暖启动格，一次完整P2、一次非空提交、消费8key，实际请求根最大上界{v['maximum_actual_request_root_upper']:.6f} CPU秒。未进入20<t<100，常规799格未采集，debt触发/OF-no-Q差异/固定影子常规比例均N/A。暖启动影子同规则不证明debt效应0；没有影子自主模型轨迹。完整G800格/W/J及配对收益均不计算。

注册归档37列，F保留全部合法key；观察到原始F最大29、资源编码缺失0。只表明本前缀接口域有效，不表明后续覆盖、正性、经验支持或概率依据。q一直是诊断先验.5，不叫已校准概率；消费8不能作为全T100概率估计。

{link('ATTEMPT_LABELS.json')}、{link('DECISION_METRICS.csv')}（10行）、{link('DECISION_SNAPSHOTS.jsonl')}、{link('PUBLICATION_BRIDGE.json')}。本次没有检测收益、控制收益、任务不退步、充分训练或预测收益结论。
''')
md('RESOURCE_AND_BUDGET.md',f'''# 原3600总帽的连续账

旧计费183.468750 + 新阅读/编辑/交付保守30 + 新根实测34.156250 = **247.625000/3600 CPU秒**。剩余3352.375000。旧实测143.875000、旧失败保守9.593750、两轮阅读/编辑/交付保守60；已知根实测合计178.031250，保守69.593750，实际缺口UNKNOWN。均累加，不从0重记。

新增根：种子定向审计6.875000、当前身份补充.171875、变更驱动SGD0 7.437500、唯一实际采集12.015625、只读真实prefix恢复7.656250；全部根审计通过。费用是tree+driver，PID和内层测量不重复加。唯一实际采集tree10.609375+driver1.406250，执行墙钟36.099392秒；2小时看门狗未触发。所有新增计量调用墙钟64.056053秒，开发撰写墙钟另计，非实验服务时间。

采集互斥账：初始化4.843750、在线.140625、训练.687500、事件/最终归档/退出2.578125、保存3.765625=12.015625。训练函数自身累计CPU.140625、墙钟2.763844、最大CPU.078125/墙钟2.656670；0或.015625的短步CPU受计时粒度影响，不能叫免费训练。外部监视始终计入根分类。

保存最大根上界1.035625秒，reserve保持5.968750。初始、pilot_prefix、pilot_complete和停止删失点均真实保存并计费；两个pilot点保存同模型/队列而计划字段不同，是多做的一次保存，费用没有删除。后续建议收敛为一个pilot完整点；当前真实源码不改，以保持prefix恢复身份。

计划分项可调配，setup220/init120/online1000/train800/events950/save360/repair150；累计分类setup137.875/init4.843750/online.140625/train.687500/events2.578125/save4.578125/repair96.921875。没有因repair接近100停下；此次是续行总费用计划不足。

累计计费5012.859375，原5小时名义余额12987.140625；历史实耗缺口UNKNOWN，名义余额不是下一批授权。{link('BUDGET.json')}、{link('charge_acquire.json')}、{link('acquire.meter.json')}和{link('acquire.process.json')}；worker24612由root记录核对，只读恢复worker19104不是新轨迹。
''')
md('NEXT_STAGE_READINESS.md',f'''# 等待用户决定：费用计划修订或暂停

**STARTED_PREFIX_INCOMPLETE / RESULTS_NOT_REVALIDATED / WAITING_USER_REVIEW**。与旧NOT_STARTED不同，真实45011已到1.07、SGD32；有效成对prefix只读恢复通过。完整T100、反馈机制和下一批成本可估性尚未通过，不申请q拟合、39条比较、B1或20种子确认。

最小建议仅针对费用规划：明确区分2×局部SGD最大CPU、实际根监视/准入和首次长墙钟费用，检查按单项最大值反复外推的保守程度；对生产者四类注册/队列/游标/通知操作及每格诊断记录按完整工作单元规划，明示未覆盖的增长成本。保留所有已测最大值及总帽、2秒实际请求、算法/训练/概率角色，不能通过删冷样本或不计监视让计划过门槛。若需要新的限定计量设施核验，先由用户决定范围与预算。

具体实现成本建议：准备/只读费用核验不超过60 CPU秒、实际SGD0；先提交修订计划。两个pilot完整点可收敛为一个，恢复代码若改变源码闭包，应使用明确保留的旧实现或审定状态迁移，不能静默忽略闭包检查。上述建议尚未实施，不自动训练/续行。

若用户批准同一前缀继续，必须读取最终247.625秒连续账、剩余3352.375，不从保存前私有账清零；读取{link('trajectory/stopped_0011_0206.complete.json')}，源代码身份一致，下一网格1.1，保持未成熟None/物理删失及原随机状态。普通接口不能重初始化一个新45011冒充恢复。

保留fixed.5及其他固定/count/GAP、去Q/去历史、匹配G/W、充分训练与简单预测基线、至少两项完整外部基线、独立确认门槛，新颖性needs-search。本prefix不能作收益或概率依据通过的证据。
''')
result=dict(status=e['status'],state='WAITING_USER_REVIEW',actual_SGD=32,GPU=0,q_fit=0,real_prefix_restore='PASS',charged_CPU=b['charged_CPU'],CPU_remaining=3600-b['charged_CPU'],changed_history=changed,protected_original_assets_checked=len(protected),reports_MD_only=all(p.suffix=='.md' for p in REPORT.iterdir()),decision_CSV_rows=len(rows),automatic_resume=False,old_reports='retained original NOT_STARTED status; new continuation status in separate folder')
(OUT/'FINAL_DELIVERY_CHECK.json').write_text(json.dumps(result,indent=2));print(json.dumps(result))
