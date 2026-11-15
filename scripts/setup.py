"""Create a private local Compose secret without overwriting existing configuration."""
import os,secrets
from pathlib import Path
p=Path('.env')
try:
    fd=os.open(p,os.O_WRONLY|os.O_CREAT|os.O_EXCL,0o600)
except FileExistsError:
    raise SystemExit('.env already exists; retained unchanged.')
with os.fdopen(fd,'w') as stream:stream.write('REVIEW_OWNER_KEY='+secrets.token_urlsafe(48)+'\n')
print('Created private .env. Read it locally to obtain your owner key. Do not commit or share it.')
