"""Delta_c_s on common client×target_group support with explicit alpha/w binding.

Atomic Delta_pair (client×unit) is NOT_MATERIALIZED by this representation.
"""

from __future__ import annotations

from typing import Any, Mapping

import numpy as np
import pandas as pd

from raven_mcs.e3.hotfix.constants import PAIR_SCHEMA_VERSION, STRUCTURAL_METRIC_NAME
from raven_mcs.e3.target_pair.constants import PAIR_DOMAIN
from raven_mcs.e3.target_pair.errors import PairSupportError, PairWeightBindingError
from raven_mcs.metrics.distribution import delta_c_s
from raven_mcs.utils.hashing import sha256_json

REQUIRED_COLUMNS_V4 = [
    "dataset",
    "seed",
    "scenario",
    "method",
    "window",
    "client_id",
    "raw_atomic_unit_id",
    "canonical_pair_id",
    "spatial_unit",
    "time_block",
    "target_group",
    "eta_r",
    "I_r",
    "alpha_client",
    "w_atomic",
    "contribution",
    "accumulated_pair_mass",
    "target_pair_mass",
    "support_mask",
    "normalization_denominator",
    "eventtrace_hash",
    "target_artifact_hash",
    "method_source_hash",
    "schema_version",
]

# Methods that require method-specific local Hajek/IPW weights (no silent uniform w).
METHODS_REQUIRE_ATOMIC_W = {
    "local_hajek",
    "twostage_hajek",
    "inst_cal",
    "debt_cal",
    "raven",
    "raven_simoracle",
}

# Methods that require explicit alpha from aggregator (always; never invent uniform).
METHODS_REQUIRE_ALPHA = {
    "fedavg_window",
    "fedasync_window",
    "flamf_timealign_adapted",
    "local_hajek",
    "twostage_hajek",
    "inst_cal",
    "debt_cal",
    "raven",
    "raven_simoracle",
}


def pair_state_schema_v4() -> dict[str, Any]:
    return {
        "schema_version": PAIR_SCHEMA_VERSION,
        "pair_domain": PAIR_DOMAIN,
        "structural_metric_name": STRUCTURAL_METRIC_NAME,
        "formula": {
            "Pi_hat_ks": "(1/S_R) sum_r eta_r I_r alpha_{k,r}^{(m)} w_{k,r,i}^{(m)} mapped to (client, target_group/stratum)",
            "Delta_c_s": "sum_{k,s} |Pi_hat_ks - pi_tar_ks|  (= ||Pi_hat - pi_tar||_1 on client×stratum support)",
            "Delta_pair": "NOT_MATERIALIZED — atomic client×unit support not used by this representation",
            "code": [
                "raven_mcs.metrics.distribution.delta_c_s",
                "raven_mcs.e3.target_pair.pair_state_v4.accumulate_pair_state_v4",
            ],
        },
        "canonical_pair_id": "client_id::target_group",
        "method_dependence": ["alpha_client", "w_atomic"],
        "required_columns": REQUIRED_COLUMNS_V4,
        "outputs": ["pair_state_v5.parquet", "delta_c_s_summary.json"],
        "no_silent_uniform_fallback": True,
        "identity_audit_outcome": "CURRENT_V4_IS_DELTA_C_S_NOT_DELTA_PAIR",
    }


def _time_block(group: str) -> int:
    for part in str(group).split("::"):
        if part.startswith("block"):
            return int(part.replace("block", ""))
    return -1


def canonical_pair_id(client_id: str, target_group: str) -> str:
    return f"{client_id}::{target_group}"


def unit_to_canonical_pair(
    unit_id: str,
    *,
    unit_meta: pd.DataFrame,
    spatial_to_client: Mapping[str, str],
) -> tuple[str, str, str]:
    """Map raw atomic unit -> (client, target_group, canonical_pair_id)."""
    if unit_id not in unit_meta.index:
        raise PairSupportError(f"PAIR_SUPPORT_ERROR: unknown unit {unit_id}")
    row = unit_meta.loc[unit_id]
    spatial = str(row["spatial_id"])
    group = str(row["target_group"])
    client = spatial_to_client.get(spatial)
    if client is None:
        raise PairSupportError(f"PAIR_SUPPORT_ERROR: no client for spatial {spatial}")
    return str(client), group, canonical_pair_id(str(client), group)


