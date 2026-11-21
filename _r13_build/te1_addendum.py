"""Append the post-run addendum to TE1_REPORT.md (the prompt requires any deviation to be recorded)."""
from __future__ import annotations

import pathlib

p = pathlib.Path(r"C:\Cursor\raven.mcs\results_traffic_e1\round_v1\TE1_REPORT.md")
t = p.read_text(encoding="utf-8")
assert "## Addendum" not in t

t += """
## Addendum (recorded after the run)

1. **A defect in this round's own pre-run checker wrote a spurious `TE1_BLOCKED.md`.** The first
   invocation compared the requested server optimizer against `ServerOptWindowRunner.SERVER_OPT`
   *before* any `install()` call, which returns the un-installed default
   `{"mode": "off", "eta_s": null}`. It is not a section-1 STOP condition: no confirm seed was started
   and no run directory was created. The file is kept as `TE1_BLOCKED.voided-selfcheck.md` for audit,
   and the checker now installs the configuration and compares it against the S1' frozen
   `SERVER_OPT_META.json`, which matched exactly
   (`{"mode": "adam", "eta_s": 0.003, "beta1": 0.9, "beta2": 0.99, "tau": 0.001}`, `local_steps` 2).

2. **Interpretation of "the test split is read only after `TE1_FROZEN_CONST.json` exists and G0 has
   passed" (section 5).** Read here as: no *confirm* test prediction is computed before the freeze. G0
   necessarily reads the screen seeds' stored test `RMSE_mu`, and section 8 places G0 before the
   freeze, while section 0 states that those seeds are design inputs which have already seen the test
   split. No confirm seed's test value was computed before `TE1_FROZEN_CONST.json` was written.

3. **The prompt's planning `MDE80` was conservative.** It projected `MDE80(n = 15) = 0.163696` from the
   screen sd `0.210430`. The confirm sd is `0.074593`, so the realised `MDE80` is `0.058027`. The
   screen sd was inflated by seed 30005 (`H = -0.456978`); the confirm set has no comparable outlier,
   its most negative seed being 30007 at `H = -0.236611`, and its sign split is 6 positive to 9
   negative. The verdict is unchanged.

4. **`K_r <= 3` is identical for both arms on every confirm seed** (mean `0.150819`, range
   `0.100000`-`0.222222`), so which arm supplies the GO-condition value does not affect the reading.

5. **The finiteness limb of the stability rule** scanned every JSON file in each run directory and
   every checkpoint tensor. The runner writes no separate training-loss series, so no loss file exists
   beyond those.

6. No `src/`, paper, frozen artifact or `results_server_optimizer/round_v1/` file was modified by this
   round; the 18 traffic runs here used the reuse-guard exemption already recorded in the diagnosis
   ledger Part IX item 65, and each carries `REUSE_GUARD_EXEMPTION.json` for the `fedavg_window` arm.
"""
p.write_text(t, encoding="utf-8")
print("appended addendum;", len(t.splitlines()), "lines,", len(t.encode()), "B")

# verify the exemption records landed on the confirm fedavg runs
import json
runs = pathlib.Path(r"C:\Cursor\raven.mcs\results_traffic_e1\round_v1\runs")
fed = sorted((runs / "C1_fedavg/traffic/fedavg_window").glob("seed*"))
with_ex = sum(1 for d in fed if (d / "REUSE_GUARD_EXEMPTION.json").is_file())
sim = sorted((runs / "C1_simoracle/traffic/raven_simoracle").glob("seed*"))
print(f"confirm fedavg runs: {len(fed)} | with REUSE_GUARD_EXEMPTION.json: {with_ex}")
print(f"confirm simoracle runs: {len(sim)} | (no exemption needed, none present: "
      f"{sum(1 for d in sim if (d / 'REUSE_GUARD_EXEMPTION.json').is_file()) == 0})")
