import sys, pathlib, json, re
ROOT = pathlib.Path(".").resolve()
sys.path.insert(0, str(ROOT/"src")); sys.path.insert(0, str(ROOT/"scripts"))
# what dataset names does load_paper_dataset accept?
src = (ROOT/"src/raven_mcs/e3/canary/dataset_load.py").read_text(encoding="utf-8")
for m in re.finditer(r'^\s*(?:if|elif)?\s*name\s*(?:==|in)\s*[^\n]{0,160}', src, re.M):
    print("  ", m.group(0).strip()[:150])
