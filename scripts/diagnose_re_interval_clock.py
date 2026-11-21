"""Single saved failing prediction, reveal invalid clock fields; no producer replay."""
import json
from re_interval_development_budget import OUT
from raven_mcs_re_interval.schema import DecisionSnapshot
from raven_mcs_re_interval.predictor import FrozenServiceModel
from raven_mcs_re_interval.planner import plan,_ForecastState
from raven_mcs.control.persistence import exclusive_json
if __name__=='__main__':
    snapshot=DecisionSnapshot.from_dict(json.loads((OUT/'snapshots/tick0202.json').read_text())['snapshot'])
    model=FrozenServiceModel.from_dict(json.loads((OUT/'trajectory/SERVICE_FROZEN_AT_20.json').read_text())['model'])
    original=_ForecastState.snapshot;found=[]
    def capture(self):
        try:return original(self)
        except Exception:
            found.append(dict(now=self.now,version=self.version,invalid=[dict(key=x.registration.key,
                registered_at=x.registration.registered_at,clock_delta=x.registration.registered_at-self.now,
                downloaded_version=x.registration.downloaded_version,version_delta=x.registration.downloaded_version-self.version)
                for x in self.pending.values() if x.registration.registered_at>self.now or x.registration.downloaded_version>self.version]))
            raise
    _ForecastState.snapshot=capture
    try:plan(snapshot,model)
    except Exception as exc:
        exclusive_json(OUT/'CLOCK_FAILURE_DIAGNOSIS.json',dict(error=str(exc),snapshot='snapshots/tick0202.json',captured=found,
            no_producer_rng_draw=True,no_training=True))
        print(json.dumps(found))
    else:raise RuntimeError('saved failure did not reproduce')
