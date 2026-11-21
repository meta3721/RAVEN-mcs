"""Bounded retry of Windows sharing races; unchanged root admission rules."""
import time,json,os
from raven_mcs_execution.budget import RootBudgetReader,RootBudgetPublisher
class AtomicPublisher(RootBudgetPublisher):
    """Retry a transient rename, preserving its actual measurement timestamp."""
    def publish(self,tree_cpu,driver_cpu,*,force=False,finished=False):
        try:return super().publish(tree_cpu,driver_cpu,force=force,finished=finished)
        except PermissionError:
            temp=self.path.with_suffix('.pending')
            # The original publisher fully wrote this payload before replace.
            # Keep its as-of time/cost, so the reader's age deduction covers
            # any retry delay. Never refresh a stale CPU sample's timestamp.
            payload=json.loads(temp.read_text(encoding='utf-8'))
            for attempt in range(10):
                try:
                    os.replace(temp,self.path);self.last_wall=payload['wall_stamp'];return
                except PermissionError:
                    if attempt==9:raise
                    time.sleep(.005)
def read_shared_json(path):
    if os.name!='nt':return json.loads(path.read_text())
    import ctypes,msvcrt
    from ctypes import wintypes
    create=ctypes.WinDLL('kernel32',use_last_error=True).CreateFileW
    create.argtypes=[wintypes.LPCWSTR,wintypes.DWORD,wintypes.DWORD,ctypes.c_void_p,wintypes.DWORD,wintypes.DWORD,wintypes.HANDLE]
    create.restype=wintypes.HANDLE
    # Sharing DELETE permits the existing atomic publisher's rename while the
    # reader owns an immutable handle to the previously published file.
    handle=create(str(path),0x80000000,1|2|4,None,3,0x80,None)
    if handle==ctypes.c_void_p(-1).value:raise ctypes.WinError(ctypes.get_last_error())
    fd=msvcrt.open_osfhandle(handle,os.O_RDONLY)
    with os.fdopen(fd,'r',encoding='utf-8') as stream:return json.load(stream)
class RootClient(RootBudgetReader):
    def read(self):
        for attempt in range(10):
            try:
                v=read_shared_json(self.path)
                if v['schema']!='root_disjoint_CPU_v1' or v['finished']:raise RuntimeError('root budget unavailable / finished')
                if self.root_id is None:self.root_id=v['root_id']
                if self.root_id!=v['root_id']:raise RuntimeError('root budget namespace changed')
                age=max(0.,time.perf_counter()-v['wall_stamp'])
                if age>1:raise RuntimeError('root budget stale; no new operation')
                v['effective_remaining']=v['remaining']-v['maximum_CPU_rate']*age-.05
                return v
            except PermissionError:
                if attempt==9:raise
                time.sleep(.005)
