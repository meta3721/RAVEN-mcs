"""Deterministic figure-only rendering from existing, unmodified result CSVs.

No model loading, predictions, training, statistical tests, or solver calls.
Run selected names with --only; main paper make_figures.main() is never called.
"""
from pathlib import Path
import argparse
import json
import hashlib
import matplotlib
matplotlib.use('Agg')
import matplotlib.pyplot as plt
from matplotlib.lines import Line2D
from matplotlib.ticker import MaxNLocator, ScalarFormatter, LogLocator, NullFormatter
import numpy as np
import pandas as pd

P=Path(__file__).resolve().parent
R=P.parent
DATA=P/'figure_data'
METHODS=['FedAvg-Window','FedAsync-Window','TimeAlign-Agg','Local-Hajek','TwoStage-Hajek','RAVEN-MCS']
LABELS=['FedAvg','FedAsync','TimeAlign','Local-Hájek','TwoStage-Hájek','RAVEN-Design']
COLORS=['#77818B','#82947B','#AF9276','#9B88A0','#5C8F98','#365E83']
MARKERS=['o','s','^','D','v','P']
E2=[METHODS[i] for i in [0,1,2,4,5]]
OUT=P/'figures/data_figures_revision_candidate'
LEDGER={}


def style():
    plt.rcParams.update({'font.family':'serif','font.serif':['Times New Roman','DejaVu Serif'],
      'mathtext.fontset':'stix','font.size':9.1,'axes.labelsize':9.6,'xtick.labelsize':9.1,
      'ytick.labelsize':9.1,'legend.fontsize':9.1,'axes.linewidth':.65,
      'pdf.fonttype':42,'ps.fonttype':42,'svg.fonttype':'none','savefig.dpi':250,
      'axes.unicode_minus':True,'hatch.linewidth':.35})


def frame(ax):
    ax.tick_params(direction='out',length=2.3,width=.6,pad=2)
    for spine in ax.spines.values():spine.set_color('#69737B')
    ax.grid(axis='x',color='#E5E8EB',linewidth=.4,zorder=0)
    ax.set_axisbelow(True)


def panel(ax,label,y=-.27):
    """A separate artist: never replaces an axis label."""
    return ax.text(.5,y,label,transform=ax.transAxes,ha='center',va='top',fontsize=9.3,clip_on=False)


def save(fig,name,record):
    OUT.mkdir(parents=True,exist_ok=True)
    fig.canvas.draw()
    for ext in ['pdf','svg','png']:
        fig.savefig(OUT/(name+'.'+ext),facecolor='white')
    record['size_inches']=list(fig.get_size_inches())
    record['axis_labels']=[{'x':a.get_xlabel(),'y':a.get_ylabel()} for a in fig.axes]
    record['font_profile']={'ordinary_pt':9.1,'axis_title_pt':9.6,'panel_pt':9.3,
                            'note':'Export sizes; final PDF insertion scale is verified separately.'}
    LEDGER[name]=record
    (OUT/'PLOT_STATISTICS_AND_SOURCES.json').write_text(json.dumps(LEDGER,indent=2,ensure_ascii=False),encoding='utf-8')
    plt.close(fig)


def stats(df,methods,col):
    result=[]
    for m in methods:
        q=df.loc[df.method==m,col].astype(float).dropna()
        assert len(q)==20,(m,col,len(q))
        result.append({'method':m,'n':len(q),'mean':float(q.mean()),'sample_sd':float(q.std(ddof=1)),
                       'seeds':sorted(df.loc[df.method==m,'seed'].astype(int).tolist())})
    return result


def main_frame(ax):
    """Main-data-figure style; does not alter appendix figures or axis limits."""
    frame(ax)
    ax.grid(False)
    for side in ['top','right']:
        ax.spines[side].set_visible(False)


