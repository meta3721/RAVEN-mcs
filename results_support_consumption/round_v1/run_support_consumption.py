"""Staged support-consumption entry. P0-P2 do not train."""

from __future__ import annotations

import argparse
import csv
import hashlib
import json
import os
import subprocess
import sys
import time
import traceback
from pathlib import Path

os.environ["OMP_NUM_THREADS"] = "1"
os.environ["MKL_NUM_THREADS"] = "1"
os.environ["OPENBLAS_NUM_THREADS"] = "1"
os.environ["NUMEXPR_NUM_THREADS"] = "1"

ROUND_DIR = Path(__file__).resolve().parent
ROOT = ROUND_DIR.parents[1]
SRC = ROOT / "src"
for entry in (str(ROUND_DIR), str(SRC)):
    if entry not in sys.path:
        sys.path.insert(0, entry)

from accounting import AccountingError, StageWatch, available_bytes, process_tree_usage, require_start_memory
from protocol import (
    A_MAX,
    ALPHA_MAX,
    BACKBONE,
    CACHE_ARMS,
    COMPLEMENT_MARGIN,
    CPU_BUDGET,
    CROSS_CLOSE_COMMIT_MIN,
    E_MIN,
    EXTERNAL_ARMS,
    LOCAL_STEPS,
    MAIN_BLOCK,
    MEAN_D_IMPROVEMENT_MIN,
    NUM_GROUPS,
    NUM_WINDOWS,
    P_MIN,
    PER_SEED_COMPLEMENT_MIN,
    PI_MIN,
    POOL_CAP,
    POOLED_COMPLEMENT_MIN,
    PROTOCOL_NAME,
    RESIDENCE_H,
    RESIDENCE_QUANTILE,
    REVIEW_BLOCK,
    S_MAX,
    SERVER_LR,
    SERVER_OPTIMIZER,
    WALL_BUDGET,
)

EXPECTED_OUTPUT = (ROOT / "results_support_consumption" / "round_v1").resolve()
CODE_FILES = (
    "accounting.py",
    "protocol.py",
    "support_distance.py",
    "cache_scheduler.py",
    "reference_replay.py",
    "critical_tests.py",
    "run_support_consumption.py",
)
UNIT_COLUMNS = "unit_id,split,target_group,opportunity_stratum,spatial_id,absolute_time"


def plain(value):
    if isinstance(value, dict):
        return {str(key): plain(item) for key, item in value.items()}
    if isinstance(value, (list, tuple)):
        return [plain(item) for item in value]
    if isinstance(value, Path):
        return str(value)
    if hasattr(value, "item"):
        try:
            return value.item()
        except Exception:
            return str(value)
    return value


def write_json(path: Path, payload) -> None:
    path.write_text(json.dumps(plain(payload), indent=2, ensure_ascii=False, allow_nan=False) + "\n", encoding="utf-8")


def write_text(path: Path, text: str) -> None:
    path.write_text(text.rstrip() + "\n", encoding="utf-8")


def implementation_hash() -> str:
    digest = hashlib.sha256()
    for name in CODE_FILES:
        digest.update(name.encode())
        digest.update((ROUND_DIR / name).read_bytes())
    return digest.hexdigest()


def source_contains(path: Path, needle: str) -> bool:
    return needle in path.read_text(encoding="utf-8")


def confirm_source_configuration() -> dict:
    checks = {
        "s_max": source_contains(SRC / "raven_mcs/e3/real_runner/constants.py", "S_MAX = 5"),
        "window_duration": source_contains(SRC / "raven_mcs/e3/real_runner/constants.py", "WINDOW_DURATION = 1.0"),
        "u_includes_staleness": source_contains(
            SRC / "raven_mcs/e3/real_runner/stage2_r3.py",
            "u = bool(compute_success and network_success and deadline_pass and staleness_pass and has_observations)",
        ),
        "alpha_max": source_contains(SRC / "raven_mcs/aggregation/methods.py", "alpha_max: float = 0.5"),
        "e_min": source_contains(SRC / "raven_mcs/aggregation/methods.py", "e_min: float = 3.0"),
        "cap_formula": source_contains(
            SRC / "raven_mcs/aggregation/feasibility.py",
            "return float(min(1.0, max(float(alpha_max), 1.0 / float(n_active))))",
        ),
        "ess_formula": source_contains(
            SRC / "raven_mcs/aggregation/feasibility.py",
            "return float(min(float(e_min), float(n_active)))",
        ),
        "server_lr": source_contains(SRC / "raven_mcs/training/window_runner.py", "learning_rate: float = 0.01"),
        "builder_local_steps_default": source_contains(
            SRC / "raven_mcs/training/window_runner.py", "local_steps: int = 5"
        ),
        "a_max": source_contains(SRC / "raven_mcs/training/window_runner.py", "a_max: float = 20.0"),
        "p_min": source_contains(SRC / "raven_mcs/training/window_runner.py", "p_min: float = 0.05"),
        "pi_min": source_contains(SRC / "raven_mcs/training/window_runner.py", "pi_min: float = 1e-6"),
        "backbone": source_contains(SRC / "raven_mcs/training/window_runner.py", "CommonNDMF"),
        "server_step": source_contains(
            SRC / "raven_mcs/training/window_runner.py", "theta_flat - float(self.eta)"
        ),
        "operative_local_steps": source_contains(ROOT / "scripts/run_joint_ou_cs_p2.py", "LOCAL_STEPS = 2"),
        "operative_s_max": source_contains(ROOT / "scripts/run_joint_ou_cs_p2.py", "S_MAX = 5"),
        "joint_passes_local_steps": source_contains(
            ROOT / "scripts/run_joint_ou_cs_p2.py", "local_steps=LOCAL_STEPS"
        ),
        "visit_passes_local_steps": source_contains(
            ROOT / "scripts/run_nodesign_supplement.py", "local_steps=p2.LOCAL_STEPS"
        ),
        "visit_passes_s_max": source_contains(ROOT / "scripts/run_nodesign_supplement.py", "s_max=p2.S_MAX"),
    }
    failed = [name for name, ok in checks.items() if not ok]
    return {"checks": checks, "failed": failed}


