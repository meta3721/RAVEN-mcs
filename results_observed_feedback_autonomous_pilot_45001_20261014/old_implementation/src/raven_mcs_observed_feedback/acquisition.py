"""Real OF-v1 bootstrap collection modules. No future predictor or q fitting."""
import json,copy,heapq,time
from dataclasses import asdict
from datetime import datetime,timezone
from pathlib import Path
from types import SimpleNamespace
import numpy as np
import torch
import pandas as pd
from . import METHOD_VERSION
from .authorization import SOURCE,DiagnosticCollectionAuthorization
from .schema import ControlConfig,Registration,InputError
from .design import DesignConfiguration
from .probability import DiagnosticPrior
from .backend import connect_full_runner
from .schema import Stage1Summary
from raven_mcs.experiments.calibration_first import SERVICE,load_inputs
from raven_mcs.training.window_runner import FullWindowRunner
from raven_mcs.models.common_ndmf import deterministic_common_ndmf
from raven_mcs.aggregation.method_policy import get_method_policy
from raven_mcs.aggregation.methods import RavenAggregator
from raven_mcs.simulation.event_trace import EventTrace,EventTraceMetadata
from raven_mcs.sag.r1l_design import DesignConfiguration as SharedDesign
from raven_mcs.e3.real_runner.generator_r3 import _block_from_stratum
from raven_mcs.e3.real_runner.stage2_r3 import sample_tau
from raven_mcs.utils.hashing import sha256_json

def build(root,out,root_budget):
    if json.loads((out/'SEED_REVIEW.json').read_text())['status']!='NO_PRIOR_SELECTION_OR_EXECUTION_FOUND':raise InputError('SEED_AUDIT_PENDING')
    # Publish only public columns before loading TRAIN values; never read TEST values.
    if not (out/'PUBLIC_CATALOGUE.parquet').exists():
        cols=['unit_id','spatial_id','absolute_time','time_index','target_group','opportunity_stratum','split','support_flag']
        pd.read_parquet(root/'results_main_rebuild_r1/data/traffic/atomic_units.parquet',columns=cols).to_parquet(out/'PUBLIC_CATALOGUE.parquet',index=False)
    inputs=load_inputs(root,out)
    seq=np.random.SeedSequence(45011);children=seq.spawn(4)
    streams=dict(zip(('model_init','local_dropout','opportunity_observation','service'),children))
    states={k:dict(entropy=v.entropy,spawn_key=list(v.spawn_key),mapped_seed=int(v.generate_state(1)[0])) for k,v in streams.items()}
    config=ControlConfig(SOURCE,DesignConfiguration(True,'explicit_45011_whole_run_on'))
    model=deterministic_common_ndmf(len(inputs.clients),seed=states['model_init']['mapped_seed'])
    owner=FullWindowRunner(trace=EventTrace(pd.DataFrame(columns=['client_id']),EventTraceMetadata('OF_DIAGNOSTIC_NO_TRACE_REPLAY',45011,100,len(inputs.clients))),
        dataset=SimpleNamespace(),model=model,aggregator=RavenAggregator(),policy=get_method_policy('raven_mcs'),mu=np.asarray(inputs.mu),num_groups=len(inputs.mu),
        local_steps=1,learning_rate=.01,seed=45011,design_configuration=SharedDesign.from_dict(config.design.to_dict()),pi_target=inputs.pi,pi_opp_joint=inputs.opp)
    app=dict(consumption_policy=METHOD_VERSION,T=100,collection_role='development_cost_and_bootstrap_fit_candidate',
        learning=dict(model=dict(class_name='CommonNDMF',spatial=len(inputs.clients),spatial_dim=32,time_dim=32,time_mlp=[5,64,32],head=[128,64,32,1],dropout=.1),
            optimizer='existing_hajek_sgd',local_steps=1,learning_rate=.01,initial_model_hash=owner._theta_hash(),scaler=inputs.scaler,feature_schema='existing spatial/hour/weekday/trend'),
        service=dict(SERVICE,resource_model='exogenous_no_shared_contention',GPU=0,streams=states,CPU_limit=3600),
        stage1=dict(p_fit='original logistic lagged at closed windows',p_prior=.2,features=['bias','hour_block','planned_workload_pre'],
            pi_opp_joint=[[c,s,v] for (c,s),v in sorted(inputs.opp.items())],a_max=20.,p_min=.05,pi_min=1e-6),data_identity=inputs.data_id,target_identity=inputs.target_id,
        encoding_version='OFq-public-state-1.1',q_role='diagnostic_prior',q_policy='pi_boot_Beta1_1')
    clock=dict(run_id='OF-v1/development_cost_and_bootstrap_fit_candidate/45011/'+out.name,
        origin_utc=datetime.now(timezone.utc).isoformat(),unit='controlled_service_unit',UTC_bridge='actual notice publication UTC logged per event; controlled logical time is not elapsed UTC')
    auth=DiagnosticCollectionAuthorization();r=connect_full_runner(owner,config=config,q_model=DiagnosticPrior(),seed=45011,data_identity=inputs.data_id,
        target_identity=inputs.target_id,probability_applicability=app,clock_namespace=clock,calibration_only=True,collection_authorization=auth,root_budget=root_budget)
    r.backend.freeze_stage1_context(0.);torch.manual_seed(states['local_dropout']['mapped_seed'])
    producer=CausalProducer(inputs,r,np.random.default_rng(streams['opportunity_observation']),np.random.default_rng(streams['service']))
    return inputs,r,producer,dict(method=METHOD_VERSION,role=auth.role,config=config.to_dict(),settings=asdict(r.settings),
        authorization=asdict(auth),scope=app,clock_namespace=clock,public_target=inputs.target,q=r.q_model.to_dict(),RNG_streams=states,SGD_limit=5000)

