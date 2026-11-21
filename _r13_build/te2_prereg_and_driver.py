"""TE2 step 2: build the re-weighted target artifact, verify it, freeze the pre-registration,
and produce the TE2 driver (a copy of the S1' driver with a target-injection hook)."""
from __future__ import annotations

import hashlib
import json
import pathlib
import shutil
import sys

import numpy as np

ROOT = pathlib.Path(r"C:\Cursor\raven.mcs")
OUT = ROOT / "results_traffic_e2/round_v1"
OUT.mkdir(parents=True, exist_ok=True)
sys.path.insert(0, str(ROOT / "src"))
sys.path.insert(0, str(ROOT / "results_server_optimizer/round_v1/driver"))

from raven_mcs.e3.canary.dataset_load import load_paper_dataset  # noqa: E402
from raven_mcs.e3.target_pair.target_wiring import freeze_fixture_target, align_mu_to_dataset  # noqa: E402
from raven_mcs.e3.stratum_seal.traffic_regions import load_frozen_traffic_station_regions  # noqa: E402

KAPPA = 5.0
SEEDS = list(range(30001, 30021))
ARMS = ["local_hajek", "inst_cal", "debt_cal", "raven_simoracle"]
CONTROL = "local_hajek"

ds = load_paper_dataset(ROOT, "traffic")
atomic = ds.atomic_df
art = freeze_fixture_target(atomic, dataset="traffic")
print("fixture artifact keys:", sorted(art.keys()))
print("  n_groups:", art["n_groups"], "len(mu):", len(art["mu"]),
      "head:", len(art["head_groups"]), "tail:", len(art["tail_groups"]))

mu, group_ids, g2i = align_mu_to_dataset(ds, art)
print(f"  aligned mu length={len(mu)}  group_id sample={list(group_ids)[:3]}")
print(f"  mu sum={float(np.sum(mu)):.6f}")

# group id -> station -> region, using the aligned group ids
station_to_region, rmeta = load_frozen_traffic_station_regions(ROOT)
code_station = {}
for c, sub in atomic.groupby("target_group", observed=True):
    sids = set(sub["spatial_id"].astype(str))
    code_station[str(c)] = sorted(sids)[0]
region_of_group = {}
unresolved = []
for gid in group_ids:
    st = code_station.get(str(gid))
    if st is None:
        unresolved.append(str(gid))
        continue
    region_of_group[str(gid)] = station_to_region.get(st)
print(f"  groups unresolved to a region: {len(unresolved)} {unresolved[:4]}")
assert not unresolved, "cannot map every aligned group id to a region; stopping as the design requires"

regions = sorted({r for r in region_of_group.values() if r})
mass1 = {r: float(sum(mu[i] for i, g in enumerate(group_ids) if region_of_group[str(g)] == r))
         for r in regions}
print("  frozen region mass (artifact path):", {k: round(v, 6) for k, v in mass1.items()})
prio = max(mass1, key=mass1.get)
assert prio == "region1", f"priority region {prio} != Phase 0's region1"
w = np.array([KAPPA if region_of_group[str(g)] == prio else 1.0 for g in group_ids])
mu5 = mu * w
mu5 = mu5 / mu5.sum()
mass5 = {r: float(sum(mu5[i] for i, g in enumerate(group_ids) if region_of_group[str(g)] == r))
         for r in regions}
print("  kappa=5 region mass (artifact path):", {k: round(v, 6) for k, v in mass5.items()})
print(f"  top-1 share = {max(mass5.values()):.4f}   (Phase 0 measured 0.6322 on the codes path)")

art5 = dict(art)
art5["mu"] = {str(g): float(mu5[i]) for i, g in enumerate(group_ids)}
art5["_artifact_path"] = "inline_fixture_freeze(kappa5_region1)"
# round-trip check: re-aligning the written artifact must reproduce the same weights
mu_rt, gid_rt, _ = align_mu_to_dataset(ds, art5)
assert list(gid_rt) == list(group_ids), "round-trip group order changed"
assert np.allclose(np.asarray(mu_rt, dtype=float), mu5, atol=1e-12), "round-trip weights differ"
mass_rt = {r: float(sum(mu_rt[i] for i, g in enumerate(gid_rt) if region_of_group[str(g)] == r))
           for r in regions}
