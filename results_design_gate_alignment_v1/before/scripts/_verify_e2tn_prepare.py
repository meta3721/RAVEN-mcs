from pathlib import Path
import json
p = Path("outputs/e2_true_stratum/E2_PROFILE_SELECTION.json")
d = json.loads(p.read_text(encoding="utf-8"))
assert d["status"] == "NO_VALID_TRUE_STRATUM_NONWRAP_PROFILE"
print("ok", d["status"])
