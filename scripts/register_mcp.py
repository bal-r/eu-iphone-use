#!/usr/bin/env python3
"""Register this private derivative without editing another plugin's settings."""
import argparse
import hashlib
import os
import tempfile
import json
from pathlib import Path
import subprocess
import sys


def atomic_write(path,data):
    fd,temp=tempfile.mkstemp(prefix=".install-",dir=path.parent)
    try:
        os.fchmod(fd,0o600)
        with os.fdopen(fd,"wb") as output:output.write(data)
        os.replace(temp,path)
    finally:
        if os.path.exists(temp):os.unlink(temp)


def main(argv=None):
    parser=argparse.ArgumentParser()
    parser.add_argument("--native",action="store_true",help="Use the plugin-bundled MCP on a host verified to support it.")
    parser.add_argument("--launcher-dir",type=Path,default=Path.home()/".local/share/balta-tech-iphone-use/integration")
    args=parser.parse_args(argv)
    installation = json.load(sys.stdin)
    if installation.get('pluginId') != 'iphone-use@balta-tech-local':
        raise SystemExit('Expected the Balta Tech plugin installation result.')
    root = Path(installation['installedPath']).resolve(strict=True)
    server = root / 'server/iphone_use.py'
    if not server.is_file() or server.is_symlink():
        raise SystemExit('Installed Balta Tech MCP entrypoint is missing or symlinked.')
    manifest=json.loads((root/'plugin.json').read_text())
    directory=args.launcher_dir.expanduser().resolve()
    directory.mkdir(parents=True,exist_ok=True,mode=0o700)
    directory.chmod(0o700)
    launcher=directory/'mcp_launcher.py'
    atomic_write(launcher,(root/'server/mcp_launcher.py').read_bytes())
    record={'installed_path':str(root),'version':manifest['version'],'server_sha256':hashlib.sha256(server.read_bytes()).hexdigest()}
    atomic_write(directory/'plugin-current.json',json.dumps(record).encode())
    if args.native:
        existing=subprocess.run(['codex','mcp','get','balta_iphone_use','--json'],capture_output=True,text=True)
        if existing.returncode==0:
            config=json.loads(existing.stdout)
            old_args=config.get('transport',config).get('args',[])
            owned=any(isinstance(value,str) and ('/balta-tech-local/iphone-use/' in value or value==str(launcher)) for value in old_args)
            if not owned:raise SystemExit('Native mode would conflict with an unrecognised balta_iphone_use registration. Preserve it and review the registration manually.')
            subprocess.run(['codex','mcp','remove','balta_iphone_use'],check=True)
    else:
        subprocess.run(['codex','mcp','add','balta_iphone_use','--','python3',str(launcher)],check=True)
    print(json.dumps({'pluginId': installation['pluginId'], 'installedPath': str(root)}, ensure_ascii=False))


if __name__ == '__main__':
    main()
