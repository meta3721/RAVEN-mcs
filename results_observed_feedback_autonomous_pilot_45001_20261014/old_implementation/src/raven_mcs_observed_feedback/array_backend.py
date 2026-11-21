"""Explicit isolated math fixture; no SGD capability."""
import copy
import numpy as np
from .schema import InputError

class ArrayBackend:
    """Isolated deterministic update fixture, never a local-training substitute."""
    kind='isolated_array_backend'

    def __init__(self, theta):
        self.theta=np.asarray(theta,dtype=float).copy()
        if self.theta.ndim!=1 or not np.all(np.isfinite(self.theta)):
            raise InputError("invalid server vector")
        self.versions={0:self.theta.copy()}
        self.work={};self.updates={}
        self.local_optimizer_steps=0

    def has_version(self, version): return version in self.versions

    def prepare_work(self, registration, summary):
        self.work[registration.key]=dict(downloaded_version=registration.downloaded_version,
                                         weights=list(summary.local_weights),training_started=False)

    def start_local_training(self, *args, **kwargs):
        raise InputError("array fixture cannot execute local training")

    def complete(self, key, update):
        value=np.asarray(update,dtype=float)
        if key not in self.work or value.shape!=self.theta.shape or not np.all(np.isfinite(value)):
            raise InputError("missing/malformed actual update")
        self.updates[key]=value.copy()

    def apply(self, keys, alpha, eta, new_version):
        if any(k not in self.updates for k in keys):
            raise InputError("actual update missing; refusing consumption")
        new=self.theta.copy()
        for k,a in zip(keys,alpha): new-=eta*a*self.updates[k]
        if not np.all(np.isfinite(new)): raise InputError("nonfinite server update")
        self.theta=new;self.versions[new_version]=new.copy()
        for key in keys:self.updates.pop(key)
        return {}

    def to_dict(self):
        return dict(kind=self.kind,theta=self.theta.tolist(),versions={str(k):v.tolist() for k,v in self.versions.items()},
                    work=copy.deepcopy(self.work),updates={k:v.tolist() for k,v in self.updates.items()},
                    local_optimizer_steps=self.local_optimizer_steps)

    def restore(self,obj):
        if obj['kind']!=self.kind: raise InputError("backend checkpoint identity mismatch")
        self.theta=np.asarray(obj['theta'],dtype=float)
        self.versions={int(k):np.asarray(v,dtype=float) for k,v in obj['versions'].items()}
        self.work=copy.deepcopy(obj['work']);self.updates={k:np.asarray(v,dtype=float) for k,v in obj['updates'].items()}
        self.local_optimizer_steps=obj['local_optimizer_steps']


