"""Stage A: exact prior-branch accounting, no new prediction or trajectory."""
import csv,json,math
from collections import Counter
from pathlib import Path
from action_difference_revision_budget import ROOT,OUT
from raven_mcs.utils.hashing import sha256_file
OLD=ROOT/'results_re_interval_development_44001_20261013'
if __name__=='__main__':
    rows=list(csv.DictReader((OLD/'DECISION_METRICS.csv').open(encoding='utf-8-sig')))
    D=[r for r in rows if 20<float(r['time'])<100]
    counts=Counter(r['classification'] for r in D)
    differences=sum(r['difference']=='True' for r in D);activation=sum(r['proven']=='True' for r in D)
    mechanism=sum(r['mechanism_difference']=='True' for r in D)
    time_points=[float(r['time']) for r in D]
    assert len(rows)==989 and len(D)==789 and len(set(time_points))==789
    assert time_points==[round(20+.1*i,10) for i in range(1,790)]
    assert differences==activation==mechanism==0
    assert counts=={'CPU_TIMEOUT':346,'UNKNOWN_FIXED_TIME_2':427,'RULE_FORCED':16}
    assert all(r['P2']=='' and r['cache']=='' for r in D if r['classification']=='CPU_TIMEOUT')
    assert all((OLD/r['snapshot']).is_file() for r in rows)
    summary=json.loads((OLD/'DEVELOPMENT_SUMMARY.json').read_text())
    ks=summary['k_distribution'];total=sum(ks.values());zero=sum(n for k,n in ks.items() if k.startswith('0/'))
    assert (zero,total)==(10183,10496)
    result=dict(status='PASS',observed_D=789,complete_D=799,missing_D=10,total_difference=0,activation=0,
        mechanism_difference=0,classification=dict(counts),same_branch_max_difference=10,
        same_branch_max_ratio=10/799,required_difference_count=math.ceil(.05*799),
        k_zero=zero,k_total=total,k_zero_ratio=zero/total,
        k_denominator='tracked plan-scenario records, not decisions',timeout_ratio=346/789,
        T100_complete=False,source_csv_sha256=sha256_file(OLD/'DECISION_METRICS.csv'))
    (OUT/'A_REVIEW.json').write_text(json.dumps(result,indent=2))
    protected={str(p):sha256_file(p) for base in (OLD,ROOT/'ccf-review-report/re_interval_development_44001_20261013') for p in base.rglob('*') if p.is_file()}
    (OUT/'PROTECTED_BEFORE.json').write_text(json.dumps(protected,indent=2))
    print(json.dumps(result))
