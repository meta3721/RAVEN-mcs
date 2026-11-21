"""Close report accounting after the final metered writer exits; reserved envelope only."""
import pathlib,json,datetime,re,csv
OUT=pathlib.Path(__file__).resolve().parent;ROOT=OUT.parent;REPORT=ROOT/'ccf-review-report'/OUT.name.replace('results_','',1)
charges=[json.loads(p.read_text(encoding='utf-8-sig')) for p in sorted(OUT.glob('charge_*.json'))]
actual=sum(r['actual_CPU'] for r in charges if isinstance(r.get('actual_CPU'),(int,float)))
charged=50+sum(r['charged_CPU'] for r in charges)
now=datetime.datetime.now(datetime.timezone.utc);start=datetime.datetime.fromisoformat('2026-10-18T18:58:19.5477347+08:00');wall=(now-start).total_seconds()
resource=(REPORT/'RESOURCE_AND_BUDGET.md').read_text(encoding='utf-8-sig')
resource=re.sub(r'截至.*?，新增已审计完整根CPU=.*?秒；保守占用=',f'截至{now.isoformat()}，新增已审计完整根CPU={actual:.6f}秒；保守占用=',resource,count=1)
resource=re.sub(r'本轮预算记账=.*?/1000秒，余额=.*?秒。',f'本轮预算记账={charged:.6f}/1000秒，余额={1000-charged:.6f}秒。',resource,count=1)
resource=re.sub(r'活动保守包络=.*?/5400秒',f'活动保守包络={wall:.3f}/5400秒',resource,count=1)
resource+='\n最终交付计量后关闭：以下计量行计入上述合计；前文可能已有同标签，按标签唯一索引，不能重复相加。\n'
for row in charges:
 if row['label'].startswith('D'):resource+='- '+json.dumps(row,ensure_ascii=False)+'\n'
resource+='\n20秒交付保守包络覆盖非计量的编辑、定点状态读取、最终索引和本次关闭写入；这些实际CPU保持UNKNOWN，未伪装为测量。未用额度不自动转为新实验授权。\n'
phases=dict(A=30+sum(r['charged_CPU'] for r in charges if r['label'].startswith('A')),B=sum(r['charged_CPU'] for r in charges if r['label'].startswith('B')),C=sum(r['charged_CPU'] for r in charges if r['label']=='C'),delivery=20+sum(r['charged_CPU'] for r in charges if r['label'].startswith('D')))
resource+='\n分项预算记账（含已明确标注的保守占用，不等同于全部实测）：'+json.dumps(phases,ensure_ascii=False)+'秒；建议阶段额度A60/B120/C700/保存交付120均在1000总额内，额度不等于消耗。\n'
(REPORT/'RESOURCE_AND_BUDGET.md').write_text(resource,encoding='utf-8')
conclusion_path=REPORT/('DECISION_REPORT.md' if (REPORT/'DECISION_REPORT.md').exists() else 'FAILURE_REPORT.md')
conclusion=conclusion_path.read_text(encoding='utf-8-sig')
conclusion+=f'\n最终费用（交付计量后）：新增已审计完整根CPU {actual:.6f}秒，另保守占用50秒（实耗UNKNOWN），总预算记账{charged:.6f}/1000秒；活动墙钟包络{wall:.3f}/5400秒。按阶段和原始计量证据见RESOURCE_AND_BUDGET.md；历史费用不并入本轮。\n'
conclusion_path.write_text(conclusion,encoding='utf-8')
budget=dict(as_of=now.isoformat(),audited_actual_CPU=actual,unmetered_conservative_occupancy=50,charged_CPU=charged,remaining_CPU=1000-charged,active_wall_envelope=wall,phases=phases,charges=charges,state='WAITING_USER_REVIEW',new_experiments_running=False,full_P3=False,paper_modified=False)
(OUT/'BUDGET_FINAL.json').write_text(json.dumps(budget,indent=2),encoding='utf-8')
decision=json.loads((OUT/'DECISION.json').read_text(encoding='utf-8-sig'));decision.update(resource_budget=budget)
(OUT/'DECISION.json').write_text(json.dumps(decision,indent=2),encoding='utf-8')
assert charged<=1000 and wall<=5400
assert all(p.suffix=='.md' for p in REPORT.iterdir() if p.is_file())
print(json.dumps(dict(status=decision['status'],C_full_valid=decision['C_full_valid'],actual_CPU=actual,charged_CPU=charged,wall=wall,state='WAITING_USER_REVIEW'),ensure_ascii=False))
