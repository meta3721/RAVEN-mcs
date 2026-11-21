import sys, pathlib, numpy as np, pandas as pd
ROOT=pathlib.Path(r"C:\Cursor\raven.mcs"); sys.path.insert(0,str(ROOT/"src"))
from raven_mcs.e3.canary.dataset_load import load_paper_dataset
from raven_mcs.e3.real_runner.runner import _predict, _mu_weights_for_test
from raven_mcs.data.target import GroupMapper, TargetBuilder
class S: pass
for b in ("sensorscope","uair","traffic"):
    ds=load_paper_dataset(ROOT,b)
    au=ds._atomic_df.copy()
    au["codes"]=pd.Categorical(au["target_group"]).codes
    m=au.set_index(au["unit_id"].astype(str))["codes"]
    s=S(); s.model=None
    st=ds._target_group_str_to_int
    bad=0; n=0
    for uid,row in zip(au["unit_id"].astype(str), au.itertuples(index=False)):
        sti=st.get(str(row.target_group))
        n+=1
        if sti != int(m[uid]): bad+=1
    print("%-11s n=%d  mismatches between sorted-str int and categorical code = %d  num_groups=%d  n unique target_group=%d"
          % (b,n,bad,ds.num_groups,au["target_group"].nunique()))
