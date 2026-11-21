"""G1 Steps 1-3: propensity diagnosis + sealed Oracle/Estimated/No-Design join.

No new training. Does not overwrite sealed E3/E4 artifacts.
"""

from __future__ import annotations

import json
import math
from collections import Counter
from pathlib import Path

import matplotlib.pyplot as plt
import numpy as np
import pandas as pd

ROOT = Path(__file__).resolve().parents[2]
OUT = Path(__file__).resolve().parent
FIG = OUT / "figures"
TAB = OUT / "tables"
E3 = ROOT / "artifacts" / "e3_formal_runs_r1" / "runs"
E4 = ROOT / "artifacts" / "e4_core_mechanism_ablation_r1" / "runs"
ET = ROOT / "artifacts" / "e3_formal_runs_r1" / "eventtraces"
PHASE_A = ROOT / "_paper_work" / "design_noharm_results" / "phase_a"

DATASETS = ("sensorscope", "uair")
SEEDS = list(range(30001, 30021))
A_MAX = 20.0
P_MIN = 0.05
PI_MIN = 1e-6
D_MAX = 10.0
Q_MIN = 0.05
METHODS = ("raven", "raven_simoracle", "raven_wo_design")
PRIMARY = ("Delta_group", "RMSE_mu", "Tail_RMSE")
SECONDARY = ("Delta_c_s",)


def _load_json(path: Path):
    return json.loads(path.read_text(encoding="utf-8"))


def _quantiles(x: np.ndarray) -> dict[str, float]:
    x = np.asarray(x, dtype=np.float64)
    x = x[np.isfinite(x)]
    if x.size == 0:
        return {k: float("nan") for k in ("min", "p1", "p5", "p50", "p95", "max")}
    qs = np.quantile(x, [0.0, 0.01, 0.05, 0.50, 0.95, 1.0])
    return {
        "min": float(qs[0]),
        "p1": float(qs[1]),
        "p5": float(qs[2]),
        "p50": float(qs[3]),
        "p95": float(qs[4]),
        "max": float(qs[5]),
    }


def _ece(y: np.ndarray, p: np.ndarray, n_bins: int = 10) -> tuple[float, list[tuple[float, float, int]]]:
    y = np.asarray(y, dtype=np.float64)
    p = np.asarray(p, dtype=np.float64)
    mask = np.isfinite(y) & np.isfinite(p)
    y, p = y[mask], p[mask]
    if y.size == 0:
        return float("nan"), []
    bins = np.linspace(0.0, 1.0, n_bins + 1)
    ece = 0.0
    curve = []
    n = float(y.size)
    for i in range(n_bins):
        lo, hi = bins[i], bins[i + 1]
        sel = (p >= lo) & (p < hi) if i < n_bins - 1 else (p >= lo) & (p <= hi)
        if not np.any(sel):
            continue
        pred = float(np.mean(p[sel]))
        obs = float(np.mean(y[sel]))
        w = float(np.mean(sel))
        ece += w * abs(pred - obs)
        curve.append((pred, obs, int(sel.sum())))
    return float(ece), curve


def _auc(y: np.ndarray, p: np.ndarray) -> float:
    y = np.asarray(y, dtype=np.float64)
    p = np.asarray(p, dtype=np.float64)
    mask = np.isfinite(y) & np.isfinite(p)
    y, p = y[mask], p[mask]
    pos = p[y > 0.5]
    neg = p[y <= 0.5]
    if pos.size == 0 or neg.size == 0:
        return float("nan")
    ranks = pd.Series(np.concatenate([neg, pos])).rank(method="average").to_numpy()
    sum_pos = float(ranks[neg.size :].sum())
    return (sum_pos - pos.size * (pos.size + 1) / 2.0) / (pos.size * neg.size)


def _brier(y: np.ndarray, p: np.ndarray) -> float:
    y = np.asarray(y, dtype=np.float64)
    p = np.asarray(p, dtype=np.float64)
    mask = np.isfinite(y) & np.isfinite(p)
    if not np.any(mask):
        return float("nan")
    return float(np.mean(np.square(p[mask] - y[mask])))


def _nll(y: np.ndarray, p: np.ndarray) -> float:
    y = np.asarray(y, dtype=np.float64)
    p = np.clip(np.asarray(p, dtype=np.float64), 1e-12, 1.0 - 1e-12)
    mask = np.isfinite(y) & np.isfinite(p)
    if not np.any(mask):
        return float("nan")
    yy, pp = y[mask], p[mask]
    return float(-np.mean(yy * np.log(pp) + (1.0 - yy) * np.log(1.0 - pp)))


def _hour_block(stratum_id: str) -> float:
    for token in str(stratum_id).split("::"):
        if token.startswith("block") and token[5:].isdigit():
            return float(token[5:])
    return 0.0


def _tv(p: np.ndarray, q: np.ndarray) -> float:
    p = np.asarray(p, dtype=np.float64)
    q = np.asarray(q, dtype=np.float64)
    if p.size == 0:
        return float("nan")
    return 0.5 * float(np.abs(p - q).sum())


