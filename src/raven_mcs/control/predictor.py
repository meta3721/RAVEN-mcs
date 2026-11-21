"""Causal discrete competing risks and client-compatible joint marks."""
from __future__ import annotations

from dataclasses import asdict, dataclass
import math
import numpy as np

from raven_mcs.control.schema import InputError, Registration, Stage1Summary, finite
from raven_mcs.control.probability import q_model_from_dict


class FrozenDict(dict):
    """Deeply immutable model payload; serialization returns ordinary copies."""
    def __init__(self, value):
        def freeze(x):
            if isinstance(x,dict):return FrozenDict(x)
            if isinstance(x,(tuple,list)):return tuple(freeze(v) for v in x)
            return x
        dict.__init__(self,((k,freeze(v)) for k,v in dict(value).items()))
    def _deny(self,*args,**kwargs):raise TypeError("frozen predictor parameters")
    __setitem__=__delitem__=clear=pop=popitem=setdefault=update=__ior__=_deny
    def __deepcopy__(self,memo):
        import copy
        return {k:copy.deepcopy(v,memo) for k,v in self.items()}
    def __reduce__(self):return (FrozenDict,(dict(self),))


class UnsupportedPrediction(Exception):
    pass


@dataclass(frozen=True)
class ServiceRecord:
    registration: Registration
    observed_until: float
    outcome: str  # completion / notified_failure / right_censored
    summary: Stage1Summary | None = None
    registration_version: int | None = None

    def __post_init__(self):
        if self.observed_until < self.registration.registered_at:
            raise InputError("invalid service exposure")
        if self.outcome not in {'completion','notified_failure','right_censored'}:
            raise InputError("invalid competing risk event")
        if self.outcome=='completion' and (self.summary is None or self.summary.frozen_at>self.observed_until):
            raise InputError("completion lacks lawful joint mark")
        if self.outcome!='completion' and self.summary is not None:
            raise InputError("noncompletion cannot reveal payload")
        if self.registration_version is not None and self.registration_version<self.registration.downloaded_version:
            raise InputError("historical download exceeds registration version")


@dataclass(frozen=True)
class RiskCell:
    stratum: tuple[str,str]
    age_bin: int
    risk: int
    completions: int
    failures: int

    def __post_init__(self):
        if self.age_bin < 1 or min(self.risk,self.completions,self.failures)<0 or self.completions+self.failures>self.risk:
            raise InputError("invalid competing risk counts")


@dataclass(frozen=True)
class JointMark:
    client: str
    stratum: tuple[str,str]
    summary: Stage1Summary
    observed_at: float
    downloaded_age: int | None


@dataclass(frozen=True)
class PublicOpportunity:
    """Preannounced registration schedule, not a simulator's future event."""
    key: str
    client: str
    time: float
    device_class: str
    network_class: str
    known_at: float


@dataclass(frozen=True)
class ForecastEvent:
    time: float
    kind: str  # register / completion / failure
    registration: Registration
    summary: Stage1Summary | None = None


