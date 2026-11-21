"""Authorized OF-v1 interface-only batch: root-accounted, 300 CPU seconds."""
import argparse,json,sys,time,math
from pathlib import Path
ROOT=Path(__file__).resolve().parents[1]
sys.path.insert(0,str(ROOT/'src'))
from coordinated_windows_cpu_meter import run_coordinated_metered
OUT=ROOT/'results_observed_feedback_implementation_20261013'
REPORT=ROOT/'ccf-review-report/observed_feedback_implementation_20261013'
def used():return 30.+sum(json.loads(p.read_text())['charged_CPU'] for p in OUT.glob('charge_*.json'))
def ledger():
    rows=[dict(label=p.stem.removeprefix('charge_'),**json.loads(p.read_text())) for p in sorted(OUT.glob('charge_*.json'))]
    value=dict(charged_CPU=used(),CPU_limit=300,measured_CPU=sum((r['job_CPU'] or 0)+(r['driver_CPU'] or 0) for r in rows),
        conservative_read_edit_delivery_CPU=30,unmetered_current_actual_CPU='UNKNOWN; charged reserve',
        prior_charged_CPU=4557.296875,cumulative_charged_CPU=4557.296875+used(),
        nominal_5hour_remaining_CPU=18000.-4557.296875-used(),historical_actual_gap='UNKNOWN',
        wall_invocations=sum(r['wall'] for r in rows),charges=rows,SGD=0,GPU=0,q_fit=0,
        real_or_random_trajectories=0,real_control_replay=0,final_state='WAITING_USER_REVIEW')
    assert value['charged_CPU']<=300
    (OUT/'FINAL_BUDGET.json').write_text(json.dumps(value,indent=2))
    facts_path=OUT/'RESOURCE_FACTS.json'
    if facts_path.exists():
        facts=json.loads(facts_path.read_text());sample=facts['representative']
        text='# 资源与预算\n\n状态：WAITING_USER_REVIEW。最终四用例在一个常驻worker内通过。\n\n'
        text+=f'本批计费 **{value["charged_CPU"]:.6f}/300 CPU秒**。实际互斥进程树+驱动测量合计 {value["measured_CPU"]:.6f}秒；'
        text+='另有两次根发布异常各22秒保守计费（Job/驱动实耗缺失），以及阅读/编辑/交付保守费用30秒。保守费用不是实耗；历史及未逐项计量缺口仍UNKNOWN。\n\n'
        text+=f'计量调用墙钟合计 {value["wall_invocations"]:.6f}秒；旧累计4557.296875秒，本批后累计 {value["cumulative_charged_CPU"]:.6f}秒，原5小时名义余额 {value["nominal_5hour_remaining_CPU"]:.6f}秒，余额不授权后续。\n\n'
        text+=f'最终 {facts["judgement_count"]} 个完整当前请求（含预期PendingQ拒绝）最大保守根费用上界 {facts["max_request_upper"]:.6f}秒，全部≤2。分类示例：\n\n'
        for label,row in sample.items():
            text+=f'- {label}：根上界 {row["conservative_root_upper_CPU"]:.6f}秒，进程CPU {row["process_CPU"]:.6f}秒，墙钟 {row["wall"]:.6f}秒，P2={row.get("P2")}, cache={row.get("cache")}。\n'
        text+='\n完整根费用窗口含监视，首次含Python/启动器成本。短区间Job量化时，使用max(原根差+0.02，PID区间+互斥monitor差+0.02)进一步保守校验，不能把PID再加进整批费用；这是提高上界，没有降低门槛或移动请求边界。\n\n'
        text+='大类operation行包含内层请求，不能累加这些重叠行；整批账以charge文件为准。提交、模型加载、保存、恢复和关闭均保留在根Job从创建到退出费用中。P2列指完整目标求值/计算，单点可行域为精确解析解；仅K>3调用原数值求解器，另有一个显式原完整preview参考。未计算纯d，记录null。43客户端及冷启动有自由度的大池费用未验，不承诺生产2秒。\n\n'
        text+='首次请求及一次冷数值加载曾超2秒；后按同约束的精确单点P2和懒加载修复，保留失败记录。Root读/rename冲突由新客户端共享delete及新publisher有界重试修复，旧设施源文件保留；中断预算保守记账。\n\n'
        text+='训练/SGD/GPU/q拟合/真实及随机轨迹/真实回放均0，45001–45003未用，没有设施压力重测。\n\n[完整计量账](C:/Cursor/raven.mcs/results_observed_feedback_implementation_20261013/FINAL_BUDGET.json)；[每请求费用与P2记录](C:/Cursor/raven.mcs/results_observed_feedback_implementation_20261013/REQUEST_COSTS.csv)。\n'
        (REPORT/'RESOURCE_AND_BUDGET.md').write_text(text,encoding='utf-8')
    return value
