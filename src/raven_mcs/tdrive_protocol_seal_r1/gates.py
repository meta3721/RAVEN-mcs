"""TDPS-G1 … TDPS-G42 gates for T-Drive real-mobility protocol seal R1."""

from __future__ import annotations

from pathlib import Path
from typing import Any

from raven_mcs.paper_data_r1.io_util import read_csv, read_json, write_json
from raven_mcs.tdrive_protocol_seal_r1.constants import FORMAL_SEEDS, METHODS, PRIMARY_METRICS


def _pass(ok: bool, detail: str) -> dict[str, Any]:
    return {"pass": bool(ok), "detail": detail}


def run_gates(root: Path, out: Path) -> dict[str, Any]:
    root = Path(root)
    out = Path(out)
    r: dict[str, dict[str, Any]] = {}

    att = read_json(out / "00_inventory/TDRIVE_PROTOCOL_NO_RUN_ATTESTATION.json")
    r["TDPS-G1"] = _pass(att.get("formal_run_started") is False and att.get("training_started") is False, "formal/training started false")
    r["TDPS-G2"] = _pass(att.get("canary_started") is False, "canary started false")

    raw = read_json(out / "01_dataset/TDRIVE_RAW_DATA_IDENTITY.json")
    r["TDPS-G3"] = _pass(raw.get("status") == "HASH_BOUND" and raw.get("all_raw_hashes_match_manifest") is True, str(raw.get("status")))
    proc = read_json(out / "01_dataset/TDRIVE_PROCESSED_DATA_IDENTITY.json")
    r["TDPS-G4"] = _pass(proc.get("status") == "HASH_BOUND", str(proc.get("status")))

    speed = read_json(out / "02_semantics/TDRIVE_SPEED_TARGET_SEMANTICS.json")
    r["TDPS-G5"] = _pass(speed.get("status") == "RECOVERED" and speed.get("processed_source_conflict") is False, speed.get("status"))
    tz = read_json(out / "02_semantics/TDRIVE_TIMEZONE_SEAL.json")
    r["TDPS-G6"] = _pass(tz.get("status") == "FROZEN" and tz.get("conversion_applied") is False, tz.get("status"))
    client = read_json(out / "02_semantics/TDRIVE_CLIENT_IDENTITY_SEAL.json")
    r["TDPS-G7"] = _pass(client.get("status") == "FROZEN" and client.get("whether_identity_is_real_vehicle") is True, client.get("status"))
    grid = read_json(out / "02_semantics/TDRIVE_SPATIAL_GRID_SEAL.json")
    r["TDPS-G8"] = _pass(grid.get("status") == "FROZEN" and grid.get("cell_meters") == 500, str(grid.get("cell_meters")))
    slot = read_json(out / "02_semantics/TDRIVE_TIME_SLOT_SEAL.json")
    r["TDPS-G9"] = _pass(slot.get("status") == "FROZEN" and slot.get("slot_duration_minutes") == 30, str(slot.get("slot_duration_minutes")))
    atomic = read_json(out / "02_semantics/TDRIVE_ATOMIC_UNIT_SEAL.json")
    r["TDPS-G10"] = _pass(atomic.get("status") == "FROZEN" and atomic.get("row_uniqueness") is True, atomic.get("status"))

    h = read_json(out / "03_target/TDRIVE_TARGET_H_SEAL.json")
    r["TDPS-G11"] = _pass(
        h.get("status") == "FROZEN" and h.get("label") == "PRE_REGISTERED_PROTOCOL_FALLBACK" and h.get("h_distinct_from_s") is True,
        h.get("label"),
    )
    mu = read_json(out / "03_target/TDRIVE_TARGET_MU_SEAL.json")
    r["TDPS-G12"] = _pass(mu.get("sum_ok") is True and mu.get("uses_speed_labels") is False, f"sum_ok={mu.get('sum_ok')}")
    s = read_json(out / "03_target/TDRIVE_OPPORTUNITY_STRATUM_SEAL.json")
    r["TDPS-G13"] = _pass(s.get("status") == "FROZEN" and s.get("h_equals_s") is False, s.get("status"))

    rseal = read_json(out / "04_selection/TDRIVE_REAL_MOBILITY_OPPORTUNITY_SEAL.json")
    r["TDPS-G14"] = _pass(rseal.get("classification") == "REAL_FROM_TDRIVE" and rseal.get("status") == "FROZEN", rseal.get("classification"))
    o = read_json(out / "04_selection/TDRIVE_OBSERVATION_SEAL.json")
    r["TDPS-G15"] = _pass("CONTROLLED_OBSERVATION" in str(o.get("eventtrace_layer", {}).get("label", "")), "O labelled")
    u = read_json(out / "04_selection/TDRIVE_USABLE_UPDATE_SEAL.json")
    r["TDPS-G16"] = _pass(u.get("classification") == "CONTROLLED_EXPERIMENTAL" and u.get("tdrive_contains_real_compute_network_deadline") is False, u.get("classification"))
    xw = read_json(out / "04_selection/TDRIVE_SELECTION_CROSSWALK.json")
    r["TDPS-G17"] = _pass(xw.get("only_opportunity_guaranteed_real") is True and len(xw.get("pipeline", [])) >= 6, "crosswalk")

    spl = read_json(out / "05_split/TDRIVE_SPLIT_SEAL.json")
    r["TDPS-G18"] = _pass(spl.get("status") == "FROZEN", spl.get("status"))
    leak = read_json(out / "05_split/TDRIVE_SPLIT_LEAKAGE_AUDIT.json")
    r["TDPS-G19"] = _pass(leak.get("all_pass") is True or leak.get("status") == "PASS", str(leak.get("status")))

    seed = read_json(out / "06_eventtrace/TDRIVE_SEED_POLICY_SEAL.json")
    r["TDPS-G20"] = _pass(list(seed.get("formal_seeds", [])) == list(FORMAL_SEEDS), str(seed.get("formal_seeds")))
    schema = read_json(out / "06_eventtrace/TDRIVE_EVENTTRACE_SCHEMA.json")
    r["TDPS-G21"] = _pass(schema.get("status") == "FROZEN", schema.get("status"))
    gen = read_json(out / "06_eventtrace/TDRIVE_EVENTTRACE_GENERATOR_SEAL.json")
    r["TDPS-G22"] = _pass(gen.get("status") == "FROZEN" and bool(gen.get("source_hashes")), "generator hashes")
    fx = read_json(out / "06_eventtrace/TDRIVE_EVENTTRACE_MICRO_FIXTURE_AUDIT.json")
    r["TDPS-G23"] = _pass(fx.get("status") == "PASS" and fx.get("checks", {}).get("method_independence") is True, fx.get("status"))

    mset = read_json(out / "07_methods/TDRIVE_METHOD_SET_SEAL.json")
    canon = [m["canonical"] for m in METHODS]
    r["TDPS-G24"] = _pass(int(mset.get("n_methods", 0)) == 5 and [m["canonical"] for m in mset.get("methods", [])] == canon, str(mset.get("n_methods")))
    ident = read_csv(out / "07_methods/TDRIVE_METHOD_IDENTITY.csv")
    hashed = all(str(row.get("implementation_hash_now", "")) for row in ident) and len(ident) == 5
    r["TDPS-G25"] = _pass(hashed, f"n_identity={len(ident)}")
    raven = read_json(out / "07_methods/TDRIVE_RAVEN_CONFIG_SEAL.json")
    r["TDPS-G26"] = _pass(raven.get("tdrive_test_tuned") is False and raven.get("status") == "FROZEN", raven.get("policy"))
    base = read_csv(out / "07_methods/TDRIVE_BASELINE_CONFIG_SEAL.csv")
    r["TDPS-G27"] = _pass(len(base) == 4 and all(str(x.get("intentionally_weakened")).lower() in {"false", "0"} for x in base), f"n_baselines={len(base)}")

    reg = read_json(out / "08_metrics/TDRIVE_METRIC_REGISTRY.json")
    r["TDPS-G28"] = _pass(
        list(reg.get("primary_structural", [])) + list(reg.get("primary_predictive", [])) == list(PRIMARY_METRICS),
        str(PRIMARY_METRICS),
    )
    dg = read_json(out / "08_metrics/TDRIVE_DELTA_GROUP_SEAL.json")
    r["TDPS-G29"] = _pass("||omega_hat - mu||_1" in str(dg.get("formula", "")) and dg.get("must_not_use_s_as_h") is True, dg.get("formula"))
    dcs = read_json(out / "08_metrics/TDRIVE_DELTA_C_S_SEAL.json")
    r["TDPS-G30"] = _pass("client × opportunity_stratum" in str(dcs.get("support", "")) and "h(i)" in str(dcs.get("forbidden_support", "")), dcs.get("support"))
    rmse = read_json(out / "08_metrics/TDRIVE_RMSE_MU_SEAL.json")
    r["TDPS-G31"] = _pass(rmse.get("status") == "FROZEN" and rmse.get("test_set_tuned") is False, rmse.get("formula"))
    rho = read_json(out / "08_metrics/TDRIVE_RMSE_RHO_READINESS.json")
    allowed = {"AVAILABLE_FINAL_ATOMIC", "NOT_AVAILABLE_MISSING_FACTOR", "NOT_COMPARABLE", "NOT_REQUIRED_FOR_TDRIVE_PRIMARY_CLAIM"}
    r["TDPS-G32"] = _pass(rho.get("classification") in allowed, str(rho.get("classification")))

    st = read_json(out / "09_statistics/TDRIVE_STATISTICAL_PROTOCOL_SEAL.json")
    r["TDPS-G33"] = _pass(st.get("status") == "FROZEN" and st.get("EPS_ZERO") == 1e-12, "stats")
    rules = read_json(out / "09_statistics/TDRIVE_CLAIM_DECISION_RULES.json")
    r["TDPS-G34"] = _pass(rules.get("success_is_not_rmse_mu_win") is True, "claim rules")

    matrix = read_csv(out / "11_future_run_matrix/TDRIVE_FUTURE_FORMAL_RUN_MATRIX_50.csv")
    r["TDPS-G35"] = _pass(len(matrix) == 50 and all(str(x.get("status")) == "NOT_AUTHORIZED_YET" for x in matrix), f"n={len(matrix)}")
    canary = read_csv(out / "11_future_run_matrix/TDRIVE_FUTURE_CANARY_PLAN.csv")
    r["TDPS-G36"] = _pass(
        len(canary) == 5
        and all(str(x.get("status")) == "NOT_AUTHORIZED_YET" for x in canary)
        and att.get("canary_started") is False,
        f"n_canary={len(canary)}",
    )
    compat = read_csv(out / "12_audits/TDRIVE_METHOD_DATA_COMPATIBILITY.csv")
    r["TDPS-G37"] = _pass(len(compat) == 5 and all(str(x.get("classification")) in {"COMPATIBLE", "ADAPTER_FIX_REQUIRED", "SCIENTIFIC_SEMANTIC_MISMATCH"} for x in compat), f"n={len(compat)}")
    wording = out / "12_audits/TDRIVE_EXTERNAL_VALIDITY_WORDING_SEAL.md"
    wtxt = wording.read_text(encoding="utf-8") if wording.is_file() else ""
    r["TDPS-G38"] = _pass("Allowed" in wtxt and "Forbidden" in wtxt, "wording seal")

    freeze = read_json(out / "13_freeze/TDRIVE_PROTOCOL_SOURCE_FREEZE.json")
    r["TDPS-G39"] = _pass(freeze.get("status") == "FROZEN" and bool(freeze.get("source_files")), "source freeze")
    master = read_json(out / "13_freeze/TDRIVE_REAL_MOBILITY_PROTOCOL_MASTER_R1.json")
    needed = ["dataset_identity", "h_i", "s_i", "R", "O", "U", "split", "methods", "metrics"]
    r["TDPS-G40"] = _pass(all(k in master for k in needed), "master keys")

    npt = read_json(out / "00_inventory/TDRIVE_NO_PERFORMANCE_TUNING_ATTESTATION.json")
    r["TDPS-G41"] = _pass(npt.get("result_dependent_semantic_choice") is False, "no result-dependent choice")
    r["TDPS-G42"] = _pass(
        npt.get("grid_chosen_by_test_metric") is False
        and npt.get("slot_chosen_by_test_metric") is False
        and npt.get("target_h_chosen_by_test_metric") is False
        and npt.get("split_chosen_by_test_metric") is False
        and npt.get("raven_config_tuned_on_tdrive_test") is False,
        "no test-metric protocol choices",
    )

    n_pass = sum(1 for v in r.values() if v["pass"])
    payload = {
        "gates": r,
        "n_pass": n_pass,
        "n_total": len(r),
        "all_pass": n_pass == len(r) == 42,
    }
    write_json(out / "13_freeze/TDRIVE_PROTOCOL_GATES_R1.json", payload)
    write_json(out / "TDRIVE_PROTOCOL_GATES_R1.json", payload)
    return payload
