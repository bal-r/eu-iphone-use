import json
import tempfile
import unittest
from unittest.mock import patch
from test_controller import FakeWDA
from wda_controller import PhoneController
from wda_client import WDAError

class BatchWorkflowTests(unittest.TestCase):
    def setUp(self):
        self.tmp=tempfile.TemporaryDirectory();self.addCleanup(self.tmp.cleanup)
        self.client=FakeWDA();self.phone=PhoneController(self.client,self.tmp.name)
        self.steps=[{"op":"tap","args":{"selector":{"label":"Target"}}}]

    def test_final_observation_avoids_another_agent_call(self):
        result=self.phone.batch(self.steps,observe="tree")
        self.assertTrue(result["complete"])
        self.assertIn("nodes",result["observation"])
        self.assertEqual(sum(p.startswith("/source") for _,p,_ in self.client.calls),1)
        self.assertEqual(len(self.client.actions()),1)

    def test_compact_omits_target_diagnostics_and_full_preserves_them(self):
        self.steps[0]["args"]["expect"]={"label":"Target"}
        compact=self.phone.batch(self.steps)
        full=self.phone.batch(self.steps,compact=False)
        self.assertNotIn("postcondition",compact["results"][0])
        self.assertIn("postcondition",full["results"][0])
        self.assertLess(len(json.dumps(compact)),len(json.dumps(full)))

    def test_reuses_last_observation_instead_of_reading_twice(self):
        result=self.phone.batch([{"op":"observe","args":{}}],observe="tree")
        self.assertIn("nodes",result["observation"])
        self.assertNotIn("nodes",result["results"][0])
        self.assertEqual(sum(p.startswith("/source") for _,p,_ in self.client.calls),1)

    def test_failed_final_read_does_not_mark_completed_actions_for_replay(self):
        with patch.object(self.phone,"observe",side_effect=WDAError("pua_timeout","timeout")):
            result=self.phone.batch(self.steps,observe="tree")
        self.assertTrue(result["complete"])
        self.assertEqual(result["completed_steps"],1)
        self.assertEqual(result["observation_error"]["code"],"pua_timeout")
        self.assertEqual(len(self.client.actions()),1)

    def test_uncertain_action_stops_without_final_read_or_replay(self):
        self.client.click_error=WDAError("action_uncertain","timeout",uncertain=True)
        result=self.phone.batch(self.steps*2,observe="tree")
        self.assertFalse(result["complete"])
        self.assertEqual(result["stopped_at"],0)
        self.assertTrue(result["error"]["uncertain"])
        self.assertFalse(any(p.startswith("/source") for _,p,_ in self.client.calls))
