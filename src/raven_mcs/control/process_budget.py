"""Process-tree CPU accounting, including terminated children on Windows."""
from __future__ import annotations
import os
import time


if os.name=='nt':
    import ctypes
    from ctypes import wintypes

    class _Accounting(ctypes.Structure):
        _fields_=[('TotalUserTime',ctypes.c_int64),('TotalKernelTime',ctypes.c_int64),
                  ('ThisPeriodTotalUserTime',ctypes.c_int64),('ThisPeriodTotalKernelTime',ctypes.c_int64),
                  ('TotalPageFaultCount',wintypes.DWORD),('TotalProcesses',wintypes.DWORD),
                  ('ActiveProcesses',wintypes.DWORD),('TotalTerminatedProcesses',wintypes.DWORD)]

    class _BasicLimits(ctypes.Structure):
        _fields_=[('PerProcessUserTimeLimit',ctypes.c_int64),('PerJobUserTimeLimit',ctypes.c_int64),
                  ('LimitFlags',wintypes.DWORD),('MinimumWorkingSetSize',ctypes.c_size_t),
                  ('MaximumWorkingSetSize',ctypes.c_size_t),('ActiveProcessLimit',wintypes.DWORD),
                  ('Affinity',ctypes.c_size_t),('PriorityClass',wintypes.DWORD),('SchedulingClass',wintypes.DWORD)]

    class _IO(ctypes.Structure):
        _fields_=[(x,ctypes.c_uint64) for x in ('ReadOperationCount','WriteOperationCount','OtherOperationCount',
                                               'ReadTransferCount','WriteTransferCount','OtherTransferCount')]

    class _ExtendedLimits(ctypes.Structure):
        _fields_=[('BasicLimitInformation',_BasicLimits),('IoInfo',_IO),('ProcessMemoryLimit',ctypes.c_size_t),
                  ('JobMemoryLimit',ctypes.c_size_t),('PeakProcessMemoryUsed',ctypes.c_size_t),('PeakJobMemoryUsed',ctypes.c_size_t)]

    kernel=ctypes.WinDLL('kernel32',use_last_error=True)
    kernel.CreateJobObjectW.argtypes=[ctypes.c_void_p,wintypes.LPCWSTR];kernel.CreateJobObjectW.restype=wintypes.HANDLE
    kernel.AssignProcessToJobObject.argtypes=[wintypes.HANDLE,wintypes.HANDLE];kernel.AssignProcessToJobObject.restype=wintypes.BOOL
    kernel.QueryInformationJobObject.argtypes=[wintypes.HANDLE,ctypes.c_int,ctypes.c_void_p,wintypes.DWORD,ctypes.c_void_p]
    kernel.QueryInformationJobObject.restype=wintypes.BOOL
    kernel.SetInformationJobObject.argtypes=[wintypes.HANDLE,ctypes.c_int,ctypes.c_void_p,wintypes.DWORD]
    kernel.SetInformationJobObject.restype=wintypes.BOOL
    kernel.TerminateJobObject.argtypes=[wintypes.HANDLE,wintypes.UINT];kernel.TerminateJobObject.restype=wintypes.BOOL
    kernel.CloseHandle.argtypes=[wintypes.HANDLE];kernel.CloseHandle.restype=wintypes.BOOL
    kernel.OpenProcess.argtypes=[wintypes.DWORD,wintypes.BOOL,wintypes.DWORD];kernel.OpenProcess.restype=wintypes.HANDLE


class ProcessTreeBudget:
    def __init__(self):
        self._final_cpu=0.
        if os.name=='nt':
            self.handle=kernel.CreateJobObjectW(None,None)
            if not self.handle:raise ctypes.WinError(ctypes.get_last_error())
            limits=_ExtendedLimits();limits.BasicLimitInformation.LimitFlags=0x2000 # kill on close
            if not kernel.SetInformationJobObject(self.handle,9,ctypes.byref(limits),ctypes.sizeof(limits)):
                raise ctypes.WinError(ctypes.get_last_error())
        else:
            self.pid=None

    def attach(self,pid):
        if os.name=='nt':
            proc=kernel.OpenProcess(0x0100|0x0001|0x0400,False,pid) # quota, terminate, query
            if not proc:raise ctypes.WinError(ctypes.get_last_error())
            try:
                if not kernel.AssignProcessToJobObject(self.handle,proc):
                    raise ctypes.WinError(ctypes.get_last_error())
            finally:kernel.CloseHandle(proc)
        else:self.pid=pid

    def cpu_seconds(self):
        if os.name=='nt':
            result=_Accounting()
            if not kernel.QueryInformationJobObject(self.handle,1,ctypes.byref(result),ctypes.sizeof(result),None):
                raise ctypes.WinError(ctypes.get_last_error())
            self._final_cpu=(result.TotalUserTime+result.TotalKernelTime)/1e7
        elif self.pid:
            try:
                with open(f'/proc/{self.pid}/stat') as f: fields=f.read().rsplit(')',1)[1].split()
                self._final_cpu=(float(fields[11])+float(fields[12]))/os.sysconf('SC_CLK_TCK')
            except FileNotFoundError:pass
        return self._final_cpu

    def terminate(self):
        if os.name=='nt':kernel.TerminateJobObject(self.handle,124)
        elif self.pid:
            import signal
            try:os.kill(self.pid,signal.SIGKILL)
            except ProcessLookupError:pass

    def close(self):
        if os.name=='nt' and self.handle:
            self.cpu_seconds();kernel.CloseHandle(self.handle);self.handle=None


def wait_accounted(process, budget, *, cpu_limit, parent_started, wall_started, pipe=None):
    """A small reserve avoids monitoring/termination latency overshooting CPU.

    A stalled child is a facility error, not a prediction fallback. The 60s
    watchdog never gets reported as a successful policy decision.
    """
    reserve=min(.08,cpu_limit*.05)
    while process.is_alive():
        total=budget.cpu_seconds()+time.process_time()-parent_started
        if total>=cpu_limit-reserve:
            budget.terminate();process.join()
            return 'cpu_timeout'
        if time.perf_counter()-wall_started>60:
            budget.terminate();process.join()
            return 'facility_stall'
        if pipe is not None and pipe.poll(.01):return 'message'
        if pipe is None:time.sleep(.01)
    return 'exited'
