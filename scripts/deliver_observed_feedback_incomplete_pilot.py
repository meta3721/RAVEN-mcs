"""Deliver actual partial pilot evidence. No experiment, fitting or replay."""
import json,runpy,time
from pathlib import Path
ROOT=Path(__file__).resolve().parents[1];OUT=ROOT/'results_observed_feedback_autonomous_pilot_45001_20261014';REPORT=ROOT/'ccf-review-report/observed_feedback_autonomous_pilot_45001_20261014'
runpy.run_path(str(ROOT/'scripts/render_observed_feedback_pilot_reports.py'))
check=json.loads((OUT/'INTERRUPTED_PREFIX_CHECK.json').read_text());b=json.loads((OUT/'BUDGET.json').read_text())
def append(name,s):
 with (REPORT/name).open('a',encoding='utf-8') as f:f.write('\n'+s+'\n')
def new(name,s):
 with (REPORT/name).open('x',encoding='utf-8') as f:f.write(s)
new('RESULT_FIXED05.md',f'''# fixed_time_0.5 — PREFIX_ONLY / WAITING_USER_REVIEW

最后已核验完整点t75、750格、3225注册、2493已持久化逻辑SGD、模型版本128；next_grid751，producer next_clock75/client0，无active_registration。模型133258380字节/private4690540字节，成对校验及状态hash通过；457源码文件与9份受保护旧资产一致。3225个已持久化key的外生抽样hash/R与OF配对相同。

运行进程16640在2026-10-14 22:46:22（北京时间）首次观察已不存在，最终meter/charge/EXECUTION_RESULT未产生。CATEGORY_LIVE和root反馈文件全部为NULL字节，mtime21:29:13；进程退出原因和确切时刻UNKNOWN。最后完整点21:28:10，不从日志恢复t75之后模型；日志本身也有不可读内容。不得将缺少终点误称T100。

已持久化SGD2493；丢失后缀真实物理工作UNKNOWN，物理范围保守2493—5000（上端仅原准入保护限额，非测量值）。未持久化区间为t75之后至未知退出，不能断言没有丢失训练。现存模型/private可作为后续恢复候选，尚未实施恢复。没有完整G800/W及本臂最终数值/在线2秒/根PID审计通过结论。

本调用2380CPU分配额和8安全余量共2388全部保守占用；不是实测费用或经审计的实际上界。保留6671.2秒启动至首次观察缺失的保守墙钟包络，不冒充运行实测时长。详情见[只读保存点核验](C:/Cursor/raven.mcs/{OUT.name}/INTERRUPTED_PREFIX_CHECK.json)。
''')
for key,strategy in [('FIXED2','fixed_time_2'),('NOQSTOP','OF-no-Q-stop')]:
 new('RESULT_'+key+'.md',f'# {strategy} — NOT_STARTED\n\n原策略与配置已冻结，新增SGD0关键路径检查通过。因fixed_time_0.5最终资源审计缺失且整批资源无法支持续行，本臂未启动，训练/回放/模型更新0。无G/W/J或Q贡献结果。保留策略，不删除失败臂，不用影子代替自主轨迹。WAITING_USER_REVIEW。\n')
