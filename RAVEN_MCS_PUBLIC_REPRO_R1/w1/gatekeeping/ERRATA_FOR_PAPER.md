# ERRATA_FOR_PAPER — items only

Round: `results_gatekeeping/round_v1/` (Part A only). **No manuscript was edited.** This
file lists items a future manuscript revision should carry. Each item names the artefact
that evidences it. Nothing here is a request to change a registered margin, endpoint or
verdict; items marked *decision* are for the user, not for the round.

---

## E-A1-1 — `power_H2_at_delta` in `A1_DESCRIPTIVE.csv` is one power, not a curve

The column is power at `θ = 0` only (the non-inferiority null-side value). The `θ = δ/2`
and `θ = δ` values, `MDE₈₀` and the bootstrap variant are in `A1_POWER.csv`. Any text that
cites the column should say "power at θ = 0", or cite the power table.

Evidence: `PREREG.md` §5; `A1_DESCRIPTIVE.csv`; `A1_POWER.csv`.

## E-A1-2 — the City Scanner "n = 10 seeds" are 10 event traces, not 10 replicates of the DGP

All City Scanner statements in this round are statements about these 10 traces
(`CS_TRACE_MANIFEST.json`, seeds 32001–32010, 100 windows, 421 clients each). No trace
generator exists in the repository, so no additional independent trace can be produced.
Any City Scanner interval, p-value or power number should be described as conditional on
this trace set.

Evidence: `CS_TRACE_MANIFEST.json`; `A1_POWER.csv` (`n_traces = 10`); protocol §0 and §3.

## E-A1-3 — the City Scanner runs were not θ-re-scored, and the trigger's reach is unknown

`A1_DESCRIPTIVE` uses the frozen City Scanner numbers as published. The round-v5.1
θ-canonical rule was established on `{uair} × {30007, 30016, 30018}` because in those runs
the final window does not aggregate and the run-time metric reads the in-memory module
instead of the saved θ. Whether that failure mode can also fire in the City Scanner
pipeline (100 windows, frozen `CS_ACCEPTED.json` markers) was **not** established by this
round, and no re-score was applied or invented. This is an open item, not a claim that the
City Scanner numbers are wrong.

Evidence: `EXECUTION_REPORT.md` §2; `PREREG.md` §2; round_v5.1 report §2.1.

## E-A1-4 — `raven_wo_design` is not an A1 comparator on City Scanner

The A1 hierarchy fixes `fedavg_window` as the comparator. `raven_wo_design` appears in this
round only as the A1.2 within-trace proxy (§3.1 of the execution report). If a later
manuscript wants the Design-off contrast on City Scanner, it is the
`raven − raven_wo_design` row (+2.45 % mean, −0.22 % median, SD 13.0 %, 7/10 seeds lower,
protocol §0), which is a different question from A1 and carries no confirmation here.

Evidence: `EXECUTION_REPORT.md` §3.1; protocol §0.

## E-A1-5 — no `proj_beta` City Scanner row exists

The protocol lists arms `raven` and `proj_beta` for SensorScope/U-Air and `raven` for City
Scanner. No frozen City Scanner `proj_beta` runs exist in the inputs, and none may be
trained in Part A. No substitute arm was used to fill the cell.

Evidence: `A1_DESCRIPTIVE.csv` (5 rows); `PREREG.md` §2.

## E-A1-6 — H1 p-values sit on the exact signed-rank resolution floor

`H1_p = 9.537e-07` for all four SensorScope/U-Air chains and `9.766e-04` for City Scanner.
These are the smallest attainable one-sided values (`2^-n`: `2^-20` and `2^-10`) and mean
`p ≤ 9.54e-07` / `p ≤ 9.77e-04`, not measured magnitudes below them. Any table that prints
more digits or stars a smaller value would be wrong.

Evidence: `A1_DESCRIPTIVE.csv`; `EXECUTION_REPORT.md` §2.

## E-A1-7 — U-Air's A1 chains sit just under the preregistered 0.80 testability line

`power(θ = 0)` is 0.697 (`raven`) and 0.674 (`proj_beta`) at n = 20 with the observed
paired SDs, while `MDE₈₀` is *below* zero (−0.076 % and −0.093 %, against δ = 0.5 %). Under
the letter of the preregistered rule (`power ≥ 0.80`) U-Air's H2 is not "testable"; under
its intent (is δ inside the 80 %-power range?) it is. Both readings are reported, and the
U-Air H2 failures (upper bounds 1.09 × δ and 1.54 × δ) are informative either way. This
near-miss is a candidate for an explicit power clause in a future preregistration.

