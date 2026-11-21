"""Restore the 16 corrupted tracked files from HEAD."""
import subprocess
from pathlib import Path

root = Path('C:/Cursor/raven.mcs')
FILES = [
    'RAVEN_MCS_PUBLIC_REPRO_R1/configs/design_rule.json',
    'RAVEN_MCS_PUBLIC_REPRO_R1/scripts/build_public_repro_bundle.py',
    'configs/dataset/cityscanner_nyc_pm25.yaml',
    'post_review/C1_kill_cityscanner/C1_KILL_INSTRUCTION.md',
    'post_review/C1_kill_cityscanner/TARGET_SPEC.json',
    'post_review/C1_kill_tdrive_spatial/C1_KILL_INSTRUCTION.md',
    'post_review/C1_kill_tdrive_spatial/DRIVER_HAJEK_SLOWDOWN_PATCH_INSTRUCTION.md',
    'post_review/C1_kill_tdrive_spatial/TARGET_SPEC.json',
    'post_review/C1_tdrive_rank/REMOTE_AGENT_PROMPT.md',
    'post_review/C1_tdrive_rank/REMOTE_SYNC.md',
    'results_c1_cityscanner/round_v1/INGEST_REPORT.json',
    'results_tdrive_rank/TD_R_ZIP_INGEST_AUDIT.json',
    'results_tdrive_rank/round_v1/TD_R_HARDWARE_STOP.json',
    'scripts/run_c1_tdrive_spatial.py',
    'src/raven_mcs/data/cityscanner.py',
    'src/raven_mcs/data/registry.py',
]
print('before:')
for f in FILES:
    print('  %-78s %d' % (f[:76], (root / f).stat().st_size))

r = subprocess.run(['git', '-C', str(root), 'checkout', '--'] + FILES,
                   capture_output=True, text=True)
print()
print('git checkout rc=%d %s' % (r.returncode, (r.stderr or '').strip()[:200]))

print()
print('after:')
bad = 0
for f in FILES:
    n = (root / f).stat().st_size
    ok = n > 2
    bad += 0 if ok else 1
    print('  %-78s %-8d %s' % (f[:76], n, 'OK' if ok else 'STILL BAD'))
print()
print('still bad: %d' % bad)
