"""Check that no text element overflows the panel frame (data coords 0..10)."""
import matplotlib

matplotlib.use("Agg")
import matplotlib.pyplot as plt

import make_fig1_icons as m

m._style()
fig, axes = plt.subplots(1, 2, figsize=(7.16, 3.1))
m.panel_a(axes[0])
m.panel_b(axes[1])
fig.canvas.draw()

renderer = fig.canvas.get_renderer()
problems = 0
for i, ax in enumerate(axes):
    xmin, xmax = ax.get_xlim()
    ymin, ymax = ax.get_ylim()
    inv = ax.transData.inverted()
    for t in ax.texts:
        bb = t.get_window_extent(renderer=renderer)
        (x0, y0), (x1, y1) = inv.transform([(bb.x0, bb.y0), (bb.x1, bb.y1)])
        if x0 < xmin - 0.05 or x1 > xmax + 0.05 or y0 < ymin - 0.05 or y1 > ymax + 0.05:
            problems += 1
            print(f"panel {i} OVERFLOW {t.get_text()!r}: "
                  f"({x0:.2f},{y0:.2f})-({x1:.2f},{y1:.2f})")
print("done,", problems, "overflow(s)")
