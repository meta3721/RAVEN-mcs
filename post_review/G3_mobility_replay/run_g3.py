"""G3: real-mobility opportunity replay diagnostics.

Read-only on sealed T-Drive processed data and E3 EventTraces.
No model training. Does not write into tdrive_protocol_seal_r1/.
"""

from __future__ import annotations

import hashlib
import json
from pathlib import Path

import matplotlib.pyplot as plt
import numpy as np
import pandas as pd

from raven_mcs.data.controlled import time_of_day_block
from raven_mcs.e3.real_runner.stage2_r3 import compute_usable_r3
from raven_mcs.simulation.event_trace import load_event_trace
from raven_mcs.tdrive_protocol_seal_r1.constants import (
    MEAN_OBSERVATION_RATE,
    S_MAX,
    WINDOW_DURATION,
)
from raven_mcs.tdrive_protocol_seal_r1.eventtrace_generator import fallback_h_id

ROOT = Path(__file__).resolve().parents[2]
OUT = Path(__file__).resolve().parent
TAB = OUT / "tables"
FIG = OUT / "figures"

ATOMIC_PATH = ROOT / "data/processed/tdrive_speed/atomic_units.parquet"
MEAS_PATH = ROOT / "data/processed/tdrive_speed/client_measurements.parquet"
IDENTITY_PATH = ROOT / "tdrive_protocol_seal_r1/01_dataset/TDRIVE_PROCESSED_DATA_IDENTITY.json"
H_SEAL_PATH = ROOT / "tdrive_protocol_seal_r1/03_target/TDRIVE_TARGET_H_SEAL.json"
ET_ROOT = ROOT / "artifacts/e3_formal_runs_r1/eventtraces"

H_ORDER = ("H1", "H2", "H3", "H4")
TV_THRESHOLD = 0.05
U_MC_N = 20000
U_MC_SEED = 30001
PROTOCOL_SEED = 30001


def _sha256_file(path: Path) -> str:
    h = hashlib.sha256()
    with path.open("rb") as f:
        for chunk in iter(lambda: f.read(1 << 20), b""):
            h.update(chunk)
    return h.hexdigest()


def _tv(p: dict[str, float], q: dict[str, float], keys: tuple[str, ...]) -> float:
    return 0.5 * float(sum(abs(p.get(k, 0.0) - q.get(k, 0.0)) for k in keys))


def _gini(x: np.ndarray) -> float:
    x = np.asarray(x, dtype=np.float64)
    x = x[np.isfinite(x)]
    if x.size == 0 or float(np.sum(x)) <= 0:
        return float("nan")
    x = np.sort(np.clip(x, 0.0, None))
    n = x.size
    return float((2.0 * np.sum(np.arange(1, n + 1) * x) / (n * np.sum(x))) - (n + 1) / n)


def _entropy(p: np.ndarray) -> float:
    p = np.asarray(p, dtype=np.float64)
    p = p[p > 0]
    if p.size == 0:
        return float("nan")
    p = p / p.sum()
    return float(-np.sum(p * np.log(p)))


def _burstiness(gaps: np.ndarray) -> float:
    if gaps.size < 2:
        return float("nan")
    mu = float(np.mean(gaps))
    sd = float(np.std(gaps, ddof=1))
    if mu + sd <= 0:
        return float("nan")
    return float((sd - mu) / (sd + mu))


def _freq(labels: pd.Series, keys: tuple[str, ...]) -> dict[str, float]:
    counts = labels.value_counts()
    total = float(counts.sum())
    if total <= 0:
        return {k: 0.0 for k in keys}
    return {k: float(counts.get(k, 0)) / total for k in keys}


