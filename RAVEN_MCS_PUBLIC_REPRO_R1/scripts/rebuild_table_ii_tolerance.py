"""Recompute the descriptive +0.5% mean-relative point-estimate tolerance.

This check has no coverage guarantee and is not a formal hypothesis test.
Does not retrain. Run from the bundle root:

    python scripts/rebuild_table_ii_tolerance.py
"""
from __future__ import annotations

import csv
import sys
from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]
PER_SEED = ROOT / "tables" / "TABLE_II_WORSTGROUP_PER_SEED.csv"
TDRIVE = ROOT / "tdrive" / "TD_R_E3.csv"

TEST_SEEDS = set(range(30011, 30021))
TDRIVE_SEEDS = set(range(30001, 30011))

# Paper SCD assignment: Design on iff phi=0.
SCD = {
    "sensorscope": "raven",
    "uair": "raven_wo_design",
}

PAPER = {
    ("uair", "fedau_window"): 0.48,
    ("uair", "obsuse_window"): 0.44,
    ("tdrive", "fedau_window"): 2.39,
    ("tdrive", "obsuse_window"): 2.43,
}


def load_rows(path: Path) -> list[dict[str, str]]:
    with path.open(encoding="utf-8", newline="") as f:
        return list(csv.DictReader(f))


def mean_rel_pct(scd: dict[int, float], base: dict[int, float]) -> float:
    keys = sorted(set(scd) & set(base))
    if not keys:
        raise SystemExit("no paired seeds")
    return sum((scd[s] - base[s]) / base[s] * 100.0 for s in keys) / len(keys)


def by_seed(rows: list[dict], dataset: str, method: str, seeds: set[int], col: str) -> dict[int, float]:
    out = {}
    for r in rows:
        if r["dataset"] != dataset or r["method"] != method:
            continue
        seed = int(r["seed"])
        if seed not in seeds:
            continue
        out[seed] = float(r[col])
    return out


def main() -> int:
    per = load_rows(PER_SEED)
    td = load_rows(TDRIVE)
    bad = 0

    print("block\tdataset\tcomparator\tmean_rel_pct\tpaper\twithin_0p5pct_point_tolerance")
    all_seeds = set(range(30001, 30021))
    for ds in ("sensorscope", "uair"):
        scd_m = SCD[ds]
        scd = by_seed(per, ds, scd_m, TEST_SEEDS, "WorstGroupRMSE")
        for base in ("fedau_window", "obsuse_window"):
            b = by_seed(per, ds, base, TEST_SEEDS, "WorstGroupRMSE")
            rel = mean_rel_pct(scd, b)
            paper = PAPER.get((ds, base))
            shown = round(rel, 2)
            within = rel <= 0.5 + 1e-12
            paper_s = "" if paper is None else f"{paper:.2f}"
            print(
                f"TableII_TEST\t{ds}\t{base}\t{rel:.6f}\t{paper_s}\t{within}"
            )
            if paper is not None and shown != paper:
                print(f"MISMATCH {ds} vs {base}: {shown} != {paper}", file=sys.stderr)
                bad += 1
        scd_all = by_seed(per, ds, scd_m, all_seeds, "WorstGroupRMSE")
        for base in ("fedau_window", "obsuse_window"):
            b = by_seed(per, ds, base, all_seeds, "WorstGroupRMSE")
            rel = mean_rel_pct(scd_all, b)
            print(
                f"TableII_ALL20\t{ds}\t{base}\t{rel:.6f}\t\t{rel <= 0.5 + 1e-12}"
            )

    scd_td = by_seed(td, "tdrive_speed", "raven_wo_design", TDRIVE_SEEDS, "WorstGroupRMSE")
    for base, paper in (("fedau_window", 2.39), ("obsuse_window", 2.43)):
        b = by_seed(td, "tdrive_speed", base, TDRIVE_SEEDS, "WorstGroupRMSE")
        rel = mean_rel_pct(scd_td, b)
        shown = round(rel, 2)
        within = rel <= 0.5 + 1e-12
        print(
            f"TDrive\ttdrive_speed\t{base}\t{rel:.6f}\t{paper:.2f}\t{within}"
        )
        if shown != paper:
            print(f"MISMATCH tdrive vs {base}: {shown} != {paper}", file=sys.stderr)
            bad += 1
        if within:
            print(f"UNEXPECTED T-Drive within tolerance vs {base}", file=sys.stderr)
            bad += 1

    if bad:
        print(f"FAIL mismatches={bad}", file=sys.stderr)
        return 1
    print("OK descriptive +0.5% point-estimate percentages matched")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