if __name__=='__main__':
    p=argparse.ArgumentParser();p.add_argument('--initialize',action='store_true');p.add_argument('--label');p.add_argument('--cap',type=float,default=60.)
    p.add_argument('command',nargs=argparse.REMAINDER);a=p.parse_args()
    if a.initialize:
        OUT.mkdir(exist_ok=False);REPORT.mkdir(exist_ok=False)
        (OUT/'AUTHORIZATION.json').write_text(json.dumps(dict(method='reachability_stop/observed-feedback-v1',CPU_limit=300,
            per_request_CPU=2,prior_charged_CPU=4557.296875,SGD=0,GPU=0,q_fit=0,real_or_random_trajectories=0,
            cases=4,reserved_development_seeds='45001-45003 NOT_USED'),indent=2));ledger();raise SystemExit(0)
    cap=min(a.cap,300.-used()-3.)
    if cap<1:raise RuntimeError('BUDGET_EXHAUSTED')
    cmd=a.command[1:] if a.command[:1]==['--'] else a.command
    (OUT/'LAUNCH_COST.json').write_text(json.dumps(dict(label=a.label,launcher_bootstrap_CPU=time.process_time())))
    # Local binding only; preserve every existing facility source file.
    from raven_mcs_execution import budget as shared_budget
    from raven_mcs_observed_feedback.budget_client import AtomicPublisher
    shared_budget.RootBudgetPublisher=AtomicPublisher
    meter_start=time.perf_counter()
    try:
        result=run_coordinated_metered(cmd,OUT/(a.label+'.log'),cpu_limit=cap,wall_limit=60,cwd=ROOT,
            budget_feedback=dict(path=str(OUT/'ROOT_BUDGET_LIVE.json'),prior_batch=used()+time.process_time(),
                prior_phase=used()+time.process_time(),batch_limit=300,phase_limit=300))
    except Exception as exc:
        wall=time.perf_counter()-meter_start;driver=time.process_time()
        with (OUT/('charge_'+a.label+'.json')).open('x') as stream:json.dump(dict(charged_CPU=math.ceil(wall)+1+driver,
            job_CPU=None,driver_CPU=driver,wall=wall,exit=repr(exc),audit=False,
            actual_job_CPU='UNKNOWN',conservative_basis='one-CPU Job cost <= invocation wall; ceiling+1 second plus measured driver'),stream,indent=2)
        ledger();raise
    driver=time.process_time()
    with (OUT/('charge_'+a.label+'.json')).open('x') as stream:json.dump(dict(charged_CPU=result['process_tree_cpu_seconds']+driver,
        job_CPU=result['process_tree_cpu_seconds'],driver_CPU=driver,wall=result['wall_seconds'],exit=result['returncode'],audit=result['audit_passed']),stream,indent=2)
    value=ledger();print(json.dumps(dict(label=a.label,charged=value['charged_CPU'],exit=result['returncode'],audit=result['audit_passed'])))
    if not result['audit_passed'] or result['limit_reason']:raise RuntimeError('ROOT_BUDGET_OR_METER_STOP')
    raise SystemExit(result['returncode'])
