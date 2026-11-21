"""Write the TE2 step-3 report from the round's own artifacts."""
from __future__ import annotations

import csv
import json
import pathlib

import numpy as np

ROOT = pathlib.Path(r"C:\Cursor\raven.mcs")
OUT = ROOT / "results_traffic_e2/round_v1"

v = json.loads((OUT / "TE2_VERDICT.json").read_text(encoding="utf-8"))
pre = json.loads((OUT / "TE2_FROZEN_PREREG.json").read_text(encoding="utf-8"))
rows = list(csv.DictReader((OUT / "tables/TE2_MAIN.csv").open(encoding="utf-8")))
arms = pre["arms"]
order = [arms["control"], "inst_cal", "debt_cal", arms["oracle_upper_bound"]]

L = [
    "# TE2 step 3 — primary cell (kappa = 5, priority region 1)",
    "",
    "Frozen server step (the round's only changed variable is the **deployment target distribution**).",
    "The target artifact was injected through `run_e3_real(target_artifact=...)` with no edit to `src/`,",
    "which works on this block because `FROZEN_TARGET_ARTIFACTS` contains only `sensorscope` and `uair`.",
    "",
    "## Pre-registration, and a hash caveat",
    "",
]
L += [f"- `TE2_FROZEN_PREREG.json`, frozen {pre['frozen_utc']}",
      f"- priority region `{pre['target_artifact']['priority_region']}`, kappa `{pre['target_artifact']['kappa']}`",
      f"- priority rule: {pre['target_artifact']['priority_rule']}",
      f"- tie note: {pre['target_artifact']['tie_note']}",
      f"- arms: control `{arms['control']}`, treatment `{arms['treatment']}`, oracle ceiling "
      f"`{arms['oracle_upper_bound']}`; roles from {arms['roles_from']}",
      f"- seeds {pre['seeds'][0]}-{pre['seeds'][-1]} ({len(pre['seeds'])})",
      f"- endpoint: {pre['primary_endpoint']}",
      f"- decision rule: {pre['decision_rule']}",
      "",
      "**Two hashes exist for the same content and must not be conflated.** Each run's",
      f"`config_snapshot.json` records the runner's own digest `sha256_json({{mu, head_groups, tail_groups,",
      f"n_groups}})`, which is `{v['artifact_sha_seen'][0][:16]}...`; the artifact file's own",
      "`_artifact_sha256` field was produced with a different serialisation and reads",
      "`f34e5b9403036cd6...`. The runner's value is the anchor: it is written into every run. The runner",
      "also labels the path itself as `inline_fixture_freeze` and overwrites any caller-supplied label,",
      "so the label is not a discriminator; the digest is.",
      "",
      "## Smoke test (the only one, on the changed critical path)",
      "",
      "One cell, `local_hajek` seed 30001. Stored `RMSE_mu` `1.01148448233591` equals a manual re-score of",
      "the same checkpoint under the concentrated weights to the last digit, differs from the re-score",
      "under the frozen weights (`1.0055697313116083`), and that frozen-weight re-score reproduces the",
      "frozen uniform-target run of the same cell (`1.0055697313116085`). The injection is therefore in",
      "force, the metric uses the new weights, and the cell still reproduces the frozen protocol when",
      "scored with the frozen target. `optimizer_steps = 0` on every run confirms the server step was not",
      "replaced.",
      "",
      "## Scores under the concentrated criterion",
      "",
      "| arm | mean test `RMSE_mu` | sd | mean concentrated validation `RMSE_mu` | mean `K_r <= 3` share |",
      "|---|---:|---:|---:|---:|",
      ]
for a in order:
    sel = [r for r in rows if r["arm"] == a and r.get("missing") == "False"]
    t = np.asarray([float(r["test_RMSE_mu"]) for r in sel])
    vv = np.asarray([float(r["val_RMSE_mu_concentrated"]) for r in sel])
    k = np.asarray([float(r["kr_le3_share"]) for r in sel])
    L.append(f"| `{a}` | {t.mean():.6f} | {t.std(ddof=1):.6f} | {vv.mean():.6f} | {k.mean():.4f} |")

