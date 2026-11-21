"""Correct multi-step seasonal-naive scoring; preserve initial artifacts.

All neural fitting used validation RMSE only. Historical neural features remain
exact daily/weekly lags, unchanged by this forecast-baseline correction.
"""
from common import *

def main():
    allrows=[]
    for name in DATASETS:
        ds=load_dataset(name)
        val=ds.atomic_df.loc[ds.atomic_df.split=='validation'].reset_index(drop=True)
        for seed in SEEDS:
            prep=OUT/'prepared'/name/f'seed{seed}'
            train=pd.read_parquet(prep/'delivered.parquet')
            pred,_,coverage=baseline_predictions(train,val)
            span=(train.absolute_time.max()-train.absolute_time.min()).total_seconds()/3600.
            rows=[]
            for method,p in pred.items():
                applicable=not(method=='seasonal_naive_week' and span<336)
                rows.append(dict(dataset=name,seed=seed,baseline=method,applicable=applicable,baseline_version='r2_multistep_phase',
                    **score(ds,name,val,p),**coverage))
            f=pd.DataFrame(rows);f.to_csv(prep/'validation_baselines_r2.csv',index=False);allrows.extend(rows)
    pd.DataFrame(allrows).to_csv(OUT/'P0_VALIDATION_BASELINES_R2.csv',index=False)
    save(OUT/'BASELINE_CORRECTION_R2.json',dict(date='2026-10-12',reason='Seasonal-naive must repeat last legally available same-season value across multi-step horizon, rather than seek only t-period.',
        information_track='offline train-delivered only',daily_period_hours=24,weekly_period_hours=168,
        weekly_applicability='at least two weeks of training time span; otherwise diagnostic only',
        model_training_changes=False,history_feature_changes=False,test_access=False,
        originals_preserved=True,authoritative_file='P0_VALIDATION_BASELINES_R2.csv'))
    print(pd.DataFrame(allrows).loc[lambda f:f.applicable].groupby(['dataset','baseline']).RMSE_mu.mean().to_string(),flush=True)

if __name__=='__main__':main()