def _quantiles(x: np.ndarray) -> dict[str, float]:
    x = np.asarray(x, dtype=np.float64)
    x = x[np.isfinite(x)]
    if x.size == 0:
        return {k: float("nan") for k in ("n", "mean", "std", "min", "p10", "p50", "p90", "max")}
    qs = np.quantile(x, [0.0, 0.10, 0.50, 0.90, 1.0])
    return {
        "n": int(x.size),
        "mean": float(np.mean(x)),
        "std": float(np.std(x, ddof=1)) if x.size > 1 else 0.0,
        "min": float(qs[0]),
        "p10": float(qs[1]),
        "p50": float(qs[2]),
        "p90": float(qs[3]),
        "max": float(qs[4]),
    }


def verify_processed_hashes() -> dict:
    identity = json.loads(IDENTITY_PATH.read_text(encoding="utf-8"))
    atomic_sha = _sha256_file(ATOMIC_PATH)
    meas_sha = _sha256_file(MEAS_PATH)
    return {
        "atomic_sha256": atomic_sha,
        "atomic_match": atomic_sha == identity["atomic_units"]["sha256"],
        "measurements_sha256": meas_sha,
        "measurements_match": meas_sha == identity["client_measurements"]["sha256"],
        "rewritten_in_r1": identity.get("rewritten_in_r1"),
        "status": identity.get("status"),
    }


def load_tdrive() -> tuple[pd.DataFrame, pd.DataFrame]:
    atomic = pd.read_parquet(
        ATOMIC_PATH,
        columns=[
            "unit_id",
            "spatial_id",
            "absolute_time",
            "time_index",
            "split",
            "opportunity_stratum",
        ],
    )
    atomic["unit_id"] = atomic["unit_id"].astype(str)
    atomic["spatial_id"] = atomic["spatial_id"].astype(str)
    atomic["split"] = atomic["split"].astype(str)
    atomic["opportunity_stratum"] = atomic["opportunity_stratum"].astype(str)
    atomic["time_index"] = atomic["time_index"].astype(int)
    atomic["absolute_time"] = pd.to_datetime(atomic["absolute_time"], utc=True)
    atomic["h_id"] = [fallback_h_id(t) for t in atomic["absolute_time"]]
    meas = pd.read_parquet(MEAS_PATH, columns=["client_id", "unit_id"])
    meas["client_id"] = meas["client_id"].astype(str)
    meas["unit_id"] = meas["unit_id"].astype(str)
    return atomic, meas


