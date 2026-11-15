"""Disposable container test: image, feedback, restart and recovery."""
import json,secrets,subprocess,tempfile,time,urllib.request,urllib.error
from pathlib import Path
ROOT=Path(__file__).resolve().parents[1]
name='dots-test-'+secrets.token_hex(5);volume=name+'-data';restored=name+'-restore';key=secrets.token_urlsafe(32);image='review-dots-acceptance:local'
def docker(*args):return subprocess.check_output(['docker',*args],text=True).strip()
def call(base,path,token=key,data=None,raw=None,content_type=None):
 headers={'Authorization':'Bearer '+token}
 if data is not None:raw=json.dumps(data).encode();content_type='application/json'
 if content_type:headers['Content-Type']=content_type
 with urllib.request.urlopen(urllib.request.Request(base+path,data=raw,headers=headers),timeout=10) as r:return r.read()
def address(container):return 'http://127.0.0.1:'+docker('port',container,'8092/tcp').rsplit(':',1)[1]
def ready(container):
 base=address(container)
 for _ in range(100):
  try:
   with urllib.request.urlopen(base,timeout=1) as r:
    if r.status==200:return base
  except (OSError,urllib.error.URLError):time.sleep(.1)
 raise RuntimeError('Service failed to start')
def start(container,vol):
 docker('run','-d','--name',container,'--read-only','--tmpfs','/tmp:size=32m','--cap-drop=ALL','--security-opt=no-new-privileges:true','-e','REVIEW_OWNER_KEY='+key,'-v',vol+':/data','-p','127.0.0.1::8092',image)
 return ready(container)
try:
 base=start(name,volume);assert docker('exec',name,'id','-u')=='10001'
 boundary='dots-test-boundary';payload=(ROOT/'tests/fixture.png').read_bytes()
 raw=(f'--{boundary}\r\nContent-Disposition: form-data; name="title"\r\n\r\nPersistence review\r\n--{boundary}\r\nContent-Disposition: form-data; name="image"; filename="design.png"\r\nContent-Type: image/png\r\n\r\n'.encode()+payload+f'\r\n--{boundary}--\r\n'.encode())
 created=json.loads(call(base,'/api/boards',raw=raw,content_type='multipart/form-data; boundary='+boundary));url='/api/boards/'+created['id'];token=created['token'];normalized=call(base,url+'/image',token)
 pin=json.loads(call(base,url+'/pins',token,data={'x':.25,'y':.6,'author':'Test reviewer','body':'Keep this comment'}))['id']
 call(base,url+'/pins/'+pin+'/resolve',data={'revision':1,'resolved':True})
 docker('restart',name);base=ready(name)
 assert call(base,url+'/image',token)==normalized
 assert json.loads(call(base,url,token))['pins'][0]['resolved']==1
 docker('stop',name)
 with tempfile.TemporaryDirectory(dir=ROOT) as tmp:
  source=Path(tmp)/'source.sqlite3';backup=Path(tmp)/'backup.sqlite3'
  docker('cp',name+':/data/review.sqlite3',str(source))
  subprocess.run(['python3',str(ROOT/'scripts/backup.py'),str(source),str(backup)],check=True)
  assert backup.stat().st_mode & 0o777==0o600
  docker('volume','create',restored)
  docker('run','--rm','--user','0','-v',restored+':/data','-v',str(backup)+':/backup:ro',image,'python','-c',"import shutil,os;shutil.copyfile('/backup','/data/review.sqlite3');os.chown('/data/review.sqlite3',10001,10001);os.chmod('/data/review.sqlite3',0o600);os.chown('/data',10001,10001)")
  restored_base=start(name+'-restored',restored)
  assert call(restored_base,url+'/image',token)==normalized
  exported=json.loads(call(restored_base,url+'/export',token));assert exported['pins'][0]['events'][0]['resolved']==1
  call(restored_base,url+'/pins/'+pin+'/resolve',data={'revision':2,'resolved':False})
  call(restored_base,url+'/pins',token,data={'x':0,'y':1,'author':'Test reviewer','body':'After recovery'})
  assert len(json.loads(call(restored_base,url,token))['pins'])==2
  call(restored_base,url+'/rotate',data={})
  try:call(restored_base,url+'/image',token);raise AssertionError('Revoked token worked')
  except urllib.error.HTTPError as error:assert error.code==400
 print('PASS: non-root read-only container; normalized image, comments and resolution history survive restart/restore; post-restore writes and revocation work')
finally:
 for container in (name,name+'-restored'):subprocess.run(['docker','rm','-f',container],stdout=subprocess.DEVNULL,stderr=subprocess.DEVNULL)
 for vol in (volume,restored):subprocess.run(['docker','volume','rm',vol],stdout=subprocess.DEVNULL,stderr=subprocess.DEVNULL)
