# Independent critical review — S1' server-optimizer evidence vs. the manuscript's negative claim

Scope: `TO_OVERLEAF_paper_tmc_r1_clean/main.tex`, sha256
`D4FB164DF90F59484BFE901B117399536CD727F4CB01FCA6A3E09CB902486E60`, 116806 B (verified).
Evidence: `results_server_optimizer/round_v1/` and the frozen artifacts it cites.
Read-only throughout; the only file written is this report.

Every number below was recomputed from primary artifacts in this workspace unless marked
"not verifiable here".

---

## 1. The paper's central negative claims, in the paper's own words

**N1 — measured ceiling, inside a stated class (the primary negative claim).**
> "The recoverable gain is bounded inside the class the method defines: weights in
> $\mathcal{C}_r$ of \eqref{eq:Cr}, selected by (P2), scored by the deployment-target
> criterion $\mathrm{RMSE}_{\mu}$." — L2110–2112
> "The GO rule, frozen before the runs, required some condition to reach $H\ge0.5\%$ with a
> positive interval lower bound, and it did not fire." — L2117–2119
> "...so the gap is a property of these endpoints rather than of an over-easy regime." — L2127–2128

**N2 — no surviving prediction-endpoint contrast (the twin claim, same section).**
> "No prediction-endpoint contrast survives Holm correction on either dataset
> (SensorScope $p_{\mathrm{Holm}}=1.000$ throughout; U-Air best raw $p=0.027$,
> $p_{\mathrm{Holm}}=0.133$), and the arm order on $\mathrm{RMSE}_{\mu}$ does not follow the
> structural order, which is what the ceiling measurement of Section~\ref{subsec:ceiling}
> anticipates." — L2100–2105

**N3 — the mechanism attributed to the weighting.**
> "Accurate margin estimates are therefore not what holds the prediction endpoint flat, since
> three of the four members are insensitive to a large change in their own aggregation
> weights." — L2142–2144
> "\noindent\textbf{Why the weights leave the prediction endpoint flat.} On SensorScope and
> U-Air the feasible set leaves (P2) little to choose." — L2152–2153

**N4 — the newly added cause (lines 2213–2221), the sentence under review.**
> "FedAvg stays $2.8\%$--$3.0\%$ above a centralized model trained on the same delivered data.
> The server applies $\eta$ times the step-normalized client update once per window, so the
> global step equals one gradient step whatever the local budget, and raising that budget from
> $2$ to $20$ steps leaves the gap unchanged. Over the run the federated parameters move
> $0.26\%$--$0.40\%$ of their initial norm on all three blocks, mostly through the output bias,
> while on SensorScope the centralized reference, trained with Adam, moves its first layer by
> $12\%$. The federated learner, not the weighting, therefore limits the prediction endpoint."

**Supporting code facts I verified (not claims, but the load-bearing mechanism):**
- `src/raven_mcs/training/client.py` L87–L107: local SGD with `p -= lr * p.grad`, then
  `update = (theta_before - theta_after) / (learning_rate * local_steps)`. So the normalized
  update is the *mean* local gradient and `E_loc` cancels exactly.
- `src/raven_mcs/training/window_runner.py` L128–L132: `eta = 0.01`, `learning_rate = 0.01`,
  `local_steps = 5`, banked as "a conservative fixed server step".
- `src/raven_mcs/e3/real_runner/central_real.py` L106: `opt = torch.optim.Adam(model.parameters(), lr=lr)`.
- `main.tex` L993–L1002 (eq. `server_update`) prints `theta_{r+1} = theta_r - eta_r sum_k alpha u_k`;
  `E_loc` never appears in it. The "one gradient step whatever the local budget" statement is
  therefore an algebraic identity of the printed model, not a measurement.

---

## 2. Does the new evidence contradict a printed claim, or re-contextualise it?

### 2.1 What the new evidence actually establishes (verified)