Evidence: `A1_POWER.csv`; `EXECUTION_REPORT.md` §3.

## E-A1-8 — City Scanner H2 is unreachable at δ_CS = 2 %, and that is a *result*, not a caveat

The declared margin δ_CS = 2 % was fixed before computation and is not revisited. The power
table shows the rule cannot reach 80 % power at any admissible within-trace variance, at
any `r ∈ {1, 3, 5}`: maximum power 0.153 (normal) / 0.176 (trace-cluster bootstrap) at
r = 5, and `MDE₈₀` between +6.0 % and +8.6 %. A City Scanner H2 non-rejection would
therefore be uninformative, and a *rejection* would require the arm to be several times
better than the margin. Any manuscript sentence of the form "RAVEN is non-inferior on City
Scanner" is currently unsupportable at this n, and the dropped-32005 sensitivity
(HL +0.59 %, upper bound +2.45 % vs δ_CS = 2 %) must not be promoted to primary to obtain
one.

Evidence: `A1_POWER.csv`; `A1_SENSITIVITY_NO32005.csv`; `EXECUTION_REPORT.md` §3.1.

## E-A1-9 — the seed-32005 sensitivity is a declared sensitivity, never primary

Removing trace 32005 halves the City Scanner paired SD (13.42 % → 6.74 %) and moves the
median paired relative difference to ≈ 0 (−0.05 %); the mean moves from +5.59 % to
+1.85 %. That is exactly why the exclusion is registered as sensitivity only. Any figure
or table that shows the no-32005 numbers must label them as sensitivity, and no confirmatory
statement may rest on them.

Evidence: `A1_SENSITIVITY_NO32005.csv`; `PREREG.md` §6.

## E-A1-10 — the θ-canonical values this round reads differ from round-v4 at the 4th significant digit

This round reads U-Air and SensorScope from `results_w1_ladder/round_v5_1/TRADEOFF_V51.csv`
(θ-canonical; 18 U-Air rows carry `source = theta_trigger`). SensorScope is numerically
unchanged (max |v5.1 − v4| = 1.8e-15, i.e. float noise). U-Air differs on 39 of 120 rows:
the 18 trigger rows move by up to **5.66e-02** in `RMSE_mu` (e.g. `("uair","raven",30018)`
1.181723 vs 1.125360), and the remaining moved rows by ~3e-04. The effect on the paired
relative contrast used here is small but not nil: mean relative difference
`raven − fedavg_window` +0.2639 % (v5.1) vs +0.2425 % (v4), and
`proj_beta − fedavg_window` +0.3929 % vs +0.3560 %. Any manuscript cell quoted from the v4
tables should be re-sourced; the v5 decision (R1 closed) is not reopened by this.
Verified in this round directly from both files (`A1_PROVENANCE.json` records both input
sha256).

Evidence: `results_w1_ladder/round_v5_1/TRADEOFF_V51.csv`; `results_w1_ladder/round_v4/TRADEOFF.csv`;
`results_w1_ladder/round_v5_1/ERRATA_FOR_PAPER.md` E-v51-4; `A1_PROVENANCE.json`.

## E-A1-11 — Part B was not authorized and its artefacts do not exist

`B0_REPRO.json`, `B0_SEED32005_PROBE.csv`, `C1_MAPS.json`, `C1_RUNS.csv`,
`C1_PRIMARY.json`, `C1_SECONDARY.csv`, `C1_A1_CHAINS.csv` and `C1_SENSITIVITY_NO32005.csv`
were not produced, because Part B requires the exact phrase `授权 C1 训练`, which was not
given. No training ran. The City Scanner within-trace variance in `A1_POWER.csv` is
therefore an explicitly labelled proxy (pilot arm-contrast scale 0.0980) reported as a
range, not a measurement; the moment B0-b exists it must replace that proxy everywhere.
The City Scanner seed-32005 row of protocol §0 (+39 %) is a single-run observation with no
seed-replicate evidence yet.

Evidence: `EXECUTION_REPORT.md` §4; `A1_POWER.csv` (`proxy_flag`, `proxy_status`);
`A1_PROVENANCE.json` (`cs_within_trace_proxy`).

## E-A1-12 — a confirmatory H2 statement on City Scanner needs new event traces, not more model seeds

