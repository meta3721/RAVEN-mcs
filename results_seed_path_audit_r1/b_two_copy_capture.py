"""Stage B — one instrumented rerun capturing the live model and the reloaded theta.

Runs U-Air / raven / seed 30007 through the production path (`run_e3_real`, the
`C0_frozen` condition, i.e. the sealed trace) with `_predict` wrapped so that at
metric time it records, in one process:

  * max |model_parameter - theta_parameter|
  * RMSE_mu from the live `runner.model`
  * RMSE_mu from a fresh module loaded with `runner.theta`
  * the largest per-unit prediction difference
  * the last window's activity flag

Output (only inside this audit directory):
  B_TWO_COPY_CAPTURE.json
  b_runs/C0_frozen/uair/raven/seed30007/...   (the rerun's own artifacts)

Read-only elsewhere; the sealed E3 tree is never touched.
"""
from __future__ import annotations

import json
import pathlib
import sys

import numpy as np
import torch

ROOT = pathlib.Path(__file__).resolve().parents[1]
sys.path.insert(0, str(ROOT / 'src'))
sys.path.insert(0, str(ROOT / 'scripts'))

import run_h_headroom as h                                    # noqa: E402
import raven_mcs.e3.real_runner.runner as R                   # noqa: E402
from raven_mcs.metrics.accuracy import rmse_mu                # noqa: E402

AUDIT = ROOT / 'results_seed_path_audit_r1'
CAPTURE = AUDIT / 'B_TWO_COPY_CAPTURE.json'
h.OUT = AUDIT                      # redirect run_arm's run_dir into the audit dir

_orig_predict = R._predict
_orig_predict_model = R._predict_model


def _capture(runner, dataset, live_pred):
    rec = {'dataset': 'uair', 'arm': 'raven', 'seed': 30007}
    th = getattr(runner, 'theta', None)
    model = getattr(runner, 'model', None)
    if th is not None and model is not None:
        sd = model.state_dict()
        gaps = {}
        for k, v in sd.items():
            if k in th:
                a = v.detach().cpu().numpy().astype(np.float64)
                b = np.asarray(th[k], dtype=np.float64)
                gaps[k] = float(np.abs(a - b).max())
        rec['max_abs_model_minus_theta'] = max(gaps.values()) if gaps else None
        rec['per_param_gap'] = gaps
        rec['theta_keys_in_model'] = len(gaps)
        fresh = type(model)(num_spatial=dataset.num_spatial)
        fresh.load_state_dict({k: torch.as_tensor(np.asarray(v, dtype=np.float64))
                               for k, v in th.items()})
        patched._busy = True
        try:
            theta_pred = _orig_predict_model(fresh, dataset)
        finally:
            patched._busy = False
        mu = getattr(runner, 'mu', None)
        if mu is not None:
            mu = np.asarray(mu, dtype=np.float64)
            w_live = R._mu_weights_for_test(live_pred, mu)
            w_theta = R._mu_weights_for_test(theta_pred, mu)
            rec['weight_sum'] = [float(w_live.sum()), float(w_theta.sum())]
            rec['rmse_mu_live'] = float(rmse_mu(live_pred['y_pred'], live_pred['y_true'], w_live))
            rec['rmse_mu_theta'] = float(rmse_mu(theta_pred['y_pred'], theta_pred['y_true'], w_theta))
            rec['max_abs_pred_diff'] = float(np.abs(live_pred['y_pred'] - theta_pred['y_pred']).max())
        else:
            rec['mu_missing'] = True
        rec['n_units'] = int(len(live_pred['y_true']))
    metrics = getattr(runner, 'metrics', None)
    if metrics:
        rec['last_window_id'] = int(metrics[-1].window_id)
        rec['last_window_active'] = bool(metrics[-1].active)
        rec['n_active_windows'] = int(sum(1 for m in metrics if m.active))
    return rec


def patched(runner, dataset, split='test'):
    out = _orig_predict(runner, dataset, split)
    if getattr(patched, '_busy', False):
        return out
    if hasattr(runner, 'theta') and hasattr(runner, 'model'):
        try:
            rec = _capture(runner, dataset, out)
        except Exception as exc:                                  # noqa: BLE001
            rec = {'error': '%s: %s' % (type(exc).__name__, exc)}
        CAPTURE.write_text(json.dumps(rec, indent=2), encoding='utf-8')
        print('captured:', json.dumps({k: v for k, v in rec.items() if k != 'per_param_gap'}), flush=True)
    return out


R._predict = patched


def main() -> None:
    AUDIT.mkdir(parents=True, exist_ok=True)
    res = h.run_arm('C0_frozen', 'uair', 'raven', 30007, tag='b_runs')
    print('run_arm result keys:', sorted(res.keys()))
    print('RMSE_mu (rerun):', res.get('RMSE_mu'))
    if CAPTURE.is_file():
        print('capture file:', CAPTURE.relative_to(ROOT))


if __name__ == '__main__':
    main()
