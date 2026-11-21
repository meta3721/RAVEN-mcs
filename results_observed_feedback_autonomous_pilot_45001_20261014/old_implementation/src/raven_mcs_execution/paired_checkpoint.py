"""Verified data pair plus immutable atomic completion marker."""
import json,os
from pathlib import Path
from raven_mcs.utils.hashing import sha256_file

class PairedCheckpointStore:
    def __init__(self,root):self.root=Path(root);self.root.mkdir(exist_ok=True)
    def path(self,name):
        p=self.root/name
        if Path(name).name!=name:raise ValueError('checkpoint local name required')
        return p
    @staticmethod
    def validate_pair_content(packet,producer,identity,model_hash):
        state=packet['state']
        if (packet['method']!=identity['method'] or state['config']['method_version']!=identity['method'] or
            state['seed']!=identity['seed'] or state['clock_namespace']!=identity['clock_namespace'] or
            producer['clock_namespace']!=identity['clock_namespace'] or producer['checkpoint_hash']!=model_hash):
            raise ValueError('checkpoint content namespace mismatch')
        if producer['T']!=state['experiment_end'] or abs(producer['tick']*state['config']['grid']-state['now'])>1e-9:
            raise ValueError('model/private endpoint or observation cursor mismatch')
    def publish(self,name,model,private,identity,*,budget,save_reserve,interrupt_after_model=False):
        budget.require_save(save_reserve)
        marker=self.path(name+'.complete.json')
        if marker.exists():raise FileExistsError(marker)
        mp=self.path(name+'.model.pending');pp=self.path(name+'.private.pending')
        with mp.open('x',encoding='utf-8') as f:json.dump(model,f,allow_nan=False);f.flush();os.fsync(f.fileno())
        if interrupt_after_model:raise InterruptedError('deterministic save interruption before private file')
        model_hash=sha256_file(mp)
        private=dict(private,checkpoint=name+'.model.json',checkpoint_hash=model_hash)
        with pp.open('x',encoding='utf-8') as f:json.dump(private,f,allow_nan=False);f.flush();os.fsync(f.fileno())
        self.validate_pair_content(model,private,identity,model_hash)
        if sha256_file(mp)!=model_hash:raise ValueError('model changed during save')
        model_final=self.path(name+'.model.json');private_final=self.path(name+'.private.json')
        os.replace(mp,model_final);os.replace(pp,private_final)
        record=dict(schema='paired_checkpoint_commit_v1',identity=identity,model=model_final.name,private=private_final.name,
            model_hash=model_hash,private_hash=sha256_file(private_final),sizes=[model_final.stat().st_size,private_final.stat().st_size])
        temporary=self.path(name+'.marker.pending')
        with temporary.open('x',encoding='utf-8') as f:json.dump(record,f);f.flush();os.fsync(f.fileno())
        # Atomic exclusive publication. Pending files are never restore candidates.
        # On Windows rename is atomic and fails if the destination exists.
        # Avoid hardlinks, which this managed workspace does not permit.
        os.rename(temporary,marker)
        self.read(marker,expected_identity=identity)
        return marker
    def read(self,marker,*,expected_identity):
        marker=Path(marker)
        if marker.parent.resolve()!=self.root.resolve() or not marker.name.endswith('.complete.json'):raise ValueError('not a published checkpoint')
        record=json.loads(marker.read_text())
        if record['schema']!='paired_checkpoint_commit_v1' or record['identity']!=expected_identity:raise ValueError('checkpoint identity mismatch')
        model=self.path(record['model']);private=self.path(record['private'])
        if sha256_file(model)!=record['model_hash'] or sha256_file(private)!=record['private_hash']:raise ValueError('checkpoint pair hash mismatch')
        packet=json.loads(model.read_text());producer=json.loads(private.read_text())
        self.validate_pair_content(packet,producer,expected_identity,record['model_hash'])
        return packet,producer
    def latest(self,*,expected_identity):
        found=[]
        for p in self.root.glob('*.complete.json'):
            self.read(p,expected_identity=expected_identity);found.append(p)
        if not found:raise ValueError('no completed checkpoint')
        return sorted(found)[-1]

def read_legacy_pair(model_path,private_path):
    model_path=Path(model_path);private=json.loads(Path(private_path).read_text())
    if private['checkpoint_hash']!=sha256_file(model_path):raise ValueError('legacy pair checksum mismatch')
    model=json.loads(model_path.read_text())
    if model['state']['clock_namespace']!=private['clock_namespace']:raise ValueError('legacy pair namespace mismatch')
    return model,private
