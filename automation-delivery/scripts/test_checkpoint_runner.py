import json
from pathlib import Path
import tempfile
import unittest
from unittest.mock import patch
import checkpoint_runner as m

class RunnerTests(unittest.TestCase):
    def setUp(self):
        self.temp=tempfile.TemporaryDirectory();self.addCleanup(self.temp.cleanup)
        self.path=Path(self.temp.name)/'state.json'
        self.items=[m.Item('0001',{'value':1}),m.Item('0002',{'value':2})]
        self.seen=[]
    def call(self,callback=None,**kwargs):
        def action(item):
            self.seen.append(item.key);return m.VerifiedResult(True)
        options=dict(checkpoint=self.path,environment='test-tenant',flow_version='v1')
        options.update(kwargs)
        return m.run_batch(self.items,callback or action,**options)
    def statuses(self):
        return [r['status'] for r in json.loads(self.path.read_text())['items'].values()]
    def test_default_one_and_repeat_skips_same_not_next(self):
        self.assertEqual(self.call()['completed'],1)
        self.assertEqual(self.call()['skipped'],1)
        self.assertEqual(self.seen,['0001'])
    def test_batch_requires_flag(self):
        for n in [2,0,-1,True,1.5]:
            with self.assertRaises(m.RunnerError): self.call(limit=n)
        self.assertEqual(self.seen,[])
    def test_explicit_batch_and_resume(self):
        self.call();self.assertEqual(self.call(limit=2,allow_batch=True)['completed'],1)
        self.assertEqual(self.seen,['0001','0002'])
        self.assertEqual(self.call(limit=2,allow_batch=True)['skipped'],2)
    def test_duplicate_and_numeric_keys_rejected(self):
        for items in [[self.items[0],self.items[0]],[m.Item(12,{})]]:
            self.items=items
            with self.assertRaises(m.RunnerError): self.call()
        self.assertEqual(self.seen,[])
    def test_environment_scope_change_rejected(self):
        self.call()
        with self.assertRaises(m.RunnerError): self.call(environment='other')
        with self.assertRaises(m.RunnerError): self.call(flow_version='v2')
        self.assertEqual(self.seen,['0001'])
    def test_input_scope_change_rejected(self):
        self.call();self.items.reverse()
        with self.assertRaises(m.RunnerError): self.call()
    def test_corrupt_checkpoint_blocks(self):
        self.path.write_text('not json')
        with self.assertRaises(m.RunnerError): self.call()
        self.assertEqual(self.seen,[])
    def test_existing_lock_never_removed(self):
        lock=self.path.with_name(self.path.name+'.lock');lock.write_text('existing')
        with self.assertRaises(m.BusyCheckpoint): self.call()
        self.assertEqual(lock.read_text(),'existing');self.assertEqual(self.seen,[])
    def test_side_effect_then_exception_blocks_retry(self):
        def action(item):
            self.seen.append(item.key);raise RuntimeError('synthetic-secret')
        with self.assertRaises(m.ReconciliationRequired): self.call(action)
        with self.assertRaises(m.ReconciliationRequired): self.call()
        self.assertEqual(self.seen,['0001']);self.assertEqual(self.statuses(),['unknown'])
        self.assertNotIn('synthetic-secret',self.path.read_text())
    def test_unverified_result_blocks(self):
        with self.assertRaises(m.ReconciliationRequired): self.call(lambda item:m.VerifiedResult(False))
        self.assertEqual(self.statuses(),['unknown'])
    def test_process_interruption_keeps_started(self):
        def interrupt(item): raise KeyboardInterrupt
        with self.assertRaises(KeyboardInterrupt): self.call(interrupt)
        self.assertEqual(self.statuses(),['started'])
        with self.assertRaises(m.ReconciliationRequired): self.call()
    def test_write_failure_before_action_does_not_call_action(self):
        with patch.object(m,'_atomic_write',side_effect=OSError('disk')):
            with self.assertRaises(OSError): self.call()
        self.assertEqual(self.seen,[])
    def test_write_failure_after_effect_remains_started(self):
        original=m._atomic_write;calls=[]
        def write(path,data):
            calls.append(1)
            if len(calls)==2: raise OSError('disk')
            original(path,data)
        with patch.object(m,'_atomic_write',side_effect=write):
            with self.assertRaises(OSError): self.call()
        self.assertEqual(self.seen,['0001']);self.assertEqual(self.statuses(),['started'])
        with self.assertRaises(m.ReconciliationRequired): self.call()
    def test_preflight_retry_must_be_explicit(self):
        def fail(item): raise ValueError('local')
        with self.assertRaises(m.RunnerError): self.call(preflight=fail)
        self.assertEqual(self.statuses(),['failed_preflight']);self.assertEqual(self.seen,[])
        with self.assertRaises(m.RunnerError): self.call()
        self.assertEqual(self.call(retry_preflight=True)['completed'],1)
    def test_checkpoint_contains_no_payload_or_raw_id(self):
        self.items=[m.Item('INTERNAL-ORDER-012345',{'detail':'PRIVATE-PAYLOAD'})]
        self.call();raw=self.path.read_text()
        self.assertNotIn('INTERNAL-ORDER-012345',raw);self.assertNotIn('PRIVATE-PAYLOAD',raw)
if __name__=='__main__': unittest.main()
