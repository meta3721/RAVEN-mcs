"""Causal label-free stopping gate. Not full RAVEN or predictive evidence."""
from __future__ import annotations

import os
os.environ.setdefault('OMP_NUM_THREADS', '2')
os.environ.setdefault('OPENBLAS_NUM_THREADS', '2')
os.environ.setdefault('MKL_NUM_THREADS', '2')
import json
import math
import time
from pathlib import Path
from dataclasses import dataclass

import numpy as np
import pandas as pd
import cvxpy as cp

ROOT = Path('C:/Cursor/raven.mcs')
OUT = Path(__file__).resolve().parent
CONFIG = dict(method='target_gain_stop', version='v1', stage='G2_geometry',
    dataset='traffic', seeds=[41001,41002,41003], grid=0.1,
    warmup=20., horizon=100., deadline=4., ess=3., cap=0.5,
    age_max=5, age_weight=0.02, wait_weight=0.20, scenarios=4,
    minimum_distinct_clients=3, minimum_gain=0.02, scoring_tolerance=1e-7,
    cpu_budget_seconds=3600, neural_training=False, old_U_used=False,
    baselines=['fixed_time_1','fixed_time_2','fixed_time_4',
               'fixed_K8_timeout4','age_count_trigger'],
    composition='empirical observed group proportions; not corrected RAVEN',
    scope='controlled geometry and waiting proxy, no prediction evidence')
PROCESS_START = time.process_time()

def save(name, value):
    (OUT/name).write_text(json.dumps(value,ensure_ascii=False,indent=2,allow_nan=False),encoding='utf-8')

@dataclass
class Msg:
    key: str
    client: str
    reg: float
    arrival: float
    q: np.ndarray
    lag: int

@dataclass
class Candidate:
    msg: Msg
    downloaded: int

class Geometry:
    def __init__(self, mu):
        self.mu=mu
        self.cache={}
        self.solves=0
        self.max_violation=0.
    def solve(self, candidates, version):
        if not candidates:
            return 1., 1., 0., np.zeros(0)
        ages=np.array([version-c.downloaded for c in candidates],float)
        Q=np.stack([c.msg.q for c in candidates],axis=1)
        key=(Q.tobytes(), ages.tobytes())
        if key in self.cache:return self.cache[key]
        K=len(candidates); E=min(CONFIG['ess'],K); cap=max(CONFIG['cap'],1/K)
        if K<=3:
            a=np.ones(K)/K
        else:
            # Rows absent from the pool contribute a known fixed L1 constant.
            present=Q.sum(axis=1)>0
            a_var=cp.Variable(K)
            problem=cp.Problem(cp.Minimize(0.5*cp.norm1(Q[present]@a_var-self.mu[present])+
                CONFIG['age_weight']*(ages/CONFIG['age_max'])@a_var),
                [a_var>=0,cp.sum(a_var)==1,a_var<=cap,cp.sum_squares(a_var)<=1/E])
            problem.solve(solver='CLARABEL',tol_gap_abs=1e-8,tol_feas=1e-9,
                          tol_gap_rel=1e-8,max_iter=200)
            if problem.status!='optimal' or a_var.value is None:
                raise RuntimeError('unaccepted geometry solve: '+str(problem.status))
            a=np.array(a_var.value,float)
            self.solves+=1
        violation=max(0.,-float(a.min()),float(a.max()-cap),
                      abs(float(a.sum()-1)),float(a@a-1/E))
        self.max_violation=max(self.max_violation,violation)
        if violation>1e-7:raise RuntimeError('weight violation '+str(violation))
        # Normalize minute solver error, then recheck the actual evaluated weights.
        a=np.maximum(a,0);a/=a.sum()
        if max(float(a.max()-cap),float(a@a-1/E))>1e-7:
            raise RuntimeError('normalization violates constraints')
        distance=float(np.abs(Q@a-self.mu).sum()/2)
        age=float(a@ages/CONFIG['age_max'])
        result=(distance+CONFIG['age_weight']*age,distance,age,a)
        self.cache[key]=result
        return result

