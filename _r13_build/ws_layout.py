"""Generate WORKSPACE_LAYOUT.md: a categorised index of every top-level entry."""
from __future__ import annotations

import csv
import pathlib
import time

ROOT = pathlib.Path(r"C:\Cursor\raven.mcs")
INV = ROOT / "_r13_build/workspace_inventory.csv"

rows = []
for r in csv.DictReader(INV.open(encoding="utf-8")):
    if int(r["depth"]) != 1:
        continue
    rows.append({"name": r["path"], "files": int(r["files"]), "gb": float(r["GB"])})

mt = {}
for r in rows:
    p = ROOT / r["name"]
    try:
        mt[r["name"]] = time.strftime("%Y-%m-%d", time.localtime(p.stat().st_mtime))
    except OSError:
        mt[r["name"]] = "?"


def classify(name: str) -> tuple[str, str, str]:
    """-> (category, purpose, movability)"""
    n = name
    C_PAPER = "1 论文与投稿"
    C_CODE = "2 代码与配置"
    C_DATA = "3 数据"
    C_FROZEN = "4 冻结证据与运行产物"
    C_RES = "5 实验轮次"
    C_REVIEW = "6 评审与报告"
    C_LIT = "7 文献检索"
    C_SCRATCH = "8 临时与代理工作区"
    C_SYS = "9 系统与技能"

    if n == "TO_OVERLEAF_paper_tmc_r1_clean":
        return C_PAPER, "**规范论文目录**（main.tex / appendix.tex / supplemental.tex / 图 / bib）", "不可移动"
    if n == "RAVEN_MCS_PUBLIC_REPRO_R1":
        return C_PAPER, "论文 Availability 引用的公开复现包（含 submission_evidence 索引）", "不可移动"
    if n.startswith(("RAVEN_MCS_FINAL", "RAVEN_MCS_SAG", "RAVEN_MCS_TMC", "manuscript_evidence_closure",
                     "paper_ready", "paper_tmc_r1", "ADVISOR_PACKAGE", "_paper_work", "post_review",
                     "deliverables", "docs", "参考文件", "archive")):
        return C_PAPER, "论文相关的封存/打包/参考材料", "需批准"
    if n in {"src", "scripts", "configs", "tests", "tools", "schemas", "notebooks"} or \
       n.startswith(("Makefile", "pyproject", "requirements", "environment", "check_", ".git")) or \
       n == ".vscode":
        return C_CODE, "代码/配置/测试", "不可移动"
    if n == "data":
        return C_DATA, "原始与处理后的数据（IoT 数据集）", "不可移动"
    if n in {"artifacts", "tdrive_protocol_seal_r1", "outputs", "evidence", "logs", "snapshots"}:
        return C_FROZEN, "冻结证据 / 运行日志 / 快照（被报告与台账引用）", "不可移动"
    if n.startswith("results_"):
        return C_RES, "单轮实验或诊断输出", "不可移动"
    if n in {"ccf-review-report", "ccfa-review-reports", "_acl_reports", "ISSUES.md", "STATUS.md",
             "CHANGELOG.md", "DESIGN_GATE_ALIGNMENT_REPORT.md", "REVIEW_ccf_raven_tmc_r1_c1hybrid.md",
             "README.md"}:
        return C_REVIEW, "评审、修复报告、项目状态与变更记录", "不可移动"
    if n.startswith("SAG_") and n.endswith(".md"):
        return C_REVIEW, "历史修复计划文档", "需批准"
    if n.startswith("literature-search-"):
        return C_LIT, "文献检索产物（ccf-literature-searcher 输出）", "需批准"
    if n in {".r11_work", ".rb_work", ".m7_work", ".r3_work", ".s1_work", "_r13_build", "_tmp_pack",
             "_tmp_ref", "_probe_new", ".sync_diag", ".pytest_cache", ".upstream_backup",
             ".codex-remote-attachments", "tmp"} or n.startswith("_handoff_sag"):
        return C_SCRATCH, "临时脚本 / 代理工作目录 / 备份（README 类报告引用其路径）", "需批准"
    if n in {".dsh", "CCFA-Skills"}:
        return C_SYS, "DSH 运行时与 CCFA 技能库", "不可移动"
    return C_SCRATCH, "未归类", "需批准"


