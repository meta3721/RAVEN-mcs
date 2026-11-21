"""Finite empirical planning on cloned summaries; never applies a model update."""
from __future__ import annotations

from dataclasses import asdict, dataclass, replace
import copy
import math
import numpy as np

from raven_mcs.aggregation.debt import update_debt
from raven_mcs_re_interval.schema import DecisionSnapshot, Delivered, InFlight, Registration, ReleaseSummary, InputError
from raven_mcs_re_interval.probability import RegistrationFeatures, q_model_from_dict,policy_context_hash
from raven_mcs_re_interval.preview import preview_release
from raven_mcs_re_interval.predictor import FrozenServiceModel, UnsupportedPrediction, ConditionalScenario
from raven_mcs.utils.hashing import sha256_json


@dataclass(frozen=True)
class Decision:
    action: str
    reason: str
    selected_offset: float | None
    plan_scores: tuple[tuple[float,float],...]=()
    p2_solves: int = 0
    cache_hits: int = 0
    scenario_digest: str = ''
    control_cpu_seconds: float = 0.
    wall_seconds: float = 0.
    forecast_only: bool = True
    evidence_role: str = 'deterministic_interface_or_empirical_planning'
    variance_transition: str = 'zero_unknown_gradient_increment'
    intervals: tuple = ()
    action_intervals: tuple = ()
    unknown_support: tuple = ()
    proven: bool = False


def fixed_fallback(snapshot, reason):
    close=snapshot.now-snapshot.window_open>=snapshot.config.tail_interval-1e-9
    return Decision('CLOSE' if close else 'WAIT',reason,0. if close else None)


def validate_planning_inputs(snapshot, model):
    # Invalid q/design inputs must not be hidden by the prediction fallback.
    for msg in snapshot.pool:
        msg.q.require(isolated_test=snapshot.isolated_test,calibration_only=snapshot.calibration_only)
    for item in snapshot.in_flight:
        item.q.require(isolated_test=snapshot.isolated_test,calibration_only=snapshot.calibration_only)
    if model.as_of>snapshot.window_open or model.version!=snapshot.predictor_version:
        raise InputError("predictor not frozen for this window")
    if snapshot.experiment_end!=100. or len(snapshot.mu)!=172:
        raise InputError('interval proof scope requires the frozen target and T=100')
    if snapshot.now-snapshot.window_open>4+1.1e-9:
        raise InputError('missed original hard deadline; outside interval proof domain')
    for t in (snapshot.now,snapshot.window_open,snapshot.experiment_end):
        if abs(t-round(t/.1)*.1)>1.1e-9:
            raise InputError('release/decision clock must use the original global grid')
    if snapshot.last_release and not 0<=snapshot.last_release.duration<=4+1.1e-9:
        raise InputError('previous release exceeds proved duration domain')


def candidate_offsets(snapshot):
    remaining=max(0.,snapshot.config.deadline-(snapshot.now-snapshot.window_open))
    offsets=sorted({round(x,10) for x in (0.,.1,.5,1.,2.,remaining) if x<=remaining+1e-9})
    if len(snapshot.pool)<snapshot.config.minimum_clients:
        offsets=[x for x in offsets if x!=0.]
    return tuple(offsets)


