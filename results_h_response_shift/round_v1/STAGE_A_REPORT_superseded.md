# EXECUTION REPORT — response-shift headroom (scheme 2), Stage A

```text
Round     : results_h_response_shift/round_v1
Prereg    : PREREG.md sha256 5efb5abd185d1807a028ce046c2923548dcf44eb96270aeb0988a52793dfd92b
            (9323 bytes), recorded in MANIFEST.sha256 before any Stage A number was computed
Stage run : A only.  Stage B not run.
DECISION  : BLOCKED  (authorisation, not data — Stage A cleared the 0.02 bar on both datasets)
Writes    : results_h_response_shift/round_v1/ only
Untouched : src/, the manuscript, results_h_headroom/, every other results_* directory,
            artifacts/. No training, no trace regeneration, no git action.
```

## 1. Stage A result — the mass gap

`μ` is the frozen deployment-group target the E3 runner uses (220 groups on SensorScope,
144 on U-Air), read once per dataset through `production_target_bundle`. `π_arr(g)` is the share of
training atomic units in group `g`, among the units that appear in the trace.

| dataset | median ‖π_arr − μ‖₁ | median (risk-set variant) | median μ-mass on absent groups | bar | `stage_B` |
|---|---|---|---|---|---|
| SensorScope | **0.56750** | 0.43146 | 0.19707 | 0.02 | **allowed** |
| U-Air | **0.60147** | 0.43926 | 0.16352 | 0.02 | **allowed** |

Per-trace, `MASS_GAP.csv`:

| ds | seed | π_arr groups present | absent | μ-mass absent | L1 (observed) | L1 (risk set) | L1 all-groups |
|---|---|---|---|---|---|---|---|
| sensorscope | 30001 | 165 | 55 | 0.2164 | 0.5144 | 0.4113 | 0.7227 |
| sensorscope | 30002 | 180 | 40 | 0.1543 | 0.5759 | 0.4357 | 0.7221 |
| sensorscope | 30003 | 169 | 51 | 0.1971 | 0.5675 | 0.4315 | 0.7607 |
| sensorscope | 30004 | 173 | 47 | 0.1842 | 0.5765 | 0.4403 | 0.7538 |
| sensorscope | 30005 | 161 | 59 | 0.2264 | 0.5467 | 0.3979 | 0.7755 |
| uair | 30001 | 121 | 23 | 0.1635 | 0.6041 | 0.4323 | 0.7519 |
| uair | 30002 | 121 | 23 | 0.1604 | 0.6784 | 0.4958 | 0.8340 |
| uair | 30003 | 123 | 21 | 0.1478 | 0.5767 | 0.4662 | 0.7388 |
| uair | 30004 | 115 | 29 | 0.2023 | 0.5859 | 0.4393 | 0.7990 |
| uair | 30005 | 115 | 29 | 0.2044 | 0.6015 | 0.4371 | 0.8062 |

**The bar is cleared by 25–30× on both datasets**, so Stage A does not forbid either one. Whatever
else this round says, it is not "the arrival mass already matches `μ`".

## 2. Side facts Stage A produced, recorded because they bound what a group offset can do here

* **The group space is sparse in any single trace.** 40–59 of 220 SensorScope groups and 21–29 of
  144 U-Air groups receive no delivered unit at all across 100 (respectively 80) windows, carrying
  15.4–22.6 % of `μ`. That mass is unreachable by any reweighting of the trace, which is why the
  primary `L1` is computed on the groups that are present and the unreachable part is reported
  separately (`l1_all_groups` = 0.72–0.83).
* **Arrival is far from delivery.** The risk set holds ~2 400 units and ~1 890 units per trace but
  only ~915 and ~730 are observed, so "appears in the trace" is not the same set as "could have
  appeared". Both variants are reported (amendment A-H1); the primary uses arrival.
* **No split contamination.** `n_observed_not_in_train_split = 0` and
  `n_riskset_not_in_train_split = 0` on all five traces of both datasets: every unit in a trace is
  a `split == "train"` atomic unit, so `π_arr` is computed on training units only, as §1 requires.
* **Group inventory matched, not assumed.** `target_group` is a composite label
  (`s103::block2`), not an integer; the label→index map is taken from the dataset's own inventory and
  asserted equal to `n_groups_runtime` (220 / 144) before use. A mismatch raises instead of
  realigning. Windows per trace: 100 (SensorScope), 80 (U-Air); clients 8 on both.

## 3. Decision — mechanical application of §0, §1, §4

`H_DECISION.json`:

```text
stage_A : {sensorscope: allowed, uair: allowed}
stage_B_ran : false
decision    : BLOCKED
winning_cells : []
blocked_reason : instruction section 0/4 — Stage B requires the phrase "授权 H 测量";
                 the request accompanying this file does not contain it
```

`BLOCKED` is used in the sense §5's `decision` field allows, and it is chosen over `STOP` because
`STOP` would assert a measurement this round did not make. The distinction matters for the next
reader: **`STOP` means "the shift does not create headroom"; this round did not test that.**

`H_SEED_ROWS.csv` and `H_SUMMARY.csv` are written with their declared columns and **no rows**
(amendment A-H4), so that their emptiness cannot later be read as an executed grid with missing
values.

## 4. What would happen if Stage B were authorised

Nothing in Stage A blocks it: both datasets are `allowed`, the frozen traces, seeds and `c` grid are
already fixed in `PREREG.md`, and the driver check in §4.1 is specified against
`results_h_headroom/` for seed 30001. 80 runs (4 `c` values × 2 datasets × 2 arms × 5 seeds), or 40
per dataset if one had been forbidden. **The phrase required is `授权 H 测量`**; it is not in the
request that accompanied this file, and Stage A does not substitute for it.

## 5. Deviations and amendments (all declared before the hash)

```text
A-H1  "among units that appear in the trace" is read as the union of `observed_unit_ids` over all
      windows and clients (arrival), with the union of `risk_set_unit_ids` reported as a companion
      column. The two differ materially (e.g. 0.5675 vs 0.4315 median on SensorScope) and both are
      in MASS_GAP.csv; the primary is labelled in H_DECISION.json. Units outside the train split
      are counted and reported, never silently dropped.
A-H2  The 0.02 bar is applied to the L1 computed on the groups present in the trace, both sides
      renormalized (i). The zero-extended variant that includes mass on absent groups (ii) is
      reported as `l1_all_groups`; it measures an unrecoverable deficit rather than a reweighting
      opportunity, and it is not the quantity the bar tests. Both definitions were fixed before the
      numbers existed.
A-H3  `μ` is seed-independent and read once per dataset; no per-trace re-derivation.
A-H4  Stage B not executed; decision BLOCKED; Stage B CSVs written header-only.
```

## 6. Files

```text
PREREG.md              the frozen rule set + amendments, hashed first
MANIFEST.sha256        PREREG.md digest
MASS_GAP.csv           10 rows: 5 traces x 2 datasets, both L1 variants and the diagnostics
STAGE_A_DETAIL.json    group inventory, unit counts, per-dataset medians
H_SEED_ROWS.csv        header only (Stage B not run)
H_SUMMARY.csv          header only (Stage B not run)
H_DECISION.json        stage_A verdicts, decision BLOCKED, winning_cells []
EXECUTION_REPORT.md    this file
```
