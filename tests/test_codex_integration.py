import contextlib
import io
import json
import os
from pathlib import Path
import subprocess
import sys
import tempfile
import threading
import time
import unittest
from unittest.mock import Mock,patch

from iphone_use import Runtime,INSTRUCTIONS,result_content,serve,tool_result
from device_lease import DeviceLease
from operation_control import OperationControl
from test_controller import FakeWDA
from wda_controller import PhoneController
from wda_client import WDAError

class IntegrationTests(unittest.TestCase):
    def setUp(self):
        self.tmp=tempfile.TemporaryDirectory();self.addCleanup(self.tmp.cleanup)
        self.runtime=Runtime(self.tmp.name);self.addCleanup(self.runtime.close)
        self.client=FakeWDA();self.client.close=Mock()
        self.runtime.client=self.client;self.runtime.phone=PhoneController(self.client,self.tmp.name)
        self.runtime.phone.screen=self.runtime.screen

    def test_concurrent_preview_and_tool_share_one_lease_instance(self):
        from concurrent.futures import ThreadPoolExecutor
        (Path(self.tmp.name)/'config.json').write_text(json.dumps({'udid':'fixture-device-1234'}))
        with patch.dict(os.environ,{'IPHONE_USE_LEASE_ROOT':str(Path(self.tmp.name)/'leases')}):
            with ThreadPoolExecutor(max_workers=8) as pool:
                instances=list(pool.map(lambda _:self.runtime.current_lease(),range(16)))
        self.assertEqual(len({id(instance) for instance in instances}),1)

    def test_first_512_characters_cover_efficient_and_private_control(self):
        for text in ('setup(status)','batch','Pause','Never replay','device(release)'):
            self.assertIn(text,INSTRUCTIONS[:512])

    def test_optional_absent_selector_skips_without_phone_action_or_screenshot(self):
        result=self.runtime.phone.tap(selector={'label':'Known optional popup'},optional=True)
        self.assertTrue(result['skipped']);self.assertEqual(self.client.actions(),[])
        self.assertFalse(any(p=='/screenshot' for _,p,_ in self.client.calls))
        with self.assertRaises(WDAError):self.runtime.phone.tap(x=1,y=1,optional=True)

    def test_optional_known_target_still_executes_only_once(self):
        result=self.runtime.phone.tap(selector={'label':'Target'},optional=True)
        self.assertTrue(result['action_executed']);self.assertEqual(len(self.client.actions()),1)

    def test_cancelled_inflight_write_retains_uncertainty(self):
        control=OperationControl();event=threading.Event()
        with control.operation(event):
            control.before_request(False);event.set()
            with self.assertRaises(WDAError) as caught:control.after_request()
        self.assertEqual(caught.exception.code,'action_uncertain')
        self.assertTrue(caught.exception.uncertain)

    def test_protocol_cancellation_stops_queued_work_before_it_runs(self):
        entered=threading.Event();release=threading.Event()
        def observe(**_):entered.set();release.wait(2);return {'nodes':[]}
        self.runtime.phone.observe=observe;self.runtime.phone.tap=Mock()
        def lines():
            yield json.dumps({'jsonrpc':'2.0','id':1,'method':'tools/call','params':{'name':'pua_observe','arguments':{}}})+'\n'
            self.assertTrue(entered.wait(2))
            yield json.dumps({'jsonrpc':'2.0','id':2,'method':'tools/call','params':{'name':'pua_tap','arguments':{'x':1,'y':1}}})+'\n'
            yield json.dumps({'jsonrpc':'2.0','method':'notifications/cancelled','params':{'requestId':2}})+'\n'
            release.set()
        out=io.StringIO()
        with patch.object(sys,'stdin',lines()),contextlib.redirect_stdout(out):serve(self.runtime)
        self.runtime.phone.tap.assert_not_called()
        replies={x['id']:x for x in map(json.loads,out.getvalue().splitlines())}
        self.assertIn('cancelled',json.dumps(replies[2]))

    def test_cancellation_between_batch_steps_never_sends_the_next_step(self):
        event=threading.Event();taps=[]
        def first(**args):taps.append(args);event.set();return {'action_executed':True}
        self.runtime.phone.tap=first
        with self.runtime.control.operation(event):
            data=tool_result(self.runtime,{'name':'pua_batch','arguments':{'steps':[{'op':'tap','args':{'x':1,'y':1}},{'op':'tap','args':{'x':2,'y':2}}]}})
        self.assertEqual(len(taps),1);self.assertIn('cancelled',json.dumps(data))

    def test_progress_is_counts_only_and_results_have_typed_outcomes(self):
        received=[]
        with self.runtime.control.operation(progress=lambda done,total:received.append((done,total))):
            result=tool_result(self.runtime,{'name':'pua_batch','arguments':{'steps':[{'op':'tap','args':{'selector':{'label':'Target'}}}]}})
        self.assertEqual(received,[(0,1),(1,1)])
        data=json.loads(result['content'][0]['text'])
        self.assertEqual(data['outcome'],'completed');self.assertTrue(data['ok'])
        uncertain=json.loads(result_content({'error':{'code':'action_uncertain','uncertain':True}})['content'][0]['text'])
        self.assertEqual(uncertain['outcome'],'uncertain')

    def test_string_setup_errors_keep_their_actionable_message(self):
        data=json.loads(result_content({'ok':False,'error':'Selected device is unavailable','next_steps':['Connect the selected device']})['content'][0]['text'])
        self.assertEqual(data['outcome'],'failed')
        self.assertIn('Selected device',data['error']['message'])
        completed=json.loads(result_content({'complete':True,'results':[{'action_executed':True}]})['content'][0]['text'])
        self.assertEqual(completed['action_state'],'completed')

    def test_target_selection_reads_fresh_state_and_sends_no_touch(self):
        result=self.runtime.call('pua_screen_action',{'action':'select','x':100,'y':220,'width':390,'height':844})
        self.assertIn('observation_id',result['selection'])
        self.assertEqual(self.client.actions(),[])
        self.assertFalse(result['action_executed'])

