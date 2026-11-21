# CODE_DIFF

src 出现了差异，需要复查。

```
diff --git a/src/raven_mcs/aggregation/feasibility.py b/src/raven_mcs/aggregation/feasibility.py
index f04571b..a511f7f 100644
--- a/src/raven_mcs/aggregation/feasibility.py
+++ b/src/raven_mcs/aggregation/feasibility.py
@@ -26,12 +26,21 @@ def validate_p2_lambdas(
     lambda_beta: float,
     lambda_group: float,
     max_server_learning_rate: float,
+    instant_calibration: bool = True,
 ) -> None:
-    """Require λ_β>0 and λ_g ≥ max server learning rate."""
+    """Require λ_β>0; require λ_g ≥ max server LR when instant calibration is on.
+
+    The raven_wo_inst ablation path may pass instant_calibration=False so that
+    λ_g=0 is legal (group-calibration term disabled). Full RAVEN keeps the
+    default instant_calibration=True gate unchanged.
+    """
     if not (lambda_beta > 0):
         raise ValueError("lambda_beta must be > 0 for P2 uniqueness")
-    if lambda_group < max_server_learning_rate:
-        raise ValueError(
-            "lambda_group must be >= max_server_learning_rate "
-            f"(got {lambda_group} < {max_server_learning_rate})"
-        )
+    if instant_calibration:
+        if lambda_group < max_server_learning_rate:
+            raise ValueError(
+                "lambda_group must be >= max_server_learning_rate "
+                f"(got {lambda_group} < {max_server_learning_rate})"
+            )
+    elif lambda_group < 0:
+        raise ValueError("lambda_group must be >= 0 when instant_calibration=False")
diff --git a/src/raven_mcs/aggregation/method_policy.py b/src/raven_mcs/aggregation/method_policy.py
index 8b2c359..b5852d5 100644
--- a/src/raven_mcs/aggregation/method_policy.py
+++ b/src/raven_mcs/aggregation/method_policy.py
@@ -24,10 +24,38 @@ class MethodPolicy:
     uses_variance_penalty: bool = False
     uses_staleness_penalty: bool = False
     uses_oracle_propensity: bool = False
+    # F-1 diagnostic arms only. uses_oracle_propensity gates the q map and the atomic p map
+    # together (window_runner.py:426-430 and :707-727); uses_oracle_p isolates the p map so the
+    # two members of RAVEN-SimOracle can be separated. No paper method sets this.
+    uses_oracle_p: bool = False
     is_external_baseline: bool = False
-    # policy: follow uses_design_ratio; always_on/off: Mode D/0; sag: SAG certificates.
-    # Never encode dataset identity here.
+    # These three fields have separate responsibilities. gate_mode is only
+    # retained to reproduce historical control policies, never the new method.
+    design_control: str = "legacy"
+    coverage_diagnostic: str = "aggregate_coverage"
+    method_version: str = "legacy-v1"
     gate_mode: str = "policy"
+    legacy_only: bool = False
+    paper_method: bool = False
+
+
+PAPER_METHOD_KEY = "raven_mcs"
+FORMAL_DEFAULT_METHOD = "raven_mcs"
+FORMAL_GATE_MODE = "aggregate_coverage"
+CONFIGURED_METHOD_VERSION = "configured-design-v1"
+LEGACY_COVERAGE_METHOD = "raven_coverage_legacy"
+
+_RAVEN_CORE = dict(
+    uses_design_ratio=True,
+    uses_observation_ipw=True,
+    uses_usable_ipw=True,
+    uses_hajek_local_loss=True,
+    uses_instant_calibration=True,
+    uses_debt=True,
+    uses_reference_penalty=True,
+    uses_variance_penalty=True,
+    uses_staleness_penalty=True,
+)
 
 
 # Method policy registry
@@ -81,17 +109,33 @@ POLICY_MAP: dict[str, MethodPolicy] = {
         uses_instant_calibration=True,
         uses_reference_penalty=True,
     ),
+    # LEGACY always-on (E1/E3/E4 historical). Not the paper default.
     "raven": MethodPolicy(
-        uses_design_ratio=True,
-        uses_observation_ipw=True,
-        uses_usable_ipw=True,
-        uses_hajek_local_loss=True,
-        uses_instant_calibration=True,
-        uses_debt=True,
-        uses_reference_penalty=True,
-        uses_variance_penalty=True,
-        uses_staleness_penalty=True,
+        **_RAVEN_CORE,
         gate_mode="always_on",
+        legacy_only=True,
+        paper_method=False,
+    ),
+    "raven_legacy_always_on": MethodPolicy(
+        **_RAVEN_CORE,
+        gate_mode="always_on",
+        legacy_only=True,
+        paper_method=False,
+    ),
+    # Unique paper method: explicit pre-window Design, independent coverage.
+    "raven_mcs": MethodPolicy(
+        **_RAVEN_CORE,
+        design_control="configured",
+        method_version=CONFIGURED_METHOD_VERSION,
+        legacy_only=False,
+        paper_method=True,
+    ),
+    "raven_coverage_legacy": MethodPolicy(
+        **_RAVEN_CORE,
+        gate_mode="aggregate_coverage",
+        method_version="coverage-controlled-v1",
+        legacy_only=True,
+        paper_method=False,
     ),
     # E4 one-factor-at-a-time RAVEN ablations.  Keep every non-ablated RAVEN
     # component identical; do not substitute a historical partial method.
@@ -100,18 +144,14 @@ POLICY_MAP: dict[str, MethodPolicy] = {
         uses_instant_calibration=True, uses_debt=True, uses_reference_penalty=True,
         uses_variance_penalty=True, uses_staleness_penalty=True,
         gate_mode="always_off",
+        legacy_only=True,
+        paper_method=False,
     ),
     "raven_sag": MethodPolicy(
-        uses_design_ratio=True,
-        uses_observation_ipw=True,
-        uses_usable_ipw=True,
-        uses_hajek_local_loss=True,
-        uses_instant_calibration=True,
-        uses_debt=True,
-        uses_reference_penalty=True,
-        uses_variance_penalty=True,
-        uses_staleness_penalty=True,
+        **_RAVEN_CORE,
         gate_mode="sag",
+        legacy_only=True,
+        paper_method=False,
     ),
     "raven_wo_obs": MethodPolicy(
         uses_design_ratio=True, uses_usable_ipw=True, uses_hajek_local_loss=True,
@@ -146,43 +186,63 @@ POLICY_MAP: dict[str, MethodPolicy] = {
         uses_staleness_penalty=True,
         uses_oracle_propensity=True,
     ),
+    # F-1 diagnostic arm: identical to legacy "raven" except that the atomic observation
+    # propensity is the true p_obs_true_by_unit while q stays estimated.
+    "raven_oracle_p": MethodPolicy(
+        **_RAVEN_CORE,
+        gate_mode="always_on",
+        legacy_only=True,
+        paper_method=False,
+        uses_oracle_p=True,
+    ),
 }
 
 
+# Aliases never point raven_mcs at legacy always-on raven.
+METHOD_ALIASES: dict[str, str] = {
+    "centralall": "central_all",
+    "centraldelivered": "central_delivered",
+    "fedavg": "fedavg_window",
+    "fedau": "fedau_window",
+    "obsuse": "obsuse_window",
+    "fedasync": "fedasync_window",
+    "timealign": "timealign_agg",
+    "time_align": "timealign_agg",
+    "time_align_agg": "timealign_agg",
+    "flamf": "flamf_original",
+    "two_stage_hajek": "twostage_hajek",
+    "instant_calibration": "inst_cal",
+    "debt_calibration": "debt_cal",
+    "simoracle": "raven_simoracle",
+    "sag": "raven_sag",
+    "sag_raven": "raven_sag",
+    "raven_formal": "raven_mcs",
+    "raven_mcs_formal": "raven_mcs",
+    "raven_full_design_legacy": "raven_legacy_always_on",
+    "raven_mcs_coverage_legacy": "raven_coverage_legacy",
+}
+
+
+def resolve_method(method: str) -> str:
+    """Canonical POLICY_MAP key. raven_mcs is the unique paper method."""
+    normalized = str(method).strip().lower().replace("-", "_")
+    seen: set[str] = set()
+    cur = normalized
+    while True:
+        if cur in seen:
+            raise ValueError(f"method alias cycle involving {cur!r}")
+        seen.add(cur)
+        if cur in POLICY_MAP:
+            return cur
+        nxt = METHOD_ALIASES.get(cur)
+        if nxt is None or nxt == cur:
+            return cur
+        cur = nxt
+
+
 def get_method_policy(method: str) -> MethodPolicy:
     """Get the policy for a method by name."""
-    normalized = method.strip().lower().replace("-", "_")
-    if normalized in POLICY_MAP:
-        return POLICY_MAP[normalized]
-    # Alias mappings
-    aliases = {
-        "centralall": "central_all",
-        "centraldelivered": "central_delivered",
-        "fedavg": "fedavg_window",
-        "fedau": "fedau_window",
-        "fedau_window": "fedau_window",
-        "obsuse": "obsuse_window",
-        "obsuse_window": "obsuse_window",
-        "fedasync": "fedasync_window",
-        "timealign": "timealign_agg",
-        "time_align": "timealign_agg",
-        "time_align_agg": "timealign_agg",
-        "flamf": "flamf_original",
-        "local_hajek": "local_hajek",
-        "twostage_hajek": "twostage_hajek",
-        "two_stage_hajek": "twostage_hajek",
-        "inst_cal": "inst_cal",
-        "instant_calibration": "inst_cal",
-        "debt_cal": "debt_cal",
-        "debt_calibration": "debt_cal",
-        "raven_mcs": "raven",
-        "raven_simoracle": "raven_simoracle",
-        "simoracle": "raven_simoracle",
-        "raven_sag": "raven_sag",
-        "sag": "raven_sag",
-        "sag_raven": "raven_sag",
-    }
-    canonical = aliases.get(normalized, normalized)
+    canonical = resolve_method(method)
     if canonical in POLICY_MAP:
         return POLICY_MAP[canonical]
     return MethodPolicy()
diff --git a/src/raven_mcs/aggregation/methods.py b/src/raven_mcs/aggregation/methods.py
index 38509fd..08e7278 100644
--- a/src/raven_mcs/aggregation/methods.py
+++ b/src/raven_mcs/aggregation/methods.py
@@ -714,6 +714,12 @@ def get_aggregator(name: str) -> Aggregator:
         # 11. RAVEN-MCS
         "raven": RavenAggregator,
         "raven_mcs": RavenAggregator,
+        "raven_mcs_formal": RavenAggregator,
+        "raven_formal": RavenAggregator,
+        "raven_coverage_legacy": RavenAggregator,
+        "raven_mcs_coverage_legacy": RavenAggregator,
+        "raven_legacy_always_on": RavenAggregator,
+        "raven_full_design_legacy": RavenAggregator,
         "raven_sag": RavenAggregator,
         "sag": RavenAggregator,
         "sag_raven": RavenAggregator,
@@ -722,6 +728,8 @@ def get_aggregator(name: str) -> Aggregator:
         "raven_wo_use": RavenAggregator,
         "raven_wo_inst": RavenWoInstAggregator,
         "raven_wo_debt": RavenAggregator,
+        # F-1 diagnostic arm: same aggregator as "raven"; only the runner-side p map differs.
+        "raven_oracle_p": RavenAggregator,
         # 12. RAVEN-SimOracle
         "raven_simoracle": RavenSimOracleAggregator,
         "simoracle": RavenSimOracleAggregator,
diff --git a/src/raven_mcs/aggregation/p2_cvxpy.py b/src/raven_mcs/aggregation/p2_cvxpy.py
index 6b28f15..333d629 100644
--- a/src/raven_mcs/aggregation/p2_cvxpy.py
+++ b/src/raven_mcs/aggregation/p2_cvxpy.py
@@ -53,6 +53,7 @@ def solve_p2(
     max_server_learning_rate: float,
     tolerance: float = 1e-6,
     backend: str = "CLARABEL",
+    instant_calibration: bool = True,
 ) -> P2Result:
     """
     Minimize
@@ -66,6 +67,7 @@ def solve_p2(
         lambda_beta=lambda_beta,
         lambda_group=lambda_group,
         max_server_learning_rate=max_server_learning_rate,
+        instant_calibration=instant_calibration,
     )
     m = np.asarray(coverage_matrix, dtype=np.float64)
     target = np.asarray(mu, dtype=np.float64)
@@ -73,6 +75,13 @@ def solve_p2(
     q = np.asarray(debt, dtype=np.float64)
     v_diag = np.asarray(variance_diag, dtype=np.float64)
     tau = np.asarray(staleness, dtype=np.float64)
+    if not np.all(np.isfinite(v_diag)):
+        v_diag = np.where(np.isfinite(v_diag), v_diag, 1.0)
+    v_diag = np.maximum(v_diag, 0.0)
+    if not np.all(np.isfinite(m)) or not np.all(np.isfinite(target)) or not np.all(
+        np.isfinite(beta)
+    ) or not np.all(np.isfinite(q)) or not np.all(np.isfinite(tau)):
+        raise ValueError("P2 inputs must be finite")
     if m.ndim != 2:
         raise ValueError("coverage_matrix must be groups × clients")
     n_groups, n_active = m.shape
diff --git a/src/raven_mcs/correction/design_ratio.py b/src/raven_mcs/correction/design_ratio.py
index 894c4f3..fe174d3 100644
--- a/src/raven_mcs/correction/design_ratio.py
+++ b/src/raven_mcs/correction/design_ratio.py
@@ -27,12 +27,14 @@ def zeta_hat_stratum(
 
     ζ̂_{k,r,s} = π^tar_{k,s} / max(π̂^opp_{k,s,r}, π_min)
     """
-    if pi_min <= 0:
+    if not np.isfinite(pi_min) or pi_min <= 0:
         raise ValueError("pi_min must be positive")
     tar = np.asarray(pi_tar, dtype=np.float64)
     opp = np.asarray(pi_hat_opp, dtype=np.float64)
     if tar.shape != opp.shape:
         raise ValueError("pi_tar and pi_hat_opp must share shape")
+    if not np.all(np.isfinite(tar)) or not np.all(np.isfinite(opp)):
+        raise ValueError("DESIGN_INPUT_ERROR: design-ratio masses must be finite")
     if np.any(tar < 0) or np.any(opp < 0):
         raise ValueError("design-ratio masses must be nonnegative")
     return tar / np.maximum(opp, float(pi_min))
diff --git a/src/raven_mcs/correction/pi_target.py b/src/raven_mcs/correction/pi_target.py
index 9dbb82a..9090a2d 100644
--- a/src/raven_mcs/correction/pi_target.py
+++ b/src/raven_mcs/correction/pi_target.py
@@ -16,7 +16,14 @@ def build_pi_target(
     *,
     split: str = "test",
 ) -> pd.DataFrame:
-    """Build pi target from frozen station-client opportunity support."""
+    """Build pi_tar(k,s) = Lambda_s^tar · lambda_{k|s}^tar.
+
+    When each stratum maps to a unique client (SensorScope/U-Air station-level s),
+    lambda_{k|s}=1 and pi_tar(k,s)=Lambda_s.
+
+    When multiple clients share a stratum (Traffic 4-region s), lambda_{k|s} is the
+    within-stratum client mass share on the frozen TEST support.
+    """
     target = TargetBuilder(
         group_mapper=GroupMapper("target_group_main"),
     ).build(atomic, split=split)
@@ -25,56 +32,106 @@ def build_pi_target(
         ["unit_id", "spatial_id", "opportunity_stratum"],
     ].copy()
     selected["unit_id"] = selected["unit_id"].astype(str)
-    selected["opportunity_stratum"] = selected[
-        "opportunity_stratum"
-    ].astype(str)
+    selected["opportunity_stratum"] = selected["opportunity_stratum"].astype(str)
     selected["target_mass"] = selected["unit_id"].map(target.atom_mass)
 
-    mapping = {
-        str(station): str(client)
-        for station, client in station_to_client.items()
-    }
+    mapping = {str(station): str(client) for station, client in station_to_client.items()}
     selected["client_id"] = selected["spatial_id"].astype(str).map(mapping)
     if selected["client_id"].isna().any():
         raise ValueError("positive target station lacks frozen client mapping")
+
     lambda_s = selected.groupby("opportunity_stratum")["target_mass"].sum()
-    target_support = selected[
-        ["client_id", "opportunity_stratum"]
-    ].drop_duplicates()
-    if bool(
-        target_support.groupby("opportunity_stratum")["client_id"].nunique().gt(1).any()
-    ):
-        raise ValueError("each stratum must map to exactly one client")
-    all_units = atomic[
-        ["spatial_id", "opportunity_stratum"]
-    ].copy()
+    mass_ks = (
+        selected.groupby(["client_id", "opportunity_stratum"])["target_mass"].sum().reset_index()
+    )
+    mass_ks = mass_ks.rename(columns={"target_mass": "mass_ks"})
+
+    all_units = atomic[["spatial_id", "opportunity_stratum"]].copy()
     all_units["opportunity_stratum"] = all_units["opportunity_stratum"].astype(str)
     all_units["client_id"] = all_units["spatial_id"].astype(str).map(mapping)
     if all_units["client_id"].isna().any():
         raise ValueError("atomic station lacks frozen client mapping")
-    support = all_units[
-        ["client_id", "opportunity_stratum"]
-    ].drop_duplicates()
-    if bool(
-        support.groupby("opportunity_stratum")["client_id"].nunique().ne(1).any()
-    ):
-        raise ValueError("station-client support is not unique by stratum")
-    support["Lambda_s_tar"] = support["opportunity_stratum"].map(
-        lambda_s,
-    ).fillna(0.0)
-    support["lambda_k_given_s_tar"] = 1.0
-    support["pi_k_s_tar"] = support["Lambda_s_tar"]
+    support = all_units[["client_id", "opportunity_stratum"]].drop_duplicates()
+    support = support.merge(mass_ks, on=["client_id", "opportunity_stratum"], how="left")
+    support["mass_ks"] = support["mass_ks"].fillna(0.0)
+    support["Lambda_s_tar"] = support["opportunity_stratum"].map(lambda_s).fillna(0.0)
+    # lambda_{k|s} = mass_ks / Lambda_s when Lambda_s>0; else 0
+    support["lambda_k_given_s_tar"] = 0.0
+    pos = support["Lambda_s_tar"] > 0
+    support.loc[pos, "lambda_k_given_s_tar"] = (
+        support.loc[pos, "mass_ks"] / support.loc[pos, "Lambda_s_tar"]
+    )
+    support["pi_k_s_tar"] = support["Lambda_s_tar"] * support["lambda_k_given_s_tar"]
     support["support_flag"] = True
-    support = support.sort_values(
-        ["client_id", "opportunity_stratum"],
-    ).reset_index(drop=True)
+    support = support.drop(columns=["mass_ks"])
+    support = support.sort_values(["client_id", "opportunity_stratum"]).reset_index(drop=True)
+
+    # Unique-client strata still get lambda=1 when that client owns all mass
     if abs(float(support["pi_k_s_tar"].sum()) - 1.0) > 1e-12:
-        raise ValueError("pi target does not sum to one")
+        raise ValueError(
+            f"pi target does not sum to one (sum={float(support['pi_k_s_tar'].sum())})"
+        )
     if bool((support["pi_k_s_tar"] < 0).any()):
         raise ValueError("pi target must be nonnegative")
     return support
 
 
+def build_pi_target_support_compatible(
+    atomic: pd.DataFrame,
+    station_to_client: dict[str, str],
+    *,
+    split: str = "test",
+    pi_opp_joint: dict[tuple[str, str], float],
+) -> pd.DataFrame:
+    """Equal mixture of the support-projected test target and frozen π^opp.
+
+    Pre-registered G1 Path A construction (not tuned):
+
+        π^{test,feas} = Π_{S_feas}(π^{test}),
+        π^{sc} = (π^{test,feas} + π^{opp}) / 2,
+
+    where S_feas is the frozen TRAIN client×stratum support.  Every feasible
+    pair with π^opp>0 receives strictly positive mass, so train-only strata
+    cannot zero a client out of E_r.  Evaluation μ stays the public test
+    artifact; only the Design-ratio numerator changes.
+    """
+    if not pi_opp_joint:
+        raise ValueError("support-compatible target requires frozen joint pi_opp")
+    test = build_pi_target(atomic, station_to_client, split=split)
+    out = test.copy()
+    feas = set(pi_opp_joint)
+    test_on_feas = []
+    opp_aligned = []
+    for row in out.itertuples(index=False):
+        key = (str(row.client_id), str(row.opportunity_stratum))
+        test_mass = float(row.pi_k_s_tar) if key in feas else 0.0
+        test_on_feas.append(test_mass)
+        opp_aligned.append(float(pi_opp_joint.get(key, 0.0)))
+    test_on_feas_arr = pd.Series(test_on_feas, index=out.index, dtype="float64")
+    opp_arr = pd.Series(opp_aligned, index=out.index, dtype="float64")
+    z_test = float(test_on_feas_arr.sum())
+    z_opp = float(opp_arr.sum())
+    if z_test <= 0.0 or z_opp <= 0.0:
+        raise ValueError("support-compatible target requires positive test-on-feas and opp mass")
+    test_feas = test_on_feas_arr / z_test
+    opp_norm = opp_arr / z_opp
+    out["pi_k_s_tar_test"] = out["pi_k_s_tar"]
+    out["pi_k_s_tar"] = 0.5 * test_feas + 0.5 * opp_norm
+    out["Lambda_s_tar"] = out.groupby("opportunity_stratum")["pi_k_s_tar"].transform("sum")
+    pos = out["Lambda_s_tar"] > 0
+    out["lambda_k_given_s_tar"] = 0.0
+    out.loc[pos, "lambda_k_given_s_tar"] = (
+        out.loc[pos, "pi_k_s_tar"] / out.loc[pos, "Lambda_s_tar"]
+    )
+    if abs(float(out["pi_k_s_tar"].sum()) - 1.0) > 1e-12:
+        raise ValueError(
+            f"support-compatible pi target does not sum to one (sum={float(out['pi_k_s_tar'].sum())})"
+        )
+    if bool((out["pi_k_s_tar"] < 0).any()):
+        raise ValueError("support-compatible pi target must be nonnegative")
+    return out
+
+
 def load_pi_target(path: Path) -> tuple[dict[tuple[str, str], float], str]:
     frame = pd.read_parquet(path)
     required = {"client_id", "opportunity_stratum", "pi_k_s_tar", "support_flag"}
diff --git a/src/raven_mcs/data/window_dataset.py b/src/raven_mcs/data/window_dataset.py
index 82ead7e..a2059b6 100644
--- a/src/raven_mcs/data/window_dataset.py
+++ b/src/raven_mcs/data/window_dataset.py
@@ -7,7 +7,7 @@ risk set records for local training.
 from __future__ import annotations
 
 from dataclasses import dataclass, field
-from typing import Any
+from typing import Any, Mapping
 
 import numpy as np
 
@@ -63,6 +63,7 @@ def extract_window_slice(
     event_trace_events: Any,  # pd.DataFrame with EventTrace schema
     processed_dataset: Any,  # ProcessedDataset
     coarse_time_groups: int | None = None,
+    h_by_unit: Mapping[str, int] | None = None,
 ) -> WindowDataSlice:
     """Extract per-window observation records from EventTrace and atomic units.
 
@@ -97,11 +98,29 @@ def extract_window_slice(
         ordered_obs_ids: list[str] = []
         O_array: list[float] = []
 
+        feats = row["opportunity_features"] if "opportunity_features" in row else {}
+        if isinstance(feats, str):
+            import json
+
+            feats = json.loads(feats)
+        if not isinstance(feats, dict):
+            feats = {}
+        stratum_by_unit = feats.get("opportunity_stratum_by_unit", {})
+        if not isinstance(stratum_by_unit, dict):
+            stratum_by_unit = {}
+        group_by_unit = feats.get("target_group_by_unit", {})
+        if not isinstance(group_by_unit, dict):
+            group_by_unit = {}
+
         for rid in risk_ids:
             unit = processed_dataset.get_atomic_by_id(rid)
             if unit is not None:
                 risk_strata.append(unit.opportunity_stratum)
-                if coarse_time_groups is None:
+                if h_by_unit is not None:
+                    if str(rid) not in h_by_unit:
+                        raise ValueError(f"unit {rid} missing from frozen paper h(i) map")
+                    risk_groups.append(int(h_by_unit[str(rid)]))
+                elif coarse_time_groups is None:
                     risk_groups.append(unit.target_group)
                 elif coarse_time_groups == 4:
                     utc_hour = int(np.floor(unit.absolute_time)) % 24
@@ -112,8 +131,15 @@ def extract_window_slice(
                         min(coarse_time_groups - 1, int(unit.time_index * coarse_time_groups / total_slots))
                     )
             else:
-                risk_strata.append("unknown")
-                risk_groups.append(-1)
+                # R=1 O=0 occupancy units are absent from labeled atomic tables.
+                # Do not invent Y; they must not appear in observed_unit_ids.
+                if rid in obs_ids:
+                    raise ValueError(f"Observed unit is absent from processed data: {rid}")
+                risk_strata.append(str(stratum_by_unit.get(str(rid), "unknown")))
+                if str(rid) in group_by_unit:
+                    risk_groups.append(int(group_by_unit[str(rid)]))
+                else:
+                    risk_groups.append(-1)
 
             is_observed = 1.0 if rid in obs_ids else 0.0
             O_array.append(is_observed)
@@ -135,13 +161,6 @@ def extract_window_slice(
         if U_val == 1:
             active_client_ids.append(client_id)
 
-        feats = row["opportunity_features"] if "opportunity_features" in row else {}
-        if isinstance(feats, str):
-            import json
-
-            feats = json.loads(feats)
-        if not isinstance(feats, dict):
-            feats = {}
         p_obs_map = feats.get("p_obs_true_by_unit", {})
         if not isinstance(p_obs_map, dict):
             p_obs_map = {}
diff --git a/src/raven_mcs/experiments/e1_entry.py b/src/raven_mcs/experiments/e1_entry.py
index 7cef86e..edb8714 100644
--- a/src/raven_mcs/experiments/e1_entry.py
+++ b/src/raven_mcs/experiments/e1_entry.py
@@ -604,6 +604,8 @@ def run_official_method(
     evaluation_split: str = "test",
     weight_safety: dict[str, float] | None = None,
     formal: bool = False,
+    design: str | None = None,
+    design_source: str = "explicit_api",
 ) -> Path:
     if method not in E1_METHODS:
         raise ValueError(f"method is not in frozen E1 registry: {method}")
@@ -667,6 +669,7 @@ def run_official_method(
         pi_min=float(weight_safety.get("pi_min", 1e-6)),
         d_max=float(weight_safety.get("d_max", 10.0)),
         q_min=float(weight_safety.get("q_min", 0.05)),
+        design=design, design_source=design_source,
     )
     initial_model_hash = runner._theta_hash()
     metrics = runner.run()
@@ -852,6 +855,11 @@ def run_official_method(
                 bool(solver_df.iloc[item.window_id]["fallback_used"])
                 if item.window_id < len(solver_df) else False
             ),
+            "configured_design": item.configured_design,
+            "actual_design": item.actual_design,
+            "coverage_gate": item.coverage_gate,
+            "configuration_source": item.configuration_source,
+            "method_version": item.method_version,
             "model_hash_before": item.theta_hash_before,
             "model_hash_after": item.theta_hash_after,
         })
@@ -1017,6 +1025,10 @@ def run_official_method(
         "experiment": "E1_balanced",
         "dataset": "sensorscope",
         "method": method,
+        "method_version": runner.policy.method_version,
+        "design_control": runner.policy.design_control,
+        "design_configuration": runner.design_configuration.to_dict() if runner.design_configuration else None,
+        "coverage_role": "diagnostic_only" if runner.policy.design_control == "configured" else "legacy_policy",
         "scenario": "balanced",
         "seed": int(seed),
         "num_windows": int(num_windows),
diff --git a/src/raven_mcs/experiments/sag_runtime.py b/src/raven_mcs/experiments/sag_runtime.py
index 42f52dd..1125f45 100644
--- a/src/raven_mcs/experiments/sag_runtime.py
+++ b/src/raven_mcs/experiments/sag_runtime.py
@@ -13,14 +13,60 @@ from raven_mcs.e3.canary.dataset_load import load_paper_dataset, load_spatial_to
 from raven_mcs.e3.real_runner.generator_r3 import build_joint_pi_opp
 from raven_mcs.e3.stratum_seal.remap import apply_sealed_opportunity_stratum
 from raven_mcs.e3.target_pair.target_wiring import production_target_bundle
+from raven_mcs.sag.deployment_groups import (
+    load_paper_h_map,
+    paper_mu,
+    unit_to_h,
+    write_paper_h_map,
+)
+from raven_mcs.sag.target_law import build_frozen_atomic_target_law, build_target_law_v1
 from raven_mcs.simulation.event_trace import EventTrace, load_event_trace
 
-
 METHODS = ("raven", "raven_wo_design", "raven_sag")
 
 SEALED_EVENTTRACE = Path("artifacts/e3_formal_runs_r1/eventtraces")
 
 
+def attach_paper_h(prepared: dict[str, Any], *, root: Path) -> dict[str, Any]:
+    """Attach the frozen 4-block paper h(i) map. Does not change s(i)/π^{tar}_{k,s}."""
+    name = str(prepared["dataset_name"])
+    try:
+        payload = load_paper_h_map(root, name)
+    except FileNotFoundError:
+        payload = write_paper_h_map(root, prepared["dataset"].atomic_df, dataset=name)
+    prepared["paper_h"] = payload
+    prepared["paper_h_by_unit"] = unit_to_h(payload)
+    prepared["paper_mu"] = paper_mu(payload)
+    prepared["paper_n_groups"] = 4
+    return prepared
+
+
+def attach_unified_target(prepared: dict[str, Any], *, root: Path) -> dict[str, Any]:
+    """Overwrite μ and π^{tar} from TARGET_LAW_RULE_V1 (train μ_g, test I_dep).
+
+    Does not change E3 production_target_bundle, s(i), or paper h(i) maps.
+    """
+    prepared = attach_paper_h(prepared, root=root)
+    law = build_target_law_v1(
+        prepared["atomic_sealed"],
+        prepared["spatial_to_client"],
+        prepared["paper_h_by_unit"],
+        dataset=str(prepared["dataset_name"]),
+    )
+    prepared["target_law"] = law
+    prepared["paper_mu"] = law.mu
+    prepared["pi_target"] = law.pi_target
+    prepared["varpi_tar"] = law.varpi
+    prepared["target_law_hash"] = law.law_hash
+    prepared["target_law_r1c"] = build_frozen_atomic_target_law(
+        prepared["atomic_sealed"],
+        prepared["spatial_to_client"],
+        prepared["paper_h_by_unit"],
+        dataset=str(prepared["dataset_name"]),
+    )
+    return prepared
+
+
 def eventtrace_dir(root: Path, dataset: str, seed: int) -> Path:
     return Path(root) / SEALED_EVENTTRACE / dataset / f"seed{seed}" / "training_eventtrace"
 
@@ -117,4 +163,6 @@ def prepare_sag_bundle(
         "head_tail": bundle["head_tail"],
         "target_artifact_path": bundle["artifact_path"],
         "target_artifact_sha256": bundle["artifact_sha256"],
+        "n_groups_runtime_fine": n_groups,
+        "paper_h": None,
     }
diff --git a/src/raven_mcs/sag/__init__.py b/src/raven_mcs/sag/__init__.py
index 1e4e636..7064873 100644
--- a/src/raven_mcs/sag/__init__.py
+++ b/src/raven_mcs/sag/__init__.py
@@ -7,6 +7,7 @@ Dataset identity is never a Gate feature.
 
 from raven_mcs.sag.certificates import (
     CertificateBundle,
+    CertificateContext,
     FrozenSagThresholds,
     compute_certificates,
 )
@@ -26,6 +27,7 @@ from raven_mcs.sag.timing import SagStages, assert_stage_order
 
 __all__ = [
     "CertificateBundle",
+    "CertificateContext",
     "CounterfactualAudit",
     "FORBIDDEN_GATE_FEATURES",
     "FrozenSagThresholds",
diff --git a/src/raven_mcs/sag/certificates.py b/src/raven_mcs/sag/certificates.py
index 837af3b..7834c22 100644
--- a/src/raven_mcs/sag/certificates.py
+++ b/src/raven_mcs/sag/certificates.py
@@ -1,17 +1,21 @@
 """Auditable SAG certificates from completed-window history only (F_{r-}).
 
-v1 models: empirical mean ± one-sided normal SE, and rolling quantiles.
-No neural / RL Gate. Coverage target is frozen at 95% (delta_cal=0.05).
+Formal coverage Gate object (R1l): aggregate realized C_t with the
+WARMUP/CERTIFIED/RESET conformal LCB. Pairwise simultaneous positive LCBs
+remain diagnostic-only (event_count_cp / dynamic_max_residual).
+B_tot uses the Theorem-3/4 decomposition.
 """
 
 from __future__ import annotations
 
-from dataclasses import asdict, dataclass
-from typing import Any, Sequence
+from dataclasses import asdict, dataclass, field
+from typing import Any, Mapping, Sequence
 
 import numpy as np
+from scipy.stats import beta as beta_dist
 
 Z_ONE_SIDED_95 = 1.6448536269514722
+EB_DELTA = 0.05
 
 
 @dataclass(frozen=True)
@@ -24,6 +28,7 @@ class FrozenSagThresholds:
     tau_safe: float = 4.0
     delta_cal: float = 0.05
     lookback_min: int = 8
+    n_min_conformal: int = 19
     lookback_max: int = 32
     quantile_level: float = 0.95
     lambda_group: float = 1.0
@@ -45,6 +50,23 @@ class FrozenSagThresholds:
         }
 
 
+@dataclass
+class CertificateContext:
+    """F_{r-}/public context. Must not contain current-window R/O/U/A/M."""
+
+    pi_target: dict[tuple[str, str], float] = field(default_factory=dict)
+    pi_safe: float | None = None
+    b_q: float = 0.0
+    n_clients: int | None = None
+    n_groups: int | None = None
+    source: str = ""
+    cov_mode: str = "event_count_cp"
+    rolling_L: int | None = None
+    regime_certified: bool = True
+    had_active_certified_regime: bool = True
+    c_hat: float | None = None
+
+
 @dataclass
 class CertificateBundle:
     C_cov_LCB: float
@@ -63,6 +85,7 @@ class CertificateBundle:
     lookback: int
     cold_start: bool
     missing_certificate: bool
+    diagnostics: dict[str, Any] = field(default_factory=dict)
 
     def as_gate_inputs(self) -> dict[str, Any]:
         return {
@@ -120,11 +143,18 @@ def mean_ucb(values: Sequence[Any], z: float = Z_ONE_SIDED_95) -> float:
     return float(mean + z * se)
 
 
-def rolling_quantile(values: Sequence[Any], level: float) -> float:
-    xs = _finite_list(values)
+def conformal_upper_quantile(values: Sequence[Any], level: float) -> float:
+    """Finite-sample order-statistic UCB: k = ceil((n+1) q)."""
+    xs = sorted(_finite_list(values))
     if not xs:
         return float("nan")
-    return float(np.quantile(np.asarray(xs, dtype=np.float64), float(level)))
+    n = len(xs)
+    k = min(n, max(1, int(np.ceil((n + 1) * float(level)))))
+    return float(xs[k - 1])
+
+
+def rolling_quantile(values: Sequence[Any], level: float) -> float:
+    return conformal_upper_quantile(values, level)
 
 
 def binary_ucb(values: Sequence[Any], z: float = Z_ONE_SIDED_95) -> float:
@@ -138,6 +168,33 @@ def binary_ucb(values: Sequence[Any], z: float = Z_ONE_SIDED_95) -> float:
     return float(min(1.0, p + z * se + 1.0 / n))
 
 
+def empirical_bernstein_lcb(
+    values: Sequence[Any],
+    *,
+    delta: float = EB_DELTA,
+    radius: float = 1.0,
+) -> float:
+    """One-sided empirical-Bernstein LCB on [0, radius] completed-window masses."""
+    xs = _finite_list(values)
+    if not xs:
+        return float("nan")
+    arr = np.asarray(xs, dtype=np.float64)
+    n = float(arr.size)
+    mean = float(arr.mean())
+    if arr.size == 1:
+        return float(max(0.0, mean))
+    var = float(arr.var(ddof=1))
+    logt = float(np.log(1.0 / float(delta)))
+    return float(
+        max(
+            0.0,
+            mean
+            - np.sqrt(max(2.0 * var * logt / n, 0.0))
+            - 3.0 * float(radius) * logt / n,
+        )
+    )
+
+
 def b_tot_from_parts(
     b_srv: float,
     delta_a: float,
@@ -147,49 +204,460 @@ def b_tot_from_parts(
     return float(b_srv) + 2.0 * float(delta_a) + 2.0 * float(delta_cal)
 
 
+def pair_key(item: Any) -> tuple[str, str]:
+    if isinstance(item, (tuple, list)) and len(item) >= 2:
+        return str(item[0]), str(item[1])
+    if isinstance(item, str) and "|" in item:
+        left, right = item.split("|", 1)
+        return left, right
+    raise TypeError(f"cannot parse pair key: {item!r}")
+
+
+def encode_pair(key: tuple[str, str]) -> str:
+    return f"{key[0]}|{key[1]}"
+
+
+def opportunity_mass_map(row: Mapping[str, Any]) -> dict[tuple[str, str], float]:
+    raw = row.get("opp_mass_by_pair") or {}
+    out: dict[tuple[str, str], float] = {}
+    if not isinstance(raw, Mapping):
+        return out
+    for key, value in raw.items():
+        try:
+            out[pair_key(key)] = float(value)
+        except (TypeError, ValueError):
+            continue
+    return out
+
+
+def opportunity_count_map(row: Mapping[str, Any]) -> dict[tuple[str, str], float]:
+    raw = row.get("opp_count_by_pair") or {}
+    out: dict[tuple[str, str], float] = {}
+    if not isinstance(raw, Mapping):
+        return out
+    for key, value in raw.items():
+        try:
+            out[pair_key(key)] = float(value)
+        except (TypeError, ValueError):
+            continue
+    return out
+
+
+def clopper_pearson_lcb(x: float, n: float, delta: float) -> float:
+    """One-sided Clopper–Pearson lower bound for a binomial proportion.
+
+    LCB = 0 if x<=0; otherwise the δ-quantile of Beta(x, n-x+1).
+    """
+    try:
+        xx = float(x)
+        nn = float(n)
+        dd = float(delta)
+    except (TypeError, ValueError):
+        return float("nan")
+    if not (np.isfinite(xx) and np.isfinite(nn) and np.isfinite(dd)):
+        return float("nan")
+    if nn <= 0.0 or xx < 0.0 or xx > nn or dd <= 0.0 or dd >= 1.0:
+        return 0.0 if nn > 0.0 and xx <= 0.0 and 0.0 < dd < 1.0 else float("nan")
+    if xx <= 0.0:
+        return 0.0
+    return float(max(0.0, min(1.0, beta_dist.ppf(dd, xx, nn - xx + 1.0))))
+
+
+def lower_pi_opp_event_count_by_pair(
+    history: Sequence[Mapping[str, Any]],
+    pairs: Sequence[tuple[str, str]],
+    *,
+    delta: float,
+    bonferroni: bool = True,
+) -> dict[tuple[str, str], dict[str, float]]:
+    """F_{r-}-measurable CP LCB from completed-window event counts (all t<r)."""
+    counts: dict[tuple[str, str], float] = {key: 0.0 for key in pairs}
+    total = 0.0
+    n_windows = 0
+    for row in history:
+        cmap = opportunity_count_map(row)
+        win_total = row.get("opp_event_total")
+        try:
+            win_n = float(win_total) if win_total is not None else float(sum(cmap.values()))
+        except (TypeError, ValueError):
+            win_n = float(sum(cmap.values()))
+        if win_n < 0 or not np.isfinite(win_n):
+            continue
+        total += win_n
+        n_windows += 1
+        for key in pairs:
+            counts[key] += float(cmap.get(key, 0.0))
+    m = max(1, len(pairs))
+    delta_pair = (float(delta) / float(m)) if bonferroni else float(delta)
+    out: dict[tuple[str, str], dict[str, float]] = {}
+    for key in pairs:
+        x = float(counts[key])
+        hat = (x / total) if total > 0.0 else float("nan")
+        lcb = clopper_pearson_lcb(x, total, delta_pair)
+        out[key] = {
+            "pi_hat_opp": hat,
+            "lower_pi_opp": lcb,
+            "n": float(total),
+            "count": x,
+            "n_windows": float(n_windows),
+            "delta_pair": float(delta_pair),
+            "m_target_positive": float(m),
+        }
+    return out
+
+
+def pair_presence_distribution(
+    pairs: Sequence[tuple[str, str]],
+) -> dict[tuple[str, str], float]:
+    """DIAGNOSTIC ONLY: unique-pair uniform. Must not enter SAG C_cov."""
+    uniq = sorted({(str(k), str(s)) for k, s in pairs})
+    if not uniq:
+        return {}
+    mass = 1.0 / float(len(uniq))
+    return {key: mass for key in uniq}
+
+
+def window_opportunity_event_counts(
+    pairs: Sequence[tuple[str, str]],
+    weights: Sequence[float] | None = None,
+) -> dict[tuple[str, str], float]:
+    """Completed-window opportunity-event counts/mass N^{opp}_{k,s}."""
+    counts: dict[tuple[str, str], float] = {}
+    if weights is None:
+        for client, stratum in pairs:
+            key = (str(client), str(stratum))
+            counts[key] = counts.get(key, 0.0) + 1.0
+        return counts
+    if len(weights) != len(pairs):
+        raise ValueError("opportunity-event weights must align with events")
+    for (client, stratum), weight in zip(pairs, weights):
+        key = (str(client), str(stratum))
+        counts[key] = counts.get(key, 0.0) + float(weight)
+    return counts
+
+
+def window_opportunity_masses(
+    pairs: Sequence[tuple[str, str]],
+    weights: Sequence[float] | None = None,
+) -> dict[tuple[str, str], float]:
+    """Completed-window π^{opp}_{k,s} from event counts/mass, not unique-pair presence."""
+    counts = window_opportunity_event_counts(pairs, weights)
+    total = float(sum(counts.values()))
+    if total <= 0.0:
+        return {}
+    return {key: float(val) / total for key, val in counts.items()}
+
+
+def lower_pi_opp_by_pair(
+    history: Sequence[Mapping[str, Any]],
+    pairs: Sequence[tuple[str, str]],
+) -> dict[tuple[str, str], dict[str, float]]:
+    """F_{r-}-measurable EB LCB on completed-window opportunity masses."""
+    out: dict[tuple[str, str], dict[str, float]] = {}
+    series: dict[tuple[str, str], list[float]] = {key: [] for key in pairs}
+    for row in history:
+        masses = opportunity_mass_map(row)
+        for key in pairs:
+            series[key].append(float(masses.get(key, 0.0)))
+    for key, values in series.items():
+        hat = float(np.mean(values)) if values else float("nan")
+        lcb = empirical_bernstein_lcb(values)
+        out[key] = {"pi_hat_opp": hat, "lower_pi_opp": lcb, "n": float(len(values))}
+    return out
+
+
+def c_cov_from_opportunity_lcb(
+    pi_target: Mapping[tuple[str, str], float],
+    lowers: Mapping[tuple[str, str], Mapping[str, float]],
+    pi_safe: float,
+) -> dict[str, Any]:
+    certified = 0.0
+    total = 0.0
+    failures: list[dict[str, Any]] = []
+    n_pos = 0
+    for key, mass in pi_target.items():
+        w = float(mass)
+        if w <= 0.0:
+            continue
+        n_pos += 1
+        total += w
+        rec = lowers.get((str(key[0]), str(key[1])), {})
+        lower = rec.get("lower_pi_opp", float("nan"))
+        try:
+            ok = float(lower) >= float(pi_safe)
+        except (TypeError, ValueError):
+            ok = False
+        if ok:
+            certified += w
+        else:
+            failures.append(
+                {
+                    "client": str(key[0]),
+                    "stratum": str(key[1]),
+                    "pi_tar": w,
+                    "pi_hat_opp": rec.get("pi_hat_opp"),
+                    "lower_pi_opp": lower,
+                }
+            )
+    c_cov = float(certified / total) if total > 0 else float("nan")
+    failures.sort(key=lambda row: float(row.get("pi_tar") or 0.0), reverse=True)
+    return {
+        "C_cov_LCB": c_cov,
+        "target_mass_certified": certified,
+        "target_mass_total": total,
+        "number_target_positive_pairs": n_pos,
+        "pi_safe": float(pi_safe),
+        "top_failures": failures[:8],
+    }
+
+
+def provisional_pi_safe_from_public_opp(
+    pi_target: Mapping[tuple[str, str], float],
+    pi_opp_joint: Mapping[tuple[str, str], float],
+    *,
+    quantile: float = 0.10,
+) -> dict[str, Any]:
+    masses = [
+        float(pi_opp_joint.get(key, 0.0))
+        for key, w in pi_target.items()
+        if float(w) > 0.0
+    ]
+    masses = [x for x in masses if np.isfinite(x) and x > 0.0]
+    candidates: dict[str, float] = {}
+    for name, q in (("q05", 0.05), ("q10", 0.10), ("q25", 0.25)):
+        candidates[name] = float(np.quantile(masses, q)) if masses else float("nan")
+    chosen = candidates.get(
+        {0.05: "q05", 0.10: "q10", 0.25: "q25"}.get(float(quantile), "q10"),
+        float("nan"),
+    )
+    return {
+        "pi_safe": chosen,
+        "quantile": float(quantile),
+        "n_positive_target_pairs": len(masses),
+        "candidates": candidates,
+        "source": "public_pi_opp_joint_quantile_on_target_positive_pairs",
+        "status": "PI_SAFE_REQUIRES_FREEZE_DECISION",
+        "frozen": False,
+    }
+
+
+def b_tot_decomposition(
+    *,
+    delta_beta_ucb: float,
+    delta_m_ucb: float,
+    delta_v_ucb: float,
+    b_m_pre: float,
+    b_q: float,
+    delta_a_ucb: float,
+    delta_cal: float,
+    n_groups: int,
+    lambda_group: float,
+    lambda_beta: float,
+    lambda_variance: float,
+) -> dict[str, float]:
+    term_beta = float(delta_beta_ucb)
+    term_m = (
+        (float(b_q) + float(lambda_group) * (2.0 * float(b_m_pre) + 1.0))
+        / float(lambda_beta)
+        * float(delta_m_ucb)
+    )
+    term_v = float(lambda_variance) / float(lambda_beta) * float(delta_v_ucb)
+    d_alpha = term_beta + term_m + term_v
+    service_direct = float(delta_m_ucb)
+    service_alpha = float(b_m_pre) * d_alpha
+    b_srv = float(np.sqrt(max(int(n_groups), 1))) * (service_direct + service_alpha)
+    active = 2.0 * float(delta_a_ucb)
+    cal = 2.0 * float(delta_cal)
+    return {
+        "B_M_pre": float(b_m_pre),
+        "B_Q": float(b_q),
+        "Delta_beta_UCB": float(delta_beta_ucb),
+        "Delta_M_UCB": float(delta_m_ucb),
+        "Delta_V_UCB": float(delta_v_ucb),
+        "term_beta": float(term_beta),
+        "term_M": float(term_m),
+        "term_V": float(term_v),
+        "D_alpha_UCB": float(d_alpha),
+        "service_direct_M_term": float(service_direct),
+        "service_alpha_term": float(service_alpha),
+        "B_srv_UCB": float(b_srv),
+        "active_set_term": float(active),
+        "cal_failure_term": float(cal),
+        "B_tot_UCB": float(b_tot_from_parts(b_srv, delta_a_ucb, delta_cal)),
+    }
+
+
 def compute_certificates(
     history: Sequence[Mapping[str, Any]],
     thresholds: FrozenSagThresholds,
+    context: CertificateContext | None = None,
 ) -> CertificateBundle:
     """Build F_{r-}-measurable certificates from completed windows only."""
+    ctx = context or CertificateContext()
     n = len(history)
     lookback = min(int(thresholds.lookback_max), n)
     recent = list(history[-lookback:]) if lookback else []
     cold = n < int(thresholds.lookback_min)
     delta_cal = float(thresholds.delta_cal)
 
-    cov_lcb = mean_lcb([row.get("realized_C_cov") for row in recent])
+    target_pairs = [
+        (str(k[0]), str(k[1]))
+        for k, w in ctx.pi_target.items()
+        if float(w) > 0.0
+    ]
+    has_counts = any(opportunity_count_map(row) or row.get("opp_event_total") for row in history)
+    if str(ctx.cov_mode) == "aggregate_stable_regime":
+        from raven_mcs.sag.aggregate_certificate import formal_aggregate_coverage
+
+        agg = formal_aggregate_coverage(
+            history,
+            pi_target=ctx.pi_target,
+            pi_safe=ctx.pi_safe,
+            regime_certified=bool(ctx.regime_certified),
+            had_active_certified_regime=bool(ctx.had_active_certified_regime),
+            c_hat=ctx.c_hat,
+            alpha=delta_cal,
+            tau_cov=float(thresholds.tau_cov),
+        )
+        cov_info = dict(agg)
+        cov_lcb = float(agg["C_LCB"])
+        lowers = {}
+        if target_pairs and ctx.pi_safe is not None and has_counts:
+            diag_lowers = lower_pi_opp_event_count_by_pair(
+                history, target_pairs, delta=delta_cal, bonferroni=True,
+            )
+            pairwise_diag = c_cov_from_opportunity_lcb(ctx.pi_target, diag_lowers, float(ctx.pi_safe))
+            cov_info["pairwise_diagnostic_C_cov_LCB"] = pairwise_diag.get("C_cov_LCB")
+            cov_info["pairwise_formal_core"] = False
+    elif str(ctx.cov_mode) == "dynamic_max_residual" and target_pairs and ctx.pi_safe is not None:
+        from raven_mcs.sag.dynamic_cov import dynamic_lower_pi_opp
+
+        dyn = dynamic_lower_pi_opp(
+            history,
+            target_pairs,
+            lookback=int(ctx.rolling_L or thresholds.lookback_min),
+            delta=delta_cal,
+            min_calib=int(thresholds.lookback_min),
+        )
+        lowers = dyn["lowers"]
+        if dyn["cold_start"]:
+            cov_info = {
+                "C_cov_LCB": float("nan"),
+                "target_mass_certified": float("nan"),
+                "number_target_positive_pairs": len(target_pairs),
+                "pi_safe": ctx.pi_safe,
+                "top_failures": [],
+                "lower_pi_opp_method": dyn["method"],
+                "C_cov_history_policy": "rolling_plus_prior_window_max_residual",
+                "q_max_residual": dyn.get("q"),
+                "n_calib": dyn.get("n_calib"),
+            }
+            cov_lcb = float("nan")
+        else:
+            cov_info = c_cov_from_opportunity_lcb(ctx.pi_target, lowers, float(ctx.pi_safe))
+            cov_lcb = float(cov_info["C_cov_LCB"])
+            cov_info["lower_pi_opp_method"] = dyn["method"]
+            cov_info["C_cov_history_policy"] = "rolling_plus_prior_window_max_residual"
+            cov_info["q_max_residual"] = dyn.get("q")
+            cov_info["n_calib"] = dyn.get("n_calib")
+    elif target_pairs and ctx.pi_safe is not None and has_counts:
+        lowers = lower_pi_opp_event_count_by_pair(
+            history, target_pairs, delta=delta_cal, bonferroni=True,
+        )
+        cov_info = c_cov_from_opportunity_lcb(ctx.pi_target, lowers, float(ctx.pi_safe))
+        cov_lcb = float(cov_info["C_cov_LCB"])
+        old_lowers = lower_pi_opp_by_pair(recent, target_pairs)
+        old_cov = c_cov_from_opportunity_lcb(ctx.pi_target, old_lowers, float(ctx.pi_safe))
+        cov_info["C_cov_LCB_old_eb"] = old_cov["C_cov_LCB"]
+        cov_info["lower_pi_opp_method"] = "clopper_pearson_event_count_bonferroni"
+        cov_info["C_cov_history_policy"] = "all_completed_windows_t_lt_r"
+        cov_info["delta_family"] = delta_cal
+        if lowers:
+            sample = next(iter(lowers.values()))
+            cov_info["delta_pair"] = sample.get("delta_pair")
+            cov_info["completed_event_total"] = sample.get("n")
+            cov_info["n_count_windows"] = sample.get("n_windows")
+    elif target_pairs and ctx.pi_safe is not None:
+        # Fail-closed: do not use the degenerate window-mass EB as the main certifier.
+        lowers = {}
+        cov_info = {
+            "C_cov_LCB": float("nan"),
+            "target_mass_certified": float("nan"),
+            "number_target_positive_pairs": len(target_pairs),
+            "pi_safe": ctx.pi_safe,
+            "top_failures": [],
+            "lower_pi_opp_method": "missing_event_counts_fail_closed",
+        }
+        cov_lcb = float("nan")
+    else:
+        lowers = {}
+        cov_info = {
+            "C_cov_LCB": float("nan"),
+            "target_mass_certified": float("nan"),
+            "number_target_positive_pairs": 0,
+            "pi_safe": ctx.pi_safe,
+            "top_failures": [],
+        }
+        cov_lcb = float("nan")
+
     ret_lcb = mean_lcb([row.get("realized_C_ret") for row in recent])
     ess_lcb = mean_lcb([row.get("realized_C_ESS") for row in recent])
     clip_ucb = mean_ucb([row.get("realized_C_clip") for row in recent])
     delta_a_ucb = binary_ucb([row.get("active_set_mismatch") for row in recent])
-    d_beta = rolling_quantile(
+    d_beta = conformal_upper_quantile(
         [row.get("Delta_beta") for row in recent], thresholds.quantile_level,
     )
-    d_m = rolling_quantile(
+    d_m = conformal_upper_quantile(
         [row.get("Delta_M") for row in recent], thresholds.quantile_level,
     )
-    d_v = rolling_quantile(
+    d_v = conformal_upper_quantile(
         [row.get("Delta_V") for row in recent], thresholds.quantile_level,
     )
-    a_sizes = _finite_list([row.get("A_common_size") for row in recent])
-    lagged_k = float(np.mean(a_sizes)) if a_sizes else float("nan")
-    b_m = float(np.sqrt(max(lagged_k, 1.0))) if np.isfinite(lagged_k) else float("nan")
-    n_g = max(int(thresholds.n_groups), 1)
-    b_srv = (
-        float(np.sqrt(n_g)) * (float(d_m) + b_m * float(d_beta))
-        if np.isfinite(d_m) and np.isfinite(d_beta) and np.isfinite(b_m)
-        else float("nan")
-    )
-    b_tot = (
-        b_tot_from_parts(b_srv, delta_a_ucb, delta_cal)
-        if np.isfinite(b_srv) and np.isfinite(delta_a_ucb)
-        else float("nan")
+    n_clients = ctx.n_clients
+    if n_clients is None or int(n_clients) <= 0:
+        b_m = float("nan")
+        bm_note = "NO_LEGAL_TIGHTER_BM_BOUND_FOUND"
+    else:
+        b_m = float(np.sqrt(float(n_clients)))
+        bm_note = "sqrt_K_prewindow_client_roster"
+    n_g = int(ctx.n_groups or thresholds.n_groups or 1)
+    parts = (
+        b_tot_decomposition(
+            delta_beta_ucb=d_beta,
+            delta_m_ucb=d_m,
+            delta_v_ucb=d_v,
+            b_m_pre=b_m,
+            b_q=float(ctx.b_q),
+            delta_a_ucb=delta_a_ucb,
+            delta_cal=delta_cal,
+            n_groups=n_g,
+            lambda_group=float(thresholds.lambda_group),
+            lambda_beta=float(thresholds.lambda_beta),
+            lambda_variance=float(thresholds.lambda_variance),
+        )
+        if np.isfinite(d_beta) and np.isfinite(d_m) and np.isfinite(d_v)
+        and np.isfinite(b_m) and np.isfinite(delta_a_ucb)
+        else None
     )
+    b_srv = float(parts["B_srv_UCB"]) if parts else float("nan")
+    b_tot = float(parts["B_tot_UCB"]) if parts else float("nan")
     missing = cold or any(
         not np.isfinite(x)
         for x in (cov_lcb, ret_lcb, ess_lcb, clip_ucb, delta_a_ucb, b_tot)
     )
+    diagnostics = {
+        **cov_info,
+        "lower_pi_opp_method": cov_info.get(
+            "lower_pi_opp_method", "clopper_pearson_event_count_bonferroni"
+        ),
+        "B_M_bound_rule": bm_note,
+        "n_clients_prewindow": n_clients,
+        "pair_lcb_sample": {
+            encode_pair(k): v for k, v in list(lowers.items())[:6]
+        },
+    }
+    if parts:
+        diagnostics.update(parts)
     return CertificateBundle(
         C_cov_LCB=float(cov_lcb),
         C_ret_LCB=float(ret_lcb),
@@ -207,4 +675,5 @@ def compute_certificates(
         lookback=lookback,
         cold_start=cold,
         missing_certificate=bool(missing),
+        diagnostics=diagnostics,
     )
diff --git a/src/raven_mcs/sag/counterfactual_audit.py b/src/raven_mcs/sag/counterfactual_audit.py
index 43eb7d9..b5d255c 100644
--- a/src/raven_mcs/sag/counterfactual_audit.py
+++ b/src/raven_mcs/sag/counterfactual_audit.py
@@ -2,15 +2,20 @@
 
 Deltas are defined only when A^D = A^0 ≠ ∅.
 Both-empty: service_diff = 0 and Delta_beta/M/V = NA (not 0).
+
+R1-A: Δβ = ||β^D−β^0||_2, ΔM = ||M^D−M^0||_2 (operator),
+ΔV = ||V^D−V^0||_2 with v_k = S²_{r-}/max(n_eff,1)+v_floor,
+service_diff_l1 = ||M^D α^D − M^0 α^0||_1. These four are independent.
 """
 
 from __future__ import annotations
 
-from dataclasses import dataclass
+from dataclasses import dataclass, field
 from typing import Any
 
 import numpy as np
 
+from raven_mcs.aggregation.p2_cvxpy import solve_p2
 from raven_mcs.correction.effective_sample_size import effective_sample_size
 from raven_mcs.correction.hajek import (
     composition,
@@ -25,6 +30,101 @@ from raven_mcs.sag.gate import zeta_tilde
 NA = None
 
 
+def l2_vector(a: np.ndarray, b: np.ndarray) -> float:
+    x = np.asarray(a, dtype=np.float64).ravel()
+    y = np.asarray(b, dtype=np.float64).ravel()
+    if x.shape != y.shape:
+        raise ValueError(f"vector shapes differ: {x.shape} vs {y.shape}")
+    return float(np.linalg.norm(x - y, ord=2))
+
+
+def operator_2norm(a: np.ndarray, b: np.ndarray | None = None) -> float:
+    mat = np.asarray(a, dtype=np.float64)
+    if b is not None:
+        mat = mat - np.asarray(b, dtype=np.float64)
+    if mat.ndim == 1:
+        mat = np.diag(mat)
+    return float(np.linalg.norm(mat, ord=2))
+
+
+def reconstruct_variance_diag(
+    n_eff: np.ndarray,
+    lagged_s2: np.ndarray,
+    *,
+    v_floor: float,
+) -> np.ndarray:
+    n = np.asarray(n_eff, dtype=np.float64).ravel()
+    s2 = np.asarray(lagged_s2, dtype=np.float64).ravel()
+    if n.shape != s2.shape:
+        raise ValueError("n_eff and lagged_s2 must share shape")
+    v = s2 / np.maximum(n, 1.0) + float(v_floor)
+    v = np.where(np.isfinite(v), v, 1.0 + float(v_floor))
+    return np.maximum(v, float(v_floor))
+
+
+def metrics_from_raw_states(
+    *,
+    beta_d: np.ndarray,
+    beta_0: np.ndarray,
+    m_d: np.ndarray,
+    m_0: np.ndarray,
+    v_d: np.ndarray,
+    v_0: np.ndarray,
+    alpha_d: np.ndarray,
+    alpha_0: np.ndarray,
+) -> dict[str, float]:
+    """Independent Δβ / ΔM / ΔV / service from explicit states (R1-A)."""
+    s_d = np.asarray(m_d, dtype=np.float64) @ np.asarray(alpha_d, dtype=np.float64)
+    s_0 = np.asarray(m_0, dtype=np.float64) @ np.asarray(alpha_0, dtype=np.float64)
+    return {
+        "Delta_beta": l2_vector(beta_d, beta_0),
+        "Delta_M": operator_2norm(m_d, m_0),
+        "Delta_V": operator_2norm(v_d, v_0),
+        "service_diff_l1": float(np.linalg.norm(s_d - s_0, ord=1)),
+        "service_diff_l2": float(np.linalg.norm(s_d - s_0, ord=2)),
+        "B_M_cf": max(operator_2norm(m_d), operator_2norm(m_0)),
+    }
+
+
+def _solve_alpha(
+    m: np.ndarray,
+    beta: np.ndarray,
+    v_diag: np.ndarray,
+    *,
+    mu: np.ndarray,
+    debt: np.ndarray,
+    staleness: np.ndarray,
+    lambda_group: float,
+    lambda_beta: float,
+    lambda_variance: float,
+    lambda_staleness: float,
+    alpha_max: float,
+    e_min: float,
+    max_server_learning_rate: float,
+) -> np.ndarray:
+    n = int(beta.size)
+    result = solve_p2(
+        m,
+        mu,
+        beta,
+        debt,
+        v_diag,
+        staleness,
+        lambda_group=lambda_group,
+        lambda_beta=lambda_beta,
+        lambda_variance=lambda_variance,
+        lambda_staleness=lambda_staleness,
+        alpha_max=alpha_max,
+        e_min=min(float(e_min), float(n)),
+        max_server_learning_rate=max_server_learning_rate,
+    )
+    alpha = np.asarray(result.alpha, dtype=np.float64).ravel()
+    total = float(alpha.sum())
+    if total <= 0:
+        return np.ones(n, dtype=np.float64) / float(n)
+    return alpha / total
+
+
 @dataclass
 class CounterfactualAudit:
     A_D: tuple[str, ...]
@@ -36,6 +136,8 @@ class CounterfactualAudit:
     active_set_mismatch: int
     both_empty: int
     service_diff: float | None
+    service_diff_l1: float | None
+    service_diff_l2: float | None
     Delta_beta: float | None
     Delta_M: float | None
     Delta_V: float | None
@@ -43,6 +145,7 @@ class CounterfactualAudit:
     realized_C_ret: float
     realized_C_ESS: float
     realized_C_clip: float
+    raw_state: dict[str, Any] = field(default_factory=dict)
 
     def as_dict(self) -> dict[str, Any]:
         return {
@@ -51,6 +154,8 @@ class CounterfactualAudit:
             "active_set_mismatch": int(self.active_set_mismatch),
             "both_empty": int(self.both_empty),
             "service_diff": self.service_diff,
+            "service_diff_l1": self.service_diff_l1,
+            "service_diff_l2": self.service_diff_l2,
             "Delta_beta": self.Delta_beta,
             "Delta_M": self.Delta_M,
             "Delta_V": self.Delta_V,
@@ -63,19 +168,12 @@ class CounterfactualAudit:
             "realized_C_ret": self.realized_C_ret,
             "realized_C_ESS": self.realized_C_ESS,
             "realized_C_clip": self.realized_C_clip,
+            "B_M_cf": self.raw_state.get("B_M_cf"),
+            "ess_clients": list(self.raw_state.get("ess_clients") or []),
+            "raw_state": dict(self.raw_state),
         }
 
 
-def _l1_half(a: np.ndarray, b: np.ndarray) -> float:
-    x = np.asarray(a, dtype=np.float64).ravel()
-    y = np.asarray(b, dtype=np.float64).ravel()
-    if x.shape != y.shape:
-        n = max(x.size, y.size)
-        x = np.pad(x, (0, n - x.size))
-        y = np.pad(y, (0, n - y.size))
-    return float(0.5 * np.abs(x - y).sum())
-
-
 def _masses(
     *,
     O: np.ndarray,
@@ -95,31 +193,28 @@ def _masses(
     return m_total, c_g, n_eff, clip
 
 
-def _stage2(
+def _stage2_matrix(
     clients: list[str],
     masses: dict[str, float],
     compositions: dict[str, np.ndarray],
     q_hat: dict[str, float],
-    variance: dict[str, float],
     *,
     d_max: float,
     q_min: float,
     num_groups: int,
-) -> tuple[np.ndarray, np.ndarray, np.ndarray]:
+) -> tuple[np.ndarray, np.ndarray]:
     n = len(clients)
+    m_mat = np.zeros((num_groups, n), dtype=np.float64)
     if n == 0:
-        empty_m = np.zeros(num_groups, dtype=np.float64)
-        return np.zeros(0), empty_m, np.zeros(0)
-    m = np.array([masses[c] for c in clients], dtype=np.float64)
+        return np.zeros(0, dtype=np.float64), m_mat
+    mass = np.array([masses[c] for c in clients], dtype=np.float64)
     q = np.array([q_hat.get(c, 0.5) for c in clients], dtype=np.float64)
     d = d_weight(q, d_max=d_max, q_min=q_min)
-    b = two_stage_mass(m, d)
+    b = two_stage_mass(mass, d)
     beta = beta_hat(b)
-    mix = np.zeros(num_groups, dtype=np.float64)
     for i, cid in enumerate(clients):
-        mix = mix + float(beta[i]) * np.asarray(compositions[cid], dtype=np.float64)
-    v = np.array([variance.get(c, 1.0) for c in clients], dtype=np.float64)
-    return beta, mix, v
+        m_mat[:, i] = np.asarray(compositions[cid], dtype=np.float64)
+    return beta, m_mat
 
 
 def audit_design_vs_nodesign(
@@ -140,16 +235,31 @@ def audit_design_vs_nodesign(
     d_max: float,
     q_min: float,
     num_groups: int,
+    v_floor: float = 1e-4,
+    mu: np.ndarray | None = None,
+    debt: np.ndarray | None = None,
+    staleness: dict[str, float] | None = None,
+    lambda_group: float = 1.0,
+    lambda_beta: float = 1.0,
+    lambda_variance: float = 0.1,
+    lambda_staleness: float = 0.1,
+    alpha_max: float = 0.5,
+    e_min: float = 3.0,
+    max_server_learning_rate: float = 1.0,
+    n_eff_override: dict[str, tuple[float, float]] | None = None,
 ) -> CounterfactualAudit:
-    """Reconstruct B/A and (when defined) Δβ/M/V on frozen p̂, q̂, O, U."""
+    """Reconstruct B/A and (when defined) independent Δβ/M/V and service."""
     b_d: list[str] = []
     b_0: list[str] = []
     masses_d: dict[str, float] = {}
     masses_0: dict[str, float] = {}
     comp_d: dict[str, np.ndarray] = {}
     comp_0: dict[str, np.ndarray] = {}
+    n_eff_d: dict[str, float] = {}
+    n_eff_0: dict[str, float] = {}
     n_effs: list[float] = []
     clips: list[float] = []
+    ess_rows: list[dict[str, Any]] = []
 
     for cid in registered:
         if cid not in attempted:
@@ -167,11 +277,55 @@ def audit_design_vs_nodesign(
             O=rec_o, groups=rec_g, zeta=z0, p_hat=ph,
             a_max=a_max, p_min=p_min, num_groups=num_groups,
         )
+        if n_eff_override and cid in n_eff_override:
+            n_d, n_0 = n_eff_override[cid]
         masses_d[cid] = m_d
         masses_0[cid] = m_0
         comp_d[cid] = c_d
         comp_0[cid] = c_0
-        n_effs.extend([n_d, n_0])
+        n_eff_d[cid] = float(n_d)
+        n_eff_0[cid] = float(n_0)
+        obs = rec_o > 0
+        if int(obs.sum()) > 0:
+            z_obs = zd[obs]
+            z_std = float(np.std(z_obs)) if z_obs.size > 1 else 0.0
+            z_min = float(np.min(z_obs))
+            z_max = float(np.max(z_obs))
+        else:
+            z_std = float("nan")
+            z_min = float("nan")
+            z_max = float("nan")
+        ess_rows.append({
+            "client": str(cid),
+            "n_obs": int(obs.sum()),
+            "zeta_std": z_std,
+            "zeta_min": z_min,
+            "zeta_max": z_max,
+            "n_eff_D": float(n_d),
+            "n_eff_0": float(n_0),
+            "abs_neff_diff": abs(float(n_d) - float(n_0)),
+        })
+        obs = rec_o > 0
+        if int(obs.sum()) > 0:
+            z_obs = zd[obs]
+            z_std = float(np.std(z_obs)) if z_obs.size > 1 else 0.0
+            z_min = float(np.min(z_obs))
+            z_max = float(np.max(z_obs))
+        else:
+            z_std = float("nan")
+            z_min = float("nan")
+            z_max = float("nan")
+        ess_rows.append({
+            "client": str(cid),
+            "n_obs": int(obs.sum()),
+            "zeta_std": z_std,
+            "zeta_min": z_min,
+            "zeta_max": z_max,
+            "n_eff_D": float(n_d),
+            "n_eff_0": float(n_0),
+            "abs_neff_diff": abs(float(n_d) - float(n_0)),
+        })
+        n_effs.extend([float(n_d), float(n_0)])
         clips.extend([clip_d, clip_0])
         if m_d > 0:
             b_d.append(cid)
@@ -188,23 +342,107 @@ def audit_design_vs_nodesign(
     delta_m: float | None = NA
     delta_v: float | None = NA
     service_diff: float | None
+    service_l1: float | None = NA
+    service_l2: float | None = NA
+    raw_state: dict[str, Any] = {}
     if both_empty:
         service_diff = 0.0
+        service_l1 = 0.0
+        service_l2 = 0.0
     elif mismatch:
         service_diff = NA
     else:
-        beta_d, mix_d, v_d = _stage2(
-            list(a_d), masses_d, comp_d, q_hat, variance,
+        clients = list(a_d)
+        beta_d, mat_d = _stage2_matrix(
+            clients, masses_d, comp_d, q_hat,
             d_max=d_max, q_min=q_min, num_groups=num_groups,
         )
-        beta_0, mix_0, v_0 = _stage2(
-            list(a_0), masses_0, comp_0, q_hat, variance,
+        beta_0, mat_0 = _stage2_matrix(
+            clients, masses_0, comp_0, q_hat,
             d_max=d_max, q_min=q_min, num_groups=num_groups,
         )
-        delta_beta = _l1_half(beta_d, beta_0)
-        delta_m = _l1_half(mix_d, mix_0)
-        delta_v = _l1_half(v_d, v_0)
-        service_diff = float(delta_m)
+        s2 = np.array([float(variance.get(c, 1.0)) for c in clients], dtype=np.float64)
+        v_d = reconstruct_variance_diag(
+            np.array([n_eff_d[c] for c in clients], dtype=np.float64),
+            s2,
+            v_floor=v_floor,
+        )
+        v_0 = reconstruct_variance_diag(
+            np.array([n_eff_0[c] for c in clients], dtype=np.float64),
+            s2,
+            v_floor=v_floor,
+        )
+        tau = np.array(
+            [(staleness or {}).get(c, 0.0) for c in clients],
+            dtype=np.float64,
+        )
+        if mu is None:
+            mu_vec = np.full(num_groups, 1.0 / float(num_groups), dtype=np.float64)
+        else:
+            mu_vec = np.asarray(mu, dtype=np.float64).ravel()
+        if debt is None:
+            q_vec = np.zeros(num_groups, dtype=np.float64)
+        else:
+            q_vec = np.asarray(debt, dtype=np.float64).ravel()
+        alpha_d = _solve_alpha(
+            mat_d, beta_d, v_d,
+            mu=mu_vec, debt=q_vec, staleness=tau,
+            lambda_group=lambda_group, lambda_beta=lambda_beta,
+            lambda_variance=lambda_variance, lambda_staleness=lambda_staleness,
+            alpha_max=alpha_max, e_min=e_min,
+            max_server_learning_rate=max_server_learning_rate,
+        )
+        alpha_0 = _solve_alpha(
+            mat_0, beta_0, v_0,
+            mu=mu_vec, debt=q_vec, staleness=tau,
+            lambda_group=lambda_group, lambda_beta=lambda_beta,
+            lambda_variance=lambda_variance, lambda_staleness=lambda_staleness,
+            alpha_max=alpha_max, e_min=e_min,
+            max_server_learning_rate=max_server_learning_rate,
+        )
+        mets = metrics_from_raw_states(
+            beta_d=beta_d, beta_0=beta_0,
+            m_d=mat_d, m_0=mat_0,
+            v_d=np.diag(v_d), v_0=np.diag(v_0),
+            alpha_d=alpha_d, alpha_0=alpha_0,
+        )
+        delta_beta = mets["Delta_beta"]
+        delta_m = mets["Delta_M"]
+        delta_v = mets["Delta_V"]
+        service_l1 = mets["service_diff_l1"]
+        service_l2 = mets["service_diff_l2"]
+        service_diff = service_l1
+        raw_state = {
+            "clients": list(clients),
+            "beta_D": beta_d.tolist(),
+            "beta_0": beta_0.tolist(),
+            "M_D": mat_d.tolist(),
+            "M_0": mat_0.tolist(),
+            "V_D_diag": v_d.tolist(),
+            "V_0_diag": v_0.tolist(),
+            "n_eff_D": [n_eff_d[c] for c in clients],
+            "n_eff_0": [n_eff_0[c] for c in clients],
+            "alpha_D": alpha_d.tolist(),
+            "alpha_0": alpha_0.tolist(),
+            "s_D": (mat_d @ alpha_d).tolist(),
+            "s_0": (mat_0 @ alpha_0).tolist(),
+            "B_M_cf": mets["B_M_cf"],
+            "Delta_beta": delta_beta,
+            "Delta_M": delta_m,
+            "Delta_V": delta_v,
+            "service_diff_l1": service_l1,
+            "service_diff_l2": service_l2,
+            "ess_clients": ess_rows,
+        }
+        vmap_d = {c: float(v_d[i]) for i, c in enumerate(clients)}
+        vmap_0 = {c: float(v_0[i]) for i, c in enumerate(clients)}
+        for row in ess_rows:
+            cid = str(row["client"])
+            row["v_D"] = vmap_d.get(cid, float("nan"))
+            row["v_0"] = vmap_0.get(cid, float("nan"))
+            row["abs_v_diff"] = abs(float(row["v_D"]) - float(row["v_0"])) if cid in vmap_d else float("nan")
+    if "ess_clients" not in raw_state:
+        raw_state["ess_clients"] = ess_rows
 
     denom = max(int(target_positive_count), 1)
     realized_cov = float(target_covered_count) / float(denom)
@@ -226,6 +464,8 @@ def audit_design_vs_nodesign(
         active_set_mismatch=mismatch,
         both_empty=both_empty,
         service_diff=service_diff,
+        service_diff_l1=service_l1,
+        service_diff_l2=service_l2,
         Delta_beta=delta_beta,
         Delta_M=delta_m,
         Delta_V=delta_v,
@@ -233,4 +473,5 @@ def audit_design_vs_nodesign(
         realized_C_ret=realized_ret,
         realized_C_ESS=realized_ess,
         realized_C_clip=realized_clip,
+        raw_state=raw_state,
     )
diff --git a/src/raven_mcs/training/window_runner.py b/src/raven_mcs/training/window_runner.py
index 58789bf..038fc07 100644
--- a/src/raven_mcs/training/window_runner.py
+++ b/src/raven_mcs/training/window_runner.py
@@ -1,7 +1,7 @@
 """Full training pipeline WindowRunner — real Common-NDMF training (P10).
 
 Each window (SAG v1.2 / PostAudit III–VI):
- 1. Read theta_r; compute F_{r-} certificates; freeze G_r
+ 1. Freeze configured Design; read theta_r; compute independent F_{r-} coverage diagnostic
  2. Realize R (risk sets) from EventTrace
  3. Freeze p_hat_obs from pre-O features
  4. Realize O; E_r = registered/attempted; B_r = {k in E_r : m>0}
@@ -9,13 +9,16 @@ Each window (SAG v1.2 / PostAudit III–VI):
  6. Freeze q_hat_use from pre-U features
  7. Realize U → A_r = B_r ∩ U_r
  8. P2 / global update / optional debt
- 9. Post-window D vs 0 audit (future Gate only)
+ 9. Post-window D vs 0 audit updates future coverage diagnostics only for configured Design
 10. After window close: update opportunity/p/q/variance state
 """
 
 from __future__ import annotations
 
 import copy
+import gc
+import os
+import tempfile
 from collections import Counter
 import hashlib
 from dataclasses import dataclass, field
@@ -44,6 +47,7 @@ from raven_mcs.correction.hajek import (
 )
 from raven_mcs.correction.pi_target import build_pi_target
 from raven_mcs.correction.second_stage import beta_hat, d_weight, two_stage_mass
+from raven_mcs.correction.stage1 import reconstruct_stage1
 from raven_mcs.data.processed_dataset import ProcessedDataset
 from raven_mcs.data.target import GroupMapper, RepeatableTimeOfDayMapper, TargetBuilder
 from raven_mcs.data.window_dataset import WindowDataSlice, extract_window_slice
@@ -52,9 +56,24 @@ from raven_mcs.models.features import extract_features
 from raven_mcs.opportunities.estimator import OpportunityEstimator
 from raven_mcs.propensity.observation import ObservationPropensity
 from raven_mcs.propensity.usable import UsablePropensity, deadline_slack_pre
-from raven_mcs.sag.certificates import FrozenSagThresholds, compute_certificates
+from raven_mcs.sag.certificates import (
+    CertificateContext,
+    FrozenSagThresholds,
+    compute_certificates,
+    encode_pair,
+    window_opportunity_event_counts,
+    window_opportunity_masses,
+)
 from raven_mcs.sag.counterfactual_audit import audit_design_vs_nodesign
 from raven_mcs.sag.gate import decide_gate, zeta_tilde
+from raven_mcs.sag.r1l_design import (
+    FORMAL_GATE_MODE,
+    apply_formal_design_zeta,
+    legacy_decide_gate_and_design,
+    DesignConfiguration,
+    configured_decide_gate_and_design,
+    apply_configured_design_zeta,
+)
 from raven_mcs.sag.sag_state import SagState
 from raven_mcs.sag.timing import (
     STAGE_GATE,
@@ -94,6 +113,11 @@ class WindowMetrics:
     a_r_size: int
     b_r_size: int = 0
     g_r: int = 0
+    configured_design: int | None = None
+    actual_design: int | None = None
+    coverage_gate: int | None = None
+    configuration_source: str = ""
+    method_version: str = "legacy-v1"
 
 
 @dataclass
@@ -129,8 +153,11 @@ class FullWindowRunner:
     device: str = "cpu"
     # E3 spatial×time: never remap via coarse time blocks unless explicitly requested.
     use_coarse_time_groups: bool = False
+    # Paper h(i): frozen unit → UTC TOD block. When set, M/μ/|G| use this map.
+    paper_h_by_unit: dict[str, int] | None = None
     # Frozen joint opportunity mass on client×stratum (same scale as pi_target).
     pi_opp_joint: dict[tuple[str, str], float] = field(default_factory=dict)
+    design_configuration: DesignConfiguration | None = None
 
     # State
     theta: dict[str, torch.Tensor] = field(default_factory=dict)
@@ -152,11 +179,26 @@ class FullWindowRunner:
     q_attempt_diagnostics: list[dict[str, Any]] = field(default_factory=list)
     q_model_version: int = 0
     sag_thresholds: FrozenSagThresholds | None = None
+    sag_pi_safe: float | None = None
     sag_state: SagState = field(default_factory=SagState)
     sag_window_logs: list[dict[str, Any]] = field(default_factory=list)
+    sag_raw_states: list[dict[str, Any]] = field(default_factory=list)
+    design_window_logs: list[dict[str, Any]] = field(default_factory=list)
 
     def __post_init__(self) -> None:
+        if self.policy.design_control == "configured":
+            if not isinstance(self.design_configuration, DesignConfiguration):
+                raise ValueError("CONFIGURATION_REQUIRED: raven_mcs requires explicit Design on/off")
+            if self.policy.coverage_diagnostic != "aggregate_coverage":
+                raise ValueError("Unsupported coverage diagnostic")
         self.mu = np.asarray(self.mu, dtype=np.float64)
+        if self.paper_h_by_unit:
+            if int(self.num_groups) != 4:
+                raise ValueError("paper h(i) requires num_groups=4")
+            if int(self.mu.size) != 4:
+                raise ValueError("paper μ must have length 4")
+        if int(self.mu.size) != int(self.num_groups):
+            raise ValueError("μ length must equal num_groups")
         if len(self.debt) != self.num_groups:
             self.debt = np.zeros(self.num_groups, dtype=np.float64)
         if len(self.omega_sum) != self.num_groups:
@@ -169,7 +211,8 @@ class FullWindowRunner:
             self.opportunity_estimator = OpportunityEstimator()
         if self.pi_target:
             self.opportunity_estimator.initialize_support(
-                key for key, mass in self.pi_target.items() if mass > 0.0
+                key for key, mass in self.pi_target.items()
+                if self._formal_raven_mcs() or mass > 0.0
             )
         if self.obs_propensity is None:
             self.obs_propensity = ObservationPropensity()
@@ -179,6 +222,17 @@ class FullWindowRunner:
         self._trainer = ClientTrainer(self.model, learning_rate=self.learning_rate)
         if self.sag_thresholds is None:
             self.sag_thresholds = FrozenSagThresholds(n_groups=int(self.num_groups))
+        if len(self.trace.events):
+            self._n_clients_pre = int(
+                pd.Series(self.trace.events["client_id"].astype(str)).nunique()
+            )
+        else:
+            self._n_clients_pre = max(
+                len({k for k, _ in self.pi_target}),
+                1,
+            )
+        self._last_cert_diagnostics: dict[str, Any] = {}
+        self._last_gate_to_design: dict[str, Any] = {}
         # Lagged FedAU participation counters. Updated only after window close.
         self._fedau_usable_count: dict[str, float] = {}
         self._fedau_attempt_count: dict[str, float] = {}
@@ -268,7 +322,12 @@ class FullWindowRunner:
             )
         else:
             if self.opportunity_estimator is None:
+                if self._formal_raven_mcs():
+                    raise ValueError("DESIGN_INPUT_ERROR: missing lagged opportunity estimator")
                 return np.ones(len(stratum_ids), dtype=np.float64)
+            lagged = self.opportunity_estimator.pi_hat()
+            if self._formal_raven_mcs() and any((client_id, s) not in lagged for s in stratum_ids):
+                raise ValueError("DESIGN_INPUT_ERROR: missing lagged opportunity support")
             pi_hat_opp = np.array(
                 [
                     self.opportunity_estimator.pi_hat().get((client_id, s), self.p_min)
@@ -279,6 +338,16 @@ class FullWindowRunner:
 
         return zeta_hat_stratum(pi_tar, pi_hat_opp, pi_min=self.pi_min)
 
+    def _design_metric_fields(self) -> dict[str, Any]:
+        rec = self._last_gate_to_design
+        return {
+            "configured_design": rec.get("configured_design"),
+            "actual_design": rec.get("Design_t"),
+            "coverage_gate": rec.get("Gate_t"),
+            "configuration_source": rec.get("configuration_source", "legacy_policy"),
+            "method_version": self.policy.method_version,
+        }
+
     def _compute_p_hat(self, features_list: list[dict[str, float]]) -> np.ndarray:
         """Compute observation propensity estimates."""
         if self.obs_propensity is None:
@@ -304,13 +373,72 @@ class FullWindowRunner:
     def _gate_mode(self) -> str:
         return str(getattr(self.policy, "gate_mode", "policy") or "policy")
 
-    def _decide_g_r(self) -> tuple[int, dict[str, Any], str | None, dict[str, bool]]:
-        """Freeze G_r from F_{r-} only. Dataset identity is not an argument."""
+    def _formal_raven_mcs(self) -> bool:
+        return self.policy.design_control == "configured"
+
+    def _certificate_context(self) -> CertificateContext:
+        return CertificateContext(
+            pi_target=dict(self.pi_target),
+            pi_safe=self.sag_pi_safe,
+            b_q=float(np.linalg.norm(np.asarray(self.debt, dtype=np.float64), ord=2)),
+            n_clients=int(self._n_clients_pre),
+            n_groups=int(self.num_groups),
+            source="prewindow_debt_and_public_target",
+            cov_mode=("aggregate_stable_regime" if self._formal_raven_mcs()
+                      else str(getattr(self, "sag_cov_mode", "aggregate_stable_regime") or "aggregate_stable_regime")),
+            rolling_L=getattr(self, "sag_rolling_L", None),
+            regime_certified=bool(getattr(self, "sag_regime_certified", True)),
+            had_active_certified_regime=bool(getattr(self, "sag_had_active_certified_regime", True)),
+            c_hat=getattr(self, "sag_c_hat", None),
+        )
+
+    def _decide_g_r(
+        self, window_id: int = -1,
+    ) -> tuple[int, dict[str, Any], str | None, dict[str, bool]]:
+        """Freeze G_r from F_{r-} only.
+
+        Configured RAVEN-MCS consumes the pre-window setting independently of
+        the aggregate coverage certificate. Only the explicit legacy coverage
+        branch below imposes Design_t := Gate_t.
+
+        always_on / always_off / policy / sag are LEGACY experiment modes.
+        """
         assert self.sag_thresholds is not None
-        bundle = compute_certificates(self.sag_state.completed(), self.sag_thresholds)
+        bundle = compute_certificates(
+            self.sag_state.completed(),
+            self.sag_thresholds,
+            self._certificate_context(),
+        )
         certs = bundle.as_gate_inputs()
-        decision = decide_gate(certs, self.sag_thresholds.gate_thresholds())
+        self._last_cert_diagnostics = dict(bundle.diagnostics)
+        if self._formal_raven_mcs():
+            rec = configured_decide_gate_and_design(
+                self._last_cert_diagnostics,
+                configuration=self._window_design_configuration,
+                window_id=window_id,
+                tau_cov=float(self.sag_thresholds.tau_cov),
+                c_cov_lcb=float(bundle.C_cov_LCB),
+            )
+            self._last_gate_to_design = rec
+            self.design_window_logs.append(dict(rec, actual_design=rec["Design_t"]))
+            return int(rec["Design_t"]), certs, None, {"aggregate_coverage": bool(rec["Gate_t"])}
         mode = self._gate_mode()
+        if mode == FORMAL_GATE_MODE:
+            rec = legacy_decide_gate_and_design(
+                self._last_cert_diagnostics,
+                tau_cov=float(self.sag_thresholds.tau_cov),
+                window_id=int(window_id),
+                c_cov_lcb=float(bundle.C_cov_LCB)
+                if np.isfinite(float(bundle.C_cov_LCB))
+                else None,
+            )
+            self._last_gate_to_design = rec
+            self.design_window_logs.append(dict(rec, actual_design=rec["Design_t"], method_version=self.policy.method_version, coverage_role="legacy_control"))
+            passed = {"aggregate_coverage": bool(rec["Gate_t"])}
+            return int(rec["Gate_t"]), certs, rec.get("fallback_reason"), passed
+        # --- LEGACY experiment / ablation path (not formal RAVEN-MCS) ---
+        decision = decide_gate(certs, self.sag_thresholds.gate_thresholds())
+        self._last_gate_to_design = {}
         if mode == "always_on":
             return 1, certs, None, decision.passed
         if mode == "always_off":
@@ -322,7 +450,11 @@ class FullWindowRunner:
         return 0, certs, "OFF_MODE_NO_DESIGN", decision.passed
 
     def _apply_zeta(self, zeta_d: np.ndarray, g_r: int) -> np.ndarray:
+        if self._formal_raven_mcs():
+            return apply_configured_design_zeta(zeta_d, g_r)
         mode = self._gate_mode()
+        if mode == FORMAL_GATE_MODE:
+            return apply_formal_design_zeta(zeta_d, g_r)
         if mode == "sag":
             return zeta_tilde(zeta_d, g_r)
         if self.policy.uses_design_ratio:
@@ -364,6 +496,25 @@ class FullWindowRunner:
                 out[cid] = 0.5
         return out
 
+    def _window_opp_events(
+        self, window_slice: WindowDataSlice,
+    ) -> tuple[dict[str, float], dict[str, float]]:
+        pairs = [
+            (str(rec.client_id), str(stratum))
+            for rec in window_slice.records
+            for stratum in rec.opportunity_strata
+        ]
+        counts = window_opportunity_event_counts(pairs)
+        masses = window_opportunity_masses(pairs)
+        return (
+            {encode_pair(key): float(val) for key, val in masses.items()},
+            {encode_pair(key): float(val) for key, val in counts.items()},
+        )
+
+    def _window_opp_mass_map(self, window_slice: WindowDataSlice) -> dict[str, float]:
+        masses, _counts = self._window_opp_events(window_slice)
+        return masses
+
     def _target_coverage(self, window_slice: WindowDataSlice) -> tuple[int, int]:
         present = {
             (str(rec.client_id), str(stratum))
@@ -397,6 +548,9 @@ class FullWindowRunner:
     ) -> None:
         log = {
             "window_id": int(window_id),
+            "method_version": self.policy.method_version,
+            "design_control": self.policy.design_control,
+            "coverage_role": "diagnostic_only" if self._formal_raven_mcs() else "legacy_control",
             "method_gate_mode": self._gate_mode(),
             "G_r": int(g_r),
             "fallback_reason": fallback_reason,
@@ -419,7 +573,28 @@ class FullWindowRunner:
         }
         if extras:
             log.update(extras)
+        log["certificate_diagnostics"] = dict(self._last_cert_diagnostics)
+        if self._last_gate_to_design:
+            log["gate_to_design"] = dict(self._last_gate_to_design)
+        if self._formal_raven_mcs():
+            log.update(self._last_gate_to_design)
+            log["actual_design"] = int(g_r)
+            log["design_configuration"] = self._window_design_configuration.to_dict()
         self.sag_window_logs.append(log)
+        raw = audit.get("raw_state") or {}
+        if (
+            int(audit.get("both_empty") or 0) == 0
+            and int(audit.get("active_set_mismatch") or 0) == 0
+            and raw
+            and len(self.sag_raw_states) < 10
+        ):
+            self.sag_raw_states.append(
+                {
+                    "window_id": int(window_id),
+                    "gate_mode": self._gate_mode(),
+                    **raw,
+                }
+            )
         history_row = {
             "window_id": int(window_id),
             "G_r": int(g_r),
@@ -436,6 +611,10 @@ class FullWindowRunner:
             "A_common_size": audit.get("A_common_size"),
             "A_D_size": audit.get("A_D_size"),
             "A_0_size": audit.get("A_0_size"),
+            "opp_mass_by_pair": dict(audit.get("opp_mass_by_pair") or {}),
+            "opp_count_by_pair": dict(audit.get("opp_count_by_pair") or {}),
+            "opp_event_total": audit.get("opp_event_total"),
+            "n_groups": int(self.num_groups),
         }
         self.sag_state.append_completed(history_row)
 
@@ -460,6 +639,8 @@ class FullWindowRunner:
         }
 
     def run(self) -> list[WindowMetrics]:
+        if getattr(self, "_dynamic_control_owner", False):
+            raise RuntimeError("Dynamic control owns this model; do not run the fixed EventTrace path")
         events = self.trace.events
 
         for window_id in range(int(self.trace.metadata.num_windows)):
@@ -468,23 +649,46 @@ class FullWindowRunner:
 
         return self.metrics
 
+    def build_dynamic_control(self, **kwargs):
+        """Explicit conditional-bundle ownership; never consumes trace final U.
+
+        Local work is prepared at registration and needs separate training
+        authorization. B0 may initialize this interface without running SGD.
+        """
+        from raven_mcs.training.dynamic_control import connect_full_runner
+        return connect_full_runner(self, **kwargs)
+
     def _process_window(
         self, window_id: int, events: "pd.DataFrame",
     ) -> WindowMetrics:
+        # Immutable snapshot before any certificate, event, or local computation.
+        # Replacing external configuration during this call affects only later windows.
+        if self._formal_raven_mcs():
+            if not isinstance(self.design_configuration, DesignConfiguration):
+                raise ValueError("CONFIGURATION_REQUIRED: invalid pre-window Design")
+            self._window_design_configuration = self.design_configuration
         before_hash = self._theta_hash()
         version = self.clock.model_version
         stages = SagStages()
-        g_r, cert_inputs, fallback_reason, gate_passed = self._decide_g_r()
+        g_r, cert_inputs, fallback_reason, gate_passed = self._decide_g_r(window_id)
         stages.mark("gate", STAGE_GATE)
 
         # Step 2: Realize R (risk sets). Do not use O/U for G_r.
         coarse_groups = (
             self.num_groups
-            if self.use_coarse_time_groups and self.num_groups in {4, 8}
+            if (
+                self.paper_h_by_unit is None
+                and self.use_coarse_time_groups
+                and self.num_groups in {4, 8}
+            )
             else None
         )
         window_slice = extract_window_slice(
-            window_id, events, self.dataset, coarse_time_groups=coarse_groups,
+            window_id,
+            events,
+            self.dataset,
+            coarse_time_groups=coarse_groups,
+            h_by_unit=self.paper_h_by_unit,
         )
         stages.mark("R", STAGE_R)
 
@@ -501,6 +705,8 @@ class FullWindowRunner:
                 "active_set_mismatch": 0,
                 "both_empty": 1,
                 "service_diff": 0.0,
+                "service_diff_l1": 0.0,
+                "service_diff_l2": 0.0,
                 "Delta_beta": None,
                 "Delta_M": None,
                 "Delta_V": None,
@@ -509,6 +715,12 @@ class FullWindowRunner:
                 "realized_C_ret": 0.0,
                 "realized_C_ESS": 0.0,
                 "realized_C_clip": 0.0,
+                "opp_mass_by_pair": {},
+                "opp_count_by_pair": {},
+                "opp_event_total": 0.0,
+                "opp_count_by_pair": {},
+                "opp_event_total": 0.0,
+                "raw_state": {},
             }
             self._record_sag_window(
                 window_id=window_id,
@@ -546,12 +758,15 @@ class FullWindowRunner:
                 a_r_size=0,
                 b_r_size=0,
                 g_r=int(g_r),
+                **self._design_metric_fields(),
             )
 
         # Freeze p̂_obs from pre-O features (planned_workload_pre / hour_block).
         client_data: dict[str, dict] = {}
         for rec in window_slice.records:
             cid = rec.client_id
+            # Keep the lagged ratio for the independent D-vs-0 diagnostic;
+            # only the frozen setting decides which factor enters computation.
             zeta_d = self._compute_zeta(cid, rec.opportunity_strata)
             features_list = [
                 {
@@ -564,8 +779,12 @@ class FullWindowRunner:
                 for stratum in rec.opportunity_strata
             ]
             # SimOracle: consume atomic p_obs_true(k,r,i) — never risk-set mean alone.
+            # F-1 also reaches this path through uses_oracle_p alone, leaving q estimated.
             if (
-                self.policy.uses_oracle_propensity
+                (
+                    self.policy.uses_oracle_propensity
+                    or getattr(self.policy, "uses_oracle_p", False)
+                )
                 and getattr(rec, "p_obs_true_by_unit", None)
             ):
                 p_map = rec.p_obs_true_by_unit or {}
@@ -599,12 +818,11 @@ class FullWindowRunner:
         for cid, data in client_data.items():
             rec = data["record"]
             zeta = self._apply_zeta(data["zeta_d"], g_r)
-            a_raw = raw_weights(zeta, data["p_hat"], a_max=self.a_max, p_min=self.p_min)
-            m_g = group_mass(rec.O, a_raw, np.array(rec.target_groups), n_groups=self.num_groups)
-            m_total = total_mass(m_g)
-            a_bar = normalized_weights(rec.O, a_raw, m_total)
-            c_g = composition(m_g, m_total)
-            n_eff = effective_sample_size(rec.O, a_raw, total_mass=m_total)
+            stage1 = reconstruct_stage1(zeta, data["p_hat"], rec.O,
+                np.array(rec.target_groups), num_groups=self.num_groups,
+                a_max=self.a_max, p_min=self.p_min)
+            a_raw, m_g, m_total = stage1.raw, stage1.groups, stage1.total
+            a_bar, c_g, n_eff = stage1.weights, stage1.composition, stage1.effective_n
             data.update({
                 "zeta": zeta,
                 "a_raw": a_raw,
@@ -635,12 +853,41 @@ class FullWindowRunner:
         # Step 6: Execute local SGD for each client
         local_updates: dict[str, np.ndarray] = {}
         train_losses: dict[str, float] = {}
+        lowmem = bool(getattr(self, "_tdrive_lowmem", False))
+        mm = None
+        mm_path: str | None = None
+        mm_index: dict[str, int] = {}
+        update_norms: dict[str, float] = {}
+        n_mm = 0
+        stream_fedavg = lowmem and getattr(self.aggregator, "name", "") == "fedavg_window"
+        fedavg_acc = None
+        fedavg_weight: dict[str, float] = {}
+        if stream_fedavg:
+            ar_ids = [
+                cid for cid in e_r_clients if int(client_data[cid]["record"].U) == 1
+            ]
+            raw_pre = np.asarray(
+                [
+                    float(np.sum(client_data[cid]["record"].O))
+                    for cid in ar_ids
+                ],
+                dtype=np.float64,
+            )
+            tot_pre = float(raw_pre.sum()) if raw_pre.size else 0.0
+            if tot_pre <= 0.0:
+                tot_pre = 1.0
+            for cid, w in zip(ar_ids, raw_pre):
+                fedavg_weight[cid] = float(w / tot_pre)
 
         for cid in e_r_clients:
             data = client_data[cid]
             rec = data["record"]
             downloaded_version = rec.downloaded_version
             self.clock.register_local_work(downloaded_version)
+            if lowmem and int(rec.U) != 1:
+                # Global apply uses A_r = B_r ∩ U only; skip discarded B_r\U
+                # updates so a 16GB host can finish T-Drive windows.
+                continue
             checkpoint = self._get_model_checkpoint(downloaded_version)
 
             observed_records = []
@@ -692,27 +939,75 @@ class FullWindowRunner:
                     f"NONFINITE_NUMERICAL_STATE: local update/loss nonfinite "
                     f"client={cid} window={window_id}"
                 )
-            local_updates[cid] = update
             train_losses[cid] = loss
-            raw_local = np.ones(len(observed_records), dtype=np.float64)
-            raw_local /= max(len(observed_records), 1)
-            self.diagnostics.append({
-                "window_id": window_id,
-                "client_id": cid,
-                "observed_unit_ids": list(rec.observed_unit_ids),
-                "risk_set_unit_ids": list(rec.risk_set_unit_ids),
-                "raw_local_weights": raw_local.tolist(),
-                "hajek_local_weights": data["a_bar"][obs_mask].tolist(),
-                "applied_local_weights": a_bar_observed.tolist(),
-                "a_bar": a_bar_observed.tolist(),
-                "w_units": a_bar_observed.tolist(),
-                "zeta_hat": data["zeta"].tolist(),
-                "p_hat": data["p_hat"].tolist(),
-                "m": float(data["m_total"]),
-                "n_eff": float(data["n_eff"]),
-                "local_loss": float(loss),
-                "update_vector_hash": sha256_json(update.tolist()),
-            })
+            if stream_fedavg:
+                if int(update.size) > 0:
+                    vec = np.asarray(update, dtype=np.float64)
+                    w = float(fedavg_weight.get(cid, 0.0))
+                    if fedavg_acc is None:
+                        fedavg_acc = w * vec
+                    else:
+                        fedavg_acc += w * vec
+                    update_norms[cid] = float(np.linalg.norm(vec))
+                self.diagnostics.append({
+                    "window_id": window_id,
+                    "client_id": cid,
+                    "observed_unit_ids": rec.observed_unit_ids,
+                })
+            elif lowmem:
+                if int(update.size) > 0:
+                    upd_f32 = np.asarray(update, dtype=np.float32)
+                    if mm is None:
+                        n_ar = sum(
+                            1
+                            for c in e_r_clients
+                            if int(client_data[c]["record"].U) == 1
+                        )
+                        tmp = tempfile.NamedTemporaryFile(
+                            prefix=f"tdrive_upd_w{window_id}_",
+                            suffix=".dat",
+                            delete=False,
+                        )
+                        tmp.close()
+                        mm_path = tmp.name
+                        mm = np.memmap(
+                            mm_path,
+                            dtype=np.float32,
+                            mode="w+",
+                            shape=(max(int(n_ar), 1), int(upd_f32.size)),
+                        )
+                    mm[n_mm] = upd_f32
+                    mm_index[cid] = n_mm
+                    update_norms[cid] = float(np.linalg.norm(upd_f32))
+                    n_mm += 1
+                self.diagnostics.append({
+                    "window_id": window_id,
+                    "client_id": cid,
+                    "observed_unit_ids": list(rec.observed_unit_ids),
+                    "a_bar": a_bar_observed.tolist(),
+                    "w_units": a_bar_observed.tolist(),
+                })
+            else:
+                local_updates[cid] = update
+                raw_local = np.ones(len(observed_records), dtype=np.float64)
+                raw_local /= max(len(observed_records), 1)
+                self.diagnostics.append({
+                    "window_id": window_id,
+                    "client_id": cid,
+                    "observed_unit_ids": list(rec.observed_unit_ids),
+                    "risk_set_unit_ids": list(rec.risk_set_unit_ids),
+                    "raw_local_weights": raw_local.tolist(),
+                    "hajek_local_weights": data["a_bar"][obs_mask].tolist(),
+                    "applied_local_weights": a_bar_observed.tolist(),
+                    "a_bar": a_bar_observed.tolist(),
+                    "w_units": a_bar_observed.tolist(),
+                    "zeta_hat": data["zeta"].tolist(),
+                    "p_hat": data["p_hat"].tolist(),
+                    "m": float(data["m_total"]),
+                    "n_eff": float(data["n_eff"]),
+                    "local_loss": float(loss),
+                    "update_vector_hash": sha256_json(update.tolist()),
+                })
         stages.mark("local", STAGE_LOCAL)
 
         # Freeze q̂_use from pre-U features on B_r (do not form A_r yet).
@@ -731,6 +1026,7 @@ class FullWindowRunner:
 
         def _run_counterfactual() -> dict[str, Any]:
             tar_n, tar_c = self._target_coverage(window_slice)
+            agg = self.aggregator
             audit_obj = audit_design_vs_nodesign(
                 registered=[rec.client_id for rec in window_slice.records],
                 attempted=attempted_clients,
@@ -751,27 +1047,63 @@ class FullWindowRunner:
                 d_max=self.d_max,
                 q_min=self.q_min,
                 num_groups=self.num_groups,
+                v_floor=float(self.v_floor),
+                mu=np.asarray(self.mu, dtype=np.float64),
+                debt=np.asarray(self.debt, dtype=np.float64),
+                staleness={
+                    cid: float(data["record"].tau) / float(max(int(self.s_max), 1))
+                    for cid, data in client_data.items()
+                },
+                lambda_group=float(getattr(agg, "lambda_group", 1.0)),
+                lambda_beta=float(getattr(agg, "lambda_beta", 1.0)),
+                lambda_variance=float(getattr(agg, "lambda_variance", 0.1)),
+                lambda_staleness=float(getattr(agg, "lambda_staleness", 0.1)),
+                alpha_max=float(getattr(agg, "alpha_max", 0.5)),
+                e_min=float(getattr(agg, "e_min", 3.0)),
+                max_server_learning_rate=float(getattr(agg, "max_server_learning_rate", 1.0)),
             )
-            return audit_obj.as_dict()
+            payload = audit_obj.as_dict()
+            masses, counts = self._window_opp_events(window_slice)
+            payload["opp_mass_by_pair"] = masses
+            payload["opp_count_by_pair"] = counts
+            payload["opp_event_total"] = float(sum(counts.values()))
+            payload["old_realized_C_cov"] = payload.get("realized_C_cov")
+            return payload
 
         if not a_r_clients:
-            stages.mark("P2", STAGE_P2)
-            audit = _run_counterfactual()
-            self._record_sag_window(
-                window_id=window_id,
-                g_r=g_r,
-                stages=stages,
-                cert_inputs=cert_inputs,
-                fallback_reason=fallback_reason,
-                gate_passed=gate_passed,
-                b_r=b_r_clients,
-                a_r=[],
-                u_r=u_r_clients,
-                m_by_client={cid: float(client_data[cid]["m_total"]) for cid in b_r_clients},
-                audit=audit,
-                p2_invoked=False,
-                extras=self._policy_extras(client_data),
-            )
+            if mm is not None:
+                mmap_obj = getattr(mm, "_mmap", None)
+                del mm
+                mm = None
+                if mmap_obj is not None:
+                    mmap_obj.close()
+                gc.collect()
+            if mm_path and os.path.exists(mm_path):
+                try:
+                    os.remove(mm_path)
+                except OSError:
+                    pass
+                mm_path = None
+            if not lowmem:
+                stages.mark("P2", STAGE_P2)
+                audit = _run_counterfactual()
+                self._record_sag_window(
+                    window_id=window_id,
+                    g_r=g_r,
+                    stages=stages,
+                    cert_inputs=cert_inputs,
+                    fallback_reason=fallback_reason,
+                    gate_passed=gate_passed,
+                    b_r=b_r_clients,
+                    a_r=[],
+                    u_r=u_r_clients,
+                    m_by_client={cid: float(client_data[cid]["m_total"]) for cid in b_r_clients},
+                    audit=audit,
+                    p2_invoked=False,
+                    extras=self._policy_extras(client_data),
+                )
+            else:
+                stages.mark("P2", STAGE_P2)
             # U=0 attempts are still valid labels for future opportunity/p/q
             # estimators.  Update only after all current-window predictions and
             # local work are complete.
@@ -797,6 +1129,7 @@ class FullWindowRunner:
                 a_r_size=0,
                 b_r_size=len(b_r_clients),
                 g_r=int(g_r),
+                **self._design_metric_fields(),
             )
 
         # Step 8: Compute method-specific alpha
@@ -895,14 +1228,39 @@ class FullWindowRunner:
 
         # Step 9: ONE global update
         theta_flat = flatten_params(self.theta)
-        for i, cid in enumerate(a_r_clients):
-            if cid in local_updates and len(local_updates[cid]) > 0:
-                theta_flat = theta_flat - float(self.eta) * alpha[i] * local_updates[cid]
+        if stream_fedavg and fedavg_acc is not None:
+            theta_flat = theta_flat - float(self.eta) * fedavg_acc
+        else:
+            for i, cid in enumerate(a_r_clients):
+                vec = None
+                if lowmem and cid in mm_index:
+                    vec = np.asarray(mm[mm_index[cid]], dtype=np.float64)
+                elif cid in local_updates and len(local_updates[cid]) > 0:
+                    vec = local_updates[cid]
+                if vec is not None and len(vec) > 0:
+                    theta_flat = theta_flat - float(self.eta) * alpha[i] * vec
 
         self.theta = unflatten_params(theta_flat, self.theta)
         self.model.load_state_dict(self.theta)
         new_version = self.clock.apply_server_update()
         self.model_versions[new_version] = copy.deepcopy(self.theta)
+        if mm is not None:
+            mmap_obj = getattr(mm, "_mmap", None)
+            try:
+                mm.flush()
+            except Exception:
+                pass
+            del mm
+            mm = None
+            if mmap_obj is not None:
+                mmap_obj.close()
+            gc.collect()
+        if mm_path and os.path.exists(mm_path):
+            try:
+                os.remove(mm_path)
+            except OSError:
+                pass
+            mm_path = None
 
         # Step 10: Update debt
         omega = coverage_mix(compositions_mat, alpha)
@@ -938,7 +1296,11 @@ class FullWindowRunner:
                     "lagged_S2": float(lagged_s2[i]),
                     "variance_proxy": float(variance_diag[i]),
                     "cold_start": bool(variance_cold_start[i]),
-                    "update_norm": float(np.linalg.norm(local_updates[cid])),
+                    "update_norm": float(
+                        update_norms[cid]
+                        if lowmem
+                        else np.linalg.norm(local_updates[cid])
+                    ),
                     "variance_state_updated_after_close": True,
                     "global_model_hash": after_hash,
                 })
@@ -960,22 +1322,23 @@ class FullWindowRunner:
 
         avg_train_loss = float(np.mean(list(train_losses.values()))) if train_losses else 0.0
 
-        audit = _run_counterfactual()
-        self._record_sag_window(
-            window_id=window_id,
-            g_r=g_r,
-            stages=stages,
-            cert_inputs=cert_inputs,
-            fallback_reason=fallback_reason,
-            gate_passed=gate_passed,
-            b_r=b_r_clients,
-            a_r=a_r_clients,
-            u_r=u_r_clients,
-            m_by_client={cid: float(client_data[cid]["m_total"]) for cid in b_r_clients},
-            audit=audit,
-            p2_invoked=True,
-            extras=self._policy_extras(client_data),
-        )
+        if not lowmem:
+            audit = _run_counterfactual()
+            self._record_sag_window(
+                window_id=window_id,
+                g_r=g_r,
+                stages=stages,
+                cert_inputs=cert_inputs,
+                fallback_reason=fallback_reason,
+                gate_passed=gate_passed,
+                b_r=b_r_clients,
+                a_r=a_r_clients,
+                u_r=u_r_clients,
+                m_by_client={cid: float(client_data[cid]["m_total"]) for cid in b_r_clients},
+                audit=audit,
+                p2_invoked=True,
+                extras=self._policy_extras(client_data),
+            )
 
         return WindowMetrics(
             window_id=window_id,
@@ -995,6 +1358,7 @@ class FullWindowRunner:
             a_r_size=len(a_r_clients),
             b_r_size=len(b_r_clients),
             g_r=int(g_r),
+            **self._design_metric_fields(),
         )
 
     def _update_lagged_estimators(
@@ -1132,7 +1496,9 @@ def build_full_runner(
     trace: EventTrace,
     dataset: ProcessedDataset,
     *,
-    method: str = "raven",
+    method: str = "raven_mcs",
+    design: str | None = None,
+    design_source: str = "explicit_api",
     n_groups: int | None = None,
     model_seed: int = 26001,
     learning_rate: float = 0.01,
@@ -1148,8 +1514,11 @@ def build_full_runner(
     q_min: float = 0.05,
     use_coarse_time_groups: bool = False,
     pi_opp_joint: dict[tuple[str, str], float] | None = None,
+    paper_h_by_unit: dict[str, int] | None = None,
 ) -> FullWindowRunner:
     """Build a FullWindowRunner for end-to-end training."""
+    from raven_mcs.sag.r1l_design import configuration_for_method
+    design_configuration = configuration_for_method(method, design, source=design_source)
     if n_groups is None:
         n_groups = dataset.num_groups
 
@@ -1177,6 +1546,8 @@ def build_full_runner(
             atomic_for_pi["target_group_main"] = (
                 RepeatableTimeOfDayMapper().map(atomic_for_pi)
             )
+        else:
+            atomic_for_pi["target_group_main"] = pd.Categorical(atomic_for_pi["target_group"]).codes
         unit_station = atomic_for_pi.set_index("unit_id")[
             "spatial_id"
         ].astype(str).to_dict()
@@ -1209,6 +1580,7 @@ def build_full_runner(
         model=model,
         aggregator=aggregator,
         policy=policy,
+        design_configuration=design_configuration,
         mu=mu,
         num_groups=n_groups,
         learning_rate=learning_rate,
@@ -1221,6 +1593,7 @@ def build_full_runner(
         pi_target=dict(pi_target or {}),
         s_max=int(s_max if s_max is not None else trace.metadata.s_max),
         use_coarse_time_groups=bool(use_coarse_time_groups),
+        paper_h_by_unit=dict(paper_h_by_unit) if paper_h_by_unit else None,
         pi_opp_joint=dict(pi_opp_joint or {}),
         seed=model_seed,
         device=device,
diff --git a/src/raven_mcs/utils/config.py b/src/raven_mcs/utils/config.py
index d19e4da..10d844d 100644
--- a/src/raven_mcs/utils/config.py
+++ b/src/raven_mcs/utils/config.py
@@ -81,6 +81,22 @@ def resolve_run_config(
     if overrides:
         cfg = deep_merge(cfg, overrides)
 
+    from raven_mcs.aggregation.method_policy import get_method_policy
+    from raven_mcs.sag.r1l_design import configuration_for_method
+    method_name = str(cfg["method"])
+    policy = get_method_policy(method_name)
+    configuration = configuration_for_method(
+        method_name, cfg.get("design"), source=cfg.get("design_source", "explicit_run_config"),
+    )
+    if policy.design_control == "configured":
+        cfg["design_configuration"] = configuration.to_dict()
+        cfg["method_version"] = policy.method_version
+        cfg["coverage_role"] = "diagnostic_only"
+    elif policy.method_version == "coverage-controlled-v1":
+        cfg["design_configuration"] = None
+        cfg["method_version"] = policy.method_version
+        cfg["coverage_role"] = "controls_legacy_design"
+
     seed_bundle = SeedBundle.from_config(cfg["seed"], cfg.get("seeds"))
     cfg["seeds"] = seed_bundle.as_dict()
     if validate:
diff --git a/src/raven_mcs/utils/manifest.py b/src/raven_mcs/utils/manifest.py
index cd10ad2..093d8d4 100644
--- a/src/raven_mcs/utils/manifest.py
+++ b/src/raven_mcs/utils/manifest.py
@@ -67,12 +67,20 @@ def git_executable() -> str | None:
     return None
 
 
-def _git_info(repo_root: Path | None = None) -> tuple[str, bool | None, str]:
+def _git_info(repo_root: Path | None = None, *, source_paths: tuple[Path, ...] | None = None) -> tuple[str, bool | None, str]:
     cwd = str(repo_root) if repo_root is not None else None
     git = git_executable()
     if git is None:
         return "NO_GIT", None, sha256_json({"git": "NO_GIT"})
     try:
+        if repo_root is not None:
+            actual_root=Path(subprocess.check_output(
+                [git,'rev-parse','--show-toplevel'],cwd=cwd,
+                stderr=subprocess.DEVNULL,text=True).strip()).resolve()
+            if actual_root!=Path(repo_root).resolve():
+                # Explicit roots must identify this checkout, not accidentally
+                # borrow a parent's identity for a nested non-repository folder.
+                return 'NO_GIT',None,sha256_json({'git':'NO_GIT','reason':'explicit_root_mismatch'})
         commit = subprocess.check_output(
             [git, "rev-parse", "HEAD"],
             cwd=cwd,
@@ -89,16 +97,26 @@ def _git_info(repo_root: Path | None = None) -> tuple[str, bool | None, str]:
         )
         dirty = bool(status_bytes.strip())
         diff_bytes = subprocess.check_output(
-            [git, "diff", "--binary", "--no-ext-diff", "HEAD"],
-            cwd=cwd,
-            stderr=subprocess.DEVNULL,
-        )
-        untracked_bytes = subprocess.check_output(
-            [git, "ls-files", "--others", "--exclude-standard", "-z"],
+            [git, "diff", "--binary", "--no-ext-diff", "--no-textconv", "HEAD"],
             cwd=cwd,
             stderr=subprocess.DEVNULL,
         )
         root = Path(cwd) if cwd is not None else Path.cwd()
+        if source_paths is None:
+            untracked_bytes = subprocess.check_output(
+                [git, "ls-files", "--others", "--exclude-standard", "-z"],
+                cwd=cwd, stderr=subprocess.DEVNULL,
+            )
+        else:
+            # Dynamic control freezes its complete computational source closure,
+            # not unrelated multi-GB output files. Scope is explicit in manifest;
+            # the historical whole-repository mode remains available unchanged.
+            names=[]
+            for path in source_paths:
+                resolved=Path(path).resolve()
+                names.append(resolved.relative_to(root.resolve()).as_posix())
+                if not resolved.is_file():raise ValueError(f"missing source dependency: {resolved}")
+            untracked_bytes=b'\0'.join(name.encode('utf-8') for name in sorted(set(names)))+b'\0'
         untracked_content = bytearray()
         for encoded_path in untracked_bytes.split(b"\0"):
             if not encoded_path:
@@ -113,7 +131,9 @@ def _git_info(repo_root: Path | None = None) -> tuple[str, bool | None, str]:
         state_hash = sha256_bytes(
             status_bytes + b"\0" + diff_bytes + b"\0" + bytes(untracked_content)
         )
-    except (subprocess.CalledProcessError, FileNotFoundError, OSError):
+    except (subprocess.CalledProcessError, FileNotFoundError, OSError) as exc:
+        if source_paths is not None:
+            raise RuntimeError(f"SOURCE_MANIFEST_GIT_STATE_FAILED: {exc!r}") from exc
         dirty = None
         state_hash = sha256_json({"git": "STATE_UNAVAILABLE", "commit": commit})
     return commit, dirty, state_hash
@@ -146,6 +166,8 @@ class RunManifest:
     environment: dict[str, Any] = field(default_factory=dict)
     phase: str = "1"
     constitution_version: str = "V2.3"
+    git_state_scope: str = "whole_repository"
+    source_files: list[str] = field(default_factory=list)
 
     def to_dict(self) -> dict[str, Any]:
         return asdict(self)
@@ -224,6 +246,7 @@ def build_manifest(
     repo_root: Path | None = None,
     require_git: bool = False,
     allow_unset_hashes: bool = False,
+    source_paths: tuple[Path, ...] | None = None,
 ) -> RunManifest:
     config_seed = config.get("seed")
     configured_seeds = config.get("seeds")
@@ -236,7 +259,7 @@ def build_manifest(
         raise ValueError(
             "seed_bundle does not match the resolved config seed streams"
         )
-    commit, dirty, git_state_hash = _git_info(repo_root)
+    commit, dirty, git_state_hash = _git_info(repo_root, source_paths=source_paths)
     if require_git and (commit == "NO_GIT" or dirty is None):
         raise RuntimeError("Git is required for an auditable run, but no repository is available")
     if not allow_unset_hashes:
@@ -288,6 +311,8 @@ def build_manifest(
         failure_reason=None,
         seeds=seed_bundle.as_dict(),
         environment=environment_fingerprint(),
+        git_state_scope="explicit_computational_source_closure" if source_paths is not None else "whole_repository",
+        source_files=[str(p) for p in source_paths] if source_paths is not None else [],
     )
     errors = manifest.validate()
     if errors:
diff --git a/src/raven_mcs/utils/validation.py b/src/raven_mcs/utils/validation.py
index 9d96a52..dc0fb3b 100644
--- a/src/raven_mcs/utils/validation.py
+++ b/src/raven_mcs/utils/validation.py
@@ -40,6 +40,8 @@ INTERNAL_CONFIG_KEYS = (
     "_method_cfg",
     "_scenario_cfg",
 )
+DESIGN_CONFIG_KEYS = {"design", "design_source", "design_configuration", "method_version", "coverage_role"}
+METHOD_IDENTITY_KEYS = {"method_version", "design_control", "design_required", "coverage_diagnostic", "coverage_role", "gate_mode", "legacy_only"}
 
 BLOCK_KEYS = {
     "clients": {"K", "local_steps", "risk_set_mean"},
@@ -152,7 +154,7 @@ def _validate_named_slices(raw: Mapping[str, Any], errors: list[str]) -> None:
         if not isinstance(value, Mapping):
             errors.append(f"{slice_name} must be a mapping")
             continue
-        _reject_unknown(value, allowed, f"{slice_name}.", errors)
+        _reject_unknown(value, allowed | (METHOD_IDENTITY_KEYS if slice_name == "_method_cfg" else set()), f"{slice_name}.", errors)
         name = value.get("name")
         if not isinstance(name, str) or not name.strip():
             errors.append(f"{slice_name}.name must be a non-empty string")
@@ -256,11 +258,22 @@ def validate_config(config: Mapping[str, Any]) -> ValidatedConfig:
     _require_keys(raw, REQUIRED_TOP_LEVEL, "", errors)
     _reject_unknown(
         raw,
-        set(REQUIRED_TOP_LEVEL) | set(INTERNAL_CONFIG_KEYS),
+        set(REQUIRED_TOP_LEVEL) | set(INTERNAL_CONFIG_KEYS) | DESIGN_CONFIG_KEYS,
         "",
         errors,
     )
 
+    if raw.get("method") in {"raven_mcs", "raven_mcs_formal", "raven_formal"}:
+        from raven_mcs.sag.r1l_design import DesignConfiguration
+        try:
+            configuration = DesignConfiguration.from_dict(raw.get("design_configuration") or {})
+            if raw.get("design") != ("on" if configuration.enabled else "off"):
+                errors.append("design and serialized design_configuration disagree")
+            if raw.get("method_version") != configuration.method_version or raw.get("coverage_role") != "diagnostic_only":
+                errors.append("configured method identity mismatch")
+        except (TypeError, ValueError) as exc:
+            errors.append(f"invalid explicit Design configuration: {exc}")
+
     for key in ("experiment", "dataset", "method", "scenario", "device", "output_dir"):
         value = raw.get(key)
         if value is not None and (not isinstance(value, str) or not value.strip()):
```

