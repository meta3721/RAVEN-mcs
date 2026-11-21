import sys, pathlib, json
ROOT = pathlib.Path(".").resolve()
sys.path.insert(0, str(ROOT/"src")); sys.path.insert(0, str(ROOT/"scripts"))
from raven_mcs.e3.canary.dataset_load import load_paper_dataset, load_spatial_to_client
from raven_mcs.e3.stratum_seal.remap import apply_sealed_opportunity_stratum
from raven_mcs.correction.pi_target import build_pi_target

def holes(name):
    ds = load_paper_dataset(ROOT, name)
    mp = load_spatial_to_client(ROOT, name)
    sealed, meta = apply_sealed_opportunity_stratum(ds.atomic_df, dataset=name, root=ROOT)
    a = sealed.copy()
    if "target_group_main" not in a.columns:
        a["target_group_main"] = a["target_group"].astype(str)
    fr = build_pi_target(a, mp, split="test")
    tar = {(str(r.client_id), str(r.opportunity_stratum)): float(r.pi_k_s_tar) for r in fr.itertuples()}
    train = sealed[sealed["split"].astype(str)=="train"]
    sbc = {}
    for r in train.itertuples(index=False):
        c = mp.get(str(r.spatial_id))
        if c is None: continue
        sbc.setdefault(c, []).append(str(r.opportunity_stratum))
    support = {(c,s) for c,ss in sbc.items() for s in set(ss)}
    zero = {k for k in support if tar.get(k, 0.0) <= 0.0}
    print(f"{name:<14} strata={meta.get('n_unique_strata'):<5} support_pairs={len(support):<5} zero_pi_tar={len(zero):<5} "
          f"({len(zero)/max(1,len(support))*100:.1f}%)  pi_target_keys={len(tar)}")
    return len(support), len(zero)

for n in ("uair", "sensorscope", "traffic"):
    try: holes(n)
    except Exception as e: print(f"{n:<14} ERROR {type(e).__name__}: {str(e)[:110]}")
