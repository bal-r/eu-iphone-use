import json
import tempfile
import threading
import unittest
from unittest.mock import Mock
from iphone_use import Runtime
from wda_setup import _write_json

class PreviewIdentityTests(unittest.TestCase):
    def setUp(self):
        self.tmp=tempfile.TemporaryDirectory();self.addCleanup(self.tmp.cleanup)
        self.runtime=Runtime(self.tmp.name);self.addCleanup(self.runtime.close)
        self.manager=self.runtime.setup_manager

    def config(self,udid):_write_json(self.runtime.state_dir/"config.json",{"udid":udid})
    def join(self):
        thread=self.runtime._device_lookup
        if thread:thread.join(2);self.assertFalse(thread.is_alive())

    def test_lookup_before_configuration_does_not_latch_out_later_device(self):
        self.runtime.identify_device()
        self.config("device-a")
        self.manager.discover=Mock(return_value={"devices":[{"udid":"device-a","model":"iPhone 16 Pro"}]})
        self.runtime.identify_device();self.join()
        self.assertEqual(self.runtime.screen.device,{"model":"iPhone 16 Pro"})
        path=self.runtime.state_dir/"device.json"
        self.assertEqual(path.stat().st_mode&0o777,0o600)
        self.assertNotIn("udid",self.runtime.screen.start()["device"])

    def test_failed_lookup_can_retry_and_device_switch_discards_previous_pixels(self):
        self.config("device-a");self.manager.discover=Mock(side_effect=RuntimeError("temporary"))
        self.runtime.identify_device();self.join()
        self.assertGreater(self.runtime._device_retry_at,0)
        self.runtime._device_retry_at=0
        self.manager.discover=Mock(return_value={"devices":[{"udid":"device-a","model":"iPhone 16 Pro"}]})
        self.runtime.identify_device();self.join()
        self.config("device-b")
        self.manager.discover=Mock(return_value={"devices":[{"udid":"device-b","model":"iPhone SE"}]})
        self.assertTrue(self.runtime.identify_device());self.join()
        self.assertTrue(self.runtime.screen.start()["discard_previous_frame"])
        self.assertEqual(self.runtime.screen.device,{"model":"iPhone SE"})

    def test_late_previous_device_lookup_cannot_overwrite_new_identity(self):
        started=threading.Event();release=threading.Event()
        def discover():
            if threading.current_thread() is old:
                started.set();release.wait(2)
                return {"devices":[{"udid":"device-a","model":"old"}]}
            return {"devices":[{"udid":"device-b","model":"new"}]}
        self.config("device-a")
        # Hold discovery until the original worker object is captured.
        gate=threading.Event()
        def blocked():gate.wait(2);return discover()
        self.manager.discover=blocked
        self.runtime.identify_device();old=self.runtime._device_lookup;gate.set();self.assertTrue(started.wait(2))
        self.config("device-b");self.runtime.identify_device();self.join()
        release.set();old.join(2)
        self.assertEqual(self.runtime.screen.device,{"model":"new"})