def fig2_e2():
    source=DATA/'FIG_E1_E2_RISK_NONINTERCHANGEABILITY.csv';d=pd.read_csv(source)
    s=stats(d,E2,'D_aligned');x=np.arange(5)
    fig,axes=plt.subplots(1,2,figsize=(3.5,1.85))
    fig.subplots_adjust(left=.27,right=.98,bottom=.29,top=.86,wspace=.50)
    labels=['FedAvg','FedAsync','TimeAlign','2S-Hájek','RAVEN-Design']
    for i,row in enumerate(s):
        ci=METHODS.index(row['method'])
        axes[0].errorbar(row['mean'],i,xerr=row['sample_sd'],fmt=MARKERS[ci],
          color=COLORS[ci],markersize=4.6 if ci==5 else 4.1,
          elinewidth=1.0 if ci==5 else .8,capsize=2.5,capthick=.8,zorder=3)
    axes[0].axvline(0,color='#263747',ls='--',lw=.8)
    lo=min(v['mean']-v['sample_sd'] for v in s);hi=max(v['mean']+v['sample_sd'] for v in s);span=hi-lo
    axes[0].set_xlim(min(0,lo)-span*.10,max(0,hi)+span*.14)
    fmt=ScalarFormatter(useMathText=True);fmt.set_powerlimits((0,0));axes[0].xaxis.set_major_formatter(fmt)
    axes[0].set_xlabel(r'$D_{\mathrm{aligned}}$',labelpad=2)
    axes[0].xaxis.set_major_locator(MaxNLocator(3))
    counts=[]
    for i,m in enumerate(E2):
        q=d.loc[d.method==m,'D_aligned'];n=int((q<0).sum());counts.append(n);ci=METHODS.index(m)
        axes[1].barh(i,n,height=.56,color=COLORS[ci],edgecolor='#263747',linewidth=.5,hatch='/' if ci==5 else None)
        axes[1].text(n+.6,i,f'{n}/{len(q)}',ha='left',va='center',fontsize=9.1)
    axes[1].axvline(10,color='#69737B',ls=':',lw=.8);axes[1].set_xlim(0,27)
    axes[1].set_xticks([0,10,20]);axes[1].set_xlabel(r'Seeds with $D<0$',labelpad=2)
    for i,ax in enumerate(axes):ax.set_yticks(x,labels if i==0 else ['']*5);ax.set_ylim(4.6,-.6);main_frame(ax)
    # Keep the same scientific tick scale, but give its multiplier a separate
    # position above the axis instead of colliding with D_aligned below it.
    fig.canvas.draw()
    axes[0].text(1,1.03,fmt.get_offset(),transform=axes[0].transAxes,
                 ha='right',va='bottom',fontsize=9.1)
    axes[0].xaxis.get_offset_text().set_visible(False)
    panel(axes[0],'(a) Risk difference',-.35);panel(axes[1],'(b) Direction count',-.35)
    save(fig,'fig2_e2_risk_noninterchangeability',{'source':str(source.relative_to(R)),'stats':s,'negative_counts':counts,'negative_denominator':20})


