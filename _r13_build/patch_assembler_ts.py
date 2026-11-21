import pathlib

p = pathlib.Path(r"C:\Cursor\raven.mcs\results_server_optimizer\round_v1\driver\write_final_artifacts.py")
t = p.read_text(encoding="utf-8")

OLD_IMP = '''import csv
import hashlib
import json
import pathlib'''
NEW_IMP = '''import csv
import hashlib
import json
import pathlib
from datetime import datetime, timezone'''
assert t.count(OLD_IMP) == 1, "import anchor"
t = t.replace(OLD_IMP, NEW_IMP)

OLD_TS = '''    "created_utc": None,
}'''
NEW_TS = '''    "created_utc": datetime.now(timezone.utc).isoformat(),
}'''
assert t.count(OLD_TS) == 1, "created_utc anchor"
t = t.replace(OLD_TS, NEW_TS)

p.write_text(t, encoding="utf-8")
print("assembler now stamps created_utc itself")

# retire the one-shot fixer so it cannot clobber the Stage C result again
f = pathlib.Path(r"C:\Cursor\raven.mcs\_r13_build\fix_artifacts_after_traffic.py")
if f.is_file():
    moved = f.with_suffix(".py.superseded")
    f.replace(moved)
    print("retired fix_artifacts_after_traffic.py ->", moved.name)
