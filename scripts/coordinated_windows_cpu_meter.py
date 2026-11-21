"""Suspended-start Windows Job meter; independent retained-PID CPU audit.

Infrastructure only. Does not import a controller, model or experiment.
No breakaway: launcher, real interpreter, nested jobs and exited workers belong
to the root job before any user code executes. Keep handles until final read.
"""
from __future__ import annotations
import ctypes as C
from ctypes import wintypes as W
import json
import os
from pathlib import Path
import subprocess
import time
import _winapi

K=C.WinDLL('kernel32',use_last_error=True)
def api(name,args,result):
    f=getattr(K,name);f.argtypes=args;f.restype=result;return f
HANDLE=W.HANDLE; DWORD=W.DWORD; SIZE=C.c_size_t
createjob=api('CreateJobObjectW',[C.c_void_p,W.LPCWSTR],HANDLE)
setjob=api('SetInformationJobObject',[HANDLE,C.c_int,C.c_void_p,DWORD],W.BOOL)
queryjob=api('QueryInformationJobObject',[HANDLE,C.c_int,C.c_void_p,DWORD,C.c_void_p],W.BOOL)
assign=api('AssignProcessToJobObject',[HANDLE,HANDLE],W.BOOL)
close=api('CloseHandle',[HANDLE],W.BOOL)
terminate=api('TerminateJobObject',[HANDLE,W.UINT],W.BOOL)
terminateprocess=api('TerminateProcess',[HANDLE,W.UINT],W.BOOL)
resume=api('ResumeThread',[HANDLE],DWORD)
openprocess=api('OpenProcess',[DWORD,W.BOOL,DWORD],HANDLE)
times=api('GetProcessTimes',[HANDLE,C.POINTER(W.FILETIME),C.POINTER(W.FILETIME),C.POINTER(W.FILETIME),C.POINTER(W.FILETIME)],W.BOOL)
wait=api('WaitForSingleObject',[HANDLE,DWORD],DWORD)
exitcode=api('GetExitCodeProcess',[HANDLE,C.POINTER(DWORD)],W.BOOL)
injob=api('IsProcessInJob',[HANDLE,HANDLE,C.POINTER(W.BOOL)],W.BOOL)
image=api('QueryFullProcessImageNameW',[HANDLE,DWORD,W.LPWSTR,C.POINTER(DWORD)],W.BOOL)
affinity=api('GetProcessAffinityMask',[HANDLE,C.POINTER(SIZE),C.POINTER(SIZE)],W.BOOL)
current=api('GetCurrentProcess',[],HANDLE)
port=api('CreateIoCompletionPort',[HANDLE,HANDLE,SIZE,DWORD],HANDLE)
completion=api('GetQueuedCompletionStatus',[HANDLE,C.POINTER(DWORD),C.POINTER(SIZE),C.POINTER(C.c_void_p),DWORD],W.BOOL)

class Accounting(C.Structure):
    _fields_=[('user',C.c_int64),('kernel',C.c_int64),('period_user',C.c_int64),('period_kernel',C.c_int64),('faults',DWORD),('total',DWORD),('active',DWORD),('terminated',DWORD)]
class Basic(C.Structure):
    _fields_=[('process_time',C.c_int64),('job_time',C.c_int64),('flags',DWORD),('min_ws',SIZE),('max_ws',SIZE),('active',DWORD),('affinity',SIZE),('priority',DWORD),('scheduling',DWORD)]
class IO(C.Structure):
    _fields_=[(n,C.c_uint64) for n in ('read','write','other','read_bytes','write_bytes','other_bytes')]
class Limits(C.Structure):
    _fields_=[('basic',Basic),('io',IO),('process_mem',SIZE),('job_mem',SIZE),('peak_process',SIZE),('peak_job',SIZE)]
class PortInfo(C.Structure):
    _fields_=[('key',C.c_void_p),('port',HANDLE)]

def check(ok):
    if not ok:raise C.WinError(C.get_last_error())
    return ok
