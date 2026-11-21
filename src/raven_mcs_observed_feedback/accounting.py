"""Disjoint category attribution on the externally measured root ledger."""
import json,time,os
from pathlib import Path
from .budget_client import RootClient,read_shared_json
class BudgetStop(RuntimeError):pass
CAPS=dict(setup=180.,initialization=120.,online=1300.,training=900.,events=700.,save=300.,repair=100.)
class CategoryAccountant:
    def __init__(self,out):
        self.out=Path(out);self.root=RootClient(Path(os.environ.get('OF_ROOT_BUDGET_PATH',self.out/'ROOT_BUDGET_LIVE.json')))
        launch=json.loads((self.out/'LAUNCH_COST.json').read_text());self.base=launch['used_categories'];self.bootstrap=launch['bootstrap_CPU']
        self.spent=dict.fromkeys(CAPS,0.);self.last_cost=0.;self.reserve=5.96875;self.records=[];self.maxima={};self.current_category=None
    def after(self,stamp):
        while True:
            v=read_shared_json(self.root.path)
            if not v['finished'] and v['wall_stamp']>=stamp+.01:return v
            time.sleep(.005)
    def remaining(self,category):return 3600-sum(self.base.values())-sum(self.spent.values())
    def operation(self,category,fn,ceiling=2.,online=False):
        if self.current_category is not None:raise RuntimeError('nested category attribution prohibited')
        begin=self.after(time.perf_counter());cpu=time.process_time();wall=time.perf_counter();error=None;value=None;self.current_category=category
        try:
            if not self.root.can_plan(0 if category=='save' else self.reserve,operation_root_ceiling=ceiling):raise BudgetStop('ROOT_HEADROOM_'+category)
            value=fn()
        except Exception as exc:error=exc
        done=time.perf_counter();end=self.after(done);local=time.process_time()-cpu
        # Every unclaimed gap since the last endpoint belongs to this next operation, once.
        attribution=end['command_used']-self.last_cost+(self.bootstrap if self.last_cost==0 else 0.)
        self.last_cost=end['command_used'];self.spent[category]+=attribution
        delta=end['command_used']-begin['command_used'];monitor=end['driver_CPU']-begin['driver_CPU']
        upper=max(delta+.02,local+monitor+.02);self.maxima[category]=max(self.maxima.get(category,0.),upper)
        record=dict(index=len(self.records),category=category,attributed_root_CPU=attribution,request_root_difference=delta,
            root_upper_CPU=upper,worker_local_CPU=local,monitor_CPU=monitor,wall=time.perf_counter()-wall,
            root_id=end['root_id'],root_begin_sequence=begin['sequence'],root_end_sequence=end['sequence'],error=repr(error) if error else None)
        self.records.append(record);self.current_category=None
        with (self.out/'COST_RECORDS.jsonl').open('a') as f:f.write(json.dumps(record)+'\n')
        (self.out/'CATEGORY_LIVE.json').write_text(json.dumps(dict(spent=self.spent,maxima=self.maxima,last_root_cost=self.last_cost,record_count=len(self.records)),indent=2))
        if online and upper>2.:raise BudgetStop('ONLINE_ROOT_REQUEST_EXCEEDS_2_CPU')
        if error:raise error
        return value
