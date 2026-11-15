import os,sqlite3,subprocess,sys,tempfile,unittest
from pathlib import Path
SCRIPT=Path(__file__).resolve().parents[1]/'scripts/backup.py'
class BackupTests(unittest.TestCase):
 def test_live_database_backup_preserves_rows_and_private_mode(self):
  with tempfile.TemporaryDirectory() as tmp:
   src=Path(tmp)/'source';dst=Path(tmp)/'backup'
   with sqlite3.connect(src) as db:
    db.execute('CREATE TABLE records(value TEXT)');db.execute("INSERT INTO records VALUES('client record')");db.commit()
    subprocess.run([sys.executable,str(SCRIPT),str(src),str(dst)],check=True,capture_output=True)
   with sqlite3.connect(dst) as db:self.assertEqual(db.execute('SELECT value FROM records').fetchone()[0],'client record')
   self.assertEqual(dst.stat().st_mode & 0o777,0o600)
 def test_existing_backup_is_never_overwritten(self):
  with tempfile.TemporaryDirectory() as tmp:
   dst=Path(tmp)/'backup';dst.write_bytes(b'keep this')
   r=subprocess.run([sys.executable,str(SCRIPT),tmp+'/missing',str(dst)],capture_output=True)
   self.assertNotEqual(r.returncode,0);self.assertEqual(dst.read_bytes(),b'keep this')
 def test_missing_source_leaves_no_empty_backup(self):
  with tempfile.TemporaryDirectory() as tmp:
   r=subprocess.run([sys.executable,str(SCRIPT),tmp+'/missing',tmp+'/backup'],capture_output=True)
   self.assertNotEqual(r.returncode,0);self.assertFalse(Path(tmp,'backup').exists());self.assertFalse(Path(tmp,'missing').exists())
