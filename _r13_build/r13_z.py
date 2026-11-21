"""R1.3 adversarial audit - final quantities.

Z1  every seed directory present anywhere in results_server_optimizer/round_v1
Z2  the zero-predictor decomposition: how much of the reported test RMSE_mu is
    a constant and how much is prediction, per arm and seed.
ASCII only.
"""
import json, math, pathlib, re, collections
import numpy as np

ROOT = pathlib.Path(r"C:\Cursor\raven.mcs")
OUT = ROOT / "results_server_optimizer/round_v1"
BUILD = ROOT / "_r13_build"

print("### Z1  seeds present under results_server_optimizer/round_v1")
seeds = collections.Counter()
for p in OUT.rglob("seed*"):
    if p.is_dir():
        m = re.fullmatch(r"seed(\d+)", p.name)
        if m:
            seeds[int(m.group(1))] += 1
for s in sorted(seeds):
    print("  seed%-6d appears in %d directories" % (s, seeds[s]))
print("  seeds outside 30001-30005: %s" % (sorted(s for s in seeds if s not in range(30001, 30006)) or "NONE"))

a = json.loads((BUILD / "r13_a_constants.json").read_text())

print()
print("### Z2  decomposition: RMSE_mu vs the zero predictor and vs the best constant")
print("  gain_vs_zero = 1 - RMSE_mu(arm)/RMSE_mu(zero);  gain_vs_const = 1 - RMSE_mu(arm)/RMSE_mu(best const)")
groups = collections.defaultdict(list)
for src, d in (("new", a["new"]), ("frozen", a["frozen"])):
    for k, v in d.items():
        b = k.split("/")[1]
        groups[(b, k)].append((src, v))

summary = collections.defaultdict(list)
for (b, k), v in sorted(groups.items()):
    st = v[0][1]
    z = 1.0 - st["test_mu"] / st["zero"]
    c = 1.0 - st["test_mu"] / st["best_const_in_sample"]
    summary[(b, k.split("/")[0] if k.startswith("FROZEN") else k.split("/")[0])].append((z, c, st["test_mu"]))
    print("  %-40s test=%.5f  zero=%.5f  const=%.5f  gain_vs_zero=%+.3f%%  gain_vs_const=%+.3f%%"
          % (k, st["test_mu"], st["zero"], st["best_const_in_sample"], 100 * z, 100 * c))

print()
print("### Z2b means per block x family")
fam = collections.defaultdict(list)
for k, v in a["new"].items():
    b = k.split("/")[1]
    tag = k.split("/")[0]
    fam[(b, tag)].append(v)
for k, v in a["frozen"].items():
    b = k.split("/")[2]
    tag = k.split("/")[1]
    fam[(b, "FROZEN:" + tag)].append(v)
for (b, tag), vs in sorted(fam.items()):
    t = float(np.mean([x["test_mu"] for x in vs]))
    z = float(np.mean([x["zero"] for x in vs]))
    c = float(np.mean([x["best_const_in_sample"] for x in vs]))
    print("  %-11s %-24s n=%d mean_test=%.6f mean_zero=%.6f mean_bestconst=%.6f  vs_zero=%+.3f%%  vs_const=%+.3f%%"
          % (b, tag, len(vs), t, z, c, 100 * (1 - t / z), 100 * (1 - t / c)))
