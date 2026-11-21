"""One authorized Traffic trajectory. Private producer, normal revision planner."""
from dataclasses import asdict,replace
from datetime import datetime,timezone
from pathlib import Path
from types import SimpleNamespace
import copy,heapq,json,time,os
import numpy as np
import pandas as pd
import torch
from . import METHOD_VERSION
from .schema import ControlConfig,Registration,P2Settings,InputError
from .probability import DiagnosticPriorQ,policy_context_hash
from .calibration_identity import ClockNamespace,applicability,service_parameters_hash
from .predictor import FrozenServiceModel,ServiceRecord,PublicOpportunity,OpportunityMark
from .session import prepare_development
from .training_backend import DevelopmentAuthorization
from .planner import candidate_offsets,fixed_fallback
from .persistence import source_identity
from raven_mcs.experiments.calibration_first import load_inputs,SERVICE,CausalTrafficProducer
from raven_mcs.control.persistence import exclusive_json
from raven_mcs.training.window_runner import FullWindowRunner
from raven_mcs.simulation.event_trace import EventTrace,EventTraceMetadata
from raven_mcs.aggregation.method_policy import get_method_policy
from raven_mcs.aggregation.methods import RavenAggregator
from raven_mcs.models.common_ndmf import deterministic_common_ndmf
from raven_mcs.e3.real_runner.generator_r3 import _block_from_stratum
from raven_mcs.e3.real_runner.stage2_r3 import sample_tau
from raven_mcs.utils.hashing import sha256_file,sha256_json

SOURCE='user_20261013_RE_interval_v3_single_development'

def build_session(root,out,*,integration=False,integration_tag=''):
    if json.loads((out/'SEED_REVIEW.json').read_text())['status']!='NO_PRIOR_SELECTION_OR_EXECUTION_FOUND':raise InputError('seed audit not clear')
    inputs=load_inputs(root,out)
    config=ControlConfig(SOURCE, __import__('raven_mcs.sag.r1l_design',fromlist=['DesignConfiguration']).DesignConfiguration(True,'preconfigured_development_44001_on'))
    owner=FullWindowRunner(trace=EventTrace(pd.DataFrame(columns=['client_id']),EventTraceMetadata('traffic_RE_interval_development',44001,100,len(inputs.clients))),
        dataset=SimpleNamespace(),model=deterministic_common_ndmf(len(inputs.clients),seed=43001),aggregator=RavenAggregator(),
        policy=get_method_policy('raven_mcs'),mu=np.asarray(inputs.mu),num_groups=len(inputs.mu),local_steps=1,
        learning_rate=.01,seed=44001,design_configuration=config.design,pi_target=inputs.pi,pi_opp_joint=inputs.opp)
    original=json.loads((root/'results_calibration_first_20261013/ACQUISITION_FROZEN_PLAN.json').read_text())
    if owner._theta_hash()!=original['scope']['learning']['initial_model_hash']:raise InputError('same initial numerical state not reconstructed')
    if list(inputs.mu)!=original['public_target']['mu']:raise InputError('public target changed')
    scope=applicability(learning=dict(model=dict(class_name='CommonNDMF',spatial=len(inputs.clients),spatial_dim=32,time_dim=32,
        head=[128,64,32,1],dropout=.1),optimizer='existing_hajek_sgd',local_steps=1,learning_rate=.01,
        initial_model_hash=owner._theta_hash(),scaler=inputs.scaler,feature_schema='existing spatial/hour/weekday/trend'),
        service=dict(SERVICE,resource_model='exogenous_no_shared_contention',device='cpu',concurrency=1),
        experiment_end=100.,data_identity=inputs.data_id,target_identity=inputs.target_id,
        stage1=dict(p_fit='original lagged observation logistic after closed windows',p_prior=.2,
            features=['bias','hour_block','planned_workload_pre'],pi_opp_joint=[[c,s,v] for (c,s),v in sorted(inputs.opp.items())],
            a_max=owner.a_max,p_min=owner.p_min,pi_min=owner.pi_min))
    version='RE_interval_same_run_warmup20_v3'
    q=DiagnosticPriorQ(policy_context_hash(config,P2Settings(),inputs.mu,version,scope))
    service=FrozenServiceModel(version,0.,(),(),q.to_dict(),resource_model='exogenous_no_shared_contention')
    namespace=asdict(ClockNamespace(('integration_no_sampling/' if integration else 'development_activation_cost_only/')+'44001/'+out.name,datetime.now(timezone.utc).isoformat()))
    session=prepare_development(owner,config=config,predictor=service,q_model=q,seed=44001,experiment_end=100.,open_time=0.,
        data_identity=inputs.data_id,target_identity=inputs.target_id,probability_applicability=scope,clock_namespace=namespace,
        run_dir=out/('integration'+integration_tag if integration else 'trajectory'))
    torch.manual_seed(44001+29)
    plan=dict(method=METHOD_VERSION,role='development_activation_cost_only',config=config.to_dict(),settings=asdict(session.runner.settings),
        scope=scope,clock_namespace=namespace,q=q.to_dict(),public_target=inputs.target,service=SERVICE,
        seeds=dict(model_initialization=43001,model_source='reconstructed deterministic initialization; no old trajectory model loaded',
            owner=44001,local_dropout=44030,producer=44014,planner='SeedSequence[44001,tick,scenario,94031]'),
        authorization=asdict(DevelopmentAuthorization(SOURCE)),SGD_limit=5000,q_fitting=False,
        statistical_set='regular grid 20<t<100; exactly799 if complete; no filtering by support/forced/timeout',
        thresholds='unchanged; mechanism difference screen 5% of D; not P3 or performance acceptance',
        seed_audit_sha256=sha256_file(out/'SEED_REVIEW.json'),sources=source_identity())
    exclusive_json(out/('INTEGRATION_CONFIG'+integration_tag+'.json' if integration else 'ACQUISITION_FROZEN_PLAN.json'),plan)
    return inputs,session

