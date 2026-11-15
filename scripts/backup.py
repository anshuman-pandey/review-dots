"""Consistent SQLite backup. Never overwrite an existing backup."""
import argparse,os,sqlite3
from pathlib import Path
p=argparse.ArgumentParser(description=__doc__);p.add_argument('source');p.add_argument('destination');args=p.parse_args()
source=Path(args.source).resolve();destination=Path(args.destination).resolve()
if source==destination:raise SystemExit('Source and destination must differ.')
os.umask(0o077)
fd=os.open(destination,os.O_WRONLY|os.O_CREAT|os.O_EXCL,0o600);os.close(fd)
try:
    with sqlite3.connect(source.as_uri()+'?mode=ro',uri=True) as src,sqlite3.connect(destination) as dst:
        src.backup(dst)
        if dst.execute('PRAGMA integrity_check').fetchone()[0]!='ok':raise RuntimeError('Backup failed integrity check.')
except Exception:
    destination.unlink(missing_ok=True)
    raise
print('Backup complete. Protect this file: it contains review images, comments and access records.')
