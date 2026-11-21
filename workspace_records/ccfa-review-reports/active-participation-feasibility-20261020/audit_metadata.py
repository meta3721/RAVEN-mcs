"""Read-only inventory audit; no labels, model training, or U generator are used."""
from pathlib import Path
import json
import math
import pandas as pd

ROOT = Path("C:/Cursor/raven.mcs")
OUT = Path(__file__).resolve().parent
occ = pd.read_parquet(
    ROOT / "data/processed/cityscanner_nyc_p2_measured_o/occupancy_units.parquet",
    columns=["unit_id", "client_id", "absolute_time", "split", "target_group", "o_observed"],
)
atomic = pd.read_parquet(
    ROOT / "data/processed/cityscanner_nyc_p2_measured_o/atomic_units.parquet",
    columns=["unit_id", "is_warmup"],
)
occ = occ.merge(atomic, on="unit_id", how="left", validate="one_to_one")
occ["absolute_time"] = pd.to_datetime(occ["absolute_time"], utc=True)
warmup = occ.loc[(occ["split"] == "train") & occ["is_warmup"].fillna(False)]
if warmup.empty:
    raise RuntimeError("No audited warmup cutoff; do not infer one.")
cutoff = warmup["absolute_time"].max()
train_end = occ.loc[occ["split"] == "train", "absolute_time"].max()
train = occ.loc[(occ["split"] == "train") & (occ["absolute_time"] > cutoff)].copy()
train["utc_day"] = train["absolute_time"].dt.floor("D")
rows = []
for day, block in train.groupby("utc_day", sort=True):
    obs = block.loc[block["o_observed"] == 1]
    counts = obs.groupby(["client_id", "target_group"]).size()
    k = int(obs["client_id"].nunique())
    budget = math.ceil(0.25 * k)
    group_counts = obs.groupby("target_group")["client_id"].nunique()
    rows.append({
        "utc_day": str(day),
        "complete_utc_day_inside_train": bool(day + pd.Timedelta(days=1) <= train_end),
        "occupied_units": int(len(block)),
        "o1_units": int(len(obs)),
        "inventory_clients_ge1": k,
        "inventory_clients_ge2": int((counts >= 2).sum()),
        "represented_groups": int(len(group_counts)),
        "budget_ceil_quarter": budget,
        "budget_covers_present_groups": budget >= len(group_counts),
        "min_clients_per_present_group": int(group_counts.min()) if len(group_counts) else 0,
    })
daily = pd.DataFrame(rows)
daily.to_csv(OUT / "daily_inventory_metadata.csv", index=False)
complete = daily.loc[daily["complete_utc_day_inside_train"]]
result = {
    "scope": "metadata only; inventory clients are upper bounds before model eligibility checks",
    "no_training": True,
    "u_generator_not_used": True,
    "warmup_last_timestamp_utc": str(cutoff),
    "post_warmup_train_occupied_units": int(len(train)),
    "post_warmup_train_o1_units": int((train["o_observed"] == 1).sum()),
    "nonempty_utc_days": len(daily),
    "days_with_all_four_groups": int((daily["represented_groups"] == 4).sum()),
    "days_with_inventory_K_at_least_8": int((daily["inventory_clients_ge1"] >= 8).sum()),
    "days_quarter_budget_covers_present_groups": int(daily["budget_covers_present_groups"].sum()),
    "inventory_clients_ge1_min_median_max": [
        int(daily["inventory_clients_ge1"].min()),
        float(daily["inventory_clients_ge1"].median()),
        int(daily["inventory_clients_ge1"].max()),
    ],
    "candidate_group_count_frequency": {
        str(int(k)): int(v) for k, v in daily["represented_groups"].value_counts().sort_index().items()
    },
    "first_utc_day": str(daily["utc_day"].min()),
    "last_utc_day": str(daily["utc_day"].max()),
    "complete_days": {
        "n": len(complete),
        "all_four_groups": int((complete["represented_groups"] == 4).sum()),
        "K_at_least_8": int((complete["inventory_clients_ge1"] >= 8).sum()),
        "K_min_median_max": [
            int(complete["inventory_clients_ge1"].min()),
            float(complete["inventory_clients_ge1"].median()),
            int(complete["inventory_clients_ge1"].max()),
        ],
        "quarter_budget_covers_present_groups": int(complete["budget_covers_present_groups"].sum()),
    },
}
(OUT / "METADATA_AUDIT.json").write_text(
    json.dumps(result, indent=2, ensure_ascii=False) + "\n", encoding="utf-8"
)
print(json.dumps(result, ensure_ascii=False, indent=2))