def _run_dir(dataset: str, method: str, seed: int) -> Path:
    if method == "raven_wo_design":
        return E4 / dataset / method / f"seed{seed}"
    return E3 / dataset / method / f"seed{seed}"


def collect_sealed_endpoints() -> pd.DataFrame:
    rows = []
    for dataset in DATASETS:
        for seed in SEEDS:
            for method in METHODS:
                path = _run_dir(dataset, method, seed) / "final_metrics.json"
                if not path.is_file():
                    rows.append(
                        {
                            "dataset": dataset,
                            "seed": seed,
                            "method": method,
                            "present": False,
                        }
                    )
                    continue
                met = _load_json(path)
                row = {
                    "dataset": dataset,
                    "seed": seed,
                    "method": method,
                    "present": True,
                }
                for key in PRIMARY + SECONDARY + ("ESS", "clip_rate_stage1", "clip_rate_stage2", "delta_ref"):
                    row[key] = met.get(key)
                rows.append(row)
    return pd.DataFrame(rows)


def _pct(new: float, ref: float) -> float:
    if ref is None or not np.isfinite(ref) or abs(ref) < 1e-15:
        return float("nan")
    return 100.0 * (float(new) - float(ref)) / float(ref)


def summarize_method_contrast(end: pd.DataFrame) -> pd.DataFrame:
    rows = []
    for dataset in DATASETS:
        wide = {}
        for method in METHODS:
            sub = end[(end.dataset == dataset) & (end.method == method) & (end.present)]
            wide[method] = sub.set_index("seed")
        seeds = sorted(
            set(wide["raven"].index) & set(wide["raven_simoracle"].index) & set(wide["raven_wo_design"].index)
        )
        for metric in PRIMARY + SECONDARY:
            est = wide["raven"].loc[seeds, metric].astype(float)
            ora = wide["raven_simoracle"].loc[seeds, metric].astype(float)
            off = wide["raven_wo_design"].loc[seeds, metric].astype(float)
            rows.append(
                {
                    "dataset": dataset,
                    "metric": metric,
                    "n": len(seeds),
                    "estimated_mean": float(est.mean()),
                    "oracle_mean": float(ora.mean()),
                    "nodesign_mean": float(off.mean()),
                    "oracle_vs_estimated_pct": float(np.nanmean([_pct(a, b) for a, b in zip(ora, est)])),
                    "estimated_vs_nodesign_pct": float(np.nanmean([_pct(a, b) for a, b in zip(est, off)])),
                    "oracle_vs_nodesign_pct": float(np.nanmean([_pct(a, b) for a, b in zip(ora, off)])),
                    "oracle_worse_than_nodesign": int((ora > off).sum()) if metric != "Delta_c_s" else int((ora > off).sum()),
                    "estimated_worse_than_nodesign": int((est > off).sum()),
                    "oracle_worse_than_estimated": int((ora > est).sum()),
                }
            )
    return pd.DataFrame(rows)


def _prepare_dataset(dataset: str):
    from raven_mcs.correction.pi_target import build_pi_target
    from raven_mcs.e3.canary.dataset_load import load_spatial_to_client
    from raven_mcs.e3.real_runner.generator_r3 import build_joint_pi_opp
    from raven_mcs.e3.stratum_seal.remap import apply_sealed_opportunity_stratum

    atomic = pd.read_parquet(ROOT / "data" / "processed" / dataset / "atomic_units.parquet")
    atomic_sealed, stratum_meta = apply_sealed_opportunity_stratum(
        atomic, dataset=dataset, root=ROOT
    )
    spatial_to_client = load_spatial_to_client(ROOT, dataset)
    atomic_for_pi = atomic_sealed.copy()
    if "target_group_main" not in atomic_for_pi.columns:
        atomic_for_pi["target_group_main"] = atomic_for_pi["target_group"].astype(str)
    pi_frame = build_pi_target(atomic_for_pi, spatial_to_client, split="test")
    pi_target = {
        (str(r.client_id), str(r.opportunity_stratum)): float(r.pi_k_s_tar)
        for r in pi_frame.itertuples()
    }
    train = atomic_sealed.loc[atomic_sealed["split"].astype(str) == "train"]
    strata_by_client: dict[str, list[str]] = {}
    for r in train.itertuples(index=False):
        c = spatial_to_client.get(str(r.spatial_id))
        if c is None:
            continue
        strata_by_client.setdefault(c, []).append(str(r.opportunity_stratum))
    for c in strata_by_client:
        strata_by_client[c] = sorted(set(strata_by_client[c]))
    pi_opp_joint = build_joint_pi_opp(sorted(strata_by_client), strata_by_client)
    unit_stratum = {
        str(r.unit_id): str(r.opportunity_stratum) for r in atomic_sealed.itertuples(index=False)
    }
    unit_group = {
        str(r.unit_id): str(r.target_group) for r in atomic_sealed.itertuples(index=False)
    }
    return {
        "pi_target": pi_target,
        "pi_opp_joint": pi_opp_joint,
        "unit_stratum": unit_stratum,
        "unit_group": unit_group,
        "stratum_meta": stratum_meta,
        "n_pi_target": len(pi_target),
        "n_pi_opp": len(pi_opp_joint),
    }


