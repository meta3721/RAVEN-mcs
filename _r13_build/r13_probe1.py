import json,pathlib
p=pathlib.Path(r'C:\Cursor\raven.mcs\results_server_optimizer\round_v1\runs\A_eta0.003\traffic\fedavg_window\seed30001\target_wiring.json')
d=json.loads(p.read_text())
def walk(o,pre=''):
    if isinstance(o,dict):
        for k,v in o.items():
            if isinstance(v,(dict,list)):
                print(pre+str(k)+' : '+type(v).__name__+' len='+str(len(v)))
                if isinstance(v,dict) and len(v)<8: walk(v,pre+'  ')
            else:
                print(pre+str(k)+' = '+repr(v)[:120])
walk(d)
