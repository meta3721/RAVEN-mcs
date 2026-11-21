import pathlib

p = pathlib.Path(r"C:\Cursor\raven.mcs\_r13_build\raven-mcs-integrity-audit.md")
txt = p.read_text(encoding="utf-8")

OLD = """### F-E — `E_min = 3` is not recorded in the frozen run configuration (low severity, traceability)

The claim is correct (§1 row A), but it is *inferred from source defaults*, not read from an
artefact: the frozen `config_snapshot.json` for all four arms on the manuscript's path records
`local_steps: 2` and `scenario: complete_aligned` and **no `e_min` key at all**. The value reaches
the solver through `window_runner.py` L989 `e_min=float(getattr(agg, "e_min", 3.0))`. Two E4 call
sites do override it to `1.0` (`e4/semantic_repair/task_b.py:53`, `e4/wo_inst_final/corrective.py:59`),
so the default is not universal in the codebase; it is universal on the `raven` / `raven_wo_design`
path the paragraph measures. A reader cannot confirm `E_min = 3` from the released run artefacts.
No number changes; the premise is simply not depositable from what was shipped."""

NEW = """### F-E — `E_min = 3` is only partly recorded in the frozen artefacts (low severity, traceability)

The claim is correct (§1 row A), but on the E3 path it is *inferred from source defaults*, not read
from an artefact: the frozen `config_snapshot.json` for all four arms the paragraph measures records
`local_steps: 2` and `scenario: complete_aligned` and **no `e_min` key at all**, and
`configs/frozen/e3_multidataset_protocol_closure/` carries only horizon / opportunity_strata /
public_target / q_feature_boundary / stage2_eligibility. The value reaches the solver through
`window_runner.py` L989 `e_min=float(getattr(agg, "e_min", 3.0))`. Partly mitigating: the E4
one-factor spec *does* deposit it — `E4_WO_INST_FINAL_ONE_FACTOR_SPEC.json` L16
`"ESS_constraints": 3.0` — and two E4 call sites override it to `1.0`
(`e4/semantic_repair/task_b.py:53`, `e4/wo_inst_final/corrective.py:59`), so the default is not
universal in the codebase even though it is universal on the `raven` / `raven_wo_design` path.
No number changes; the premise is simply not confirmable from the E3 run artefacts themselves.

### F-KR — For U-Air Design-on the trace-derived and runner-derived `K_r` disagree (moderate, reproducibility)

`K_r` is directly recorded, not derived: `window_metrics.json` carries `a_r_size` (= `K_r`) and
`active_clients` (= `len`), and `main.tex` L880 defines `K_r = |A_r|`. On SensorScope and on U-Air
Design-off the independent trace artefact `.rb_work/evidence_headroom/REACHABILITY_WINDOWS.parquet`
(`n_active`) agrees with the runner **row for row** (2 000/2 000 and 1 600/1 600). On **U-Air
Design-on it does not**: `trace − K_r ∈ {0: 741, 1: 503, 2: 141, 3: 16, 4: 1}`, 113 windows are
trace-active but runner-inactive, and the trace-based `K_r ≤ 3` share over the *same* 1 402 windows
is **77.389 %**, not the printed **90.157 %**.

Consequence: the `90.2 % of 1402` claim is traceable to `window_metrics.json` only; it is not
derivable from the released EventTraces. That is a genuine artefact disagreement between two
deposited objects for the same windows, and it is not disclosed anywhere. It does not by itself
falsify the sentence — the sentence's perimeter is the runner's active window set, which is
self-consistent — but a reader who recomputes from the traces will get a different number and no
explanation. This is the mechanism paragraph's counterpart to §4.2: the numbers are right against
one deposited object and not against another.

Note also that `K_r ≤ 3` (this paragraph) and `|A_r| ≤ 2` (ledger item 62, 51.4 % / 69.0 %) are
**different thresholds of the same statistic**, not two renderings of one fact. Both verify: the
`≤ 3` shares are 78.58 / 90.16 / 79.01 %, and the `≤ 2` shares are 965/1877 = 51.41 % (SS) and
968/1402 = 69.04 % (UA Design-on), matching ledger item 62 exactly."""

assert txt.count(OLD) == 1, f"anchor count = {txt.count(OLD)}"
txt = txt.replace(OLD, NEW)

# --- amend F-H with the measured unit convention and the CI vintage ---
OLD2 = """The bundled source agrees with L1834, not with the new sentence: `PART_A_REPORT.md` L15 flags the
SensorScope pair as outside the equivalence band and passing the practical line ("超出带 /
**通过**"), and L17 flags U-Air as outside the band but failing it ("不通过"). So one of the two
numbers is designated practically significant and Holm-significant by this paper, and the new
sentence calls the pair a small margin. The numbers are right and traceable; the characterisation
conflicts with the paper's own. A reader who checks L1834/L2092 will read the new sentence as
downplaying a result the paper claims elsewhere."""

NEW2 = """The bundled source agrees with L1834, not with the new sentence: `PART_A_REPORT.md` L15 flags the
SensorScope pair as outside the equivalence band and passing the practical line ("超出带 /
**通过**"), and L17 flags U-Air as outside the band but failing it ("不通过"). So one of the two
numbers is designated practically significant and Holm-significant by this paper, and the new
sentence calls the pair a small margin. The numbers are right and traceable; the characterisation
conflicts with the paper's own. A reader who checks L1834/L2092 will read the new sentence as
downplaying a result the paper claims elsewhere.

Two provenance details, both resolved in the paragraph's favour. (i) The printed CI brackets
`[0.563, 0.970]` and `[0.098, 0.471]` reproduce **exactly** from the bundled
`w1/tradeoff_v4/PART_A_REPORT.md` L15/L17. Recomputing the same contrast from
`results_w1_ladder/round_v4/FULL_SEED_LADDER.csv` instead gives `[0.561, 0.965]` and
`[0.091, 0.470]` — a third vintage that agrees to the second decimal but not the third. The
manuscript matches the bundled report, so this is a vintage spread across artefacts, not a
manuscript error; it does mean the pair is not reproducible to the printed precision from
`round_v4` alone. (ii) "pp" is a fixed rescaling, not a percentage of anything natural:
`pp_group = 50 × d_group` on every row of `FULL_SEED_LADDER.csv` (max deviation 0.0), matching
`GAP_DECOMPOSITION.csv` `pp_total = 50 × delta_total`. The `0.5` pp practical line is therefore
`0.01` in `Δ_group` units. This is internally consistent and is how the paper uses it elsewhere;
it is recorded because a reader cannot infer the unit from the sentence."""

assert txt.count(OLD2) == 1, f"anchor2 count = {txt.count(OLD2)}"
txt = txt.replace(OLD2, NEW2)

p.write_text(txt, encoding="utf-8")
print("patched OK; lines =", len(txt.splitlines()), "; bytes =", len(txt.encode('utf-8')))
