#!/usr/bin/env python3
"""S1' server-optimizer re-screen driver.

Instruction: ccfa-review-reports/raven-mcs-s1prime-server-optimizer-execution-prompt.md
User-confirmed amendments (2026-10-07):
  A1  G0 is a TRUE IDENTITY TEST: the subclass with the optimizer set to plain SGD at
      eta_s = eta must reproduce, bit-exact, an UNMODIFIED FullWindowRunner re-run in the
      current tree.  Comparison against the frozen artifacts is a disclosed diagnostic,
      not a gate (P0_REPORT.md section 5 documents a 4.20e-7 RMSE_mu miss for `raven`
      caused by artifact vintage, unrelated to this override).
  A2  G0 is NOT gated on NSW-Traffic: the E3 traffic tree has no fedavg_window and no
      raven arm (only central_all, central_delivered, debt_cal, inst_cal, local_hajek,
      raven_simoracle).  The E2 complete_aligned contract is recorded as disclosure only.
  A3  Stage C evaluates MDE80 at n = 5 per section 2; n = 15 is left to a separately
      authorized confirmatory run.

Injection: `build_full_runner` resolves `FullWindowRunner` as a module global, so rebinding
`raven_mcs.training.window_runner.FullWindowRunner` installs the subclass with NO src/ edit.

No src/, manuscript, artifacts/ or other results_* writes.  No EventTrace is created.
"""
from __future__ import annotations

import argparse
import copy
import csv
import hashlib
import json
import math
import pathlib
import shutil
import sys
import time
from datetime import datetime, timezone

import numpy as np
import pandas as pd

ROOT = pathlib.Path(__file__).resolve().parents[3]
sys.path.insert(0, str(ROOT / "src"))

OUT = ROOT / "results_traffic_e2" / "round_v1"
RUNS = OUT / "runs"
E3_TRACES = ROOT / "artifacts/e3_formal_runs_r1/eventtraces"

INSTRUCTION = ROOT / "ccfa-review-reports/raven-mcs-s1prime-server-optimizer-execution-prompt.md"
SCREEN_SEEDS = [30001, 30002, 30003, 30004, 30005]
GATE_SEED = 30001
ETA_GLOBAL_DEFAULT = 0.01
LOCAL_STEPS = 2

BLOCKS = ("sensorscope", "uair", "traffic")
G0_BLOCKS = ("sensorscope", "uair")          # amendment A2
STAGE_A_ETA_S = (1e-3, 3e-3, 1e-2)
BETA1, BETA2, TAU = 0.9, 0.99, 1e-3

# The E3 protocol-closure reuse guard refuses `traffic + complete_aligned + formal seed +
# {fedavg_window, ..., raven}`.  Ledger Part IX item 65 records a user-authorized, default-off
# opt-in (`allow_reused_traffic_rerun`) that must be passed explicitly by the caller and is written
# into that run's own ledger `source_identity`.  It is passed ONLY for the traffic block, so the
# SensorScope and U-Air runs never carry a misleading exemption flag.
TRAFFIC_REUSE_EXEMPTION = True


def dump_json(obj, p: pathlib.Path) -> None:
    p.parent.mkdir(parents=True, exist_ok=True)
    p.write_text(json.dumps(obj, indent=2, sort_keys=True, default=str) + "\n", encoding="utf-8")


def now() -> str:
    return datetime.now(timezone.utc).isoformat()


def _git_commit() -> str | None:
    try:
        import subprocess
        out = subprocess.run(["git", "rev-parse", "HEAD"], cwd=str(ROOT), capture_output=True,
                             text=True, timeout=20)
        return out.stdout.strip() or None
    except Exception:
        return None


def sha256_file(p: pathlib.Path) -> str:
    h = hashlib.sha256()
    with p.open("rb") as f:
        for chunk in iter(lambda: f.read(1 << 20), b""):
            h.update(chunk)
    return h.hexdigest()


# --------------------------------------------------------------------- the subclass
import raven_mcs.training.window_runner as _wr  # noqa: E402
from raven_mcs.training.client import _flatten_params as flatten_params  # noqa: E402
from raven_mcs.training.client import unflatten_params  # noqa: E402

_Base = _wr.FullWindowRunner


class ServerOptWindowRunner(_Base):
    """Identical to FullWindowRunner except that the server step is replaced.

    With SERVER_OPT["mode"] == "off" every method is the base implementation.
    """

    SERVER_OPT: dict = {"mode": "off", "eta_s": None, "beta1": BETA1, "beta2": BETA2, "tau": TAU}
    DIAG: list = []

    def _process_window(self, window_id, events):
        cfg = type(self).SERVER_OPT
        mode = cfg.get("mode", "off")
        if mode == "off":
            return super()._process_window(window_id, events)

        theta_old = flatten_params(self.theta)
        wm = super()._process_window(window_id, events)   # base SGD step, writes theta_sgd
        theta_sgd = flatten_params(self.theta)

        if not bool(getattr(wm, "active", False)):
            # No server update on an inactive window: nothing for the optimizer to consume,
            # and the step counter must not advance.
            type(self).DIAG.append({"window_id": int(window_id), "active": False, "applied": False})
            return wm

        eta = float(self.eta)
        if abs(eta - ETA_GLOBAL_DEFAULT) > 1e-15:
            raise RuntimeError(f"expected global eta {ETA_GLOBAL_DEFAULT}, got {eta}")
        g_r = (theta_old - theta_sgd) / eta

        if mode == "sgd":
            # Identity: eta_s == eta and plain SGD reproduce theta_sgd exactly.
            theta_new = theta_sgd
            diag = {"m_norm": float("nan"), "v_norm": float("nan"), "t": 0}
        elif mode == "adam":
            if getattr(self, "_so_state", None) is None:
                self._so_state = {
                    "m": np.zeros_like(g_r), "v": np.zeros_like(g_r), "t": 0,
                }
            st = self._so_state
            st["t"] += 1
            b1, b2, tau = float(cfg["beta1"]), float(cfg["beta2"]), float(cfg["tau"])
            st["m"] = b1 * st["m"] + (1.0 - b1) * g_r
            st["v"] = b2 * st["v"] + (1.0 - b2) * g_r * g_r
            m_hat = st["m"] / (1.0 - b1 ** st["t"])
            v_hat = st["v"] / (1.0 - b2 ** st["t"])
            theta_new = theta_old - float(cfg["eta_s"]) * m_hat / (np.sqrt(v_hat) + tau)
            diag = {"m_norm": float(np.linalg.norm(st["m"])), "v_norm": float(np.linalg.norm(st["v"])),
                    "t": int(st["t"])}
        else:
            raise ValueError(f"unknown server-optimizer mode {mode!r}")

        if not np.all(np.isfinite(theta_new)):
            raise FloatingPointError(f"non-finite theta after server optimizer at window {window_id}")

        self.theta = unflatten_params(theta_new, self.theta)
        self.model.load_state_dict(self.theta)
        self.model_versions[self.clock.model_version] = copy.deepcopy(self.theta)
        rec = {
            "window_id": int(window_id),
            "active": True,
            "applied": True,
            "g_norm": float(np.linalg.norm(g_r)),
            "sgd_move_norm": float(np.linalg.norm(theta_sgd - theta_old)),
            "opt_move_norm": float(np.linalg.norm(theta_new - theta_old)),
        }
        rec.update(diag)
        type(self).DIAG.append(rec)
        return wm


