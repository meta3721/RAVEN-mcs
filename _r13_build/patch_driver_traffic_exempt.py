import pathlib

p = pathlib.Path(r"C:\Cursor\raven.mcs\results_server_optimizer\round_v1\driver\s1p_driver.py")
t = p.read_text(encoding="utf-8")

OLD = "BETA1, BETA2, TAU = 0.9, 0.99, 1e-3"
NEW = '''BETA1, BETA2, TAU = 0.9, 0.99, 1e-3

# The E3 protocol-closure reuse guard refuses `traffic + complete_aligned + formal seed +
# {fedavg_window, ..., raven}`.  Ledger Part IX item 65 records a user-authorized, default-off
# opt-in (`allow_reused_traffic_rerun`) that must be passed explicitly by the caller and is written
# into that run's own ledger `source_identity`.  It is passed ONLY for the traffic block, so the
# SensorScope and U-Air runs never carry a misleading exemption flag.
TRAFFIC_REUSE_EXEMPTION = True'''
assert t.count(OLD) == 1, "const anchor"
t = t.replace(OLD, NEW)

OLD2 = '''                "server_opt_windowrunner_patch": "raven_mcs.training.window_runner.FullWindowRunner",
            },'''
NEW2 = '''                "server_opt_windowrunner_patch": "raven_mcs.training.window_runner.FullWindowRunner",
                "allow_reused_traffic_rerun": bool(TRAFFIC_REUSE_EXEMPTION and block == "traffic"),
                "reuse_guard_note": (
                    "ledger Part IX item 65; the guard refuses this cell by default and the opt-in is "
                    "recorded here so the run identifies itself"
                ) if (TRAFFIC_REUSE_EXEMPTION and block == "traffic") else None,
            },'''
assert t.count(OLD2) == 1, "source_identity anchor"
t = t.replace(OLD2, NEW2)

p.write_text(t, encoding="utf-8")
print("patched s1p_driver.py")