assert abs(max(mass_rt.values()) - max(mass5.values())) < 1e-12, "round-trip top-1 share differs"
print(f"  round-trip check: weights and top-1 share reproduce exactly ({max(mass_rt.values()):.6f})")
art5["_artifact_sha256"] = hashlib.sha256(
    json.dumps({k: art5[k] for k in ("mu", "head_groups", "tail_groups", "n_groups")},
               sort_keys=True, default=str).encode()).hexdigest()
jpath = OUT / "TE2_TARGET_ARTIFACT_KAPPA5.json"
jpath.write_text(json.dumps(art5, indent=2), encoding="utf-8")

# ---- freeze the pre-registration ----
pre = {
    "round": "TE2", "block": "NSW-Traffic", "scenario": "complete_aligned",
    "frozen_protocol": {"local_steps": 2, "server_step": "frozen (no override, driver mode 'off')",
                        "n_groups": int(art["n_groups"])},
    "target_artifact": {"file": jpath.relative_to(ROOT).as_posix(),
                        "inline_sha256": art5["_artifact_sha256"],
                        "kappa": KAPPA, "priority_region": prio,
                        "priority_rule": "region holding the largest share of the frozen pre-outcome "
                                         "target mass at kappa=1; ties broken by ascending region id",
                        "tie_note": "region1/2/3 tie at 0.255814 under kappa=1; the tie-break rule "
                                    "above is part of the pre-registration and was fixed after Phase 0",
                        "region_mass_kappa1": mass1, "region_mass_kappa5": mass5},
    "arms": {"control": CONTROL, "treatment": ["inst_cal", "debt_cal"], "oracle_upper_bound":
             "raven_simoracle", "roles_from": "runner.py L498-L502 p2_methods"},
    "seeds": SEEDS,
    "primary_endpoint": "RMSE_mu under the concentrated target weights",
    "secondary_endpoints": ["WorstGroupRMSE", "Tail_RMSE", "Delta_group", "Delta_c-s"],
    "contrast": "D_s = RMSE_mu(local_hajek, s) - RMSE_mu(treatment, s), paired on seed",
    "decision_rule": "supported only if the bootstrap interval lies entirely favourable AND the mean "
                     "exceeds its own MDE80 AND the effect is at least 2 % of the control's "
                     "deployment-weighted error; every ladder cell is reported as measured",
    "bootstrap": {"draws": 10000, "rng": 20261007},
    "phase0": {"verdict": "CONTINUE", "caveat": "the sd measured in Phase 0 is a lower bound because "
                                                "those checkpoints were trained under the uniform target"},
    "frozen_utc": __import__("datetime").datetime.now(__import__("datetime").timezone.utc).isoformat(),
}
(OUT / "TE2_FROZEN_PREREG.json").write_text(json.dumps(pre, indent=2, sort_keys=True), encoding="utf-8")
print("\nfroze", (OUT / "TE2_FROZEN_PREREG.json").relative_to(ROOT).as_posix())

# ---- the TE2 driver: copy of the S1' driver + a target-injection hook ----
drv = OUT / "driver"
drv.mkdir(exist_ok=True)
src = ROOT / "results_server_optimizer/round_v1/driver/s1p_driver.py"
raw = src.read_bytes()
old_out = b'OUT = ROOT / "results_server_optimizer" / "round_v1"'
new_out = b'OUT = ROOT / "results_traffic_e2" / "round_v1"'
assert raw.count(old_out) == 1
raw = raw.replace(old_out, new_out)
hook = b"TARGET_ARTIFACT = None  # set by the TE2 round script; None = production target\n\n\n"
anchor = b"def run_complete("
assert raw.count(anchor) == 1
raw = raw.replace(anchor, hook + anchor)
call = b"            spatial_to_client=load_spatial_to_client(ROOT, block),"
assert raw.count(call) == 1
raw = raw.replace(call, call + b"\n            target_artifact=TARGET_ARTIFACT,")
(drv / "s1p_driver.py").write_bytes(raw)
print("wrote", (drv / "s1p_driver.py").relative_to(ROOT).as_posix(),
      f"({len(raw)} B, injection hook added)")
