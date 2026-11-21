"""External observation/accounting only; no changes to frozen scientific packages."""
import json,time
from raven_mcs_observed_feedback.accounting import CategoryAccountant
class RollingAccount(CategoryAccountant):
    def operation(self,category,fn,ceiling=2.,online=False):
        before=len(self.records)
        try:return super().operation(category,fn,ceiling,online)
        finally:
            if len(self.records)>before:
                self.records[-1]['operation_kind']=getattr(fn,'__name__','call')
    def rolling_summary(self,r,p,tick,sizes,previous=None):
        previous=previous or dict(time=1.07,registrations=46,SGD=32,notices=16,grid=10,spent=dict.fromkeys(self.spent,0.),driver_CPU=0.,cost_record_count=0)
        root=self.root.read();notices=sum(x['event']!='register' for x in p.publication_bridge);registrations=len(r.attempts)
        current=dict(time=r.now,registrations=registrations,R1=sum(x.R for x in r.attempts.values()),SGD=r.backend.local_optimizer_steps,notices=notices,grid=tick,
            spent=self.spent.copy(),driver_CPU=root['driver_CPU'],cost_record_count=len(self.records),private_queue=len(p.pending),P=len(r.pool),F=len(r.in_flight),checkpoint_bytes=sizes)
        delta={k:current[k]-previous[k] for k in ('registrations','SGD','notices','grid','driver_CPU')};delta['spent']={k:current['spent'][k]-previous['spent'][k] for k in self.spent}
        records=self.records[previous['cost_record_count']:];kinds={}
        for row in records:kinds[row['operation_kind']]=kinds.get(row['operation_kind'],0)+1
        delta['operation_counts']=kinds
        remaining_regs=max(0,(100-p.next_clock)*len(p.inputs.clients)-p.next_client);remaining_grid=1000-tick
        n=max(1,current['registrations']-46);ng=max(1,tick-10);nd=max(1,delta['registrations']);dg=max(1,delta['grid'])
        cum_unit=dict(training=current['spent']['training']/n,events=current['spent']['events']/n,online=current['spent']['online']/ng)
        recent_unit=dict(training=delta['spent']['training']/nd,events=delta['spent']['events']/nd,online=delta['spent']['online']/dg)
        # Planned costs are warnings. Do not add monitor_CPU to already inclusive root categories.
        plan=sum(2*max(cum_unit[k],recent_unit[k])*remaining_regs for k in ('training','events'))+2*max(cum_unit['online'],recent_unit['online'])*remaining_grid
        plan+=max(5.96875,2*self.maxima.get('save',0.))*(1+remaining_grid//50)
        return dict(current=current,segment=delta,cumulative_unit_CPU=cum_unit,recent_unit_CPU=recent_unit,
            proposed_remaining_CPU=plan,remaining_effective_CPU=root['effective_remaining'],warning=plan>root['effective_remaining'],
            forecast_role='warning_only_not_admission_or_statistical_guarantee',one_off_resume_CPU=self.spent['initialization'],
            monitor_CPU_is_in_root=True,actual_P2_solves=r.cache.solves,cache_hits=r.cache.hits,save_upper_CPU=self.maxima.get('save'),reserve=self.reserve,
            unknown='later conic/queue/history growth not guaranteed by measured units; cold costs retained in cumulative records')