def scan_checkpoints(root: Path) -> dict:
    if not root.exists():
        return {"root": str(root), "missing": True, "incomplete": [], "complete_final_count": 0}
    incomplete = []
    for partial in root.rglob("partial_model.pt"):
        if not (partial.parent / "final.pt").is_file():
            incomplete.append(str(partial.relative_to(ROOT)))
    complete = sum(1 for _ in root.rglob("final.pt"))
    return {
        "root": str(root.relative_to(ROOT)),
        "missing": False,
        "incomplete": incomplete,
        "complete_final_count": complete,
    }


def source_index() -> list[dict]:
    candidates = [
        ("instruction", Path(r"C:/Users/szr/Desktop/record/1/ccfa-review-reports/support-consumption-experiment-instructions.md")),
        ("practice_report", Path(r"C:/Users/szr/Desktop/record/1/ccfa-review-reports/raven-mcs-method1-method3-practice-report.md")),
        ("xw_gate", ROOT / "results_xw_pool/round_v1/P0_GATE.json"),
        ("xw_prereg", ROOT / "results_xw_pool/round_v1/P0_GATE_PREREG.md"),
        ("xw_geometry", ROOT / "results_xw_pool/round_v1/p0_geometry.py"),
        ("m1_status", ROOT / "results_m1_attribution/round_v1/M1_STATUS.json"),
        ("m1_prereg", ROOT / "results_m1_attribution/round_v1/M1_PREREG.md"),
        ("hotspot_decision", ROOT / "results_cityscanner_lowcost_screen/round_v1/hotspot/DECISION_REPORT.md"),
        ("of_repo", ROOT / "ccf-review-report/of_v1_small_scope_20261018_190539/DECISION_REPORT.md"),
        ("of_desktop", Path(r"C:/Users/szr/Desktop/record/1/ccf-review-report/of_v1_small_scope_20261018_190539/DECISION_REPORT.md")),
    ]
    rows = []
    for name, path in candidates:
        rows.append({"name": name, "path": str(path), "exists": path.is_file(), "bytes": path.stat().st_size if path.is_file() else 0})
    return rows


def ledger_append(path: Path, rows: list[dict]) -> None:
    fields = ["stage", "block", "dataset", "seed", "path", "split", "columns_read", "labels_read", "purpose"]
    exists = path.is_file()
    with path.open("a", encoding="utf-8", newline="") as handle:
        writer = csv.DictWriter(handle, fieldnames=fields)
        if not exists:
            writer.writeheader()
        for row in rows:
            writer.writerow({key: row.get(key, "") for key in fields})


def running_path(output: Path, stage: str) -> Path:
    return output / f"{stage}.RUNNING.json"


def budget_path(output: Path) -> Path:
    return output / "BUDGET_LEDGER.json"


def load_budget(output: Path) -> list[dict]:
    path = budget_path(output)
    if not path.is_file():
        return []
    return json.loads(path.read_text(encoding="utf-8"))


def save_budget(output: Path, rows: list[dict]) -> None:
    write_json(budget_path(output), rows)


def prior_cost(output: Path, stage: str) -> tuple[float, float]:
    cpu = wall = 0.0
    for row in load_budget(output):
        if row.get("stage") == stage and row.get("status") != "running":
            cpu += float(row.get("cpu_seconds", 0.0))
            wall += float(row.get("wall_seconds", 0.0))
    return cpu, wall


def status_path(output: Path, stage: str) -> Path:
    return output / f"{stage}_STATUS.json"


def existing_status(output: Path, stage: str) -> dict | None:
    path = status_path(output, stage)
    if not path.is_file():
        return None
    return json.loads(path.read_text(encoding="utf-8"))


def banner(stage: str, sample: dict) -> None:
    print(
        f"stage={stage} cpu={sample['cpu_seconds']:.3f}/{CPU_BUDGET[stage]:.0f} "
        f"wall={sample['wall_seconds']:.3f}/{WALL_BUDGET[stage]:.0f} "
        f"remaining_cpu={sample['remaining_cpu']:.3f} remaining_wall={sample['remaining_wall']:.3f}",
        flush=True,
    )


def failure_markdown(stage: str, status: str, detail: str, sample: dict, scope: str, cancelled: str) -> str:
    cause = "资源门槛在重型导入之前触发，没有进行回放。" if str(status).startswith("RESOURCE") or str(status).startswith("ACCOUNTING") else "门槛比较来自本次回放；更深层机制解释未单独验证"
    return "\n".join([
        f"# FAILURE_REPORT_{stage}",
        "",
        f"- 状态：{status}",
        f"- 未满足条件：{detail}",
        f"- 实测与阈值：见同目录 {stage}_STATUS.json",
        "- 首个失败位置：见状态文件的 evidence",
        f"- 原因层：{cause}",
        f"- 已完成范围：{scope}",
        f"- CPU 秒：{sample.get('cpu_seconds', '未闭合')}",
        f"- wall 秒：{sample.get('wall_seconds', '未闭合')}",
        f"- 峰值 RSS 字节：{sample.get('peak_rss_bytes', '')}",
        f"- 最小可用内存字节：{sample.get('available_bytes', sample.get('min_available_bytes', ''))}",
        f"- 取消的后续队列：{cancelled}",
        "- WAITING_USER_REVIEW",
        "",
        "无新增训练、尚无预测收益结果。",
    ])


def write_failure(output: Path, stage: str, status: str, detail: str, sample: dict, evidence: dict, scope: str, cancelled: str) -> None:
    payload = {
        "stage": stage,
        "status": status,
        "detail": detail,
        "evidence": plain(evidence),
        "sample": plain(sample),
        "scope": scope,
        "cancelled": cancelled,
        "waiting_user_review": True,
        "training": False,
        "prediction_gain": False,
    }
    write_json(status_path(output, stage), payload)
    write_text(output / f"FAILURE_REPORT_{stage}.md", failure_markdown(stage, status, detail, sample, scope, cancelled))


