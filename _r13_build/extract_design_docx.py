"""Extract RAVEN-MCS_V2.3 design docx to text, and search it for reuse/seal/guard concepts."""
from __future__ import annotations

import json
import pathlib
import re

from docx import Document
from docx.table import Table
from docx.text.paragraph import Paragraph

ROOT = pathlib.Path(r"C:\Cursor\raven.mcs")
DOCX = ROOT / "参考文件/RAVEN-MCS_V2.3_实验设计方案.docx"
OUTTXT = ROOT / "_r13_build/DESIGN_V23_EXTRACT.txt"


def iter_block_items(parent):
    from docx.oxml.ns import qn

    body = parent.element.body
    for child in body.iterchildren():
        if child.tag == qn("w:p"):
            yield Paragraph(child, parent)
        elif child.tag == qn("w:tbl"):
            yield Table(child, parent)


doc = Document(str(DOCX))
lines: list[str] = []
n_par = n_tbl = 0
for block in iter_block_items(doc):
    if isinstance(block, Paragraph):
        t = block.text.rstrip()
        if t:
            style = (block.style.name or "") if block.style is not None else ""
            lines.append(f"[{style}] {t}" if style and style.lower() not in ("normal", "body text") else t)
            n_par += 1
    else:
        n_tbl += 1
        lines.append(f"--- TABLE {n_tbl} ---")
        for row in block.rows:
            cells = [c.text.replace("\n", " / ").strip() for c in row.cells]
            lines.append(" | ".join(cells))
        lines.append("--- END TABLE ---")

text = "\n".join(lines)
OUTTXT.write_text(text, encoding="utf-8")

print(f"docx: {DOCX.name}")
print(f"paragraphs with text: {n_par} | tables: {n_tbl} | extracted chars: {len(text)}")
print(f"wrote {OUTTXT}")
print()

KEYWORDS = ["复用", "重跑", "重训", "封印", "封存", "封存块", "金丝雀", "canary", "guard", "守卫",
            "sealed", "seal", "REUSE", "reuse", "禁止", "阻断", "拦截", "schedul", "30001", "30020",
            "31001", "traffic", "交通", "NSW", "fedavg_window", "twostate", "twostage", "flamf",
            "fedasync", "五", "排除", "一次性", "不可重"]
hits = {}
for kw in KEYWORDS:
    idx = [m.start() for m in re.finditer(re.escape(kw), text)]
    if idx:
        hits[kw] = len(idx)
print("keyword hit counts (case-sensitive unless the keyword is lower-case):")
for kw, n in sorted(hits.items(), key=lambda kv: -kv[1]):
    print(f"   {kw!r}: {n}")

print()
print("=== context for the strongest signals ===")
for kw in ["复用", "重跑", "封存", "封印", "金丝雀", "canary", "guard", "守卫", "sealed", "阻断", "拦截", "30001", "31001", "traffic", "交通"]:
    for m in list(re.finditer(re.escape(kw), text))[:3]:
        s = max(0, m.start() - 90)
        e = min(len(text), m.end() + 90)
        snippet = text[s:e].replace("\n", " ")
        print(f"  [{kw}] ...{snippet}...")
print()
print("=== does the doc mention any error code or guard module path? ===")
for pat in ["REUSED", "DUPLICATE", "REUSE_ONLY", "traffic_reuse_guard", "reuse_guard", "protocol_closure",
            "E2_TRAFFIC", "CanaryTrafficSealed"]:
    n = len(re.findall(re.escape(pat), text))
    print(f"   {pat}: {n}")