def load(seed):
    base=ROOT/'results_main_rebuild_r1'
    atomic=pd.read_parquet(base/'data/traffic/atomic_units.parquet',
                          columns=['unit_id','target_group','split','support_flag'])
    groups=sorted(atomic.target_group.astype(str).unique()); gi={g:i for i,g in enumerate(groups)}
    test=atomic.loc[(atomic.split=='test')&atomic.support_flag.astype(bool)]
    counts=test.target_group.astype(str).value_counts()
    mu=np.array([counts.get(g,0)/len(test) for g in groups],float)
    if abs(mu.sum()-1)>1e-12:raise RuntimeError('mu mass')
    lookup=dict(zip(atomic.unit_id.astype(str),atomic.target_group.astype(str)))
    split=dict(zip(atomic.unit_id.astype(str),atomic.split.astype(str)))
    # Intentionally omit old U, old tau/version, oracle variables and labels.
    columns=['window_id','client_id','registration_time','arrival_time',
             'compute_success','network_success','compute_duration','network_duration','observed_unit_ids']
    events=pd.read_parquet(base/f'eventtraces/traffic/seed{seed}/training_eventtrace/events.parquet',columns=columns)
    if np.max(np.abs(events.arrival_time-events.registration_time-events.compute_duration-events.network_duration))>1e-10:
        raise RuntimeError('service timestamps incompatible')
    rng=np.random.default_rng(seed+830000)
    lags=np.array([int(rng.integers(6,9)) if rng.random()<0.2 else int(rng.integers(0,6)) for _ in range(len(events))])
    regs=[];completions=[]
    for pos,r in enumerate(events.itertuples(index=False)):
        uids=json.loads(r.observed_unit_ids)
        if any(split[uid]!='train' for uid in uids):raise RuntimeError('non-training observed UID')
        q=np.zeros(len(groups))
        for uid in uids:q[gi[lookup[uid]]]+=1
        if uids:q/=len(uids)
        m=Msg(f'{int(r.window_id)}::{r.client_id}',str(r.client_id),float(r.registration_time),
              float(r.arrival_time),q,int(lags[pos]))
        regs.append(m)
        if uids and bool(r.compute_success) and bool(r.network_success):completions.append(m)
    regs.sort(key=lambda m:(m.reg,m.key));completions.sort(key=lambda m:(m.arrival,m.key))
    return mu,regs,completions,len(events)

def calibration_batches(completions):
    # Freeze at t=20; never includes a completion after the warmup boundary.
    bins=[[] for _ in range(200)]
    for m in completions:
        if m.arrival<=CONFIG['warmup']:
            idx=min(199,int(math.ceil(m.arrival*10-1e-9))-1)
            # The predictor receives observed warmup version age, not the
            # untruncated simulator lag variable unavailable to the controller.
            registration_version=int(math.floor(m.reg+1e-10))
            downloaded=max(0,registration_version-m.lag)
            reception_version=int(math.floor(m.arrival-1e-10))
            observed_age=max(0,reception_version-downloaded)
            visible=Msg(m.key,m.client,m.reg,m.arrival,m.q,observed_age)
            bins[max(0,idx)].append(visible)
    # Public registration clock is periodic; retain empirical within-clock phase.
    phases={phase:[bins[i] for i in range(200) if i%10==phase] for phase in range(10)}
    return phases