def _ess(o: np.ndarray, a: np.ndarray) -> float:
    from raven_mcs.correction.effective_sample_size import effective_sample_size

    weighted = o * a
    mass = float(weighted.sum())
    if mass <= 0:
        return 0.0
    return float(effective_sample_size(o, a, total_mass=mass))


def replay_propensity(dataset: str, ctx: dict) -> tuple[pd.DataFrame, pd.DataFrame, pd.DataFrame]:
    from raven_mcs.correction.design_ratio import zeta_hat_stratum
    from raven_mcs.correction.hajek import raw_weights
    from raven_mcs.correction.second_stage import d_weight
    from raven_mcs.opportunities.estimator import OpportunityEstimator
    from raven_mcs.propensity.observation import ObservationPropensity
    from raven_mcs.propensity.usable import UsablePropensity, deadline_slack_pre
    from raven_mcs.simulation.event_trace import load_event_trace

    pi_target = ctx["pi_target"]
    pi_opp = ctx["pi_opp_joint"]
    unit_stratum = ctx["unit_stratum"]

    unit_rows = []
    client_rows = []
    window_rows = []

    for seed in SEEDS:
        trace_dir = ET / dataset / f"seed{seed}" / "training_eventtrace"
        trace, identity = load_event_trace(trace_dir)
        events = trace.events.copy()
        obs_est = ObservationPropensity()
        use_est = UsablePropensity()
        opp_est = OpportunityEstimator()
        if pi_target:
            opp_est.initialize_support(key for key, mass in pi_target.items() if mass > 0.0)

        n_windows = int(trace.metadata.num_windows)
        for window_id in range(n_windows):
            rows = events.loc[events["window_id"] == window_id]
            win_clip_on = []
            win_clip_off = []
            win_ess_on = []
            win_ess_off = []
            win_ess_ora = []
            win_zeta = []
            clients_er_on = []
            clients_er_off = []
            clients_ar_on = []
            clients_ar_off = []
            opp_counts: Counter[tuple[str, str]] = Counter()
            pending_obs: list[tuple[np.ndarray, np.ndarray]] = []
            pending_q: list[tuple[np.ndarray, float]] = []

            for rec in rows.itertuples(index=False):
                cid = str(rec.client_id)
                risk = list(rec.risk_set_unit_ids or [])
                obs_ids = set(str(x) for x in (rec.observed_unit_ids or []))
                feats = rec.opportunity_features if isinstance(rec.opportunity_features, dict) else {}
                p_map = feats.get("p_obs_true_by_unit") or {}
                if not isinstance(p_map, dict):
                    p_map = {}
                strata = [unit_stratum.get(str(uid), "unknown") for uid in risk]
                o = np.asarray([1.0 if str(uid) in obs_ids else 0.0 for uid in risk], dtype=np.float64)
                planned = float(getattr(rec, "planned_workload_pre", getattr(rec, "raw_workload", len(risk))))
                log_plan = float(np.log1p(planned))
                feat_mat = np.asarray(
                    [[1.0, _hour_block(s), log_plan] for s in strata],
                    dtype=np.float64,
                )
                if feat_mat.size == 0:
                    continue
                p_hat = np.asarray([obs_est.predict(x) for x in feat_mat], dtype=np.float64)
                oracle_p_mean = float(getattr(rec, "oracle_p", feats.get("p_obs_true", np.nan)))
                p_true = np.asarray(
                    [float(p_map[str(uid)]) if str(uid) in p_map else oracle_p_mean for uid in risk],
                    dtype=np.float64,
                )
                atomic_ok = all(str(uid) in p_map for uid in risk) if risk else False
                pi_tar = np.asarray(
                    [float(pi_target.get((cid, str(s)), 0.0)) for s in strata],
                    dtype=np.float64,
                )
                pi_hat_frozen = np.asarray(
                    [float(pi_opp.get((cid, str(s)), 0.0)) for s in strata],
                    dtype=np.float64,
                )
                online_map = opp_est.pi_hat()
                pi_hat_online = np.asarray(
                    [float(online_map.get((cid, str(s)), P_MIN)) for s in strata],
                    dtype=np.float64,
                )
                zeta = zeta_hat_stratum(pi_tar, pi_hat_frozen, pi_min=PI_MIN)
                zeta_online = zeta_hat_stratum(pi_tar, pi_hat_online, pi_min=PI_MIN)
                a_on = raw_weights(zeta, p_hat, a_max=A_MAX, p_min=P_MIN)
                a_off = raw_weights(np.ones_like(zeta), p_hat, a_max=A_MAX, p_min=P_MIN)
                a_ora = raw_weights(zeta, p_true, a_max=A_MAX, p_min=P_MIN)
                a_mis_lo = raw_weights(zeta, np.clip(p_hat * 0.8, 1e-6, 1.0), a_max=A_MAX, p_min=P_MIN)
                a_mis_hi = raw_weights(zeta, np.clip(p_hat * 1.2, 1e-6, 1.0), a_max=A_MAX, p_min=P_MIN)
                n_obs = int(o.sum())
                ess_on = _ess(o, a_on)
                ess_off = _ess(o, a_off)
                ess_ora = _ess(o, a_ora)
                clip_on = float(np.mean(np.abs(a_on) >= A_MAX - 1e-12)) if a_on.size else 0.0
                clip_off = float(np.mean(np.abs(a_off) >= A_MAX - 1e-12)) if a_off.size else 0.0
                clip_ora = float(np.mean(np.abs(a_ora) >= A_MAX - 1e-12)) if a_ora.size else 0.0
                m_on = float((o * a_on).sum())
                m_off = float((o * a_off).sum())
                u_val = int(rec.U)
                attempted = int(getattr(rec, "attempted", 1 if obs_ids else 0))
                if m_on > 0:
                    clients_er_on.append(cid)
                if m_off > 0:
                    clients_er_off.append(cid)
                if m_on > 0 and u_val == 1:
                    clients_ar_on.append(cid)
                if m_off > 0 and u_val == 1:
                    clients_ar_off.append(cid)

                q_feat = np.array(
                    [
                        1.0,
                        float(rec.model_age),
                        0.0,
                        0.0,
                        deadline_slack_pre(float(window_id + 1), float(rec.registration_time)),
                    ],
                    dtype=np.float64,
                )
                q_hat = float(use_est.predict(q_feat))
                q_true = float(feats.get("q_use_true", getattr(rec, "oracle_q", np.nan)))
                d_hat = float(d_weight(np.array([q_hat]), d_max=D_MAX, q_min=Q_MIN)[0])
                d_true = float(d_weight(np.array([max(q_true, 1e-12)]), d_max=D_MAX, q_min=Q_MIN)[0]) if np.isfinite(q_true) else float("nan")

                win_clip_on.append(clip_on)
                win_clip_off.append(clip_off)
                win_ess_on.append(ess_on)
                win_ess_off.append(ess_off)
                win_ess_ora.append(ess_ora)
                win_zeta.extend(zeta.tolist())
                opp_counts.update((cid, str(s)) for s in strata)

                for i, uid in enumerate(risk):
                    unit_rows.append(
                        {
                            "dataset": dataset,
                            "seed": seed,
                            "window_id": window_id,
                            "client_id": cid,
                            "unit_id": str(uid),
                            "stratum": strata[i],
                            "hour_block": _hour_block(strata[i]),
                            "O": float(o[i]),
                            "p_hat": float(p_hat[i]),
                            "p_true": float(p_true[i]),
                            "p_true_atomic": bool(atomic_ok),
                            "pi_tar": float(pi_tar[i]),
                            "pi_opp_frozen": float(pi_hat_frozen[i]),
                            "pi_opp_online": float(pi_hat_online[i]),
                            "zeta": float(zeta[i]),
                            "zeta_online": float(zeta_online[i]),
                            "a_on": float(a_on[i]),
                            "a_off": float(a_off[i]),
                            "a_oracle": float(a_ora[i]),
                            "a_mis_lo": float(a_mis_lo[i]),
                            "a_mis_hi": float(a_mis_hi[i]),
                        }
                    )
                client_rows.append(
                    {
                        "dataset": dataset,
                        "seed": seed,
                        "window_id": window_id,
                        "client_id": cid,
                        "n_risk": int(len(risk)),
                        "n_obs": n_obs,
                        "U": u_val,
                        "attempted": attempted,
                        "ess_on": ess_on,
                        "ess_off": ess_off,
                        "ess_oracle": ess_ora,
                        "ess_ratio_on": ess_on / n_obs if n_obs else 0.0,
                        "ess_ratio_off": ess_off / n_obs if n_obs else 0.0,
                        "clip_on": clip_on,
                        "clip_off": clip_off,
                        "clip_oracle": clip_ora,
                        "m_on": m_on,
                        "m_off": m_off,
                        "mean_zeta": float(np.mean(zeta)) if zeta.size else float("nan"),
                        "max_zeta": float(np.max(zeta)) if zeta.size else float("nan"),
                        "frac_pi_tar_zero": float(np.mean(pi_tar <= 0.0)) if pi_tar.size else float("nan"),
                        "q_hat": q_hat,
                        "q_true": q_true,
                        "d_hat": d_hat,
                        "d_true": d_true,
                        "model_age": float(rec.model_age),
                    }
                )
                if attempted == 1:
                    pending_q.append((q_feat, float(u_val)))
                if len(risk) > 0:
                    pending_obs.append((feat_mat, o))

            for feat_mat, o_upd in pending_obs:
                obs_est.update_records_after_completion(feat_mat, o_upd)
            for q_feat, u_upd in pending_q:
                use_est.update_lagged(q_feat, u_upd)
            if opp_counts:
                opp_est.update_window(window_id, opp_counts)
            window_rows.append(
                {
                    "dataset": dataset,
                    "seed": seed,
                    "window_id": window_id,
                    "n_clients": int(len(rows)),
                    "same_er": set(clients_er_on) == set(clients_er_off),
                    "same_ar": set(clients_ar_on) == set(clients_ar_off),
                    "n_er_on": len(clients_er_on),
                    "n_er_off": len(clients_er_off),
                    "n_ar_on": len(clients_ar_on),
                    "n_ar_off": len(clients_ar_off),
                    "clip_on": float(np.mean(win_clip_on)) if win_clip_on else 0.0,
                    "clip_off": float(np.mean(win_clip_off)) if win_clip_off else 0.0,
                    "ess_on": float(np.mean(win_ess_on)) if win_ess_on else 0.0,
                    "ess_off": float(np.mean(win_ess_off)) if win_ess_off else 0.0,
                    "ess_oracle": float(np.mean(win_ess_ora)) if win_ess_ora else 0.0,
                    "mean_zeta": float(np.mean(win_zeta)) if win_zeta else float("nan"),
                    "max_zeta": float(np.max(win_zeta)) if win_zeta else float("nan"),
                    "eventtrace_hash": identity.get("trace_hash"),
                }
            )
    return pd.DataFrame(unit_rows), pd.DataFrame(client_rows), pd.DataFrame(window_rows)


