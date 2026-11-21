"""One-time S3 version fork after the frozen S2 gate; keeps v2 byte-identical."""
import json
from pathlib import Path
from revision_feasibility_budget import ROOT,OUT

if __name__=='__main__':
    assert json.loads((OUT/'S2_RESULT.json').read_text())['status']=='PASS'
    dst=ROOT/'src/raven_mcs_re_interval';dst.mkdir(exist_ok=False)
    names=['schema','probability','predictor','planner','lifecycle','preview','stage1','isolation']
    for name in names:
        text=(ROOT/f'src/raven_mcs/control/{name}.py').read_text(encoding='utf-8')
        text=text.replace('raven_mcs.control','raven_mcs_re_interval')
        text=text.replace('from raven_mcs_re_interval.process_budget','from raven_mcs.control.process_budget')
        text=text.replace('from raven_mcs_re_interval.calibration_identity','from raven_mcs.control.calibration_identity')
        (dst/f'{name}.py').write_text(text,encoding='utf-8')
    (dst/'__init__.py').write_text('"""Opt-in R/E interval revision; no experiment starts on import."""\nMETHOD_VERSION="reachability_stop/conditional-bundle-RE-interval-v3"\n',encoding='utf-8')
    print('Created separate version package; original raven_mcs untouched')
