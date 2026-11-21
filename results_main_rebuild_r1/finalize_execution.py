"""Authoritative R2 aggregation, saved-prediction QA, curves and stop report."""
from common import *
import matplotlib
matplotlib.use('Agg')
import matplotlib.pyplot as plt

UNITS={'traffic':'vehicles/h','sensorscope':'deg C','uair':'ug/m3'}
NAMES={'traffic':'Traffic','sensorscope':'SensorScope','uair':'U-Air'}

def main():
    baselines=pd.read_csv(OUT/'P0_VALIDATION_BASELINES_R2.csv')
    refs={}
    for (d,s),part in baselines.loc[baselines.applicable].groupby(['dataset','seed']):
        refs[(d,s)]=part.loc[part.RMSE_mu.idxmin()]
    datasets={d:load_dataset(d) for d in DATASETS}
    queries={d:ds.atomic_df.loc[ds.atomic_df.split=='validation'].reset_index(drop=True) for d,ds in datasets.items()}
    rows=[];checks=[];curve_metrics=[];net_displacements=[]
    for p in sorted((OUT/'P1').rglob('summary.json')):
        r=json.loads(p.read_text(encoding='utf-8'));run=p.parent;d=r['dataset'];s=r['seed']
        track=run.relative_to(OUT/'P1').parts[0]
        config=json.loads((run/'config.json').read_text(encoding='utf-8'))
        direct=score(datasets[d],d,queries[d],np.load(run/'best_validation_predictions.npy'))
        error=abs(direct['RMSE_mu']-r['RMSE_mu'])
        if error>1e-4:raise RuntimeError(('saved prediction score mismatch',str(run),error))
        curve=pd.read_csv(run/'training_curve.csv')
        if len(curve)==0 or curve.effective_passes.iloc[-1]<200:raise RuntimeError('incomplete budget')
        if track!='uniform' and len(curve)!=200:raise RuntimeError('central curve length')
        if track=='central_all':
            b=pd.read_csv(run/'privileged_validation_baselines_r2.csv');ref=b.loc[b.RMSE_mu.idxmin()]
        else:ref=refs[(d,s)]
        r.update(track=track,scoring_version='r2_physical_float64',original_training_summary_RMSE=r['RMSE_mu'],
            RMSE_mu=direct['RMSE_mu'],MAE_mu=direct['MAE_mu'],WorstGroupRMSE=direct['WorstGroupRMSE'],
            strongest_baseline=ref.baseline,baseline_RMSE=float(ref.RMSE_mu),
            relative_gain=(float(ref.RMSE_mu)-direct['RMSE_mu'])/float(ref.RMSE_mu),
            meaningful_validation_pass=(float(ref.RMSE_mu)-direct['RMSE_mu'])/float(ref.RMSE_mu)>=.02,
            information=config.get('information','train_delivered_only'))
        rows.append(r)
        checks.append(dict(run=str(run.relative_to(OUT)),saved_prediction_score_difference=error,budget_complete=True,
            curve_best_matches_summary=bool(abs(curve.best_validation_RMSE.min()-r['original_training_summary_RMSE'])<1e-8)))
        if not checks[-1]['curve_best_matches_summary']:raise RuntimeError('curve best mismatch')
        for node in (1,3,10,30,100,200):
            ck=run/f'pass{node}.pt'
            if not ck.exists():raise RuntimeError(('missing checkpoint',str(ck)))
            state=torch.load(ck,map_location='cpu',weights_only=False)['state_dict']
            if node==1:previous=state
            else:
                net_displacements.append(dict(run=str(run.relative_to(OUT)),budget_node=node,
                    parameter_displacement_from_previous_saved_node=float(np.sqrt(sum(float(torch.sum((state[k]-previous[k])**2)) for k in state))),
                    scope='net checkpoint displacement, not per-update norm'))
                previous=state
    runs=pd.DataFrame(rows);runs.to_csv(OUT/'P1_ALL_RUNS_R2.csv',index=False)
    pd.DataFrame(net_displacements).to_csv(OUT/'P1_CHECKPOINT_DISPLACEMENTS.csv',index=False)
    central=runs.loc[runs.track=='central_delivered']
    if len(central)!=108:raise RuntimeError(('central count',len(central)))
    grouped=central.groupby(['model','dataset','optimizer','lr'],as_index=False).agg(n=('seed','size'),
        mean_RMSE=('RMSE_mu','mean'),sd_RMSE=('RMSE_mu','std'),baseline_RMSE=('baseline_RMSE','mean'),
        mean_relative_gain=('relative_gain','mean'),all_plateau=('plateau_pass','all'),min_seed_gain=('relative_gain','min'))
    grouped.to_csv(OUT/'P1_CENTRAL_GRID_R2.csv',index=False)
    selected=[]
    for (model,d),part in grouped.groupby(['model','dataset']):
        valid=part.loc[(part.n==3)&part.all_plateau&(part.mean_relative_gain>=.02)]
        row=(valid if len(valid) else part).sort_values('mean_RMSE').iloc[0].to_dict()
        row['eligible']=bool(len(valid));selected.append(row)
    selection=pd.DataFrame(selected);selection.to_csv(OUT/'P1_CENTRAL_SELECTED_R2.csv',index=False)
    passes={m:bool(g.eligible.all() and len(g)==3) for m,g in selection.groupby('model')}
    if any(passes.values()):raise RuntimeError('unified central gate passed; continue uniform search instead of stop')
    # Training and validation curves for the six selected configurations.
    fig,axs=plt.subplots(2,3,figsize=(15,8.3))
    for col,d in enumerate(DATASETS):
        for model,color,label in [('ndmf','#226596','Common-NDMF'),('history','#c36e27','HistoryResidual')]:
            choice=selection.loc[(selection.model==model)&(selection.dataset==d)].iloc[0]
            part=central.loc[(central.model==model)&(central.dataset==d)&(central.optimizer==choice.optimizer)&(central.lr==choice.lr)]
            traincurves=[];valcurves=[]
            for _,r in part.iterrows():
                cfg=json.loads((OUT/r.run/'config.json').read_text(encoding='utf-8'));curve=pd.read_csv(OUT/r.run/'training_curve.csv')
                traincurves.append(np.sqrt(2*curve.train_half_mse_standardized.to_numpy())*cfg['scaler_std'])
                valcurves.append(curve.validation_RMSE_mu_physical.to_numpy())
            traincurves=np.stack(traincurves);valcurves=np.stack(valcurves)
            x=np.arange(1,201)
            for ax,arr in [(axs[0,col],traincurves),(axs[1,col],valcurves)]:
                ax.plot(x,arr.mean(axis=0),color=color,label=f'{label}, {choice.optimizer} {choice.lr:g}')
                ax.fill_between(x,arr.min(axis=0),arr.max(axis=0),color=color,alpha=.12)
                ax.set_xscale('log');ax.set_xlabel('Effective training passes');ax.set_ylabel(f'RMSE ({UNITS[d]})')
            for seed,rtrain,rval in zip(part.seed,traincurves,valcurves):
                curve_metrics.extend(dict(dataset=d,model=model,seed=int(seed),pass_id=i+1,train_RMSE_physical=float(t),validation_RMSE_mu=float(v)) for i,(t,v) in enumerate(zip(rtrain,rval)))
        meanref=np.mean([refs[(d,s)].RMSE_mu for s in SEEDS])
        axs[1,col].axhline(meanref,color='black',linestyle='--',label='Strongest applicable simple baseline (seed mean)')
        axs[0,col].set_title(f'{NAMES[d]}: delivered-observation train RMSE')
        axs[1,col].set_title(f'{NAMES[d]}: deployment-weighted validation RMSE')
        for ax in axs[:,col]:ax.legend(fontsize=7)
    fig.suptitle('Central-delivered: mean and seed range, seeds 41001-41003; validation only',fontsize=12)
    fig.tight_layout();fig.savefig(OUT/'P1_TRAIN_VALIDATION_CURVES_R2.png',dpi=170);plt.close(fig)
    pd.DataFrame(curve_metrics).to_csv(OUT/'P1_SELECTED_TRAIN_VALIDATION_CURVES_R2.csv',index=False)
    # All optimizer alternatives remain visible, rather than only successful runs.
    fig,axs=plt.subplots(2,3,figsize=(15,8))
    for row,model in enumerate(('ndmf','history')):
        for col,d in enumerate(DATASETS):
            ax=axs[row,col]
            for (opt,lr),part in central.loc[(central.dataset==d)&(central.model==model)].groupby(['optimizer','lr']):
                values=np.stack([pd.read_csv(OUT/r.run/'training_curve.csv').validation_RMSE_mu_physical for _,r in part.iterrows()])
                ax.plot(np.arange(1,201),values.mean(axis=0),label=f'{opt} {lr:g}',linewidth=1.1)
            ax.axhline(np.mean([refs[(d,s)].RMSE_mu for s in SEEDS]),color='black',linestyle='--',label='Strongest legal simple')
            ax.set(title=f'{model} / {NAMES[d]}',xlabel='Effective passes',ylabel=f'Validation RMSE ({UNITS[d]})');ax.set_xscale('log');ax.legend(fontsize=6)
    fig.suptitle('All six optimizer configurations per backbone; seed means; validation only')
    fig.tight_layout();fig.savefig(OUT/'P1_ALL_OPTIMIZER_CURVES_R2.png',dpi=170);plt.close(fig)
    # A single development U trajectory, explicitly separate from seed confirmation.
    u=runs.loc[runs.track=='uniform'].iloc[0];uc=pd.read_csv(OUT/u.run/'training_curve.csv')
    fig,axs=plt.subplots(1,2,figsize=(11,4))
    axs[0].plot(uc.effective_passes,uc.validation_RMSE_mu_physical,label='Uniform / Traffic / seed 41001')
    axs[0].axhline(u.baseline_RMSE,color='black',linestyle='--',label='Strongest applicable simple baseline')
    axs[0].set(xlabel='Effective passes',ylabel='Validation RMSE (vehicles/h)',title='Uniform development trajectory');axs[0].legend(fontsize=8)
    axs[1].plot(uc.samples_processed,uc.server_updates)
    axs[1].set(xlabel='Observed samples processed (count)',ylabel='Server updates (count)',title='Recorded training budget')
    fig.tight_layout();fig.savefig(OUT/'P1_UNIFORM_TRAFFIC_DEVELOPMENT.png',dpi=160);plt.close(fig)
    # Check unchanged source data and legal history, including a multi-step example.
    sources=json.loads((OUT/'P0_DATA_AUDIT.json').read_text(encoding='utf-8'))
    for x in sources:
        d=x['dataset']
        if str(datasets[d].atomic_df.absolute_time.dtype)!='datetime64[ns, UTC]':raise RuntimeError('original training timestamps were not ns')
        for seed in SEEDS:
            if str(pd.read_parquet(OUT/'prepared'/d/f'seed{seed}'/'delivered.parquet').absolute_time.dtype)!='datetime64[ns, UTC]':raise RuntimeError('delivered training timestamps were not ns')
        if sha(ROOT/'data/processed'/d/'atomic_units.parquet')!=x['source_atomic_sha']:raise RuntimeError('atomic source changed')
        if sha(ROOT/'data/processed'/d/'client_measurements.parquet')!=x['source_client_sha']:raise RuntimeError('measurement source changed')
    dummy=pd.DataFrame(dict(spatial_id=['s','s'],absolute_time=pd.to_datetime(['2026-01-01T00:00Z','2026-01-02T00:00Z']),observation=[1.,2.]))
    q=pd.DataFrame(dict(spatial_id=['s','s'],absolute_time=pd.to_datetime(['2026-01-02T00:00Z','2026-01-05T00:00Z'])))
    bp,h,_=baseline_predictions(dummy,q)
    if not np.array_equal(bp['persistence'],[1.,2.]) or not np.array_equal(bp['seasonal_naive_day'],[1.,2.]):raise RuntimeError('history timestamp or multistep baseline error')
    if h[0,0]!=1. or h[0,8]!=1.:raise RuntimeError('current query observation included')
    save(OUT/'EXECUTION_QA.json',dict(passed=True,trajectories_checked=len(checks),central_delivered_trajectories=108,
        max_saved_score_difference=max(x['saved_prediction_score_difference'] for x in checks),
        all_curves_200_passes=True,all_checkpoints_present=True,source_data_unchanged=True,
        strict_recent_history_excludes_query_timestamp=True,multistep_seasonal_baseline_checked=True,
        pandas_time_resolution_guard='all actual source and delivered timestamps ns; explicitly normalize us inputs to ns; no fitted input changes',
        no_test_forecasts_or_scores=True,details=checks))
    geom=pd.read_csv(OUT/'P2_GEOMETRY_SUMMARY.csv')
    supply=pd.DataFrame(json.loads((OUT/'P0_SUPPLY_AUDIT.json').read_text(encoding='utf-8')))
    total=dict(training_trajectories=len(runs),central_delivered=108,uniform_development=int((runs.track=='uniform').sum()),
        privileged_diagnostic=int((runs.track=='central_all').sum()),samples_processed=int(runs.samples_processed.sum()),
        optimizer_steps=int(runs.optimizer_steps.sum()),sum_trajectory_wall_seconds=float(runs.elapsed_seconds.sum()))
    stop=dict(status='STOP_P1_NO_VALID_UNIFIED_BACKBONE',date='2026-10-12',central_gate=passes,
        gate_threshold_mean_relative_gain=.02,plateau_tolerance=.005,formal_tests_scored=False,
        U_B_P_R_end_to_end_confirmation_started=False,main_experiment_complete=False,
        reason='Neither of the two prespecified backbones passed all three dataset learning gates. Uniform development curve also failed budget plateau.',
        totals=total,authoritative_baselines='P0_VALIDATION_BASELINES_R2.csv',authoritative_runs='P1_ALL_RUNS_R2.csv')
    save(OUT/'EXECUTION_STATUS.json',stop)
    lines=['# RAVEN-MCS 主实验重建：执行报告','',
        '日期：2026-10-12。依据：2026-10-11 主实验重建协议；执行范围来自用户“请按你的实验方案执行”。交接材料中的历史数字作为背景，不作为新增实验结果。','',
        '**当前状态：学习门槛未通过，按协议停在 P1。主实验重建尚未完成，也没有新增 RAVEN 收益结论。** 两套预定骨干均没有在三块数据上通过 Central-delivered 门槛，不能进入昂贵的四臂确认。','',
        '## 1. 实际完成的工作','',
        f'- 9 条正式生成的开发事件轨迹：3 个数据集 × 3 个开发种子（41001–41003），每条采用原 nominal 参与规则和 2000 次机会 Monte Carlo；Traffic/SensorScope 各 100 个唯一窗口，U-Air 80 个。',
        f'- 108 条 Central-delivered 训练：2 套统一骨干 × 3 数据集 × 6 个优化器配置 × 3 种子，每条 200 个有效遍历。',
        '- 1 条 Traffic 均匀联邦开发训练，达到 200 个有效遍历；本地 Adam 每调用重置状态，服务器使用原始位移，真实陈旧模型版本。它只用于开发诊断。',
        '- 3 条 U-Air Central-all 特权诊断，沿用已选择的 SGD 0.03，未另搜优化器；全部训练标签可见，每条 200 遍历。',
        f'- 总计 {total["training_trajectories"]} 条训练轨迹，处理 {total["samples_processed"]:,} 个样本次，执行 {total["optimizer_steps"]:,} 个 optimizer steps。单条运行时间之和 {total["sum_trajectory_wall_seconds"]:.1f} 秒；并行运行，不能将其当作任务实际经过时间或纯 GPU 时间。',
        '- 完成自然窗口及 Traffic K/ESS/cap 的无标签几何诊断。未启动正式种子 42001–42020 的训练或测试评分。','',
        '## 2. 信息条件、计分与实施修正','',
        '沿用时间顺序 train/validation/test 划分。训练与基线只用 U=1 的已交付训练观测；持久性和滞后特征只访问查询时间之前的训练观测，验证期和测试期标签均不回灌历史。均值、空间均值与季节均值是训练集拟合统计量；历史残差模型的这些参考统计量采用离线训练拟合，不能解读为每个训练时点的在线可用信息。所有候选共享观测拟合 scaler，验证预测反变换至物理单位；部署评分采用冻结空间×时间 mu 和 float64 物理目标。','',
        'Traffic 的 metadata 明确目标为 traffic_volume（vehicles/h）；原通用 loader 的 average_speed 标签不能沿用。其客户端观测按正式 TrafficE3Dataset 的 station=client、精确流量测量构造到新目录。SensorScope/U-Air 沿用现有受控客户端测量，训练观测与目标真值的差异属于现有任务定义。','',
        '执行期间修正 seasonal-naive：多步预测重复最近合法、同周期相位的观测，而不是仅查找 t−24h/t−168h。周基线要求训练观测跨至少两周；SensorScope/U-Air 的周结果只作诊断。修正在验证阶段完成，未更改神经模型输入、拟合过程或测试协议。R2 CSV/图/本报告是权威汇总；原始基线和原 summary 保留，但其中旧 seasonal-naive/relative_gain 已被 R2 汇总替代。原神经 summary 使用 float32 标签评估；R2 从保存预测以 float64 真值重计分，数值差异见 QA。','',
        '源数据加载会读到包含测试行的整张表；P0 查看测试划分元数据，生产 pi_target 使用冻结测试人群的 client/stratum 组成。这不是测试标签预测或调参。未执行测试预测、测试误差、测试 checkpoint 选择。','',
        '## 3. 学习门槛：验证集，三个开发种子','',
        '表中 RMSE 是三个种子的均值；最强适用基线按种子选出，收益为种子配对相对改善的均值。门槛：平均改善至少 2%，且三个种子的 100→200 最佳验证误差改善均小于 0.5%。这是开发筛选，未作统计确认。','',
        '| 骨干 | 数据集 | 优化器 / LR | 基线 RMSE | 模型 RMSE ± SD | 配对改善 | 平台 | 达标 |',
        '|---|---|---|---:|---:|---:|---|---|']
    for _,r in selection.iterrows():
        lines.append(f'| {r.model} | {NAMES[r.dataset]} ({UNITS[r.dataset]}) | {r.optimizer} / {r.lr:g} | {r.baseline_RMSE:.4f} | {r.mean_RMSE:.4f} ± {r.sd_RMSE:.4f} | {100*r.mean_relative_gain:.2f}% | {"是" if r.all_plateau else "否"} | {"是" if r.eligible else "否"} |')
    lines+=['','Common-NDMF 在 Traffic/SensorScope 的 Central-delivered 筛选中达标；U-Air 失败。HistoryResidual 在 Traffic 达标，SensorScope/U-Air 失败。因此没有候选可成为协议要求的三数据集有效统一骨干。学习门槛要求集中式与均匀联邦都通过，不能把当前集中式达标直接称为主实验达标。','',
        f'Traffic 的单条 Uniform 开发训练：Adam 0.003，rho=0.5，RMSE={u.RMSE_mu:.4f} vehicles/h，相对最强适用简单基线改善 {100*u.relative_gain:.2f}%；100→200 最佳验证 RMSE 改善 {100*u.improvement_100_to_200:.3f}%，超过 0.5% 容忍度，尚不能认定预算充分。缺少其余配置与种子确认。','',
        'U-Air Central-all 的三个特权模型平均 RMSE 为 '+f'{runs.loc[runs.track=="central_all"].RMSE_mu.mean():.4f} ug/m3；同信息的空间均值基线为 {runs.loc[runs.track=="central_all"].baseline_RMSE.mean():.4f}。'+
        '扩大到全部训练标签仍未超过其简单基线，且最佳 checkpoint 很早出现，延长训练出现验证恶化。因此不能只用交付稀疏解释全部失败；该单配置诊断也不能证明所有容量或优化方案都无效。','',
        '## 4. 参与与可行域诊断','',
        '| 自然轨迹 | 活跃窗口数 | K 最大值 | 单点可行域比例 | 有实际组自由度比例 | 设计校正 gate 开启比例 |',
        '|---|---:|---:|---:|---:|---:|']
    for _,r in geom.loc[geom.condition=='natural_original'].iterrows():
        lines.append(f'| {NAMES[r.dataset]} | {r.windows} | {r.K_max} | {100*r.singleton_share:.2f}% | {100*r.high_freedom_share:.2f}% | {100*r.gate_on_share:.2f}% |')
    maincond=geom.loc[geom.condition=='fixedK8_ESS0.5_cap2K'].iloc[0]
    lines+=['','这些比例以活跃窗口为分母；原约束 ESS_min=3、cap=0.5。SensorScope/U-Air 的退化问题在本次新轨迹中仍然存在。gate 开启指生产 aggregate-coverage 的设计校正开关，不代表完整 RAVEN 所有目标项是否启用。零更新探针只用于捕获不依赖神经更新的 U 权重、损失和 gate，不构成模型结果或完整 RAVEN 实验。','',
        f'Traffic 的 K=8、ESS=4、cap=0.25 组成诊断：从自然 K≥8 窗口取排序前 8 个不同客户端，共 {maincond.windows} 个窗口，全部达到 rank≥1 且至少两组 W_g≥0.01 的筛选条件。平均可调整部署质量只有 {100*maincond.mean_adjustable_mass:.2f}%；单窗未覆盖整个时间部署目标是结构特征，不能把全局不可达质量归零。',
        '已分别计算 K=4/8，ESS ratio=0.25/0.5/0.8 及 K=8 的 cap=1.5/K、2/K、4/K。自然轨迹最大 K=15，因此没有可用的 K=16 组成载荷；P1 停止后未生成受控 K=16 调度。按 K 截取的组成诊断不等于新的受控参与实验，也不支持按 K 的预测效果结论。','',
        f'主条件下，校正参考违反约束的窗口比例为 {100*maincond.beta_violation_share:.2f}%，纯投影平均 L2 修复距离为 {maincond.mean_projection_distance:.6f}。逐组 min/max/W、每窗 rank、ESS、投影距离和约束强度均已输出。最初 CLARABEL 对一次投影返回 optimal_inaccurate，未接受该结果；全部投影改用凸问题的 KKT 双重标量搜索并逐次核验可行性与驻点条件。组范围的 CLARABEL 求解全部为 optimal。','',
        '## 5. 证据边界与下一步','',
        '没有运行 U/B/P/R 的端到端确认，没有新测试 RMSE、置信区间、显著性或 RAVEN 增益。纯投影结果仅是几何诊断；没有四臂同 prestate 更新差，也没有完成新版完整 RAVEN runner 与 Adam 原始位移协议的集成。不能以这些缺失值补成论文主结果。','',
        '本轮已排除“只运行旧短预算所以无法判断”的一部分解释：对两套预定骨干做了统一 200 遍历与优化器搜索，并保留全部曲线；仍未建立三数据集有效骨干。它不排除其它模型、优化方案、信息轨道或有效采样调度的改进空间。下一轮应先针对 U-Air 的空间均值残差与时间外推验证继续设计学习模型；若扩充候选超出本协议，应明确形成新的验证协议，测试集继续留待配置冻结后一次性评价。Traffic 若独立开展机制研究，也须另行声明条件研究范围，并先让均匀联邦跨种子达到预算平台。','',
        '集中式逐 run 曲线含训练物理 RMSE、部署加权和未加权验证误差、样本处理量、optimizer steps 与时间。均匀开发轨迹仅记录部署加权验证误差。旧 run 没有逐步更新范数日志；补充的 checkpoint displacement 是两个保存节点之间的净参数位移，不能替代逐步更新范数。未来四臂执行时须补齐这些日志。','',
        'Uniform 缓存沿用生产 window 级校准统计，并禁止重放窗口再次加入 gate history；首轮仍可能在不同真实事件中重复遇到相同 unit ID。本次尚未实现协议所写的跨首轮 unit-ID 去重校准规则，因此该均匀轨迹只保留为优化开发诊断，不作为新版 gate 的确认。正式四臂前必须明确 unit/event 校准语义并实现既定去重规则，不能把窗口数冒充独立单元数。集中式学习失败及本轮停止原因不依赖这个 gate。','',
        '## 6. 文件索引与复现','',
        '- `EXECUTION_STATUS.json`：停止原因、队列状态和实际预算。',
        '- `P1_ALL_RUNS_R2.csv` / `P1_CENTRAL_GRID_R2.csv` / `P1_CENTRAL_SELECTED_R2.csv`：权威新结果。',
        '- `P0_VALIDATION_BASELINES_R2.csv`：适用性、物理单位预测基线与历史覆盖。',
        '- `P1_TRAIN_VALIDATION_CURVES_R2.png` / `P1_ALL_OPTIMIZER_CURVES_R2.png` / `P1_UNIFORM_TRAFFIC_DEVELOPMENT.png`：真实训练曲线。',
        '- `P2_GEOMETRY_WINDOWS.csv` / `P2_GEOMETRY_GROUP_RANGES.csv` / `P2_GEOMETRY_SUMMARY.csv` / `P2_GEOMETRY_AUDIT.json`：每窗与各约束条件诊断。',
        '- `EXECUTION_QA.json` / `UNIFORM_NUMERICAL_PARITY.json`：保存预测重评分、200 遍历、checkpoint、源数据、历史与 Adam 数值语义核验。',
        '- `P1/`：每条运行的 config、summary、训练曲线、最佳模型及预算 checkpoint；`prepared/`：交付样本与精确 U 损失缓存；`eventtraces/`：唯一真实事件轨迹。','',
        '所有新增执行器、配置和结果位于本目录；未覆盖 src、论文或旧冻结结果，未 commit/push。','',
        '使用项目 `.venv_new/Scripts/python.exe`。按以下顺序复现；已有完成 summary 会复用，不重复训练：','',
        '```text',
        'results_main_rebuild_r1/prepare.py',
        'results_main_rebuild_r1/refresh_baselines.py',
        'results_main_rebuild_r1/train_central.py --model ndmf',
        'results_main_rebuild_r1/train_central.py --model history',
        'results_main_rebuild_r1/prepare_uniform.py',
        'results_main_rebuild_r1/train_uniform.py --single',
        'results_main_rebuild_r1/diagnose_information.py',
        'results_main_rebuild_r1/diagnose_geometry.py',
        'results_main_rebuild_r1/finalize_execution.py',
        '```','',
        '不要在当前停止状态直接调用 train_uniform.py 的完整网格入口并继续聚合确认；该入口保留用于新协议通过学习门槛后执行。']
    (OUT/'EXECUTION_REPORT.md').write_text('\n'.join(lines)+'\n',encoding='utf-8')
    print(selection.to_string(index=False),flush=True)
    print('STATUS',json.dumps(stop),flush=True)

if __name__=='__main__':main()