工作区短状态：

```
M RAVEN_MCS_PUBLIC_REPRO_R1/BUNDLE_SUMMARY.json
 M RAVEN_MCS_PUBLIC_REPRO_R1/MANIFEST.csv
 M RAVEN_MCS_PUBLIC_REPRO_R1/PROTOCOL.json
 M RAVEN_MCS_PUBLIC_REPRO_R1/README.md
 M RAVEN_MCS_PUBLIC_REPRO_R1/tables/TABLE_E3_MAIN_EFFECTIVENESS.csv
 M TO_OVERLEAF_paper_tmc_r1_clean/appendix.tex
 M TO_OVERLEAF_paper_tmc_r1_clean/figure_data/FIG_E3_E3_PREDICTION_RISK.csv
 M TO_OVERLEAF_paper_tmc_r1_clean/figure_data/FIG_E4_E4_COMPONENT_ABLATION.csv
 M TO_OVERLEAF_paper_tmc_r1_clean/figure_data/FIG_W1_DESIGN_GATE.csv
 M TO_OVERLEAF_paper_tmc_r1_clean/figures/fig1_raven_problem_framework.pdf
 M TO_OVERLEAF_paper_tmc_r1_clean/figures/fig2_e2_risk_noninterchangeability.pdf
 M TO_OVERLEAF_paper_tmc_r1_clean/figures/fig3_e3_structural_mismatch.pdf
 M TO_OVERLEAF_paper_tmc_r1_clean/figures/fig4_e3_prediction_risk.pdf
 M TO_OVERLEAF_paper_tmc_r1_clean/figures/fig4_e3_prediction_risk.png
 M TO_OVERLEAF_paper_tmc_r1_clean/figures/fig5_e4_component_ablation.pdf
 M TO_OVERLEAF_paper_tmc_r1_clean/figures/fig5_e4_component_ablation.png
 M TO_OVERLEAF_paper_tmc_r1_clean/figures/fig6_e4_uair_excl_design.pdf
 M TO_OVERLEAF_paper_tmc_r1_clean/figures/fig6_e4_uair_excl_design.png
 M TO_OVERLEAF_paper_tmc_r1_clean/figures/fig_certificate_audit.pdf
 M TO_OVERLEAF_paper_tmc_r1_clean/figures/fig_g3_tdrive_h_mass.pdf
 M TO_OVERLEAF_paper_tmc_r1_clean/figures/fig_w1_design_gate.pdf
 M TO_OVERLEAF_paper_tmc_r1_clean/figures/fig_w1_design_gate.png
 M TO_OVERLEAF_paper_tmc_r1_clean/main.tex
 M TO_OVERLEAF_paper_tmc_r1_clean/reference.bib
 M TO_OVERLEAF_paper_tmc_r1_clean/supplemental.tex
 M _paper_work/figures/fig1_raven_problem_framework.pdf
 M _paper_work/figures/fig1_raven_problem_framework.png
 M _paper_work/figures/fig1_raven_problem_framework.svg
 M _paper_work/make_figures.py
 M configs/audit/q_feature_whitelist.yaml
 M configs/dataset/cityscanner_nyc_pm25.yaml
 M configs/experiment/E3_main_complete.yaml
 M docs/reports/E1_FORMAL_FREEZE_R1_PREFLIGHT.md
 M docs/reports/E1_R2_COMMUNICATION_METRIC_NOTE.md
 M post_review/C1_kill_cityscanner/C1_KILL_INSTRUCTION.md
 M post_review/C1_kill_cityscanner/TARGET_SPEC.json
 M post_review/C1_kill_tdrive_spatial/C1_KILL_INSTRUCTION.md
 M post_review/C1_kill_tdrive_spatial/DRIVER_HAJEK_SLOWDOWN_PATCH_INSTRUCTION.md
 M post_review/C1_kill_tdrive_spatial/TARGET_SPEC.json
 M post_review/C1_tdrive_rank/REMOTE_AGENT_PROMPT.md
 M post_review/C1_tdrive_rank/REMOTE_SYNC.md
 M results_c1_cityscanner/round_v1/INGEST_REPORT.json
 M results_support_consumption/round_v1/BUDGET_LEDGER.json
 M results_support_consumption/round_v1/DECISION_REPORT.md
 M results_support_consumption/round_v1/P0_STATUS.json
 M results_tdrive_rank/TD_R_ZIP_INGEST_AUDIT.json
 M results_tdrive_rank/round_v1/TD_R_HARDWARE_STOP.json
 M scripts/build_public_repro_bundle.py
 M scripts/check_e2_traffic_formal_runs_gates.py
 M scripts/run_c1_tdrive_spatial.py
 M scripts/run_experiment.py
 M scripts/run_tdrive_rank_v1.py
 M src/raven_mcs/aggregation/feasibility.py
 M src/raven_mcs/aggregation/method_policy.py
 M src/raven_mcs/aggregation/methods.py
 M src/raven_mcs/aggregation/p2_cvxpy.py
 M src/raven_mcs/correction/design_ratio.py
 M src/raven_mcs/correction/pi_target.py
 M src/raven_mcs/data/cityscanner.py
 M src/raven_mcs/data/window_dataset.py
 M src/raven_mcs/experiments/e1_entry.py
 M src/raven_mcs/experiments/sag_runtime.py
 M src/raven_mcs/sag/__init__.py
 M src/raven_mcs/sag/certificates.py
 M src/raven_mcs/sag/counterfactual_audit.py
 M src/raven_mcs/training/window_runner.py
 M src/raven_mcs/utils/config.py
 M src/raven_mcs/utils/manifest.py
 M src/raven_mcs/utils/validation.py
 M tests/unit/test_e1_entry_r3_opportunity.py
 M tests/unit/test_e1_entry_r4_attempt_semantics.py
?? .codex-remote-attachments/
?? .m7_work/
?? .r11_work/
?? .r3_work/
?? .rb_work/
?? .s1_work/
?? .sync_diag/
?? .venv_new/
?? .vscode/
?? ADVISOR_PACKAGE_TMC_R1/
?? DESIGN_GATE_ALIGNMENT_REPORT.md
?? RAVEN_MCS_FINAL_FIGURE_TABLE_PAPER_SPECIFICATION_SEAL_R1/
?? RAVEN_MCS_FINAL_PAPER_DATA_ASSET_FREEZE_R1/
?? RAVEN_MCS_FINAL_TABLE_II_REPAIR_R1/
?? RAVEN_MCS_PUBLIC_REPRO_R1/cityscanner/
?? RAVEN_MCS_PUBLIC_REPRO_R1/cityscanner_p2/
?? RAVEN_MCS_PUBLIC_REPRO_R1/new_target/
?? RAVEN_MCS_PUBLIC_REPRO_R1/scripts/rebuild_e3_scd_holm_fedau_obsuse.py
?? RAVEN_MCS_PUBLIC_REPRO_R1/scripts/rebuild_table_ii.py
?? RAVEN_MCS_PUBLIC_REPRO_R1/scripts/rebuild_table_ii_tolerance.py
?? RAVEN_MCS_PUBLIC_REPRO_R1/submission_evidence/
?? RAVEN_MCS_PUBLIC_REPRO_R1/tables/E3_SCD_WORSTGROUP_SLICE_REL.csv
?? RAVEN_MCS_PUBLIC_REPRO_R1/tables/E3_SCD_WORSTGROUP_VS_FEDAU_OBSUSE_HOLM.csv
?? RAVEN_MCS_PUBLIC_REPRO_R1/tables/SCD_PHI.csv
?? RAVEN_MCS_PUBLIC_REPRO_R1/tables/SCD_PHI.json
?? RAVEN_MCS_PUBLIC_REPRO_R1/tables/SCD_PHI_BY_SEED.csv
?? RAVEN_MCS_PUBLIC_REPRO_R1/tables/SCD_PHI_DECISION.json
?? RAVEN_MCS_PUBLIC_REPRO_R1/tables/TABLE_II_FREEZE.json
?? RAVEN_MCS_PUBLIC_REPRO_R1/tables/TABLE_II_MAIN_EFFECTIVENESS.csv
?? RAVEN_MCS_PUBLIC_REPRO_R1/tables/TABLE_II_WORSTGROUP_PER_SEED.csv
?? RAVEN_MCS_PUBLIC_REPRO_R1/tdrive/TD_R_E3.csv
?? RAVEN_MCS_PUBLIC_REPRO_R1/tdrive/TD_R_E3_PAIRED.csv
?? RAVEN_MCS_PUBLIC_REPRO_R1/tdrive/TD_R_E3_SUMMARY.csv
?? RAVEN_MCS_PUBLIC_REPRO_R1/tdrive/TD_R_FREEZE.json
?? RAVEN_MCS_PUBLIC_REPRO_R1/tdrive/TD_R_PHI.csv
?? RAVEN_MCS_PUBLIC_REPRO_R1/w1/
?? RAVEN_MCS_TMC_r1_overleaf/
?? REVIEW_ccf_raven_tmc_r1_c1hybrid.md
?? SAG_G1_R1B_SEMANTIC_REPAIR_PLAN.md
?? SAG_G1_R1C_REPAIR_PLAN.md
?? SAG_G1_R1D_PLAN.md
?? SAG_G1_R1_REPAIR_PLAN.md
?? TO_OVERLEAF_paper_tmc_r1_clean/_check.txt
?? TO_OVERLEAF_paper_tmc_r1_clean/ccfa-review-reports/
?? TO_OVERLEAF_paper_tmc_r1_clean/figures/fig_learning_capacity_r2.png
?? TO_OVERLEAF_paper_tmc_r1_clean/main.aux
?? TO_OVERLEAF_paper_tmc_r1_clean/main.bbl
?? TO_OVERLEAF_paper_tmc_r1_clean/main.blg
?? TO_OVERLEAF_paper_tmc_r1_clean/main.log
?? TO_OVERLEAF_paper_tmc_r1_clean/main.pdf
?? TO_OVERLEAF_paper_tmc_r1_clean/main.txt
?? TO_OVERLEAF_paper_tmc_r1_clean/supplemental.aux
?? TO_OVERLEAF_paper_tmc_r1_clean/supplemental.bbl
?? TO_OVERLEAF_paper_tmc_r1_clean/supplemental.blg
?? TO_OVERLEAF_paper_tmc_r1_clean/supplemental.log
?? TO_OVERLEAF_paper_tmc_r1_clean/supplemental.pdf
?? _acl_reports/
?? _handoff_sag_g1_r1/
?? _handoff_sag_g1_r1b/
?? _handoff_sag_g1_r1c/
?? _handoff_sag_g1_r1d/
?? _handoff_sag_g1_r1e/
?? _paper_work/FedAU_backfill_instruction.md
?? _paper_work/FedAU_baseline_experiment_instruction.md
?? _paper_work/FedAU_critical_fix_instruction.md
?? _paper_work/FedAU_three_actions_instruction.md
?? _paper_work/P0_drifting_stress_instruction.md
?? _paper_work/P1_deployment_consequence_instruction.md
?? _paper_work/P2A_positioning_rewrite_instruction.md
?? _paper_work/P3_design_noharm_instruction.md
?? _paper_work/_append_fedau_figures.py
?? _paper_work/_append_obsuse_figures.py
?? _paper_work/_check_fig1.py
?? _paper_work/_cite_audit.py
?? _paper_work/_cite_compare.py
?? _paper_work/_cite_dump.py
?? _paper_work/_integrity_audit.py
?? _paper_work/_paper_work.lnk
?? _paper_work/_ref_consistency.py
?? _paper_work/_run_design_phase_a.py
?? _paper_work/_tmp_docx_extract/
?? _paper_work/bibtex.log
?? _paper_work/ccfa-rebuttal-m1-m3.md
?? _paper_work/ccfa-review-report.md
?? _paper_work/ccfa-review-reports/
?? _paper_work/deployment_consequence_results/
?? _paper_work/design_noharm_results/
?? _paper_work/drifting_window_results/
?? _paper_work/fedau_window_results/
?? _paper_work/figure_data/
?? _paper_work/figures/fig1_raven_problem_framework.tiff
?? _paper_work/figures/fig1_raven_problem_framework_v2.pdf
?? _paper_work/figures/fig1_raven_problem_framework_v2.png
?? _paper_work/figures/fig1_raven_problem_framework_v3.pdf
?? _paper_work/figures/fig1_raven_problem_framework_v3.png
?? _paper_work/figures/fig2_e2_risk_noninterchangeability.pdf
?? _paper_work/figures/fig2_e2_risk_noninterchangeability.png
?? _paper_work/figures/fig2_e2_risk_noninterchangeability.svg
?? _paper_work/figures/fig2_e2_risk_noninterchangeability.tiff
?? _paper_work/figures/fig3_e3_structural_mismatch.pdf
?? _paper_work/figures/fig3_e3_structural_mismatch.png
?? _paper_work/figures/fig3_e3_structural_mismatch.svg
?? _paper_work/figures/fig3_e3_structural_mismatch.tiff
?? _paper_work/figures/fig4_e3_prediction_risk.pdf
?? _paper_work/figures/fig4_e3_prediction_risk.png
?? _paper_work/figures/fig4_e3_prediction_risk.svg
?? _paper_work/figures/fig4_e3_prediction_risk.tiff
?? _paper_work/figures/fig5_e4_component_ablation.pdf
?? _paper_work/figures/fig5_e4_component_ablation.png
?? _paper_work/figures/fig5_e4_component_ablation.svg
?? _paper_work/figures/fig5_e4_component_ablation.tiff
?? _paper_work/figures/fig6_e4_uair_excl_design.pdf
?? _paper_work/figures/fig6_e4_uair_excl_design.png
?? _paper_work/figures/fig6_e4_uair_excl_design.svg
?? _paper_work/figures/fig6_e4_uair_excl_design.tiff
?? _paper_work/figures_nature/
?? _paper_work/main.aux
?? _paper_work/main.bbl
?? _paper_work/main.blg
?? _paper_work/main.log
?? _paper_work/main.pdf
?? _paper_work/main.tex
?? _paper_work/make_fig1_icons.py
?? _paper_work/make_fig1_redesign.py
?? _paper_work/make_figures_nature.py
?? _paper_work/obsuse_window_results/
?? _paper_work/pass1.log
?? _paper_work/pass2.log
?? _paper_work/pass3.log
?? _paper_work/reference.bib
?? _paper_work/worst_group_results/
?? "_paper_work/\346\224\271\345\212\250\346\200\273\347\273\223_\345\210\235\347\250\277\345\210\260\347\273\210\347\250\277.md"
?? _probe_new/
?? _r13_build/
?? _tmp_pack/
?? _tmp_ref/
?? artifacts/
?? baseline-references-to-download.md
?? ccf-review-report/
?? ccfa-review-reports/literature-search-20261002-design-rule-theoremization/
?? ccfa-review-reports/next-ai-handoff.md
?? ccfa-review-reports/raven-mcs-a1-c1-gatekeeping-exogenous-protocol.md
?? ccfa-review-reports/raven-mcs-active-set-repair-analysis-20260927.md
?? ccfa-review-reports/raven-mcs-active-set-repair-design.md
?? ccfa-review-reports/raven-mcs-aggregate-total-execution-prompt.md
?? ccfa-review-reports/raven-mcs-ceiling-ladder-manuscript-execution-prompt.md
?? ccfa-review-reports/raven-mcs-cross-window-pool-experiment-design.md
?? ccfa-review-reports/raven-mcs-defensive-prose-diagnosis-20261011.md
?? ccfa-review-reports/raven-mcs-defensive-prose-revision-checks.json
?? ccfa-review-reports/raven-mcs-defensive-prose-revision.md
?? ccfa-review-reports/raven-mcs-design-gate-proposition-draft.md
?? ccfa-review-reports/raven-mcs-endpoint-screen-execution-prompt.md
?? ccfa-review-reports/raven-mcs-estimand-gate-execution-prompt.md
?? ccfa-review-reports/raven-mcs-evidence-axis-audit.md
?? ccfa-review-reports/raven-mcs-exogenous-endpoint-execution-prompt.md
?? ccfa-review-reports/raven-mcs-exogenous-target-execution-prompt.md
?? ccfa-review-reports/raven-mcs-exogenous-target-preregistration.md
?? ccfa-review-reports/raven-mcs-experiment-design-audit.md
?? ccfa-review-reports/raven-mcs-experiment-report-20260924.md
?? ccfa-review-reports/raven-mcs-f1-experiment-design.md
?? ccfa-review-reports/raven-mcs-f1-experiment-summary.md
?? ccfa-review-reports/raven-mcs-fedavg-restore-execution-prompt.md
?? ccfa-review-reports/raven-mcs-gate-dose-execution-prompt.md
?? ccfa-review-reports/raven-mcs-group-decomposition-b1-draft.md
?? ccfa-review-reports/raven-mcs-group-identity-execution-prompt.md
?? ccfa-review-reports/raven-mcs-h-headroom-preregistration.md
?? ccfa-review-reports/raven-mcs-h-response-shift-execution-prompt.md
?? ccfa-review-reports/raven-mcs-handoff-2026-10-06.md
?? ccfa-review-reports/raven-mcs-honesty-text-repairs-execution-prompt.md
?? ccfa-review-reports/raven-mcs-integrity-audit-new-passages.md
?? ccfa-review-reports/raven-mcs-integrity-audit.md
?? ccfa-review-reports/raven-mcs-literature-monitor-20260927.md
?? ccfa-review-reports/raven-mcs-m7-bundle-refresh-protocol.md
?? ccfa-review-reports/raven-mcs-main-experiment-rebuild-design-20261011.md
?? ccfa-review-reports/raven-mcs-method-definition-card.md
?? ccfa-review-reports/raven-mcs-method-definition-consistency-audit.md
?? ccfa-review-reports/raven-mcs-method-definition-consistency.patch
?? ccfa-review-reports/raven-mcs-method-definition-sync-list.md
?? ccfa-review-reports/raven-mcs-method-revision-evaluation.md
?? ccfa-review-reports/raven-mcs-method1-method3-practice-report.md
?? ccfa-review-reports/raven-mcs-metric-definition-diagnosis.md
?? ccfa-review-reports/raven-mcs-new-block-traffic-execution-prompt.md
?? ccfa-review-reports/raven-mcs-oracle-baseline-remeasurement-protocol.md
?? ccfa-review-reports/raven-mcs-r12-response-to-review.md
?? ccfa-review-reports/raven-mcs-reachability-attribution-experiment-design.md
?? ccfa-review-reports/raven-mcs-round11-execution-report.md
?? ccfa-review-reports/raven-mcs-round11-text-repair-instruction.md
?? ccfa-review-reports/raven-mcs-tier2-directions-20260927.md
?? ccfa-review-reports/raven-mcs-tmc-blind-review.md
?? ccfa-review-reports/raven-mcs-tmc-independent-review-2026-09-11.md
?? ccfa-review-reports/raven-mcs-tmc-rereview-2026-09-11.md
?? ccfa-review-reports/raven-mcs-tmc-rereview-wording-2026-09-11.md
?? ccfa-review-reports/raven-mcs-tmc-rereview-wording-2026-09-12.md
?? ccfa-review-reports/raven-mcs-tmc-review-deepseek-r15.md
?? ccfa-review-reports/raven-mcs-tmc-review-deepseek-r16.md
?? ccfa-review-reports/raven-mcs-tmc-review-deepseek-r17.md
?? ccfa-review-reports/raven-mcs-tmc-review-deepseek-r18.md
?? ccfa-review-reports/raven-mcs-tmc-review-round10.md
?? ccfa-review-reports/raven-mcs-tmc-review-round5.md
?? ccfa-review-reports/raven-mcs-tmc-review-round6.md
?? ccfa-review-reports/raven-mcs-tmc-review-round7.md
?? ccfa-review-reports/raven-mcs-tmc-review-round8.md
?? ccfa-review-reports/raven-mcs-tmc-review-round9.md
?? ccfa-review-reports/raven-mcs-tmc-review.md
?? ccfa-review-reports/raven-mcs-traffic-concentrated-target-experiment-design.md
?? ccfa-review-reports/raven-mcs-traffic-e1-confirm-execution-prompt.md
?? ccfa-review-reports/raven-mcs-traffic-struct-readout-execution-prompt.md
?? ccfa-review-reports/raven-mcs-two-constant-disclosure-execution-prompt.md
?? ccfa-review-reports/raven-mcs-uair-headroom-design.md
?? ccfa-review-reports/raven-mcs-unspecified-venue-review.md
?? ccfa-review-reports/raven-mcs-w1-handoff-for-gpt.md
?? ccfa-review-reports/raven-mcs-w1-ladder-frontier-execution-prompt.md
?? ccfa-review-reports/raven-mcs-w1-necessity-analysis.md
?? ccfa-review-reports/raven-mcs-w1-round-v3-execution-prompt.md
?? ccfa-review-reports/raven-mcs-w1-round-v4-execution-prompt.md
?? ccfa-review-reports/raven-mcs-w1-round-v5-R1R3R4-protocol.md
?? ccfa-review-reports/raven-mcs-w1-round-v5_1-execution-prompt.md
?? ccfa-review-reports/snapshots/
?? check_paper_data_metadata_and_claim_repair_r2.py
?? check_raven_final_figure_table_paper_specification_seal_r1.py
?? check_raven_final_paper_data_asset_freeze_r1.py
?? check_raven_manuscript_evidence_closure_r1.py
?? check_raven_tableii_unit_scale_repair_r1.py
?? check_tdrive_real_mobility_protocol_seal_r1.py
?? configs/control/
?? configs/deployment_group_map/
?? configs/frozen/e2_certification/
?? configs/frozen/e2_data_recovery/
?? configs/frozen/e2_dgp_certification/
?? configs/frozen/e2_empirical/
?? configs/frozen/e2_finite_sample_gate/
?? configs/frozen/e2_global_windows/
?? configs/frozen/e2_legal_horizon/
?? configs/frozen/e2_spatial_identity/
?? configs/frozen/e2_stage2/
?? configs/frozen/e2_stage2_stratum/
?? configs/frozen/e2_stratum/
?? configs/frozen/e2_traffic/
?? configs/frozen/e2_traffic_profiles/
?? configs/frozen/e2_traffic_profiles_s1/
?? configs/frozen/e2_traffic_public_target/
?? configs/frozen/e2_true_stratum/
?? configs/frozen/e3_delta_cs_atomic_rho_hotfix_r1/
?? configs/frozen/e3_multidataset_protocol_closure/
?? configs/frozen/e3_pair_rho_hotfix_r1/
?? configs/frozen/e3_real_runner_correctness_r1/
?? configs/frozen/e3_semantic_alignment_r2/
?? configs/frozen/e3_stratum_reuse_seal_r1/
?? configs/frozen/e3_target_pair_metric_final_r1/
?? configs/method/configured_design_v1.json
?? configs/method/fedau_window.yaml
?? configs/method/obsuse_window.yaml
?? configs/method/raven_coverage_legacy.yaml
?? configs/method/raven_mcs.yaml
?? configs/sag_g1/r1m_method_freeze.json
?? configs/sag_g1_r1/
?? literature-search-20260910-mcs-mobile-field-datasets/
?? literature-search-20260911-cityscanner-no2-bounds/
?? literature-search-20260919-raven-mcs-citation-verify/
?? literature-search-20260922-exogenous-mobile-datasets/
?? literature-search-20261009-concentrated-target/
?? literature-search-20261010-selection-corrected-aggregation/
?? manuscript_evidence_closure_r1/
?? outputs/_tmp_e3f_probe/
?? outputs/_tmp_e3f_probe2/
?? outputs/_tmp_e3r_probe/
?? outputs/_tmp_e3r_probe2/
?? outputs/_tmp_g9_ledger_test.jsonl
?? outputs/_tmp_pf_probe/
?? outputs/_tmp_pf_probe_bal/
?? outputs/_tmp_schedule_extract/
?? outputs/archive/
?? outputs/data_recovery/
?? outputs/e2_balanced_calibration/
?? outputs/e2_balanced_dgp/
?? outputs/e2_distribution/
?? outputs/e2_empirical/
?? outputs/e2_global_window/
?? outputs/e2_hard_variance/
?? outputs/e2_stage2_stratum/
?? outputs/e2_traffic_balanced_canary/
?? outputs/e2_traffic_canary/
?? outputs/e2_traffic_profile_s1/
?? outputs/e2_traffic_profiles/
?? outputs/e2_traffic_public_target_canary/
?? outputs/e2_traffic_real_runner_canary/
?? outputs/e2_traffic_runner_consistency/
?? outputs/e2_true_stratum/
?? outputs/plans/E2_FORMAL_RUNTIME_AND_STORAGE_ESTIMATE.json
?? outputs/plans/E2_FORMAL_RUNTIME_AND_STORAGE_ESTIMATE.md
?? outputs/sag_g1/archive_rerun_20260829-122556/
?? outputs/sag_g1_r1/
?? outputs/sag_g1_r1b/
?? outputs/sag_g1_r1c/
?? outputs/sag_g1_r1d/
?? outputs/sag_g1_r1e/
?? outputs/traffic_mapping/
?? outputs/traffic_public_target/
?? paper_ready_r1/
?? paper_ready_r2/
?? paper_tmc_r1/
?? post_review/B_intermittent_protocol_R/
?? post_review/C11_repro/
?? post_review/C1_kill_cityscanner/C1_KILL_REPORT.md
?? post_review/C1_kill_cityscanner/EVENTTRACE_REPORT.md
?? post_review/C1_kill_cityscanner/GENERATE_EVENTTRACE_INSTRUCTION.md
?? post_review/C1_kill_cityscanner/RANKING_INSTRUCTION.md
?? post_review/C1_kill_tdrive_spatial/X1_EXECUTION_STEPS.md
?? post_review/C1_tdrive_rank/C6_OVERLEAF_PACKAGE.md
?? post_review/C1_tdrive_rank/PAPER_INGEST_WRITING_INSTRUCTION.md
?? post_review/C1_tdrive_rank/PAPER_INGEST_WRITING_REPORT.md
?? post_review/C2_scd_phi/
?? post_review/C4_manifest_hash/
?? post_review/C6_page_compress/
?? post_review/C7_floss/
?? post_review/FEDAU_WINDOW_SPEC/
?? post_review/G0_MANIFEST.md
?? post_review/G1_path_b_gated_default/
?? post_review/G1_propensity_design/
?? post_review/G1_support_compatible/
?? post_review/G2_external_baselines/
?? post_review/G3_mobility_replay/
?? post_review/G4_practical_estimator/
?? post_review/G5_solver_significance/
?? post_review/GPT_C2_atomic_target/
?? post_review/JOINT_MEASURED_OU_RANK/
?? post_review/P0_ni_artifact/
?? post_review/P1_claim_ceiling/
?? post_review/P2_new_target/
?? post_review/PATH_A_HAJEK/
?? post_review/WRITING_PASS.md
?? results_action_difference_revision_20261013/
?? results_active_set_repair/
?? results_aggregate_total/
?? results_c1_cityscanner/round_v1/C1_KILL_AUDIT.json
?? results_c1_cityscanner/round_v1/C1_KILL_REPORT.md
?? results_c1_cityscanner/round_v1/CS_PHI_DECISION.json
?? results_c1_cityscanner/round_v1/CS_TRACE_MANIFEST.json
?? results_c1_cityscanner/round_v1/CS_TRAIN_LEDGER.json
?? results_c1_cityscanner/round_v1/CS_TRAIN_SETUP.json
?? results_c1_cityscanner/round_v1/EXECUTION_LOG.md
?? results_c1_cityscanner/round_v1/GO.json
?? results_c1_cityscanner/round_v1/runs/
?? results_c1_cityscanner/round_v1/tables/
?? results_c1_kill/
?? results_calibration_diagnostic_20261013_122013/
?? results_calibration_first_20261013/
?? results_ceiling_class_r1/
?? results_cityscanner_full_vs_projection_20261018/
?? results_cityscanner_lowcost_screen/
?? results_conditional_bundle_b0_20261012_223821/
?? results_design_gate_alignment_v1/
?? results_endpoint_screen/
?? results_estimand_selection/
?? results_evidence_axis/
?? results_exogenous_target/
?? results_gate_dose/
?? results_gatekeeping/
?? results_group_identity/
?? results_h_headroom/
?? results_h_response_shift/
?? results_int_r/
?? results_joint_ou/
?? results_m1_attribution/
?? results_main_rebuild_r1/
?? results_new_block_traffic/
?? results_nodesign_supplement/
?? results_observed_feedback_acquisition_45011_20261014/
?? results_observed_feedback_autonomous_pilot_45001_20261014/
?? results_observed_feedback_autonomous_pilot_45001_recovery_20261015/
?? results_observed_feedback_continuation_45011_20261014/
?? results_observed_feedback_implementation_20261013/
?? results_observed_feedback_persistent_cost_20261014/
?? results_observed_feedback_preparation_20261013/
?? results_observed_feedback_readiness_20261014/
?? results_observed_feedback_rolling_45011_20261014_s1/
?? results_observed_feedback_rolling_45011_20261014_s2/
?? results_of_v1_small_scope_20261018_190539/
?? results_oracle_root_cause/
?? results_p2_new_target/
?? results_paper_ceiling/
?? results_path_a_hajek/
?? results_prop3_audit/
?? results_re_interval_development_44001_20261013/
?? results_reachability_detector_v1/
?? results_reachability_method_prep_20261012_220855/
?? results_reachability_v2_p0_20261012_215621/
?? results_regime_b_endpoints/
?? results_revision_feasibility_20261013_125348/
?? results_sag_g1/
?? results_seed_path_audit_r1/
?? results_server_optimizer/
?? results_support_consumption/round_v1/CONFIRMATION_DATA_STATUS.md
?? results_support_consumption/round_v1/DATA_USAGE_LEDGER.csv
?? results_support_consumption/round_v1/FAILURE_REPORT_P1.md
?? results_support_consumption/round_v1/FAILURE_REPORT_P2_INVALID_IMPLEMENTATION_previous.md
?? results_support_consumption/round_v1/METHOD_SPEC.md
?? results_support_consumption/round_v1/P0_ASSET_AUDIT.md
?? results_support_consumption/round_v1/P1_DECISION.md
?? results_support_consumption/round_v1/P1_EVENT_LEDGER.parquet
?? results_support_consumption/round_v1/P1_STATUS.json
?? results_support_consumption/round_v1/P1_SUMMARY.csv
?? results_support_consumption/round_v1/P1_WINDOW_METRICS.csv
?? results_support_consumption/round_v1/P2.RUNNING.json
?? results_support_consumption/round_v1/P2_CRITICAL_TESTS.json
?? results_support_consumption/round_v1/P2_STATUS_INVALID_IMPLEMENTATION_previous.json
?? results_support_consumption/round_v1/PROTOCOL_FREEZE.json
?? results_support_consumption/round_v1/SOURCE_INDEX.md
?? results_table2_audit/
?? results_tdrive_rank/round_v1/EXECUTION_LOG.md
?? results_tdrive_rank/round_v1/SMOKE_HEARTBEAT.txt
?? results_tdrive_rank/round_v1/TRAIN_DETACHED.log
?? results_tdrive_rank/round_v1/WATCHDOG_STDOUT.log
?? results_tdrive_rank/round_v1/_mux.py
?? results_tdrive_rank/round_v1/resume_train_watchdog.sh
?? results_tdrive_rank/round_v1/runs/tdrive_speed/fedau_window/seed30001/checkpoints/
?? results_tdrive_rank/round_v1/runs/tdrive_speed/fedau_window/seed30002/checkpoints/
?? results_tdrive_rank/round_v1/runs/tdrive_speed/fedau_window/seed30003/checkpoints/
?? results_tdrive_rank/round_v1/runs/tdrive_speed/fedau_window/seed30004/checkpoints/
?? results_tdrive_rank/round_v1/runs/tdrive_speed/fedau_window/seed30005/checkpoints/
?? results_tdrive_rank/round_v1/runs/tdrive_speed/fedau_window/seed30006/checkpoints/
?? results_tdrive_rank/round_v1/runs/tdrive_speed/fedau_window/seed30007/checkpoints/
?? results_tdrive_rank/round_v1/runs/tdrive_speed/fedau_window/seed30008/checkpoints/
?? results_tdrive_rank/round_v1/runs/tdrive_speed/fedau_window/seed30009/checkpoints/
?? results_tdrive_rank/round_v1/runs/tdrive_speed/fedau_window/seed30010/checkpoints/
?? results_tdrive_rank/round_v1/runs/tdrive_speed/fedavg_window/seed30001/TD_R_TRAIN_TRACEBACK.txt
?? results_tdrive_rank/round_v1/runs/tdrive_speed/fedavg_window/seed30001/checkpoints/
?? results_tdrive_rank/round_v1/runs/tdrive_speed/fedavg_window/seed30002/checkpoints/
?? results_tdrive_rank/round_v1/runs/tdrive_speed/fedavg_window/seed30003/checkpoints/
?? results_tdrive_rank/round_v1/runs/tdrive_speed/fedavg_window/seed30004/checkpoints/
?? results_tdrive_rank/round_v1/runs/tdrive_speed/fedavg_window/seed30005/checkpoints/
?? results_tdrive_rank/round_v1/runs/tdrive_speed/fedavg_window/seed30006/checkpoints/
?? results_tdrive_rank/round_v1/runs/tdrive_speed/fedavg_window/seed30007/checkpoints/
?? results_tdrive_rank/round_v1/runs/tdrive_speed/fedavg_window/seed30008/checkpoints/
?? results_tdrive_rank/round_v1/runs/tdrive_speed/fedavg_window/seed30009/checkpoints/
?? results_tdrive_rank/round_v1/runs/tdrive_speed/fedavg_window/seed30010/checkpoints/
?? results_tdrive_rank/round_v1/runs/tdrive_speed/obsuse_window/seed30001/checkpoints/
?? results_tdrive_rank/round_v1/runs/tdrive_speed/obsuse_window/seed30002/checkpoints/
?? results_tdrive_rank/round_v1/runs/tdrive_speed/obsuse_window/seed30003/checkpoints/
?? results_tdrive_rank/round_v1/runs/tdrive_speed/obsuse_window/seed30004/checkpoints/
?? results_tdrive_rank/round_v1/runs/tdrive_speed/obsuse_window/seed30005/checkpoints/
?? results_tdrive_rank/round_v1/runs/tdrive_speed/obsuse_window/seed30006/checkpoints/
?? results_tdrive_rank/round_v1/runs/tdrive_speed/obsuse_window/seed30007/checkpoints/
?? results_tdrive_rank/round_v1/runs/tdrive_speed/obsuse_window/seed30008/checkpoints/
?? results_tdrive_rank/round_v1/runs/tdrive_speed/obsuse_window/seed30009/checkpoints/
?? results_tdrive_rank/round_v1/runs/tdrive_speed/obsuse_window/seed30010/checkpoints/
?? results_tdrive_rank/round_v1/runs/tdrive_speed/raven/seed30001/checkpoints/
?? results_tdrive_rank/round_v1/runs/tdrive_speed/raven/seed30002/checkpoints/
?? results_tdrive_rank/round_v1/runs/tdrive_speed/raven/seed30003/checkpoints/
?? results_tdrive_rank/round_v1/runs/tdrive_speed/raven/seed30004/checkpoints/
?? results_tdrive_rank/round_v1/runs/tdrive_speed/raven/seed30005/checkpoints/
?? results_tdrive_rank/round_v1/runs/tdrive_speed/raven/seed30006/checkpoints/
?? results_tdrive_rank/round_v1/runs/tdrive_speed/raven/seed30007/checkpoints/
?? results_tdrive_rank/round_v1/runs/tdrive_speed/raven/seed30008/checkpoints/
?? results_tdrive_rank/round_v1/runs/tdrive_speed/raven/seed30009/checkpoints/
?? results_tdrive_rank/round_v1/runs/tdrive_speed/raven/seed30010/checkpoints/
?? results_tdrive_rank/round_v1/runs/tdrive_speed/raven_wo_design/seed30001/checkpoints/
?? results_tdrive_rank/round_v1/runs/tdrive_speed/raven_wo_design/seed30002/checkpoints/
?? results_tdrive_rank/round_v1/runs/tdrive_speed/raven_wo_design/seed30003/checkpoints/
?? results_tdrive_rank/round_v1/runs/tdrive_speed/raven_wo_design/seed30004/checkpoints/
?? results_tdrive_rank/round_v1/runs/tdrive_speed/raven_wo_design/seed30005/checkpoints/
?? results_tdrive_rank/round_v1/runs/tdrive_speed/raven_wo_design/seed30006/checkpoints/
?? results_tdrive_rank/round_v1/runs/tdrive_speed/raven_wo_design/seed30007/checkpoints/
?? results_tdrive_rank/round_v1/runs/tdrive_speed/raven_wo_design/seed30008/TD_R_TRAIN_TRACEBACK.txt
?? results_tdrive_rank/round_v1/runs/tdrive_speed/raven_wo_design/seed30008/checkpoints/
?? results_tdrive_rank/round_v1/runs/tdrive_speed/raven_wo_design/seed30009/checkpoints/
?? results_tdrive_rank/round_v1/runs/tdrive_speed/raven_wo_design/seed30010/checkpoints/
?? results_tdrive_rank/round_v1/runs/tdrive_speed/twostage_hajek/seed30001/checkpoints/
?? results_tdrive_rank/round_v1/runs/tdrive_speed/twostage_hajek/seed30002/checkpoints/
?? results_tdrive_rank/round_v1/runs/tdrive_speed/twostage_hajek/seed30003/checkpoints/
?? results_tdrive_rank/round_v1/runs/tdrive_speed/twostage_hajek/seed30004/checkpoints/
?? results_tdrive_rank/round_v1/runs/tdrive_speed/twostage_hajek/seed30005/checkpoints/
?? results_tdrive_rank/round_v1/runs/tdrive_speed/twostage_hajek/seed30006/checkpoints/
?? results_tdrive_rank/round_v1/runs/tdrive_speed/twostage_hajek/seed30007/checkpoints/
?? results_tdrive_rank/round_v1/runs/tdrive_speed/twostage_hajek/seed30008/checkpoints/
?? results_tdrive_rank/round_v1/runs/tdrive_speed/twostage_hajek/seed30009/checkpoints/
?? results_tdrive_rank/round_v1/runs/tdrive_speed/twostage_hajek/seed30010/checkpoints/
?? results_tdrive_rank/round_v1/smoke_pid.txt
?? results_tdrive_rank/round_v1/smoke_stderr.log
?? results_tdrive_rank/round_v1/smoke_stderr.prev_leak.log
?? results_tdrive_rank/round_v1/smoke_stderr.prev_oom.log
?? results_tdrive_rank/round_v1/smoke_stderr.prev_oppdiag.log
?? results_tdrive_rank/round_v1/smoke_stdout.log
?? results_tdrive_rank/round_v1/smoke_stdout.prev_leak.log
?? results_tdrive_rank/round_v1/smoke_stdout.prev_oom.log
?? results_tdrive_rank/round_v1/smoke_stdout.prev_oppdiag.log
?? results_tdrive_rank/round_v1_laptop_canary/
?? results_text_repairs/
?? results_traffic_e1/
?? results_traffic_e2/
?? results_traffic_struct/
?? results_two_constant/
?? results_w1_ladder/
?? results_xw_pool/
?? scripts/_e2ee_unpacked_specialized.py
?? scripts/_e2sr_unpacked_specialized.py
?? scripts/_extract_schedule_from_transcript.py
?? scripts/_probe_h1_fix.py
?? scripts/_run_e2bc_ledger_sequence.py
?? scripts/_run_e2bd_ledger_sequence.py
?? scripts/_run_e2dr_ledger_sequence.py
?? scripts/_run_e2ee_ledger_sequence.py
?? scripts/_run_e2gw_ledger_sequence.py
?? scripts/_run_e2hv_ledger_sequence.py
?? scripts/_run_e2lb_ledger_sequence.py
?? scripts/_run_e2pf_ledger_sequence.py
?? scripts/_run_e2pt_ledger_sequence.py
?? scripts/_run_e2rc_ledger_sequence.py
?? scripts/_run_e2rr_ledger_sequence.py
?? scripts/_run_e2s1_ledger_sequence.py
?? scripts/_run_e2sr_ledger_sequence.py
?? scripts/_run_e2tr_ledger_sequence.py
?? scripts/_scan_empirical_gates.py
?? scripts/_scan_stage2_gates.py
?? scripts/_verify_e2ee_prepare_artifacts.py
?? scripts/_verify_e2sr_prepare.py
?? scripts/_verify_e2tn_prepare.py
?? scripts/action_difference_revision_budget.py
?? scripts/analyze_e3_formal_runs.py
?? scripts/analyze_e4_ablation_semantic_integrity_repair.py
?? scripts/analyze_e4_core_mechanism_ablation.py
?? scripts/archive_observed_feedback_pilot_legacy.py
?? scripts/audit_calibration_first.py
?? scripts/audit_deployment_consequence.py
?? scripts/audit_observed_feedback_persistent_cost.py
?? scripts/audit_observed_feedback_preparation.py
?? scripts/audit_observed_feedback_seed45011.py
?? scripts/audit_re_interval_development.py
?? scripts/audit_seed45011_metadata_fast.py
?? scripts/audit_seed45011_targeted.py
?? scripts/audit_table2_uair_fedavg.py
?? scripts/audit_worst_group_rmse.py
?? scripts/build_e3_v2_protocol.py
?? scripts/build_observed_feedback_package.py
?? scripts/build_observed_feedback_recovery_entry.py
?? scripts/build_observed_feedback_recovery_validation.py
?? scripts/c1_analysis.py
?? scripts/c1_deletion_driver.py
?? scripts/c1_registration.py
?? scripts/calibration_budget.py
?? scripts/check_action_difference_candidate.py
?? scripts/check_calibration_diagnostic_delivery.py
?? scripts/check_coordinated_checkpoint.py
?? scripts/check_design_gate_configuration.py
?? scripts/check_e2_balanced_dgp_single_trace_compact_evidence.py
?? scripts/check_e2_balanced_dgp_single_trace_gates.py
?? scripts/check_e2_balanced_hard_variance_compact_evidence.py
?? scripts/check_e2_balanced_hard_variance_gates.py
?? scripts/check_e2_data_horizon_spatial_recovery_compact_evidence.py
?? scripts/check_e2_data_horizon_spatial_recovery_gates.py
?? scripts/check_e2_empirical_eventtrace_gates.py
?? scripts/check_e2_global_window_finite_gate_compact_evidence.py
?? scripts/check_e2_global_window_finite_gate_gates.py
?? scripts/check_e2_legal_horizon_balanced_gates.py
?? scripts/check_e2_legal_horizon_compact_evidence.py
?? scripts/check_e2_stage2_stratum_gates.py
?? scripts/check_e2_traffic_balanced_canary_compact_evidence.py
?? scripts/check_e2_traffic_balanced_canary_gates.py
?? scripts/check_e2_traffic_formal_results_analysis_gates.py
?? scripts/check_e2_traffic_mapping_readiness_compact_evidence.py
?? scripts/check_e2_traffic_mapping_readiness_gates.py
?? scripts/check_e2_traffic_numerical_tolerance_and_final_claim_seal_gates.py
?? scripts/check_e2_traffic_offline_metric_reconstruction_and_claim_correction_gates.py
?? scripts/check_e2_traffic_profile_runner_consistency_compact_evidence.py
?? scripts/check_e2_traffic_profile_runner_consistency_gates.py
?? scripts/check_e2_traffic_profile_s1_final_freeze_compact_evidence.py
?? scripts/check_e2_traffic_profile_s1_final_freeze_gates.py
?? scripts/check_e2_traffic_public_target_qseal_compact_evidence.py
?? scripts/check_e2_traffic_public_target_qseal_gates.py
?? scripts/check_e2_traffic_real_runner_canary_compact_evidence.py
?? scripts/check_e2_traffic_real_runner_canary_gates.py
?? scripts/check_e2_traffic_s1_s6_profile_freeze_compact_evidence.py
?? scripts/check_e2_traffic_s1_s6_profile_freeze_gates.py
?? scripts/check_e2_true_stratum_compact_evidence.py
?? scripts/check_e2_true_stratum_gates.py
?? scripts/check_e3_delta_cs_atomic_rho_final_hotfix_gates.py
?? scripts/check_e3_final_evidence_provenance_and_wording_seal_gates.py
?? scripts/check_e3_formal_evidence_integrity_and_claim_closure_gates.py
?? scripts/check_e3_formal_execution_integrity_gates.py
?? scripts/check_e3_local_hajek_weight_and_p2_certificate_final_closure_gates.py
?? scripts/check_e3_multidataset_protocol_closure_gates.py
?? scripts/check_e3_multidataset_real_runner_canary_gates.py
?? scripts/check_e3_numerical_integrity_clean_canary_gates.py
?? scripts/check_e3_pair_rho_production_consumption_hotfix_gates.py
?? scripts/check_e3_protocol_reuse_and_readiness_gates.py
?? scripts/check_e3_real_runner_pair_oracle_correctness_closure_gates.py
?? scripts/check_e3_semantic_alignment_and_runner_integration_closure_gates.py
?? scripts/check_e3_stratum_identity_and_traffic_reuse_seal_gates.py
?? scripts/check_e3_target_pair_metric_final_integration_closure_gates.py
?? scripts/check_e4_ablation_semantic_integrity_repair_gates.py
?? scripts/check_e4_core_mechanism_ablation_gates.py
?? scripts/check_e4_wo_inst_reference_penalty_final_correction_gates.py
?? scripts/check_first_prefix_planner.py
?? scripts/check_observed_feedback_arithmetic.py
?? scripts/check_observed_feedback_autonomous_sgd0.py
?? scripts/check_observed_feedback_cold_large_pool.py
?? scripts/check_observed_feedback_diagnostic_sgd0.py
?? scripts/check_observed_feedback_driver_sgd0.py
?? scripts/check_observed_feedback_interrupted_prefix.py
?? scripts/check_observed_feedback_persistent_cost.py
?? scripts/check_observed_feedback_recovery_facility.py
?? scripts/check_observed_feedback_root_publication.py
?? scripts/check_pair_identity_addendum.py
?? scripts/check_paper_data_clean_and_package_r1.py
?? scripts/check_re_interval_development_entry.py
?? scripts/check_root_admission_contract.py
?? scripts/compare_observed_feedback_autonomous_pilot.py
?? scripts/compare_observed_feedback_recovery_pilot.py
?? scripts/compare_observed_feedback_recovery_pilot_v2.py
?? scripts/complete_seed45011_current_identity.py
?? scripts/compute_cityscanner_phi.py
?? scripts/compute_joint_ou_cs_p2_phi.py
?? scripts/compute_path_a_no2_phi.py
?? scripts/compute_scd_phi.py
?? scripts/coordinated_windows_cpu_meter.py
?? scripts/deliver_observed_feedback_incomplete_pilot.py
?? scripts/diagnose_calibration_d0.py
?? scripts/diagnose_calibration_support.py
?? scripts/diagnose_re_interval_clock.py
?? scripts/diagnostic_bounded.py
?? scripts/diagnostic_legacy_meter_repro.py
?? scripts/diagnostic_meter_check.py
?? scripts/diagnostic_meter_workload.py
?? scripts/estimand_gate_round2.py
?? scripts/estimand_selection.py
?? scripts/exogenous_target_cityscanner.py
?? scripts/exogenous_target_endpoints.py
?? scripts/export_e2_balanced_dgp_single_trace_evidence.py
?? scripts/export_e2_balanced_hard_variance_evidence.py
?? scripts/export_e2_data_horizon_spatial_recovery_evidence.py
?? scripts/export_e2_empirical_eventtrace_evidence.py
?? scripts/export_e2_global_window_finite_gate_evidence.py
?? scripts/export_e2_legal_horizon_balanced_evidence.py
?? scripts/export_e2_stage2_stratum_evidence.py
?? scripts/export_e2_traffic_balanced_canary_evidence.py
?? scripts/export_e2_traffic_formal_results_analysis_evidence.py
?? scripts/export_e2_traffic_mapping_readiness_evidence.py
?? scripts/export_e2_traffic_numerical_tolerance_and_final_claim_seal_evidence.py
?? scripts/export_e2_traffic_offline_metric_reconstruction_evidence.py
?? scripts/export_e2_traffic_profile_runner_consistency_evidence.py
?? scripts/export_e2_traffic_profile_s1_final_freeze_evidence.py
?? scripts/export_e2_traffic_public_target_qseal_evidence.py
?? scripts/export_e2_traffic_real_runner_canary_evidence.py
?? scripts/export_e2_traffic_real_runner_ledger_closure_evidence.py
?? scripts/export_e2_traffic_s1_s6_profile_freeze_evidence.py
?? scripts/export_e2_true_stratum_nonwrap_evidence.py
?? scripts/export_e3_delta_cs_atomic_rho_final_hotfix_evidence.py
?? scripts/export_e3_final_evidence_provenance_and_wording_seal_evidence.py
?? scripts/export_e3_formal_evidence_integrity_and_claim_closure_evidence.py
?? scripts/export_e3_formal_runs_evidence.py
?? scripts/export_e3_local_hajek_weight_and_p2_certificate_final_closure_evidence.py
?? scripts/export_e3_multidataset_protocol_closure_evidence.py
?? scripts/export_e3_multidataset_real_runner_canary_evidence.py
?? scripts/export_e3_numerical_integrity_clean_canary_evidence.py
?? scripts/export_e3_pair_rho_production_consumption_hotfix_evidence.py
?? scripts/export_e3_protocol_reuse_and_readiness_evidence.py
?? scripts/export_e3_real_runner_pair_oracle_correctness_closure_evidence.py
?? scripts/export_e3_semantic_alignment_and_runner_integration_closure_evidence.py
?? scripts/export_e3_stratum_identity_and_traffic_reuse_seal_evidence.py
?? scripts/export_e3_target_pair_metric_final_integration_closure_evidence.py
?? scripts/export_e4_ablation_semantic_integrity_repair.py
?? scripts/export_e4_core_mechanism_ablation_evidence.py
?? scripts/export_paper_data_clean_and_package_r1.py
?? scripts/extract_rolling45011_evidence.py
?? scripts/finalize_action_difference_delivery.py
?? scripts/finalize_calibration_diagnostic.py
?? scripts/finalize_e3_formal_runs.py
?? scripts/finalize_e3_multidataset_real_runner_canary.py
?? scripts/finalize_e3_numerical_integrity_clean_canary.py
?? scripts/finalize_e4_ablation_semantic_integrity_repair.py
?? scripts/finalize_e4_core_mechanism_ablation.py
?? scripts/finalize_e4_wo_inst_reference_penalty_final_correction.py
?? scripts/finalize_observed_feedback_45011_continuation.py
?? scripts/finalize_observed_feedback_acquisition_stopped.py
?? scripts/finalize_observed_feedback_implementation.py
?? scripts/finalize_observed_feedback_readiness.py
?? scripts/finalize_re_interval_revision.py
?? scripts/freeze_e3_formal_source.py
?? scripts/freeze_e3_numerical_integrity_source.py
?? scripts/freeze_e4_formal_source.py
?? scripts/gate_dose.py
?? scripts/generate_e3_drifting_traces.py
?? scripts/generate_observed_feedback_pilot_driver.py
?? scripts/generate_observed_feedback_pilot_verifier.py
?? scripts/group_identity_check.py
?? scripts/h_fedavg_restore.py
?? scripts/h_response_shift.py
?? scripts/ingest_joint_ou_cs_p2.py
?? scripts/ingest_path_a_no2.py
?? scripts/new_block_traffic.py
?? scripts/new_block_traffic_stages.py
?? scripts/normalize_e4_ablation_semantic_integrity_repair_artifacts.py
?? scripts/observed_feedback_acquisition_budget.py
?? scripts/observed_feedback_continuation_budget.py
?? scripts/observed_feedback_fixed2_restore.py
?? scripts/observed_feedback_implementation_budget.py
?? scripts/observed_feedback_persistent_cost_budget.py
?? scripts/observed_feedback_persistent_worker.py
?? scripts/observed_feedback_pilot_account.py
?? scripts/observed_feedback_pilot_budget.py
?? scripts/observed_feedback_pilot_common.py
?? scripts/observed_feedback_preparation_budget.py
?? scripts/observed_feedback_readiness_budget.py
?? scripts/observed_feedback_recovery_account.py
?? scripts/observed_feedback_recovery_budget.py
?? scripts/observed_feedback_recovery_common.py
?? scripts/observed_feedback_recovery_io.py
?? scripts/observed_feedback_recovery_meter.py
?? scripts/observed_feedback_recovery_publisher.py
?? scripts/observed_feedback_rolling_budget.py
?? scripts/observed_feedback_rolling_budget_s2.py
?? scripts/observed_feedback_rolling_costs.py
?? scripts/observed_feedback_root_publisher.py
?? scripts/package_sag_g1_r1_submission.py
?? scripts/package_sag_g1_r1b_submission.py
?? scripts/package_sag_g1_r1c_submission.py
?? scripts/package_sag_g1_r1d_submission.py
?? scripts/package_sag_g1_r1f_submission.py
?? scripts/package_sag_g1_r1g_submission.py
?? scripts/package_sag_g1_r1h_submission.py
?? scripts/package_sag_g1_r1i_submission.py
?? scripts/package_sag_g1_r1j_submission.py
?? scripts/package_sag_g1_r1k_submission.py
?? scripts/package_sag_g1_r1l_submission.py
?? scripts/package_sag_g1_r1l_v11_submission.py
?? scripts/package_sag_g1_r1l_v12_submission.py
?? scripts/package_sag_g1_r1l_v13_submission.py
?? scripts/package_sag_g1_r1m_submission.py
?? scripts/precheck_e3_numerical_integrity_clean_canary.py
?? scripts/prepare_coordinated_meter.py
?? scripts/prepare_e2_balanced_dgp_and_single_trace_certification.py
?? scripts/prepare_e2_balanced_hard_variance_and_certification.py
?? scripts/prepare_e2_data_horizon_and_spatial_recovery.py
?? scripts/prepare_e2_empirical_eventtrace_and_profile_refreeze.py
?? scripts/prepare_e2_global_window_and_finite_sample_gate.py
?? scripts/prepare_e2_legal_horizon_and_balanced_calibration.py
?? scripts/prepare_e2_stage2_eligibility_and_true_stratum_refreeze.py
?? scripts/prepare_e2_traffic_balanced_design_canary.py
?? scripts/prepare_e2_traffic_formal_results_analysis.py
?? scripts/prepare_e2_traffic_mapping_and_readiness.py
?? scripts/prepare_e2_traffic_numerical_tolerance_and_final_claim_seal.py
?? scripts/prepare_e2_traffic_offline_metric_reconstruction.py
?? scripts/prepare_e2_traffic_profile_runner_consistency_hotfix.py
?? scripts/prepare_e2_traffic_profile_s1_final_freeze.py
?? scripts/prepare_e2_traffic_public_target_and_qseal.py
?? scripts/prepare_e2_traffic_real_runner_canary.py
?? scripts/prepare_e2_traffic_s1_s6_profile_freeze.py
?? scripts/prepare_e2_true_stratum_and_nonwrap_schedule_repair.py
?? scripts/prepare_e3_delta_cs_atomic_rho_final_hotfix.py
?? scripts/prepare_e3_final_evidence_provenance_and_wording_seal.py
?? scripts/prepare_e3_formal_evidence_integrity_and_claim_closure.py
?? scripts/prepare_e3_formal_runs.py
?? scripts/prepare_e3_local_hajek_weight_and_p2_certificate_final_closure.py
?? scripts/prepare_e3_multidataset_protocol_closure.py
?? scripts/prepare_e3_multidataset_real_runner_canary.py
?? scripts/prepare_e3_numerical_integrity_clean_canary.py
?? scripts/prepare_e3_pair_rho_production_consumption_hotfix.py
?? scripts/prepare_e3_protocol_reuse_and_readiness.py
?? scripts/prepare_e3_real_runner_pair_oracle_correctness_closure.py
?? scripts/prepare_e3_semantic_alignment_and_runner_integration_closure.py
?? scripts/prepare_e3_stratum_identity_and_traffic_reuse_seal.py
?? scripts/prepare_e3_target_pair_metric_final_integration_closure.py
?? scripts/prepare_e4_ablation_semantic_integrity_repair.py
?? scripts/prepare_e4_core_mechanism_ablation.py
?? scripts/prepare_e4_wo_inst_reference_penalty_final_correction.py
?? scripts/prepare_interval_revision_package.py
?? scripts/prepare_observed_feedback_cold_input.py
?? scripts/prepare_observed_feedback_fixed2_resume.py
?? scripts/prepare_observed_feedback_pilot.py
?? scripts/prepare_observed_feedback_pilot_resume.py
?? scripts/prepare_observed_feedback_recovery.py
?? scripts/prepare_observed_feedback_rolling_s2.py
?? scripts/prepare_paper_data_clean_and_package_r1.py
?? scripts/re_interval_development_budget.py
?? scripts/reconcile_first_budget.py
?? scripts/refine_e3_final_evidence_provenance_and_wording_seal_narratives.py
?? scripts/render_observed_feedback_pilot_reports.py
?? scripts/render_observed_feedback_recovery_reports.py
?? scripts/render_observed_feedback_rolling_reports.py
?? scripts/restore_re_interval_development_state.py
?? scripts/resume_calibration_first.py
?? scripts/resume_observed_feedback_45011.py
?? scripts/resume_observed_feedback_45011_s2.py
?? scripts/resume_observed_feedback_autonomous_pilot.py
?? scripts/resume_re_interval_development.py
?? scripts/review_action_difference_failure.py
?? scripts/review_first_seed_audit.py
?? scripts/revision_feasibility_budget.py
?? scripts/revision_feasibility_s2.py
?? scripts/run_active_set_repair.py
?? scripts/run_c1_cityscanner.py
?? scripts/run_calibration_first.py
?? scripts/run_corrective_e4_ablation_semantic_integrity_repair.py
?? scripts/run_e3_drifting.py
?? scripts/run_e3_f1.py
?? scripts/run_e3_fedau_window.py
?? scripts/run_e3_formal_runs.py
?? scripts/run_e3_formal_stages_remaining.py
?? scripts/run_e3_multidataset_real_runner_canary.py
?? scripts/run_e3_numerical_integrity_clean_canary.py
?? scripts/run_e3_obsuse_window.py
?? scripts/run_e4_formal_ablations.py
?? scripts/run_e4_smoke.py
?? scripts/run_final_corrective_e4_wo_inst_reference_penalty.py
?? scripts/run_h_headroom.py
?? scripts/run_int_r_v1.py
?? scripts/run_int_r_v2.py
?? scripts/run_joint_ou_cs_p2.py
?? scripts/run_nodesign_supplement.py
?? scripts/run_observed_feedback_45011.py
?? scripts/run_observed_feedback_autonomous_pilot.py
?? scripts/run_observed_feedback_fixed2_resume.py
?? scripts/run_observed_feedback_pilot_recovery.py
?? scripts/run_p2_nt_e3.py
?? scripts/run_path_a_no2.py
?? scripts/run_re_interval_development.py
?? scripts/run_smoke_e4_ablation_semantic_integrity_repair.py
?? scripts/seal_e3_formal_raw_results.py
?? scripts/seal_e4_ablation_semantic_integrity_repair.py
?? scripts/seal_e4_raw_results.py
?? scripts/summarize_calibration_first.py
?? scripts/summarize_e3_drifting.py
?? scripts/summarize_e3_fedau_window.py
?? scripts/summarize_e3_obsuse_window.py
?? scripts/summarize_re_interval_development.py
?? scripts/validate_conditional_bundle_b0.py
?? scripts/validate_e2_claim_matrix.py
?? scripts/validate_e2_claim_matrix_final.py
?? scripts/validate_observed_feedback_four_paths.py
?? scripts/validate_re_interval_revision.py
?? scripts/verify_and_summarize_rolling45011.py
?? scripts/verify_observed_feedback_45011_prefix.py
?? scripts/verify_observed_feedback_autonomous_arm.py
?? scripts/verify_observed_feedback_preparation.py
?? scripts/verify_observed_feedback_recovery_arm.py
?? scripts/verify_observed_feedback_recovery_arm_v2.py
?? scripts/verify_re_interval_clock_repair.py
?? scripts/w1_cs_norm_diag.py
?? scripts/w1_debt_eta_infer.py
?? scripts/w1_debt_rule_diag.py
?? scripts/w1_ladder.py
?? scripts/w1_phase5.py
?? scripts/w1_replay.py
?? scripts/w1_v3_debt.py
?? scripts/w1_v3_explore.py
?? scripts/w1_v3_gunits.py
?? scripts/w1_v3_myopic.py
?? scripts/w1_v3_ruler.py
?? scripts/w1_v3_source.py
?? scripts/w1_v3_source_post.py
?? scripts/w1_v4_check.py
?? scripts/w1_v4_fullseed.py
?? scripts/w1_v4_proj.py
?? scripts/w1_v4_train.py
?? scripts/w1_v51_a2.py
?? scripts/w1_v51_a3.py
?? scripts/w1_v51_dbg_as.py
?? scripts/w1_v51_dbg_as10.py
?? scripts/w1_v51_dbg_as11.py
?? scripts/w1_v51_dbg_as12.py
?? scripts/w1_v51_dbg_as13.py
?? scripts/w1_v51_dbg_as14.py
?? scripts/w1_v51_dbg_as2.py
?? scripts/w1_v51_dbg_as3.py
?? scripts/w1_v51_dbg_as4.py
?? scripts/w1_v51_dbg_as5.py
?? scripts/w1_v51_dbg_as6.py
?? scripts/w1_v51_dbg_as7.py
?? scripts/w1_v51_dbg_as8.py
?? scripts/w1_v51_dbg_as9.py
?? scripts/w1_v51_dbg_bad.py
?? scripts/w1_v51_dbg_ball.py
?? scripts/w1_v51_dbg_ball2.py
?? scripts/w1_v51_dbg_ball3.py
?? scripts/w1_v51_dbg_compare.py
?? scripts/w1_v51_dbg_cross.py
?? scripts/w1_v51_dbg_inputs.py
?? scripts/w1_v51_dbg_kinds.py
?? scripts/w1_v51_dbg_proj.py
?? scripts/w1_v51_dbg_proj2.py
?? scripts/w1_v51_dbg_proj3.py
?? scripts/w1_v51_dbg_proj4.py
?? scripts/w1_v51_dbg_proj5.py
?? scripts/w1_v51_dbg_qp.py
?? scripts/w1_v51_dbg_qp2.py
?? scripts/w1_v51_dbg_qp3.py
?? scripts/w1_v51_dbg_qp4.py
?? scripts/w1_v51_dbg_slsqp.py
?? scripts/w1_v51_dbg_tau.py
?? scripts/w1_v51_dbg_tau2.py
?? scripts/w1_v51_dbg_tau3.py
?? scripts/w1_v51_dbg_tau4.py
?? scripts/w1_v51_dbg_tau5.py
?? scripts/w1_v51_dbg_tau6.py
?? scripts/w1_v51_dbg_win.py
?? scripts/w1_v51_dbg_win2.py
?? scripts/w1_v51_dbg_win3.py
?? scripts/w1_v51_dbg_win4.py
?? scripts/w1_v51_dbg_win5.py
?? scripts/w1_v51_dbg_win6.py
?? scripts/w1_v51_frozen_rows.py
?? scripts/w1_v51_gates.py
?? scripts/w1_v51_oracle.py
?? scripts/w1_v51_recon.py
?? scripts/w1_v51_refactor.py
?? scripts/w1_v51_refactor2.py
?? scripts/w1_v51_refactor3.py
?? scripts/w1_v51_refactor4.py
?? scripts/w1_v51_refactor5.py
?? scripts/w1_v51_refactor6.py
?? scripts/w1_v51_refactor7.py
?? scripts/w1_v51_refactor8.py
?? scripts/w1_v51_struct.py
?? scripts/w1_v51_uniform_rows.py
?? scripts/w1_v51a_capchoice.py
?? scripts/w1_v51a_cmp.py
?? scripts/w1_v51a_cmp2.py
?? scripts/w1_v51a_dbg.py
?? scripts/w1_v51a_dbg2.py
?? scripts/w1_v51a_evidence.py
?? scripts/w1_v51a_gates.py
?? scripts/w1_v51a_oracle.py
?? scripts/w1_v51a_probe.py
?? scripts/w1_v51a_run.py
?? scripts/w1_v51a_scan.py
?? scripts/w1_v5_a1.py
?? scripts/w1_v5_a2.py
?? scripts/w1_v5_a3.py
?? scripts/w1_v5_a3_robust.py
?? scripts/w1_v5_probe_gself.py
?? scripts/w1_v5_recon.py
?? scripts/w1_v5_xref_legacy.py
?? scripts/windows_cpu_meter.py
?? snapshots/
?? src/e3_v2_context.py
?? src/e3_v2_eventtrace.py
?? src/e3_v2_protocol.py
?? src/raven_mcs/control/
?? src/raven_mcs/correction/stage1.py
?? src/raven_mcs/data/cityscanner_eventtrace.py
?? src/raven_mcs/data/cityscanner_p2_measured_o.py
?? src/raven_mcs/data/cityscanner_p2_measured_o_eventtrace.py
?? src/raven_mcs/data/cityscanner_p2_measured_o_no2.py
?? src/raven_mcs/data/cityscanner_p2_measured_o_no2_eventtrace.py
?? src/raven_mcs/e2/balanced_dgp/
?? src/raven_mcs/e2/empirical/
?? src/raven_mcs/e2/global_window/
?? src/raven_mcs/e2/hard_variance/
?? src/raven_mcs/e2/legal_horizon/
?? src/raven_mcs/e2/stage2/
?? src/raven_mcs/e2/traffic_balanced_canary/
?? src/raven_mcs/e2/traffic_final_seal/
?? src/raven_mcs/e2/traffic_formal_analysis/
?? src/raven_mcs/e2/traffic_mapping/
?? src/raven_mcs/e2/traffic_offline_recon/
?? src/raven_mcs/e2/traffic_profiles/
?? src/raven_mcs/e2/traffic_public_target/
?? src/raven_mcs/e2/true_stratum/
?? src/raven_mcs/e3/
?? src/raven_mcs/e4/
?? src/raven_mcs/experiments/calibration_first.py
?? src/raven_mcs/experiments/conditional_bundle.py
?? src/raven_mcs/experiments/legacy_coverage_freeze.py
?? src/raven_mcs/experiments/r1m_method_freeze.py
?? src/raven_mcs/experiments/run_sag_g1_r1.py
?? src/raven_mcs/experiments/run_sag_g1_r1b.py
?? src/raven_mcs/experiments/run_sag_g1_r1c.py
?? src/raven_mcs/experiments/run_sag_g1_r1d.py
?? src/raven_mcs/experiments/run_sag_g1_r1e.py
?? src/raven_mcs/experiments/run_sag_g1_r1f.py
?? src/raven_mcs/experiments/run_sag_g1_r1g.py
?? src/raven_mcs/experiments/run_sag_g1_r1h.py
?? src/raven_mcs/experiments/run_sag_g1_r1i.py
?? src/raven_mcs/experiments/run_sag_g1_r1j.py
?? src/raven_mcs/experiments/run_sag_g1_r1k.py
?? src/raven_mcs/experiments/run_sag_g1_r1l.py
?? src/raven_mcs/experiments/run_sag_g1_r1l_v11.py
?? src/raven_mcs/experiments/run_sag_g1_r1l_v12.py
?? src/raven_mcs/experiments/run_sag_g1_r1l_v13.py
?? src/raven_mcs/experiments/run_sag_g1_r1m.py
?? src/raven_mcs/final_figure_table_paper_specification_seal_r1/
?? src/raven_mcs/final_paper_data_asset_freeze_r1/
?? src/raven_mcs/final_table_ii_unit_scale_repair_r1/
?? src/raven_mcs/manuscript_evidence_closure_r1/
?? src/raven_mcs/paper_data_r1/
?? src/raven_mcs/paper_data_r2/
?? src/raven_mcs/sag/aggregate_certificate.py
?? src/raven_mcs/sag/availability_stress.py
?? src/raven_mcs/sag/cfm1.py
?? src/raven_mcs/sag/deployment_groups.py
?? src/raven_mcs/sag/dynamic_cov.py
?? src/raven_mcs/sag/e3v1_root_cause.py
?? src/raven_mcs/sag/evidence.py
?? src/raven_mcs/sag/oracle_ceiling.py
?? src/raven_mcs/sag/oracle_stress_builder.py
?? src/raven_mcs/sag/r1j_calibration.py
?? src/raven_mcs/sag/r1j_eval.py
?? src/raven_mcs/sag/r1j_features.py
?? src/raven_mcs/sag/r1j_predictor.py
?? src/raven_mcs/sag/r1j_spec.py
?? src/raven_mcs/sag/r1k_aggregate.py
?? src/raven_mcs/sag/r1k_barrier.py
?? src/raven_mcs/sag/r1k_eval.py
?? src/raven_mcs/sag/r1k_scale.py
?? src/raven_mcs/sag/r1k_spec.py
?? src/raven_mcs/sag/r1l_block.py
?? src/raven_mcs/sag/r1l_conformal.py
?? src/raven_mcs/sag/r1l_design.py
?? src/raven_mcs/sag/r1l_spec.py
?? src/raven_mcs/sag/r1l_state.py
?? src/raven_mcs/sag/r1l_theory.py
?? src/raven_mcs/sag/r1m_eval.py
?? src/raven_mcs/sag/r1m_features.py
?? src/raven_mcs/sag/r1m_predictor.py
?? src/raven_mcs/sag/r1m_reset.py
?? src/raven_mcs/sag/r1m_spec.py
?? src/raven_mcs/sag/r1m_track.py
?? src/raven_mcs/sag/stress_gate_builder.py
?? src/raven_mcs/sag/stress_mask.py
?? src/raven_mcs/sag/stress_summary.py
?? src/raven_mcs/sag/target_law.py
?? src/raven_mcs/sag/window_completeness.py
?? src/raven_mcs/sag/window_context.py
?? src/raven_mcs/tdrive_protocol_seal_r1/
?? src/raven_mcs/training/cache_identity.py
?? src/raven_mcs/training/dynamic_control.py
?? src/raven_mcs_execution/
?? src/raven_mcs_observed_feedback/
?? src/raven_mcs_re_interval/
?? tdrive_protocol_seal_r1/
?? tests/control_b0/
?? tests/integration/test_configured_design_runner.py
?? tests/integration/test_e2_balanced_dgp_single_trace_stop.py
?? tests/integration/test_e2_balanced_hard_variance_stop.py
?? tests/integration/test_e2_data_horizon_spatial_recovery_stop.py
?? tests/integration/test_e2_empirical_eventtrace_integration.py
?? tests/integration/test_e2_global_window_finite_gate_stop.py
?? tests/integration/test_e2_stage2_stratum_integration.py
?? tests/integration/test_e2_traffic_balanced_canary_stop.py
?? tests/integration/test_e2_traffic_mapping_readiness_stop.py
?? tests/integration/test_e2_traffic_profile_runner_consistency_stop.py
?? tests/integration/test_e2_traffic_profile_s1_final_freeze_stop.py
?? tests/integration/test_e2_traffic_public_target_qseal_stop.py
?? tests/integration/test_e2_traffic_real_runner_canary_stop.py
?? tests/integration/test_e2_traffic_s1_s6_profile_freeze_stop.py
?? tests/integration/test_e2_true_stratum_nonwrap_integration.py
?? tests/integration/test_e3_formal_runs_stop.py
?? tests/integration/test_e3_multidataset_real_runner_canary_stop.py
?? tests/integration/test_e3_numerical_integrity_clean_canary_stop.py
?? tests/integration/test_e3_real_runner_integration.py
?? tests/integration/test_e3_semantic_runner_integration.py
?? tests/integration/test_e3_target_pair_metric_final_integration.py
?? tests/test_e2_legal_horizon_balanced_calibration.py
?? tests/unit/test_BM_predictability.py
?? tests/unit/test_Btot_decomposition.py
?? tests/unit/test_a100_handled_separately.py
?? tests/unit/test_a1_reproduces_natural.py
?? tests/unit/test_abstract_has_no_old_dataset_gate_claim.py
?? tests/unit/test_aggregate_certificate_outputs_gate_t.py
?? tests/unit/test_aggregate_delta_unchanged.py
?? tests/unit/test_aggregate_feature_causal.py
?? tests/unit/test_aggregate_gate_threshold_unchanged.py
?? tests/unit/test_aggregate_lcb_formula.py
?? tests/unit/test_aggregate_no_current_mask.py
?? tests/unit/test_aggregate_no_current_oracle.py
?? tests/unit/test_aggregate_no_future_calibration.py
?? tests/unit/test_aggregate_same_a_calibration.py
?? tests/unit/test_aggregate_validity_builder.py
?? tests/unit/test_aggregate_warmup_min8.py
?? tests/unit/test_alpha_unchanged.py
?? tests/unit/test_availability_corollary_designated_entity.py
?? tests/unit/test_availability_corollary_no_atleast_one_overclaim.py
?? tests/unit/test_availability_entity_level.py
?? tests/unit/test_availability_mask_deterministic.py
?? tests/unit/test_availability_mask_nested.py
?? tests/unit/test_availability_mask_outcome_independent.py
?? tests/unit/test_availability_upper_bound.py
?? tests/unit/test_boundary_near_rule_frozen.py
?? tests/unit/test_boundary_near_rule_unchanged.py
?? tests/unit/test_boundary_rich_rule_frozen.py
?? tests/unit/test_c_cov_builder.py
?? tests/unit/test_c_cov_formula.py
?? tests/unit/test_c_cov_no_current_R_leakage.py
?? tests/unit/test_c_cov_semantics.py
?? tests/unit/test_c_cov_target_mass.py
?? tests/unit/test_c_cov_target_mass_weighted.py
?? tests/unit/test_c_lcb_clip_zero.py
?? tests/unit/test_calibration_buffer_cleared_after_reset.py
?? tests/unit/test_calibration_same_a.py
?? tests/unit/test_calibration_same_block.py
?? tests/unit/test_calibration_same_dataset.py
?? tests/unit/test_calibration_spec_frozen.py
?? tests/unit/test_certificate_coverage_domain.py
?? tests/unit/test_certificate_router_source_in_snapshot.py
?? tests/unit/test_certificate_width.py
?? tests/unit/test_certificates_source_in_snapshot.py
?? tests/unit/test_certified_above_tau_design_on.py
?? tests/unit/test_certified_below_tau_design_off.py
?? tests/unit/test_certified_does_not_imply_exchangeability.py
?? tests/unit/test_certified_requires_nmin.py
?? tests/unit/test_cf0_matches_e3v1.py
?? tests/unit/test_cf1_fixed_definition.py
?? tests/unit/test_cf2_fixed_definition.py
?? tests/unit/test_cfm1_budget_matching.py
?? tests/unit/test_cfm1_cf0_unchanged.py
?? tests/unit/test_cfm1_deficit_logged.py
?? tests/unit/test_cfm1_no_cross_time_fill.py
?? tests/unit/test_cfm1_no_replacement_padding.py
?? tests/unit/test_cfm1_rule_frozen_before_run.py
?? tests/unit/test_cfm1_same_pi_safe.py
?? tests/unit/test_cfm1_same_seed_semantics.py
?? tests/unit/test_cfm1_same_target_law.py
?? tests/unit/test_cfm1_same_tau_cov.py
?? tests/unit/test_cli_default_raven_mcs.py
?? tests/unit/test_completeness_rule_frozen_before_oracle_join.py
?? tests/unit/test_completeness_rule_outcome_blind.py
?? tests/unit/test_compute_certificates_routes_aggregate_mode.py
?? tests/unit/test_conclusion_has_no_old_dataset_gate_claim.py
?? tests/unit/test_configured_design_configuration.py
?? tests/unit/test_counterfactual_metrics_independent.py
?? tests/unit/test_current_mask_cannot_control_design.py
?? tests/unit/test_current_window_not_in_own_calibration.py
?? tests/unit/test_current_window_not_in_own_q.py
?? tests/unit/test_dataset_name_cannot_control_design.py
?? tests/unit/test_delta_unchanged.py
?? tests/unit/test_design_equals_gate.py
?? tests/unit/test_design_t_controls_window_close.py
?? tests/unit/test_design_t_equals_gate_t.py
?? tests/unit/test_dynamic_cov_history_only.py
?? tests/unit/test_dynamic_cov_joint_coverage_metric.py
?? tests/unit/test_dynamic_cov_monotonic_history.py
?? tests/unit/test_dynamic_cov_no_current_window.py
?? tests/unit/test_dynamic_cov_window_block_calibration.py
?? tests/unit/test_e2_balanced_dgp_single_trace_core.py
?? tests/unit/test_e2_balanced_hard_variance_core.py
?? tests/unit/test_e2_data_horizon_spatial_recovery_core.py
?? tests/unit/test_e2_empirical_eventtrace_core.py
?? tests/unit/test_e2_global_window_finite_gate_core.py
?? tests/unit/test_e2_stage2_stratum_core.py
?? tests/unit/test_e2_traffic_balanced_canary_core.py
?? tests/unit/test_e2_traffic_formal_results_analysis_core.py
?? tests/unit/test_e2_traffic_mapping_readiness_core.py
?? tests/unit/test_e2_traffic_profile_runner_consistency_core.py
?? tests/unit/test_e2_traffic_profile_s1_final_freeze_core.py
?? tests/unit/test_e2_traffic_public_target_qseal_core.py
?? tests/unit/test_e2_traffic_real_runner_canary_core.py
?? tests/unit/test_e2_traffic_s1_s6_profile_freeze_core.py
?? tests/unit/test_e2_true_stratum_nonwrap_core.py
?? tests/unit/test_e3_delta_cs_atomic_rho_final_hotfix_core.py
?? tests/unit/test_e3_evidence_integrity_claim_closure_core.py
?? tests/unit/test_e3_final_evidence_provenance_and_wording_seal_core.py
?? tests/unit/test_e3_formal_runs_core.py
?? tests/unit/test_e3_local_hajek_weight_and_p2_final_closure_core.py
?? tests/unit/test_e3_multidataset_protocol_closure_core.py
?? tests/unit/test_e3_multidataset_real_runner_canary_core.py
?? tests/unit/test_e3_numerical_integrity_core.py
?? tests/unit/test_e3_numerical_integrity_finite.py
?? tests/unit/test_e3_pair_rho_production_consumption_hotfix_core.py
?? tests/unit/test_e3_protocol_reuse_and_readiness_core.py
?? tests/unit/test_e3_real_runner_pair_oracle_correctness_core.py
?? tests/unit/test_e3_semantic_alignment_core.py
?? tests/unit/test_e3_stratum_identity_and_traffic_reuse_seal_core.py
?? tests/unit/test_e3_target_pair_metric_final_integration_core.py
?? tests/unit/test_e3v1_cooccurrence_metric.py
?? tests/unit/test_e3v1_eventtrace_unchanged.py
?? tests/unit/test_e3v1_generation_dag_complete.py
?? tests/unit/test_e3v1_sampling_distortion_metric.py
?? tests/unit/test_e3v1_source_snapshot_complete.py
?? tests/unit/test_e3v1_temporal_continuity_metric.py
?? tests/unit/test_e3v2_eventtrace_has_real_timestamp.py
?? tests/unit/test_e3v2_eventtrace_hash_reproducible.py
?? tests/unit/test_e3v2_no_current_window_leakage.py
?? tests/unit/test_e3v2_pi_safe_unchanged.py
?? tests/unit/test_e3v2_population_rule_frozen.py
?? tests/unit/test_e3v2_public_context_whitelist.py
?? tests/unit/test_e3v2_source_snapshot_complete.py
?? tests/unit/test_e3v2_target_law_unchanged.py
?? tests/unit/test_e3v2_tau_cov_unchanged.py
?? tests/unit/test_e3v2_window_rule_frozen.py
?? tests/unit/test_e4_ablation_semantic_integrity_repair.py
?? tests/unit/test_e4_ablation_switch_regression.py
?? tests/unit/test_e4_wo_inst_reference_penalty_final_correction.py
?? tests/unit/test_event_count_lcb_no_current_window.py
?? tests/unit/test_event_count_mass.py
?? tests/unit/test_evidence_paths_exist_in_package.py
?? tests/unit/test_false_safe_definition.py
?? tests/unit/test_false_unsafe_definition.py
?? tests/unit/test_feature_spec_fixed.py
?? tests/unit/test_feature_whitelist.py
?? tests/unit/test_fedau_window_aggregator.py
?? tests/unit/test_finite_sample_quantile.py
?? tests/unit/test_forbidden_claims_listed.py
?? tests/unit/test_formal_cov_le_oracle_safe_when_joint_valid.py
?? tests/unit/test_formal_execution_chain_complete.py
?? tests/unit/test_formal_gate_is_aggregate.py
?? tests/unit/test_formal_policy_unique.py
?? tests/unit/test_formal_runner_no_static_gate_lookup.py
?? tests/unit/test_full_stress_grid_exact.py
?? tests/unit/test_g4_practical_estimator_lemmas.py
?? tests/unit/test_gate_from_CLCB_only.py
?? tests/unit/test_gate_t_controls_design_t.py
?? tests/unit/test_gate_t_is_unique_design_authority.py
?? tests/unit/test_gate_threshold_unchanged.py
?? tests/unit/test_gate_to_design_provenance_schema.py
?? tests/unit/test_gate_uses_lcb_only.py
?? tests/unit/test_group_mapping_consistency.py
?? tests/unit/test_group_mapping_frozen.py
?? tests/unit/test_int_r_occupancy.py
?? tests/unit/test_interior_diagnostic_does_not_overwrite_main.py
?? tests/unit/test_intro_has_no_old_dataset_gate_claim.py
?? tests/unit/test_joint_validity_builder.py
?? tests/unit/test_kn_not_clipped.py
?? tests/unit/test_lcb_monotonicity.py
?? tests/unit/test_lcb_sample_size_behavior.py
?? tests/unit/test_legacy_gate_absent_from_formal_path.py
?? tests/unit/test_legacy_raven_cannot_be_paper_default.py
?? tests/unit/test_legacy_raven_isolated.py
?? tests/unit/test_lookback_fixed.py
?? tests/unit/test_lower_bound_formula.py
?? tests/unit/test_mu_pi_same_target_law.py
?? tests/unit/test_n_lt_19_warmup_off.py
?? tests/unit/test_n_min_is_19.py
?? tests/unit/test_natural_track_unchanged.py
?? tests/unit/test_no_adaptive_stress_level_added.py
?? tests/unit/test_no_alias_cycle.py
?? tests/unit/test_no_calibration_repair.py
?? tests/unit/test_no_calibration_retuning_after_results.py
?? tests/unit/test_no_calibration_run.py
?? tests/unit/test_no_clip_conformal.py
?? tests/unit/test_no_counterfactual_sweep.py
?? tests/unit/test_no_current_ROU_leakage.py
?? tests/unit/test_no_current_mask_leakage.py
?? tests/unit/test_no_dataset_gate_override.py
?? tests/unit/test_no_dynamic_cov_run.py
?? tests/unit/test_no_e3_modification.py
?? tests/unit/test_no_five_seed_started.py
?? tests/unit/test_no_future_calibration.py
?? tests/unit/test_no_future_score.py
?? tests/unit/test_no_mass_mapping_model_zoo.py
?? tests/unit/test_no_model_zoo.py
?? tests/unit/test_no_new_experiment_run.py
?? tests/unit/test_no_oracle_current_gate_leakage.py
?? tests/unit/test_no_pair_targeted_deletion.py
?? tests/unit/test_no_posthoc_predictor_tuning.py
?? tests/unit/test_no_posthoc_reset_tuning.py
?? tests/unit/test_no_predictor_repair.py
?? tests/unit/test_no_predictor_retuning_after_results.py
?? tests/unit/test_no_predictor_run.py
?? tests/unit/test_no_proof_sketch.py
?? tests/unit/test_no_raven_mcs_to_raven_legacy_resolution.py
?? tests/unit/test_no_sag_started.py
?? tests/unit/test_no_sampling_causal_claim_without_match.py
?? tests/unit/test_no_static_gate_override.py
?? tests/unit/test_no_stress_created.py
?? tests/unit/test_no_stress_level_added.py
?? tests/unit/test_no_tau_tuning.py
?? tests/unit/test_no_theory_file_modified.py
?? tests/unit/test_obsuse_window_aggregator.py
?? tests/unit/test_opportunity_event_mass.py
?? tests/unit/test_optional_drift_omitted.py
?? tests/unit/test_oracle_cannot_control_current_design.py
?? tests/unit/test_oracle_labels_not_used_in_training.py
?? tests/unit/test_oracle_pass_rate.py
?? tests/unit/test_oracle_real_support_definition.py
?? tests/unit/test_oracle_safe_definition.py
?? tests/unit/test_oracle_safe_le_real_support.py
?? tests/unit/test_oracle_stress_monotonicity.py
?? tests/unit/test_pairwise_barrier_derivation.py
?? tests/unit/test_pairwise_history_unchanged.py
?? tests/unit/test_pairwise_retired_from_core.py
?? tests/unit/test_paper_data_clean_and_package_r1.py
?? tests/unit/test_paper_method_has_single_canonical_resolution.py
?? tests/unit/test_pi_safe_config.py
?? tests/unit/test_pi_safe_rule_frozen.py
?? tests/unit/test_pi_safe_unchanged.py
?? tests/unit/test_pi_target_support_compatible.py
?? tests/unit/test_positive_lcb_impossible_when_zero_prob_gt_delta.py
?? tests/unit/test_predictor_refit_only_after_reset.py
?? tests/unit/test_predictor_snapshot_frozen_within_block.py
?? tests/unit/test_predictor_spec_frozen.py
?? tests/unit/test_primary_sensor_a040_present.py
?? tests/unit/test_prop1_proof_complete.py
?? tests/unit/test_prop2_proof_complete.py
?? tests/unit/test_r1e_c_cov_formula_unchanged.py
?? tests/unit/test_r1e_coverage_metric_same_as_r1d.py
?? tests/unit/test_r1e_global_max_residual_window_unit.py
?? tests/unit/test_r1e_no_5seed_execution.py
?? tests/unit/test_r1e_no_sag_execution.py
?? tests/unit/test_r1e_no_threshold_tuning.py
?? tests/unit/test_r1e_nonvacuity_attribution_identity.py
?? tests/unit/test_r1e_pi_safe_no_outcome_selection.py
?? tests/unit/test_r1e_pi_safe_rule_q10_frozen.py
?? tests/unit/test_r1e_r1d_artifacts_immutable.py
?? tests/unit/test_r1e_real_support_is_diagnostic_only.py
?? tests/unit/test_r1e_stage1_stop_rules.py
?? tests/unit/test_r1e_stage2_context_quantile_prior_only.py
?? tests/unit/test_r1e_stage2_fallback_global_when_context_short.py
?? tests/unit/test_r1e_stage2_no_q_manual_shrink.py
?? tests/unit/test_r1e_stage2_trigger_requires_calibration_bottleneck.py
?? tests/unit/test_r1e_target_rule_hash_unchanged.py
?? tests/unit/test_r1e_thresholds_unchanged.py
?? tests/unit/test_r1e_tod_context_not_from_current_event_presence.py
?? tests/unit/test_r1e_tod_context_pre_window_only.py
?? tests/unit/test_r1e_tod_predictor_dataset_name_forbidden.py
?? tests/unit/test_r1e_tod_predictor_global_fallback.py
?? tests/unit/test_r1e_tod_predictor_no_current_window.py
?? tests/unit/test_r1e_tod_predictor_same_block_selection.py
?? tests/unit/test_r1e_tod_predictor_strictly_prior.py
?? tests/unit/test_r1e_zero_certified_mass_not_nan.py
?? tests/unit/test_r1e_zero_mass_included_in_mean.py
?? tests/unit/test_r1f_e3_trace_hash_frozen.py
?? tests/unit/test_r1f_gate_artifact_derived.py
?? tests/unit/test_r1f_no_hardcoded_verdict.py
?? tests/unit/test_r1f_pi_safe_frozen.py
?? tests/unit/test_r1f_target_law_frozen.py
?? tests/unit/test_r1f_tau_cov_frozen.py
?? tests/unit/test_r1g_gate_artifact_derived.py
?? tests/unit/test_r1g_no_hardcoded_verdict.py
?? tests/unit/test_r1h_gate_artifact_derived.py
?? tests/unit/test_r1h_input_hashes_frozen.py
?? tests/unit/test_r1h_no_hardcoded_verdict.py
?? tests/unit/test_r1i_gate_artifact_derived.py
?? tests/unit/test_r1i_input_freeze.py
?? tests/unit/test_r1i_oracle_unchanged.py
?? tests/unit/test_r1i_verdict_not_hardcoded.py
?? tests/unit/test_r1j_gate_artifact_derived.py
?? tests/unit/test_r1j_input_freeze.py
?? tests/unit/test_r1j_mask_unchanged.py
?? tests/unit/test_r1j_oracle_groundtruth_unchanged.py
?? tests/unit/test_r1j_stress_grid_unchanged.py
?? tests/unit/test_r1j_verdict_not_hardcoded.py
?? tests/unit/test_r1k_gate_artifact_derived.py
?? tests/unit/test_r1k_input_freeze.py
?? tests/unit/test_r1k_verdict_not_hardcoded.py
?? tests/unit/test_r1l_gate_artifact_derived.py
?? tests/unit/test_r1l_input_freeze.py
?? tests/unit/test_r1l_no_experiment_run.py
?? tests/unit/test_r1l_v11_k_orderstat_valid.py
?? tests/unit/test_r1l_v11_randomized_rank_ties.py
?? tests/unit/test_r1l_v11_ties_proof_event_direction.py
?? tests/unit/test_r1l_v12_mock_gate_design_cases.py
?? tests/unit/test_r1l_v13_mock_raven_mcs_cases.py
?? tests/unit/test_r1l_verdict_not_hardcoded.py
?? tests/unit/test_r1m_alpha_unchanged.py
?? tests/unit/test_r1m_frozen_theory_constants.py
?? tests/unit/test_r1m_gate_artifact_derived.py
?? tests/unit/test_r1m_method_freeze_uses_raven_mcs.py
?? tests/unit/test_r1m_method_list_uses_raven_mcs.py
?? tests/unit/test_r1m_nmin_19.py
?? tests/unit/test_r1m_no_legacy_gate_bypass.py
?? tests/unit/test_r1m_raven_mcs_formal_alias.py
?? tests/unit/test_r1m_restart_defined.py
?? tests/unit/test_r1m_tau_unchanged.py
?? tests/unit/test_r1m_verdict_not_hardcoded.py
?? tests/unit/test_raven_mcs_formal_alias_matches_raven_mcs.py
?? tests/unit/test_raven_mcs_formal_alias_same_policy.py
?? tests/unit/test_raven_mcs_not_always_on.py
?? tests/unit/test_raven_mcs_not_legacy.py
?? tests/unit/test_raven_mcs_not_legacy_static_gate.py
?? tests/unit/test_raven_mcs_resolves_to_aggregate_coverage.py
?? tests/unit/test_raven_mcs_resolves_to_formal_policy.py
?? tests/unit/test_raw_timestamp_retention.py
?? tests/unit/test_reset_clears_buffer.py
?? tests/unit/test_reset_design_off.py
?? tests/unit/test_reset_gate_off.py
?? tests/unit/test_reset_not_retroactive.py
?? tests/unit/test_reset_refits_new_snapshot.py
?? tests/unit/test_reset_restarts_warmup.py
?? tests/unit/test_reset_trigger_after_completed_miscoverage.py
?? tests/unit/test_ridge_alpha_fixed.py
?? tests/unit/test_root_cause_verdict_not_hardcoded.py
?? tests/unit/test_same_a_stratum_only.py
?? tests/unit/test_scale_history_causal.py
?? tests/unit/test_scale_mapping_conditional_positive.py
?? tests/unit/test_scale_mapping_old.py
?? tests/unit/test_secondary_uair_a020_present.py
?? tests/unit/test_section_vii_marked_pre_r1m.py
?? tests/unit/test_section_vii_remains_pre_r1m_legacy.py
?? tests/unit/test_sensor_a040_audit_complete.py
?? tests/unit/test_sensor_scope_ceiling_recomputed.py
?? tests/unit/test_source_snapshot_contains_window_close.py
?? tests/unit/test_source_snapshot_contains_window_runner.py
?? tests/unit/test_stress_levels_exact.py
?? tests/unit/test_stress_levels_frozen.py
?? tests/unit/test_stress_track_separate.py
?? tests/unit/test_stress_unchanged.py
?? tests/unit/test_target_compatibility.py
?? tests/unit/test_target_law_rule_frozen.py
?? tests/unit/test_target_law_unchanged.py
?? tests/unit/test_target_no_outcome_selection.py
?? tests/unit/test_target_no_test_outcome_leakage.py
?? tests/unit/test_target_opportunity_mismatch_metric.py
?? tests/unit/test_tau_cov_unchanged.py
?? tests/unit/test_tau_unchanged.py
?? tests/unit/test_theorem1_proof_complete.py
?? tests/unit/test_theorem_conditional_on_assumption_A.py
?? tests/unit/test_theory_tex_sealed.py
?? tests/unit/test_threshold_gap_decomposition_identity.py
?? tests/unit/test_thresholds_unchanged.py
?? tests/unit/test_transitive_source_closure.py
?? tests/unit/test_uair_a020_audit_complete.py
?? tests/unit/test_uair_ceiling_recomputed.py
?? tests/unit/test_uair_not_hardcoded_unsafe.py
?? tests/unit/test_uair_unsafe_windows_all_audited.py
?? tests/unit/test_warmup8_not_nominal_95.py
?? tests/unit/test_warmup_design_off.py
?? tests/unit/test_warmup_gate_off.py
?? tests/unit/test_warmup_min8.py
?? tests/unit/test_window_boundary_status.py
?? tests/unit/test_window_close_no_dataset_level_design_flag.py
?? tests/unit/test_window_close_receives_gate_t.py
?? tests/unit/test_window_runner_calls_compute_certificates.py
?? tmp/
?? tools/
```
