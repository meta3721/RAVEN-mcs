"""READ-ONLY: per-seed comparison of the U-Air Design-on RMSE_mu across vintages."""
import json
import pathlib

import pandas as pd

ROOT = pathlib.Path(r"C:\Cursor\raven.mcs")
E3 = ROOT / "artifacts/e3_formal_runs_r1/runs"
E4 = ROOT / "artifacts/e4_core_mechanism_ablation_r1/runs"
SEEDS = list(range(30001, 30021))

hm = pd.read_csv(ROOT / ".rb_work/evidence_headroom/HEADROOM.csv")
tab = pd.read_csv(ROOT / "paper_ready_r1/01_core_data/e4/E4_FINAL_VALID_EVIDENCE_240.csv")

rows = []
for s in SEEDS:
    stored_on = None
    for f in ("final_metrics.json", "final_metrics_dual_domain.json"):
        p = E3 / "uair" / "raven" / ("seed%d" % s) / f
        if p.is_file():
            d = json.loads(p.read_text(encoding="utf-8"))
            if stored_on is None and "RMSE_mu" in d:
                stored_on = float(d["RMSE_mu"])
    p = E4 / "uair" / "raven_wo_design" / ("seed%d" % s) / "final_metrics.json"
    stored_off = float(json.loads(p.read_text(encoding="utf-8"))["RMSE_mu"]) if p.is_file() else None
    h_on = float(hm[(hm.dataset == "uair") & (hm.arm == "raven") & (hm.seed == s)].RMSE_mu_tar.iloc[0])
    h_off = float(hm[(hm.dataset == "uair") & (hm.arm == "raven_wo_design") & (hm.seed == s)].RMSE_mu_tar.iloc[0])
    t_on = float(tab[(tab.dataset == "U-Air") & (tab.configuration == "RAVEN-MCS") & (tab.seed == s)].RMSE_mu.iloc[0])
    t_off = float(tab[(tab.dataset == "U-Air") & (tab.configuration == "RAVEN-w/o-Design") & (tab.seed == s)].RMSE_mu.iloc[0])
    rows.append({"seed": s, "stored_E3_on": stored_on, "table_on": t_on, "headroom_on": h_on,
                 "stored_off": stored_off, "table_off": t_off, "headroom_off": h_off,
                 "headroom_on_minus_stored": h_on - stored_on})
df = pd.DataFrame(rows)
pd.set_option("display.width", 200)
print(df.to_string(index=False))
print()
print("means:")
print(df[["stored_E3_on", "table_on", "headroom_on", "stored_off", "table_off", "headroom_off"]].mean())
print()
print("checkpoint_hash of the uair raven runs (from the 240 table):")
sub = tab[(tab.dataset == "U-Air") & (tab.configuration == "RAVEN-MCS")]
print(sub[["seed", "checkpoint_hash", "metrics_hash", "path", "source_file"]].head(3).to_string(index=False))
print()
print("how many seeds differ HEADROOM vs stored on the design-ON arm: %d / %d"
      % (int((df.headroom_on_minus_stored.abs() > 1e-9).sum()), len(df)))
print("max |diff| = %.6f ; relative to stored: %.4f %%"
      % (df.headroom_on_minus_stored.abs().max(),
         100 * (df.headroom_on.mean() / df.stored_E3_on.mean() - 1)))
print()
print("implied Design effect on U-Air RMSE_mu (ratio of means, %%):")
print("  from stored E3/E4 final_metrics : %+.6f %%" % (100 * (df.stored_off.mean() / df.stored_E3_on.mean() - 1)))
print("  from the 240-cell evidence table: %+.6f %%" % (100 * (df.table_off.mean() / df.table_on.mean() - 1)))
print("  from HEADROOM.csv               : %+.6f %%" % (100 * (df.headroom_off.mean() / df.headroom_on.mean() - 1)))
print("  FIG_E4_E4_COMPONENT_ABLATION.csv: -6.885463676716227 %")
print("  main.tex printed               : 6.885 %%")
