import pathlib

p = pathlib.Path(r"C:\Cursor\raven.mcs\results_server_optimizer\round_v1\driver\s1p_driver.py")
txt = p.read_text(encoding="utf-8")

# --- 1. comparator: separate the wall-clock field explicitly ---
OLD = '''def same_final_metrics(a: dict, b: dict) -> tuple[bool, list]:
    """Bit-exact comparison of every key, including nested group_rmse."""
    diffs = []
    for k in sorted(set(a) | set(b)):
        va, vb = a.get(k, "<missing>"), b.get(k, "<missing>")
        if isinstance(va, dict) and isinstance(vb, dict):
            for kk in sorted(set(va) | set(vb)):
                if va.get(kk) != vb.get(kk):
                    diffs.append(f"{k}.{kk}: {va.get(kk)!r} vs {vb.get(kk)!r}")
        elif va != vb:
            diffs.append(f"{k}: {va!r} vs {vb!r}")
    return (not diffs), diffs'''

NEW = '''# `runtime_seconds` is a wall-clock measurement, not a function of the computation, so no two runs
# can agree on it.  It is the ONLY field excluded from the bit-exact comparison, it is named here in
# one place, and every comparison reports both verdicts (deterministic / literal).
WALL_CLOCK_FIELDS = frozenset({"runtime_seconds"})


def same_final_metrics(a: dict, b: dict) -> tuple[bool, list, list, dict]:
    """Bit-exact comparison of every key, including nested group_rmse.

    Returns (deterministic_equal, deterministic_diffs, all_diffs, wall_clock_values).
    """
    det_diffs, all_diffs, wall = [], [], {}

    def cmp(name: str, va, vb) -> None:
        if va != vb:
            all_diffs.append(f"{name}: {va!r} vs {vb!r}")
            if name in WALL_CLOCK_FIELDS:
                wall[name] = [va, vb]
            else:
                det_diffs.append(f"{name}: {va!r} vs {vb!r}")

    for k in sorted(set(a) | set(b)):
        va, vb = a.get(k, "<missing>"), b.get(k, "<missing>")
        if isinstance(va, dict) and isinstance(vb, dict):
            for kk in sorted(set(va) | set(vb)):
                cmp(f"{k}.{kk}", va.get(kk), vb.get(kk))
        else:
            cmp(k, va, vb)
    return (not det_diffs), det_diffs, all_diffs, wall'''
assert txt.count(OLD) == 1, "anchor1"
txt = txt.replace(OLD, NEW)

# --- 2. record source identity in the ledger ---
OLD2 = '''            dataset_name=block,
            scenario="complete_aligned",
            local_steps=int(local_steps),
        )'''
NEW2 = '''            dataset_name=block,
            scenario="complete_aligned",
            local_steps=int(local_steps),
            source_identity={
                "git_commit": _git_commit(),
                "s1p_driver_sha256": sha256_file(pathlib.Path(__file__)),
                "s1p_instruction_sha256": sha256_file(INSTRUCTION) if INSTRUCTION.is_file() else None,
                "server_opt": dict(ServerOptWindowRunner.SERVER_OPT),
                "server_opt_windowrunner_patch": "raven_mcs.training.window_runner.FullWindowRunner",
            },
        )'''
assert txt.count(OLD2) == 1, "anchor2"
txt = txt.replace(OLD2, NEW2)

OLD3 = '''def now() -> str:
    return datetime.now(timezone.utc).isoformat()'''
NEW3 = '''def now() -> str:
    return datetime.now(timezone.utc).isoformat()


def _git_commit() -> str | None:
    try:
        import subprocess
        out = subprocess.run(["git", "rev-parse", "HEAD"], cwd=str(ROOT), capture_output=True,
                             text=True, timeout=20)
        return out.stdout.strip() or None
    except Exception:
        return None'''
assert txt.count(OLD3) == 1, "anchor3"
txt = txt.replace(OLD3, NEW3)

# --- 3. G0 / G2 use the new comparator signature ---
OLD4 = '''            fm_off, fm_sgd = load_fm(d_off), load_fm(d_sgd)
            same, diffs = same_final_metrics(fm_off, fm_sgd)'''
NEW4 = '''            fm_off, fm_sgd = load_fm(d_off), load_fm(d_sgd)
            same, det_diffs, all_diffs, wall = same_final_metrics(fm_off, fm_sgd)
            ck_a = d_off / "checkpoints" / "final.pt"
            ck_b = d_sgd / "checkpoints" / "final.pt"
            theta_identical = (ck_a.is_file() and ck_b.is_file()
                               and sha256_file(ck_a) == sha256_file(ck_b))'''
assert txt.count(OLD4) == 1, "anchor4"
txt = txt.replace(OLD4, NEW4)

OLD5 = '''                "bit_exact": same, "differences": diffs,'''
NEW5 = '''                "deterministic_bit_exact": same,
                "literal_bit_exact": not all_diffs,
                "deterministic_differences": det_diffs,
                "all_differences": all_diffs,
                "wall_clock_values": wall,
                "final_theta_bit_identical": bool(theta_identical),
                "final_theta_sha256": {
                    "baseline": sha256_file(ck_a) if ck_a.is_file() else None,
                    "identity": sha256_file(ck_b) if ck_b.is_file() else None,
                },'''
assert txt.count(OLD5) == 1, "anchor5"
txt = txt.replace(OLD5, NEW5)

