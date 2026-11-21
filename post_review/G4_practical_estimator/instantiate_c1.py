"""Instantiate G4 C1 status from the sealed G1 three-layer panel.

Does not claim tightness. Writes tables only under this folder.
"""

from __future__ import annotations

import csv
import json
from pathlib import Path

from lemmas import instantiate_from_g1_row

ROOT = Path(__file__).resolve().parents[2]
G1 = ROOT / "post_review/G1_propensity_design/tables/three_layer_panel.csv"
OUT = Path(__file__).resolve().parent
TAB = OUT / "tables"


def main() -> None:
    TAB.mkdir(parents=True, exist_ok=True)
    rows = list(csv.DictReader(G1.open(encoding="utf-8")))
    inst = [instantiate_from_g1_row(r) for r in rows]
    flat = []
    for item in inst:
        g = item["C1_times_Bmin_global_pi_min"]
        z = item["C1_times_Bmin_zeta_floor"]
        flat.append(
            {
                "dataset": item["dataset"],
                "a5_holds": item["a5_holds"],
                "frac_pi_tar_zero": item["frac_pi_tar_zero"],
                "pi_opp_min_global": item["pi_opp_min_global"],
                "pi_min_from_zeta_max": item["pi_min_from_zeta_max"],
                "p_true_min": item["p_true_min"],
                "clip_on_mean": item["clip_on_mean"],
                "ess_ratio_on_mean": item["ess_ratio_on_mean"],
                "mean_abs_a_on_minus_oracle": item["mean_abs_a_on_minus_oracle"],
                "C1_Bmin_global_defined": g["defined"],
                "C1_Bmin_global": g["C1"],
                "C1_Bmin_zeta_defined": z["defined"],
                "C1_Bmin_zeta": z["C1"],
                "C_pi_zeta": z["C_pi"],
                "C_p_zeta": z["C_p"],
                "C_q_zeta": z["C_q"],
                "C_clip_zeta": z["C_clip"],
            }
        )
    pd_ok = True
    try:
        import pandas as pd

        pd.DataFrame(flat).to_csv(TAB / "c1_instantiation.csv", index=False)
    except ImportError:
        pd_ok = False
        with (TAB / "c1_instantiation.csv").open("w", encoding="utf-8", newline="") as f:
            w = csv.DictWriter(f, fieldnames=list(flat[0]))
            w.writeheader()
            w.writerows(flat)
    (OUT / "C1_INSTANTIATION.json").write_text(json.dumps(inst, indent=2), encoding="utf-8")
    print(json.dumps({"n": len(flat), "pandas": pd_ok, "rows": flat}, indent=2))


if __name__ == "__main__":
    main()
