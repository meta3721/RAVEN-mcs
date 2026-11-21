import pathlib

p = pathlib.Path(r"C:\Cursor\raven.mcs\results_server_optimizer\round_v1\driver\preflight_section0.py")
txt = p.read_text(encoding="utf-8")

OLD = """def measure(ckpt: pathlib.Path, seed: int):
    theta = load_theta(ckpt)
    if not isinstance(theta, dict):
        return None
    keys = sorted(theta.keys())
    n_spatial = int(theta["spatial.weight"].shape[0])"""

NEW = """def measure(ckpt: pathlib.Path, seed: int):
    obj = load_theta(ckpt)
    if not isinstance(obj, dict):
        return None
    # federated arms store the raw theta dict; central_all / central_delivered wrap it
    wrapper = None
    if "state_dict" in obj and isinstance(obj["state_dict"], dict):
        wrapper = {k: v for k, v in obj.items() if k != "state_dict"}
        theta = obj["state_dict"]
    else:
        theta = obj
    keys = sorted(theta.keys())
    n_spatial = int(theta["spatial.weight"].shape[0])"""

assert txt.count(OLD) == 1, f"anchor count {txt.count(OLD)}"
txt = txt.replace(OLD, NEW)

OLD2 = """            rec = {
                "dataset": ds,
                "arm": arm,
                "seed": seed,"""
NEW2 = """            rec = {
                "dataset": ds,
                "arm": arm,
                "seed": seed,
                "checkpoint_wrapper": wrapper,"""
assert txt.count(OLD2) == 1, f"anchor2 count {txt.count(OLD2)}"
txt = txt.replace(OLD2, NEW2)

p.write_text(txt, encoding="utf-8")
print("patched;", len(txt.splitlines()), "lines")