def require_prior(output: Path, stage: str) -> dict:
    order = {"P1": "P0", "P2": "P1"}
    prior = order.get(stage)
    if prior is None:
        return {}
    status = existing_status(output, prior)
    if status is None or status.get("status") != "PASS":
        raise AccountingError(f"REFUSE_SKIP: {prior} is not PASS")
    freeze = json.loads((output / "PROTOCOL_FREEZE.json").read_text(encoding="utf-8"))
    if freeze.get("implementation_hash") != implementation_hash():
        raise AccountingError("REFUSE_SKIP: implementation hash does not match the freeze")
    return status


def freeze_payload(contexts: dict, source_checks: dict, fixtures: dict, code_hash: str) -> dict:
    return {
        "protocol": PROTOCOL_NAME,
        "main_block": MAIN_BLOCK,
        "review_block": REVIEW_BLOCK,
        "s_max": S_MAX,
        "residence_h": RESIDENCE_H,
        "pool_cap": POOL_CAP,
        "complement_margin": COMPLEMENT_MARGIN,
        "alpha_max": ALPHA_MAX,
        "e_min": E_MIN,
        "cap": "min(1, max(alpha_max, 1/K))",
        "ess": "min(E_min, K)",
        "a_max": A_MAX,
        "p_min": P_MIN,
        "pi_min": PI_MIN,
        "local_steps": LOCAL_STEPS,
        "builder_local_steps_default_not_used": 5,
        "server_lr": SERVER_LR,
        "server_optimizer": SERVER_OPTIMIZER,
        "backbone": BACKBONE,
        "num_windows": NUM_WINDOWS,
        "num_groups": NUM_GROUPS,
        "design": "frozen_on",
        "gate_controls_design": False,
        "reference": "stage1(zeta_hat_stratum(pi_target, pi_opp), lagged observation propensity)",
        "q_use_in_reference": False,
        "downloaded_version_role": "audit_only",
        "per_seed_complement_min": PER_SEED_COMPLEMENT_MIN,
        "pooled_complement_min": POOLED_COMPLEMENT_MIN,
        "cross_close_commit_min": CROSS_CLOSE_COMMIT_MIN,
        "mean_d_improvement_min": MEAN_D_IMPROVEMENT_MIN,
        "residence_quantile": RESIDENCE_QUANTILE,
        "age_definition": "close_index - arrival_close; arrival close has age 0",
        "source_checks": source_checks,
        "blocks": {
            name: {
                "dataset": context.dataset,
                "mu": context.mu.tolist(),
                "setup_checks": context.setup_checks,
                "encoding": context.encoding,
            }
            for name, context in contexts.items()
        },
        "fixtures": fixtures,
        "implementation_hash": code_hash,
        "training": False,
    }


