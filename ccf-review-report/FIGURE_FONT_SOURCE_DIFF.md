# 图内字体局部修订源码差异

相对于本轮备份，而非Git HEAD；未包含用户之前已有改动。

## fig1_framework_vector.py

```diff
--- before/fig1_framework_vector.py
+++ after/fig1_framework_vector.py
@@ -11,6 +11,7 @@
 import re
 import shutil
 import subprocess
+import json
 from html import escape
 from contextlib import contextmanager
 from reportlab.pdfgen import canvas
@@ -22,7 +23,7 @@
     out = Path(output_dir)
     out.mkdir(parents=True, exist_ok=True)
     stem = out / 'fig1_raven_problem_framework'
-    W, H, scale = 1500, 700, 7.16 * 72 / 1500
+    W, H, scale = 1500, 710, 7.16 * 72 / 1500
     fonts = Path(__file__).parent / 'assets/fonts'
     if not fonts.exists():
         fonts = Path(__file__).parent / 'figures/fig1_redesign_candidate/assets/fonts'
@@ -45,12 +46,18 @@
     blue, teal, ochre = '#365E83', '#287B78', '#966D36'
     pale_b, pale_t, pale_o = '#EBF2F8', '#E9F3F1', '#FAF2E7'
     texts = []
+    text_bounds = []
+    current_group = ''
 
     @contextmanager
     def group(name):
+        nonlocal current_group
+        previous_group = current_group
+        current_group = name
         svg.append(f'<g id="{name}">')
         yield
         svg.append('</g>')
+        current_group = previous_group
 
     def line(points, color=ink, width=1.8, dashed=False, arrow=False, halo=False):
         if halo:
@@ -86,7 +93,10 @@
         svg.append(f'<circle cx="{x}" cy="{y}" r="{r}" fill="{fill}" stroke="{edge}" stroke-width="{width}"/>')
 
     def text(x,y,s,size=21,bold=False,color=ink,anchor='middle'):
-        size = max(size, 26 if bold and not s.startswith('(') else 24)
+        # At the manuscript's actual 0.99721 insertion scale these are
+        # 9.08 pt ordinary text and 9.60 pt module labels. Sub/superscripts
+        # retain their separate mathematical hierarchy.
+        size = max(size, 28 if bold and not s.startswith('(') else 26.5)
         # Explicit sub/sup runs: selectable Unicode text with exact positions.
         runs=[]; mode=None; b=bold; it=False
         for part in re.split(r'(<[^>]+>)',s):
@@ -109,6 +119,8 @@
             offsets.append(pos);total=max(total,pos+ww);last_offset=pos;last_dy=dy
         xstart=x-total/2 if anchor=='middle' else x-total if anchor=='end' else x
         texts.append((x,y,s,size))
+        text_bounds.append({'group':current_group,'text':s,'ordinary_export_pt':size*scale,
+            'x0':xstart,'x1':xstart+total,'baseline':y})
         for (val,fs,dy,font,b,it,hat,ww),offset in zip(runs,offsets):
             xx=xstart+offset
             pdf.setFillColor(color);pdf.setFont(font,fs);pdf.drawString(xx,H-y-dy,val)
@@ -132,12 +144,12 @@
     # Native primitives only. Draw independent feedback underneath current flows;
     # white casings make crossings unambiguous (no junctions at crossings).
     with group('next-window-debt-feedback'):
-        arrow([(1310,550),(1310,565),(755,565),(755,235)],color=ochre, dashed=True,halo=True)
-        text(1010,558,'<b>Q</b><sub>r+1</sub>: next-window debt',19,color=ochre)
+        arrow([(1310,575),(755,575),(755,235)],color=ochre, dashed=True,halo=True)
+        text(1010,568,'<b>Q</b><sub>r+1</sub>: next-window debt',19,color=ochre)
     with group('next-window-history-feedback'):
-        line([(1380,630),(1380,650),(370,650),(370,96)],blue,dashed=True,halo=True)
+        line([(1380,640),(1380,650),(370,650),(370,96)],blue,dashed=True,halo=True)
         arrow([(370,96),(395,96)],color=blue,dashed=True,halo=True)
-        arrow([(1165,650),(1165,210),(1145,210)],color=blue,dashed=True,halo=True)
+        arrow([(1195,650),(1195,210),(1145,210)],color=blue,dashed=True,halo=True)
         text(630,642,'Updated histories → next window',19,color=blue)
 
     with group('sensing-scene'):
@@ -151,38 +163,38 @@
         circle(49,135,5,ink);circle(78,135,5,ink)
         rect(59,101,9,7,teal,teal)
         line([(63,100),(63,94)],teal,1.5)
-        text(80,179,'Mobile sensing',19)
+        text(94,179,'Mobile sensing',19)
         arrow([(145,110),(187,110)])
     with group('local-records'):
-        text(274,30,'Observation <i>O</i>',22,bold=True)
-        rect(193,52,142,105,'white','#758B9C',1.3)
-        rect(193,52,142,29,pale_b,'#758B9C',1.3)
-        text(264,73,'Local records',20)
-        for y in [106,131]:line([(193,y),(335,y)],'#B4C0C8',1)
+        text(285,30,'Observation <i>O</i>',22,bold=True)
+        rect(193,52,156,105,'white','#758B9C',1.3)
+        rect(193,52,156,29,pale_b,'#758B9C',1.3)
+        text(271,73,'Local records',20)
+        for y in [106,131]:line([(193,y),(349,y)],'#B4C0C8',1)
         line([(238,81),(238,157)],'#B4C0C8',1);line([(285,81),(285,157)],'#B4C0C8',1)
         text(216,101,'i',19);text(262,101,'Z',19);text(309,101,'…',19)
         text(216,127,'…',19);text(262,127,'…',19);text(309,127,'…',19)
         arrow([(264,157),(264,290)])
     with group('shared-correction'):
-        rect(385,35,215,115,pale_b,blue,1.4,5)
+        rect(377,35,230,115,pale_b,blue,1.4,5)
         text(492,61,'Pre-outcome state',21,bold=True)
         text(492,86,'Selection / lagged',19)
         text(492,108,'state',19)
         text(492,134,'π<sup>tar</sup>; fixed Design',20)
         arrow([(492,150),(492,195)],color=blue)
-        rect(395,195,195,60,pale_b,blue,1.5,5)
-        text(492,219,'R/O correction',22,bold=True)
-        text(492,244,'Record weights a<sub>k,r,i</sub>',20)
+        rect(395,195,230,60,pale_b,blue,1.5,5)
+        text(510,219,'R/O correction',22,bold=True)
+        text(510,244,'Record weights a<sub>k,r,i</sub>',20)
         # Same correction produces normalized training weights and total mass.
-        arrow([(395,225),(350,225),(350,321),(335,321)],color=blue)
+        arrow([(395,225),(363,225),(363,321),(344,321)],color=blue)
         text(341,278,'ā',23,color=blue,anchor='end')
         arrow([(492,255),(492,350)],color=blue)
         text(510,294,'Mass m<sub>k,r</sub>',20,color=blue,anchor='start')
         # The pre-U history is an input to d, not a current update-vector input.
-        arrow([(590,88),(615,88),(615,334),(555,334),(555,350)],color=blue)
-        text(610,323,'pre-U',18,color=blue,anchor='end')
+        arrow([(607,88),(643,88),(643,334),(555,334),(555,350)],color=blue)
+        text(620,323,'pre-U',18,color=blue,anchor='end')
     with group('local-training-and-window'):
-        rect(120,290,215,65,'#F5F7F8',muted,1.3,5)
+        rect(114,290,230,65,'#F5F7F8',muted,1.3,5)
         text(232,316,'Local normalized',21,bold=True)
         text(232,340,'training',21,bold=True)
         arrow([(232,355),(232,389)])
@@ -197,27 +209,27 @@
         text(165,583,'Usable clients',18,color=muted)
         text(165,608,'Positive mass',18,color=muted)
     with group('reference-reconstruction'):
-        rect(395,350,195,65,pale_b,blue,1.8,5)
-        text(492,375,'Reference mass',22,bold=True)
-        text(492,401,'d<sub>k,r</sub>; β̂<sub>k,r</sub> ∝ m<sub>k,r</sub>d<sub>k,r</sub>',21)
-        arrow([(590,383),(651,383)],color=blue,width=2.2)
+        rect(395,350,230,65,pale_b,blue,1.8,5)
+        text(510,375,'Reference mass',22,bold=True)
+        text(510,401,'d<sub>k,r</sub>; β̂<sub>k,r</sub> ∝ m<sub>k,r</sub>d<sub>k,r</sub>',21)
+        arrow([(625,383),(651,383)],color=blue,width=2.2)
         text(697,317,'Reference',21,bold=True,color=blue)
         text(697,350,'<b>β̂</b><sub>r</sub>',24,color=blue)
         bars(658,415,[58,31,47,24],blue,w=15,gap=8)
         arrow([(751,383),(800,383)],color=blue,width=2.3)
     with group('p2-inputs'):
-        rect(655,35,155,120,'white','#A3B7C4',1.1,4)
-        text(732,59,'Active support',20,bold=True)
-        text(732,83,'A<sub>r</sub> ; M<sub>r</sub>',23)
+        rect(650,35,175,120,'white','#A3B7C4',1.1,4)
+        text(737,59,'Active support',20,bold=True)
+        text(737,83,'A<sub>r</sub> ; M<sub>r</sub>',23)
         for r in range(2):
             for c in range(4):rect(694+c*19,98+r*19,16,16,[pale_b,'#BCD0DF','#83A7C2','white'][(r+c)%4],muted,.6)
-        arrow([(810,115),(820,115),(820,280),(840,280),(840,300)],color=blue)
-        rect(825,35,110,120,'white','#A3B7C4',1.1,4)
-        text(880,59,'Target',20,bold=True)
-        text(880,83,'<b>μ</b>',24)
-        bars(850,138,[30,44,22],ochre,w=14,gap=7)
-        arrow([(880,155),(880,300)],color=blue)
-        rect(960,35,185,120,'white','#A3B7C4',1.1,4)
+        arrow([(825,115),(830,115),(830,280),(840,280),(840,300)],color=blue)
+        rect(835,35,110,120,'white','#A3B7C4',1.1,4)
+        text(890,59,'Target',20,bold=True)
+        text(890,83,'<b>μ</b>',24)
+        bars(860,138,[30,44,22],ochre,w=14,gap=7)
+        arrow([(890,155),(890,300)],color=blue)
+        rect(950,35,205,120,'white','#A3B7C4',1.1,4)
         text(1052,57,'Weight caps',20,bold=True)
         text(1052,81,'Effective support',24)
         poly([(1023,112),(1040,94),(1070,97),(1084,121),(1061,147),(1025,136)],pale_t,teal)
@@ -264,33 +276,35 @@
     with group('composition-and-post-aggregation-state'):
         # Composition is computed from weights + M, never from theta.
         arrow([(1105,419),(1105,490)],color=teal,halo=True)
-        rect(1048,490,125,43,'white',teal,1.2,3)
-        text(1110,518,'<b>ω</b><sub>r</sub> = M<sub>r</sub><b>α</b><sup>⋆</sup><sub>r</sub>',20)
-        arrow([(1173,511),(1215,511)],color=teal,halo=True)
+        rect(1040,490,145,43,'white',teal,1.2,3)
+        text(1112,518,'<b>ω</b><sub>r</sub> = M<sub>r</sub><b>α</b><sup>⋆</sup><sub>r</sub>',20)
+        arrow([(1185,511),(1215,511)],color=teal,halo=True)
         text(1355,468,'After aggregation',20,bold=True)
-        rect(1215,485,275,65,pale_o,ochre,1.4,4)
+        rect(1215,485,275,90,pale_o,ochre,1.4,4)
         # Minimal two-row group ledger: no experimental values.
         rect(1224,493,52,48,'white',ochre,.8)
         line([(1224,517),(1276,517)],ochre,.7);line([(1249,493),(1249,541)],ochre,.7)
-        text(1236,513,'g',18);text(1263,513,'…',18)
-        text(1236,537,'g',18);text(1263,537,'…',18)
+        text(1236,512,'g',18);text(1263,512,'…',18)
+        text(1236,536,'g',18);text(1263,536,'…',18)
         text(1382,508,'Group debt',21,bold=True)
-        text(1382,535,'<b>Q</b><sub>r+1</sub> ← (<b>Q</b><sub>r</sub>, <b>μ</b> − <b>ω</b><sub>r</sub>)',21)
-        rect(1215,580,275,50,pale_b,blue,1.3,4)
-        text(1352,600,'Updated histories',20,bold=True)
-        text(1352,622,'Selection / variance',19)
+        text(1352,566,'<b>Q</b><sub>r+1</sub> ← (<b>Q</b><sub>r</sub>, <b>μ</b> − <b>ω</b><sub>r</sub>)',21)
+        rect(1215,580,275,60,pale_b,blue,1.3,4)
+        text(1352,603,'Updated histories',20,bold=True)
+        text(1352,632,'Selection / variance',19)
     with group('legend-and-panel-labels'):
         line([(45,628),(85,628)],ink,1.8,arrow=True);text(95,635,'Current window',19,anchor='start')
         line([(45,656),(85,656)],ink,1.8,dashed=True,arrow=True);text(95,662,'Next-window feedback',19,anchor='start')
         line([(15,675),(345,675)],'#D4DCE1',1)
         line([(395,675),(1145,675)],'#D4DCE1',1)
-        line([(1215,675),(1490,675)],'#D4DCE1',1)
+        line([(1195,675),(1495,675)],'#D4DCE1',1)
         text(180,697,'(a) Sensing + usable updates',23,bold=True)
         text(770,697,'(b) Reference reconstruction and feasible calibration',23,bold=True)
-        text(1352,697,'(c) Aggregate + feedback',22,bold=True)
+        text(1345,697,'(c) Aggregate + feedback',22,bold=True)
 
     pdf.showPage();pdf.save()
     svg.append('</svg>');stem.with_suffix('.svg').write_text('\n'.join(svg),encoding='utf-8')
+    stem.with_suffix('.fonts.json').write_text(json.dumps({'width_bp':W*scale,
+        'height_bp':H*scale,'labels':text_bounds},indent=2,ensure_ascii=False),encoding='utf-8')
     exe=poppler or shutil.which('pdftoppm')
     if exe:
         subprocess.run([str(exe),'-singlefile','-r','250','-png',str(stem.with_suffix('.pdf')),str(stem)],check=True,stdout=subprocess.PIPE,stderr=subprocess.PIPE)
```

