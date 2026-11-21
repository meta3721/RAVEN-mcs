# X1 execution steps — T-Drive four-quadrant Design-on ranking

```text
Mode: design + execution queue (not result-presentation)
Venue and assumptions: IEEE TMC regular; independent hybrid table; not Table II
Skill: ccf-experiment-designer
Humanization: skipped (raw protocol / queue; no manuscript tables or captions)
Experiment ID: C1-KILL-TD-SPATIAL  (advisor-package name: X1)
Status now: LOCKED; phi frozen; 10 EventTraces on disk; train 1/50
No-fabrication: PASS — ranking cells remain TBD until AUDIT.complete_matrix
Next owner after a complete matrix: user (ingest decision); ccf-paper-writer only if c1_kill=true
```

Do **not** start `--stage phi`, `--stage generate --force`, or `--stage all`. Those stages are already done. This file only resumes **train → tables**.

---

## Claim-evidence matrix (this block only)

| Claim | Reviewer question | Evidence | Dataset | Baselines | Metrics | Result | Status |
| --- | --- | --- | --- | --- | --- | --- | --- |
| Title method can run Design under real taxi \(R\) | Is \(\phi=0\) before RMSE? | `GO.json` / `C1_SCD_FREEZE.json` | T-Drive processed, four-quadrant \(\mu\) | — | \(\phi\), Design on | \(\phi=0\), Design ON | **done** |
| Stack vs FedAU/ObsUse on that ranking | Inside the paper’s −0.5% “win” bar? | 10-seed paired relative | same, 178 windows | FedAvg, Hájek, FedAU, ObsUse, raven | RMSE_μ ↓, WorstGroupRMSE ↓, \(\Delta_{\mathrm{group}}\), \(\Delta_{c\text{-}s}\) | TBD | **1/50** |

Kill bar (frozen **before** RMSE, do not edit):

SCD (`raven`) paired mean relative vs **both** `fedau_window` and `obsuse_window` \(\le -0.005\) on WorstGroupRMSE **or** on RMSE_μ.

Missing the bar is a legal negative. Do not retune \(\phi\), \(h(i)\), \(p_{\mathrm{obs}}\), \(s_{\max}\), windows, seeds, or lambdas.

---

## Frozen contract (do not change)

| Item | Value | Do not |
| --- | --- | --- |
| Spec | `post_review/C1_kill_tdrive_spatial/TARGET_SPEC.json` `LOCKED` | Edit the JSON |
| Driver | `scripts/run_c1_tdrive_spatial.py` | Overwrite `tdrive_protocol_seal_r1/` |
| Device | hardcoded `"cpu"` (`_device()`) | Flip to CUDA without a separate index fix |
| \(\phi\) | 0/285659, `design_on=true`, `scd_method=raven` | Recompute after any RMSE |
| \(h(i)\) | `beijing_grid_4_quadrant_median_gx_gy_all_cells_no_Y` | UTC H1–H4 |
| \(R\) | real T-Drive occupancy (same processed table as TD-R-E3) | Overlay GPS on stations |
| \(O/U\) | \(p_{\mathrm{obs}}=0.35\), `compute_usable_r3` \(s_{\max}=5\) | Call them measured |
| Seeds | 31001–31010 | Reuse 30001 UTC traces |
| Windows | 178 | Shorten for speed |
| Methods | `fedavg_window`, `twostage_hajek`, `fedau_window`, `obsuse_window`, `raven` | Add FLOSS / force-Design extra |
| Label | hybrid, controlled \(O/U\), not end-to-end MCS | Mix into Table II |
| Keep | `runs/.../fedavg_window/seed31001/C1_ACCEPTED.json` | Delete it |

---

## Confirmed methods / baselines

```text
Display name: RAVEN-Design (raven), phi=0
Implementation: scripts/run_c1_tdrive_spatial.py + existing raven policy
Status: confirmed (GO.json design_on=true, used_y_or_rmse=false)
Baselines: FedAvg-Window, TwoStage-Hájek, FedAU-Window, ObsUse-Window (windowed adapters)
Device: cpu
```

Schedule order in the driver (seed-major):

`31001 fedavg → hajek → fedau → obsuse → raven`, then the same five for `31002` … `31010`.

Already accepted: **fedavg_window / 31001** only. Remaining: **49** jobs.

