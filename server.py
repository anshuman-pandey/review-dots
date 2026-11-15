import io,os,hmac
from flask import Flask,g,request,jsonify,send_file
from werkzeug.exceptions import HTTPException
from reviews import Reviews,Invalid,MAX_BYTES

def create_app(path,owner_key):
    if not isinstance(owner_key,str) or not owner_key.isascii() or len(owner_key)<32:raise ValueError('Set REVIEW_OWNER_KEY to at least 32 random ASCII characters.')
    app=Flask(__name__);app.config.update(MAX_CONTENT_LENGTH=MAX_BYTES+65536,MAX_FORM_MEMORY_SIZE=65536,MAX_FORM_PARTS=4)
    def db():
        if 'db' not in g:g.db=Reviews(path)
        return g.db
    def token():
        value=request.headers.get('Authorization','')
        return value[7:] if value.startswith('Bearer ') else ''
    def owner():
        if not hmac.compare_digest(token().encode(),owner_key.encode()):raise Invalid('Owner access denied.')
    def access(key):
        if not hmac.compare_digest(token().encode(),owner_key.encode()):db().auth(key,token())
    def data():
        b=request.get_json()
        if not isinstance(b,dict):raise Invalid('Expected a JSON object.')
        return b
    @app.teardown_appcontext
    def close(error):
        store=g.pop('db',None)
        if store:store.close()
    @app.after_request
    def headers(r):
        r.headers.update({'Cache-Control':'no-store','X-Content-Type-Options':'nosniff','Referrer-Policy':'no-referrer','Content-Security-Policy':"default-src 'none'; img-src 'self' blob:; script-src 'self'; style-src 'self'; connect-src 'self'; base-uri 'none'; frame-ancestors 'none'; form-action 'self'"});return r
    @app.errorhandler(Invalid)
    def invalid(e):return jsonify(error=str(e)),400
    @app.errorhandler(HTTPException)
    def http_error(e):return jsonify(error=e.description),e.code
    @app.get('/')
    def home():return app.send_static_file('index.html')
    @app.get('/api/boards')
    def listing():owner();return jsonify([dict(r) for r in db().db.execute('SELECT id,title FROM boards ORDER BY rowid DESC')])
    @app.post('/api/boards')
    def create():
        owner();file=request.files.get('image')
        if file is None:raise Invalid('Choose an image.')
        key,secret=db().create(request.form.get('title'),file.stream.read(MAX_BYTES+1));return jsonify(id=key,token=secret),201
    @app.get('/api/boards/<key>')
    def board(key):access(key);return jsonify(db().view(key))
    @app.get('/api/boards/<key>/image')
    def image(key):access(key);return send_file(io.BytesIO(db().image(key)),mimetype='image/png',download_name='review.png')
    @app.post('/api/boards/<key>/pins')
    def pin(key):
        access(key);b=data();return jsonify(id=db().add(key,b.get('x'),b.get('y'),b.get('author'),b.get('body'))),201
    @app.post('/api/boards/<key>/pins/<pin>/resolve')
    def resolve(key,pin):owner();b=data();db().resolve(key,pin,b.get('revision'),b.get('resolved'));return jsonify(ok=True)
    @app.post('/api/boards/<key>/rotate')
    def rotate(key):owner();return jsonify(token=db().rotate(key))
    @app.get('/api/boards/<key>/export')
    def export(key):access(key);return send_file(io.BytesIO(db().export(key).encode()),mimetype='application/json',as_attachment=True,download_name='review.json')
    return app

if __name__=='__main__':
    os.umask(0o077)
    create_app(os.environ.get('REVIEW_DATABASE','review.sqlite3'),os.environ.get('REVIEW_OWNER_KEY','')).run(host='127.0.0.1',port=8092)
