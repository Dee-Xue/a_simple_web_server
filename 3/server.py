from http.server import BaseHTTPRequestHandler, HTTPServer
import os, sys

class RequestHandler(BaseHTTPRequestHandler):

    Error_Page = """\
        <html>
        <body>
        <h1>Error accessing {path}</h1>
        <p>{msg}</p>
        </body>
        </html>
        """

    def do_GET(self):
        try:

            full_path = os.getcwd() + self.path

            if not os.path.exists(full_path):
                raise Exception("'{0}' not found".format(self.path))

            elif os.path.isfile(full_path):
                self.handle_file(full_path)

            else:
                raise Exception("Unknown object '{0}'".format(self.path))

        except Exception as msg:
            self.handle_error(msg)

    def handle_file(self, full_path):
        try:
            with open(full_path, 'rb') as reader:
                content = reader.read()
            self.send_content(content)
        except IOError as msg:
            msg = "'{0}' cannot be read: {1}".format(self.path, msg)
            self.handle_error(msg)

    def handle_error(self, msg):
        content = self.Error_Page.format(path=self.path, msg=msg)
        self.send_content(content.encode('utf-8'), 404)

    def send_content(self, content, status = 200):
        self.send_response(status)
        self.send_header("Content-type", "text/html")
        self.send_header("Content-Length", str(len(content)))
        self.end_headers()
        self.wfile.write(content)

if __name__ == '__main__':
    ServerAddress = ('', 8000)
    server = HTTPServer(ServerAddress, RequestHandler)
    server.serve_forever()

