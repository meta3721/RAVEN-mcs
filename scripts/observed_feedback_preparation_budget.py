"""Preparation-only 120 CPU-second ledger; no controller or acquisition entry."""
import argparse,json,sys,time
from pathlib import Path
from windows_cpu_meter import run_metered
ROOT=Path(__file__).resolve().parents[1]
OUT=ROOT/'results_observed_feedback_preparation_20261013'
REPORT=ROOT/'ccf-review-report/observed_feedback_preparation_20261013'

def used():
    return 20.+sum(json.loads(p.read_text())['charged_CPU'] for p in OUT.glob('charge_*.json'))

def ledger():
    rows=[dict(label=p.stem.removeprefix('charge_'),**json.loads(p.read_text())) for p in sorted(OUT.glob('charge_*.json'))]
    cost=used();assert cost<=120.
    value=dict(status='WAITING_USER_REVIEW',limit_CPU=120.,charged_CPU=cost,
        measured_disjoint_CPU=sum(r['job_CPU']+r['driver_CPU'] for r in rows),conservative_inspection_delivery_CPU=20.,
        inspection_actual_CPU='UNKNOWN; charged conservative reserve',prior_charged_CPU=4535.093750,
        cumulative_charged_CPU=4535.093750+cost,nominal_5hour_remaining_CPU=18000.-4535.093750-cost,
        historical_actual_gap='UNKNOWN',wall_invocations=sum(r['wall'] for r in rows),charges=rows,
        new_trajectories=0,SGD=0,GPU=0,q_fit=0,random_replay=0,production_controller_implementation=0)
    (OUT/'FINAL_BUDGET.json').write_text(json.dumps(value,indent=2))
    (REPORT/'BUDGET_LEDGER.md').write_text(
        '# 准备批预算\n\nWAITING_USER_REVIEW。\n\n'
        f'本批计费 **{cost:.6f} CPU秒 / 120**，其中外层互斥Job树+驱动实测 '
        f'{value["measured_disjoint_CPU"]:.6f} CPU秒，阅读、文件核对与交付保守计20秒。'
        '保守费用不是实测CPU；未逐项计量部分的实际CPU仍未知。失败调用计费，不重复计PID或内层Job。\n\n'
        f'计量调用墙钟合计 {value["wall_invocations"]:.6f}秒，不含人员设计时间。'
        f'旧累计4535.093750秒，本批后累计 {value["cumulative_charged_CPU"]:.6f}秒，'
        f'原5小时名义余额 {value["nominal_5hour_remaining_CPU"]:.6f}秒。历史实耗缺口未知，余额不授权下一批。\n\n'
        '新增轨迹、SGD、GPU、q拟合、随机回放、生产控制器实现均为0；未重复设施测试。\n\n'
        '[逐调用账与原始计量](C:/Cursor/raven.mcs/results_observed_feedback_preparation_20261013/FINAL_BUDGET.json)。\n',encoding='utf-8')

if __name__=='__main__':
    p=argparse.ArgumentParser();p.add_argument('--initialize',action='store_true');p.add_argument('--label');p.add_argument('--cap',type=float,default=30.)
    p.add_argument('command',nargs=argparse.REMAINDER);a=p.parse_args()
    if a.initialize:
        OUT.mkdir(exist_ok=False);REPORT.mkdir(exist_ok=False)
        (OUT/'AUTHORIZATION.json').write_text(json.dumps(dict(scope='one method specification and evidence plan only',
            CPU_limit=120,conservative_reserve=20,prior_charged_CPU=4535.093750,
            production_controller=0,training=0,q_fit=0,random_replay=0,new_trajectories=0),indent=2));ledger();raise SystemExit(0)
    cap=min(a.cap,120.-used()-3.)
    if cap<1.:raise RuntimeError('PREPARATION_BUDGET_EXHAUSTED')
    cmd=a.command[1:] if a.command[:1]==['--'] else a.command
    result=run_metered(cmd,OUT/(a.label+'.log'),cpu_limit=cap,wall_limit=60,cwd=ROOT)
    driver=time.process_time()
    with (OUT/('charge_'+a.label+'.json')).open('x') as f:json.dump(dict(charged_CPU=result['process_tree_cpu_seconds']+driver,
        job_CPU=result['process_tree_cpu_seconds'],driver_CPU=driver,wall=result['wall_seconds'],exit=result['returncode'],audit=result['audit_passed']),f,indent=2)
    ledger();print(json.dumps(dict(label=a.label,charged=used(),exit=result['returncode'],audit=result['audit_passed'])))
    if not result['audit_passed'] or result['limit_reason']:raise RuntimeError('PREPARATION_METER_OR_BUDGET_STOP')
    raise SystemExit(result['returncode'])
