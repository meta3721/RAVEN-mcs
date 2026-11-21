"""Write the TE2 Phase 0 report."""
from __future__ import annotations

import json
import pathlib

ROOT = pathlib.Path(r"C:\Cursor\raven.mcs")
D = ROOT / "results_traffic_e2/round_v1"
d = json.loads((D / "TE2_PHASE0.json").read_text(encoding="utf-8"))
s = d["paired_vs_control"]

L = [
    "# TE2 Phase 0 — power gate",
    "",
    "Mode: re-scoring of stored checkpoints only. **No training run was executed.** Phase 0 exists",
    "because the previous round skipped it and ended with an 80 % minimum detectable effect of 5.80 %",
    "against an estimate of 1.49 %, i.e. it could not resolve the bar it was aimed at.",
    "",
    "## Primary cell as realised",
    "",
    f"- priority rule: the region holding the largest share of the frozen pre-outcome target mass under",
    f"  `kappa = 1`; the realised masses are `region0 0.232558`, `region1/2/3 0.255814` each, so **three",
    f"  regions tie and the rule as written is not well defined**. The run resolved the tie by ascending",
    f"  region id, giving **{d['priority_region']}**; an explicit tie-break must be added to the",
    f"  pre-registration before any confirmatory run.",
    f"- `kappa = 5` on that region gives region shares {d['region_mass_kappa5']} —",
    f"  a **top-1 share of {max(d['region_mass_kappa5'].values()):.4f}**, against the design table's analytic",
    f"  `0.6250` for four equal regions. Close, because the frozen regions are nearly equal.",
    f"- concentrated weight vector sha256 `{d['mass_sha256']}`.",
    "",
    "**Correction to the design's own diagnostic.** The design listed `effective groups` at the *group*",
    "level; that metric is wrong for this treatment. Multiplying whole regions by a constant leaves the",
    "172 group masses nearly uniform inside each region, so the group-level effective count stays near 126",
    "of 172 and says nothing. The concentration this design exploits is at the **region** level, where the",
    "realised top-1 share is 0.6322 and the effective number of regions is about 2.9 of 4. A later `kappa`",
    "must be judged on the region-level share.",
    "",
    "## Scores under the concentrated criterion (20 frozen seeds, 30001-30020)",
    "",
    "| arm | mean `RMSE_mu`, concentrated target | mean under the frozen target |",
    "|---|---:|---:|",
]
for a in ("local_hajek", "inst_cal", "debt_cal", "raven_simoracle"):
    L.append(f"| `{a}` | {sum(d['arms'][a]['concentrated_per_seed']) / d['n_seeds']:.6f} | "
             f"{d['arms'][a]['frozen_target_mean']:.6f} |")
L += [
    "",
    "## The gate",
    "",
    f"`n = {d['n_seeds']}`, `t = (2.093024, 0.860951)`, bar = 2 % of the control's concentrated error =",
    f"`{d['bar_2pct_of_control']:.6f}`.",
    "",
    "| contrast | mean `D` | sd `D` | `MDE80` | bootstrap 95 % | `MDE80 <= 2 % bar` |",
    "|---|---:|---:|---:|---|---|",
]
for a, v in sorted(s.items()):
    L.append(f"| `local_hajek - {a}` | {v['mean_D']:+.6f} | {v['sd_D']:.6f} | {v['MDE80']:.6f} | "
             f"[{v['boot_lo']:+.5f}, {v['boot_hi']:+.5f}] | **{v['passes']}** |")
L += [
    "",
    f"**Verdict: `{d['verdict']}`.** The realised `MDE80` is 34 to 65 times smaller than the bar, so the",
    "design can resolve effects far below the 2 % the decision rule needs. No `TE2_BLOCKED.md` is written.",
    "",
    "## Two caveats that the next step must carry",
    "",
    "1. **The sd is a lower bound.** These checkpoints were trained under the *uniform* target, so all four",
    "   arms predict almost the same thing and their spread on the concentrated criterion is small by",
    "   construction. In the real round the arms are trained *for* the concentrated target and can diverge",
    "   much more, so the realised paired sd will be larger and the realised `MDE80` correspondingly",
    "   larger. The gate therefore establishes that the *scoring path* is precise enough, not that the",
    "   confirmatory round will be powered.",
    "2. **No arm is separated here, and the control is nominally best.** Mean `D` is negative for every",
    "   treatment, i.e. the P2 arms are very slightly *worse* than the no-P2 control under the concentrated",
    "   criterion, and every interval contains zero. That is the expected reading for models trained",
    "   against a different criterion, and it is precisely why the round's treatment has to be a training",
    "   run rather than a re-scoring. It is not evidence about the design's question.",
    "",
    "## Cost of the next step, for the decision",
    "",
    "- step 3 (primary cell, `kappa = 5`, four arms, 20 seeds) 80 runs, about 55 minutes;",
    "- step 4 (ladder `kappa in {1,2,10}` plus the single-region limit) 320 runs more;",
    "- step 5 (priority-region sensitivity) 240 runs more;",
    "- total 640 runs, about 7 hours on the same single-threaded path.",
    "",
    "Because of caveat 1 the honest ordering is to run step 3 first and re-estimate the paired sd from",
    "arms that were actually trained for the concentrated target, before committing to steps 4 and 5.",
]
(D / "TE2_PHASE0_REPORT.md").write_text("\n".join(L) + "\n", encoding="utf-8")
print("wrote", (D / "TE2_PHASE0_REPORT.md").relative_to(ROOT).as_posix(),
      (D / "TE2_PHASE0_REPORT.md").stat().st_size, "B")
print("TE2_BLOCKED.md present:", (D / "TE2_BLOCKED.md").exists(), "(expected False)")
