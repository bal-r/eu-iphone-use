import hashlib
from pathlib import Path
import sys
import tempfile
import unittest

ROOT = Path(__file__).resolve().parents[1]
sys.path.insert(0, str(ROOT / 'server'))
from local_auth import connection_token
from wda_hardening import SOURCE_PATH, PATCHED_SHA256, harden_source, verify_hardened_source
from wda_controller import PhoneController

class PrivacyTests(unittest.TestCase):
    def test_capability_is_random_persistent_private_and_never_follows_symlinks(self):
        with tempfile.TemporaryDirectory() as temporary:
            directory = Path(temporary)
            first = connection_token(directory)
            self.assertRegex(first, r'^[0-9a-f]{64}$')
            self.assertEqual(first, connection_token(directory))
            path = directory / 'connection-token'
            self.assertEqual(path.stat().st_mode & 0o777, 0o600)
            path.unlink()
            external = directory / 'external'
            external.write_text('private unrelated content')
            path.symlink_to(external)
            with self.assertRaises(OSError): connection_token(directory)
            self.assertEqual(external.read_text(), 'private unrelated content')

    def test_exact_wda_patch_is_idempotent_and_tampering_is_rejected(self):
        with tempfile.TemporaryDirectory() as temporary:
            source = Path(temporary)
            target = source / SOURCE_PATH
            target.parent.mkdir(parents=True)
            target.write_bytes((ROOT / 'tests/fixtures/FBWebServer.m').read_bytes())
            harden_source(source)
            self.assertEqual(hashlib.sha256(target.read_bytes()).hexdigest(), PATCHED_SHA256)
            verify_hardened_source(source)
            harden_source(source)
            body = target.read_text()
            self.assertIn('self.screenshotsBroadcaster.interface = @"127.0.0.1"', body)
            self.assertIn('NSString *bindingIP = @"127.0.0.1"', body)
            self.assertNotIn('setDefaultHeader:@"Access-Control-Allow-Origin"', body)
            target.write_text(body + '\n// unreviewed change\n')
            with self.assertRaises(ValueError): verify_hardened_source(source)
            with self.assertRaises(ValueError): harden_source(source)
            self.assertTrue(target.read_text().endswith('// unreviewed change\n'))

    def test_cleanup_deletes_only_this_process_observations(self):
        with tempfile.TemporaryDirectory() as temporary:
            directory = Path(temporary)
            controller = PhoneController(None, directory)
            own = directory / 'owned.png'; own.write_bytes(b'private pixels')
            unrelated = directory / 'unrelated.png'; unrelated.write_bytes(b'other session')
            controller.capture_paths.add(own)
            controller.cleanup_captures()
            self.assertFalse(own.exists())
            self.assertTrue(unrelated.exists())

    def test_runtime_has_no_telemetry_module_or_online_app_lookup(self):
        for name in ('analytics.py', 'posthog.json', 'ga4.json'):
            self.assertFalse((ROOT / 'server' / name).exists())
        source = (ROOT / 'server/iphone_use.py').read_text()
        self.assertNotIn('self.analytics', source)
        self.assertNotIn('from analytics', source)
        self.assertNotIn('urllib', (ROOT / 'server/wda_apps.py').read_text())
