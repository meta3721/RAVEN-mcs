import sys
from pathlib import Path
ROOT=Path(__file__).resolve().parents[1];sys.path.insert(0,str(ROOT/'src'))
import torch
torch.set_num_threads(1);torch.set_num_interop_threads(1)
from raven_mcs_observed_feedback.execution import run
status=run(ROOT,ROOT/'results_observed_feedback_continuation_45011_20261014')
print(status);raise SystemExit(0 if status=='COMPLETE_T100_ACQUISITION' else 2)
