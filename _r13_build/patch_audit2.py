import pathlib

p = pathlib.Path(r"C:\Cursor\raven.mcs\_r13_build\raven-mcs-integrity-audit.md")
txt = p.read_text(encoding="utf-8")

OLD = """The three differing files are exactly the three that `git status` reports as modified under
`TO_OVERLEAF_paper_tmc_r1_clean/figure_data/`, which corroborates that the worktree copies were
regenerated (post-θ-resampling) while the bundle copies were not. The handoff's single-pair
comparison therefore understated the drift by a factor of three; the E4 pair is not the only, nor
necessarily the most consequential, lag point."""

NEW = """The three differing files are exactly the three that `git status` reports as modified under
`TO_OVERLEAF_paper_tmc_r1_clean/figure_data/`, which corroborates that the worktree copies were
regenerated while the bundle copies were not. The handoff's single-pair comparison therefore
understated the drift by a factor of three; the E4 pair is not the only, nor necessarily the most
consequential, lag point.

For the E4 pair the *reason* is now established, and it is a legitimate one. The frozen per-run
records give U-Air Design `RMSE_μ` means of `1.191114` (E3 `uair/raven`) vs `1.113059`
(E4 `uair/raven_wo_design`), i.e. **−6.553094 %**, and the frozen 240-cell evidence table agrees —
`results_seed_path_audit_r1/C4_T4_STATS.csv` even carries that figure in a `printed_old` column.
The printed **−6.885464 %** instead uses `full_mean = 1.195366`, the θ-copy re-score in
`results_active_set_repair/round_v1/E2_UAIR_CELLS.csv` (source `"G1c selected: tree"`), which
replaces exactly three U-Air seeds — `30007`, `30016`, `30018` — under the mirror/θ ruling recorded
in `results_endpoint_screen/round_v1/EXECUTION_REPORT.md` §1 ("the checkpoint score is canonical
there", max `|Δ| = 0.05661`). So the worktree figure is the θ-rescored value the manuscript prints
and the bundle holds the pre-θ value; the manuscript's number is defensible under that ruling.
`Δ_group` was **not** replaced and still matches the frozen records exactly (−6.943368 %), which is
consistent with the handoff's observation that all ten differing rows are U-Air
`RMSE_mu`/`Tail_RMSE`. The defect is therefore **not** that the figure is wrong, but that (i) the
bundle was never refreshed to the ruling it depends on, and (ii) neither `MANIFEST.csv` nor
`verify.py` can express "this value is the pre-ruling vintage", so the inconsistency is invisible to
every automated check the bundle ships."""

assert txt.count(OLD) == 1, f"anchor count = {txt.count(OLD)}"
txt = txt.replace(OLD, NEW)

OLD2 = """* It left the `+0.768` / `+0.286` pair untraced. It is traceable; see §2 claim H and F-H."""

NEW2 = """* It left the `+0.768` / `+0.286` pair untraced. It is traceable; see §2 claim H and F-H.
* Its own script is incomplete relative to its docstring: `.rb_work/audit_new_paragraphs.py`
  (`f133c63898bc6269`) advertises claims A/B/C and H but implements only D/E/F, G and I–P. The
  unimplemented ones are precisely the claims its report marks `OK (no new claim)` or `OK with
  caveat`, so the two claim rows it treated most lightly are the two it did not compute. Both are
  verified here (§1 rows A/B/C/H)."""

assert txt.count(OLD2) == 1, f"anchor2 count = {txt.count(OLD2)}"
txt = txt.replace(OLD2, NEW2)

# --- severity table: add F-KR ---
OLD3 = """| F-E `E_min` not in run artefacts | **low** | premise inferred from defaults, not deposited |"""
NEW3 = """| F-KR trace vs runner `K_r` (U-Air Design-on) | **moderate (Reproducibility)** | two deposited artefacts give 77.4 % vs 90.2 % for the same 1 402 windows |
| F-E `E_min` not in run artefacts | **low** | premise inferred from defaults, not deposited on the E3 path |"""

assert txt.count(OLD3) == 1, f"anchor3 count = {txt.count(OLD3)}"
txt = txt.replace(OLD3, NEW3)

# --- no-invention: record the two corrections I made to my own first reading ---
OLD4 = """Where my first reading was wrong I recorded it (§4.5, negative `mde80`)."""
NEW4 = """Where my first reading was wrong I recorded it: I first read the negative `mde80` values as
structurally impossible and the column as unreproducible, and both readings were wrong (§4.5)."""
assert txt.count(OLD4) == 1, f"anchor4 count = {txt.count(OLD4)}"
txt = txt.replace(OLD4, NEW4)

p.write_text(txt, encoding="utf-8")
print("patched OK; lines =", len(txt.splitlines()), "; bytes =", len(txt.encode("utf-8")))
