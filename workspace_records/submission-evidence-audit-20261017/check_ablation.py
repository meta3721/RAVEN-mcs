from pathlib import Path
import re,csv,json
root=Path('C:/Cursor/raven.mcs/TO_OVERLEAF_paper_tmc_r1_clean')
t=(root/'main.tex').read_text(encoding='utf-8-sig')
t=t[t.index('\\label{tab:e4_ablation}'):t.index('\\end{table}',t.index('\\label{tab:e4_ablation}'))]
rows=list(csv.DictReader((root/'figure_data/FIG_E4_E4_COMPONENT_ABLATION.csv').open()))
mapping={(r['dataset'],r['component'],r['metric']):r for r in rows}
dataset=None; checks=[]
for line in t.splitlines():
    if 'multirow' in line:
        dataset='SensorScope' if 'SensorScope' in line else 'U-Air'
    if not line.startswith('&'):continue
    cells=line.split('&')[1:]
    component=cells[0].strip()
    for metric,cell in zip(['Delta_group','Delta_c_s','RMSE_mu','Tail_RMSE'],cells[1:]):
        r=mapping[(dataset,component,metric)]; v=float(r['relative_change_percent'])
        under='<0.001' in cell
        ok=abs(v)<.001 if under else abs(float(re.search(r'[+-]?\d+\.\d+',cell).group())-v)<=.000500001
        sig=('ast' in cell)==(r['holm_significant'].lower()=='true')
        checks.append({'dataset':dataset,'component':component,'metric':metric,'value_ok':ok,'significance_ok':sig})
result={'cells_checked':len(checks),'all_values_match_printed_precision':all(r['value_ok'] for r in checks),'all_significance_markers_match':all(r['significance_ok'] for r in checks),'checks':checks}
(Path(__file__).parent/'ablation-preservation.json').write_text(json.dumps(result,ensure_ascii=False,indent=2),encoding='utf-8')
print({k:v for k,v in result.items() if k!='checks'})
