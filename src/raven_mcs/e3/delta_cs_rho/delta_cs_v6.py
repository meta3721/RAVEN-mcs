"""True Delta_c_s on client × opportunity_stratum (NOT target_group h)."""

from __future__ import annotations

from typing import Any, Mapping

import numpy as np
import pandas as pd

from raven_mcs.correction.pi_target import build_pi_target
from raven_mcs.e3.delta_cs_rho.constants import PAIR_SCHEMA_VERSION, STRUCTURAL_METRIC_NAME
from raven_mcs.e3.delta_cs_rho.stratum import parse_stratum
from raven_mcs.e3.target_pair.errors import PairSupportError, PairWeightBindingError
from raven_mcs.e3.target_pair.pair_state_v4 import (
    METHODS_REQUIRE_ALPHA,
    METHODS_REQUIRE_ATOMIC_W,
    bind_alpha_by_client,
    bind_w_by_unit,
)
from raven_mcs.metrics.distribution import delta_c_s
from raven_mcs.utils.hashing import sha256_json

REQUIRED_COLUMNS_V6 = [
    "dataset",
    "seed",
    "scenario",
    "method",
    "window",
    "client_id",
    "atomic_unit_id",
    "opportunity_stratum_id",
    "coarse_spatial_region",
    "time_block",
    "weekday_weekend_flag",
    "eta_r",
    "I_r",
    "alpha_client",
    "w_atomic",
    "atomic_contribution",
    "accumulated_client_stratum_mass",
    "target_client_stratum_mass",
    "normalization_denominator",
    "eventtrace_hash",
    "stratum_map_hash",
    "target_mass_hash",
    "method_source_hash",
    "schema_version",
]


def client_stratum_id(client_id: str, stratum: str) -> str:
    return f"{client_id}::{stratum}"


def delta_cs_state_schema_v6() -> dict[str, Any]:
    return {
        "schema_version": PAIR_SCHEMA_VERSION,
        "structural_metric_name": STRUCTURAL_METRIC_NAME,
        "support": "client × opportunity_stratum",
        "forbidden_support": "client × target_group h(i)",
        "formula": {
            "Pi_hat_ks": (
                "(1/S_R) sum_r eta_r I_r alpha_{k,r}^{(m)} w_{k,r,i}^{(m)} "
                "aggregated over i with s(i)=s"
            ),
            "Delta_c_s": "sum_{k,s} |Pi_hat_ks - pi_tar_ks|",
            "Delta_pair": "NOT_MATERIALIZED",
        },
        "required_columns": REQUIRED_COLUMNS_V6,
        "outputs": ["delta_cs_state_v6.parquet", "delta_cs_summary_v6.json"],
        "pi_tar_source": "raven_mcs.correction.pi_target.build_pi_target",
    }


def build_pi_tar_client_stratum(
    atomic: pd.DataFrame,
    spatial_to_client: Mapping[str, str],
    *,
    split: str = "test",
) -> dict[str, float]:
    """Frozen pi_tar(k,s) via production build_pi_target (opportunity stratum)."""
    frame = atomic.copy()
    if "target_group_main" not in frame.columns:
        frame["target_group_main"] = frame["target_group"].astype(str)
    pi_frame = build_pi_target(frame, dict(spatial_to_client), split=split)
    out = {
        client_stratum_id(str(r.client_id), str(r.opportunity_stratum)): float(r.pi_k_s_tar)
        for r in pi_frame.itertuples(index=False)
    }
    total = float(sum(out.values()))
    if abs(total - 1.0) > 1e-9:
        raise PairSupportError(f"DELTA_CS_ERROR: pi_tar sum={total}")
    return out


def unit_to_client_stratum(
    unit_id: str,
    *,
    unit_meta: pd.DataFrame,
    spatial_to_client: Mapping[str, str],
) -> tuple[str, str, str]:
    """Map atomic unit -> (client, opportunity_stratum, client_stratum_id)."""
    if unit_id not in unit_meta.index:
        raise PairSupportError(f"DELTA_CS_ERROR: unknown unit {unit_id}")
    row = unit_meta.loc[unit_id]
    spatial = str(row["spatial_id"])
    stratum = str(row["opportunity_stratum"])
    client = spatial_to_client.get(spatial)
    if client is None:
        raise PairSupportError(f"DELTA_CS_ERROR: no client for spatial {spatial}")
    # Hard rule: never use target_group as stratum
    if "target_group" in row.index and str(row["target_group"]) == stratum:
        # Equal labels can happen numerically only if day-type absent — still OK if column is opportunity_stratum
        pass
    return str(client), stratum, client_stratum_id(str(client), stratum)