def layer_panels(unit: pd.DataFrame, client: pd.DataFrame, ctxs: dict) -> pd.DataFrame:
    rows = []
    for dataset in DATASETS:
        u = unit[unit.dataset == dataset]
        c = client[client.dataset == dataset]
        pi_opp = np.asarray(list(ctxs[dataset]["pi_opp_joint"].values()), dtype=np.float64)
        pi_tar = np.asarray(list(ctxs[dataset]["pi_target"].values()), dtype=np.float64)
        realized = u.groupby(["client_id", "stratum"]).size()
        keys = list(ctxs[dataset]["pi_opp_joint"].keys())
        realized_mass = np.array([float(realized.get(k, 0.0)) for k in keys], dtype=np.float64)
        if realized_mass.sum() > 0:
            realized_mass = realized_mass / realized_mass.sum()
        frozen_mass = np.array([ctxs[dataset]["pi_opp_joint"][k] for k in keys], dtype=np.float64)
        target_mass = np.array([ctxs[dataset]["pi_target"].get(k, 0.0) for k in keys], dtype=np.float64)
        if target_mass.sum() > 0:
            target_mass = target_mass / target_mass.sum()
        nll_keys = u.apply(lambda r: ctxs[dataset]["pi_opp_joint"].get((r.client_id, r.stratum), PI_MIN), axis=1)
        nll_opp = float(-np.mean(np.log(np.clip(nll_keys.to_numpy(dtype=np.float64), PI_MIN, 1.0))))

        p_ece, _ = _ece(u.O.to_numpy(), u.p_hat.to_numpy())
        p_ece_ora, _ = _ece(u.O.to_numpy(), u.p_true.to_numpy())
        q_ece, _ = _ece(c.U.to_numpy(), c.q_hat.to_numpy())
        q_ece_ora, _ = _ece(c.U.to_numpy(), c.q_true.to_numpy())
        zq = _quantiles(u.zeta.to_numpy())
        pq = _quantiles(u.p_hat.to_numpy())
        oq = _quantiles(pi_opp)
        row = {
            "dataset": dataset,
            "n_units": int(len(u)),
            "n_client_windows": int(len(c)),
            "opp_nll_frozen": nll_opp,
            "opp_tv_realized_vs_frozen": _tv(realized_mass, frozen_mass),
            "opp_tv_realized_vs_target": _tv(realized_mass, target_mass),
            "opp_l1_realized_vs_frozen": float(np.abs(realized_mass - frozen_mass).sum()),
            "opp_support_coverage": float(np.mean(realized_mass[frozen_mass <= 0] == 0)) if realized_mass.size else float("nan"),
            "opp_near_zero_frac": float(np.mean(pi_opp <= PI_MIN)) if pi_opp.size else float("nan"),
            "p_hat_brier": _brier(u.O, u.p_hat),
            "p_true_brier": _brier(u.O, u.p_true),
            "p_hat_nll": _nll(u.O, u.p_hat),
            "p_true_nll": _nll(u.O, u.p_true),
            "p_hat_ece": p_ece,
            "p_true_ece": p_ece_ora,
            "p_hat_auc": _auc(u.O, u.p_hat),
            "p_true_auc": _auc(u.O, u.p_true),
            "p_hat_below_pmin": float(np.mean(u.p_hat < P_MIN)),
            "p_true_below_pmin": float(np.mean(u.p_true < P_MIN)),
            "p_hat_atomic_frac": float(np.mean(u.p_true_atomic)),
            "q_hat_brier": _brier(c.U, c.q_hat),
            "q_true_brier": _brier(c.U, c.q_true),
            "q_hat_ece": q_ece,
            "q_true_ece": q_ece_ora,
            "q_hat_auc": _auc(c.U, c.q_hat),
            "q_true_auc": _auc(c.U, c.q_true),
            "q_hat_std": float(np.nanstd(c.q_hat)),
            "q_true_std": float(np.nanstd(c.q_true)),
            "q_hat_near_const": bool(np.nanstd(c.q_hat) < 0.02),
            "d_clip_frac": float(np.mean(c.d_hat >= D_MAX - 1e-12)),
            "mean_abs_d_hat_minus_1": float(np.nanmean(np.abs(c.d_hat - 1.0))),
            "mean_abs_d_hat_minus_d_true": float(np.nanmean(np.abs(c.d_hat - c.d_true))),
            "clip_on_mean": float(c.clip_on.mean()),
            "clip_off_mean": float(c.clip_off.mean()),
            "clip_oracle_mean": float(c.clip_oracle.mean()),
            "ess_ratio_on_mean": float(c.ess_ratio_on.mean()),
            "ess_ratio_off_mean": float(c.ess_ratio_off.mean()),
            "mean_abs_a_on_minus_oracle": float(np.mean(np.abs(u.a_on - u.a_oracle))),
            "mean_abs_a_on_minus_off": float(np.mean(np.abs(u.a_on - u.a_off))),
            "mean_abs_a_on_minus_mislo": float(np.mean(np.abs(u.a_on - u.a_mis_lo))),
            "mean_abs_a_on_minus_mishi": float(np.mean(np.abs(u.a_on - u.a_mis_hi))),
            "frac_pi_tar_zero": float(np.mean(u.pi_tar <= 0.0)),
        }
        for prefix, qd in (("zeta", zq), ("p_hat", pq), ("pi_opp", oq)):
            for k, v in qd.items():
                row[f"{prefix}_{k}"] = v
        ptrue_q = _quantiles(u.p_true.to_numpy())
        for k, v in ptrue_q.items():
            row[f"p_true_{k}"] = v
        qhat_q = _quantiles(c.q_hat.to_numpy())
        for k, v in qhat_q.items():
            row[f"q_hat_{k}"] = v
        rows.append(row)
    return pd.DataFrame(rows)


