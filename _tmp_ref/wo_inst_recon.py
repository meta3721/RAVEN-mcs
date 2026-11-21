import json, csv, pathlib, statistics as st
c = json.loads(pathlib.Path("artifacts/e4_wo_inst_reference_penalty_final_correction_r1/E4_WO_INST_FINAL_CLAIM.json").read_text(encoding="utf-8"))
print("=== corrected wo_inst claim vs Table IV (main.tex 1948 / 1955) ===")
base = {"SensorScope_Delta_group":1.013943,"SensorScope_Delta_c_s":1.290318,"SensorScope_RMSE_mu":7.938893,
        "UAir_Delta_group":1.092362,"UAir_Delta_c_s":1.233390,"UAir_RMSE_mu":1.191114}
tab  = {"SensorScope_Delta_group":-0.260,"SensorScope_Delta_c_s":0.310,"SensorScope_RMSE_mu":-0.002,
        "UAir_Delta_group":-0.089,"UAir_Delta_c_s":-0.143,"UAir_RMSE_mu":0.131}
for k, v in c["cells"].items():
    if k not in base: continue
    pct = v["mean_paired_diff"]/base[k]*100
    ok = "MATCH" if abs(pct-tab[k]) < 0.002 else "differs"
    print(f"  {k:<26} mean_paired_diff={v['mean_paired_diff']:+.8f}  -> {pct:+.4f}%   Table IV {tab[k]:+7.3f}   {ok}   holm_p={v['p_holm']:.6g}")
print()
print("=== the corrected run artifact dir ===")
d = pathlib.Path("artifacts/e4_wo_inst_reference_penalty_final_correction_r1")
for p in sorted(d.iterdir())[:14]:
    print(f"  {p.name:<52} {p.stat().st_size:>8} B" + ("  DIR" if p.is_dir() else ""))
