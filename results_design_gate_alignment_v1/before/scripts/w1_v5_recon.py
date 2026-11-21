"""W1 round v5 - structural reconnaissance only (no A1/A2/A3 statistics).

Read-only.  Prints ASCII only.  Reports dataset/trace structure needed to freeze
PREREG.md: test-unit counts, fine-group counts, four-block partition, per-run
window counts and per-window client counts, and the presence of checkpoints.
"""
from __future__ import annotations

import json
import pathlib
import sys
from collections import Counter

import numpy as np

ROOT = pathlib.Path(__file__).resolve().parents[1]
sys.path.insert(0, str(ROOT / "src"))
sys.path.insert(0, str(ROOT / "scripts"))

from raven_mcs.data.target import RepeatableTimeOfDayMapper            # noqa: E402
from raven_mcs.e3.canary.dataset_load import load_paper_dataset       # noqa: E402
from raven_mcs.e3.target_pair.target_wiring import production_target_bundle  # noqa: E402

E3 = ROOT / "artifacts/e3_formal_runs_r1/runs"
V4T = ROOT / "results_w1_ladder/round_v4/train/v4/C0_frozen"
ARMS = ("uniform_window", "proj_beta", "proj_beta_debt")
FROZEN = ("fedavg_window", "inst_cal", "raven")
SEEDS = list(range(30001, 30021))


def block_of(label: str) -> int:
    for part in str(label).split("::"):
        if part.startswith("block"):
            return int(part[5:])
    raise ValueError(label)


def main() -> None:
    for ds_name in ("sensorscope", "uair"):
        ds = load_paper_dataset(ROOT, ds_name)
        bundle = production_target_bundle(root=ROOT, dataset_name=ds_name, dataset=ds)
        mu = np.asarray(bundle["mu"], dtype=np.float64)
        gids = list(bundle["group_id_by_index"])
        test = ds.atomic_df[ds.atomic_df["split"] == "test"].copy()
        blocks = RepeatableTimeOfDayMapper().map(test).to_numpy(dtype=int)
        g2i = ds._target_group_str_to_int
        fine = [str(g) for g in test["target_group"].tolist()]
        parsed = np.asarray([block_of(g) for g in fine], dtype=int)
        print("== dataset %s" % ds_name)
        print("   n_spatial=%d  n_test_units=%d  n_fine_groups_artifact=%d  n_test_groups=%d"
              % (ds.num_spatial, len(test), len(gids), len(set(fine))))
        print("   blocks from RepeatableTimeOfDayMapper: %s"
              % dict(sorted(Counter(blocks.tolist()).items())))
        print("   blocks from group-string parse     : %s"
              % dict(sorted(Counter(parsed.tolist()).items())))
        print("   block partitions identical: %s" % bool(np.array_equal(blocks, parsed)))
        print("   group string examples: %s" % list(dict.fromkeys(fine))[:3])
        print("   head_tail: n_head=%d n_tail=%d" % (bundle["head_tail"]["n_head"],
                                                      bundle["head_tail"]["n_tail"]))
        print("   mu len=%d sum=%.12f n_zero=%d" % (len(mu), float(mu.sum()), int((mu == 0).sum())))
        print("   trace dir exists: %s"
              % (E3 / "eventtraces" / ds_name / "seed30001" / "training_eventtrace").is_dir())
    print()
    print("== per-run window/client structure (v4 train tree)")
    for ds_name in ("sensorscope", "uair"):
        for arm in ARMS:
            nw, ks, ck = [], Counter(), 0
            for seed in SEEDS:
                p = V4T / ds_name / arm / ("seed%d" % seed)
                wm = json.loads((p / "window_metrics.json").read_text(encoding="utf-8"))
                act = [w for w in wm if w.get("active")]
                nw.append(len(act))
                for w in act:
                    ks[len(w["active_clients"])] += 1
                if (p / "checkpoints" / "final.pt").is_file():
                    ck += 1
            print("   %-9s %-16s seeds=%d windows[min,max]=[%d,%d] K-hist=%s ckpt=%d"
                  % (ds_name, arm, len(nw), min(nw), max(nw), dict(sorted(ks.items())), ck))
    print()
    print("== frozen E3 tree (fedavg_window, inst_cal, raven)")
    for ds_name in ("sensorscope", "uair"):
        for arm in FROZEN:
            nw, ks, ck, fm = [], Counter(), 0, 0
            for seed in SEEDS:
                p = E3 / ds_name / arm / ("seed%d" % seed)
                if not (p / "final_metrics.json").is_file():
                    continue
                fm += 1
                wm = json.loads((p / "window_metrics.json").read_text(encoding="utf-8"))
                act = [w for w in wm if w.get("active")]
                nw.append(len(act))
                for w in act:
                    ks[len(w["active_clients"])] += 1
                if (p / "checkpoints" / "final.pt").is_file():
                    ck += 1
            print("   %-9s %-16s final_metrics=%d windows[min,max]=[%s,%s] K-hist=%s ckpt=%d"
                  % (ds_name, arm, fm,
                     min(nw) if nw else "-", max(nw) if nw else "-",
                     dict(sorted(ks.items())), ck))


if __name__ == "__main__":
    main()