def tdrive_mobility(atomic: pd.DataFrame, meas: pd.DataFrame, mu_seal: dict) -> dict:
    train_atomic = atomic.loc[atomic["split"] == "train"].copy()
    test_atomic = atomic.loc[atomic["split"] == "test"].copy()
    train_units = set(train_atomic["unit_id"])
    r = meas.loc[meas["unit_id"].isin(train_units)].merge(
        train_atomic[["unit_id", "spatial_id", "time_index", "h_id", "opportunity_stratum", "absolute_time"]],
        on="unit_id",
        how="inner",
    )
    if r.empty:
        raise RuntimeError("T-Drive train R is empty after join")

    mu_emp = _freq(test_atomic["h_id"], H_ORDER)
    mu_seal_h = {g["h_id"]: float(g["mu"]) for g in mu_seal["groups"]}
    pi_real = _freq(r["h_id"], H_ORDER)
    pi_bal = _freq(train_atomic["h_id"], H_ORDER)
    pi_flat = {k: 0.25 for k in H_ORDER}

    test_strata = set(test_atomic["opportunity_stratum"])
    train_r_strata = set(r["opportunity_stratum"])
    train_only_r_strata = train_r_strata - test_strata
    zero_h_test = {h for h in H_ORDER if int((test_atomic["h_id"] == h).sum()) == 0}
    r_units = r.drop_duplicates("unit_id")
    frac_units_zero_stratum = float(r_units["opportunity_stratum"].isin(train_only_r_strata).mean())

    slots = np.sort(train_atomic["time_index"].unique())
    n_slots = int(slots.size)
    slot_min, slot_max = int(slots[0]), int(slots[-1])
    slot_cut_half = slot_min + 0.50 * (slot_max - slot_min)
    slot_cut_late = slot_min + 0.80 * (slot_max - slot_min)

    client_slots = {
        cid: np.sort(vals.unique())
        for cid, vals in r.groupby("client_id", sort=False)["time_index"]
    }
    active_per_slot = r.groupby("time_index")["client_id"].nunique()
    n_clients = int(r["client_id"].nunique())
    active_frac = (active_per_slot / n_clients).reindex(slots, fill_value=0.0).to_numpy(dtype=float)

    gaps_all = []
    n_with_gap = 0
    early_and_late = 0
    early_not_late = 0
    slots_active = []
    for times in client_slots.values():
        times = np.asarray(times, dtype=int)
        slots_active.append(times.size)
        if times.size >= 2:
            gaps_all.append(np.diff(times))
            n_with_gap += 1
        early = bool(np.any(times <= slot_cut_half))
        late = bool(np.any(times > slot_cut_late))
        if early and late:
            early_and_late += 1
        elif early and not late:
            early_not_late += 1
    gaps = np.concatenate(gaps_all) if gaps_all else np.asarray([], dtype=float)
    per_client_burst = np.asarray(
        [_burstiness(np.diff(np.asarray(t, dtype=float))) for t in client_slots.values() if len(t) >= 3],
        dtype=float,
    )

    stratum_counts = r.groupby("opportunity_stratum").size().to_numpy(dtype=float)
    stratum_p = stratum_counts / stratum_counts.sum()
    top_decile = max(1, int(np.ceil(0.10 * stratum_counts.size)))
    top_decile_share = float(np.sort(stratum_counts)[::-1][:top_decile].sum() / stratum_counts.sum())

    times = np.sort(train_atomic["absolute_time"].unique())
    if times.size >= 2:
        slot_hours = float(np.median(np.diff(times).astype("timedelta64[s]").astype(float)) / 3600.0)
    else:
        slot_hours = float("nan")

    n_client_windows = int(r.groupby(["client_id", "time_index"]).ngroups)

    return {
        "n_train_atomic": int(len(train_atomic)),
        "n_test_atomic": int(len(test_atomic)),
        "n_train_R_events": int(len(r)),
        "n_clients_with_R": n_clients,
        "n_client_windows": n_client_windows,
        "n_train_slots": n_slots,
        "slot_hours_median": slot_hours,
        "n_spatial_cells_atomic": int(atomic["spatial_id"].nunique()),
        "n_spatial_cells_train_atomic": int(train_atomic["spatial_id"].nunique()),
        "n_spatial_cells_train_R": int(r["spatial_id"].nunique()),
        "cell_coverage_vs_train_atomic": float(r["spatial_id"].nunique() / max(train_atomic["spatial_id"].nunique(), 1)),
        "unit_coverage_vs_train_atomic": float(r["unit_id"].nunique() / max(len(train_atomic), 1)),
        "mean_R_per_train_unit": float(len(r) / max(len(train_atomic), 1)),
        "mu_test_empirical": mu_emp,
        "mu_test_seal": mu_seal_h,
        "mu_tv_empirical_vs_seal": _tv(mu_emp, mu_seal_h, H_ORDER),
        "pi_opp_real_R": pi_real,
        "pi_opp_balanced_unit": pi_bal,
        "pi_opp_balanced_flat": pi_flat,
        "tv_real_vs_mu": _tv(pi_real, mu_seal_h, H_ORDER),
        "tv_balanced_unit_vs_mu": _tv(pi_bal, mu_seal_h, H_ORDER),
        "tv_balanced_flat_vs_mu": _tv(pi_flat, mu_seal_h, H_ORDER),
        "n_zero_support_h_on_test": int(len(zero_h_test)),
        "n_train_R_strata": int(len(train_r_strata)),
        "n_test_strata": int(len(test_strata)),
        "n_train_only_R_strata": int(len(train_only_r_strata)),
        "frac_train_R_strata_zero_test": float(len(train_only_r_strata) / max(len(train_r_strata), 1)),
        "frac_train_R_units_zero_test_stratum": frac_units_zero_stratum,
        "client_active_fraction": _quantiles(active_frac),
        "slots_active_per_client": _quantiles(np.asarray(slots_active, dtype=float)),
        "interarrival_slots": _quantiles(gaps.astype(float)),
        "interarrival_hours": _quantiles(gaps.astype(float) * slot_hours) if np.isfinite(slot_hours) else {},
        "burstiness_pooled_gaps": _burstiness(gaps.astype(float)),
        "burstiness_per_client": _quantiles(per_client_burst),
        "n_clients_with_gap": n_with_gap,
        "dropout_early_not_late": int(early_not_late),
        "dropout_rate_among_early": float(early_not_late / max(early_and_late + early_not_late, 1)),
        "stratum_visit_gini": _gini(stratum_counts),
        "stratum_visit_entropy": _entropy(stratum_p),
        "stratum_visit_cv": float(np.std(stratum_counts, ddof=1) / np.mean(stratum_counts)),
        "stratum_top_decile_share": top_decile_share,
        "spatial_R_cv": float(
            r.groupby("spatial_id").size().std(ddof=1) / r.groupby("spatial_id").size().mean()
        ),
    }


