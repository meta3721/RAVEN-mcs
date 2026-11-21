import json
from pathlib import Path
p = Path("artifacts/e3_formal_runs_r1/eventtraces/sensorscope/seed30001/generation_meta.json")
print(p.read_text(encoding="utf-8")[:700])