def write_p0_documents(output: Path, contexts: dict, replays: dict, source_rows: list[dict], checkpoints: list[dict], source_checks: dict, fixtures: dict, sample: dict) -> None:
    code_hash = implementation_hash()
    write_json(output / "PROTOCOL_FREEZE.json", freeze_payload(contexts, source_checks, fixtures, code_hash))
    index_lines = ["# SOURCE_INDEX", ""]
    for row in source_rows:
        state = "存在" if row["exists"] else "缺失"
        index_lines.append(f"- {row['name']}: {state}, {row['bytes']} 字节, `{row['path']}`")
    index_lines.append("")
    index_lines.append("缺失文件只记录为缺失，不补写其内容。旧的 xw/M1 结果不作为本次消费规则。")
    write_text(output / "SOURCE_INDEX.md", "\n".join(index_lines))
    audit = ["# P0_ASSET_AUDIT", "", "## 参考重建", ""]
    for name, replay in replays.items():
        audit.append(f"### {name} seed {replay.seed}")
        audit.append(f"- trace_hash: `{replay.trace_hash}`")
        for key in (
            "n_rows", "n_u1", "n_u0", "n_u1_tau_above_smax", "n_u0_tau_above_smax",
            "n_u1_arrival_close_ne_window", "n_positive", "n_zero_mass", "n_one_hot",
            "n_mixed", "max_abs_composition_error", "min_positive_mass",
        ):
            audit.append(f"- {key}: {replay.audit.get(key)}")
        audit.append(f"- 首个正质量窗口: `{json.dumps(replay.audit.get('first_positive'), ensure_ascii=False)}`")
        audit.append("- q_use、oracle 概率和 target_value 没有进入参考。")
        audit.append("")
    audit.extend([
        "## 原 U",
        "",
        "原 U 同时要求 compute、network、deadline、staleness 和观测。`staleness_pass = tau <= S_max`。",
        "因此原 U 已经包含版本陈旧。新臂仍按自己的下载版本再过滤，不沿用 trace 里的 downloaded_version。",
        "",
        "## 检查点",
        "",
    ])
    for item in checkpoints:
        audit.append(f"- {item['root']}: 完整 final.pt {item['complete_final_count']} 个，未完成且排除 {item['incomplete']}")
    audit.extend([
        "",
        "本次不加载任何历史 checkpoint。partial 且没有 final.pt 的目录排除。",
        "",
        "## 调度器",
        "",
        "固定测试创建了一次非神经网络的版本更新，并完成了状态恢复。没有 SGD，也没有预测。",
        "",
        f"## 资源",
        "",
        f"- CPU 秒: {sample['cpu_seconds']:.6f}",
        f"- wall 秒: {sample['wall_seconds']:.6f}",
        f"- 峰值 RSS 字节: {sample['peak_rss_bytes']}",
        f"- 最小可用内存字节: {sample['min_available_bytes']}",
    ])
    write_text(output / "P0_ASSET_AUDIT.md", "\n".join(audit))
    spec = "\n".join([
        "# METHOD_SPEC",
        "",
        "问题：在相同的数据、上传机会、关闭网格、训练终点和最大驻留预算下，按当前目标支持保留并联合消费更新，是否能在部署预测目标上优于立即聚合和普通缓存。",
        "P0–P2 不回答预测收益。",
        "",
        "## 参考",
        "",
        "候选是原记录 U=1、合法到达、训练单元。m_j 和 c_j 来自 `reconstruct_stage1`。",
        "Design 固定为开：zeta 使用冻结的 pi_target / pi_opp，pi_min=1e-6。",
        "观测校正是滞后的 ObservationPropensity，先验 0.2，最少 5 条历史，特征为 bias、hour_block、log1p(计划工作量)。",
        "工作量按风险集长度，和原 runner 在缺少 planned_workload_pre 列时的定义相同。",
        "不乘 q_use，不用 oracle_p 或 oracle_q，也不把单一组标签当成未经验证的 one-hot。",
        "one-hot 只在该客户端观测单元确实同属一组时出现。",
        "",
        "## 调度",
        "",
        "年龄 = 关闭序号 − 到达关闭。到达关闭的年龄是 0。",
        "到达关闭由 arrival_time 的半开区间 [w, w+1) 决定。",
        "同一关闭先按 (client, registration window, retry) 注册，再按同一顺序交付，然后才关闭。",
        "注册时冻结本臂当前版本。HOLD 不增加版本，也不推动服务器优化器。",
        "每客户端最多一个 pending。更高下载版本替换旧消息；同版本保留更晚的注册时间。被替换者永久 superseded。",
        "池上限 64 个客户端。溢出按最早到达时间、再按 attempt_id 丢弃。",
        "I-Proj 在到达关闭释放。F1-Proj 在最老年龄达到 1 时释放。F2-Proj 在年龄达到 2 时释放。",
        "S-Proj 在年龄达到 2 时整池释放。否则只有 H 和 A 都非空且 D(P) <= min(D(H), D(A)) − 0.01 才互补释放。",
        "空的正质量池不求解，也不制造优化器步骤。超过年龄 2 的消息过期。终点不追加关闭。",
        "D 是 cap/ESS 可行集上的最小 0.5 L1 距离。失败的求解不能沿用上一次的值。",
        "",
        "## 进入 P2 的主块门槛",
        "",
        "主块是 measured-O。visit 只作边界，不能在主块失败后替补。",
        f"- 每个开发种子的互补释放至少 {PER_SEED_COMPLEMENT_MIN:.0%}，三个种子合计至少 {POOLED_COMPLEMENT_MIN:.0%}。分母是全部关闭。",
        f"- 每个种子至少 {CROSS_CLOSE_COMMIT_MIN:.0%} 的正质量交付在到达关闭之后 committed。分母是全部正质量交付。",
        f"- 每个种子上 S 的 100 次关闭平均 D 比 I 至少低 {MEAN_D_IMPROVEMENT_MIN}。未释放前记 1，之后沿用最近一次释放的 D。",
        "- 没有重复消费、未来信息、时间缩放或同一次释放中的重复客户端。",
        "- S 的释放时间和释放集合不能与 F1 或 F2 完全相同。",
        "- 若 F1 或 F2 的平均 D、平均驻留和 0.95 分位驻留都严格更低，则记 NO_STRUCTURAL_ADVANTAGE。",
        "",
        "这些阈值在看到结果之前写定，之后不改。",
        "",
        "## 训练配置只记录不执行",
        "",
        f"骨干 {BACKBONE}，本地 {LOCAL_STEPS} 步，服务器学习率 {SERVER_LR}，每个非空释放一次加权 SGD。",
        "builder 的本地步数默认值是 5；City Scanner 实际调用传入 2。冻结值用 2。",
        "TwoStage-Hájek 和 FedAvg-Window 有入口，但本阶段调用会拒绝执行。",
    ])
    write_text(output / "METHOD_SPEC.md", spec)
    confirmation = ["# CONFIRMATION_DATA_STATUS", ""]
    for name, context in contexts.items():
        confirmation.append(f"## {name}")
        confirmation.append(f"- 划分: {context.confirmation['split_names']}")
        confirmation.append(f"- 额外划分: {context.confirmation['unresolved_extra_split']}")
        confirmation.append(f"- {context.confirmation['reason']}")
        confirmation.append("")
    confirmation.append("P4 不能把现有 test 或 validation 说成未参与选择的独立确认。这不阻止开发集上的 P1 回放。")
    write_text(output / "CONFIRMATION_DATA_STATUS.md", "\n".join(confirmation))


def run_p0(output: Path, watch: StageWatch) -> dict:
    import critical_tests
    from reference_replay import GateStop, load_block, replay_seed

    banner("P0", watch.sample())
    fixtures = critical_tests.run_fixture_tests()
    watch.raise_for_limits()
    source_checks = confirm_source_configuration()
    if source_checks["failed"]:
        raise GateStop("BLOCKED_METHOD_IDENTITY", f"source configuration mismatch: {source_checks['failed']}", source_checks)
    contexts = {}
    replays = {}
    ledger_rows = []
    for name, seed in ((MAIN_BLOCK, 33001), (REVIEW_BLOCK, 32001)):
        print(f"P0 load {name}", flush=True)
        context = load_block(name)
        contexts[name] = context
        print(f"P0 replay {name} seed {seed}", flush=True)
        replays[name] = replay_seed(context, seed)
        watch.raise_for_limits()
        banner("P0", watch.sample())
        ledger_rows.append({
            "stage": "P0",
            "block": name,
            "dataset": context.dataset,
            "seed": seed,
            "path": str(context.trace_root / f"seed{seed}" / "training_eventtrace"),
            "split": "train",
            "columns_read": "event trace fields except use of oracle_p, oracle_q, q_use, downloaded_version, target_value",
            "labels_read": "no",
            "purpose": "stage1 reference audit",
        })
        ledger_rows.append({
            "stage": "P0",
            "block": name,
            "dataset": context.dataset,
            "seed": "",
            "path": str(context.trace_root.parent.parent),
            "split": "train_and_test_for_frozen_pi_only",
            "columns_read": UNIT_COLUMNS,
            "labels_read": "no",
            "purpose": "frozen pi and group identity",
        })
    checkpoints = [
        scan_checkpoints(ROOT / "results_joint_ou" / "round_v1"),
        scan_checkpoints(ROOT / "results_c1_cityscanner" / "round_v1"),
    ]
    source_rows = source_index()
    sample = watch.raise_for_limits()
    if "torch" in sys.modules:
        raise GateStop("BLOCKED_METHOD_IDENTITY", "torch was imported")
    write_p0_documents(output, contexts, replays, source_rows, checkpoints, source_checks, fixtures, sample)
    ledger_append(output / "DATA_USAGE_LEDGER.csv", ledger_rows)
    status = {
        "stage": "P0",
        "status": "PASS",
        "training": False,
        "prediction_gain": False,
        "implementation_hash": implementation_hash(),
        "fixtures": "PASS",
        "main_trace": replays[MAIN_BLOCK].trace_hash,
        "review_trace": replays[REVIEW_BLOCK].trace_hash,
        "sample": plain(sample),
    }
    write_json(status_path(output, "P0"), status)
    print("P0 PASS", flush=True)
    return status


