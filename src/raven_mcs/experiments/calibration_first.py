"""One approved real Traffic acquisition. No fit, validation, or run queue.

The private producer reveals registrations and service notices in time order.
It never materializes old U or passes future payloads to the controller.
"""
from __future__ import annotations
from dataclasses import asdict,replace
from datetime import datetime,timezone
from pathlib import Path
from types import SimpleNamespace
import copy,heapq,json,time
import numpy as np
import pandas as pd
import torch

from raven_mcs.control.schema import ControlConfig,Registration,P2Settings,InputError
from raven_mcs.sag.r1l_design import DesignConfiguration
from raven_mcs.control.probability import DiagnosticPriorQ,policy_context_hash
from raven_mcs.control.calibration_identity import ClockNamespace,applicability,service_parameters_hash
from raven_mcs.control.predictor import FrozenServiceModel,ServiceRecord,PublicOpportunity
from raven_mcs.control.persistence import exclusive_json,save_checkpoint
from raven_mcs.experiments.conditional_bundle import prepare_conditional_bundle,restore_conditional_bundle
from raven_mcs.training.dynamic_control import CalibrationAuthorization
from raven_mcs.training.window_runner import FullWindowRunner
from raven_mcs.simulation.event_trace import EventTrace,EventTraceMetadata
from raven_mcs.aggregation.method_policy import get_method_policy
from raven_mcs.aggregation.methods import RavenAggregator
from raven_mcs.models.common_ndmf import deterministic_common_ndmf
from raven_mcs.correction.pi_target import build_pi_target
from raven_mcs.e3.real_runner.generator_r3 import build_joint_pi_opp,_block_from_stratum
from raven_mcs.e3.real_runner.stage2_r3 import sample_tau
from raven_mcs.utils.hashing import sha256_json,sha256_file

SERVICE=dict(source='existing_R3_nominal_law_with_explicit_failure_notices_v1',
    device_prior=[.3,.5,.2],compute_success=[.70,.90,.98],network_success=[.80,.95,.99],
    mean_compute=[.80,.50,.20],compute_log_sd=.3,network_log_mean=float(np.log(.3)),network_log_sd=.2,
    aligned_tail_blocks=[2,3],tail_compute_success_factor=.75,tail_network_success_factor=.80,
    tail_compute_mean_factor=1.25,download_lag='80% uniform0..5; 20% uniform6..8; clipped only at version0',
    failure_notification='compute failure after attempted compute duration; network failure after attempted network duration',
    real_compute_floor='max(sampled_compute_duration, measured_local_training_process_CPU_seconds)',
    clock_cost_assumption='one measured CPU second lower-bounds one controlled service unit; wall time reported separately',
    mean_observation_rate=.35,tail_observation_scale=.55,opportunity_theta_align=1.25,
    risk_set_size=4,registration_phase='clock+.05+.01*client_index',occupancy='one registration/client/clock')

def load_inputs(root,out):
    data=root/'results_main_rebuild_r1/data/traffic'
    catalog=pd.read_parquet(out/'PUBLIC_CATALOGUE.parquet')
    # Value readers explicitly filter TRAIN. TEST support remains metadata only.
    train=pd.read_parquet(data/'atomic_units.parquet',filters=[('split','==','train')])
    measured=pd.read_parquet(data/'client_measurements.parquet',filters=[('split','==','train')],
        columns=['client_id','unit_id','potential_measurement','split'])
    if set(train.split)!= {'train'} or set(measured.split)!= {'train'}:raise InputError('nonTRAIN value reader')
    clients=sorted(train.spatial_id.astype(str).unique())
    mapping={c:c for c in clients}
    groups=sorted(catalog.target_group.astype(str).unique());gi={g:i for i,g in enumerate(groups)}
    selected=catalog[(catalog.split=='test') & catalog.support_flag.astype(bool)]
    counts=selected.target_group.astype(str).value_counts();mu=tuple(float(counts.get(g,0)/len(selected)) for g in groups)
    # The shared target helper names this metadata field target_group_main;
    # this frozen bundle uses target_group. The alias preserves every group.
    target_catalog=catalog.assign(target_group_main=catalog.target_group)
    pt=build_pi_target(target_catalog,mapping,split='test')
    pi={(str(r.client_id),str(r.opportunity_stratum)):float(r.pi_k_s_tar) for r in pt.itertuples()}
    pools={}
    for row in train.itertuples():pools.setdefault((str(row.spatial_id),str(row.opportunity_stratum)),[]).append(str(row.unit_id))
    strata={c:sorted(s for (k,s) in pools if k==c) for c in clients}
    opp=build_joint_pi_opp(clients,strata)
    if any(pi.get(k,0)<=0 for k in opp):raise InputError('positive target/design support missing')
    mean=float(train.target_value.mean());std=float(train.target_value.std(ddof=0))
    if not np.isfinite(std) or std<=0:raise InputError('invalid TRAIN scaler')
    values={(str(r.client_id),str(r.unit_id)):(float(r.potential_measurement)-mean)/std for r in measured.itertuples()}
    meta={str(r.unit_id):dict(spatial_id=str(r.spatial_id),absolute_time=float(pd.Timestamp(r.absolute_time).timestamp()/3600),
        time_index=int(r.time_index),stratum=str(r.opportunity_stratum),group=gi[str(r.target_group)]) for r in train.itertuples()}
    if any((c,u) not in values for (c,s),uids in pools.items() for u in uids):raise InputError('measurement missing, no truth fallback')
    target=dict(mu=mu,groups=groups,pi_target=[[c,s,v] for (c,s),v in sorted(pi.items())],
        catalogue=sha256_file(out/'PUBLIC_CATALOGUE.parquet'),published_before_window_0=True)
    return SimpleNamespace(clients=clients,pools=pools,strata=strata,opp=opp,pi=pi,mu=mu,groups=groups,meta=meta,values=values,
        spatial={c:i for i,c in enumerate(clients)},time_slots=int(catalog.time_index.max())+1,
        scaler=dict(mean=mean,std=std,source='TRAIN atomic values only'),target=target,
        data_id=sha256_json({str(f):sha256_file(f) for f in (data/'atomic_units.parquet',data/'client_measurements.parquet')}),
        target_id=sha256_json(target))