class _ForecastState:
    def __init__(self,snapshot,model):
        self.initial=snapshot;self.model=model
        self.now=snapshot.now;self.open=snapshot.window_open;self.version=snapshot.model_version
        self.pool={m.registration.client:m for m in snapshot.pool}
        self.pending={x.registration.key:x for x in snapshot.in_flight}
        self.debt=np.asarray(snapshot.debt).copy();self.last=snapshot.last_release
        self.consumed=set();self.closed=[]
        self.registrations={x.registration.key:x.registration for x in snapshot.in_flight}

    def snapshot(self):
        return replace(self.initial,now=self.now,window_open=self.open,model_version=self.version,
            debt=tuple(self.debt),pool=tuple(sorted(self.pool.values(),key=lambda x:x.registration.client)),
            in_flight=tuple(self.pending[k] for k in sorted(self.pending)),last_release=self.last)

    def expire(self):
        for cid,msg in list(self.pool.items()):
            if self.version-msg.registration.downloaded_version>self.initial.config.age_max:self.pool.pop(cid)
        for key,item in list(self.pending.items()):
            if self.version-item.registration.downloaded_version>self.initial.config.age_max:self.pending.pop(key)

    def event(self,event):
        reg=event.registration
        if event.kind in ('register_outside_R','register_ineligible'):
            if self.model.resource_model!='exogenous_no_shared_contention':
                raise UnsupportedPrediction('EXCLUDED_MESSAGE_RESOURCE_EFFECT_UNKNOWN')
            # Physical attempts remain in the live runner. This declared service
            # model has no shared contention, so these records cannot alter P2.
            self.registrations[reg.key]=reg
            return
        if event.kind=='register':
            # At forecast registration the placeholder downloaded_version holds
            # a historical lag, not another policy's server version.
            if reg.downloaded_version>self.version:
                raise UnsupportedPrediction('REGISTRATION_AGE_EXCEEDS_AVAILABLE_VERSION')
            reg=replace(reg,downloaded_version=self.version-reg.downloaded_version)
            features=RegistrationFeatures(self.version-reg.downloaded_version,reg.device_class,reg.network_class,
                max(0.,self.open+self.initial.config.deadline-reg.registered_at),len(self.pool),len(self.pending),
                policy_context_hash(self.initial.config,self.initial.settings,self.initial.mu,self.initial.predictor_version,self.initial.probability_applicability),reg.registered_at,
                clock_run_id=(self.initial.clock_namespace or {}).get('run_id',''),service_parameters_hash=self.initial.service_parameters_hash)
            q=q_model_from_dict(self.model.q_model).predict_at_registration(features)
            q.require(isolated_test=self.initial.isolated_test,calibration_only=self.initial.calibration_only)
            self.pending[reg.key]=InFlight(reg,q);self.registrations[reg.key]=reg
            return
        item=self.pending.pop(reg.key,None)
        if item is None:return  # expired in an earlier predicted window
        reg=item.registration
        if event.kind=='failure':return
        if event.kind!='completion' or event.summary is None:raise InputError("invalid predictive event")
        if event.summary.design_enabled!=self.initial.config.design.enabled:
            raise UnsupportedPrediction("JOINT_MARK_DESIGN_INCOMPATIBLE")
        if self.version-reg.downloaded_version>self.initial.config.age_max:return
        summary=replace(event.summary,frozen_at=reg.registered_at,
            provenance='forecast_joint_mark/'+event.summary.provenance,
            estimator_version='forecast/'+event.summary.estimator_version,
            design_source=self.initial.config.design.source)
        msg=Delivered(reg,summary,item.q,event.time)
        previous=self.pool.get(reg.client)
        if previous and (previous.registration.registered_at,previous.key)>(reg.registered_at,reg.key):return
        self.pool[reg.client]=msg

    def release(self,cache,counters):
        if self.pool:
            if len(self.pool)>43:raise InputError('interval alpha error bound exceeds K=43 scope')
            snapshot=self.snapshot()
            # Clock/revision do not enter P2; avoid repeating identical solves.
            cache_key=sha256_json(dict(pool=[asdict(m) for m in snapshot.pool],debt=list(self.debt),
                version=self.version,variance=snapshot.variance,settings=asdict(snapshot.settings),mu=snapshot.mu))
            if cache_key in cache:
                preview=cache[cache_key];counters['hits']+=1
            else:
                preview=preview_release(snapshot,with_reachability=False)
                cache[cache_key]=preview;counters['solves']+=1
            if set(preview.keys)&self.consumed:raise InputError("duplicate forecast consumption")
            self.consumed.update(preview.keys)
            self.debt=update_debt(self.debt,mu=np.asarray(snapshot.mu),omega=np.asarray(preview.omega),
                                  eta=snapshot.settings.server_eta)
            self.last=ReleaseSummary(self.now,preview.ell,preview.age,self.now-self.open)
            self.version+=1;self.pool.clear()
        self.closed.append(dict(time=self.now,version=self.version,consumed=sorted(self.consumed),
                                last=asdict(self.last) if self.last else None))
        self.open=self.now;self.expire()