def install(mode: str, eta_s=None) -> None:
    ServerOptWindowRunner.SERVER_OPT = {
        "mode": mode, "eta_s": eta_s, "beta1": BETA1, "beta2": BETA2, "tau": TAU,
    }
    ServerOptWindowRunner.DIAG = []
    _wr.FullWindowRunner = ServerOptWindowRunner


def uninstall() -> None:
    _wr.FullWindowRunner = _Base


# --------------------------------------------------------------------- run harness
def trace_dir(block: str, seed: int) -> pathlib.Path:
    return E3_TRACES / block / ("seed%d" % seed) / "training_eventtrace"


TARGET_ARTIFACT = None  # set by the TE2 round script; None = production target


def run_complete(d: pathlib.Path) -> bool:
    """A cell counts as done only when both of its terminal artifacts exist.

    `run_e3_real` can refuse before writing anything (the reuse guard raises before its own mkdir), and
    a directory left behind by such a refusal must never be mistaken for a completed run.
    """
    return (d / "final_metrics.json").is_file() and (d / "checkpoints" / "final.pt").is_file()


def run_one(block: str, arm: str, seed: int, local_steps: int, tag: str, mode: str,
            eta_s=None, force: bool = False) -> pathlib.Path:
    from raven_mcs.e3.canary.dataset_load import load_paper_dataset, load_spatial_to_client
    from raven_mcs.e3.real_runner.runner import run_e3_real

    d = RUNS / tag / block / arm / ("seed%d" % seed)
    if d.exists():
        if run_complete(d) and not force:
            print(f"  [skip] {d.relative_to(ROOT)} (complete)")
            return d
        print(f"  [redo] {d.relative_to(ROOT)} "
              f"({'forced' if force else 'incomplete cell'})", flush=True)
        shutil.rmtree(d)
    d.mkdir(parents=True)

    install(mode, eta_s)
    try:
        t0 = time.perf_counter()
        run_e3_real(
            root=ROOT,
            run_dir=d,
            dataset=load_paper_dataset(ROOT, block),
            method=arm,
            seed=int(seed),
            eventtrace_dir=trace_dir(block, seed),
            spatial_to_client=load_spatial_to_client(ROOT, block),
            target_artifact=TARGET_ARTIFACT,
            dataset_name=block,
            scenario="complete_aligned",
            local_steps=int(local_steps),
            source_identity={
                "git_commit": _git_commit(),
                "s1p_driver_sha256": sha256_file(pathlib.Path(__file__)),
                "s1p_instruction_sha256": sha256_file(INSTRUCTION) if INSTRUCTION.is_file() else None,
                "server_opt": dict(ServerOptWindowRunner.SERVER_OPT),
                "server_opt_windowrunner_patch": "raven_mcs.training.window_runner.FullWindowRunner",
                "allow_reused_traffic_rerun": bool(TRAFFIC_REUSE_EXEMPTION and block == "traffic"),
                "reuse_guard_note": (
                    "ledger Part IX item 65; the guard refuses this cell by default and the opt-in is "
                    "recorded here so the run identifies itself"
                ) if (TRAFFIC_REUSE_EXEMPTION and block == "traffic") else None,
            },
        )
        dt = time.perf_counter() - t0
        n_applied = sum(1 for r in ServerOptWindowRunner.DIAG if r.get("applied"))
        dump_json(
            {
                "tag": tag, "block": block, "arm": arm, "seed": int(seed),
                "local_steps": int(local_steps), "server_opt": dict(ServerOptWindowRunner.SERVER_OPT),
                "runtime_seconds": dt, "n_windows_optimizer_applied": n_applied,
                "diag_first": ServerOptWindowRunner.DIAG[:3],
                "diag_last": ServerOptWindowRunner.DIAG[-3:],
                "created_utc": now(),
                # The ledger cannot carry these: run_e3_real writes only git_commit,
                # source_manifest_hash, method_source_hash, runner_source_hash and dataset_hash from
                # source_identity (runner.py L307-L311), so the exemption is recorded here, in the
                # driver's own per-run artifact, and in a dedicated file below.
                "reuse_guard_exemption": bool(TRAFFIC_REUSE_EXEMPTION and block == "traffic"),
                "reuse_guard_code_default": "DUPLICATE_REUSED_TRAFFIC_RUN_BLOCKED",
                "reuse_guard_ledger_part": "Part IX item 65" if (TRAFFIC_REUSE_EXEMPTION and block == "traffic") else None,
            },
            d / "SERVER_OPT_META.json",
        )
        if TRAFFIC_REUSE_EXEMPTION and block == "traffic":
            dump_json(
                {
                    "exemption": "allow_reused_traffic_rerun=True",
                    "guard": "src/raven_mcs/e3/protocol_closure/reuse_guard.py",
                    "guard_default": "raises DuplicateReusedTrafficRunBlocked",
                    "authorized_by": "user, 2026-10-08",
                    "ledger_record": "ccfa-review-reports/raven-mcs-metric-definition-diagnosis.md Part IX item 65",
                    "caveat": "This run is NOT the sealed E2 Traffic Complete-aligned object and must "
                              "not be compared with the frozen E3 traffic evidence as if it were.",
                    "run": {"block": block, "arm": arm, "seed": int(seed), "tag": tag},
                    "created_utc": now(),
                },
                d / "REUSE_GUARD_EXEMPTION.json",
            )
        print(f"  [run ] {d.relative_to(ROOT)}  {dt:.1f}s  optimizer_steps={n_applied}")
    except Exception as exc:  # noqa: BLE001
        dump_json({"failed": True, "error": f"{type(exc).__name__}: {exc}"[:500],
                   "block": block, "arm": arm, "seed": int(seed), "tag": tag,
                   "server_opt": dict(ServerOptWindowRunner.SERVER_OPT), "created_utc": now()},
                  d / "RUN_FAILED.json")
        raise
    finally:
        uninstall()
    return d


