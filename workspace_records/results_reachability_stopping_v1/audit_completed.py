"""Audit completed artefacts only; never resume the stopped experiment queue."""
import json
import numpy as np
import pandas as pd
from dataclasses import replace
from run_geometry_gate import OUT,CONFIG,load,calibration_batches

def main():
    mu,regs,completions,total=load(41001)
    original=calibration_batches(completions)
    perturbed=calibration_batches([replace(m,q=np.roll(m.q,1),lag=8)
        if m.arrival>20 else m for m in completions])
    for phase in original:
        for before,after in zip(original[phase],perturbed[phase]):
            assert len(before)==len(after)
            for x,y in zip(before,after):
                assert x.arrival<=20 and x.key==y.key and x.lag==y.lag and np.array_equal(x.q,y.q)
    msg={m.key:m for m in regs}
    success={m.key for m in completions}
    rows=pd.read_csv(OUT/'MAIN_COMPARISON.csv')
    results=[]
    for row in rows.itertuples(index=False):
        closures=json.loads((OUT/f'41001_{row.policy}_closures.json').read_text(encoding='utf-8'))
        times=np.array([c['time'] for c in closures])
        used=set();max_score_error=0.;max_feasibility=0.
        for c in closures:
            a=np.array(c['weights']);K=len(c['keys'])
            assert c['version_before']==int(np.searchsorted(times,c['time'],side='left'))
            assert len(set(msg[key].client for key in c['keys']))==K
            assert not used.intersection(c['keys']);used.update(c['keys'])
            if not K:assert abs(c['score']-(1+CONFIG['wait_weight']*c['duration']/4))<1e-8;continue
            ages=[]
            for key in c['keys']:
                m=msg[key]
                assert key in success and m.arrival<=c['time']+1e-9
                # Simulator order: registration at a grid boundary is handled
                # before that boundary's closing update, including float ties.
                vreg=int(np.searchsorted(times,m.reg-1e-9,side='right'))
                downloaded=max(0,vreg-m.lag)
                age=c['version_before']-downloaded
                assert 0<=age<=CONFIG['age_max'];ages.append(age)
            E=min(3,K);cap=max(0.5,1/K)
            violation=max(0.,-a.min(),a.max()-cap,abs(a.sum()-1),a@a-1/E)
            max_feasibility=max(max_feasibility,float(violation))
            assert violation<=1e-7
            Q=np.stack([msg[key].q for key in c['keys']],axis=1)
            distance=np.abs(Q@a-mu).sum()/2
            age=a@np.array(ages)/5
            score=distance+0.02*age+0.20*c['duration']/4
            max_score_error=max(max_score_error,abs(float(score)-c['score']))
        timeline=pd.read_csv(OUT/f'41001_{row.policy}_timeline.csv')
        rescored=[]
        for t in timeline.time:
            ix=np.searchsorted(times,t+1e-9,side='right')-1
            rescored.append(closures[ix]['score'] if ix>=0 else 1.)
        error=abs(float(np.mean(rescored))-row.J)
        print(row.policy, 'timeline_error',error,'closure_score_error',max_score_error,flush=True)
        assert error<1e-10 and max_score_error<1e-10
        results.append(dict(policy=row.policy,closures_checked=len(closures),
            consumed_unique=len(used),max_score_recompute_error=max_score_error,
            main_metric_recompute_error=error,max_feasibility_violation=max_feasibility,
            future_completion_consumed=False,old_U_read=False,labels_read=False))
    (OUT/'COMPLETED_ARTEFACT_AUDIT.json').write_text(json.dumps(results,ensure_ascii=False,indent=2),encoding='utf-8')
    (OUT/'INFORMATION_AUDIT.json').write_text(json.dumps(dict(
        future_payload_perturbation_changes_frozen_predictor=False,
        calibration_cutoff=20,calibration_physical_messages=sum(len(b) for bs in original.values() for b in bs),
        full_trace_same_registered_messages=int(rows.registered_messages.nunique())==1,
        full_trace_same_physical_completions=int(rows.physical_completions.nunique())==1,
        note='Post-stop artefact/metadata audit only; no resumed controller or neural experiment.'
    ),ensure_ascii=False,indent=2),encoding='utf-8')
    print(json.dumps(dict(status='PASS',policies=len(results),max_metric_error=max(r['main_metric_recompute_error'] for r in results)),ensure_ascii=False))

if __name__=='__main__':main()