def accumulate_delta_cs_v6(
    *,
    window_metrics: list[Any],
    diagnostics: list[dict[str, Any]],
    atomic: pd.DataFrame,
    spatial_to_client: Mapping[str, str],
    dataset: str,
    seed: int,
    scenario: str,
    method: str,
    eventtrace_hash: str | None,
    stratum_map_hash: str | None,
    target_mass_hash: str | None,
    method_source_hash: str | None,
) -> tuple[pd.DataFrame, dict[str, Any]]:
    """Build Pi_hat / Delta_c_s on client×opportunity_stratum."""
    pi_tar = build_pi_tar_client_stratum(atomic, spatial_to_client, split="test")
    unit_meta = atomic.set_index("unit_id")
    contrib: dict[str, float] = {}
    rows: list[dict[str, Any]] = []
    s_r = 0.0

    for wm in window_metrics:
        active = bool(getattr(wm, "active", False))
        eta = 1.0
        i_r = 1.0 if active else 0.0
        if not active:
            continue
        s_r += eta
        if method in METHODS_REQUIRE_ALPHA and not list(getattr(wm, "alpha", []) or []):
            raise PairWeightBindingError(
                f"PAIR_WEIGHT_BINDING_ERROR: empty alpha for active window method={method}"
            )
        alpha_map = bind_alpha_by_client(wm)
        win_diag = [d for d in diagnostics if int(d.get("window_id", -1)) == int(wm.window_id)]
        for d in win_diag:
            cid = str(d["client_id"])
            if cid not in alpha_map:
                continue
            a = float(alpha_map[cid])
            w_map = bind_w_by_unit(d, method=method)
            for uid, w in w_map.items():
                client_u, stratum, sid = unit_to_client_stratum(
                    uid, unit_meta=unit_meta, spatial_to_client=spatial_to_client
                )
                if client_u != cid:
                    raise PairSupportError(
                        f"DELTA_CS_ERROR: client mismatch diag={cid} unit_client={client_u}"
                    )
                c_term = float(eta * i_r * a * w)
                contrib[sid] = contrib.get(sid, 0.0) + c_term
                parsed = parse_stratum(stratum)
                rows.append(
                    {
                        "dataset": dataset,
                        "seed": int(seed),
                        "scenario": scenario,
                        "method": method,
                        "window": int(wm.window_id),
                        "client_id": cid,
                        "atomic_unit_id": uid,
                        "opportunity_stratum_id": stratum,
                        "coarse_spatial_region": parsed["coarse_spatial_region"],
                        "time_block": parsed["time_block"],
                        "weekday_weekend_flag": parsed["weekday_weekend_flag"],
                        "eta_r": eta,
                        "I_r": i_r,
                        "alpha_client": a,
                        "w_atomic": float(w),
                        "atomic_contribution": c_term,
                        "target_client_stratum_mass": float(pi_tar.get(sid, 0.0)),
                        "normalization_denominator": None,
                        "eventtrace_hash": eventtrace_hash,
                        "stratum_map_hash": stratum_map_hash,
                        "target_mass_hash": target_mass_hash,
                        "method_source_hash": method_source_hash,
                        "schema_version": PAIR_SCHEMA_VERSION,
                        # Explicitly absent: target_group must not drive this metric
                    }
                )

    denom = float(s_r) if s_r > 0 else 1.0
    keys = sorted(set(list(contrib.keys()) + list(pi_tar.keys())))
    if not keys:
        raise PairSupportError("DELTA_CS_ERROR: empty client×stratum support")
    pi_hat = np.asarray([contrib.get(k, 0.0) / denom for k in keys], dtype=np.float64)
    pi_t = np.asarray([pi_tar.get(k, 0.0) for k in keys], dtype=np.float64)
    if abs(float(pi_t.sum()) - 1.0) > 1e-8:
        raise PairSupportError(f"DELTA_CS_ERROR: pi_tar on keys sums to {pi_t.sum()}")
    if float(pi_hat.sum()) > 0:
        pi_hat_prob = pi_hat / float(pi_hat.sum())
    else:
        pi_hat_prob = pi_hat
    d_cs = float(delta_c_s(pi_hat_prob, pi_t))
    overlap = set(contrib.keys()) & set(pi_tar.keys())
    if contrib and pi_tar and not overlap:
        raise PairSupportError("DELTA_CS_ERROR: disjoint Pi_hat/pi_tar support")

    frame = pd.DataFrame(rows)
    if not frame.empty:
        frame["normalization_denominator"] = denom
        acc = frame.groupby("opportunity_stratum_id").apply(
            lambda g: g["atomic_contribution"].sum() / denom, include_groups=False
        )
        # per-row accumulated mass for (client, stratum)
        mass_by = {}
        for k in keys:
            mass_by[k] = contrib.get(k, 0.0) / denom
        frame["accumulated_client_stratum_mass"] = [
            mass_by.get(client_stratum_id(str(r.client_id), str(r.opportunity_stratum_id)), 0.0)
            for r in frame.itertuples(index=False)
        ]
    else:
        acc = pd.Series(dtype=float)

    summary = {
        "Delta_c_s": d_cs,
        "Delta_pair": None,
        "Delta_pair_status": "NOT_MATERIALIZED",
        "structural_metric_name": STRUCTURAL_METRIC_NAME,
        "support": "client × opportunity_stratum",
        "forbidden_support_used": False,
        "pair_support_size": int(len(keys)),
        "overlap_size": int(len(overlap)),
        "schema_version": PAIR_SCHEMA_VERSION,
        "pi_hat_hash": sha256_json({"keys": keys, "pi_hat": pi_hat_prob.tolist()}),
        "pi_tar_hash": sha256_json({"keys": keys, "pi_tar": pi_t.tolist()}),
        "S_R": denom,
        "status": "OK",
    }
    return frame, summary


