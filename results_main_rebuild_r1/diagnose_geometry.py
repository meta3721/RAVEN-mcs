"""Label-free feasible-set audit using real first-cycle client compositions.

Fixed-K rows are composition diagnostics from sorted distinct-client subsets of
natural windows, not newly generated controlled participation experiments.
No forecasts or full RAVEN training are produced by this script.
"""
from common import *
import cvxpy as cp
from functools import lru_cache
import time

TOL=1e-7
SOLVES=[]
PROJECTION_CHECKS=[]

def constraints(a,E,cap):
    return [a>=0,cp.sum(a)==1,a<=cap,cp.sum_squares(a)<=1/E]

def violation(a,E,cap):
    return max(0.,float(-a.min()),float(a.max()-cap),abs(float(a.sum()-1)),float(a@a-1/E))

@lru_cache(maxsize=None)
def extrema(v,E,cap):
    v=np.array(v); K=len(v)
    if abs(E-K)<1e-10 or abs(cap-1/K)<1e-10 or np.ptp(v)<1e-10:
        val=float(v.mean());return val,val
    a=cp.Variable(K);out=[]
    for sign in (1.,-1.):
        p=cp.Problem(cp.Minimize(sign*v@a),constraints(a,E,cap))
        p.solve(solver='CLARABEL',tol_gap_abs=1e-9,tol_feas=1e-9,tol_gap_rel=1e-9,max_iter=250)
        if p.status!='optimal' or a.value is None:raise RuntimeError(('extrema',p.status,K,E,cap))
        err=violation(a.value,E,cap)
        if err>TOL:raise RuntimeError(('extrema violation',err))
        SOLVES.append(dict(kind='range',status=p.status,violation=err))
        out.append(float(v@a.value))
    return out[0],out[1]

def projection(beta,E,cap):
    K=len(beta)
    if abs(E-K)<1e-10 or abs(cap-1/K)<1e-10:return np.ones(K)/K
    if violation(beta,E,cap)<=1e-10:return beta.copy()
    # KKT form: clip(s*beta-lambda,0,cap), s=1/(1+2*nu).
    # First capped-simplex projection; then scalar search for active ESS.
    def simplex(s):
        scaled=s*beta;low=float(scaled.min()-cap);high=float(scaled.max())
        for _ in range(70):
            lam=(low+high)/2
            if np.clip(scaled-lam,0,cap).sum()>1:low=lam
            else:high=lam
        lam=(low+high)/2
        return np.clip(scaled-lam,0,cap),lam
    answer,lam=simplex(1.);s=1.
    if answer@answer>1/E:
        low,high=0.,1.
        for _ in range(65):
            s=(low+high)/2;answer,lam=simplex(s)
            if answer@answer>1/E:high=s
            else:low=s
        s=low;answer,lam=simplex(s)
    err=violation(answer,E,cap)
    if err>TOL:raise RuntimeError(('projection violation',err))
    reduced_gradient=answer/s-beta+lam/s
    interior=(answer>1e-8)&(answer<cap-1e-8)
    residual=max(float(np.max(np.abs(reduced_gradient[interior]),initial=0)),
        float(np.max(-reduced_gradient[answer<=1e-8],initial=0)),
        float(np.max(reduced_gradient[answer>=cap-1e-8],initial=0)))
    if residual>1e-6:raise RuntimeError(('projection KKT',residual))
    PROJECTION_CHECKS.append(dict(violation=err,KKT_residual=residual))
    return answer

def one(name,seed,w,condition,indices,E,cap,ranges):
    M=np.asarray(w['M'],dtype=float)[:,indices];mu=np.asarray(w['mu'],dtype=float)
    K=len(indices);beta=np.asarray(w['beta'],dtype=float)[indices];beta/=beta.sum()
    if not np.allclose(M.sum(axis=0),1.,atol=1e-7):raise RuntimeError('non-normalized composition')
    rank=int(np.linalg.matrix_rank(M-M.mean(axis=1,keepdims=True),tol=1e-10))
    Ws=[]; positive=mu>0
    for g,v in enumerate(M):
        lo,hi=extrema(tuple(np.round(np.sort(v),12)),round(E,12),round(cap,12));width=max(0.,hi-lo);Ws.append(width)
        ranges.append(dict(dataset=name,seed=seed,window_id=w['window_id'],condition=condition,K=K,E=E,cap=cap,
            group_index=g,mu=mu[g],minimum=lo,maximum=hi,W=width))
    Ws=np.array(Ws);adjustable=positive&(Ws>=.01)
    proj=projection(beta,E,cap);u=np.ones(K)/K
    return dict(dataset=name,seed=seed,window_id=w['window_id'],condition=condition,K=K,E=E,ess_ratio=E/K,cap=cap,
        composition_rank=rank,ess_displacement_upper_bound=float(np.sqrt(max(0,1/E-1/K))),
        singleton=abs(E-K)<1e-10 or abs(cap-1/K)<1e-10,n_adjustable_positive_groups=int(adjustable.sum()),
        adjustable_target_mass=float(mu[adjustable].sum()),unreachable_target_mass=float(mu[(M.max(axis=1)<=1e-12)&positive].sum()),
        max_group_range=float(Ws.max()),high_freedom=rank>=1 and adjustable.sum()>=2,
        beta_violates=violation(beta,E,cap)>1e-7,projection_distance=float(np.linalg.norm(proj-beta)),
        projection_to_uniform_l1=float(np.abs(proj-u).sum()),projected_ESS=float(1/(proj@proj)),projected_max_weight=float(proj.max()),
        gate=int(w['g_r']),beta_scope='natural payload' if condition=='natural_original' else 'renormalized subset; diagnostic only')

