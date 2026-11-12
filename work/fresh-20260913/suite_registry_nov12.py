"""Observe exact owned processes;no shutdown or process-termination operations exist here."""
from pathlib import Path
from datetime import datetime,timezone
import argparse,ctypes,ctypes.wintypes,json,os
w=Path(__file__).resolve().parent;path=w/'suite-registry-nov12.json'
ap=argparse.ArgumentParser();ap.add_argument('action',choices=['register','status']);ap.add_argument('--pid',type=int);ap.add_argument('--label');ap.add_argument('--proof');a=ap.parse_args()
k=ctypes.WinDLL('kernel32',use_last_error=True);k.OpenProcess.argtypes=[ctypes.wintypes.DWORD,ctypes.wintypes.BOOL,ctypes.wintypes.DWORD];k.OpenProcess.restype=ctypes.wintypes.HANDLE;k.CloseHandle.argtypes=[ctypes.wintypes.HANDLE];k.GetProcessTimes.argtypes=[ctypes.wintypes.HANDLE]+[ctypes.POINTER(ctypes.wintypes.FILETIME)]*4;k.GetExitCodeProcess.argtypes=[ctypes.wintypes.HANDLE,ctypes.POINTER(ctypes.wintypes.DWORD)]
def identity(pid):
 h=k.OpenProcess(0x1000,False,pid)
 if not h:return None
 try:
  times=[ctypes.wintypes.FILETIME()for _ in range(4)];assert k.GetProcessTimes(h,*map(ctypes.byref,times));code=ctypes.wintypes.DWORD();assert k.GetExitCodeProcess(h,ctypes.byref(code));return dict(birth=times[0].dwHighDateTime<<32|times[0].dwLowDateTime,active=code.value==259)
 finally:k.CloseHandle(h)
j=json.loads(path.read_text())if path.exists()else dict(shutdown_authorized=False,suites_must_exit_naturally=True,jobs=[])
assert not j['shutdown_authorized']
if a.action=='register':
 live=identity(a.pid);assert live and live['active']and a.label
 assert not any(x['pid']==a.pid and x['birth']==live['birth']for x in j['jobs'])
 j['jobs'].append(dict(pid=a.pid,birth=live['birth'],label=a.label,proof=a.proof));temp=path.with_suffix('.tmp');temp.write_text(json.dumps(j,indent=2)+'\n');os.replace(temp,path);print('Registered',a.label,a.pid)
else:
 running=[];completed=[]
 for x in j['jobs']:
  live=identity(x['pid']);(running if live and live['active']and live['birth']==x['birth']else completed).append(x['label'])
 status=dict(status='OBSERVING_SUITES_WITHOUT_SHUTDOWN',observed_at=datetime.now(timezone.utc).isoformat(),shutdown_authorized=False,running=running,completed=completed);(w/'suite-registry-nov12-status.json').write_text(json.dumps(status,indent=2)+'\n');print(json.dumps(status))
