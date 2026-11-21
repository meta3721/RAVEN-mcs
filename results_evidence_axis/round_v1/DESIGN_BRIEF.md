# Evidence axis — design brief (reconnaissance complete; corrected)

Round: `results_evidence_axis/round_v1/`
Basis: `EVIDENCE_BASE.md` (measured 2026-10-06, with the §1a/§2/§3/§6b corrections).
**No protocol written, no training run.** Manuscript untouched (`main.tex 02447bfe…`).

## Reconnaissance result, corrected

* The deployment targets on SensorScope and U-Air are effectively uniform (top-1 group
  0.53 % / 0.79 %; 1 − H/H_max 0.0027 / 0.0010).
* With the checkpoint fixed and only the **evaluation** weights changed, `RMSE_μ` and the
  uniform-weighted RMSE differ by 0.82 % (SS) / 0.26 % (UA). This is an evaluation-layer
  statement: it does not bound what reweighting during training could do to the per-group
  errors, and the earlier brief's use of it as such a bound is withdrawn.
* The designs are not blind: the audited paired MDE is 0.42–0.45 % (SS) and 0.08–0.09 % (UA)
  (`A1_POWER.csv` `mde80`, audit `EV-2`/`EV-3`), and the measured member spread is 0.026 pp
  (SS) / 0.357 pp (UA) across the six rules. **The right reading is "the design can see an
  effect of this size and the effect is absent."**
* A window's contributing clients reach 0.67 % (SS) / 0.89 % (UA) of the target-positive
  mass, and the frozen traces vary that by only ±0.04 pp; the client population's repertoire
  covers 100 % of the target mass, so a regenerated-trace design could dose exposure from
  ≈0 to 100 %.
* The Design factor moves `RMSE_μ` by 6.875 % and `Δ_c-s` by 3–5 %, and it changes the
  **participating set** as well as the weights (`round_v3`). Which of those two carries the
  6.9 % is **not identified** by anything on disk. Design is the alignment factor; calling
  that movement "composition" was a relabel and is withdrawn.

## What that implies

* **Option B is not a repair.** Dosing reachability varies the same factor (support/design)
  and, per the above, it would measure the Design factor's dose response — a legitimate
  experiment, but not "alignment buys accuracy".
* **The Evidence-axis result the measurements support is the measured null plus its
  resolution**, with §6b's identification question left explicitly open.
* The paper's 6.885 % / 4.990 % ablation numbers remain valid and are the strongest
  structural statements the design owns.

## Option C, corrected and recommended

**C1 — the measured null with its resolution (no training).** Proposed text and number ledger:
`WRITING_PROPOSAL.md`. Contents: the six-rule member spread on both blocks; the audited MDE;
the two pre-outcome overlap statistics (target top-group share; window R_mass); and the
explicit statement that no alignment-improves-prediction claim is made.

**C2 (optional addendum) — the identification experiment that §6b leaves open.** If the
Evidence axis is to carry a *positive* statement, the one open question is whether the 6.9 %
comes from the participating set or from the weights. That is testable: hold the weights at a
declared rule and vary which client–windows enter (or vice versa) on the frozen traces. It is
a real intervention, it needs pre-registration and training authorization, and it is the only
route to a claim beyond the null. Not started.

## Option A, restated (no longer described as an expected null)

Re-run the gate-dose protocol with an internally consistent reference (fresh m = 0 in the
same tree; masks unchanged, content hashes `masks 6b456bd3…`, `wiring b9de9d9b…`). 168 runs,
≈50 min. **Corrected expectation:** this is *not* expected to be zero. The two arms differ in
support as well as weights, and the evaluation-layer statement of §2 does not bound a
support/dose manipulation. A non-zero dose response is plausible, and if it appears it
licenses exactly one claim — "a pre-outcome structural statistic (ρ) predicts the accuracy
cost of the Design factor, with a measured slope and interval on these two blocks" — and
**not** "alignment improves prediction". It remains the stopped round's open item and is
worth running for that claim if the paper wants it.

## Recommendation

1. **Do C1 now** (writing authorization only): it is the only Evidence-axis statement the
   measurements support, and it also removes the wrong MDE scale from that paragraph.
2. Decide separately whether to pursue **C2** (identification: set versus weights) — that is
   the only route to a positive Evidence claim, and it needs its own pre-registration.
3. Treat **A** as a candidate for a *different*, narrower claim (ρ predicts the Design cost),
   not as a repair of E1.

## What is needed from the user

1. Approve C1 as the Evidence-axis text (`WRITING_PROPOSAL.md`).
2. Decide on `EV-2`: the proposal quotes the audited MDE, which means the ceiling sentence's
   current 0.17–0.36 pp / 0.70–0.80 pp also needs fixing in the same pass (audit's wording:
   "0.17–0.36 pp, against a 0.42–0.45 pp paired MDE"). Confirm scope, or I will cite the
   manuscript's current numbers and leave `EV-2` open.
3. Say whether C2 or A should be designed next; either needs a pre-registration and an
   explicit training authorization.