def execute(policy,seed,mu,regs,completions,phases):
    geom=Geometry(mu);pool={};downloads={};version=0;open_time=0.
    ir=ic=0;closures=[];consumed=set();expired=0;superseded=0
    last_score=1.; last_distance=1.; last_age=0.
    evaluations=[];decision_log=[]
    for tick in range(1,1001):
        now=round(tick/10,10)
        if time.process_time()-PROCESS_START>CONFIG['cpu_budget_seconds']:
            raise RuntimeError('CPU_BUDGET')
        # Process registrations and completions in physical order since last tick.
        while True:
            tr=regs[ir].reg if ir<len(regs) else math.inf
            tc=completions[ic].arrival if ic<len(completions) else math.inf
            if min(tr,tc)>now+1e-10:break
            if tr<=tc:
                m=regs[ir];downloads[m.key]=max(0,version-m.lag);ir+=1
            else:
                m=completions[ic];ic+=1
                if m.key not in downloads:raise RuntimeError('completion before registration')
                dl=downloads[m.key]
                if version-dl>CONFIG['age_max']:expired+=1;continue
                previous=pool.get(m.client)
                if previous is not None:
                    superseded+=1
                    if previous.msg.reg>m.reg:continue
                pool[m.client]=Candidate(m,dl)
        for cid in list(pool):
            if version-pool[cid].downloaded>CONFIG['age_max']:
                del pool[cid];expired+=1
        candidates=sorted(pool.values(),key=lambda c:c.msg.client)
        elapsed=now-open_time
        close=False;reason=''
        if now<=CONFIG['warmup']+1e-9:
            close=elapsed>=1-1e-9;reason='common_warmup'
        elif policy.startswith('fixed_time_'):
            interval=float(policy.rsplit('_',1)[1]);close=elapsed>=interval-1e-9;reason='fixed_time'
        elif elapsed>=CONFIG['deadline']-1e-9:
            close=True;reason='deadline'
        elif policy=='fixed_K8_timeout4':
            close=len(candidates)>=8;reason='K8'
        elif policy=='age_count_trigger':
            age_mean=np.mean([version-c.downloaded for c in candidates]) if candidates else 0.
            close=len(candidates)>=8 or (len(candidates)>=3 and age_mean>=3);reason='age_count'
        elif policy=='target_gain_stop' and len(candidates)>=3:
            current=geom.solve(candidates,version)[0]
            future_losses=[]
            rng=np.random.default_rng(np.random.SeedSequence([seed,tick,94031]))
            next_phase=tick%10
            possible=phases[next_phase]
            for sc in range(CONFIG['scenarios']):
                templates=possible[int(rng.integers(len(possible)))]
                future=dict(pool)
                for j,template in enumerate(templates):
                    # A predictive sample from historical payload/lag, not actual future.
                    age=min(version,template.lag)
                    if age>CONFIG['age_max']:continue
                    sampled=Msg(f'pred::{tick}::{sc}::{j}',template.client,now+0.05,now+0.1,
                                template.q,template.lag)
                    future[sampled.client]=Candidate(sampled,version-age)
                future_losses.append(geom.solve(sorted(future.values(),key=lambda c:c.msg.client),version)[0])
            gain=current-float(np.mean(future_losses))
            cost=CONFIG['wait_weight']*CONFIG['grid']/CONFIG['deadline']
            close=gain<=cost
            reason='marginal_gain_below_cost' if close else 'wait_for_target_gain'
            decision_log.append(dict(time=now,elapsed=elapsed,K=len(candidates),current_loss=current,
                                     predicted_gain=gain,waiting_cost=cost,close=close))
        if close:
            loss,distance,age,a=geom.solve(candidates,version)
            last_score=loss+CONFIG['wait_weight']*elapsed/CONFIG['deadline']
            last_distance=distance;last_age=age
            keys=[c.msg.key for c in candidates]
            if consumed.intersection(keys):raise RuntimeError('duplicate consumption')
            consumed.update(keys)
            closures.append(dict(time=now,duration=elapsed,K=len(candidates),distance=distance,
                                 age=age,score=last_score,reason=reason,
                                 keys=keys,weights=a.tolist(),version_before=version))
            pool={};version+=1;open_time=now
        if now>CONFIG['warmup']+1e-9:
            evaluations.append((now,last_score,last_distance,last_age))
    f=pd.DataFrame(evaluations,columns=['time','score','distance','age'])
    f.to_csv(OUT/f'{seed}_{policy}_timeline.csv',index=False)
    save(f'{seed}_{policy}_closures.json',closures)
    if decision_log:save(f'{seed}_{policy}_decisions.json',decision_log)
    post=[c for c in closures if c['time']>CONFIG['warmup']]
    return dict(seed=seed,policy=policy,J=float(f.score.mean()),geometry_distance=float(f.distance.mean()),
                age=float(f.age.mean()),mean_window_duration=float(np.mean([c['duration'] for c in post])),
                scored_closures=len(post),consumed_messages=len(consumed),registered_messages=ir,
                physical_completions=ic,expired=expired,superseded=superseded,
                solves=geom.solves,max_feasibility_violation=geom.max_violation,
                close_times=[c['time'] for c in post],predictions_produced=False)