def protocol_dataset(name: str) -> dict:
    atomic = pd.read_parquet(
        ROOT / f"data/processed/{name}/atomic_units.parquet",
        columns=["unit_id", "spatial_id", "absolute_time", "split", "opportunity_stratum"],
    )
    atomic["unit_id"] = atomic["unit_id"].astype(str)
    atomic["spatial_id"] = atomic["spatial_id"].astype(str)
    atomic["split"] = atomic["split"].astype(str)
    atomic["absolute_time"] = pd.to_datetime(atomic["absolute_time"], utc=True)
    atomic["h_id"] = [f"H{int(time_of_day_block(t)) + 1}" for t in atomic["absolute_time"]]
    train = atomic.loc[atomic["split"] == "train"]
    test = atomic.loc[atomic["split"] == "test"]
    mu = _freq(test["h_id"], H_ORDER)
    pi_bal = _freq(train["h_id"], H_ORDER)

    trace, _ident = load_event_trace(ET_ROOT / name / f"seed{PROTOCOL_SEED}" / "training_eventtrace")
    ev = trace.events
    rows = []
    for rec in ev.itertuples(index=False):
        risk = list(getattr(rec, "risk_set_unit_ids") or [])
        for uid in risk:
            rows.append({"client_id": str(rec.client_id), "window_id": int(rec.window_id), "unit_id": str(uid)})
    long = pd.DataFrame(rows)
    long = long.merge(atomic[["unit_id", "spatial_id", "h_id", "opportunity_stratum"]], on="unit_id", how="left")
    pi_prot = _freq(long["h_id"], H_ORDER)

    n_windows = int(ev["window_id"].nunique())
    n_clients = int(ev["client_id"].nunique())
    active = ev.groupby("window_id")["client_id"].nunique() / max(n_clients, 1)
    client_windows = {
        cid: np.sort(vals.unique())
        for cid, vals in ev.groupby("client_id", sort=False)["window_id"]
    }
    gaps = []
    for times in client_windows.values():
        times = np.asarray(times, dtype=int)
        if times.size >= 2:
            gaps.append(np.diff(times))
    gaps = np.concatenate(gaps) if gaps else np.asarray([], dtype=float)
    test_strata = set(test["opportunity_stratum"].astype(str))
    r_strata = set(long["opportunity_stratum"].dropna().astype(str))
    return {
        "dataset": name,
        "source": "e3-complete-aligned EventTrace risk sets (protocol-generated R)",
        "seed": PROTOCOL_SEED,
        "n_clients": n_clients,
        "n_windows": n_windows,
        "n_R_client_units": int(len(long)),
        "mean_client_active_fraction": float(active.mean()) if len(active) else float("nan"),
        "interarrival_windows": _quantiles(gaps.astype(float)),
        "burstiness_pooled_gaps": _burstiness(gaps.astype(float)),
        "mu_test": mu,
        "pi_opp_protocol": pi_prot,
        "pi_opp_balanced_unit": pi_bal,
        "tv_protocol_vs_mu": _tv(pi_prot, mu, H_ORDER),
        "tv_balanced_unit_vs_mu": _tv(pi_bal, mu, H_ORDER),
        "frac_train_R_strata_zero_test": float(len(r_strata - test_strata) / max(len(r_strata), 1)),
        "cell_coverage_vs_train_atomic": float(
            long["spatial_id"].nunique() / max(train["spatial_id"].nunique(), 1)
        ),
        "g1_opp_tv_realized_vs_target": {"sensorscope": 0.28929050586510274, "uair": 0.4243892492138365}[name],
        "g1_frac_pi_tar_zero": {"sensorscope": 0.0, "uair": 0.2546875}[name],
    }


