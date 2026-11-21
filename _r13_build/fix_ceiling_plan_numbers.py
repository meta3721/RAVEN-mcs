"""Correct the plan's percentage table to the artifact-exact values (line-wrap-insensitive anchors)."""
from __future__ import annotations

import hashlib
import pathlib

P = pathlib.Path(
    r"C:\Cursor\raven.mcs\ccfa-review-reports\raven-mcs-ceiling-ladder-manuscript-execution-prompt.md")
raw = P.read_bytes()
print("before:", len(raw), "B  sha256", hashlib.sha256(raw).hexdigest()[:16])

# order matters: the longer string first, so the short one does not pre-empt it
FIXES = [
    (b"| `0.6322` | `+0.023` (interval `[+0.006, +0.041]`) |",
     b"| `0.6322` | `+0.022` (interval `[+0.005, +0.042]`) |"),
    (b"| `0.7746` | `+0.045` (interval `[+0.024, +0.070]`) |",
     b"| `0.7746` | `+0.045` (interval `[+0.024, +0.069]`) |"),
    (b"| **single region, `1.0000`** | **`+0.097` (interval `[+0.066, +0.131]`)** |",
     b"| **single region, `1.0000`** | **`+0.097` (interval `[+0.067, +0.130]`)** |"),
    (b"`[+0.066 %, +0.131 %]`", b"`[+0.067 %, +0.130 %]`"),
    (b"`+0.131 %`", b"`+0.130 %`"),
    (b"Source of every value: `results_traffic_e2/round_v1/TE2_STEP4_VERDICT.json` (rungs),",
     b"Source of every value: `results_traffic_e2/round_v1/TE2_STEP4_VERDICT.json` (rungs; each percentage"
     b" is `100 * mean_gap / control_mean` and each interval `100 * boot_lo|boot_hi / control_mean`,"
     b" computed from the artifact's own fields rather than from its rounded `pct_of_control`),"),
]
for old, new in FIXES:
    n = raw.count(old)
    print(f"  {n} x {old[:56].decode()!r}")
    assert n == 1, f"anchor count {n} for {old[:40]!r}"
    raw = raw.replace(old, new)

P.write_bytes(raw)
stale = sum(raw.count(b) for b in (b"+0.023", b"+0.006, +0.041", b"+0.024, +0.070",
                                   b"+0.066, +0.131", b"+0.131 %"))
print("after :", len(raw), "B  sha256", hashlib.sha256(raw).hexdigest()[:16],
      " stale tokens:", stale)
assert stale == 0
