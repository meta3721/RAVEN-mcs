# Diagnostic record — consolidated: correctness defects, the measured gain ceiling, layer provenance, and the RAVEN-MCS evidence base

```text
Date: 2026-09-23 (supersedes the 2026-09-20 metric-definition record)
Added: 2026-09-24 — D-6, §2 L6–L9, §3 T8: the constructed regime as a bound on the achievable gain
Implemented: 2026-09-24 — F-3 in `main.tex` §VII-A.2 and `appendix.tex` (A5/A6 audit); §7 items 16–17
Corrected: 2026-09-24 — T3 restated: `RAVEN-SimOracle` is a joint p/q oracle, so the null cannot be
           attributed to `q`; the U-Air readings are re-derived as −0.028% (sd 0.265%). Touches
           §0 D-6, §2 L7, §3 T3, §3 T8, §8 F-2. The same correction was applied to
           `raven-mcs-method-revision-evaluation.md`. No manuscript file changed.
Implemented (paper): 2026-09-25 — D-1 as Option 1: φ removed from all three `.tex` files, the Design
           factor restated as an explicit configuration, and Table III plus the appendix four-block
           table completed into a within-dataset Design factorial (§7 items 18–21). Main 16 pp.,
           supplement 15 pp., equation labels 41, 0 undefined, 0 overfull > 2 pt.
Executed:  2026-09-24 — F-1 and the ceiling map. The ceiling map is read from the frozen artifacts
           (**T9**); F-1 ran 160 new cells and returns Δ_oracle = +0.104% / −0.251%, inside the
           pre-registered bound, so **H-A is refuted** (§3 T8 item 2, §3 T8's H-A outcome, §8 item 8).
           Standalone write-up: `ccfa-review-reports/raven-mcs-f1-experiment-summary.md`.
           Anchor correction the same day: the `raven` cell is the forced-Design row on U-Air, not
           the deployed method (T9); the U-Air columns of T9 and F-1 carry that caveat.
Executed (H/U1): 2026-09-24/25 — the H headroom grid (180 runs, pre-registered STOP on 5 seeds) and
           its U-Air extension **U1** (270 new runs, 45 new traces, 20 seeds): the pre-registered GO
           rule never fired, all six |H| ≤ 0.217 %, and the Design support cost settled at
           **+6.31…+7.39 %** with every CI lower bound above **+4.75 %**. §3A;
           `results_h_headroom/round_v1/` and `round_u1/`.
Audited:   2026-09-25 — the main comparison's U-Air `FedAvg-Window` cell traced to a 2026-08-11
           runner that dropped the zero-target-mass pairs. §2A N1; `results_table2_audit/`.
Corrected: 2026-09-27 — **four corrections to §2A** (N3 rewritten, N4 downgraded to a disclosed
           redundancy, N7 added, N2 given its metric attribution). The `−6.17 %` / `−9.11 %` sentence
           is `WorstGroupRMSE` **paired TEST**, and on that metric against equal-delivery comparators
           it is `+0.48 %` / `+0.44 %`; on `RMSE_μ` the win is `+0.54 %` (TEST) / `+0.09 %` (ALL20),
           not `+0.55 %`. The earlier claimed "0.35 % printed-versus-recomputed gap" **was wrong** and
           is withdrawn. See §7 items 22–25.
Reviewed:  2026-09-25 — full review after Option 1: absolute **4/10 weak reject**, progress
           **+0.40**. `ccfa-review-reports/raven-mcs-tmc-review.md`; the prior version is kept at
           `snapshots/raven-mcs-tmc-review-2026-09-20-pre-option1.md`.
Reviewed (external): 2026-09-27 — advisor-supplied GPT review of **the current build** (`main(6).pdf`
           16 pp. + `supplemental.pdf` 15 pp.), kept verbatim at
           `ccfa-review-reports/raven-mcs-unspecified-venue-review.md` (33 284 B,
           sha256 `5b1f1d4f…`). Its verdict is **4/10 weak reject, confidence 4/5** — the same number
           this record's round-3 review reached independently, from **different** decisive negatives.
           Recorded as **Part III**, ordered by logical upstream-ness and then by weight. It
           **reopens one correctness question** (P3's A6 clause list, and `ε_clip` as the retained
           mitigation) and names **five stated-versus-true defects in the current build**. It does
           **not** touch the hidden-confounding/ignorability axis. No manuscript file changed.
Implemented (paper): 2026-09-28 — **Part III X-1 repaired, X-6 and X-21 with it.** A6 is split into
           **A6a** (stabilizers inactive *at the true margins*: `π^opp≥π_min`, `p^obs≥p_min`,
           `π^tar/(π^opp p^obs)≤a_max` under Design on or `1/p^obs≤a_max` under Design off, and
           `1/q^use≤d_max`) and **A6b** (the three bounded interpolation errors, which is what keeps
           `ε_π`, `ε_p`, `ε_q` defined).  `eq:eps_clip` is replaced **in place** by the measurable
           `ε_stab,r = ‖β_r^T − β_r^⋆‖₁` (`eq:eps_stab`, still equation **37**), and Proposition 3 now
           assumes A1, A4, A5, A6b and concludes
           `‖β̂_r − β_r^⋆‖₁ ≤ C₁(ε_π+ε_p+ε_q) + ε_stab,r` with the new envelope
           `C₁=(2K_rn_r/B_min)(d_max·max{L_π,L_p}+a_max·L_q)`.  The appendix proof is rewritten in four
           steps that never use A6a, plus the support lemma.  Two published statements were wrong and
           are corrected: the audit read the a-side clause as a bound on `1/p^obs` when the implemented
           weight carries `π^tar/π^opp`, and it used `a_max=40` where the E3 runs resolved **20**
           (§7 items 37–39, Part III III.9).  Measured at the true margins,
           `max π^tar/(π^opp p^obs)` is **19.26** on SensorScope but **23.47** on U-Air, so the clause
           **fails on U-Air**; `ε_stab` has median 0, p95 `0.0719`/`0.0528`, max `0.553`/`0.680`, and
           is positive on 10.7 %/11.1 % of active windows.  Build after the write: main **16 pp.**,
           supplement **16 pp.** (was 15), 41 equations, 0 errors, 0 undefined, 0 overfull.
Implemented (paper): 2026-09-28/29 — **detail-level notation pass, requested by the user while the
           major items wait.**  It changes no claim, number, table, equation or result; it only defines
           symbols the paper was using before defining them, and unifies two spellings of one object.
           Fixed: `θ, Θ, f_θ, Y_i, C^dep` and the learned-object sentence (§III-A); `γ_r, E_loc,
           θ^{(E_loc)}` (§III-B) and `ℓ` at its first use (§III-E); `S_max` (§III-B), also unified
           from the lowercase `s_max` in §VII-A and the four appendix construction notes; `𝒢, 𝒮` as
           sets and `h: I→𝒢`, `s: I→𝒮` as mappings (§III-B); `I_dep` (§III-C); the `Pr{·}` operator
           (§III-B, eqs. (2)–(3)); and the indicator `1{·} → \mathbf{1}{·}` in three places (§V, the
           Gate line, the appendix Gate algorithm line) with a definition at first use in both
           documents.  Also removed a now-redundant disambiguation sentence and restored `α_r ∈ C_r`
           with a pointer to the feasible set (25) and program (P2) where `ω = Mα` first appears.
           **Still open:** `h(i)` is used in §II before §III-B defines it.  Side effect: main
           **16 → 17 pp.** (the four tail references sit on p. 17); supplement unchanged at 16 pp.
           No training, no artifact touched, no git operation.  §7 item 40.
Implemented (paper): 2026-09-29 — **the mirror/θ re-sourcing applied (§7 item 47), driven by the
           pre-registered rule that the `theta` copy is paper-conformant.**  Seven printed `RMSE_μ`
           cells move to the θ values (Table III U-Air TwoStage `1.2160→1.2202` and RAVEN-Design
           `1.1911→1.1954`; the appendix all-method table Local-Hájek `1.1882→1.1923`, TwoStage,
           Inst-Cal, RAVEN-Design, RAVEN-SimOracle `1.1914→1.1958`), each with its std recomputed at
           θ; the derived text follows (Design cost on U-Air `6.553→6.886 %` and tail `6.875→7.221 %`
           in §V and in the Table III caption, Inst's prediction cost `0.131/0.136 → 0.143/0.149 %`,
           and the U-Air half of the Fig. 4 caption), and Table IV's U-Air prediction cells are
           recomputed from paired θ series (Design `−6.553→−6.885`, `−6.875→−7.221`; Use
           `+0.024→+0.025`, `+0.025→+0.026`; Inst `+0.131→+0.143`, `+0.136→+0.149`; Holm flags
           unchanged at `9.5e−6` and `0.0194`).  Three `figure_data/` files were resampled and **four
           figures rebuilt** (`fig_w1_design_gate`, `fig4_e3_prediction_risk`, `fig5_e4_component_ablation`,
           `fig6_e4_uair_excl_design`).  Not changed, with evidence: every `WorstGroupRMSE` cell, the
           four-block table, all `Δ_group`/`Δ_c-s` cells (model-free; recomputation bit-identical),
           §V's `2.46 %` (recomputed `2.4578 %` under the same denominator), `+0.48 %/+0.44 %` and
           `+0.002 %/+0.075 %` (the RAVEN-NoDesign rows), and the caption's `+7.9 %/+8.0 %`.
           Build after the write: main **17 pp.**, supplement **16 pp.**, 0 errors, 0 undefined,
           0 overfull, em dashes 2/3 in `main.tex` and 0 in `appendix.tex` (`check_prose_quality.py`
           clean on `main.tex`; it times out on the 100 KB `appendix.tex` at both full-file and
           section scope, a pre-existing tooling limit, and that file's edit was digits only).
Implemented (paper): 2026-09-29 — **M1 closed: the Design factor now has a stated standard (two equations).**
           The gap the φ removal left — a factor with no criterion — is filled in §VII-E by a new
           paragraph, "Setting the Design factor". Eq. **(42)** is the support gate
           `ρ_r = n^zero_r/n_r`, `D_r = on ⟺ ρ_r = 0`: Design is on exactly when no delivered training
           unit sits on a stratum the public target map declares empty. It reads only public pre-window
           information, is a stopping condition rather than an endpoint preference, and returns on the
           reported blocks the settings their rankings already use (on for SensorScope, NSW-Traffic and
           both City Scanner rankings; off for U-Air `35.4 %` and T-Drive `47.4 %`). Eq. **(43)** is the
           switch point of the normalized four-endpoint objective `Ĵ_r(D)`; the two settings are
           indifferent when `w_c·4.990 = w_g·6.943 + w_μ·6.885 + w_t·7.221`, so a structure-only
           deployment keeps Design on iff `w_c/w_g > 1.39`, while `RMSE_μ`-only keeps it off, and on
           SensorScope every term moves the same way, so Design on is optimal for every weight vector.
           The switch point is scoped as a decision standard for blocks of this kind, not a universal
           law, and **both settings remain reported** with Table IV recording what the gate forgoes on
           U-Air (the `4.990 %` `Δ_c-s` gain). Supporting edits: §III-D `1049–1057` now points to the
           gate instead of saying no setting is selected; contributions `222–227`; §VII-G `2170–2177`;
           the appendix statistic is relabelled as the gate's input (`appendix.tex:70–76`,
           `2362–2391`, table header "Design (42)"); `supplemental.tex` equation counter 42 → 43 so the
           supplement continues at (44) with no gap. The paper's own `RMSE_μ` cost of Design was also
           harmonized to `6.885 %` (three places) so it matches Table IV's paired value. Verified: main
           **17 pp.** (unchanged), supplement **16 pp.** (unchanged), 43 numbered equations, 0 errors,
           0 undefined references, 0 overfull, em dashes 2/3, prose check with no hard failure,
           appendix freeze invariant 0/0 (no hardcoded equation number ≥41 existed, so the two new
           numbers 42–43 collide with nothing). Snapshot: `snapshots/2026-09-29-pre-m1-design-rule/`.
           §7 item 51.
Implemented (paper): 2026-09-29 — **X-5 and X-7 fixed (wording only, three sentences).** X-5: the setup
           sentence no longer claims that every experiment except the balanced control uses 20 paired
           seeds; it now names the exceptions (the balanced control's five and the four ten-seed
           protocol tables: the T-Drive ranking and the three supplemental rankings). X-7: appendix F's
           opening no longer says the sealed family uses Design-*off* on U-Air and no longer maps the
           SensorScope/U-Air rows of Table III onto the two settings; it states that the family is
           evaluated with Design on and that the U-Air panels therefore diagnose that arm rather than
           the deployed setting, which is Design on for SensorScope and Design off for U-Air. Both
           edits keep their paragraph's physical line count, so no recorded line citation shifts.
           Build after the edit: main **17 pp.**, supplement **16 pp.**, 0 errors, 0 undefined,
           0 overfull, em dashes 2/3, no prose hard failure, freeze invariant 0/0. §7 item 50.
Implemented (paper): 2026-09-29 — **X-4 fixed (one sentence in §V).** The Local-Hájek sentence
           no longer attributes the coincidence to a shared Design-support restriction, which the
           appendix's own licensing rule contradicts and which described the pre-repair
           `fedavg_window`. It now states what the degeneracy audit proves: the coincidence holds
           wherever both arms keep the same active set, because the realized within-client Hájek
           weights are uniform on these traces, and the two supplemental U-Air rows differ only in
           the active set. Build after the edit: main **17 pp.**, supplement **16 pp.**, 0 errors,
           0 undefined, 0 overfull, em dashes 2/3, no prose hard failure, freeze invariant 0/0. §7 item 49.
Implemented (paper): 2026-10-02 — **B1 written: Proposition 4 (group decomposition of the deployment-target
           criterion) plus the RMSE-only corollary, with the appendix proof.**  §VI now carries
           `prop:group_decomposition`: for any partition of the supported test units,
           `RMSE_μ² = Σ_g μ^eval_g RMSE_g²`, the feasible-direction derivative
           `Σ_g d_g RMSE_g²/(2 RMSE_μ)`, and the ordering condition
           `Σ_g (μ'^eval_g − μ^eval_g)(RMSE²_{g,a} − RMSE²_{g,b})`; §VII-E's "Setting the Design factor"
           points to it and states that it covers the `RMSE_μ` side only.  Appendix
           `app:proof_prop4` proves both parts.  Verification before the write:
           `results_group_identity/round_v1/` (E1 identity on 470 rows, max `1.78e-15`; E2 exact layer
           `≤1.43e-16` with Taylor residuals `1.09e-5 / 7.15e-6 / 1.99e-5`; E3 30 pair-cells with zero
           order/sign inconsistencies; E4 recovers the published `RMSE_μ` Design gap on both datasets,
           SensorScope `+0.00536 %` vs `+0.005 %` and U-Air `−6.875 %` vs `−6.885 %`; E5 within-group
           weight variance `≈1e-38`).  **Scope kept:** the identity is not assumption-free (partition,
           within-group weights independent of the other groups' masses, `μ^eval` a probability vector),
           it is not a training-side statement, and it does **not** cover `Δ_group` or `Δ_c-s` — the
           earlier draft's claim that all four printed percentages follow from it was withdrawn.
           Build: main **17 pp.**, supplement **16 pp.**, 43 equations (no new equation number),
           proposition numbers 1–3 unchanged, supplement proposition counter 3 → 4 so its own
           propositions continue at 5–6, 0 errors, 0 undefined, 0 overfull, em dashes 2/3,
           freeze invariant 0/0.  Snapshot `snapshots/2026-10-02-pre-group-decomposition/`. §7 item 52.
Closed:     2026-09-29 — **the last two mirror-sourced candidates checked; X-4b closed.** §7 item 48.
           Of the two, one is a real (record-only) effect and one is a false alarm. **(a) The H grid:**
           ten U-Air `raven_simoracle` runs under `round_u1` carry the same inactive final window; their
           checkpoints were re-evaluated at θ with each run's own wiring (production target for
           C0/C1/C3, the block-uniform override for C4, `DiurnalBlindNDMF` for C3) and the values
           reproduce the E3 tree's θ cells to the last digit. Nothing the paper prints moves: §VII-F's
           H facts use the frozen Design-off oracle, whose runs are clean, and all six `H_RMSE_mu`
           cells are bit-identical after the correction. The triggered runs feed only the `H_design` /
           `design_support_cost` columns, so the **record's** §3A H4 table was corrected instead
           (C0/C1/C3/C4 `+6.968/+6.989/+6.980/+6.991 %` → `+7.356/+7.186/+7.366/+7.388 %`; C2 and C5
           untouched; the quoted range becomes `+6.31…+7.39 %` and every CI lower bound still clears
           `+4.75 %` at `+4.751 %`). **(b) §VII-F's class-internal numbers** were suspected of reading
           the frozen tree; they do not — `compute_ceiling_class_paired.py` reads the frozen tree only
           for SensorScope, while its U-Air half reads the θ cells of `E2_UAIR_CELLS.csv`, so
           `+0.040 %` and `2.04 % [1.33, 2.75]` were already θ-consistent. With this, no printed
           number in the manuscript traces to the mirror, and X-4b is closed (items 46–48);
           X-4/X-5/X-7 remain open on their own terms.
Reviewed (round 4): 2026-10-02 — **version-comparison re-review focused on whether the external
           review's seven majors are resolved.** Canonical report rewritten in place at
           `ccfa-review-reports/raven-mcs-tmc-review.md` (the English round-3 text is archived at
           `snapshots/2026-10-02-pre-round4-raven-mcs-tmc-review.md`); the structured contract passes
           `ccf-paper-reviewer/scripts/validate_version_comparison.py` (PASS, stored at
           `results_group_identity/round_v1/comparison_check.json`).  **Relative progress** under the
           frozen 8-dimension contract: weighted delta **+0.20 → improved**, entirely from
           technical correctness 4 → 5 (`W2`, `W5`, `W7` closed); no traceable decrease.  **Absolute
           readiness: 5/10 weak reject, upper edge (was 4/10)** — the external review's own §15
           condition ("先消除硬伤 … 可考虑由 4 到 5") is met and the repairs exposed no worse
           experimental problem.  **Resolved:** `W2` (A6a/A6b + `ε_stab` + four-step proof + corrected
           audit), `W5` (§VII-F re-grounded on `C_r`+(P2)+`RMSE_μ`), `W7` (all five table/text
           conflicts).  **Partially resolved:** `W3` (A6a measured to fail on U-Air, Design support
           cost quantified; the fixed-active-set mechanism control `M8` is still missing), `W6`
           (in-paper config/SOP gaps unchanged; new external-validity evidence exists outside the
           paper).  **Unresolved:** `W1` (matched-budget necessity of the full method), `W4`
           (FedIPW/FedPALS mapping).  **New issues:** `N1` — the appendix's City Scanner row is a
           region-level structural zero while `eq:design_gate` is key-level (`ρ = 14.35 %` on that
           block), and the paper does not explain the two objects (`newly_revealed_by_evidence`);
           `N2` — this round's exogenous-target and endpoint evidence is entirely outside the paper;
           `N3` — the `6.886 → 6.885` harmonisation (closed in round, zero score effect).
Manuscript: TO_OVERLEAF_paper_tmc_r1_clean (main.pdf **17 pp.** + supplemental.pdf **16 pp.**; the
            build reviewed on 2026-09-27 was 16 + 15, and the +1 on the main text is the notation pass)
Inputs: this record; ccfa-review-reports/raven-mcs-method-revision-evaluation.md (2026-09-23);
        ccfa-review-reports/raven-mcs-unspecified-venue-review.md (the external review, Part III);
        results_prop3_audit/round_v1/ (the ε_stab audit and its independent replication);
        snapshots/2026-09-28-pre-prop3-fix/ (the two `.tex` files before the repair)
Status: assessment and decision record. This record itself changed no manuscript file.
        The P0 edits in §7 items 12-15 and the 2026-09-28 write in items 37–39 were applied
        separately, on explicit instruction.
Boundary: changes listed in §7 are those made after the previous review round (2026-09-12).
Purpose: **consolidated 2026-09-25.** Part I orders every finding by class and weight and points into
         the evidence below; Part II holds the evidence and the ledger; Part III records the
         2026-09-27 external review against the same evidence, ranked by logical upstream-ness, and
         the 2026-09-28 resolution of its first item.
         Structure note: section numbers 0–11 and every item label (R, L, T, S, E, G, D) are
         unchanged, because other documents cite them. New material is inserted as §2A and §3A
         rather than renumbering anything; Part III follows the same rule with its own label space,
         X-1…X-21, so that no existing citation moves.
         Part IV follows the same rule: it adds a new part and its own subsection space, IV.1–IV.9,
         and renumbers nothing.
Added (record): 2026-10-03 — **Part IV**, the evidence refresh: the v4 contribution rewrite and the
         register fix E1–E9 indexed by line anchor; the design-repair round P0-1…P0-3, EA-1…EA-3, its
         two duplication-only deletions and the band `\label`; the design-repair's own defect **F5**
         (the "instantaneous calibration … neither prediction drivers" scope against Table IV's U-Air
         `Inst` row `+0.143 %` / `+0.149 %`, `p_Holm = 0.0194`), now `partially closed` at the text
         level; the round-7 closure table (9 closed, 6 partial, 8 open, plus `F6`) and round 7's
         correction that `R5-13`'s `6.55 %` / `6.885 %` is one object, not two; the
         round-v4/v5/v5.1/v5.1a chain with AM-1…AM-6, the corrected oracle (optimal to `1e-13` in
         objective value; `122 094` feasible perturbations with improvement `0.0`) and the two
         surviving gate failures; the v5.1 θ-canonical re-sourcing of the six U-Air Part B cells and
         five paired rows; the gatekeeping round (A1 hierarchy, descriptive results, Part B at
         `r = 3`, and the two statements that follow); the errata index `E-v51-1…4`, `E-A1-8/10/13`,
         `E-B-1…11` plus the two protocol-level defects; and the explicit unlock arithmetic.
Implemented (paper, adjacent): 2026-10-03 — the same pass wrote seven evidence items and three
         offsets into `main.tex`: the `P0-1`/`F5` scope in both places with the κ=1000 rule named
         outside the verdict, the bootstrap/Holm-family documentation, the `E-v51-1` explanation
         replacement (the false "composition and mass inputs … vary weakly with the model trajectory"
         deleted, "reference not numerically stable" never in the file), the `eps_impl ≤ 2.42e-5`
         bound and its `6`–`16 %` ratio, the City Scanner H2 testability result, the trace-level
         reading of the dominant City Scanner trace, and the Design-cost scope; plus eight verified
         duplication deletions. Snapshot `snapshots/2026-10-03-pre-evidence-errata/`. Build: main
         **17 pp.**, 0 errors, 0 undefined, 0 overfull, em dashes 0, `\label` 97, net length
         **+8 lines / +28 words** (2 234 → 2 242 lines, 112 857 → 113 126 bytes; not reduced to
         zero — see the pass report). IV.9.
Contents: Part I — consolidated diagnosis, ordered by importance
          Part II — §0 decisions; §1–§2 root defects 1–2; §2A correctness defect (U-Air baseline);
                    §3 root defect 3 (ceiling); §3A the headroom experiments; §4 scenarios;
                    §5 earlier problems; §6 degeneration; §7 changelog; §8 next actions;
                    §9 incident log; §10 reproduce; §11 boundaries
          Part III — the external review (2026-09-27): X-1…X-21, ranked, with what was verified
                    here and what was not, and III.9 = the X-1 repair of 2026-09-28
          Part IV — the 2026-10-03 evidence refresh: the v4 contribution rewrite E1–E9, the
                    design-repair round and its defect F5, the closure tables, the
                    round-v4/v5/v5.1/v5.1a chain, the gatekeeping round, the errata index,
                    the unlock arithmetic, and what the companion paper pass changed
          Part V — the 2026-10-04 state: the round-9 review and its scores, the P0 repair
                    pass, the M7 bundle refresh, what still blocks, and §V.5 = what is
                    still stale or unindexed in Parts I–III
          Part VI — the 2026-10-06 completion of the H line: the `m_total` rule that closes the
                    U-Air `fedavg_window` gate, the H table on the corrected arm, the active-set
                    regime finding, and correction items 45–48
Added (record, current state): 2026-10-04 — **Part V**, the current-state index: the round-9
          version-comparison review under the unchanged frozen contract `TMC-J-R4` (weighted readiness
          **3.25**, stance **5/10 held**, relative delta **0.00 `unchanged`**, 20 closed / 5 partial /
          1 moot / 4 open (the round-9 §6 table lists 21 `closed` rows — see §V.1), the disclosed Clarity judgement call worth +0.15, and the ten new findings
          `H1`…`H10`); the `P0` pass that repaired `H1`, `H2`, `H3`, `H4` and `H6` (**4 change blocks,
          +19 / −12 lines, net +7**, 12 302 → 12 377 words, 17 pp held, `appendix.tex` untouched,
          snapshot `snapshots/2026-10-04-pre-p0-fix/`); and the `M7` public-bundle refresh (**217 files /
          2 921 397 bytes** added — 216 under `w1/` plus the rebuilt `MANIFEST.csv`; `verify.py` `checked=2116 mismatches=0`, `M7` closed, so
          Reproducibility 2 → 3 and the readiness sum becomes **3.35** for a mechanical reason).
          **The round-10 audit of this very part, and of the bundle refresh it records, is
          `ccfa-review-reports/raven-mcs-tmc-review-round10.md`; its findings M-1…M-4 and A-1…A-7 are applied
          to Part V and to the correction block above. M-4 is the one with teeth for every earlier round:
          **round 9’s §6 quotes for `R5-6`, `F1` and `F8` were inherited, not re-read, and two of them
          appear in no version after round 8** — so a closure table’s "re-verified" label has to be earned
          by quoting the frozen file, not the previous report.** **§V.5 of Part V lists the eleven parts of this record that are still stale or unindexed, and
          which of them would today mislead a reader.**
Executed (H line): 2026-10-06 — **the H headroom line's FedAvg arm is closed, and the H table is
          re-measured on it.** The one gate both rounds recorded as `"pass": "True"` with
          `known_nonrepro: true` — the U-Air `fedavg_window` arm of `round_v1`/`round_u1`, off the
          frozen 2026-08-11 artifact by `3.96e-02` at seed 30001 (−3.27 %) and `1.35e-01` at seed
          30006 (−10.53 %) — is closed by a single rule: a client-window with `pi_tar = 0` gets
          `m_total = 0` and leaves `e_r`, while the trace keeps its `U` byte for byte. Under it the
          arm reproduces the frozen artifact on **20/20 seeds, exactly** (`0.000e+00` on `RMSE_mu`,
          `Tail_RMSE`, `RMSE_rho` and `Delta_group`), with identical active-client sets on every
          window; 240/240 trace pairings match; both oracle arms re-verify at `0.0`
          (`results_h_headroom/round_v3/`). The H table rebuilt on that arm (6 conditions × 20
          seeds × 2 oracle arms) returns `decision = go` under the unchanged `go_bar = 0.005`,
          and **all six `go` cells are the design-off oracle arm** — the same object §3A H4 already
          quantifies as the U-Air support cost. The design-on oracle has no headroom
          (`|H| ≤ 0.68 %`). New structural evidence: the dropped and kept active sets are
          *identical* between a FedAvg arm and an oracle arm on 20/20 seeds in both regimes, so the
          ≈6 % is a regime switch rather than an oracle effect. **Part VI**; no manuscript file
          changed. The `+6.31…+7.39 %` support-cost range quoted above and in §3A is pre-θ and
          measured on the superseded arm — correction item 45 (Part VI) replaces its level.
Corrected (record): 2026-10-06 — **the round-3 FedAvg grid's `C4`/`C5` cells are not block-uniform, and
          the `C4`/`C5` rows of the VI.3 H table inherit that** (correction item 49). `C4` is numerically
          the `C0` cell on all 20 seeds and every numeric field; the cause is an injected condition whose
          `target` stayed `test_share`, so the block-uniform target-bundle patch never ran, while the
          h_round B side did carry it. Found by the endpoint round's replay gate, which stopped 10 of its
          12 cell sets for that and a second, separate reason (the replay reconstruction lacks the
          per-condition injections). `results_regime_b_endpoints/round_v1/P2_REPORT.md`.
          **Repaired the same day (item 50)**: 40 C4/C5 FedAvg runs re-trained with the condition
          dictionary verbatim (Δ`RMSE_mu` +0.0032 each, Δ`Delta_c-s` exactly 0), the C4/C5 H rows
          re-derived (`H_best 0.059330 → 0.061820` and `0.052110 → 0.054595`, both still `go`, decision
          unchanged), and the replay rebuilt with the per-condition injections so its gate now passes 7
          of 12 cell sets instead of 2. **The endpoint round then closed at 12 of 12** (items 51–52:
          the non-aggregating-final-window criterion, validated 6/6 against 0/198 before use, extended
          first to `C2`/`C5` and then to `C1`), with six disclosed provenance exemptions and no change
          to the `1e-12` tolerance; the final reading is `E_dec` down `20.1–39.1 %` in regime B,
          entirely through false-alarm suppression, B retaining `0.00–2.48 %` of the exceedance mass
          against A's `17.5–33.9 %`.
Manuscript: 2026-10-06 — **round-12 review applied, and the revision ledger is now Part VII of this
          record.** The round-12 review (`ccfa-review-reports/raven-mcs-tmc-review.md`, rewritten in
          place in version-comparison mode, previous text archived at
          `snapshots/2026-10-06-pre-round12-raven-mcs-tmc-review.md`) compared the text frozen by the
          round-10 audit (`88ecd743…`) with the r11 text-repair state (`59e4f4d5…`): 4 hunks, +5/−6,
          three defects resolved, classification `improved` (+0.05, Terminology; exactly on the frozen
          threshold, disclosed), stance held at **5/10**, readiness sum **3.30**, Evidence still the
          blocking axis. Applied on that review: three prose-only edits in `main.tex` — the availability
          paragraph now names the `w1/` subtree, `w1/PAPER_NUMBERS.csv` and `verify.py` (M2); the band
          paragraph cites `w1/ladder_v3/PREREG.md` as where the band and its reading rule were fixed
          (M4); and the attribution verdict, the κ exclusion and the prediction pointer move to their own
          contribution bullet (CL-3). `main.tex` **`59e4f4d5…` → `02447bfe6256632b…`** (3 hunks, +9/−1,
          +63 words), `main.pdf` **17 pp held**, 0 errors / 0 undefined / 0 multiply-defined / 0 overfull;
          no number, table, figure or claim changed, no new experiment, no bibliography change. Snapshot
          `snapshots/2026-10-06-pre-r12-fix/`. **Part VII** holds the twelve-column revision ledger;
          `ccfa-review-reports/raven-mcs-r12-response-to-review.md` is the response artifact. E1 and E2
          remain open, and **NEW-r12-1** forbids re-offering the U-Air exceedance endpoint as E1's repair.
```

---

# Part I — Consolidated diagnosis, ordered by importance

## I.1 The verdict in one paragraph

The manuscript is an honest, well-scoped paper whose central empirical claim cannot be supported on
the blocks it reports. Four classes of finding stand. **Tier 1** was a correctness defect: the U-Air
`FedAvg-Window` baseline had been produced by a runner that dropped the 72 of 288 zero-target-mass
training pairs, so one stated win was an artifact of an unequal-information baseline. It is **closed**,
repaired under route A on 2026-09-27 and written into the manuscript. **Tier 2** is the evidence
ceiling, and it now sets the verdict on its own: no correction in the family moves the primary endpoint
by 0.5 %, two independent pre-registered experiments show this is a property of the endpoints rather
than of a testbed that was made too easy, and until 2026-09-27 the paper stated neither the bound nor
the experiment that measured it. **Tier 3** is provenance: the deployment target is evaluation-derived
and `U` is measured nowhere, so the objects are not what they are named. **Tier 4** is a ledger of what
has been repaired. **Tier 5** is the repair routes that remain, ranked by what they can still buy.

**Status 2026-10-04: this paragraph is the 2026-09-27 state and is left as written; the current numbers are 5/10 with a weighted readiness sum of 3.25, and the current repairs are indexed in Part V and in the round-9 correction block above.** Absolute readiness on the frozen rubric was then **4 / 10 weak reject**. Round 2 measured **+0.40** on the
progress scale and round 3 **+0.10**: the route-A repair bought soundness (+1) and cost reproducibility
(−1) by leaving the shipped bundle stale, and it did not create the evidence the contribution needs. A
third-round erratum dated 2026-09-27 withdrew one review concern and the mechanism attribution of
another. See §7 items 26–34 and `results_active_set_repair/round_v1/`.

**Added 2026-09-27.** An external review of the same build (the advisor's GPT report; **Part III**)
reaches the same absolute number — **4/10 weak reject** — from partly different decisive negatives,
and adds two items that outrank everything left in Tier 5. **X-1** reopens a correctness question
inside Tier 1's *theory* rather than its artifacts: A6 concludes that four stabilizers are inactive
while its clauses cover only two of them, and the `ε_clip` residual the paper retains as its fallback
carries ceiling excess only — so Proposition 3 is not established in the regime the paper itself
reports. **X-2** is the claim form of §VII-F, written in the previous round: an oracle-propensity
stress grid cannot bound a correction *family*. Five further items (**X-3**–**X-7**) are false
statements in the current build, each verified in-source below and each fixable without compute.

**Resolved 2026-09-28.** **X-1 is now fixed in the paper**, and X-6 and X-21 with it (III.9). The paper
no longer asserts a guarantee it cannot carry: A6 is split into **A6a** (inactivity at the true
margins, with the ceiling clause stated on the composite weight) and **A6b** (the bounded
interpolation errors), the unmeasurable `ε_clip` is replaced by the measurable
`ε_stab,r = ‖β_r^T − β_r^⋆‖₁`, and Proposition 3 is stated with A6b alone plus that explicit term, so
A5 and A6b give a perturbation bound and A6a is only what makes the term vanish. The repair also
produced two corrections to statements the paper had already published: the audit's a-side clause was
read in the wrong form **and** at the wrong ceiling constant, and at the true margins that clause
**fails on U-Air** (`23.47 > a_max = 20`) while passing on SensorScope (`19.26`) — so the earlier
"only the `q` side fails" narrative is withdrawn. What did **not** change: the empirical picture
(T-c/T-e/T-f), the verdict, and X-2–X-5, X-7, X-4b, which stay open.

## I.2 Tier 1 — correctness: closed 2026-09-27

**Closed.** The U-Air active-set defect was repaired under route A on 2026-09-27 and written into the
manuscript. The item anchors `N1`–`N7` are retained so that external citations still resolve; their
subjects and outcomes are in §2A below. Evidence lives in `results_active_set_repair/round_v1/`
(187-check verifier, manifest, worktree hashes, and the independent review of the review). There is no
open Tier-1 correctness item in this record.

**Qualified 2026-09-27 by Part III X-1, then closed 2026-09-28.** The external review reopened a
correctness item that is Tier-1 in class but *theoretical* rather than artifactual: A6's clause list
does not imply the floor inactivity it concludes, and `ε_clip` — the residual this record's earlier
repair chose to retain rather than cancel — cannot carry a floor-induced distortion. Verified
in-source here (III.3). It was upstream of T-c and of everything the paper says theory covers, so it
ranked above the Tier-5 routes in I.6. **The repair is written into the manuscript** (§7 items 37–39,
III.9): A6a/A6b, `ε_stab`, the four-step proof, and the corrected audit readings. Two items remain
open in the same neighbourhood and are *not* part of the closure: X-2 (§VII-F's family-bound claim
form) and X-4b (the three disputed U-Air seeds, root-caused on 2026-09-29 in §7 item 46).

One residual, carried in §7's open-defect table rather than here: the `wo_inst` ablation repair of
2026-08-12 is unfinished at `counterfactual_audit._solve_alpha`, so that arm cannot be re-run. No
manuscript value depends on it.

## I.3 Tier 2 — the evidence ceiling: the central claim cannot be supported on these blocks

| # | finding | where |
|:--|:---|:---|
| **T-a** | Every propensity route moves `RMSE_μ` by **≤0.03 %** in either direction; exact `p` and `q` together are worth +0.008 %/−0.028 % | §3 T1–T9 |
| **T-b** | The best any reweighting reaches is 0.112 % on SensorScope; on U-Air, re-anchored to the deployed method, the uncorrected central reference is **5.85 % worse** | §3 T9 |
| **T-c** | **The ceiling is not a testbed artifact.** F-1 hardened the observation propensity inside the stratum (Δ_oracle **+0.104 %/−0.251 %**); H/U1 stressed six conditions against a pre-registered 0.5 % bar, no cell reached 0.217 % and none fired GO. **Stated in the paper** as of §7 item 33 | §3 T8, §3A |
| **T-d** | **H-A is refuted**; what remains is H-B, endpoint weight-blindness | §3 T8 item 2 |
| **T-e** | The structural endpoint the paper wins on is decoupled from prediction by the paper's own ablations. The 2026-09-27 erratum sharpens this: with the corrected `wo_inst` reruns, **the Design factor is the only component that moves `Δ_group` materially**, and every other component moves it by at most 0.26 % | §3 T4, §6 |
| **T-f** | `U` is measured in no block, so the layer carrying most of the machinery is simultaneously unmeasured and worth ≤0.03 % | §2 L1, §2A |

**Part III adds to this tier, without changing a number in it.** T-c's statement is challenged on its
*claim form* (**X-2**: the grid measures one oracle-propensity configuration, and true propensities are
not the RMSE-optimal reweighting, so it cannot bound a family). T-e is what the external review reads as
"only the Design factor moves anything", and it converts that into a demand for a matched-budget
comparison against simple target calibration (**X-10**). The solver counts are re-read as feasibility
rather than optimality (**X-8**), and the coverage table's pooled `0.959` against a `6/8` U-Air cell is
raised as an evidence limit (**X-15**).

**X-2 closed 2026-09-29, and this is what the ceiling now is and is not.** §VII-F was re-grounded on the
class the paper defines (weights in `C_r`, selected by (P2), scored by `RMSE_mu`) and now carries two
measured quantities plus one proved perturbation bound: the pre-registered headroom from the
uncorrected member to the best oracle-margin member (`H`, unchanged: GO rule frozen, never fired,
`|H| ≤ 0.217 %`, F-1 hardening `15`–`21×` and still under `0.5 %`); the class-internal cost of
estimating the two margins (one calibrated member, only the margins swapped: `−0.008 %`
`[−0.041, +0.025]` on SensorScope and `+0.040 %` `[−0.090, +0.171]` on U-Air, paired over 20 seeds,
with TwoStage-Hájek `2.04 %` `[1.33, 2.75]` above the oracle member on U-Air and nothing comparable on
SensorScope); and the composition-level perturbation \eqref{eq:g4_comp} plus Proposition 3.
**The honest limit:** these bound the *data* side (what the selection margins cost) and the
*perturbation* side (what the plug-in moves inside the class). They do **not** prove how much the class
as a whole can gain over the uncorrected member. That quantity is only *measured*, by the pre-registered
`H` grid and by the class-wide ablation in which no propensity route moves `RMSE_mu` by more than
`0.03 %` (T-a). Reaching a *proved* family-gain statement needs one of three things this record has not
done: a transfer assumption strong enough to carry the composition bound to `RMSE_mu` (form only, and
the constant is vacuous at `π_min = 10⁻⁶`); an oracle over the *weights* themselves, optimised against
the evaluation metric (the class's empirical optimum, which needs retraining per candidate `α` or a
last-window surrogate); or a wider class than `C_r` (unconstrained ESS, a learned gate) to show the
ceiling is not an artifact of the constraints.

## I.4 Tier 3 — provenance and scope: the objects are not what they are named

| # | finding | where | moved? |
|:--|:---|:---|:---|
| **P-a** | The deployment target is evaluation-derived (`RMSE_μ` against a test-split share) | §1 R1–R4 | **no** |
| **P-b** | Both selection margins are stratum-constant by construction, so the reported regime is the easy one; now disclosed with its dispersion | §2 L6–L9 | disclosed only |
| **P-c** | The six-scenario family is complete and never enumerated; `complete_counteracting` is invisible | §4 S1–S7 | **no** |
| **P-d** | Equal-weight problems that survive independently of the above | §5 E1–E6, §6 G1–G7 | **no** |

**Part III maps onto this tier as follows.** The external review reaches **P-a** independently and in
its own words — it asks why the deployment target is a test-split frequency, whether an independent
historical or predefined target preserves the conclusions, and it explicitly declines to call the
construction label leakage while still requiring the acquisition story (**X-12**, its §9 "目标信息" and
§14 Q5). It restates **T-f** as "真实 U 在任何实验块都没有测量" plus the City-Scanner cell-versus-vehicle
client question (**X-13**). It does **not** reach **P-b** (the stratum-constant margins), **P-c** (the
unreported `complete_counteracting` scenario) or **P-d**. One item is a new class this record has no
anchor for: the mathematical mapping to FedIPW and FedPALS (**X-14**), which our tooling cannot
reproduce because `web_fetch` fails on every host here.

## I.5 Tier 4 — what has been repaired (ledger)

| decision | what it fixed | evidence |
|:---|:---|:---|
| **D-4** | Layer provenance and construction constants stated; abstract, Table III caption and limitations scoped | §7 items 12–15 |
| **D-6** | The dispersion of the two margins stated beside the constants | §7 items 16–17 |
| **D-1** | φ removed from all three `.tex` files; the Design factor restated as an explicit configuration; Table III completed into a within-dataset factorial; the appendix statistic demoted to descriptive provenance | §7 items 18–21 |
| **D-6 / T8** | F-1 executed; H-A refuted | §3 T8, `raven-mcs-f1-experiment-summary.md` |
| **Route A** | **The U-Air correctness defect written out of the manuscript**: the `FedAvg-Window` row and three appendix no-Design rows rebuilt on the licensed set, `tab:app_block_rmse` and `tab:app_p2_coverage` updated, the `−9.11 % / −6.17 %` sentence replaced by a within-Design-family statement plus the six-comparator qualification, the Local-Hájek coincidence reattributed, and the metric scale disclosed (closing `N7`). **Tier 1 closed** | §7 items 26–32 |
| **T-c** | **The ceiling stated**: §VII-F "Recoverable-Gain Ceiling" now carries the frozen GO rule, the negative result on both blocks, the U-Air MDE caveat, and the F-1 hardening test | §7 item 33 |
| **X-1** | **The guarantee matched to what the paper can prove**: A6 split into A6a (inactivity *at the true margins*, ceiling clause on the composite weight) and A6b (bounded interpolation errors); `ε_clip` replaced by the measurable `ε_stab,r = ‖β_r^T − β_r^⋆‖₁`; Proposition 3 restated with A1, A4, A5, A6b and the new envelope `C₁`; appendix proof rewritten in four steps that never use A6a, plus the support lemma. **X-6 and X-21 closed with it** | §7 items 37–39, Part III III.9 |

## I.6 Tier 5 — repair routes, ranked by what they can still buy

| rank | route | what it buys | status |
|:--|:---|:---|:---|
| **X-1** | ~~**Complete A6, or widen `ε_clip` to carry the floor residual, or weaken the claim.**~~ | restores a printed guarantee; upstream of §VI-E, the abstract and the A5/A6 audit's role | **done 2026-09-28**; option (i)+(ii): A6a/A6b added and `ε_clip` replaced by the measurable `ε_stab`; §7 items 37–39, III.9 |
| **X-2** | ~~**Narrow §VII-F's closing claim** from a family bound to the tested oracle configuration, keeping the MDE disclosure~~ **done 2026-09-29 (plan c)**: the ceiling is re-grounded on `C_r` + (P2) + `RMSE_mu`, with the class-internal margins comparison and the \eqref{eq:g4_comp} anchor; §7 item 42, I.3 | removes the one over-reach in the round-2 write | **closed; the proved family-gain statement is still absent and is now stated as such** |
| **X-3–X-5, X-7** | **Four stated-versus-true repairs** (Table III caption; the Local-Hájek sentence; the blanket seed count; the Design-on/off family statement) — X-6 was closed on 2026-09-28 by the X-1 rewrite | removes false statements a reviewer can check in the PDF | **new 2026-09-27; zero compute** |
| — | ~~X-6: P3's hypothesis said to hold on SensorScope while A6 fails on both datasets~~ | the adjacent contradiction | **closed 2026-09-28** as a side effect of items 37–39 |
| — | ~~X-21: the audit's a-side clause read in the wrong form and at `a_max=40`~~ | a published reading that was wrong twice over | **closed 2026-09-28**; §7 item 38 |
| — | ~~Restate and rebuild the U-Air comparison~~ (N1–N4, N7) | **done 2026-09-27**; Tier 1 closed | §7 items 26–32 |
| — | ~~State the ceiling using F-1 + H/U1~~ | **done 2026-09-27**; §VII-F, 220 words, no page added | §7 item 33 |
| ~~1~~ | ~~**Report the endpoint-keyed Design rule**~~ — **done 2026-09-29 by §7 item 51**: eqs. (42) support gate + (43) switch point, `main.tex:2033–2076`; **and 2026-10-02 by item 52**, Proposition 4 gives the criterion's proved decomposition | `ccf-paper-writer` (applied) | the offered rule was declined on 2026-09-28 and accepted on 2026-09-29 in the two-equation form; item 52 adds the proved structure behind its `RMSE_μ` side; main stays 17 pp. |
| 2 | **State the attribution gap**: that the U-Air structural effect is carried by the Design factor and that the ablation family does not separate Debt-Cal's route to the same endpoint | closes the repair condition of review M8 | numbers in hand |
| 3 | ~~**Refresh the shipped bundle** `RAVEN_MCS_PUBLIC_REPRO_R1` so it matches the corrected tables~~ **done 2026-10-04 (Part V, §V.3)**: `w1/` added with 217 files and the three indexes rebuilt; `M7` closed, `Reproducibility` 2 → 3 | removed review M7, the only traceable score decrease | executed |
| 4 | **Obtain an exogenous target map** (D-2/D-3) | the only route that addresses P-a; nothing else substitutes | external, open |
| 5 | **Measure `U` somewhere** | converts T-f from "unmeasured" to "measured but small" | no block exists |
| — | ~~Make the construction harder~~ | **closed**: F-1 and U1 both ran; it does not raise the ceiling | §3 T8, §3A |
| — | ~~Use a positivity gate as the Design rule~~ | **closed**: A5 holds on U-Air, so such a gate would switch Design *on* there, into the 6.55 %-worse branch. **Distinct from the gate written on 2026-09-29** (item 51), which tests target-map emptiness of the delivered units rather than A5 | §7 open defects; item 51 |

## I.7 Action list in priority order

| # | action | owner | why now |
|:--|:---|:---|:---|
| X-1 | ~~Complete A6's clause list (or widen `ε_clip`, or weaken the statement)~~ **done 2026-09-28**: A6a/A6b, `ε_stab`, four-step proof, corrected audit readings | `ccf-paper-writer` (applied), `ccf-paper-reviewer` to audit | Part III III.9; §7 items 37–39 |
| X-2 | Narrow §VII-F's closing sentence to the tested oracle configuration | `ccf-paper-writer` | one sentence; Part III X-2 |
| ~~X-5, X-7~~ **both done 2026-09-29 by §7 item 50** (X-3 by item 45; X-4 by item 49) | `ccf-paper-writer` (applied) | all five stated-versus-true defects the external review named are now applied; X-5 and X-7 were wording-only and each kept its paragraph's line count | Part III III.4; §7 items 45/49/50 |
| X-4b | ~~Adjudicate the three disputed U-Air seeds, then re-source every cell that came from them~~ **closed 2026-09-29 by §7 items 46–48**: cause is mirror-versus-theta at an inactive final window, the theta copy is conformant, the cells are re-sourced, and the two residual mirror-sourced candidates (H grid, §VII-F class-internal) are checked — no paper number depends on them | done; X-4's wording stays in the row above | Part III III.5 |
| X-21b | Tooling still carries the wrong constant and the old clause form: `tools/a5_a6_support_audit.py` defaults to `--a-max 40` and reads `1/p^obs` | `ccf-integrity-auditor` | re-running the tool would contradict the corrected supplement; Part III III.9 |
| 1 | Add the endpoint-keyed Design rule and the support-cost mechanism | `ccf-paper-writer` | closes the "no rule for Design" gap the φ removal opened, at zero compute |
| 2 | State the attribution gap beside the U-Air structural claim | `ccf-paper-writer` | one paragraph; closes review M8's repair condition |
| ~~3~~ **done 2026-10-04** | ~~Refresh the reproduction bundle so it matches the corrected tables~~ executed under Option A (Part V, §V.3); three refresh defects stay open | `ccf-integrity-auditor` (applied) | `M7` closed; `Reproducibility` 2 → 3 |
| 4 | Enumerate the six scenarios and report `complete_counteracting` | `ccf-paper-writer` | read-only, already computed |
| 5 | Pursue an exogenous target map | external | the only route to P-a |
| 6 | Finish the bibliography verification (24 of 54 entries) and settle the desk items | `ccf-integrity-auditor`, `ccf-submission-checker` | packaging |

---

# Part II — Evidence, ledger, and boundaries

Section numbers 0–11 below are unchanged from the 2026-09-23 record so that other documents'
citations (`§3 T8`, `§2 L6`, `§4 S2`, `D-1`, `§7 items 18–21`, …) still resolve. The two new
sections are §2A and §3A.

## 0. Decision register

### D-1 — φ is withdrawn from the Design-switch role — DECIDED AND IMPLEMENTED

**Decided 2026-09-21. Implemented in the manuscript 2026-09-25 as Option 1 (§7 items 18–21).**
`φ` no longer appears anywhere in `main.tex`, `appendix.tex`, or `supplemental.tex`; the Design
factor is an explicit configuration and both settings are reported on both blocks.

`φ` currently decides, per block, whether the opportunity/design ratio is applied
(Algorithm 1: `Design_t ← ON` iff `φ = 0`). That role is withdrawn because φ is not a
deployment-target statistic. It measures **the overlap between the training pair set and the
test-split pair set**:

| block | what determines φ | verified? |
|:---|:---|:---|
| SensorScope | test-split pair set contains all 440 training pairs → φ = 0 | **verified numerically** |
| U-Air | 72 of 288 training pairs have no test unit → φ = 35.4% | **verified numerically** |
| T-Drive | supplement states the lookup is **test-split stratum frequency** | stated by the paper |
| City Scanner ×2 | φ = 0 **by construction** ("follows from positive regional μ, not from checking target-positive pairs") | stated by the paper |
| NSW-Traffic four-region | "four-region freeze"; provenance not established | **unverified** |

At least four of six blocks therefore set the switch by evaluation-split coverage or by
construction. Consequences: the Design/NoDesign assignment of every block loses its stated
justification; the U-Air forced-Design diagnostic now reads as "Design removes 35.4% of
training units because those cells are absent from the test split"; and any target-mass claim
that depends on φ must be suspended until an exogenous target map exists. The *observation*
that arriving data need not match a deployment target does not depend on φ.

### D-2 — the "public deployment target" must be re-sourced

`π^tar_{k,s}` is a **test-split** client–stratum mass, and the vector that weights `RMSE_μ` is
the **supported-test-unit count share**. Until an exogenous public target map exists,
target-mass claims should be restricted to blocks that have one, or restated as "target on the
reachable evaluation support".

### D-3 — the dataset search requirement was over-specified; the object needed is a target map

**Refined 2026-09-21.** A search for a single dataset that both records `O`/`U` **and** carries
data on `π^tar = 0` cells returned nothing, and it cannot succeed as posed:

1. **`π^tar` is a construct, not a dataset field.** No released dataset ships a deployment
   target, so "a dataset with `π^tar = 0` cells" is unsatisfiable by construction.
2. **Genuine zero target mass combined with arriving data is the normal case** under selection
   bias, not a rare commodity. It appears automatically once an exogenous target map is chosen.
3. **Measured `O` and `U` are platform operation logs.** Released research datasets publish
   sensor values, not task/upload logs, so the conjunction is structurally rare.

Recommended path, in order of cost: (i) keep the disclosed protocol-constructed `O`/`U`;
(ii) obtain an **exogenous public target map** for the two blocks that already have real `R`
(T-Drive, City Scanner) from a geographic or statistical source (population, POI/land use,
official monitoring objective) defined on the same cells; (iii) restrict target-mass claims on
SensorScope and U-Air to nothing, leaving them as protocol development tables. This needs no
new sensing data. It is a recommendation, not a decision.

### D-4 — layer provenance and construction parameters must be stated — DECIDED AND IMPLEMENTED

**Decided and implemented 2026-09-21 as P0.** The paper now states which layer is measured in
which block, that the four protocol blocks are semi-synthetic, and the construction constants;
and the abstract, the main-table caption and the limitations are scoped accordingly. See §2
L1–L5 and §7 items 12–15.

### D-5 — which revision route to pursue, if any

**Open.** The method-revision evaluation (2026-09-23) concluded that none of the three proposed
revisions can yield more than 1% on `RMSE_μ` on the existing protocol blocks, and reduced the
strongest of them to a **necessity test for P2** rather than a gain route. The one experiment
worth running is V1 on City Scanner Pilot 2 (see §3 T6 and §8 item 1).

### D-6 — the *difficulty* of the constructed regime must be declared, not only its provenance

**Decided 2026-09-24.** D-4 fixed *where the layers come from*. It does not fix *how much the
regime leaves to correct*. Because `p_obs` is two-valued and block-level (§2 L6), and because the
endpoint is nearly indifferent to the propensity pair even when both members are exact (§3 T3), the
protocol blocks pin the correction problem close to its easiest identifiable point. Publishing the
constants without
publishing the dispersion invites the reader to read the `+0.5%` tolerance as a property of the
method rather than of the generator — exactly the inference §3 T8 records as unsupported.

Consequence for the manuscript: wherever the construction constants appear, the **within-stratum
dispersion of the true propensities** must appear beside them, together with one sentence that the
reported predictive gains are therefore not bounds on realistic regimes. The dispersion is a
zero-cost number: for `O` it is 0, for `U` it is one value per client-window (§3 T8, F-3).

Status: **implemented for the dispersion, open for the mechanism.** F-3 was written into the paper
on 2026-09-24 (§7 items 16–17): the main text now states that both construction parameters are
constant within a stratum rather than varying per unit, and the A5/A6 audit section now reports the
two-valued observation rate and the per-client-window usable-update rate beside the constants.
F-1 and F-2, the re-runs that would test whether the regime *causes* the flat gains, are not run.

---

## 1. Root defect 1 — the deployment target is evaluation-derived

**R1 — φ is a train/test pair-coverage statistic.** On U-Air the target map has 288 keys: 216
carry `π^tar > 0` and equal the 216 test pairs exactly, while 72 carry an explicit 0 and equal
the 72 train-only pairs exactly. Of 5688 training risk units, 3672 (64.56%) are positive and
2016 (35.44%) are "present but zero"; **missing keys: 0**. On SensorScope the map has 440 keys,
all positive, equal to both pair sets, so φ = 0 by coverage coincidence.

**R2 — `RMSE_μ` degenerates to the unweighted pooled RMSE on SensorScope and U-Air.** The
per-unit weight is `μ^eval_{h(i)}/n_{h(i)}` and `μ^eval_g = n_g/N` exactly (all `μ_g × N` are
integers summing to N), so `w_i = 1/N`. Verified: the weight vector is uniform to 1e-12 on both
blocks, and `sqrt(Σ_g (n_g/N) RMSE_g²) = 7.9389` equals the published value to four decimals.
On the two main blocks the primary metric is not target-weighted at all.

**R3 — `Δ_group` uses the same count-share vector**, over 220 groups (SensorScope) and 144
(U-Air) rather than four.

**R4 — the manuscript claim versus the artifacts.** §VII-A.1 said the masses are "constructed
from the training split without test-label values" while the vector weighting `RMSE_μ` and
`Δ_group` is the supported-**test**-unit share. The clause was softened to "label-free masses";
the substance is unresolved and is D-2.

**Disclosure status.** The supplement does state that SensorScope and U-Air "look up test-split
client–stratum mass" and that T-Drive looks up test-split stratum frequency, and the current
§VII-A.3 states the `RMSE_μ` degeneration. What the paper never draws is the consequence: φ is
a coverage statistic, and the two main blocks' target weighting is vacuous.

---

## 2. Root defect 2 — the selection layers are constructed, and the compounding direction is designed in

Ranked second only because it is the same kind of defect as §1: the label does not match the
artifact. Its practical weight is comparable, because it supplies the *inputs* to every block.

**L1 — O and U are constructed in the four protocol blocks, and U is measured nowhere.**
Verified in `src/raven_mcs/e3/real_runner/generator_r3.py` (generator
`e3-complete-aligned-r3-v1`):

- **R**: every client receives exactly one opportunity event per window, so no client is ever
  opportunity-censored; the stratum is drawn from a **constructed** joint law
  (`build_joint_pi_opp`: equal client mass `1/|K|` times `exp(-1.25)` against time blocks
  {2,3}).
- **O**: designed Bernoulli, `p = clip(0.35 × scale, 0.05, 0.95)` with `scale = 0.55` on
  blocks {2,3}, giving 0.1925 there and 0.35 elsewhere.
- **U**: designed device-tier compute and network success (`compute_usable_r3`) with
  `align_disadvantage = True` on blocks {2,3} and staleness capped at `s_max = 5`.
- Each client-window draws at most four risk units.

| block | R | O | U |
|:---|:---|:---|:---|
| SensorScope, U-Air, NSW-Traffic | always-on, stratum from a constructed law | constructed | constructed |
| T-Drive | **real** (taxi trajectories) | constructed | constructed |
| City Scanner NYC PM2.5 | **real** (visit occupancy) | constructed | constructed |
| City Scanner Pilot 2 | **real** (visit occupancy) | **measured** (finite PM2.5) | constructed |
| INT-R (supplement) | **simulated** occupancy thinned to 0.425 | constructed | constructed |

Counts: R real in 3 blocks, O measured in 1, **U measured in 0**.

**L2 — what the paper says and does not say.** It says: Complete-aligned means "R, O, and U are
all active and non-random in the same direction" (§VII-A.2); "Original SensorScope and U-Air
traces are not claimed to contain mobile clients" (§VII-A.1, about R); "O and U stay controlled
except Pilot 2 measured O" (§VII-G); "not a jointly measured observation-and-network process"
(supplement). It does not say: that the four protocol blocks are semi-synthetic; the
construction constants; that the alignment direction is designed in; or that the scenario
family has six members (the supplement mentions "six risk-semantic scenarios" once and never
lists them, so `complete_counteracting`, in which U opposes R and O, is invisible).

**L3 — consequence: the mismatch that `Δ_group` measures is partly designed.** All three layers
are tilted against the same two time blocks, so the compounding misalignment is built rather
than observed, and `Δ_group ≈ 1.0` out of a maximum of 2 is largely a property of that
construction. Since `Δ_group` is one of the two endpoints the paper wins on, that win is doubly
qualified: self-referential (E1) and construction-driven (L3). **§4 partly answers this.**

**L4 — correction to this record's own earlier audit.** The A5/A6 audit's readings were
generator constants: `min p_obs_true = 0.1925 = 0.35 × 0.55` exactly, `min π^opp = 6.33e-4` is
the closed form of `build_joint_pi_opp`, and `q_use_true` is a Monte Carlo over a synthetic
prestate. The audit remains a valid statement about the released traces, but it carries **no**
information about any real sensing process, and my earlier review statement that "the
observation-side clause is satisfied" gave that evidence more weight than it has.

**L5 — the plan had it right, and the paper dropped the label.** The earliest design document
(`参考文件/RAVEN-MCS_V2.3_实验设计方案.docx`) declares the experiment nature as
**半合成受控实验 + 真实轨迹一致性实验**, places `p_obs` and `q_use` under `selection/` as
constructed objects, and states that short gaps are used only for the public reference and
"不作为客户端已观测". The provenance was therefore documented at plan level; the manuscript
carried over only the word "controlled". This is scope and labelling drift, not concealment,
and it is why the remedy is specification rather than a new dataset.

**L6 — the observation propensity is two-valued, and the release proves it.** In the released
audit (`artifacts/a5_a6_audit/audit_records.csv`, 28 800 rows, SensorScope + U-Air), `p_obs_true`
takes **exactly two values**, `0.1925` and `0.35`, and no others. The code explains why:
`generator_r3.py` lines 152–156 set `p_obs = clip(0.35 × scale, 0.05, 0.95)` with
`scale = 0.55 if block in {2,3} else 1.0`, where `block` is parsed from the unit's **target-group**
label. So `p_obs` is a function of the UTC block alone: it carries no client, no unit and no label
information.

The two-valuedness proves more than it first appears, because the recorded field is a **risk-set
mean**: `generator_r3.py` line 231 sets `p_mean = mean(p_obs_by_unit.values())` and line 240 stores
`p_obs_true = p_mean`, while the per-unit dict goes to a separate field,
`p_obs_true_by_unit` (line 241), which the audit does not read. Had any risk set ever mixed UTC
blocks, `p_mean` would have taken intermediate values strictly between `0.1925` and `0.35`. Over
28 800 events on two datasets it takes only the two extremes. **Every risk set is therefore
block-pure, so `p_obs` is exactly constant within every risk set and every opportunity stratum —
verified, not inferred.**

Two consequences the paper does not currently draw:

- **The Design and observation branch reduces to a two-parameter affine rescale** of the observed
  mass. `a = ζ̂^o / max{p̂^obs, p_min}` can take only two distinct values up to sampling noise in
  `p̂^obs`, so there is no high-dimensional propensity field to estimate and no propensity–label
  interaction to undo.
- **Within any opportunity stratum the propensity is constant**, because the UTC block is a
  component of the stratum label (`region::block::weekday`) as well as of the group label. The
  paper's stated assumption, "The main blocks assume within-stratum exchangeability,
  `ν^opp_{k,r}(i|s) = ν^tar_{i|s}`" (`main.tex` lines 1496–1499), is therefore **not at risk from
  the observation layer anywhere in the main tables**: the `O` layer contributes zero
  within-stratum tilt by construction. The only within-stratum discrepancy the generator can still
  create is the uniform-over-pool risk-set draw (`rng.choice(support, k = min(4, |support|))`)
  against the test-split target share. Prop. 2 and the design-ratio simplification are thus
  exercised only in the regime where their key assumption holds by fiat, not approximately.

**L7 — the usable-update propensity is a per-client-window quantity, and it is not label-dependent.**
Same file: `q_use_true` takes 1105 distinct values on `[0, 0.9815]`, at most **8 within any single
`(dataset, seed, window)`** — one per client. This is by construction: `U` is decided once per
client-window (`compute_usable_r3` is called once per client, `generator_r3.py` lines 161–172, and
all risk units in that client-window share the decision), the event row stores a single
`q_use_true` value per event (line 242), and `align_disadvantage` is again a
block-level flag. So the `U` layer does vary across clients and windows — it is not degenerate —
but it is driven by device tier, registration time and staleness, none of which depends on the
label. Against that, T3 shows that substituting true propensities for both estimated ones moves
`RMSE_μ` by **+0.008%** (SensorScope) and **−0.028%** (U-Air). That contrast is a joint oracle and
does not isolate `q`.

**L8 — the one real `O` measurement disagrees with the construction by 2.5×–4.5×, and the constant
moved without a record.** The only measured observation layer in the repository is City Scanner NYC
Pilot 2 (`o_layer = MEASURED_FINITE_PM25`, `p_obs_bernoulli = false`):

| quantity | value | source |
|:---|:---|:---|
| measured `O=1` share, joint O/U round | **0.871** (`measured_o0_fraction = 0.12908`) | `results_joint_ou/round_v1/INGEST_REPORT.json` |
| measured `O=1` share, path-A round | **0.859** (`measured_o0_fraction = 0.14071`) | `results_path_a_hajek/round_v1/INGEST_REPORT.json` |
| constructed `p_obs`, blocks {0,1} | **0.35** | `generator_r3.py` line 61 |
| constructed `p_obs`, blocks {2,3} | **0.1925** | `generator_r3.py` lines 155–156 |
| E1 balanced `O` | [0.15, 0.25] | `experiments/e1_entry.py` |
| E2 balanced `O` | 0.20, constant | `e2/generators.py` line 151 |

The denominators differ — the measured figure is the share of PM∪NO₂ union GPS cell-slots that
carry a finite PM₂.₅ value, whereas the constructed figure is a per-risk-unit Bernoulli
probability — so this is not a calibration error. It is the **absence** of a calibration: had the
constructed value ever been anchored to the only measurement the repository has, a one-directional
factor of 2.5–4.5 could not have survived unreported. The same repository also carries this
constant at three different values — `0.20` in `configs/scenario/*.yaml` and in
`semantic_alignment/complete_aligned_r2.py` line 87 / `protocol_closure/complete_aligned.py` line
102, `0.35` in the E3 runner that actually produces Table III, and `0.85` as the
`delivery_mode="high"` floor — and the `0.85` floor is the value closest to the measurement, in the
one configuration explicitly labelled "for non-degenerate correctness fixtures only"
(`generator_r3.py` lines 69–78).

**L9 — even the measured-`O` block runs on a controlled `U`, in the repository's own words.**
`scripts/ingest_joint_ou_cs_p2.py` (driven by `post_review/JOINT_MEASURED_OU_RANK/TARGET_SPEC.json`)
writes `results_joint_ou/round_v1/INGEST_REPORT.json`, which declares provenance per layer:
`r_layer = REAL_FROM_UNION_PM_NO2_GPS`, `o_layer = MEASURED_FINITE_PM25`,
`u_layer = CONTROLLED_EXPERIMENTAL compute_usable_r3 s_max=5`. The claim "`U` is measured in no
block" (§VII-A.2; §2 L1 above) is therefore not an inference from absence — it is the literal
content of that field, and the controlled substitute is the **same function** used in every
synthetic block. `sample_tau`'s docstring adds "P(age > S_max) ≈ 0.20 under this **controlled
design (not performance-tuned)**", and `q_true` has no closed form: it is estimated by
`estimate_q_true_mc(m=2000)`. A layer with no closed form and no measurement cannot have been
fitted to anything.

---

## 2A. Correctness defect — CLOSED 2026-09-27

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
| `N7` | Table III's `RMSE_μ` column mixes metric scales across datasets, undisclosed | **implemented**: §VII-A now states the U-Air and NSW-Traffic standardization ($\sigma=17.363$, $575.776$), that SensorScope is physical, and that ratio columns are scale-invariant |

Verification: `results_active_set_repair/round_v1/verify_report_claims.py` (137 checks, 139 with
`--deep`), `MANIFEST.sha256`, `EXPERIMENT_REPORT_FOR_VERIFICATION.md`,
`REVIEW_OF_REVIEW_20260927.md`.


## 3. Root defect 3 — the recoverable gain is capped, and the machinery is already near-oracle

This is the finding that explains why no endpoint separates the methods: the quantity the
correction family can act on is a small fraction of the observed gap. Sources:
`artifacts/e3_formal_runs_r1/runs/*/final_metrics.json` (20 seeds per block) and
`ccfa-review-reports/raven-mcs-method-revision-evaluation.md`.

**T1 — the two central references already differ by most of the gap.**

| block | Central-All | Central-Delivered | federal methods | RAVEN vs Central-All |
|:---|:---|:---|:---|:---|
| SensorScope | 7.6004 | 7.9291 | 7.9309–7.9399 | +4.45% |
| U-Air | 1.0556 | 1.1782 | 1.1882–1.2160 | +13.3% |
| traffic | 0.9538 | 0.9754 | ≈1.0035 | — |

`Central-All` trains on all valid observations with no `U` restriction; `Central-Delivered`
trains centrally on the delivered data with no correction. **They already differ by 4.3% and
11.6%**, i.e. the distance from the federal family to `Central-All` is dominated by **which
samples were delivered**, not by how they were weighted.

**T2 — no reweighting can recover a sample that was never delivered.** This is a structural cap
on the entire correction family (Design, O, U, P2, debt) taken together, not a defect in any one
of them. It is the same fact as E4's null `U` ablation seen from the other side.

**T3 — the plug-in propensity pair is not the bottleneck, and the null cannot be attributed to
either member.** `RAVEN-SimOracle` replaces **both** estimated propensities by their true values: a
single flag, `uses_oracle_propensity`, gates the usable map (`rec.oracle_q`, `window_runner.py`
lines 426–430) and the atomic observation map (`p_obs_true_by_unit`, lines 707–727). Against the
reference `RAVEN` the contrast on `RMSE_μ` is **+0.008%** (SensorScope, sd 0.070% of the baseline
mean) and **−0.028%** (U-Air, sd 0.265%), re-derived over the same 20 paired seeds from
`artifacts/e3_formal_runs_r1/runs/*/*/final_metrics.json`. Nothing measurable follows from exact
propensities, which is a stronger statement than the earlier `q`-only reading and is the one the
evidence supports. What it does **not** support is naming the usable-update layer as the irrelevant
one: no arm in the repository separates `p` from `q`, so the null may be carried by either or by
both, and settling that needs an oracle-`p`-only and an oracle-`q`-only arm
(`raven-mcs-f1-experiment-design.md` §4.1). The rest of T3's role in this record is unchanged.
F-1 measured the split directly rather than leaving it open: on `RMSE_μ` under the published
construction the observation member alone is worth **−0.005%** (SensorScope) and **+0.017%** (U-Air),
so the usable member accounts for roughly **+0.013%** and **−0.045%**. Neither carries the null.

**T4 — prediction is insensitive to the aggregation weights.** On U-Air seed 30001 over 80
windows, P2 moves `α` away from `β̂` by a mean L1 distance of **0.337** (max 1.256), while
`RMSE_μ` barely moves. A large change in the aggregation composition produces a negligible
change in prediction.

**T5 — the scenario family agrees.** Across all six risk-semantic scenarios (§4 S2), `RMSE_μ`
spans 1.0042–1.0050 (**+0.08%**) while `RMSE_ρ` spans 1.0085–1.0304 (**+2.2%**). The whole
designed selection shift is worth 0.08% of target risk.

**T6 — P2's own off-switch already beats it, inside the paper's own baseline list.**
`TwoStageHajekAggregator.compute_server_weights` returns `_normalize(payload.beta_hat)`
(`src/raven_mcs/aggregation/methods.py` lines 314–320). It is therefore **exactly RAVEN's
reference with P2 switched off**, sharing the identical `β̂`, so the only difference from RAVEN
is the P2 projection plus debt. On **City Scanner Pilot 2**, the one block with measured `O`:

| method | `RMSE_μ` | `Δ_group` |
|:---|:---|:---|
| TwoStage-Hájek (= `β̂`, no P2) | **0.7097 ± 0.0204** | 0.0607 ± 0.0206 |
| RAVEN-Design | 0.7135 ± 0.0206 | **0.0465 ± 0.0119** |

The P2-off member is **0.54% better on prediction** (sd 0.45%; RAVEN wins 2 of 10 seeds). In the
other direction, Table IV's Inst row **is** `λ_g = 0` with P2 retained (Gen2): on U-Air it makes
`RMSE_μ` significantly worse by `+0.131%` and `Tail_RMSE` by `+0.136%`; on SensorScope it is not
significant. **So both available "P2 off" and "P2 weakened" configurations have already been
run, and neither supports a predictive value for P2.**

**T7 — the ceiling and what would raise it.** The honest expected gain from any reweighting-based
revision on these blocks is under 1%, below the paper's own 0.5% practical threshold. A larger
gain would require one of: (i) model misspecification in the direction of the shift, since with a
correctly specified model equal weighting is asymptotically optimal; (ii) a target law whose
total-variation distance from the arrival law is large **and** an evaluation weighted by that law
rather than by unit counts; or (iii) a downstream decision that depends on group-level error. On
the existing blocks, method-to-method gaps above 1% occur only where `R` is real (T-Drive: 1.6%;
Pilot 2: about 1.2%).

**T8 — the construction regime is a candidate *cause* of the flat gains in T1–T7, and that claim is
testable.** T1–T7 measure the ceiling; §2 L6–L9 describe the generator. The link between them is a
hypothesis, recorded here with its mechanism and its falsification test rather than as a finding.

The mechanism splits into three claims that can fail independently:

- **H-A (identifiability is built in).** With `p_obs` two-valued, block-level and constant within
  stratum (L6), the observation-side correction has two parameters to estimate and no
  propensity–label interaction to remove. Under a correctly specified constant propensity, inverse
  probability weighting is unbiased and equal weighting is asymptotically optimal — this is exactly
  T7(i). A sub-1% separation between the corrected and the uncorrected families is therefore what
  theory predicts *for this generator*, independently of whether RAVEN would separate on a
  realistic one.
- **H-B (the endpoint is insensitive to the axis the method acts on).** `RMSE_μ` responds to the
  residual mass error, which is at the `10^-3` level, not to the designed tilt magnitude (0.55).
  T4 (P2 moves `α` by mean L1 0.337 with `RMSE_μ` flat) and T3 (exact propensities move `RMSE_μ` by ≤0.03%)
  are two instances. The reported gain is thus dominated by terms the construction does not manage.
- **H-C (real propensities are harder on both axes at once).** A real `O`/`U` would plausibly have
  many distinct, label-correlated, occasionally-zero propensities (device and NIC heterogeneity,
  missing-not-at-random connectivity or battery, scheduled sampling). That raises the *achievable*
  gain above 0.5% while simultaneously raising the risk that a plug-in propensity is misspecified.
  The constructed regime pins the first axis at its easiest point and does not control the second.

**Consequence for how the headline may be read.** If H-A–H-C hold, the `+0.5%` tolerance is
**neither a lower nor an upper bound** on the gain in a realistic regime: the protocol blocks are
too easy to falsify the method and too insensitive to confirm it. That is weaker, and more
defensible, than either "the method works" or "the construction inflated the gain".

**Outcome, 2026-09-24: H-A is refuted, H-B stands.** F-1 ran. Making the selection law harder on the
axis the observation correction acts on raised the value of an exact propensity by 15–21×, from
0.005%/0.017% to +0.104%/−0.251%, which confirms H-A's mechanism. The amplified figure is still
2–5× below the paper's own 0.5% practical threshold, and on U-Air it carries the wrong sign, so the
constructed regime is not what caps the gain. What remains is H-B: the endpoint is close to
indifferent to the weights, which is also what the Stage A ceiling map shows from the other side
(every propensity route ≤0.03%; the only large route on U-Air is deletion, −6.55%).

**Falsification, at near-zero data cost.** Three tests, in increasing cost, all on existing code:

1. **F-3 (one number, available now).** Report the within-stratum dispersion of the true
   propensities beside the construction constants. For `O` it is **0** by L6; for `U` it is one
   value per client-window by L7. Published next to `0.35` and `0.55`, this lets the reader see the
   difficulty directly. No re-run. **Done 2026-09-24** in `main.tex` §VII-A.2 and the `appendix.tex`
   A5/A6 audit (§7 items 16–17).
2. **F-1 (re-run the aligned arm; one experiment). — RUN 2026-09-24, H-A REFUTED.** The test as
   first written here could not work, for a structural reason established in
   `raven-mcs-f1-experiment-design.md` §0: in E3 the opportunity stratum is nested inside the target
   group (`h(i) = s93::block0`, `s(i) = s93::block0::weekend`), and E3's `tail_score` analogue *is*
   the block, so an E2-style block-indexed score would be stratum-constant and would reproduce the
   existing construction under a new name. The executed manipulation therefore moves the propensity
   inside the stratum, on the unit's `time_index` tercile, at a per-block marginal held to machine
   precision (`|Δ| ≤ 5.6e-17`). The decisive endpoint is the within-trace contrast
   `RMSE_μ(plug-in) − RMSE_μ(exact p)`, which removes the model-capacity confound that the
   originally stated RAVEN-vs-baseline criterion carries.

   Result, 160 runs over 20 paired seeds, harness reproducing the `raven` cell to 0.0000%:
   `Δ_oracle` is **+0.104%** (SensorScope, 4.7 σ) and **−0.251%** (U-Air, 2.1 σ) on the harder trace,
   against −0.005% and +0.017% on the published one. Both are inside the pre-registered 0.5% bound,
   and U-Air carries the wrong sign, so **H-A is refuted**: the constructed regime is not what caps
   the gain. The mechanism is nevertheless confirmed in direction, since making the selection law
   harder raised the value of an exact propensity by 15–21×. Full readout in
   `raven-mcs-f1-experiment-design.md` §5.4; artifacts `artifacts/e3_f1_theta1_r1` (harder trace)
   and `artifacts/e3_f1_score_dependent_r1` (published trace).

   **Anchor caveat (added 2026-09-24, see T9).** Both arms ran the `raven` policy. That is the
   paper's table method on SensorScope, but on U-Air `raven` is the *forced-Design* diagnostic row
   (1.1911) while Table III's U-Air method is `RAVEN-NoDesign` (1.1131). The U-Air column of F-1
   therefore describes the forced-Design configuration, not the deployed one. The E1 verdict is
   unaffected, because the contrast is within a single trace and a single policy with only the
   propensity map varying, but the U-Air figure must not be read as a statement about the paper's
   U-Air method. Re-running the U-Air arm against a design-removed base needs a
   `raven_wo_design_oracle_p` policy and is not done.
3. **F-2 (the same, for `U`).** Add a unit-level component to `q` plus an occasional true zero, and
   compare it against a new **oracle-`q`-only** arm: T3's existing contrast is a joint oracle and
   cannot serve as the baseline. If exact `q` still does not matter, the `U` branch has no
   predictive role under either regime and T6's conclusion strengthens. The flag split this needs
   is the one F-1 already requires (`raven-mcs-f1-experiment-design.md` §4.1).

With F-1 executed, the only proposed experiment left in this record that could **raise** the observed
gain is F-2, and §8 item 8 records why it is now low value.

**T9 — the ceiling map, measured (Stage A, executed 2026-09-24; U-Air anchor corrected 2026-09-24).**
Before F-1 was implemented, every improvement route the existing artifacts can price was read off
them: the `raven` cell (`artifacts/e3_formal_runs_r1/runs`) against the E4 one-factor ablations
(`artifacts/e4_core_mechanism_ablation_r1/runs`), paired on the 20 formal seeds. `delta%` is
(ablated − reference)/reference; σ is |mean| over the standard error of the paired difference.

**Anchor correction.** The first version of this table used `raven` as the reference on *both*
datasets. That is wrong for U-Air. `method_policy.py` defines `raven` = `_RAVEN_CORE` +
`gate_mode="always_on"`, so its design ratio is applied unconditionally; a repository-wide search
finds **no φ in the E3 runner path at all**, and the published `config_snapshot.json` for the two
datasets differs only in `n_groups_frozen` (220 vs 144) and the target artifact. Table III is
explicit: on U-Air it reports `RAVEN-NoDesign` = **1.1131** as the table method and labels
`raven`'s 1.1911 as `RAVEN-Design (forced)`, a diagnostic row (`main.tex` lines 1754–1757,
1821–1822). 1.1131 is exactly `runs/uair/raven_wo_design`. So on U-Air the reference for anything
called "the paper's method" is the design-removed run, and the column below is a **forced-Design
factorial**, not a price list against the deployed configuration.

| module changed | SensorScope `RMSE_μ` | U-Air `RMSE_μ` (forced-Design factorial) | SensorScope `Δ_group` | U-Air `Δ_group` | σ (`RMSE_μ`, SS / UA) |
|:---|---:|---:|---:|---:|:---|
| remove design (ζ̂ + Gate) | +0.005% | −6.553% | +1.237% | −6.943% | 0.3 / 10.0 |
| remove observation IPW | +0.012% | −0.010% | +0.096% | +0.123% | 2.5 / 1.0 |
| remove usable IPW | +0.012% | +0.024% | +0.026% | +0.014% | 2.5 / 1.1 |
| remove Inst (P2 group term) | **−0.090%** | **+2.086%** | +2.110% | +2.494% | 1.6 / 6.4 |
| remove debt | +0.000% | +0.001% | +0.014% | +0.004% | 0.1 / 0.7 |
| exact `p` and `q` (joint oracle) | −0.008% | +0.028% | +0.200% | −0.017% | 0.5 / 0.5 |

**Two claims from the first version are withdrawn.**

1. *"On U-Air the largest available move is deletion: dropping the design branch buys 6.55%."* This
   is not headroom. The paper **already deploys that branch on U-Air**, and Table III already
   reports both rows side by side with the reversal explained (`main.tex` lines 1757–1760, 1933).
   It is a branch assignment the φ rule makes, not an unexploited improvement. The row stays in the
   table because it is the correct price of *forcing* Design on U-Air, which is what the `raven`
   cell is.
2. *The U-Air reference bounds.* Against the actual table method (1.1131) rather than the forced row,
   `Central-Delivered` (1.1782) is **5.85% worse**, not 1.10% better, and `Central-All` (1.0556) is
   **5.17% better** and unreachable by reweighting. On U-Air the deployed method therefore already
   beats uncorrected central training and every federal baseline in the tree (1.1882–1.2160).

**What survives.** The SensorScope column is anchored correctly: the table method there is
`RAVEN-Design` = the `raven` cell = 7.9380, and every module is worth at most 0.09%, the only
non-trivial one negative. The propensity family is ≤0.03% on both datasets, which on U-Air is now a
statement about the design-removed base. Note that the E4 tree carries **no** design-removed module
factorial, so the four other U-Air rows cannot be re-anchored from existing artifacts; they must be
read as a forced-Design factorial or re-run. `remove Inst` matches `twostage_hajek` to four decimals
on U-Air (both 1.2160, in the forced factorial), which is where the "the whole RAVEN-versus-`β̂`
gap is the P2 group term" reading came from, and that reading inherits the same anchor caveat.

Overlap: the Design-removal and Inst rows restate Table IV's existing rows. What is new is placing
all five modules and three endpoints in one σ-annotated frame.

---

## 3A. The headroom experiments — H (round_v1) and its U-Air extension U1

Placed here because it is the decisive evidence for §3: two pre-registered experiments that separate
"the estimator is lazy" from "the space does not exist". Pre-registration:
`ccfa-review-reports/raven-mcs-h-headroom-preregistration.md` (revisions 1 and 2 frozen before the
runs they govern). Design of the extension: `ccfa-review-reports/raven-mcs-uair-headroom-design.md`.
Artifacts: `results_h_headroom/round_v1/` (180 runs) and `round_u1/` (270 new runs, 45 new traces).

**H1 — the question and the rule.** `H = (RMSE_μ(FedAvg) − RMSE_μ(oracle)) / RMSE_μ(FedAvg)` on
paired arms and the same EventTrace. Six conditions move one knob at a time plus one combination:
opportunity tilt `θ ∈ {1.25, 2.5, 4.0}`, tail observation scale `∈ {0.55, 0.25, 0.10}`, a
diurnal-blind backbone, and a block-uniform target law. The arms are `fedavg_window`,
`raven_simoracle` (true `p`, true `q`, Design on) and a NoDesign oracle added by revision 1. The rule
was frozen before any stress run: **GO** iff some `c ∈ {C1…C5}` has `H ≥ 0.5 %` **and** CI lower
bound `> 0`; otherwise **STOP**, which the pre-registration states formally withdraws the claim that
the correction family can improve prediction on these protocols.

**H2 — round_v1, 5 seeds, 180 runs: STOP, with one conclusive half.** `H_DECISION.json` records
`decision = STOP`, `go_cells = []`. SensorScope is conclusive: all six point estimates lie in
[−0.03 %, +0.08 %] with a paired-difference MDE of **0.17–0.36 pp**. U-Air is not: its MDE is
**1.38–1.91 pp**, which cannot exclude a 1 % effect, and U-Air is the only block with an effect whose
CI excludes zero.

**H3 — U1, U-Air extended to 20 seeds: the rule could fire and did not.** 270 new runs, 45 new
traces, seeds 30006–30020, the five original seeds reused bit-identically (`|diff| = 0.000e+00` on
all three metrics). Revision 2 froze the U-Air oracle arm to the NoDesign arm, which is inert
(`H ≡ H_nodesign` in every cell). The gate was re-run at the new seed 30006 and `raven_simoracle`
reproduced the frozen value at `abs_diff = 0.00e+00`.

| condition | `H_nodesign` at 20 seeds [95 % CI] | at 5 seeds | shift | MDE | GO threshold | GO |
|:---|---:|---:|---:|---:|---:|:---|
| C0 frozen | **−0.2166 %** [−0.7154, +0.2822] | +0.22 % | −0.44 pp | 0.70 pp | 0.50 % | no |
| C1 strong tilt | **−0.0044 %** [−0.5378, +0.5291] | **+0.77 %** | **−0.78 pp** | 0.75 pp | 0.53 % | no |
| C2 extreme tilt | **+0.0371 %** [−0.5281, +0.6023] | −0.07 % | +0.11 pp | 0.80 pp | 0.57 % | no |
| C3 low capacity | **−0.2107 %** [−0.7094, +0.2881] | +0.24 % | −0.45 pp | 0.70 pp | 0.50 % | no |
| C4 block-uniform | **−0.2161 %** [−0.7155, +0.2833] | +0.22 % | −0.44 pp | 0.70 pp | 0.50 % | no |
| C5 combined | **+0.0283 %** [−0.5360, +0.5926] | −0.09 % | +0.12 pp | 0.80 pp | 0.56 % | no |

Every point estimate satisfies `|H| ≤ 0.2166 %`, an order of magnitude below the bar, and all six sit
below revision 2's 0.30 % band floor, so the pre-registered escalation to 45 seeds is **not run**.
**C1 is the headline: the cell the source report flagged as closest to GO collapses from +0.77 % to
−0.0044 %.** The apparent near-breach was small-sample noise. SensorScope stays at 5 seeds because
its MDE is already 0.17–0.36 pp.

**H4 — the one stable effect is a support loss, not a weighting gain.** Design carries the target-mass
ratio `ζ̂ = π^tar/π^opp`, which drives the weight of any `(client, stratum)` with `π^tar = 0` to zero;
on U-Air that discards 72 of 288 pairs. Measured on the *oracle* arms, so it is not estimator failure:

| condition | U-Air support cost [95 % CI] | SensorScope |
|:---|---:|---:|
| C0 | **+7.356 %** [+6.032, +8.681] | −0.020 % |
| C1 | **+7.186 %** [+6.007, +8.376] | +0.022 % |
| C2 | **+6.317 %** [+4.769, +7.865] | +0.011 % |
| C3 | **+7.366 %** [+6.036, +8.696] | −0.018 % |
| C4 | **+7.388 %** [+6.062, +8.715] | −0.023 % |
| C5 | **+6.308 %** [+4.751, +7.865] | +0.011 % |

All six U-Air lower bounds exceed **+4.75 %** (minimum **+4.751 %**, C5); SensorScope is ≈0. The cost is
invariant to the tilt strength, the backbone and the target law (C0 ≈ C3 ≈ C4 ≈ +7.37 %; C1 ≈ +7.19 %;
C2 ≈ C5 ≈ +6.31 %), i.e. it is driven by the dropped support alone. This supplies the mechanism §7's
open-defect list said was missing, and it is the fact behind the endpoint-keyed Design rule in Part I,
Tier 5 rank 2.  **θ re-sourcing (2026-09-29, §7 item 48):** the four conditions C0/C1/C3/C4 use the ten
H-grid runs whose final window does not aggregate, so their support costs are recomputed at the θ copy
(were +6.968/+6.989/+6.980/+6.991 %); C2 and C5 have no triggered run and are unchanged. The H column
the paper quotes is unaffected — on U-Air it is pinned to the Design-off oracle, whose runs are clean,
and its six cells reproduce bit-identically after the correction. `results_seed_path_audit_r1/C9_H_THETA_RECHECK.{csv,json}`

**H5 — what this establishes.** The ceiling in §3 is **not** an artifact of an easy testbed. Two
independent manipulations reach the same verdict: F-1 (§3 T8) hardened the observation propensity
*inside* the stratum, at a marginal held to 5.6×10⁻¹⁷, and got `Δ_oracle` = +0.104 %/−0.251 %; H/U1
stressed the opportunity tilt, the observation level, the backbone capacity and the target law under
a pre-registered bar and got no GO anywhere. H-A (the construction is the cause) is refuted; H-B (the
endpoints are nearly blind to the weights) is what remains.

**H6 — the caveat, and what is still open.** The realized U-Air sd (1.07–1.21 pp) landed at the top of
the projected range, so the realized MDE is **0.70–0.80 pp**, slightly worse than the projected
0.55–0.76 pp. The correct statement is: 80 % power excludes true effects of ≈0.75 pp or more, and C2
and C5 have 95 % upper bounds at +0.60 %, so those two cells do not yet exclude a true effect of about
0.5 % at 95 %. The source report's sentence "±0.03 % is the spatial ceiling" should therefore be
scoped to SensorScope or restated as "at 20 seeds every point estimate has `|H| ≤ 0.22 %` and the
pre-registered GO rule did not fire". Not run: revision 2's U2 (45 seeds), and no `U` measurement.

---

## 4. The scenario family is already complete, and it partly answers §2

**S1 — Verdict: the six scenarios are fully tabulatable from existing results, with no re-run.**
`artifacts/e2_traffic_formal_runs_r1/` holds 600 result cells = **6 scenarios × 5 methods × 20
seeds**, `status = PASS` for all 600, with no duplicates.

| column needed | file | field |
|:---|:---|:---|
| per (scenario, method, seed) RMSE_μ / RMSE_ρ / gap | `formal_results.csv` | `RMSE_mu`, `RMSE_rho`, `Gap_mis` |
| pre-aggregated mean/std/median/IQR/CI95 | `formal_statistics.csv` | 4 metrics × 30 cells |
| per-group RMSE → WorstGroupRMSE | `formal_group_metrics.csv` | `group`, `RMSE` (6×5×20×4) |
| per-scenario paired tests (Raven vs 4 baselines × 3 metrics) | `paired_comparisons.csv` | Wilcoxon + CI + wins/losses + p |
| solver and denominator diagnostics | `formal_runtime_metrics.csv` | `P2_solver_failure_count`, `denominator_zero_count` |

`Gap_mis = RMSE_μ − RMSE_ρ` is pre-computed per row, so Δ_μ, Δ_ρ and the generalised
difference-of-differences `D(S) = Δ_μ(S) − Δ_ρ(S)` (paired by seed, reference = `balanced`) are
available for every scenario.

**S2 — the computed family table** (means over 5 methods × 20 seeds; `D` over 100 paired values):

| scenario | RMSE_μ | RMSE_ρ | Gap_mis | **D(S)** | seeds with D < 0 |
|:---|:---|:---|:---|:---|:---|
| balanced | 1.0042 | 1.0085 | −0.0042 | — | — |
| opportunity_only | 1.0043 | 1.0142 | −0.0099 | −0.00572 | 60/100 |
| observation_only | 1.0044 | 1.0196 | −0.0152 | −0.01096 | 81/100 |
| usable_only | 1.0044 | 1.0140 | −0.0095 | −0.00531 | 65/100 |
| **complete_aligned** | 1.0050 | 1.0304 | −0.0254 | **−0.02115** | 87/100 |
| complete_counteracting | 1.0043 | 1.0210 | −0.0167 | −0.01249 | 74/100 |

The reproduced `complete_aligned` value **−0.02115 matches the manuscript exactly**, which
validates the read path against the published number.

**S3 — the three layers add up, which supplies the control that §2 L2/L3 said was missing.**
Single-layer ΔGap is −0.0057 (opportunity), −0.0110 (observation) and −0.0053 (usable), summing
to −0.0220, against the measured aligned ΔGap of −0.0212, i.e. **96% additivity**. The
counteracting scenario is predicted by `opp + obs − usable = −0.0114` against a measured
−0.0125. So the compounding misalignment is not a black box: it is the sum of three separately
controllable layers, and `usable_only` contributes the least, consistent with T2 and E4.

**S4 — the core claim is robust across the family, but the reported magnitude is the maximum.**
`D < 0` in all five non-reference scenarios, so the arrival-versus-target distinction is
directionally robust beyond the single aligned arm, which is a genuine strengthening of the
Prop. 1 premise. However `|D|` spans −0.0053 to −0.0212, a factor of four, and **the paper
reports the largest value**. Power also varies sharply: `opportunity_only` is negative in only
60/100 seeds, which is barely above chance, while `complete_aligned` reaches 87/100.

**S5 — the headline tolerance endpoint carries no scenario information.** WorstGroupRMSE across
the six scenarios spans 1.1740–1.1767 (range 0.0027) while the per-scenario seed standard
deviation is 0.010–0.017, so the scenario effect is **four to six times below the noise**.

**S6 — two prerequisites before any scenario table is published.**
First, `paired_comparisons.csv` carries `multiple_comparison_policy = none_familywise…`, i.e.
**no family correction**; the paper's existing Holm discipline must be applied. Second,
**`Δ_group` and `Δ_c-s` are absent from the E2 tree**, which holds only RMSE_μ, RMSE_ρ,
`Gap_mis` and per-group RMSE.

**S7 — relation to E5.** E5 shows `D ≈ −Δ_ρ` with method-invariance; S4 adds
scenario-dependence of magnitude and the maximum-selection problem. Both critiques stand.

---

## 5. Earlier problems of equal weight, independent of §1–§4

IDs are stable labels, not a rank. E1, E2 and E6 bear most on the verdict.

**E1 — the two endpoints that carry the wins are the functional the method minimizes.**
`Δ_group(R) = ‖ω̄_R − μ‖₁` is the time average of the quantity whose instantaneous squared form
enters P2 with the debt term on the same μ; `Δ_c-s` measures distance to the same `π^tar` the
reconstruction factor reproduces. The one non-self-referential endpoint, `RMSE_μ`, shows no
separation on any block (SensorScope spans 7.9293–7.9389 across five methods; U-Air
1.1120–1.2160, RAVEN-NoDesign third of six). S5 adds that the whole scenario family moves
`RMSE_μ` by only 0.08%.

**E2 — the comparator set contains no external method, and two of its members are RAVEN
constructions.** `TwoStage-Hájek` is `_normalize(β̂)` (T6), i.e. RAVEN's reference with the
calibration removed. `ObsUse-Window` is the authors' own ablated variant: its aggregator docstring
says "no design ratio, Hajek local loss, (P2), or debt", and with observation rates equal to one
it coincides with `FedAU-Window` to 1e-12. These two are the comparators for the headline `+0.5%`
worst-group tolerance (`+0.44%`, `+0.48%`). `TimeAlign-Agg` is "in the spirit of" a 2026 TMC paper
that uses **the same three datasets** (SensorScope, U-Air, NSW-Traffic) and is explicitly not an
official reproduction. `FedAU-Window` adapts a method whose original evidence is CIFAR/SVHN/CINIC
image classification.

**E3 — the sharp theory does not cover the evaluated system.** Prop. 3 needs A6, and the
supplement's own audit reports A6 failing on both datasets (the `q_min` floor active on
5.22%/5.18% of observed windows; `1/q^use > d_max` on 24.22%/23.75%). Prop. 2 covers the ideal
pooled estimator under A1–A3 only.

**E4 — the deployed-configuration ablation shows no practically meaningful positive effect.**
Excluding the U-Air Design row, which ablates a configuration the paper does not deploy, the
remaining rows give: Obs `+0.123%*` on `Δ_group` and not significant elsewhere; Use
`+0.014 / −0.014 / +0.024 / +0.025`, all non-significant; Inst `−0.089 / −0.143` on the
structural endpoints with `+0.131%* / +0.136%*` on prediction; Debt `+0.004%* / +0.002%*`.
Nothing clears the paper's own 0.5% minimum-practical-effect bar. On SensorScope, Design
`+1.237%* / +0.597%*` is the only component above that bar and it moves prediction by `+0.005%`;
Obs is significantly **harmful** on `Δ_c-s` (`−0.070%*`).

**E5 — `D_aligned` collapses to its own second term.** `corr(D, Δ_ρ) = −0.9988`,
`sd(D)/sd(Δ_ρ) = 0.975`, `sign(D) = −sign(Δ_ρ)` in 98/100 seeds, and the statistic cannot vary
with the method (all five give `−0.02115 … −0.02137`). The stated null is not the theory's null:
the target law is fixed across the two arms while the arrival law moves by scenario design.

**E6 — the P2 component's predictive value is already contradicted by the paper's own numbers.**
See T6: the P2-off member (`TwoStage-Hájek`) is 0.54% better than RAVEN on the measured-`O`
block, and the P2-weakened member (`λ_g = 0`) is significantly worse on U-Air. The clean
attribution (identical `β̂`, difference is exactly P2 plus debt) makes this hard to explain away
by any other component.

---

## 6. Degeneration and component removal: what the derivation covers

**G1 — the assumption class already admits partial degeneration.** A4 requires `λ_β > 0` and
permits `λ_g, λ_v, λ_s ≥ 0`. Thm. 1's strong convexity comes only from the reference-penalty
term ("`J_r` is `λ_β`-strongly convex"), so zeroing an aggregate weight leaves existence and
uniqueness intact. Prop. 3's P2 step uses the reference non-expansion, whose inequality chain
contains only `λ_β`. Code agrees: `aggregation/feasibility.py` requires
`λ_group ≥ max_server_learning_rate` when instantaneous calibration is on and only `λ_group ≥ 0`
when it is off. So the Inst / Debt / variance / staleness degenerations are **inside** the
analysed class.

**G2 — O-off and U-off are outside the theory.** They change the estimator, not the program.
Prop. 2 presumes the ideal ratios at all three layers, so nothing states what `β̂` estimates once
a factor is deleted; and Prop. 3 is a small-perturbation result of order `ε`, whereas deleting
an inverse-propensity factor is an `O(1)` change.

**G3 — no rule for when to degenerate.** The only switch is φ, now withdrawn (D-1). No result
selects a degenerate variant.

**G4 — what the removal data actually shows.**

| removal | endpoints (relative %) | significant? | φ branch? | covered by theory? |
|:---|:---|:---|:---|:---|
| U-Air Design | Δ_group −6.943, RMSE −6.553, Tail −6.875 improve; Δ_c-s +4.990 worsens | yes | **yes** (U-Air deploys NoDesign), so not a new degeneration | yes, as a rule branch |
| U-Air Inst | Δ_group −0.089, Δ_c-s −0.143 improve; RMSE +0.131, Tail +0.136 worsen | gains **not** significant, costs significant | no | G1 only; no selection result |
| U-Air Use | Δ_c-s −0.014, rest positive | none | no | no |
| **SensorScope Obs** | Δ_c-s **−0.070** improves, Δ_group +0.096 | **significant** | no | **no** |
| SensorScope Inst | Δ_group −0.260 improves (ns), Δ_c-s +0.310 worsens | mixed | no | G1 only |
| both Debt | both endpoints +0.014 / +0.004 worsen | significant but tiny | no | G1 |

The only **significant, non-φ** degeneration benefit is SensorScope Obs removal improving
`Δ_c-s` by 0.070%, and Obs has opposite signs across blocks.

**G5 — ablation-definition drift, which must be settled before any degeneration claim.**
`e4/wo_inst_final/evidence.py` records: Gen0 — "original E4 wo_inst **skipped P2**"; Gen1 — "used
`lambda_beta=1e-8` != E3 full-RAVEN `lambda_beta=1.0`"; Gen2, the one behind Table IV — keeps P2
with `λ_group = 0` and `λ_β` matched to full RAVEN. "Removing Inst" therefore names two different
experiments across generations.

**G6 — warning for any future automatic degeneration rule.** Keying such a rule on the reported
endpoints would deepen the circularity of E1. Any such mechanism needs pre-registration, a
held-out selection criterion, and family correction.

**G7 — the proposed revision routes, as evaluated.** The method-revision evaluation (2026-09-23)
examined three proposals: (i) shrink P2's group term toward the arrival law by `μ_λ = (1−λ)ρ + λμ`;
(ii) replace the φ switch by a continuous Design factor; (iii) estimate composite balancing
weights directly instead of multiplying three inverse factors. Conclusions:

- **Route (i)** remains the strongest but must be rewritten: only the `λ_g`-shrinkage version keeps
  the estimand; the `μ_λ` version changes it and needs a new assumption (frozen, split-independent
  mixing law) and a bias–variance proposition that does not yet exist. Its `λ = 0` endpoint is
  **not** `ObsUse-Window`, and `λ_g ∈ (0,1)` with instant calibration on violates the shipped
  feasibility constraint. **It is already partly run**: `λ_g = 0` is Table IV's Inst row.
- **Route (ii) does not work as stated.** `0^γ = 0` for `γ > 0`, and Yamada's
  `r_α = p/(αp + (1−α)p')` gives `r_α = 0` when `p = 0`. Neither literature supplies a floor at
  `π^tar = 0`; Yamada bounds the ratio **above** by `1/α`. A floor requires replacing the target
  law by a mixture `π_κ = (1−κ)π^tar + κ π^opp`, which changes the estimand, and it necessarily
  keys on test-split coverage (R1), so it does not resolve D-1.
- **Route (iii)** overlaps P2's own group term, degenerates to post-stratification
  (`w_s = π^tar_s/ρ̂_s`) when the moments are strata indicators, would drive `Δ_group` toward zero
  by construction (E6/E1), and aims at weight-estimation error that T3 has already ruled out as
  the bottleneck.
- **Internal-consistency constraint discovered:** routes (i) and (ii) are the same "target
  mixing" operation applied at different layers. If both are used, `κ` and `λ` must be bound to a
  single mixing law, otherwise `β̂` and P2 chase different estimands.

---

## 7. Changelog — paper modifications since the previous review round

Boundary: after the 2026-09-12 review. All in `TO_OVERLEAF_paper_tmc_r1_clean/`.

| # | change | where | basis | status |
|:--|:---|:---|:---|:---|
| 1 | A5 split into **A5 (positivity and shared support)** and **A6 (inactive stabilization and bounded plug-in error)**; Prop. 3 restated under A1 and A4–A6; scope sentence that `ε_clip` is retained; U-Air reversal attributed to A6 | `main.tex` §VI-A/E, §VII-G; `appendix.tex` | the old A5 mixed qualitative positivity with quantitative bound-inactivity, and only the latter is empirically false | done |
| 2 | New supplement section **"Support-Hypothesis Audit for A5 and A6"** with the per-dataset table and a limits paragraph | `appendix.tex` | reports A5 holding and A6 failing on the released traces | done |
| 3 | §IV-E and §VI-F **splice grammar** repaired; §VI-F first two clauses back-reference §IV-E; "can be false-safe at rate α" corrected to a bound | `main.tex` | ungrammatical where appendix pointers had replaced citations | done |
| 4 | **Assumption 1** trimmed: the "not assumed globally" sentence deleted as entailed | `main.tex` §VI-F | added no condition beyond the `g`-conditioning | done |
| 5 | `\COMMENT{scope; does not prove Assumption A}` → `Assumption~1` | `appendix.tex` algorithm | placeholder name in a shipped algorithm | done |
| 6 | **§VII-A.1 group map corrected**: `h(i)` = spatial unit × four UTC time blocks, 220 / 144 groups, label-free masses | `main.tex` | manuscript said four groups; the runs used the spatial×time map | done |
| 7 | **§VII-A.3 metric definitions added**: `RMSE_μ` display with weight law; three distinct vectors `μ`, `μ^eval`, `μ^blk`; the SensorScope/U-Air degeneration; `WorstGroupRMSE` as the max of four UTC-block scores; `Tail_RMSE` as the frozen late-day blocks 2–3; `RMSE_ρ` as the same functional with arrival weights | `main.tex` §VII-A.3 | none of these were defined | done |
| 8 | Table I column header `\|G\|` → `WG blocks` | `main.tex` | the four UTC blocks are the aggregation level of `WorstGroupRMSE`, not the dataset's group count | done |
| 9 | §VII-D under-served check uses `μ^blk_b` instead of `μ_g` | `main.tex` | separates the four-block marginal from the group marginal | done |
| 10 | **`Δ_group` definition made readable**, including the ℓ1 reading and `0 ≤ Δ_group ≤ 2` | `main.tex` §IV-D | it was an unnumbered inline formula whose prose name did not match the symbol | done |
| 11 | `reference.bib` restored (54 entries, ICLR/INFOCOM attribution intact) | `reference.bib` | truncated to 0 bytes; see §9 | done |
| 12 | **§VII-A.2 new paragraph (P0)**: which layer is measured in which block; the four protocol blocks are semi-synthetic; construction constants; and the scoping sentence that the Table III structural-alignment results are conditional on the construction | `main.tex` §VII-A.2 | L1–L3; the paper disclosed "controlled" but never the construction | done |
| 13 | Abstract: "a Complete-aligned protocol" → "a **protocol-constructed** Complete-aligned selection" | `main.tex` abstract | D-4 | done |
| 14 | Table III caption: "This is a protocol development table on station traces, not a real-mobility ranking." → "…station traces **whose `O` and `U` layers are protocol-constructed**…" | `main.tex` | D-4 | done |
| 15 | §VII-G: "`O` and `U` **stay controlled** except Pilot 2 measured `O`." → "`O` and `U` **are protocol-constructed** except Pilot 2 measured `O`." | `main.tex` | D-4 | done |
| 16 | §VII-A.2 (the P0 paragraph): added that **both construction parameters are constant within a stratum** rather than varying per unit, naming the two mechanisms (observation rate set by the UTC block that the stratum already fixes; usable-update rate drawn once per client-window), and the scoping sentence that the reported predictive gains describe this construction rather than the range attainable when selection varies at the unit level | `main.tex` §VII-A.2 | D-6, L6–L7, T8 F-3 | done |
| 17 | A5/A6 audit section: new paragraph reporting the **dispersion** of the two selection margins on the released traces — the observation rate takes only `0.1925` and `0.35` over all `28800` records and is therefore stratum-constant, and the usable-update rate is drawn once per client-window and shared by that window's at most four risk units | `appendix.tex` §"Support-Hypothesis Audit" | D-6, L6–L7, T8 F-3 | done |
| 18 | **D-1 implemented (Option 1). Method restated without a data-derived switch.** Equation (32) is retained in its slot but now defines the **Design factor** `ζ̂^o = π^tar / max{π̂^opp, π_min}` when `D_t = on` and `= 1` when `D_t = off`, with `D_t ∈ {on, off}` a configuration supplied to Algorithm 1. Algorithm 1's φ line and its `IF φ = 0` branch are replaced by `IF D_t = on`; the algorithm now produces only `θ_{t+1}` and `Q_{t+1}`. §V-E and the §V-C preamble state that the factor is configured before the window opens, that the two settings differ nowhere else, that both are reported, and that a data-derived selector would have to be justified on the evaluation it changes. The zero-target statistic survives only as a descriptive number in the supplemental material | `main.tex` §V-C, §V-E, Algorithm 1, eq. (32) | D-1, Option 1 | done |
| 19 | **Table III completed into a within-dataset Design factorial.** One row added: SensorScope `RAVEN-NoDesign` `RMSE_μ` 7.9384 ± 0.0468, `WorstGroupRMSE` 8.6711 ± 0.0481, `Δ_group` 1.0265 ± 0.0278, `Δ_c-s` 1.2719 ± 0.0308. `WorstGroupRMSE` is not stored in `final_metrics.json`; it was recomputed from the saved checkpoints with the `run_int_r_v2.py` path, and the recomputation **reproduces the published `RAVEN-Design` four-block row to 4×10⁻⁵** (7.4903 / 7.5864 / 8.6707 / 8.2075, WG 8.6707) before being applied to the new row. The U-Air `RAVEN-Design (forced)` label becomes `RAVEN-Design`. Caption rewritten to report the trade: Design is worth +1.237% `Δ_group` and +0.597% `Δ_c-s` on SensorScope at unchanged prediction, and costs 6.553% `RMSE_μ` / 6.943% `Δ_group` / 6.875% tail on U-Air while improving `Δ_c-s` by 4.990% (17.1σ) | `main.tex` Table III | D-1, §3 T9 anchor correction | done |
| 20 | The same factorial added to the appendix four-block table: SensorScope `RAVEN-NoDesign` = 7.4907 / 7.5868 / 8.6711 / 8.2079, WG 8.6711 ± 0.0481; U-Air `RAVEN-Design (forced)` relabelled `RAVEN-Design`; caption and the surrounding assignment sentences rewritten as reported settings rather than a rule | `appendix.tex` `tab:app_block_rmse` | D-1 | done |
| 21 | **Abstract, contributions, §I, §VII, limitations and the whole appendix de-φ'd.** The abstract states the two settings trade off across endpoints with the measured numbers; contributions and §I report the factor as an explicit configuration; the appendix section `Frozen φ Assignments…` becomes `Target-Coverage Statistic and City Scanner Hybrid Rankings`, its table caption and column header demote the statistic to descriptive provenance and record the Design setting *used* rather than *selected*; every "RAVEN-Design if and only if φ = 0", "Design is withheld (φ = 47.4%)" and "forced RAVEN-Design" is replaced by the corresponding configuration statement | `main.tex`, `appendix.tex` | D-1, Option 1 | done |

Side effects of the whole change set: main text **15 → 16 pages** (page 15 saturated; page 16
holds roughly nine reference lines, and the P0 paragraph did not add a page). Equation numbering
unchanged at 41, so the 67 frozen literals in `appendix.tex` remain valid;
`tools/freeze_appendix_refs.py --check` reports 0 to freeze and 0 unresolvable. Supplement clean
(0 overfull, 0 undefined). Main carries only the pre-existing 5.6 pt log-only overfull. Em
dashes: 2, both pre-existing.

Items 16–17 left every one of those invariants where it was: main **16 pages**, supplement
**15 pages**, equation labels **41**, `tools/freeze_appendix_refs.py --check` reports 0 to freeze
and 0 unresolvable (56 appendix-internal references kept), 0 undefined references or citations, em
dashes still 2, and the only overfull box is the same pre-existing 5.63672 pt one. The 144 added
words return `PASS: 144 words; em dashes 0/3; 0 issue(s)` from
`CCFA-Skills/ccf-paper-writer/scripts/check_prose_quality.py`; both added passages were verified
present in the built PDFs by text extraction, not only in source.

Items 18–21 (Option 1) left the build invariants where they were: main **16 pages**, supplement
**15 pages**, equation labels **41**, 0 LaTeX errors, 0 undefined references or citations,
`tools/freeze_appendix_refs.py --check` reports **0 to freeze and 0 unresolvable** (57
appendix-internal references kept), 0 overfull boxes above 2 pt, em dashes in `main.tex` still 2 and
in `appendix.tex` 0. Equation (32) kept its number, which is why the frozen literals in
`appendix.tex` did not move; the freeze tool's only conversion was `\eqref{eq:design_factor} → 32`.
A source-level ripgrep over all three `.tex` files returns **no `\phi`**, and a text extraction of
both built PDFs returns **no** `forced RAVEN-Design`, `RAVEN-Design (forced)`, `frozen heuristic`,
or `Design fraction`.

### Record corrections — 2026-09-27 (this file only; no manuscript change)

Four corrections from the N-forensics round. **Nothing in `TO_OVERLEAF_paper_tmc_r1_clean/` was
edited**, so every build invariant in items 18–21 still holds.

| # | correction | evidence |
|:--|:---|:---|
| 22 | **§2A N3 rewritten, and its status changed from `open` to root-cause located.** The item previously claimed a 0.35 % printed-versus-recomputed gap. The printed `1.1882` **is** the E3 tree's ALL20 mean `1.188238` (0.003 %). The real defect is mixed sourcing: `RMSE_μ`/`Δ_group`/`Δ_c-s` from the E3 run tree, `WorstGroupRMSE` from `RAVEN_MCS_PUBLIC_REPRO_R1/tables/TABLE_II_WORSTGROUP_PER_SEED.csv`, the two disagreeing at seeds 30007 / 30016 / 30018 by 2–5 %, with 30016 and 30018 inside the TEST window | `artifacts/e3_formal_runs_r1/runs/uair/*/final_metrics.json`; the repro CSV; per-seed diff in §2A N3 |
| 23 | **§2A N4 corrected from a hidden defect to a disclosed redundancy.** `Local-Hájek` is **bit-identical** to frozen `FedAvg` on both datasets (not merely equal to four decimals), and the manuscript already states the coincidence and its cause in the paragraph following Table III | per-seed identity in both frozen sources; `appendix.tex` prints `1.1882` for both rows |
| 24 | **New §2A N7: the `RMSE_μ` column mixes metric scales across datasets.** SensorScope is `IDENTITY_RAW_PHYSICAL` / `zscore_applied: false` / no sigma; U-Air is `OFFLINE_LINEAR_CONVERSION` / `zscore_applied: true` / `sigma = 17.36325121670317`. Exact recovery: `1.188238 × 17.36325121670317 = 20.631670`, the U-Air `FedAvg-Window` value in the sealed source, so the sealed source stores the **physical** domain and is not itself wrong. Also: all three policies declare `store_fields: [RMSE_mu_std, RMSE_mu_phys, MAE_mu_std, MAE_mu_phys]` but **no** `final_metrics.json` carries any `*_std`/`*_phys` field | `artifacts/e3_formal_runs_r1/runs/*/*/metric_scale_policy.json` (220/220 sensorscope, 220/220 uair, 120/120 traffic); key census over every `final_metrics.json`; `manuscript_evidence_closure_r1/01_table_sources/TABLE_II_E3_MAIN_EFFECTIVENESS_FINAL.csv` |
| 25 | **§2A N2 given its metric attribution; N1–N7 renumbered to one scheme.** The `−6.17 %` / `−9.11 %` sentence is `WorstGroupRMSE`, **paired**, **TEST**, measured against the contaminated batch; on that metric against equal-delivery comparators it is `+0.48 %` (`FedAU`) / `+0.44 %` (`ObsUse`). Separately, Part I had used N4 for the forced-Design finding while §2A used N4 for `Local-Hájek`; the forced-Design item is now **N6** in both places | exhaustive match over {metric} × {reference} × {source} × {window} × {aggregation} reproduces −9.11 %/−6.17 % to 0.002 pp as WG-paired-TEST10 on the repro source |

Also carried forward, unchanged in substance but no longer "unlocated": the `RAVEN-Design` row is the
**forced-Design** run, and its equal-delivery gap to a clean FedAvg (`1.1119`) is **+7.12 %**, so the
printed same-batch comparison `1.2630` versus `1.2596` **understates** the U-Air Design cost.

### Manuscript write — 2026-09-27 (route A repair) and 2026-09-28 (Proposition 3 repair)

| # | change | where |
|:--|:---|:---|
| 26 | U-Air `FedAvg-Window` row replaced with the licensed-set values: `1.1882→1.1119`, `1.2596→1.1690`, `1.1218→1.0446`, `1.2621→1.3138` | `main.tex` Table III |
| 27 | `tab:app_e3_uair`: FedAvg, FedAsync, TimeAlign and Debt-Cal rows replaced; caption now states that each row uses the active set its own definition licenses | `appendix.tex` |
| 28 | `tab:app_block_rmse` UA `FedAvg-Window` row replaced with `1.1015 / 1.1144 / 1.1690 / 1.0721`, WG `1.1690` | `appendix.tex` |
| 29 | `tab:app_p2_coverage` U-Air row: `70.10 / 63--75` → `72.61 / 63--79` | `appendix.tex` |
| 30 | the `TEST $-$9.11 % / $-$6.17 %` sentence replaced by a within-Design-family statement (RAVEN-Design vs TwoStage-Hájek, $2.46\%$, $10/10$) plus the six-comparator `Δ_group` qualification; the development-table summary's `FedAvg/TwoStage-Hájek` claim corrected | `main.tex` §V |
| 31 | the Local-Hájek coincidence attributed to the shared Design-support restriction | `main.tex` §V |
| 32 | metric scale disclosed: U-Air and NSW-Traffic standardized ($\sigma=17.363$, $575.776$), SensorScope physical, ratio columns invariant (closes N7) | `main.tex` §VII-A |

Build invariants after item 32: main **16 pages**, supplement **15 pages**, equation labels **41**,
0 undefined references or citations, 0 overfull boxes above 2 pt,
`tools/freeze_appendix_refs.py --check` reports 0 to freeze and 0 unresolvable (57 kept), em dashes
in `main.tex` 2 and in `appendix.tex` 0.

Still not written: the three feasibility-audit counts (778 warnings / 85 runs / 6438 windows /
$2.686\times10^{-8}$). Their population is not the 180-run set that `tab:app_p2_coverage` covers, so
the effect of substituting the rebuilt methods cannot be determined without a solver-log re-audit.
Reporting them unchanged is deliberate; inventing replacements is not an option.


| 33 | **New §VII-F "Recoverable-Gain Ceiling".** States the headroom definition $H$, the pre-registered $0.5\%$ GO rule, that it did not fire on either block, the SensorScope MDE of $0.17$--$0.36$ points, the U-Air $20$-seed re-run with $\vert H\vert\le0.217\%$ and its $0.70$--$0.80$ point MDE caveat, and the F-1 hardening result ($15$--$21\times$, $0.104\%$ / $0.251\%$, H-A refuted). Closes review M2/M5 and the open-defect rows for the ceiling and the F-1 result. 220 words; main stays **16 pages** | `main.tex` §VII-F |


| 34 | **Erratum: an open-defect row added on 2026-09-27 was wrong and has been removed and replaced.** It claimed that Table IV's U-Air `Inst` row contradicted the E4 arm it names, quoting a tree mean of `1.119606` against the printed `-0.089`. In fact `artifacts/e4_ablation_semantic_integrity_repair_r1/E4_WO_INST_FINAL_DECISION.json` (2026-08-12) records `proven_invalid: true` with `authorized_corrective_reruns: 40` and the reason "Parent raven_wo_inst skipped P2 by setting alpha=beta when uses_instant_calibration=False". The tree arm's `p2_invocation_states.json` is empty (`3` bytes) where every sibling arm logs 0.87-1.23 MB, confirming P2 never ran. The 40 corrective reruns reproduce Table IV to four decimals (`UAir_Delta_group` `-0.0894 %`, `Holm p = 0.105`). **Table IV is correct; the tree arm is the superseded one.** The row is replaced by the real residual (`wo_inst` fix unfinished at `counterfactual_audit._solve_alpha`) | this file; `results_active_set_repair/round_v1/EXPERIMENT_REPORT_FOR_VERIFICATION.md` SS0.3; `ccfa-review-reports/raven-mcs-tmc-review.md` M8/M9 |


| 35 | **Part III written: the external review recorded, ranked and cross-mapped.** The advisor-supplied GPT review (2026-09-27; `main(6).pdf` 16 pp. + `supplemental.pdf` 15 pp.; **4/10 weak reject**, confidence 4/5) is kept verbatim at `ccfa-review-reports/raven-mcs-unspecified-venue-review.md` and recorded as **Part III** in twenty ranked items (X-1…X-20) under a stated ordering rule. Six items were verified against the shipped `.tex` and artifacts in this workspace; the rest are marked *reported only*. It reopens one correctness question (**X-1**, P3/A6) and names five stated-versus-true defects in the current build (**X-3**…**X-7**). **No manuscript file changed** | this file; `ccfa-review-reports/raven-mcs-unspecified-venue-review.md` |

| 36 | ~~**Record correction: the frozen E3 tree and the route-A rebuild disagree at three U-Air seeds, for five arms the repair did not touch.**~~ **Restored 2026-09-29 (the row was lost in an earlier edit of this file) and its framing corrected by item 46.** Found while verifying X-4, not raised by the external review. `E2_UAIR_CELLS.csv` reproduces the frozen `final_metrics.json` **exactly at 17 of 20 seeds** for `local_hajek`, `inst_cal`, `raven`, `raven_simoracle` and `twostage_hajek`, and differs at **30007 / 30016 / 30018** by 2–5 % of `RMSE_μ` — the same three seeds §2A N3 flagged for source mixing, two of them (30016, 30018) inside the TEST window. The frozen tree is intact: all 20 disputed `final_metrics.json` files match `E3_CANONICAL_HASH_MANIFEST.json` (11 752 entries, round `E3-FORMAL-RUNS-R1`). **What was wrong here:** stage E2 does not retrain, so this is not a second pipeline; the seeds, arms and magnitudes were right and the cause is the mirror-versus-theta effect of item 46 | `artifacts/e3_formal_runs_r1/E3_CANONICAL_HASH_MANIFEST.json`; `results_active_set_repair/round_v1/E2_UAIR_CELLS.csv`; Part III III.5 |

| 37 | **Manuscript write (authorized): the Proposition 3 repair — Part III X-1, with X-6.** First authorized edit of the 2026-09-28 round; `snapshots/2026-09-28-pre-prop3-fix/` holds both files beforehand. `main.tex`: A6 split into **A6a** (inactivity at the true margins, with the ceiling clause on `π^tar/(π^opp p^obs)` under Design on and `1/p^obs` under Design off, and the note that `d_max ≤ 1/q_min` makes the last clause imply `q^use ≥ q_min`) and **A6b** (the three interpolation bounds that keep `ε_π, ε_p, ε_q` defined); `eq:eps_clip` replaced **in place** by `eq:eps_stab` (`ε_stab,r = ‖β_r^T − β_r^⋆‖₁`, still equation **37**); Proposition 3 now assumes A1, A4, A5, A6b + `1^⊤b_r^T ≥ B_min` + shared `A_r, M_r, C_r` and concludes `C₁(ε_π+ε_p+ε_q) + ε_stab,r` with `C₁=(2K_rn_r/B_min)(d_max·max{L_π,L_p}+a_max·L_q)`; two corollaries and the "C₁ is vacuous at `π_min=10^{-6}`" note added; the §VII-C scope sentences and the §VII-G limitation rewritten, which also **closes X-6**. `appendix.tex`: `eq:g4_c1` replaced, the proof of Proposition 3 rewritten in four steps that never use A6a plus the support lemma, the proof-obligation summary updated. 41 numbered equations preserved, so every frozen literal in `appendix.tex` still resolves | `TO_OVERLEAF_paper_tmc_r1_clean/main.tex`, `appendix.tex`; Part III III.9 |
| 38 | **Tool-supported write: the audit's a-side clause corrected, and its constant corrected (X-21).** The published audit read the observation-side clause as `1/p^obs ≤ a_max`, which does not bound `ζ̂^o/max{p̂^obs,p_min}`, and evaluated it at `a_max=40` although `run_e3_real` calls `build_full_runner` without overriding any weight-safety constant (`runner.py:471–484`), so the E3 runs resolved **20** (defaults at `window_runner.py:1433–1437`); `40` belongs to the E1-R2 calibration and the E2 traffic runner. The audit table's A6 row is replaced by two decisive rows (Design off: `max 1/p^obs`; Design on: `max ζ/p^obs`) plus an `ε_stab` row, and the conclusion paragraph now states that the clause **fails on U-Air** (23.47 > 20, on 2.74 % of active client-windows) while holding on SensorScope (19.26). **The earlier "the failure is a property of the usable-update stage" narrative is withdrawn**: under Design on the opportunity stage contributes through the composite ceiling. Read-only audit `results_prop3_audit/round_v1/`; **no experimental results table touched** | `TO_OVERLEAF_paper_tmc_r1_clean/appendix.tex`; `results_prop3_audit/round_v1/A5A6_EPS_STAB.{json,md}`, `compute_a5a6_eps_stab.py`, and the independent `compute_eps_stab.py` / `EPS_STAB.json` |
| 39 | **Record correction: the two published statements in item 38 were wrong, and the constant in the *tooling* is still wrong.** `tools/a5_a6_support_audit.py` defaults to `--a-max 40` with a comment calling 40 the frozen formal value, and it computes `n_obs/p_obs_true.clip(p_min)` as the a-side weight; re-running it would therefore contradict the corrected supplement. Recorded as **X-21b** in I.7 and left unfixed, because the 2026-09-28 instruction limited the write to the two `.tex` files. Also recorded: the repair costs one page on the supplement (**15 → 16 pp.**; main unchanged at 16 pp.), with 0 errors, 0 undefined and 0 overfull | `tools/a5_a6_support_audit.py:125–127`; `results_prop3_audit/round_v1/`; Part III III.9 |
| 40 | **Detail-level notation pass (user-requested, 2026-09-28/29).** The user audited the paper page by page and asked, for each symbol, whether it was assumed known; in every case it was simply undefined. Nine rounds of edits, all inside `main.tex` except one appendix line, none touching a claim, number, table, result or equation index (still 41 equations; the stabilization error is still (37), the feasible set (25), the P2 objective (28)): **(a)** theta, Theta, f_theta, Y_i and C^dep defined in §III-A, with the codomain and the learned object, and a now-redundant Y_i versus varpi^tar disambiguation sentence removed; **(b)** gamma_r > 0, E_loc and the post-step parameter defined in §III-B, and the squared loss at its first use in §III-E; **(c)** S_max defined in §III-B, and the lowercase s_max in §VII-A plus four appendix construction notes unified to it; **(d)** the group and stratum codomains G and S defined as sets, with h and s written as mappings from units; **(e)** the deployment domain I_dep defined in §III-C; **(f)** the probability operator Pr defined where eqs. (2)–(3) use it; **(g)** the indicator written as bold-1 in three places, with a definition at first use in both documents; **(h)** the feasible set and the calibration program named at the first occurrence of omega = M alpha. Verification: both documents 0 error, 0 undefined, 0 overfull; the appendix reference freeze still reports 0 to freeze and 0 unresolvable; both files LF. **Cost: main 16 to 17 pp.** | `TO_OVERLEAF_paper_tmc_r1_clean/main.tex`, `appendix.tex`; the open-defect row list below |
| 41 | **Notation items deliberately left open.** `h(i)` is still used in the Related Work (§II, two occurrences) before §III-B defines it; the indicator `\mathbf{1}{·}` and the all-ones vector `\mathbf{1}` still share a glyph (disambiguated by context only); and the user declined (2026-09-28) the offered endpoint-keyed Design rule, so **M1 stays open by decision**, not by omission | §7 open-defect table; I.6/I.7 |
| 42 | **Manuscript write (authorized, plan "c"): §VII-F re-grounded on the aggregate class, closing X-2.** The user rejected the first draft of the fix because it took the external review's *narrow-the-statement* branch and satisfied none of the three conditions the review asked for (method class, performance criterion, upper bound). Plan (c) instead binds the ceiling to the class the paper already defines: weights in `C_r` of (25), selected by (P2), scored by `RMSE_mu`. Opening sentence no longer says "reachable by any correction in this family"; the closing no longer says "bounds what any later claim about the correction family can reach". The published H facts (GO rule, not fired, both MDEs, F-1 $15$–$21\times$) are unchanged word for word. Added: the **clean class-internal comparison** (one calibrated member, only the observation and usable-update margins swapped) with paired $95\%$ intervals over $20$ seeds, and the composition-level anchor \eqref{eq:g4_comp} plus Proposition 3. New evidence, no new experiment: `results_ceiling_class_r1/compute_ceiling_class_paired.py` → `CEILING_CLASS_PAIRED.json` (read-only). Verified: main **17 pp.** (unchanged by this edit), 0 error, 0 undefined, 0 overfull, **41** equations (`eq:Cr`=(25), `eq:g4_comp`=(40) cited correctly), em dashes still 2, `check_prose_quality.py` reports no hard failure | `TO_OVERLEAF_paper_tmc_r1_clean/main.tex:2073–2113`; `results_ceiling_class_r1/` |
| 43 | **The three routes to a *proved* family-gain statement, with cost estimates (user-requested, 2026-09-29).** §VII-F now bounds the data side and the perturbation side; the class's total achievable gain is still **measured only** (I.3). Three routes, estimated before any work: **W3**, a metric-level formal bound, needs more than a metric-Lipschitz step: changing α changes the model trajectory, while Proposition 3's non-expansion holds at a *fixed window state*, so the missing link is a **training-stability assumption**; 2–5 days, no experiment; expected reviewer effect low to moderate, because at `π_min = 10⁻⁶` the constant is vacuous and the external review states that wording cannot buy credit. **W4**, a mechanism for why the calibrated members absorb margin-estimation error while an uncalibrated member of the same class does not, needs one mechanism paragraph plus a **read-only** surrogate computed from existing per-window artifacts; 1–2 days, and a full dose–response version would need a TwoStage-Hájek arm added to the H grid (3–7 days of compute); expected effect moderate to high, because it identifies *which part of the class* does the work and answers W1/C2. **W-α**, an oracle over the weights themselves optimised against the evaluation metric, is the only route that yields a *measured upper bound over the class*; the last-window surrogate needs the final window's local updates re-trained (2–4 days) and the full-trajectory version needs retraining per candidate α (weeks). Decision recorded: run the **W4 read-only surrogate first**; hold W3 unless a training-stability assumption is authorized | this file; `results_ceiling_class_r1/`; I.3 |
| 44 | **W4 read-only surrogate executed; the absorption mechanism it was meant to support is not supported, and §VII-F was corrected the same hour.** `results_ceiling_class_r1/compute_calibration_absorption.py` → `CALIBRATION_ABSORPTION.json` (read-only, frozen artifacts only, no solver, no training). Measured per active window over 20 seeds: the reference perturbation `e_ref = ‖β̂_r − β_r^T‖₁` has median **0.171** (SensorScope) / **0.077** (U-Air), p95 **0.789** / **0.658**, max **1.155** on both; the arm identity "TwoStage-Hájek normalizes the reference" is confirmed to machine precision (the largest coordinate gap between `α` and `β̂` is `2.2e-16`), so for that arm the whole reference perturbation reaches the aggregate composition (`d_comp = e_ref`); Local-Hájek moves **more** (median 0.379 / 0.180, max 1.597) because its weights are not the normalized reference; and for the calibrated arms the *provable* composition bound `‖M_r‖₂·e_ref` is the **same order** as those exact uncalibrated changes, because `‖M_r‖₂ ≈ 1` on these traces. **Consequence:** the sentence written minutes earlier ("the calibrated members absorb a margin estimation error that this member of the same class does not") is not supported and has been replaced by the two facts it can carry: the margin swap is *not* small before aggregation, three of the four members are metric-neutral under it on U-Air, and the fourth responds by 2.04 % although its composition change is no larger than Local-Hájek's. The flat prediction endpoint therefore does **not** come from accurate margin estimates. Main stays 17 pp., 0 error, 0 undefined, 0 overfull, 41 equations, em dashes 2, prose check with no hard failure | `main.tex:2097–2113`; `results_ceiling_class_r1/CALIBRATION_ABSORPTION.json`; §7 item 43 |
| 45 | **Manuscript write (authorized, X-3): Table III's tolerance sentence scoped to the settings that meet it.** The user first re-checked whether Table III declares the 2×2 at all; it does, **in words**: caption `main.tex:1862–1863` ("Both Design settings are reported on both blocks, so the table is a within-dataset factor rather than a single configuration"), carried by two RAVEN rows per dataset (`1889–1890`, `1897–1898`). The strings "2×2" and "factorial" never appear in the paper, which is why a keyword search misses it; the word "within-dataset factorial" is this record's own (I.5, D-1). The defect was the neighbouring sentence, now scoped: SensorScope both settings and U-Air RAVEN-NoDesign stay inside the descriptive `+0.5 %` worst-group line; **U-Air RAVEN-Design is outside it at `+7.9 %` and `+8.0 %`** (against FedAU-Window `1.1701` and ObsUse-Window `1.1692` from the table's own rows), matching §VII-G's one-setting-per-block statement at `2128–2129`. Verified: main **17 pp.** (unchanged), 0 error, 0 undefined, 0 overfull, 41 equations, em dashes 2, prose check with no hard failure; caption confirmed in the built PDF p. 13 | `TO_OVERLEAF_paper_tmc_r1_clean/main.tex:1862–1873`; Part III III.4 |
| 46 | **Seed-path audit (design + execution): record item 36's framing was wrong, the mechanical cause is located, and the affected cells are enumerated.** Design and all results in `results_seed_path_audit_r1/` (`DESIGN.md`, `A0_CODE_DIFF.md`, `A1_INACTIVE_FINAL_SWEEP.csv`, `A2_PATH_COMPARISON.csv`, `B_TWO_COPY_CAPTURE.json`). **A0**: the run-time source revision is available (`recovered_source/window_runner.py`, `f7bff5e30c…` = the ledger's `method_source_hash`) and has the *same* model/theta sync semantics as the current tree (sync only in the active path); revision, batch, and damage are all refuted (`runner_source_hash`/`method_source_hash`/`git_commit` identical across all 20 seeds, timestamps continuous, trace/checkpoint/metrics all sealed). **A1**: the trigger is a **final window that does not aggregate** — seeds `{30007, 30016, 30018}` in every U-Air tree (E3 27/180 runs, E4 12/100, E1 6/86), zero in FedAU/ObsUse and **zero in every SensorScope tree**, so there is no replication block. **A2**: an implementation written independently from the published definition reproduces the round's re-evaluated cells exactly (controls agree to 0.0000 %; the three triggered seeds differ by −2.0 %…+5.1 %), and the E1 repair tree shows the same divergence with byte-identical checkpoints. **Stage B** (one instrumented rerun, U-Air/raven/30007, checkpoint hash reproduced exactly): at metric time the live module differs from `theta` by a largest parameter gap of `0.0348`, `RMSE_mu` = **1.142487** from the live module (the tree's stored value) versus **1.189413** from a fresh module loaded with `theta` (the E2 / public-repro / independent value). So the divergence is a **mirror-versus-theta** effect: the run-time metric evaluates the in-memory module, not the parameter vector the run saves. **Verdict per the pre-registered rule:** the `theta` copy is paper-conformant, the three tree cells are superseded, and the route-A G1c ruling ("the tree is the source, the repro CSV is the outlier") does not hold at those seeds. **Affected printed cells:** Table III's U-Air RAVEN-Design row, `tab:app_e3_uair`'s five Design-on rows, and the U-Air ablation rows using `raven_wo_{inst,obs,use,debt}`; clean are SensorScope, U-Air FedAvg/TwoStage/FedAU/ObsUse/**RAVEN-NoDesign**, the four rebuilt appendix rows, and the central rows. **Impact:** the five Design-on 20-seed means move `+0.338 %…+0.372 %`, so derived percentages and X-4's Local-Hájek question need recomputation. **No manuscript file changed by this audit** | `results_seed_path_audit_r1/`; §7 item 36; Part III III.5 |

| 47 | **Manuscript write (authorized, 2026-09-29): the mirror/θ re-sourcing applied to the affected U-Air cells, the tabular and textual consequences, and the figure pipeline.** Deliverable and full per-cell list: `results_seed_path_audit_r1/C3_CELL_DIFF.md` (`C3_CELL_DIFF.csv`, `C_IMPACT_RECALC.csv/.json`, `C4_T4_STATS.csv`, `C7_E3_ARMS_THETA.csv`); scripts `c_impact_recalc.py`, `c3_cell_diff.py`, `c4_t4_stats.py`, `c5_w1_recompute.py`, `c6_wg_relatives.py`, `c7_e3_arms_theta.py`, `c8_apply_figure_data.py`. **Rule applied:** only the three triggered seeds need re-evaluation (the other 17 agree), so each corrected mean is `(17 frozen + 3 θ)/20`. **Changed in `main.tex`:** Table III U-Air TwoStage `1.2160±0.0716 → 1.2202±0.0672` and RAVEN-Design `1.1911±0.0659 → 1.1954±0.0635` (lines 1895/1898); Design-on `RMSE_μ` in §V `1.1911→1.1954` (1820); the Design cost on U-Air `6.553→6.886 %` and tail `6.875→7.221 %` in §V (1586–1588), in the Table III caption (1866–1868) and in the §VII-E paragraph (2015); Inst's prediction cost `0.131/0.136 → 0.143/0.149 %` (2047); Table IV's U-Air prediction cells `−6.553→−6.885`, `−6.875→−7.221`, `+0.024→+0.025`, `+0.025→+0.026`, `+0.131→+0.143`, `+0.136→+0.149` (2002/2004/2005); the Fig. 4 caption's U-Air half now reads "worsen `Δ_group` and `RMSE_μ` by about `7.5 %`" (1911–1912, was "`Δ_group` by about `7.5 %` and RMSE by about `7.1 %`"). **Changed in `appendix.tex`:** the all-method table's `RMSE_μ` column for Local-Hájek `1.1882→1.1923`, TwoStage `1.2160→1.2202`, Inst-Cal and RAVEN-Design `1.1911→1.1954`, RAVEN-SimOracle `1.1914→1.1958` (1880–1885). **Changed in `figure_data/`:** `FIG_W1_DESIGN_GATE.csv` U-Air `RMSE_mu_pct` `7.07231→7.45650` (estimated) and `7.10791→7.50451` (oracle) under that file's own per-seed-relative convention; `FIG_E4_E4_COMPONENT_ABLATION.csv` U-Air `RMSE_mu`/`Tail_RMSE` rows (relative change, paired mean difference, Holm p); `FIG_E3_E3_PREDICTION_RISK.csv` the nine affected E3 arms at the three seeds (`RMSE_mu`, `Tail_RMSE`). Four figures rebuilt with `make_figures.py`: `fig_w1_design_gate`, `fig4_e3_prediction_risk`, `fig5_e4_component_ablation`, `fig6_e4_uair_excl_design` (PDF+PNG; the other five PDFs differ only in embedded build metadata). **Verified unchanged, with evidence:** every `WorstGroupRMSE` cell is already θ (the θ 20-seed mean is `1.2630`, whereas the mirror reconstruction would be ≈`0.0075` lower), the four-block table's U-Air rows, every `Δ_group`/`Δ_c-s` cell and percentage (the recomputation from tree values is bit-identical: `−6.943368…`, `+4.989835…`), §V's `2.46 %` (same TwoStage denominator gives `2.4578 %`), the tolerance relatives `+0.48 %/+0.44 %` and `+0.002 %/+0.075 %` (they are the RAVEN-NoDesign rows, recomputed `+0.478/+0.443` and `+0.002/+0.075`), the X-3 caption's `+7.9 %/+8.0 %` (`+7.944`/`+8.024`), and all SensorScope cells. **Newly found while building the list:** the generation-2 `w/o-Inst` corrective reruns also carry the trigger (so Table IV's Inst row needed the same treatment; θ values `1.142423→1.189399`, `1.173732→1.158093`, `1.129598→1.186332`); the H-grid's U-Air `raven_simoracle` runs carry it in four conditions (10 runs, incl. seed 30014 under `C1_tilt_strong`); and §VII-F's two U-Air class-internal numbers (`+0.040 %`, `2.04 % [1.33, 2.75]`) come from the frozen tree via `results_ceiling_class_r1/compute_ceiling_class_paired.py`. **Left as-is and disclosed:** the unused `MAE_mu`/`RMSE_rho` columns of `FIG_E3_E3_PREDICTION_RISK.csv` still hold mirror values (the figure plots neither). Build after the write: main **17 pp.**, supplement **16 pp.**, 0 errors, 0 undefined references, 0 overfull, em dashes 2/3 in `main.tex` and 0 in `appendix.tex`, `check_prose_quality.py` clean on `main.tex` (no hard failure; it times out on `appendix.tex` at both full-file and section scope, a pre-existing tooling limit that this digits-only appendix edit does not touch), `tools/freeze_appendix_refs.py --check` = 0 to freeze / 0 unresolvable. Build note for reproducers: the local `pdflatex` crash (`0xC0000409`) truncated `main.aux` mid-write and broke `xr` in the supplement; one `pdflatex -draftmode main.tex` pass completes the aux (`\@abspage@last{17}`) and the supplement then compiles. Snapshot: `snapshots/2026-09-29-pre-theta-resource/` (both `.tex`, the three CSVs, the four PDFs) | `TO_OVERLEAF_paper_tmc_r1_clean/`; `results_seed_path_audit_r1/`; §7 item 46 |

| 48 | **Closure round: the two remaining mirror-sourced candidates checked, X-4b closed.** Both were raised by item 47 as "newly found while building the list"; the user asked for the read-only recomputation before closing. **(a) H grid — real but record-only.** The A1 sweep's ten triggered `round_u1` runs are all the *Design-on* oracle (`raven_simoracle`): C0/C3/C4 at seeds 30007/30016/30018 and C1 at 30014. Each checkpoint was re-evaluated at θ with that run's own wiring (`c9_h_theta_recheck.py`: production target bundle for C0/C1, the block-uniform override rebuilt exactly as `run_h_headroom.block_uniform_target` for C4, `DiurnalBlindNDMF` for C3), giving `+4.10 % / −1.35 % / +5.02 %`-type shifts per run; the C0 values equal the E3 tree's θ cells for the same runs to the last digit (`1.189208/1.157351/1.185403`), which validates the wiring. Effect on claims: **none in the manuscript** — U-Air's quoted H is pinned to the frozen Design-off arm (`FREEZE_ARM_DATASET=uair`, code path line 374), the ten runs do not enter it, and all six `H_RMSE_mu` cells reproduce bit-identically; the reader-visible facts (`\|H\| ≤ 0.217 %`, every interval containing zero, the `0.70`–`0.80` pp MDE) therefore stand. The correction lands in the **record's** §3A H4 table only: C0/C1/C3/C4 support costs `+6.968/+6.989/+6.980/+6.991 %` → `+7.356/+7.186/+7.366/+7.388 %`, C2/C5 unchanged, quoted range `+6.31…+6.99 %` → `+6.31…+7.39 %`, minimum CI lower bound `+4.751 %` (C5) so "all six above `+4.75 %`" still holds, and the invariance pattern becomes `C0 ≈ C3 ≈ C4 ≈ +7.37 %`, `C1 ≈ +7.19 %`, `C2 ≈ C5 ≈ +6.31 %`. **(b) §VII-F class-internal numbers — false alarm, withdrawn.** `compute_ceiling_class_paired.py` reads the frozen E3 tree only for its **SensorScope** half; its U-Air half calls `rebuilt_uair()`, i.e. the θ column `RMSE_mu_std` of `E2_UAIR_CELLS.csv`, so `+0.040 %` and `2.04 % [1.33, 2.75]` were θ-consistent as printed (the JSON stores `calibrated − oracle`; the paper quotes `oracle − calibrated`). Consequence: **every printed number in the manuscript is now θ-sourced**, and **X-4b is closed** (items 46–48: adjudication → write → residual check). X-4, X-5 and X-7 stay open on their own terms; X-4's fix now has the θ series it needs (`local_hajek` 20-seed mean `1.192251`). No manuscript file changed by this round; main stays 17 pp., supplement 16 pp., 0 error, 0 undefined, 0 overfull | `results_seed_path_audit_r1/C9_H_THETA_RECHECK.{csv,json}`; `c9_h_theta_recheck.py`; §3A H4; Part I Tier 5 rank 2 |

| 49 | **Manuscript write (authorized): X-4 fixed in §V, one sentence, no number changed.** The sentence at `main.tex:1851–1853` claimed Local-Hájek coincides with FedAvg **because both restrict the active set to the Design support**, which (i) contradicts the appendix's own per-row licensing rule (`appendix.tex:1865–1867`), (ii) describes the pre-repair `fedavg_window` defect that route A removed (record §2A N1), and (iii) is falsified by the printed rows themselves — after the θ re-sourcing Local-Hájek reads `1.1923` against FedAvg-Window's `1.1119` (before it, `1.1882`; the two coincide only on SensorScope, `7.9389` both). New wording: the coincidence holds **wherever the two arms keep the same active set**, because the realized within-client Hájek weights are uniform on these traces (the appendix's degeneracy audit: weight range `0` over 9,666 effective client-windows, `appendix.tex:1555–1583`), and on U-Air the supplemental rows differ only because Local-Hájek restricts the set to the target-mass support while FedAvg-Window keeps every delivered client. No numeric value, table, figure or claim changed; the referenced facts are unchanged and now attributed to the section that proves them. Verified: main **17 pp.** (unchanged), supplement **16 pp.** (unchanged), 0 errors, 0 undefined references, 0 overfull, em dashes 2/3, `check_prose_quality.py` no hard failure, `tools/freeze_appendix_refs.py --check` = 0 to freeze / 0 unresolvable, and the built PDF text carries the new sentence. Snapshot: `snapshots/2026-09-29-pre-x4-fix/`. **X-5 and X-7 remain open**, each with its replacement text already written in `results_seed_path_audit_r1/D_TEXT_FIXES_X4_X5_X7.md` | `TO_OVERLEAF_paper_tmc_r1_clean/main.tex:1851–1856`; `appendix.tex:1555–1583`, `1865–1867`; §7 item 12 (X-4 row) |

| 50 | **Manuscript write (authorized): X-5 and X-7 fixed, wording only.** **X-5** (`main.tex:1594–1596`, §V setup paragraph): "All experiments except the balanced control use 20 paired seeds" was false for four protocol-comparison tables that use ten — `tab:tdrive_hybrid` (`main.tex:1736`, 10 seeds / 178 windows) and `tab:traffic_four_region` / `tab:cityscanner_hybrid` / `tab:cityscanner_p2_measured_o` (`appendix.tex:1918/2465/2535`, 10 seeds / 100 windows each). Now: "All experiments use 20 paired seeds except the balanced control (five) and four ten-seed tables (the T-Drive ranking here, three in the supplement)." **X-7** (`appendix.tex:1685–1688`, appendix F opening): the sentence claimed the sealed same-backbone family "uses the Design-off setting on U-Air" and that "the sensor-scope and U-Air rows of Table~III are the Design-on and Design-off settings respectively". Both halves were wrong — the family's U-Air bars are the **Design-on** arm, as its own figure captions say (`appendix.tex:1788–1790`, `1801–1803`), Table III reports both settings on both blocks, and Design-off is the *deployed* U-Air setting (`main.tex:2125–2128`). Now: the family is evaluated with Design on, the U-Air panels therefore diagnose that arm rather than the deployed setting, and the deployment choice is Design on for SensorScope and Design off for U-Air. No number, table, figure or claim changed; both paragraphs keep their physical line count, so every line citation recorded in items 37–49 and Part III remains valid. Verified: main **17 pp.**, supplement **16 pp.**, 0 errors, 0 undefined references, 0 overfull, em dashes 2/3, `check_prose_quality.py` no hard failure, `tools/freeze_appendix_refs.py --check` = 0 to freeze / 0 unresolvable (no new cross-reference was introduced), and both new sentences were read back from the built PDFs with `pdftotext`. Snapshot: `snapshots/2026-09-29-pre-x5x7-fix/`. With this, all five stated-versus-true defects the external review named (X-3, X-4, X-5, X-6, X-7) are applied | `TO_OVERLEAF_paper_tmc_r1_clean/main.tex:1594–1596`; `appendix.tex:1685–1688`; `results_seed_path_audit_r1/D_TEXT_FIXES_X4_X5_X7.md` |

| 51 | **M1 closed: the Design factor standard written into the paper as two equations, with the scope kept honest.** The user asked whether the missing criterion could be stated as a formula rather than prose, and chose the two-part form. **Added** `main.tex:2033–2076`, §VII-E, paragraph "Setting the Design factor": (i) the **support gate** (42), `ρ_r = n^zero_r/n_r` over delivered training units whose attached client–stratum carries zero public target mass, with `D_r = on ⟺ ρ_r = 0`; (ii) the **switch point** (43), the argmin of the normalized four-endpoint objective `Ĵ_r(D) = Σ_e w_e M_{e,r}(D)/M_{e,r}(on)`, `e ∈ {Δ_group, Δ_c-s, RMSE_μ, Tail}`, whose indifference condition is `w_c·4.990 = w_g·6.943 + w_μ·6.885 + w_t·7.221`, giving `w_c/w_g > 1.39` for structure-only deployments and "always on" on SensorScope. **Design choices that keep it defensible:** the gate uses only public pre-window information and states a stopping condition, not an endpoint preference; the switch point is explicitly scoped as a standard for blocks of this kind; both settings remain reported (Table IV still quantifies the `4.990 %` `Δ_c-s` gain the gate forgoes on U-Air); and the paper no longer claims that no setting is ever selected — §III-D `1049–1057`, the contributions entry `222–227` and §VII-G `2170–2177` were aligned, and the appendix statistic was relabelled from "descriptive, does not select" to "the input of gate (42)" (`appendix.tex:70–76`, `2362–2391`, header `Design (42)`). **Not the refuted construction:** the positivity gate tested A5, which holds on U-Air and would turn Design on there; this gate tests target-map emptiness of the delivered units, which is positive exactly on the blocks where the factor costs structure and prediction (decision register updated accordingly). **Numbering and budget:** the two equations take numbers 42–43, i.e. *after* every existing equation, so no equation in the 1–41 range renumbers and the appendix's hardcoded main-equation numbers (32/35/37/38/39/40) stay valid; the search confirmed no hardcoded number ≥41 existed in either file. `supplemental.tex`'s counter moves 42 → 43 so the supplement's equations continue at (44) with the pre-existing gap closed (previously 43–119, now 44–120). Main stays **17 pp.** and the supplement **16 pp.** with 0 error, 0 undefined, 0 overfull; two overfull boxes introduced by the first draft were fixed (the objective equation was set as a two-line `aligned`, and the appendix column header shortened). The paper's Design `RMSE_μ` cost was harmonized to `6.885 %` in §V, the Table III caption and §VII-E so it matches Table IV's paired value. Record-keeping: the four places that said "no derived rule replaces φ" are marked superseded, the §8/M1 action row is closed, and the decision register distinguishes this gate from the refuted positivity gate | `TO_OVERLEAF_paper_tmc_r1_clean/main.tex:2033–2076`; `appendix.tex:70–76`, `2362–2391`; `supplemental.tex`; `snapshots/2026-09-29-pre-m1-design-rule/`; §3A H4; items 18–21 |

| 52 | **Manuscript write (authorized): the deployment-target criterion now has a proved group decomposition (Proposition 4), with the design-gate support condition as its neighbour.** `main.tex` §VI, after Proposition 3, carries `prop:group_decomposition`: for any partition `G` of the supported test units, `RMSE_μ² = Σ_g μ^eval_g RMSE_g²`, the feasible-direction derivative `Σ_g d_g RMSE_g²/(2 RMSE_μ)`, and the ordering condition `Σ_g (μ'^eval_g − μ^eval_g)(RMSE²_{g,a} − RMSE²_{g,b})`; a following paragraph states the three conditions, that it re-weights a fixed prediction set rather than retraining, and that it decides the `RMSE_μ` side of the Design trade-off only. §VII-E's "Setting the Design factor" now points to it. The appendix gains `app:proof_prop4` (identity by regrouping the weighted sum; derivative because the within-group weights do not depend on the other masses; ordering by subtraction). **Evidence behind the write** (`results_group_identity/round_v1/`, produced under the GPT-drafted protocol, read-only): E1 identity on **470 rows** (City Scanner 150 cells from `ENDPOINT_TABLE.csv`, SensorScope/U-Air 320 rows from `post_review/G2_external_baselines/tables/per_seed.csv`) with **max absolute error 1.78e-15**, zero `source_mismatch`, block masses rebuilt through `_mu_weights_for_test` (never four equal weights); E2 exact layer `≤1.43e-16` and Taylor residuals `1.09e-5` (run→M1), `7.15e-6` (run→M2), `1.99e-5` (M1→M2), `4.58e-7` (frozen `d=(0.02,−0.01,−0.01,0)`); E3 **30 pair-cells, zero order/sign inconsistencies** and zero all-four-components-same-sign violations, no rank flip observed; E4 recovers the published `RMSE_μ` Design gap on both datasets (SensorScope `+0.00536 %` vs `+0.005 %`, U-Air `−6.875 %` vs `−6.885 %`); E5 within-group weight variance `≈1e-38` on all three datasets, so the equal-weight `RMSE_g` is the right object. **Corrections applied to the earlier draft:** the switch numbers `4.990` and `6.943` are `Δ_c-s` and `Δ_group` and are **not** outputs of this identity (only the `RMSE_μ` entry is), and the identity is **not** assumption-free. **Numbering and budget:** no new equation number (43 unchanged) because the identity is stated inline; the proposition sits after Proposition 3 so numbers 1–3 and the sixteen hardcoded `Proposition~N` strings stay valid; `supplemental.tex`'s proposition counter moves 3 → 4 so the appendix's own propositions become 5 and 6 (they are `\ref`-ed). Verified: main **17 pp.**, supplement **16 pp.**, 0 errors, 0 undefined, 0 overfull, em dashes 2/3, prose check with no hard failure, freeze invariant 0/0, and both new passages read back from the built PDFs. **What this does not do:** it does not theorem-ize the switch point (still a measured decision standard) and it does not bound the support loss for `ρ_r > 0` (that stays the explicit `GAP` of `PROOF_SKELETON.md`). Snapshot `snapshots/2026-10-02-pre-group-decomposition/` | `TO_OVERLEAF_paper_tmc_r1_clean/main.tex` §VI + §VII-E; `appendix.tex` `app:proof_prop4`; `supplemental.tex`; `results_group_identity/round_v1/`; §7 items 46–51 |

### Open manuscript defects NOT changed

| item | where | note |
|:---|:---|:---|
| **the `wo_inst` ablation fix is unfinished at one call site** | `src/raven_mcs/sag/counterfactual_audit.py:106`; `feasibility.py:29-46`; `p2_cvxpy.py:56,70`; `src/raven_mcs/e4/wo_inst_final/` | The 2026-08-12 wo_inst repair added an `instant_calibration` flag so that `lambda_group=0` is legal for the ablation (`E4_WO_INST_SEMANTIC_FIX.json`), but `counterfactual_audit._solve_alpha` still calls `solve_p2` without the flag, so `RavenWoInstAggregator` raises `lambda_group must be >= max_server_learning_rate`. The arm cannot be re-run until that call site is covered. Nine lines of the repair also remain uncommitted. No manuscript value depends on this |
| ~~**P3's A6 clause list does not imply the inactivity it concludes, and `ε_clip` carries ceiling excess only**~~ (**X-1**, verified) — **closed 2026-09-28 by §7 items 37–38** | was `main.tex:1127–1136` (A6), `707–715` (`a`), `1256–1267` (`ε_clip`), `1303–1307` (the mitigation) and `appendix.tex:763–830` (proof). Now `main.tex:1127–1146` (A6a/A6b), `1267–1278` (the `ε_stab` definition, label at `1277`), `1285–1321` (Prop 3), `1327–1339` (corollaries); proof at `appendix.tex:767–898` | Closed as option (i)+(ii) together: the missing clauses are stated in A6a *and* the residual is replaced by the measurable `ε_stab`. Part III III.3, III.9 |
| ~~**§VII-F's closing claim is a family bound**~~ (**X-2**, verified) — **closed 2026-09-29 by §7 item 42** | was `main.tex:2076–2077` ("reachable by any correction in this family") and `2093–2095` ("bounds what any later claim about the correction family can reach"); now `2073–2113`, re-grounded on `C_r` (25) + (P2) + `RMSE_mu`, with the class-internal margins comparison and the \eqref{eq:g4_comp} anchor | Closed as plan (c): method class and criterion are named, the bound is the measured class-internal one plus the proved composition-level perturbation. **What it still does not do**: prove the class's total achievable gain; that remains measured (H) and is recorded in I.3 |
| ~~**Table III caption extends the tolerance to both settings on both blocks**~~ (**X-3**, verified) — **closed 2026-09-29 by §7 item 45** | was `main.tex:1872–1873`; contradicted by `main.tex:2128–2129` (§VII-G) and by the table's own U-Air RAVEN-Design row (`1.2630` versus FedAU-Window `1.1701` and ObsUse-Window `1.1692`) | Now scoped: SensorScope both settings, U-Air RAVEN-NoDesign inside the line, U-Air RAVEN-Design outside it at `+7.9 %` and `+8.0 %`. **Note for future readers: the 2×2 content was never missing** — the caption declares it in words at `1862–1863` ("Both Design settings are reported on both blocks, so the table is a within-dataset factor") and the body carries two RAVEN rows per dataset; the string "2×2"/"factorial" never appears in the paper, so keyword searches fail on it |
| ~~**the Local-Hájek coincidence sentence**~~ (**X-4**, verified) — **fixed 2026-09-29 by §7 item 49** | was `main.tex:1851–1853` (§V), against the appendix's own per-row licensing rule (`appendix.tex:1865–1867`), the degeneracy analysis (`appendix.tex:1555–1583`) and the printed rows (`1.1923` versus `1.1119` after the θ re-sourcing, `1.1882` before it) | the sentence said Local-Hájek coincides with FedAvg **because both restrict the active set to the Design support**; FedAvg-Window keeps every delivered client, so that attribution described the pre-repair `fedavg_window` defect (record §2A N1). Rewritten to the fact the appendix proves: the coincidence holds **wherever both keep the same active set**, because the realized within-client Hájek weights are uniform on these traces (weight range `0` over 9,666 effective client-windows), and the two supplemental U-Air rows differ only in the active set. Sourcing layer in III.5 |
| ~~**the blanket seed count**~~ (**X-5**, verified) — **fixed 2026-09-29 by §7 item 50** | was `main.tex:1594`; the four ten-seed tables are `main.tex:1736` (`tab:tdrive_hybrid`) and `appendix.tex:1918/2465/2535` (`tab:traffic_four_region`, `tab:cityscanner_hybrid`, `tab:cityscanner_p2_measured_o`) | the sentence read "All experiments except the balanced control use 20 paired seeds"; four protocol-comparison tables use **ten** (178 and 100 windows). Rewritten to state the two exceptions, naming the T-Drive ranking and the three supplemental tables. Line count unchanged, so no other citation shifts |
| ~~**P3's hypothesis said to hold on SensorScope while A6 is said to fail on both datasets**~~ (**X-6**, verified) — **closed 2026-09-28 by §7 item 37** | was `main.tex:1876–1880`, rewritten at `1909–1916` | The rewritten scope paragraph says A5 and A6b hold while A6a fails on both datasets, so the adjacent contradiction is gone |
| ~~**the audit's a-side clause read in the wrong form, and at `a_max=40`**~~ (**X-21**, verified here 2026-09-28) — **closed by §7 item 38** | was `appendix.tex:2153` (table row) and `2186–2189` (the "verdict is unchanged at 20 or 40" sentence); `runner.py:471–484` and `window_runner.py:1433–1437` fix the operative constant | The clause is now read on `π^tar/(π^opp p^obs)`, at `a_max=20`, and **fails on U-Air** (`23.47`; 2.74 % of active client-windows) while holding on SensorScope (`19.26`); the "only the `q` side fails" narrative is withdrawn. The **tooling still carries both errors** — see X-21b in I.7 |
| ~~**the sealed family's Design setting**~~ (**X-7**, verified) — **fixed 2026-09-29 by §7 item 50** | was `appendix.tex:1685–1688`, against `appendix.tex:1788–1790`, `1801–1803` (its own figure captions) and `main.tex:1851–1853`, `2125–2128` | the opening said the sealed family "uses the Design-off setting on U-Air" and that the SensorScope and U-Air rows of Table III "are the Design-on and Design-off settings respectively" — both wrong: the family's U-Air bars are the **Design-on** arm (the E3 `raven` arm), Table III reports **both** settings on both blocks, and Design-off is the *deployed* U-Air setting. Rewritten to say the family is evaluated with Design on, that the U-Air panels therefore diagnose that arm rather than the deployed setting, and that the deployment choice is Design on for SensorScope and Design off for U-Air. Line count unchanged |
| ~~**three disputed U-Air seeds**~~ (**X-4b**, record-only, found here) — **re-sourced 2026-09-29 by §7 item 47** | was `results_active_set_repair/round_v1/E2_UAIR_CELLS.csv` versus `artifacts/e3_formal_runs_r1/runs/uair/*/seed{30007,30016,30018}/final_metrics.json` | **Root-caused 2026-09-29 (§7 item 46):** the trigger is a final window that does not aggregate, where the run-time metric evaluates the in-memory module instead of the saved `theta` (a largest parameter gap of `0.0348`; live `1.142487` versus theta `1.189413`); the theta copy is paper-conformant, so the three tree cells are superseded. **Applied (§7 item 47):** seven printed `RMSE_μ` cells, the derived text percentages, Table IV's U-Air prediction cells and three `figure_data/` files re-sourced; the appendix row for Local-Hájek `1.1882 → 1.1923` no longer collides with FedAvg's `1.1119`, and X-4's Local-Hájek question now needs the θ-based `local_hajek` series (`1.192251` over 20 seeds) rather than the mirror one |
| ~~**the H grid's U-Air `raven_simoracle` runs carry the same trigger**~~ (found while building §7 item 47) — **checked and closed 2026-09-29 by §7 item 48** | `results_h_headroom/round_u1/runs/{C0_frozen,C1_tilt_strong,C3_low_capacity,C4_block_uniform}/uair/raven_simoracle` (10 runs: seeds 30007/30016/30018, plus 30014 under `C1_tilt_strong`) | the ten checkpoints were re-evaluated at θ (`results_seed_path_audit_r1/c9_h_theta_recheck.py` → `C9_H_THETA_RECHECK.{csv,json}`, self-checked against the E3 tree's θ values to the last digit). **No paper number moves:** §VII-F's `\|H\| ≤ 0.217 %`, its intervals and the MDE are computed on the frozen Design-off oracle, whose runs are clean, and all six `H_RMSE_mu` cells reproduce bit-identically. The triggered runs feed only the `H_design` / `design_support_cost` columns, which the paper never prints; the record's own support-cost cells were corrected in §3A H4 |
| ~~**§VII-F's U-Air class-internal numbers are mirror-based**~~ (suspected 2026-09-29, same step) — **withdrawn as a false alarm 2026-09-29 (§7 item 48)** | `main.tex:2101–2107` (`+0.040 %`, and `2.04 % [1.33, 2.75]` for TwoStage-Hájek) via `results_ceiling_class_r1/compute_ceiling_class_paired.py` | the claim that the script reads the frozen tree holds only for its **SensorScope** half (a clean block). Its U-Air half calls `rebuilt_uair()`, which reads `results_active_set_repair/round_v1/E2_UAIR_CELLS.csv` column `RMSE_mu_std` — the θ cells — so `+0.040 %` and `2.04 %` were θ-consistent as printed. Sign convention checked: the JSON stores `calibrated − oracle` while §VII-F quotes `oracle − calibrated`. The `e_ref` facts are model-free. **No change needed** |
| ~~**the endpoint-keyed Design rule is not written**~~ — **written 2026-09-29 by §7 item 51 (M1 closed)** | now `main.tex:2033–2076` (§VII-E, "Setting the Design factor"), eqs. (42)–(43); §III-D points to it at `1049–1057`, contributions at `226`, §VII-G at `2176`; appendix `70–76`, `2362–2391` | the paper now states the standard it was missing: a **support gate** `ρ_r = n^zero_r / n_r`, `D_r = on ⟺ ρ_r = 0` (42), and the **switch point** of a normalized four-endpoint objective, `w_c·4.990 = w_g·6.943 + w_μ·6.885 + w_t·7.221`, i.e. structure-only deployments keep Design on iff `w_c/w_g > 1.39` (43). The gate is a stopping condition (it withholds the factor exactly where the ablation measures the largest effect, 6.943 %/6.885 % on U-Air) and returns on the reported blocks the settings their rankings already use; the switch point is scoped as a decision standard for blocks of this kind, not a universal law |
| ~~no derived rule replaces φ for choosing a Design setting~~ — **superseded 2026-09-29 by §7 item 51** | §V-E, Table III, §VII-E, §VII-G | Option 1 (items 18–21) reports the factorial instead of selecting; the successor rule the φ removal left open is now written as the support gate (42) plus the switch point (43). **It is not the refuted positivity gate:** that construction tested A5, which holds on U-Air and would therefore switch Design *on* there, into the 6.55 %-worse branch; the support gate tests the target-map emptiness of the delivered units, which is positive exactly on the blocks where the factor costs structure and prediction. Both settings remain reported, so the factorial is intact and Table IV records what the gate forgoes on U-Air (the 4.990 % `Δ_c-s` gain) |
| ~~φ still drives the Design switch~~ **closed by items 18–21** | Algorithm 1; §V-E; eq. (32); the appendix φ table | D-1 implemented as Option 1: the switch is an explicit configuration and both settings are reported. The residual — the *choice* of setting per block had no derived rule — is closed by item 51 |
| the `μ` identity and target provenance | §VII-A.1, §VII-A.3, supplement | D-2 open; §VII-A.2's wording deliberately stays neutral |
| six scenarios never enumerated; `complete_counteracting` never reported | §VII-A.2; supplement runtime table | **feasible today, see §4**; not yet written up |
| the *difficulty* of the constructed regime is nowhere stated | §VII-A.2 (the P0 paragraph) | **closed by items 16–17**: the constants now appear with their dispersion, so `+0.5%` no longer reads as a property of the method; what stays open is the causal question of T8, not the disclosure |
| "forced" never defined | §VII-A.2, Table II/III/IV captions, §VII-G and six more places | means overriding the φ branch; two surface forms coexist |
| `g` never defined | Assumption 1; Thm. 2 | the conditioning object of the coverage guarantee |
| Availability names `TABLE_II_MAIN_EFFECTIVENESS.csv` as "canonical Table II" | Data and Code Availability | the main comparison is Table **III** |
| remaining spliced appendix pointers | §I evaluation paragraph, §VII-A.1 City Scanner paragraphs, Table I caption, §VII-C.2, §VII-G | ungrammatical |
| table captions say "controlled" while the body now says "protocol-constructed" | Table I/II captions | bridged by one sentence in §VII-A.2 |
| `tab:app_e2_daligned` presents one measurement as five method rows | supplement | see E5 |
| Table IV's U-Air Design row duplicates Table III's two RAVEN rows | main | one experiment presented twice |
| 24 of 54 bibliography entries unverified | `reference.bib` | one misattribution already found and fixed |
| author masking inconsistent; TMC page policy unverified | title page / format | desk-level hygiene |
| **`h(i)` used before it is defined** (notation item left open by §7 item 41) | `main.tex:323`, `331` (§II Related Work) versus `412` (§III-B, where `h: I→𝒢` is defined) | one-clause fix either way: replace the two `$h(i)$` by "the deployment groups", or add `Section~\ref{sec:system_model}` at first use. Zero compute |
| **`\mathbf{1}` is overloaded** (notation item left open by §7 item 41) | indicator `\mathbf{1}{·}` (14 places) versus all-ones vector `\mathbf{1}^{\top}` (17 places), both files | context disambiguates (a brace argument versus `^{\top}`), so this is acceptable; the alternative is a mechanical rename of one of the two (e.g. indicator to `\mathbb{I}{·}`), 14 edits, no semantic change |
| **main text is 17 pp. after the notation pass** (was 16) | `main.pdf`; the fourth page-worth is references [51]–[54] | options: move the editorial URL/licence annotations of [51]/[52] into Data and Code Availability (~5 lines, no information lost); or compress the repeated boundary statements in §VII-G (endorsed by the external review's C10); or accept 17 pp. and settle the budget with the majors |

---

## 8. Next actions

Reordered 2026-09-25 to match Part I. The order is by class and weight: correctness first, then the
ceiling, then the rule that the φ removal left open, then external evidence, then packaging.
Superseded items are kept at the end for the record.

**Added 2026-09-27 from the external review (Part III). These precede items 1–11.** Items 1–2 are
already complete as §7 items 26–32, and item 3 as §7 item 33, so the numbered list below is now a
record of work already done rather than a queue. **Updated 2026-09-28:** the first bullet is done
(§7 items 37–39, III.9), and with it X-6 and X-21; what follows is the live queue.

- ~~**X-1 — repair A6 / `ε_clip`.**~~ **Done 2026-09-28.** Both of the first two options were applied
  together: A6a states the missing clauses, and the retained residual is replaced by the measurable
  `ε_stab,r = ‖β_r^T − β_r^⋆‖₁` with the `C₁` re-derived. X-6 (the adjacent §VII-C contradiction) and
  X-21 (the audit's a-side clause and its `a_max`) closed with it.
- **X-2 — narrow §VII-F's closing sentence** to the tested oracle configuration, keeping the MDE
  caveat. **Next in the queue; no other item is cheaper or more load-bearing.**
- **X-4, X-5, X-7 — three stated-versus-true repairs, all zero compute:** the Local-Hájek sentence (and
  the sourcing of its row); the blanket seed count; appendix F's Design setting. III.4 gives the exact
  locations and what each contradicts. (X-3 was the fourth and is done, §7 item 45; X-6 was the fifth;
  **X-4 is done as of 2026-09-29, §7 item 49, and X-5 with X-7, §7 item 50 — all five are now applied**.)
- **X-21b — fix the tooling** so `tools/a5_a6_support_audit.py` stops defaulting to `a_max=40` and
  stops reading the `1/p^obs` form; otherwise a re-run contradicts the corrected supplement.
- **X-4b — adjudicate seeds 30007/30016/30018** before any further U-Air write: the sealed tree and the
  route-A rebuild disagree there for five arms the repair did not touch, and both sources are intact
  (III.5).
- **Page budget.** The 2026-09-28 write moved the supplement from 15 to 16 pp. Recovering the page
  means cutting ~12–15 typeset lines, which would have to come from text unrelated to this repair.
- Then the previously open evidence routes: the fixed-active-set control (`M8`/X-9), a matched-budget
  comparison against simple target calibration (X-10), an exogenous target map (P-a/X-12), a measured
  `U` (T-f/X-13), and the fine-group harm distribution (X-11).

1. **Repair the U-Air baseline (§2A N1, N2, N4).** Re-run `fedavg_window` and `local_hajek` on U-Air
   with the current runner (equal delivery), relabel both rows, and move the U-Air claim from prediction
   to `Δ_group` (1.0165 versus 1.0446). Numbers are already in `results_table2_audit/`. Any further
   analysis on the old row is void. Note the metric: the `−6.17 %` / `−9.11 %` sentence is
   `WorstGroupRMSE`, not `RMSE_μ`.
2. **Rebuild the U-Air `FedAvg-Window` row from a single frozen batch and disclose the metric scale
   (§2A N3, N7).** Both root causes are now located, so this is an edit rather than an investigation:
   take `RMSE_μ`, `Δ_group`, `Δ_c-s` **and** `WorstGroupRMSE` from one artifact, and state that the
   U-Air `RMSE_μ` column is z-scored by `sigma = 17.36325121670317` while SensorScope's is raw. Also
   decide whether Table III should print the physical U-Air values, which is what the sealed source and
   `metric_scale_policy.json`'s `primary_domain: "physical"` both imply.
3. ~~**Add the ceiling to the paper**~~ **done 2026-09-27**: §VII-F "Recoverable-Gain Ceiling" states the frozen GO rule, the negative result on both blocks, the U-Air MDE caveat, and the F-1 hardening test. Closes review M2/M5.
   outcome (H's STOP, U1's confirmation), not an outside criticism, and it is worth about +0.5 on
   Evidence. Scope the sentence: SensorScope conclusive at MDE 0.17–0.36 pp; U-Air "every point
   estimate `|H| ≤ 0.22 %`, GO rule not fired", with the 0.70–0.80 pp MDE caveat (§3A H6).
4. **Write the endpoint-keyed Design rule** (§3A H4): Design helps `Δ_c-s` in 3 of 4 blocks and hurts
   `Δ_group` in 3 of 4, the mechanism is the +6.31…+7.39 % U-Air support cost, and no uniform setting
   works — Pilot 2 favours Design on two endpoints while City Scanner contradicts the support
   statistic. This closes review M1 and M4 at zero compute.
5. **Write up the scenario family** (§4). Read-only; the numbers are computed. Prerequisites: fix the
   Holm family for the per-scenario tests, and note that `Δ_group` cannot be included from the E2
   tree (S6).
6. **Obtain an exogenous public target map** for the blocks that already have real `R` (T-Drive,
   City Scanner) — see D-2/D-3. The only route that addresses §1, and nothing else substitutes.
7. **Do not switch datasets.** PEMS-BAY is a fixed-loop-detector traffic speed series (325 sensors,
   5 min, roughly six months), so it supplies neither a mobility-derived `R` nor any `U`; at best it
   could make `O` measured, and it duplicates the fixed-sensor type already used in NSW-Traffic.
8. **Decide the fate of the Design branch** once D-2 resolves, and **settle G5** before any
   degeneration claim.
9. **Reframe the contribution.** With H-A refuted and the ceiling measured twice, the honest
   positioning is: RAVEN is a target-composition *diagnostic and accounting* framework, the
   predictive payoff is not demonstrated on these protocols, and the reachable range is capped (T1–T2,
   §3A). Items 3 and 4 supply the evidence for that framing; the paper should be written to it rather
   than to a predictive claim.
10. **Ship the recomputed per-block scores** (the new `WorstGroupRMSE` cell in §7 item 19) and finish
    the bibliography verification.
11. **Score-change conditions**: one endpoint whose target is external to the method with a corrected
    gain → +1 overall; a measured-`U` block → +0.5 to +1; clarity and consistency fixes alone →
    about +0.5. §4 S3 raises the middle item's value, since the counteracting control already exists.

**Superseded or completed, kept for the record.**

- **V1 on City Scanner Pilot 2** (previously item 1) — no longer first. Its purpose was to test
  whether P2 is beneficial; §3 T6 already shows `TwoStage-Hájek = _normalize(β̂)` scores better, and
  §3A removes the headroom it would have measured. Run it only if the predictive claim is revived.
- **Record the difficulty of the constructed regime, and test it** (D-6, T8) — **both stages done.**
  F-3 put the dispersion in the paper (§7 items 16–17); F-1 ran 160 cells with the harness reproducing
  the published `raven` to 0.0000 % and returned `Δ_oracle` = +0.104 % (SensorScope, 4.7 σ) and
  −0.251 % (U-Air, 2.1 σ), inside the bound, so **H-A is refuted**. F-2 was not run and is now
  low-value. The headroom question was then re-asked under five stress conditions by H and U1 (§3A)
  with the same verdict.

---

## 9. Incident log — repository file corruption

At **2026-09-21 07:24:52**, 56 tracked files share one modification timestamp; **16 of them were
truncated**. Damage and recovery:

| file | was | restored to |
|:---|:---|:---|
| `TO_OVERLEAF_paper_tmc_r1_clean/reference.bib` | 0 B | 19520 B (54 entries) |
| `src/raven_mcs/data/registry.py` | 0 B | 1226 B |
| `src/raven_mcs/data/cityscanner.py` | 2 B | 14330 B |
| `scripts/run_c1_tdrive_spatial.py` | 0 B | 47177 B |
| `RAVEN_MCS_PUBLIC_REPRO_R1/scripts/build_public_repro_bundle.py` | 0 B | 14814 B |
| `RAVEN_MCS_PUBLIC_REPRO_R1/configs/design_rule.json` | 0 B | 122 B |
| `configs/dataset/cityscanner_nyc_pm25.yaml` | 2 B | 950 B |
| `post_review/C1_kill_cityscanner/C1_KILL_INSTRUCTION.md` | 2 B | 5208 B |
| `post_review/C1_kill_cityscanner/TARGET_SPEC.json` | 2 B | 3718 B |
| `post_review/C1_kill_tdrive_spatial/C1_KILL_INSTRUCTION.md` | 2 B | 3366 B |
| `post_review/C1_kill_tdrive_spatial/DRIVER_HAJEK_SLOWDOWN_PATCH_INSTRUCTION.md` | 2 B | 6976 B |
| `post_review/C1_kill_tdrive_spatial/TARGET_SPEC.json` | 2 B | 1260 B |
| `post_review/C1_tdrive_rank/REMOTE_AGENT_PROMPT.md` | 2 B | 2705 B |
| `post_review/C1_tdrive_rank/REMOTE_SYNC.md` | 2 B | 1470 B |
| `results_c1_cityscanner/round_v1/INGEST_REPORT.json` | 2 B | 884 B |
| `results_tdrive_rank/TD_R_ZIP_INGEST_AUDIT.json` | 2 B | 1618 B |
| `results_tdrive_rank/round_v1/TD_R_HARDWARE_STOP.json` | 2 B | 1500 B |

Consequences before recovery: the whole `raven_mcs.data` import chain failed, taking down
`raven_mcs.correction.pi_target`, `raven_mcs.e3.*`, and `scripts/compute_scd_phi.py`. That is
why the φ readings in §1 were recomputed after recovery rather than read from that script.

Recovery method: `git checkout --` for 15 files; `reference.bib` from the reproduction package
`_tmp_pack/7.26-vs-current-verification/current_paper/reference.bib`, the only backup whose key
set matches the compiled `main.bbl` exactly (54/54, no missing, no extra, INFOCOM attribution
present). `git HEAD` was not usable for it: 51 keys and the uncorrected venue attribution.
Verified afterwards: five key modules import, `bibtex` regenerates 54 `\bibitem`, `main.log`
reports 0 undefined citations and 0 undefined references, both PDFs rebuild.

Cause: unknown. The damaged set clusters on `C1_tdrive_rank`, `C1_kill_*` and the reproduction
bundle, which looks like an interrupted bulk write or checkout. An earlier edit in the same
session failed with `ReplaceFileW EIO (Win32 1175)` on `main.tex`. Content written to those 15
files after their last commit is unrecoverable.

Prevention: run `_tmp_ref/damage_scan_full.py` before any commit or package build.

---

## 10. Reproduce

```text
_tmp_ref/phi_zero_decompose.py     φ zero-set partition (missing key vs explicit zero) and
                                   test/train pair coverage; §1 R1
_tmp_ref/a4_mu_check.py            μ_g × N integrality → μ is the unit-count share; R2
_tmp_ref/a4_final_verify.py        weight-vector uniformity and the four-block identity; R2/R3
_tmp_ref/confirm_metric_lineage.py Table III == 20-seed means of the E3 run metrics
_tmp_ref/analyse_daligned.py       D vs Δ_ρ / Δ_μ statistics; E5
_tmp_ref/rank_interchange.py       method rankings under both risks and the power check
_tmp_ref/scenario_inventory.py     six-scenario completeness and per-scenario aggregates; §4 S1
_tmp_ref/scenario_table.py         family table, generalised D(S), additivity and
                                   WorstGroupRMSE sensitivity; §4 S2–S5
_tmp_ref/verify_p0_rendered.py     confirms each P0 edit in the built PDF (§7 items 12–15)
_tmp_ref/bib_verify.py             bibliography entry count and undefined-citation count
_tmp_ref/damage_scan_full.py       repository truncation scan; §9
_tmp_ref/check_stratum_constant_layers.py  distinct values of p_obs_true / q_use_true and their
                                   per-client-window structure, from the released audit; L6/L7
_tmp_ref/f1_stage_a_ceilings.py    the ceiling map: full RAVEN vs published references, per endpoint
                                   and dataset, with paired sds; T9
_tmp_ref/f1_ablation_ceilings.py   full RAVEN vs the E4 one-factor ablations, five modules x three
                                   endpoints, with sigma; T9
_tmp_ref/f1_compare.py             F-1 pairing and MDE helper
_tmp_ref/f1_readout.py             the F-1 verdict readout: gate 1 reproduction, E1 on both arms,
                                   manipulation gate; T8 item 2
_tmp_ref/f1_generator_check.py     theta_O generator validation: theta=0 bit-identity against the
                                   published trace, marginal preservation, within-stratum dispersion
_tmp_ref/audit_nodesign_pairing.py reconciles the NoDesign supplement's paired relative means against
                                   ratio-of-means: the Delta_group paired column carries an unstable
                                   sign on City Scanner (6/10 wins, 31 pp dispersion); §3A H4
_tmp_ref/u1_readout.py             the U1 verdict readout: decision file, 20-seed H and support cost,
                                   5-seed comparison, reuse bit-identity, arm-freeze check
_tmp_ref/u1_precise.py             precise U1 sd / MDE / GO-threshold table; §3A H3
```

Findings without a script: T1–T3 (central references and the oracle comparison) come from
`artifacts/e3_formal_runs_r1/runs/*/final_metrics.json`, and T6 from
`src/raven_mcs/aggregation/methods.py` lines 314–320 plus `appendix.tex` lines 2446–2449. §2A N1–N5
come from `results_table2_audit/{uair_table2_summary_with_current_fedavg.csv,uair_paired_vs_fedavg.csv,AUDIT_META.json}`
and `results_h_headroom/round_{v1,u1}/GATE_uair.json`, produced by `scripts/audit_table2_uair_fedavg.py`.
§3A comes from `scripts/run_h_headroom.py` (extended 2026-09-25 with `--round`, `--seeds`,
`--reuse-from`, `--freeze-arm-dataset`, `--full-seed-dataset`, `--decision-name`; defaults unchanged
and regression-verified against `round_v1` to 0.000e+00) plus
`results_h_headroom/{round_v1,round_u1,round_v1_verify}/`. Route
evaluations in §6 G7 and the literature verification are in
`ccfa-review-reports/raven-mcs-method-revision-evaluation.md`.

Other key inputs: `data/processed/{sensorscope,uair}/atomic_units.parquet`,
`artifacts/e3_semantic_alignment_and_runner_integration_closure_r1/E3_*_TARGET_SEMANTICS_R2.json`,
`artifacts/e2_traffic_formal_runs_r1/formal_*.csv` and `paired_comparisons.csv`,
`artifacts/e2_traffic_formal_results_analysis_r1/COMPLETE_ALIGNED_DOD.csv`,
`configs/e2_numeric/scenario_direction_registry.yaml`, and for L6–L9
`artifacts/a5_a6_audit/audit_records.csv` (28 800 rows),
`results_joint_ou/round_v1/INGEST_REPORT.json`,
`results_path_a_hajek/round_v1/INGEST_REPORT.json`, `configs/scenario/*.yaml`, and for T9 and T8
item 2 the two F-1 arms `artifacts/e3_f1_score_dependent_r1/` (published trace, θ = 0) and
`artifacts/e3_f1_theta1_r1/` (F-1-O trace, θ = 1.0), 160 cells over 20 paired seeds, with the
driver `scripts/run_e3_f1.py` and the θ_O generator
`src/raven_mcs/e3/real_runner/generator_r3_score.py`.

---

## 11. What this record does not do

It does not implement D-2 or D-3, and it does not edit the manuscript: D-1 was implemented as Option 1
on explicit instruction (§7 items 18–21), and §2A's repairs are specified but not applied. D-6 and its
F-1 test are complete, as is the H/U1 headroom work. It does not run revision 2's U2 (45 seeds), V1, or
T8's remaining F-2; does not rescore the paper beyond the review cited in the header; does not produce
the LaTeX versions of the scenario or gain-ceiling tables; ~~does not locate the root cause of §2A N3~~
(**superseded 2026-09-27**: N3's root cause is located — mixed sourcing across two frozen batches —
and N7 records the undisclosed U-Air metric scale); does not settle the NSW-Traffic target-map
provenance or the 0.34 % residual between the U-Air four-block identity and the published `RMSE_μ`
(**note: this is a distinct item from N3's 0.34 % ALL20 gap between the repro CSV and the run tree; the
two share a magnitude and have not been shown to share a cause**); and does not re-verify the 24
unverified bibliography entries.

Part III adds four more things it does not do. It did not, as written on 2026-09-27, re-derive
Proposition 3, add the missing A6 clauses, or widen `ε_clip` — those were *specified* in III.3 and
left unapplied. **Superseded 2026-09-28**: all three were applied on explicit instruction, as A6a/A6b
plus the measurable `ε_stab` (III.9, §7 items 37–39); what remains unapplied is X-2 and X-3–X-5, X-7.
It did not adjudicate the three disputed U-Air seeds when Part III was written; they were root-caused afterwards in §7 item 46. Earlier it recorded that the sealed tree and the
route-A rebuild disagree there, not which one is right. It did not itself read FedIPW, FedPALS or
FedAU — those three comparisons (X-14) come from the external review and cannot be reproduced with
this workspace's tooling. And it did not verify the external review's own unverified items: the City
Scanner `63.9 %/39.5 %` mean ratios, the coverage table's `233/243` and `6/8` counts, the title page's
masking state, and its reading of the FedAU adaptation.

Two claims it explicitly declines to make. First, it does **not** claim that the constructed regime
caused the flat gains: T8 recorded that as a hypothesis with a stated falsification test, F-1 ran it,
H-A was refuted, and H-B is what survives. Second, it does **not** claim the ceiling is zero: §3A H6
records that U-Air's realized MDE is 0.70–0.80 pp and that two cells still admit a true effect of
about 0.5 % at 95 %.

---

# Part III — The external review (advisor-supplied GPT report, 2026-09-27)

```text
Source:   ccfa-review-reports/raven-mcs-unspecified-venue-review.md (33 284 B,
          sha256 5b1f1d4f607f5f65fcfddb17c02a104e22b2e9d75563eb3927b43d93911396d6)
Input:    main(6).pdf (16 pp.) + supplemental.pdf (15 pp.) — the Overleaf build of the current
          TO_OVERLEAF_paper_tmc_r1_clean/: after Option 1, the route-A write, and §VII-F
Verdict:  4/10 weak reject, judgement confidence 4/5. Dimension scores: 原创性 3, 技术正确性 2,
          实验证据 2, 重要性与影响 3, 清晰度 2, 可复现性 2, 伦理与局限披露 4; 综合研究质量 2/5,
          相关工作定位 3/5
Its own stated boundary: read both PDFs in full, visually checked main pp. 8/12/13 and supplement
          pp. 11/14/15, and did NOT run the code, the per-seed artifacts, or the published package
Recorded: 2026-09-27. No manuscript file changed by this part.
```

## III.0 What it is, and the one place it converges

The review is an outside, protocol-style assessment (16 sections: screening, contribution map, live
literature check, verdict, S/W items, claim-evidence audit, statistics audit, a five-perspective
simulation, a ten-row action table `C1`–`C10`, eight author questions, and a score-change table). It
read the same two PDFs this record's verification pass checked, so its findings are about **the current
build**, not about an older version.

**It converges with this record on the number and diverges on the reason.** Both reach **4/10 weak
reject** independently. The external review's three decisive negatives are (i) P3's applicability,
(ii) novelty versus three named neighbours, (iii) the absence of a stable external utility. This
record's are (i) the measured ceiling (T-a…T-c), (ii) the artifact-versus-manuscript gap (`M7`),
(iii) the attribution gap (`M8`). Two axes overlap; the theory item is new here, and — see III.7 — the
review never reaches this record's Tier-3 identification boundary.

**A capability difference worth recording.** The external review resolved FedAU, FedIPW and FedPALS
against their published texts. This workspace cannot: `web_fetch` fails on every host here
(`resolves to a non-public IP address`), leaving only `web_search` summaries. X-14 is therefore
**reported only**, and routing it to a tool with live retrieval is the correct action.

## III.1 The ordering rule

Two axes, applied in order:

1. **Logical upstream-ness.** An item ranks higher when other text inherits it — when leaving it
   standing makes a claim that several paragraphs, captions or tables depend on *false*, rather than
   making one sentence false.
2. **Weight within that.** *Stated-versus-true* (a false statement in the build) outranks *missing
   evidence* (a true claim that is unsupported), which outranks *packaging*.

The result is four blocks plus a boundary: **X-1–X-2** (claims other text inherits), **X-3–X-7** (five
false statements in the current build), **X-8–X-13** (evidence the review asks for that this record
already had open, or that it opens on the same axis), **X-14–X-19** (capability, compliance,
presentation), and **X-20** (what the review does not cover at all). **X-21 was added on 2026-09-28**,
in the same class as X-3–X-7 but found here while executing X-1.

## III.2 The ranked register

| ID | the review's claim, compressed | class | status here |
|:---|:---|:---|:---|
| **X-1** | P3's A6 clause list does not imply the stabilizer inactivity it concludes, and `ε_clip` — the residual the paper retains — records ceiling excess only, so the weakened version is not established | correctness (theory) | **verified in-source**, III.3; **fixed in the manuscript 2026-09-28**, III.9 |
| **X-2** | §VII-F's closing claim bounds a correction *family*; an oracle-propensity stress grid cannot establish that | correctness of a claim | **verified in-source** (text + judgement), III.4; **open** |
| **X-3** | Table III's caption extends the `+0.5 %` tolerance to both settings on both blocks | stated-versus-true | **verified in-source**, III.4; **fixed 2026-09-29** (§7 item 45) |
| **X-4** | §V says Local-Hájek coincides with FedAvg because both restrict the active set to the Design support, while the appendix prints `1.1882` against FedAvg's `1.1119` and licenses the two rows differently | stated-versus-true | **verified in-source**, III.4–III.5; **open** |
| **X-5** | "All experiments except the balanced control use 20 paired seeds" is false for four tables | stated-versus-true | **verified in-source**, III.4; **open** |
| **X-6** | P3's hypothesis is called the SensorScope Design-on regime while A6 is said to fail on both datasets, in adjacent sentences | stated-versus-true | **verified in-source**, III.4; **closed 2026-09-28** by the X-1 rewrite |
| **X-7** | Appendix F's opening says the sealed same-backbone family uses Design-**off** on U-Air; its own figures and captions and §V say Design-**on** | stated-versus-true | **verified in-source**, III.4; **open** |
| **X-8** | `778` warnings / `6438` windows / `2.686e-8` certify feasibility, not optimality | evidence scope | **verified in-source**; also already open here as a *stale population* item |
| **X-9** | The support-set diagnosis does not uniquely locate the U-Air reversal; a fixed-active-set control is needed, and "excluded one explanation" must be separated from "located the cause" | evidence | **same item as our `M8`** (its 2×2 arm is the same ask; code-blocked here) |
| **X-10** | Only the Design factor moves anything; a matched-budget comparison against simple target calibration (and against matching-plus-variance) is missing | evidence / necessity | **reported only**, but it is `M8` generalized and it restates T-e |
| **X-11** | `WorstGroupRMSE` is a maximum over four UTC blocks while `Δ_group` spans 220/144 groups, so fine-group harm is unknown | evidence | **reported only** |
| **X-12** | The target is a test-split frequency; its deployment acquisition is unstated and independent-historical or predefined targets are untested. It explicitly declines to call this leakage | provenance | **same item as our `P-a` / D-2 / D-3** |
| **X-13** | `U` is measured in no block; City Scanner's clients are cells, not vehicles | provenance | **same item as our `T-f`** |
| **X-14** | FedIPW (two-stage enrollment/participation IPW, aggregate calibration) and FedPALS (eqs. (8)–(9): target-composition matching, convex-hull feasibility, variance/ESS regularization) must be compared mathematically, not by concept labels | novelty | **reported only — not reproducible here** (III.0) |
| **X-15** | The coverage table pools to `233/243 ≈ 0.959`, while the U-Air `a=1.00` cell is `6/8 = 0.75`; the joint bound is not the conditional false-safe rate | evidence | **reported only** |
| **X-16** | Backbone, hyper-parameters, the `λ` values, the propensity estimator's fitting and T-Drive's label `Y` are not recoverable from the two PDFs, and the package promises table reconstruction, not retraining | reproducibility | **partly verified** (the backbone is named once, `appendix.tex:1668`, with no architecture or hyper-parameters) |
| **X-17** | The title page keeps a named author, affiliation, e-mail and funding while another author is masked; double-blind compliance is unknown because the venue is unspecified | compliance | **reported only** |
| **X-18** | The Gate occupies too much of the main line and is weakly tied to the algorithm | presentation | **reported only** |
| **X-19** | Spliced appendix pointers, lowercase paragraph openers, a mis-attributed table mention, an over-long caption, small table type, crowded figure annotations; and "heuristic" language that survives the Design restatement | presentation | **partly verified**: the spliced pointers were already a desk item here; the "heuristic" residue is verified (below) |
| **X-20** | *(boundary)* The review never addresses ignorability, hidden confounding or MNAR | boundary | **verified in-source**; III.7 |
| **X-21** | *(found here, 2026-09-28)* The support-hypothesis audit read its a-side clause as a bound on `1/p^obs` rather than on `π^tar/(π^opp p^obs)`, **and** evaluated it at `a_max=40` where the E3 runs resolved `20`; both errors made the clause look satisfied | stated-versus-true | **verified in-source** (`runner.py:471–484`); **fixed 2026-09-28**, III.9 |

Two of X-19's four "heuristic" hits are the Design switch and the other two are not, which is the
precision the record needs: `main.tex:164` still introduces the NoDesign setting from "a frozen
zero-target heuristic", while `main.tex:1716`, `main.tex:1906` and `appendix.tex:1854` use the word for
the **four-region map**, not for the Design factor. The config-semantics residue is therefore one
sentence in the abstract, not four.

## III.3 X-1 in full — A6's clause list, and the residual that cannot carry the floor

This is the only item in the review that outranks the Tier-5 routes, because everything the paper says
theory covers inherits it. Its two halves are both correct, and both were checked here against the
shipped sources.

**Half one — the clause list does not imply the conclusion.** A6 (`main.tex:1127–1136`) concludes that
"the floors `π_min`, `p_min`, `q_min` and the ceiling `d_max` ... are inactive there, and the clipping
residual ... vanishes", on the strength of three clauses: `π^opp ≥ π_min`, `1/p^true_min ≤ a_max`, and
`1/q^true_min ≤ d_max`. Those clauses cover **two** of the four objects — `π_min` (by the first) and
`d_max` (by the third). **No clause implies `p^true ≥ p_min`, `q^true ≥ q_min`, or `ζ^o/p^true ≤ a_max`.**

The second clause is additionally mis-specified, because the implemented weight is not `1/p`:

    a = min{ a_max, ζ̂^o / max{p̂^obs, p_min} }          (main.tex:707–715)
    ζ̂^o = π^tar / max{π̂^opp, π_min}                    (main.tex:660–672)

so the quantity the ceiling acts on carries the design ratio. The review's instance reproduces
exactly: with `π^tar = 0.5`, `π^opp = 0.01`, `p = 0.2`, one gets `1/p = 5 ≤ 40 = a_max` while
`a = 50/0.2 = 250 > 40` — the ceiling is active although the stated condition holds, with **zero**
estimation error. That refutes only the inference "the listed conditions make the clipping residual
vanish", which is exactly the inference A6 makes.

**Half two — the retained residual cannot carry a floor.** `ε_clip` (`main.tex:1256–1267`) is the
coordinatewise positive part against the two ceilings:

    ε_clip = max{ max(ã − a_max)_+ , max(d̃ − d_max)_+ }

where `ã`, `d̃` are the *unclipped* plug-in ratios. A floor acts downward: if the true margin is below
the floor and the estimate is exact, the implemented ratio is **smaller** than the ideal, both positive
parts are zero, and `ε_π = ε_p = ε_q = ε_clip = 0` while `ã ≠ a*`. The proof needs that case to be
empty: the displayed Lipschitz bound (`appendix.tex:788–799`) carries only `ε_π`, `ε_p`, `ε_q`, i.e. it
is derived as if `max{p̂, p_min} = p̂` and `max{q̂, q_min} = q̂`.

**This is not a hypothetical regime.** The paper's own audit reports the `q_min` floor active on
**5.22 % / 5.18 %** of observed client-windows (quoted in
`ccfa-review-reports/snapshots/raven-mcs-tmc-review-2026-09-20-pre-option1.md:197–198`). And the
mitigation written in the previous round — `main.tex:1303–1307`, "retained in the proof rather than set
to zero; A6 is exactly the hypothesis that removes it" — does not close the gap, because what is
retained covers the ceilings only.

**Consequence, in the conservative form.** Proposition 3 is **not established** in the regime the paper
itself reports (A6 fails on both datasets, `main.tex:1879–1882`). The review's stronger reading — that
the printed bound is false where the floors activate with near-exact estimates — is consistent with the
algebra; whether it is *realized* on the released traces is the live question, and the 5.2 % floor
activation rate is what makes it live.

**Repair options (writing only for (i) and (iii); re-derivation for (ii)).**

1. **Complete the assumption.** Add `p^true ≥ p_min`, `q^true ≥ q_min`, and replace
   `1/p^true_min ≤ a_max` with a bound on the composite, `ζ^o/max{p^true,p_min} ≤ a_max`
   (worst case `1/(π_min p_min) ≤ a_max`). Then the printed proof's inequalities follow as written.
2. **Widen the residual.** Extend `ε_clip`, or add a floor residual beside it, to carry the
   floor-induced deviation, and re-derive `C₁`. The envelope has room: the mass bound at
   `appendix.tex:804–817` already multiplies `(a_max + d_max)` into `ε_clip`. This is a re-derivation,
   not a rewording.
3. **Weaken the claim.** Drop "the clipping residual vanishes" from A6 and state P3 as applying only
   where A5 *and* floor/ceiling inactivity hold — i.e. not on these traces.

Option (i) or (ii) is required if the abstract (`main.tex:82`, `main.tex:240`) is to keep calling the
clipped plug-in a stable perturbation of the reference.

## III.4 The five stated-versus-true defects, with what each contradicts

*(The review named five; **X-6 was closed on 2026-09-28** by the X-1 rewrite, and a sixth defect of the
same class, **X-21**, was found here while executing X-1 — it is recorded in III.2 and III.9 rather than
in the table below, which stays as written on 2026-09-27 so that its citations keep resolving.)*

All five are checkable inside the PDF, and all five are zero-compute. Four of the five were introduced
or left behind by this round's own writes, which is the part worth recording.

| ID | location | what it says | what contradicts it |
|:---|:---|:---|:---|
| **X-3** | `main.tex:1825–1826` (Table III caption) | "Both RAVEN settings stay within the descriptive `+0.5 %` worst-group tolerance versus those two on SensorScope and on U-Air" | `main.tex:2055–2057` names one setting per block; U-Air Design-on is `1.2630` against FedAvg `1.1690` (`main.tex:1798`), ≈ **+7.9 %** versus FedAU/ObsUse |
| **X-4** | `main.tex:1804–1806` | "Local-Hájek coincides with FedAvg on U-Air because both restrict the active set to the Design support" | `appendix.tex:1807–1808` states the opposite rule (rows that do not read `π^tar` keep every delivered client); the rows print `1.1882` (`appendix.tex:1822`) versus `1.1119` (`appendix.tex:1819`). The sentence is in fact a description of the defect N1 removed — the old `fedavg_window` ran *on* the Design-support restriction |
| **X-5** | `main.tex:1547` | "All experiments except the balanced control use 20 paired seeds" | `main.tex:1689` (T-Drive, 10 seeds / 178 windows) and `appendix.tex:1860`, `2373`, `2443` (10 seeds / 100 windows each) |
| **X-6** | `main.tex:1876–1880` | "…that is the SensorScope Design-on regime, not the U-Air Design-on regime. The support-hypothesis audit … reports A5 holding and A6 failing on both datasets" | the two sentences cannot both stand; if A6 fails on SensorScope, P3's hypothesis does not hold there |
| **X-7** | `appendix.tex:1627–1630` | "The sealed same-backbone protocol family below uses the Design-off setting on U-Air" | `appendix.tex:1730–1732` ("U-Air RAVEN-MCS in this figure uses Design on"), `appendix.tex:1743–1745`, and `main.tex:1801–1804` |

**X-2** belongs to this block by weight but not by class: `main.tex:2044–2046` closes §VII-F with "it
bounds what any later claim about the correction family can reach on these blocks". True propensities
are not the finite-sample RMSE-optimal reweighting and the stress grid is finite, so the honest form is
"no oracle-propensity configuration tested here recovers `H ≥ 0.5 %`", with the U-Air MDE caveat kept.
One sentence.

## III.5 X-4's second layer — three seeds, five arms, one mirror (found here, not by the review)

*Corrected 2026-09-29:* the heading said "two pipelines", which was wrong — stage E2 re-evaluates frozen checkpoints rather than retraining. The seeds (30007/30016/30018) and the arm set are as recorded below; the cause, and the verdict that the `theta` copy is paper-conformant, are in §7 item 46.

Verifying X-4 required settling where the appendix's `1.1882` comes from. It is not a transcription
error and it is not stale in the usual sense:

- In the **sealed E3 tree**, `local_hajek` and `fedavg_window` are **bit-identical on all 20 U-Air
  seeds**, mean `RMSE_μ = 1.188238`, `Δ_group = 1.121762`, `Δ_c-s = 1.262132`. The appendix's
  `1.1882 / 1.1218 / 1.2621` is exactly that arm's own value. The coincidence the manuscript describes
  was therefore *real* — and it was real **because the old `fedavg_window` inherited the Design-support
  restriction**, which is the N1 defect itself.
- In the **route-A rebuild**, `fedavg_window` moves to `1.111932` (its licensed active set) while
  `local_hajek` moves to `1.192251`. The two are no longer identical, so the §V sentence is false
  against the repaired table regardless of sourcing.
- The rebuild reproduces the sealed tree **exactly at 17 of 20 seeds** for the five arms the repair did
  not touch (`local_hajek`, `inst_cal`, `raven`, `raven_simoracle`, `twostage_hajek`) and differs at
  **30007 / 30016 / 30018** by 2–5 % of `RMSE_μ`. Those are the same three seeds §2A N3 flagged for
  source mixing, and two of them lie inside the TEST window used by the headline paired statements.
  The two central arms (`central_all`, `central_delivered`) agree everywhere; the four repaired arms
  differ at all 20 seeds, as designed.
- **The sealed tree is not disturbed.** All 20 disputed `final_metrics.json` files match
  `E3_CANONICAL_HASH_MANIFEST.json` (11 752 entries, round `E3-FORMAL-RUNS-R1`). So this is a genuine
  two-pipeline disagreement, not corruption — the phenomenon §9 of this record exists to distinguish.
- **What it bears on.** The U-Air block now mixes pipelines: Table III's `FedAvg` row and four appendix
  rows carry rebuilt values, while the Design-on values the paper quotes (`1.1911`, hence the `6.553 %`
  Design cost), the remaining appendix rows and Table IV's U-Air Design rows carry sealed-tree values.
  The frozen-versus-rebuilt mean for `local_hajek` is `1.188238 → 1.192251`, **+0.338 %** — the same
  magnitude as the still-unlocated 0.34 % residual §11 declines to settle, with no shown common cause.
- **What would adjudicate it.** One disputed cell re-run from source with its trace hash compared
  against the sealed trace, or a trace-hash comparison between the sealed tree and the rebuild for
  seeds 30007/30016/30018. Until then, no further U-Air number should be written.

## III.6 Mapping onto Part I's tiers

| Part I tier | what the external review adds |
|:---|:---|
| **Tier 1** (correctness, "closed") | **X-1 reopens it on the theory side.** The artifact defect stays closed; the printed guarantee does not |
| **Tier 2** (the ceiling) | **X-2** attacks the claim form of §VII-F, not its numbers; **X-8** re-reads the solver counts; **X-15** adds a coverage-table limit |
| **Tier 3** (provenance) | **X-12 = P-a** reached independently, including the explicit refusal to call it leakage; **X-13 = T-f**. It does not reach P-b, P-c or P-d |
| **Tier 4** (the ledger) | **X-3…X-7** show four of the five defects were introduced or left by this round's own writes (items 26–33) — the ledger needs them recorded as a *cost* of route A, not only as a gain |
| **Tier 5** (remaining routes) | **X-9 = M8**, **X-10 = M8 generalized**, **X-11** is new (fine-group harm), **X-14** is new and unreachable here |

## III.7 X-20 — the boundary: what the review does not cover

The review contains **no** treatment of ignorability, hidden confounding, unobserved covariates or
MNAR. It uses "positivity" exactly once, and only to separate two things this record also separates:
a training unit whose target mass is zero is not the same as a target-positive region with no
observed support (its §6 W3). Its list of alternative mechanisms for the U-Air reversal — zero-target
samples excluded, cross-sample parameter sharing, finite-window normalization, calibration
constraints — is an **algorithmic** list, not an identification-theoretic one. Its remedy (C4) is a
fixed-active-set control, which is the step *before* the identification question and is cheap.

So the axis this record flagged as its remaining open direction (Claude's new-report items 11 and 12:
MNAR selection and an unobserved covariate) is **neither covered nor substituted** by this review. What
the review does establish is that the cheaper predecessor of that experiment — holding the active set
fixed and varying only the weights — is now demanded by two independent reviews, and that its absence
is itself a repair condition.

## III.8 What changed in this record

1. **Part III added**, with the review kept verbatim beside it for citation.
2. **I.2 qualified**: Tier 1's "no open correctness item" now carries the X-1 exception.
3. **I.1, I.3, I.4** extended with pointers into Part III rather than new tiers.
4. **I.6 and I.7 re-ordered**: X-1, X-2 and X-3…X-7 now precede every remaining Tier-5 route, because
   they are claims the current build makes and the others are evidence it lacks.
5. **§7 items 35 and 36** added; **§7's open-defect table** gained rows for X-1…X-7 and X-4b.
6. **§8** gained the external-review block ahead of items 1–11, with the note that items 1–3 are now
   history rather than a queue.
7. **§11** extended with the four things Part III does not do.

**Added 2026-09-28.** 8. **I.1, I.2 and I.5** now record the closure of X-1 and the two corrections it
produced; 9. **I.6 and I.7** mark X-1, X-6 and X-21 done and add **X-21b** (the tooling still carries
the wrong constant and the old clause form); 10. **III.2** carries per-item status (X-1, X-6, X-21
closed) and the new **X-21** row; 11. **III.9** is the resolution record for the repair, with the
measurements, the acceptance evidence and what stayed open; 12. **§7 items 37–39** and the open-defect
table record the write, the audit and the withdrawn "only the `q` side fails" narrative; 13. **§11**
was corrected — its "Part III does not re-derive Proposition 3" sentence was superseded — and a
paragraph of §11 that a previous edit had left stranded after III.8 was moved back into §11.

Nothing in `TO_OVERLEAF_paper_tmc_r1_clean/` was edited by Part III itself; the build invariants
recorded after §7 item 32 therefore still held when Part III was written. That is no longer the
current build: on 2026-09-28 items 37–39 edited both `.tex` files on explicit instruction, and the
live invariants are the ones recorded there (main **16 pp.**, supplement **16 pp.**, 41 equations,
0 errors, 0 undefined, 0 overfull).

## III.9 Resolution of X-1 — 2026-09-28

Written because the user asked for the repair, then for this record to carry it. Scope: `main.tex`
and `appendix.tex` only, plus the read-only audit under `results_prop3_audit/round_v1/`; no training,
no change to any experimental results table, no git operation. The two files were snapshotted to
`snapshots/2026-09-28-pre-prop3-fix/` before the first edit.

**What the review's X-1 claimed, and what survived checking.** Both halves were verified in-source
before anything was changed: (i) A6's clauses covered only `π_min` and `d_max`, so they could not
imply the inactivity of `p_min`, `q_min`, or of the composite ceiling — the reviewer's instance
(`π^tar=0.5, π^opp=0.01, p=0.2, a_max=40` gives `1/p = 5 ≤ 40` but `a = 250 > 40`) reproduces against
`main.tex:707–715` and `660–672`; and (ii) `ε_clip` was a positive part against the two ceilings, so
a floor-induced distortion produced `ε_π = ε_p = ε_q = ε_clip = 0` with `ã ≠ a*`, exactly the case the
old proof's displayed inequality needed to be empty.

**The repair.**

| element | before | after |
|:---|:---|:---|
| assumption | A6 = four objects inactive, from three clauses | **A6a** = the four clauses that actually imply inactivity *at the true margins*, with the ceiling on `π^tar/(π^opp p^obs)` (Design on) or `1/p^obs` (Design off); **A6b** = the three bounded interpolation errors on `π^opp`, `p^obs` and `q^use`, against `ε_π`, `ε_p` and `ε_q` respectively |
| residual | `ε_clip = max{(ã−a_max)_+, (d̃−d_max)_+}` — ceiling excess only, not measurable from released data | `ε_stab,r = ‖β_r^T − β_r^⋆‖₁` — what the stabilizers move at the **true** margins, measurable on a released trace |
| Proposition 3 | assumes A1, A4–A6; bound `C₁(ε_π+ε_p+ε_q+ε_clip)` | assumes A1, A4, **A5, A6b**, plus `1^⊤b_r^T ≥ B_min` and shared `A_r, M_r, C_r`; bound `C₁(ε_π+ε_p+ε_q) + ε_stab,r` |
| envelope | `C₁ ∝ max{d_max/(π_min²p_min), d_max/(π_min p_min p_min^true), a_max/(q_min q_min^true), a_max+d_max}` | `C₁ = (2K_rn_r/B_min)(d_max·max{L_π,L_p} + a_max·L_q)`, `L_π=π^tar_max/(π_min²p_min)`, `L_p=π^tar_max/(π_min p_min²)`, `L_q=min{q_min^{-2}, d_max²}`; Design off: `L_π=0`, `L_p=1/p_min²` |
| proof | one Lipschitz display and one mass display, both needing A6 | four steps — T's Lipschitz property (no A6a), mass error (implementation-side bounds only), the Hájek step `‖x/1^⊤x − y/1^⊤y‖₁ ≤ 2‖x−y‖₁/1^⊤x` at `x=b^T`, triangle inequality — plus a support lemma (`a>0 ⇔ π^tar>0 ⇔ a^⋆>0`) |
| corollaries | — | (a) A6a ⇒ `ε_stab = 0` and the sharp form returns; (b) Design off contributes nothing from the observation side iff `p^obs ≥ p_min` and `1/p^obs ≤ a_max` |

The bound is *not* claimed to be informative: at the frozen `π_min = 10^{-6}`, `L_π ≤ 2×10^{13}`, so
the envelope is vacuous and the paper now says so; the term with numerical content is `ε_stab`.

**X-21, found while executing X-1.** The audit's a-side reading was wrong twice over: it tested
`1/p^obs ≤ a_max`, which does not bound `ζ̂^o/max{p̂^obs,p_min}`, and it used `a_max = 40` while the E3
runs resolved **20**. `run_e3_real` calls `build_full_runner` without any weight-safety override
(`src/raven_mcs/e3/real_runner/runner.py:471–484`), so the defaults at
`src/raven_mcs/training/window_runner.py:1433–1437` are the operative constants; `40` belongs to the
E1-R2 calibration and to the E2 traffic runner.

**The measurements** (`results_prop3_audit/round_v1/A5A6_EPS_STAB.{json,md}`, script
`compute_a5a6_eps_stab.py`; an independently written second implementation `compute_eps_stab.py` /
`EPS_STAB.json` reproduces them to twelve significant digits).

| reading (true margins, frozen `A_r`, 20 seeds) | SensorScope | U-Air |
|:---|:---|:---|
| active windows / active client-windows | 1877 / 4849 | 1402 / 2923 |
| A6a Design-on clause `max π^tar/(π^opp p^obs)` vs `a_max = 20` | **19.26 — holds, narrowly** | **23.47 — fails** |
| client-windows above the ceiling | 0 (0 %) | 80 (2.74 %) |
| `ε_stab` median / p95 / max | 0 / 0.0719 / 0.553 | 0 / 0.0528 / 0.680 |
| windows with `ε_stab > 0` | 10.71 % | 11.13 % |

Two consequences the record must carry. First, **the "the failure is a property of the usable-update
stage" narrative is withdrawn**: under Design on the opportunity stage contributes through the
composite ceiling, and on U-Air that clause is the one that breaks. Second, the Design-on clause is
**threshold-dependent** — it fails at 20 and would pass at 40 — so any future change of `a_max` has to
re-run this reading.

**Verification performed.** Acceptance greps: `\varepsilon_{\mathrm{clip}}` 0, `eq:eps_clip` 0,
"clipping residual" 0, bare `A6` 0 (A6a 23, A6b 13); numbered equations still **41**, with
`eq:eps_stab → 37`, `eq:g4_beta → 38`, `eq:g4_alpha → 39`, `eq:g4_comp → 40`, so every frozen literal
in `appendix.tex` still points where it did; `tools/freeze_appendix_refs.py --check` reported 4 refs
to freeze and 0 unresolvable, and `--apply` was run (appendix-internal refs kept dynamic, 59 of them).
The reviewer's counterexample was re-run against the new A6a (fails, as it should) and `ε_stab > 0`
there; a synthetic all-stabilizers-inactive case returns exactly 0. The audit re-check reproduces the
published readings it does not change (`min p^obs = 0.1925`; `q_min` floor 5.224 %/5.184 %;
`q < 1/d_max` 24.218 %/23.750 %; all-records 41.525 %/41.859 %). The independent implementation adds
that `π^tar` matches the values stored in the frozen run state (`delta_cs_state_v6`, 27054/16227 rows,
max abs diff 0.0), that `A_r` is identical across all nine arms writing `window_metrics.json`, and
that with Design off the observation-side contribution to `ε_stab` is exactly 0 — which is corollary
(b) holding empirically.

**What this resolution does not do.** It does not touch X-2 (the §VII-F claim form), X-3, X-4, X-5,
X-7 or X-4b; it does not re-run the headroom experiments; it does not change any empirical number; it
does not fix the tooling, so `tools/a5_a6_support_audit.py` still defaults to `--a-max 40` and still
reads the `1/p^obs` form (recorded as X-21b in I.7); and it costs one page on the supplement
(15 → 16 pp.), because the four-step proof, the support lemma and the two new audit rows do not fit in
the space the old text occupied.

---

# Part IV — The 2026-10-03 evidence refresh: what closed, what moved, and what the paper still owes

Written because the user asked for a dated diagnostic entry covering the v4 contribution rewrite, the
register fix, the design-repair round, the round-7 closure table, the round-v4/v5/v5.1/v5.1a amendment
chain, the θ-canonical re-sourcing, the gatekeeping round, the errata index and the unlock arithmetic.
Status vocabulary: `closed` / `partially closed` / `open` / `new`. Every line anchor below is in
`TO_OVERLEAF_paper_tmc_r1_clean/main.tex` as it stands after this part's companion manuscript pass
(2 242 lines at the time of writing; the pre-pass snapshot is
`snapshots/2026-10-03-pre-evidence-errata/main.tex`, 2 234 lines). The audit's `P0`/`EA`/`FL` anchors
were quoted against the 2 226-line state and have drifted by up to +8 lines.

## IV.1 The v4 contribution rewrite and the register fix (E1–E9) — `closed`, indexed

Both passes are already in the paper. Indexed here with their current line anchors; not re-narrated.
Source of the edit definitions: `ccfa-review-reports/raven-mcs-tmc-review-round6.md` §2 (E1–E9 plus the
Table I caption deduplication) and §3 (structure and length re-measurement).

| id | what it did | anchor now | status |
|---|---|---|---|
| v4 contribution rewrite | the third contribution item was rewritten to separate the projection from the other (P2) terms and to drop the unsupported attribution | L235-249 | `closed` |
| `E1` | registered-interval wording, no null-equivalence claim (`statistically equivalent` = 0 hits) | L240-242 | `closed` |
| `E2` | band denominator named as the **same-support hindsight optimum** | L609-611 | `closed` |
| `E3` | κ=1000 projection-with-debt rule labelled a new rule of this study and exploratory; frozen-strength `+0.0073` pp stated separately | L2088-2092 | `closed` |
| `E4` | projection tolerance `1e-10`; replay residuals reported as a residual, not an identity; exploratory status at the point of use | L2229-2235 | `closed` as an edit — its *explanation* was false, see the manuscript pass item 5 |
| `E5` | flatness mechanism: `3279` windows, `ℓ₁` range median `1e-13` | L970-974 | `closed` |
| `E6` | broken duplicated sentence restored in §VII-A | L1551-1555 | `closed`; its grammar defect is round-6 `F4`, still `open` |
| `E7` | unsupported "their oracle values" clause deleted | L1848-1850 | `closed` |
| `E8` | (27) re-scoped to a one-sided residual bound, not a benefit term | L1852-1854 | `closed` |
| `E9` | "does not amplify in α, per (eq:g4_alpha)" qualified | L227-228 | `closed` |

Round 6 also recorded **six undeclared edits** beyond the E1–E9 list; all were inspected there and none
produced a new defect, but the declared edit list was not exhaustive. That finding is not re-opened here.

## IV.2 Design-repair round: P0-1…P0-3, EA-1…EA-3, two deletions, the band label, and its own defect F5

Source: `ccfa-review-reports/raven-mcs-experiment-design-audit.md` §8 (edit table, deletions, length and
structure accounting, compile verification) and `…-review-round7.md` §2 (independent per-edit
verification).

| element | evidence behind it | anchor now | status |
|---|---|---|---|
| `P0-1a` frozen-configuration scope in the contributions | `round_v2/PHASE4_INPUT_GAPS.md:72` (λ_g = 1.0, λ_β = 1.0, λ_v = 0.1, λ_s = 0.1); `round_v4/PREREG.md:52` (η = 0.01) | L229-234 | `closed` at the P0-1 standard; text strengthened by the companion pass, which names the κ=1000 rule as outside the verdict |
| `P0-1b` frozen-configuration scope at the results verdict | same; `round_v4/TRADEOFF_PAIRED.csv:26,61` (κ=1000 arm outside the band) | L1845-1851 | `closed`; text strengthened the same way |
| `P0-2` closable-gap value once per dataset + four qualifiers + non-convertibility | `round_v2/PHASE3_REPORT.md:77` (3.44 pp SensorScope / 1.32 pp U-Air `R_on`, 20 seeds); `round_v2/EXECUTION_REPORT.md:118` (report-half `Δ*` 0.97276 / 1.06311, gaps 3.12 / 1.33 pp) | L609-615 | `closed` |
| `P0-3a` decision rule + practical-significance status + necessity half | `round_v1/PREREG.md:43-44`; `round_v3/EXECUTION_REPORT.md:105` | L610-616 | `closed` |
| `P0-3b` `ℓ₁` scoping of the flatness sentence | `MYOPIC_DIAG.json:3-13` (ℓ₁ surface only); the uniqueness theorem | L970-974 | `closed` |
| `\label{subsec:equivalence_band}` | new label so the results text can cite the band | label at L573, cited at L1850 | `closed` (`main.aux` → III-F, p. 5; `\label` 96 → 97) |
| `EA-1` debt-ablation ruler | `E4_ABLATION_HOLM_RESULTS.csv` (the ablation statistic is a relative change) | L2081-2083 | `closed` |
| `EA-2` worst-group equivalence wording | "descriptive rather than a formal non-inferiority test" | L1781-1783 | `closed` |
| `EA-3` necessity half of the band rule | `round_v1/PREREG.md:43-44` (necessity = interval entirely beyond +0.10) | L614-616 | `closed` as a *rule*; the per-component necessity verdicts are the audit's `FL-6`, still `open` |
| deletion 1 | §VII intro roadmap paragraph, deleted in full; every deleted statement survives in the RQ bullets, the Introduction, Table I's caption and §VII-B | `\subsection{Experimental Setup}` now follows the RQ bullets at L1453 | `closed` |
| deletion 2 | §VII-C "Development-table findings", two duplicated runs removed; the paragraph's non-duplicated content retained verbatim | L1925-1935 | `closed` |
| measurement | length 2 230 → 2 226 lines; structure counts unchanged at 4 / 4 / 37 / 42 / 8 / 29 / 4 / 2 with `\label` 97; 17 pp, 0 errors, 0 undefined, 0 overfull | `…-review-round7.md` §2 | `closed` |

**`F5` (found by round 7 in this repair; provenance `previously_undetected`).** The frozen-configuration
scoping of `P0-1a`/`P0-1b` put the **prediction half** of the scoped verdict in direct tension with the
paper's own ablation at exactly the configuration the verdict named: the verdict read "instantaneous
calibration and debt are neither **prediction drivers** nor structural contributors", while Table IV's
U-Air `Inst` row reads `+0.143 %` on `RMSE_μ` and `+0.149 %` on Tail RMSE, both `p_Holm = 0.0194`. Status
before this part: **`open`**. Round 7 rated it moderate and `writing`-owned, and round 6's own evidence
table already showed the tension.

**What the companion manuscript pass did to it.** The contribution sentence no longer states a prediction
null. It now reads that at the frozen configuration instantaneous calibration and debt "are not structural
contributors", names the κ=1000 rule as outside that verdict, and states that the prediction half "is not
a null, but the small Inst reading of Table IV"
(L229-236). The words "prediction drivers" are gone from the paper, and the null is replaced by a citation
to the table that carries the effect. The adjacent `F6` dangling reference is repaired in the same
pass: the trained-rule paragraph's "(the value the read-only ladder above also gives)" becomes "the value
of the results section that prints it also gives" (L2088, now citing `subsec:eval_rq2`).

**Status: `partially closed`.** `F5`'s *wording* is discharged at the verdict and the contradiction is no
longer in the reader's path, which is the standard round 7 set and is now met. What keeps it short of
`closed` is that the remaining tension is statistical rather than rhetorical and no text edit settles it:
§VII-H still reports the U-Air `Inst` removal as Holm-significant on `RMSE_μ` and Tail
(`0.143 %` / `0.149 %`, `p_Holm = 0.0194`, L2082-2083) while the contribution states no prediction driver,
and round 7's closure table still lists `F5` as an open issue against the version it reviewed. A later
round must either reclassify that row or accept the audit's `FL-6`/`FL-7` point that the `Inst` arm is not
a clean single-component removal: `CONFIG_REGISTRY.csv` shows `λ_g = 0.0` only for `w/o-Inst`, so the
removal changes the objective's group term as well.

## IV.3 Round-7 closure table: 9 closed / 6 partial / 8 open, plus `F6`, and the `R5-13` correction

Source: `ccfa-review-reports/raven-mcs-tmc-review-round7.md` §6 (23 rows: `R5-1`…`R5-17`, `C1`, `C2`,
`F1`…`F4`) and §7 (new findings `F5`, `F6`). Round 7's verdict was **5/10 weak reject, upper edge**,
weighted readiness sum **2.90**, relative progress **0.00**: no dimension could rise because a sibling
open issue still carried each deduction.

* **Closed (9):** `R5-2` (band decision rule + non-test status, L610-616), `R5-3` (band denominator named
  and valued, L609-615), `R5-4` (failed pre-registered gates disclosed at the point of use, L2092 and the
  availability statement), `R5-6` ((27) as a one-sided bound, L1852-1854), `R5-7` ("does not amplify"
  scoped to α, L227-228), `R5-9` (unsupported "their oracle values" clause deleted), `R5-12` (dangling
  duplicated clause in §VI-A), `R5-14` (band verdicts in consistent units), `F1` (the flatness sentence no
  longer reads against the uniqueness theorem). **`closed`.**
* **Partially closed (6):** `R5-1` (verdict scoped in both required places; the κ=1000 identity clause and
  the ablation necessity verdict still absent — see IV.8), `R5-5` (flatness narrowly scoped; the *why* and
  the tie-break result `Δ_myo_tb = 1.05140` still uncited — grep `1.05140` = 0 hits), `R5-11` (body prints
  the U-Air RMSE cost; the abstract sentence still lacks a ruler), `R5-15` (label and disclaimer landed;
  placement is still a modelling subsection), `R5-17` (`M_r`-drift ruler caveat still only in the
  availability section), `F2` (residual "interchangeable" sense at L1934). **`partially closed`.**
* **Open (8):** `R5-8` (`Proj_{C_r}(β̂)` undefined at first use, L245-246; every `Proj` hit is a use, none
  a definition), `R5-10` (the (43) coefficients unlabelled as U-Air Table IV entries, L2039-2041), `R5-13`
  (abstract `6.55 %` vs body/table `6.885 %`), `R5-16` ("recoverable" names two headroom objects), `C1`,
  `C2`, `F3` (abstract `1.24 %` has no ruler), `F4` (doubled connectives at L1551-1553). **`open`.**
* **`F6` (new, minor):** the caveat introduced by `P0-2` used "read-only ladder contrasts" with no
  definition, 1 459 lines before its only other use, and the paper has no ladder table or arm list
  (grep `ladder` = 2 hits). The companion pass **removes the dangling occurrence**: the trained-rule
  paragraph's "(the value the read-only ladder above also gives)" becomes "the value
  the results section that prints it also gives", which points at the results section that actually
  carries the `+0.768` pp value. **The band paragraph's occurrence at L618 is deliberately kept**, because the
  round-7 `P0-2` requirement is precisely that statement — the read-only ladder contrasts use the
  report-half subset whose optimum differs, so band verdicts are not convertible between the two — and
  deleting it would drop a required qualifier. `ladder` therefore goes **2 → 1 hits, not to zero**, and
  `F6` is **`partially closed`**: the dangling reference is repaired, but the term still has no
  definition and the paper still has no ladder table. A one-clause definition in the band paragraph
  remains the smallest outstanding fix.

**The round-7 correction of record for `R5-13`.** Round 6 read the abstract `6.55 %` (abstract, L87) and
the body `6.885 %` as "different contrasts/objects". They are **not**: both name the U-Air `RMSE_μ` cost of
Design (abstract "on U-Air it costs `6.55 %` of RMSE"; body "costs `6.885 %` of `RMSE_μ` … on U-Air";
Table IV's U-Air Design row `-6.885^ast`). It is **one object with two values, not two objects**, and the
evidence (`tables/E4_ABLATION_HOLM_RESULTS.csv`; `round_v4/PART_A_REPORT.md`) supports only `6.885`, so
the abstract figure has no source. **Resolved in substance, verified here:** the current abstract no longer
contains `6.55` (grep = 0 hits); it reads "on U-Air, turning Design on costs $6.885\%$ of RMSE and improves
client--stratum mismatch by $4.990\%$", i.e. the surviving value is the evidenced one. `R5-13` is therefore
**`closed` in the file**, even though round 7's closure table lists it `open` against the version it
reviewed. What remains genuinely **`open`** is the `F3`/`R5-11` half: that abstract sentence still carries
no ruler and no baseline, and the adjacent SensorScope sentence quotes `+0.768` and `+0.922` points without
naming the uniform-weight ruler or the closable-gap units in which they are measured.

## IV.4 The round-v4 / v5 / v5.1 / v5.1a chain: what the amendments fixed and what is still `approximate`

**Why v5's gates failed.** Both failures were protocol strictness, not rule failures. `G-self` demanded
`α L∞ = 0` exactly, and the measured value was `6.45e-09` (U-Air `proj_beta`, seed 30001) with endpoints
still agreeing to `≤ 4.4e-15`, so A1 stopped on a solver artefact (`round_v5_1/AMENDMENTS.md` AM-1;
`round_v5/ERRATA_FOR_PAPER.md` E-v5-1). The `G-xref` gate measured spread across solver paths, which is the
wrong ruler for a strictly convex projection whose optimum is unique, and it compared two *different*
problems, because the `raw`/`β/Σβ` axis projects a different point (AM-2).

**What AM-1…AM-5 amended** (`round_v5_1/AMENDMENTS.md`). AM-1: `α L∞ ≤ 1e-8` **and** both endpoints
`≤ 1e-12` against `final_metrics`. AM-2: `G-xref` replaced by an **exact numpy projection oracle** with
gates O-G0 (KKT per window), O-G1 (objective against a fresh CVXPY CLARABEL solve at `1e-12`, projected
back onto `C_r`) and O-G2 (uniform control), with the verdict `certified` iff `max eps_impl ≤ 5e-6`, else
`approximate`. AM-3: the A2 stop rule replaced by a three-part G0 with the trigger set **fixed in advance**
as `{uair} × {30007, 30016, 30018} × 6 arms` = 18 rows, θ-canonical for every row. AM-4: the
WorstGroupRMSE tolerance became `1e-8` **relative** (observed `1.95e-09`). AM-5: five TOST labels plus
`inconclusive`, because v5 let "equivalent" and "harm" overlap.

**The corrected oracle (round v5.1a, `AMENDMENT_AM-6.md`).** The v5.1 oracle was *suboptimal*, not merely
imprecise: its O-G1 sample objective exceeded a feasible comparator by `+1.11e-06`, which is impossible for
an exact projection. AM-6 replaced the three-level active-set enumeration with the standard two-multiplier
dual and removed SLSQP from the production path; **no rule, threshold, margin, family or contrast moved**.
Outcome (`round_v5_1a/O_GATES_RERUN.json`, `ORACLE_EVIDENCE.json`):

| gate | v5.1 | v5.1a | tolerance | pass |
|---|---|---|---|---|
| O-G0 primal (6 558 windows) | 9.41e-13 | **6.66e-16** | 1e-13 | yes |
| O-G0 complementary slackness | 3.81e-08 | **4.88e-17** | 1e-12 | yes |
| O-G0 stationarity | 7.22 | **6.67e-01** | 1e-12 | **no** |
| O-G1 objective (200 windows) | +1.11e-06 | **+9.64e-12** | 1e-12 | **no** (7/200) |
| O-G2 uniform control | 0.0 | **0.0** | 0.0 | yes (K = 1…64) |
| small-K brute force (142 cases, K = 2…5) | — | **worst objective gap 9.95e-14** | 1e-14 | fail by 10× |
| feasible-perturbation test (122 094 points) | — | **worst improvement 0.0** | 0 | **yes** |

* **The oracle is optimal to `1e-13` in objective value** on the independent small-K brute force, and no
  feasible perturbation improves it.
* **The two remaining gate failures are each diagnosed, and neither is smoothed over.** (i) The stationarity
  residual is a **metric artefact**: in the `τ + 2λa` form the residual cancels catastrophically on the
  `K = 3` near-uniform ball points, where the multipliers themselves are `~1e9` and are not representable in
  double precision. The returned points are feasible to `1e-15`, sit on the ball to the last bit, and are
  never beaten by a feasible perturbation. (ii) O-G1 is **comparator-limited**: CLARABEL returns
  `optimal_inaccurate` on **135/200** windows with raw infeasibility up to **5.16e-08**, and projecting its
  raw point back onto `C_r` is not an exact contraction for the flat `K = 3` debt problems.
* **`A1′` remains `approximate` with `eps_impl ≤ 2.42e-5`.** The four measured maxima are `9.07e-06`,
  `1.03e-05`, `2.42e-05`, `2.40e-05` in v5.1 and `3.96e-06`, `9.92e-06`, `2.42e-05`, `2.30e-05` on the
  rerun; `2.4e-05` in E-v51-1 §4 is the same quantity at one fewer digit.
* **Trained α is bit-identical to its own replay:** `alpha_linf_trained = 0.0` on all 160 measured cells,
  B-G1 reports 0 mismatching windows on 120/120 runs, and the endpoint residual against the unmodified
  repository replay path was `2.1e-06 … 8.6e-05`, a property of the warm-started solver path rather than of
  a different problem.
* **All 20 structural contrast verdicts are unchanged** with the oracle endpoints in place of the trained
  ones: max `|Δpp| = 6.18e-04` pp (`Delta_group`, `proj_beta_debt − proj_beta`, SensorScope), max on
  `Δ_c-s` `3.38e-04` pp, and no `p_holm` crosses `0.05` in either direction.
* **What is still not settled, stated plainly:** the point-level evidence tolerance is `1e-8`, not the
  `1e-12` the rerun set for itself; the stationarity gate as written does not pass; and O-G1 at `1e-12`
  does not pass. **`partially closed`.**

## IV.5 The v5.1 θ-canonical re-sourcing of the U-Air Part B cells — `closed`, with no manuscript target

Source: `round_v5_1/ERRATA_FOR_PAPER.md` E-v51-4; `round_v5_1/A3P_RESOURCE_UPAIR.csv`;
`round_v5_1/A3P_SUMMARY.json` (`n_cells_differing_4sig = 6`).

**All six U-Air Part B `RMSE_μ` cells and all five U-Air paired `RMSE_μ` rows differ from v4 at the 4th
significant digit.** Cell means (v4 → θ-canonical): `proj_beta` `1.19248 → 1.19691`, `proj_beta_debt`
`1.19037 → 1.19470`, `inst_cal` `1.19112 → 1.19537`, `raven` `1.19111 → 1.19537`, `uniform_window`
`1.18936 → 1.19349`, `fedavg_window` `1.18824 → 1.19225`. Paired rows (mean diff, 95 % CI, `p_holm`):

| contrast | mean diff | 95 % CI | `p_holm` |
|---|---|---|---|
| `proj_beta − uniform_window` | 0.003120 → **0.003418** | [0.000805, 0.005372] → **[0.000901, 0.005919]** | 0.1332 → **0.1198** |
| `raven − proj_beta` | −0.001363 → **−0.001544** | [−0.002555, −0.000247] → **[−0.002812, −0.000340]** | 0.1332 → **0.1198** |
| `proj_beta − fedavg_window` | 0.004240 → **0.004658** | [−0.000764, 0.009599] → **[−0.000492, 0.010110]** | 0.3420 → **0.2462** |
| `uniform_window − fedavg_window` | 0.001120 → **0.001240** | [−0.004098, 0.007099] → **[−0.003932, 0.007334]** | 0.8408 → **0.9273** |
| `proj_beta_debt − proj_beta` | −0.002103 → **−0.002212** | [−0.004315, −0.000024] → **[−0.004323, −0.000104]** | 0.3420 → **0.2276** |

**SensorScope is unaffected**: the θ re-score reproduces `final_metrics.json` bit-exactly on all 120 rows,
so its manuscript values stand. No verdict moved: the v5 label and the v5.1 label agree on all 8 primary
rows once the AM-5 vocabulary is applied to the v5 interval (`A3P_SIDE_BY_SIDE.csv`).

**Manuscript consequence, and the reason this item needed no edit.** The claim that Part B's U-Air
`RMSE_mu` values need re-sourcing presumes the paper prints them. **It does not.** A full-text search of
`main.tex` and `appendix.tex` finds none of the six θ-canonical cell means (`1.19225`, `1.19537`,
`1.19349`, `1.19691`, `1.19470`), none of the five v4 paired values, and none of the five θ-canonical
paired values. The trained-rule paragraph prints only the **group**-endpoint means plus three quantities
that sum to the same numbers: `0.98464` / `1.01158` / `1.01394` / `1.01409` / `1.02693` / `1.05577` on
SensorScope and `1.08001` / `1.09162` / `1.09236` / `1.09241` / `1.09734` / `1.12176` on U-Air, with
`+0.768` pp, `+1.347` pp, `+0.580` pp, `+0.0073` pp and `+0.118` pp. The only paired-`RMSE_μ` statistics
actually on the page are "U-Air best raw `p = 0.027`, `p_Holm = 0.133`", which is the **v4** trained-rule
`RMSE_μ` family: `round_v4/TRADEOFF_PAIRED.csv:32` (`proj_beta − uniform_window`, the family's best raw
`p = 0.026642`) and `:33` (`raven − proj_beta`, `p_wilcoxon 0.029575`), both with `p_holm = 0.133209`. The
θ-canonical counterparts are `0.0227` / `0.1198` and `0.0296` / `0.1198`. Replacing them would put a
different number on the page for no verdict change, so they were left alone and recorded here instead.
**`closed` as a re-sourcing finding; `open` only as a one-digit θ-consistency of `0.027` / `0.133` in
§VII-H, for a future hygiene pass.**

**Adjacent cells this pass could not fix.** `appendix.tex` prints U-Air `RMSE_μ` values that are canonical
against the **round-v4 θ** tree (`Local-Hajek 1.1923`, `Inst-Cal 1.1954`, `RAVEN-Design 1.1954`,
`RAVEN-SimOracle 1.1958`, `TwoStage-Hajek 1.2202`) and not against the round-v5.1 θ table
(`uniform_window 1.19349`, `inst_cal 1.19537`, `proj_beta 1.19691`, `proj_beta_debt 1.19470`).
`appendix.tex` is outside this pass's edit scope, which is `main.tex` only, so the discrepancy is recorded
here rather than corrected. **No main-text number depends on those rows.**

## IV.6 Gatekeeping round (A1 + Part B at r = 3) — mostly `new`, one `measured null`

Source: `results_gatekeeping/round_v1/EXECUTION_REPORT.md` (Part A §1-§3, Part B §B.1-§B.11),
`A1_DESCRIPTIVE.csv`, `A1_POWER.csv`, `C1_PRIMARY.json`, `C1_A1_CHAINS.csv`, `C1_MAPS.json`, and its
`ERRATA_FOR_PAPER.md` (`E-A1-1`…`E-A1-13`, `E-B-1`…`E-B-11`).

**The A1 hierarchy.** One chain per `(dataset, arm)` against `fedavg_window`, tested in order and gated:
**H1 structure** (paired Wilcoxon on the structural endpoint) → **H2 non-inferiority**
(`RMSE_μ(arm)/RMSE_μ(fedavg) − 1 < δ`, decided by the Hodges–Lehmann estimate and the one-sided 95 % upper
bound of its Wilcoxon-inverted interval, `U_wilcox < δ`) → **H3 superiority** (tested only if H2 was
rejected, `L_wilcox > 0`). α is split by a **graphical Holm (Bretz–Maurer–Brannath–Posch) family within
each dataset, never across datasets**, with equal initial weights `1/K`; City Scanner is a family of size
one. Margins: **δ = 0.5 %** on SensorScope and U-Air, **δ_CS = 2 %** on City Scanner, declared before any
A1 number was computed.

**Descriptive results** (every row is labelled `post hoc descriptive` and must never be cited as
confirmatory):

* **SensorScope completes H2 for both arms.** `raven` HL `−0.000131` with one-sided upper bound
  `+0.000241`; `proj_beta` HL `−0.000273` with upper bound `+0.000305`; both below δ = 0.5 %, at the
  signed-rank resolution floor `p = 9.537e-07`. H3 is not rejected in either chain, because the HL point
  estimates are negative.
* **U-Air H2 is not rejected.** `raven` upper bound **+0.54 %** (1.09 × δ), `proj_beta` **+0.77 %**
  (1.54 × δ). Both chains land just under the preregistered `power(θ = 0) ≥ 0.80` testability rule at
  `0.697` / `0.674`, but their `MDE₈₀` is **−0.076 %** / **−0.093 %**, so the margin is inside their
  80 %-power range and the observed failures are informative rather than artefacts of low power.
* **City Scanner H2 is untestable** at δ_CS = 2 % with the ten event traces that exist: power `0.120` at
  r = 1 and at most **0.153** anywhere in the admissible σ_W range (r = 5, most optimistic scenario; the
  trace-cluster bootstrap puts the same cell at 0.176), with `MDE₈₀` **+6.0 % … +8.6 %**, that is **3–4 ×
  the declared margin**. The binding term is the between-trace variance, which no number of model seeds on
  the same ten traces can reduce. This is `E-A1-8`, filed as a result rather than a caveat.
* **The protocol's own §0 summary row does not reproduce** (`E-A1-13`): `raven − raven_wo_design` gives
  relative mean `+2.368 %` here against the protocol's `+2.45 %`, median `−0.625 %` against `−0.22 %`, and
  8/10 against 7/10 seeds lower, **while the absolute per-trace values are bit-identical to the frozen
  table on 200/200 cells**. The mismatch is a **convention** difference, per-trace ratio versus pooled, and
  no conclusion of the round depends on the row. **`open` as a protocol-text defect.**

**Part B at `r = 3`** (150 newly trained rows and 30 reused frozen rows, zero failures, no TBDs):

* **B0-a is bit-exact: PASS.** Both frozen seed-32001 rows reproduce with `max |Δ| = 0.0` on every endpoint
  (`RMSE_mu`, `WorstGroupRMSE`, `Delta_group`, `Delta_c_s`) and with a matching `eventtrace_hash`. A side
  check showed that forcing `torch.set_num_threads(1)` *breaks* bit-exactness (`4.2e-08` on `Delta_group`),
  so every Part B run uses the frozen default thread configuration (`E-B-1`).
* **The seed-32005 anomaly is trace-driven, not a single-seed instability** (`E-B-7`). On trace 32005
  alone, both arms, five model seeds, the ratios are **+38.46 % / +28.73 % / +24.45 % / +35.43 % /
  +30.78 %** (mean +31.57 %, SD 5.52 pp, 5/5 seeds ≥ +20 %). The registered training-instability-outlier
  language is therefore **not licensed**, and the primary is computed on all ten traces.
* **Maps and coverage** (`C1_MAPS.json`): all four maps cover all **959** `(client, stratum)` keys in the
  union of the ten traces' risk sets, with `n_missing = 0`; π_floor = `4.784688995215311e-04`, more than
  480 × the ζ denominator floor `1e-6`; control realized ρ = **0.143450** (range 0.1296–0.1553), which
  reproduces the frozen 14.35 %; floor realized ρ = **0.000000** by construction; M1/M2 realized ρ ≈ **1 %**
  (0.010077 / 0.009848).
* **Primary `H_mech` is inconclusive** (`C1_PRIMARY.json`): HL paired relative difference **−0.000192**,
  percentile trace-cluster bootstrap CI **[−0.018930, +0.122754]**, two-sided paired Wilcoxon
  **p = 0.9219**, power at δ_CS = 2 % **0.151**, `MDE₈₀ = −6.10 %`, 3/10 traces where the control arm is
  worse. The reading is identical under the percentile, basic and Wilcoxon-inverted intervals. `E-B-6`.
* **Structural guardrail retained: 101.9 %.** `Δ_group(fedavg)` 0.195335, `Δ_group(ctrl)` 0.070644,
  `Δ_group(floor)` 0.068224, so the floored arm keeps **1.0194** of the FedAvg→RAVEN `Δ_group` gain
  (per-trace 0.871–1.328), far above the 50 % B3 threshold. `Δ_c-s` is **not** like-for-like across arms,
  because each is measured against its own `π^tar`: 0.812260 / 0.567578 / 0.789248 (`E-B-5`).
* **Secondary family (m = 4): none rejected.** Holm thresholds 0.0125 / 0.0167 / 0.025 / 0.05;
  `M2mu − ctrl` p = 0.4922, dose slope `+0.044061` p = 0.541, `ctrl_floor − wo_design` p = 0.6250,
  `M1mu − ctrl` p = 0.9219. Two are informative as description only: the cost of the tilt alone is
  `+0.06 %` with a `±0.6` pp CI, and the dose slope flips sign to `−0.005` when trace 32005 is removed, so
  no dose-response claim is supported.
* **H2 is unreachable for all three new arms.** The whole one-sided 95 % interval lies above +2 %
  (3.83 %, 4.14 %, 8.15 %), H3 is not tested anywhere, and H1 is confirmed for all three on 10/10 traces at
  the n = 10 resolution floor `9.77e-04` (`E-B-8`).
* **B3 applied mechanically gives row 3**: `H_mech` inconclusive, so the round reports the interval and the
  power, makes **no mechanism claim**, adds no traces or model seeds, and does not raise `r`. Row 4 does not
  trigger, because B0-b shows the anomaly at all five seeds.

**The two statements that follow from this round, and where each now lives.**

1. **The reported Design cost is neither shown to be a deletion effect nor shown to be free.** The floored
   arm zeroes the deletion, keeps 101.9 % of the structural gain, and the deletion contrast is
   under-powered at 0.151 against δ_CS, at n = 10 traces and r = 3. **Applied to the manuscript** as a
   Limitations sentence, because the paper states a Design cost on U-Air and SensorScope and the reading
   must not be over-claimed in either direction.
2. **Trace 32005 must be described as a trace-level outlier, not a training-instability one.** The
   registered language for the alternative is explicitly *not licensed* by B0-b (`E-B-7`). **Applied** as a
   Limitations sentence, together with the fact that the no-trace recomputation is a declared sensitivity
   and never primary (`E-A1-9`).

**Evidence-axis status: `measured null`, not a missing experiment.** R1, whether structural alignment
converts into prediction, is closed as a measured null. The SensorScope dose interval excludes the 0.25 %
effect decisively and the U-Air dose interval excludes it marginally, which is the clause that closed R1;
the dose-response slope includes zero on both datasets and the U-Air point estimate has the opposite sign.

## IV.7 Errata index and the protocol-level defects found

| index | file | items | status |
|---|---|---|---|
| `E-v5-1`…`E-v5-3` | `round_v5/ERRATA_FOR_PAPER.md` | the `M_r`-drift explanation is false; the worst-group column is `TBD` behind the A2-G0 stop; the prediction statement must use the equivalence/harm vocabulary | **superseded** by `E-v51-*` |
| `E-v51-1`…`E-v51-4` | `round_v5_1/ERRATA_FOR_PAPER.md` | trained rules and the deleted "reference not numerically stable" phrase; worst-group scores and the AM-5 non-inferiority labels; the AM-5 prediction statement; the θ-canonical Part B re-sourcing | `E-v51-1` and `E-v51-4` re-confirmed by `round_v5_1a`; `E-v51-2` and `E-v51-3` untouched and carried into the gatekeeping round |
| `E-A1-1`…`E-A1-13` | `results_gatekeeping/round_v1/ERRATA_FOR_PAPER.md` | the power column is one point not a curve; the "n = 10 seeds" are ten event traces; the City Scanner rows were not θ-re-scored; `raven_wo_design` is not an A1 comparator on City Scanner; no `proj_beta` City Scanner row exists; H1 p-values sit on the resolution floor; U-Air sits just under the 0.80 line; **City Scanner H2 is unreachable, a result not a caveat**; the seed-32005 sensitivity is never primary; the θ-canonical values differ from v4 at the 4th digit; Part B was not authorised; a confirmatory H2 needs new traces rather than more seeds; **the protocol's §0 `raven − raven_wo_design` row does not reproduce** | `E-A1-8`, `E-A1-10` and `E-A1-13` are load-bearing; `E-A1-11` is superseded, because Part B was subsequently authorised as `授权C1训练，r=3` |
| `E-B-1`…`E-B-11` | `results_gatekeeping/round_v1/ERRATA_FOR_PAPER.md` | bit-exactness is thread-count dependent; the r = 3 run count is internally inconsistent (130 vs 150); the floored arm is not region-matched to μ; M1/M2 live on the control key support rather than the raw cross product; `Δ_c-s` is not comparable across arms with different `π^tar`; **the primary `H_mech` is inconclusive and the design is underpowered**; **the anomaly is trace-driven**; the confirmatory chains stop at H1; **the Part-A `MANIFEST.sha256` timeline block is duplicated with a stale hash**; the two reused Design-off arms have ρ = 0 by construction; three Part-A artefact hashes are historical, not stale-and-wrong | `E-B-6`, `E-B-7` and `E-B-9` are load-bearing |

**Two protocol-level defects, recorded as `open` because nothing in this pass repairs them.**

* **(a) The gatekeeping protocol §0 convention does not reproduce.** Its `raven − raven_wo_design`
  relative-difference summary is stated under a convention that the round's own per-trace ratio convention
  does not match, **while the absolute per-trace values are bit-identical to the frozen table on 200/200
  cells** (`EXECUTION_REPORT.md` §1.2; `E-A1-13`). The defect is in the protocol text's convention, not in
  the data, and no conclusion depends on the row.
* **(b) Part A's `MANIFEST.sha256` duplicated its registration-timeline block five times, and the first
  copy carries a stale intermediate PREREG hash.** Measured: the `# REGISTRATION TIMELINE` header occurs
  **five** times; copy 1 is truncated to the `t1` text and ends at the hash
  `4165f0dcab38e0711523f8bdc8da6eca350f32b28b68271be5c5cca3fc3fe572`, which appears in no copy of the
  `t2` text and in no other round file; copies 2-5 are identical to each other and carry the correct `t2`
  hash `1e1816cd3431a1c49c92f2806ab83b981b4392d216906af1323425c819f7719e`. The file also explains that a
  file cannot contain the hash of its own final bytes, which is why the executed hash lives in the manifest
  rather than inside `PREREG.md`. Recorded as `E-B-9`; the manifest is a round artefact and is outside this
  pass's edit scope.

## IV.8 Unlock arithmetic — explicit

From `ccfa-review-reports/raven-mcs-tmc-review-round7.md` §8, §11 and §12, restated as a closed sum.

* Round-7 weighted readiness is **2.90**, the overall stance is **5/10 weak reject (upper edge)**, and the
  relative progress delta is **0.00**. No dimension could rise because every deduction was still carried by
  a sibling open issue.
* **Closing `R5-1`'s remaining half together with `R5-8`, `R5-10` and `F4` takes Soundness 4 → 5 and
  Clarity 3 → 4, and the weighted sum 2.90 → 3.25**, with no new experiment. That is one clause naming the
  κ=1000 arm and the frozen-strength contrast as the same recursion at different weights, plus either the
  per-component necessity verdict or an explicit non-necessity disclaimer, plus three one-line
  disambiguations: define `Proj_{C_r}` at first use, label the (43) coefficients, and repair the doubled
  connectives.
* **`F5` is this part's extra term in the same sum.** It is `writing`-owned and text-only, and its wording
  is now discharged in the paper (IV.2), so it no longer blocks Soundness; what it still owes is the
  round-7 closure-table reclassification.
* **A 6/10 additionally requires the evidence axis, weight 0.25, to move, and that axis is now a
  `measured null` rather than a missing experiment.** The gatekeeping round converted it: the mechanism
  question is answerable, because H_mech compares two new arms on the same traces and is not the same power
  problem as H2, but the answer came back inconclusive, so no further run of the same design buys the
  score. The 6/10 path is therefore no longer "run the missing experiment".

## IV.9 What this part's companion manuscript pass changed, and what it deliberately did not

The full before → after list, the deletions and the length accounting are in the pass's own report; this is
the record-level index of the same set, with the final anchors.

| item | paper anchor now | source |
|---|---|---|
| `P0-1` frozen-configuration scope in the contributions, plus the κ=1000 exclusion and the `F5` narrowing | L229-234 | round-7 `P0` list; `F5` |
| `P0-1` frozen-configuration scope at the results verdict, plus the κ=1000 exclusion | L1845-1851 | round-7 `P0` list |
| statistics documentation: `10 000`-draw seed-level paired percentile bootstrap at seed `20261002`, and the Holm families actually used | L1624-1631 | the design audit's interval-type gap |
| `E-v51-1` reproducibility explanation replaced; "reference not numerically stable" and the "composition and mass inputs … vary weakly with the model trajectory" explanation deleted | L2225-2235 | `E-v51-1` items 1-3 |
| `eps_impl` stated as `6`–`16 %` of the small debt and Inst readings | L2073-2075 | `E-v51-1` item 4; `A1P_IMPL_RERUN.csv` |
| City Scanner H2 untestable, stated as a result | L2162-2164 | `E-A1-8` |
| trace 32005 as a trace-level outlier reproduced across five model seeds | L2164-2168 | `E-B-7`, `E-A1-9` |
| the Design cost is neither a shown deletion effect nor shown to be free | L2168-2170 | `C1_PRIMARY.json` guardrail; B3 row 3 |
| `P0-2`, `P0-3a`, `P0-3b` and the `\label` verified rather than re-edited; `F6`'s dangling "read-only ladder above also gives" replaced by a cross-reference to the results section | L573, L609-616, L970-974, L2088 | audit §8; round-6 `F6` |

**Length accounting and the deletions that offset the additions.** Measured with the same
newline-splitting convention for both files (`[System.IO.File]::ReadAllLines`): **2 234 → 2 242 lines
(+8)**, words **12 300 → 12 328 (+28)**, bytes **112 857 → 113 126 (+269)**. So the net length did
**not** come down to zero: eight additions worth roughly 16 lines were partly offset by eight
duplication-only deletions worth roughly 8 lines, and the 17-page count is unchanged because the
additions absorbed the tail-page slack. Every deletion below was verified before it was made; nothing
unique was removed.

| # | deleted passage | verified duplication |
|---|---|---|
| 1 | the two closing sentences of the contributions ("Usable-update correction and target debt remain in the factorization and in the accounting recursion.  At the frozen strength they are not the measured structural gain.") | both components are stated in contribution (2) L216-228 and the same verdict is restated at the results anchor L1845-1851 |
| 2 | the (P2) `Δ_group`/`Δ_cs`/`+0.922`/`+0.286`/`+0.768` detail from contribution (3) | the same numbers with their intervals are printed at L1843-1847; "the design factor is the only further component that survives" is stated at L1837-1838 |
| 3 | "the observation and usable-update factors" from the results band list | Obs and Use are separately reported in the ablation paragraph L2062-2071 |
| 4 | "and the two main-table method-family endpoints per dataset" from the Holm enumeration | the main table's families are the families of `round_v4/PREREG.md` §1.2 and are named at their point of use |
| 5 | "The balanced control is a sanity check, not a superiority test." | ~~the same source states "not a superiority test" twice, and the no-harm result is given in the same sentence~~ **CORRECTED 2026-10-03 (round 8, `F7`; see the correction block below). This justification does not reproduce.** `sanity check` and `not a superiority test` each return **0 hits** over `main.tex`, `appendix.tex` and `supplemental.tex`, so there was never a second occurrence to appeal to. The no-harm result survives in the post-pass text at L1646-1649, but the *reading* of that result did not, and a number is not its own interpretation. **The deletion was not duplication and the passage has been restored.** |
| 6 | "No test result tunes the selection process, parameters, groups, or strata." | ~~stated in the Introduction (no test result tunes the process) and in §VII-E ("the test seeds were not opened")~~ **CORRECTED 2026-10-03 (round 8, `F7`; see the correction block below). This justification does not reproduce.** `No test result tunes` returns **0 hits**; `tune/tuned/tuning` returns 3 hits, none of them this statement (`+0.170 tune` is a seed-half label, `tuning seeds` is the debt-weight disclosure); `were not opened` returns **0 hits**, and the nearest text is about the *validation* half rather than the test-seed rule. **The deletion was not duplication and the passage has been restored.** |
| 7 | "The main comparison and the ablation report both Design settings on both blocks, since Algorithm 2 takes `D_t` as a configuration." | §VI-B L1049-1052 and the support-gate paragraph L2014-2018 |
| 8 | "; we claim no best worst-group method" | Table III's caption already says "We do not claim a Holm-significant RMSE win", and the sentence keeps the `1.2630` vs `1.1690` comparison that makes the point. The adjacent "sealed same-backbone family … is in the supplemental material" sentence was compressed to one clause rather than deleted, because its two load-bearing statements (on U-Air those bars are Design-on; Local-Hájek coincides with FedAvg-Window wherever the active set matches) are not recoverable from a single other line. **CORRECTED 2026-10-03 (round 8, `F7`):** round 8 read the caption as adjacent but not equivalent, since it disclaims a Holm-significant RMSE win rather than a best worst-group method; the general claim is restored in the post-pass text as "; we claim no best worst-group method." |

**Deliberately not changed, with the reason.**

* The **abstract** (`R5-13`: `6.55 %` against `6.885 %`; `F3`/`R5-11`: `1.24 %` with no ruler). Outside this
  pass's scope and it needs the abstract's own pass; recorded in IV.3.
* **`Δ*`.** The two closable-gap values and their four qualifiers were already correct and are untouched.
* **No U-Air `ζ` number** was written, no `proj_beta`/`proj_beta_debt` arm was called frozen RAVEN, no
  prediction "better/worse" claim was written, and no new or changed number entered the paper except
  `ε_impl ≤ 2.42e-5` and the `6`–`16 %` ratio, both from `A1P_IMPL_RERUN.csv` and `A1P_IMPL.csv`, plus the
  `10 000` / `20261002` / family enumeration, which comes from the round protocol texts.
  **CORRECTED 2026-10-03 (round 8, `F1`):** the `6`–`16 %` ratio was taken from the task instruction
  rather than derived, and it does not reproduce. Dividing `ε_impl ≤ 2.42e-5` by each reading converted
  to endpoint units gives at most `0.11 %` of the four `Inst` readings and `2.16 / 7.62 / 2.73 / 4.89 %`
  of the four `debt` readings; on the two U-Air debt rows the bound exceeds the reading, so no ratio is
  defined there. The ratio is withdrawn in the post-pass text and replaced by those per-reading bounds,
  derived from `A1P_IMPL_RERUN.csv` (240 rows; `max eps_impl_group = 2.420009e-05`, `alpha_linf_trained = 0`
  on all 240, `b_g1_mismatch_windows = 0` on all 240) and `GATES_V51.csv` (`O-gate` row,
  `2.4198935053565407e-05` against a `5e-6` budget).
* **`appendix.tex` was not touched**, because the scope is `main.tex` only, so the U-Air `RMSE_μ` rows there
  that are canonical against the round-v4 θ tree rather than the round-v5.1 θ table remain as they were
  (IV.5).

### Record corrections — 2026-10-03 (round 8; `main.tex` re-attribution pass)

Round 8 found that **two of the justifications in the deletion table above do not reproduce** (`F7`) and
that **one of the numbers this section credits to the paper has no derivation** (`F1`). Both are corrected
in place above with `~~strikethrough~~` on the false claim; this block is the index. The rows that were
*not* duplication have been restored to `main.tex`, so the "eight duplication-only deletions" count is now
six, and the net length of the paper is unchanged by the restoration because the re-attribution pass
replaced superseded sentences rather than appending.

| # | correction | evidence |
|:--|:---|:---|
| 33 | **Deletion-table row 5's justification is false.** The record claimed "the same source states 'not a superiority test' twice". `sanity check` and `not a superiority test` each return **0 hits** across `main.tex`, `appendix.tex` and `supplemental.tex`; the row was a deletion of a reading, not of a duplicate. The sentence is restored. | exhaustive string search over the three `.tex` files; round-8 report §2.2 row 4 |
| 34 | **Deletion-table row 6's justification is false.** The record claimed the statement is in the Introduction and in a §VII-E sentence "the test seeds were not opened". `No test result tunes` returns **0 hits**; `were not opened` returns **0 hits**; the post-pass text at that location answers a *validation-half* rule, not the pre-registration tuning rule, and `tune/tuned/tuning` has no hit carrying this statement. The sentence is restored. | same search; round-8 report §2.2 row 5 |
| 35 | **The `6`–`16 %` ratio is withdrawn.** It was carried from the task instruction and never derived. The verified statement is the per-reading bound: `ε_impl ≤ 2.42e-5` is at most `0.11 %` of each of the four `Inst` readings and `2.16 / 7.62 / 2.73 / 4.89 %` of the four `debt` readings, with the two U-Air debt rows defining no ratio because the bound exceeds the reading. | `A1P_IMPL_RERUN.csv` (240 rows); `GATES_V51.csv` `O-gate`; round-8 report §2.3 |
| 36 | **Deletion-table row 8's surviving claim is narrower than the deletion.** The general statement "we claim no best worst-group method" is not equivalent to Table III's caption, which disclaims only a Holm-significant RMSE win. The general claim is restored beside the `1.2630` vs `1.1690` sentence. | round-8 report §2.2 row 7 |
| 37 | **Attribution of the structural gain rewritten, and this is the substantive change of the round.** The paper had credited the (P2) group-matching, variance and staleness terms and the debt recursion with producing structural target-mass alignment. The evidence attributes alignment instead to (i) the corrected reference, with the design factor `ζ` the only ingredient shown necessary and practically significant, and (ii) **imposing `C_r` and projecting onto it**. The remaining (P2) objective terms are retained as the definition of the criterion and for the unique minimizer; the debt recursion is retained as auditable accounting. Mechanism: `‖M_r α − μ‖₁` is exactly flat on `C_r` (median range `10⁻¹³` over `3 279` active windows) because a window's active clients reach only a few of the target's groups, so the constraint is load-bearing and the objective terms are not. | `round_v4/PART_A_REPORT.md` §1-2; `round_v3/EXECUTION_REPORT.md` §2-3; `round_v3/MYOPIC_DIAG.json`; `round_v3/ERRATA_v2.md` §1 |

### Record corrections — 2026-10-04 (round 9; the `P0` pass and the bundle refresh)

Round 9 found that the round-8 re-attribution left a program-wide contradiction on the page (`H1`), that
the mechanism clause written in round 8 is contradicted by the paper's own diagnostic file (`H2`), that
`ε_impl`'s unit was stated one way and applied two ways (`H3`), that "already sits inside that band"
understated a value that is 2.5× inside it (`H4`), that the compression pass truncated a sentence into a
fragment (`H6`), and that five scope qualifiers plus the `120 of 120` replay count and the `10^{-10}`
solver tolerance were dropped (`H8`, `H9`). All of those except `H5`, `H7` and `H8` are repaired in the
`P0` pass recorded in **Part V**. This block is the index of the record-level corrections; the rows above
are corrected in place.

| # | correction | evidence |
|:--|:---|:---|
| 38 | **The round-8 attribution rewrite was incomplete, and the record said it was complete.** Item 37 above describes the new attribution (projection + `ζ`) as the round's substantive change, which it was, but it did not record that the *program-wide* form of the withdrawn credit survived at the contributions list — so the paper asserted both sides of the same question (`H1`). The surviving site is now scoped to its named components. | round-9 report §7 `H1`; `main.tex` L230-233 against L1828-1832 |
| 39 | **The mechanism clause in item 37 above is too strong, and the falsifying measurement was in the repository.** The clause "no feasible `α` moves its group distribution toward `μ`" is contradicted by `MYOPIC_DIAG.json`: the tie-broken per-window rule reaches `1.05140` against uniform `1.06213`, a `0.0107` pp `Δ_group` gain (per-seed max `0.0337`). What the `10⁻¹³` flatness supports is that the group objective is flat **across the feasible set**, not that the endpoint cannot move. The paper now states the flatness and the tie-break together. | `round_v3/MYOPIC_DIAG.json` (`d_myo_tb`, `d_unif`, `max_abs_diff_tb_vs_unif`); `round_v3/EXECUTION_REPORT.md:134`; round-9 report §7 `H2` |
| 40 | **`ε_impl`'s unit was conflated and one of its two bounds was false.** It was defined as a distance "in percentage points of group mass" and then used as a numerator against pp *readings*; and "at most `0.11 %` of any of the four `Inst` readings" holds for U-Air only — the two SensorScope `Inst` readings (`+0.310 %`, `− 0.260 %`) give `≈ 0.94 %` and `≈ 0.78 %`. The identity `1 pp = 0.02` mass is now printed with the bound, and the `Inst` comparison is stated with its actual maximum. | round-9 report §7 `H3`; `main.tex` L601-602 (`pp = Δ/2 × 100`); `supplemental.tex` appendix K-A |
| 41 | **`Item 37's "8.23 to 21.73" feasibility range now has a located source — and the source shows the sentence mislabels it.** The two tokens occur exactly twice in the evidence, as the last column of the `B0` table in `round_v3/EXECUTION_REPORT.md`: **L62** `raven_wo_design … 8.23` and **L63** `raven_simoracle … 21.73`. So the range spans **across arms** — the low end is the design-off baseline and the high end is the oracle arm — while the subject of the paper sentence is the uncorrected reference, whose own value on that block is **16.81** (`raven`; `raven_wo_obs` 15.36, `raven_wo_use` 16.01, `count` 5.97, `uniform` 0). The per-seed companion artifact gives block means `raven` 16.68, `raven_simoracle` 22.11, `raven_wo_obs` 15.38, `raven_wo_use` 15.70, `raven_wo_design` 7.84, `count` 5.62, `uniform` 0, so no single-arm reading reproduces the printed pair. **This is a wording defect in the paper, not a missing source**: either name the arms or print the reference’s own value. Recorded as `A-8` in the round-10 audit. | `results_w1_ladder/round_v3/EXECUTION_REPORT.md` L59-66; `round_v3/SOURCE_LADDER.csv` (`outside_Cr_l1`, sensorscope/`B0`); `w1/PAPER_NUMBERS.csv` L37-38; round-9 report §9 (iii); round-10 report §3 `A-8` |
| 42 | **The `M7` bundle defect is closed.** The refresh recorded here as item 3 of I.6 was executed on 2026-10-04 under the drafted Option-A instruction: **217 files / 2 921 397 bytes** added — exactly **216 files under `w1/` (214 payload files plus `w1/PAPER_NUMBERS.csv` and `w1/EXCLUDED_HASHES.csv`) and the rebuilt `MANIFEST.csv`**; this record re-verified all **214 payload files as byte-identical to their working-tree sources**; `w1/PAPER_NUMBERS.csv` (83 rows), `w1/EXCLUDED_HASHES.csv` (610 rows / 29 380 661 bytes, hash-listed and not redistributed) and `w1/MANIFEST_ADDITIONS.csv`; `MANIFEST.csv` +264/−10 rows; `BUNDLE_SUMMARY.json` set to `bundle_revision = R1.1`; `README.md` gained its `## W1 evidence` section; the bundle's own `verify.py` returns `checked=2116 mismatches=0`. Four defects in the refresh remain open and are recorded in Part V, §V.3. | Part V, §V.3; `RAVEN_MCS_PUBLIC_REPRO_R1/w1/` |
| 43 | **The two "UNLOCATED" rows for the closable gap are false and are corrected here.** Rows 1-2 of `w1/PAPER_NUMBERS.csv` report `3.44` and `1.32` pp as unlocatable. Both are on **line 77** of `RAVEN_MCS_PUBLIC_REPRO_R1/w1/frontier/PHASE3_REPORT.md` (`(pi_unif - pi_star)/2 = 3.44 pp`, `可回收 1.32 pp`), whose sha256 is `1D1C39F75098BE6AA862F888B8260F4E44166ED441CE9CE4C2FD6F80971F8281`. The search failed because the file is UTF-8 while the searching process read it in the console's GBK code page. | bundled file at the quoted line and hash; Part V, §V.3 |
| 44 | **Item 35's replacement bound is right for the `debt` readings and wrong for the `Inst` readings, and the three ratios in row 35 rest on conversions this record never stored.** The `debt` bounds reproduce (`2.16 / 7.62 / 2.73 / 4.89 %` from `2.42e-5` over readings of `+0.0141 / +0.0040 / +0.00426 / +0.00239 %`), and the `Inst` half is the `H3` defect corrected in item 40 above; separately, the `Δ`-unit readings the ratios divide by (`1.84e-2`, `1.54e-2`, `1.46e-4`) come from `pp = Δ/2 × 100`, which no bundle file states, so those rows cannot be opened at a named source. | Part V, §V.3 defect 2; round-9 report §7 `H3` |

# Part V — The 2026-10-04 state: round-9 review, the `P0` repair pass, and the bundle refresh

This part records the two work items completed on 2026-10-04 and the review that produced them. It is a
*record-level* index: every claim below is anchored to a file, a line or a hash, and the two scorecards are
the reviewer's, not this record's. Where this part disagrees with Parts I-III, this part is current and
Parts I-III are the historical state.

## V.1 Round 9 — version comparison against round 8, and what it scored

Round 9 asked the version-comparison question only (round 8 → current), under the unchanged frozen contract
`TMC-J-R4` (8 dimensions, weights `0.10 / 0.20 / 0.25 / 0.15 / 0.10 / 0.10 / 0.05 / 0.05`, anchors 1-5,
threshold 4/10, `|Δ| < 0.05` = `unchanged`).

| field | round 8 | round 9 |
|:--|:--|:--|
| weighted readiness sum | 3.25 | **3.25** |
| overall stance | 5/10 (threshold 4/10) | **5/10 held** |
| relative progress delta | +0.35 (`improved`; Soundness 4→5, Clarity 3→4) | **0.00 (`unchanged`)** |
| traceable increases / decreases | 1 / 0 | **0 / 0** |
| confidence | 4/5 | 4/5 |
| closure counts | 15 closed / 3 partial / 8 open | **20 closed / 5 partial / 1 moot / 4 open** — the round-9 report’s §6 table in fact carries **21** rows whose status cell says `closed` (`R5-1`, `R5-2`, `R5-3`, `R5-4`, `R5-6`, `R5-7`, `R5-8`, `R5-9`, `R5-10`, `R5-11`, `R5-12`, `R5-14`, `F1`, `F2`, `F3`, `F4`, `F5`, `F6`, `F7`, `F8`, `F9`) while its own summary line says "20 closed" and lists the same 21 IDs, so the count is 21, or 20 if `F4` — already closed at round 8 — is excluded from the new tally; the round-10 audit records the discrepancy as `A-6` |

**What closed in round 9:** `F1` (the false `6`-`16 %` ratio, replaced by per-reading bounds), `F2` (the
two reference frames separated), `F7` (three deletions restored to the file), `F8` (`ε_impl` given a
definition and a unit) and `F9` (the predicate-less sentence closed). **What did not move:** five closures of
`previously_undetected` sentence defects are excluded from the relative delta by the frozen provenance rule,
and the re-attribution is a re-scoping of `R5-1`/`R5-5`, both already counted at round 8.

**The one disclosed judgement call.** If the `F1`/`F2`/`F7`/`F9` repairs were counted as satisfying round 8's
published Clarity raise condition, Clarity would be 5 and the weighted sum **3.40** (Δ +0.15, `improved`).
The reviewer declined to take it, because those five were the *previous* pass's own defects rather than the
carriers round 8 named for Clarity, and of those five carriers exactly one (`R5-5`'s mechanism half) moved —
into a clause the paper's own `MYOPIC_DIAG.json` contradicts. The decision and its arithmetic are in the
round-9 report §8.

**The ten new findings `H1`…`H10`.** `H1` (the program-wide attribution at L230 contradicting L1828), `H2` (the
mechanism clause contradicted by `d_myo_tb`), `H3` (`ε_impl`'s unit and its false `Inst` bound), `H4` ("already
sits inside that band" plus mixed coordinates), `H5` (the privacy sentence filed under the coverage-Gate
paragraph), `H6` (the truncated sentence at L265-268), `H7` (the `240`-run claim against a `120`-run gate),
`H8` (five deleted scope qualifiers), `H9` (the dropped `120 of 120`, the `10^{-10}` tolerance, the
"structural endpoint" qualifier, "three to four orders of magnitude"), `H10` (two shipped-comment / label
residues, no PDF effect). None was charged as a relative-progress decrease; all are charged in the readiness
discussion.

**What is still open from round 9's own list:** `R5-16` ("recoverable" naming two headroom objects), `R5-15`
(band placement with no preregistration pointer), `C1` (Proposition 4's unused directional-derivative clause),
`C2` (the coverage-Gate apparatus), `F10` (build warnings), `H5`, `H7`, `H8`, and `R5-5`'s ℓ₂ half.

## V.2 The `P0` pass — the five fixes, exactly what changed

Authorised as "直接做P0，先别动其他东西". Scope: `main.tex` plus one `supplemental.tex` sentence. Structure was
not to move, and did not: `\begin{table` 4, `\begin{figure` 4, `\begin{equation` 37, `\cite{` 42,
`\section{` 8, `\subsection{` 29, `\begin{proposition` 4, `\begin{theorem` 2, `\label{` 97 — all identical
before and after.

Line-level measurement of the whole pass (block-level `difflib` on the two files, newline-split):
**4 change blocks, +19 / −12 lines, +7 net**, words **12 302 → 12 377**, bytes **112 870 → 113 379**,
`main.pdf` **17 pp before and after**, `supplemental.pdf` 16 pp. `appendix.tex` untouched. The net is measured by the same newline-splitting convention the rest of this record uses: **2 239 → 2 246 lines**, and the block-level count is **4 blocks, +19 / −12**. Two figures printed in this section earlier were wrong and are withdrawn: the `+5` net and the pair `20 inserted / 23 deleted`, both artefacts of counting a `Compare-Object` line-set rather than diff blocks. A pre-edit snapshot
is kept at `snapshots/2026-10-04-pre-p0-fix/`.

| finding | what the paper said | what it says now | note |
|:--|:--|:--|:--|
| `H1` program-wide attribution | "the **calibration terms** and debt are not shown to contribute to alignment" | "the **objective terms beyond the reference anchor**, and the debt recursion, are not shown to contribute to alignment.  Imposing the feasible set and projecting onto it is what does." | names the objects, so the contributions list no longer denies what §VII-C affirms |
| `H2` unmeasured mechanism | "the active clients reach only a few of the target's `220` or `144` groups, so **no feasible `α` moves its group distribution toward `μ`**: the mismatch is a support limitation, not an allocation error" | "so the group objective is **flat across the feasible set** and on its own cannot move the window's group distribution toward `μ`.  The endpoint moves only through the tie-break among those equivalent points … gains `0.0107` pp of group mass over uniform weights (`1.05140` against `1.06213`, per-seed maximum `0.0337`)" | the sentence now states the flatness **and** the tie-break that moves the endpoint; the measurement was previously uncited (`1.05140` grepped to 0) |
| `H3` `ε_impl` unit and `Inst` bound | "at most `0.11 %` of any of the four `Inst` readings" | the bound is now printed **in one unit with its conversion shown**: `2.42\times10^{-5}` in the `\Delta` units of the structural endpoints, "equivalently `1.21\times10^{-3}` in the percentage-point convention" (i.e. `\times50`, the paper's `pp = \Delta/2 \times 100`), and the `Inst` comparison is stated with its actual maximum (`≤ 0.94 %`) | `supplemental.tex` Appendix K-A; the debt-reading ratios (`2.16 / 7.62 / 2.73 / 4.89 %`) are unchanged and reproduce |
| `H4` band antecedent and "already" | "its group effect of `+0.039` (`[+0.013,+0.063]`) **already sits inside** that band" | "Its effect on the group endpoint, `+0.039` (`[+0.013,+0.063]`) in the closable-gap units of Section III-F, is **well inside** the `±0.10` band" | the value is `2.5×` inside the band, so "already" read as "barely"; the coordinate is now named instead of shared with the `Δ_c-s` clause |
| `H6` truncated sentence | "Independent hybrid ceilings, namely … of the supplemental material." (no verb) | "… of the supplemental material, **are not mixed into that development table**." | four words restored; the clause survived in six other places, so the repair is free |

**`H5`, `H7` and `H8` were not part of the `P0` scope and remain open.** `H5` (placement of the privacy
sentence) and `H8` (the five deleted scope qualifiers) are wording/placement items; `H7` is a
disclosure-completeness residual that the deletion moved in the *safer* direction.

**Everything the pass did not touch, verified rather than assumed:** `appendix.tex` unchanged
(`29ADD10FB7F8424714FD19632054B28AF33F184580DE69F0094864121332B627`, mtime 2026-10-02); no number changed
except `0.11 %` → the per-reading `Inst` statement; the forbidden-claim list honoured (no cross-dataset
averaging, no `RMSE_μ`/`WorstGroupRMSE` superiority claim, no U-Air `ζ`, `Δ*` only with its four
qualifiers, `proj_beta`/`proj_beta_debt` never called RAVEN, the `±0.10` band never a hypothesis test).

## V.3 The `M7` bundle refresh — executed, with four defects left open

Executed 2026-10-04 under the drafted Option-A instruction
(`ccfa-review-reports/raven-mcs-m7-bundle-refresh-protocol.md`): byte-identical copies, no compute, no
manuscript edit, no git action. Payload **217 files / 2 921 397 bytes** (budget 20 MB, gate `G-M7-4` passed)
under `w1/`, plus the three index files.

| item | value |
|:--|:--|
| trees added | `w1/frontier` 21 files, `w1/ladder_v3` 13, `w1/tradeoff_v4` 12 + 122 `final_metrics.json`, `w1/audit_v5/{round_v5,round_v5_1,round_v5_1a}`, `w1/gatekeeping` 16, `w1/exogenous` 3 |
| the two content-addressed indexes | `w1/PAPER_NUMBERS.csv` (83 rows), `w1/MANIFEST_ADDITIONS.csv` |
| hash-listed, not redistributed | `w1/EXCLUDED_HASHES.csv`: **610 rows / 29 380 661 bytes** (`checkpoints/final.pt`, `window_metrics.json`, `pair_state.parquet`, and single files > 2 MB), with the reason stated in `README.md` |
| indexes rebuilt | `MANIFEST.csv` **+264 / −10 rows** (now 2 116 rows), `BUNDLE_SUMMARY.json` with `bundle_revision = "R1.1"` and a `w1_evidence` block, `README.md` + a `## W1 evidence` section |
| the bundle's own verifier | `verify.py` → **`checked=2116 mismatches=0`** (re-run by this record, not accepted from the executor) |
| a defect found in the bundle *before* this pass | `MANIFEST.csv` was already stale before `M7` (5 rows not reproducible from `HEAD`); the refresh reconciled 6 rows to disk content without touching file bytes, and that pre-existing staleness is recorded here rather than charged to the refresh |

**Four defects in the refresh itself, recorded as open.**

1. **Two false `UNLOCATED` rows (`w1/PAPER_NUMBERS.csv`, rows 1-2).** `3.44` and `1.32` pp are both on
   **line 77** of `w1/frontier/PHASE3_REPORT.md`
   (sha256 `1D1C39F75098BE6AA862F888B8260F4E44166ED441CE9CE4C2FD6F80971F8281`), quoted here because this
   record has already mis-cited that line once:
   `` `(Δ_unif − Δ*)/2 = 3.44 pp` `` and `` `可回收 **1.32 pp**` ``. The search failed because the file is UTF-8 while
   the searching process used the console code page (GBK) — so this is a **search-convention** defect, and
   the protocol's own "never re-encode" rule is what made it possible. **The row text is now false in a second
   way:** it asserts that `round_v2/PHASE3_REPORT.md` "is NOT in the protocol's artifact list and was not
   copied", while the same file **is** in the bundle byte-identically at `w1/frontier/PHASE3_REPORT.md` (both
   `13 599` bytes, sha256 `1D1C39F7…`). So the two rows need the source filled in and both sentences rewritten,
   not only a status change. Fix: set `source_file` to the bundle path, `status = located`, and name the
   working-tree copy as the original location.
2. **Six `UNLOCATED` rows are conversion-derived rather than unstored, and the conversion is not a missing ingredient.** The `Δ`-unit readings `1.84e-2`,
   `1.54e-2`, `1.46e-4` and the three ratios derived from them (`17 %`, `0.13 %`, `0.16 %`) come from
   `pp = Δ/2 × 100`, which **is** printed (`main.tex` L604), so the factor `×50` is the paper's own definition
   and those rows are reconstructible from the paper plus the stored readings. What they have in common is
   that no **bundle** file states the converted value, which is a labelling gap in **this record's**
   instruction rather than in the executor's work. Fix: deposit a `w1/CONVERSIONS.csv` and mark those rows
   `derived` with the conversion named, instead of `UNLOCATED`.
3. **Twenty of the seventy `located` rows do not print a value that literally occurs in the named file, and only twelve carry a derivation note.** Measured over
   all 83 rows: **50** `located` rows contain their `printed_value` verbatim in the named file, **20** do not,
   and `source_row_or_key` documents a transformation for only **12** of the 70. Each of the 20 is
   reconstructible (`×50` for the `pp` rows, a 20-seed mean for the `WorstGroupRMSE` rows, a count of
   unchanged verdicts for `20/20`, an order of magnitude for `10^{-13}`, a rounded `0.0337` for a stored
   `0.03369405…`), so `located` is defensible in substance — but it does double duty for *found at this row*
   and *computed from this row*, and a reviewer who opens the row will not find the printed digits. Fix: split
   the status into `located` and `derived_from`, and state the transformation in the row.
4. **Four rows are stored but not printed, and one row set traces outside the `w1/` trees.** `0.120`, `0.153`
   (City Scanner A1 power), `0.0325` and `− 0.1224` (dose-response slopes) are in the bundle and in neither
   the paper nor the supplement — which is what the row reports, `0 hits in main.tex or supplemental.tex`, so
   the claim is exact and correct as printed. It does **not** extend to `appendix.tex`: `0.0325` occurs once
   there (`appendix.tex` L1928, a `\pm` in the `RAVEN-SimOracle` row of the U-Air table) and is an unrelated
   standard deviation, so the row set has no `paper_file:paper_line`; the ablation percentages of `main.tex` L2055-2077
   trace to the already-bundled `tables/` files rather than to `w1/`. Fix: a `NOT_PRINTED` label and a
   `tables/` pointer.

**One manuscript-side pointer remains unauthorised and unapplied.** `main.tex` L2211-2221's availability
sentence still points at the bundle generally; naming `w1/` in one clause would make the new subtree
citable, but it is a manuscript edit and needs its own authorisation.

**One index artefact that does not reconcile, recorded and not repaired.** `BUNDLE_SUMMARY.json` reports
`file_count = 2117` and `total_bytes = 179 916 789`; this record measures **2 118 files / 180 207 845 bytes**
under the bundle root (recursive, `-Force`), a **+1 file / +291 056-byte** difference — and `291 056` is
**exactly the size of `RAVEN_MCS_PUBLIC_REPRO_R1/MANIFEST.csv`**. Read against the manifest itself
(2 116 rows, and no row for `MANIFEST.csv`), the arithmetic closes: the manifest-registered set plus
`MANIFEST.csv` plus `BUNDLE_SUMMARY.json` is 2 118, which is exactly what this record measures on disk,
whereas the declared `2 117` is the manifest-registered set plus the manifest alone — so **the declared
total excludes `BUNDLE_SUMMARY.json` itself**, and `verify.py` and `PROTOCOL.json` are likewise not
manifest-registered.
That is a counting convention of the bundle builder rather than lost content, and the same self-exclusion is
what makes `verify.py` print `checked=2116`. Filed as an unexplained index-vs-disk difference rather than a
defect of the copied payload; `mismatches=0` is unaffected, because it is a hash check and not a total.

## V.4 What round 9 and the `P0` pass settle, and what still blocks

**Settled.** `M7` (bundle refresh) is closed, so **Reproducibility 2 → 3** and the weighted readiness sum is
**3.35** — the first movement on that dimension in the paper's history, and it is mechanical rather than
scientific. Five of round 9's ten new findings are repaired on the page and two record defects behind them
(the false `UNLOCATED` rows, the too-strong mechanism clause in item 39) are now indexed.

**Still blocking, by weight (§8 of the round-9 report, unchanged by the `P0` pass).**

1. **Evidence (0.25).** No prediction endpoint survives Holm on any block (`p_Holm = 1.000` on SensorScope;
   U-Air best raw `0.027`, `p_Holm = 0.133`), and the paper's own decomposition still shows uniform weights
   close `68.96 %` of the SensorScope group gap. The `P0` pass does not touch this axis, and the mechanism
   experiment that would have addressed it came back `inconclusive` (Part IV, `C1`/`H_mech`).
2. **Clarity (0.15, at 4).** The `P0` pass discharged `H1`, `H2`, `H3`, `H4` and `H6`; the raise condition
   additionally names `R5-5`'s measurement citation (now half-supplied by the tie-break sentence),
   `R5-15` (band placement, still with no preregistration pointer anywhere in `main.tex`) and `R5-16`
   ("recoverable" naming two headroom objects).
3. **Reproducibility (0.10).** The three refresh defects of §V.3, plus `F10`: five multiply-defined citation
   labels (from `xr`/`supplemental.aux`) and the supplemental `Overfull \vbox (3.42152pt)` / float-only page 10.
   The gate line "0 errors / 0 undefined / 0 overfull" is true for `main.log` and does not cover
   `LaTeX Warning` lines.
4. **Terminology (0.05).** `R5-16`; `H3`'s unit statement is now consistent, so this axis owes only the
   disambiguation.

**`C1` and `C2` remain the only free space in a 17-pp paper**: Proposition 4's unused directional-derivative
clause, and ~40 lines of coverage-Gate apparatus for an instrument that never acts.

## V.5 What is NOT yet written into this record, and why

A list of the still-stale parts, kept here so the next pass does not have to rediscover it. Each entry says
whether it is stale because the record is *historical* (left deliberately) or because a **completed** change
has not been indexed yet (a gap).

| # | part / section | state | why |
|:--|:--|:--|:--|
| 1 | **I.1** "verdict in one paragraph" | historical + annotated | it is the 2026-09-27 verdict ("4/10"); the 2026-10-04 status line now points to Part V, but the paragraph's own text is deliberately untouched |
| 2 | **I.3 T-e** and **I.6 route 2** ("state the attribution gap… closes review M8") | **stale, not annotated** | the attribution gap was stated in round 8 and then re-attributed again in round 8 and the `P0` pass, so the route is done and still reads as open. Together with `§6` (entry 7 below) this is the largest single gap in Part I |
| 3 | **I.6 ranked routes** | partly stale | routes 2 and 3 are executed; route 6 (bibliography verification, "24 of 54 entries") is untouched and unindexed |
| 4 | **I.7 action list** | partly stale | item 3 annotated as done; items 1 and 2 are done (the endpoint-keyed Design rule was added, the attribution was stated); item 6 (bibliography) still open |
| 5 | **I.6 / I.7 issue vocabulary** | historical | the rounds 4-9 issue IDs (`R5-*`, `F*`, `C1`, `C2`, `W*`, `M7`, `H1`-`H10`) never appear in Part I; Parts I-II are indexed only under the `D-*`, `T-*`, `P-*`, `X-*`, `N*` vocabulary. Re-indexing them would be a rewrite, not an annotation |
| 6 | **§0 decision register** (`D-1`…`D-6`), **I.4 P-a** ("deployment target is evaluation-derived — no"), **I.6 route 4 / I.7 item 5** ("obtain an exogenous target map — external, open") | **superseded, unindexed** | the exogenous round was executed on 2026-10-02 and is not mentioned anywhere in this record: `results_exogenous_target/round_v1/` built three maps (exogenous M1, exogenous M2, and an evaluation-derived control) for City Scanner and returned **`gate = off` on all three**, with the exogenous maps supporting almost no activity (`ρ ≤ 0.98`-`1.00 %`) against the evaluation-derived map's `ρ = 14.35 %`; the block runs as Design on (`CS_ACCEPTED.json: design_on = true`). So the object now exists, and what it shows is that the exogenous target the record asked for is **weaker on this block, not stronger** — which is a finding, not a closure, and it needs its own row in I.4/I.6. **The bundled copy of this round in `w1/exogenous/` is 3 files, not the full tree** |
| 7 | **§3 / §3A / §4** (ceiling map, headroom, scenario family) | historical, numbers still valid | no round since 2026-09-29 changed a number in the ceiling map; **but `§6`'s component-removal verdict is the old attribution and is superseded** by Part IV §IV.1 and item 37 — as written it credits the (P2) objective terms with the structural gain, which rounds 8-9 withdrew |
| 8 | **§7 changelog / open-defect table (§7 items 1-52)** | **stale, not annotated** | it stops at 2026-10-02; its "open manuscript defects NOT changed" table predates rounds 7-9 and now understates what is closed and overstates what is not. The live list is the round-9 closure table: `R5-16`, `C1`, `C2`, `F10` open; `R5-5`, `R5-15`, `R5-17` partial; `H5`, `H7`, `H8` new and open |
| 9 | **§8 next actions**, **§10 reproduce**, **§11 what this record does not do** | **stale** | `§8` is the 2026-09-29 action list (its items on the endpoint-keyed rule and the attribution gap are done); `§10` never mentions `w1/` or the bundle's `verify.py`, which is now the single command that reproduces the released evidence; `§11`'s boundary list predates the whole W1 ladder, the gatekeeping round and the public bundle |
| 10 | **Part III (the external review `X-1`…`X-21`)** | **partly closed, unindexed** | `X-1`, `X-2`, `X-3`-`X-7` and `X-21` are closed in III.9 and §7, but `X-10` (matched-budget comparison against simple target calibration), `X-12`/`X-13` (target acquisition and the unmeasured `U`), `X-14` (the FedIPW/FedPALS mapping, still the `W4` novelty boundary) and `X-15` are neither closed nor re-ranked, and rounds 7-9 have since moved the ranking |
| 11 | **§9 incident log**, **§5 E1-E6**, **§2 selection-layer provenance**, **§2A** | historical, still valid | no later round touched them; `§2`'s "the compounding direction is part of the construction" remains the standing scope caveat, re-verified in the paper by round 9's `R5-12` |
| 12 | **The "8.23 to 21.73" verification status, wherever it is cited** | **closed 2026-10-04, with a finding** | the tokens are located (`round_v3/EXECUTION_REPORT.md` L62-63) and the sentence mislabels them — correction item 41 and round-10 `A-8`. Any record that still calls this range "unverified" (round 9 §9(iii), and the independent 2026-10-04 review's "Unresolved" list) is now dated |
| 13 | **§3A H4's support-cost level, and the header line that quotes `+6.31…+7.39 %`** | **stale level, corrected 2026-10-06** | the range is pre-θ and its denominator is the superseded U-Air `fedavg_window` arm (correction item 45, Part VI). The effect itself is unchanged — re-measured on the arm that reproduces the frozen artifact, the same gap is `+6.45 / +6.51 / +5.88 / +6.46 / +6.49 / +5.89 %` (C0…C5) with every CI lower bound above `+4.49 %`. H4's "driven by the dropped support alone" is *strengthened*, not weakened: Part VI.4 shows the two active sets are identical across a FedAvg arm and an oracle arm on 20/20 seeds, and nested (A ⊂ B) on the FedAvg side under an identical trace and config hash |

**The one-line summary of §V.5.** The record's *evidence and correctness* content (Parts II-III) is historical
and honest as history; what it lacks is an index of the four rounds that followed (7, 8, 9 and the `P0` pass),
and entries 2, 3, 4, 6, 7, 8 and 9 are the places where a reader would today be **misled** rather than merely
dated — chiefly the attribution-gap route, `§6`'s component verdict, `§7`'s open-defect table, and the
exogenous-target route that is listed as "external, open" and has in fact been run.

# Part VI — The 2026-10-06 completion of the H line: the FedAvg rule, the H table, and the active-set regime

This part records one execution — round 3 of the H-headroom line — and the four record corrections it
forces. Every claim is anchored to a file, a line or a hash. Where it disagrees with §3A or with the
header block, this part is current and those are the historical state. **No manuscript file changed.**

Round 3 did not set out to test a hypothesis about the paper. It set out to remove one obstacle: the
FedAvg arm that every H and U1 cell had been measured against was not reproducible, and both rounds had
waived that gate rather than fail it. What follows is (i) the rule that closes the gate, (ii) the H
table re-measured on an arm that passes it, (iii) the structural result that came out of the rebuild,
and (iv) the record corrections — including a level correction to §3A H4.

## VI.1 The defect this closes

`GATE_uair.json` (H round) and `GATE_uair.json` (U1 round) both compare a rerun against the frozen
2026-08-11 artifact and record, for `fedavg_window` only:

| seed | frozen | rerun | abs diff | relative | recorded |
|:--|---:|---:|---:|---:|:---|
| 30001 | 1.210848485707097 | 1.1712625825964957 | `3.958590311060117e-02` | −3.27 % | `known_nonrepro: true`, `"pass": "True"` |
| 30006 | 1.2856115928072611 | 1.1502492213912836 | `1.353623714159775e-01` | −10.53 % | `known_nonrepro: true`, `"pass": "True"` |

The oracle arm in the same gate matched at `0.00e+00`. The audit already in this record (header line:
"the main comparison's U-Air `FedAvg-Window` cell traced to a 2026-08-11 runner that dropped the
zero-target-mass pairs", §2A N1) had the mechanism right; what was missing was an enforcement point.
Round 2 tried to fix it by rewriting the trace's `U` and stopped 0.145–0.170 % short; the trace was the
wrong object.

## VI.2 The rule, and its gate

**Rule.** A client-window whose `(client_id, opportunity_stratum)` carries `pi_tar = 0` gets
`m_total = 0` and therefore leaves the aggregation set `e_r`. The event trace is left byte-identical to
the frozen one. Implemented for the FedAvg arm only, at run time, without editing `src/`
(`.r3_work/r3_masszero.py`, sha256 `36F560138FDC5321…`; driver `.r3_work/r3_p1p2.py`, `00BFEDAE33C7BA27…`).

**Gate** (the same three items as the earlier stage, 20 seeds, no waiver):

| check | result |
|:---|:---|
| `\|ΔRMSE_mu\| ≤ 1e-9` vs the stored artifact | pass, **20/20**, max diff `0.000e+00` |
| `\|ΔDelta_group\| ≤ 1e-9` | pass, **20/20**, max diff `0.000e+00` |
| active-client set identical on every window | pass, **20/20** |
| not required by the gate, reported anyway: `Tail_RMSE`, `RMSE_rho` | `0.000e+00` on 20/20 |
| trace pairing, FedAvg vs the stored oracle run (`EventTrace_hash`) | **240/240** |
| oracle-arm re-measurement on the frozen trace: `raven_simoracle` (positive control) | `1.196856` / `1.283674` = frozen, `0.0` |
| oracle-arm re-measurement: `raven_simoracle_nodesign` | `1.154653` / `1.142415` = stored, `0.0` |

`tables/C0_REPRO.csv`, `tables/C0_REPRO_extra_metrics.csv`, `tables/ORACLE_ARM_VERIFY.csv`,
`.r3_work/r3_pairing_check.py`. So the rule is not an approximation of the stored behaviour: on the C0
condition it *is* the stored behaviour.

## VI.3 The H table on the corrected arm, and the decision

`H = (RMSE_mu(fedavg_window) − RMSE_mu(oracle)) / RMSE_mu(fedavg_window)`, U-Air, n = 20 seeds
(30001–30020), Student-t intervals, df = 19. Pre-registered in `PREREG_P2.md` before any cell of this
round was computed, with `go_bar = 0.005` carried over unchanged from the 2026-09-24 round and the
round-v1 rule form `cell go ⇔ H_ci_lo > go_bar`.

| condition | FedAvg `RMSE_mu` | design-on oracle | H [95 % CI] | go | design-off oracle | H [95 % CI] | go |
|:--|---:|---:|:--|:--|---:|:--|:--|
| C0 frozen | 1.188238 | 1.191447 | −0.27 % [−0.80, +0.26] | no | 1.114401 | **+6.17 %** [+4.71, +7.64] | **yes** |
| C1 strong tilt | 1.175616 | 1.180165 | −0.39 % [−0.85, +0.08] | no | 1.103798 | **+6.12 %** [+5.03, +7.22] | **yes** |
| C2 extreme tilt | 1.179738 | 1.184399 | −0.41 % [−0.95, +0.14] | no | 1.114360 | **+5.48 %** [+4.06, +6.89] | **yes** |
| C3 low capacity | 1.188034 | 1.191298 | −0.28 % [−0.80, +0.24] | no | 1.114124 | **+6.18 %** [+4.72, +7.64] | **yes** |
| C4 block-uniform | 1.188238 | 1.194778 | −0.55 % [−1.08, −0.03] | no | 1.117278 | **+5.93 %** [+4.46, +7.40] | **yes** |
| C5 combined | 1.179322 | 1.187190 | −0.68 % [−1.23, −0.13] | no | 1.117102 | **+5.21 %** [+3.79, +6.63] | **yes** |

**Caveat added 2026-10-06 (correction item 49, repaired the same day — see item 50):** the FedAvg column
of the **C4** and **C5** rows was not the block-uniform condition — those A-side runs were executed as
`test_share` and the `C4` cell was numerically the `C0` cell. **Item 50 repairs this**: the corrected
FedAvg means are `1.191394` (C4) and `1.182424` (C5), the corrected `H_best` values `0.061820` (C4) and
`0.054595` (C5), both still `go`. The table above shows the pre-repair values; C0–C3 are unaffected
either way.

`H_DECISION.json`: `go_cells` = the six design-off cells, `decision = "go"`. On the design-on arm the
interval contains zero on C0–C3 and excludes it on the *negative* side on C4/C5 (FedAvg better by
0.55 % and 0.68 %), i.e. `equivalent_zero`, not `benefit`.

## VI.4 The regime finding — what the `go` is, and what it is not

1. **The six `go` cells are §3A H4's object, re-measured.** H4 already names the U-Air support cost
   (`+6.31…+7.39 %` pre-θ, `+6.968/+6.989/−/+6.980/+6.991/−` after θ re-sourcing) and already concludes
   it is "driven by the dropped support alone". Reproduced here from the same stored runs on the old
   denominator, the six values are `+6.98 / +6.99 / +6.32 / +6.99 / +7.00 / +6.31 %` — H4 verified, not
   superseded.
2. **Its nearest manuscript counterpart is `tab:e4_ablation`'s U-Air Design row** (`Δ_group −6.943*`,
   `Δ_c-s +4.990*`, `RMSE_mu −6.885*`, tail `−7.221*`, Holm-adjusted) and the `ρ_r` gate of
   `eq:design_gate`, which already sets Design off for U-Air (`ρ = 35.4 %`). Measured here on a
   different arm (oracle propensity instead of estimated): `RMSE_mu −6.44 %`, `Δ_group −7.51 %` versus
   the frozen `raven` arm. Same sign, comparable magnitude, no contradiction. **The `go` therefore
   recovers a manuscript-reported, Holm-significant trade-off; it is not untapped headroom and licenses
   no new claim.**
3. **The mechanism is a regime, shared across methods — the new evidence.** Comparing the
   window→`active_clients` maps (with `a_r_size`), not their sizes, over all 20 seeds
   (`tables/ACTIVE_SET_REGIME.csv`):

   | pairing | result | regime |
   |:---|:---|:---|
   | frozen-rule FedAvg vs design-on oracle | **identical, 20/20** | A: 66/80 windows, 2.32 clients |
   | old-rule FedAvg vs design-off oracle | **identical, 20/20** | B: 74/80 windows, 2.81 clients |
   | frozen-rule FedAvg vs design-off oracle | different windows, 20/20 | — |

   The four arms form a complete 2 × 2 (regime × weighting family): the regime factor moves `RMSE_mu`
   by ≈6 %, the weighting/information factor by ≤0.3 % (within regime A, H = −0.27 % [−0.80, +0.26];
   within regime B, H = −0.22 % [−0.72, +0.28]). This is a *stronger* form of H4's conclusion: the
   support loss is not merely "the dominant term", it is the same set of client-windows for a FedAvg
   arm and an oracle arm, so no weighting rule separates them.
4. **The two regimes are a single-variable contrast, and A is nested inside B.** On the FedAvg side
   both regimes were run with the **same `EventTrace_hash` and the same `config_hash` on 20/20
   seeds**, so the injected `m_total` rule is the only difference. There, A's active-client set is a
   **subset** of B's in every shared window (20/20 seeds), A never holds a window B lacks, and the
   medians are **145 vs 192** client-windows — A keeps **74.6 %** of B's, i.e. drops ≈25 %, which is
   the `72 of 288` pairs (25.0 %) H4 records, seen as client-windows
   (`tables/REGIME_AB_FEDAVG.csv`). So regime B is not "more data" or a different environment: it is
   the same delivered client-windows, with the zero-target-mass ones no longer excluded from `e_r`.
5. **Still open.** Whether regime B's ≈6 % is legitimate estimation or a side-effect of relaxing the
   delivery/design bookkeeping is not settled, and round 3 measured `RMSE_mu` and `Δ_group` only. The
   paper's own price side is `Δ_c-s +4.990 %`. What *is* settled is that the two regimes differ in the
   aggregation rule alone — same trace, same config — so the remaining question is a modelling choice
   (whether pairs with `π^tar = 0` belong in the prediction endpoint), which is exactly the Design
   trade-off `tab:e4_ablation` prices.

## VI.5 Record corrections — 2026-10-06 (items 45–48)

These continue this record's *correction* series (items 33–44 in the two blocks above); they are **not**
§7's changelog items 45–48, which are the 2026-09-29 manuscript writes.

| # | correction | evidence |
|:--|:---|:---|
| 45 | **The U-Air `fedavg_window` arm behind every H/U1 level was off the manuscript's own FedAvg by up to 10.5 %, and the level of §3A H4 moves with it.** The arm is closed by the `m_total` rule (VI.2, 20/20 exact). H4's *effect* is a difference of two `H`s that share that denominator, so it is nearly arm-invariant but not exactly so: on the arm that reproduces the frozen artifact the same gap is `+6.45 / +6.51 / +5.88 / +6.46 / +6.49 / +5.89 %` (C0…C5) with CI lower bounds `+5.13 / +5.48 / +4.49 / +5.14 / +5.16 / +4.49 %`, against `+6.98 / +6.99 / +6.32 / +6.99 / +7.00 / +6.31 %` on the superseded arm. Sign, ordering (C2 ≈ C5 < C0 ≈ C1 ≈ C3 ≈ C4), and the "every CI lower bound clears the bar" conclusion are unchanged; the level falls by `0.42`–`0.53` pp, which is the denominator ratio `1.188238 / 1.111932 ≈ 1.069` acting on the same numerator. | `results_h_headroom/round_v3/tables/SUPPORT_COST_CORRECTED.csv` (sha256 `8d0c16de…`); `tables/H_SUMMARY_oldfedavg*.csv`; `round_v1/GATE_uair.json`; `round_u1/GATE_uair.json` |
| 46 | **§3A's `H_nodesign` column is a regime-B quantity and is reproduced exactly here — but it must not be read as the oracle's information value.** Independent recomputation from the same stored runs returns C0 `−0.2166 %` [−0.7154, +0.2822], the value printed in §3A; the five other conditions also reproduce. Against the corrected FedAvg the *same* arm reads `+6.17 %` [+4.71, +7.64]. The two differ only in the denominator, and the gap between them (`6.39` pp) is exactly the old arm's own offset — so the §3A column measures a regime, and the corrected table measures that regime against the manuscript's FedAvg. | `results_h_headroom/round_v3/tables/H_SUMMARY.csv`; §3A line 979 |
| 47 | **The arm the support cost rests on had never been equality-gated.** The H round's gate asserted equality only for `fedavg_window` (waived) and `raven_simoracle` (matched); for `raven_simoracle_nodesign` it recorded a finite *smoke* value (`oracle_nodesign_smoke_RMSE_mu = 1.1546527250489613`) and required nothing of it. That arm is now equality-verified against the stored runs on the frozen trace at two seeds, `abs_diff = 0.0`. No number in §3A changes; the provenance claim does. | `round_v1/GATE_uair.json` (`oracle_nodesign_smoke_RMSE_mu`); `round_v3/tables/ORACLE_ARM_VERIFY.csv`; `.r3_work/r3_verify_oracle_arms.py` |
| 48 | **H4's mechanism gains a set-level proof, and the H line's decision is a `go` that must be read as H4.** "Driven by the dropped support alone" was an invariance argument over conditions (C0 ≈ C3 ≈ C4); it is now also an identity of the active sets between a FedAvg arm and an oracle arm on 20/20 seeds in both regimes (VI.4.3), plus a nesting result on the FedAvg side: same trace and same config hash in both regimes (20/20 seeds), A ⊂ B in every shared window, A never holds a window B lacks, medians `145` vs `192` client-windows (A keeps `74.6 %`, i.e. drops ≈25 % = H4's `72/288`). The 2 × 2 gives the effect sizes: regime ≈6 %, weights/information ≤0.3 %. | `round_v3/tables/ACTIVE_SET_REGIME.csv`; `round_v3/tables/REGIME_AB_FEDAVG.csv` (sha256 `bd7ccdf2…`); `round_v3/tables/UAIR_ARM_CONTEXT.csv` |
| 49 | **The round-3 FedAvg grid's `C4` and `C5` cells are not the condition they are labelled with, so the `C4`/`C5` rows of the VI.3 table have a condition-invalid FedAvg arm.** `round_v3/runs/C4_block_uniform/.../fedavg_window/seed*` are identical to the `C0` runs **on every numeric field except `runtime_seconds`, on all 20 seeds**, and carry the same `pi_tar_hash` (`8bab153a707d1267`) — i.e. the block-uniform override never took effect. Cause: `r3_p1p2.train_fedavg` built the injected condition as `dict(H.CONDITIONS["C0_frozen"])` and overwrote only `theta`/`tail_scale`/`model`, so `target` stayed `"test_share"` and `H.injected(...)` skipped the `block_uniform` branch that rescales the target bundle `mu`; the `pi_target_override` that was passed does not change the zero-mass set and left no metric trace. The h_round B-side `C4`/`C5` runs **did** carry that patch (`RMSE_mu 1.174352` vs `1.171263` at C0 seed 30001), so **the two sides of the C4/C5 comparisons are not the same condition**. Found by the endpoint round's replay gate (`results_regime_b_endpoints/round_v1/P2_REPORT.md` §3b). C0–C3 are unaffected; C5's FedAvg arm is θ=4 + `diurnal_blind` on `test_share`. **Repaired: item 50.** | `round_v3/P0_CELLS.csv` (`A_side_source`, values); `round_v3/runs/{C0_frozen,C4_block_uniform}/uair/fedavg_window/seed*/final_metrics.json`; `.rb_work/probe_c4_noop.py` output; `P2_REPORT.md` §3b |
| 50 | **Item 49 repaired, and the endpoint round's replay path repaired with it; the round-3 H verdict is unchanged.** Fourty FedAvg runs re-trained under `H.CONDITIONS[cond]` verbatim so the block-uniform bundle applies (`results_h_headroom/round_v3_fix/runs/`): `RMSE_mu` moves `+0.003157` (C4) / `+0.003102` (C5) on 20/20 seeds each, `Delta_group` by ≤0.015, and `Delta_c-s` by **exactly 0** — the metric is `sum |Pi_hat_ks − pi_tar_ks|` on `client × opportunity_stratum`, which a strictly positive rescaling of the *group* mass cannot move, so the P0 price cells were mislabelled but never wrong. Re-derived rows (estimator, `go_bar = 0.005` unchanged): C4 FedAvg `1.188238 → 1.191394`, `H_best 0.059330 → 0.061820` [0.047162, 0.076477]; C5 `1.179322 → 1.182424`, `H_best 0.052110 → 0.054595` [0.040396, 0.068793]; **both `go`, decision still `go`, six Design-off cells unchanged**; C0–C3 identical to ≤4.4e-16. Separately, the replay rebuilt inside `run_h_headroom.injected(...)` with the block-rescaled `mu` and a condition-matched oracle A side: the gate now passes **7 of 12** cell sets (was 2), with exact reproduction on every passing set; the five stopped sets are C1/FedAvg (seed 30014, whose exemption test correctly fails because the audit's θ value belongs to a different run) and C2/C5 × both pairs (seed 30002, covered by no pre-existing list). No tolerance was loosened and no exemption was invented after seeing values. Reported endpoint result: `E_dec` falls 23–39 % in regime B in all seven passing sets, entirely through false-alarm suppression, with B's exceedance-mass retention collapsing to `0.1 %` (2.1 % in one cell) against A's `20–34 %` — **no decision-quality claim survives for either regime**. | `round_v3_fix/{tables/C45_REPAIR_GATE.csv,REPAIR_GATE.json,tables/H_SUMMARY_fix.csv,tables/H_FIX_DIFF.csv,H_DECISION_fix.json}`; `results_regime_b_endpoints/round_v1/{P2B_ADDENDUM.md,P2B_REPORT.md,tables/P2B_GATE.csv,P2B_GATE.json}` |
| 51 | **The non-aggregating-final-window criterion extended to C2/C5 on authorization; the endpoint gate now passes 11 of 12 sets, and one set stays stopped by scope.** The 2026-09-29 audit's criterion (its `A1_INACTIVE_FINAL_SWEEP.csv: last_active`, enumerated there only for the frozen trees) was read from each run's own `window_metrics.json` and validated **before** scoring: it holds for **6/6** replay-failing A-side cells, **0/198** passing A-side cells and **0/204** B-side cells, i.e. it separates the classes exactly. Under the authorized scope (`C2`, `C5`) four cells are exempted (seed `30002`, both pairs) as *provenance* statements — their stored metrics are not reproducible from their checkpoints — and each affected set is reported twice: primary over exact-replay cells (n=16) and a labelled sensitivity including the exempted cell (n=17), differing by 3–4 pp without changing sign, interval or conclusion. **fedavg `C1` seed 30014 satisfies the criterion but lies outside the authorized scope and remains hard-failing**; no other cell is waived. Across the 11 reportable sets the reading is uniform: `E_dec` down 23–39 % in regime B, entirely false-alarm suppression, B's exceedance-mass retention `0.0–0.6 %` (2.06 % in one cell) against A's `17.5–33.9 %`. | `results_regime_b_endpoints/round_v1/{P2C_ADDENDUM.md,P2C_REPORT.md,tables/P2C_CLASS_TEST.csv,tables/P2C_GATE.csv,tables/P2C_CONTRASTS.csv,P2C_GATE.json}` |
| 52 | **The same criterion extended to `C1` on authorization closes the endpoint round: 12 of 12 cell sets pass, with six disclosed exemptions and no tolerance change.** The one set `P2C` left stopped was fedavg `C1` seed `30014`; it satisfies the criterion (its run's last window is inactive) but was outside that addendum's scope, and its audit-θ route does not apply because `C9_H_THETA_RECHECK.csv`'s θ value for that cell belongs to the h_round run, not the round-v3 one. With `C1` in scope the gate passes **12/12**; the six exempted cells (`C1 30014`, `C2 30002`, `C5 30002` × both pairs) are provenance statements, each offset by a labelled sensitivity at n=17. Final endpoint reading over all twelve sets: `E_dec` falls **20.1–39.1 %** in regime B with the CI excluding zero everywhere, entirely through false-alarm suppression (A `0.20–0.28` vs B `0.001–0.006`), while B's exceedance-mass retention is **0.00–2.48 %** against A's **17.5–33.9 %** (exactly zero on both `C2` and both `C5` cells). **No decision-quality claim survives for either regime**, and the result contradicts neither the P0 calibration price (`+3.1…+4.8 %`) nor the round-3 H verdict: the two endpoints measure opposing sides of the same rule change. The tolerance stayed `1e-12` throughout; the criterion had to pass a discrimination test before use; no earlier exemption route was retracted. | `results_regime_b_endpoints/round_v1/{P2D_ADDENDUM.md,P2D_REPORT.md,tables/P2D_RUNS_SCORED.csv,tables/P2D_GATE.csv,tables/P2D_CONTRASTS.csv,P2D_GATE.json}` |

## VI.6 What Part VI does not do

* It does not re-open the `STOP` of `results_h_response_shift/round_v1/H_DECISION.json`, which rests on
  the predictor-endpoint cells and stands independently of the FedAvg defect.
* It does not revise any manuscript claim, table or number; the round's H cells land on the paper's own
  Design-removal row and on `eq:design_gate`.
* It does not adjudicate whether regime B's gain is legitimate estimation (VI.4.4).
* It does not carry the corrected arm into SensorScope, which H4 already reports as ≈0 and which round
  3 did not re-run.
* It touches no file under `TO_OVERLEAF_paper_tmc_r1_clean/`; the scorecard is unaffected.

## VI.7 Reproduce

```text
.venv_new/Scripts/python.exe .r3_work/r3_p1p2.py --run      # P1 gate + P2 training (120 runs)
.venv_new/Scripts/python.exe .r3_work/r3_htable.py           # H table, support cost, H_DECISION.json
.venv_new/Scripts/python.exe .r3_work/r3_pairing_check.py    # 240/240 EventTrace_hash pairings
.venv_new/Scripts/python.exe .r3_work/r3_verify_oracle_arms.py
.venv_new/Scripts/python.exe .r3_work/r3_active_sets.py
.venv_new/Scripts/python.exe .r3_work/r3_regime_fedavg.py
```

| artifact | sha256 (first 8) |
|:---|:---|
| `round_v3/PREREG_P2.md` | `1ae031f8` |
| `round_v3/EXECUTION_REPORT.md` | `ff0fa272` |
| `round_v3/H_DECISION.json` | `8715a3b0` |
| `round_v3/tables/H_SUMMARY.csv` | `9af72e0c` |
| `round_v3/tables/SUPPORT_COST_CORRECTED.csv` | `8d0c16de` |
| `round_v3/tables/ACTIVE_SET_REGIME.csv` | `fc32027b` |
| `round_v3/tables/REGIME_AB_FEDAVG.csv` | `bd7ccdf2` |
| `round_v3/tables/ORACLE_ARM_VERIFY.csv` | `5930136e` |
| `round_v3/tables/C0_REPRO.csv` | `5f468591` |
| `round_v3/tables/UAIR_ARM_CONTEXT.csv` | `a70c91a2` |

# Part VII — Round-12 revision ledger (canonical, updated in place)

Owner: `ccf-rebuttal-writer`. This is the single revision ledger for the round-12 review
(`raven-mcs-tmc-review.md`, version-comparison mode, contract `TMC-J-R4`, historical `main.tex`
`88ecd743321e38e9`, reviewed current `59e4f4d5cffff4ff`). It is not a scorecard: the reviewer owns the
scores, and the next comparison round decides whether any dimension moves. Columns follow
`references/revision-ledger.md`.

Manuscript after this revision: `main.tex` **`02447bfe6256632b…`**, 113 854 B, 3 hunks / +9 / −1 lines,
+63 source words; `main.pdf` **17 pp** held, 0 errors / 0 undefined / 0 multiply-defined / 0 overfull;
`supplemental.pdf` 16 pp with its one pre-existing overfull box unchanged. Pre-edit snapshot:
`snapshots/2026-10-06-pre-r12-fix/`. **No number, table, figure or claim changed; no new experiment; no
bibliography change.**

| ID | First seen | Current version | Concern | Origin | Applies to | Affected dimension | Status | Action / location | Evidence | Comparative score effect | Risk |
| --- | --- | --- | --- | --- | --- | --- | --- | --- | --- | --- | --- |
| R5-16 | round 5 | `59e4f4d5` | "recoverable" carried two quantities | inherited | both | Clarity, Terminology | `resolved` | renamed at both sites (r11); current text has two uses, both the ceiling sense | `main.tex` L1819, L2194; round-12 diff hunks 1 and 4 | Terminology +1 (round-12 progress scorecard) | none |
| M3 | round-10 state | `59e4f4d5` | privacy sentence had the wrong antecedent | inherited | both | Clarity | `resolved` | resequenced (r11) | round-12 diff hunk 3 | none | none |
| A-8 | round 10 audit | `59e4f4d5` | the `8.23`–`21.73` range mislabelled two arms' tokens | inherited | both | Clarity | `resolved` | range deleted (r11); qualitative claim retained | round-12 diff hunk 2 | none | the magnitude is no longer printed |
| M2 | round-10 state | `02447bfe` | availability paragraph named no artifact behind the new numbers | inherited | both | Reproducibility | **`done`** | Data and Code Availability, first paragraph now names `w1/`, `w1/PAPER_NUMBERS.csv` and `verify.py` | `RAVEN_MCS_PUBLIC_REPRO_R1/w1/` (217 files), `verify.py`; r12 edit hunk 3 | reviewer's condition for Reproducibility 2→3 is now met; re-scoring belongs to the next round | none |
| M4 | round-12 review | `02447bfe` | the band's rule is on the page, its provenance is not | previously_undetected | both | Clarity, Reproducibility | **`done`** | §"Structural Alignment Objective", band paragraph now cites `w1/ladder_v3/PREREG.md` as where the band and its reading rule were fixed | bundled `w1/ladder_v3/PREREG.md` L97–98 states both rules; r12 edit hunk 2 | supports the same Reproducibility condition | the pointer names a file inside the released bundle |
| CL-3 | round-12 review | `02447bfe` | contribution 3 carried the theorem, the verdict, the κ exclusion and a table pointer in one bullet | previously_undetected | both | Clarity | **`done`** | contributions list: the verdict, the κ exclusion and the prediction pointer move to their own `\item` ("What the measurement does not attribute"); the moved text is verbatim | L215–237 before, L215–239 after; r12 edit hunk 1 | completes the Clarity repair condition; the raise itself is the next round's call | one more bullet; no claim changed |
| NEW-r12-3 | round-12 review | `02447bfe` | "closable gap" versus "closed by uniform weights" | newly_revealed_by_evidence | current | Terminology | `open` (deferred) | none; the review did not charge it | L606–609, L1819, L2194 | none | two near-identical names for two different gaps remain |
| E1 | round 9 | `02447bfe` | alignment is not shown to buy accuracy, and **every** repair route on SensorScope and U-Air is now measured and closed | inherited | both | Evidence, Significance | `open` | no manuscript change possible on these two blocks: the weights route (Part VIII item 62: 51.4 % / 69.0 % of active windows have `\|A_r\| ≤ 2`), the estimand route (item 61: regret 0, `d̄ = 0`), the gate law (item 59: both slopes `null`), the gate decision (item 60: unreachable by construction) and the exceedance endpoint (`NEW-r12-1`) are all closed by measurement. The III-table row those labels select is **row 4**: report the bound (`results_evidence_axis/round_v1/WRITING_PROPOSAL.md`) after that round's four corrections. A new block (NSW-Traffic) is in design, where N1 holds (6.7 % `≤ 2`, mean `\|A_r\|` 12.06) | L2096–2101; `results_regime_b_endpoints/round_v1/P2D_REPORT.md`; `results_gate_dose/round_v2/JOINT_READING.md`; `results_new_block_traffic/round_v1/S0_VERDICT.json` | holds the stance at 5/10 | decisive |
| E2 | round 9 | `02447bfe` | the named calibration program is not what moves the endpoint | inherited | both | Significance, Originality | `open` | not addressed; the new bullet makes the verdict visible but does not lead the contribution list with the projection | L229–237, L1826–1856 | none by itself | high |
| NEW-r12-1 | round-12 endpoint round | `02447bfe` | the decision endpoint is saturated on U-Air in both regimes | newly_revealed_by_evidence | current | Evidence | `open` (boundary) | recorded; it forbids re-offering the same endpoint as E1's repair | `tables/P2D_CONTRASTS.csv`; `P2D_REPORT.md` | none; it narrows E1's repair path | prevents repeating an instrument that cannot separate the arms |
| NEW-r12-2 | round 9 (F10) | `02447bfe` | supplemental build keeps one overfull box | inherited | both | Reproducibility | `partially_resolved` | labels fixed earlier; the vbox remains; no supplemental edit this pass | `main.log` 0/0/0; `supplemental.log` 1 Overfull | none | low |

Ledger rules honoured: nothing is marked `done` that does not exist at a named manuscript location;
no response text promises an action absent from this table; the two evidence items are recorded as
`open` with the reason rather than answered with prose.

Response artifact for this revision: `ccfa-review-reports/raven-mcs-r12-response-to-review.md`.

---

# Part VIII — Record corrections, 2026-10-07 (rounds 13–15: the Evidence-axis closure, gate-dose v2, estimand selection)

Owner: `ccf-rebuttal-writer`. This continues the *correction* series of VI.5 (items 45–52) and is
**not** Part VII's review ledger. Every item below was found and measured on 2026-10-07 in this
session's rounds; no manuscript file, `src/` file or existing `results_*` directory was edited by
any of them. `main.tex` remains `02447bfe6256632b…` throughout.

## VIII.1 Corrections (items 53–62)

| # | correction | evidence |
|:--|:---|:---|
| 53 | **The Evidence axis now has a measured bound, and the bound is why the axis never moved.** The deployment targets are near-uniform: the largest group carries **0.53 %** of the mass on SensorScope (220 groups) and **0.79 %** on U-Air (144 groups); `1 − H/H_max` is **0.0027** and **0.0010**. A window's contributing clients reach only **0.67 %** (SS) and **0.89 %** (UA) of the target-positive mass. With the checkpoint fixed and only the **evaluation** weights changed, `RMSE_μ` and the uniform-weighted RMSE differ by **0.8208 %** (SS) and **0.2660 %** (UA) at 20 seeds. Scope caveat, stated because an earlier draft of this record got it wrong: these are **evaluation-layer** figures and bound nothing about reweighting during training. | `.rb_work/evidence_headroom/{TARGET_CONCENTRATION,HEADROOM,REACHABILITY,REACHABILITY_CEILING}.csv`; `results_evidence_axis/round_v1/EVIDENCE_BASE.md` §1–§3 |
| 54 | **The manuscript's paired MDE pair is on two scales, and the second value is the wrong one.** `main.tex` L2115–2120 quotes SensorScope `0.17`–`0.36` pp and U-Air `0.70`–`0.80` "points". `results_gatekeeping/round_v1/A1_POWER.csv` gives `mde80` **0.42–0.45 %** (SS) and **0.08–0.09 %** (UA), so the U-Air range is off by roughly a decade. Consequence for reading the U-Air null: the design **can** see effects of the size the weighting term could carry, so the correct statement is "the effect is absent", not "the endpoint is blind". This is audit item `EV-2` and it remains **open** — no manuscript edit. Own recomputation of the `mde80` column disagrees with it (see item 55), so the convention must be settled before either number is printed. | `ccfa-review-reports/raven-mcs-evidence-axis-audit.md` `EV-2`/`EV-3`; `results_gatekeeping/round_v1/A1_POWER.csv`; `.rb_work/evidence_headroom/MDE_RECONCILIATION.csv` |
| 55 | **The `A1_POWER.csv` `mde80` column is not reproducible from its own inputs, and the discrepancy is unexplained.** The paired MDE from the column's own `paired_sd` and `n` is `2.802·s_d/√n` = **0.00618** (SS) and **0.0649** (UA) in absolute terms, i.e. 0.078 % and 5.4 % of the frozen `RMSE_μ` means — while the column itself prints 0.00445 and −0.000758 (negative). Neither the column nor the recomputation is adopted here; the disagreement is recorded because two rounds have now quoted numbers from it. | `.rb_work/evidence_headroom/MDE_RECONCILIATION.csv`; `results_gatekeeping/round_v1/A1_POWER.csv` columns `paired_sd`, `se_used`, `mde80` |
| 56 | **The `ρ` frame in the gate-dose instruction cannot be satisfied as written, and the two candidate frames differ materially.** The instruction pins `m = 0` to SensorScope `0` and U-Air `≈ 0.354` while specifying the `c1_deletion_driver::rho_for` semantics (delivered `U = 1` units on non-test splits). On these datasets those select different frames: the trace-delivered frame gives **0.2543** (UA) and the train-atom frame gives **0.35443037974683544**, which is the pinned value and equals `post_review/C2_scd_phi/tables/SCD_PHI.csv::phi_train_unit`. Only the train-atom frame is within the instruction's own 1e-6 tolerance (the printed `0.354` is 4.3e-4 away). The same issue forces ρ to carry **no seed dimension**, which is what the design needs but is not what "per (dataset, level, seed)" says. Resolved by user confirmation 2026-10-07: train-atom frame, unrounded anchor. | `results_gate_dose/round_v1/{RHO.csv,TARGET_WIRING.json}` (`m0_rho_check`); `scripts/gate_dose.py::CONFIRMED`; `results_gate_dose/round_v1/P0_REPORT.md` §3.1 |
| 57 | **The gate-dose instruction's `m = 0` gate assumed the stored artifacts are the same object as a fresh run; they are not for the `raven` arm.** `raven_wo_design` reproduces its stored artifacts bit-exactly (`\|Δ\| = 0` on all four endpoints), but `raven` does not: `\|ΔRMSE_μ\|` is **4.20e-7** (SS) and **3.78e-10** (UA) against a 1e-9 bound, because θ itself differs (`max\|Δθ\|` 3.09e-7 / 1.49e-8). Two runs inside one environment are bit-identical, so this is not noise: the stored artifacts predate the current tree (ledger `git_commit b01db69e…`, 22 files / +4173−176 lines of drift, and the artifacts lack the `p2_invocation_states.json` audit file the current runner writes). Round v2 resolves it by generating its own `m = 0` cells for `raven` and using the stored artifacts only in the drift check. | `results_gate_dose/round_v1/P0_REPORT.md` §5; `results_gate_dose/round_v2/{GATE_G2.json,GATE_G3.json}` |
| 58 | **The gate-dose II-3 bound was calibrated on one favourable cell.** `GATE_AMENDMENT.md` records that II-3 justifies the relative 1e-6 bound with "the measured drift (5.3e-8 relative on SensorScope)", which holds for seed 30001 `RMSE_mu` only. Measured over 20 seeds × 2 datasets × 4 endpoints the drift reaches **1.516e-06** (Δ_group, SS seed 30019) and **2.229e-06** (RMSE_mu, UA seed 30002), so the bound missed in **3 of 40** cells while `active_clients` was identical in **40 of 40**. The bound was amended to 1e-5 (500× below δ = 0.5 %) on authorization, with the original verdict, the file `GATE_G3.json` and the pre-amendment stop record `GATE_REPORT.md` **preserved unchanged**, and with a 95th-percentile condition (≤ 2e-6) added so the amended bound must clear the bulk of the distribution, not just its worst cell. | `results_gate_dose/round_v2/{GATE_AMENDMENT.md,GATE_ORIGINAL.json,GATE_G3.json,GATE_G3_AMENDED.json}` |
| 59 | **`ρ` does not predict the accuracy cost of Design; it does predict the calibration cost, and that is a different endpoint.** Round v2 (246 runs, 200 dose cells, amended gate pass): H1 slopes **+0.001365** (SS, CI [−0.003556, +0.006356]) and **−0.073079** (UA, CI [−0.165370, +0.022770]) — both `null`, so `gate_law = not supported`, H2 `not_tested` and `ρ*` unreported. The descriptive slopes are the informative part: `r_Δc-s` is **−0.1331** (SS) and **−0.3565** (UA) with both intervals strictly negative, while `r_Δgroup` changes sign between datasets (**+0.0568** SS, **−0.1523** UA). SensorScope's prediction-endpoint dose response is at most **+0.17 %** against δ = 0.5 %; U-Air's is **+6.6 % to +7.5 %** and *decreasing* in ρ. | `results_gate_dose/round_v2/{DOSE_DECISION.json,tables/DOSE_SLOPES.csv,tables/DOSE_SUMMARY.csv}`; `PART_II_REPORT.md` §2–§3 |
| 60 | **The gate cannot beat both fixed settings in this design, for a structural reason.** For `w_pred` the gate-versus-`always_on` difference is **identically zero on all 20 seeds** (reported as measured, `n_zero_diffs: 20`), because at ρ = 0 the gate's rule *is* `always_on`; the protocol's `open` condition requires the CI upper bound to be < 0 for **both** comparisons, so it is unreachable by construction. `gate_decision = null`. This was not knowable from the instruction and is recorded so that no future round re-offers the same comparison as a test. | `results_gate_dose/round_v2/DOSE_DECISION.json` → `h3.primary_w_pred`; `PART_II_REPORT.md` §4 |
| 61 | **The estimand gap is large, real, and does not reach the selection decision.** Arrival-weighted validation misreports the deployment risk by **−4.11 % to −4.12 %** on SensorScope (all nine candidates, Student-t intervals excluding zero) and **+0.27 % to +0.62 %** on U-Air, yet the ranking is preserved exactly: disagreement rate `d̄ = 0` (Wilson [0.000, 0.161]), regret identically `0.000000`, median Kendall τ = 1.000, and sign-flip rate **0.0000** on pairs with `\|ΔR_μ\| > δ`. Both datasets are labelled `saturated` by the base-rate condition. The misreport is near-constant across candidates — a level shift, not a ranking change — which is why the largest such gap on record converts into zero selection cost. Both were registered before the scores existed: `WEIGHTS.csv` was written in its own stage, and the `TV(π_arr, μ)` figures are **0.3548** (SS) / **0.4255** (UA) at group level. | `results_estimand_selection/round_v1/{SELECTION_DECISION.json,WEIGHTS.csv,tables/RISK_ROWS.csv,tables/SELECTION.csv}`; `PART_I_REPORT.md` §3–§4 |
| 62 | **Method-level lesson: the block's ability to move the endpoint was never checked before the endpoint was run.** Every Evidence-axis route on SensorScope and U-Air is now measured and closed — weights, estimand selection, gate law, gate decision, exceedance decision — and the four rounds share one cause: the usable freedom of the weights was never established first. It is not usable there: **51.4 %** (SS, 965/1877 active windows) and **69.0 %** (UA, 968/1402) have `\|A_r\| ≤ 2`, so under `α_max = 0.5` the weights are pinned by the constraint. Any future Evidence-axis round must state and measure its necessary conditions **before** spending runs, not after. | `.rb_work/estimand_inventory.py` output; `results_estimand_selection/round_v1/INVENTORY.json` → `active_window_support`; `raven-mcs-new-block-traffic-execution-prompt.md` §0 (`N1`) |

## VIII.2 Ledger rules honoured

* Items 53–62 are corrections and closures, not scorecard entries: nothing here is marked `done` at
  a manuscript location, because **no manuscript location exists for any of them**. The only
  manuscript-adjacent items (54, 55) are recorded as **open** with their blocking reason.
* Item 55 is recorded as an **unresolved disagreement**, not as a resolved correction, because two
  candidates remain and choosing one now would be choosing after seeing which number is convenient.
* Item 58 discloses an authorization-driven amendment with the pre-amendment verdict preserved
  verbatim; the amendment changed one tolerance and nothing else, and its own first confirmation
  rule was withdrawn in writing before it could run because it required non-existent artifacts.
* The round-v2 driver's execution defects found while producing the numbers it reports — a dose
  output path that omitted the level and would have made successive levels overwrite each other, a
  level-key format mismatch (`RHO.csv` floats vs `MASKS.json` strings), an unwired `p3` CLI stage,
  an H3 column-name mismatch, and a missing `wilson` helper — are recorded in
  `results_gate_dose/round_v2/PART_II_REPORT.md` §6 rather than in this ledger, because they were
  caught and fixed **before** any reported number was produced. The path defect is the one that
  would have been silent: it crashed on the first attempt with no cell reported.
* No number in this part contradicts Parts I–VII. Where an earlier part's figure is superseded
  (the MDE pair, item 54), the supersession is stated rather than silently applied.

## VIII.3 Standing state after this part

`main.tex` `02447bfe6256632b…` (unchanged, 17 pp). Evidence-axis labels now on record:
Part I `saturated` on both blocks, Part II `gate_law = not supported`, `gate_decision = null`. The
III-table row those labels select is **row 4**: report the bound
(`results_evidence_axis/round_v1/WRITING_PROPOSAL.md`) after the four corrections listed in that
round's review — the MDE convention (item 54), the evaluation-layer scope of the fixed-checkpoint
figures (item 53), the withdrawn "composition" relabel, and per-dataset sourcing of every table
cell. A separate round is in design for a new block (`NSW-Traffic`) whose `N1` condition already
holds; it has not been run and no number from it exists.

---

# Part IX — Record corrections, 2026-10-08 (workspace hygiene, the traffic lineage, and the reuse-guard exemption)

Owner: `ccf-rebuttal-writer`. This continues the correction series of VI.5 (items 45-52) and VIII.1
(items 53-62) and is **not** a review ledger. Every item was measured on 2026-10-08 in this session.

## IX.1 Corrections (items 63-65)

| # | correction | evidence |
|:--|:---|:---|
| 63 | **85 of the entries under `src/` are untracked, and the cause is "never staged", not an ignore rule; 82 % of the affected files predate the last commit.** `git ls-files src` gives 116 tracked files; `git status --porcelain -- src` gives 85 untracked entries, which expand to **357 files / 3.2 MB**. `git check-ignore -v` returns nothing for `reuse_guard.py`, `real_runner/runner.py` or `protocol_closure/__init__.py`; `.gitignore` has no `src`/`e3`/`protocol` rule; `core.excludesfile` is unset — so no ignore rule explains it. The untracked set is **292 files from 2026-08, 48 from 2026-09 and 17 from 2026-10**, i.e. most of it predates HEAD (`2e47464`, 2026-09-11 08:40:44 +0800, the last commit in the repository). It is therefore not "work after the last commit" but whole packages that were never added. The largest untracked packages are `src/raven_mcs/e3/` (125 files, 2026-08-28 17:01:55 -> 2026-10-07 17:00:59), `src/raven_mcs/e4/` (30), `src/raven_mcs/paper_data_r1/` (16), `src/raven_mcs/tdrive_protocol_seal_r1/` (15), and six 9-11-file packages all stamped 2026-08-28 17:01:55-56. Files by date: `2026-08-05` 7, `2026-08-21` 4, `2026-08-28` 167, `2026-08-30` 105, `2026-08-31` 9, `2026-09-05` 4, `2026-09-11` 4, `2026-09-23` 1, `2026-09-28` 7, `2026-09-29` 32, `2026-10-07` 17. **Attribution limit, stated so it is not over-read:** mtimes record *when*, never *who*. The workspace therefore **cannot** establish that several agents caused the untracking. What it does establish is that the tree was worked on across at least eleven distinct days with commits stopped on 2026-09-11, which is consistent with the project record naming more than one agent (handoff §10-§16 are "another Agent"), but that is corroboration, not proof. | `_r13_build/SRC_UNTRACKED_AUDIT.json` (script `_r13_build/audit_src_untracked.py`); `git ls-files src`; `git status --porcelain -- src`; `git check-ignore -v`; `git log -1 --format=%ci` |
| 64 | **The three NSW-Traffic run trees are three different experiments, and the reuse guard protects the oldest of them, not the newest.** (i) `artifacts/e2_traffic_formal_runs_r1` — 2026-08-07 23:32 to 08-09 07:51, 20 seeds x 6 scenarios x 5 arms (`fedavg_window`, `fedasync_window`, `flamf_timealign_adapted`, `twostage_hajek`, `raven`) = 600 runs; its `complete_aligned` subset (20 x 5 = **100 runs**) is exactly the "sealed E2 Traffic Complete-aligned 100-run block" the guard names. (ii) `artifacts/e3_formal_runs_r1/runs/traffic` — 2026-08-11 15:47 to 17:37, 6 arms x 20 seeds = 120 runs; E3 **reused** E2's traces (`E3_TRAFFIC_EVENTTRACE_REUSE_AUDIT.csv` marks every row `COPIED` from `e2_traffic_formal_runs_r1/eventtraces/<seed>/complete_aligned/training_eventtrace`) and trained only the arms outside the reuse list, so `fedavg_window` and `raven` have **no E3 counterpart** — which is why the S1' instruction's three traffic arms do not all exist and why no frozen traffic `fedavg_window` exists. (iii) `results_new_block_traffic/round_v1` — 2026-10-07 15:25 to 16:27:41, S0 (read-only family screen) plus an S1 ladder that **trained** `fedavg_window` at `local_steps` 5/10/20 x seeds 30001-30003 (9 runs) and **read** the 2-step rung from the sealed E2 grid (`local_steps_source = sealed_e2_complete_aligned_read_only`). Guard provenance - **[amended 2026-10-08, see item 66]** `reuse_guard.py` mtime **2026-10-07 17:00:29** and `real_runner/runner.py` mtime **2026-10-07 17:00:32**, both after the 16:27:41 end of round (iii). As first written this invited the reading that the guard *module* was created then; item 66 corrects that. What the timestamps establish is that both files were last written after round (iii) closed and that the guard was therefore not enforced on round (iii)'s path - not that the module is new. Round (iii)'s driver `scripts/new_block_traffic_stages.py` contains no guard bypass (grep for `guard`/`assert_schedulable`/`DuplicateReused`: 0 hits) and its nine `traffic + complete_aligned + seed 30001-30003 + fedavg_window` runs succeeded, which are precisely the cells the guard refuses, so the guard was not enforced on that path at that time. **Limit:** round (iii)'s ledger records `runner_source_hash: null` (it passed no `source_identity`), and both files are untracked, so the runner version in force during round (iii) cannot be read directly. | `artifacts/e2_traffic_formal_runs_r1/runs/30001/*/`; `artifacts/e3_formal_runs_r1/E3_TRAFFIC_EVENTTRACE_REUSE_AUDIT.csv`; `results_new_block_traffic/round_v1/S1_LADDER.csv`; file mtimes; `scripts/new_block_traffic_stages.py` |
| 65 | **The E3 traffic reuse guard was relaxed on 2026-10-08 by explicit user authorization, in one narrow, reversible form.** `assert_schedulable_e3_run` gains a default-`False` `allow_reused_traffic_rerun` parameter; `run_e3_real` reads it from its own `source_identity`, so an exempted run records the exemption inside its own ledger, and the guard emits a `RuntimeWarning` when the exemption is exercised so it cannot be silent. `is_reused_e2_traffic_block` is unchanged and still returns `True` for those cells, so any caller asking "is this a reused block?" gets the same answer as before. Verified after the edit: default -> `DuplicateReusedTrafficRunBlocked`; `allow_reused_traffic_rerun=False` -> `DuplicateReusedTrafficRunBlocked`; `allow_reused_traffic_rerun=True` -> no raise with the warning emitted; `raven_simoracle` and SensorScope cells unaffected. `reuse_guard.py` 46d26da601b82672 -> 3d79703e5456016b; `runner.py` 4c25921a042e1954 -> c82b261c10c3eb2b. Every file a change would touch was copied byte-for-byte to `results_server_optimizer/round_v1/backup_pre_guard_change/` **before** the edit, together with sha256 manifests of 9 175 sealed-evidence files (hashes only) and a runnable `RESTORE.py`. **Caveats that must travel with any later traffic run:** the guard exists because E3 traffic reused E2 rather than retraining, and the runner has drifted since the E3 runs (their ledger records `runner_source_hash = 2f5728de...`; the worktree file now hashes to c82b261c10c3eb2b), so a new traffic run is **not** the same object as the frozen E3 traffic evidence and must never be compared to it as if it were. The S1' round itself ran entirely under the **unmodified** guard: no cell of that round used the exemption. | `src/raven_mcs/e3/protocol_closure/reuse_guard.py`; `src/raven_mcs/e3/real_runner/runner.py`; `results_server_optimizer/round_v1/backup_pre_guard_change/BACKUP_MANIFEST.json` |

## IX.2 Ledger rules honoured

* Items 63-65 are corrections and provenance records, not scorecard entries.
* Item 63 states an attribution limit rather than converting a timestamp pattern into a claim about
  authorship.
* Item 64 corrects a conflation in this session's own reporting (the 16:27 round is not the block the
  guard protects).
* Item 65 records an authorized exception together with its reversal path and the caveat that the
  newly permitted runs are not the sealed objects.

## IX.3 Standing state after this part

`src/` now differs from its pre-2026-10-08 state in exactly two files, both recorded above with hashes
and a restore script. The S1' round (`results_server_optimizer/round_v1/`) is unchanged and was
produced under the unmodified guard.

## IX.4 Second-pass corrections and additions (items 66-68), 2026-10-08

| # | correction | evidence |
|:--|:---|:---|
| 66 | **Correction to item 64: the protocol-closure guard is not new.** Item 64 recorded only that `reuse_guard.py` has mtime 2026-10-07 17:00:29, which invited the reading that the guard was created then. It was not. `artifacts/e3_multidataset_real_runner_canary_r1/E3_CANARY_TRAFFIC_REUSE_GUARD.json` (**mtime 2026-08-10 21:57:49**, duplicated at `artifacts/e3_numerical_integrity_clean_canary_fix_r1/E3_CANARY_TRAFFIC_REUSE_GUARD.json` 2026-08-11 09:29:51) reports `formal_block_still_active: true` and `is_reused_e2_helper: true`, and both of those values are produced by **calling the protocol-closure guard's own functions** (`assert_schedulable_e3_run`, `is_reused_e2_traffic_block`) through `e3/canary/traffic_reuse_guard.py`. The guard therefore existed and refused correctly on **2026-08-10**, two months before the timestamp item 64 cites. What the 2026-10-07 17:00:29 / 17:00:32 writes mark is the **wiring of the guard into `run_e3_real`** (plus a rewrite of the untracked guard file) - which is what let round (iii) at 15:25-16:27 train nine `fedavg_window` traffic cells that the guard refuses today. Both files are untracked, so neither the guard's nor the runner's pre-17:00 content can be read; the wiring inference rests on the timestamps, on those nine runs succeeding, and on the driver containing no bypass. | `artifacts/e3_multidataset_real_runner_canary_r1/E3_CANARY_TRAFFIC_REUSE_GUARD.json`; `src/raven_mcs/e3/canary/traffic_reuse_guard.py`; file mtimes |
| 67 | **There are two traffic guards, not one, and they are layered.** `e3/protocol_closure/reuse_guard.py` (the formal-seed guard) refuses `traffic + complete_aligned + seed in 30001..30020 + {fedavg_window, fedasync_window, flamf_timealign_adapted, twostage_hajek, raven}` with `DUPLICATE_REUSED_TRAFFIC_RUN_BLOCKED`. `e3/canary/traffic_reuse_guard.py` (the canary guard) **imports the formal-seed guard** and adds a strictly wider exclusion: the same five methods on traffic at **any** seed, including the canary seed 31001, raising `REUSED_METHOD_PATH_NOT_EXECUTED_IN_TRAFFIC_CANARY`. Its recorded proof lists the canary's permitted traffic methods as exactly `local_hajek, inst_cal, debt_cal, raven_simoracle, central_all, central_delivered` - **exactly the six arms present in `artifacts/e3_formal_runs_r1/runs/traffic`** - so the arm gap recorded in item 64 is the guard's design rather than an accident. Verified after the item-65 exemption: `build_traffic_reuse_guard_evidence()` still returns `status: PASS`, `duplicate_blocked: true`, `formal_block_still_active: true`; `assert_canary_schedulable` still raises for `fedavg_window` and `raven` at seed 31001 and still permits `raven_simoracle` and `debt_cal`; the new opt-in does **not** leak into the canary path, because the canary guard calls `assert_schedulable_e3_run` without the flag and independently raises its own code. | `src/raven_mcs/e3/canary/traffic_reuse_guard.py`; `E3_CANARY_TRAFFIC_REUSE_GUARD.json`; live re-run of the evidence builder |
| 68 | **The V2.3 design document contains neither guard and no reuse/seal-block policy.** `参考文件/RAVEN-MCS_V2.3_实验设计方案.docx` (mtime 2026-07-26 20:39, 405 866 B; 242 non-empty paragraphs, 35 tables, 26 859 extracted characters) has **zero** occurrences of `guard`, `守卫`, `sealed` as a run-block concept, `复用`, `重跑` in the reuse sense, `金丝雀`, `canary`, `30001`, `31001`, `REUSED`, `DUPLICATE`, `REUSE_ONLY`, `traffic_reuse_guard`, `reuse_guard`, `protocol_closure`, `E2_TRAFFIC` or `CanaryTrafficSealed`. Its thirteen `封`-family hits are configuration **freeze** rules (e.g. "冻结配置后生成 frozen_config.yaml 和 hash", "测试段只在最终冻结配置后运行一次"), a different concept. What the document does specify, and what the guards later operationalise, is: **G1 事件复现** ("同一 seed 下所有方法的 R、O、E、U、计算时延、网络时延完全相同"); the test-once rule and the manifest requirement ("每个 run 的 manifest.json 至少包含 Git commit、dirty 状态、数据哈希、配置哈希、环境哈希…"); a staged seed protocol ("先 3 个种子筛选，再用 5 个种子确认；最终冻结后跑 20 种子"); and NSW Traffic as a controlled dataset with a mandatory station-quality gate. The reuse/seal policy itself lives only in code plus the 2026-08-10 evidence. Note for item A3 of the S1' round: the document's own staged logic (small screen, then confirmation, then 20) is consistent with reading the S1' instruction's `n = 15` as the eventual confirmatory set rather than the screen, although the document's numbers (3 / 5 / 20) are not the instruction's (5 / 15). | `_r13_build/DESIGN_V23_EXTRACT.txt`; `_r13_build/DESIGN_V23_GUARD_SEARCH.md`; scripts `extract_design_docx.py`, `search_design_concepts.py` |

## IX.5 Third-pass additions (items 69-73), 2026-10-08

| # | correction | evidence |
|:--|:---|:---|
| 69 | **The NSW-Traffic Stage A was completed under the recorded exemption, and all three blocks PASS N3'.** After the user authorized the narrow guard exemption and asked for the traffic block, its 15 grid cells ran (`fedavg_window`, `eta_s in {1e-3, 3e-3, 1e-2}` x seeds 30001-30005; all 15 complete). Validation means: `eta_s=1e-3` 0.864388, **`eta_s=3e-3` 0.819805 (selected)**, `eta_s=1e-2` 0.907197, each over 5/5 usable screen seeds. N3' on test against the frozen `central_delivered` on the same seeds: `c = 0.9737694569747332`, new `fedavg = 0.8350944692092265`, `ratio_to_c = 0.8575895076886716` -> **PASS** (SensorScope 0.986505 PASS, U-Air 0.832921 PASS). For NSW-Traffic `frozen_fedavg_window` is `None` because the E3 traffic tree has no such arm, so N3's PARTIAL branch is not evaluable there and only PASS/FAIL apply; this is recorded rather than papered over. Every traffic run carries `REUSE_GUARD_EXEMPTION.json` plus a `reuse_guard_exemption` field in `SERVER_OPT_META.json` (15/15), so each identifies itself as exempted. | `results_server_optimizer/round_v1/{S1P_FROZEN_CONFIG.json,S1P_STAGE_A_VERDICT.json,tables/STAGE_A_GRID.csv}`; `runs/A_eta*/traffic/fedavg_window/seed*/REUSE_GUARD_EXEMPTION.json` |
| 70 | **Traffic passed its own identity test, closing the gap amendment A2 left.** A2 had excluded NSW-Traffic from G0 because the E3 traffic tree lacks `fedavg_window` and `raven`, so the override had never been checked there. Running `traffic/fedavg_window/seed30001` with the override disabled and again with the override active but the server optimizer set to plain SGD gives **32/32 deterministic fields equal**, only `runtime_seconds` differing, and a **byte-identical final checkpoint** (`15de443736271d97`); the `K_r <= 3` share is identical (0.111111). A forced repeat of one traffic cell reproduced `RMSE_mu` (0.8628721594092053), the checkpoint hash (`7180a33de2eea17c`) and the validation `RMSE_mu` (0.8562045367964333) exactly. The identity property and determinism therefore now hold on all three blocks. | `results_server_optimizer/round_v1/S1P_TRAFFIC_G0_DIAGNOSTIC.json`; driver `traffic_identity_check.py` |
| 71 | **Correction to item 65: the ledger cannot carry the exemption, so item 65's wording was wrong.** `run_e3_real` writes only `git_commit`, `source_manifest_hash`, `method_source_hash`, `runner_source_hash` and `dataset_hash` out of `source_identity` (`runner.py` L307-L311), so a custom key such as `allow_reused_traffic_rerun` never reaches the ledger. Item 65 (and the guard's own docstring) claimed that every exempted run records the exemption in its run ledger; that was false as written. Fixed in two places: the driver now writes `REUSE_GUARD_EXEMPTION.json` and a `reuse_guard_exemption` field in `SERVER_OPT_META.json` into every exempted run directory (15/15 traffic cells), and the guard docstring now states where the record actually lives. The guard file hash after this correction is recorded in `backup_pre_guard_change/BACKUP_MANIFEST.json`. | `src/raven_mcs/e3/real_runner/runner.py` L307-L311; `src/raven_mcs/e3/protocol_closure/reuse_guard.py`; `results_server_optimizer/round_v1/backup_pre_guard_change/BACKUP_MANIFEST.json` |
| 72 | **Two defects in this session's own driver, both found and fixed; neither changed a reported number.** (a) `run_one` created the run directory *before* calling `run_e3_real`, so a guard refusal left an empty directory that a later pass treated as a completed run and skipped - this mis-classified traffic cells as `diverged` twice before it was caught. Fixed with a completeness gate (a cell counts as done only when both `final_metrics.json` and `checkpoints/final.pt` exist) plus a `RUN_FAILED.json` marker on failure. (b) Level selection could average over fewer than the five screen seeds: on the first traffic attempt `eta_s=1e-3` was selected from a **single** surviving seed and the following test pass then crashed on a missing `final_metrics.json`. Fixed by requiring all five screen seeds to be usable for a level to be selectable (otherwise the block is reported `NO_ELIGIBLE_LEVEL`) and by tolerating a missing cell in the test pass. Both changes only tighten validity or prevent a false skip; the final traffic selection uses 5/5 seeds, and the frozen configuration's selection was identical across every pass that produced it. | driver `s1p_driver.py` (`run_complete`, `all_screen_seeds_usable`); `runs/*/RUN_FAILED.json` |
| 73 | **The E3 metric schema has no loss field at all, and the E2 schema is a different, older set.** `artifacts/e3_formal_runs_r1/runs/<block>/<arm>/final_metrics.json` carries the **same 32 keys** for `sensorscope/raven`, `uair/raven` and `traffic/raven_simoracle` (`missing_vs_SS = []`, `extra_vs_SS = []`). `artifacts/e2_traffic_formal_runs_r1/runs/<seed>/complete_aligned/fedavg_window/final_metrics.json` carries a **different 21-key** schema whose extras include `Gap_mis`, `target_risk_objective`, `empirical_risk_objective`, `active_window_count`, `completed_windows`, `P2_solver_failure_count`, `stale_update_count`, `hard_arrival_count` and `group_rmse` - none of which exists in the E3 schema. Two consequences. (i) The S1' instruction's "final training Hajek loss" is **not obtainable on any block**, not merely on traffic: this is the fourth place that instruction assumes an artifact that does not exist (after G0's traffic arms, the validation metric, and the frozen-uniformity of G0). (ii) An earlier reading in this session which described several E3 fields as "`None`" was reading **absent** keys through `dict.get` and is withdrawn; the traffic `final_metrics.json` contains no non-finite value. | key-set comparison over the four `final_metrics.json` files; `results_server_optimizer/round_v1/tables/STAGE_A_VALIDATION.csv` (`hajek_target_risk_objective` empty for every cell) |

## IX.6 Fourth-pass addition (item 74), 2026-10-08: the NSW-Traffic Stage C and the round's close

| # | correction | evidence |
|:--|:---|:---|
| 74 | **NSW-Traffic Stage C was run, and H is negative on all three blocks: the oracle-margin route is closed by measurement, not by undertraining.** With the frozen configuration (`eta_s* = 3e-3`) and both arms (the user chose to run `raven` as well, so the recorded exemption was exercised for it too), the paired-by-seed headroom is `mean_H = -0.080700`, bootstrap 95 % CI `[-0.268877, +0.017194]`, `MDE80(n = 5) = 0.349835`, `K_r <= 3` share `0.111111`, and **`kr_excluded_from_GO = False`** - so this NO-GO-H is a *measured* result, unlike SensorScope and U-Air where section 6's clause excludes the block before H is even consulted. Combined with the earlier runs: N3' is PASS on all three blocks (SensorScope 0.986505, U-Air 0.832921, NSW-Traffic 0.857589 against the frozen `central_delivered` on the same seeds), and H is negative everywhere (SensorScope -0.018749 CI `[-0.039045, +0.001548]`; U-Air **-0.163333 CI `[-0.247807, -0.059271]`, strictly negative**; NSW-Traffic as above). Two conclusions follow and should travel together: a standard server optimizer *does* make the federated learner train (parameter movement rises 7-70x over the frozen SGD step), and once it does, the oracle-margin reference `raven_simoracle` supplies **no headroom on any block** - on U-Air it is significantly *worse* than plain FedAvg. That is the measured form of the concern section 0 raised when it noted the earlier H had been measured on an untrained model. A process note in the same item: an intermediate one-shot fixer (`_r13_build/fix_artifacts_after_traffic.py`, now retired to `.superseded`) rewrote the traffic Stage C entry back to `not_run`; it was caught by re-reading `tables/STAGE_C_H.csv`, the Stage C computation was re-executed compute-only with every run skipped as complete, and the assembler now stamps `created_utc` itself so the fixer is unnecessary. No incorrect value survives in the final artifacts (`S1P_VERDICT.json`, `S1P_STAGE_C_H.json`, `tables/STAGE_C_H.csv`). | `results_server_optimizer/round_v1/{S1P_VERDICT.json,S1P_STAGE_C_H.json,tables/STAGE_C_H.csv,S1P_REPORT.md,S1P_BLOCKED.md}`; `driver/stageC_traffic.log` |

## IX.7 Fifth-pass additions (items 75-86), 2026-10-10

| # | correction | evidence |
|:--|:---|:---|
| 75 | **The Adam server-step replacement was confirmed on NSW-Traffic and the oracle-margin headroom is negative there too: `NO-GO-H`.** Fifteen paired confirm seeds (30006-30020) with all 15 pairs passing stability and 10/10 screen pairs passing: `mean_H = -0.014921178351331239`, bootstrap 95 % CI `[-0.0542302207818337, +0.0175677080705695]`, `MDE80 = 0.05802695298194278`, `K_r <= 3` share `0.15081907510478937`. Correction to the instruction that commissioned it: its planning `MDE80(n = 15) = 0.163696` was conservative, the realised value is `0.058027`. The realised detectable effect is still 3.9x the point estimate, so this null cannot police the paper's 0.5 pp bar - a limit the paper's own limitations paragraph now states (item 80). | `results_traffic_e1/round_v1/{TE1_VERDICT.json,TE1_FROZEN_CONST.json,TE1_REPORT.md,tables/TE1_CONFIRM.csv,tables/TE1_KR.csv}` |
| 76 | **A spurious `TE1_BLOCKED.md` was written by this session's own pre-run check and is retained as voided evidence rather than deleted.** The check read `ServerOptWindowRunner.SERVER_OPT` **before** `install()`, so it saw `{"mode": "off", "eta_s": None}`, compared that against the S1' frozen `SERVER_OPT_META.json` and mis-read the difference as an identity failure. The correct check installs the frozen configuration first and then compares. The file was renamed `TE1_BLOCKED.voided-selfcheck.md` so the mistake stays auditable, and no blocked file exists for the round. | `results_traffic_e1/round_v1/TE1_BLOCKED.voided-selfcheck.md` |
| 77 | **The structural readout of the same 15 confirm runs separates on both structural endpoints, and is recorded as exploratory because it was scored after the prediction contrast.** `Delta_group` mean `0.007875461474741708`, CI `[0.005050083024358629, 0.011032292876163016]`, `MDE80 0.004762`; `Delta_c-s` mean `0.009939661215117069`, CI `[0.006724524039012507, 0.013241532821026799]`, `MDE80 0.005114`; both classified `SEPARATED-ORACLE`. 14/15 pairs are positive, with seed 30012 at `-0.002650` (`Delta_group`) and seed 30006 at `-0.000867` (`Delta_c-s`) kept in the tables rather than dropped. 0/15 missing; metric applicability reports only `APPLICABLE`. **The separation is an exploratory reading, not a pre-registered positive, and it may not be moved into the abstract.** | `results_traffic_struct/round_v1/{TS1_SUMMARY.json,TS1_REPORT.md,tables/TS1_PAIRS.csv,TWO_CONSTANTS.json}` |
| 78 | **An independent reviewer's file was overwritten at the canonical path by this session, and three of this session's own readings were withdrawn.** (a) An archive step captured 16 643 B while this session's own round-14 review was 40 376 B, the size difference was not checked, and the file was overwritten. The independent review was restored to `ccfa-review-reports/raven-mcs-tmc-review.md`, this session's review moved to `-deepseek-r15.md`, and the r14 file archived under `snapshots/`. (b) Two readings were withdrawn after recomputation: "FedAdam makes the learner train, therefore the ceiling claim is strengthened" (that direction is not implied by the runs) and "federated beats centralized by 1.4-16.7 %" (the two quantities are not on the same footing). (c) A third, "on SensorScope and U-Air every arm is worse than the constant, therefore no arm has skill", was withdrawn after establishing that the constant was an oracle over the test split while the arms are train-fitted; the split means are SS train `+0.3006` / val `+2.0186` / test `+7.6572` and U-Air `0.0000` / `-0.1456` / `-0.8066`. | `snapshots/2026-10-09-grok-raven-mcs-tmc-review.md`; `ccfa-review-reports/raven-mcs-tmc-review.md`, `-deepseek-r15.md` |
| 79 | **The two constants were disclosed with names, numbers and provenance, closing the largest clarity hole in the metric definition.** The metric definition now names the **test-fitted constant** `2.088`/`0.678`/`1.007` and the **training-mean predictor** `7.647`/`1.054`/`1.007` with the ratios 3.7x/1.6x; a second edit relabels the `1.007` cell, and a third adds one reference sentence to the table caption. Provenance on record: for a weighted metric whose weights sum to one the best constant is the weighted mean and its RMSE is the weighted standard deviation, so the comparator was an **oracle over the same split the arms were fitted on**, not a trained baseline. The earlier omission of this fact is recorded, not explained away. | `results_two_constant/round_v1/{TC_GATES.md,TC_TWO_CONSTANTS.json}`; `ccfa-review-reports/raven-mcs-two-constant-disclosure-execution-prompt.md` |
| 80 | **Four honesty text repairs were applied in place; one further candidate was diagnosed and deliberately not edited; and one of the round's own justifications was corrected.** (1) The conclusion now marks the structural readout as scored after the prediction contrast, matching the limitations wording. (2) The limitations now states that the `5.80 %` detectable effect is too coarse to resolve the ceiling section's `0.5 %` bar. (3) The availability section now names the two run trees behind the Adam replacement and its structural readout, states that they are internal to this study rather than part of the released bundle, and gives the confirm seed range `30006-30020` and the two-constant file. (4) One 150-character source line was rewrapped. Gates H0-H4 all PASS: reverse-replacing all four edits recovers the pre-edit sha256 **exactly**, `main.pdf` stays **18 pages** with 0 errors, 0 undefined, 0 multiply-defined and 0 Overfull, and em dashes stay 0/3. **Not edited**: contribution 4's "the corpus is not a null" points at the U-Air component-removal ablation `tab:e4_ablation` while the limitations sentence is about the paired oracle-margin headroom on NSW-Traffic, so the two are different objects and no conflict exists. **Correction**: edit 4 was justified as restoring the file's width convention, but the file already contains 26 other lines longer than 120 characters, so it is a tidy rather than a repair. A proposed "reframe the abstract and contribution list" repair was found to have nothing to act on, because the abstract already refuses both the optimisation claim and the RMSE win. | `results_text_repairs/round_v1/{HT_GATES.md,HT_EDITS.md}`; `main.tex` `73fa475e...` -> `3cc106ca...` |
| 81 | **All four of this project's datasets were screened for the two conditions a concentrated-target projection needs, and none satisfies both.** Concentration is the test-split deployment target mass over aggregation groups; slack is the share of active windows with `K_r > 3`, where `eq:Cr` does not force uniform weights. SensorScope: top-1 `0.53 %` of 220 groups (effective 216.9), slack `24.7 %` (median `K_r` 3, max 6). U-Air: `0.79 %` of 144 (effective 143.3), slack `19.7 %` (median 2, max 5). NSW-Traffic: `0.58 %` of 172 groups = 43 stations x 4 UTC blocks, with the four-block view exactly `25 %`/`50 %`, so wholly uniform; slack `88.9 %` (median `K_r` 12, max 26). T-Drive: 4 groups with top-1 `51.4 %` and top-2 `75.0 %`, the only natively concentrated target, but it has no run tree and `load_spatial_to_client` raises for it, so it cannot be run through this pipeline. **The failure directions are complementary**: traffic alone has the slack but a uniform target, SensorScope and U-Air are non-uniform only in the four-block view and their feasible set is locked, and T-Drive is concentrated but not runnable. The project's own design plan had already proposed the remaining route - a service-weighted target with priority areas weighted twice, fixed before training. | `results_text_repairs/round_v1/BLOCK_SCREEN.json` |
| 82 | **A standard-mode dataset search for a natively concentrated target returned no candidate that met the inclusion bar.** Twelve public queries returned overwhelmingly fragmentary PDF excerpts with no stable title, author list, venue or landing page, plus off-topic hits (knowledge tracing, MNIST/CIFAR federated partitions, an unrelated UK driving-network paper). Under the search skill's source policy, snippet-only evidence and untraceable PDFs are excluded, so no scored candidate was entered and `papers.md` is empty by decision rather than omission. Six leads are recorded as **unverified** with the specific check each needs (Citi Bike described as a de-facto shared-mobility benchmark; Caltech/JPL EV-charging sessions; low-cost sensor networks against reference-grade monitors; a Northeast-China PM-sensor performance paper; an ICCT report on the spatial concentration of charging demand; an unidentified NeurIPS 2023 Datasets & Benchmarks record). Two class-level hypotheses are recorded as **inference, not search evidence**: demand-type targets are the class that concentrates, while sensor-coverage benchmarks such as Metr-LA and PEMS-BAY would concentrate no more than NSW-Traffic does. This is a search outcome, not a finding that the field lacks such datasets. | `literature-search-20261009-concentrated-target/{search-notes.md,papers.md,papers.csv}` |
| 83 | **The TE2 power gate passed, and three of its own premises needed correction.** Priority region `region1` under the pre-declared rule; `kappa = 5` gives a top-1 region share of `0.6322` against the design's analytic `0.6250`, with the concentrated weight vector sha256 recorded. Re-scoring the 20 frozen uniform-target checkpoints under the concentrated criterion gives paired `MDE80` of `0.000312`/`0.000593`/`0.000310` against the 2 % bar `0.020288`, i.e. 34-65x smaller, so the gate returns `CONTINUE`. Corrections: (a) the priority rule picked `region1` out of a **three-way tie** (`region1/2/3` all `0.255814` at `kappa = 1`), so an explicit tie-break had to be added to the pre-registration; (b) the design's `effective groups` diagnostic was at the **wrong level** - multiplying whole regions by a constant leaves the group masses uniform inside each region, so the group-level count stays near 126 of 172 and measures nothing, while the region-level share is what this treatment actually moves; (c) the measured paired sd is a **lower bound**, because those checkpoints were trained under the uniform target, and no arm separated with the no-P2 control nominally best - which is exactly why the treatment had to be a training run rather than a re-scoring. | `results_traffic_e2/round_v1/{TE2_PHASE0.json,TE2_PHASE0_REPORT.md}` |
| 84 | **TE2 step 3 ran the primary cell under an injected concentrated target: the pre-registered claim is not supported, and the reason is the class rather than the projection.** 80 cells (`local_hajek`, `inst_cal`, `debt_cal`, `raven_simoracle` x 20 seeds) at `kappa = 5`, frozen server step, target injected through `run_e3_real(target_artifact=...)`, which needs no `src/` edit because `FROZEN_TARGET_ARTIFACTS` contains only `sensorscope` and `uair`. Paired against the control: `inst_cal` `+0.000149` (+0.015 %), `debt_cal` `+0.000388` (+0.038 %), **oracle ceiling `+0.000228` (+0.0225 %)**, against the 2 % bar `0.020288`; no arm separated, and `debt_cal`'s interval excludes zero while its mean stays below its own `MDE80`, which is precisely what the two-condition rule exists for. Two readings travel with the negative: the contrast **sign flipped positive** versus Phase 0, whose three treatment contrasts were all negative, so training for the concentrated target does move the criterion the right way; and the paired sd came out `0.000442`/`0.000846`, essentially Phase 0's lower bound, so the warning that training would widen it **did not materialise**. Feasible-set slack is preserved at a mean `K_r <= 3` share of `0.1478`. Critically the **oracle ceiling is itself only +0.0225 %**, so the projection already reached the order of the whole class's available room. | `results_traffic_e2/round_v1/{TE2_FROZEN_PREREG.json,TE2_VERDICT.json,TE2_REPORT.md,TE2_TARGET_ARTIFACT_KAPPA5.json,tables/TE2_MAIN.csv}` |
| 85 | **The ceiling ladder closes the concentrated-target route by measurement: the weight class cannot buy even 0.1 % of the deployment-weighted error at the most extreme concentration that exists.** Two arms (control and oracle) at `kappa = 10` and at the single-region limit, 20 seeds, 80 cells, with the **exact** single-region target realised (top-1 share `1.0000`, the other three regions exactly zero; the smoke cell ran finite at `RMSE_mu 1.017231579646864`, so the planned `kappa = 100` fallback was not needed). Oracle gap by rung: `kappa = 1` (frozen runs) `+0.000013` (+0.0013 %, interval contains zero, not separated); `kappa = 5` `+0.000228` (+0.0225 %); `kappa = 10` `+0.000462` (+0.0454 %); **single-region `+0.000994` (+0.0970 %, CI `[+0.00068, +0.00134]`, separated)**. The gap is **monotone in concentration**, about 75x from `kappa = 1` to the limit, and separated at `kappa >= 5`, so concentration does create statistically detectable room as the design hypothesised. But the magnitude at the physical extreme is still **20x below the 2 % bar**, and concentration cannot exceed the single-region limit, so the ladder has no further rung: **the lever is exhausted**. The bottleneck is the ceiling rather than the projection, since at `kappa = 5` the projection arms already reached `+0.015 %`/`+0.038 %` against a ceiling of `+0.0225 %`. This is the strongest negative the project holds on the deployment-headroom question, and it is on the only block that has feasible-set slack. | `results_traffic_e2/round_v1/{TE2_STEP4_VERDICT.json,tables/TE2_STEP4_MAIN.csv}` |
| 86 | **Five defects and deviations in this round, recorded rather than smoothed over.** (a) `tables/` was not created before the post-processing write, so the step-3 job crashed **after** all 80 runs had completed; only the post-processing was re-run, no cell was retrained, and a preliminary read of the completed cells gives test `RMSE_mu` values identical to the final ones. (b) The runner hard-codes `_artifact_path = "inline_fixture_freeze"` and overwrites any caller-supplied label, so the label is not a discriminator and the recorded digest is. (c) Two digests exist for the same content - the runner's own `sha256_json({mu, head_groups, tail_groups, n_groups})`, written into every run's config snapshot (`fbade3683aaf3e72...`), and the artifact file's own field produced with a different serialisation (`f34e5b9403036cd6...`); the runner's is the anchor. (d) `align_mu_to_dataset` requires the artifact's `mu` to be a **dict keyed by group id**, not a list; the first attempt supplied a list and raised. (e) The injection path works on traffic only because traffic is absent from `FROZEN_TARGET_ARTIFACTS`; on SensorScope or U-Air the frozen file wins and the same experiment would need a different route. None of these altered a reported number. | `results_traffic_e2/round_v1/driver/{te2_round.py,te2_step4.py,te2_stderr.log}` |

## IX.8 Sixth-pass additions (items 87-88), 2026-10-10: the ceiling-ladder writing round

| # | correction | evidence |
|:--|:---|:---|
| 87 | **The ceiling ladder was written into the manuscript, and the round is blocked by its own page gate rather than by any content problem; the manuscript was never left over budget.** The plan (`ccfa-review-reports/raven-mcs-ceiling-ladder-manuscript-execution-prompt.md`) specified four insertions and a hard 18 pp allowance. Applied in place, they total +1879 B and build to **19 pages**, so W2 failed and section 7's blocked path ran: the file was restored byte-for-byte to `3cc106ca4b6087d9...`, 119922 B, 18 pp, and `CW_BLOCKED.md` was written instead of a workaround. W0, W1, W3, W4 and W5 all pass: all four anchors matched once; reversing the insertions recovers the pre-edit sha256 exactly with the CRLF count unchanged; prose stays at em dashes 0/3 with none of the banned defensive phrases; twelve of twelve printed numbers recompute from the artifacts; and the title, abstract and contribution-list regions are byte-identical, which is what proves the change did not drift into a scope repositioning. Marginal page cost, one build per variant with the same command sequence: pre-edit control 18, ceiling paragraph alone (`+1227` B) **18**, ceiling paragraph plus availability naming (`+1407` B) **18**, all four (`+1879` B) **19**. The substance therefore fits and the overflow is caused by the two cross-reference sentences, about 440 B between them. Three options are recorded unapplied: apply the measured-fit scope (the ceiling paragraph plus the availability naming) and drop the two cross-references; or keep all four and compress the ceiling paragraph by about four lines; or keep all four and have the author name a cut elsewhere. | `results_paper_ceiling/round_v1/{CW_GATES.md,CW_BLOCKED.md,CW_NUMBERS.json}`; `_r13_build/{cw_apply.py,cw_one.py,cw_outputs.py}`; `main.tex` `3cc106ca...` -> `f55e49fd...` (variant, not applied) |
| 88 | **W4 caught a real wrong number before any manuscript write survived, and this round also produced a process defect of its own.** (a) The frozen rung's top-region share had been written as `0.2500`, which is the design-stage analytic value for four equal regions. The measured frozen target gives region0 `0.232558` and regions 1-3 `0.255814`, so the share is **`0.2558`**; the number was wrong in the plan, in the insertion text and in the design file's analytic table, and only the design table was labelled as analytic. It was corrected in both copies of the insertion text and W4 now sources it from `TE2_PHASE0.json`, so no incorrect value reached the canonical file. This is the first time a gate in this project caught an error before publication rather than after. (b) A triage script imported `cw_apply.py` to reuse its constants, which re-executed the whole module and applied edit 1 to an already-edited file before failing on edit 2. No damage occurred, because the assertions precede the write, and the lesson is recorded: scratch scripts that write the manuscript must guard their side effects behind a `__main__` check or expose constants from a side-effect-free module. (c) A separate triage used Python `subprocess` to drive pdflatex with `capture_output=True`; every build returned a sentinel because the failure was swallowed, so the measurement was redone from the shell, where the same builds succeed. | `results_paper_ceiling/round_v1/CW_NUMBERS.json` (`correction_caught_by_this_gate`); `_r13_build/cw_fix_share.py`; `results_traffic_e2/round_v1/TE2_PHASE0.json` |

