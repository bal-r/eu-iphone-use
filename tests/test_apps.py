"""Local app discovery must work without any network lookup."""
import json
from pathlib import Path
import socket
import subprocess
import sys
import tempfile
import unittest
from unittest.mock import patch

sys.path.insert(0, str(Path(__file__).resolve().parents[1] / 'server'))
from wda_apps import AppCatalog

class FakeSetup:
    config = {}

class AppTests(unittest.TestCase):
    def setUp(self):
        self.temp = tempfile.TemporaryDirectory()
        self.addCleanup(self.temp.cleanup)
        self.directory = Path(self.temp.name)
        self.setup = FakeSetup()
        self.setup.config = {}
        self.catalog = AppCatalog(self.directory, self.setup)

    def test_offline_reference_does_not_claim_installation(self):
        with patch.object(socket, 'create_connection', side_effect=AssertionError('No Internet')):
            result = self.catalog.lookup('Calculator', source='catalog')
        self.assertTrue(result['ok'])
        self.assertEqual(result['candidates'][0]['bundle_id'], 'com.apple.calculator')
        self.assertFalse(result['candidates'][0]['installed_verified'])
        self.assertEqual(result['searched_sources'], ['catalog'])

    def test_unknown_app_never_falls_back_to_online_search(self):
        with patch.object(socket, 'create_connection', side_effect=AssertionError('No Internet')):
            result = self.catalog.lookup('Unknown private app')
        self.assertTrue(result['ok'])
        self.assertEqual(result['candidates'], [])
        self.assertEqual(result['searched_sources'], ['installed', 'catalog'])
        self.assertFalse(self.catalog.lookup('Calculator', source='apple')['ok'])

    def test_device_formats_reject_invalid_and_duplicate_bundle_ids(self):
        rows = AppCatalog.parse_installed({'result': {'apps': [
            {'name': 'Example', 'bundleIdentifier': 'com.example.App'},
            {'name': 'Duplicate', 'bundleID': 'com.example.App'},
            {'name': 'Invalid', 'bundleId': '../escape'}, None]}})
        self.assertEqual(len(rows), 1)
        self.assertTrue(rows[0]['installed_verified'])
        mapped = AppCatalog.parse_installed({'result': {'installedApps': {'com.example.Other': {'displayName': 'Other'}}}})
        self.assertEqual(mapped[0]['bundle_id'], 'com.example.Other')

    def test_inventory_is_cached_privately_and_only_matches_are_returned(self):
        self.setup.config = {'udid': '00008150-ABCDEF0123456789'}
        def run(argv, **kwargs):
            self.assertIn('--include-all-apps', argv)
            self.assertNotIn('shell', kwargs)
            Path(argv[argv.index('--json-output') + 1]).write_text(json.dumps({'result': {'apps': [
                {'name': 'Example', 'bundleIdentifier': 'com.example.App'},
                {'name': 'Unrelated private app', 'bundleIdentifier': 'com.private.Other'}]}}))
            return subprocess.CompletedProcess(argv, 0)
        with patch('wda_apps.subprocess.run', side_effect=run) as probe:
            first = self.catalog.lookup('Example', source='installed')
            second = self.catalog.lookup('Example', source='installed')
        self.assertEqual(probe.call_count, 1)
        self.assertEqual(first['candidates'], second['candidates'])
        self.assertEqual(len(first['candidates']), 1)
        self.assertTrue(first['candidates'][0]['installed_verified'])
        cache = self.directory / 'apps-installed-cache.json'
        self.assertEqual(cache.stat().st_mode & 0o777, 0o600)
        self.assertFalse(list(self.directory.glob('apps-device-*')))

    def test_failed_inventory_is_not_misreported_as_verified(self):
        self.setup.config = {'udid': '00008150-ABCDEF0123456789'}
        with patch('wda_apps.subprocess.run', return_value=subprocess.CompletedProcess([], 1)):
            result = self.catalog.lookup('Example', source='installed')
        self.assertFalse(result['ok'])
        self.assertEqual(result['error']['code'], 'app_lookup_unavailable')
        self.assertFalse((self.directory / 'apps-installed-cache.json').exists())
        self.assertFalse(list(self.directory.glob('apps-device-*')))

    def test_invalid_parameters_are_rejected(self):
        for arguments in ({'query': ''}, {'query': 'x'*101}, {'query': 'x', 'limit': True},
                          {'query': 'x', 'source': 'remote'}, {'query': 'x', 'country': 'CHN'}):
            self.assertFalse(self.catalog.lookup(**arguments)['ok'])