---

## Step 0 — preflight (minutes)

Working directory: `C:\Cursor\raven.mcs`.

```powershell
cd C:\Cursor\raven.mcs
$py = ".\.venv_new\Scripts\python.exe"

# 0.1 no other C1 train running
Get-CimInstance Win32_Process -Filter "Name='python.exe'" |
  Where-Object { $_.CommandLine -match 'run_c1_tdrive_spatial.py' } |
  Select-Object ProcessId, CommandLine

# 0.2 freeze still Design-on and unused-Y
$py -c "import json; g=json.load(open('results_c1_kill/round_v1/GO.json',encoding='utf-8')); f=json.load(open('results_c1_kill/round_v1/C1_SCD_FREEZE.json',encoding='utf-8')); assert g['design_on'] and g['phi_train_unit']==0.0 and g['scd_method']=='raven'; assert f['used_y_or_rmse'] is False; print('phi_ok', f['phi_train_unit'], 'n_zero', f['n_train_zero'])"

# 0.3 ten EventTraces + parquet
$py -c "from pathlib import Path; r=Path('artifacts/e3_c1_tdrive_spatial_eventtraces_v1/tdrive_spatial_h');
miss=[s for s in range(31001,31011) if not (r/f'seed{s}/training_eventtrace/events.parquet').is_file()];
print('missing_parquet', miss or 'none')"

# 0.4 accepted canary still there
$py -c "import json; p=json.load(open('results_c1_kill/round_v1/runs/tdrive_spatial_h/fedavg_window/seed31001/C1_ACCEPTED.json',encoding='utf-8')); print(p['method'], p['seed'], p['n_windows'], round(p['RMSE_mu'],4), p['device'])"
```

Abort if: another `run_c1_tdrive_spatial.py` is alive; `design_on` is false; any `events.parquet` missing; the 31001 FedAvg marker is gone.

If parquet is missing for a seed: `--stage generate` **without** `--force` (reuses identity when present). Never `--force`.

---

## Step 1 — smoke (one IPW path, not a paper number)

Existing `--stage smoke` only reuses FedAvg 31001. That is not an IPW check.

The diagnostics patch is already in `_lagged_light`. The first **new** job is `twostage_hajek` seed 31001. Treat its first windows as the smoke:

```powershell
cd C:\Cursor\raven.mcs
.\.venv_new\Scripts\python.exe scripts\run_c1_tdrive_spatial.py --stage train --max-runs 2
```

`--max-runs 2` = FedAvg 31001 **REUSED** + Hájek 31001 **real**.

Watch `results_c1_kill/round_v1/EXECUTION_LOG.md`:

| Window 1–5 of Hájek | Action |
| --- | --- |
| ~10–40 s / window (same order as FedAvg) | patch OK; let the job finish |
| minutes per window and rising | **stop the process**; do not continue the 49-job matrix |

Hájek 31001 is part of the official 50, not a throwaway. Do not delete `C1_ACCEPTED.json` if it appears.

UTC GPU Hájek was ~0.3 h / 178 windows; CPU FedAvg on this block was 0.61 h. Budget Hájek 31001 **0.5–2 h** if the patch holds.

---

## Step 2 — remaining matrix

After Hájek 31001 has `C1_ACCEPTED.json`:

```powershell
cd C:\Cursor\raven.mcs
.\.venv_new\Scripts\python.exe scripts\run_c1_tdrive_spatial.py --stage train
```

Resume is automatic: any `C1_ACCEPTED.json` is skipped. If the process dies, run the **same** command again.

Do not pass `--force`. Do not pass `--stage all`. Do not change `--seeds`.

Optional heartbeat (another terminal, do not start a second train):

```powershell
Get-Content C:\Cursor\raven.mcs\results_c1_kill\round_v1\EXECUTION_LOG.md -Tail 20
```

Wall-clock (one CPU process, UTC-method times as a prior): **about 2.5–4 days**. FedAU / ObsUse / Design-on raven are the heavy rows (~2 h each on the UTC GPU ledger). Do not interpret that as a result.

---

## Step 3 — tables / audit (driver already does this at end of `--stage train`)

If train exited early, rebuild tables only:

```powershell
.\.venv_new\Scripts\python.exe scripts\run_c1_tdrive_spatial.py --stage tables
```