def usable_layer_mc() -> dict:
    rng = np.random.default_rng(U_MC_SEED)
    recs = []
    for i in range(U_MC_N):
        has_obs = bool(rng.random() < MEAN_OBSERVATION_RATE)
        window_id = int(i % 64)
        usable = compute_usable_r3(
            rng=rng,
            registration_time=float(window_id) + 0.1,
            window_deadline=float(window_id) + WINDOW_DURATION,
            window_id=window_id,
            s_max=int(S_MAX),
            has_observations=has_obs,
        )
        recs.append(
            {
                "O": int(has_obs),
                "U": int(usable["U"]),
                "deadline_miss": int(not usable["deadline_pass"]),
                "staleness_fail": int(not usable["staleness_pass"]),
                "compute_fail": int(not usable["compute_success"]),
                "network_fail": int(not usable["network_success"]),
                "tau": int(usable["tau"]),
            }
        )
    df = pd.DataFrame(recs)
    given_o = df.loc[df["O"] == 1]
    return {
        "classification": "CONTROLLED_EXPERIMENTAL",
        "source": "raven_mcs.e3.real_runner.stage2_r3.compute_usable_r3",
        "p_obs": MEAN_OBSERVATION_RATE,
        "s_max": S_MAX,
        "n": U_MC_N,
        "seed": U_MC_SEED,
        "observation_rate": float(df["O"].mean()),
        "usable_update_rate_given_R": float(df["U"].mean()),
        "usable_update_rate_given_O": float(given_o["U"].mean()) if len(given_o) else float("nan"),
        "deadline_miss_rate_given_R": float(df["deadline_miss"].mean()),
        "staleness_fail_rate_given_R": float(df["staleness_fail"].mean()),
        "compute_fail_rate_given_R": float(df["compute_fail"].mean()),
        "network_fail_rate_given_R": float(df["network_fail"].mean()),
        "deadline_miss_rate_given_O": float(given_o["deadline_miss"].mean()) if len(given_o) else float("nan"),
        "staleness_fail_rate_given_O": float(given_o["staleness_fail"].mean()) if len(given_o) else float("nan"),
        "compute_fail_rate_given_O": float(given_o["compute_fail"].mean()) if len(given_o) else float("nan"),
        "network_fail_rate_given_O": float(given_o["network_fail"].mean()) if len(given_o) else float("nan"),
        "tau_mean": float(df["tau"].mean()),
        "tau_p90": float(np.quantile(df["tau"], 0.90)),
        "frac_tau_gt_smax": float((df["tau"] > S_MAX).mean()),
        "not_real_tdrive_device_logs": True,
    }