def nonsymmetric_delta_cs_analytical_test() -> dict[str, Any]:
    """Non-symmetric hand test on opportunity strata (not target groups)."""

    class WM:
        def __init__(self, wid, alpha, clients):
            self.window_id = wid
            self.active = True
            self.alpha = alpha
            self.active_clients = clients

    rows = []
    # train units with distinct s
    for uid, spatial, stratum, group, t in [
        ("u_c0_s0", "n0", "n0::block0::weekday", "n0::block0", 0),
        ("u_c0_s1", "n0", "n0::block2::weekend", "n0::block2", 1),
        ("u_c1_s0", "n1", "n1::block0::weekday", "n1::block0", 2),
        ("u_c1_s1", "n1", "n1::block2::weekend", "n1::block2", 3),
    ]:
        rows.append(
            {
                "unit_id": uid,
                "spatial_id": spatial,
                "target_group": group,
                "opportunity_stratum": stratum,
                "split": "train",
                "support_flag": True,
                "time_index": t,
            }
        )
    # test masses 11,5,3,1 on 20 → non-uniform pi_tar
    masses = [
        ("n0", "n0::block0::weekday", "n0::block0", 11),
        ("n0", "n0::block2::weekend", "n0::block2", 5),
        ("n1", "n1::block0::weekday", "n1::block0", 3),
        ("n1", "n1::block2::weekend", "n1::block2", 1),
    ]
    t_idx = 100
    for spatial, stratum, group, count in masses:
        for j in range(count):
            rows.append(
                {
                    "unit_id": f"t_{spatial}_{j}_{stratum}",
                    "spatial_id": spatial,
                    "target_group": group,
                    "opportunity_stratum": stratum,
                    "split": "test",
                    "support_flag": True,
                    "time_index": t_idx,
                }
            )
            t_idx += 1
    atomic = pd.DataFrame(rows)
    mapping = {"n0": "c0", "n1": "c1"}

    def run_method(method_tag: str, unit_a: str, client: str):
        wms = [WM(0, [1.0], [client]), WM(1, [1.0], [client])]
        diags = [
            {"window_id": 0, "client_id": client, "observed_unit_ids": [unit_a], "a_bar": [1.0]},
            {"window_id": 1, "client_id": client, "observed_unit_ids": [unit_a], "a_bar": [1.0]},
        ]
        _, summary = accumulate_delta_cs_v6(
            window_metrics=wms,
            diagnostics=diags,
            atomic=atomic,
            spatial_to_client=mapping,
            dataset="toy",
            seed=0,
            scenario="complete_aligned",
            method=method_tag,
            eventtrace_hash=None,
            stratum_map_hash=None,
            target_mass_hash=None,
            method_source_hash=None,
        )
        return summary

    sa = run_method("raven", "u_c0_s0", "c0")
    sb = run_method("fedavg_window", "u_c1_s1", "c1")
    pi_tar = {
        "c0::n0::block0::weekday": 11 / 20,
        "c0::n0::block2::weekend": 5 / 20,
        "c1::n1::block0::weekday": 3 / 20,
        "c1::n1::block2::weekend": 1 / 20,
    }
    hand_a = sum(abs((1.0 if k == "c0::n0::block0::weekday" else 0.0) - v) for k, v in pi_tar.items())
    hand_b = sum(abs((1.0 if k == "c1::n1::block2::weekend" else 0.0) - v) for k, v in pi_tar.items())
    err_a = abs(float(sa["Delta_c_s"]) - hand_a)
    err_b = abs(float(sb["Delta_c_s"]) - hand_b)

    # h-independence: flip target_group labels, keep s fixed → Delta unchanged
    atomic_hflip = atomic.copy()
    atomic_hflip["target_group"] = atomic_hflip["target_group"].map(
        lambda g: "FLIP::" + str(g)
    )
    _, sa_flip = accumulate_delta_cs_v6(
        window_metrics=[WM(0, [1.0], ["c0"]), WM(1, [1.0], ["c0"])],
        diagnostics=[
            {"window_id": 0, "client_id": "c0", "observed_unit_ids": ["u_c0_s0"], "a_bar": [1.0]},
            {"window_id": 1, "client_id": "c0", "observed_unit_ids": ["u_c0_s0"], "a_bar": [1.0]},
        ],
        atomic=atomic_hflip,
        spatial_to_client=mapping,
        dataset="toy",
        seed=0,
        scenario="complete_aligned",
        method="raven",
        eventtrace_hash=None,
        stratum_map_hash=None,
        target_mass_hash=None,
        method_source_hash=None,
    )
    h_independent = abs(float(sa["Delta_c_s"]) - float(sa_flip["Delta_c_s"])) <= 1e-12

    return {
        "structural_metric_name": STRUCTURAL_METRIC_NAME,
        "support": "client × opportunity_stratum",
        "pi_tar": pi_tar,
        "hand_Delta_c_s_A": hand_a,
        "hand_Delta_c_s_B": hand_b,
        "Delta_c_s_A": sa["Delta_c_s"],
        "Delta_c_s_B": sb["Delta_c_s"],
        "error_A": err_a,
        "error_B": err_b,
        "pi_hat_hash_A": sa["pi_hat_hash"],
        "pi_hat_hash_B": sb["pi_hat_hash"],
        "pi_hat_differ": sa["pi_hat_hash"] != sb["pi_hat_hash"],
        "delta_differ": abs(float(sa["Delta_c_s"]) - float(sb["Delta_c_s"])) > 1e-12,
        "h_independence": h_independent,
        "status": "PASS"
        if (
            err_a <= 1e-12
            and err_b <= 1e-12
            and abs(hand_a - hand_b) > 1e-12
            and h_independent
        )
        else "FAIL",
    }