def owner_for(inputs,config):
    return FullWindowRunner(trace=EventTrace(pd.DataFrame(columns=['client_id']),EventTraceMetadata('traffic_causal_calibration',43001,100,len(inputs.clients))),
        dataset=SimpleNamespace(),model=deterministic_common_ndmf(len(inputs.clients),seed=43001),
        aggregator=RavenAggregator(),policy=get_method_policy('raven_mcs'),mu=np.asarray(inputs.mu),num_groups=len(inputs.mu),
        local_steps=1,learning_rate=.01,seed=43001,design_configuration=config.design,
        pi_target=inputs.pi,pi_opp_joint=inputs.opp)

def prepare_calibration_only(root,out):
    audit=json.loads((out/'SEED_REVIEW.json').read_text(encoding='utf-8'))
    if audit['status']!='NO_PRIOR_SELECTION_OR_EXECUTION_FOUND':raise InputError('SEED_AUDIT_NOT_CLEAR')
    inputs=load_inputs(root,out)
    config=ControlConfig('user_20261013_first_calibration_only',DesignConfiguration(True,'preconfigured_calibration_run_on'))
    owner=owner_for(inputs,config)
    scope=applicability(learning=dict(model=dict(class_name='CommonNDMF',spatial=len(inputs.clients),spatial_dim=32,time_dim=32,
        head=[128,64,32,1],dropout=.1),optimizer='existing_hajek_sgd',local_steps=1,learning_rate=.01,
        initial_model_hash=owner._theta_hash(),scaler=inputs.scaler,feature_schema='existing spatial/hour/weekday/trend'),
        service=SERVICE,experiment_end=100.,data_identity=inputs.data_id,target_identity=inputs.target_id,
        stage1=dict(p_fit='existing observation logistic lagged at completed windows',p_prior=.2,features=['bias','hour_block','planned_workload_pre'],
            pi_opp_joint=[[c,s,v] for (c,s),v in sorted(inputs.opp.items())],a_max=owner.a_max,p_min=owner.p_min,pi_min=owner.pi_min))
    namespace=asdict(ClockNamespace('calibration_only/fit/43001/'+out.name,datetime.now(timezone.utc).isoformat()))
    version='same_run_warmup20_competing_risks_v1'
    prior=DiagnosticPriorQ(policy_context_hash(config,P2Settings(),inputs.mu,version,scope))
    service=FrozenServiceModel(version,0.,(),(),prior.to_dict())
    exclusive_json(out/'ACQUISITION_FROZEN_PLAN.json',dict(scope=scope,clock_namespace=namespace,config=config.to_dict(),settings=asdict(P2Settings()),
        q=prior.to_dict(),seeds=dict(acquisition=43001,planner='SeedSequence[43001,tick,scenario,94031]'),
        seed_audit=sha256_file(out/'SEED_REVIEW.json'),public_target=inputs.target,service=SERVICE,
        all_thresholds='unchanged; no calibration score or pass computed; no fit this batch'))
    session=prepare_conditional_bundle(owner,config=config,predictor=service,q_model=prior,seed=43001,experiment_end=100.,open_time=0.,
        data_identity=inputs.data_id,target_identity=inputs.target_id,run_dir=out/'trajectory',repo_root=root,
        stage1_as_of=0.,calibration_only=True,probability_applicability=scope,clock_namespace=namespace)
    return inputs,session