**(a) The movement facts are correct and reproduce.** `PREFLIGHT_SECTION0.json`
(84 records, seeds 30001–30003) reconstructs `theta_init = deterministic_common_ndmf(n_spatial, seed=run_seed)`
and reports, per seed 30001:
`fedavg_window` 0.2619 % (SS), 0.4269 % (UA); `raven` 0.2692 % / 0.4015 %;
`local_hajek` 0.2619 % / 0.4269 %; traffic `local_hajek` 0.3667 %. Top mover is `head.8.bias` at
41–62 % of squared movement. `spatial.weight` moves 0.0050–0.0088 %. SensorScope `central_all`
moves `head.0.weight` by 12.1524 %. **The manuscript's L2217–2220 sentence is factually exact.**
I independently re-derived these from the checkpoints with a fresh implementation and got
0.02157/0.02791 (η=1e-3), 0.05392/0.06822 (η=3e-3), 0.17811/0.20124 (η=1e-2) on SS/UA seed 30001,
matching `tables/MOVEMENT.csv` to 5 d.p.

**(b) The optimizer swap moves the model 7–70× more.** `tables/MOVEMENT.csv`: 2.491–2.802 %
(η=1e-3), 5.392–9.340 % (3e-3), 17.14–23.17 % (1e-2), against 0.26–0.43 % frozen. Verified.

**(c) The centralized reference is barely trained.** `PREFLIGHT_SECTION0.json`:
`central_all`/`central_delivered` move only 2.31–3.33 % of their *total* norm; the 12 % figure is
one tensor. This is a fact the manuscript does not state and it materially weakens the sentence it
is used to support.

**(d) Headroom H flips sign once the learner trains.** `S1P_STAGE_C_H.json` +
`tables/STAGE_C_H.csv`: mean H = −0.0187 (SS, CI [−0.0390, +0.0015]), −0.1633 (UA, CI
[−0.2478, −0.0593]), −0.0807 (Traffic, CI [−0.2689, +0.0172]); NO-GO-H on all three blocks.
Represented as paired test-RMSE differences in the same file:
SS oracle 7.990282 − fedavg 7.845273 = −1.848 % (oracle *worse*);
UA 1.135215 − 0.977494 = −13.89 %; Traffic 0.896929 − 0.835094 = −6.90 %.
**The manuscript's own interpretation of the ceiling inverts here.**

### 2.2 What I could NOT verify, and one artifact defect

**Defect (isolated, not fatal).** `tables/STAGE_A_GRID.csv` carries the *selected-η* test value in
the `test_*` columns of *all three* η rows for a given (block, seed). `driver/s1p_driver.py`
L724–L742 builds `test_rows` at the selected η only and then merges on
`r["block"] == t["block"] and r["seed"] == t["seed"]` — η is not part of the key. Reproduced:

| block | η | CSV `test_RMSE_mu` | run-dir `final_metrics.json` |
|---|---|---|---|
| sensorscope | 0.001 / 0.003 / 0.01 | 7.845273 / 7.845273 / 7.845273 | 7.870630 / 7.891182 / **7.845273** |
| uair | 0.001 / 0.003 / 0.01 | 0.977494 ×3 | 1.095797 / **0.977494** / 1.033618 |
| traffic | 0.001 / 0.003 / 0.01 | 0.835094 ×3 | 0.874426 / **0.835094** / 0.915626 |

The value is right for the *selected* η (0.01 / 0.003 / 0.003), so **N3′ is not fabricated and the
endpoints are supported by the run directories**; but the CSV silently makes the test endpoint look
η-invariant. Consequence: the tables cannot be used as evidence about endpoint sensitivity to the
server step, and any reader reproducing "all three blocks PASS" from the table alone gets the right
verdict for the wrong reason.

