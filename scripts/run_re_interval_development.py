"""Explicit single-run entry; no seed loop, no calibration or confirmation."""
import json
from re_interval_development_budget import ROOT,OUT,used
if __name__=='__main__':
    from raven_mcs_re_interval.development_acquisition import acquire
    if not (OUT/'ENTRY_INTEGRATION_PASS_final.json').is_file():raise RuntimeError('entry integration required')
    acquire(ROOT,OUT,cpu_remaining=2700-used()-100)