class LeaseTests(unittest.TestCase):
    def setUp(self):
        self.tmp=tempfile.TemporaryDirectory();self.addCleanup(self.tmp.cleanup)
        self.env=patch.dict(os.environ,{'IPHONE_USE_LEASE_ROOT':self.tmp.name});self.env.start();self.addCleanup(self.env.stop)

    def test_other_conversation_is_blocked_until_release_and_then_needs_observation(self):
        a=DeviceLease('fixture');b=DeviceLease('fixture');self.addCleanup(a.close);self.addCleanup(b.close)
        a.claim('Calculator test')
        with self.assertRaises(WDAError) as caught:b.claim()
        self.assertEqual(caught.exception.code,'device_held')
        self.assertEqual(caught.exception.details['holder']['label'],'Calculator test')
        a.release()
        with self.assertRaises(WDAError):
            with b.hold(mutation=True):self.fail('stale action permitted')
        b.observed()
        with b.hold(mutation=True):pass

    def test_idle_lease_expires_and_active_calls_are_not_released(self):
        a=DeviceLease('idle',idle_seconds=.08);b=DeviceLease('idle');self.addCleanup(a.close);self.addCleanup(b.close)
        with a.hold():
            time.sleep(.12)
            with self.assertRaises(WDAError):b.claim()
        deadline=time.monotonic()+1
        while a.status()['held_by_this_chat'] and time.monotonic()<deadline:time.sleep(.02)
        b.claim()
        self.assertTrue(b.status()['held_by_this_chat'])

    def test_kernel_releases_a_crashed_owner_without_restarting_phone_service(self):
        source="from device_lease import DeviceLease; import time; d=DeviceLease('crash'); d.claim('fixture'); print('held',flush=True); time.sleep(20)"
        process=subprocess.Popen([sys.executable,'-c',source],env={**os.environ,'PYTHONPATH':str(Path(__file__).resolve().parents[1]/'server')},stdout=subprocess.PIPE,text=True)
        try:
            self.assertEqual(process.stdout.readline().strip(),'held')
            b=DeviceLease('crash');self.addCleanup(b.close)
            with self.assertRaises(WDAError):b.claim()
            process.terminate();process.wait(timeout=2)
            self.assertIsNone(b.status()['holder'])
            b.claim();self.assertTrue(b.status()['held_by_this_chat'])
        finally:
            if process.poll() is None:process.kill();process.wait(timeout=2)
            process.stdout.close()
