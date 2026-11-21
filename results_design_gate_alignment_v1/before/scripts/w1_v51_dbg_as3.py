import sys, numpy as np
sys.path.insert(0, "scripts")
import w1_v51_oracle as O
for v in (np.array([0.44721023, 0.32726116, 0.22552860]),
          np.array([1.34163069, 0.98178349, 0.67658581])):
    print("v", v)
    print("  pbs:", O._project_ball_simplex(v, 0.5, 1.0/3.0))
    a, lam, act = O.project_Cr(v, 0.5, 3.0)
    print("  Cr :", np.round(a,10), act, "sum", a.sum(), "n2", float(a@a))