def load_fm(d: pathlib.Path) -> dict:
    return json.loads((d / "final_metrics.json").read_text(encoding="utf-8"))


# `runtime_seconds` is a wall-clock measurement, not a function of the computation, so no two runs
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
    return (not det_diffs), det_diffs, all_diffs, wall


# --------------------------------------------------------------------- G1 (static audit)
G1_FINDINGS = [
    {
        "line": "L1170-L1172",
        "code": "self.model.load_state_dict(self.theta); new_version = self.clock.apply_server_update(); "
                "self.model_versions[new_version] = copy.deepcopy(self.theta)",
        "sees_theta_new": True,
        "why": "these are the writes the override re-does after the optimizer step; the override "
               "re-loads the model and re-registers the latest version with theta_new",
    },
    {
        "line": "L1173-L1190",
        "code": "memmap flush/close of mm, mmap_obj",
        "sees_theta_new": "not_applicable",
        "why": "touches no theta / model / model_versions",
    },
    {
        "line": "L1191-L1198",
        "code": "debt update, self.scale += eta, self.omega_sum += eta*omega",
        "sees_theta_new": "not_applicable",
        "why": "reads omega, self.mu, self.eta only",
    },
    {
        "line": "L1200-L1202",
        "code": "self._update_lagged_estimators(window_slice, client_data); "
                "self._update_variance_state(local_updates, a_r_clients)",
        "sees_theta_new": "not_applicable",
        "why": "both methods (L1289, L1384) take window/client arguments and contain no reference to "
               "self.theta, self.model or self.model_versions (verified by full-file scan)",
    },
    {
        "line": "L1204",
        "code": "after_hash = self._theta_hash()",
        "sees_theta_new": False,
        "why": "REAL FINDING: _theta_hash() (L253-L255) iterates sorted(self.theta.items()), so under "
               "the override it is computed BEFORE the optimizer step and therefore hashes theta_sgd, "
               "while the run continues from theta_new",
        "feeds_final_metrics": False,
    },
    {
        "line": "L1231, L1236-L1237",
        "code": "per-client 'global_model_hash': after_hash; 'model_hash_before'/'model_hash_after'",
        "sees_theta_new": False,
        "why": "derived from the same stale after_hash",
        "feeds_final_metrics": False,
    },
    {
        "line": "L1269-L1287",
        "code": "return WindowMetrics(..., theta_hash_after=after_hash, ...)",
        "sees_theta_new": False,
        "why": "WindowMetrics.theta_hash_after carries the pre-optimizer hash",
        "feeds_final_metrics": False,
    },
]

G1_STOP = False  # no affected metric reaches final_metrics.json -> section 3's STOP does not fire


# --------------------------------------------------------------------- gates
def gate_g0() -> dict:
    rows = []
    ok_all = True
    for block in G0_BLOCKS:
        for arm in ("fedavg_window", "raven"):
            print(f"G0 {block}/{arm} seed{GATE_SEED}: unmodified baseline")
            d_off = run_one(block, arm, GATE_SEED, LOCAL_STEPS, "g0_baseline", "off", force=True)
            print(f"G0 {block}/{arm} seed{GATE_SEED}: subclass with plain SGD")
            d_sgd = run_one(block, arm, GATE_SEED, LOCAL_STEPS, "g0_identity", "sgd",
                            eta_s=ETA_GLOBAL_DEFAULT, force=True)
            fm_off, fm_sgd = load_fm(d_off), load_fm(d_sgd)
            same, det_diffs, all_diffs, wall = same_final_metrics(fm_off, fm_sgd)
            ck_a = d_off / "checkpoints" / "final.pt"
            ck_b = d_sgd / "checkpoints" / "final.pt"
            theta_identical = (ck_a.is_file() and ck_b.is_file()
                               and sha256_file(ck_a) == sha256_file(ck_b))
            frozen_dir = ROOT / "artifacts/e3_formal_runs_r1/runs" / block / arm / ("seed%d" % GATE_SEED)
            frozen_cmp = None
            if (frozen_dir / "final_metrics.json").is_file():
                fm_frozen = load_fm(frozen_dir)
                per = {}
                for k, v in fm_frozen.items():
                    if isinstance(v, (int, float)) and isinstance(fm_sgd.get(k), (int, float)):
                        per[k] = {"frozen": v, "rerun": fm_sgd.get(k), "abs_diff": abs(v - fm_sgd.get(k))}
                frozen_cmp = {"dir": str(frozen_dir.relative_to(ROOT)).replace("\\", "/"), "fields": per}
            rows.append({
                "block": block, "arm": arm, "seed": GATE_SEED,
                "baseline_dir": str(d_off.relative_to(ROOT)).replace("\\", "/"),
                "identity_dir": str(d_sgd.relative_to(ROOT)).replace("\\", "/"),
                "deterministic_bit_exact": same,
                "literal_bit_exact": not all_diffs,
                "deterministic_differences": det_diffs,
                "all_differences": all_diffs,
                "wall_clock_values": wall,
                "final_theta_bit_identical": bool(theta_identical),
                "final_theta_sha256": {
                    "baseline": sha256_file(ck_a) if ck_a.is_file() else None,
                    "identity": sha256_file(ck_b) if ck_b.is_file() else None,
                },
                "frozen_artifact_diagnostic": frozen_cmp,
            })
            ok_all = ok_all and same and theta_identical
            print(f"   deterministic_bit_exact={same}  theta_bit_identical={theta_identical}"
                  + ("" if same else f"  diffs={det_diffs[:3]}")
                  + (f"  wall_clock_excluded={wall}" if wall else ""))
    return {"gate": "G0",
            "rule": "subclass(SGD, eta_s=eta) vs unmodified FullWindowRunner; deterministic fields "
                    "of final_metrics.json bit-exact AND final checkpoint byte-identical. "
                    "runtime_seconds is excluded and reported separately (wall clock)",
            "blocks_gated": list(G0_BLOCKS), "traffic_gated": False,
            "traffic_note": "E3 traffic tree has no fedavg_window/raven arm (amendment A2)",
            "pass": bool(ok_all), "rows": rows}