class DevelopmentProducer(CausalTrafficProducer):
    """Original physical law, re-bound seed and revision registration/auth types."""
    def __init__(self,inputs,session):
        self.inputs=inputs;self.session=session;self.rng=np.random.default_rng(44001+13)
        self.next_clock=0;self.next_client=0;self.pending=[];self.training_cpu=0.;self.training_wall=0.
        self.registration_versions={};self.opportunities=[];self.p_pending=[]
    def register_current(self):
        i=self.inputs;s=self.session;r=s.runner;c=i.clients[self.next_client];now=self.next_registration()
        r.advance_time(now)
        strata=i.strata[c];cond=np.asarray([i.opp[(c,x)] for x in strata]);cond/=cond.sum()
        st=strata[int(self.rng.choice(len(strata),p=cond))];support=i.pools[(c,st)]
        risk=list(self.rng.choice(support,size=min(4,len(support)),replace=False));tail=_block_from_stratum(st) in {2,3}
        p=np.asarray([.35*(.55 if _block_from_stratum(i.meta[u]['stratum']) in {2,3} else 1.) for u in risk])
        flags=(self.rng.random(len(risk))<p).astype(int)
        tier=int(self.rng.choice([0,1,2],p=[.3,.5,.2]));download,_=sample_tau(self.rng,r.model_version,5)
        key=f'{self.next_clock:03d}::{c}';reg=Registration(key,c,now,download,f'tier-{tier}',f'net-tier-{tier}')
        self.registration_versions[key]=r.model_version
        features=[dict(bias=1.,hour_block=float(_block_from_stratum(i.meta[u]['stratum'])),planned_workload_pre=float(len(risk))) for u in risk]
        s.register_observations(reg,stratum_ids=[st]*len(risk),p_pre_features=features,observation=flags,
            group_ids=[i.meta[u]['group'] for u in risk],metadata_as_of=r.backend.stage1_as_of,
            provenance='prewindow_public_catalogue_plus_current_TRAIN_O')
        self.opportunities.append(PublicOpportunity(key,c,now,reg.device_class,reg.network_class,now))
        self.p_pending.append((key,features,flags.tolist()))
        if np.any(flags):
            records=[]
            for u,flag in zip(risk,flags):
                if flag:
                    m=i.meta[u];records.append(dict(spatial_id=m['spatial_id'],absolute_time=m['absolute_time'],time_index=m['time_index'],
                        observed_value=i.values[(c,u)],spatial_to_idx=i.spatial,total_time_slots=i.time_slots))
            cpu=time.process_time();wall=time.perf_counter()
            update,loss=r.start_local_training(key,records,authorization=DevelopmentAuthorization(SOURCE))
            cpu=time.process_time()-cpu;self.training_cpu+=cpu;self.training_wall+=time.perf_counter()-wall
            if not np.isfinite(loss) or not np.all(np.isfinite(update)):raise InputError('NONFINITE_LOCAL_SGD')
            if self.training_cpu>2000:raise InputError('ORIGINAL_TRAINING_CPU_SUBBUDGET_EXHAUSTED')
            pcs=SERVICE['compute_success'][tier]*(.75 if tail else 1.);pns=SERVICE['network_success'][tier]*(.80 if tail else 1.)
            mean=SERVICE['mean_compute'][tier]*(1.25 if tail else 1.)
            compute_ok=bool(self.rng.random()<pcs);duration=max(float(self.rng.lognormal(np.log(mean),.3)),cpu)
            network_ok=bool(self.rng.random()<pns) if compute_ok else False
            net=float(self.rng.lognormal(np.log(.3),.2)) if compute_ok else 0.
            outcome='completion' if compute_ok and network_ok else ('network_failure' if compute_ok else 'compute_failure')
            heapq.heappush(self.pending,(now+duration+net,key,outcome,update if outcome=='completion' else None))
        self.next_client+=1
        if self.next_client==len(i.clients):self.next_client=0;self.next_clock+=1
    def freeze_service_at_20(self):
        r=self.session.runner;records=[]
        for rec in r.attempts.values():
            R=r.private_stage1[rec.registration.key].total>0;E=rec.features.model_age<=5
            if not R or not E:continue
            if rec.q.role!='diagnostic_prior':raise InputError('unexpected positive-domain q role')
            outcome='completion' if rec.physical_outcome=='completion' else ('notified_failure' if rec.physical_outcome in {'compute_failure','network_failure'} else 'right_censored')
            until=rec.completed_at if outcome=='completion' else (next(e['time'] for e in r.events if e['kind']=='notified_failure' and e['key']==rec.registration.key) if outcome=='notified_failure' else 20.)
            records.append(ServiceRecord(rec.registration,until,outcome,r.private_stage1[rec.registration.key] if outcome=='completion' else None,self.registration_versions[rec.registration.key]))
        history=tuple(OpportunityMark(**x) for x in r.opportunity_marks)
        model=FrozenServiceModel.from_history(records,cutoff=20.,version=r.predictor.version,q_model=r.q_model,
            joint_opportunities=history,resource_model='exogenous_no_shared_contention')
        r.freeze_next_estimators(predictor=model,q_model=r.q_model)
        exclusive_json(self.session.run_dir/'SERVICE_FROZEN_AT_20.json',dict(clock_namespace=r.clock_namespace,
            source_cutoff=20.,model=model.to_dict(),parameter_hash=service_parameters_hash(model),
            all_registration_count=len(history),conditional_service_records=[asdict(x) for x in records]))

