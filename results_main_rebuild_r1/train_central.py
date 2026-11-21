from __future__ import annotations
import os
os.environ.setdefault('CUBLAS_WORKSPACE_CONFIG', ':4096:8')
import argparse, time, copy
from concurrent.futures import ProcessPoolExecutor
from common import *
from raven_mcs.models.common_ndmf import CommonNDMF
from torch import nn

GRID = [('adam',x) for x in [3e-4,1e-3,3e-3]]+[('sgd',x) for x in [1e-3,1e-2,3e-2]]

class HistoryResidual(CommonNDMF):
    def __init__(self,num_spatial):
        super().__init__(num_spatial=num_spatial)
        self.history_mlp=nn.Sequential(nn.Linear(30,64),nn.ReLU(),nn.Linear(64,32),nn.ReLU())
        self.head[0]=nn.Linear(160,128)
    def forward(self,sp,hour,wday,trend,history):
        es=self.spatial(sp); et=self.time_mlp(self.time_features(hour,wday,trend))
        x=torch.cat([es,et,es*et,torch.abs(es-et),self.history_mlp(history)],dim=-1)
        return history[:,28]+self.head(x).squeeze(-1)

def make_model(name,ds,seed):
    torch.manual_seed(seed)
    return CommonNDMF(num_spatial=ds.num_spatial) if name=='ndmf' else HistoryResidual(ds.num_spatial)

def tensor_inputs(ds,frame,train,model,mean,std,device):
    values=list(features(ds,frame))
    if model=='history':
        _,hist,_=baseline_predictions(train,frame)
        for columns in [list(range(8)),[24,25,28,29]]:
            hist[:,columns]=(hist[:,columns]-mean)/std
        values.append(torch.tensor(hist))
    return [x.to(device) for x in values]

