import sys, numpy as np
sys.path.insert(0, "scripts")
import w1_v51_oracle as O
for K in (3,5,8,16,32,64):
    v = np.full(K, 1.0/K); hi = 0.5
    print("K=%-3d clip_sum=%r tau=%r x_sum=%r maxdiff=%r" % (
        K, O._clip_sum(v, hi), O.solve_tau(v, hi),
        float(O._clip(v - O.solve_tau(v,hi), hi).sum()),
        float(np.max(np.abs(O._clip(v - O.solve_tau(v,hi), hi) - v)))))
