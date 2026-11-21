"""S1' pre-flight: independently recompute the section-0 parameter-movement premises.

Read-only. Reconstructs the initial theta exactly (theta_init = model init under the run seed,
per window_runner.py L192 + e3/real_runner/runner.py L476 + models/common_ndmf.py L85-92) and
compares it against each frozen checkpoint.

Self-validating: the model module is content-identical to the frozen run commit b01db69e
(empty git diff), so a wrong reconstruction would show an O(1) difference rather than the
claimed sub-percent movement.
"""
from __future__ import annotations

import hashlib
import json
import math
import pathlib
import sys

import torch

ROOT = pathlib.Path(r"C:\Cursor\raven.mcs")
sys.path.insert(0, str(ROOT / "src"))

from raven_mcs.models.common_ndmf import deterministic_common_ndmf  # noqa: E402

BLOCKS = [
    ("sensorscope", ROOT / "artifacts/e3_formal_runs_r1/runs/sensorscope"),
    ("uair", ROOT / "artifacts/e3_formal_runs_r1/runs/uair"),
    ("traffic", ROOT / "artifacts/e3_formal_runs_r1/runs/traffic"),
]
E2_TRAFFIC = ROOT / "artifacts/e2_traffic_formal_runs_r1/runs"
SCREEN_SEEDS = [30001, 30002, 30003]

OUT = ROOT / "results_server_optimizer/round_v1"
OUT.mkdir(parents=True, exist_ok=True)


def sha256_file(p: pathlib.Path) -> str:
    h = hashlib.sha256()
    with p.open("rb") as f:
        for chunk in iter(lambda: f.read(1024 * 1024), b""):
            h.update(chunk)
    return h.hexdigest()


def load_theta(p: pathlib.Path):
    try:
        return torch.load(p, map_location="cpu", weights_only=False)
    except TypeError:
        return torch.load(p, map_location="cpu")


def measure(ckpt: pathlib.Path, seed: int):
    obj = load_theta(ckpt)
    if not isinstance(obj, dict):
        return None
    # federated arms store the raw theta dict; central_all / central_delivered wrap it
    wrapper = None
    if "state_dict" in obj and isinstance(obj["state_dict"], dict):
        wrapper = {k: v for k, v in obj.items() if k != "state_dict"}
        theta = obj["state_dict"]
    else:
        theta = obj
    keys = sorted(theta.keys())
    n_spatial = int(theta["spatial.weight"].shape[0])
    init = deterministic_common_ndmf(n_spatial, seed=seed).state_dict()
    tot_d2 = 0.0
    tot_i2 = 0.0
    per = {}
    for k in keys:
        a = init[k].detach().cpu().double()
        b = theta[k].detach().cpu().double()
        if a.shape != b.shape:
            raise ValueError(f"shape mismatch for {k}: init {tuple(a.shape)} vs ckpt {tuple(b.shape)}")
        d2 = float(((b - a) ** 2).sum())
        i2 = float((a ** 2).sum())
        per[k] = {
            "d_norm": math.sqrt(d2),
            "i_norm": math.sqrt(i2),
            "rel": (math.sqrt(d2) / math.sqrt(i2)) if i2 > 0 else float("nan"),
            "d2": d2,
        }
        tot_d2 += d2
        tot_i2 += i2
    overall = math.sqrt(tot_d2) / math.sqrt(tot_i2)
    for k in per:
        per[k]["share_of_d2"] = per[k]["d2"] / tot_d2 if tot_d2 > 0 else float("nan")
    top = sorted(per.items(), key=lambda kv: -kv[1]["d2"])[:4]
    return {
        "checkpoint_wrapper": wrapper,
        "n_spatial": n_spatial,
        "overall_rel_movement": overall,
        "overall_rel_movement_pct": 100.0 * overall,
        "tensors": {k: {kk: vv for kk, vv in v.items() if kk != "d2"} for k, v in per.items()},
        "top_movers": [
            {"tensor": k, "rel": v["rel"], "share_of_sq_movement": v["share_of_d2"]} for k, v in top
        ],
    }