class CausalProducer:
    def __init__(self,inputs,runner,opportunity_rng,service_rng):
        self.inputs=inputs;self.runner=runner;self.opportunity_rng=opportunity_rng;self.service_rng=service_rng
        self.next_clock=0;self.next_client=0;self.pending=[];self.p_pending=[];self.training_cpu=0.;self.training_wall=0.;self.training_samples=[]
        self.publication_bridge=[];self.operation=None;self.stop_after_steps=None
        self.pause_requested=None
        self.active_registration=None
    def invoke(self,category,fn,ceiling=2.):return self.operation(category,fn,ceiling) if self.operation else fn()
    def next_registration(self):return float('inf') if self.next_clock>=100 else round(self.next_clock+.05+.01*self.next_client,10)
    def register_current(self):
        i=self.inputs;r=self.runner;c=i.clients[self.next_client];now=self.next_registration();rng=self.opportunity_rng
        def registration():
            r.advance_time(now);strata=i.strata[c];cond=np.asarray([i.opp[(c,x)] for x in strata]);cond/=cond.sum();st=strata[int(rng.choice(len(strata),p=cond))]
            risk=list(rng.choice(i.pools[(c,st)],size=min(4,len(i.pools[(c,st)])),replace=False));tail=_block_from_stratum(st) in {2,3}
            p=np.asarray([.35*(.55 if _block_from_stratum(i.meta[u]['stratum']) in {2,3} else 1.) for u in risk]);flags=(rng.random(len(risk))<p).astype(int)
            tier=int(self.service_rng.choice([0,1,2],p=[.3,.5,.2]));download,_=sample_tau(self.service_rng,r.model_version,5)
            key=f'{self.next_clock:03d}::{c}';reg=Registration(key,c,now,download,f'tier-{tier}',f'net-tier-{tier}')
            owner=r.backend.stage1_context();group_ids=[i.meta[u]['group'] for u in risk]
            pfeatures=np.array([[1.,float(_block_from_stratum(i.meta[u]['stratum'])),float(len(risk))] for u in risk])
            obs=owner.obs_propensity.predict_batch(pfeatures)
            from .stage1 import freeze_stage1
            summary=freeze_stage1(config=r.config,target_opportunity=[owner.pi_target[(c,st)]]*len(risk),lagged_opportunity=[owner.pi_opp_joint[(c,st)]]*len(risk),
                p_obs=obs,observation=flags,group_ids=group_ids,num_groups=len(r.mu),now=now,estimator_as_of=r.backend.stage1_as_of,
                estimator_version=str(owner.p_model_version),provenance='published_catalogue_and_current_TRAIN_observations')
            r.on_register(reg,summary);self.p_pending.append((key,pfeatures.tolist(),flags.tolist()))
            records=[]
            for u,flag in zip(risk,flags):
                if flag:
                    m=i.meta[u];records.append(dict(spatial_id=m['spatial_id'],absolute_time=m['absolute_time'],time_index=m['time_index'],observed_value=i.values[(c,u)],spatial_to_idx=i.spatial,total_time_slots=i.time_slots))
            self.publication_bridge.append(dict(key=key,event='register',logical=now,utc=datetime.now(timezone.utc).isoformat()))
            self.active_registration=dict(key=key,records=records,tail=tail,tier=tier,stage='registered')
            return key,records,tail,tier
        if self.active_registration is None:
            key,records,tail,tier=self.invoke('events',registration)
        else:
            frame=self.active_registration;key,records,tail,tier=frame['key'],frame['records'],frame['tail'],frame['tier']
        if records and self.active_registration['stage']!='queued':
            if self.active_registration['stage']=='registered':
                sample={}
                def train():
                    cpu=time.process_time();wall=time.perf_counter();value=r.start_local_training(key,records,authorization=r.collection_authorization)
                    sample.update(CPU=time.process_time()-cpu,wall=time.perf_counter()-wall)
                    update,loss=value
                    if not np.isfinite(loss) or not np.all(np.isfinite(update)):raise InputError('NONFINITE_LOCAL_SGD')
                    self.training_cpu+=sample['CPU'];self.training_wall+=sample['wall']
                    self.training_samples.append(dict(key=key,**sample,E=r.attempts[key].E))
                    self.active_registration.update(stage='trained',update=update.tolist(),compute_CPU=sample['CPU'])
                    return value
                update,loss=self.invoke('training',train,2.)
                cpu=sample['CPU']
                if not np.isfinite(loss) or not np.all(np.isfinite(update)):raise InputError('NONFINITE_LOCAL_SGD')
                self.active_registration.update(stage='trained',update=update.tolist(),compute_CPU=cpu)
            else:update=np.asarray(self.active_registration['update']);cpu=self.active_registration['compute_CPU']
            def queue():
                pcs=SERVICE['compute_success'][tier]*(.75 if tail else 1.);pns=SERVICE['network_success'][tier]*(.80 if tail else 1.)
                mean=SERVICE['mean_compute'][tier]*(1.25 if tail else 1.);compute_ok=bool(self.service_rng.random()<pcs)
                duration=max(float(self.service_rng.lognormal(np.log(mean),.3)),cpu);network_ok=bool(self.service_rng.random()<pns) if compute_ok else False
                net=float(self.service_rng.lognormal(np.log(.3),.2)) if compute_ok else 0.
                outcome='completion' if compute_ok and network_ok else ('network_failure' if compute_ok else 'compute_failure')
                heapq.heappush(self.pending,(round(now+duration+net,10),key,outcome,update if outcome=='completion' else None))
                self.active_registration['stage']='queued'
            self.invoke('events',queue)
        def finish():
            self.next_client+=1
            if self.next_client==len(i.clients):self.next_client=0;self.next_clock+=1
            self.active_registration=None
        self.invoke('events',finish)
    def notices_through(self,now):
        while min(self.next_registration(),self.pending[0][0] if self.pending else float('inf'))<=now+1e-10:
            if self.pause_requested is not None and self.pause_requested():return False
            if self.next_registration()<=(self.pending[0][0] if self.pending else float('inf')):
                if self.stop_after_steps is not None and self.runner.backend.local_optimizer_steps>=self.stop_after_steps:return False
                self.register_current()
            else:
                def notify():
                    at,key,event,update=heapq.heappop(self.pending)
                    if event=='completion':self.runner.on_completion(key,at,update=update)
                    else:self.runner.on_failure(key,at,reason=event)
                    self.publication_bridge.append(dict(key=key,event=event,logical=at,utc=datetime.now(timezone.utc).isoformat()))
                self.invoke('events',notify)
        return True
    def reclaim_terminal_storage(self):
        # The declared download support is at most eight preceding versions.
        # Training at registration has finished before any version is reclaimed.
        r=self.runner
        for key in list(r.backend.updates):
            if r.attempts[key].consumed is not None:r.backend.updates.pop(key)
        for version in list(r.backend.owner.model_versions):
            if version<max(0,r.model_version-8):r.backend.owner.model_versions.pop(version)
    def after_close(self):
        r=self.runner;owner=r.backend.owner;remain=[]
        for key,features,flags in self.p_pending:
            if r.attempts[key].registration.registered_at<r.now:owner.obs_propensity.update_records_after_completion(np.asarray(features),np.asarray(flags))
            else:remain.append((key,features,flags))
        self.p_pending=remain;owner.p_model_version+=1;r.backend.freeze_stage1_context(r.now)
    def to_dict(self):
        po=asdict(self.runner.backend.owner.obs_propensity)
        for k in ('weights','_previous_weights'):po[k]=None if po[k] is None else po[k].tolist()
        po['history_x']=[x.tolist() for x in po['history_x']]
        return dict(next_clock=self.next_clock,next_client=self.next_client,pending=[dict(at=a,key=k,event=e,update=None if u is None else u.tolist()) for a,k,e,u in self.pending],
            p_pending=self.p_pending,opportunity_rng=copy.deepcopy(self.opportunity_rng.bit_generator.state),service_rng=copy.deepcopy(self.service_rng.bit_generator.state),
            training_cpu=self.training_cpu,training_wall=self.training_wall,training_samples=self.training_samples,publication_bridge=self.publication_bridge,
            active_registration=copy.deepcopy(self.active_registration),
            live_observation=po,p_model_version=self.runner.backend.owner.p_model_version)
    def restore(self,obj):
        for k in ('next_clock','next_client','p_pending','training_cpu','training_wall','training_samples','publication_bridge'):setattr(self,k,obj[k])
        self.active_registration=copy.deepcopy(obj.get('active_registration'))
        self.pending=[(x['at'],x['key'],x['event'],None if x['update'] is None else np.asarray(x['update'])) for x in obj['pending']];heapq.heapify(self.pending)
        self.opportunity_rng.bit_generator.state=obj['opportunity_rng'];self.service_rng.bit_generator.state=obj['service_rng']
        from raven_mcs.propensity.observation import ObservationPropensity
        po=copy.deepcopy(obj['live_observation'])
        for k in ('weights','_previous_weights'):po[k]=None if po[k] is None else np.asarray(po[k])
        po['history_x']=[np.asarray(x) for x in po['history_x']]
        restored=ObservationPropensity(**po)
        for k in ('weights','_previous_weights','history_x','history_y'):setattr(restored,k,po[k])
        self.runner.backend.owner.obs_propensity=restored;self.runner.backend.owner.p_model_version=obj['p_model_version']
