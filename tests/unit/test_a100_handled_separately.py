from pathlib import Path
import pandas as pd
from raven_mcs.sag.r1k_barrier import strict_positive_lcb_possible
ROOT = Path(__file__).resolve().parents[2]

def test_a100_handled_separately() -> None:
    frame = pd.read_csv(ROOT / "results_sag_g1/round_r1k/pairwise_barrier/R1K_PAIRWISE_BARRIER_BY_LEVEL.csv")
    a1 = frame.loc[frame["availability_level"].astype(float).round(2) == 1.00]
    stress = frame.loc[frame["availability_level"].astype(float) < 0.95]
    assert a1["strict_positive_lcb_possible"].astype(str).str.lower().isin(["true", "1"]).all()
    assert (~stress["strict_positive_lcb_possible"].astype(str).str.lower().isin(["true", "1"])).all()
    assert (ROOT / "results_sag_g1/round_r1k/pairwise_barrier/R1K_A100_PAIR_PRESENCE_AUDIT.csv").is_file()
    assert strict_positive_lcb_possible(1.0)
