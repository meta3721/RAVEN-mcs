"""Only the changed publication path; no model/Job benchmark or trajectory."""
import sys,json,tempfile,time
from pathlib import Path
ROOT=Path(__file__).resolve().parents[1];sys.path.insert(0,str(ROOT/'src'))
from observed_feedback_root_publisher import SharingTolerantPublisher
from raven_mcs_observed_feedback.budget_client import RootClient
OUT=ROOT/'results_observed_feedback_rolling_45011_20261014_s2'
p=Path(tempfile.mkdtemp(prefix='root_unit_',dir=OUT))/'root.json'
pub=SharingTolerantPublisher(dict(path=str(p),prior_batch=313.21875,prior_phase=0,batch_limit=3600,phase_limit=3600),60)
reader=RootClient(p)
for n in range(3):
 pub.publish(float(n),0.,force=True);v=reader.read();assert v['command_used']==n and v['sequence']==n+1
pub.publish(3.,0.,force=True,finished=True)
(OUT/'ROOT_PUBLICATION_CHECK.json').write_text(json.dumps(dict(status='PASS',scope='only workspace publication/read path',SGD=0,finished=json.loads(p.read_text())['finished']),indent=2));print('ROOT_WORKSPACE_PUBLICATION_PASS')
