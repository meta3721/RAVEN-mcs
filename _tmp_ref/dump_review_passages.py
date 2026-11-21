"""Dump the passages a reviewer of the post-Option-1 manuscript would read."""
import pymupdf

import pathlib

doc = pymupdf.open("main.pdf")
txt = "\n".join(p.get_text() for p in doc)
flat = " ".join(txt.split())
out = []


def show(tag, anchor, span):
    i = flat.find(anchor)
    out.append("=" * 25 + " " + tag + " " + "=" * 25)
    out.append(flat[i:i + span] if i >= 0 else "NOT FOUND: " + anchor)
    out.append("")


show("ABSTRACT", "Abstract", 2000)
show("DESIGN FACTOR", "Design factor of window", 1700)
show("ALGORITHM", "Window-close RAVEN-MCS with the Design", 900)
show("TABLE III ROWS", "Development table for the main comparison", 2400)
doc.close()
pathlib.Path("../_tmp_ref/review_passages.txt").write_text("\n".join(out), encoding="utf-8")
print("written")