def build_pi_tar_client_group(
    atomic: pd.DataFrame,
    spatial_to_client: Mapping[str, str],
    *,
    split: str = "test",
) -> dict[str, float]:
    """Target pair mass on client×target_group from TEST atom masses (uniform atoms)."""
    test = atomic.loc[
        (atomic["split"].astype(str) == split) & atomic["support_flag"].astype(bool)
    ].copy()
    if test.empty:
        raise PairSupportError("PAIR_SUPPORT_ERROR: empty test support")
    mass_atom = 1.0 / float(len(test))
    out: dict[str, float] = {}
    for row in test.itertuples(index=False):
        client = spatial_to_client[str(row.spatial_id)]
        pid = canonical_pair_id(str(client), str(row.target_group))
        out[pid] = out.get(pid, 0.0) + mass_atom
    total = sum(out.values())
    if abs(total - 1.0) > 1e-9:
        raise PairSupportError(f"PAIR_SUPPORT_ERROR: pi_tar sum={total}")
    return out


def bind_alpha_by_client(window_metrics_row: Any) -> dict[str, float]:
    """Bind alpha to client_id via frozen active_clients order (no sorted zip fallback)."""
    alpha = list(getattr(window_metrics_row, "alpha", []) or [])
    clients = list(getattr(window_metrics_row, "active_clients", []) or [])
    if not alpha and not clients:
        return {}
    if len(alpha) != len(clients):
        raise PairWeightBindingError(
            f"PAIR_WEIGHT_BINDING_ERROR: alpha/clients length mismatch "
            f"{len(alpha)} vs {len(clients)}"
        )
    out = {str(c): float(a) for c, a in zip(clients, alpha)}
    if len(out) != len(clients):
        raise PairWeightBindingError("PAIR_WEIGHT_BINDING_ERROR: duplicate client in active_clients")
    return out


def bind_w_by_unit(diag: dict[str, Any], *, method: str) -> dict[str, float]:
    """Bind local weights explicitly by atomic_unit_id."""
    unit_ids = [str(u) for u in (diag.get("observed_unit_ids") or [])]
    weights = diag.get("a_bar") or diag.get("w_units")
    if weights is None:
        if method in METHODS_REQUIRE_ATOMIC_W:
            raise PairWeightBindingError(
                f"PAIR_WEIGHT_BINDING_ERROR: missing atomic w for method={method}"
            )
        # Baseline methods without Hajek: equal local weights is the frozen definition
        if not unit_ids:
            return {}
        return {u: 1.0 / len(unit_ids) for u in unit_ids}
    w_arr = np.asarray(weights, dtype=np.float64)
    if len(w_arr) != len(unit_ids):
        raise PairWeightBindingError(
            f"PAIR_WEIGHT_BINDING_ERROR: w/unit length mismatch {len(w_arr)} vs {len(unit_ids)}"
        )
    if float(w_arr.sum()) <= 0:
        raise PairWeightBindingError("PAIR_WEIGHT_BINDING_ERROR: non-positive w sum")
    w_arr = w_arr / float(w_arr.sum())
    return {u: float(w) for u, w in zip(unit_ids, w_arr)}


