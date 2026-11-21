"""Fixed one-second reproducer of the old launcher race, inside safe root Job."""
from pathlib import Path
import json
from windows_cpu_meter import run_metered
ROOT=Path(__file__).resolve().parents[1]
OUT=ROOT/'results_calibration_diagnostic_20261013_122013'
if __name__=='__main__':
    r=run_metered([ROOT/'.venv_new/Scripts/python.exe','scripts/diagnostic_meter_workload.py','--mode','legacy'],
        OUT/'D1_legacy_delayed_attach.log',cpu_limit=5,wall_limit=10,cwd=ROOT,legacy_attach_delay=.2)
    print(json.dumps(r))