@dataclass(frozen=True)
class FrozenServiceModel:
    version: str
    as_of: float
    cells: tuple[RiskCell,...]
    marks: tuple[JointMark,...]
    q_model: dict
    opportunities: tuple[PublicOpportunity,...] = ()
    opportunity_history: tuple[PublicOpportunity,...] = ()
    schedule_complete_until: float | None = None
    grid: float = .1
    minimum_risk: int = 5

    def __post_init__(self):
        finite((self.as_of,), 'predictor time', nonnegative=True)
        if self.grid != .1 or self.minimum_risk != 5 or not self.version:
            raise InputError("predictor configuration mismatch")
        if q_model_from_dict(self.q_model).as_of > self.as_of:
            raise InputError("predictor contains a future q model")
        if any(m.observed_at>self.as_of or m.summary.frozen_at>m.observed_at for m in self.marks):
            raise InputError("predictor contains future joint marks")
        if any(o.known_at>self.as_of for o in self.opportunities):
            raise InputError("future opportunity catalogue not public at snapshot time")
        if any(o.time>self.as_of or o.known_at>self.as_of for o in self.opportunity_history):
            raise InputError("opportunity history contains future registrations")
        object.__setattr__(self,'q_model',FrozenDict(self.q_model))

    @classmethod
    def from_history(cls, records, *, cutoff, version, q_model, opportunities=(), opportunity_history=(),
                     schedule_complete_until=None):
        """Build from already observed records, including right censoring.

        Called only on authorized history. B0 uses small explicit records, not
        event traces, fitted performance models or random trajectories.
        """
        records=tuple(records)
        if any(r.observed_until>cutoff or r.registration.registered_at>cutoff for r in records):
            raise InputError("service history exceeds calibration cutoff")
        strata=sorted({r.registration.stratum for r in records})
        cells=[];marks=[]
        for layer in strata:
            rows=[r for r in records if r.registration.stratum==layer]
            max_bin=max((math.ceil((r.observed_until-r.registration.registered_at)/.1-1e-9) for r in rows),default=0)
            for l in range(1,max_bin+1):
                lower=(l-1)*.1; upper=l*.1
                risk=comp=fail=0
                for r in rows:
                    duration=r.observed_until-r.registration.registered_at
                    in_bin=lower+1e-9 < duration <= upper+1e-9
                    exposed=duration>=upper-1e-9 or (r.outcome!='right_censored' and in_bin)
                    risk+=int(exposed)
                    comp+=int(in_bin and r.outcome=='completion')
                    fail+=int(in_bin and r.outcome=='notified_failure')
                cells.append(RiskCell(layer,l,risk,comp,fail))
        for r in records:
            if r.outcome=='completion':
                marks.append(JointMark(r.registration.client,r.registration.stratum,r.summary,
                                      r.observed_until,r.registration_version-r.registration.downloaded_version
                                      if r.registration_version is not None else None))
        return cls(version,cutoff,tuple(cells),tuple(marks),q_model.to_dict(),tuple(opportunities),
                   tuple(opportunity_history),schedule_complete_until)

    def _sample_outcome(self, registration, now, end, rng,*,joint_mark=None):
        elapsed=max(0.,now-registration.registered_at)
        first=int(math.floor(elapsed/self.grid+1e-9))+1
        last=int(math.floor((end-registration.registered_at)/self.grid+1e-9))
        cell_map={(r.stratum,r.age_bin):r for r in self.cells}
        compatible=[m for m in self.marks if m.client==registration.client and m.stratum==registration.stratum]
        if not compatible:
            raise UnsupportedPrediction(f"NO_COMPATIBLE_MARK:{registration.client}:{registration.stratum}")
        # Stop as soon as a sampled terminal event occurs; never invent a tail
        # probability if the still-surviving path reaches insufficient support.
        for l in range(first,last+1):
            cell=cell_map.get((registration.stratum,l))
            if cell is None or cell.risk<self.minimum_risk:
                raise UnsupportedPrediction(f"INSUFFICIENT_RISK:{registration.stratum}:{l}")
            value=float(rng.random()); time=round(registration.registered_at+l*self.grid,10)
            if value < cell.completions/cell.risk:
                mark=joint_mark if joint_mark is not None else compatible[int(rng.integers(len(compatible)))]
                return ForecastEvent(time,'completion',registration,mark.summary)
            if value < (cell.completions+cell.failures)/cell.risk:
                return ForecastEvent(time,'failure',registration)
        return None

    def sample_scenarios(self, snapshot):
        if self.as_of>snapshot.window_open or self.version!=snapshot.predictor_version:
            raise InputError("predictor was not frozen before window open")
        end=min(snapshot.now+snapshot.config.horizon,snapshot.experiment_end)
        if self.schedule_complete_until is None and not self.opportunity_history:
            raise UnsupportedPrediction("NO_PUBLIC_OR_HISTORICAL_OPPORTUNITY_CLOCK")
        if self.schedule_complete_until is not None and self.schedule_complete_until < end-1e-9:
            raise UnsupportedPrediction("PUBLIC_CLOCK_HORIZON_UNSUPPORTED")
        scenarios=[]
        tick=int(round(snapshot.now/self.grid))
        for sc in range(snapshot.config.scenarios):
            rng=np.random.default_rng(np.random.SeedSequence([snapshot.seed,tick,sc,94031]))
            events=[]
            for item in snapshot.in_flight:
                result=self._sample_outcome(item.registration,snapshot.now,end,rng)
                if result is not None: events.append(result)
            opportunities=[o for o in self.opportunities if snapshot.now<o.time<=end]
            if self.schedule_complete_until is None:
                # Joint historical registration batches, sampled on the public
                # periodic clock. No independent reassignment of client marks.
                batches={}
                for o in self.opportunity_history:
                    batches.setdefault(int(math.floor(o.time)),[]).append(o)
                clocks=sorted(batches)
                for clock in range(int(math.floor(snapshot.now)),int(math.floor(end))+1):
                    templates=batches[clocks[int(rng.integers(len(clocks)))]]
                    for j,o in enumerate(templates):
                        time=clock+(o.time-math.floor(o.time))
                        if snapshot.now<time<=end:
                            opportunities.append(PublicOpportunity(f'hist::{tick}::{sc}::{clock}::{j}',
                                o.client,time,o.device_class,o.network_class,self.as_of))
            for o in sorted(opportunities,key=lambda x:(x.time,x.key)):
                marks=[m for m in self.marks if m.client==o.client and m.stratum==(o.device_class,o.network_class)]
                if not marks: raise UnsupportedPrediction(f"NO_COMPATIBLE_MARK:{o.client}")
                future_mark=marks[int(rng.integers(len(marks)))]
                age=future_mark.downloaded_age
                if age is None:raise UnsupportedPrediction("HISTORICAL_REGISTRATION_AGE_UNAVAILABLE")
                # Actual predicted download version is resolved at this event
                # in each plan, since server versions differ between plans.
                reg=Registration(o.key,o.client,o.time,age,o.device_class,o.network_class)
                events.append(ForecastEvent(o.time,'register',reg))
                result=self._sample_outcome(reg,o.time,end,rng,joint_mark=future_mark)
                if result is not None:events.append(result)
            scenarios.append(tuple(sorted(events,key=lambda x:(x.time,0 if x.kind=='register' else 1,x.registration.key))))
        return tuple(scenarios)

    def to_dict(self): return asdict(self)

    @classmethod
    def from_dict(cls,obj):
        obj=dict(obj)
        obj['cells']=tuple(RiskCell(tuple(x['stratum']),x['age_bin'],x['risk'],x['completions'],x['failures']) for x in obj['cells'])
        obj['marks']=tuple(JointMark(x['client'],tuple(x['stratum']),Stage1Summary.from_dict(x['summary']),
                                   x['observed_at'],x['downloaded_age']) for x in obj['marks'])
        for k in ('opportunities','opportunity_history'):
            obj[k]=tuple(PublicOpportunity(**x) for x in obj[k])
        return cls(**obj)
