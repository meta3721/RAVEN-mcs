import pathlib, re
p = pathlib.Path("ccfa-review-reports/raven-mcs-metric-definition-diagnosis.md")
L = p.read_text(encoding="utf-8").split("\n")
log = []

def sub_row(prefix, new):
    for i, l in enumerate(L):
        if l.startswith(prefix):
            L[i] = new; log.append(f"row rewritten @{i+1}: {prefix[:44]}"); return True
    log.append(f"NOT FOUND: {prefix[:60]}"); return False

def drop_row(prefix):
    for i, l in enumerate(L):
        if l.startswith(prefix):
            del L[i]; log.append(f"row deleted @{i+1}: {prefix[:44]}"); return True
    log.append(f"NOT FOUND: {prefix[:60]}"); return False

sub_row("| 1 | Fix N1",
        "| 1 | ~~Fix N1–N2 and N4 in the manuscript~~ **done 2026-09-27** | `ccf-paper-writer` | "
        "executed under route A; the four rows are rebuilt on the licensed set and the `Δ_group` claim is qualified |")
sub_row("| 4 | Rebuild the U-Air",
        "| 4 | ~~Rebuild the U-Air `FedAvg-Window` row from one frozen batch and state the metric scale~~ "
        "**done 2026-09-27** | `ccf-paper-writer` | G1c selected the E3 tree; §VII-A now states σ |")
drop_row("| **the U-Air `FedAvg-Window` and `Local-Hájek` rows rest on")
drop_row("| **the U-Air `FedAvg-Window` row is sourced from two frozen batches")
drop_row("| **Table III's `RMSE_μ` column mixes metric scales")

# changelog for the manuscript write
anchor = "### Open manuscript defects NOT changed"
block = """### Manuscript write — 2026-09-27 (route A repair; first authorized `.tex` edit)

| # | change | where |
|:--|:---|:---|
| 26 | U-Air `FedAvg-Window` row replaced with the licensed-set values: `1.1882→1.1119`, `1.2596→1.1690`, `1.1218→1.0446`, `1.2621→1.3138` | `main.tex` Table III |
| 27 | `tab:app_e3_uair`: FedAvg, FedAsync, TimeAlign and Debt-Cal rows replaced; caption now states that each row uses the active set its own definition licenses | `appendix.tex` |
| 28 | `tab:app_block_rmse` UA `FedAvg-Window` row replaced with `1.1015 / 1.1144 / 1.1690 / 1.0721`, WG `1.1690` | `appendix.tex` |
| 29 | `tab:app_p2_coverage` U-Air row: `70.10 / 63--75` → `72.61 / 63--79` | `appendix.tex` |
| 30 | the `TEST $-$9.11 % / $-$6.17 %` sentence replaced by a within-Design-family statement (RAVEN-Design vs TwoStage-Hájek, $2.46\\%$, $10/10$) plus the six-comparator `Δ_group` qualification; the development-table summary's `FedAvg/TwoStage-Hájek` claim corrected | `main.tex` §V |
| 31 | the Local-Hájek coincidence attributed to the shared Design-support restriction | `main.tex` §V |
| 32 | metric scale disclosed: U-Air and NSW-Traffic standardized ($\\sigma=17.363$, $575.776$), SensorScope physical, ratio columns invariant (closes N7) | `main.tex` §VII-A |

Build invariants after item 32: main **16 pages**, supplement **15 pages**, equation labels **41**,
0 undefined references or citations, 0 overfull boxes above 2 pt,
`tools/freeze_appendix_refs.py --check` reports 0 to freeze and 0 unresolvable (57 kept), em dashes
in `main.tex` 2 and in `appendix.tex` 0.

Still not written: the three feasibility-audit counts (778 warnings / 85 runs / 6438 windows /
$2.686\\times10^{-8}$). Their population is not the 180-run set that `tab:app_p2_coverage` covers, so
the effect of substituting the rebuilt methods cannot be determined without a solver-log re-audit.
Reporting them unchanged is deliberate; inventing replacements is not an option.

"""
if anchor in L:
    i = L.index(anchor)
    L[i:i] = block.split("\n")
    log.append(f"changelog block inserted before line {i+1} ({anchor})")
else:
    log.append("ANCHOR NOT FOUND for changelog block")

p.write_text("\n".join(L), encoding="utf-8")
print("\n".join(log))
print(f"record now {len(L)} lines")
