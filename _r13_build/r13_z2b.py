import json, numpy as np, collections, pathlib
a=json.loads(pathlib.Path(r"C:\Cursor\raven.mcs\_r13_build\r13_a_constants.json").read_text())
fam=collections.defaultdict(list)
for k,v in a["new"].items():
    fam[(k.split("/")[1],k.split("/")[0])].append(v)
for k,v in a["frozen"].items():
    fam[(k.split("/")[2],"FROZEN:"+k.split("/")[1])].append(v)
order={"sensorscope":0,"uair":1,"traffic":2}
for (b,tag),vs in sorted(fam.items(), key=lambda kv:(order[kv[0][0]],kv[0][1])):
    t=float(np.mean([x["test_mu"] for x in vs])); z=float(np.mean([x["zero"] for x in vs]))
    c=float(np.mean([x["best_const_in_sample"] for x in vs]))
    print("%-11s %-24s n=%d mean_test=%.6f zero=%.6f bestconst=%.6f  vs_zero=%+.3f%%  vs_const=%+.3f%%"
          %(b,tag,len(vs),t,z,c,100*(1-t/z),100*(1-t/c)))
print()
for key in ("A_eta0.01/sensorscope/30001","A_eta0.003/uair/30001","A_eta0.003/traffic/30001","A_eta0.003/traffic/30005"):
    v=a["new"][key]
    print("%-28s test=%.5f zero=%.5f const=%.5f vs_zero=%+.3f%% vs_const=%+.3f%% corr=%+.3f predmean=%+.4f predsd=%.4f ymean=%+.4f"%(
        key,v["test_mu"],v["zero"],v["best_const_in_sample"],100*(1-v["test_mu"]/v["zero"]),
        100*(1-v["test_mu"]/v["best_const_in_sample"]),v["corr_pred_true"],v["model_pred_mean"],v["model_pred_sd"],v["y_mean"]))
