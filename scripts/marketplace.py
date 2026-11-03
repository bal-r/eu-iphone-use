"""Register this reviewed local source, preserving unrelated marketplace entries."""
import json
from pathlib import Path
import subprocess
import sys

NAME='balta-tech-local'


def ensure(root):
    root=Path(root).resolve(strict=True)
    listing=json.loads(subprocess.run(['codex','plugin','marketplace','list','--json'],capture_output=True,text=True,check=True).stdout)
    existing=next((entry for entry in listing.get('marketplaces',[]) if entry.get('name')==NAME),None)
    old=None
    if existing:
        old=Path(existing['root']).resolve(strict=True)
        if old==root:return
        manifest=json.loads((old/'plugin.json').read_text())
        if existing.get('marketplaceSource',{}).get('sourceType','local')!='local' or manifest.get('name')!='iphone-use' or manifest.get('author',{}).get('name')!='Balta Tech':
            raise SystemExit('Preserving an unrecognised Balta marketplace source; review its registration manually.')
        subprocess.run(['codex','plugin','marketplace','remove',NAME],check=True)
    try:subprocess.run(['codex','plugin','marketplace','add',str(root),'--json'],check=True)
    except Exception:
        if old is not None:subprocess.run(['codex','plugin','marketplace','add',str(old),'--json'],check=True)
        raise

if __name__=='__main__':ensure(sys.argv[1])