OLD6 = '''            ok_all = ok_all and same
            print(f"   bit_exact={same}" + ("" if same else f"  diffs={diffs[:3]}"))'''
NEW6 = '''            ok_all = ok_all and same and theta_identical
            print(f"   deterministic_bit_exact={same}  theta_bit_identical={theta_identical}"
                  + ("" if same else f"  diffs={det_diffs[:3]}")
                  + (f"  wall_clock_excluded={wall}" if wall else ""))'''
assert txt.count(OLD6) == 1, "anchor6"
txt = txt.replace(OLD6, NEW6)

OLD7 = '''    return {"gate": "G0", "rule": "subclass(SGD, eta_s=eta) vs unmodified FullWindowRunner, bit-exact",'''
NEW7 = '''    return {"gate": "G0",
            "rule": "subclass(SGD, eta_s=eta) vs unmodified FullWindowRunner; deterministic fields "
                    "of final_metrics.json bit-exact AND final checkpoint byte-identical. "
                    "runtime_seconds is excluded and reported separately (wall clock)",'''
assert txt.count(OLD7) == 1, "anchor7"
txt = txt.replace(OLD7, NEW7)

OLD8 = '''    same, diffs = same_final_metrics(load_fm(d1), load_fm(d2))
    return {"gate": "G2", "rule": "same (block, arm, seed, config) twice -> identical final_metrics.json",
            "pass": bool(same), "differences": diffs,'''
NEW8 = '''    same, det_diffs, all_diffs, wall = same_final_metrics(load_fm(d1), load_fm(d2))
    return {"gate": "G2", "rule": "same (block, arm, seed, config) twice -> identical final_metrics.json "
                                  "on all deterministic fields; runtime_seconds excluded as wall clock",
            "pass": bool(same), "deterministic_differences": det_diffs,
            "all_differences": all_diffs, "wall_clock_values": wall,'''
assert txt.count(OLD8) == 1, "anchor8"
txt = txt.replace(OLD8, NEW8)

OLD9 = '''    lines += ["", "## G2 — determinism", "", f"- **pass: {g2['pass']}**",
              f"- differences: {'; '.join(g2['differences'][:5]) if g2['differences'] else 'none'}", ""]'''
NEW9 = '''    lines += ["", "## G2 — determinism", "", f"- **pass: {g2['pass']}**",
              f"- deterministic differences: "
              f"{'; '.join(g2.get('deterministic_differences', [])[:5]) or 'none'}",
              f"- wall-clock field excluded and reported: {g2.get('wall_clock_values') or 'none'}", ""]'''
assert txt.count(OLD9) == 1, "anchor9"
txt = txt.replace(OLD9, NEW9)

# --- 4. G0 table columns ---
OLD10 = '''        "| block | arm | seed | bit-exact | differences |",
        "| --- | --- | --- | --- | --- |",
    ]
    for r in g0["rows"]:
        lines.append(f"| {r['block']} | {r['arm']} | {r['seed']} | {r['bit_exact']} | "
                     f"{'; '.join(r['differences'][:3]) if r['differences'] else 'none'} |")'''
NEW10 = '''        "| block | arm | seed | deterministic bit-exact | final theta byte-identical | "
        "deterministic differences | wall-clock field |",
        "| --- | --- | --- | --- | --- | --- | --- |",
    ]
    for r in g0["rows"]:
        lines.append(f"| {r['block']} | {r['arm']} | {r['seed']} | {r['deterministic_bit_exact']} | "
                     f"{r['final_theta_bit_identical']} | "
                     f"{'; '.join(r['deterministic_differences'][:3]) or 'none'} | "
                     f"`runtime_seconds` (excluded) |")'''
assert txt.count(OLD10) == 1, "anchor10"
txt = txt.replace(OLD10, NEW10)

# --- 5. G0 pass definition uses deterministic + theta ---
OLD11 = '''    g0 = gate_g0()
    print(f"G0 pass={g0['pass']}")
    if not g0["pass"]:'''
NEW11 = '''    g0 = gate_g0()
    print(f"G0 pass={g0['pass']}")
    dump_json({"g1": g1, "g0": g0}, OUT / "S1P_GATES_PARTIAL.json")
    if not g0["pass"]:'''
assert txt.count(OLD11) == 1, "anchor11"
txt = txt.replace(OLD11, NEW11)

# --- 6. CLI stages ---
OLD12 = '''    ap.add_argument("--stage", choices=("gates",), default="gates")'''
NEW12 = '''    ap.add_argument("--stage", choices=("gates", "g2"), default="gates")'''
assert txt.count(OLD12) == 1, "anchor12"
txt = txt.replace(OLD12, NEW12)

OLD13 = '''    args = ap.parse_args()
    return cmd_gates(args)'''
NEW13 = '''    args = ap.parse_args()
    if args.stage == "g2":
        OUT.mkdir(parents=True, exist_ok=True)
        g2 = gate_g2()
        dump_json(g2, OUT / "S1P_G2.json")
        print(f"G2 pass={g2['pass']}")
        return 0 if g2["pass"] else 3
    return cmd_gates(args)'''
assert txt.count(OLD13) == 1, "anchor13"
txt = txt.replace(OLD13, NEW13)

p.write_text(txt, encoding="utf-8")
print("patched;", len(txt.splitlines()), "lines")
