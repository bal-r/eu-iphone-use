"""Private per-device ownership across MCP conversations; no phone operations."""
import contextlib
import fcntl
import hashlib
import json
import os
from pathlib import Path
import re
import tempfile
import threading
import time
import uuid
from wda_client import WDAError


def device_key(state_dir):
    try:udid=json.loads((Path(state_dir)/'config.json').read_text()).get('udid')
    except (OSError,ValueError,AttributeError):return None
    return hashlib.sha256(udid.encode()).hexdigest()[:32] if isinstance(udid,str) and re.fullmatch(r'[A-Za-z0-9-]{8,64}',udid) else None


class DeviceLease:
    def __init__(self,key,idle_seconds=60):
        base=Path(os.environ.get('IPHONE_USE_LEASE_ROOT',str(Path.home()/'.local/share/balta-tech-iphone-use/leases')))
        self.directory=base/key;self.directory.mkdir(parents=True,exist_ok=True,mode=0o700)
        self.directory.chmod(0o700)
        self.path=self.directory/'owner.json';self.owner=uuid.uuid4().hex
        self.idle_seconds=idle_seconds;self._fd=None;self._lock=threading.RLock()
        self._active=0;self._last=0;self._release_pending=False;self._needs_observation=False
        self._stop=threading.Event()
        self._thread=threading.Thread(target=self._watch,name='phone-lease-expiry',daemon=True);self._thread.start()

    def _read(self):
        try:return json.loads(self.path.read_text())
        except (OSError,ValueError):return {}

    def _write(self,value):
        fd,name=tempfile.mkstemp(prefix='.owner-',dir=self.directory)
        try:
            os.fchmod(fd,0o600)
            with os.fdopen(fd,'w') as stream:json.dump(value,stream)
            os.replace(name,self.path)
        finally:
            if os.path.exists(name):os.unlink(name)

    def status(self):
        record=self._read();holder=record.get('holder')
        if isinstance(holder,dict) and self._fd is None:
            probe=os.open(self.directory/'owner.lock',os.O_CREAT|os.O_RDWR|getattr(os,'O_CLOEXEC',0),0o600)
            try:
                try:fcntl.flock(probe,fcntl.LOCK_EX|fcntl.LOCK_NB)
                except BlockingIOError:pass
                else:holder=None;fcntl.flock(probe,fcntl.LOCK_UN)
            finally:os.close(probe)
        if isinstance(holder,dict):
            holder={k:holder[k] for k in ('label','pid','expires_at') if k in holder}
            # Metadata is only a hint; flock is the authority on acquisition.
            if holder.get('expires_at',0)<time.time() and record.get('active') is not True:holder=None
        return {'held_by_this_chat':self._fd is not None,'holder':holder,'fresh_observation_required':self._needs_observation}

    def claim(self,label=None):
        with self._lock:
            if self._fd is None:
                fd=os.open(self.directory/'owner.lock',os.O_CREAT|os.O_RDWR|getattr(os,'O_CLOEXEC',0),0o600)
                try:fcntl.flock(fd,fcntl.LOCK_EX|fcntl.LOCK_NB)
                except BlockingIOError:
                    os.close(fd)
                    raise WDAError('device_held','Another conversation controls this iPhone. Wait for release; no phone action was sent.',details={'holder':self.status()['holder'],'action_executed':False,'replay_action':False})
                previous=self._read().get('last_owner')
                self._needs_observation=previous not in (None,self.owner)
                self._fd=fd
            self._last=time.monotonic()
            record=self._read()
            old=record.get('holder') or {}
            text=label if isinstance(label,str) and label.strip() else old.get('label','Phone task')
            self._write({'last_owner':self.owner,'holder':{'label':text[:60],'pid':os.getpid(),'expires_at':time.time()+self.idle_seconds},'active':self._active>0})
            return self.status()

    @contextlib.contextmanager
    def hold(self,mutation=False):
        with self._lock:
            self.claim()
            if mutation and self._needs_observation:
                raise WDAError('fresh_observation_required','Another conversation used the phone. Observe fresh state before acting.',details={'action_executed':False,'replay_action':False})
            self._active+=1;self.claim()
        try:yield
        finally:
            with self._lock:
                self._active-=1;self._last=time.monotonic()
                if self._release_pending:self.release()
                elif self._fd is not None:self.claim()

    def observed(self):self._needs_observation=False

    def release(self):
        with self._lock:
            if self._active:
                self._release_pending=True;return False
            self._release_pending=False
            if self._fd is None:return False
            self._write({'last_owner':self.owner,'holder':None,'active':False})
            fcntl.flock(self._fd,fcntl.LOCK_UN);os.close(self._fd);self._fd=None
            return True

    def _watch(self):
        while not self._stop.wait(min(1,self.idle_seconds/2)):
            with self._lock:
                if self._fd is not None and not self._active and time.monotonic()-self._last>=self.idle_seconds:self.release()

    def close(self):
        self.release();self._stop.set()
        if threading.current_thread() is not self._thread:self._thread.join(timeout=1)