def gate_g2() -> dict:
    block, arm = "sensorscope", "fedavg_window"
    print(f"G2 {block}/{arm} seed{GATE_SEED} eta_s=1e-3 (adam) x2")
    d1 = run_one(block, arm, GATE_SEED, LOCAL_STEPS, "g2_det_a", "adam", eta_s=1e-3, force=True)
    d2 = run_one(block, arm, GATE_SEED, LOCAL_STEPS, "g2_det_b", "adam", eta_s=1e-3, force=True)
    same, det_diffs, all_diffs, wall = same_final_metrics(load_fm(d1), load_fm(d2))
    return {"gate": "G2", "rule": "same (block, arm, seed, config) twice -> identical final_metrics.json "
                                  "on all deterministic fields; runtime_seconds excluded as wall clock",
            "pass": bool(same), "deterministic_differences": det_diffs,
            "all_differences": all_diffs, "wall_clock_values": wall,
            "run_a": str(d1.relative_to(ROOT)).replace("\\", "/"),
            "run_b": str(d2.relative_to(ROOT)).replace("\\", "/")}


def gate_g1() -> dict:
    return {"gate": "G1", "rule": "list every line of _process_window after L1169 that reads "
                                   "self.theta / self.model / self.model_versions, and say whether the "
                                   "override makes it see theta_new",
            "stop_condition": "if such a metric feeds final_metrics.json, STOP",
            "stop": bool(G1_STOP), "findings": G1_FINDINGS,
            "final_metrics_key_count": 32,
            "final_metrics_has_hash_key": False}


def hashes(paths) -> dict:
    return {str(p.relative_to(ROOT)).replace("\\", "/"): sha256_file(p) for p in paths if p.is_file()}


def write_gates(g1, g0, g2) -> pathlib.Path:
    md = OUT / "S1P_GATES.md"
    lines = [
        "# S1' gates",
        "",
        f"Instruction: `{INSTRUCTION.relative_to(ROOT).as_posix()}`  ",
        f"sha256 `{sha256_file(INSTRUCTION)}`  ",
        f"Written: {now()}",
        "",
        "Amendments confirmed by the user on 2026-10-07 before any run: **A1** G0 is a true identity",
        "test against a re-run of the unmodified runner, with the frozen-artifact comparison demoted to",
        "a disclosed diagnostic; **A2** G0 is not gated on NSW-Traffic, whose E3 tree has no",
        "`fedavg_window` or `raven` arm; **A3** Stage C evaluates `MDE80` at n = 5 per section 2.",
        "",
        "## G1 — reads-after-update audit",
        "",
        f"- STOP condition fired: **{g1['stop']}**",
        "- `final_metrics.json` carries 32 keys and **no** hash / theta / model key, so the affected",
        "  logged values do not reach the decision metric.",
        "",
        "| line | code | sees theta_new | note |",
        "| --- | --- | --- | --- |",
    ]
    for f in g1["findings"]:
        lines.append(f"| `{f['line']}` | `{f['code'][:110]}` | {f['sees_theta_new']} | {f['why']} |")
    lines += [
        "",
        "## G0 — identity test",
        "",
        f"- **pass: {g0['pass']}**",
        f"- gated blocks: {', '.join(g0['blocks_gated'])}; traffic gated: {g0['traffic_gated']}",
        "",
        "| block | arm | seed | deterministic bit-exact | final theta byte-identical | "
        "deterministic differences | wall-clock field |",
        "| --- | --- | --- | --- | --- | --- | --- |",
    ]
    for r in g0["rows"]:
        lines.append(f"| {r['block']} | {r['arm']} | {r['seed']} | {r['deterministic_bit_exact']} | "
                     f"{r['final_theta_bit_identical']} | "
                     f"{'; '.join(r['deterministic_differences'][:3]) or 'none'} | "
                     f"`runtime_seconds` (excluded) |")
    lines += ["", "### Frozen-artifact diagnostic (not a gate)", "",
              "| block | arm | field | frozen | re-run | \\|delta\\| |", "| --- | --- | --- | --- | --- | --- |"]
    for r in g0["rows"]:
        fc = r.get("frozen_artifact_diagnostic")
        if not fc:
            continue
        for k in ("RMSE_mu", "Delta_group", "Delta_c_s", "Tail_RMSE"):
            if k in fc["fields"]:
                f = fc["fields"][k]
                lines.append(f"| {r['block']} | {r['arm']} | `{k}` | {f['frozen']!r} | {f['rerun']!r} | "
                             f"{f['abs_diff']:.3e} |")
    lines += ["", "## G2 — determinism", "", f"- **pass: {g2['pass']}**",
              f"- deterministic differences: "
              f"{'; '.join(g2.get('deterministic_differences', [])[:5]) or 'none'}",
              f"- wall-clock field excluded and reported: {g2.get('wall_clock_values') or 'none'}", ""]
    md.write_text("\n".join(lines) + "\n", encoding="utf-8")
    return md