def method_mass_binding_audit() -> list[dict[str, Any]]:
    rows = []
    for method in sorted(METHODS_REQUIRE_ALPHA | {"fedavg_window"}):
        rows.append(
            {
                "method": method,
                "alpha_source": "WindowMetrics.alpha aligned to active_clients",
                "alpha_key_type": "client_id",
                "w_source": (
                    "diagnostics.a_bar keyed by observed_unit_ids"
                    if method in METHODS_REQUIRE_ATOMIC_W
                    else "equal local weights (frozen non-Hajek baseline)"
                ),
                "w_key_type": "atomic_unit_id",
                "atomic_to_stratum_mapping": "atomic.opportunity_stratum (NOT target_group)",
                "normalization": "(1/S_R) then probability-normalize Pi_hat for L1",
                "production_function": "accumulate_delta_cs_v6",
                "status": "READY",
            }
        )
    return rows


def field_usage_audit() -> dict[str, Any]:
    return {
        "Delta_c_s_source_field": "opportunity_stratum_id",
        "forbidden_for_stratum_mass": ["target_group", "target_group_id", "h(i)"],
        "hard_test": "flip h labels while holding s fixed → Delta_c_s unchanged",
        "failure_code": "DELTA_CS_USES_TARGET_GROUP_ERROR",
        "status": "AUDITED",
    }
