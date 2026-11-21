"""TS1: structural readout of Delta_group and Delta_c_s from the 15 TE1 confirm pairs.

Read-only on TE1 (only final_metrics.json), read-only on everything else. No training, no metric
recomputation. Outputs under results_traffic_struct/round_v1/.
"""
from __future__ import annotations

import csv
import json
import math
import pathlib
from datetime import datetime, timezone

import numpy as np

ROOT = pathlib.Path(r"C:\Cursor\raven.mcs")
OUT = ROOT / "results_traffic_struct/round_v1"
TE1 = ROOT / "results_traffic_e1/round_v1"
SEEDS = list(range(30006, 30021))
ARM_DIRS = {"fedavg_window": "C1_fedavg/traffic/fedavg_window",
            "raven_simoracle": "C1_simoracle/traffic/raven_simoracle"}
METRICS = ("Delta_group", "Delta_c_s")
BOOT_DRAWS, BOOT_SEED = 10000, 20261007
T_LO, T_HI = 2.144786687917804, 0.8680547815574207     # t_{0.975,14}, t_{0.80,14}


def jdump(o, p: pathlib.Path) -> None:
    p.parent.mkdir(parents=True, exist_ok=True)
    p.write_text(json.dumps(o, indent=2, sort_keys=True, default=str) + "\n", encoding="utf-8")


def blocked(reason: str, detail: str = "") -> int:
    OUT.mkdir(parents=True, exist_ok=True)
    (OUT / "TS1_BLOCKED.md").write_text(
        f"# TS1 BLOCKED\n\n{datetime.now(timezone.utc).isoformat()}\n\n## Reason\n\n{reason}\n\n"
        f"## Detail\n\n{detail}\n", encoding="utf-8")
    print("BLOCKED:", reason)
    return 2