def main():
    t=time.monotonic();rows=[];ranges=[];supply=[]
    save(OUT/'P2_GEOMETRY_CONFIG.json',dict(seeds=list(SEEDS),source='first-cycle exact production payloads',
        solver='CLARABEL',solver_abs_feas_gap=1e-9,acceptance_feasibility_tolerance=TOL,
        fixed_K_selection='first K distinct clients in sorted client_id order in every natural window with at least K active clients',
        fixed_K_values=[4,8,16],ess_ratios=[.25,.5,.8],cap_factor=2,cap_sensitivity=[1.5,4],
        projection_solver='capped-simplex/ESS dual bisection, feasibility and KKT checked',
        labels_used=False,controlled_trace_generated=False,forecast_evidence=False))
    for name in DATASETS:
        for seed in SEEDS:
            cache=torch.load(OUT/'prepared'/name/f'seed{seed}'/'uniform_cache.pt',weights_only=False)
            for w in cache['windows']:
                if w['phase']!='first' or not w['clients']:continue
                K=len(w['clients']);ix=np.arange(K)
                rows.append(one(name,seed,w,'natural_original',ix,min(3,K),min(1.,max(.5,1/K)),ranges))
                if name!='traffic':continue
                for k in (4,8,16):
                    if K<k:continue
                    for ratio in (.25,.5,.8):
                        rows.append(one(name,seed,w,f'fixedK{k}_ESS{ratio:g}_cap2K',ix[:k],ratio*k,2/k,ranges))
                    if k==8:
                        for factor in (1.5,4):
                            rows.append(one(name,seed,w,f'fixedK8_ESS0.5_cap{factor:g}K',ix[:k],4,factor/8,ranges))
            print('GEOMETRY',name,seed,'complete',round(time.monotonic()-t,1),flush=True)
    f=pd.DataFrame(rows);f.to_csv(OUT/'P2_GEOMETRY_WINDOWS.csv',index=False)
    pd.DataFrame(ranges).to_csv(OUT/'P2_GEOMETRY_GROUP_RANGES.csv',index=False)
    summary=f.groupby(['dataset','condition'],as_index=False).agg(windows=('K','size'),K_min=('K','min'),K_max=('K','max'),
        singleton_share=('singleton','mean'),high_freedom_share=('high_freedom','mean'),
        mean_adjustable_mass=('adjustable_target_mass','mean'),mean_unreachable_mass=('unreachable_target_mass','mean'),
        beta_violation_share=('beta_violates','mean'),mean_projection_distance=('projection_distance','mean'),gate_on_share=('gate','mean'))
    summary.to_csv(OUT/'P2_GEOMETRY_SUMMARY.csv',index=False)
    save(OUT/'P2_GEOMETRY_AUDIT.json',dict(solves=len(SOLVES),statuses=sorted(set(x['status'] for x in SOLVES)),
        max_feasibility_violation=max((x['violation'] for x in SOLVES),default=0),
        projections_checked=len(PROJECTION_CHECKS),max_projection_violation=max((x['violation'] for x in PROJECTION_CHECKS),default=0),
        max_projection_KKT_residual=max((x['KKT_residual'] for x in PROJECTION_CHECKS),default=0),
        projection_solver_amendment='Initial CLARABEL projection attempt returned optimal_inaccurate; no incomplete result accepted. Recomputed all projections with exact KKT dual form.',
        K16_natural_supply=0 if not any(x['K']>=16 for x in rows if x['condition']=='natural_original') else 'present',
        K16_note='No natural development payload has 16 active clients; controlled K16 schedule was not generated after P1 stop.',
        distinct_range_problems=extrema.cache_info().misses,seconds=time.monotonic()-t,
        evidence_scope='geometry and pure projection only; no update differences or forecasts'))
    print(summary.to_string(index=False),flush=True)

if __name__=='__main__':main()