def fig_g3_tdrive():
    mass=pd.read_csv(DATA/'FIG_G3_TDRIVE_H_MASS.csv');tv=pd.read_csv(DATA/'FIG_G3_TDRIVE_TV.csv')
    fig,axes=plt.subplots(1,2,figsize=(3.5,2.02));fig.subplots_adjust(left=.14,right=.98,bottom=.27,top=.80,wspace=.60)
    ax=axes[0];x=np.arange(4);w=.25
    for j,(col,label,color,hatch) in enumerate([('mu_test_seal',r'Target $\mu$','#77818B',None),('pi_opp_real_R',r'Real $R$','#365E83','/'),('pi_opp_balanced_unit','Unit-balanced','#82947B','\\')]):
        ax.bar(x+(j-1)*w,mass[col],w,label=label,color=color,hatch=hatch,edgecolor='#263747',linewidth=.45)
    ax.set_xticks(x,mass.h_id,fontsize=9.1);ax.set_ylim(0,.78);ax.set_yticks([0,.3,.6]);ax.set_ylabel('Group mass')
    handles,labels=ax.get_legend_handles_labels()
    fig.legend(handles,labels,loc='upper center',bbox_to_anchor=(.52,1.015),ncol=3,frameon=False,fontsize=9.1,columnspacing=.8,handlelength=1.3)
    ax=axes[1];vals=tv.tv_opp_vs_mu.to_numpy();bars=ax.bar(np.arange(3),vals,.56,color=['#365E83','#77818B','#82947B'],edgecolor='#263747',linewidth=.5)
    for b,v,h in zip(bars,vals,['/','', '\\']):b.set_hatch(h);ax.text(b.get_x()+b.get_width()/2,v+.012,f'{v:.3f}',ha='center',fontsize=9.1)
    ax.axhline(.05,color='#69737B',ls=':',lw=.9)
    ax.set_xticks([0,1,2],['T-Drive','SS\nprot.','UA\nprot.'],fontsize=9.1);ax.set_ylim(0,.38);ax.set_ylabel(r'TV$(\pi^{\mathrm{opp}},\mu)$')
    for ax in axes:main_frame(ax)
    panel(axes[0],'(a) Four-block masses',-.36);panel(axes[1],'(b) Four-block TV',-.36)
    save(fig,'fig_g3_tdrive_h_mass',{'sources':['FIG_G3_TDRIVE_H_MASS.csv','FIG_G3_TDRIVE_TV.csv'],'masses':mass.to_dict('records'),'tv':tv.to_dict('records'),'threshold':.05,'threshold_source':'post_review/G3_mobility_replay/PROTOCOL.md RQ1'})


def fig_w1_design_gate():
    d=pd.read_csv(DATA/'FIG_W1_DESIGN_GATE.csv');fig,axes=plt.subplots(1,2,figsize=(3.5,2.30))
    fig.subplots_adjust(left=.14,right=.98,bottom=.26,top=.84,wspace=.55)
    annotation_records=[]
    for ax,col,cap in zip(axes,['Delta_group_pct','RMSE_mu_pct'],['(a) Group mismatch','(b) Target RMSE']):
        values=[]
        for j,var in enumerate(['Estimated','Oracle']):
            vals=[float(d.loc[(d.dataset==ds)&(d.variant==var),col].iloc[0]) for ds in ['SensorScope','U-Air']]
            bars=ax.bar(np.arange(2)+(j-.5)*.38,vals,.28,label=var,color=['#82947B','#365E83'][j],hatch=['/',''][j],edgecolor='#263747',linewidth=.5)
            for b,v in zip(bars,vals):
                # Two reserved annotation rows per sign, independent of tiny bar heights.
                label_y=(.84+j*.105) if v>=0 else (.06+j*.10)
                label_x=b.get_x()+b.get_width()/2 if v>=0 else (j-.5)*.68
                ann=ax.annotate(f'{v:+.3f}',xy=(b.get_x()+b.get_width()/2,v),xytext=(label_x,label_y),textcoords=ax.get_xaxis_transform(),
                   ha='center',va='center',fontsize=9.1,
                   arrowprops={'arrowstyle':'-','lw':.55,'color':'#69737B'},annotation_clip=False)
                annotation_records.append({'metric':col,'value':v,'text':ann.get_text()})
            values+=vals
        lo=min(0,min(values));hi=max(0,max(values));span=hi-lo
        ax.set_ylim(lo-.38*span,hi+.38*span);ax.set_xlim(-.75,1.75);ax.axhline(0,color='#263747',ls='--',lw=.8)
        ax.set_xticks([0,1],['SensorScope','U-Air'],fontsize=9.1);ax.set_ylabel('Change (%)');main_frame(ax);panel(ax,cap,-.29)
        # Outward alignment keeps complete dataset names separate at final
        # column width without changing category positions or the x range.
        ax.get_xticklabels()[0].set_ha('right')
        ax.get_xticklabels()[1].set_ha('left')
    handles,labels=axes[0].get_legend_handles_labels();fig.legend(handles,labels,loc='upper center',ncol=2,frameon=False,fontsize=9.1,bbox_to_anchor=(.52,1.01))
    fig.canvas.draw();ren=fig.canvas.get_renderer();boxes=[]
    for ax in axes:
        anns=[t for t in ax.texts if isinstance(t,matplotlib.text.Annotation)]
        bb=[a.get_window_extent(ren) for a in anns]
        # Text-only bounding boxes exclude leader lines.
        bb=[matplotlib.text.Text.get_window_extent(a,ren) for a in anns]
        for i,b in enumerate(bb):
            assert ax.bbox.contains(b.x0,b.y0) and ax.bbox.contains(b.x1,b.y1),('annotation outside axes', b.bounds, ax.bbox.bounds, [a.get_text() for a in anns])
            for other in bb[i+1:]:assert not b.overlaps(other),'numeric labels overlap'
    save(fig,'fig_w1_design_gate',{'source':'figure_data/FIG_W1_DESIGN_GATE.csv','rows':d.to_dict('records'),'labels':annotation_records,'denominator':'No-Design','label_bbox_check':'within axes; no numeric-label overlap'})


