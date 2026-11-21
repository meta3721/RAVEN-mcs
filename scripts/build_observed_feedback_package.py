"""Create independent immutable schemas and exact stage1 reuse; no experiments."""
import json,hashlib
from pathlib import Path
from observed_feedback_implementation_budget import ROOT,OUT,REPORT
def digest(p):return hashlib.sha256(p.read_bytes()).hexdigest()
if __name__=='__main__':
    old=json.loads((ROOT/'results_observed_feedback_preparation_20261013/PROTECTED_BEFORE.json').read_text())
    for p,h in old.items():assert digest(Path(p))==h,p
    prep=ROOT/'ccf-review-report/observed_feedback_preparation_20261013'
    texts={p.name:p.read_text(encoding='utf-8') for p in prep.glob('*.md')};assert len(texts)==6
    protected={**old,**{str(p):digest(p) for p in prep.glob('*.md')}}
    protected.update({str(p):digest(p) for p in (ROOT/'src/raven_mcs').rglob('*.py')})
    with (OUT/'PROTECTED_BEFORE.json').open('x') as f:json.dump(protected,f,indent=2)
    with (OUT/'FROZEN_INPUTS.json').open('x') as f:json.dump(dict(spec_hash=digest(prep/'METHOD_SPEC_CANDIDATE.md'),
        boundary_hash=digest(REPORT/'EXECUTION_BOUNDARY_FROZEN.md'),prior_reports_read=sorted(texts),protected_files=len(protected)),f,indent=2)
    dest=ROOT/'src/raven_mcs_observed_feedback';dest.mkdir(exist_ok=False)
    (dest/'__init__.py').write_text('"""Observed causal feedback; independent identity, no future predictor."""\nMETHOD_VERSION="reachability_stop/observed-feedback-v1"\n')
    source=(ROOT/'src/raven_mcs_re_interval/schema.py').read_text().replace('raven_mcs_re_interval','raven_mcs_observed_feedback')
    for line in ('    horizon: float = 8.\n','    scenarios: int = 4\n','    tail_interval: float = 2.\n','    minimum_risk: int = 5\n','    predictor_version: str\n'):
        assert line in source;source=source.replace(line,'')
    source=source.replace('    method_version: str = METHOD_VERSION','    theta: float = .02\n    kappa: float = .10\n    patience: float = .20\n    method_version: str = METHOD_VERSION')
    source=source.replace('deadline=4., horizon=8., scenarios=4, age_max=5,','deadline=4., age_max=5,')
    source=source.replace('warmup=20., tail_interval=2., age_weight=.02, wait_weight=.20,','warmup=20., age_weight=.02, wait_weight=.20,')
    source=source.replace('minimum_clients=3, minimum_risk=5, scoring_tolerance=1e-7,','minimum_clients=3, scoring_tolerance=1e-7, theta=.02, kappa=.10, patience=.20,')
    source=source.replace('configuration changes frozen RE-interval-v3 definition','configuration changes frozen OF-v1 definition')
    source=source.replace('    duration: float\n','    duration: float\n    omega: tuple[float,...] = ()\n')
    source=source.replace("    service_parameters_hash: str = ''","    service_parameters_hash: str = ''\n    q_model_version: str = ''")
    source=source.replace("        if not self.mu or abs(sum(self.mu)-1)","        if self.calibration_only:raise InputError('calibration_only not authorized for OF-v1')\n        if self.experiment_end!=100.:raise InputError('OF-v1 requires T100')\n        if self.last_release and len(self.last_release.omega)!=len(self.mu):raise InputError('last actual omega missing')\n        if not self.mu or abs(sum(self.mu)-1)")
    source=source.replace("obj['last_release']=ReleaseSummary(**obj['last_release'])","obj['last_release']=ReleaseSummary(**dict(obj['last_release'],omega=tuple(obj['last_release']['omega'])))")
    (dest/'schema.py').write_text(source)
    stage=(ROOT/'src/raven_mcs_re_interval/stage1.py').read_text().replace('raven_mcs_re_interval','raven_mcs_observed_feedback')
    (dest/'stage1.py').write_text(stage)
    lifecycle=(ROOT/'src/raven_mcs_re_interval/lifecycle.py').read_text()
    array=lifecycle[lifecycle.index('class ArrayBackend:'):lifecycle.index('class DynamicWindowRunner:')]
    (dest/'array_backend.py').write_text('"""Explicit isolated math fixture; no SGD capability."""\nimport copy\nimport numpy as np\nfrom .schema import InputError\n\n'+array)
    print(json.dumps(dict(status='SCHEMAS_CREATED',old_files_preserved=True,production_training=0)))
