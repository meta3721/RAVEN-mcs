"""D1 equivalent topology only: finite CPU work, no data/controller/SGD."""
import argparse
import ctypes
import json
import multiprocessing as mp
import os
import time
from pathlib import Path

def identity(role):
    b=ctypes.create_unicode_buffer(32768)
    ctypes.windll.kernel32.GetModuleFileNameW(None,b,len(b))
    return dict(role=role,pid=os.getpid(),ppid=os.getppid(),actual_image=b.value)

def burn(seconds):
    start=time.process_time()
    while time.process_time()-start<seconds:
        sum(i*i for i in range(2000))

def worker(pipe):
    pipe.send(identity('planning_worker'))
    if pipe.recv()!='GO':return
    burn(.4);pipe.send(dict(cpu=time.process_time(),role='child_before_exit'))
    pipe.close()

def infinite_worker(pipe):
    pipe.send(identity('planning_worker'))
    if pipe.recv()!='GO':return
    burn(300)

if __name__=='__main__':
    p=argparse.ArgumentParser();p.add_argument('--mode',choices=['normal','timeout','planner_timeout','legacy'],required=True)
    a=p.parse_args()
    print(json.dumps(identity('actual_parent')),flush=True)
    if a.mode=='legacy':
        # Remains alive long enough for intentionally delayed launcher attach.
        burn(1.0);print(json.dumps(dict(self_CPU=time.process_time())),flush=True)
    else:
        from raven_mcs.control.process_budget import ProcessTreeBudget
        inner=ProcessTreeBudget();inner.attach(os.getpid())
        ctx=mp.get_context('spawn');parent,child=ctx.Pipe()
        process=ctx.Process(target=worker if a.mode=='normal' else infinite_worker,args=(child,))
        parent_started=time.process_time();wall_started=time.perf_counter()
        process.start();child.close()
        msg=parent.recv();print(json.dumps(msg),flush=True)
        nested=ProcessTreeBudget();nested.attach(process.pid);parent.send('GO')
        if a.mode=='normal':
            burn(.2);print(json.dumps(parent.recv()),flush=True);process.join()
            print(json.dumps(dict(inner_inclusive_CPU=inner.cpu_seconds(),child_included_CPU=nested.cpu_seconds(),parent_self_CPU=time.process_time())),flush=True)
            nested.close()
            # Match acquisition: inner self Job left alive until process exit.
        elif a.mode=='planner_timeout':
            from raven_mcs.control.process_budget import wait_accounted
            status=wait_accounted(process,nested,cpu_limit=2,parent_started=parent_started,wall_started=wall_started)
            process.join()
            total=nested.cpu_seconds()+time.process_time()-parent_started
            print(json.dumps(dict(status=status,terminated_child=process.pid,child_exit=process.exitcode,
                child_included_CPU=nested.cpu_seconds(),parent_increment_CPU=time.process_time()-parent_started,
                combined_planning_CPU=total,inner_inclusive_CPU=inner.cpu_seconds())),flush=True)
            assert status=='cpu_timeout' and process.exitcode==124 and 0<total<=2
            nested.close()
        else:
            process.join()