groups: dict[str, list] = {}
for r in rows:
    cat, purpose, mov = classify(r["name"])
    groups.setdefault(cat, []).append({**r, "purpose": purpose, "mov": mov})

total_files = sum(r["files"] for r in rows)
total_gb = sum(r["gb"] for r in rows)

L = ["# 工作区分区索引（workspace layout）", "",
     f"生成时间：{time.strftime('%Y-%m-%d %H:%M')}　·　顶层条目 **{len(rows)}** 个"
     f"　·　文件 **{total_files:,}** 个　·　合计 **{total_gb:.1f} GB**", "",
     "用途：47 GB / 29 万文件的工作区靠肉眼无法导航。这份索引把每个顶层条目归到九类之一，"
     "并标注**能否移动**。", "",
     "> **重要结论：不要用「移动目录」来整理。** 逐个名字做过引用检查，几乎所有目录都被别处引用"
     "（`tmp` 578 次、`outputs` 2 607 次、`evidence` 4 090 次、`deliverables` 1 972 次；"
     "`results_traffic_e2` / `results_w1_ladder` 被 `ccf-review-report/PAPER_CLAIM_EVIDENCE_MAP.md` 引用；"
     "`_handoff_sag_*` / `paper_ready_*` 被 `scripts/*.py` 引用）。移动任一目录都会打断论文证据链、"
     "脚本路径或报告索引。", "",
     "| 类别 | 条目数 | 文件数 | 体积 |", "|---|---:|---:|---:|"]
for cat in sorted(groups):
    g = groups[cat]
    L.append(f"| {cat} | {len(g)} | {sum(x['files'] for x in g):,} | {sum(x['gb'] for x in g):.2f} GB |")
L.append(f"| **合计** | **{len(rows)}** | **{total_files:,}** | **{total_gb:.1f} GB** |")

for cat in sorted(groups):
    g = sorted(groups[cat], key=lambda x: -x["gb"])
    L += ["", f"## {cat}", "",
          "| 条目 | 文件 | 体积 | 最后修改 | 内容 / 用途 | 可移动性 |",
          "|---|---:|---:|---|---|---|"]
    for x in g:
        L.append(f"| `{x['name']}` | {x['files']:,} | {x['gb']*1000:.0f} MB | {mt[x['name']]} | "
                 f"{x['purpose']} | {x['mov']} |")

L += ["", "## 空间分析与处置建议", "",
      "### 体量集中在 2026-10-13~19 的四轮观测反馈试点", "",
      "| 目录 | 体积 | 日期 |", "|---|---:|---|"]
for x in sorted(rows, key=lambda r: -r["gb"])[:6]:
    L.append(f"| `{x['name']}` | {x['gb']:.2f} GB | {mt[x['name']]} |")
L += ["", "这四轮合计约 **17.1 GB**，占全工作区 36 %。它们都是 `results_*`，"
      "属于实验轮次而不是已发布证据，**是否长期保留由你决定**（删除后无法从论文侧复原）。", "",
      "### 三档处置", "",
      "| 档 | 动作 | 候选 | 可回收 |", "|---|---|---|---|",
      "| A | 可直接删除（可再生） | `.pytest_cache`、`.sync_diag`、`_probe_new`、`_r13_build` 的 "
      "`build_*` 子目录 | 小（< 0.05 GB） |",
      "| B | 打包归档到 `_archive_2026-11/`（保留但不占顶层） | 6 个 `literature-search-*`、"
      "7 个 `_handoff_sag_*`、5 个 `SAG_*_PLAN.md`、`.upstream_backup` | ≈ 0.3 GB |",
      "| C | **需你逐项确认后**才可删 | 17 GB 的四轮试点 + 其余 `results_*` 中已不再引用的轮次 | 最高 20+ GB |",
      "",
      "**我没有执行任何 A/B/C 动作。** 删除证据类目录不可逆，且部分目录仍被索引与报告引用；"
      "按项目一贯纪律，这类操作必须先由你点头。", ""]

out = ROOT / "WORKSPACE_LAYOUT.md"
out.write_text("\n".join(L) + "\n", encoding="utf-8")
print(f"wrote {out}  ({out.stat().st_size} B, {len(L)} lines, {len(rows)} entries)")
for cat in sorted(groups):
    g = groups[cat]
    print(f"  {cat:<26} {len(g):>3} entries  {sum(x['gb'] for x in g):>7.2f} GB")
