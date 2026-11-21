"""Exclusive new-version checkpoints; old v2 is never relabelled or migrated."""
import json
from pathlib import Path
from . import METHOD_VERSION
from .schema import InputError
from .lifecycle import DynamicWindowRunner
from raven_mcs.utils.hashing import sha256_file

def source_identity():
    root=Path(__file__).resolve().parents[2]
    files=list((root/'src/raven_mcs_re_interval').glob('*.py'))+list((root/'src/raven_mcs').rglob('*.py'))
    files.append(root/'scripts/windows_cpu_meter.py')
    return {str(p.relative_to(root).as_posix()):sha256_file(p) for p in sorted(files)}

def save_checkpoint(path,runner):
    with Path(path).open('x',encoding='utf-8') as f:
        json.dump(dict(method=METHOD_VERSION,q_event='I(100)|H,R=1,E=1',
            evidence_status='IMPLEMENTATION_ONLY',sources=source_identity(),state=runner.to_dict()),f,allow_nan=False)

def restore_checkpoint(path,*,backend):
    value=json.loads(Path(path).read_text(encoding='utf-8'))
    if value.get('method')!=METHOD_VERSION or value.get('q_event')!='I(100)|H,R=1,E=1':
        raise InputError('checkpoint method/estimand mismatch; explicit old v2 path required')
    if value.get('sources')!=source_identity():raise InputError('revision checkpoint computational sources changed')
    return DynamicWindowRunner.from_dict(value['state'],backend=backend)