Read, do not rewrite by hand:

- `results_c1_kill/round_v1/AUDIT.json`
- `results_c1_kill/round_v1/tables/C1_E3_SUMMARY.csv`
- `results_c1_kill/round_v1/tables/C1_E3_PAIRED.csv`
- `results_c1_kill/round_v1/C1_TRAIN_LEDGER.json`

Required for a ranking:

```text
AUDIT.status = PASS
AUDIT.complete_matrix = true
n_expected = 50
n_rows = 50  (ledger; accepted or REUSED)
eventtrace_hash_consistent = true
table_ii_untouched = true
tdrive_hybrid_untouched = true
```

Then record `c1_kill` true/false from the file. Do not round, do not drop a seed to flip the bar.

---

## Step 4 — stop conditions (ingest / writing)

| AUDIT | Paper action | Forbidden |
| --- | --- | --- |
| `INCOMPLETE` | nothing | Quote partial means as a ranking |
| `PASS` and `c1_kill=true` | independent hybrid table; Design on because \(\phi=0\); hybrid label | Mix into Table II; restore formal NI |
| `PASS` and `c1_kill=false` | `C1_KILL_REPORT.md` only; keep UTC hybrid as Design-off negative | Retune \(h(i)\) / \(\phi\); call it a win because \(\Delta_{\mathrm{group}}\) moved |

This step is **not** authorized in X1. Handoff: `ccf-paper-writer` only after the user says to ingest.

---

## Ablations / extra methods

None in X1. `raven_wo_design`, Use/Debt cuts, restricted-support are X5/X6. Do not append them to `mandatory_methods`.

---

## Robustness / failure

- CUDA: driver stays CPU. A CUDA retry is a **different** authorized patch, not this queue.
- Hájek memory leak: if window times explode, stop; do not “fix” by dropping Hájek from the table.
- Incomplete 10-seed subset: not a ranking.

---

## Smoke scope (deduplicated)

One IPW check: Hájek 31001 first windows (Step 1). FedAvg smoke already executed. No per-method ceremonial smoke.

---

## Result template (fill only from AUDIT PASS)

Setting: real taxi \(R\); controlled \(O/U\); four-quadrant \(\mu\); \(\phi=0\); seeds 31001–31010; 178 windows.

| Method | RMSE_μ ↓ | WorstGroupRMSE ↓ | \(\Delta_{\mathrm{group}}\) | \(\Delta_{c\text{-}s}\) | n |
| --- | --- | --- | --- | --- | ---: |
| FedAvg-Window | TBD | TBD | TBD | TBD | 10 |
| TwoStage-Hájek | TBD | TBD | TBD | TBD | 10 |
| FedAU-Window | TBD | TBD | TBD | TBD | 10 |
| ObsUse-Window | TBD | TBD | TBD | TBD | 10 |
| RAVEN-Design (`raven`) | TBD | TBD | TBD | TBD | 10 |

| Comparator | RMSE_μ paired rel. | WG paired rel. | n | contributes to `c1_kill` |
| --- | --- | --- | ---: | --- |
| FedAU-Window | TBD | TBD | 10 | both \(\le -0.5\%\) on RMSE **or** WG |
| ObsUse-Window | TBD | TBD | 10 | same |

FedAvg 31001 numbers already in the ledger are **not** 10-seed means. Do not copy them into this table until n=10.

---

## Execution priority

| Priority | Action | Stop |
| --- | --- | --- |
| P0 | Step 0 preflight | abort if freeze/traces/marker fail |
| P0 | Step 1 Hájek 31001 | abort if window time explodes |
| P0 | Step 2 `--stage train` to 50 | resume on crash; no retune |
| P0 | Step 3 AUDIT | ranking only if PASS |
| — | Step 4 writing | user authorization |

---

## Commands that are out of scope

```text
python scripts/run_c1_tdrive_spatial.py --stage all
python scripts/run_c1_tdrive_spatial.py --stage generate --force
python scripts/run_c1_tdrive_spatial.py --stage phi
# any edit of TARGET_SPEC.json, GO.json, C1_SCD_FREEZE.json after RMSE
# any edit of TO_OVERLEAF_paper_tmc_r1_clean/main.tex Table II / tdrive hybrid
```
