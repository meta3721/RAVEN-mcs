"""Causal discrete competing risks and client-compatible joint marks."""
from __future__ import annotations

from dataclasses import asdict, dataclass
import math
import numpy as np

from raven_mcs_re_interval.schema import InputError, Registration, Stage1Summary, finite
from raven_mcs_re_interval.probability import q_model_from_dict


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
class OpportunityMark:
    key: str
    client: str
    time: float
    device_class: str
    network_class: str
    known_at: float
    R: int
    registration_age: int
    clock_run_id: str
    provenance: str

    def __post_init__(self):
        if self.R not in (0,1) or self.registration_age<0 or not self.clock_run_id or not self.provenance:
            raise InputError('incomplete all-registration opportunity mark')


@dataclass(frozen=True)
class UnknownSupport:
    key: str
    earliest_effect_time: float
    reason: str


@dataclass(frozen=True)
class ConditionalScenario:
    events: tuple[ForecastEvent,...]
    unknowns: tuple[UnknownSupport,...] = ()

    def to_dict(self):return asdict(self)

    @classmethod
    def from_dict(cls,obj):
        return cls(tuple(ForecastEvent(e['time'],e['kind'],Registration(**e['registration']),
            Stage1Summary.from_dict(e['summary']) if e['summary'] is not None else None) for e in obj['events']),
            tuple(UnknownSupport(**u) for u in obj['unknowns']))


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
    joint_opportunities: tuple[OpportunityMark,...] = ()
    resource_model: str = 'UNDECLARED'

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
        if any(o.time>self.as_of or o.known_at>self.as_of for o in self.joint_opportunities):
            raise InputError('all-registration history exceeds cutoff')
        if self.joint_opportunities and len({o.clock_run_id for o in self.joint_opportunities})!=1:
            raise InputError('mixed run clocks need an explicit transport model')
        object.__setattr__(self,'q_model',FrozenDict(self.q_model))

    @classmethod
    def from_history(cls, records, *, cutoff, version, q_model, opportunities=(), opportunity_history=(),
                     schedule_complete_until=None,joint_opportunities=(),resource_model='UNDECLARED'):
        """Build from already observed records, including right censoring.

        Called only on authorized history. B0 uses small explicit records, not
        event traces, fitted performance models or random trajectories.
        """
        records=tuple(records)
        if any(r.observed_until>cutoff or r.registration.registered_at>cutoff for r in records):
            raise InputError("service history exceeds calibration cutoff")
        bykey={o.key:o for o in joint_opportunities}
        if any(r.registration.key not in bykey for r in records):
            raise InputError('service fitting requires ALL-registration R/age provenance')
        records=tuple(r for r in records if bykey[r.registration.key].R==1 and bykey[r.registration.key].registration_age<=5)
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
                   tuple(opportunity_history),schedule_complete_until,
                   joint_opportunities=tuple(joint_opportunities),resource_model=resource_model)

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
        """R/age are joint all-registration marks; unknowns remain explicit."""
        if self.as_of>snapshot.window_open or self.version!=snapshot.predictor_version:
            raise InputError('predictor not frozen before window')
        current_run=(snapshot.clock_namespace or {}).get('run_id','isolated_fixture' if snapshot.isolated_test else '')
        if self.joint_opportunities and any(o.clock_run_id!=current_run for o in self.joint_opportunities):
            raise InputError('joint opportunity clock requires same run; no implicit cross-run transport')
        end=min(snapshot.now+snapshot.config.horizon,snapshot.experiment_end)
        if self.opportunity_history and not self.joint_opportunities:
            raise InputError('R/age missing: completion-only marks cannot define opportunity stream')
        scenes=[];tick=int(round(snapshot.now/self.grid))
        for sc in range(4):
            rng=np.random.default_rng(np.random.SeedSequence([snapshot.seed,tick,sc,94031]))
            events=[];unknown=[]
            def service(reg,start,mark=None):
                try:
                    event=self._sample_outcome(reg,start,end,rng,joint_mark=mark)
                    if event is not None:events.append(event)
                except UnsupportedPrediction as exc:
                    text=str(exc);when=start
                    if text.startswith('INSUFFICIENT_RISK:'):
                        l=int(text.rsplit(':',1)[1]);when=max(start,reg.registered_at+(l-1)*self.grid)
                    unknown.append(UnknownSupport(reg.key,when,text))
            for item in snapshot.in_flight:service(item.registration,snapshot.now)
            opportunities=[]
            if self.schedule_complete_until is None:
                batches={}
                for o in self.joint_opportunities:batches.setdefault(int(math.floor(o.time)),[]).append(o)
                if not batches:
                    unknown.append(UnknownSupport('opportunity_clock',snapshot.now,'NO_LAWFUL_JOINT_CLOCK'))
                else:
                    clocks=sorted(batches)
                    for clock in range(int(math.floor(snapshot.now)),int(math.floor(end))+1):
                        template=batches[clocks[int(rng.integers(len(clocks)))]]
                        for j,o in enumerate(template):
                            t=round(clock+o.time-math.floor(o.time),10)
                            if snapshot.now<t<=end:opportunities.append((f'hist::{tick}::{sc}::{clock}::{j}',t,o))
            elif self.schedule_complete_until<end-1e-9:
                unknown.append(UnknownSupport('clock_horizon',snapshot.now,'PUBLIC_CLOCK_HORIZON_UNSUPPORTED'))
            else:
                for o in self.opportunities:
                    if not snapshot.now<o.time<=end:continue
                    history=[h for h in self.joint_opportunities if (h.client,h.device_class,h.network_class)==(o.client,o.device_class,o.network_class)]
                    if not history:
                        unknown.append(UnknownSupport(o.key,o.time,'NO_JOINT_R_AGE_HISTORY'));continue
                    h=history[int(rng.integers(len(history)))]
                    opportunities.append((o.key,o.time,h))
            for key,t,o in sorted(opportunities,key=lambda x:(x[1],x[0])):
                reg=Registration(key,o.client,t,o.registration_age,o.device_class,o.network_class)
                if o.R==0 or o.registration_age>snapshot.config.age_max:
                    if self.resource_model!='exogenous_no_shared_contention':
                        unknown.append(UnknownSupport(key,t,'EXCLUDED_MESSAGE_RESOURCE_EFFECT_UNKNOWN'))
                    events.append(ForecastEvent(t,'register_outside_R' if o.R==0 else 'register_ineligible',reg))
                    continue
                events.append(ForecastEvent(t,'register',reg))
                marks=[m for m in self.marks if m.client==o.client and m.stratum==(o.device_class,o.network_class)]
                if not marks:
                    unknown.append(UnknownSupport(key,t,'NO_COMPATIBLE_MARK'));continue
                # Registration age is from ALL registrations, never the completion subset.
                mark=marks[int(rng.integers(len(marks)))];service(reg,t,mark)
            scenes.append(ConditionalScenario(tuple(sorted(events,key=lambda e:(e.time,0 if e.kind.startswith('register') else 1,e.registration.key))),tuple(unknown)))
        return tuple(scenes)

    def to_dict(self): return asdict(self)

    @classmethod
    def from_dict(cls,obj):
        obj=dict(obj)
        obj['cells']=tuple(RiskCell(tuple(x['stratum']),x['age_bin'],x['risk'],x['completions'],x['failures']) for x in obj['cells'])
        obj['marks']=tuple(JointMark(x['client'],tuple(x['stratum']),Stage1Summary.from_dict(x['summary']),
                                   x['observed_at'],x['downloaded_age']) for x in obj['marks'])
        for k in ('opportunities','opportunity_history'):
            obj[k]=tuple(PublicOpportunity(**x) for x in obj[k])
        obj['joint_opportunities']=tuple(OpportunityMark(**x) for x in obj.get('joint_opportunities',()))
        return cls(**obj)
