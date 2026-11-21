"""Uniform-weight end-to-end training with the exact cached local losses/Gate.

Vectorized clients execute one full local minibatch (risk sets have <=4 units).
Adam state resets per call, so its first bias-corrected step is g/(abs(g)+eps).
The numerical parity check compares this step with torch.optim.Adam.
"""
from __future__ import annotations
import os
os.environ.setdefault('CUBLAS_WORKSPACE_CONFIG', ':4096:8')
import argparse,time,types
from concurrent.futures import ProcessPoolExecutor
from common import *
from train_central import make_model, tensor_inputs
from torch.func import functional_call, grad, vmap

def no_control_flow(self,sp,hour,wday,trend):
    es=self.spatial(sp);et=self.time_mlp(self.time_features(hour,wday,trend))
    return self.head(torch.cat([es,et,es*et,torch.abs(es-et)],dim=-1)).squeeze(-1)

def prepare_model(model_name,ds,seed,device):
    model=make_model(model_name,ds,seed).to(device)
    if model_name=='ndmf': model.forward=types.MethodType(no_control_flow,model)
    return model

def local_loss(params,model,args,target,weights):
    pred=functional_call(model,params,tuple(args))
    return .5*torch.sum(weights*(pred-target)**2)

def verify_step():
    ds=load_dataset('traffic');torch.set_num_threads(1)
    model=prepare_model('ndmf',ds,91,'cpu');model.eval()
    p={k:v.detach().clone().requires_grad_() for k,v in model.named_parameters()}
    args=[torch.tensor([0,1,2,3]),torch.tensor([0.,6.,12.,18.]),torch.tensor([1.,2.,3.,4.]),torch.tensor([.1,.2,.3,.4])]
    y=torch.tensor([.1,.5,-.2,1.]);w=torch.tensor([.1,.2,.3,.4])
    g=grad(lambda x:local_loss(x,model,args,y,w))(p)
    expected={k:p[k]-.001*g[k]/(torch.abs(g[k])+1e-8) for k in p}
    optimizer=torch.optim.Adam(model.parameters(),lr=.001,betas=(.9,.999),eps=1e-8)
    optimizer.zero_grad();loss=.5*torch.sum(w*(model(*args)-y)**2);loss.backward();optimizer.step()
    err=max(float(torch.max(torch.abs(expected[k]-v)).detach()) for k,v in model.named_parameters())
    batched={k:torch.stack([p[k],p[k]]) for k in p}
    original=prepare_model('ndmf',ds,91,'cpu');original.eval()
    vg=vmap(grad(lambda x,a,t,b:local_loss(x,original,a,t,b)),in_dims=(0,0,0,0),randomness='different')(
        batched,[torch.stack([x,x]) for x in args],torch.stack([y,y]),torch.stack([w,w]))
    grad_err=max(float(torch.max(torch.abs(vg[k][0]-g[k])).detach()) for k in p)
    if err>2e-7 or grad_err>2e-6:raise RuntimeError((err,grad_err))
    check=dict(adam_step_max_abs_error=err,vmap_gradient_max_abs_error=grad_err,passed=True,
        source='torch.optim.Adam, identical initial parameters and weighted full local batch',test_access=False)
    save(OUT/'UNIFORM_NUMERICAL_PARITY.json',check);print('PARITY',json.dumps(check),flush=True)

