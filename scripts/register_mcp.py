#!/usr/bin/env python3
"""Register this private derivative without editing another plugin's settings."""
import json
from pathlib import Path
import subprocess
import sys


def main():
    installation = json.load(sys.stdin)
    if installation.get('pluginId') != 'iphone-use@balta-tech-local':
        raise SystemExit('Expected the Balta Tech plugin installation result.')
    root = Path(installation['installedPath']).resolve(strict=True)
    server = root / 'server/iphone_use.py'
    if not server.is_file() or server.is_symlink():
        raise SystemExit('Installed Balta Tech MCP entrypoint is missing or symlinked.')
    subprocess.run(['codex', 'mcp', 'add', 'balta_iphone_use', '--', 'python3', str(server)], check=True)
    print(json.dumps({'pluginId': installation['pluginId'], 'installedPath': str(root)}, ensure_ascii=False))


if __name__ == '__main__':
    main()