def main() -> int:
    OUT.mkdir(parents=True, exist_ok=True)
    (OUT / "tables").mkdir(parents=True, exist_ok=True)

    # ---- step 1: TE1 state check ----
    v = json.loads((TE1 / "TE1_VERDICT.json").read_text(encoding="utf-8"))
    ok = v.get("verdict") == "NO-GO-H" and v.get("n_analysis") == 15
    print(f"TE1_VERDICT.json: verdict={v.get('verdict')!r} n_analysis={v.get('n_analysis')!r} -> "
          f"{'OK' if ok else 'STOP'}")
    if not ok:
        return blocked("TE1_VERDICT.json is not in the required state",
                       json.dumps({"verdict": v.get("verdict"), "n_analysis": v.get("n_analysis")}))

    # ---- step 2: read the 30 files ----
    rows, seen_appl = [], set()
    for seed in SEEDS:
        rec = {"seed": seed}
        for arm, rel in ARM_DIRS.items():
            p = TE1 / "runs" / rel / ("seed%d" % seed) / "final_metrics.json"
            rec[f"file_{arm}"] = p.relative_to(ROOT).as_posix()
            rec[f"file_exists_{arm}"] = p.is_file()
            fm = json.loads(p.read_text(encoding="utf-8")) if p.is_file() else {}
            for m in METRICS:
                rec[f"{m}_{arm}"] = fm.get(m)
                rec[f"{m}_applicability_{arm}"] = fm.get(f"{m}_applicability")
                seen_appl.add(str(fm.get(f"{m}_applicability")))
            rec[f"_fm_keys_{arm}"] = sorted(fm.keys())
        rows.append(rec)

    # ---- step 3: D per metric ----
    for m in METRICS:
        inc, Ds = [], []
        for r in rows:
            fa, sa = r[f"{m}_applicability_fedavg_window"], r[f"{m}_applicability_raven_simoracle"]
            fv, sv = r[f"{m}_fedavg_window"], r[f"{m}_raven_simoracle"]
            good = (fa == "APPLICABLE" and sa == "APPLICABLE"
                    and isinstance(fv, (int, float)) and isinstance(sv, (int, float))
                    and math.isfinite(float(fv)) and math.isfinite(float(sv)))
            r[f"D_{m}"] = (float(fv) - float(sv)) if good else None
            r[f"included_{m}"] = bool(good)
            if good:
                inc.append(r["seed"])
                Ds.append(r[f"D_{m}"])
        rows_by_metric_ok = inc

        n = len(Ds)
        summary = {"n": n, "n_missing": len(SEEDS) - n,
                   "missing_seeds": [s for s in SEEDS if s not in inc],
                   "included_seeds": inc}
        if n != len(SEEDS):
            summary.update({"label": "INCOMPLETE", "mean": None, "sd": None,
                            "bootstrap_interval": None, "MDE80": None,
                            "note": "section 3: any missing pair makes this metric INCOMPLETE; the "
                                    "complete pairs are listed but not summarized into a separation "
                                    "label"})
        else:
            D = np.asarray(Ds, dtype=np.float64)
            mean, sd = float(D.mean()), float(D.std(ddof=1))
            rng = np.random.default_rng(BOOT_SEED)
            boot = np.asarray([float(np.mean(rng.choice(D, size=n, replace=True)))
                               for _ in range(BOOT_DRAWS)])
            lo, hi = (float(x) for x in np.percentile(boot, [2.5, 97.5]))
            mde = (T_LO + T_HI) * sd / math.sqrt(n)
            label = ("SEPARATED-ORACLE" if lo > 0 else
                     "SEPARATED-FEDAVG" if hi < 0 else "NOT-SEPARATED")
            summary.update({"mean": mean, "sd": sd,
                            "bootstrap_interval": {"draws": BOOT_DRAWS, "rng": BOOT_SEED,
                                                   "lower": lo, "upper": hi},
                            "MDE80": mde, "label": label,
                            "label_rule": "interval entirely above 0 -> SEPARATED-ORACLE; entirely "
                                          "below 0 -> SEPARATED-FEDAVG; contains 0 -> NOT-SEPARATED"})
        summary["applicability_strings_seen"] = sorted(seen_appl)
        summary["field_present"] = {m: all(r[f"{m}_applicability_fedavg_window"] is not None
                                           or r[f"{m}_applicability_raven_simoracle"] is not None
                                           for r in rows) for m in METRICS}
        if m == METRICS[0]:
            first = summary
        else:
            second = summary

    # ---- write the pair table ----
    fields = ["seed", "included_Delta_group", "included_Delta_c_s"]
    for m in METRICS:
        fields += [f"{m}_fedavg_window", f"{m}_applicability_fedavg_window",
                   f"{m}_raven_simoracle", f"{m}_applicability_raven_simoracle", f"D_{m}"]
    fields += ["file_fedavg_window", "file_raven_simoracle"]
    with (OUT / "tables/TS1_PAIRS.csv").open("w", newline="", encoding="utf-8") as f:
        w = csv.DictWriter(f, fieldnames=fields, extrasaction="ignore")
        w.writeheader()
        w.writerows(rows)

    summary_all = {"created_utc": datetime.now(timezone.utc).isoformat(),
                   "instruction_sha256": __import__("hashlib").sha256(
                       (ROOT / "ccfa-review-reports/"
                        "raven-mcs-traffic-struct-readout-execution-prompt.md").read_bytes()).hexdigest(),
                   "analysis_set": {"block": "NSW-Traffic", "seeds": [SEEDS[0], SEEDS[-1]],
                                    "n_seeds": len(SEEDS), "arms": list(ARM_DIRS)},
                   "te1_verdict_at_read": {"verdict": v.get("verdict"), "n_analysis": v.get("n_analysis")},
                   "metrics": {METRICS[0]: first, METRICS[1]: second},
                   "not_claimed": ["TE1 is not reopened and RMSE_mu is not re-scored",
                                   "no transfer claim from the frozen-server-step tables",
                                   "these 15 seeds are not combined with any other seed",
                                   "a separated contrast would be a property of this pipeline and "
                                   "these two arms, not a deployment decision and not E1"]}
    jdump(summary_all, OUT / "TS1_SUMMARY.json")

    # ---- report ----
    L = ["# TS1: structural readout from the TE1 confirm runs", "",
         f"- Instruction: `ccfa-review-reports/raven-mcs-traffic-struct-readout-execution-prompt.md`, "
         f"sha256 `{summary_all['instruction_sha256']}`",
         f"- TE1 state at read: verdict `{v.get('verdict')}`, `n_analysis = {v.get('n_analysis')}`",
         f"- Analysis set: NSW-Traffic, TE1 confirm seeds {SEEDS[0]}-{SEEDS[-1]}, arms "
         f"`C1_fedavg/traffic/fedavg_window` and `C1_simoracle/traffic/raven_simoracle`",
         "- Both stored metrics are mismatches; a smaller value is the better arm; "
         "`D_s(m) = m(fedavg, s) - m(raven_simoracle, s)`, so positive D favours the oracle-margin arm.",
         "", "## Labels", "",
         "| metric | n | n_missing | mean D | sd D | bootstrap 95% | MDE80 | label |",
         "|---|---:|---:|---:|---:|---|---:|---|"]
    for m in METRICS:
        s = summary_all["metrics"][m]
        if s["label"] == "INCOMPLETE":
            L.append(f"| `{m}` | {s['n']} | {s['n_missing']} | - | - | - | - | **INCOMPLETE** |")
        else:
            b = s["bootstrap_interval"]
            L.append(f"| `{m}` | {s['n']} | {s['n_missing']} | {s['mean']:.6f} | {s['sd']:.6f} | "
                     f"[{b['lower']:.6f}, {b['upper']:.6f}] | {s['MDE80']:.6f} | **{s['label']}** |")
    L += ["", f"Applicability strings seen across the 30 files: "
              f"`{first['applicability_strings_seen']}`.", ""]
    miss = {m: summary_all["metrics"][m]["missing_seeds"] for m in METRICS
            if summary_all["metrics"][m]["n_missing"]}
    L += ["## Missing pairs", "",
          ("None: every one of the 15 pairs carried both fields as `APPLICABLE` with finite values "
           "for both metrics." if not miss else json.dumps(miss)), "",
          "## What this round does not claim", ""]
    L += [f"- {x}" for x in summary_all["not_claimed"]]
    L += [""]
    (OUT / "TS1_REPORT.md").write_text("\n".join(L), encoding="utf-8")

    for m in METRICS:
        s = summary_all["metrics"][m]
        print(f"  {m:<12} n={s['n']} missing={s['n_missing']} "
              + (f"mean={s['mean']:+.6f} sd={s['sd']:.6f} CI=[{s['bootstrap_interval']['lower']:+.6f},"
                 f"{s['bootstrap_interval']['upper']:+.6f}] MDE80={s['MDE80']:.6f} -> {s['label']}"
                 if s["label"] != "INCOMPLETE" else "-> INCOMPLETE"))
    print("applicability strings seen:", first["applicability_strings_seen"])
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
