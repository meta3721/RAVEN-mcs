# HANDOFF: rewrite Algorithm 2 and the E3 setup paragraph

Paste this to the executor AI:

```text
You are the SCD-ALG2-E3-SETUP writing executor for repo C:\Cursor\raven.mcs.
Read this entire file and post_review/C2_scd_phi/PROTOCOL_ALG2.json.
Read post_review/C2_scd_phi/SCD_PHI.json and SCD_PHI_DECISION.json before editing.
Edit TO_OVERLEAF_paper_tmc_r1_clean/main.tex only, plus appendix.tex solely if a sentence would contradict the new rule.
Do not invent numbers. Do not train. Do not change Table II cells.
Do not set Design_t := Gate_t. Do not pick a threshold from RMSE.
If you would need a third ranking dataset, stop.
```

```text
Experiment ID: SCD-ALG2-E3-SETUP
Canonical manuscript: TO_OVERLEAF_paper_tmc_r1_clean/main.tex
Paper method: support-conditional Design (SCD), NOT coverage Gate
phi freeze: post_review/C2_scd_phi/SCD_PHI_DECISION.json (status PASS)
```

---

## 0. Role and stop conditions

Make the SCD switch an explicit, reusable, label-free support test in Algorithm~\ref{alg:window_close} and in the E3/E4 setup paragraph. The test must recover the current table assignment (SensorScope Design ON, U-Air Design OFF) without using E3 RMSE.

Stop and ask the human if any of the following happens:

- `SCD_PHI_DECISION.json` is not `PASS`, or you cannot find `phi_train_unit`.
- You would pick \(\tau>0\) after seeing U-Air, or you would set `Design_t := Gate_t`.
- You would change Table~\ref{tab:main_effectiveness} numbers, method keys, or retrain.
- You would claim a third-city confirmation or an online per-window Design switch.
- SensorScope \(\phi\) in the JSON is not \(0\).
- You need a number that is not in `SCD_PHI.json` or already in `main.tex`.

Do not edit INT-R traces, do not `git push`, do not commit unless asked.

---

## 1. Why this edit exists

Reviewer C2: Algorithm 2 currently takes "frozen target-support compatibility"; E3 then says Design on SensorScope and off U-Air because \(25.5\%\) of U-Air risk units have \(\pi^{\mathrm{tar}}=0\). A skeptic can read that as "turn Design off where full Design hurt."

Required fix (this round): state an explicit reusable support test and apply it **without** E3 RMSE. A third ranking trace is **out of scope**.

The measurement round already froze:

```text
phi_scd := phi_train_unit
Design ON iff phi_scd == 0
SensorScope: 0 / 10285 = 0
U-Air:      2016 / 5688 = 0.35443037974683544  -> 35.4%
```

G1 / current manuscript \(25.5\%\) is a **different denominator**: EventTrace occurrence-weighted `phi_et_occ = 0.2546875` (13040/51200). Do not silently replace one with the other.

---

## 2. Frozen rule (do not retune)

Let \(\mathcal{I}_{\mathrm{risk}}^{\mathrm{train}}\) be the unique training-split atomic units. For unit \(i\), \(\pi_i^{\mathrm{tar}}\) is the frozen public client--stratum target \(\pi^{\mathrm{tar}}(k(i),s(i))\) already defined in Section~\ref{subsec:target_measures} (`build_pi_target`, `split="test"`). Missing keys are \(0\).