def stop(state,seed,reason,rows,cpu):
    save('EXECUTION_STATUS.json',dict(status=state,stage='G2',seed=seed,reason=reason,
         cpu_seconds=cpu,new_neural_runs=0,remaining_seeds_cancelled=True,
         cross_dataset_cancelled=True,formal_cancelled=True))
    text=f'''# STOP_REPORT\n\n状态：{state}。失败层：G2 标签无关控制门槛。\n\n原因：{reason}\n\n已执行 Traffic/{seed} 的共同受控事件流比较。真实模型预测、RMSE、神经训练与完整 RAVEN 实验均为 0。几何—等待代理不能替代任务收益。\n\n本进程 CPU：{cpu:.3f} 秒。原项目和方案 1 STOP 均未修改。\n\n剩余开发种子、跨数据回放、propensity/完整共同聚合器集成、端到端训练、正式20种子与消融均取消。禁止调系数、换种子或扩大预算继续本轮。\n\n详细结果见 MAIN_COMPARISON.csv；规则见 PROTOCOL.md。\n'''
    (OUT/'STOP_REPORT.md').write_text(text,encoding='utf-8')

def main():
    save('FROZEN_CONFIG.json',CONFIG)
    save('EXECUTION_STATUS.json',dict(status='RUNNING',stage='G0_G1',new_neural_runs=0))
    (OUT/'PROOF_LEDGER.md').write_text('''# 证明账本\n\nP1 因果信息接口：代码只暴露当前池与暖启动经验模型，当前阶段不使用原 U、oracle 或标签。\nP2 有限截止/消费：40网格截止，逐消息唯一消费与版本递增有执行断言。\nP3 Bellman 最优性：真实已知核下的条件命题；未声称实现全局最优。\nP4 单步策略：经验模型和有限场景近似，真实期望保证未建立。\nP5 几何到预测：未证明，不产生预测收益结论。\nP6 新 U/propensity：重新按物理到达及动态版本判定；IPW不用于当前门槛，正式训练前必须重算。\n''',encoding='utf-8')
    rows=[]
    for seed in CONFIG['seeds']:
        mu,regs,completions,total=load(seed)
        phases=calibration_batches(completions)
        for policy in CONFIG['baselines']+['target_gain_stop']:
            start=time.process_time();row=execute(policy,seed,mu,regs,completions,phases)
            row['cpu_seconds']=time.process_time()-start;rows.append(row)
            pd.DataFrame([{k:v for k,v in r.items() if k!='close_times'} for r in rows]).to_csv(OUT/'MAIN_COMPARISON.csv',index=False)
            print(json.dumps({k:row[k] for k in ['seed','policy','J','geometry_distance','mean_window_duration','cpu_seconds']},ensure_ascii=False),flush=True)
        current=rows[-1];controls=rows[-6:-1];best=min(controls,key=lambda r:r['J'])
        gain=(best['J']-current['J'])/best['J']
        cpu=time.process_time()-PROCESS_START
        reason=f"新 J={current['J']:.8f}，最强基线 {best['policy']} J={best['J']:.8f}，相对改善={gain*100:.4f}%。"
        if current['J']>best['J']+CONFIG['scoring_tolerance']:
            stop('STOP_GEOMETRY_WAIT_BASELINE',seed,reason,rows,cpu);print('STOP',reason,flush=True);return
        if any(current['close_times']==r['close_times'] for r in controls[:3]):
            stop('STOP_NO_DISTINCT_MECHANISM',seed,reason,rows,cpu);print('STOP',reason,flush=True);return
        if gain<CONFIG['minimum_gain']:
            stop('STOP_NO_INCREMENTAL_VALUE',seed,reason,rows,cpu);print('STOP',reason,flush=True);return
    save('EXECUTION_STATUS.json',dict(status='TRAFFIC_GEOMETRY_PASS',stage='G2',
         new_neural_runs=0,cpu_seconds=time.process_time()-PROCESS_START,
         next='cross-dataset geometry; full predictive implementation still required'))

if __name__=='__main__':
    try:main()
    except Exception as e:
        cpu=time.process_time()-PROCESS_START
        stop('STOP_IMPLEMENTATION_OR_BUDGET',None,repr(e),[],cpu)
        raise