records = []
skipped = []
for ds, base in BLOCKS:
    if not base.is_dir():
        skipped.append((ds, "block dir missing", str(base)))
        continue
    for arm_dir in sorted([p for p in base.iterdir() if p.is_dir()]):
        arm = arm_dir.name
        for seed in SCREEN_SEEDS:
            ck = arm_dir / f"seed{seed}" / "checkpoints" / "final.pt"
            if not ck.is_file():
                skipped.append((ds, arm, f"seed{seed}: no checkpoint"))
                continue
            m = measure(ck, seed)
            if m is None:
                skipped.append((ds, arm, f"seed{seed}: checkpoint is not a state dict"))
                continue
            man = arm_dir / f"seed{seed}" / "runtime_manifest.json"
            ck_hash_recorded = None
            if man.is_file():
                try:
                    ck_hash_recorded = json.loads(man.read_text(encoding="utf-8")).get("checkpoint_hash")
                except Exception:
                    pass
            rec = {
                "dataset": ds,
                "arm": arm,
                "seed": seed,
                "checkpoint": str(ck.relative_to(ROOT)).replace("\\", "/"),
                "checkpoint_sha256": sha256_file(ck),
                "checkpoint_hash_recorded": ck_hash_recorded,
                **m,
            }
            rec["checkpoint_hash_matches_file_sha256"] = (
                ck_hash_recorded == rec["checkpoint_sha256"] if ck_hash_recorded else None
            )
            records.append(rec)
            print(
                f"{ds:<12} {arm:<22} seed{seed}  overall={100*m['overall_rel_movement']:.4f}%  "
                f"top={m['top_movers'][0]['tensor']}({100*m['top_movers'][0]['share_of_sq_movement']:.1f}% of movement)"
            )

# --- what the prompt claims ---
print()
print("=== per (dataset, arm) mean over the 3 screen seeds ===")
summary = {}
for r in records:
    summary.setdefault((r["dataset"], r["arm"]), []).append(r["overall_rel_movement_pct"])
for (ds, arm), vals in sorted(summary.items()):
    print(f"  {ds:<12} {arm:<22} mean={sum(vals)/len(vals):.4f}%   n={len(vals)}")

print()
print("=== section-0 claims to test ===")
print("  fedavg_window / raven / local_hajek move 0.26% (SS), 0.40% (UA), 0.28% (Traffic)")
print("  mostly through the output bias head.8.bias")
print("  spatial embeddings move 0.01%")
print("  on SensorScope central_all moves head.0.weight by 12.2%")

print()
print("=== named-tensor detail (SS + traffic) ===")
for r in records:
    if r["seed"] != 30001:
        continue
    t = r["tensors"]
    print(f"  {r['dataset']:<12} {r['arm']:<22} spatial={100*t['spatial.weight']['rel']:.4f}%  "
          f"head.0.weight={100*t['head.0.weight']['rel']:.4f}%  "
          f"head.8.bias={100*t['head.8.bias']['rel']:.4f}%  "
          f"head.8.bias_share_of_movement={100*t['head.8.bias']['share_of_d2']:.2f}%")

if skipped:
    print()
    print(f"=== skipped ({len(skipped)}) ===")
    for s in skipped:
        print("  ", s)

(OUT / "PREFLIGHT_SECTION0.json").write_text(
    json.dumps(
        {
            "purpose": "independent recomputation of the S1' section-0 parameter-movement premises",
            "method": "theta_init = deterministic_common_ndmf(n_spatial, seed=run_seed).state_dict(); "
                      "theta_final = checkpoints/final.pt; movement = ||final-init||_2 / ||init||_2",
            "model_module_identical_to_frozen_commit": "b01db69e (empty git diff for src/raven_mcs/models/common_ndmf.py)",
            "screen_seeds": SCREEN_SEEDS,
            "records": records,
            "skipped": [list(map(str, s)) for s in skipped],
        },
        indent=2,
        sort_keys=True,
    ),
    encoding="utf-8",
)
print()
print("wrote", OUT / "PREFLIGHT_SECTION0.json")
