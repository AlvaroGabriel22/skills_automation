from pathlib import Path
import tempfile
import unittest
import zipfile
from unittest.mock import patch
from file_delivery import deliver

class DeliveryTests(unittest.TestCase):
    def test_copy_move_and_collision(self):
        with tempfile.TemporaryDirectory() as d:
            p=Path(d);src=p/'input.csv';src.write_text('OS,status\n0001,ok\n')
            result=deliver(src,p/'out'/'report.csv')
            self.assertTrue(src.exists());self.assertEqual(result['bytes'],src.stat().st_size)
            with self.assertRaises(FileExistsError): deliver(src,p/'out'/'report.csv',move=True)
            self.assertTrue(src.exists())
            result=deliver(src,p/'moved.csv',move=True)
            self.assertTrue(result['source_removed']);self.assertFalse(src.exists())
    def test_invalid_preserved(self):
        with tempfile.TemporaryDirectory() as d:
            p=Path(d)
            for content in [b'',b'<!doctype html><html>login</html>',b'not pdf']:
                src=p/'in.pdf';src.write_bytes(content)
                with self.assertRaises(ValueError): deliver(src,p/'out.pdf','pdf',True)
                self.assertTrue(src.exists());self.assertFalse((p/'out.pdf').exists())
    def test_xlsx_structure(self):
        with tempfile.TemporaryDirectory() as d:
            p=Path(d);src=p/'in.xlsx'
            with zipfile.ZipFile(src,'w') as z:
                z.writestr('[Content_Types].xml','synthetic');z.writestr('xl/workbook.xml','synthetic')
            self.assertEqual(deliver(src,p/'out.xlsx','xlsx')['business_validation'],'caller_responsibility')
    def test_unsupported_publication_preserves_source(self):
        with tempfile.TemporaryDirectory() as d:
            p=Path(d);src=p/'in.csv';src.write_text('synthetic data')
            with patch('file_delivery.os.link',side_effect=OSError('unsupported')):
                with self.assertRaises(OSError): deliver(src,p/'out.csv',move=True)
            self.assertTrue(src.exists());self.assertFalse((p/'out.csv').exists())
            self.assertEqual(list(p.glob('.delivery-*')),[])
    def test_symlink_and_partial_refused(self):
        with tempfile.TemporaryDirectory() as d:
            p=Path(d);src=p/'in.part';src.write_text('partial')
            with self.assertRaises(ValueError): deliver(src,p/'out')
            link=p/'link';link.symlink_to(src)
            with self.assertRaises(ValueError): deliver(link,p/'out')
if __name__=='__main__': unittest.main()
