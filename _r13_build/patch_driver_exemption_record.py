import pathlib

p = pathlib.Path(r"C:\Cursor\raven.mcs\results_server_optimizer\round_v1\driver\s1p_driver.py")
t = p.read_text(encoding="utf-8")

OLD = '''                "diag_first": ServerOptWindowRunner.DIAG[:3],
                "diag_last": ServerOptWindowRunner.DIAG[-3:],
                "created_utc": now(),
            },
            d / "SERVER_OPT_META.json",
        )'''
NEW = '''                "diag_first": ServerOptWindowRunner.DIAG[:3],
                "diag_last": ServerOptWindowRunner.DIAG[-3:],
                "created_utc": now(),
                # The ledger cannot carry these: run_e3_real writes only git_commit,
                # source_manifest_hash, method_source_hash, runner_source_hash and dataset_hash from
                # source_identity (runner.py L307-L311), so the exemption is recorded here, in the
                # driver's own per-run artifact, and in a dedicated file below.
                "reuse_guard_exemption": bool(TRAFFIC_REUSE_EXEMPTION and block == "traffic"),
                "reuse_guard_code_default": "DUPLICATE_REUSED_TRAFFIC_RUN_BLOCKED",
                "reuse_guard_ledger_part": "Part IX item 65" if (TRAFFIC_REUSE_EXEMPTION and block == "traffic") else None,
            },
            d / "SERVER_OPT_META.json",
        )
        if TRAFFIC_REUSE_EXEMPTION and block == "traffic":
            dump_json(
                {
                    "exemption": "allow_reused_traffic_rerun=True",
                    "guard": "src/raven_mcs/e3/protocol_closure/reuse_guard.py",
                    "guard_default": "raises DuplicateReusedTrafficRunBlocked",
                    "authorized_by": "user, 2026-10-08",
                    "ledger_record": "ccfa-review-reports/raven-mcs-metric-definition-diagnosis.md Part IX item 65",
                    "caveat": "This run is NOT the sealed E2 Traffic Complete-aligned object and must "
                              "not be compared with the frozen E3 traffic evidence as if it were.",
                    "run": {"block": block, "arm": arm, "seed": int(seed), "tag": tag},
                    "created_utc": now(),
                },
                d / "REUSE_GUARD_EXEMPTION.json",
            )'''
assert t.count(OLD) == 1, "meta anchor"
t = t.replace(OLD, NEW)
p.write_text(t, encoding="utf-8")
print("patched: exemption now recorded in SERVER_OPT_META.json and REUSE_GUARD_EXEMPTION.json")
