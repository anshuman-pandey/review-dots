"""Immutable image review boards. Callers authenticate owner operations."""
import hashlib,hmac,io,json,math,secrets,sqlite3,warnings
from datetime import datetime,timezone
from PIL import Image,ImageOps
MAX_BYTES=10*1024*1024
MAX_PIXELS=16_000_000
class Invalid(ValueError):pass

def text(value,limit):
    if not isinstance(value,str) or not value.strip() or len(value)>limit or '\x00' in value:raise Invalid('Text is missing or too long.')
    return value.strip()

def image_bytes(raw):
    if type(raw) is not bytes or not 1<=len(raw)<=MAX_BYTES:raise Invalid('Choose a PNG or JPEG no larger than 10 MiB.')
    try:
        with warnings.catch_warnings():
            warnings.simplefilter('error',Image.DecompressionBombWarning)
            with Image.open(io.BytesIO(raw)) as source:
                if source.format not in ('PNG','JPEG') or source.width*source.height>MAX_PIXELS or getattr(source,'n_frames',1)!=1:raise Invalid('Use a single PNG or JPEG up to 16 megapixels.')
                source.load();img=ImageOps.exif_transpose(source).convert('RGBA');clean=Image.new('RGBA',img.size);clean.paste(img);out=io.BytesIO();clean.save(out,format='PNG');data=out.getvalue()
                if len(data)>MAX_BYTES:raise Invalid('Decoded PNG exceeds 10 MiB. Resize the image.')
                return data,clean.width,clean.height
    except Invalid:raise
    except (OSError,ValueError,Image.DecompressionBombError,Image.DecompressionBombWarning):raise Invalid('This image cannot be decoded.')

def stamp():return datetime.now(timezone.utc).isoformat()
def digest(token):return hashlib.sha256(token.encode()).hexdigest()

class Reviews:
    def __init__(self,path):
        self.db=sqlite3.connect(path,timeout=5);self.db.row_factory=sqlite3.Row;self.db.execute('PRAGMA foreign_keys=ON')
        self.db.executescript('''CREATE TABLE IF NOT EXISTS boards(id TEXT PRIMARY KEY,title TEXT,token_hash TEXT,image BLOB,width INTEGER,height INTEGER,created_at TEXT);
        CREATE TABLE IF NOT EXISTS pins(id TEXT PRIMARY KEY,board TEXT REFERENCES boards(id),x REAL,y REAL,author TEXT,body TEXT,resolved INTEGER DEFAULT 0,revision INTEGER DEFAULT 1,created_at TEXT);
        CREATE TABLE IF NOT EXISTS events(pin TEXT REFERENCES pins(id),revision INTEGER,resolved INTEGER,created_at TEXT);''')
    def close(self):self.db.close()
    def create(self,title,raw):
        title=text(title,200);data,width,height=image_bytes(raw);key=secrets.token_urlsafe(16);token=secrets.token_urlsafe(32)
        with self.db:self.db.execute('INSERT INTO boards VALUES(?,?,?,?,?,?,?)',(key,title,digest(token),data,width,height,stamp()))
        return key,token
    def auth(self,key,token):
        row=self.db.execute('SELECT token_hash FROM boards WHERE id=?',(key,)).fetchone()
        if row is None or not isinstance(token,str) or not hmac.compare_digest(row[0],digest(token)):raise Invalid('Board access denied.')
    def view(self,key):
        row=self.db.execute('SELECT id,title,width,height,created_at FROM boards WHERE id=?',(key,)).fetchone()
        if row is None:raise Invalid('Board not found.')
        result=dict(row);result['pins']=[dict(r) for r in self.db.execute('SELECT * FROM pins WHERE board=? ORDER BY rowid',(key,))];return result
    def image(self,key):
        row=self.db.execute('SELECT image FROM boards WHERE id=?',(key,)).fetchone()
        if row is None:raise Invalid('Board not found.')
        return row[0]
    def add(self,key,x,y,author,body):
        for value in (x,y):
            if type(value) not in (int,float) or not math.isfinite(value) or not 0<=value<=1:raise Invalid('Pin coordinates must be within the image.')
        author=text(author,80);body=text(body,4000);pin=secrets.token_urlsafe(16)
        with self.db:
            self.db.execute('BEGIN IMMEDIATE');self.view(key)
            if self.db.execute('SELECT count(*) FROM pins WHERE board=?',(key,)).fetchone()[0]>=1000:raise Invalid('This board has reached 1000 comments.')
            self.db.execute('INSERT INTO pins(id,board,x,y,author,body,created_at) VALUES(?,?,?,?,?,?,?)',(pin,key,x,y,author,body,stamp()))
        return pin
    def resolve(self,key,pin,expected,resolved):
        if type(expected) is not int or expected<1 or type(resolved) is not bool:raise Invalid('Invalid resolution request.')
        with self.db:
            self.db.execute('BEGIN IMMEDIATE')
            row=self.db.execute('SELECT revision FROM pins WHERE id=? AND board=?',(pin,key)).fetchone()
            if row is None or row[0]!=expected:raise Invalid('Comment changed. Reload before resolving.')
            self.db.execute('UPDATE pins SET resolved=?,revision=revision+1 WHERE id=?',(int(resolved),pin))
            self.db.execute('INSERT INTO events VALUES(?,?,?,?)',(pin,expected+1,int(resolved),stamp()))
    def rotate(self,key):
        token=secrets.token_urlsafe(32)
        with self.db:
            if not self.db.execute('UPDATE boards SET token_hash=? WHERE id=?',(digest(token),key)).rowcount:raise Invalid('Board not found.')
        return token
    def export(self,key):
        result=self.view(key);result['image_sha256']=hashlib.sha256(self.image(key)).hexdigest()
        for p in result['pins']:p['events']=[dict(r) for r in self.db.execute('SELECT revision,resolved,created_at FROM events WHERE pin=? ORDER BY revision',(p['id'],))]
        return json.dumps(result,ensure_ascii=False,indent=2)