class CausalTrafficProducer:
    """Private pending notice queue and RNG; controller receives current notices only."""
    def __init__(self,inputs,session):
        self.inputs=inputs;self.session=session;self.rng=np.random.default_rng(43001+13)
        self.next_clock=0;self.next_client=0;self.pending=[];self.training_cpu=0.;self.training_wall=0.
        self.registration_versions={};self.opportunities=[];self.p_pending=[]
    def next_registration(self):
        if self.next_clock>=100:return float('inf')
        return self.next_clock+.05+.01*self.next_client
    def register_current(self):
        i=self.inputs;s=self.session;r=s.runner;c=i.clients[self.next_client];now=self.next_registration()
        r.advance_time(now)
        strata=i.strata[c];cond=np.asarray([i.opp[(c,x)] for x in strata]);cond/=cond.sum()
        st=strata[int(self.rng.choice(len(strata),p=cond))];support=i.pools[(c,st)]
        risk=list(self.rng.choice(support,size=min(4,len(support)),replace=False));tail=_block_from_stratum(st) in {2,3}
        p=np.asarray([.35*(.55 if _block_from_stratum(i.meta[u]['stratum']) in {2,3} else 1.) for u in risk])
        flags=(self.rng.random(len(risk))<p).astype(int)
        # Device/network profile is emitted at registration BEFORE service outcomes.
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
            for u,f in zip(risk,flags):
                if not f:continue
                m=i.meta[u];records.append(dict(spatial_id=m['spatial_id'],absolute_time=m['absolute_time'],time_index=m['time_index'],
                    observed_value=i.values[(c,u)],spatial_to_idx=i.spatial,total_time_slots=i.time_slots))
            cpu=time.process_time();wall=time.perf_counter()
            update,loss=r.start_local_training(key,records,authorization=CalibrationAuthorization('user_20261013_first_only'))
            cpu=time.process_time()-cpu;self.training_cpu+=cpu;self.training_wall+=time.perf_counter()-wall
            if not np.isfinite(loss) or not np.all(np.isfinite(update)):raise InputError('NONFINITE_LOCAL_SGD')
            if self.training_cpu>2000:raise InputError('ORIGINAL_TRAINING_CPU_SUBBUDGET_EXHAUSTED')
            pcs=SERVICE['compute_success'][tier]*(.75 if tail else 1.)
            pns=SERVICE['network_success'][tier]*(.80 if tail else 1.)
            mean=SERVICE['mean_compute'][tier]*(1.25 if tail else 1.)
            compute_ok=bool(self.rng.random()<pcs);duration=max(float(self.rng.lognormal(np.log(mean),.3)),cpu)
            network_ok=bool(self.rng.random()<pns) if compute_ok else False
            net=float(self.rng.lognormal(np.log(.3),.2)) if compute_ok else 0.
            outcome='completion' if compute_ok and network_ok else ('network_failure' if compute_ok else 'compute_failure')
            heapq.heappush(self.pending,(now+duration+net,key,outcome,update if outcome=='completion' else None))
        self.next_client+=1
        if self.next_client==len(i.clients):self.next_client=0;self.next_clock+=1
    def notices_through(self,now):
        while min(self.next_registration(),self.pending[0][0] if self.pending else float('inf'))<=now+1e-10:
            if self.next_registration()<=(self.pending[0][0] if self.pending else float('inf')):self.register_current()
            else:
                at,key,event,update=heapq.heappop(self.pending)
                if event=='completion':self.session.runner.on_completion(key,at,update=update)
                else:self.session.runner.on_failure(key,at,reason=event)
    def reclaim_terminal_storage(self):
        """Keep all event/label evidence; discard only unusable tensor storage.

        The declared producer can request at most the previous eight versions.
        Pending work was already trained at registration. Keeping those nine
        checkpoints preserves every allowed future download in this source.
        """
        r=self.session.runner
        for key in list(r.backend.updates):
            if r.attempts[key].consumed is not None:r.backend.updates.pop(key)
        cutoff=max(0,r.model_version-8)
        for version in list(self.session.owner.model_versions):
            if version<cutoff:self.session.owner.model_versions.pop(version)
    def after_close(self):
        s=self.session;remain=[]
        for key,features,outcomes in self.p_pending:
            # Observations existed at registration; fit only after its window has closed.
            if s.runner.attempts[key].registration.registered_at<s.runner.now:
                s.owner.obs_propensity.update_records_after_completion(np.asarray([[f['bias'],f['hour_block'],f['planned_workload_pre']] for f in features]),np.asarray(outcomes))
            else:remain.append((key,features,outcomes))
        self.p_pending=remain;s.owner.p_model_version+=1
        s.freeze_stage1_for_next_window(as_of=s.runner.now)
    def freeze_service_at_20(self):
        r=self.session.runner;records=[]
        for rec in r.attempts.values():
            if rec.q.role!='diagnostic_prior':raise InputError('unexpected q evidence role')
            if rec.terminal_reason=='no_observations':continue
            outcome='completion' if rec.physical_outcome=='completion' else ('notified_failure' if rec.physical_outcome in {'compute_failure','network_failure'} else 'right_censored')
            until=rec.completed_at if outcome=='completion' else (next(e['time'] for e in r.events if e['kind']=='notified_failure' and e['key']==rec.registration.key) if outcome=='notified_failure' else 20.)
            records.append(ServiceRecord(rec.registration,until,outcome,r.private_stage1[rec.registration.key] if outcome=='completion' else None,self.registration_versions[rec.registration.key]))
        model=FrozenServiceModel.from_history(records,cutoff=20.,version=r.predictor.version,q_model=r.q_model,opportunity_history=self.opportunities)
        r.freeze_next_estimators(predictor=model,q_model=r.q_model)
        exclusive_json(self.session.run_dir/'SERVICE_FROZEN_AT_20.json',dict(clock_namespace=r.clock_namespace,
            source_cutoff=20.,model=model.to_dict(),parameter_hash=service_parameters_hash(model),
            observations=len(records),records=[asdict(x) for x in records]))
    def to_dict(self):
        return dict(next_clock=self.next_clock,next_client=self.next_client,rng=copy.deepcopy(self.rng.bit_generator.state),
            pending=[dict(at=at,key=key,event=event,update=None if update is None else update.tolist()) for at,key,event,update in self.pending],
            training_cpu=self.training_cpu,training_wall=self.training_wall,registration_versions=self.registration_versions,
            opportunities=[asdict(x) for x in self.opportunities],p_pending=self.p_pending)
    def restore(self,obj):
        for key in ('next_clock','next_client','training_cpu','training_wall','registration_versions','p_pending'):setattr(self,key,obj[key])
        self.rng.bit_generator.state=obj['rng'];self.opportunities=[PublicOpportunity(**x) for x in obj['opportunities']]
        self.pending=[(x['at'],x['key'],x['event'],None if x['update'] is None else np.asarray(x['update'])) for x in obj['pending']];heapq.heapify(self.pending)