def intervals(source,cols,name,metric_labels):
    d=pd.read_csv(DATA/source);d=d[d.method.isin(METHODS)&d.dataset.isin(['SensorScope','U-Air'])]
    fig,axes=plt.subplots(2,2,figsize=(3.5,3.12));fig.subplots_adjust(left=.27,right=.97,top=.96,bottom=.19,wspace=.28,hspace=.72)
    allstats=[]
    for row,ds in enumerate(['SensorScope','U-Air']):
        for col,metric in enumerate(cols):
            ax=axes[row,col];s=stats(d[d.dataset==ds],METHODS,metric);allstats.append({'dataset':ds,'metric':metric,'stats':s})
            for i,q in enumerate(s):ax.errorbar(q['mean'],i,xerr=q['sample_sd'],fmt=MARKERS[i],color=COLORS[i],markersize=3.7,capsize=2,elinewidth=.8,capthick=.7,zorder=3)
            low=min(q['mean']-q['sample_sd'] for q in s);high=max(q['mean']+q['sample_sd'] for q in s);pad=(high-low)*.12 or .01
            ax.set_xlim(low-pad,high+pad);ax.set_ylim(5.55,-.55);ax.set_yticks(range(6),LABELS if col==0 else ['']*6)
            ax.tick_params(axis='y',labelsize=9.1,length=0);ax.xaxis.set_major_locator(MaxNLocator(3));frame(ax)
            panel(ax,f'({"abcd"[row*2+col]}) {ds}\n{metric_labels[col]}',-.25)
    save(fig,name,{'source':str((DATA/source).relative_to(R)),'filter_methods':METHODS,'filter_datasets':['SensorScope','U-Air'],'stats':allstats,'uncertainty':'sample standard deviation ddof=1','interval_extents_complete':True})


def fig3_structural():
    intervals('FIG_E2_E3_STRUCTURAL_ALIGNMENT.csv',['Delta_group','Delta_c_s'],'fig3_e3_structural_mismatch',[r'$\Delta_{\mathrm{group}}$',r'$\Delta_{c-s}$'])


def fig4_prediction():
    intervals('FIG_E3_E3_PREDICTION_RISK.csv',['RMSE_mu','Tail_RMSE'],'fig4_e3_prediction_risk',[r'$\mathrm{RMSE}_{\mu}$','Tail RMSE'])


def bands(ax,x,mask,color):
    start=None
    for i,on in enumerate(np.r_[mask,False]):
        if on and start is None:start=i
        if not on and start is not None:
            ax.axvspan(x[start]-.5,x[i-1]+.5,color=color,lw=0,zorder=0);start=None


