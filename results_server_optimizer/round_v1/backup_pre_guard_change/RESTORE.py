"""Restore src/raven_mcs/e3/{protocol_closure/reuse_guard.py,real_runner/runner.py} to their
pre-2026-10-08 state from this backup. Run with the project venv python."""
import hashlib, pathlib, shutil, sys

ROOT = pathlib.Path(r"C:\Cursor\raven.mcs")
B = pathlib.Path(__file__).resolve().parent
EXPECT = {"src/raven_mcs/e3/protocol_closure/reuse_guard.py": "46d26da601b82672b4a770995dcb6fa1e06dcfaf32556b4b358804abef6d520d",
         "src/raven_mcs/e3/real_runner/runner.py": "4c25921a042e1954398618afc1f81ec0957929beeb0a8b4388590912d2994fda"}
for rel, want in EXPECT.items():
    src = B / "src" / rel
    dst = ROOT / rel
    shutil.copy2(src, dst)
    got = hashlib.sha256(dst.read_bytes()).hexdigest()
    print(("RESTORED " if got == want else "MISMATCH ") + rel + " " + got[:16])
    if got != want:
        sys.exit(1)
print("restore complete")