def run_one(spec):
    name,seed,model_name,opt_name,lr=spec[:5]
    track=spec[5] if len(spec)>5 else 'central_delivered'
    if track not in ('central_delivered','central_all'): raise ValueError(track)
    run=OUT/'P1'/track/model_name/name/f'{opt_name}_{lr:g}'/f'seed{seed}'
    if (run/'summary.json').exists(): return json.loads((run/'summary.json').read_text(encoding='utf-8'))
    ds,trace,identity=load_inputs(name,seed)
    train=pd.read_parquet(OUT/'prepared'/name/f'seed{seed}'/'delivered.parquet')
    if track=='central_all':
        train=ds.atomic_df.loc[ds.atomic_df.split=='train'].copy().reset_index(drop=True)
        train['observation']=train.target_value
    val=ds.atomic_df.loc[ds.atomic_df.split=='validation'].reset_index(drop=True)
    torch.set_num_threads(1); torch.use_deterministic_algorithms(True)
    device='cuda' if torch.cuda.is_available() else 'cpu'
    model=make_model(model_name,ds,seed).to(device)
    mean=float(train.observation.mean()); std=max(float(train.observation.std(ddof=0)),1e-6)
    tx=tensor_inputs(ds,train,train,model_name,mean,std,device)
    vx=tensor_inputs(ds,val,train,model_name,mean,std,device)
    y=torch.tensor((train.observation.to_numpy()-mean)/std,dtype=torch.float32,device=device)
    vtarget=torch.tensor(val.target_value.to_numpy(),dtype=torch.float32,device=device)
    vw,_=metric_weights(ds,name,val); vw=torch.tensor(vw,dtype=torch.float64,device=device)
    optimizer=torch.optim.Adam(model.parameters(),lr=lr,betas=(.9,.999),eps=1e-8) if opt_name=='adam' else torch.optim.SGD(model.parameters(),lr=lr,momentum=.9)
    scheduler=torch.optim.lr_scheduler.MultiStepLR(optimizer,milestones=[50,100,150],gamma=.3)
    rng=np.random.default_rng(seed+701); n=len(train); processed=0; steps=0; best=float('inf'); best100=float('inf'); best_epoch=0; rows=[]; t=time.monotonic()
    run.mkdir(parents=True,exist_ok=True)
    save(run/'config.json',dict(dataset=name,seed=seed,model=model_name,optimizer=opt_name,lr=lr,
        scaler_mean=mean,scaler_std=std,trace_hash=identity['trace_hash'],train_unique=n,information='all_train_targets_privileged' if track=='central_all' else 'train_delivered_only',budget=200,
        train_input_meaning='all training target labels (privileged)' if track=='central_all' else 'observed client measurements',validation_input_meaning='frozen target labels',test_access=False))
    print('TRAIN_START',name,seed,model_name,opt_name,lr,n,flush=True)
    for epoch in range(1,201):
        model.train(); order=rng.permutation(n); losses=[]
        for start in range(0,n,64):
            idx=torch.tensor(order[start:start+64],dtype=torch.long,device=device)
            optimizer.zero_grad(set_to_none=True)
            pred=model(*[x[idx] for x in tx]); loss=.5*torch.mean((pred-y[idx])**2)
            if not torch.isfinite(loss): raise RuntimeError(f'nonfinite training {spec} epoch {epoch}')
            loss.backward(); optimizer.step(); processed+=len(idx); steps+=1; losses.append(float(loss.detach()))
        scheduler.step(); model.eval()
        with torch.no_grad():
            prediction=model(*vx)*std+mean
            rmse=float(torch.sqrt(torch.sum(vw*(prediction.double()-vtarget.double())**2)))
            unweighted=float(torch.sqrt(torch.mean((prediction-vtarget)**2)))
            train_pred=model(*tx)
            train_loss=float(.5*torch.mean((train_pred-y)**2))
        if rmse<best:
            best=rmse; best_epoch=epoch
            torch.save(dict(state_dict=model.state_dict(),epoch=epoch,mean=mean,std=std),run/'best.pt')
            np.save(run/'best_validation_predictions.npy',prediction.detach().cpu().numpy())
        if epoch<=100: best100=min(best100,rmse)
        rows.append(dict(effective_passes=processed/n,samples_processed=processed,optimizer_steps=steps,server_updates=0,
            train_half_mse_standardized=train_loss,validation_RMSE_mu_physical=rmse,validation_RMSE_unweighted_physical=unweighted,
            best_validation_RMSE=best,lr=optimizer.param_groups[0]['lr'],elapsed_seconds=time.monotonic()-t))
        if epoch in [1,3,10,30,100,200]:
            torch.save(dict(state_dict=model.state_dict(),epoch=epoch,mean=mean,std=std),run/f'pass{epoch}.pt')
            pd.DataFrame(rows).to_csv(run/'training_curve.csv',index=False)
            print('CHECKPOINT',name,seed,model_name,opt_name,lr,epoch,round(rmse,6),round(best,6),round(time.monotonic()-t,2),flush=True)
    baseline_dir=OUT/'prepared'/name/f'seed{seed}'
    baseline_path=baseline_dir/'validation_baselines_r2.csv'
    if not baseline_path.exists():baseline_path=baseline_dir/'validation_baselines.csv'
    baselines=pd.read_csv(baseline_path)
    if 'applicable' in baselines:baselines=baselines.loc[baselines.applicable]
    if track=='central_all':
        bp,_,_=baseline_predictions(train,val)
        span=(train.absolute_time.max()-train.absolute_time.min()).total_seconds()/3600.
        baselines=pd.DataFrame([dict(baseline=k,**score(ds,name,val,p)) for k,p in bp.items() if k!='seasonal_naive_week' or span>=336])
        baselines.to_csv(run/'privileged_validation_baselines_r2.csv',index=False)
    strongest=float(baselines.RMSE_mu.min()); ref=str(baselines.loc[baselines.RMSE_mu.idxmin(),'baseline'])
    summary=dict(dataset=name,seed=seed,model=model_name,optimizer=opt_name,lr=lr,track=track,RMSE_mu=best,best_pass=best_epoch,
        best_at_100=best100,improvement_100_to_200=(best100-best)/best100,plateau_pass=(best100-best)/best100<.005,
        strongest_baseline=ref,baseline_RMSE=strongest,relative_gain=(strongest-best)/strongest,
        meaningful_validation_pass=(strongest-best)/strongest>=.02,elapsed_seconds=time.monotonic()-t,
        samples_processed=processed,optimizer_steps=steps,run=str(run.relative_to(OUT)))
    save(run/'summary.json',summary)
    print('TRAIN_DONE',json.dumps(summary),flush=True)
    return summary