# --------------------------------------------------------------------- Stage A
#
# PRE-REGISTERED before any grid run (recorded here and echoed into S1P_FROZEN_CONFIG.json):
#
#   1. The runner does not emit a validation metric: `run_e3_real` calls `_predict(..., split="test")`
#      only, and `window_metrics.json` rows carry just {window_id, active, active_clients, a_r_size,
#      alpha, beta_hat}.  A validation RMSE_mu is therefore computed here as READ-ONLY post-processing
#      from the saved checkpoint, reusing the repo's own `_predict` with `split="validation"`.
#   2. Validation RMSE_mu weights each validation unit by `mu_g / count_g` with `mu_g` taken from a
#      `TargetBuilder(..., split="validation")` build on the same `target_group_main` mapping that
#      `build_full_runner` uses.  The test-mu-weighted variant is recorded as a sensitivity only.
#   3. Selection uses ONLY validation means.  Nothing derived from the test split is written to any
#      file until `S1P_FROZEN_CONFIG.json` exists.  The seal is procedural, not physical: the runner
#      itself writes test metrics into each run directory as part of its own output contract, which
#      cannot be changed without editing `src/`.
#   4. Ties within 0.1 % of the best validation mean go to the smaller eta_s.
#   5. A run counts as FAILED for its eta_s if any non-finite value appears in final_metrics or the
#      checkpoint fails to load.
STAGE_A_TIE_REL = 1e-3

# The E3 protocol closure's reuse guard refuses `traffic` + `complete_aligned` + formal seed +
# {fedavg_window, fedasync_window, flamf_timealign_adapted, twostage_hajek, raven} with
# DUPLICATE_REUSED_TRAFFIC_RUN_BLOCKED (src/raven_mcs/e3/protocol_closure/reuse_guard.py, untracked,
# mtime 2026-10-07 17:00:29 -- added after the earlier traffic round finished at 16:27).  Stage A
# trains `fedavg_window` on traffic, so those cells are refused.  Per section 1 that condition cannot
# be met without editing src/, so it is recorded as a BLOCKED block rather than worked around; the
# refusal is caught per cell so the SensorScope and U-Air cells are unaffected and the exact error
# text is preserved.  See S1P_BLOCKED.md.
TRAFFIC_REUSE_GUARD_NOTE = (
    "traffic + complete_aligned + seed in 30001..30020 + fedavg_window/raven is REUSE_ONLY_NO_RERUN"
)


def _validation_mu(dataset, n_groups: int) -> np.ndarray:
    from raven_mcs.data.target import GroupMapper, RepeatableTimeOfDayMapper, TargetBuilder

    atomic = dataset.atomic_df.copy()
    if n_groups == 4:
        atomic["target_group_main"] = RepeatableTimeOfDayMapper().map(atomic)
    else:
        atomic["target_group_main"] = pd.Categorical(atomic["target_group"]).codes
    tgt = TargetBuilder(group_mapper=GroupMapper("target_group_main")).build(atomic, split="validation")
    return np.asarray([float(tgt.group_mass.get(str(g), 0.0)) for g in range(n_groups)], dtype=np.float64)


def validation_rmse_mu(block: str, dataset, ckpt: pathlib.Path, n_groups: int) -> dict:
    """Read-only validation RMSE_mu from a saved checkpoint."""
    from raven_mcs.e3.real_runner.runner import CommonNDMF_from_ckpt, _predict, _mu_weights_for_test
    from raven_mcs.metrics.accuracy import rmse_mu

    class _Shim:
        pass

    shim = _Shim()
    shim.model = CommonNDMF_from_ckpt(pathlib.Path(ckpt), dataset.num_spatial)
    pred = _predict(shim, dataset, split="validation")
    out = {"n_val_units": int(len(pred["y_true"]))}
    for tag, mu in (("val_mu", _validation_mu(dataset, n_groups)), ("test_mu", None)):
        if tag == "test_mu":
            continue
        w = _mu_weights_for_test(pred, mu)
        out[f"{tag}_mass_sum"] = float(np.sum(mu))
        out[f"RMSE_mu_{tag}"] = float(rmse_mu(pred["y_pred"], pred["y_true"], w)) if len(w) else None
    return out


def movement_per_tensor(ckpt: pathlib.Path, seed: int) -> dict:
    """Relative parameter movement of the saved checkpoint against the seed-reconstructed init."""
    import torch
    from raven_mcs.models.common_ndmf import deterministic_common_ndmf

    obj = torch.load(ckpt, map_location="cpu", weights_only=False)
    theta = obj["state_dict"] if isinstance(obj, dict) and "state_dict" in obj else obj
    init = deterministic_common_ndmf(int(theta["spatial.weight"].shape[0]), seed=seed).state_dict()
    tot_d2 = tot_i2 = 0.0
    per = {}
    for k in sorted(theta):
        a = init[k].detach().cpu().double()
        b = theta[k].detach().cpu().double()
        d2 = float(((b - a) ** 2).sum())
        i2 = float((a ** 2).sum())
        per[k] = (math.sqrt(d2) / math.sqrt(i2)) if i2 > 0 else float("nan")
        tot_d2 += d2
        tot_i2 += i2
    return {
        "overall_rel_movement": math.sqrt(tot_d2) / math.sqrt(tot_i2),
        "head_0_weight_rel": per.get("head.0.weight"),
        "head_8_bias_rel": per.get("head.8.bias"),
        "spatial_weight_rel": per.get("spatial.weight"),
    }