**Unverifiable / weakened points.**
- The "raising that budget from 2 to 20 steps leaves the gap unchanged" experiment is *not* in
  `round_v1/`. Its source is `results_new_block_traffic/round_v1/S1_LADDER.csv`
  (local_steps 2/5/10/20, ratio-to-c 1.02962/1.02814/1.02780/1.02911, mean RMSE 1.0066/1.0052/1.0049/1.0061)
  — and it was run **only on NSW-Traffic**, three seeds (30001–30003), with the 2-step rung *read*
  from sealed E2, not trained. The manuscript sentence is a mechanism sentence, true by algebra
  (client.py L100–L107), so the missing arm is not a contradiction; but as *evidence* it is one
  block, n=3.
- Stage C's H is not the paper's H. The paper defines H against "the best member evaluated on true
  margins" (L2113–L2115); the round computes it against the `raven_simoracle` arm. That is a
  different, weaker quantity, and the round's own report (deviation 7, non-like-for-like optimizer
  comparison) says so.
- The U-Air `fedavg_window` frozen baseline does not reproduce in this tree:
  `S1P_GATES.md` L44–L55 shows `RMSE_mu` 1.210848 → 1.171263 (−3.27 %), active windows 66 → 74.
  This is a real reproducibility miss on a Table II baseline arm.

### 2.3 Per-question answers