def ft(v):return ((v.dwHighDateTime<<32)|v.dwLowDateTime)/1e7
def process_times(handle):
    a,b,c,d=(W.FILETIME() for _ in range(4));check(times(handle,C.byref(a),C.byref(b),C.byref(c),C.byref(d)))
    return dict(created_filetime=ft(a),exited_filetime=ft(b),kernel_cpu=ft(c),user_cpu=ft(d),cpu_seconds=ft(c)+ft(d))
def proc_image(handle):
    b=C.create_unicode_buffer(32768);n=DWORD(len(b));check(image(handle,0,b,C.byref(n)));return b.value

def run_coordinated_metered(command, log, *, cpu_limit, wall_limit, cwd, legacy_attach_delay=None, budget_feedback=None):
    """Return disjoint job+monitor costs; PID sum is audit only, never added.

    legacy_attach_delay is reserved for the fixed no-training D1 reproducer.
    Normal entry always starts suspended, assigns, then resumes. A failed PID
    audit blocks the next phase even if the Job retained aggregate CPU.
    """
    log=Path(log);start=time.perf_counter();cpu0=time.process_time()
    from raven_mcs_execution.budget import RootBudgetPublisher
    publisher=RootBudgetPublisher(budget_feedback,cpu_limit) if budget_feedback else None
    job=check(createjob(None,None));cp=check(port(HANDLE(-1),None,0,1))
    info=PortInfo(C.c_void_p(1),cp);check(setjob(job,7,C.byref(info),C.sizeof(info)))
    lim=Limits();lim.basic.flags=0x2000|0x10 # kill-on-close + one-CPU affinity
    allowed=SIZE();system=SIZE();check(affinity(current(),C.byref(allowed),C.byref(system)))
    lim.basic.affinity=allowed.value & -allowed.value
    # Kernel user-time backstop plus total user+kernel polling below.
    lim.basic.flags |= 0x4
    lim.basic.job_time=int(cpu_limit*1e7)
    check(setjob(job,9,C.byref(lim),C.sizeof(lim)))
    env=dict(os.environ,PYTHONPATH=str(Path(cwd)/'src'),PYTHONDONTWRITEBYTECODE='1',
             OMP_NUM_THREADS='1',MKL_NUM_THREADS='1',OPENBLAS_NUM_THREADS='1',NUMEXPR_NUM_THREADS='1',
             PYTHONHASHSEED='26004',CUDA_VISIBLE_DEVICES='')
    handles={};records={};notifications=[];errors=[];root_handle=None;thread_handle=None;reason=None
    def retain(pid,handle=None):
        if pid in handles:return
        handle=handle or openprocess(0x1000|0x100000,False,pid)
        if not handle:
            errors.append(dict(pid=pid,error='process_not_openable_before_exit',code=C.get_last_error()));return
        member=W.BOOL();check(injob(handle,job,C.byref(member)))
        handles[pid]=handle
        records[pid]=dict(pid=pid,joined_observed_wall=time.perf_counter()-start,
            root_job_member=bool(member.value),image=proc_image(handle),initial_cpu=process_times(handle)['cpu_seconds'])
    def drain():
        while True:
            msg=DWORD();key=SIZE();pid=C.c_void_p()
            ok=completion(cp,C.byref(msg),C.byref(key),C.byref(pid),0)
            if not ok:
                if C.get_last_error()==258:break
                check(ok)
            n=int(pid.value or 0)
            notifications.append(dict(message=msg.value,pid=n,wall=time.perf_counter()-start))
            if msg.value==6:retain(n)
    def accounting():
        a=Accounting();check(queryjob(job,1,C.byref(a),C.sizeof(a),None));return a
    try:
        with log.open('xb') as stream, open(os.devnull,'rb') as null:
            import msvcrt
            oh=msvcrt.get_osfhandle(stream.fileno());ih=msvcrt.get_osfhandle(null.fileno())
            os.set_handle_inheritable(oh,True);os.set_handle_inheritable(ih,True)
            si=subprocess.STARTUPINFO();si.dwFlags=subprocess.STARTF_USESTDHANDLES
            si.hStdInput=ih;si.hStdOutput=oh;si.hStdError=oh
            flags=0x08000000 | (0x4 if legacy_attach_delay is None else 0)
            root_handle,thread_handle,pid,tid=_winapi.CreateProcess(None,subprocess.list2cmdline([str(x) for x in command]),None,None,True,flags,env,str(cwd),si)
            if legacy_attach_delay is not None:time.sleep(legacy_attach_delay)
            check(assign(job,root_handle));retain(pid,root_handle)
            (log.with_suffix('.process.json')).write_text(json.dumps(dict(root_pid=pid,root_image=records[pid]['image'],command=[str(x) for x in command],suspended_start=legacy_attach_delay is None,assigned_before_execution=legacy_attach_delay is None),indent=2))
            if legacy_attach_delay is None:
                if resume(thread_handle)==0xffffffff:raise C.WinError(C.get_last_error())
            close(thread_handle);thread_handle=None
            while True:
                drain();a=accounting();elapsed=time.perf_counter()-start
                total=(a.user+a.kernel)/1e7+time.process_time()-cpu0
                if publisher:publisher.publish((a.user+a.kernel)/1e7,time.process_time()-cpu0)
                if not a.active:break
                if reason is None and (total>=cpu_limit-.15 or elapsed>wall_limit):
                    reason='cpu' if total>=cpu_limit-.15 else 'wall'
                    check(terminate(job,124))
                if reason is not None and elapsed>wall_limit+5:raise RuntimeError('termination did not complete')
                time.sleep(.005)
            check(wait(root_handle,5000)==0)
            drain();a=accounting()
            code=DWORD();check(exitcode(root_handle,C.byref(code)))
            for p,h in handles.items():
                check(wait(h,5000)==0);records[p].update(process_times(h))
                ec=DWORD();check(exitcode(h,C.byref(ec)));records[p]['exit_code']=ec.value
                records[p]['exit_observed_wall']=time.perf_counter()-start
            total=(a.user+a.kernel)/1e7;pid_sum=sum(r['cpu_seconds'] for r in records.values())
            tolerance=.03125*len(records)+.01
            valid=(a.total==len(records) and all(r['root_job_member'] for r in records.values()) and not errors and abs(total-pid_sum)<=tolerance)
            result=dict(command=[str(x) for x in command],returncode=code.value,process_tree_cpu_seconds=total,
                monitor_cpu_seconds=time.process_time()-cpu0,wall_seconds=time.perf_counter()-start,limit_reason=reason,
                log=str(log),pids=list(records.values()),notifications=notifications,errors=errors,
                job_total_processes=a.total,job_active_processes=a.active,independent_pid_CPU_sum=pid_sum,
                difference_seconds=total-pid_sum,predeclared_tolerance_seconds=tolerance,
                audit_passed=valid,CPU_limit=cpu_limit,single_CPU_affinity=lim.basic.affinity,
                mutually_exclusive_costs=['process_tree_cpu_seconds','monitor_cpu_seconds'],
                included_not_additive=['independent_pid_CPU_sum','individual_PID_CPU','inner_job_CPU'],
                cpu_scope='creation through process exit; root created suspended, descendants inherit before execution' if legacy_attach_delay is None else 'legacy delayed assignment, diagnostic only')
            log.with_suffix('.meter.json').write_text(json.dumps(result,indent=2),encoding='utf-8')
            if publisher:publisher.publish(total,time.process_time()-cpu0,force=True,finished=True)
            return result
    finally:
        terminate(job,124)
        # If assignment/setup itself failed, the owned suspended root might
        # not belong to the Job yet. Never leave that process orphaned.
        if root_handle and wait(root_handle,0)!=0:
            terminateprocess(root_handle,124);wait(root_handle,5000)
        if thread_handle:close(thread_handle)
        for h in handles.values():close(h)
        if root_handle and root_handle not in handles.values():close(root_handle)
        close(job);close(cp)