def decide(td: dict, proto: dict[str, dict], u_layer: dict, hashes: dict) -> dict:
    rq1 = {
        "tdrive_real": float(td["tv_real_vs_mu"]),
        "tdrive_balanced_unit": float(td["tv_balanced_unit_vs_mu"]),
        "sensorscope_protocol": float(proto["sensorscope"]["tv_protocol_vs_mu"]),
        "uair_protocol": float(proto["uair"]["tv_protocol_vs_mu"]),
        "threshold": TV_THRESHOLD,
    }
    rq1_flags = {
        k: (v > TV_THRESHOLD)
        for k, v in rq1.items()
        if k != "threshold" and k != "tdrive_balanced_unit"
    }
    stratum_mismatch = float(td["frac_train_R_strata_zero_test"]) > TV_THRESHOLD
    h_ok = bool(rq1_flags["tdrive_real"] and rq1_flags["sensorscope_protocol"] and rq1_flags["uair_protocol"])
    if not hashes["atomic_match"] or not hashes["measurements_match"]:
        verdict = "G3_FAIL"
        reason = "processed T-Drive hashes do not match the protocol seal"
    elif h_ok:
        verdict = "G3_ACCEPTED"
        reason = "4-block TV exceeds 0.05 on real T-Drive R and on both protocol-generated datasets"
    elif stratum_mismatch or float(td["tv_real_vs_mu"]) > 0:
        verdict = "G3_RQ1_WEAK"
        reason = "4-block T-Drive TV is at or below 0.05; mismatch remains at stratum/spatial layer or is only weak at H"
    else:
        verdict = "G3_FAIL"
        reason = "real-trace mismatch absent at both H and stratum layers"

    rq2 = {
        "method_ranking_on_tdrive": "NOT_RUN",
        "n_zero_support_h_on_test": td["n_zero_support_h_on_test"],
        "frac_train_R_units_zero_test_stratum": td["frac_train_R_units_zero_test_stratum"],
        "frac_train_R_strata_zero_test": td["frac_train_R_strata_zero_test"],
        "g1_uair_frac_pi_tar_zero": 0.2546875,
        "g1_sensorscope_frac_pi_tar_zero": 0.0,
    }
    if td["n_zero_support_h_on_test"] == 0 and float(td["frac_train_R_units_zero_test_stratum"]) < 0.05:
        rq2["predicted_design_default"] = "keep Design if it keys on H1-H4 only (SensorScope-like H support)"
    elif float(td["frac_train_R_units_zero_test_stratum"]) >= 0.20:
        rq2["predicted_design_default"] = (
            "if Design keys on s=spatial×block×weekday test mass, expect U-Air-like support shift; "
            "H1-H4 support is complete. Do not change Path B from this diagnostic alone."
        )
    else:
        rq2["predicted_design_default"] = "inconclusive without T-Drive training"

    return {
        "verdict": verdict,
        "reason": reason,
        "evidence_level": "A",
        "rq1": rq1,
        "rq1_clears_threshold": rq1_flags,
        "rq2": rq2,
        "u_layer_controlled": True,
        "usable_update_rate_given_R": u_layer["usable_update_rate_given_R"],
        "seal_dir_written": False,
        "formal_tdrive_training": False,
    }