def evaluate_plans(snapshot, model, scenarios, offsets=None, *, horizon=None):
    """Exact implementation path also used for hand-authored B0 scenarios.

    Only the test calls this with explicit deterministic forecast events. The
    production caller always uses four historical conditional samples.
    """
    offsets=candidate_offsets(snapshot) if offsets is None else tuple(offsets)
    if len(scenarios)!=snapshot.config.scenarios:raise InputError("exactly four common scenarios required")
    end=min(snapshot.now+(snapshot.config.horizon if horizon is None else horizon),snapshot.experiment_end)
    count=int(round((end-snapshot.now)/snapshot.config.grid))
    if count<=0:return Decision('CLOSE','experiment_end',0.)
    cache={};counters=dict(solves=0,hits=0);scores=[]
    for offset in offsets:
        values=[]
        for events in scenarios:
            state=_ForecastState(snapshot,model);index=0;first=False;score_sum=0.
            if offset==0:
                state.release(cache,counters);first=True
            for tick in range(1,count+1):
                now=round(snapshot.now+tick*snapshot.config.grid,10)
                while index<len(events) and events[index].time<=now+1e-9:
                    event=events[index]
                    if event.time<=snapshot.now:raise InputError("forecast contains an already observed event")
                    state.now=event.time;state.event(event);index+=1
                state.now=now;state.expire()
                elapsed=now-state.open
                deadline=elapsed>=snapshot.config.deadline-1e-9
                planned=(not first and now>=snapshot.now+offset-1e-9 and
                         len(state.pool)>=snapshot.config.minimum_clients)
                tail=first and elapsed>=snapshot.config.tail_interval-1e-9
                if deadline or planned or tail:
                    state.release(cache,counters);first=True
                score_sum+=state.last.score(snapshot.config) if state.last else 1.
            values.append(score_sum/count)
        scores.append((float(offset),float(np.mean(values))))
    if not scores: return fixed_fallback(snapshot,'no_legal_candidate/fixed_time_2')
    best=min(v for _,v in scores)
    offset=min(o for o,v in scores if v<=best+snapshot.config.scoring_tolerance)
    return Decision('CLOSE' if offset==0 else 'WAIT','conditional_bundle',offset,tuple(scores),
                    counters['solves'],counters['hits'],sha256_json([[asdict(e) for e in s] for s in scenarios]))


def score_envelope():
    """Outward floating envelope of the exact [0,1.22] score (K<=43,G=172)."""
    k,g=43,172;u=np.finfo(float).eps
    da=1e-7+8*k*u;dm=1e-9+2*g*u;gamma=2*g*u/(1-2*g*u)
    ell=.5*((1+gamma)*(1+(2*k+1)*da)+(1+dm))*(1+gamma)
    arithmetic=64*(g+k+1)*u
    return (math.nextafter(-.02*k*da-arithmetic,-math.inf),
        math.nextafter(ell+.02*(1+(k+1)*da)+.05*(4+1e-9+1e-10+200*u)+arithmetic,math.inf))


