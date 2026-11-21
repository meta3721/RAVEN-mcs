# G4 ↔ G1 correspondence (handbook §8.4)

G1 numbers are sealed diagnostics. This table is the theory–experiment contract. It is not a new experiment.

| Theory symbol | G1 object | SensorScope | U-Air | Reading |
|---|---|---:|---:|---|
| A5 / \(\pi_{\min}\) on \(\{\pi^{\mathrm{tar}}>0\}\) | `frac_pi_tar_zero` | **0** | **0.255** | U-Air: A5 fails. \(C_1\) undefined. Theorem does not apply to Design-on. |
| \(\mathcal{A}_r\) fixed? | same-\(A_r\) vs No-Design | **100%** | **51.6%** | U-Air Design changes the feasible set. Outside the P2 non-expansion hypothesis. |
| \(\varepsilon_\pi\) (implemented) | frozen generator \(\pi^{\mathrm{opp}}\) | TV(realized, frozen) 0.061 | 0.056 | Production Design does **not** use online \(\widehat\pi\). Implemented \(\varepsilon_\pi=0\). |
| \(\varepsilon_p\) | \(\hat p\) Brier / ECE; \(\|a_{\mathrm{on}}-a_{\mathrm{oracle}}\|\) | 0.172 / 0.059; 1.74 | 0.170 / 0.058; **1.14** | Plug-in \(p\) is imperfect. Oracle-\(p\) still reverses U-Air primaries. |
| \(\varepsilon_q\) | \(\hat q\) ECE; oracle \(q\) used by `raven_simoracle` | 0.094 | 0.108 | \(\hat q\) miscalibrated. Oracle-\(q\) still reverses U-Air. |
| \(\varepsilon_{\mathrm{clip}}\) | clip rate; \(\zeta_{\max}\) vs \(a_{\max}=20\) | 0.047; \(\zeta_{\max}=3.71\) | 0.057; \(\zeta_{\max}=4.52\) | Clip is modest. Not the U-Air mechanism. |
| \(B_{\min}\) / ESS | `ess_ratio_on_mean` (Design / No-Design) | 0.772 / 0.772 | 0.569 / 0.763 | Smaller ESS loosens \(C_1\). Seed-level ESS does **not** sort the U-Air reversal. |
| \(\|\widehat\alpha-\alpha^{\mathrm{oracle}}\|\) | oracle vs estimated endpoints | \(\Delta_{\mathrm{group}}\) −1.03% vs −1.23% | **−0.02%** | Same Design, \(\mathcal{A}_r\) shared: plug-in error is small after P2. Matches the bound. |
| \(\|M(\alpha^{\mathrm{Design}}-\alpha^{\mathrm{off}})\|\) | Design vs No-Design | slight \(\Delta_{\mathrm{group}}\) gain | **+7.5%** primaries | Not a plug-in gap. Support shift. Theorem correctly refuses this comparison. |

## Instantiation rule

`instantiate_c1.py` reports \(C_1 B_{\min}\) at \(K_r=n_r=1\) (Lipschitz piece only).

- Using the **global** \(\min\pi^{\mathrm{opp}}\) (\(\sim 6\cdot10^{-4}\)) makes \(C_1\) huge even on SensorScope. That is the conservative bound, not a numerical prediction.
- Using \(\pi_{\min}\approx 1/\zeta_{\max}\) on \(\{\pi^{\mathrm{tar}}>0\}\) is the relevant supported-ratio floor (SS \(\zeta_{\max}=3.71\), U-Air \(4.52\)).
- On U-Air the script **forces** \(C_1=\infty\) because A5 fails, regardless of \(\zeta_{\max}\).

ESS is a qualitative flag for \(B_{\min}\), not a substitute for \(B_{\min}\).

## What this does to novelty / W4

The missing object was a bound from estimated/clipped ratios to the P2 decision. That bound now exists and is 1-Lipschitz through calibration **when support is compatible**.

W4 (estimated propensity) is therefore a **controlled remainder** on SensorScope. It is **not** the explanation of W1 on U-Air. Path B remains the paper default.