def _quantile(values: list[float]) -> float | None:
    import numpy as np

    if not values:
        return None
    return float(np.quantile(np.asarray(values, dtype=np.float64), RESIDENCE_QUANTILE, method="linear"))


def _arm_summary(block: str, method: str, seed: int, attempts, scheduler, sample: dict) -> dict:
    windows = scheduler.ledger
    if [row["window_id"] for row in windows] != list(range(NUM_WINDOWS)):
        scheduler.faults.append("window grid was rescaled or incomplete")
    committed = []
    cross = 0
    positive = 0
    residence = []
    for attempt in attempts:
        if attempt.positive:
            positive += 1
        message = scheduler.terminal.get(attempt.attempt_id)
        if message is None:
            scheduler.faults.append(f"missing terminal state {attempt.attempt_id}")
            continue
        if message.state == "committed" and attempt.positive:
            committed.append(message)
            residence.append(int(message.residence))
            if int(message.commit_close) > int(attempt.arrival_close):
                cross += 1
    releases = tuple((row["window_id"], tuple(row["committed_attempt_ids"])) for row in windows if row["action"] == "RELEASE")
    return {
        "block": block,
        "protocol": PROTOCOL_NAME,
        "method": method,
        "seed": int(seed),
        "split": "development",
        "checkpoint": "none",
        "n_windows": len(windows),
        "complementary_releases": sum(row["reason"] == "COMPLEMENTARY_RELEASE" for row in windows),
        "complementary_rate": sum(row["reason"] == "COMPLEMENTARY_RELEASE" for row in windows) / NUM_WINDOWS,
        "positive_delivered": positive,
        "cross_close_committed": cross,
        "cross_close_commit_rate": (cross / positive) if positive else 0.0,
        "mean_D": sum(row["d_carried"] for row in windows) / NUM_WINDOWS,
        "mean_residence": (sum(residence) / len(residence)) if residence else None,
        "p95_residence": _quantile(residence),
        "n_committed": len(committed),
        "n_superseded": sum(message.state == "superseded" for message in scheduler.terminal.values()),
        "n_overflow": scheduler.overflow_count,
        "n_expired": sum(message.state == "expired" for message in scheduler.terminal.values()),
        "n_endpoint_unconsumed": sum(message.state == "endpoint_unconsumed" for message in scheduler.terminal.values()),
        "n_version_rejected": sum(message.state == "version_rejected" for message in scheduler.terminal.values()),
        "overflow_workload": scheduler.overflow_workload,
        "overflow_group_mass": scheduler.overflow_group_mass.tolist(),
        "faults": list(scheduler.faults),
        "release_signature": releases,
        "cpu_seconds": sample["cpu_seconds"],
        "wall_seconds": sample["wall_seconds"],
        "peak_rss_bytes": sample["peak_rss_bytes"],
        "min_available_bytes": sample["min_available_bytes"],
        "windows": windows,
        "scheduler": scheduler,
    }


def _dominates(cache: dict, target: dict) -> bool:
    if cache["mean_residence"] is None or target["mean_residence"] is None:
        return False
    if cache["p95_residence"] is None or target["p95_residence"] is None:
        return False
    return (
        cache["mean_D"] < target["mean_D"]
        and cache["mean_residence"] < target["mean_residence"]
        and cache["p95_residence"] < target["p95_residence"]
    )


def judge_main(summaries: list[dict]) -> dict:
    rows = [row for row in summaries if row["block"] == MAIN_BLOCK]
    unmet = []
    identical = []
    dominated = []
    for seed in sorted({row["seed"] for row in rows}):
        by_method = {row["method"]: row for row in rows if row["seed"] == seed}
        ess = by_method["S-Proj"]
        immediate = by_method["I-Proj"]
        if ess["release_signature"] == by_method["F1-Proj"]["release_signature"]:
            identical.append({"seed": seed, "matches": "F1-Proj"})
        if ess["release_signature"] == by_method["F2-Proj"]["release_signature"]:
            identical.append({"seed": seed, "matches": "F2-Proj"})
        if ess["complementary_rate"] < PER_SEED_COMPLEMENT_MIN:
            unmet.append({"seed": seed, "metric": "complementary_rate", "value": ess["complementary_rate"], "threshold": PER_SEED_COMPLEMENT_MIN})
        if ess["cross_close_commit_rate"] < CROSS_CLOSE_COMMIT_MIN:
            unmet.append({"seed": seed, "metric": "cross_close_commit_rate", "value": ess["cross_close_commit_rate"], "threshold": CROSS_CLOSE_COMMIT_MIN})
        gap = immediate["mean_D"] - ess["mean_D"]
        if gap < MEAN_D_IMPROVEMENT_MIN:
            unmet.append({"seed": seed, "metric": "mean_D_improvement", "value": gap, "threshold": MEAN_D_IMPROVEMENT_MIN})
        for method in ("F1-Proj", "F2-Proj"):
            if _dominates(by_method[method], ess):
                dominated.append(seed)
    pooled = sum(row["complementary_releases"] for row in rows if row["method"] == "S-Proj") / (3 * NUM_WINDOWS)
    if pooled < POOLED_COMPLEMENT_MIN:
        unmet.append({"seed": "pooled", "metric": "complementary_rate", "value": pooled, "threshold": POOLED_COMPLEMENT_MIN})
    faults = [row for row in summaries if row["faults"]]
    if faults:
        status = "INVALID_IMPLEMENTATION"
    elif identical:
        status = "NO_ADAPTIVE_MECHANISM"
    elif dominated:
        status = "NO_STRUCTURAL_ADVANTAGE"
    elif unmet:
        status = "NO_OPPORTUNITY"
    else:
        status = "PASS"
    return {"status": status, "unmet": unmet, "identical": identical, "dominated": dominated, "pooled_complement_rate": pooled}