def stage_a(args) -> int:
    from raven_mcs.e3.canary.dataset_load import load_paper_dataset

    grid_dir = OUT / "tables"
    grid_dir.mkdir(parents=True, exist_ok=True)
    val_rows = []
    for block in BLOCKS:
        dataset = load_paper_dataset(ROOT, block)
        n_groups = int(dataset.num_groups)
        for eta_s in STAGE_A_ETA_S:
            for seed in SCREEN_SEEDS:
                tag = "A_eta%g" % eta_s
                row = {"block": block, "arm": "fedavg_window", "seed": seed, "eta_s": eta_s,
                       "run_dir": "", "blocked": False, "blocked_reason": "", "error": "",
                       "ckpt_ok": False, "finite": False, "diverged": True}
                try:
                    d = run_one(block, "fedavg_window", seed, LOCAL_STEPS, tag, "adam", eta_s=eta_s)
                    row["run_dir"] = str(d.relative_to(ROOT)).replace("\\", "/")
                    ck = d / "checkpoints" / "final.pt"
                    row.update(validation_rmse_mu(block, dataset, ck, n_groups))
                    row.update(movement_per_tensor(ck, seed))
                    row["ckpt_ok"] = True
                    hajek = json.loads((d / "final_metrics.json").read_text(encoding="utf-8"))
                    row["hajek_target_risk_objective"] = hajek.get("target_risk_objective")
                    row["no_h_mass_loss"] = hajek.get("Gap_mis")
                    row["finite"] = all(
                        not isinstance(v, float) or math.isfinite(v) for v in hajek.values()
                    )
                    row["diverged"] = not (row["ckpt_ok"] and row["finite"]
                                           and row.get("RMSE_mu_val_mu") is not None
                                           and math.isfinite(row.get("RMSE_mu_val_mu") or float("nan")))
                except Exception as exc:  # noqa: BLE001
                    row["blocked"] = "DuplicateReusedTrafficRunBlocked" in type(exc).__name__
                    row["blocked_reason"] = TRAFFIC_REUSE_GUARD_NOTE if row["blocked"] else ""
                    row["error"] = f"{type(exc).__name__}: {exc}"[:400]
                    row["diverged"] = True
                val_rows.append(row)
                # incremental write so a later refusal cannot lose completed cells
                with (grid_dir / "STAGE_A_VALIDATION.csv").open("w", newline="", encoding="utf-8") as f:
                    w = csv.DictWriter(f, fieldnames=sorted({k for r in val_rows for k in r}))
                    w.writeheader()
                    w.writerows(val_rows)
                print(f"  A {block:<12} eta={eta_s:<7g} seed{seed}  "
                      f"val={row.get('RMSE_mu_val_mu')!r}  "
                      f"{'BLOCKED' if row['blocked'] else 'diverged=' + str(row['diverged'])}",
                      flush=True)

    with (grid_dir / "STAGE_A_VALIDATION.csv").open("w", newline="", encoding="utf-8") as f:
        w = csv.DictWriter(f, fieldnames=sorted({k for r in val_rows for k in r}))
        w.writeheader()
        w.writerows(val_rows)

    # ---- selection on validation ONLY ----
    frozen = {"schema": "S1P_STAGE_A_SELECTION_V1", "created_utc": now(),
              "selection_rule": "per block: argmin of the mean validation RMSE_mu over the 5 screen "
                                "seeds among non-diverged levels; ties within 0.1 % go to the smaller "
                                "eta_s", "tie_rel": STAGE_A_TIE_REL,
              "validation_metric": "RMSE_mu on the validation split, weights mu_g / count_g with mu_g "
                                   "from TargetBuilder(split='validation') on target_group_main",
              "screen_seeds": SCREEN_SEEDS, "grid_eta_s": list(STAGE_A_ETA_S),
              "test_split_read": False}
    per_block = {}
    for block in BLOCKS:
        levels = {}
        for eta_s in STAGE_A_ETA_S:
            rs = [r for r in val_rows if r["block"] == block and r["eta_s"] == eta_s
                  and not r["diverged"] and not r["blocked"]]
            n_blocked = sum(1 for r in val_rows
                            if r["block"] == block and r["eta_s"] == eta_s and r["blocked"])
            levels[eta_s] = {
                "n_non_diverged": len(rs),
                "n_screen_seeds": len(SCREEN_SEEDS),
                # Section 4 selects on "the mean validation RMSE_mu over the 5 seeds", so a level is
                # eligible only when all five screen seeds produced a usable run.  A level averaged
                # over a surviving subset is recorded but not selectable.
                "all_screen_seeds_usable": len(rs) == len(SCREEN_SEEDS),
                "n_blocked": n_blocked,
                "mean_val_RMSE_mu": (float(np.mean([r["RMSE_mu_val_mu"] for r in rs])) if rs else None),
            }
        ok = {k: v for k, v in levels.items() if v.get("all_screen_seeds_usable")}
        if not ok:
            blk = [r for r in val_rows if r["block"] == block and r["blocked"]]
            if blk:
                reason = "BLOCKED: " + TRAFFIC_REUSE_GUARD_NOTE
            elif any(v["n_non_diverged"] for v in levels.values()):
                reason = ("NO_ELIGIBLE_LEVEL: every level lost at least one screen seed to divergence, "
                          "so none can be averaged over the 5 seeds section 4 specifies")
            else:
                reason = "every level diverged"
            per_block[block] = {"eta_s_star": None, "reason": reason, "levels": levels,
                                "n_blocked_cells": len(blk),
                                "example_error": (blk[0]["error"] if blk else "")}
            continue
        best = min(ok.values(), key=lambda v: v["mean_val_RMSE_mu"])["mean_val_RMSE_mu"]
        cands = sorted(k for k, v in ok.items()
                       if v["mean_val_RMSE_mu"] <= best * (1.0 + STAGE_A_TIE_REL))
        per_block[block] = {"eta_s_star": float(cands[0]), "tie_candidates": [float(c) for c in cands],
                            "levels": levels}
    frozen["per_block"] = per_block
    cfg_path = OUT / "S1P_FROZEN_CONFIG.json"
    dump_json(frozen, cfg_path)
    digest = sha256_file(cfg_path)
    print(f"  froze S1P_FROZEN_CONFIG.json sha256={digest}")

    # ---- only now open the test split ----
    test_rows = []
    for block in BLOCKS:
        star = per_block[block]["eta_s_star"]
        if star is None:
            continue
        for r in val_rows:
            if r["block"] != block or r["eta_s"] != star:
                continue
            fm_path = (ROOT / r["run_dir"] / "final_metrics.json") if r.get("run_dir") else None
            if fm_path is None or not fm_path.is_file():
                continue
            fm = json.loads(fm_path.read_text(encoding="utf-8"))
            test_rows.append({"block": block, "seed": r["seed"], "eta_s": star,
                              "test_RMSE_mu": fm.get("RMSE_mu"), "test_Delta_group": fm.get("Delta_group"),
                              "test_Delta_c_s": fm.get("Delta_c_S"), "test_Tail_RMSE": fm.get("Tail_RMSE")})
    with (grid_dir / "STAGE_A_GRID.csv").open("w", newline="", encoding="utf-8") as f:
        w = csv.DictWriter(f, fieldnames=sorted({k for r in val_rows + test_rows for k in r}))
        w.writeheader()
        for r in val_rows:
            rr = dict(r)
            m = [t for t in test_rows if t["block"] == r["block"] and t["seed"] == r["seed"]
                 and t["eta_s"] == r["eta_s"]]
            if m:
                rr.update({k: v for k, v in m[0].items() if k.startswith("test_")})
            w.writerow(rr)

    # ---- N3' per block on test ----
    n3 = {}
    for block in BLOCKS:
        star = per_block[block]["eta_s_star"]
        if star is None:
            why = per_block[block].get("reason", "no non-diverged level")
            if why.startswith("BLOCKED"):
                v = "BLOCKED"
            elif why.startswith("NO_ELIGIBLE_LEVEL"):
                v = "NO_ELIGIBLE_LEVEL"
            else:
                v = "FAIL"
            n3[block] = {"verdict": v, "reason": why,
                         "example_error": per_block[block].get("example_error", "")}
            continue
        c_vals, f_vals, new_vals = [], [], []
        for r in test_rows:
            if r["block"] != block:
                continue
            sd = ROOT / "artifacts/e3_formal_runs_r1/runs" / block / "central_delivered" / ("seed%d" % r["seed"]) / "final_metrics.json"
            fd = ROOT / "artifacts/e3_formal_runs_r1/runs" / block / "fedavg_window" / ("seed%d" % r["seed"]) / "final_metrics.json"
            if sd.is_file():
                c_vals.append(json.loads(sd.read_text(encoding="utf-8")).get("RMSE_mu"))
            if fd.is_file():
                f_vals.append(json.loads(fd.read_text(encoding="utf-8")).get("RMSE_mu"))
            new_vals.append(r["test_RMSE_mu"])
        c = float(np.mean(c_vals)) if c_vals else None
        frozen_fed = float(np.mean(f_vals)) if f_vals else None
        new = float(np.mean(new_vals)) if new_vals else None
        if c is None or new is None:
            n3[block] = {"verdict": "FAIL", "reason": "missing central_delivered or new mean"}
            continue
        if new <= 1.01 * c:
            verdict = "PASS"
        elif frozen_fed is not None and new <= frozen_fed * 0.99:
            verdict = "PARTIAL"
        else:
            verdict = "FAIL"
        n3[block] = {"verdict": verdict, "eta_s_star": star, "c_central_delivered": c,
                     "frozen_fedavg_window": frozen_fed, "new_fedavg": new,
                     "ratio_to_c": new / c if c else None,
                     "vs_frozen_fedavg_rel": (new / frozen_fed - 1.0) if frozen_fed else None,
                     "threshold_1p01c": 1.01 * c}
    dump_json({"frozen_config_sha256": digest, "N3_prime": n3, "created_utc": now()},
              OUT / "S1P_STAGE_A_VERDICT.json")
    for block, v in n3.items():
        print(f"  N3' {block:<12} {v['verdict']}  ratio_to_c={v.get('ratio_to_c')}"
              + (f"  ({v.get('reason', '')[:80]})" if v["verdict"] == "BLOCKED" else ""), flush=True)
    return 0