append('STRATEGY_IMPLEMENTATION_REPORT.md','''OF首段t33.29发生root预算读数过期，在新注册执行前拒绝并保存。设施修复仅对原“stale”错误等待新读数，不扩大1秒有效期、不接受旧读数；实际模型/control与producer/RNG恢复前hash相等，已完成OF。首份设施归档检查与一次缺失脚本调用失败均保留费用，修复后v2外部脚本冻结通过。科学包冻结后未改。

本轮末次只读工具使用基础Python时触发numpy依赖缺失；改为直接加载未改的hashing文件、用相同成对内容条件读取原保存数据，再核验通过，首失败计费0.21875，成功4.171875。无训练/求解/回放。固定0.5的最终进程审计缺失属于未解决设施问题，未伪造方法验收通过。''')
append('RESOURCE_AND_BUDGET.md',f'''资源口径补正：上文job_wall_measured为通用ledger历史字段，含未审计fixed05的6671.2保守包络，不应把合计全部称实测。审计成功调用墙钟合计{sum(x['wall'] for x in b['charges'] if x['audit']):.6f}秒；未审计调用墙钟单列{sum(x['wall'] for x in b['charges'] if not x['audit']):.6f}秒。fixed05精确CPU、退出墙钟及PID归属终审均UNKNOWN，2388只是保守预算占用，不能证成完整根费用通过。

OF原首段＋恢复实际完整模型SGD3354；恢复段新增2220（3354−1134），不把父段1134再次算为物理训练。恢复首条滚动规划从0计数带入父段累计数，只用于预警；相应差分需扣父段1134SGD/原注册数，费用采用独立阶段账，不将原规划差分解释为新增实际工作。已保存原记录，未改历史结果。

整批物理工作保守范围5847—8354（OF3354＋fixed052493—5000）；其余两臂0。无法依据未知后缀给出更窄范围。GPU0，概率拟合0。''')
append('FAILURE_REPORT.md',f'''具体失败阶段：C的第二臂fixed_time_0.5，预期T100/1000格/4300注册且进程终审；实测仅t75/750格/3225注册可恢复，终审及费用文件缺失。系统运行中断的根因UNKNOWN，进程已消失且关键文件NULL是确定证据；不把它推断成科学效用差或信息违规。OF完整验收仍有效；fixed05仅完整前缀可读。fixed2、no-Q-stop和四臂效用筛查取消。

主对照固定.5的rW/rG/dG、两条路线及保护条件均NOT_EVALUATED；fixed2同样无完整指标，Q停止贡献NOT_EVALUATED。OF已有G=.945218023、W=.601503759仅单臂描述值，不形成新收益。已完成1/4，partial1/4，未启动2/4；PAIRING_INCOMPLETE，非PILOT_UTILITY_NOT_ESTABLISHED。

本报告时新批预算占用{b['charged_CPU']:.6f}/3000，剩{b['remaining_CPU']:.6f}；墙钟留账{b['wall_used']:.6f}/14400，剩{b['remaining_wall']:.6f}，末次交付核验仍继续计费。历史5522.609375加新{b['historical_plus_new_charged_CPU']:.6f}。未知费用不按0处理，不把旧预算余额转入。

恢复候选fixed05/trajectory/tick0750.complete.json已读验：下一格751、producer75/client0，实际model/Q/L/V/p历史及私有RNG俱存。t75之后所有未持久化模型/物理工作未知，不能从日志拼接。真正继续前必须建立新明确预算及核验损坏文件/进程终审原因，并实施独立恢复等值核验；本轮不自动重启。
''')
append('NEXT_STAGE_READINESS.md','''最小续行申请建议（尚未授权）：先只读确认中断/文件NULL原因与可恢复数据，修复可持续运行及最终费用落盘；科学策略/种子/阈值不改。然后恢复fixed.5 t75→T100，独立运行fixed2与no-Q-stop，并完成四臂终审与原筛查。按OF成功费用和fixed前缀观察规划：fixed余段200CPU、fixed2及noQ各600CPU、设施与三臂核验100CPU、保存增长/失败留额300CPU，共1800新增CPU秒/GPU0；新增执行墙钟建议9000秒。以上是申请量与增长留额，不是保证；每次完整在线2CPU和每臂累计5000物理SGD原限额保留，fixed续行需先确认原未知后缀的可用步数和墙钟，不自动将上限重置。

如果只能保留固定0.5未知物理上界5000，则原每臂步数限额下不能证明可继续；必须先找回审计证据确定实际物理SGD/累计执行墙钟，否则用户需明确决定是否终止该批或如何处理原未知额度，不能私自新增“可用”步数。剩余CPU名义数不构成完整运行授权。45002/45003、q拟合、B1、39条、正式确认均未启动。

本次只标OF及关键路径已验证；整批方法/自主效用验收未通过。预测性能RESULTS_NOT_REVALIDATED。保持WAITING_USER_REVIEW。''')
delivery=json.loads((OUT/'DELIVERY_CHECK.json').read_text());delivery.update(full_arms=1,partial_arms=1,not_started_arms=2,root_audit_missing=True,method_or_threshold_changed=False,unresolved=['interrupted root final audit','unknown fixed05 physical suffix','four-arm completeness'],files=[p.name for p in REPORT.iterdir()])
(OUT/'DELIVERY_CHECK.json').write_text(json.dumps(delivery,indent=2));print(json.dumps(delivery))
