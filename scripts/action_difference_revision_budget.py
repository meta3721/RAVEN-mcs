"""A-E batch: 300 CPU sec, B120 / evidence+mechanism180, zero collection."""
import argparse,json,time
import sys
from pathlib import Path
from windows_cpu_meter import run_metered
ROOT=Path(__file__).resolve().parents[1]
sys.path.insert(0,str(ROOT/'src'))
OUT=ROOT/'results_action_difference_revision_20261013'
REPORT=ROOT/'ccf-review-report/action_difference_revision_20261013'
def used(phase=None):
    rows=[json.loads(p.read_text()) for p in OUT.glob('charge_*.json')]
    return (30 if phase is None else 15)+sum(r['charged_CPU'] for r in rows if phase is None or r['phase']==phase)

def export_ledger():
    rows=[dict(label=p.stem.removeprefix('charge_'),**json.loads(p.read_text())) for p in sorted(OUT.glob('charge_*.json'))]
    measured=sum(r.get('job_CPU',0.)+(r.get('driver_CPU') or 0.) for r in rows)
    charged=used()
    ledger=dict(status='WAITING_USER_REVIEW',charged_CPU=charged,measured_disjoint_CPU=measured,
        conservative_failed_import_CPU=1.,inspection_and_delivery_reserve_CPU=30.,
        facility_charged_CPU=used('facility'),mechanism_charged_CPU=used('mechanism'),
        limits=dict(batch=300,facility=120,mechanism=180),
        prior_application_charged_CPU=4475.578125,cumulative_application_charged_CPU=4475.578125+charged,
        nominal_5_hour_remaining_CPU=18000-4475.578125-charged,
        historical_unmetered_actual_CPU='UNKNOWN',unmetered_current_inspection_actual_CPU='UNKNOWN; conservatively charged reserve',
        summed_metered_invocation_wall_seconds=sum(r.get('wall',0.) for r in rows),
        training=0,SGD=0,GPU=0,q_fit=0,new_trajectories=0,charges=rows)
    assert charged<=300 and ledger['facility_charged_CPU']<=120 and ledger['mechanism_charged_CPU']<=180
    (OUT/'FINAL_BUDGET.json').write_text(json.dumps(ledger,indent=2))
    (REPORT/'BUDGET_LEDGER.md').write_text(
        '# 本批封账\n\n状态：WAITING_USER_REVIEW。\n\n'
        f'本批计费 **{charged:.6f} CPU秒**；设施 {ledger["facility_charged_CPU"]:.6f}/120，'
        f'证据与机制 {ledger["mechanism_charged_CPU"]:.6f}/180，总上限300。\n\n'
        f'互斥进程树与驱动的实际测量合计 {measured:.6f} CPU秒。另计导入失败的保守费用1 CPU秒，'
        '以及检查、阅读、文档交付与微小封账尾部的保守预留30 CPU秒（各阶段15）。'
        '这31秒不是实际测量值；未逐项计量部分的实际CPU未知，不用保守费用冒充实耗。'
        '失败调用全部保留并计费，PID与内部Job费用没有重复相加。\n\n'
        f'计量调用墙钟合计 {ledger["summed_metered_invocation_wall_seconds"]:.6f}秒，'
        '不是含人工阅读和交付的全会话墙钟。单次保存墙钟2.990260秒；C有限分支内核墙钟5.171111秒。\n\n'
        f'旧计费4475.578125秒；累计计费 {ledger["cumulative_application_charged_CPU"]:.6f}秒；'
        f'原5小时申请名义余额 {ledger["nominal_5_hour_remaining_CPU"]:.6f}秒。历史实耗缺口仍为UNKNOWN。'
        '余额不构成下一批授权。训练、SGD、GPU、q拟合和新增轨迹均为0。\n\n'
        '[逐调用费用、墙钟与计量依据](C:/Cursor/raven.mcs/results_action_difference_revision_20261013/FINAL_BUDGET.json)。\n',encoding='utf-8')
if __name__=='__main__':
    p=argparse.ArgumentParser();p.add_argument('--initialize',action='store_true');p.add_argument('--phase',choices=['facility','mechanism']);p.add_argument('--label');p.add_argument('--cap',type=float,default=60)
    p.add_argument('--coordinated',action='store_true');p.add_argument('command',nargs=argparse.REMAINDER);a=p.parse_args()
    if a.initialize:
        OUT.mkdir(exist_ok=False);REPORT.mkdir(exist_ok=False)
        (OUT/'AUTHORIZATION.json').write_text(json.dumps(dict(CPU_limit=300,facility_limit=120,mechanism_limit=180,
            reserve_by_phase=15,prior_application_charged_CPU=4475.578125,SGD=0,GPU=0,q_fit=0,new_trajectories=0,
            v3_collection_paused=True,stages=['A','B','C','D_only_if_C_passes','E']),indent=2))
        print(str(OUT));raise SystemExit(0)
    phase_limit=120 if a.phase=='facility' else 180
    cap=min(a.cap,300-used()-5,phase_limit-used(a.phase)-5)
    if cap<1:raise RuntimeError('BUDGET_EXHAUSTED')
    cmd=a.command[1:] if a.command[:1]==['--'] else a.command
    if a.coordinated:
        from coordinated_windows_cpu_meter import run_coordinated_metered
        result=run_coordinated_metered(cmd,OUT/(a.label+'.log'),cpu_limit=cap,wall_limit=100,cwd=ROOT,
            budget_feedback=dict(path=str(OUT/'ROOT_BUDGET_LIVE.json'),prior_batch=used()+time.process_time(),
                prior_phase=used(a.phase)+time.process_time(),batch_limit=300,phase_limit=phase_limit))
    else:result=run_metered(cmd,OUT/(a.label+'.log'),cpu_limit=cap,wall_limit=100,cwd=ROOT)
    driver=time.process_time()
    with (OUT/('charge_'+a.label+'.json')).open('x') as f:json.dump(dict(phase=a.phase,charged_CPU=result['process_tree_cpu_seconds']+driver,
        job_CPU=result['process_tree_cpu_seconds'],driver_CPU=driver,wall=result['wall_seconds'],exit=result['returncode'],audit=result['audit_passed']),f,indent=2)
    export_ledger()
    print(json.dumps(dict(label=a.label,charged=used(),phase_charged=used(a.phase),exit=result['returncode'],audit=result['audit_passed'])))
    if not result['audit_passed'] or result['limit_reason']:raise RuntimeError('FACILITY_OR_BUDGET_STOP')
    raise SystemExit(result['returncode'])
