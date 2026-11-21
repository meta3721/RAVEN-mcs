"""Render the six published arrival-log support summaries; no experiment calls.

Source: appendix.tex, tab:arrival_support (Appendix F-A). Values are rounded
table summaries, not reconstructed window data. No uncertainty is fabricated.
"""
from pathlib import Path
import argparse
import json
import re
import matplotlib
matplotlib.use('Agg')
import matplotlib.pyplot as plt
import numpy as np
from data_figures_revision import style

ROOT = Path(__file__).resolve().parent
ROWS = [
    ('Traffic', '<=3', 294, 75.000, 25.000, 0.000, 1.5000),
    ('Traffic', '>3', 1696, 75.000, 25.000, 0.000, 1.5000),
    ('SensorScope', '<=3', 1475, 98.916, 1.084, 0.000, 1.9783),
    ('SensorScope', '>3', 402, 97.748, 0.000, 2.252, 1.9550),
    ('U-Air', '<=3', 1197, 98.551, 1.449, 0.000, 1.9710),
    ('U-Air', '>3', 318, 97.024, 0.000, 2.976, 1.9405),
]


def verify_source():
    text = (ROOT/'appendix.tex').read_text(encoding='utf-8')
    pos = text.index(r'\label{tab:arrival_support}')
    block = text[pos:text.index(r'\end{table}', pos)]
    found = []
    for line in block.splitlines():
        if not re.match(r'^(Traffic|SensorScope|U-Air) &', line):
            continue
        a = [x.strip().replace('$', '').replace(r'\\', '') for x in line.split('&')]
        k = '<=3' if r'\le' in a[1] else '>3'
        found.append((a[0], k, int(a[2]), *[float(x) for x in a[3:]]))
    assert found == ROWS, ('Arrival-table values differ', found)
    assert all(abs(sum(row[3:6])-100) < 1e-9 for row in ROWS)
    return found


def render(out):
    rows = verify_source()
    out = Path(out); out.mkdir(parents=True, exist_ok=True)
    style()
    fig, ax = plt.subplots(figsize=(3.5, 2.05))
    fig.subplots_adjust(left=.32, right=.86, bottom=.24, top=.83)
    yy = np.array([0, 1, 2.35, 3.35, 4.7, 5.7])
    colors = ['#D4DADE', '#BD9D74', '#365E83']
    hatches = [None, '//', None]
    labels = ['Missing', 'Narrow', 'Adjustable']
    for j, label in enumerate(labels):
        vals = np.array([row[3+j] for row in rows])
        left = np.array([sum(row[3:3+j]) for row in rows])
        ax.barh(yy, vals, left=left, height=.66, label=label,
                color=colors[j], hatch=hatches[j], edgecolor='#50606D',
                linewidth=.35, zorder=2)
        for y, value, start in zip(yy, vals, left):
            if value == 0:
                continue
            if value >= 15:
                ax.text(start+value/2, y, f'{value:.3f}', ha='center',
                        va='center', fontsize=9.1, zorder=4)
            else:
                ax.annotate(f'{value:.3f}', xy=(start+value/2, y),
                    xytext=(103, y), textcoords='data', ha='left',
                    va='center', fontsize=9.1,
                    color='#365E83' if j == 2 else '#72552E',
                    arrowprops={'arrowstyle':'-', 'lw':.5, 'color':'#69737B'},
                    annotation_clip=False)
    ticks = [f'{row[0]}  '+(r'$K\leq3$' if row[1]=='<=3' else r'$K>3$') for row in rows]
    ax.set_yticks(yy, ticks, fontsize=9.1)
    ax.set_ylim(6.35, -.65); ax.set_xlim(0, 100)
    ax.set_xticks([0, 25, 50, 75, 100])
    ax.set_xlabel('Target mass (%)', fontsize=9.6, labelpad=3)
    ax.tick_params(axis='y', length=0, pad=3)
    ax.tick_params(axis='x', length=2.3, width=.6, pad=2)
    for side in ['top', 'right', 'left']:
        ax.spines[side].set_visible(False)
    ax.spines['bottom'].set_color('#69737B'); ax.spines['bottom'].set_linewidth(.65)
    handles, names = ax.get_legend_handles_labels()
    fig.legend(handles, names, loc='upper center', bbox_to_anchor=(.52, 1.005),
               ncol=3, frameon=False, fontsize=9.1, handlelength=1.2,
               columnspacing=.8, handletextpad=.4)
    fig.canvas.draw()
    renderer = fig.canvas.get_renderer()
    for obj in list(ax.texts)+ax.get_yticklabels()+[ax.xaxis.label]:
        bb = obj.get_window_extent(renderer)
        assert fig.bbox.contains(bb.x0, bb.y0) and fig.bbox.contains(bb.x1, bb.y1), ('Text clipped', obj.get_text(), bb.bounds)
    name = 'fig_arrival_support_geometry'
    for ext in ['pdf', 'svg', 'png']:
        fig.savefig(out/f'{name}.{ext}', facecolor='white', dpi=250)
    plt.close(fig)
    record = {'source':'appendix.tex#tab:arrival_support', 'seed_range':[30001,30020],
        'support':'nonempty formal complete-aligned arrival logs; not the full Design-on P2 support',
        'columns':['dataset','K','windows','missing_pct','narrow_pct','adjustable_pct','L1'],
        'rows':rows, 'source_table_match':True, 'uncertainty':'none; existing rounded table summaries',
        'aggregation':'seed means within stratum, then equally weighted; as specified in Appendix F-A',
        'size_inches':[3.5,2.05], 'axis_limits':[0,100]}
    (out/'ARRIVAL_SUPPORT_FIGURE_SOURCES.json').write_text(json.dumps(record,indent=2),encoding='utf-8')
    return record


if __name__ == '__main__':
    parser = argparse.ArgumentParser()
    parser.add_argument('--out', type=Path, default=ROOT/'figures/page_fill_candidate')
    print(render(parser.parse_args().out))
