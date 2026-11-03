import tempfile
import unittest
from unittest.mock import Mock
from iphone_use import Runtime
from wda_controller import PhoneController
from wda_client import WDAError
from test_controller import FakeWDA
from test_screen_protocol import MockScreen

class PreviewGeometryTests(unittest.TestCase):
    def setUp(self):
        self.tmp=tempfile.TemporaryDirectory();self.addCleanup(self.tmp.cleanup)
        self.runtime=Runtime(self.tmp.name)
        self.client=FakeWDA();self.screen=MockScreen(self.tmp.name)
        self.runtime.screen.close()
        self.runtime.client=self.client;self.runtime.screen=self.screen
        self.runtime.phone=PhoneController(self.client,self.tmp.name)
        self.runtime.phone.screen=self.screen
        self.screen.fresh_geometry=lambda:dict(self.client.size)
        self.args={"action":"tap","x":100,"y":200,"width":390,"height":844}

    def reads(self):
        return sum(p=="/window/size" for _,p,_ in self.client.calls)

    def test_repeated_gestures_reuse_geometry_with_fresh_frames(self):
        self.runtime.screen_gesture(self.args);self.runtime.screen_gesture(self.args)
        self.assertEqual(self.reads(),1)
        self.assertEqual(len(self.client.actions()),2)

    def test_rotated_frame_forces_refresh_and_refuses_old_points(self):
        self.runtime.screen_gesture(self.args)
        self.client.size={"width":844,"height":390}
        with self.assertRaises(WDAError) as caught:self.runtime.screen_gesture(self.args)
        self.assertEqual(caught.exception.code,"stale_viewport")
        self.assertEqual(len(self.client.actions()),1)

    def test_missing_live_frame_does_not_reuse_cached_geometry(self):
        self.screen.fresh_geometry=lambda:None
        self.runtime.screen_gesture(self.args);self.runtime.screen_gesture(self.args)
        self.assertEqual(self.reads(),2)

    def test_explicit_geometry_probe_is_always_fresh(self):
        self.runtime.screen_gesture(self.args)
        self.client.size={"width":844,"height":390}
        result=self.runtime.screen_gesture({"action":"viewport"})
        self.assertEqual(result["viewport"]["width"],844)
        self.assertEqual(len(self.client.actions()),1)
