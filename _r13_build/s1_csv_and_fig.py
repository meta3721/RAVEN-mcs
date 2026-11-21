"""S1: substitute the certified theta RMSE_mu into the prediction-risk figure CSV, then
regenerate only fig4. Read-only inputs; no inference, no re-scoring."""
from __future__ import annotations

import csv
import hashlib
import pathlib
import sys

ROOT = pathlib.Path(r"C:\Cursor\raven.mcs")
PAPER = ROOT / "TO_OVERLEAF_paper_tmc_r1_clean"
CSV = PAPER / "figure_data/FIG_E3_E3_PREDICTION_RISK.csv"
C7 = ROOT / "results_seed_path_audit_r1/C7_E3_ARMS_THETA.csv"
AFFECTED = {"30007", "30016", "30018"}
# figure method name -> audit arm name (C7_E3_ARMS_THETA.csv)
MAP = {"FedAvg-Window": "fedavg_window", "FedAsync-Window": "fedasync_window",
       "TimeAlign-Agg": "flamf_timealign_adapted", "Debt-Cal": "debt_cal"}

theta = {}
for r in csv.DictReader(C7.open(encoding="utf-8")):
    theta[(r["arm"], r["seed"])] = r["RMSE_mu"]

raw = CSV.read_bytes()
pre = hashlib.sha256(raw).hexdigest()
crlf = raw.count(bytes([13, 10]))
nl = raw.count(bytes([10]))
eol = b"\r\n" if crlf == nl else b"\n"
lines = raw.split(eol)
header = lines[0].decode().split(",")
assert header[3] == "RMSE_mu", header
print("pre :", len(raw), "B  sha256", pre[:16], " eol", eol, " lines", len(lines))

changed = []
for i, ln in enumerate(lines):
    s = ln.decode("utf-8")
    if not s or s.startswith("dataset,"):
        continue
    f = s.split(",")
    if len(f) != len(header):
        continue
    if f[0] == "U-Air" and f[1] in MAP and f[2] in AFFECTED:
        key = (MAP[f[1]], f[2])
        new = theta[key]
        changed.append((f[1], f[2], f[3], new))
        f[3] = new
        lines[i] = ",".join(f).encode("utf-8")

print(f"  rows to change: {len(changed)} (expected 12)")
for m, s, old, new in changed:
    print(f"    {m:<16} seed {s}  {float(old):.6f} -> {float(new):.6f}")
assert len(changed) == 12, "unexpected number of rows"

out = eol.join(lines)
post = hashlib.sha256(out).hexdigest()
CSV.write_bytes(out)
print("post:", len(out), "B  sha256", post[:16], " eol preserved:", out.count(bytes([13, 10])) == crlf)

print("\n=== regenerating fig4 only ===")
sys.path.insert(0, str(PAPER))
import importlib
mf = importlib.import_module("make_figures")
print("  SRC =", mf.SRC)
print("  OUT =", mf.OUT)
before = {p.name: hashlib.sha256(p.read_bytes()).hexdigest()[:16]
          for p in (mf.OUT).glob("fig4_e3_prediction_risk.*")}
mf.fig4_prediction()
after = {p.name: hashlib.sha256(p.read_bytes()).hexdigest()[:16]
         for p in (mf.OUT).glob("fig4_e3_prediction_risk.*")}
for k in sorted(after):
    print(f"  {k:<32} {before.get(k, 'MISSING')} -> {after[k]}  "
          f"{'changed' if before.get(k) != after[k] else 'unchanged'}")