def accumulate_pair_state_v4(
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
    target_artifact_hash: str | None,
    method_source_hash: str | None,
) -> tuple[pd.DataFrame, dict[str, Any]]:
    """Build Pi_hat on client×target_group common support with explicit bindings."""
    pi_tar = build_pi_tar_client_group(atomic, spatial_to_client, split="test")
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
                # Delivered/attempted clients without alpha are not in A_r — skip with no invent
                continue
            a = float(alpha_map[cid])
            w_map = bind_w_by_unit(d, method=method)
            for uid, w in w_map.items():
                client_u, group, pid = unit_to_canonical_pair(
                    uid, unit_meta=unit_meta, spatial_to_client=spatial_to_client
                )
                if client_u != cid:
                    raise PairSupportError(
                        f"PAIR_SUPPORT_ERROR: client mismatch diag={cid} unit_client={client_u}"
                    )
                c_term = float(eta * i_r * a * w)
                contrib[pid] = contrib.get(pid, 0.0) + c_term
                meta = unit_meta.loc[uid]
                rows.append(
                    {
                        "dataset": dataset,
                        "seed": int(seed),
                        "scenario": scenario,
                        "method": method,
                        "window": int(wm.window_id),
                        "client_id": cid,
                        "raw_atomic_unit_id": uid,
                        "canonical_pair_id": pid,
                        "spatial_unit": str(meta["spatial_id"]),
                        "time_block": _time_block(group),
                        "target_group": group,
                        "eta_r": eta,
                        "I_r": i_r,
                        "alpha_client": a,
                        "w_atomic": float(w),
                        "contribution": c_term,
                        "target_pair_mass": float(pi_tar.get(pid, 0.0)),
                        "support_mask": pid in pi_tar,
                        "normalization_denominator": None,  # filled after
                        "eventtrace_hash": eventtrace_hash,
                        "target_artifact_hash": target_artifact_hash,
                        "method_source_hash": method_source_hash,
                        "schema_version": PAIR_SCHEMA_VERSION,
                    }
                )

    denom = float(s_r) if s_r > 0 else 1.0
    keys = sorted(set(list(contrib.keys()) + list(pi_tar.keys())))
    if not keys:
        raise PairSupportError("PAIR_SUPPORT_ERROR: empty canonical pair support")
    pi_hat = np.asarray([contrib.get(k, 0.0) / denom for k in keys], dtype=np.float64)
    # Frozen definition uses (1/S_R) sum; renormalize only if residual mass for numerical safety
    # Keep L1 definition against target on the same keys (no forced re-normalize that hides support bugs)
    pi_t = np.asarray([pi_tar.get(k, 0.0) for k in keys], dtype=np.float64)
    if abs(float(pi_t.sum()) - 1.0) > 1e-8:
        raise PairSupportError(f"PAIR_SUPPORT_ERROR: pi_tar on keys sums to {pi_t.sum()}")
    # If Pi_hat has positive mass, normalize to probability for Delta_pair L1 distance
    if float(pi_hat.sum()) > 0:
        pi_hat_prob = pi_hat / float(pi_hat.sum())
    else:
        pi_hat_prob = pi_hat
    d_cs = float(delta_c_s(pi_hat_prob, pi_t))
    # Support overlap check — must not be empty when both have mass
    overlap = set(contrib.keys()) & set(pi_tar.keys())
    if contrib and pi_tar and not overlap:
        raise PairSupportError(
            "PAIR_SUPPORT_ERROR: disjoint Pi_hat/pi_tar support (raw ID mismatch artifact)"
        )
    frame = pd.DataFrame(rows)
    if not frame.empty:
        frame["normalization_denominator"] = denom
        acc = frame.groupby("canonical_pair_id")["contribution"].transform("sum") / denom
        frame["accumulated_pair_mass"] = acc
        mass_by_pair = frame.groupby("canonical_pair_id")["contribution"].sum() / denom
        total = float(mass_by_pair.sum()) or 1.0
        frame["accumulated_pair_mass_normalized"] = frame["canonical_pair_id"].map(
            (mass_by_pair / total).to_dict()
        )
    summary = {
        "Delta_c_s": d_cs,
        "Delta_pair": None,
        "Delta_pair_status": "NOT_MATERIALIZED",
        "structural_metric_name": STRUCTURAL_METRIC_NAME,
        "pair_domain": PAIR_DOMAIN,
        "pair_support_size": int(len(keys)),
        "overlap_size": int(len(overlap)),
        "schema_version": PAIR_SCHEMA_VERSION,
        "pi_hat_hash": sha256_json({"keys": keys, "pi_hat": pi_hat_prob.tolist()}),
        "pi_tar_hash": sha256_json({"keys": keys, "pi_tar": pi_t.tolist()}),
        "S_R": denom,
        "support_disjoint": False,
        "status": "OK",
    }
    if abs(d_cs - 2.0) < 1e-12 and not overlap:
        raise PairSupportError("PAIR_SUPPORT_ERROR: Delta_c_s=2 from disjoint support")
    return frame, summary


def analytical_delta_pair_toy() -> dict[str, Any]:
    """Symmetric toy (may have Delta_A == Delta_B); prefer nonsymmetric_delta_c_s_toy."""
    return nonsymmetric_delta_c_s_toy()


