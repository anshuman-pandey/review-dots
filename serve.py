"""Run the persistent WSGI service; configure HTTPS at a trusted reverse proxy."""
import os
from pathlib import Path
from waitress import serve
from server import create_app


def application():
    os.umask(0o077)
    data=Path(os.environ.get('REVIEW_DATA_DIR','./data'))
    data.mkdir(parents=True,exist_ok=True,mode=0o700)
    return create_app(str(data/'review.sqlite3'),os.environ.get('REVIEW_OWNER_KEY',''))

if __name__=='__main__':
    serve(application(),host=os.environ.get('REVIEW_BIND','127.0.0.1'),port=int(os.environ.get('PORT','8092')),
          threads=4,max_request_body_size=10*1024*1024+65536,expose_tracebacks=False)
