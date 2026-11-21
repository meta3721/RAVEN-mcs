#!/bin/bash
# Detached resume loop for TD-R-E3. Reuses TD_R_ACCEPTED.json; does not start a
# second trainer while one is already running.
set -u
cd /root/raven.mcs
LOG=results_tdrive_rank/round_v1/TRAIN_DETACHED.log
export PYTHONUNBUFFERED=1
export PATH="/usr/local/miniconda3/envs/py312/bin:$PATH"

count_done() {
  python - << 'PY'
import json
from pathlib import Path
p = Path("results_tdrive_rank/round_v1/TD_R_TRAIN_LEDGER.json")
if not p.is_file():
    print(0)
    raise SystemExit
d = json.loads(p.read_text(encoding="utf-8"))
print(sum(1 for r in d.get("rows", []) if r.get("path_status") == "REAL_PATH_EXECUTED"))
PY
}

train_pids() {
  pgrep -f "[p]ython -u scripts/run_tdrive_rank_v1.py --stage train" || true
}

echo "$(date -u +%Y-%m-%dT%H:%M:%SZ) watchdog start done=$(count_done) existing=$(train_pids | tr '\n' ' ')" >> "$LOG"
fail=0
while true; do
  done_n=$(count_done)
  if [ "$done_n" -ge 60 ]; then
    echo "$(date -u +%Y-%m-%dT%H:%M:%SZ) complete ${done_n}/60" >> "$LOG"
    exit 0
  fi
  if [ -n "$(train_pids)" ]; then
    sleep 60
    continue
  fi
  echo "$(date -u +%Y-%m-%dT%H:%M:%SZ) resume train done=${done_n}/60" >> "$LOG"
  python -u scripts/run_tdrive_rank_v1.py --stage train >> "$LOG" 2>&1
  rc=$?
  echo "$(date -u +%Y-%m-%dT%H:%M:%SZ) train exit rc=${rc} done=$(count_done)" >> "$LOG"
  if [ "$rc" -eq 0 ]; then
    fail=0
    continue
  fi
  fail=$((fail + 1))
  if [ "$fail" -ge 5 ]; then
    echo "$(date -u +%Y-%m-%dT%H:%M:%SZ) giving up after ${fail} failures" >> "$LOG"
    exit "$rc"
  fi
  sleep 30
done