def run_p1(output: Path, watch: StageWatch) -> dict:
    import pandas as pd

    from cache_scheduler import run_cache
    from reference_replay import BLOCKS, GateStop, load_block, replay_seed
    from support_distance import DistanceFailure

    banner("P1", watch.sample())
    contexts = {MAIN_BLOCK: load_block(MAIN_BLOCK), REVIEW_BLOCK: load_block(REVIEW_BLOCK)}
    summaries = []
    event_rows = []
    window_rows = []
    ledger_rows = []
    seeds = {"measured-O": (33001, 33002, 33003), "visit": (32001, 32002, 32003)}
    for block, seed_list in seeds.items():
        for seed in seed_list:
            print(f"P1 replay {block} seed {seed}", flush=True)
            replay = replay_seed(contexts[block], seed)
            ledger_rows.append({
                "stage": "P1",
                "block": block,
                "dataset": contexts[block].dataset,
                "seed": seed,
                "path": str(BLOCKS[block]["trace_root"] / f"seed{seed}" / "training_eventtrace"),
                "split": "development",
                "columns_read": "same frozen reference as P0",
                "labels_read": "no",
                "purpose": "no-training cache replay",
            })
            for method in CACHE_ARMS:
                print(f"P1 arm {block} {method} seed {seed}", flush=True)
                try:
                    scheduler = run_cache(method, replay.attempts, contexts[block].mu, NUM_WINDOWS)
                except DistanceFailure as exc:
                    status = "INFEASIBLE_CONFIGURATION" if "INFEASIBLE_CONFIGURATION" in str(exc) else "SOLVER_PAUSE"
                    raise GateStop(status, str(exc), {"block": block, "seed": seed, "method": method}) from exc
                sample = watch.raise_for_limits()
                summary = _arm_summary(block, method, seed, replay.attempts, scheduler, sample)
                summaries.append(summary)
                for row in summary["windows"]:
                    window_rows.append({
                        "block": block,
                        "protocol": PROTOCOL_NAME,
                        "method": method,
                        "seed": seed,
                        "split": "development",
                        "checkpoint": "none",
                        "window_id": row["window_id"],
                        "action": row["action"],
                        "reason": row["reason"],
                        "n_H": row["n_H"],
                        "n_A": row["n_A"],
                        "n_P": row["n_P"],
                        "d_h": row["d_h"],
                        "d_a": row["d_a"],
                        "d_p": row["d_p"],
                        "d_carried": row["d_carried"],
                        "committed_attempt_ids": ";".join(row["committed_attempt_ids"]),
                        "version_after": row["version_after"],
                        "cpu_seconds": sample["cpu_seconds"],
                        "wall_seconds": sample["wall_seconds"],
                        "peak_rss_bytes": sample["peak_rss_bytes"],
                        "status": "replay",
                        "evidence_path": "P1_EVENT_LEDGER.parquet",
                    })
                for attempt in replay.attempts:
                    message = scheduler.terminal.get(attempt.attempt_id)
                    event_rows.append({
                        "block": block,
                        "protocol": PROTOCOL_NAME,
                        "method": method,
                        "seed": seed,
                        "attempt_id": attempt.attempt_id,
                        "client_id": attempt.client_id,
                        "registration_window": attempt.registration_window,
                        "arrival_close": attempt.arrival_close,
                        "m": attempt.m,
                        "c0": attempt.composition[0],
                        "c1": attempt.composition[1],
                        "c2": attempt.composition[2],
                        "c3": attempt.composition[3],
                        "state": None if message is None else message.state,
                        "commit_close": None if message is None else message.commit_close,
                        "release_reason": None if message is None else message.release_reason,
                        "download_version": None if message is None else message.download_version,
                        "residence_closes": None if message is None else message.residence,
                        "raw_workload": attempt.raw_workload,
                    })
                summary.pop("scheduler", None)
                summary.pop("windows", None)
            banner("P1", watch.sample())
    judgment = judge_main(summaries)
    sample = watch.sample()
    summary_fields = [
        "block", "protocol", "method", "seed", "split", "checkpoint", "complementary_releases",
        "complementary_rate", "positive_delivered", "cross_close_committed", "cross_close_commit_rate",
        "mean_D", "mean_residence", "p95_residence", "n_committed", "n_superseded", "n_overflow",
        "n_expired", "n_endpoint_unconsumed", "n_version_rejected", "overflow_workload",
        "cpu_seconds", "wall_seconds", "peak_rss_bytes", "min_available_bytes", "status", "evidence_path",
    ]
    with (output / "P1_SUMMARY.csv").open("w", encoding="utf-8", newline="") as handle:
        writer = csv.DictWriter(handle, fieldnames=summary_fields)
        writer.writeheader()
        for row in summaries:
            writer.writerow({
                key: row.get(key, "") if key not in {"status", "evidence_path"} else (
                    judgment["status"] if key == "status" else "P1_DECISION.md"
                )
                for key in summary_fields
            })
    pd.DataFrame(window_rows).to_csv(output / "P1_WINDOW_METRICS.csv", index=False)
    pd.DataFrame(event_rows).to_parquet(output / "P1_EVENT_LEDGER.parquet", index=False)
    ledger_append(output / "DATA_USAGE_LEDGER.csv", ledger_rows)
    lines = [
        "# P1_DECISION",
        "",
        f"- 主块状态：{judgment['status']}",
        f"- 合并互补释放比例：{judgment['pooled_complement_rate']}",
        f"- 未满足项：`{json.dumps(judgment['unmet'], ensure_ascii=False)}`",
        f"- 与普通缓存相同的释放：`{json.dumps(judgment['identical'], ensure_ascii=False)}`",
        f"- 普通缓存严格占优的种子：{judgment['dominated']}",
        "",
        "visit 的数字在 P1_SUMMARY.csv，只作为边界。它不能替换 measured-O。",
        "正权重使用要等训练时的实际 alpha，这次回放不把它算作已验证。",
        "",
        "无新增训练、尚无预测收益结果。",
    ]
    write_text(output / "P1_DECISION.md", "\n".join(lines))
    status = {
        "stage": "P1",
        "status": judgment["status"],
        "judgment": plain(judgment),
        "training": False,
        "prediction_gain": False,
        "sample": plain(sample),
    }
    write_json(status_path(output, "P1"), status)
    if judgment["status"] != "PASS":
        write_text(
            output / "FAILURE_REPORT_P1.md",
            failure_markdown("P1", judgment["status"], json.dumps(judgment["unmet"], ensure_ascii=False), sample, "P0 and the P1 replay", "P2 P3 P4"),
        )
    print(f"P1 {judgment['status']}", flush=True)
    return status


