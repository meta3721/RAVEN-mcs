"""Evidence pack for the round-14 review: the frozen-vs-FedAdam contrast, the confound, and H.

Read-only. Output: results_server_optimizer/round_v1/REVIEW_EVIDENCE_PACK.json
"""
from __future__ import annotations

import csv
import json
import pathlib

ROOT = pathlib.Path(r"C:\Cursor\raven.mcs")
OUT = ROOT / "results_server_optimizer" / "round_v1"
BLOCKS = ("sensorscope", "uair", "traffic")
SEEDS = range(30001, 30006)


def mean(xs):
    xs = [x for x in xs if isinstance(x, (int, float))]
    return sum(xs) / len(xs) if xs else None


pack = {"purpose": "frozen-pipeline vs FedAdam contrast, and the optimizer confound", "blocks": {}}

grid = list(csv.DictReader((OUT / "tables" / "STAGE_A_GRID.csv").open(encoding="utf-8")))
cfg = json.loads((OUT / "S1P_FROZEN_CONFIG.json").read_text(encoding="utf-8"))
hjson = json.loads((OUT / "S1P_STAGE_C_H.json").read_text(encoding="utf-8"))["H"]

for b in BLOCKS:
    star = cfg["per_block"][b].get("eta_s_star")
    new_fed = mean([float(r["test_RMSE_mu"]) for r in grid
                    if r["block"] == b and r["eta_s"] == str(star) and r.get("test_RMSE_mu")])
    frozen_fed = mean([json.loads((ROOT / f"artifacts/e3_formal_runs_r1/runs/{b}/fedavg_window/seed{s}/final_metrics.json")
                                   .read_text(encoding="utf-8"))["RMSE_mu"] for s in SEEDS
                       if (ROOT / f"artifacts/e3_formal_runs_r1/runs/{b}/fedavg_window/seed{s}/final_metrics.json").is_file()])
    central = mean([json.loads((ROOT / f"artifacts/e3_formal_runs_r1/runs/{b}/central_delivered/seed{s}/final_metrics.json")
                                .read_text(encoding="utf-8"))["RMSE_mu"] for s in SEEDS
                    if (ROOT / f"artifacts/e3_formal_runs_r1/runs/{b}/central_delivered/seed{s}/final_metrics.json").is_file()])
    mov = {e: mean([float(r["overall_rel_movement"]) for r in grid
                    if r["block"] == b and r["eta_s"] == e and r.get("overall_rel_movement")])
           for e in ("0.001", "0.003", "0.01")}
    pack["blocks"][b] = {
        "eta_s_star": star,
        "fedavg_test_RMSE_mu_frozen": frozen_fed,
        "fedavg_test_RMSE_mu_FedAdam": new_fed,
        "relative_change_vs_frozen": (new_fed / frozen_fed - 1.0) if (new_fed and frozen_fed) else None,
        "central_delivered_test_RMSE_mu_frozen": central,
        "FedAdam_fedavg_vs_central_relative": (new_fed / central - 1.0) if (new_fed and central) else None,
        "frozen_fedavg_vs_central_relative": (frozen_fed / central - 1.0) if (frozen_fed and central) else None,
        "mean_overall_movement_by_eta_s": mov,
        "frozen_fedavg_movement_from_section0": None,
        "H": {k: hjson.get(b, {}).get(k) for k in
              ("mean_H", "boot_lo", "boot_hi", "MDE80_n5", "verdict")},
        "kr_clause_excluded_from_GO": (hjson.get(b, {}).get("kr_clause") or {}).get("excluded_from_GO"),
        "kr_le3_share": (hjson.get(b, {}).get("kr_clause") or {}).get("share_kr_le3"),
    }

# frozen movement from the section-0 preflight
pf = json.loads((OUT / "PREFLIGHT_SECTION0.json").read_text(encoding="utf-8"))
for r in pf["records"]:
    if r["arm"] == "fedavg_window" and r["seed"] == 30001:
        pack["blocks"][r["dataset"]]["frozen_fedavg_movement_from_section0"] = r["overall_rel_movement"]
    if r["arm"] in ("central_all", "central_delivered") and r["seed"] == 30001:
        pack["blocks"][r["dataset"]].setdefault("central_movement_by_arm", {})[r["arm"]] = {
            "overall": r["overall_rel_movement"],
            "head_0_weight": r["tensors"]["head.0.weight"]["rel"],
        }

pack["optimizer_asymmetry"] = {
    "federated_server_step": "theta <- theta - eta * sum_i alpha_i u_i, u_i = (theta_before - theta_after)/"
                             "(client_lr * local_steps); window_runner.py L1155-L1167, client.py L104-L107",
    "federated_effective_global_step": "one client-sized gradient step per window, independent of local_steps",
    "centralized_reference": "torch.optim.Adam(lr=1e-3) with local_steps = max(local_steps*10, 20) = 20 minibatch "
                             "steps of 32 units (central_real.py L106, L111-L117; runner.py central branch)",
    "consequence": "the paper's federated-vs-centralized statements compare two differently-optimized and both "
                   "severely undertrained models",
}
(OUT / "REVIEW_EVIDENCE_PACK.json").write_text(json.dumps(pack, indent=2, sort_keys=True, default=str) + "\n",
                                               encoding="utf-8")

for b, v in pack["blocks"].items():
    print(f"{b}:")
    print(f"   frozen fedavg      = {v['fedavg_test_RMSE_mu_frozen']}")
    print(f"   FedAdam fedavg     = {v['fedavg_test_RMSE_mu_FedAdam']}  ({100*v['relative_change_vs_frozen']:+.2f} % vs frozen)")
    print(f"   central_delivered  = {v['central_delivered_test_RMSE_mu_frozen']}")
    print(f"   FedAdam vs central = {100*v['FedAdam_fedavg_vs_central_relative']:+.2f} %")
    print(f"   frozen  vs central = {100*v['frozen_fedavg_vs_central_relative']:+.2f} %")
    print(f"   movement  frozen={100*(v['frozen_fedavg_movement_from_section0'] or 0):.3f} %  "
          f"FedAdam={ {k: round(100*x,3) for k,x in v['mean_overall_movement_by_eta_s'].items()} }")
    print(f"   H = {v['H']['mean_H']}  CI [{v['H']['boot_lo']}, {v['H']['boot_hi']}]  {v['H']['verdict']}")
print()
print("wrote", OUT / "REVIEW_EVIDENCE_PACK.json")
