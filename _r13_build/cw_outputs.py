"""W4 (corrected sources), then CW_GATES.md, CW_BLOCKED.md and CW_NUMBERS.json."""
from __future__ import annotations

import json
import pathlib

ROOT = pathlib.Path(r"C:\Cursor\raven.mcs")
OUT = ROOT / "results_paper_ceiling/round_v1"
OUT.mkdir(parents=True, exist_ok=True)

R2 = ROOT / "results_traffic_e2/round_v1"
V = json.loads((R2 / "TE2_STEP4_VERDICT.json").read_text(encoding="utf-8"))
P0 = json.loads((R2 / "TE2_PHASE0.json").read_text(encoding="utf-8"))
PRE = json.loads((R2 / "TE2_FROZEN_PREREG.json").read_text(encoding="utf-8"))
ladder = {r["rung"]: r for r in V["ceiling_ladder"]}
settings = {s["name"]: s for s in V["settings"]}


def rung(key):
    return next(r for k, r in ladder.items() if k.startswith(key))


def pct(r, field):
    return round(100.0 * r[field] / r["control_mean"], 3)


CHECKS = [
    ("+0.001", pct(rung("kappa=1"), "mean_gap"), "TE2_STEP4_VERDICT ceiling_ladder[kappa=1] 100*mean_gap/control_mean"),
    ("-0.010", pct(rung("kappa=1"), "boot_lo"), "…[kappa=1] 100*boot_lo/control_mean"),
    ("+0.015", pct(rung("kappa=1"), "boot_hi"), "…[kappa=1] 100*boot_hi/control_mean"),
    ("+0.022", pct(rung("kappa=5"), "mean_gap"), "…[kappa=5] 100*mean_gap/control_mean"),
    ("+0.045", pct(rung("kappa10"), "mean_gap"), "…[kappa10] 100*mean_gap/control_mean"),
    ("+0.097", pct(rung("single_region"), "mean_gap"), "…[single_region] 100*mean_gap/control_mean"),
    ("+0.067", pct(rung("single_region"), "boot_lo"), "…[single_region] 100*boot_lo/control_mean"),
    ("+0.130", pct(rung("single_region"), "boot_hi"), "…[single_region] 100*boot_hi/control_mean"),
    ("0.2558", round(max(P0["region_mass_frozen"].values()), 4), "TE2_PHASE0 region_mass_frozen max"),
    ("0.6322", round(max(PRE["target_artifact"]["region_mass_kappa5"].values()), 4),
     "TE2_FROZEN_PREREG target_artifact.region_mass_kappa5 max"),
    ("0.7746", settings["kappa10"]["top1"], "TE2_STEP4_VERDICT settings[kappa10].top1"),
    ("1.0000", settings["single_region"]["top1"], "TE2_STEP4_VERDICT settings[single_region].top1"),
]
rows, bad = [], []
print("=== W4 number traceability (corrected sources) ===")
for printed, derived, src in CHECKS:
    ok = abs(float(printed) - float(derived)) < 5e-4
    rows.append({"printed": printed, "derived": derived, "source": src, "match": ok})
    print(f"  {printed:>8}  derived {derived:>8}  {'OK' if ok else 'MISMATCH'}  {src}")
    if not ok:
        bad.append(printed)
assert not bad, f"W4 mismatches: {bad}"
(OUT / "CW_NUMBERS.json").write_text(json.dumps(
    {"rows": rows,
     "extra": {"0.5 %": "main.tex L2131-L2132, the ceiling section's own GO rule",
               "5.80 %": "results_traffic_e1/round_v1/TE1_VERDICT.json MDE80, already printed at L2246"},
     "internal_threshold_not_used": "the TE2 design's 2 % decision bar is an internal planning choice and "
                                    "appears nowhere in the manuscript",
     "correction_caught_by_this_gate": {
         "was": "0.2500 for the frozen rung's top-region share",
         "why_wrong": "0.2500 is the design-stage analytic value for four equal regions; the measured "
                      "frozen target gives region0 0.232558 and regions 1-3 0.255814, so the top share is "
                      "0.2558",
         "now": "0.2558, sourced from TE2_PHASE0.json region_mass_frozen",
         "found_by": "W4 before any manuscript write survived, so no incorrect number ever reached the "
                     "canonical file"}},
    indent=2, sort_keys=True) + "\n", encoding="utf-8")