L += ["", "## The pre-registered contrast", "",
      f"Bar = 2 % of the control's deployment-weighted error = `{v['bar_2pct_of_control']:.6f}`; "
      f"`n = {v['n_pairs']}`.", "",
      "| contrast | mean D | sd D | MDE80 | bootstrap 95 % | interval favourable | "
      "mean > own MDE80 | effect >= 2 % bar | **separated** |",
      "|---|---:|---:|---:|---|---|---|---|---|"]
for a, c in sorted(v["contrasts"].items()):
    if "mean_D" not in c:
        L.append(f"| `{v['contrasts'] and a}` | | | | | | | | {c.get('verdict')} |")
        continue
    cond = c["conditions"]
    L.append(f"| control - `{a}` | {c['mean_D']:+.6f} | {c['sd_D']:.6f} | {c['MDE80']:.6f} | "
             f"[{c['boot_lo']:+.5f}, {c['boot_hi']:+.5f}] | {cond['interval_entirely_favourable']} | "
             f"{cond['mean_exceeds_own_MDE80']} | {cond['effect_ge_2pct_of_control']} | "
             f"**{c['separated']}** |")

sep = [a for a, c in v["contrasts"].items() if c.get("separated")]
L += [
    "",
    f"**Result under the pre-registered rule: no treatment arm is separated.** "
    f"{'Separated arms: ' + ', '.join(sep) if sep else 'Every treatment contrast fails at least one of the three conditions, so the structural-concentration claim is not supported at this cell.'}",
    "",
    "The control-versus-oracle contrast is the ceiling of what any weighting inside this class could buy",
    "at this concentration; where it is small, the treatment has little room by construction rather than",
    "by failure of the projection.",
    "",
    "## The number this step was run to obtain",
    "",
    "Phase 0 could only give a lower bound on the paired sd, because its checkpoints were trained under",
    "the uniform target. These arms were trained **for** the concentrated target, so this paired sd is the",
    "real one:",
    "",
]
for a, c in sorted(v["contrasts"].items()):
    if "sd_D" in c:
        L.append(f"- control vs `{a}`: paired sd `{c['sd_D']:.6f}` "
                 f"({100 * c['sd_D'] / c['control_mean']:.4f} % of the control level), "
                 f"`MDE80 = {c['MDE80']:.6f}`, against the 2 % bar `{v['bar_2pct_of_control']:.6f}`.")
L += [
    "",
    "## Feasible-set slack under the concentrated target",
    "",
    f"Mean `K_r <= 3` share across the 80 cells: `{v['kr_le3_share_mean']:.4f}`. The design required this",
    "to be re-measured because the aggregation weights feed back into the active set; the frozen",
    "uniform-target value was `0.1111` on one cell and `0.1508` pooled on the confirm set.",
    "",
    "## What this step does not do",
    "",
    "- It does not run the `kappa` ladder, the priority-region sensitivity, or the attribution ablations.",
    "  Steps 4 and 5 are unstarted and their cost is unchanged.",
    "- It is not evidence about real deployments: the priority region and its weight were chosen by the",
    "  authors and declared before the runs, which is what makes the contrast interpretable, and it is",
    "  also what limits the claim to the declared scenario.",
    "- No manuscript change follows from it.",
]
(OUT / "TE2_REPORT.md").write_text("\n".join(L) + "\n", encoding="utf-8")
print("wrote", (OUT / "TE2_REPORT.md").relative_to(ROOT).as_posix(),
      (OUT / "TE2_REPORT.md").stat().st_size, "B")
print("cells:", len(rows), "missing:", sum(1 for r in rows if r.get('missing') == 'True'))
print("separated:", sep if sep else "none")