\begin{equation}
\phi=\frac{\#\{i\in\mathcal{I}_{\mathrm{risk}}^{\mathrm{train}}:\pi_i^{\mathrm{tar}}=0\}}{\#\mathcal{I}_{\mathrm{risk}}^{\mathrm{train}}},\qquad
\mathrm{Design}=\mathrm{ON}\iff\phi=0.
\end{equation}

Properties you must keep in the prose:

- Label-free: no \(Y\), no RMSE, no residuals.
- Computed from the frozen public target and the training support; **constant across windows** for that public target.
- Motivated by A5 positivity, not by Table II.
- \(\mathrm{Gate}_t\) remains diagnostic and does **not** switch Design.

Forbidden substitutes:

- `phi_et_occ` as the Algorithm 2 statistic (not transferable without traces).
- `phi_train_pair` as the Algorithm 2 statistic.
- `build_pi_target_support_compatible` (failed repair, not a method).
- Any \(\tau\) fitted to RMSE (including \(\tau=0.25\) chosen because U-Air is \(0.354\)).

---

## 3. How to talk about 35.4% vs 25.5%

| Quantity | Exact | One-decimal | Role in this pass |
| --- | ---: | ---: | --- |
| U-Air `phi_train_unit` | \(2016/5688=0.35443037974683544\) | \(35.4\%\) | **Operational SCD test** (Algorithm 2, E3 setup) |
| U-Air `phi_et_occ` | \(13040/51200=0.2546875\) | \(25.5\%\) | **Realized-trace diagnostic only** (with \(\mathcal{A}_r\) overlap \(51.6\%\)) |
| SensorScope both | \(0\) | \(0\%\) | Design ON |

In the E3 **setup** paragraph, the reason Design is off on U-Air is \(\phi=35.4\%\) on train units, not \(25.5\%\).

Keep \(25.5\%\) in the **reversal diagnostic** sentences (theory bound, Fig.~\ref{fig:w1_design_gate} discussion, Section~\ref{subsec:discussion_gate}) **only if** you name the denominator: realized always-on EventTrace risk appearances, not the Algorithm 2 train-unit \(\phi\). One short clause is enough. Do not delete \(51.6\%\) (already in the paper; do not recompute it).

Do not write \(35.443\%\) or extra digits. Do not invent \(2016/5688\) as a percentage other than \(35.4\%\).

---

## 4. Required edits in `main.tex`

### 4.1 Display the test (once)

Add one numbered equation for \(\phi\), with a label such as `eq:scd_phi`, immediately **before** Algorithm~\ref{alg:window_close} (after the sentence that currently says Design is by target-support compatibility, ~ll.1266--1267).

Rewrite that sentence so it:

- defines \(\mathcal{I}_{\mathrm{risk}}^{\mathrm{train}}\) as the unique training atomic units;
- states \(\mathrm{Design}_t=\mathrm{ON}\) iff \(\phi=0\);
- states that \(\phi\) is frozen for the public target and does not use labels or RMSE;
- repeats that \(\mathrm{Gate}_t\) does not switch Design.

Keep it short. Do not paste CSV columns.

### 4.2 Algorithm 2 (`alg:window_close`, ~ll.1298--1335)

Replace the REQUIRE line "frozen target-support compatibility" with the public \(\pi^{\mathrm{tar}}\) and \(\mathcal{I}_{\mathrm{risk}}^{\mathrm{train}}\).

Replace the branch

```text
IF the frozen public target is support-compatible
  Design_t <- ON
ELSE
  Design_t <- OFF
```

with an explicit \(\phi\) computation and \(\phi=0\) test. Suggested structure (keep `algorithmic` commands, do not switch packages):

```text
REQUIRE window t; recorded R,O,U; public mu; debt; model;
        frozen public pi^tar; training risk units I_risk^train
ENSURE theta_{t+1}, Q_{t+1}, Design_t
STATE phi <- |{i in I_risk^train : pi_i^tar = 0}| / |I_risk^train|
      (frozen public target; no labels; constant across windows)
IF phi = 0
  Design_t <- ON
  compute lagged opportunity/design ratios
ELSE
  Design_t <- OFF
  set zeta^o <- 1 on observed pairs
ENDIF
... remainder unchanged ...
```

Caption may stay "support-conditional Design" or become "support-conditional Design (\(\phi=0\) test)". Do not mention Gate in the caption.

Do not recompute \(\phi\) from the current window's realized risk set. The algorithm may say "frozen" / "once per public target" in a `\COMMENT`.

### 4.3 E3/E4 setup paragraph (~ll.1893--1899)

This is the second mandatory block. Replace the current "Design is kept on SensorScope, where target support is compatible, and dropped on U-Air, where 25.5% of risk units have \(\pi^{\mathrm{tar}}=0\)" with the explicit test **and** the frozen measurements:

- Cite Algorithm~\ref{alg:window_close} and \eqref{eq:scd_phi}.
- SensorScope: \(\phi=0\) (0 of 10285 train units) \(\Rightarrow\) Design ON.
- U-Air: \(\phi=35.4\%\) (2016 of 5688 train units) \(\Rightarrow\) Design OFF.
- Full Design remains a labeled U-Air diagnostic.
- Keep the failed support-compatible mixture sentence.
- One honest clause: the test recovers this two-dataset assignment; it is not a third-city confirmation.

Do not say E3 chose the switch after seeing RMSE. Fig.~\ref{fig:w1_design_gate} may still **explain** why Design hurts on U-Air; that figure is diagnosis, not the switch protocol.

### 4.4 Coupled "how SCD is chosen" sentences (mandatory consistency)

Update these so they name the \(\phi=0\) test instead of an unexplained "compatible / not":

| Approx. locus | Current gist | Required |
| --- | --- | --- |
| Intro ~ll.239--240 | on when compatible (SS), off when not (UA) | on iff \(\phi=0\); SS \(\phi=0\), UA \(\phi>0\) |
| ~l.642 | applies Design when compatible support | point to \eqref{eq:scd_phi} / Algorithm 2 |
| ~ll.1207--1208 | Design-enabled reconstruction when compatible | same test; Gate still separate |
| E3 aims ~ll.1782--1784 | Design on SS; off UA | by the \(\phi=0\) test |
| Fig.~\ref{fig:w1_design_gate} caption ~ll.2104--2105 | "E3 therefore applies Design on SS and withholds it on UA" | withhold **because** \(\phi>0\) on U-Air; the figure is the reversal diagnosis, not the selection rule |
| Conclusion ~ll.2503--2504 | applies Design when compatible support | iff \(\phi=0\) |

Do **not** dump 2016/5688 into the introduction or conclusion. Intro/conclusion: qualitative \(\phi=0\) vs \(\phi>0\) is enough. Exact counts live in the E3 setup paragraph.

### 4.5 Optional one-sentence disambiguation of 25.5%

If you leave \(25.5\%\) in ~ll.1592, 2244--2245, or 2407, add a short denominator clause so it cannot be read as Algorithm 2's \(\phi\). Example shape (do not copy if it creates an em dash):

"The operational test is the train-unit fraction \(\phi\); the \(25.5\%\) figure is the realized EventTrace occurrence share, reported with the \(\mathcal{A}_r\) overlap \(51.6\%\)."

If that would bloat a tight paragraph, move the occurrence share into the same sentence as \(51.6\%\) and let E3 setup carry \(35.4\%\).

### 4.6 Do not expand unless needed

Leave Table~\ref{tab:main_effectiveness} caption as "on for SensorScope, off for U-Air" unless one clause "by the \(\phi=0\) test" fits without wrapping badly.

Do not rewrite Algorithm 1. Do not move Gate to supplemental in this pass. Do not add Traffic/T-Drive \(\phi\) unless the human asks later.

`appendix.tex`: only touch a sentence that still describes the E3 switch as an unexplained two-dataset flag. INT-R supplemental stays occupancy robustness, not a new SCD rule.

---

## 5. Claim ceiling (REPORT-level, also for the manuscript)

Allowed:

- SCD is now an explicit \(\phi=0\) test on frozen public \(\pi^{\mathrm{tar}}\) vs training units.
- The test is label-free and recovers SensorScope ON / U-Air OFF.
- U-Air full Design remains a diagnostic; the reversal is still support incompatibility (A5 / \(\mathcal{A}_r\)), not plug-in failure.

Forbidden:

- "Online per-window Design" or "the Gate now switches Design".
- "Transfer demonstrated on a third city / Traffic / T-Drive ranking".
- "We chose \(\phi=0\) because it maximized E3 RMSE".
- Replacing every \(25.5\%\) with \(35.4\%\) without changing the denominator.
- Lab names: G1, SCD-PHI, INT-R round, SHA hashes.
- Em dashes. "Confirmed." "Publication-ready."
- `\ref{app:...}` from `main.tex` (xr is one-way; say "the supplemental material").

---

## 6. Writing mechanics

- File: `TO_OVERLEAF_paper_tmc_r1_clean/main.tex`.
- Keep IEEE `algorithm`/`algorithmic` style already in the file.
- Do not add new packages.
- After edits, grep `main.tex` for leftover "frozen target-support compatibility" in Algorithm 2. That phrase must not remain as the switch.
- Grep for `25.5`. Every remaining hit must either be the EventTrace diagnostic with a denominator, or you must have a reason it is not about the SCD switch.
- Grep `---` and Unicode em dash; none in new sentences.
- Do not change author `****`, GitHub URL, or Table II digits.

Compile if a local LaTeX build is already documented for this folder; if it is not, do not spend the pass installing TeX. Do not "fix" unrelated overfull boxes.

---

## 7. Execution order

1. Read `SCD_PHI_DECISION.json`. If not PASS, stop.
2. Read current Algorithm 2, the paragraph at ~ll.1266--1267, and ~ll.1893--1899.
3. Insert \eqref{eq:scd_phi} and rewrite Algorithm 2 (§4.1--4.2).
4. Rewrite the E3 setup paragraph (§4.3).
5. Consistency pass (§4.4--4.5).
6. Grep gates in §6.
7. Write `post_review/C2_scd_phi/ALG2_WRITING_REPORT.md`: list of changed loci, the two U-Air percentages with denominators, and a statement that Table II was not touched.
8. Stop. No training. No commit unless asked.

---

## 8. Done when

- Algorithm 2 contains \(\phi\) and `Design ON iff \(\phi=0\)`.
- E3 setup reports SS \(\phi=0\) (0/10285) and UA \(\phi=35.4\%\) (2016/5688).
- Gate is still not the switch.
- Table II digits unchanged.
- `ALG2_WRITING_REPORT.md` exists.