def export_results(model_name):
    rows=[json.loads(p.read_text(encoding='utf-8')) for p in (OUT/'P1/central_delivered'/model_name).rglob('summary.json')]
    if not rows: return
    f=pd.DataFrame(rows); f.to_csv(OUT/f'P1_CENTRAL_{model_name.upper()}_RUNS.csv',index=False)
    summary=f.groupby(['dataset','optimizer','lr'],as_index=False).agg(n=('seed','size'),mean_RMSE=('RMSE_mu','mean'),
        mean_relative_gain=('relative_gain','mean'),all_plateau=('plateau_pass','all'),min_seed_gain=('relative_gain','min'))
    selected=[]
    for ds,part in summary.groupby('dataset'):
        valid=part.loc[(part.n==3)&part.all_plateau&(part.mean_relative_gain>=.02)]
        row=(valid if len(valid) else part).sort_values('mean_RMSE').iloc[0].to_dict()
        row['eligible']=bool(len(valid)); selected.append(row)
    save(OUT/f'P1_CENTRAL_{model_name.upper()}_SELECTION.json',dict(model=model_name,selected=selected,
        all_three_datasets_pass=len(selected)==3 and all(x['eligible'] for x in selected),test_access=False))
    import matplotlib
    matplotlib.use('Agg')
    import matplotlib.pyplot as plt
    fig,axes=plt.subplots(1,3,figsize=(15,4.5))
    for ax,name in zip(axes,DATASETS):
        part=f.loc[f.dataset==name]
        for (opt,lr),runs in part.groupby(['optimizer','lr']):
            curves=[pd.read_csv(OUT/r['run']/'training_curve.csv') for _,r in runs.iterrows()]
            vals=np.stack([c.validation_RMSE_mu_physical.to_numpy() for c in curves])
            ax.plot(curves[0].effective_passes,vals.mean(axis=0),label=f'{opt} {lr:g}')
        best_simple=np.mean([pd.read_csv(OUT/'prepared'/name/f'seed{s}'/'validation_baselines.csv').RMSE_mu.min() for s in SEEDS])
        ax.axhline(best_simple,color='black',linestyle='--',label='strongest legal baseline')
        ax.set(title=f'{name}: validation deployment RMSE',xlabel='Effective training passes',ylabel=f'RMSE ({load_dataset(name).metadata.target_unit})')
        ax.set_xscale('log'); ax.legend(fontsize=7)
    fig.suptitle(f'{model_name} / Central-delivered / seeds 41001–41003 / validation only')
    fig.tight_layout(); fig.savefig(OUT/f'P1_CENTRAL_{model_name.upper()}_CURVES.png',dpi=160); plt.close(fig)
    print('SELECTION',model_name,json.dumps(selected),flush=True)

def main():
    ap=argparse.ArgumentParser();ap.add_argument('--model',choices=['ndmf','history'],default='ndmf');ap.add_argument('--workers',type=int,default=2)
    args=ap.parse_args()
    specs=[(d,s,args.model,opt,lr) for d in DATASETS for opt,lr in GRID for s in SEEDS]
    with ProcessPoolExecutor(max_workers=args.workers) as ex:
        for result in ex.map(run_one,specs): pass
    export_results(args.model)

if __name__=='__main__': main()