def checkpoint_pair(session,producer,tick):
    path=session.save(f'checkpoint_tick{tick:04d}.json')
    exclusive_json(session.run_dir/f'producer_tick{tick:04d}.json',dict(schema='private_causal_producer_v1',
        checkpoint=path.name,checkpoint_hash=sha256_file(path),clock_namespace=session.runner.clock_namespace,
        T=100.,tick=tick,state=producer.to_dict(),torch_rng=torch.get_rng_state().tolist()))
    return path

def acquire_first(root,out,*,cpu_remaining):
    torch.set_num_threads(1);torch.set_num_interop_threads(1)
    inputs,session=prepare_calibration_only(root,out);producer=CausalTrafficProducer(inputs,session)
    # Attach self to a nested Job so finished planner children remain charged.
    from raven_mcs.control.process_budget import ProcessTreeBudget
    import os
    meter=ProcessTreeBudget();meter.attach(os.getpid());start= time.perf_counter();status='PREFIX';tick=0
    try:
        checkpoint_pair(session,producer,0)
        for tick in range(1,1001):
            # Reserve saving/statistics/cleanup before the batch's external hard ceiling.
            if meter.cpu_seconds()>=cpu_remaining-180:
                status='CPU_BUDGET_PREFIX';tick-=1;break
            now=round(tick*.1,10);producer.notices_through(now);session.runner.advance_time(now)
            decision=session.decide()
            if decision.action=='CLOSE':session.close();producer.after_close()
            if tick==200:producer.freeze_service_at_20()
            producer.reclaim_terminal_storage()
            if tick%100==0:
                checkpoint_pair(session,producer,tick)
                print(json.dumps(dict(tick=tick,T=100,registrations=len(session.runner.attempts),local_sgd_steps=session.runner.backend.local_optimizer_steps,
                    cpu=meter.cpu_seconds(),wall=time.perf_counter()-start,planner_calls=len(session.runner.decisions)),ensure_ascii=False),flush=True)
        else:status='COMPLETE_T100';session.runner.finish_finite_endpoint()
        if status!='COMPLETE_T100':session.runner.finish_observation()
        # Different terminal/prefix save name preserves every periodic checkpoint.
        path=session.save(f'{status}_tick{tick:04d}.json')
        exclusive_json(session.run_dir/(status+'_producer.json'),dict(checkpoint=path.name,checkpoint_hash=sha256_file(path),tick=tick,T=100.,
            state=producer.to_dict(),torch_rng=torch.get_rng_state().tolist(),clock_namespace=session.runner.clock_namespace))
        records=list(session.runner.attempts.values());positive=[r for r in records if r.terminal_reason!='no_observations']
        from collections import Counter
        support={}
        for r in positive:
            layer=f'{r.registration.device_class}/{r.registration.network_class}'
            layerrow=support.setdefault(layer,dict(R1=0,mature=0,consumed=0,censored=0))
            layerrow['R1']+=1;layerrow['mature']+=int(r.consumed is not None);layerrow['consumed']+=int(r.consumed==1);layerrow['censored']+=int(r.consumed is None)
        decisions=session.runner.decisions;fallback=sum('fixed_time_2' in d['reason'] for d in decisions)
        report=dict(status=status,T_target=100,T_observed=session.runner.now,checkpoint=str(path),registrations=len(records),
            positive_observation_attempts=len(positive),mature=sum(r.consumed is not None for r in positive),
            consumed=sum(r.consumed==1 for r in positive),censored=sum(r.consumed is None for r in positive),
            physical_pending=sum(r.physical_outcome=='pending' for r in positive),terminal_reasons=dict(Counter(r.terminal_reason for r in records)),
            support=support,client_support=len({r.registration.client for r in positive}),
            age_support=dict(Counter(r.features.model_age for r in positive)),
            predictor_supported_cells=sum(c.risk>=5 for c in session.runner.predictor.cells),predictor_total_cells=len(session.runner.predictor.cells),
            planning_calls=len(decisions),fallback_calls=fallback,fallback_proportion=fallback/len(decisions) if decisions else None,
            post_warmup_fallback_proportion=sum('fixed_time_2' in d['reason'] for d in decisions[200:])/len(decisions[200:]) if len(decisions)>200 else None,
            decision_reasons=dict(Counter(d['reason'] for d in decisions)),
            local_sgd_steps=session.runner.backend.local_optimizer_steps,training_cpu_seconds=producer.training_cpu,training_wall_seconds=producer.training_wall,
            acquisition_process_tree_cpu_seconds=meter.cpu_seconds(),wall_seconds=time.perf_counter()-start,
            planner_cpu_seconds=sum(a['total_cpu_seconds'] for a in session.controller.accounting),
            planner_wall_seconds=sum(a['wall_seconds'] for a in session.controller.accounting),gpu=0,
            max_actual_weight_residual=max((c['preview']['solver'].get('normalized_weight_residual',0.) for c in session.runner.closures),default=0.),
            q_role='diagnostic_prior',q_calibration_pass='NOT_COMPUTED',q_fitted=False,
            next_status='WAITING_USER_REVIEW',remaining_trajectories_executed=0,B1_executed=False,formal_executed=False)
        exclusive_json(out/'FIRST_ACQUISITION_RESULT.json',report)
        print(json.dumps(report,ensure_ascii=False),flush=True)
    except Exception as exc:
        import traceback
        session.runner.finish_observation()
        path=session.save(f'FAILED_tick{tick:04d}.json')
        exclusive_json(session.run_dir/'FAILED_producer.json',dict(checkpoint=path.name,checkpoint_hash=sha256_file(path),
            tick=tick,T=100.,state=producer.to_dict(),torch_rng=torch.get_rng_state().tolist(),clock_namespace=session.runner.clock_namespace))
        exclusive_json(out/'ACQUISITION_FAILURE.json',dict(error=str(exc),trace=traceback.format_exc(),tick=tick,now=session.runner.now,
            CPU=meter.cpu_seconds(),wall=time.perf_counter()-start,training_steps=session.runner.backend.local_optimizer_steps,
            checkpoint=str(path),status='WAITING_USER_REVIEW'))
        raise
    finally:
        # Do not close an active kill-on-close Job containing this process.
        # Windows releases it when the acquisition process exits.
        pass
