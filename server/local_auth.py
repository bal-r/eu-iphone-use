"""Private capability for the local USB proxy; never a remote-service credential."""
import os
from pathlib import Path
import re
import secrets
import stat
import fcntl


def connection_token(state_dir):
    directory = Path(state_dir)
    directory.mkdir(parents=True, exist_ok=True, mode=0o700)
    path = directory / "connection-token"
    fd = os.open(path, os.O_RDWR | os.O_CREAT | getattr(os, "O_NOFOLLOW", 0), 0o600)
    try:
        fcntl.flock(fd, fcntl.LOCK_EX)
        info = os.fstat(fd)
        if not stat.S_ISREG(info.st_mode) or info.st_nlink != 1:
            raise ValueError("The local connection token must be a private regular file.")
        os.fchmod(fd, 0o600)
        value = os.read(fd, 256).decode("ascii").strip()
        if not value:
            value = secrets.token_hex(32)
            os.write(fd, (value + "\n").encode())
            os.fsync(fd)
        if not re.fullmatch(r"[0-9a-f]{64}", value):
            raise ValueError("Invalid local connection token; stop the service before replacing it.")
        return value
    finally:
        os.close(fd)