def run_one(spec):
    name,seed,model_name,lr,rho=spec
    run=OUT/'P1/uniform'/model_name/name/f'adam_{lr:g}_rho{rho:g}'/f'seed{seed}'
    if (run/'summary.json').exists():return json.loads((run/'summary.json').read_text(encoding='utf-8'))
    torch.set_num_threads(1);torch.use_deterministic_algorithms(True)
    device='cuda' if torch.cuda.is_available() else 'cpu';ds=load_dataset(name)
    train=pd.read_parquet(OUT/'prepared'/name/f'seed{seed}'/'delivered.parquet')
    cache=torch.load(OUT/'prepared'/name/f'seed{seed}'/'uniform_cache.pt',weights_only=False)
    val=ds.atomic_df.loc[ds.atomic_df.split=='validation'].reset_index(drop=True)
    mean=float(train.observation.mean());std=max(float(train.observation.std(ddof=0)),1e-6)
    model=prepare_model(model_name,ds,seed,device);current={k:v.detach().clone() for k,v in model.named_parameters()}
    N=len(cache['windows'])//2; prepared=[]
    lookup=ds._atomic_df.set_index('unit_id')
    observations=ds._client_df.set_index(['client_id','unit_id']).potential_measurement
    for window in cache['windows']:
        clients=window['clients'];K=len(clients)
        if not K:prepared.append(None);continue
        maxn=max(len(c['unit_ids']) for c in clients)
        fargs=[];targets=[];weights=[];counts=[];taus=[]
        for c in clients:
            f=lookup.loc[c['unit_ids']].reset_index()
            x=tensor_inputs(ds,f,train,model_name,mean,std,device)
            y=torch.tensor([(observations.loc[(c['client_id'],u)]-mean)/std for u in c['unit_ids']],dtype=torch.float32,device=device)
            w=torch.tensor(c['weights'],dtype=torch.float32,device=device)
            count=len(y);counts.append(count);taus.append(c['tau'])
            if count<maxn:
                x=[torch.cat([z,torch.zeros((maxn-count,*z.shape[1:]),dtype=z.dtype,device=device)]) for z in x]
                y=torch.cat([y,torch.zeros(maxn-count,device=device)]);w=torch.cat([w,torch.zeros(maxn-count,device=device)])
            fargs.append(x);targets.append(y);weights.append(w)
        prepared.append(dict(args=[torch.stack([x[j] for x in fargs]) for j in range(len(fargs[0]))],
            target=torch.stack(targets),weights=torch.stack(weights),taus=taus,count=sum(counts),K=K,g_r=window['g_r']))
    vx=tensor_inputs(ds,val,train,model_name,mean,std,device)
    vt=torch.tensor(val.target_value.to_numpy(),dtype=torch.float64,device=device)
    vw,_=metric_weights(ds,name,val);vw=torch.tensor(vw,dtype=torch.float64,device=device)
    tx=tensor_inputs(ds,train,train,model_name,mean,std,device);ty=torch.tensor((train.observation.to_numpy()-mean)/std,dtype=torch.float32,device=device)
    lossgrad=vmap(grad(lambda p,a,t,w:local_loss(p,model,a,t,w)),in_dims=(0,0,0,0),randomness='different')
    versions={0:current};version=0;processed=0;calls=0;updates=0;best=float('inf');best100=float('inf');best_pass=0;curve=[];n=len(train);t=time.monotonic();cycle=0;nodes=[1,3,10,30,100,200];node=0
    run.mkdir(parents=True,exist_ok=True)
    save(run/'config.json',dict(dataset=name,seed=seed,model=model_name,lr=lr,rho=rho,mean=mean,std=std,
        trace_hash=cache['trace_hash'],policy=cache['loss_policy'],budget=200,calibration_unique_windows=cache['calibration_unique_windows'],
        optimizer_state='reset per call',loss='exact cached production Hajek weights',test_access=False,
        computation='vectorized one full local batch; no U=0 neural update can affect uniform weights or coverage Gate'))
    print('UNIFORM_START',name,seed,model_name,lr,rho,flush=True)
    while processed/n<200:
        for j in range(N):
            p=prepared[j if cycle==0 else N+j]
            if p is not None:
                model.train();torch.manual_seed(seed*100003+version)
                base=[versions[max(0,version-tau)] for tau in p['taus']]
                batched={k:torch.stack([x[k] for x in base]) for k in current}
                g=lossgrad(batched,p['args'],p['target'],p['weights'])
                passes=processed/n;factor=.3**sum(passes>=x for x in [50,100,150]);rate=lr*factor
                with torch.no_grad():
                    delta={k:rate*g[k]/(torch.abs(g[k])+1e-8) for k in current}
                    current={k:current[k]-rho*delta[k].mean(dim=0) for k in current}
                processed+=p['count'];calls+=p['K'];updates+=1
            version+=1;versions[version]=current
            versions={k:v for k,v in versions.items() if k>=version-8}
            if processed/n>=200:break
        cycle+=1;model.load_state_dict(current);model.eval()
        with torch.no_grad():
            pred=model(*vx)*std+mean;rmse=float(torch.sqrt(torch.sum(vw*(pred.double()-vt)**2)))
            tl=float(.5*torch.mean((model(*tx)-ty)**2))
        if not np.isfinite(rmse):raise RuntimeError(f'nonfinite U {spec}')
        if rmse<best:
            best=rmse;best_pass=processed/n
            torch.save(dict(state_dict=current,effective_passes=best_pass,mean=mean,std=std),run/'best.pt')
            np.save(run/'best_validation_predictions.npy',pred.detach().cpu().numpy())
        if processed/n<=100 or not np.isfinite(best100):best100=min(best100,rmse)
        curve.append(dict(effective_passes=processed/n,samples_processed=processed,local_optimizer_steps=calls,server_updates=updates,
            train_half_mse_standardized=tl,validation_RMSE_mu_physical=rmse,best_validation_RMSE=best,
            lr=lr*.3**sum(processed/n>=x for x in [50,100,150]),elapsed_seconds=time.monotonic()-t))
        if node<len(nodes) and processed/n>=nodes[node]:
            torch.save(dict(state_dict=current,effective_passes=processed/n,mean=mean,std=std),run/f'pass{nodes[node]}.pt')
            pd.DataFrame(curve).to_csv(run/'training_curve.csv',index=False)
            print('UNIFORM_CHECKPOINT',name,seed,lr,rho,nodes[node],round(rmse,6),round(best,6),round(time.monotonic()-t,2),flush=True);node+=1
    pd.DataFrame(curve).to_csv(run/'training_curve.csv',index=False)
    baseline_dir=OUT/'prepared'/name/f'seed{seed}'
    baseline_path=baseline_dir/'validation_baselines_r2.csv'
    if not baseline_path.exists():baseline_path=baseline_dir/'validation_baselines.csv'
    b=pd.read_csv(baseline_path)
    if 'applicable' in b:b=b.loc[b.applicable]
    ref=b.loc[b.RMSE_mu.idxmin()]
    r=dict(dataset=name,seed=seed,model=model_name,lr=lr,rho=rho,RMSE_mu=best,best_pass=best_pass,best_at_100=best100,
        improvement_100_to_200=(best100-best)/best100,plateau_pass=(best100-best)/best100<.005,
        strongest_baseline=ref.baseline,baseline_RMSE=float(ref.RMSE_mu),relative_gain=(float(ref.RMSE_mu)-best)/float(ref.RMSE_mu),
        elapsed_seconds=time.monotonic()-t,samples_processed=processed,optimizer_steps=calls,server_updates=updates,run=str(run.relative_to(OUT)))
    save(run/'summary.json',r);print('UNIFORM_DONE',json.dumps(r),flush=True);return r

