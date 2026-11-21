"""Revert only the [10] entry (morishita2026who) to its original Morishita/arXiv record."""
from __future__ import annotations

import hashlib
import pathlib
import re

BIB = pathlib.Path(r"C:\Cursor\raven.mcs\TO_OVERLEAF_paper_tmc_r1_clean/reference.bib")
raw = BIB.read_bytes()
pre = hashlib.sha256(raw).hexdigest()
text = raw.decode("utf-8")
print(f"pre : {len(raw)} B  sha256 {pre[:16]}")

ORIGINAL = """@misc{morishita2026who,
  title={Who Trains Matters: Federated Learning under Enrollment and Participation Selection Biases},
  author={Morishita, Gota},
  howpublished={arXiv preprint arXiv:2604.26604},
  year={2026},
  month={Apr},
  url={https://arxiv.org/abs/2604.26604}
}"""

KEY = "morishita2026who"
start = re.search(r"@\w+\{" + re.escape(KEY) + r",", text)
assert start, "key not found"
tail = text[start.start():]
m = re.search(r"\n\}", tail)
assert m, "closing brace not found"
end = start.start() + m.end()
old = text[start.start():end]
old_title = re.search(r"title=\{(.*?)\},", old, re.S)
print("  current title:", old_title.group(1)[:90] if old_title else "?")
print("  restoring to :", "Who Trains Matters: Federated Learning under Enrollment and Participation Selection Biases")
text = text[:start.start()] + ORIGINAL + text[end:]

out = text.encode("utf-8")
BIB.write_bytes(out)
print(f"post: {len(out)} B  sha256 {hashlib.sha256(out).hexdigest()[:16]}")
print("  entries:", len(re.findall(r"(?m)^@", text)),
      " ([1] and [3] must still be the new papers)")
for k in ("ganti2011mobile", "xu2025rethinking", "morishita2026who"):
    blk = re.search(r"@\w+\{" + re.escape(k) + r",.*?\n\}", text, re.S)
    t = re.search(r"title=\{(.*?)\},", blk.group(0), re.S)
    print(f"    {k:<20} {t.group(1)[:76] if t else '?'}")