def fig_certificate():
    d=pd.read_csv(DATA/'FIG_CERTIFICATE_WINDOWS.csv');cert=d[d.state_before_decision=='CERTIFIED']
    fig,axes=plt.subplots(2,1,figsize=(3.5,3.00));fig.subplots_adjust(left=.18,right=.97,top=.91,bottom=.20,hspace=1.8)
    ax=axes[0]
    for ds,color,mark,label in [('sensorscope','#365E83','o','SensorScope'),('uair','#82947B','s','U-Air')]:
        q=cert[cert.dataset==ds];ax.scatter(q.C_t,q.C_LCB,s=11,facecolors='none',edgecolors=color,marker=mark,lw=.65,label=label,zorder=3,alpha=.55)
    bad=cert[cert.C_LCB>cert.C_t+1e-12]
    ax.scatter(bad.C_t,bad.C_LCB,marker='x',s=24,color='#A65B4E',lw=.9,label='Miscoverage',zorder=5)
    hi=max(float(cert.C_t.max()),float(cert.C_LCB.max()),.2)*1.06
    ax.plot([0,hi],[0,hi],ls='--',color='#69737B',lw=.7)
    ax.axhline(.05,color='#69737B',ls=':',lw=.7);ax.axvline(.05,color='#69737B',ls=':',lw=.7)
    ax.set_xlim(0,hi);ax.set_ylim(0,hi);ax.set_yticks([0,.1,.2]);ax.set_xlabel(r'$C_t$',labelpad=1);ax.set_ylabel(r'$C_t^{\mathrm{LCB}}$')
    ax.legend(loc='lower center',bbox_to_anchor=(.5,1.03),ncol=3,frameon=False,
              fontsize=9.1,columnspacing=.6,handlelength=1.1,labelspacing=.15,handletextpad=.3)
    panel(ax,'(a) CERTIFIED windows',-.65);frame(ax)
    tr=d[(d.dataset=='sensorscope')&(d.availability_level==.4)].sort_values('window_id');x=tr.window_id.to_numpy();ax=axes[1]
    bands(ax,x,tr.state_before_decision.eq('WARMUP').to_numpy(),'#E4E7EA');bands(ax,x,tr.state_before_decision.eq('RESET').to_numpy(),'#F1DFDB')
    for col,label,color,ls in [('C_t',r'$C_t$','#365E83','-'),('C_hat',r'$\widehat C_t$','#82947B','--'),('C_LCB',r'$C_t^{\mathrm{LCB}}$','#9B88A0','-.')]:ax.plot(x,tr[col],label=label,color=color,ls=ls,lw=.9)
    trig=tr[tr.reset_trigger_after_window.astype(int)==1];ax.scatter(trig.window_id,trig.C_LCB,marker='x',s=26,color='#A65B4E',lw=1,zorder=5,label='RESET trigger')
    ax.axhline(.05,color='#69737B',ls=':',lw=.8);ax.set_xlim(-1,float(x.max())+1);ax.set_ylim(0,.10)
    ax.set_xlabel('Window',labelpad=1);ax.set_ylabel('Coverage');ax.legend(loc='lower center',bbox_to_anchor=(.5,1.04),fontsize=9.1,frameon=False,ncol=2,labelspacing=.15,columnspacing=.6,handlelength=1.4)
    panel(ax,r'(b) SensorScope, $a=0.40$',-.65);frame(ax)
    fig.canvas.draw();renderer=fig.canvas.get_renderer()
    top_panel=axes[0].texts[-1].get_window_extent(renderer)
    assert not top_panel.overlaps(axes[1].get_legend().get_window_extent(renderer))
    assert not top_panel.overlaps(axes[0].xaxis.label.get_window_extent(renderer))
    save(fig,'fig_certificate_audit',{'source':'figure_data/FIG_CERTIFICATE_WINDOWS.csv','n_certified':len(cert),'n_miscoverage':len(bad),'timeline_rows':len(tr),'reset_trigger_windows':trig.window_id.astype(int).tolist(),'axis_label_check':[a.get_xlabel() for a in axes],'identity':'legacy coverage-controlled candidate; coverage diagnostic only'})