def evaluate_interval_plans(snapshot,model,scenarios):
    """Whole unknown suffix, equal scenario weights, grouped first actions."""
    if len(scenarios)!=4:raise InputError('four unrenormalized scenarios required')
    offsets=candidate_offsets(snapshot);end=min(snapshot.now+8,snapshot.experiment_end)
    n=int(round((end-snapshot.now)/.1))
    if n<=0:return Decision('CLOSE','experiment_end',0.)
    low,high=score_envelope();cache={};counters=dict(solves=0,hits=0);rows=[];unknown=[]
    for sc in scenarios:
        if not isinstance(sc,ConditionalScenario):raise InputError('explicit unknown-support scenario required')
        if any(not math.isfinite(u.earliest_effect_time) for u in sc.unknowns):raise InputError('invalid unknown clock')
        unknown.extend(asdict(u) for u in sc.unknowns)
    for offset in offsets:
        lowers=[];uppers=[];prefix_counts=[]
        for sc in scenarios:
            cutoff=min((u.earliest_effect_time for u in sc.unknowns),default=math.inf)
            state=_ForecastState(snapshot,model);index=0;first=False;values=[]
            if offset==0 and snapshot.now<cutoff-1e-10:state.release(cache,counters);first=True
            for tick in range(1,n+1):
                now=round(snapshot.now+tick*.1,10)
                if now>=cutoff-1e-10:break
                try:
                    while index<len(sc.events) and sc.events[index].time<=now+1e-9:
                        event=sc.events[index]
                        if event.time<=snapshot.now:raise InputError('already observed forecast event')
                        state.now=event.time;state.event(event);index+=1
                except UnsupportedPrediction as exc:
                    # No state beyond the failing event is used, including all
                    # later version/replacement/debt and release effects.
                    unknown.append(dict(key=event.registration.key,earliest_effect_time=event.time,reason=str(exc)))
                    break
                state.now=now;state.expire();elapsed=now-state.open
                deadline=elapsed>=4-1e-9
                planned=not first and now>=snapshot.now+offset-1e-9 and len(state.pool)>=snapshot.config.minimum_clients
                tail=first and elapsed>=2-1e-9
                if deadline or planned or tail:state.release(cache,counters);first=True
                value=state.last.score(snapshot.config) if state.last else 1.
                if not low<=value<=high:raise InputError('score escaped proved numerical envelope')
                values.append(value)
            k=len(values);a=math.fsum(values)
            # Outward allowance for prefix summation, suffix arithmetic, four
            # scenario averaging, and legacy integral summation comparison.
            u=np.finfo(float).eps;gamma=(4*n+32)*u/(1-(4*n+32)*u)
            margin=gamma*max(1.,abs(low),abs(high))*4
            lowers.append((a+(n-k)*low)/n-margin)
            uppers.append((a+(n-k)*high)/n+margin);prefix_counts.append(k)
        rows.append(dict(offset=offset,L=math.nextafter(math.fsum(lowers)/4,-math.inf),
            U=math.nextafter(math.fsum(uppers)/4,math.inf),known_cells=prefix_counts))
    groups=[]
    for action in ('CLOSE','WAIT'):
        candidates=[r for r in rows if (r['offset']==0)==(action=='CLOSE')]
        if not candidates:continue
        upper=min(r['U'] for r in candidates)
        groups.append(dict(action=action,L=min(r['L'] for r in candidates),U=upper,
            witness_offset=min(r['offset'] for r in candidates if r['U']<=upper+1e-7)))
    fallback=fixed_fallback(snapshot,'UNKNOWN_FIXED_TIME_2')
    if len(groups)==1:
        chosen=groups[0];action=chosen['action'];reason='RULE_FORCED';offset=chosen['witness_offset'];proven=False
    else:
        winners=[g for g in groups if all(g['U']+1e-7<h['L'] for h in groups if h['action']!=g['action'])]
        if winners:
            chosen=winners[0];action=chosen['action'];offset=chosen['witness_offset'];reason='INTERVAL_PROVEN';proven=True
        else:action=fallback.action;offset=fallback.selected_offset;reason=fallback.reason;proven=False
    return Decision(action,reason,offset,p2_solves=counters['solves'],cache_hits=counters['hits'],
        scenario_digest=sha256_json([s.to_dict() for s in scenarios]),intervals=tuple(rows),
        action_intervals=tuple(groups),unknown_support=tuple(unknown),proven=proven)


def plan(snapshot: DecisionSnapshot, model: FrozenServiceModel, *, isolated_scenarios=None):
    validate_planning_inputs(snapshot,model)
    elapsed=snapshot.now-snapshot.window_open
    if elapsed>=snapshot.config.deadline-1e-9:return Decision('CLOSE','hard_deadline',0.)
    if snapshot.now<=snapshot.config.warmup+1e-9:
        return Decision('CLOSE' if elapsed>=1-1e-9 else 'WAIT','common_warmup',0. if elapsed>=1-1e-9 else None)
    # Compute the actual complete P2 preview and independent current distance,
    # not the old L2 function. Its result is diagnostic, not a future certificate.
    preview_release(snapshot)
    try:
        if isolated_scenarios is not None and not snapshot.isolated_test:
            raise InputError('hand-authored scenarios forbidden outside isolated test')
        scenarios=model.sample_scenarios(snapshot) if isolated_scenarios is None else isolated_scenarios
        result=evaluate_interval_plans(snapshot,model,scenarios)
        return replace(result,p2_solves=result.p2_solves+int(bool(snapshot.pool)))
    except UnsupportedPrediction as exc:
        return fixed_fallback(snapshot,'UNSUPPORTED_PREDICTION/fixed_time_2/'+str(exc))