Because the binding variance is between-trace (§3.1), no `r` fixes E-A1-8. Protocol §3
already flags that only a rebuilt trace generator could provide independence, and that
model-seed replicates on the existing 20 traces (SensorScope/U-Air) would inherit the same
traces and therefore not be independent of the descriptive analysis. This remains a user
decision and was not designed further in this round.

Evidence: `A1_POWER.csv`; protocol §3; `EXECUTION_REPORT.md` §4.

## E-A1-13 — the protocol's own §0 summary row for `raven − raven_wo_design` does not reproduce from the frozen tables

Protocol §0 prints `raven − raven_wo_design` (relative `RMSE_μ`) as "mean +2.45 %,
median **−0.22 %**, SD 13.0 %, **7/10** seeds where the first arm is lower". Computed this
round from `results_nodesign_supplement/round_v1/tables/cityscanner_seed_rows.csv` by
per-trace ratio `RMSE_μ(raven)/RMSE_μ(raven_wo_design) − 1`, the same row reads
**mean +2.368 %, median −0.625 %, SD 12.99 %, 8/10 seeds lower**. The absolute per-trace
values in that file are bit-identical to the frozen City Scanner table
(`results_c1_cityscanner/round_v1/tables/CS_E3.csv`, 200/200 cells, max |Δ| = 0), so the
difference is one of relative-difference convention, not of data.
No conclusion of this round depends on that row: it is not an A1 chain, and it is used only
as the A1.2 proxy, whose value (0.0980) is stated with its own definition. Any manuscript
text quoting the §0 numbers for this contrast should state the convention it used.

Evidence: `results_nodesign_supplement/round_v1/tables/cityscanner_seed_rows.csv`;
protocol §0; `A1_PROVENANCE.json` (`cs_within_trace_proxy`).

---
---

# ERRATA (Part B — C1 deletion mechanism, r = 3)

Items only; **no manuscript was edited**. Appended after the Part-A items E-A1-1 … E-A1-13.

## E-B-1 — bit-exactness of the City Scanner training path is thread-count dependent

With `torch.set_num_threads(1)` the rebuilt driver misses the frozen seed-32001 rows by up
to **4.2e-8** on `Delta_group` (4.0e-10 on `RMSE_mu`, 3.2e-10 on `Delta_c_s`); with the
default thread count of the frozen runs the reproduction is exact to the last bit (max |Δ| =
0.0 on all four endpoints, both arms). B0-a therefore passed only in the default
configuration, and **every** Part B run (including the reused-arm extra seeds that the
primary is paired against) was trained in that same default configuration, so no arm is
compared against a differently-reduced counterpart. Any future re-run of the City Scanner
block that changes `torch.set_num_threads`, `OMP_NUM_THREADS` or the machine's core count
should expect ~1e-8 relative drift on the structural endpoints and must re-run the B0-a gate
before it is compared with these rows.

Evidence: `B0_REPRO.json` (pass, max |Δ| = 0.0), `B0_REPRO__b0a_t1.json` (fail, 4.2e-8);
`C1_EXECUTION_LOG.md`.

## E-B-2 — the protocol's r = 3 run count is internally inconsistent (130 vs 150)

Protocol §2 B1 estimates "3 arms × 10 × r (+ 2 reused arms × 10 × (r − 1)) … at r = 3 it is
130 runs", but its own arm table marks **three** reused arms (`fedavg_window`,
`raven_wo_design`, `raven_ctrl` = frozen RAVEN). This round trained **150** new runs — the
extra 20 are the second extra model seed of `raven_ctrl`, without which the primary contrast
`raven_ctrl` vs `raven_ctrl_floor` would be unbalanced (r = 1 against r = 3). The change is
registered in `PREREG.md` AMENDMENT 1 before the first run and is a coverage increase only;
no map, margin, seed, contrast or endpoint was chosen after seeing a C1 `RMSE_μ`.

Evidence: protocol §2 B1; `PREREG.md` AMENDMENT 1 §A2; `C1_RUNS.csv` (180 rows: 150 new, 30
reused).

## E-B-3 — `raven_ctrl_floor` is not exactly region-matched to μ

Flooring every zero control key with π_floor and renormalizing — exactly as protocol §2 B1
defines the mechanism arm — also changes the map's region marginals, because the 812 zero
keys are not spread evenly over the four regions: region0 0.23732 → 0.23846, region1
0.47464 → 0.40386, region2 0.07081 → 0.08890, region3 0.21722 → 0.26878 (μ = the control
values). The primary contrast `raven_ctrl − raven_ctrl_floor` therefore isolates the removal
of deletion *plus* a within-region re-mix of at most ≈7 pp in region1, and not deletion
alone. No region re-matching was applied, because protocol §2 B1 defines the arm without
one; the deviation is reported next to the structural guardrail rather than silently
repaired. Any manuscript sentence that describes this contrast as "same tilt, only the
deletion differs" must carry this qualification.

