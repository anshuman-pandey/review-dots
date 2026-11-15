import io,json,tempfile,unittest
from PIL import Image,PngImagePlugin
from reviews import Reviews,Invalid,image_bytes
from server import create_app

def png():
 out=io.BytesIO();info=PngImagePlugin.PngInfo();info.add_text('secret','remove me');Image.new('RGB',(320,180),'#e4c8a4').save(out,format='PNG',pnginfo=info);return out.getvalue()
class ReviewTests(unittest.TestCase):
 def setUp(self):self.tmp=tempfile.TemporaryDirectory();self.path=self.tmp.name+'/db';self.db=Reviews(self.path);self.id,self.token=self.db.create('Draft',png())
 def tearDown(self):self.db.close();self.tmp.cleanup()
 def test_image_is_sanitized(self):
  with Image.open(io.BytesIO(self.db.image(self.id))) as im:self.assertNotIn('secret',im.info);self.assertEqual(im.size,(320,180))
 def test_invalid_images_rejected(self):
  for raw in [b'',b'<svg/>',b'fake image',b'x'*(10*1024*1024+1)]:
   with self.assertRaises(Invalid):image_bytes(raw)
 def test_pin_coordinates_rejected(self):
  for x in [-1,1.1,float('nan'),float('inf'),True,None,'0.2']:
   with self.assertRaises(Invalid):self.db.add(self.id,x,.5,'Sam','Comment')
 def test_resolution_stale_and_cross_board(self):
  pin=self.db.add(self.id,.2,.7,'Sam','Move this');self.db.resolve(self.id,pin,1,True)
  with self.assertRaises(Invalid):self.db.resolve(self.id,pin,1,False)
  other,_=self.db.create('Other',png())
  with self.assertRaises(Invalid):self.db.resolve(other,pin,2,False)
  self.db.resolve(self.id,pin,2,False);self.assertEqual(self.db.view(self.id)['pins'][0]['resolved'],0)
 def test_export_history_no_credentials(self):
  pin=self.db.add(self.id,0,1,'Sam','<script>literal</script>');self.db.resolve(self.id,pin,1,True);raw=self.db.export(self.id);self.assertNotIn(self.token,raw);self.assertNotIn('token_hash',raw);self.assertEqual(len(json.loads(raw)['pins'][0]['events']),1)
 def test_rotation_and_persistence(self):
  new=self.db.rotate(self.id)
  with self.assertRaises(Invalid):self.db.auth(self.id,self.token)
  self.db.close();self.db=Reviews(self.path);self.db.auth(self.id,new)
 def test_comment_validation(self):
  for body in ['',None,'a'*4001]:
   with self.assertRaises(Invalid):self.db.add(self.id,.5,.5,'Sam',body)
class HTTPTests(unittest.TestCase):
 def setUp(self):
  self.tmp=tempfile.TemporaryDirectory();self.app=create_app(self.tmp.name+'/db','o'*40);self.c=self.app.test_client();self.owner={'Authorization':'Bearer '+'o'*40};r=self.c.post('/api/boards',headers=self.owner,data={'title':'Test','image':(io.BytesIO(png()),'draft.png')}).get_json();self.id=r['id'];self.guest={'Authorization':'Bearer '+r['token']};self.url='/api/boards/'+self.id
 def tearDown(self):self.tmp.cleanup()
 def test_guest_workflow_owner_resolution(self):
  r=self.c.post(self.url+'/pins',headers=self.guest,json={'x':.3,'y':.4,'author':'Reviewer','body':'Change this'});self.assertEqual(r.status_code,201);pin=r.get_json()['id']
  self.assertEqual(self.c.post(self.url+'/pins/'+pin+'/resolve',headers=self.guest,json={'revision':1,'resolved':True}).status_code,400)
  self.assertEqual(self.c.post(self.url+'/pins/'+pin+'/resolve',headers=self.owner,json={'revision':1,'resolved':True}).status_code,200)
  self.assertEqual(self.c.get(self.url,headers=self.guest).get_json()['pins'][0]['resolved'],1)
 def test_guest_cannot_list_create_or_rotate(self):
  self.assertEqual(self.c.get('/api/boards',headers=self.guest).status_code,400)
  self.assertEqual(self.c.post('/api/boards',headers=self.guest).status_code,400)
  self.assertEqual(self.c.post(self.url+'/rotate',headers=self.guest).status_code,400)
 def test_revocation_blocks_image_and_export(self):
  self.c.post(self.url+'/rotate',headers=self.owner)
  for path in [self.url,self.url+'/image',self.url+'/export']:self.assertEqual(self.c.get(path,headers=self.guest).status_code,400)
 def test_upload_body_limit(self):
  self.app.config['MAX_CONTENT_LENGTH']=100
  self.assertEqual(self.c.post('/api/boards',headers=self.owner,data={'title':'Big','image':(io.BytesIO(png()),'x.png')}).status_code,413)
 def test_export_and_image_headers(self):
  r=self.c.get(self.url+'/export',headers=self.guest);self.assertTrue(r.headers['Content-Disposition'].startswith('attachment'));self.assertEqual(r.headers['Cache-Control'],'no-store');self.assertNotIn('Access-Control-Allow-Origin',r.headers)
  self.assertEqual(self.c.get(self.url+'/image',headers=self.guest).mimetype,'image/png')
