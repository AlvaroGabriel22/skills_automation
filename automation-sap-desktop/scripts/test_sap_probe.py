import json
from pathlib import Path
import subprocess
import sys
import time
from types import SimpleNamespace as NS
import unittest
import sap_probe as m

class Collection:
    def __init__(self,values): self.values=values
    @property
    def Count(self): return len(self.values)
    def __call__(self,index): return self.values[index]
class Node:
    def __init__(self,ident='root',children=None):
        self.Id=ident;self.Type='GuiContainer' if children is not None else 'GuiTextField'
        self.Name='metadata';self.ContainerType=children is not None
        self.Children=Collection(children or [])
    @property
    def Text(self): raise AssertionError('Text must never be read')
def session(ident,system='QAS',client='100',user='USER',busy=False,number=0):
    s=Node(ident,[]);s.Busy=busy
    s.Info=NS(SystemName=system,Client=client,User=user,SessionNumber=number)
    return s
def records(sessions):
    engine=NS(Children=Collection([NS(Children=Collection(sessions))]))
    return m.list_sessions(engine,time.monotonic()+1)
class ProbeTests(unittest.TestCase):
    def test_selects_by_identity_not_first(self):
        a=session('a',system='PRD');b=session('b')
        self.assertIs(m.select_session(records([a,b]),'QAS','100','USER').session,b)
    def test_duplicate_requires_explicit_id(self):
        rows=records([session('a'),session('b')])
        with self.assertRaises(m.ProbeError): m.select_session(rows,'QAS','100','USER')
        self.assertEqual(m.select_session(rows,'QAS','100','USER','b').session_id,'b')
    def test_busy_session_not_silently_ignored(self):
        rows=records([session('a'),session('b',busy=True)])
        with self.assertRaises(m.ProbeError): m.select_session(rows,'QAS','100','USER')
        self.assertEqual(m.select_session(rows,'QAS','100','USER','a').session_id,'a')
    def test_missing_or_wrong_identity_fails(self):
        rows=records([session('a')])
        for identity in [('','100','USER'),('PRD','100','USER'),('QAS','200','USER')]:
            with self.assertRaises(m.ProbeError): m.select_session(rows,*identity)
    def test_public_metadata_has_no_username(self):
        self.assertNotIn('PRIVATE-USER',json.dumps(records([session('a',user='PRIVATE-USER')])[0].public()))
    def test_identity_change_is_detected(self):
        s=session('a');r=records([s])[0];m.assert_identity(r)
        s.Info.Client='200'
        with self.assertRaises(m.ProbeError): m.assert_identity(r)
    def test_inventory_only_metadata(self):
        result=m.inventory(Node('root',[Node('child')]),time.monotonic()+1)
        self.assertEqual([x['id'] for x in result['components']],['root','child'])
        self.assertFalse(result['truncated']);self.assertEqual(result['unreadable'],0)
    def test_total_node_limit(self):
        result=m.inventory(Node('root',[Node(str(i)) for i in range(100)]),time.monotonic()+1,max_nodes=3)
        self.assertEqual(len(result['components']),3);self.assertTrue(result['truncated'])
    def test_depth_limit_and_cycle(self):
        n=Node('cycle',[]);n.Children=Collection([n])
        result=m.inventory(n,time.monotonic()+1,max_depth=2)
        self.assertEqual(len(result['components']),3);self.assertTrue(result['truncated'])
    def test_deadline_and_busy_timeout(self):
        with self.assertRaises(m.ProbeError): m.inventory(Node(),time.monotonic()-1)
        with self.assertRaises(m.ProbeError): m.wait_ready(session('a',busy=True),time.monotonic()+0.01,interval=0.002)
    def test_session_limit_fails_instead_of_partial_selection(self):
        engine=NS(Children=Collection([NS(Children=Collection([session('a'),session('b')]))]))
        with self.assertRaises(m.ProbeError): m.list_sessions(engine,time.monotonic()+1,cap=1)
    def test_help_does_not_import_com(self):
        result=subprocess.run([sys.executable,str(Path(m.__file__)),'--help'],capture_output=True,text=True)
        self.assertEqual(result.returncode,0);self.assertIn('--inventory',result.stdout)
if __name__=='__main__': unittest.main()