def seed_join(end: pd.DataFrame, client: pd.DataFrame, window: pd.DataFrame) -> pd.DataFrame:
    rows = []
    for dataset in DATASETS:
        for seed in SEEDS:
            c = client[(client.dataset == dataset) & (client.seed == seed)]
            w = window[(window.dataset == dataset) & (window.seed == seed)]
            mets = {}
            for method in METHODS:
                sub = end[(end.dataset == dataset) & (end.seed == seed) & (end.method == method)]
                if sub.empty or not bool(sub.iloc[0]["present"]):
                    continue
                for key in PRIMARY + SECONDARY:
                    mets[f"{method}__{key}"] = float(sub.iloc[0][key])
            if not mets:
                continue
            row = {
                "dataset": dataset,
                "seed": seed,
                "clip_on_mean": float(c.clip_on.mean()) if len(c) else float("nan"),
                "ess_ratio_on_mean": float(c.ess_ratio_on.mean()) if len(c) else float("nan"),
                "q_hat_brier": _brier(c.U, c.q_hat),
                "q_hat_std": float(c.q_hat.std()) if len(c) else float("nan"),
                "same_ar_frac": float(w.same_ar.mean()) if len(w) else float("nan"),
                "same_er_frac": float(w.same_er.mean()) if len(w) else float("nan"),
                "frac_pi_tar_zero": float(c.frac_pi_tar_zero.mean()) if len(c) else float("nan"),
            }
            row.update(mets)
            if "raven__Delta_group" in mets and "raven_wo_design__Delta_group" in mets:
                for key in PRIMARY + SECONDARY:
                    row[f"est_vs_off_{key}_pct"] = _pct(mets[f"raven__{key}"], mets[f"raven_wo_design__{key}"])
                    row[f"ora_vs_off_{key}_pct"] = _pct(mets[f"raven_simoracle__{key}"], mets[f"raven_wo_design__{key}"])
                    row[f"ora_vs_est_{key}_pct"] = _pct(mets[f"raven_simoracle__{key}"], mets[f"raven__{key}"])
            rows.append(row)
    return pd.DataFrame(rows)


