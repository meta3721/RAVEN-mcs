import json, pathlib
ROOT = pathlib.Path(".")
F = ROOT/"artifacts/e3_formal_runs_r1/runs/sensorscope"
N = ROOT/"results_active_set_repair/round_v1/repair/C0_frozen/sensorscope"
print(f"{'method':<26} {'field':<16} {'frozen':<20} {'rerun':<20} same?")
for m in ("fedavg_window", "raven_simoracle", "fedasync_window", "flamf_timealign_adapted", "debt_cal"):
    try:
        a = json.loads((F/m/"seed30001/runtime_manifest.json").read_text(encoding="utf-8"))
        b = json.loads((N/m/"seed30001/runtime_manifest.json").read_text(encoding="utf-8"))
    except FileNotFoundError: print(f"{m:<26} (missing)"); continue
    for f in ("EventTrace_hash","config_hash","metric_hash","checkpoint_hash"):
        same = "SAME" if a.get(f)==b.get(f) else "DIFF"
        print(f"{m:<26} {f:<16} {str(a.get(f))[:18]:<20} {str(b.get(f))[:18]:<20} {same}")
    print()
