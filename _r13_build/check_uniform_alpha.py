import json
import pathlib

ROOT = pathlib.Path(r"C:\Cursor\raven.mcs")
ARMS = [
    ("SensorScope Design ON ", ROOT / "artifacts/e3_formal_runs_r1/runs/sensorscope/raven"),
    ("U-Air       Design ON ", ROOT / "artifacts/e3_formal_runs_r1/runs/uair/raven"),
    ("U-Air       Design OFF", ROOT / "artifacts/e4_core_mechanism_ablation_r1/runs/uair/raven_wo_design"),
]

print("Checking the prior audit's F1 claim: for windows with K_r <= 3, are the RETURNED alphas exactly uniform?")
print()

for label, d in ARMS:
    le3 = 0
    exact = 0
    worst_dev = 0.0
    worst_where = None
    le3_viol = 0
    worst_l2_excess = 0.0
    worst_l2_where = None
    for s in sorted([p for p in d.iterdir() if p.is_dir()]):
        wm = s / "window_metrics.json"
        if not wm.is_file():
            continue
        for i, r in enumerate(json.loads(wm.read_text(encoding="utf-8"))):
            if not r.get("active"):
                continue
            k = r.get("a_r_size") if r.get("a_r_size") is not None else len(r.get("active_clients") or [])
            if k is None or k > 3:
                continue
            a = r.get("alpha")
            if not a:
                continue
            le3 += 1
            dev = max(abs(x - 1.0 / k) for x in a)
            if dev < 1e-12:
                exact += 1
            if dev > worst_dev:
                worst_dev = dev
                worst_where = (s.name, i, k, [round(x, 9) for x in a])
            l2 = sum(x * x for x in a)
            excess = l2 - 1.0 / k
            if excess > 1e-9:
                le3_viol += 1
            if excess > worst_l2_excess:
                worst_l2_excess = excess
                worst_l2_where = (s.name, i, k, l2)
    print(f"{label}")
    print(f"   windows with K_r<=3 and alpha present : {le3}")
    print(f"   exactly uniform (max dev < 1e-12)     : {exact}  ({100.0*exact/le3:.2f}%)")
    print(f"   windows not exactly uniform           : {le3-exact}")
    print(f"   worst |alpha_k - 1/K_r|               : {worst_dev:.6e}   at {worst_where}")
    print(f"   worst ||alpha||^2 - 1/K_r (excess)    : {worst_l2_excess:.6e}   at {worst_l2_where}")
    print(f"   windows with excess > 1e-9            : {le3_viol}")
    print()

print("Prior audit F1 claims: 1475 windows K_r<=3 on SS, 368 exactly uniform, max dev 9.17e-5,")
print("worst constraint excess +1.5e-8, solver acceptance gate <= 1e-7.")