def _style():
    plt.rcParams.update(
        {
            "figure.dpi": 140,
            "savefig.dpi": 180,
            "font.size": 9,
            "axes.spines.top": False,
            "axes.spines.right": False,
            "axes.grid": True,
            "grid.alpha": 0.25,
        }
    )


def make_figures(unit: pd.DataFrame, client: pd.DataFrame, window: pd.DataFrame, join: pd.DataFrame, ctxs: dict) -> None:
    _style()
    colors = {"sensorscope": "#1f77b4", "uair": "#d62728"}

    # Fig 1: calibration panels
    fig, axes = plt.subplots(2, 2, figsize=(8.2, 7.2))
    titles = [
        ("p_hat vs O", "unit", "p_hat", "O"),
        ("q_hat vs U", "client", "q_hat", "U"),
        ("p_true vs O", "unit", "p_true", "O"),
        ("q_true vs U", "client", "q_true", "U"),
    ]
    frames = {"unit": unit, "client": client}
    for ax, (title, which, pcol, ycol) in zip(axes.ravel(), titles):
        for dataset in DATASETS:
            df = frames[which]
            df = df[df.dataset == dataset]
            ece, curve = _ece(df[ycol].to_numpy(), df[pcol].to_numpy())
            if curve:
                xs = [c[0] for c in curve]
                ys = [c[1] for c in curve]
                ax.plot(xs, ys, "o-", color=colors[dataset], label=f"{dataset} ECE={ece:.3f}")
        ax.plot([0, 1], [0, 1], "--", color="0.5", linewidth=1)
        ax.set_xlim(0, 1)
        ax.set_ylim(0, 1)
        ax.set_xlabel("predicted")
        ax.set_ylabel("observed frequency")
        ax.set_title(title)
        ax.legend(fontsize=7)
    fig.tight_layout()
    fig.savefig(FIG / "fig1_calibration_panels.png")
    fig.savefig(FIG / "fig1_calibration_panels.pdf")
    plt.close(fig)

    # Fig 2: opportunity reliability
    fig, axes = plt.subplots(1, 2, figsize=(8.2, 3.6))
    for ax, dataset in zip(axes, DATASETS):
        u = unit[unit.dataset == dataset]
        keys = list(ctxs[dataset]["pi_opp_joint"].keys())
        realized = u.groupby(["client_id", "stratum"]).size()
        x = np.array([ctxs[dataset]["pi_opp_joint"][k] for k in keys], dtype=np.float64)
        y = np.array([float(realized.get(k, 0.0)) for k in keys], dtype=np.float64)
        if y.sum() > 0:
            y = y / y.sum()
        ax.scatter(x, y, s=10, alpha=0.55, color=colors[dataset])
        lim = max(float(np.max(x) if x.size else 0.01), float(np.max(y) if y.size else 0.01))
        ax.plot([0, lim], [0, lim], "--", color="0.5", linewidth=1)
        ax.set_title(f"{dataset}: frozen pi_opp vs realized")
        ax.set_xlabel("pi_opp_joint")
        ax.set_ylabel("realized risk-set mass")
    fig.tight_layout()
    fig.savefig(FIG / "fig2_opportunity_reliability.png")
    fig.savefig(FIG / "fig2_opportunity_reliability.pdf")
    plt.close(fig)

    # Fig 3: log-scale weight ECDF
    fig, axes = plt.subplots(1, 2, figsize=(8.2, 3.6), sharey=True)
    for ax, dataset in zip(axes, DATASETS):
        u = unit[unit.dataset == dataset]
        for col, lab, ls in (
            ("a_on", "Design+estimated p", "-"),
            ("a_oracle", "Design+oracle p", "--"),
            ("a_off", "No-Design+estimated p", ":"),
        ):
            v = np.clip(u[col].to_numpy(dtype=np.float64), 1e-8, None)
            xs = np.sort(v)
            ys = np.linspace(0, 1, xs.size, endpoint=True)
            ax.plot(xs, ys, ls, label=lab, linewidth=1.4)
        ax.set_xscale("log")
        ax.set_title(dataset)
        ax.set_xlabel("raw weight a")
        ax.set_ylabel("ECDF")
        ax.legend(fontsize=7)
    fig.tight_layout()
    fig.savefig(FIG / "fig3_weight_ecdf.png")
    fig.savefig(FIG / "fig3_weight_ecdf.pdf")
    plt.close(fig)

    # Fig 4: ESS ratio
    fig, axes = plt.subplots(1, 2, figsize=(8.2, 3.6), sharey=True)
    for ax, dataset in zip(axes, DATASETS):
        c = client[client.dataset == dataset]
        ax.hist(c.ess_ratio_on, bins=30, alpha=0.55, label="Design", color=colors[dataset])
        ax.hist(c.ess_ratio_off, bins=30, alpha=0.35, label="No-Design", color="0.35")
        ax.set_title(f"{dataset}: ESS / n_obs")
        ax.set_xlabel("ESS ratio")
        ax.legend(fontsize=7)
    fig.tight_layout()
    fig.savefig(FIG / "fig4_ess_ratio.png")
    fig.savefig(FIG / "fig4_ess_ratio.pdf")
    plt.close(fig)

    # Fig 5: seed clip vs primary degradation
    fig, axes = plt.subplots(1, 3, figsize=(9.6, 3.3))
    for ax, metric in zip(axes, PRIMARY):
        for dataset in DATASETS:
            j = join[join.dataset == dataset]
            ax.scatter(
                j.clip_on_mean,
                j[f"est_vs_off_{metric}_pct"],
                color=colors[dataset],
                label=dataset,
                s=28,
            )
        ax.axhline(0, color="0.5", linewidth=1)
        ax.set_xlabel("mean clip_rate (Design)")
        ax.set_ylabel(f"{metric} est vs no-design (%)")
        ax.set_title(metric)
        ax.legend(fontsize=7)
    fig.tight_layout()
    fig.savefig(FIG / "fig5_clip_vs_endpoint.png")
    fig.savefig(FIG / "fig5_clip_vs_endpoint.pdf")
    plt.close(fig)

    # Fig 6: reversal vs reliability / support
    fig, axes = plt.subplots(1, 3, figsize=(9.6, 3.3))
    j_u = join[join.dataset == "uair"]
    axes[0].scatter(j_u.same_ar_frac, j_u.est_vs_off_Delta_group_pct, color=colors["uair"], s=28)
    axes[0].set_xlabel("frac windows with same A_r")
    axes[0].set_ylabel("U-Air Δgroup est vs off (%)")
    axes[0].set_title("support overlap vs reversal")
    axes[1].scatter(j_u.ess_ratio_on_mean, j_u.est_vs_off_Delta_group_pct, color=colors["uair"], s=28)
    axes[1].set_xlabel("mean ESS ratio (Design)")
    axes[1].set_title("ESS vs reversal")
    axes[2].scatter(j_u.ora_vs_est_Delta_group_pct, j_u.est_vs_off_Delta_group_pct, color=colors["uair"], s=28)
    axes[2].axvline(0, color="0.5", linewidth=1)
    axes[2].set_xlabel("oracle vs estimated Δgroup (%)")
    axes[2].set_title("oracle gap vs estimated reversal")
    fig.tight_layout()
    fig.savefig(FIG / "fig6_reversal_vs_reliability.png")
    fig.savefig(FIG / "fig6_reversal_vs_reliability.pdf")
    plt.close(fig)