def export(model):
    f=pd.DataFrame([json.loads(p.read_text(encoding='utf-8')) for p in (OUT/'P1/uniform'/model).rglob('summary.json')])
    f.to_csv(OUT/f'P1_UNIFORM_{model.upper()}_RUNS.csv',index=False)
    selected=[]
    for name,part in f.groupby('dataset'):
        tab=part.groupby(['lr','rho'],as_index=False).agg(n=('seed','size'),mean_RMSE=('RMSE_mu','mean'),mean_relative_gain=('relative_gain','mean'),all_plateau=('plateau_pass','all'))
        valid=tab.loc[(tab.n==3)&tab.all_plateau&(tab.mean_relative_gain>=.02)]
        row=(valid if len(valid) else tab).sort_values('mean_RMSE').iloc[0].to_dict();row['dataset']=name;row['eligible']=bool(len(valid));selected.append(row)
    result=dict(model=model,selected=selected,all_three_datasets_pass=len(selected)==3 and all(x['eligible'] for x in selected),test_access=False)
    save(OUT/f'P1_UNIFORM_{model.upper()}_SELECTION.json',result);print('UNIFORM_SELECTION',json.dumps(result),flush=True)

def main():
    ap=argparse.ArgumentParser();ap.add_argument('--model',choices=['ndmf','history'],default='ndmf');ap.add_argument('--workers',type=int,default=2);ap.add_argument('--check-only',action='store_true');ap.add_argument('--single',action='store_true');args=ap.parse_args()
    verify_step()
    if args.check_only:return
    if args.single:
        run_one(('traffic',41001,args.model,.003,.5));return
    specs=[(d,s,args.model,lr,rho) for d in DATASETS for lr in [3e-4,1e-3,3e-3] for rho in [.5,1.] for s in SEEDS]
    with ProcessPoolExecutor(max_workers=args.workers) as ex:
        for r in ex.map(run_one,specs):pass
    export(args.model)

if __name__=='__main__':main()
