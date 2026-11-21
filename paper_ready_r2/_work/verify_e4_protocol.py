"""R2 protocol verification (offline, read-only): can sealed E4 Holm p-values be
exactly reproduced from the 240 final valid cells with the frozen paired protocol?

Frozen protocol hypothesis (from R1 evidence):
- paired same-seed diffs: diff = ablation - full_RAVEN per (dataset, seed, metric)
- test: Wilcoxon signed-rank (two-sided), like E3_FORMAL_PAIRED_TESTS (test_status=WILCOXON)
- multiplicity: Holm over the 8 cells of each component family (2 datasets x 4 metrics)
- alpha=0.05
- effect size: mean(diff)/std(diff) (paired dz)
"""
import json
import sys

import numpy as np
import pandas as pd
from scipy import stats

ROOT = r"D:\Cursor\raven.mcs"
CELLS = pd.read_csv(ROOT + r"\paper_ready_r1\01_core_data\e4\E4_FINAL_VALID_EVIDENCE_240.csv")
SEALED = json.load(open(
    ROOT + r"\artifacts\e4_wo_inst_reference_penalty_final_correction_r1\E4_COMPONENT_CLAIM_MATRIX_FINAL_R3.json",
    encoding="utf-8"))

COMPONENT_OF = {
    "RAVEN-w/o-Design": "Design",
    "RAVEN-w/o-Obs": "Obs",
    "RAVEN-w/o-Use": "Use",
    "RAVEN-w/o-Inst": "Inst",
    "RAVEN-w/o-Debt": "Debt",
}
METRICS = ["Delta_group", "Delta_c_s", "RMSE_mu", "Tail_RMSE"]
DS_MAP = {"SensorScope": "SensorScope", "U-Air": "UAir"}

print("cells:", len(CELLS))
print("configs:", sorted(CELLS.configuration.unique()))
print("datasets:", sorted(CELLS.dataset.unique()))
print("seeds:", CELLS.seed.nunique())
print("wo_inst generations:", CELLS[CELLS.configuration == "RAVEN-w/o-Inst"].generation.unique())
print()

def holm(raw_ps):
    """Holm-Bonferroni adjusted p-values (step-down), min(1, raw*m) cumulative max."""
    n = len(raw_ps)
    order = np.argsort(raw_ps)
    adj = np.empty(n)
    prev = 0.0
    for rank, idx in enumerate(order):
        m_i = n - rank
        cand = min(1.0, raw_ps[idx] * m_i)
        val = max(prev, cand)
        prev = val
        adj[idx] = val
    return adj

mismatches = []
for method, comp in COMPONENT_OF.items():
    fam_raw = {}
    fam_cells = {}
    for ds in ["SensorScope", "U-Air"]:
        full = CELLS[(CELLS.dataset == ds) & (CELLS.configuration == "RAVEN-MCS")]
        abl = CELLS[(CELLS.dataset == ds) & (CELLS.configuration == method)]
        assert len(full) == 20 and len(abl) == 20, (ds, comp, len(full), len(abl))
        merged = full.merge(abl, on="seed", suffixes=("_f", "_a"))
        for m in METRICS:
            diffs = (merged[m + "_a"] - merged[m + "_f"]).to_numpy(dtype=float)
            if np.allclose(diffs, 0):
                p = 1.0
            else:
                # exact two-sided Wilcoxon signed-rank on non-zero diffs (scipy default)
                res = stats.wilcoxon(diffs, zero_method="wilcox", correction=False, alternative="two-sided")
                p = float(res.pvalue)
            fam_raw[(DS_MAP[ds] + "_" + m)] = p
            fam_cells[(DS_MAP[ds] + "_" + m)] = diffs

    keys = list(fam_raw.keys())
    adj = holm(np.array([fam_raw[k] for k in keys]))
    for k, holm_p, raw_p in zip(keys, adj, [fam_raw[k] for k in keys]):
        sealed_cell = SEALED[comp]["cells"].get(k)
        if sealed_cell is None:
            mismatches.append((comp, k, "MISSING_SEALED_CELL"))
            continue
        sealed_holm = sealed_cell["p_holm"]
        ok = abs(holm_p - sealed_holm) < 1e-12
        if not ok:
            mismatches.append((comp, k, "HOLM_MISMATCH", raw_p, holm_p, sealed_holm))
        # effect size check: mean/std
        d = fam_cells[k]
        es = d.mean() / d.std(ddof=1) if d.std(ddof=1) > 0 else 0.0
        sealed_es = sealed_cell["effect_size_paired"]
        if not np.isclose(es, sealed_es, rtol=1e-6, atol=1e-9):
            mismatches.append((comp, k, "ES_MISMATCH", es, sealed_es))

print("mismatches:", len(mismatches))
for mm in mismatches:
    print(mm)
