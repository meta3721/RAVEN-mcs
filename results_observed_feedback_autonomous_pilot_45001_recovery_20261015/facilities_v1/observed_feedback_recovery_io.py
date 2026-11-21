"""Atomic validated JSON publication; measured timestamps are never refreshed."""
import json,os,time,uuid,hashlib
from pathlib import Path
def durable_json(path,value,*,previous=False):
 path=Path(path);path.parent.mkdir(parents=True,exist_ok=True)
 data=json.dumps(value,allow_nan=False,ensure_ascii=False).encode('utf-8')
 temp=path.with_name(path.name+'.'+uuid.uuid4().hex+'.pending')
 with temp.open('xb') as f:f.write(data);f.flush();os.fsync(f.fileno())
 assert json.loads(temp.read_bytes())==json.loads(data)
 if previous and path.exists():
  try:old=json.loads(path.read_bytes())
  except (ValueError,UnicodeDecodeError):raise RuntimeError('existing JSON invalid; preserve evidence and stop')
  durable_json(path.with_name(path.name+'.previous'),old)
 for attempt in range(90):
  try:os.replace(temp,path);return
  except PermissionError:
   if attempt==89:raise
   time.sleep(.01)
def sync_existing(path):
 with Path(path).open('r+b') as f:f.flush();os.fsync(f.fileno())
def file_hash(path):
 h=hashlib.sha256()
 with Path(path).open('rb') as f:
  for block in iter(lambda:f.read(1048576),b''):h.update(block)
 return h.hexdigest()