## data_figures_revision.py

```diff
--- before/data_figures_revision.py
+++ after/data_figures_revision.py
@@ -29,8 +29,8 @@
 
 def style():
     plt.rcParams.update({'font.family':'serif','font.serif':['Times New Roman','DejaVu Serif'],
-      'mathtext.fontset':'stix','font.size':9,'axes.labelsize':9,'xtick.labelsize':8,
-      'ytick.labelsize':8,'legend.fontsize':9,'axes.linewidth':.65,
+      'mathtext.fontset':'stix','font.size':9.1,'axes.labelsize':9.6,'xtick.labelsize':9.1,
+      'ytick.labelsize':9.1,'legend.fontsize':9.1,'axes.linewidth':.65,
       'pdf.fonttype':42,'ps.fonttype':42,'svg.fonttype':'none','savefig.dpi':250,
       'axes.unicode_minus':True,'hatch.linewidth':.35})
 
@@ -44,7 +44,7 @@
 
 def panel(ax,label,y=-.27):
     """A separate artist: never replaces an axis label."""
-    return ax.text(.5,y,label,transform=ax.transAxes,ha='center',va='top',fontsize=9,clip_on=False)
+    return ax.text(.5,y,label,transform=ax.transAxes,ha='center',va='top',fontsize=9.3,clip_on=False)
 
 
 def save(fig,name,record):
@@ -54,6 +54,8 @@
         fig.savefig(OUT/(name+'.'+ext),facecolor='white')
     record['size_inches']=list(fig.get_size_inches())
     record['axis_labels']=[{'x':a.get_xlabel(),'y':a.get_ylabel()} for a in fig.axes]
+    record['font_profile']={'ordinary_pt':9.1,'axis_title_pt':9.6,'panel_pt':9.3,
+                            'note':'Export sizes; final PDF insertion scale is verified separately.'}
     LEDGER[name]=record
     (OUT/'PLOT_STATISTICS_AND_SOURCES.json').write_text(json.dumps(LEDGER,indent=2,ensure_ascii=False),encoding='utf-8')
     plt.close(fig)
@@ -81,7 +83,7 @@
     source=DATA/'FIG_E1_E2_RISK_NONINTERCHANGEABILITY.csv';d=pd.read_csv(source)
     s=stats(d,E2,'D_aligned');x=np.arange(5)
     fig,axes=plt.subplots(1,2,figsize=(3.5,1.85))
-    fig.subplots_adjust(left=.27,right=.98,bottom=.29,top=.96,wspace=.50)
+    fig.subplots_adjust(left=.27,right=.98,bottom=.29,top=.86,wspace=.50)
     labels=['FedAvg','FedAsync','TimeAlign','2S-Hájek','RAVEN-Design']
     for i,row in enumerate(s):
         ci=METHODS.index(row['method'])
@@ -98,10 +100,16 @@
     for i,m in enumerate(E2):
         q=d.loc[d.method==m,'D_aligned'];n=int((q<0).sum());counts.append(n);ci=METHODS.index(m)
         axes[1].barh(i,n,height=.56,color=COLORS[ci],edgecolor='#263747',linewidth=.5,hatch='/' if ci==5 else None)
-        axes[1].text(n+.6,i,f'{n}/{len(q)}',ha='left',va='center',fontsize=8)
+        axes[1].text(n+.6,i,f'{n}/{len(q)}',ha='left',va='center',fontsize=9.1)
     axes[1].axvline(10,color='#69737B',ls=':',lw=.8);axes[1].set_xlim(0,27)
     axes[1].set_xticks([0,10,20]);axes[1].set_xlabel(r'Seeds with $D<0$',labelpad=2)
     for i,ax in enumerate(axes):ax.set_yticks(x,labels if i==0 else ['']*5);ax.set_ylim(4.6,-.6);main_frame(ax)
+    # Keep the same scientific tick scale, but give its multiplier a separate
+    # position above the axis instead of colliding with D_aligned below it.
+    fig.canvas.draw()
+    axes[0].text(1,1.03,fmt.get_offset(),transform=axes[0].transAxes,
+                 ha='right',va='bottom',fontsize=9.1)
+    axes[0].xaxis.get_offset_text().set_visible(False)
     panel(axes[0],'(a) Risk difference',-.35);panel(axes[1],'(b) Direction count',-.35)
     save(fig,'fig2_e2_risk_noninterchangeability',{'source':str(source.relative_to(R)),'stats':s,'negative_counts':counts,'negative_denominator':20})
 
@@ -112,20 +120,20 @@
     ax=axes[0];x=np.arange(4);w=.25
     for j,(col,label,color,hatch) in enumerate([('mu_test_seal',r'Target $\mu$','#77818B',None),('pi_opp_real_R',r'Real $R$','#365E83','/'),('pi_opp_balanced_unit','Unit-balanced','#82947B','\\')]):
         ax.bar(x+(j-1)*w,mass[col],w,label=label,color=color,hatch=hatch,edgecolor='#263747',linewidth=.45)
-    ax.set_xticks(x,mass.h_id,fontsize=8);ax.set_ylim(0,.78);ax.set_yticks([0,.3,.6]);ax.set_ylabel('Group mass')
+    ax.set_xticks(x,mass.h_id,fontsize=9.1);ax.set_ylim(0,.78);ax.set_yticks([0,.3,.6]);ax.set_ylabel('Group mass')
     handles,labels=ax.get_legend_handles_labels()
-    fig.legend(handles,labels,loc='upper center',bbox_to_anchor=(.52,1.015),ncol=3,frameon=False,fontsize=9,columnspacing=.8,handlelength=1.3)
+    fig.legend(handles,labels,loc='upper center',bbox_to_anchor=(.52,1.015),ncol=3,frameon=False,fontsize=9.1,columnspacing=.8,handlelength=1.3)
     ax=axes[1];vals=tv.tv_opp_vs_mu.to_numpy();bars=ax.bar(np.arange(3),vals,.56,color=['#365E83','#77818B','#82947B'],edgecolor='#263747',linewidth=.5)
-    for b,v,h in zip(bars,vals,['/','', '\\']):b.set_hatch(h);ax.text(b.get_x()+b.get_width()/2,v+.012,f'{v:.3f}',ha='center',fontsize=8)
+    for b,v,h in zip(bars,vals,['/','', '\\']):b.set_hatch(h);ax.text(b.get_x()+b.get_width()/2,v+.012,f'{v:.3f}',ha='center',fontsize=9.1)
     ax.axhline(.05,color='#69737B',ls=':',lw=.9)
-    ax.set_xticks([0,1,2],['T-Drive','SS\nprot.','UA\nprot.'],fontsize=8.5);ax.set_ylim(0,.38);ax.set_ylabel(r'TV$(\pi^{\mathrm{opp}},\mu)$')
+    ax.set_xticks([0,1,2],['T-Drive','SS\nprot.','UA\nprot.'],fontsize=9.1);ax.set_ylim(0,.38);ax.set_ylabel(r'TV$(\pi^{\mathrm{opp}},\mu)$')
     for ax in axes:main_frame(ax)
     panel(axes[0],'(a) Four-block masses',-.36);panel(axes[1],'(b) Four-block TV',-.36)
     save(fig,'fig_g3_tdrive_h_mass',{'sources':['FIG_G3_TDRIVE_H_MASS.csv','FIG_G3_TDRIVE_TV.csv'],'masses':mass.to_dict('records'),'tv':tv.to_dict('records'),'threshold':.05,'threshold_source':'post_review/G3_mobility_replay/PROTOCOL.md RQ1'})
 
 
 def fig_w1_design_gate():
-    d=pd.read_csv(DATA/'FIG_W1_DESIGN_GATE.csv');fig,axes=plt.subplots(1,2,figsize=(3.5,2.05))
+    d=pd.read_csv(DATA/'FIG_W1_DESIGN_GATE.csv');fig,axes=plt.subplots(1,2,figsize=(3.5,2.30))
     fig.subplots_adjust(left=.14,right=.98,bottom=.26,top=.84,wspace=.55)
     annotation_records=[]
     for ax,col,cap in zip(axes,['Delta_group_pct','RMSE_mu_pct'],['(a) Group mismatch','(b) Target RMSE']):
@@ -135,17 +143,21 @@
             bars=ax.bar(np.arange(2)+(j-.5)*.38,vals,.28,label=var,color=['#82947B','#365E83'][j],hatch=['/',''][j],edgecolor='#263747',linewidth=.5)
             for b,v in zip(bars,vals):
                 # Two reserved annotation rows per sign, independent of tiny bar heights.
-                label_y=(.81+j*.13) if v>=0 else (.07+j*.08)
+                label_y=(.84+j*.105) if v>=0 else (.06+j*.10)
                 label_x=b.get_x()+b.get_width()/2 if v>=0 else (j-.5)*.68
                 ann=ax.annotate(f'{v:+.3f}',xy=(b.get_x()+b.get_width()/2,v),xytext=(label_x,label_y),textcoords=ax.get_xaxis_transform(),
-                   ha='center',va='center',fontsize=8,
+                   ha='center',va='center',fontsize=9.1,
                    arrowprops={'arrowstyle':'-','lw':.55,'color':'#69737B'},annotation_clip=False)
                 annotation_records.append({'metric':col,'value':v,'text':ann.get_text()})
             values+=vals
         lo=min(0,min(values));hi=max(0,max(values));span=hi-lo
         ax.set_ylim(lo-.38*span,hi+.38*span);ax.set_xlim(-.75,1.75);ax.axhline(0,color='#263747',ls='--',lw=.8)
-        ax.set_xticks([0,1],['SensorScope','U-Air'],fontsize=8);ax.set_ylabel('Change (%)');main_frame(ax);panel(ax,cap,-.29)
-    handles,labels=axes[0].get_legend_handles_labels();fig.legend(handles,labels,loc='upper center',ncol=2,frameon=False,fontsize=9,bbox_to_anchor=(.52,1.01))
+        ax.set_xticks([0,1],['SensorScope','U-Air'],fontsize=9.1);ax.set_ylabel('Change (%)');main_frame(ax);panel(ax,cap,-.29)
+        # Outward alignment keeps complete dataset names separate at final
+        # column width without changing category positions or the x range.
+        ax.get_xticklabels()[0].set_ha('right')
+        ax.get_xticklabels()[1].set_ha('left')
+    handles,labels=axes[0].get_legend_handles_labels();fig.legend(handles,labels,loc='upper center',ncol=2,frameon=False,fontsize=9.1,bbox_to_anchor=(.52,1.01))
     fig.canvas.draw();ren=fig.canvas.get_renderer();boxes=[]
     for ax in axes:
         anns=[t for t in ax.texts if isinstance(t,matplotlib.text.Annotation)]
@@ -168,7 +180,7 @@
             for i,q in enumerate(s):ax.errorbar(q['mean'],i,xerr=q['sample_sd'],fmt=MARKERS[i],color=COLORS[i],markersize=3.7,capsize=2,elinewidth=.8,capthick=.7,zorder=3)
             low=min(q['mean']-q['sample_sd'] for q in s);high=max(q['mean']+q['sample_sd'] for q in s);pad=(high-low)*.12 or .01
             ax.set_xlim(low-pad,high+pad);ax.set_ylim(5.55,-.55);ax.set_yticks(range(6),LABELS if col==0 else ['']*6)
-            ax.tick_params(axis='y',labelsize=8,length=0);ax.xaxis.set_major_locator(MaxNLocator(3));frame(ax)
+            ax.tick_params(axis='y',labelsize=9.1,length=0);ax.xaxis.set_major_locator(MaxNLocator(3));frame(ax)
             panel(ax,f'({"abcd"[row*2+col]}) {ds}\n{metric_labels[col]}',-.25)
     save(fig,name,{'source':str((DATA/source).relative_to(R)),'filter_methods':METHODS,'filter_datasets':['SensorScope','U-Air'],'stats':allstats,'uncertainty':'sample standard deviation ddof=1','interval_extents_complete':True})
 
@@ -191,7 +203,7 @@
 
 def fig_certificate():
     d=pd.read_csv(DATA/'FIG_CERTIFICATE_WINDOWS.csv');cert=d[d.state_before_decision=='CERTIFIED']
-    fig,axes=plt.subplots(2,1,figsize=(3.5,3.00));fig.subplots_adjust(left=.18,right=.97,top=.97,bottom=.20,hspace=1.8)
+    fig,axes=plt.subplots(2,1,figsize=(3.5,3.00));fig.subplots_adjust(left=.18,right=.97,top=.91,bottom=.20,hspace=1.8)
     ax=axes[0]
     for ds,color,mark,label in [('sensorscope','#365E83','o','SensorScope'),('uair','#82947B','s','U-Air')]:
         q=cert[cert.dataset==ds];ax.scatter(q.C_t,q.C_LCB,s=11,facecolors='none',edgecolors=color,marker=mark,lw=.65,label=label,zorder=3,alpha=.55)
@@ -201,14 +213,15 @@
     ax.plot([0,hi],[0,hi],ls='--',color='#69737B',lw=.7)
     ax.axhline(.05,color='#69737B',ls=':',lw=.7);ax.axvline(.05,color='#69737B',ls=':',lw=.7)
     ax.set_xlim(0,hi);ax.set_ylim(0,hi);ax.set_yticks([0,.1,.2]);ax.set_xlabel(r'$C_t$',labelpad=1);ax.set_ylabel(r'$C_t^{\mathrm{LCB}}$')
-    ax.legend(loc='upper left',frameon=False,fontsize=8,labelspacing=.15,handletextpad=.3)
+    ax.legend(loc='lower center',bbox_to_anchor=(.5,1.03),ncol=3,frameon=False,
+              fontsize=9.1,columnspacing=.6,handlelength=1.1,labelspacing=.15,handletextpad=.3)
     panel(ax,'(a) CERTIFIED windows',-.65);frame(ax)
     tr=d[(d.dataset=='sensorscope')&(d.availability_level==.4)].sort_values('window_id');x=tr.window_id.to_numpy();ax=axes[1]
     bands(ax,x,tr.state_before_decision.eq('WARMUP').to_numpy(),'#E4E7EA');bands(ax,x,tr.state_before_decision.eq('RESET').to_numpy(),'#F1DFDB')
     for col,label,color,ls in [('C_t',r'$C_t$','#365E83','-'),('C_hat',r'$\widehat C_t$','#82947B','--'),('C_LCB',r'$C_t^{\mathrm{LCB}}$','#9B88A0','-.')]:ax.plot(x,tr[col],label=label,color=color,ls=ls,lw=.9)
     trig=tr[tr.reset_trigger_after_window.astype(int)==1];ax.scatter(trig.window_id,trig.C_LCB,marker='x',s=26,color='#A65B4E',lw=1,zorder=5,label='RESET trigger')
     ax.axhline(.05,color='#69737B',ls=':',lw=.8);ax.set_xlim(-1,float(x.max())+1);ax.set_ylim(0,.10)
-    ax.set_xlabel('Window',labelpad=1);ax.set_ylabel('Coverage');ax.legend(loc='lower center',bbox_to_anchor=(.5,1.04),fontsize=8,frameon=False,ncol=2,labelspacing=.15,columnspacing=.6,handlelength=1.4)
+    ax.set_xlabel('Window',labelpad=1);ax.set_ylabel('Coverage');ax.legend(loc='lower center',bbox_to_anchor=(.5,1.04),fontsize=9.1,frameon=False,ncol=2,labelspacing=.15,columnspacing=.6,handlelength=1.4)
     panel(ax,r'(b) SensorScope, $a=0.40$',-.65);frame(ax)
     fig.canvas.draw();renderer=fig.canvas.get_renderer()
     top_panel=axes[0].texts[-1].get_window_extent(renderer)
@@ -220,7 +233,7 @@
 def fig_learning_capacity():
     root=R/'results_main_rebuild_r1';d=pd.read_csv(root/'P1_SELECTED_TRAIN_VALIDATION_CURVES_R2.csv');sel=pd.read_csv(root/'P1_CENTRAL_SELECTED_R2.csv');base=pd.read_csv(root/'P0_VALIDATION_BASELINES_R2.csv')
     b=base[base.applicable.astype(str).str.lower()=='true'];refs=b.loc[b.groupby(['dataset','seed']).RMSE_mu.idxmin()]
-    fig,axes=plt.subplots(2,3,figsize=(7.16,2.65));fig.subplots_adjust(left=.09,right=.98,top=.87,bottom=.17,wspace=.48,hspace=.45)
+    fig,axes=plt.subplots(2,3,figsize=(7.16,2.65));fig.subplots_adjust(left=.09,right=.965,top=.87,bottom=.17,wspace=.48,hspace=.45)
     configs=[];records=[]
     for j,(ds,title,unit) in enumerate([('traffic','Traffic','vehicles/h'),('sensorscope','SensorScope','°C'),('uair','U-Air','μg/m³')]):
         for model,color,ls in [('ndmf','#365E83','-'),('history','#AF9276','--')]:
@@ -233,15 +246,17 @@
                 records.append({'dataset':ds,'model':model,'metric':col,'mean':mean.tolist(),'min':low.tolist(),'max':high.tolist()})
         value=float(refs.loc[refs.dataset==ds,'RMSE_mu'].mean());axes[1,j].axhline(value,color='#59616A',ls=':',lw=1)
         for row,ax in enumerate(axes[:,j]):
-            ax.set_xscale('log');ax.set_xlim(1,200);ax.set_xticks([1,10,100,200],['1','10','100','200']);ax.xaxis.set_minor_formatter(NullFormatter());ax.set_ylabel(f'RMSE ({unit})',fontsize=8.5)
+            ax.set_xscale('log');ax.set_xlim(1,200);ax.set_xticks([1,10,100,200],['1','10','100','200']);ax.xaxis.set_minor_formatter(NullFormatter());ax.set_ylabel(f'RMSE ({unit})',fontsize=9.6)
+            ax.get_xticklabels()[-2].set_ha('right')
+            ax.get_xticklabels()[-1].set_ha('left')
             ax.yaxis.set_major_locator(MaxNLocator(3));frame(ax)
-            ax.text(.03,.92,f'({"abcdef"[row*3+j]})',transform=ax.transAxes,fontsize=9,va='top',bbox={'facecolor':'white','edgecolor':'none','pad':.5,'alpha':.85})
-        axes[0,j].set_title(title,fontsize=9,pad=3)
-    fig.text(.018,.66,'Training',rotation=90,ha='center',va='center',fontsize=9)
-    fig.text(.018,.30,'Validation',rotation=90,ha='center',va='center',fontsize=9)
-    fig.text(.54,.04,'Effective training passes (log scale)',ha='center',fontsize=9)
+            ax.text(.03,.92,f'({"abcdef"[row*3+j]})',transform=ax.transAxes,fontsize=9.1,va='top',bbox={'facecolor':'white','edgecolor':'none','pad':.5,'alpha':.85})
+        axes[0,j].set_title(title,fontsize=9.6,pad=3)
+    fig.text(.018,.66,'Training',rotation=90,ha='center',va='center',fontsize=9.3)
+    fig.text(.018,.30,'Validation',rotation=90,ha='center',va='center',fontsize=9.3)
+    fig.text(.54,.04,'Effective training passes (log scale)',ha='center',fontsize=9.6)
     handles=[Line2D([0],[0],color='#365E83',lw=1,label='Common-NDMF'),Line2D([0],[0],color='#AF9276',ls='--',lw=1,label='HistoryResidual'),Line2D([0],[0],color='#59616A',ls=':',lw=1,label='Strongest simple baseline (validation)')]
-    fig.legend(handles=handles,loc='upper center',bbox_to_anchor=(.53,1.015),ncol=3,fontsize=9,frameon=False,handlelength=2)
+    fig.legend(handles=handles,loc='upper center',bbox_to_anchor=(.53,1.015),ncol=3,fontsize=9.1,frameon=False,handlelength=2)
     save(fig,'fig_learning_capacity_r2',{'source':'results_main_rebuild_r1/P1_SELECTED_TRAIN_VALIDATION_CURVES_R2.csv','configuration_source':'P1_CENTRAL_SELECTED_R2.csv','baseline_source':'P0_VALIDATION_BASELINES_R2.csv','configurations':configs,'seed_range':[41001,41003],'uncertainty':'three-seed min/max, not confidence interval','baselines':refs[['dataset','seed','baseline','RMSE_mu']].to_dict('records'),'curves':records})
 
 
```

