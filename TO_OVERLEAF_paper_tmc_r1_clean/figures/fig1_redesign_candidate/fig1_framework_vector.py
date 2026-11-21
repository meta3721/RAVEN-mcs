"""Editable reconstruction of the approved Fig. 1 concept; no experiment inputs.

All icons are original native primitives. SVG contains live text and semantic
groups; PDF is drawn from the same primitives (never an embedded raster).
Only this figure is generated. Requires reportlab; PNG preview uses pdftoppm.
"""
from pathlib import Path
import math
import base64
import os
import re
import shutil
import subprocess
from html import escape
from contextlib import contextmanager
from reportlab.pdfgen import canvas
from reportlab.pdfbase import pdfmetrics
from reportlab.pdfbase.ttfonts import TTFont


def render_fig1(output_dir, poppler=None):
    out = Path(output_dir)
    out.mkdir(parents=True, exist_ok=True)
    stem = out / 'fig1_raven_problem_framework'
    W, H, scale = 1500, 700, 7.16 * 72 / 1500
    fonts = Path(__file__).parent / 'assets/fonts'
    if not fonts.exists():
        fonts = Path(__file__).parent / 'figures/fig1_redesign_candidate/assets/fonts'
    for name, filename in [('F1', 'STIXGeneral.ttf'), ('F1B', 'STIXGeneralBol.ttf'), ('F1I', 'STIXGeneralItalic.ttf')]:
        if name not in pdfmetrics.getRegisteredFontNames():
            pdfmetrics.registerFont(TTFont(name, str(fonts / filename)))
    pdf = canvas.Canvas(str(stem.with_suffix('.pdf')), pagesize=(W*scale,H*scale))
    pdf.setTitle('RAVEN-MCS: reference reconstruction and feasible aggregation')
    pdf.setAuthor('')
    pdf.scale(scale, scale)
    svg = [f'<svg xmlns="http://www.w3.org/2000/svg" width="7.16in" height="{H*scale/72:.6f}in" viewBox="0 0 {W} {H}">',
           '<title>RAVEN-MCS: reference reconstruction and feasible aggregation</title>',
           '<desc>Active-window mechanism. Original editable vector reconstruction; schematic objects are not experimental data.</desc>']
    svg.append('<defs><style>')
    for filename, weight, style in [('STIXGeneral.ttf','normal','normal'),('STIXGeneralBol.ttf','bold','normal'),('STIXGeneralItalic.ttf','normal','italic')]:
        data=base64.b64encode((fonts/filename).read_bytes()).decode()
        svg.append(f"@font-face {{font-family: 'RavenSTIX'; font-weight:{weight}; font-style:{style}; src:url(data:font/ttf;base64,{data}) format('truetype');}}")
    svg.append('</style></defs>')
    ink, muted = '#263747', '#667583'
    blue, teal, ochre = '#365E83', '#287B78', '#966D36'
    pale_b, pale_t, pale_o = '#EBF2F8', '#E9F3F1', '#FAF2E7'
    texts = []

    @contextmanager
    def group(name):
        svg.append(f'<g id="{name}">')
        yield
        svg.append('</g>')

    def line(points, color=ink, width=1.8, dashed=False, arrow=False, halo=False):
        if halo:
            line(points, '#FFFFFF', width+5)
        pdf.setStrokeColor(color); pdf.setLineWidth(width)
        pdf.setDash([7,5] if dashed else [])
        p = pdf.beginPath(); p.moveTo(points[0][0], H-points[0][1])
        for x,y in points[1:]: p.lineTo(x,H-y)
        pdf.drawPath(p)
        coords=' '.join(f'{x},{y}' for x,y in points)
        dash=' stroke-dasharray="7 5"' if dashed else ''
        svg.append(f'<polyline points="{coords}" fill="none" stroke="{color}" stroke-width="{width}"{dash}/>')
        if arrow:
            x,y=points[-1]; x0,y0=points[-2]; a=math.atan2(y-y0,x-x0)
            s=10; q=[(x,y),(x-s*math.cos(a)+4*math.sin(a),y-s*math.sin(a)-4*math.cos(a)),(x-s*math.cos(a)-4*math.sin(a),y-s*math.sin(a)+4*math.cos(a))]
            poly(q,color,color,0.5)

    def rect(x,y,w,h,fill='white',edge=ink,width=1.4,rx=0):
        pdf.setFillColor(fill); pdf.setStrokeColor(edge); pdf.setLineWidth(width);pdf.setDash([])
        pdf.roundRect(x,H-y-h,w,h,rx,stroke=1,fill=1)
        svg.append(f'<rect x="{x}" y="{y}" width="{w}" height="{h}" rx="{rx}" fill="{fill}" stroke="{edge}" stroke-width="{width}"/>')

    def poly(points,fill,edge=ink,width=1.4):
        pdf.setFillColor(fill);pdf.setStrokeColor(edge);pdf.setLineWidth(width);pdf.setDash([])
        p=pdf.beginPath();p.moveTo(points[0][0],H-points[0][1])
        for x,y in points[1:]:p.lineTo(x,H-y)
        p.close();pdf.drawPath(p,fill=1,stroke=1)
        svg.append(f'<polygon points="'+ ' '.join(f'{x},{y}' for x,y in points)+f'" fill="{fill}" stroke="{edge}" stroke-width="{width}"/>')

    def circle(x,y,r,fill='white',edge=ink,width=1.3):
        pdf.setFillColor(fill);pdf.setStrokeColor(edge);pdf.setLineWidth(width);pdf.setDash([])
        pdf.circle(x,H-y,r,fill=1,stroke=1)
        svg.append(f'<circle cx="{x}" cy="{y}" r="{r}" fill="{fill}" stroke="{edge}" stroke-width="{width}"/>')

    def text(x,y,s,size=21,bold=False,color=ink,anchor='middle'):
        # Explicit sub/sup runs: selectable Unicode text with exact positions.
        runs=[]; mode=None; b=bold; it=False
        for part in re.split(r'(<[^>]+>)',s):
            if part in ['<sub>','<sup>']:mode=part[1:-1]
            elif part in ['</sub>','</sup>']:mode=None
            elif part=='<b>':b=True
            elif part=='</b>':b=bold
            elif part=='<i>':it=True
            elif part=='</i>':it=False
            elif part:
                fs=size*.72 if mode else size;dy=5 if mode=='sub' else -8 if mode=='sup' else 0
                font='F1B' if b else 'F1I' if it else 'F1'
                hat='\u0302' in part
                part=part.replace('\u0302','')
                runs.append((part,fs,dy,font,b,it,hat,pdfmetrics.stringWidth(part,font,fs)))
        offsets=[];total=0;last_offset=0;last_dy=0
        for r in runs:
            dy=r[2];ww=r[-1]
            pos=last_offset if dy and last_dy and dy!=last_dy else total
            offsets.append(pos);total=max(total,pos+ww);last_offset=pos;last_dy=dy
        xstart=x-total/2 if anchor=='middle' else x-total if anchor=='end' else x
        texts.append((x,y,s,size))
        for (val,fs,dy,font,b,it,hat,ww),offset in zip(runs,offsets):
            xx=xstart+offset
            pdf.setFillColor(color);pdf.setFont(font,fs);pdf.drawString(xx,H-y-dy,val)
            for char in val:
                assert ord(char) in pdfmetrics.getFont(font).face.charToGlyph, (char, font)
            svg.append(f'<text x="{xx:.3f}" y="{y+dy:.3f}" font-family="RavenSTIX, STIXGeneral, Times New Roman, serif" font-size="{fs}" font-weight="{"bold" if b else "normal"}" font-style="{"italic" if it else "normal"}" fill="{color}">{escape(val)}</text>')
            if hat:
                bx=xx+pdfmetrics.stringWidth(val.split('β')[0],font,fs) if 'β' in val else xx
                bw=pdfmetrics.stringWidth('β',font,fs)
                line([(bx,y+dy-fs*.77),(bx+bw*.5,y+dy-fs*.91),(bx+bw,y+dy-fs*.77)],color,1.1)

    def arrow(points,**kwargs):line(points,arrow=True,**kwargs)
    def bars(x,y,heights,color=blue,w=15,gap=8):
        for i,h in enumerate(heights):rect(x+i*(w+gap),y-h,w,h,color,color,.7)
        line([(x-4,y+2),(x+len(heights)*(w+gap)-gap+4,y+2)],muted,1)
    def packet(x,y,color=blue):
        poly([(x,y),(x+22,y),(x+30,y+8),(x+30,y+40),(x,y+40)],'white',color)
        line([(x+22,y),(x+22,y+8),(x+30,y+8)],color,1)
        for yy in [16,23,30]:line([(x+5,y+yy),(x+24,y+yy)],color,1)

    # Native primitives only. Draw independent feedback underneath current flows;
    # white casings make crossings unambiguous (no junctions at crossings).
    with group('next-window-debt-feedback'):
        arrow([(1310,550),(1310,565),(755,565),(755,235)],color=ochre, dashed=True,halo=True)
        text(1010,558,'<b>Q</b><sub>r+1</sub>: next-window debt',19,color=ochre)
    with group('next-window-history-feedback'):
        line([(1380,630),(1380,650),(370,650),(370,96)],blue,dashed=True,halo=True)
        arrow([(370,96),(395,96)],color=blue,dashed=True,halo=True)
        arrow([(1165,650),(1165,210),(1145,210)],color=blue,dashed=True,halo=True)
        text(630,642,'Updated histories → next window',19,color=blue)

    with group('sensing-scene'):
        text(80,30,'Opportunity <i>R</i>',22,bold=True)
        for row in range(3):
            for col in range(3):rect(15+col*43,50+row*34,38,29,'#F0F3F4','#CFD7DB',.8)
        rect(15,89,124,17,'#DCE3E7','#DCE3E7',.1)
        rect(64,50,18,104,'#DCE3E7','#DCE3E7',.1)
        line([(15,98),(139,98)],'white',1.4,dashed=True)
        poly([(43,118),(48,108),(72,108),(81,118),(88,120),(88,134),(38,134),(38,122)],pale_b,blue)
        circle(49,135,5,ink);circle(78,135,5,ink)
        rect(59,101,9,7,teal,teal)
        line([(63,100),(63,94)],teal,1.5)
        text(80,179,'Mobile sensing',19)
        arrow([(145,110),(187,110)])
    with group('local-records'):
        text(266,30,'Observation <i>O</i>',22,bold=True)
        rect(193,52,142,105,'white','#758B9C',1.3)
        rect(193,52,142,29,pale_b,'#758B9C',1.3)
        text(264,73,'Local records',20)
        for y in [106,131]:line([(193,y),(335,y)],'#B4C0C8',1)
        line([(238,81),(238,157)],'#B4C0C8',1);line([(285,81),(285,157)],'#B4C0C8',1)
        text(216,101,'i',19);text(262,101,'Z',19);text(309,101,'…',19)
        text(216,127,'…',19);text(262,127,'…',19);text(309,127,'…',19)
        arrow([(264,157),(264,290)])
    with group('shared-correction'):
        rect(395,35,195,105,pale_b,blue,1.4,5)
        text(492,61,'Pre-outcome state',21,bold=True)
        text(492,88,'Selection / lagged state',19)
        text(492,116,'π<sup>tar</sup>; fixed Design',20)
        arrow([(492,140),(492,195)],color=blue)
        rect(395,195,195,60,pale_b,blue,1.5,5)
        text(492,219,'R/O correction',22,bold=True)
        text(492,244,'Record weights a<sub>k,r,i</sub>',20)
        # Same correction produces normalized training weights and total mass.
        arrow([(395,225),(350,225),(350,321),(335,321)],color=blue)
        text(341,278,'ā',23,color=blue,anchor='end')
        arrow([(492,255),(492,350)],color=blue)
        text(510,294,'Mass m<sub>k,r</sub>',20,color=blue,anchor='start')
        # The pre-U history is an input to d, not a current update-vector input.
        arrow([(590,88),(615,88),(615,334),(555,334),(555,350)],color=blue)
        text(610,323,'pre-U',18,color=blue,anchor='end')
    with group('local-training-and-window'):
        rect(130,290,205,65,'#F5F7F8',muted,1.3,5)
        text(232,316,'Local normalized',21,bold=True)
        text(232,340,'training',21,bold=True)
        arrow([(232,355),(232,389)])
        packet(218,391)
        text(286,414,'<b>u</b><sub>k,r</sub>',24)
        arrow([(218,411),(193,411),(193,468)],color=blue)
        text(120,455,'Usability <i>U</i>',21,bold=True)
        arrow([(35,511),(335,511)],width=1.4)
        circle(35,511,3,ink);line([(260,475),(260,523)],ink,1.8)
        packet(96,468);packet(178,468);packet(291,468,'#AAB2B8')
        text(35,540,'Open',19);text(260,540,'Close',19);text(308,565,'Late',19,color=muted)
        text(151,596,'Only usable, positive-mass clients',18,color=muted)
    with group('reference-reconstruction'):
        rect(395,350,195,65,pale_b,blue,1.8,5)
        text(492,375,'Reference mass',22,bold=True)
        text(492,401,'d<sub>k,r</sub>; β̂<sub>k,r</sub> ∝ m<sub>k,r</sub>d<sub>k,r</sub>',21)
        arrow([(590,383),(651,383)],color=blue,width=2.2)
        text(697,317,'Reference',21,bold=True,color=blue)
        text(697,350,'<b>β̂</b><sub>r</sub>',24,color=blue)
        bars(658,415,[58,31,47,24],blue,w=15,gap=8)
        arrow([(751,383),(800,383)],color=blue,width=2.3)
    with group('p2-inputs'):
        rect(665,35,135,120,'white','#A3B7C4',1.1,4)
        text(732,59,'Active support',20,bold=True)
        text(732,83,'A<sub>r</sub> ; M<sub>r</sub>',23)
        for r in range(2):
            for c in range(4):rect(694+c*19,98+r*19,16,16,[pale_b,'#BCD0DF','#83A7C2','white'][(r+c)%4],muted,.6)
        arrow([(800,115),(810,115),(810,280),(840,280),(840,300)],color=blue)
        rect(825,35,110,120,'white','#A3B7C4',1.1,4)
        text(880,59,'Target',20,bold=True)
        text(880,83,'<b>μ</b>',24)
        bars(850,138,[30,44,22],ochre,w=14,gap=7)
        arrow([(880,155),(880,300)],color=blue)
        rect(960,35,185,120,'white','#A3B7C4',1.1,4)
        text(1052,57,'Weight caps',20,bold=True)
        text(1052,81,'Effective support',20,bold=True)
        poly([(1023,112),(1040,94),(1070,97),(1084,121),(1061,147),(1025,136)],pale_t,teal)
        text(1054,129,'C<sub>r</sub>',24,color=teal)
        arrow([(990,155),(950,155),(950,300)],color=teal)
        rect(665,190,135,45,pale_o,ochre,1.2,4)
        text(732,219,'Current <b>Q</b><sub>r</sub>',21)
        arrow([(710,235),(710,270),(775,270),(775,315),(800,315)],color=ochre)
        rect(960,190,185,45,'#F1F4F6',muted,1.2,4)
        text(1052,219,'Lagged V<sub>r</sub>; staleness',20)
        arrow([(1052,235),(1052,335),(1020,335)],color=blue)
    with group('single-p2-program'):
        rect(800,300,220,125,pale_t,teal,2.5,7)
        text(910,329,'P2: calibration',24,bold=True,color=teal)
        text(910,359,'Reference fidelity',21)
        text(910,386,'Group alignment',21)
        text(910,411,'Debt + state regularization',18)
        arrow([(1020,383),(1055,383)],color=teal,width=2.3)
    with group('single-weight-output'):
        text(1102,326,'Weights',21,bold=True,color=teal)
        text(1102,350,'<b>α</b><sup>⋆</sup><sub>r</sub> ∈ C<sub>r</sub>',23,color=teal)
        bars(1064,415,[39,27,43,36],teal,w=15,gap=8)
        arrow([(1155,383),(1235,383)],color=teal,width=2.3,halo=True)
    with group('usable-update-stream'):
        arrow([(208,488),(225,488),(225,437),(355,437),(355,452),(1204,452),(1204,403),(1235,403)],color=blue,width=2.1,halo=True)
        text(850,472,'Usable normalized model updates <b>u</b><sub>k,r</sub>',20,color=blue)
    with group('aggregation-and-model'):
        text(1300,301,'Weighted',22,bold=True)
        text(1300,326,'aggregation',22,bold=True)
        for y in [346,371,396]:
            rect(1235,y,120,21,'#E4EBEF',blue,1.5,3)
            circle(1338,y+10,3,'white',blue,.8)
            line([(1248,y+10),(1283,y+10)],blue,1.5)
        arrow([(1355,383),(1400,383)],width=1.8)
        text(1442,301,'Updated',21,bold=True)
        text(1442,326,'model',21,bold=True)
        text(1442,350,'θ<sub>r+1</sub>',25)
        for a in [(1410,374),(1410,410)]:
            for b in [(1440,365),(1440,392),(1440,420)]:line([a,b],blue,1)
        for a in [(1440,365),(1440,392),(1440,420)]:line([a,(1470,392)],blue,1)
        for x,y in [(1410,374),(1410,410),(1440,365),(1440,392),(1440,420),(1470,392)]:circle(x,y,6,pale_b,blue,1)
    with group('composition-and-post-aggregation-state'):
        # Composition is computed from weights + M, never from theta.
        arrow([(1105,419),(1105,490)],color=teal,halo=True)
        rect(1059,490,102,43,'white',teal,1.2,3)
        text(1110,518,'<b>ω</b><sub>r</sub> = M<sub>r</sub><b>α</b><sup>⋆</sup><sub>r</sub>',20)
        arrow([(1161,511),(1215,511)],color=teal,halo=True)
        text(1355,468,'After aggregation',20,bold=True)
        rect(1215,485,275,65,pale_o,ochre,1.4,4)
        # Minimal two-row group ledger: no experimental values.
        rect(1228,497,44,40,'white',ochre,.8)
        line([(1228,517),(1272,517)],ochre,.7);line([(1247,497),(1247,537)],ochre,.7)
        text(1238,512,'g',18);text(1260,512,'…',18)
        text(1238,533,'g',18);text(1260,533,'…',18)
        text(1382,508,'Group debt',21,bold=True)
        text(1382,535,'<b>Q</b><sub>r+1</sub> ← (<b>Q</b><sub>r</sub>, <b>μ</b> − <b>ω</b><sub>r</sub>)',21)
        rect(1215,580,275,50,pale_b,blue,1.3,4)
        text(1352,600,'Updated histories',20,bold=True)
        text(1352,622,'Selection / variance',19)
    with group('legend-and-panel-labels'):
        line([(45,628),(85,628)],ink,1.8,arrow=True);text(95,635,'Current window',19,anchor='start')
        line([(45,656),(85,656)],ink,1.8,dashed=True,arrow=True);text(95,662,'Next-window feedback',19,anchor='start')
        line([(15,675),(345,675)],'#D4DCE1',1)
        line([(395,675),(1145,675)],'#D4DCE1',1)
        line([(1215,675),(1490,675)],'#D4DCE1',1)
        text(180,697,'(a) Sensing and usable updates',23,bold=True)
        text(770,697,'(b) Reference reconstruction and feasible calibration',23,bold=True)
        text(1352,697,'(c) Aggregate + feedback',22,bold=True)

    pdf.showPage();pdf.save()
    svg.append('</svg>');stem.with_suffix('.svg').write_text('\n'.join(svg),encoding='utf-8')
    exe=poppler or shutil.which('pdftoppm')
    if exe:
        subprocess.run([str(exe),'-singlefile','-r','250','-png',str(stem.with_suffix('.pdf')),str(stem)],check=True,stdout=subprocess.PIPE,stderr=subprocess.PIPE)
    return stem


if __name__ == '__main__':
    import argparse
    parser=argparse.ArgumentParser()
    parser.add_argument('--out',default=str(Path(__file__).parent))
    parser.add_argument('--poppler')
    args=parser.parse_args()
    print(render_fig1(args.out,args.poppler))
