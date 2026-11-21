"""Two predeclared exact scalar calculations; not a controller or a replay."""
import json,hashlib
from fractions import Fraction as F
from observed_feedback_preparation_budget import OUT,REPORT

if __name__=='__main__':
    spec=REPORT/'METHOD_SPEC_CANDIDATE.md'
    inputs=dict(spec_sha256=hashlib.sha256(spec.read_bytes()).hexdigest(),
        theta='1/50',kappa='1/10',nu='1/5',age_weight='1/50',eta='1/100',
        mu=['1/2','1/2'],omega=['4/5','1/5'],K=3,uniform_weights=['1/3']*3,
        identical_columns=True,age='2/5',last_ell='3/10',last_age='2/5',elapsed='3/10',D='4',
        histories=[['3/10','0'],['0','3/10']],
        role='generic-simplex exact arithmetic only; not Traffic or executed P2; no stochastic or real replay')
    with (OUT/'ARITHMETIC_INPUTS_FROZEN.json').open('x') as stream:json.dump(inputs,stream,indent=2)
    mu=list(map(F,inputs['mu']));omega=list(map(F,inputs['omega']))
    ell=sum(abs(x-y) for x,y in zip(omega,mu))/2
    c=ell+F(inputs['age_weight'])*F(inputs['age'])
    last=F(inputs['last_ell'])+F(inputs['age_weight'])*F(inputs['last_age'])
    u=F(inputs['elapsed'])/F(inputs['D']);theta=F(inputs['theta']);eta=F(inputs['eta'])
    rows=[]
    for h in inputs['histories']:
        Q=list(map(F,h));Qhat=[q/(1+sum(Q)) for q in Q]
        b=sum(q*(o-m) for q,o,m in zip(Qhat,omega,mu))
        B=last-c+F(inputs['kappa'])*b+F(inputs['nu'])*u
        without_Q=last-c+F(inputs['nu'])*u
        Qnext=[max(F(0),q+eta*(m-o)) for q,m,o in zip(Q,mu,omega)]
        drift=(sum(x*x for x in Qnext)-sum(x*x for x in Q))/2
        upper=eta*sum(q*(m-o) for q,m,o in zip(Q,mu,omega))+eta*eta*sum((m-o)**2 for m,o in zip(mu,omega))/2
        assert drift<=upper
        row=dict(Q=h,ell=str(ell),c=str(c),b=str(b),B_exact=str(B),B=float(B),
            threshold=float(theta+F(1,10**7)),inequality_holds=B>=theta+F(1,10**7),
            without_Q_B=str(without_Q),without_Q_inequality=without_Q>=theta+F(1,10**7),
            next_Q=list(map(str,Qnext)),drift=str(drift),drift_upper=str(upper))
        rows.append(row)
    assert rows[0]['inequality_holds'] and not rows[1]['inequality_holds']
    assert not any(row['without_Q_inequality'] for row in rows)
    result=dict(status='PASS_SPEC_ALGEBRA_ONLY',exact_fraction_arithmetic=True,history_effect=True,
        actual_P2_execution=False,production_controller=False,Traffic_empirical_evidence=False,
        generic_analytic_singleton_feasible_set=True,random_replay=0,SGD=0,q_fit=0,new_trajectories=0,rows=rows)
    with (OUT/'ARITHMETIC_RESULT.json').open('x') as stream:json.dump(result,stream,indent=2)
    print(json.dumps(result))
