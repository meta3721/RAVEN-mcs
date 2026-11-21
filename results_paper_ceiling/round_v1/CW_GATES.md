# CW gates - ceiling ladder into the manuscript

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
