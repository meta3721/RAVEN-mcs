"""Write the vs-training-mean comparison report (no manuscript change)."""
from __future__ import annotations

import json
import pathlib

ROOT = pathlib.Path(r"C:\Cursor\raven.mcs")
D = ROOT / "results_paper_ceiling/round_v1"
d = json.loads((D / "VS_TRAIN_MEAN.json").read_text(encoding="utf-8"))

tm = d["training_mean_predictor"]
PRINTED = {"SensorScope": (7.6471, {"FedAvg-Window": 7.9389, "TwoStage-H\u00e1jek": 7.9309,
                                    "FedAU-Window": 7.9364, "ObsUse-Window": 7.9293,
                                    "RAVEN-Design": 7.9380, "RAVEN-NoDesign": 7.9384}),
           "U-Air": (1.0537, {"FedAvg-Window": 1.1119, "TwoStage-H\u00e1jek": 1.2202,
                              "FedAU-Window": 1.1128, "ObsUse-Window": 1.1120,
                              "RAVEN-Design": 1.1954, "RAVEN-NoDesign": 1.1131})}
TRAFFIC = (1.0067, {"central_all (tree, 20 seeds)": 0.9538,
                    "central_delivered (tree, 20 seeds)": 0.9754,
                    "local_hajek = inst_cal = debt_cal = raven_simoracle (tree, 20 seeds)": 1.0035,
                    "fedavg_window, Adam step (TE1, 15 confirm seeds)": 0.9671,
                    "raven_simoracle, Adam step (TE1, 15 confirm seeds)": 0.9731})

L = ["# Do the paper's models beat the training-mean predictor?", "",
     "Assessment only. **No manuscript file was touched.** The question matters because the training-mean",
     "predictor is the paper's no-information baseline: it uses only the training split, so it is the right",
     "comparator for skill, whereas the test-fitted constant is an oracle over the same labels the arms are",
     "scored on.", "",
     "## The baseline, recomputed from the data and checked against the manuscript", "",
     "| block | training-split target mean | training-mean predictor `RMSE_mu` | manuscript prints | match | test-fitted constant | test target mean |",
     "|---|---:|---:|---:|---|---:|---:|"]
for b, key in (("SensorScope", "sensorscope"), ("U-Air", "uair"), ("NSW-Traffic", "traffic")):
    v = tm[key]
    printed = {"sensorscope": 7.647, "uair": 1.054, "traffic": 1.007}[key]
    L.append(f"| {b} | {v['c_unweighted']:+.4f} | **{v['train_mean_predictor_rmse_mu']:.4f}** | {printed} | "
             f"{d['verification'][key]['match']} | {v['test_fitted_constant_rmse_mu']:.4f} | "
             f"{v['test_target_mean']:+.4f} |")
L += ["", "The baseline is therefore exactly reproducible, and the level shift it exposes is the mechanism:",
      "SensorScope's training target mean is `+0.3006` while its test target mean is `+7.6572`, a factor of",
      "25. On U-Air the shift is `-0.0000` to `-0.8066`. On NSW-Traffic the two coincide, which is why the",
      "training-mean predictor and the test-fitted constant take the same value there.", "",
      "## Verdict per block", ""]

for block, (base, arms) in PRINTED.items():
    L += [f"### {block} (training-mean predictor {base:.4f})", "",
          "| model as printed | `RMSE_mu` | versus the training-mean predictor | beats it? |",
          "|---|---:|---:|---|"]
    for a, v in sorted(arms.items(), key=lambda kv: kv[1]):
        pct = 100 * (v / base - 1)
        L.append(f"| {a} | {v:.4f} | **{pct:+.2f} %** | {'yes' if v < base else 'no'} |")
    L += ["", f"**{sum(1 for v in arms.values() if v < base)} of {len(arms)} beat it.**", ""]

base, arms = TRAFFIC
L += [f"### NSW-Traffic (training-mean predictor {base:.4f}, the same value as the test-fitted constant)",
      "", "| model | `RMSE_mu` | versus the training-mean predictor | beats it? |", "|---|---:|---:|---|"]
for a, v in sorted(arms.items(), key=lambda kv: kv[1]):
    L.append(f"| {a} | {v:.4f} | **{100 * (v / base - 1):+.2f} %** | {'yes' if v < base else 'no'} |")
L += ["", f"**{sum(1 for v in arms.values() if v < base)} of {len(arms)} beat it**, but the four P2 arms beat it by",
      "only `0.32 %`, which is consistent with the concentration ladder's finding that this weight class has",
      "about `0.02 %` to `0.1 %` of room on this block.", "",
      "## What this means", "",
      "1. **On both air-quality blocks, no model in the paper beats a constant computed from the training",
      "   split.** All six printed U-Air rows and all six SensorScope rows are worse, by `3.7 %` to `15.8 %`.",
      "2. **The reason is the level shift, not the aggregation rule.** When the target level moves by far more",
      "   than the residual spread, a constant carries the level error alone while a fitted model carries the",
      "   same level error plus estimation variance, so the model loses. The printed ratio between the two",
      "   constants, `3.7x` on SensorScope and `1.6x` on U-Air, is exactly that spread difference.",
      "3. **This is the sharpest form of the paper's own negative and it supports its thesis**, since it shows",
      "   the deployment-level error is governed by the target's level rather than by the weights. The",
      "   manuscript prints the baseline and says the absolute column is read against it, but it does not",
      "   state the verdict, so a reader must do this arithmetic.",
      "4. **NSW-Traffic is the exception and the model class does have skill there**, because its training and",
      "   test levels coincide; that is also why the two baselines coincide at `1.0067`.", "",
      "## Provenance of the numbers compared", "",
      "- The SensorScope and U-Air rows are the manuscript's printed values. An earlier scan of",
      "  `artifacts/e3_formal_runs_r1/runs/{sensorscope,uair}` reproduced the SensorScope row exactly",
      "  (`fedavg_window` 20-seed mean `7.9389`) but not the U-Air row, and the difference is explained by an",
      "  existing audit rather than by a conflict: `results_seed_path_audit_r1/C3_CELL_DIFF.md` records that",
      "  three U-Air seeds (30007, 30016, 30018) do not aggregate in their last window, so run-time",
      "  `RMSE_mu` came from the in-memory mirror while the paper's convention is the theta copy, and that",
      "  audit updated the affected cells on 2026-09-29. The paper's U-Air FedAvg row is also the later",
      "  `fedavg_window_current` (`1.1119 +/- 0.0603`, matching the print to the digit), not the frozen",
      "  `fedavg_window` (`1.1923`) that the scanned tree still holds.",
      "- The NSW-Traffic rows come from the frozen E3 tree (20 seeds) and from the Adam-replacement tree",
      "  (15 confirm seeds); the four P2 arms are identical to four decimal places there.",
      "- No number in this report was estimated or rounded from a model output; the baseline was recomputed",
      "  and the arm values are read from the manuscript or from `final_metrics.json`.", ""]
(D / "VS_TRAIN_MEAN.md").write_text("\n".join(L) + "\n", encoding="utf-8")
print("wrote", (D / "VS_TRAIN_MEAN.md").relative_to(ROOT).as_posix(),
      (D / "VS_TRAIN_MEAN.md").stat().st_size, "B")
