from http.server import BaseHTTPRequestHandler, HTTPServer
import os, sys, subprocess

#------------------------------------------------------------------------------------

class base_case(object):

    def handle_file(self, handler,full_path):
        try:
            with open(full_path, 'rb') as reader:
                content = reader.read()
            handler.send_content(content)
        except IOError as msg:
            msg = "'{0}' cannot be read: {1}".format(self.path, msg)
            handler.handle_error(msg)
            
    def index_path(self, handler):
        return os.path.join(handler.full_path, 'index.html')
        
    def test(self, handler):
        assert False, 'Not implemented.'
        
    def act(self, handler):
        assert False, 'Not implemented.'
        
#------------------------------------------------------------------------------------        
        
class case_no_file(base_case):
    def test(self, handler):
        return not os.path.exists(handler.full_path)
        
    def act(self, handler):
        raise Exception("'{0}' not found".format(handler.full_path))

#------------------------------------------------------------------------------------

class case_cgi_file(base_case):

    def run_cgi(self, handler):
        data = subprocess.check_output(['python3', handler.full_path])
        handler.send_content(data)
        
    def test(self, handler):
        return os.path.isfile(handler.full_path) and \
               handler.full_path.endswith('.py')
               
    def act(self, handler):
        self.run_cgi(handler)

#------------------------------------------------------------------------------------

class case_is_file(base_case):

    def test(self, handler):
        return os.path.isfile(handler.full_path)
        
    def act(self, handler):
        self.handle_file(handler, handler.full_path)
        
#------------------------------------------------------------------------------------
        
class case_directory_index_file(base_case):

    def test(self, handler):
        return os.path.isdir(handler.full_path) and \
            os.path.isfile(self.index_path(handler))
               
    def act(self, handler):
        self.handle_file(handler, self.index_path(handler))
        
#------------------------------------------------------------------------------------
        
class case_directory_no_index_file(base_case):

    Listing_page = """\
        <html>
        <body>
        <ul>
        {0}
        </ul>
        </body>
        </html>
        """

    def list_dir(self, handler, full_path):
        try:
            entries = os.listdir(full_path)
            bullets = ['<li>{0}</li>'.format(e)
                for e in entries]
            page = self.Listing_page.format('\n'.join(bullets))
            handler.send_content(page.encode('utf-8'))
        except OSError as msg:
            msg = "'{0}' can not be listed".format(full_path)
            handler.handle_error(msg)

    def test(self, handler):
        return os.path.isdir(handler.full_path) and \
               not os.path.isfile(self.index_path(handler))
               
    def act(self, handler):
        self.list_dir(handler, handler.full_path)
        
#------------------------------------------------------------------------------------
             
class case_always_fail(base_case):

    def test(self, handler):
        return True
        
    def act(self, handler):
        raise Exception("Unknown object '{0}'".format(handler.path))
       
#------------------------------------------------------------------------------------

class RequestHandler(BaseHTTPRequestHandler):

    Error_Page = """\
        <html>
        <body>
        <h1>Error accessing {path}</h1>
        <p>{msg}</p>
        </body>
        </html>
        """
        
    Cases = [case_no_file(),
             case_cgi_file(),
             case_is_file(),
             case_directory_index_file(),
             case_directory_no_index_file(),
             case_always_fail()]

    def do_GET(self):
        try:
            self.full_path = os.getcwd() + self.path
            
            for case in self.Cases:
                handler = case
                if handler.test(self):
                    handler.act(self)
                    break
                    
        except Exception as msg:
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
        
#------------------------------------------------------------------------------------

if __name__ == '__main__':
    ServerAddress = ('', 8000)
    server = HTTPServer(ServerAddress, RequestHandler)
    server.serve_forever()