Evidence: `C1_MAPS.json` (`checks.control_region_marginals`, `checks.floor_region_marginals`,
`arms.raven_ctrl_floor`); `EXECUTION_REPORT.md` §B.3, §B.5.

## E-B-4 — the M1/M2 arm maps are defined on the control key support, not on the raw map table

`MAPS_KEY_LEVEL.csv` is a 3568-row cross product (446 cells × 8 strata) of which only 1164
`(cell, stratum)` pairs exist in the atomic table. Rescaling M1/M2 within region on the raw
cross product leaves phantom keys carrying mass, so on the real support the region marginals
miss μ by up to 7.03 pp (M1) and 5.82 pp (M2) and the arms would not be region-matched. The
registered construction therefore restricts M1/M2 to the control map's 1164-key support and
rescales there, so all six arms share the same key support and the same region marginals μ.
The realized deleted shares are unaffected (the zero pattern on the real support is the same
in both variants): ρ = 1.0077 % (M1) and 0.9848 % (M2), against 14.345 % for the control map.

Evidence: `C1_MAPS.json` (`map_meta.*.rejected_alternative`); `PREREG.md` AMENDMENT 1 §A2.1.

## E-B-5 — Δ_c-s is not comparable across arms with different π^tar

`Delta_c_s` is `Σ|Π̂_{k,s} − π^tar_{k,s}|` **against each run's own π^tar**. The guardrail
row in `C1_PRIMARY.json` therefore compares a distance-to-its-own-target
(`raven_ctrl_floor` 0.789, all-positive flattened target) with a distance-to-a-different-
target (`raven_ctrl` 0.568, 812-zero target), and the M arms sit at 1.41 / 1.43 against
their ACS/311 shapes. Directional statements such as "the floor arm is worse on Δ_c-s" are
not licensed by these numbers alone. `Δ_group = ‖ω̂ − μ‖₁` does not have this problem,
because μ is the same frozen vector for every arm.

Evidence: `src/raven_mcs/metrics/distribution.py`; `C1_PRIMARY.json`
(`structural_guardrail.Delta_c_s_mean`); `EXECUTION_REPORT.md` §B.5.

## E-B-6 — the primary `H_mech` is inconclusive, and the design is underpowered at δ_CS

Primary: HL = −0.019 %, percentile trace-cluster CI [−1.893 %, +12.275 %], Wilcoxon
p = 0.9219, n = 10 traces, r = 3. The CI is neither above 0 nor inside ±δ_CS under **any** of
the three interval types, so the mechanical reading is "inconclusive" and the B3 table
licenses **no mechanism claim**. The power of the H2-style rule at δ_CS = 2 % and θ = 0 is
0.151 (sd(`d_t`) = 10.30 %, SE = 3.26 %): by the A1 §5 testability rule the City Scanner
deletion question is *not testable* at this n, and no power statement should be read into
the primary. Removing trace 32005 gives HL −0.558 %, CI [−2.318 %, +3.528 %] — still
inconclusive under the registered rule, missing the ±2 % region by 0.32 pp on the lower
bound.

Evidence: `C1_PRIMARY.json`; `C1_SENSITIVITY_NO32005.csv`; `EXECUTION_REPORT.md` §B.5, §B.9,
§B.10.

## E-B-7 — the +39 % seed-32005 anomaly is trace-driven, not a training-instability outlier

Trace 32005 with five model seeds {32005, 132005, 232005, 332005, 432005} gives
`RMSE_μ(raven)`/`RMSE_μ(raven_wo_design) − 1` = +38.46 %, +28.73 %, +24.45 %, +35.43 %,
+30.78 % (mean +31.57 %, SD 5.52 pp): **all five** model seeds reproduce the gap. The B3 row
that would have allowed describing that seed as a training-instability outlier therefore does
not apply, and the earlier Part-A reading of seed 32005 as "one seed" must not be turned into
"one unlucky model seed" in the manuscript: the trace itself is the unit that behaves
differently, and under r = 3 replication the trace is still the only independent unit
available.

Evidence: `B0_SEED32005_PROBE.csv`; `B0_SEED32005_PROBE.json`; `EXECUTION_REPORT.md` §B.2.

