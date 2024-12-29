#!/home/felddorf/www/cgi-bin/requestForm_api/venv/bin/python3

import cgitb
cgitb.enable()

from wsgiref.handlers import CGIHandler
from sys import path

# Flaskアプリのパスを追加
path.insert(0, '/felddorf/www/cgi-bin/requestForm_api')

try:
    from app import app
except ImportError as e:
    print("Content-Type: text/plain")
    print()
    print(f"Flaskアプリのインポートエラー: {e}")
    raise

class ProxyFix(object):
    def __init__(self, app):
        self.app = app

    def __call__(self, environ, start_response):
        # ※要書き換え
        environ['SERVER_NAME'] = "felddorf.sakura.ne.jp"
        environ['SERVER_PORT'] = "80"
        environ['REQUEST_METHOD'] = "GET"
        environ['SCRIPT_NAME'] = ""
        environ['PATH_INFO'] = "/"
        environ['QUERY_STRING'] = ""
        environ['SERVER_PROTOCOL'] = "HTTP/1.1"
        return self.app(environ, start_response)
    
if __name__ == '__main__':
   app.wsgi_app = ProxyFix(app.wsgi_app)
   CGIHandler().run(app)