# CW blocked - the ceiling ladder does not fit the page allowance at the full scope

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
The concentration ladder of Section~\ref{subsec:ceiling} bounds,
at the original server step, what re-weighting inside this class could buy on
this block across the full range of target concentration, so the null above is
not an artefact of a nearly uniform target.
```

Extend the conclusion sentence ending `... at an $80\%$ minimum detectable effect of $5.80\%$.`:

```text
, while at the frozen server step the class's recoverable gain stays
at $+0.097\%$, below the $0.5\%$ bar, even when the whole deployment target is
concentrated on one region (Section~\ref{subsec:ceiling}).
```

## What this round did not do

No other content was cut; the title, abstract and contribution list are unchanged; no result tree or
frozen artifact was touched; no `v2` or `revised` copy of the manuscript exists. Each measurement applied
a variant in place and restored the file in a `finally` block whose assertion on the pre-edit hash passed
on every run.