## E-B-8 — the confirmatory chains stop at H1; H2 is not established for any new arm

For `raven_ctrl_floor`, `raven_M1mu` and `raven_M2mu` vs `fedavg_window`: H1 is rejected on
all three (p = 9.77e-04, `Δ_group` lower on 10/10 traces), but H2 is **not** rejected —
the one-sided 95 % Wilcoxon-inverted upper bound is +3.83 %, +4.14 % and +8.15 % against
δ_CS = 2 %, and H3 is therefore never tested (registered string "not tested (H2 not
rejected)"). The only confirmatory statements this round can support are structural
(`Δ_group`), not predictive; in particular nothing here establishes that the floored or the
exogenous-support arms are non-inferior to `fedavg_window` on `RMSE_μ`.

Evidence: `C1_A1_CHAINS.csv`; `EXECUTION_REPORT.md` §B.7.

## E-B-9 — the Part-A `MANIFEST.sha256` registration-timeline block is duplicated and its first copy carries a stale hash

`MANIFEST.sha256` contains the `REGISTRATION TIMELINE` comment block **five times**, and its
**first** copy records `PREREG.md as executed: 4165f0dcab38…`, a value that matches no
current file. The last four copies record `1e1816cd3431a1c…`, which **is** the sha256 of
`PREREG.md` as Part A left it and is also the value in `A1_PROVENANCE.json`
(`prereg_sha256`). The duplication is a side effect of the Part-A script appending its
timeline on each of several invocations; Part B did not create it and did not remove it.
Part B appended its own block (AMENDMENT 1, with the operative `PREREG.md` hash
`d44558d959c70d08…` computed **before** the first run) and edited nothing above it. Anyone
reading the manifest should treat the first timeline copy's "as executed" hash as stale and
the later copies as operative; the immutable anchors are the `PROTOCOL.md` hash and the first
`PREREG.md` hash `c30ea27366df3217…`.

Evidence: `MANIFEST.sha256`; `A1_PROVENANCE.json` (`prereg_sha256.PREREG.md`).

## E-B-10 — the two reused Design-off arms have realized ρ = 0 by construction

`fedavg_window` and `raven_wo_design` never apply ζ (Design off), so their realized deleted
share is 0 and the control map's 14.35 % deletion rate is a property of the map
`raven_ctrl` uses, not of those arms. `C1_RUNS.csv` therefore reports `rho_realized = 0` for
them and `C1_MAPS.json` reports the control map's 14.345 % figure separately as a structural
reference. The dose-response slope uses the realized values; anyone re-deriving a
"deleted vs RMSE" scatter from `C1_RUNS.csv` must not read the Design-off rows as
"ρ = 14.35 %".

Evidence: `C1_MAPS.json` (`arms.*.rho_note`); `C1_RUNS.csv`; `EXECUTION_REPORT.md` §B.3.

## E-B-11 — three Part-A artefact hashes in `MANIFEST.sha256` are historical, not stale-and-wrong

The Part-A "post-computation artefact hashes" block lists `PREREG.md` (`c30ea273…`),
`EXECUTION_REPORT.md` (`aeae1eb5…`) and `ERRATA_FOR_PAPER.md` (`a0004a55…`), none of which
matches the file on disk now. That is by construction: Part B **appended** to those three
files (AMENDMENT 1 and the Part B sections), which is exactly what this round was instructed
to do, and the Part-A block is left untouched as history. The operative hashes are the ones
in the Part B block at the end of the manifest (`PREREG.md` `d44558d9…`,
`EXECUTION_REPORT.md` `e8d8f3c6…`, `ERRATA_FOR_PAPER.md` `cb79106b…` as of finalisation).
The registration anchors of Part A — the `PROTOCOL.md` hash `916b5576…` and the first
`PREREG.md` hash `c30ea273…` at t0 — are unaffected and still verify. Verified this round:
all five frozen inputs (`CS_TRAIN_SETUP.json`, `CS_PHI_DECISION.json`, `MAPS_KEY_LEVEL.csv`,
`CS_E3.csv`, `scripts/run_nodesign_supplement.py`) still hash to their Part-A values, and no
file under `results_c1_cityscanner/`, `results_nodesign_supplement/`,
`results_exogenous_target/`, `artifacts/`, `src/`, `data/` or `tdrive_protocol_seal_r1/` was
modified during Part B.

Evidence: `MANIFEST.sha256` (both blocks); `C1_RECON.json` (`inputs`); file mtimes.
