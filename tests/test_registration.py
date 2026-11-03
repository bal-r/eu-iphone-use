import importlib.util
import io
import json
from pathlib import Path
import tempfile
import unittest
from unittest.mock import patch

ROOT=Path(__file__).resolve().parents[1]
spec=importlib.util.spec_from_file_location('register', ROOT/'scripts/register_mcp.py')
registration=importlib.util.module_from_spec(spec)
spec.loader.exec_module(registration)

class RegistrationTests(unittest.TestCase):
    def test_installs_in_its_own_namespace_without_reading_other_configuration(self):
        with tempfile.TemporaryDirectory() as temporary:
            root=Path(temporary).resolve(); (root/'server').mkdir(); (root/'server/iphone_use.py').write_text('# fixture')
            installation={'pluginId':'iphone-use@balta-tech-local','installedPath':str(root)}
            with patch.object(registration.sys,'stdin',io.StringIO(json.dumps(installation))), patch.object(registration.subprocess,'run') as run, patch('sys.stdout',io.StringIO()):
                registration.main()
            run.assert_called_once_with(['codex','mcp','add','balta_iphone_use','--','python3',str(root/'server/iphone_use.py')],check=True)

    def test_rejects_a_different_plugin_before_registering(self):
        with patch.object(registration.sys,'stdin',io.StringIO('{"pluginId":"unrelated"}')), patch.object(registration.subprocess,'run') as run:
            with self.assertRaises(SystemExit): registration.main()
        run.assert_not_called()
