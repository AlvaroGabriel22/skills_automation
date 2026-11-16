import os
from pathlib import Path
import tempfile
import unittest
from prepare_env import prepare

class PrepareEnvTests(unittest.TestCase):
    def test_create_and_preserve(self):
        with tempfile.TemporaryDirectory() as d:
            p=Path(d)/'project'
            self.assertTrue(prepare(p,'web')['env_created'])
            self.assertIn('AUTOMATION_PASSWORD=\n',(p/'.env').read_text())
            (p/'.env').write_text('AUTOMATION_PASSWORD=synthetic-only\n')
            result=prepare(p,'sap')
            self.assertFalse(result['env_created'])
            self.assertEqual((p/'.env').read_text(),'AUTOMATION_PASSWORD=synthetic-only\n')
            self.assertNotIn('synthetic-only',str(result))
            self.assertEqual((p/'.gitignore').read_text().splitlines().count('.env'),1)
            if os.name=='posix': self.assertEqual((p/'.env').stat().st_mode & 0o777,0o600)
    def test_symlink_refused(self):
        with tempfile.TemporaryDirectory() as d:
            p=Path(d); target=p/'elsewhere'; target.write_text('untouched')
            (p/'.env').symlink_to(target)
            with self.assertRaises(ValueError): prepare(p,'web')
            self.assertEqual(target.read_text(),'untouched')
    def test_ignore_preserved(self):
        with tempfile.TemporaryDirectory() as d:
            p=Path(d);(p/'.gitignore').write_text('custom-rule')
            prepare(p,'sap')
            self.assertTrue((p/'.gitignore').read_text().startswith('custom-rule\n'))
            self.assertIn('.state/',(p/'.gitignore').read_text())
            self.assertIn('SAP_SESSION_ID=',(p/'.env.example').read_text())
if __name__=='__main__': unittest.main()
