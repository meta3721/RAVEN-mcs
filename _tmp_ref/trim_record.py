import pathlib, re
p = pathlib.Path("ccfa-review-reports/raven-mcs-metric-definition-diagnosis.md")
lines = p.read_text(encoding="utf-8").split("\n")

def find(pat, start=0):
    rx = re.compile(pat)
    for i in range(start, len(lines)):
        if rx.match(lines[i]):
            return i
    return -1

tomb_i2 = """## I.2 Tier 1 — correctness: closed 2026-09-27

**Closed.** The U-Air active-set defect was repaired under route A on 2026-09-27 and written into
the manuscript. The item anchors `N1`–`N7` are retained so that external citations still resolve;
their subjects and outcomes are in §2A below. Evidence lives in
`results_active_set_repair/round_v1/` (137-check verifier, manifest, and the independent review of
the review). There is no open Tier-1 correctness item in this record.
"""

tomb_2a = """## 2A. Correctness defect — CLOSED 2026-09-27

**Status: closed and implemented.** The U-Air training-active-set defect was repaired under route A
and written into the manuscript the same day. Sequencing and evidence are outside this record; the
anchors `N1`–`N7` are kept only so that earlier citations still resolve.

| anchor | subject | outcome |
|:--|:---|:---|
| `N1` | the 2026-08-11 runner dropped the 72 of 288 zero-target pairs for four no-Design methods, not one | rebuilt on the licensed set; 1600/1600 per-run active-set assertion for all four |
| `N2` | the stated win was measured against an unequal-delivery baseline | withdrawn; the manuscript now reports a tie against all six no-Design comparators |
| `N3` | the row mixed two frozen batches disagreeing at 3 of 20 seeds | resolved: the E3 tree is the single reproducible source (6/6 bit-exact); the public-repro CSV is the outlier |
| `N4` | `Local-Hájek` coincides with the frozen `FedAvg` | disclosed; now stated as coincidence with FedAvg restricted to the Design support |
| `N5` | the surviving claim | written: prediction and worst-group are ties, structure separates against five of six, Debt-Cal ties both |
| `N6` | the `raven` cell was the forced-Design row | anchor correction already in place since §3 T9 |
| `N7` | Table III's `RMSE_μ` column mixes metric scales across datasets, undisclosed | **implemented**: §VII-A now states the U-Air and NSW-Traffic standardization ($\\sigma=17.363$, $575.776$), that SensorScope is physical, and that ratio columns are scale-invariant |

Verification: `results_active_set_repair/round_v1/verify_report_claims.py` (137 checks, 139 with
`--deep`), `MANIFEST.sha256`, `EXPERIMENT_REPORT_FOR_VERIFICATION.md`,
`REVIEW_OF_REVIEW_20260927.md`.
"""

# --- §2A
h2a = find(r"^## 2A\.")
h3 = find(r"^## 3\.")
assert h2a > 0 and h3 > h2a, (h2a, h3)
lines[h2a:h3] = tomb_2a.split("\n") + [""]
print(f"§2A   : replaced lines {h2a+1}-{h3} ({h3-h2a} lines) with a {len(tomb_2a.splitlines())}-line tombstone")

# --- I.2
h12 = find(r"^## I\.2")
h13 = find(r"^## I\.3")
assert 0 < h12 < h13, (h12, h13)
lines[h12:h13] = tomb_i2.split("\n") + [""]
print(f"I.2   : replaced lines {h12+1}-{h13} ({h13-h12} lines) with a {len(tomb_i2.splitlines())}-line tombstone")

p.write_text("\n".join(lines), encoding="utf-8")
print(f"record now {len(lines)} lines (was 1281)")
