"""Fixed OFq-public-state-1.1: 37 numeric columns, no fit or future inputs."""
import json,math,time
import numpy as np
from dataclasses import asdict
VERSION='OFq-public-state-1.1'
NAMES=tuple([f'age{i}' for i in range(6)]+['remaining','elapsed','slack','P_count','F_count_scaled','P_mean_age','F_mean_age','P_oldest_age','F_oldest_age',
    'L_ell','L_age','L_duration','L_gap','has_L','Q_size','Q_P_alignment','Q_L_alignment','P_distance','P_effective_n','P_mass','has_P',
    'V_mean','V_max','has_V','root_remaining_fraction','root_sample_age','root_sample_valid','remaining_elapsed','remaining_P','remaining_age','elapsed_Q_P'])
def encode_public_registration(features,mu,version):
    h=json.loads(features.history_json);P=h['pool'];F=h['public_inflight'];L=h['last'];Q=np.asarray(h['debt']);mu=np.asarray(mu)
    qhat=Q/(1+Q.sum());remaining=(100-features.as_of)/100;elapsed=h['elapsed']/4;slack=features.maximum_deadline_slack/4
    def ages(pool):return [(version-m['registration']['downloaded_version'])/5 for m in pool]
    pa=ages(P);fa=ages(F);pbar=np.mean([np.asarray(m['summary']['masses'])/sum(m['summary']['masses']) for m in P],axis=0) if P else mu.copy()
    palign=float(qhat@(pbar-mu)) if P else 0.;lalign=float(qhat@(np.asarray(L['omega'])-mu)) if L else 0.
    pe=float(np.mean([m['summary']['effective_n'] for m in P])) if P else 0.;pm=float(np.mean([sum(m['summary']['masses']) for m in P])) if P else 0.
    vals=list(h['variance'].values());vm=float(np.mean(vals)) if vals else 0.;vx=max(vals) if vals else 0.
    root=h.get('root_resource',{});valid=bool(root.get('valid'));sample_age=max(0.,root.get('sample_age_at_read',0.)) if valid else 0.
    values=[int(features.model_age==i) for i in range(6)]+[remaining,elapsed,slack,len(P)/43,len(F)/(43+len(F)),
        np.mean(pa) if pa else 0,np.mean(fa) if fa else 0,max(pa) if pa else 0,max(fa) if fa else 0,
        L['ell'] if L else 0,L['age'] if L else 0,L['duration']/4 if L else 0,min(100,features.as_of-L['time'])/100 if L else 0,int(bool(L)),
        float(Q.sum()/(1+Q.sum())),palign,lalign,.5*float(np.abs(pbar-mu).sum()) if P else 0,pe/(1+pe),pm/(1+pm),int(bool(P)),
        vm/(1+vm),vx/(1+vx),int(bool(vals)),root.get('effective_remaining',0.)/3600 if valid else 0,sample_age,int(valid),
        remaining*elapsed,remaining*len(P)/43,remaining*features.model_age/5,elapsed*palign]
    assert len(values)==len(NAMES)==37
    lawful=all(math.isfinite(float(x)) for x in values) and 0<=features.model_age<=5 and valid and len(P)<=43
    return dict(version=VERSION,names=NAMES,values=[float(x) for x in values],raw_F_count=len(F),raw_P_count=len(P),
        public_categories=dict(device=features.device_class,network=features.network_class),support='IN_SCHEMA_DOMAIN_NOT_EMPIRICAL_SUPPORT' if lawful else 'ENCODING_DOMAIN_OR_RESOURCE_MISSING',
        data_role='diagnostic_archive_not_fitted_probability')
