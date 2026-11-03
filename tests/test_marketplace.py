import importlib.util
import json
from pathlib import Path
import subprocess
import tempfile
import unittest
from unittest.mock import Mock,patch

spec=importlib.util.spec_from_file_location('marketplace',Path(__file__).resolve().parents[1]/'scripts/marketplace.py')
marketplace=importlib.util.module_from_spec(spec);spec.loader.exec_module(marketplace)

class MarketplaceTests(unittest.TestCase):
    def test_local_checkout_move_preserves_other_sources_and_rolls_back_failed_add(self):
        with tempfile.TemporaryDirectory() as directory:
            old=(Path(directory)/'old').resolve();new=(Path(directory)/'new').resolve();old.mkdir();new.mkdir()
            (old/'plugin.json').write_text(json.dumps({'name':'iphone-use','author':{'name':'Balta Tech'}}))
            listing={'marketplaces':[{'name':'unrelated','root':'/unrelated'},{'name':'balta-tech-local','root':str(old),'marketplaceSource':{'sourceType':'local'}}]}
            seen=[]
            def run(argv,**kw):
                seen.append(argv)
                if 'list' in argv:return Mock(stdout=json.dumps(listing))
                if str(new) in argv:raise subprocess.CalledProcessError(1,argv)
                return Mock()
            with patch.object(marketplace.subprocess,'run',side_effect=run):
                with self.assertRaises(subprocess.CalledProcessError):marketplace.ensure(new)
            self.assertEqual(seen[-1],['codex','plugin','marketplace','add',str(old),'--json'])
            self.assertEqual([v for v in seen if 'remove' in v],[['codex','plugin','marketplace','remove','balta-tech-local']])