**(i) Is "the prediction endpoint is flat / no recoverable gain" a property of the method class or
of the frozen training pipeline?**
Of the frozen pipeline, and the new evidence demonstrates that cleanly. All three surfaces move
together: parameter movement 0.26–0.43 % → 2.5–23 %; test RMSE on UA 1.159925 → 0.977494 and on
Traffic → 0.835094 (both land **below** the centralized comparator the same verdict file uses,
c = 1.173574 and 0.973769 respectively — the Traffic comparison is cross-runner, E2 reference
≈1.0066); oracle-margin headroom from +0.11 %/+0.23 % to −1.85 %/−13.89 %. It does **not**
contradict N1 as printed, because N1 is explicitly scoped
("inside the class the method defines", L2110) and the class is the frozen learner plus a weight
rule. It *does* contradict the unrestricted reading that L2127–2128 ("a property of these
endpoints rather than of an over-easy regime") invites, and it directly contradicts the new
sentence's causal conclusion.
**Verdict: re-contextualisation of N1/N2 as scoped; contradiction of N4 as written.**

Relative to the frozen federated arms on the same seeds, the FedAdam endpoint changes are
−0.80 % (SS: 7.908942 → 7.845273), −15.73 % (UA: 1.159925 → 0.977494), and, against the E2
reference the 2→20 ladder itself uses (c = 0.977673), −14.58 % on NSW-Traffic (1.006631 → 0.835094,
a different runner — `S1_LADDER.csv` vs `S1P_STAGE_A_VERDICT.json`).

**(ii) Is the centralized comparison a fair federation comparison?**
No, and the manuscript now admits the decisive asymmetry inside the same sentence while still
drawing the federation conclusion from it. `central_real.py` L106 trains the reference with Adam;
the federated arms use normalized-SGD with a fixed `eta = 0.01` server step
(`window_runner.py` L128–L132). The paper's strongest evidence for "the learner limits the
endpoint" is therefore a contrast between *optimizers*, not between *federation and centralization*.
Worse, the reference is itself barely trained (2.4–3.2 % total movement,
`PREFLIGHT_SECTION0.json`), so "FedAvg stays 2.8 %–3.0 % above a centralized model" is a gap to a
weakly-trained comparator. And the manipulation actually run — replacing only the server step with
FedAdam — *reverses* the gap on U-Air and NSW-Traffic vs the frozen federated arm, so the sentence's
own disclosed manipulation refutes its conclusion. The L1568 statement ("Central-All,
Central-Delivered, and RAVEN-SimOracle are reference-only methods") does not repair this: a
reference-only label does not license a causal claim drawn from it.

**(iii) Does "the federated learner, not the weighting, therefore limits the prediction endpoint"
follow?**
No. The sentence's own evidence base is two contrasts: (a) local budget 2→20 changes the gap by
0.18 % (frozen pipeline, NSW-Traffic only, n=3); (b) the centralized reference uses Adam while the
federated arm does not. (a) is an algebraic identity of the normalization (client.py L104–L107). (b)
is exactly the confound, and it is a *disclosed* confound. "The weighting does not limit the
endpoint" is supportable from (a) plus the S1' mechanism paragraph. "The federated learner limits
the endpoint" is not: it requires holding the optimizer fixed, which the evidence does the opposite
of. In the same measurement design, changing only the server step took UA from 1.15992 to 0.97749,
so the demonstrated limiter is the *server step*, i.e. an optimizer/steps-size choice inside the
federated learner rather than "the federated learner". The inference is a non sequitur of the
affirming-the-consequent form: the budget ladder rules out one budget, and the optimizer contrast
shows the fix lies in the optimizer — which the sentence attributes to the opposite cause.

---

## 3. Is the headline negative result still defensible in weakened form?

**Strongest defensible version (the one I would sign):**
"Inside the frozen configuration — weights in $\mathcal{C}_r$ chosen by (P2), scored by
$\mathrm{RMSE}_\mu$, with the server step $\eta=0.01$ applied to a step-normalized client update —
the recoverable prediction gain is not measurable on SensorScope or U-Air (all estimates inside
$[-0.03\%,+0.08\%]$), the observed re-weightings do not move $\mathrm{RMSE}_\mu$, and the
oracle-margin ceiling is not positive. Local budget is not the binding resource: because the client
update is divided by $\gamma_r E_{\mathrm{loc}}$ (client.py L104–L107), the window move is one
gradient step at any budget, and a 2→20 ladder confirms the gap is unchanged. This ceiling is a
property of the frozen training pipeline and is conditional on its server step; a different server
optimizer is a different learner and is outside the measured class."

That version is true, is supported by artifacts in this workspace, and preserves the paper's
contribution: the endpoint ceiling is real *for the rule family the paper compares*.

**Strongest indefensible version (what the current text asserts):**
"...Over the run the federated parameters move 0.26 %–0.40 % of their initial norm ... while on
SensorScope the centralized reference, trained with Adam, moves its first layer by 12 %. The
federated learner, not the weighting, therefore limits the prediction endpoint." (L2217–2221)
This asserts a general cause (the federated learner) from a contrast whose only manipulated
variable is the optimizer (Adam vs normalized SGD at η = 0.01), on a reference the same paragraph
reveals to be barely trained, and it generalises beyond the class the ceiling section scopes itself
to at L2110.

**Which the current text asserts:** It asserts the indefensible version at L2220–2221, and the
defensible version at L2110–2128. The manuscript therefore now contains both, three hundred lines
apart, with no boundary drawn between them. That internal inconsistency is the most serious
finding of this review after the disconfirmed causal inference itself.

---

## 4. Dimension ranking

Ordered by how much the new evidence moves them: Soundness > Significance > Evidence > Clarity >
Reproducibility.

| Dimension | Score | One-line deduction | Concrete repair condition |
|---|---|---|---|
| **Soundness** | **2** (was 4) | L2220–2221 infers a learner-level cause from an optimizer-only contrast that its own disclosed Adam/η=0.01 asymmetry produces, and contradicts the scoped L2110 framing; the reference it compares against moves only 2.4–3.2 % of its norm. | Retrain the centralized reference under the *same* server rule and report a second federated arm under Adam; if the endpoint then moves for both, the ceiling is a pipeline statement. Either way, restate L2220–2221 as a pipeline/steps-size statement unless an optimizer-matched control replicates it. |
| **Significance** | **3** (was 4) | The headline "no recoverable gain in this rule class" survives, but the *managerial* reading ("the federated learner limits the endpoint") is disconfirmed, so the negative result narrows from a finding about windowed FL to a finding about one frozen pipeline. Gains remain real: the R↔O↔U structural contribution of L1775–1860 is untouched. | Add the optimizer-matched control; if the endpoint moves, reframe the ceiling as "the frozen server step, not the aggregation weights, held the endpoint flat" and re-state the contribution at that scope. Score returns to 4 if the paper says this explicitly. |
| **Evidence** | **4** (was 4) | The new movement/H/endpoint facts are reproducible from primary artifacts and I reproduced them independently; the deduction is for the η-insensitive `STAGE_A_GRID.csv` `test_*` columns (driver merge key omits η) and for a single-block, n=3 budget ladder whose 2-step rung was read, not trained. | Fix the Stage A merge to key on (block, seed, η); re-run the 2→20 ladder on SensorScope and U-Air at n≥5, or strike "on all three blocks"-adjacent generalisations. Score returns to 5 with the ladder replicated and the CSV corrected. |
| **Clarity** | **3** (was 4) | The new sentence prints the confounding variable ("trained with Adam") and then draws the opposite conclusion from it; "overall parameter movement", "% of initial norm" and "% of first layer movement" are used interchangeably; the new sentence lives in a *Limitations* paragraph that never names the optimizer, and "local budget" vs "server step" are not distinguished. | State the two knobs separately and decode the metric ("‖Δθ‖₂/‖θ₀‖₂"); move the ceiling's scope boundary next to L2221, or cut the inference clause and keep the measurement. |
| **Reproducibility** | **4** (was 4) | Primary run directories, `MOVEMENT.csv`, `PREFLIGHT_SECTION0.json` and `S1P_STAGE_C_H.json` re-derive the reported quantities; deductions are the CSV merge defect, the U-Air baseline reproduction miss (−3.27 %, `S1P_GATES.md` L44–L55) and the fact that the "N3′ PASS on all three blocks" verdict is traceable through a table whose `test_*` columns are copied across η (the value is correct for the selected η, but the table cannot show it). | Correct the merge key, log the U-Air divergence as a Table II caveat, and carry the reuse-guard exemption and the sourced-not-trained ladder rung into the artifact the paper cites. |

No dimension is fatal: the structural contribution and the measured ceiling *as scoped* remain
sound. The damage is concentrated in one inference sentence and in the scope boundary it crosses.

---

## 5. Exposed claims (abstract / introduction / conclusion / affected body text)

| # | Location | Exact sentence | Why exposed | Fix |
|---|---|---|---|---|
| E1 | L2220–2221 (Limitations) | "The federated learner, not the weighting, therefore limits the prediction endpoint." | Contradicted by the round's own FedAdam comparison, which changes only the optimizer and does change the endpoint (UA 1.15992→0.97749; Traffic→0.83509 vs E2 c≈1.0066). | Delete the causal clause, or condition it: "the frozen server step, not the aggregation weights, limits the endpoint in this pipeline." |
| E2 | L2213–2216 | "FedAvg stays $2.8\%$--$3.0\%$ above a centralized model trained on the same delivered data. The server applies $\eta$ times the step-normalized client update once per window, so the global step equals one gradient step whatever the local budget, and raising that budget from $2$ to $20$ steps leaves the gap unchanged." | The gap is to a comparator on a different optimizer; the ladder is NSW-Traffic only, n=3, and its 2-step rung was read from sealed E2 (`S1_LADDER.csv` `local_steps_source`), not trained. | Scope to NSW-Traffic with n and source stated; add the optimizer-matched comparator. |
| E3 | L2217–2220 | "Over the run the federated parameters move $0.26\%$--$0.40\%$ of their initial norm on all three blocks, mostly through the output bias, while on SensorScope the centralized reference, trained with Adam, moves its first layer by $12\%$." | Factually correct (verified), but it presents the confound as context and suppresses the companion fact that the reference moves only 2.4–3.2 % of its total norm, i.e. it is itself barely trained. | Add the total-norm figure and the Adam disclosure in the same breath; the reader currently cannot see the confound. |
| E4 | L2127–2128 | "Hardening the observation propensity to vary within a stratum and correlate with the label raises the oracle gap by $15$--$21\times$, to $0.104\%$ on SensorScope and $0.251\%$ on U-Air, both inside the same bound, so the gap is a property of these endpoints rather than of an over-easy regime." | "a property of these endpoints" is now known to be conditional on the frozen server step; under FedAdam the UA headroom is −13.89 %, not "inside the same bound". | Insert "at this server step" and cross-reference the FedAdam sensitivity, or state the condition in the ceiling's own scope sentence (L2110). |
| E5 | L2142–2144 and L2152 | "Accurate margin estimates are therefore not what holds the prediction endpoint flat..." / "\textbf{Why the weights leave the prediction endpoint flat.}" | Not contradicted — S1' re-confirms that re-weighting alone does not move the endpoint — but "holds ... flat" now reads as a learner-level cause rather than a pipeline-level one. | Retitle/rephrase to "why the weights cannot move the prediction endpoint in this configuration"; the mechanism paragraph (L2153–2167, K_r≤3 share 0.753/0.662) is correct and should stay. |
| E6 | L2100–2105 | "No prediction-endpoint contrast survives Holm correction on either dataset ... and the arm order on $\mathrm{RMSE}_{\mu}$ does not follow the structural order, which is what the ceiling measurement of Section~\ref{subsec:ceiling} anticipates." | Still true of the six *weight rules* compared there (all frozen-optimizer). Exposed only if read as a statement about the method class. | Append "at the frozen server step; the server step is a separate axis and is not varied here." |
| E7 | Abstract L77–79 | "It does not prove that deployment-target risk is optimized." | Correct and now *better* supported; no change needed. Listed because it is the abstract claim a hostile reviewer will pair with E1. | None. |
| E8 | Abstract L81–84 | "Against uniform server weights, the structural gain that remains is the projection of that corrected reference onto the feasible set. On SensorScope the projection is worth $+0.768$ percentage points of group mismatch over uniform weights..." | Untouched by S1' (group endpoint, frozen pipeline, verified mapping to L1833–1834). Keep. | None. |
| E9 | Contributions L229–239 | "...on the prediction half (Section~\ref{subsec:eval_rq3}) the corpus is not a null, and the reading it carries is the small Inst entry of Table~\ref{tab:e4_ablation}." | "not a null" is scoped to the ablation corpus and remains true; but it is the only positive prediction-side claim and will be read against E1. | Add "at the frozen server step". |
| E10 | Conclusion L2238–2241 | "On the protocol development table, the FedAvg structural gap is mostly closed by uniform server weights, and the surviving part requires the reconstructed reference projected onto the feasible set." | The *attribution* ("the surviving part requires the reconstructed reference") competes with the now-live alternative explanation that the federated optimizer is the binding constraint. If FedAdam alone closes the FedAvg structural gap, this sentence's attribution is undermined. | I could **not** verify this from `round_v1/` — `STAGE_A_GRID.csv` does contain `test_Delta_group` per seed, but those columns carry the η-merge defect, so I will not draw a conclusion from them. Either recompute Δ_group from the corrected per-η run directories and report it, or add a caveat until it is recomputed. |
| E11 | Conclusion L2244–2246 | "...usable-update correction has no isolated effect in the tested family; target debt remains internal accounting; and no ranking jointly measures $R$, $O$, and $U$." | True as printed, and the strongest part of the paper. The word "tested family" is doing the same scoping work that L2221 overruns. | None required; consider using the same phrasing at L2221. |

Note on the abstract: the abstract does not itself assert the flat-endpoint causal claim. Its
exposure is indirect — it promises a measurement paper, and E1 is the one sentence where the
measurement is over-read. The conclusion's L2244–2246 already models the correct hedge
("in the tested family"); E1 should adopt it.

---

## 6. What would change my mind

I would withdraw this criticism — and score Soundness back to 4 — if any of the following holds.

1. **An optimizer-matched control.** A centralized reference trained with the *same* normalized-SGD
   `eta = 0.01` server rule (or federated arms trained with Adam) shows the gap unchanged at
   2.8–3.0 % and the endpoint flat. That would make "the federated learner" the right noun. The
   round explicitly says this control was not run (`S1P_REPORT.md` deviation 7) and that it is
   "outside this round".
2. **A two-factor design.** Server optimizer × aggregation rule at fixed data, model, weights,
   scenario and seeds, with the *weighting* effect measured under Adam. If the weighting still does
   not move $\mathrm{RMSE}_\mu$ while the optimizer does, the paper's negative claim becomes stronger
   than it is today, not weaker.
3. **Evidence that the FedAdam gains are an artifact.** The FedAdam arms at η=3e-3/1e-2 produce
   non-monotone test endpoints (`STAGE_A_GRID.csv`: UA 1.0958/0.9775/1.0336; SS 7.8706/7.8912/7.8453
   from the run directories) and only 5 screen seeds, with no paired significance test against the
   frozen arms. A paired test showing the −15.7 % (UA) and −17 % (Traffic, cross-runner) changes are
   inside seed noise would restore the flat-endpoint reading. I judge this unlikely: the UA change is
   ~15 % against a paired spread of ~2 %, and the traffic ladder's own seed spread is 0.3–0.6 %.
4. **A corrected H computation.** If the paper's own H (best member on true margins, per L2113–2115)
   computed under FedAdam is still ≈0 or positive, then the "no recoverable gain" claim survives the
   optimizer change and only E1 falls. S1' measures a different oracle (`raven_simoracle`), so this
   question is open on the evidence in this workspace. This is the single experiment I would ask for
   first, because it is cheap and it decides whether the ceiling survives at all.
5. **A correction of the Stage A merge** that shows the `test_*` columns I flagged are in fact
   η-keyed in a later artifact than the one in this workspace. I verified the defect against
   `driver/s1p_driver.py` sha256 `308007730989dafc…` (matching `S1P_REPORT.md` L4) and the run
   directories; a newer driver plus regenerated tables would settle it.

What would *not* change my mind: further restatements that the server step was frozen by design.
It was (`window_runner.py` L128–L132, and the paper says so at L232 and L1848), and that is exactly
why the claim at L2220–2221 cannot be generalised past it. The frozen choice is a legitimate scope
boundary, not a defence of the inference drawn across it.

---

## 7. Bottom line

The new evidence **does not undermine the paper's central negative claim as it is scoped**
(L2110–2128: no recoverable prediction gain inside the frozen weighting class; the GO rule did not
fire). I reproduced every load-bearing number behind the new sentence and they are correct.
The evidence **does contradict** the one causal sentence added at L2220–2221, because that sentence
draws a learner-level conclusion from an optimizer-only manipulation that its own text discloses
("trained with Adam"), against a comparator that moves 2.4–3.2 % of its own norm, and in the same
design the endpoint demonstrably does move (U-Air 1.15992 → 0.97749; NSW-Traffic 1.0066 → 0.83509).
The manuscript now asserts both the defensible and the indefensible version, three hundred lines
apart, with no boundary between them. Repair is one experiment (optimizer-matched control, or H
recomputed under FedAdam) plus one sentence; the paper's structural contribution is untouched.

*Verification limits: I read `results_server_optimizer/round_v1/` (report, verdicts, gates, frozen
config, blocked notice, driver source, tables, and the run directories and frozen artifacts they
point at). I did not re-execute any training run. The 2→20 budget ladder lives in a different round
(`results_new_block_traffic/round_v1/S1_LADDER.csv`) and was read, not re-run. The
"Go/Significance" of the Adam gain against a properly-trained centralized baseline is not
established by any artifact in this workspace.*