# --------------------------------------------------------------------- Stage C
#
# GO-H per section 6, with amendment A3 (MDE80 evaluated at n = 5):
#   H = (RMSE_mu(fedavg) - RMSE_mu(raven_simoracle)) / RMSE_mu(fedavg), paired by seed
#   GO-H  iff  mean(H) >= 1 %  AND  bootstrap 95 % lower bound > 0.5 %  AND  MDE80 < 0.5 * mean(H)
#   AND the block is not excluded by the section-6 K_r clause: "do not upgrade SS/UA to GO if more
#   than 25 % of active windows have K_r <= 3".
STAGE_C_BOOT_DRAWS = 10000
STAGE_C_BOOT_SEED = 20261007
STAGE_C_H_BAR = 0.01
STAGE_C_H_LCB_BAR = 0.005
STAGE_C_KR_EXCLUDE = 0.25
STAGE_C_KR_GUARD_BLOCKS = ("sensorscope", "uair")


def kr_le3_share(run_dir: pathlib.Path) -> dict:
    rows = json.loads((run_dir / "window_metrics.json").read_text(encoding="utf-8"))
    act = [r for r in rows if r.get("active")]
    if not act:
        return {"n_active": 0, "share_kr_le3": None, "share_ar_le2": None}
    return {
        "n_active": len(act),
        "share_kr_le3": sum(1 for r in act if (r.get("a_r_size") or 0) <= 3) / len(act),
        "share_ar_le2": sum(1 for r in act if (r.get("a_r_size") or 0) <= 2) / len(act),
    }


def mde80_paired(sd: float, n: int) -> float:
    from scipy import stats
    return float((stats.t.ppf(0.975, n - 1) + stats.t.ppf(0.80, n - 1)) * sd / math.sqrt(n))


