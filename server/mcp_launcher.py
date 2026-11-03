"""Stable local MCP launcher. The installer atomically updates its private target."""
import hashlib
import json
import os
from pathlib import Path
import runpy
import sys


def launch(marker=None):
    marker=Path(marker or Path(__file__).with_name("plugin-current.json"))
    record=json.loads(marker.read_text())
    root=Path(record["installed_path"]).resolve(strict=True)
    server=root/"server/iphone_use.py"
    if server.is_symlink() or not server.is_file():raise SystemExit("Installed MCP entrypoint is unavailable; reinstall Balta Tech iPhone Use.")
    if hashlib.sha256(server.read_bytes()).hexdigest()!=record["server_sha256"]:
        raise SystemExit("Installed MCP changed after registration; rerun the reviewed installer.")
    manifest=json.loads((root/"plugin.json").read_text())
    if manifest["version"]!=record["version"]:raise SystemExit("MCP installation version mismatch.")
    os.environ["BALTA_IPHONE_LAUNCHER_VERSION"]=record["version"]
    os.environ["BALTA_IPHONE_INSTALL_MARKER"]=str(marker)
    sys.path.insert(0,str(server.parent))
    sys.argv[0]=str(server)
    runpy.run_path(str(server),run_name="__main__")

if __name__=="__main__":launch()