def fig_learning_capacity():
    root=R/'results_main_rebuild_r1';d=pd.read_csv(root/'P1_SELECTED_TRAIN_VALIDATION_CURVES_R2.csv');sel=pd.read_csv(root/'P1_CENTRAL_SELECTED_R2.csv');base=pd.read_csv(root/'P0_VALIDATION_BASELINES_R2.csv')
    b=base[base.applicable.astype(str).str.lower()=='true'];refs=b.loc[b.groupby(['dataset','seed']).RMSE_mu.idxmin()]
    fig,axes=plt.subplots(2,3,figsize=(7.16,2.65));fig.subplots_adjust(left=.09,right=.965,top=.87,bottom=.17,wspace=.48,hspace=.45)
    configs=[];records=[]
    for j,(ds,title,unit) in enumerate([('traffic','Traffic','vehicles/h'),('sensorscope','SensorScope','°C'),('uair','U-Air','μg/m³')]):
        for model,color,ls in [('ndmf','#365E83','-'),('history','#AF9276','--')]:
            q=d[(d.dataset==ds)&(d.model==model)];choice=sel[(sel.dataset==ds)&(sel.model==model)].iloc[0]
            configs.append({'dataset':ds,'model':model,'optimizer':choice.optimizer,'lr':float(choice.lr)})
            for row,col in enumerate(['train_RMSE_physical','validation_RMSE_mu']):
                piv=q.pivot(index='pass_id',columns='seed',values=col).sort_index();assert piv.shape==(200,3) and list(piv.columns)==[41001,41002,41003]
                xx=piv.index.to_numpy();mean=piv.mean(axis=1).to_numpy();low=piv.min(axis=1).to_numpy();high=piv.max(axis=1).to_numpy();ax=axes[row,j]
                ax.plot(xx,mean,color=color,ls=ls,lw=1);ax.fill_between(xx,low,high,color=color,alpha=.13,lw=0)
                records.append({'dataset':ds,'model':model,'metric':col,'mean':mean.tolist(),'min':low.tolist(),'max':high.tolist()})
        value=float(refs.loc[refs.dataset==ds,'RMSE_mu'].mean());axes[1,j].axhline(value,color='#59616A',ls=':',lw=1)
        for row,ax in enumerate(axes[:,j]):
            ax.set_xscale('log');ax.set_xlim(1,200);ax.set_xticks([1,10,100,200],['1','10','100','200']);ax.xaxis.set_minor_formatter(NullFormatter());ax.set_ylabel(f'RMSE ({unit})',fontsize=9.6)
            ax.get_xticklabels()[-2].set_ha('right')
            ax.get_xticklabels()[-1].set_ha('left')
            ax.yaxis.set_major_locator(MaxNLocator(3));frame(ax)
            ax.text(.03,.92,f'({"abcdef"[row*3+j]})',transform=ax.transAxes,fontsize=9.1,va='top',bbox={'facecolor':'white','edgecolor':'none','pad':.5,'alpha':.85})
        axes[0,j].set_title(title,fontsize=9.6,pad=3)
    fig.text(.018,.66,'Training',rotation=90,ha='center',va='center',fontsize=9.3)
    fig.text(.018,.30,'Validation',rotation=90,ha='center',va='center',fontsize=9.3)
    fig.text(.54,.04,'Effective training passes (log scale)',ha='center',fontsize=9.6)
    handles=[Line2D([0],[0],color='#365E83',lw=1,label='Common-NDMF'),Line2D([0],[0],color='#AF9276',ls='--',lw=1,label='HistoryResidual'),Line2D([0],[0],color='#59616A',ls=':',lw=1,label='Strongest simple baseline (validation)')]
    fig.legend(handles=handles,loc='upper center',bbox_to_anchor=(.53,1.015),ncol=3,fontsize=9.1,frameon=False,handlelength=2)
    save(fig,'fig_learning_capacity_r2',{'source':'results_main_rebuild_r1/P1_SELECTED_TRAIN_VALIDATION_CURVES_R2.csv','configuration_source':'P1_CENTRAL_SELECTED_R2.csv','baseline_source':'P0_VALIDATION_BASELINES_R2.csv','configurations':configs,'seed_range':[41001,41003],'uncertainty':'three-seed min/max, not confidence interval','baselines':refs[['dataset','seed','baseline','RMSE_mu']].to_dict('records'),'curves':records})


