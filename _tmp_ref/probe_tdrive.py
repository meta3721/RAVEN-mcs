import sys, pathlib, traceback
ROOT = pathlib.Path(".").resolve()
sys.path.insert(0, str(ROOT/"src")); sys.path.insert(0, str(ROOT/"scripts"))
from raven_mcs.e3.canary.dataset_load import load_paper_dataset, load_spatial_to_client
from raven_mcs.e3.stratum_seal.remap import apply_sealed_opportunity_stratum
from raven_mcs.correction.pi_target import build_pi_target
ds = load_paper_dataset(ROOT, "tdrive_speed"); print("loaded:", type(ds).__name__)
mp = load_spatial_to_client(ROOT, "tdrive_speed"); print("mapping size:", len(mp))
try:
    sealed, meta = apply_sealed_opportunity_stratum(ds.atomic_df, dataset="tdrive_speed", root=ROOT)
    print("sealed ok", meta)
except Exception:
    traceback.print_exc()
