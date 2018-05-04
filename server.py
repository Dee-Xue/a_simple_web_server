from http.server import BaseHTTPRequestHandler, HTTPServer

class RequestHandler(BaseHTTPRequestHandler):

    Page = '''\
<html>
<body>
<p> Hello World! </p>
</body>
</html>
'''

    def do_GET(self):
        self.send_response(200)
        self.send_header("Content-type", "text/html")
        self.send_header("Content-Length", str(len(self.Page)))
        self.end_headers()
        self.wfile.write(self.Page.encode('utf-8'))

if __name__ == '__main__':
    ServerAddress = ('', 8000)
    server = HTTPServer(ServerAddress, RequestHandler)
    server.serve_forever()

