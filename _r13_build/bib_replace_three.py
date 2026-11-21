"""Replace three bibliography entries, keeping the keys so numbering and every \\cite site are unchanged."""
from __future__ import annotations

import hashlib
import pathlib
import re

BIB = pathlib.Path(r"C:\Cursor\raven.mcs\TO_OVERLEAF_paper_tmc_r1_clean/reference.bib")
raw_bytes = BIB.read_bytes()
pre = hashlib.sha256(raw_bytes).hexdigest()
crlf = raw_bytes.count(bytes([13, 10]))
eol = b"\r\n" if crlf == raw_bytes.count(bytes([10])) else b"\n"
text = raw_bytes.decode("utf-8")
print(f"pre : {len(raw_bytes)} B  sha256 {pre[:16]}  eol {eol}")

NEW = {
    # [1] position: ganti2011mobile
    "ganti2011mobile": """@article{ganti2011mobile,
  title={Sensing Data Aggregation in Mobile Crowd Sensing: A Cloud-Enhanced-Edge--End Framework With DQN-Based Offloading},
  author={Yang, G. and Sang, J. and Zhang, X. and He, X. and Liu, Y. and Sun, F.},
  journal={IEEE Internet of Things Journal},
  volume={11},
  number={19},
  pages={31852--31861},
  year={2024},
  publisher={IEEE}
}""",
    # [3] position: xu2025rethinking
    "xu2025rethinking": """@article{xu2025rethinking,
  title={{TMAE}: Entropy-Aware Masked Autoencoder for Low-Cost Traffic Flow Map Inference},
  author={Luo, X. and Wu, Q. and Wang, Y. and Zhang, K. and Dai, H.-N. and Chen, D.},
  journal={IEEE Internet of Things Journal},
  volume={12},
  number={14},
  pages={27255--27268},
  year={2025},
  publisher={IEEE}
}""",
    # [10] position: morishita2026who
    "morishita2026who": """@article{morishita2026who,
  title={Long-Term Client Selection for Federated Learning With Non-IID Data: A Truthful Auction Approach},
  author={Tan, J. and Liu, Z. and Guo, K. and Zhao, M.},
  journal={IEEE Internet of Things Journal},
  volume={12},
  number={5},
  pages={4953--4970},
  year={2025},
  publisher={IEEE}
}""",
}

for key, new_entry in NEW.items():
    start = re.search(r"@\w+\{" + re.escape(key) + r",", text)
    assert start, f"key not found: {key}"
    assert text.count(key) >= 1
    # find the closing brace of this entry: first line that is '}' after the start
    tail = text[start.start():]
    m = re.search(r"\n\}", tail)
    assert m, f"no closing brace for {key}"
    end = start.start() + m.end()
    old_entry = text[start.start():end]
    TITLE_RE = re.compile(r"title=\{(.*?)\},", re.S)
    old_m = TITLE_RE.search(old_entry)
    new_m = TITLE_RE.search(new_entry)
    old_t = old_m.group(1)[:86] if old_m else "?"
    new_t = new_m.group(1)[:86] if new_m else "?"
    print("\n  " + key)
    print("    old: " + old_t)
    print("    new: " + new_t)
    text = text[:start.start()] + new_entry + text[end:]

out = text.encode("utf-8")
BIB.write_bytes(out)
print(f"\npost: {len(out)} B  sha256 {hashlib.sha256(out).hexdigest()[:16]}  "
      f"entries now {len(re.findall(r'(?m)^@', text))}")
