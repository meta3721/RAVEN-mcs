#!/usr/bin/env python3
from __future__ import annotations

import os
import shutil
import subprocess
import sys
import tempfile
from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]
PY = sys.executable

with tempfile.TemporaryDirectory(prefix="e2ee_unpack_") as tmp:
    tmp_path = Path(tmp)
    for rel in [
        "src/raven_mcs/__init__.py",
        "src/raven_mcs/e2",
        "src/raven_mcs/data",
        "src/raven_mcs/utils",
        "configs",
        "scripts/check_e2_empirical_eventtrace_gates.py",
        "scripts/export_e2_empirical_eventtrace_evidence.py",
        "scripts/prepare_e2_empirical_eventtrace_and_profile_refreeze.py",
        "scripts/run_and_log.py",
        "tests/unit/test_e2_empirical_eventtrace_core.py",
        "tests/integration/test_e2_empirical_eventtrace_integration.py",
        "outputs/e2_empirical",
        "outputs/audits",
        "outputs/gates",
        "data/processed/sensorscope/atomic_units.parquet",
    ]:
        src = ROOT / rel
        if not src.exists():
            continue
        dest = tmp_path / rel
        if src.is_dir():
            shutil.copytree(src, dest, dirs_exist_ok=True)
        else:
            dest.parent.mkdir(parents=True, exist_ok=True)
            shutil.copy2(src, dest)
    env = dict(os.environ, PYTHONPATH=str(tmp_path / "src"))
    junit = ROOT / "logs/e2_empirical_eventtrace_unpacked_specialized.xml"
    junit.parent.mkdir(parents=True, exist_ok=True)
    proc = subprocess.run(
        [
            PY, "-m", "pytest", "-q",
            "tests/unit/test_e2_empirical_eventtrace_core.py",
            "tests/integration/test_e2_empirical_eventtrace_integration.py",
            f"--junitxml={junit}",
        ],
        cwd=tmp_path,
        env=env,
    )
    raise SystemExit(proc.returncode)
