"""Second pass: concept-level search of the V2.3 design doc, written to a UTF-8 report."""
from __future__ import annotations

import pathlib
import re

ROOT = pathlib.Path(r"C:\Cursor\raven.mcs")
TXT = ROOT / "_r13_build/DESIGN_V23_EXTRACT.txt"
OUT = ROOT / "_r13_build/DESIGN_V23_GUARD_SEARCH.md"
text = TXT.read_text(encoding="utf-8")
lines = text.split("\n")

L = []
A = L.append
A("# V2.3 实验设计方案 — 与「复用/封存/守卫」相关的检索结果")
A("")
A(f"来源：`参考文件/RAVEN-MCS_V2.3_实验设计方案.docx`（mtime 2026-07-26 20:39，405 866 B）")
A(f"提取正文 {len(text)} 字符，{len(lines)} 行。")
A("")

CONCEPTS = {
    "守卫/封锁类": r"guard|守卫|封锁|阻断|拦截|禁止调度|不可重跑|schedul",
    "复用/重跑类": r"复用|重跑|重训|重新训练|沿用|直接读取|同一批|一次生成|frozen run|no.?rerun",
    "封存/封印类": r"封印|封存|seal|sealed|freeze|冻结",
    "金丝雀/canary": r"金丝雀|canary|canary seed",
    "E2/E3 协议块": r"\bE2\b|\bE3\b|complete_aligned|protocol_closure|reuse_guard|REUSE_ONLY",
    "种子号": r"\b3[01]00[0-9]\b|30020|31001",
    "NSW/交通": r"NSW|交通",
}
A("## 1. 概念级命中")
A("")
A("| 概念组 | 命中行数 |")
A("| --- | --- |")
found_lines = set()
for name, pat in CONCEPTS.items():
    hit = [i for i, ln in enumerate(lines) if re.search(pat, ln, re.IGNORECASE)]
    A(f"| {name} | {len(hit)} |")
    found_lines.update(hit)
A("")

A("## 2. 逐条上下文（去重后按行号）")
A("")
for i in sorted(found_lines):
    ln = lines[i].strip()
    if not ln:
        continue
    A(f"- L{i+1}: {ln[:400]}")
A("")

A("## 3. 文档的全部标题（章节结构）")
A("")
for i, ln in enumerate(lines):
    if ln.startswith("[Heading") or ln.startswith("[Title"):
        A(f"- L{i+1}: {ln}")
A("")

A("## 4. 与「可复现/冻结/交付」相关的段落原文")
A("")
REPRO = r"复现|可复现|冻结|封|锁定|manifest|hash|哈希|审计|一致性|交付|artifact|工件"
for i, ln in enumerate(lines):
    if re.search(REPRO, ln, re.IGNORECASE) and len(ln.strip()) > 3:
        A(f"- L{i+1}: {ln.strip()[:400]}")
OUT.write_text("\n".join(L), encoding="utf-8")
print("wrote", OUT, len(L), "lines")