def nonsymmetric_delta_c_s_toy() -> dict[str, Any]:
    """Non-symmetric hand test: Pi_A != Pi_B and Delta_c_s_A != Delta_c_s_B."""

    class WM:
        def __init__(self, wid, alpha, clients):
            self.window_id = wid
            self.active = True
            self.alpha = alpha
            self.active_clients = clients

    # Non-uniform test masses: 0.55, 0.25, 0.15, 0.05 via repeated test units
    rows = []
    # train units
    for uid, spatial, group, t in [
        ("u_c0_g0", "n0", "n0::block0", 0),
        ("u_c0_g1", "n0", "n0::block2", 1),
        ("u_c1_g0", "n1", "n1::block0", 2),
        ("u_c1_g1", "n1", "n1::block2", 3),
    ]:
        rows.append(
            {
                "unit_id": uid,
                "spatial_id": spatial,
                "target_group": group,
                "opportunity_stratum": f"{group}::weekday",
                "split": "train",
                "support_flag": True,
                "time_index": t,
            }
        )
    # test: 11 units with masses 0.55/0.25/0.15/0.05 => counts 11,5,3,1 on 20 atoms
    masses = [
        ("n0", "n0::block0", 11),
        ("n0", "n0::block2", 5),
        ("n1", "n1::block0", 3),
        ("n1", "n1::block2", 1),
    ]
    t_idx = 100
    for spatial, group, count in masses:
        for j in range(count):
            rows.append(
                {
                    "unit_id": f"t_{spatial}_{group}_{j}",
                    "spatial_id": spatial,
                    "target_group": group,
                    "opportunity_stratum": f"{group}::weekday",
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
        _, summary = accumulate_pair_state_v4(
            window_metrics=wms,
            diagnostics=diags,
            atomic=atomic,
            spatial_to_client=mapping,
            dataset="toy",
            seed=0,
            scenario="complete_aligned",
            method=method_tag,
            eventtrace_hash=None,
            target_artifact_hash=None,
            method_source_hash=None,
        )
        return summary

    sa = run_method("raven", "u_c0_g0", "c0")
    sb = run_method("fedavg_window", "u_c1_g1", "c1")
    # pi_tar on client×group from atom counts / 20
    pi_tar = {
        "c0::n0::block0": 11 / 20,
        "c0::n0::block2": 5 / 20,
        "c1::n1::block0": 3 / 20,
        "c1::n1::block2": 1 / 20,
    }
    # Pi_A one-hot on c0::n0::block0; Pi_B one-hot on c1::n1::block2
    hand_a = sum(abs((1.0 if k == "c0::n0::block0" else 0.0) - v) for k, v in pi_tar.items())
    hand_b = sum(abs((1.0 if k == "c1::n1::block2" else 0.0) - v) for k, v in pi_tar.items())
    err_a = abs(float(sa["Delta_c_s"]) - hand_a)
    err_b = abs(float(sb["Delta_c_s"]) - hand_b)
    return {
        "structural_metric_name": STRUCTURAL_METRIC_NAME,
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
        "exact_match": err_a <= 1e-12 and err_b <= 1e-12,
        "pair_domain": PAIR_DOMAIN,
        "status": "PASS"
        if err_a <= 1e-12 and err_b <= 1e-12 and abs(hand_a - hand_b) > 1e-12
        else "FAIL",
    }


def method_pair_weight_binding_audit() -> list[dict[str, Any]]:
    rows = []
    for method in sorted(METHODS_REQUIRE_ALPHA | {"fedavg_window"}):
        rows.append(
            {
                "method": method,
                "alpha_source": "WindowMetrics.alpha aligned to WindowMetrics.active_clients",
                "alpha_key_type": "client_id",
                "w_source": (
                    "diagnostics.a_bar keyed by observed_unit_ids"
                    if method in METHODS_REQUIRE_ATOMIC_W
                    else "equal local weights (frozen non-Hajek baseline definition)"
                ),
                "w_key_type": "atomic_unit_id",
                "exact_normalization": "w renormalized to sum 1 over observed units; Pi_hat via (1/S_R) then prob-normalize for L1",
                "fallback_allowed": method not in METHODS_REQUIRE_ATOMIC_W,
                "silent_uniform_alpha_forbidden": True,
                "integration_test_status": "PENDING",
            }
        )
    return rows