def write_tables(td: dict, proto: dict[str, dict], u_layer: dict, hashes: dict, decision: dict) -> None:
    TAB.mkdir(parents=True, exist_ok=True)
    FIG.mkdir(parents=True, exist_ok=True)

    h_rows = []
    for h in H_ORDER:
        h_rows.append(
            {
                "h_id": h,
                "mu_test_seal": td["mu_test_seal"][h],
                "pi_opp_real_R": td["pi_opp_real_R"][h],
                "pi_opp_balanced_unit": td["pi_opp_balanced_unit"][h],
                "pi_opp_balanced_flat": td["pi_opp_balanced_flat"][h],
            }
        )
    pd.DataFrame(h_rows).to_csv(TAB / "tdrive_h_mass.csv", index=False)

    cmp_rows = []
    for name, row in (
        (
            "tdrive_real",
            {
                "R_source": "real T-Drive trajectories",
                "tv_opp_vs_mu": td["tv_real_vs_mu"],
                "tv_balanced_unit_vs_mu": td["tv_balanced_unit_vs_mu"],
                "mean_active_frac": td["client_active_fraction"]["mean"],
                "burstiness": td["burstiness_pooled_gaps"],
                "frac_zero_test_stratum": td["frac_train_R_strata_zero_test"],
            },
        ),
        (
            "sensorscope_protocol",
            {
                "R_source": "protocol-generated Complete-aligned",
                "tv_opp_vs_mu": proto["sensorscope"]["tv_protocol_vs_mu"],
                "tv_balanced_unit_vs_mu": proto["sensorscope"]["tv_balanced_unit_vs_mu"],
                "mean_active_frac": proto["sensorscope"]["mean_client_active_fraction"],
                "burstiness": proto["sensorscope"]["burstiness_pooled_gaps"],
                "frac_zero_test_stratum": proto["sensorscope"]["frac_train_R_strata_zero_test"],
            },
        ),
        (
            "uair_protocol",
            {
                "R_source": "protocol-generated Complete-aligned",
                "tv_opp_vs_mu": proto["uair"]["tv_protocol_vs_mu"],
                "tv_balanced_unit_vs_mu": proto["uair"]["tv_balanced_unit_vs_mu"],
                "mean_active_frac": proto["uair"]["mean_client_active_fraction"],
                "burstiness": proto["uair"]["burstiness_pooled_gaps"],
                "frac_zero_test_stratum": proto["uair"]["frac_train_R_strata_zero_test"],
            },
        ),
    ):
        cmp_rows.append({"dataset": name, **row})
    pd.DataFrame(cmp_rows).to_csv(TAB / "rq1_opportunity_tv.csv", index=False)

    mob_rows = [
        {"metric": k, "value": v}
        for k, v in td.items()
        if not isinstance(v, (dict, list))
    ]
    pd.DataFrame(mob_rows).to_csv(TAB / "tdrive_mobility_scalars.csv", index=False)

    x = np.arange(len(H_ORDER))
    width = 0.25
    fig, ax = plt.subplots(figsize=(6.4, 3.6))
    ax.bar(x - width, [td["mu_test_seal"][h] for h in H_ORDER], width, label=r"target $\mu$ (test)")
    ax.bar(x, [td["pi_opp_real_R"][h] for h in H_ORDER], width, label=r"real-trace $\pi^{opp}$")
    ax.bar(x + width, [td["pi_opp_balanced_unit"][h] for h in H_ORDER], width, label=r"balanced-unit $\pi^{opp}$")
    ax.set_xticks(x, H_ORDER)
    ax.set_ylabel("mass")
    ax.set_title("T-Drive H1–H4: target vs real mobility vs balanced units")
    ax.legend(frameon=False)
    fig.tight_layout()
    fig.savefig(FIG / "tdrive_h_mass.pdf")
    fig.savefig(FIG / "tdrive_h_mass.png", dpi=160)
    plt.close(fig)

    payload = {
        "hashes": hashes,
        "tdrive": td,
        "protocol": proto,
        "u_layer": u_layer,
        "decision": decision,
    }
    (OUT / "G3_SUMMARY.json").write_text(json.dumps(payload, indent=2, default=str), encoding="utf-8")


def main() -> None:
    TAB.mkdir(parents=True, exist_ok=True)
    FIG.mkdir(parents=True, exist_ok=True)
    hashes = verify_processed_hashes()
    mu_seal = json.loads(H_SEAL_PATH.read_text(encoding="utf-8"))
    atomic, meas = load_tdrive()
    td = tdrive_mobility(atomic, meas, mu_seal)
    proto = {name: protocol_dataset(name) for name in ("sensorscope", "uair")}
    u_layer = usable_layer_mc()
    u_layer["expected_usable_updates"] = float(td["n_client_windows"] * u_layer["usable_update_rate_given_R"])
    decision = decide(td, proto, u_layer, hashes)
    write_tables(td, proto, u_layer, hashes, decision)
    print(json.dumps({"verdict": decision["verdict"], "reason": decision["reason"], "rq1": decision["rq1"]}, indent=2))


if __name__ == "__main__":
    main()