def main() -> None:
    FIG.mkdir(parents=True, exist_ok=True)
    TAB.mkdir(parents=True, exist_ok=True)
    print("collect sealed endpoints")
    end = collect_sealed_endpoints()
    end.to_csv(TAB / "sealed_method_endpoints.csv", index=False)
    contrast = summarize_method_contrast(end)
    contrast.to_csv(TAB / "oracle_estimated_nodesign_contrast.csv", index=False)
    print(contrast.to_string(index=False))

    ctxs = {}
    unit_parts = []
    client_parts = []
    window_parts = []
    for dataset in DATASETS:
        print(f"prepare {dataset}")
        ctxs[dataset] = _prepare_dataset(dataset)
        print(f"replay {dataset}")
        u, c, w = replay_propensity(dataset, ctxs[dataset])
        unit_parts.append(u)
        client_parts.append(c)
        window_parts.append(w)
        print(f"  units={len(u)} clients={len(c)} windows={len(w)}")

    unit = pd.concat(unit_parts, ignore_index=True)
    client = pd.concat(client_parts, ignore_index=True)
    window = pd.concat(window_parts, ignore_index=True)
    # keep seed-level unit dump lean: parquet only
    unit.to_parquet(TAB / "unit_records.parquet", index=False)
    client.to_csv(TAB / "client_window_records.csv", index=False)
    window.to_csv(TAB / "window_records.csv", index=False)

    panels = layer_panels(unit, client, ctxs)
    panels.to_csv(TAB / "three_layer_panel.csv", index=False)
    print(panels.to_string(index=False))

    join = seed_join(end, client, window)
    brier_rows = []
    for (ds, seed), g in unit.groupby(["dataset", "seed"]):
        brier_rows.append(
            {
                "dataset": ds,
                "seed": int(seed),
                "p_hat_brier_seed": _brier(g.O, g.p_hat),
                "p_true_brier_seed": _brier(g.O, g.p_true),
            }
        )
    join = join.merge(pd.DataFrame(brier_rows), on=["dataset", "seed"], how="left")
    if (PHASE_A / "window_alignment.csv").is_file():
        wa = pd.read_csv(PHASE_A / "window_alignment.csv")
        overlap = (
            wa.groupby(["dataset", "seed"], as_index=False)["same_clients"]
            .mean()
            .rename(columns={"same_clients": "phase_a_same_clients_frac"})
        )
        join = join.merge(overlap, on=["dataset", "seed"], how="left")
    join.to_csv(TAB / "seed_join.csv", index=False)

    make_figures(unit, client, window, join, ctxs)

    gaps = {
        "oracle_p_source": "EventTrace opportunity_features.p_obs_true_by_unit + oracle_p",
        "oracle_q_source": "EventTrace opportunity_features.q_use_true + oracle_q",
        "oracle_pi_opp": "production Design already uses frozen generator joint pi_opp; not online EMA",
        "misspecified_1": "weight-level p_hat x0.8/x1.2 only; no retrain",
        "misspecified_2": "not run (would require omitted-covariate retrain or estimator replay with dropped hour_block)",
        "clip_grid_on_val": "not run; needs new training or val-only protocol",
        "lambda_pareto": "not run; needs P2 re-solve / retrain on val",
        "g1b_gating": "not implemented; wait for decision tree",
    }
    (OUT / "gaps.json").write_text(json.dumps(gaps, indent=2), encoding="utf-8")
    summary = {
        "n_unit_rows": int(len(unit)),
        "n_client_rows": int(len(client)),
        "n_window_rows": int(len(window)),
        "p_true_atomic_frac": {
            ds: float(unit[unit.dataset == ds].p_true_atomic.mean()) for ds in DATASETS
        },
        "uair_same_ar_frac": float(window[window.dataset == "uair"].same_ar.mean()),
        "sensorscope_same_ar_frac": float(window[window.dataset == "sensorscope"].same_ar.mean()),
    }
    (OUT / "run_summary.json").write_text(json.dumps(summary, indent=2), encoding="utf-8")
    print("G1 diagnosis written to", OUT)


if __name__ == "__main__":
    main()