## arrival_support_figure.py

```diff
--- before/arrival_support_figure.py
+++ after/arrival_support_figure.py
@@ -45,7 +45,7 @@
     out = Path(out); out.mkdir(parents=True, exist_ok=True)
     style()
     fig, ax = plt.subplots(figsize=(3.5, 2.05))
-    fig.subplots_adjust(left=.29, right=.86, bottom=.24, top=.83)
+    fig.subplots_adjust(left=.32, right=.86, bottom=.24, top=.83)
     yy = np.array([0, 1, 2.35, 3.35, 4.7, 5.7])
     colors = ['#D4DADE', '#BD9D74', '#365E83']
     hatches = [None, '//', None]
@@ -61,19 +61,19 @@
                 continue
             if value >= 15:
                 ax.text(start+value/2, y, f'{value:.3f}', ha='center',
-                        va='center', fontsize=8, zorder=4)
+                        va='center', fontsize=9.1, zorder=4)
             else:
                 ax.annotate(f'{value:.3f}', xy=(start+value/2, y),
                     xytext=(103, y), textcoords='data', ha='left',
-                    va='center', fontsize=8,
+                    va='center', fontsize=9.1,
                     color='#365E83' if j == 2 else '#72552E',
                     arrowprops={'arrowstyle':'-', 'lw':.5, 'color':'#69737B'},
                     annotation_clip=False)
     ticks = [f'{row[0]}  '+(r'$K\leq3$' if row[1]=='<=3' else r'$K>3$') for row in rows]
-    ax.set_yticks(yy, ticks, fontsize=8)
+    ax.set_yticks(yy, ticks, fontsize=9.1)
     ax.set_ylim(6.35, -.65); ax.set_xlim(0, 100)
     ax.set_xticks([0, 25, 50, 75, 100])
-    ax.set_xlabel('Target mass (%)', fontsize=9, labelpad=3)
+    ax.set_xlabel('Target mass (%)', fontsize=9.6, labelpad=3)
     ax.tick_params(axis='y', length=0, pad=3)
     ax.tick_params(axis='x', length=2.3, width=.6, pad=2)
     for side in ['top', 'right', 'left']:
@@ -81,7 +81,7 @@
     ax.spines['bottom'].set_color('#69737B'); ax.spines['bottom'].set_linewidth(.65)
     handles, names = ax.get_legend_handles_labels()
     fig.legend(handles, names, loc='upper center', bbox_to_anchor=(.52, 1.005),
-               ncol=3, frameon=False, fontsize=9, handlelength=1.2,
+               ncol=3, frameon=False, fontsize=9.1, handlelength=1.2,
                columnspacing=.8, handletextpad=.4)
     fig.canvas.draw()
     renderer = fig.canvas.get_renderer()
```

