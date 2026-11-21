import pathlib

p = pathlib.Path(r"C:\Cursor\raven.mcs\results_server_optimizer\round_v1\driver\preflight_section0.py")
txt = p.read_text(encoding="utf-8")

OLD = """    return {
        "n_spatial": n_spatial,"""
NEW = """    return {
        "checkpoint_wrapper": wrapper,
        "n_spatial": n_spatial,"""
assert txt.count(OLD) == 1, f"anchor count {txt.count(OLD)}"
txt = txt.replace(OLD, NEW)

OLD2 = """                "seed": seed,
                "checkpoint_wrapper": wrapper,"""
NEW2 = """                "seed": seed,"""
assert txt.count(OLD2) == 1, f"anchor2 count {txt.count(OLD2)}"
txt = txt.replace(OLD2, NEW2)

p.write_text(txt, encoding="utf-8")
print("patched;", len(txt.splitlines()), "lines")