def stage_c(args) -> int:
    cfg = json.loads((OUT / "S1P_FROZEN_CONFIG.json").read_text(encoding="utf-8"))
    av = json.loads((OUT / "S1P_STAGE_A_VERDICT.json").read_text(encoding="utf-8"))
    grid = list(csv.DictReader((OUT / "tables" / "STAGE_A_GRID.csv").open(encoding="utf-8")))

    rows, hres = [], {}
    for block in BLOCKS:
        star = cfg["per_block"][block].get("eta_s_star")
        n3 = av["N3_prime"].get(block, {}).get("verdict")
        if star is None or n3 != "PASS":
            hres[block] = {"verdict": "not_run", "reason": f"N3'={n3}"}
            continue
        for arm in ("raven_simoracle", "raven"):
            for seed in SCREEN_SEEDS:
                try:
                    run_one(block, arm, seed, LOCAL_STEPS, "C_%s" % arm, "adam", eta_s=star)
                except Exception as exc:  # noqa: BLE001
                    rows.append({"block": block, "arm": arm, "seed": seed, "blocked": True,
                                 "error": f"{type(exc).__name__}: {exc}"[:300]})
        fed, sim, rav, kr = {}, {}, {}, None
        for r in grid:
            if r["block"] != block or float(r["eta_s"]) != float(star):
                continue
            seed = int(r["seed"])
            fed[seed] = float(r["test_RMSE_mu"])
            if kr is None and r.get("run_dir"):
                kr = kr_le3_share(ROOT / r["run_dir"])
        for arm, store in (("raven_simoracle", sim), ("raven", rav)):
            for seed in SCREEN_SEEDS:
                pth = RUNS / ("C_%s" % arm) / block / arm / ("seed%d" % seed) / "final_metrics.json"
                if pth.is_file():
                    store[seed] = json.loads(pth.read_text(encoding="utf-8")).get("RMSE_mu")
        seeds = sorted(set(fed) & set(sim))
        if len(seeds) < 3:
            hres[block] = {"verdict": "not_run", "reason": f"only {len(seeds)} paired seeds"}
            continue
        Hs = np.asarray([(fed[s] - sim[s]) / fed[s] for s in seeds], dtype=np.float64)
        rng = np.random.default_rng(STAGE_C_BOOT_SEED)
        boot = np.asarray([np.mean(rng.choice(Hs, size=len(Hs), replace=True))
                           for _ in range(STAGE_C_BOOT_DRAWS)])
        lo, hi = np.percentile(boot, [2.5, 97.5])
        sd = float(np.std(Hs, ddof=1))
        mde = mde80_paired(sd, len(Hs))
        mean_h = float(np.mean(Hs))
        cond_h = mean_h >= STAGE_C_H_BAR
        cond_lcb = float(lo) > STAGE_C_H_LCB_BAR
        cond_mde = mde < 0.5 * mean_h if mean_h > 0 else False
        guard = kr is not None and kr.get("share_kr_le3") is not None and \
            block in STAGE_C_KR_GUARD_BLOCKS and kr["share_kr_le3"] > STAGE_C_KR_EXCLUDE
        verdict = "GO-H" if (cond_h and cond_lcb and cond_mde and not guard) else "NO-GO-H"
        hres[block] = {
            "verdict": verdict, "eta_s_star": star, "n_paired_seeds": len(seeds),
            "paired_seeds": seeds, "H_by_seed": [float(x) for x in Hs], "mean_H": mean_h,
            "boot_lo": float(lo), "boot_hi": float(hi), "paired_sd": sd, "MDE80_n5": mde,
            "cond_mean_ge_1pct": bool(cond_h), "cond_lcb_gt_0.5pct": bool(cond_lcb),
            "cond_mde_lt_half_H": bool(cond_mde),
            "kr_clause": {"applies": block in STAGE_C_KR_GUARD_BLOCKS,
                          "share_kr_le3": (kr or {}).get("share_kr_le3"),
                          "threshold": STAGE_C_KR_EXCLUDE, "excluded_from_GO": bool(guard)},
            "fedavg_test_RMSE_mu": {str(s): fed[s] for s in seeds},
            "raven_simoracle_test_RMSE_mu": {str(s): sim[s] for s in seeds},
            "raven_descriptive_test_RMSE_mu": {str(s): rav[s] for s in seeds if s in rav},
            "kr_le3_under_new_config": kr,
            "bootstrap": {"draws": STAGE_C_BOOT_DRAWS, "rng_seed": STAGE_C_BOOT_SEED,
                          "type": "percentile 95%"},
        }
        print(f"  C {block:<12} mean_H={mean_h:.6f} "
              f"CI=[{float(lo):.6f},{float(hi):.6f}] MDE80={mde:.6e} "
              f"kr_le3={(kr or {}).get('share_kr_le3')} -> {verdict}", flush=True)

    with (OUT / "tables" / "STAGE_C_H.csv").open("w", newline="", encoding="utf-8") as f:
        w = csv.DictWriter(f, fieldnames=["block", "arm", "seed", "blocked", "error"])
        w.writeheader()
        w.writerows(rows)
    dump_json({"H": hres, "created_utc": now(),
               "amendment_A3": "MDE80 evaluated at n = 5 per section 2; n = 15 reserved for the "
                               "separately authorized confirmatory run"},
              OUT / "S1P_STAGE_C_H.json")
    return 0


def cmd_gates(args) -> int:
    OUT.mkdir(parents=True, exist_ok=True)
    g1 = gate_g1()
    print(f"G1 stop={g1['stop']}")
    g0 = gate_g0()
    print(f"G0 pass={g0['pass']}")
    dump_json({"g1": g1, "g0": g0}, OUT / "S1P_GATES_PARTIAL.json")
    if not g0["pass"]:
        dump_json({"g1": g1, "g0": g0, "g2": None}, OUT / "S1P_GATES.json")
        write_gates(g1, g0, {"pass": None, "differences": ["not run: G0 failed"]})
        (OUT / "S1P_BLOCKED.md").write_text(
            "# S1' blocked at G0\n\nG0 (identity test) failed; per section 3 the round stops before any "
            "grid run.  See `S1P_GATES.md`.\n", encoding="utf-8")
        return 2
    g2 = gate_g2()
    print(f"G2 pass={g2['pass']}")
    dump_json({"g1": g1, "g0": g0, "g2": g2}, OUT / "S1P_GATES.json")
    write_gates(g1, g0, g2)
    if not g2["pass"]:
        (OUT / "S1P_BLOCKED.md").write_text(
            "# S1' blocked at G2\n\nG2 (determinism) failed; per section 3 the round stops before any "
            "grid run.  See `S1P_GATES.md`.\n", encoding="utf-8")
        return 3
    print("all gates passed")
    return 0


def main() -> int:
    ap = argparse.ArgumentParser(description=__doc__)
    ap.add_argument("--stage", choices=("gates", "g2", "A", "C"), default="gates")
    ap.add_argument("--force", action="store_true", help="re-run existing cells")
    args = ap.parse_args()
    if args.stage == "A":
        return stage_a(args)
    if args.stage == "C":
        return stage_c(args)
    if args.stage == "g2":
        OUT.mkdir(parents=True, exist_ok=True)
        g2 = gate_g2()
        dump_json(g2, OUT / "S1P_G2.json")
        print(f"G2 pass={g2['pass']}")
        return 0 if g2["pass"] else 3
    return cmd_gates(args)


if __name__ == "__main__":
    raise SystemExit(main())
