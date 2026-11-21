import sys, json, pathlib, hashlib
import numpy as np, pandas as pd, torch
ROOT=pathlib.Path(r'C:\Cursor\raven.mcs')
sys.path.insert(0,str(ROOT/'src'))
ck=ROOT/'results_server_optimizer/round_v1/runs/A_eta0.003/traffic/fedavg_window/seed30001/checkpoints/final.pt'
obj=torch.load(ck,map_location='cpu',weights_only=False)
print('type',type(obj))
if isinstance(obj,dict):
    print('keys',list(obj.keys())[:20])
    sd=obj.get('state_dict',obj)
    print('n tensors',len(sd))
    for k,v in list(sd.items())[:6]:
        print(' ',k,tuple(v.shape),v.dtype)
    if 'spatial.weight' in sd: print('num_spatial',sd['spatial.weight'].shape)
    for k in sd:
        if 'head' in k: print('  HEAD',k,tuple(sd[k].shape))