def run_p2(output: Path, watch: StageWatch) -> dict:
    import critical_tests
    import pandas as pd

    from cache_scheduler import run_cache
    from reference_replay import load_block, replay_seed

    banner("P2", watch.sample())
    fixtures = critical_tests.run_fixture_tests()
    context = load_block(MAIN_BLOCK)
    replay = replay_seed(context, 33001)
    scheduler = run_cache("S-Proj", replay.attempts, context.mu, NUM_WINDOWS)
    previous = pd.read_csv(output / "P1_WINDOW_METRICS.csv")
    subset = previous.loc[
        (previous["block"] == MAIN_BLOCK) & (previous["method"] == "S-Proj") & (previous["seed"] == 33001) & (previous["window_id"] < 5)
    ].sort_values("window_id")
    mismatches = []
    for row, record in zip(subset.itertuples(index=False), scheduler.ledger[:5]):
        if int(row.window_id) != int(record["window_id"]) or str(row.reason) != str(record["reason"]):
            mismatches.append({"window_id": int(record["window_id"]), "p1": str(row.reason), "p2": str(record["reason"])})
        p1_ids = "" if pd.isna(row.committed_attempt_ids) else str(row.committed_attempt_ids)
        if p1_ids != ";".join(record["committed_attempt_ids"]):
            mismatches.append({"window_id": int(record["window_id"]), "field": "committed_attempt_ids"})
    positive = next(attempt for attempt in replay.attempts if attempt.positive)
    composition_sum = sum(positive.composition)
    if abs(composition_sum - 1.0) > 1e-6:
        mismatches.append({"attempt_id": positive.attempt_id, "composition_sum": composition_sum})
    if "target_value" in replay.audit["columns"]:
        mismatches.append({"field": "target_value"})
    sample = watch.raise_for_limits()
    if mismatches or scheduler.faults:
        raise RuntimeError(f"INVALID_IMPLEMENTATION: {mismatches or scheduler.faults}")
    if "torch" in sys.modules:
        raise RuntimeError("INVALID_IMPLEMENTATION: torch imported")
    write_json(output / "P2_CRITICAL_TESTS.json", {"fixtures": fixtures, "fragment_mismatches": mismatches, "status": "PASS"})
    diff = subprocess.run(["git", "diff", "--", "src"], cwd=ROOT, capture_output=True, text=True, check=False)
    status_short = subprocess.run(["git", "status", "--short"], cwd=ROOT, capture_output=True, text=True, check=False)
    write_text(output / "CODE_DIFF.md", "\n".join([
        "# CODE_DIFF",
        "",
        "src 没有为本次实验修改。" if not diff.stdout.strip() else "src 出现了差异，需要复查。",
        "",
        "```",
        diff.stdout.strip(),
        "```",
        "",
        "工作区短状态：",
        "",
        "```",
        status_short.stdout.strip(),
        "```",
    ]))
    write_text(output / "P2_IMPLEMENTATION_REPORT.md", "\n".join([
        "# P2_IMPLEMENTATION_REPORT",
        "",
        "四个固定测试和 measured-O seed 33001 的前五个关闭都与 P1 一致。",
        "调度器独立于旧的 lifecycle 控制器。训练入口没有执行。",
        "保存的状态包含池、版本、随机数、优化器计数、账本和预算。只保存权重会被拒绝。",
        f"CPU 秒 {sample['cpu_seconds']:.6f}，wall 秒 {sample['wall_seconds']:.6f}。",
        "",
        "无新增训练、尚无预测收益结果。",
    ]))
    write_text(output / "TRAINING_REQUEST.md", "\n".join([
        "# TRAINING_REQUEST",
        "",
        "P0–P2 已完成，训练尚未开始。",
        "",
        "请求批准后才可以进入 P3a。批准前不训练。",
        "第一批只在 measured-O 的开发种子上训练 I-Proj、F1-Proj、F2-Proj 和 S-Proj。",
        "visit 仍只作边界。Traffic、SensorScope 和 U-Air 不进入这一批。",
        "TwoStage-Hájek 与 FedAvg-Window 不在这四个缓存臂的对照里启动。",
        "不降低门槛，不增加种子，不改关闭网格、目标或分组。",
        "P4 的 bootstrap 需要另一次预算批准。现有划分不能声称独立确认。",
        "",
        "无新增训练、尚无预测收益结果。",
    ]))
    status = {"stage": "P2", "status": "PASS", "training": False, "prediction_gain": False, "sample": plain(sample)}
    write_json(status_path(output, "P2"), status)
    print("P2 PASS", flush=True)
    return status