def fig_cityscanner_candidate():
    files=[R/'results_c1_cityscanner/round_v1/tables/CS_E3.csv',R/'results_joint_ou/round_v1/tables/JO_E3.csv']
    methods=['fedavg_window','twostage_hajek','fedau_window','obsuse_window','raven'];labels=['FedAvg','TwoStage-Hájek','FedAU','ObsUse','RAVEN-Design']
    colors=['#77818B','#5C8F98','#B18A75','#9B88A0','#365E83'];marks=['o','v','s','D','P'];rows=[]
    fig,axes=plt.subplots(2,2,figsize=(7.16,2.05));fig.subplots_adjust(left=.15,right=.98,top=.91,bottom=.17,wspace=.34,hspace=1.05)
    for row,(file,protocol) in enumerate(zip(files,['Visit occupancy: real R, controlled O/U','Pilot 2: union-GPS R, measured O, controlled U'])):
        d=pd.read_csv(file)
        for j,(metric,title) in enumerate([('Delta_group',r'Group mismatch $\downarrow$'),('RMSE_mu',r'Target RMSE $\downarrow$')]):
            ax=axes[row,j];ss=[]
            for i,m in enumerate(methods):
                q=d.loc[d.method==m,metric];assert len(q)==10
                mean=float(q.mean());sd=float(q.std(ddof=1));ss.append({'method':m,'mean':mean,'sample_sd':sd})
                ax.errorbar(mean,i,xerr=sd,fmt=marks[i],color=colors[i],markersize=4,capsize=2,lw=.8)
            ax.set_yticks(range(5),labels if j==0 else ['']*5);ax.set_ylim(4.5,-.5);ax.xaxis.set_major_locator(MaxNLocator(3));frame(ax)
            panel(ax,f'({"abcd"[row*2+j]}) '+(['Group mismatch ↓','Target RMSE ↓','Worst-group RMSE ↓\n(block-specific z-score)'][j]),-.25)
            rows.append({'protocol':protocol,'source':str(file.relative_to(R)),'metric':metric,'stats':ss})
        axes[row,0].text(0,1.15,protocol,transform=axes[row,0].transAxes,ha='left',fontsize=8.3,bbox={'fc':'white','ec':'none','pad':0})
    save(fig,'fig_cityscanner_core_candidate',{'rows':rows,'uncertainty':'mean ± sample SD, 10 seeds per protocol','integration':'candidate; main integration compiled to 15 pages; full endpoints remain in table'})


FUNCTIONS={f.__name__:f for f in [fig2_e2,fig_g3_tdrive,fig_w1_design_gate,fig3_structural,fig4_prediction,fig_certificate,fig_learning_capacity,fig_cityscanner_candidate]}
if __name__=='__main__':
    a=argparse.ArgumentParser();a.add_argument('--out',type=Path,default=OUT);a.add_argument('--only',nargs='+',choices=list(FUNCTIONS),default=list(FUNCTIONS));args=a.parse_args()
    OUT=args.out;style()
    for name in args.only:FUNCTIONS[name]();print('wrote',name,flush=True)