def checkpoint_pair(session,producer,tick,label):
    path=session.save(f'{label}_tick{tick:04d}.json')
    exclusive_json(session.run_dir/f'{label}_producer_tick{tick:04d}.json',dict(schema='RE_interval_private_producer_v3',
        checkpoint=path.name,checkpoint_hash=sha256_file(path),tick=tick,T=100.,clock_namespace=session.runner.clock_namespace,
        state=producer.to_dict(),torch_rng=torch.get_rng_state().tolist(),controller=session.controller.to_dict()))
    return path

def acquire(root,out,*,cpu_remaining):
    torch.set_num_threads(1);torch.set_num_interop_threads(1)
    inputs,session=build_session(root,out);producer=DevelopmentProducer(inputs,session)
    from raven_mcs.control.process_budget import ProcessTreeBudget
    meter=ProcessTreeBudget();meter.attach(os.getpid());start=time.perf_counter();tick=0;status='PREFIX'
    metrics=(out/'DECISION_RECORDS.jsonl').open('x',encoding='utf-8')
    try:
        checkpoint_pair(session,producer,0,'START')
        for tick in range(1,1001):
            if meter.cpu_seconds()>cpu_remaining-200 or time.perf_counter()-start>7000:
                status='CPU_BUDGET_PREFIX' if meter.cpu_seconds()>cpu_remaining-200 else 'WATCHDOG_PREFIX';tick-=1;break
            now=round(tick*.1,10);producer.notices_through(now);session.runner.advance_time(now)
            snapshot=session.runner.snapshot();before=sha256_json(asdict(snapshot));shadow=fixed_fallback(snapshot,'shadow_fixed_time_2')
            legal=sorted({'CLOSE' if o==0 else 'WAIT' for o in candidate_offsets(snapshot)})
            if now-snapshot.window_open>=4-1e-9:legal=['CLOSE']
            if now<=20:legal=['CLOSE' if now-snapshot.window_open>=1-1e-9 else 'WAIT']
            snapshot_path=f'snapshots/tick{tick:04d}.json'
            (out/'snapshots').mkdir(exist_ok=True)
            exclusive_json(out/snapshot_path,dict(snapshot=asdict(snapshot),predictor_parameter_hash=snapshot.service_parameters_hash))
            decision=session.controller.decide(snapshot,session.runner.predictor)
            if sha256_json(asdict(session.runner.snapshot()))!=before:raise InputError('planning/shadow mutated actual state')
            row=dict(tick=tick,time=now,window_open=snapshot.window_open,snapshot=snapshot_path,pool=len(snapshot.pool),inflight=len(snapshot.in_flight),
                N=int(round((min(now+8.,100.)-now)/.1)),candidate_offsets=candidate_offsets(snapshot),
                legal_actions=legal,shadow=shadow.action,shadow_legal=shadow.action in legal,decision=asdict(decision),
                classification=('ENDPOINT_GRID' if tick==1000 else ('WARMUP' if tick<=200 else
                    {'hard_deadline':'HARD_DEADLINE','common_warmup':'WARMUP'}.get(decision.reason,
                    'CPU_TIMEOUT' if 'CPU_TIMEOUT' in decision.reason else decision.reason))),
                accounting_index=len(session.controller.accounting)-1,closure_index=None,consumed_keys=[])
            session.runner.decisions.append(dict(time=now,**asdict(decision)))
            if decision.action=='CLOSE':
                closure=session.close();producer.after_close();row['closure_index']=len(session.runner.closures)-1;row['consumed_keys']=closure['preview']['keys']
            metrics.write(json.dumps(row,allow_nan=False)+'\n');metrics.flush()
            if tick==200:producer.freeze_service_at_20()
            producer.reclaim_terminal_storage()
            if tick%100==0:
                if tick%200==0:checkpoint_pair(session,producer,tick,'PERIODIC')
                print(json.dumps(dict(tick=tick,registrations=len(session.runner.attempts),SGD=session.runner.backend.local_optimizer_steps,
                    cpu=meter.cpu_seconds(),wall=time.perf_counter()-start)),flush=True)
        else:
            status='COMPLETE_T100';session.runner.finish_finite_endpoint()
        if status!='COMPLETE_T100':session.runner.finish_observation()
        path=checkpoint_pair(session,producer,tick,status)
        exclusive_json(out/'ACQUISITION_RESULT.json',dict(status=status,T_observed=session.runner.now,T_target=100.,tick=tick,
            checkpoint=str(path),method=METHOD_VERSION,seed=44001,registrations=len(session.runner.attempts),
            SGD=session.runner.backend.local_optimizer_steps,training_CPU=producer.training_cpu,training_wall=producer.training_wall,
            process_tree_CPU=meter.cpu_seconds(),wall=time.perf_counter()-start,planning_calls=len(session.runner.decisions),
            q_role='diagnostic_prior_NOT_CALIBRATED',q_fit=0,GPU=0,next_status='WAITING_USER_REVIEW'))
    except Exception as exc:
        import traceback
        session.runner.finish_observation()
        path=checkpoint_pair(session,producer,tick,'FAILED')
        exclusive_json(out/'ACQUISITION_FAILURE.json',dict(error=str(exc),trace=traceback.format_exc(),tick=tick,now=session.runner.now,
            CPU=meter.cpu_seconds(),wall=time.perf_counter()-start,SGD=session.runner.backend.local_optimizer_steps,
            checkpoint=str(path),status='WAITING_USER_REVIEW'))
        raise
    finally:metrics.close()