def write_decision(output: Path) -> None:
    p0 = existing_status(output, "P0") or {}
    p1 = existing_status(output, "P1") or {}
    p2 = existing_status(output, "P2") or {}
    judgment = p1.get("judgment", {})
    ran = p0.get("status") == "PASS"
    lines = [
        "# DECISION_REPORT",
        "",
        "1. 跨窗口保留是否带来互补：" + (
            "主块达到了预先写定的互补、跨关闭消费和 D 门槛。"
            if p1.get("status") == "PASS"
            else "回放尚未完成。" if not ran else f"主块状态是 {p1.get('status', '尚未运行')}。"
        ),
        "2. 缓存是否改变消费时间：" + (
            "P1 账本分开记录了到达关闭和 committed 关闭。正权重仍待训练核验。"
            if p1 else "消费时间尚未回放。"
        ),
        "3. 是否优于普通缓存：" + (
            "开发回放没有显示 F1 或 F2 在 D 和驻留上同时严格占优，也没有与它们的释放完全相同。"
            if p1.get("status") == "PASS"
            else "还不能把主块说成优于普通缓存。"
        ),
        "4. 是否变成任务收益：无新增训练、尚无预测收益结果。",
        "5. 相对旧证据：" + (
            "这次回放实现了 HOLD/CONSUME，没有把旧 xw 池里当窗全消费的零结果改写成新机制。"
            if ran else "调度代码已经写在新目录，但还没有在轨迹上执行。旧结果目录没有改写。"
        ),
        f"6. 成本：见 BUDGET_LEDGER.json。P0={p0.get('status')}，P1={p1.get('status')}，P2={p2.get('status')}。",
        "7. 独立确认：" + (
            "没有未参与模型选择的日期、区域或批次。P4 不能声称独立确认。"
            if ran else "划分尚未审计。"
        ),
        "",
        f"合并互补比例：{judgment.get('pooled_complement_rate', '未计算')}",
        "",
        "无新增训练、尚无预测收益结果。",
    ]
    write_text(output / "DECISION_REPORT.md", "\n".join(lines))


def main() -> int:
    parser = argparse.ArgumentParser()
    parser.add_argument("--stage", required=True, choices=["P0", "P1", "P2"])
    parser.add_argument("--output", required=True)
    parser.add_argument("--resume", action="store_true")
    args = parser.parse_args()
    output = Path(args.output).resolve()
    if output != EXPECTED_OUTPUT:
        print("output must be results_support_consumption/round_v1", flush=True)
        return 2
    output.mkdir(parents=True, exist_ok=True)
    if running_path(output, args.stage).exists():
        print("ACCOUNTING_INCOMPLETE: previous attempt did not close its ledger", flush=True)
        return 3
    resumable = {"RESOURCE_PAUSE", "RESOURCE_EXIT", "RESOURCE_BUDGET", "ACCOUNTING_INCOMPLETE"}
    current = existing_status(output, args.stage)
    if current is not None and current.get("status") not in resumable:
        print(f"{args.stage} already recorded as {current.get('status')}", flush=True)
        return 0 if current.get("status") == "PASS" else 1
    if current is not None:
        archive = output / f"{args.stage}_STATUS_{current.get('status')}_previous.json"
        if not archive.exists():
            status_path(output, args.stage).replace(archive)
    del args.resume
    try:
        started = time.perf_counter()
        free = require_start_memory()
        print(f"available_bytes={free}", flush=True)
        require_prior(output, args.stage)
    except AccountingError as exc:
        text = str(exc)
        status = text.split(":", 1)[0]
        usage = process_tree_usage()
        sample = {
            "available_bytes": available_bytes(),
            "cpu_seconds": usage["cpu_seconds"],
            "wall_seconds": time.perf_counter() - started,
            "rss_bytes": usage["rss_bytes"],
            "peak_rss_bytes": usage["peak_rss_bytes"],
            "complete": usage["complete"],
            "note": "stopped before heavy imports",
        }
        write_failure(output, args.stage, status, text, sample, {"available_bytes": sample["available_bytes"]}, "none", "P0 P1 P2 P3 P4")
        rows = load_budget(output)
        rows.append({"stage": args.stage, "status": status, **plain(sample)})
        save_budget(output, rows)
        write_decision(output)
        print(text, flush=True)
        return 3
    prior_cpu, prior_wall = prior_cost(output, args.stage)
    cpu_budget = CPU_BUDGET[args.stage] - prior_cpu
    wall_budget = WALL_BUDGET[args.stage] - prior_wall
    if cpu_budget <= 0 or wall_budget <= 0:
        print("RESOURCE_BUDGET: no remaining stage budget", flush=True)
        return 3
    watch = StageWatch(args.stage, cpu_budget, wall_budget)
    write_json(running_path(output, args.stage), {"stage": args.stage, "status": "running"})
    try:
        if args.stage == "P0":
            result = run_p0(output, watch)
        elif args.stage == "P1":
            result = run_p1(output, watch)
        else:
            result = run_p2(output, watch)
        sample = watch.sample()
        rows = load_budget(output)
        rows.append({"stage": args.stage, "status": result["status"], **plain(sample)})
        save_budget(output, rows)
        running_path(output, args.stage).unlink(missing_ok=True)
        write_decision(output)
        return 0 if result["status"] == "PASS" else 1
    except Exception as exc:
        sample = {}
        try:
            sample = watch.sample()
        except Exception:
            sample = {"cpu_seconds": None, "wall_seconds": None}
        status = getattr(exc, "status", None) or "INVALID_IMPLEMENTATION"
        if isinstance(exc, AccountingError):
            text = str(exc)
            status = text.split(":", 1)[0]
        evidence = getattr(exc, "evidence", {})
        if not status_path(output, args.stage).is_file():
            write_failure(output, args.stage, status, str(exc), sample, evidence, args.stage, "later stages")
        rows = load_budget(output)
        rows.append({"stage": args.stage, "status": status, **plain(sample)})
        save_budget(output, rows)
        running_path(output, args.stage).unlink(missing_ok=True)
        write_decision(output)
        traceback.print_exc()
        return 1


if __name__ == "__main__":
    raise SystemExit(main())