GATES = """# CW gates - ceiling ladder into the manuscript

Instruction: `ccfa-review-reports/raven-mcs-ceiling-ladder-manuscript-execution-prompt.md`. Skill
`ccf-paper-writer` mode `draft`, with the `ccf-humanization` preflight. Verdict: **W2 FAIL; the round is
blocked and the manuscript is restored to its pre-edit state.** The other four gates pass.

## W0 - pre-edit state: PASS

- Pre-edit sha256 `3cc106ca4b6087d9d6a47d69936abf0cd95914b0285e1a86d3c938acb5ad161c`, 119922 B, 2345
  newlines, CRLF 0.
- All four anchors matched exactly once.
- Sign-off recorded: the user instructed `按你的方案执行论文编写` on 2026-10-10, approving the plan as
  written. The plan's open page-budget item resolves by the plan's own default: on 19 pages, stop and
  report rather than cut.

## W1 - byte integrity: PASS

- Full-scope variant `f55e49fd03a4987f8c0d6caf046987fce46693b784e2d7446a0b9868cfc74a03`, 121801 B
  (+1879 B). Reversing all four insertions recovers the pre-edit sha256 exactly; the CRLF count is
  unchanged.

## W2 - build: FAIL

Same command sequence throughout; `main.bbl` is present, so no bibtex run is needed and the counts are
faithful.

| variant | added bytes | `main.pdf` |
|---|---:|---:|
| pre-edit control | 0 | 18 |
| ceiling paragraph only | +1227 | **18** |
| ceiling paragraph + availability naming | +1407 | **18** |
| all four insertions | +1879 | **19** |

The allowance is a hard 18 pp. The substance fits; the overflow is caused by the last two insertions, the
limitations cross-reference and the conclusion clause, about 440 B between them. No other content was cut.

## W3 - prose: PASS

`check_prose_quality.py --scope paper`: 14972 words, em dashes **0/3**, only the pre-existing semicolon
advisory. None of the banned phrases occurs (`we acknowledge`, `it should be noted`, `while this is
encouraging`, `publication-ready`, `confirmed by`, `approved`).

## W4 - number traceability: PASS, and it caught a real error before any write survived

Twelve of twelve numbers recomputed from the artifacts match; see `CW_NUMBERS.json`. Two numbers come
from elsewhere by design: the `0.5 %` bar is the ceiling section's own GO rule (main.tex L2131-L2132) and
`5.80 %` is the TE1 detectable effect already printed at L2246. The TE2 design's internal `2 %` decision
bar appears nowhere in the manuscript.

**Caught:** the frozen rung's top-region share had been written as `0.2500`, which is the design-stage
analytic value for four equal regions. The measured frozen target gives region0 `0.232558` and regions 1
to 3 `0.255814`, so the share is `0.2558`. The value was corrected in both copies of the insertion text
and W4 now sources it from `TE2_PHASE0.json`. No incorrect number reached the canonical file.

## W5 - scope did not drift: PASS

| region | pre | post | identical |
|---|---|---|---|
| abstract | `8ad25984072ed33e` | `8ad25984072ed33e` | yes |
| title | `b917a3c614517ece` | `b917a3c614517ece` | yes |
| contribution list | `82c33423ed680a72` | `82c33423ed680a72` | yes |

The insertions contain zero em dashes.

## State of the manuscript

Restored byte-for-byte: `3CC106CA4B6087D9D6A47D69936ABF0CD95914B0285E1A86D3C938ACB5AD161C`, 119922 B,
18 pp. The tree was never left over budget. The full-scope variant is recorded by hash and its text is in
`CW_BLOCKED.md`.
"""
(OUT / "CW_GATES.md").write_text(GATES, encoding="utf-8")

BLOCKED = """# CW blocked - the ceiling ladder does not fit the page allowance at the full scope

## Blocking condition

The page allowance is a hard 18 pp. The four insertions the plan specifies total +1879 B and build to
**19 pages**. The plan's W2 says: on a 19-page `main.pdf`, write `CW_BLOCKED.md` and stop, without
exceeding the allowance and without cutting other content unapproved. The manuscript has been restored to
`3cc106ca4b6087d9d6a47d69936abf0cd95914b0285e1a86d3c938acb5ad161c`, 119922 B, 18 pp.

## What is not the problem

The substance fits, measured with the same build sequence:

| variant | `main.pdf` |
|---|---:|
| pre-edit control | 18 |
| **ceiling paragraph only** | **18** |
| **ceiling paragraph + availability naming** | **18** |
| all four insertions | 19 |

The overflow comes from the last two insertions: a cross-reference sentence in the limitations paragraph
and a clause in the conclusion, about 440 B between them.

## Three options, with cost and benefit

**Option A - the measured-fit scope (recommended).** Apply the ceiling paragraph and the availability
naming; drop the two cross-references. Verified at 18 pp with 0 errors and 0 Overfull. Evidence gains its
measurement and Reproducibility gains the named tree, which are the two axes this change was for. The
limitations paragraph would not point at the new paragraph and the conclusion would not carry the number.

**Option B - all four sites, ceiling paragraph compressed by about four lines.** The paragraph runs to
fourteen source lines and must keep all five required content items, so the realistic saving is two to
four lines; whether that is enough is untested and would need its own build. This is `compress` mode on
new text, not a cut of existing content.

**Option C - all four sites plus a cut elsewhere.** Requires the author to name the cut. The plan's
sign-off block asks for exactly this and it was left unnamed, so the plan's default applied.

## The two deferred insertions, verbatim

Append to the limitations sentence ending `... after the Adam replacement.`:

```text
The concentration ladder of Section~\\ref{subsec:ceiling} bounds,
at the original server step, what re-weighting inside this class could buy on
this block across the full range of target concentration, so the null above is
not an artefact of a nearly uniform target.
```

Extend the conclusion sentence ending `... at an $80\\%$ minimum detectable effect of $5.80\\%$.`:

```text
, while at the frozen server step the class's recoverable gain stays
at $+0.097\\%$, below the $0.5\\%$ bar, even when the whole deployment target is
concentrated on one region (Section~\\ref{subsec:ceiling}).
```

## What this round did not do

No other content was cut; the title, abstract and contribution list are unchanged; no result tree or
frozen artifact was touched; no `v2` or `revised` copy of the manuscript exists. Each measurement applied
a variant in place and restored the file in a `finally` block whose assertion on the pre-edit hash passed
on every run.
"""
(OUT / "CW_BLOCKED.md").write_text(BLOCKED, encoding="utf-8")
print("\nwrote:", ", ".join(sorted(p.name for p in OUT.rglob("*") if p.is_file())))
