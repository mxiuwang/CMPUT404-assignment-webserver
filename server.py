#  coding: utf-8 
import socketserver
import os
from urllib import request

# Copyright 2013 Abram Hindle, Eddie Antonio Santos
# 
# Licensed under the Apache License, Version 2.0 (the "License");
# you may not use this file except in compliance with the License.
# You may obtain a copy of the License at
# 
#     http://www.apache.org/licenses/LICENSE-2.0
# 
# Unless required by applicable law or agreed to in writing, software
# distributed under the License is distributed on an "AS IS" BASIS,
# WITHOUT WARRANTIES OR CONDITIONS OF ANY KIND, either express or implied.
# See the License for the specific language governing permissions and
# limitations under the License.
#
#
# Furthermore it is derived from the Python documentation examples thus
# some of the code is Copyright © 2001-2013 Python Software
# Foundation; All Rights Reserved
#
# http://docs.python.org/2/library/socketserver.html
#
# run: python freetests.py

# try: curl -v -X GET http://127.0.0.1:8080/


class MyWebServer(socketserver.BaseRequestHandler):
    
    def handle(self):
        self.data = self.request.recv(1024).strip()
        print ("Got a request of: %s\n" % self.data)

        # should this be here or at the end?
        self.request.sendall(bytearray("OK",'utf-8')) 
        
        all_data_list = self.data.decode("utf-8").split('\r\n')
        http_request = all_data_list[0]
        print(http_request)

        # requirement 14
        if "GET" not in http_request: # or if "POST" in http_request and "PUT" in http_request and "DELETE" in http_request:
            self.request.sendall('405 Method Not Allowed')
            print("Method Not Allowed")
            return 
        
        _, requestURL, httpVer = map(lambda x: x.strip(), http_request.split(' '))
        print("requestURL",requestURL) # /index.html
        print("httpVer",httpVer) # HTTP/1.1
        
        # Requirement 1 
        pyPath = os.path.dirname(os.path.realpath(__file__)) + "/www" # __file__ = server.py 
        print("pyPath",pyPath, type(pyPath)) # /Users/michellewang/Desktop/School/Cmput_404/assginment1/www

        requestURL = os.path.normpath(requestURL)
        print("requestURL",requestURL)
        if requestURL[0] in ['\\', '/']:
            requestURL = requestURL[1:]

        requestPath = os.path.join(pyPath, requestURL)
        print("requestPath", requestPath) # /Users/michellewang/Desktop/School/Cmput_404/assginment1/www/index.html

        responseCode = '200 OK'

        requestPath = os.path.normpath(requestPath)

        with open(requestPath, 'rb') as f:
            fileBuf = f.read()
        
        # Requirements 5, 6: display the right MIME content type 
        ext = os.path.splitext(requestPath)[1]
        print("ext",ext)
        content_type = 'application/octet-stream'
        if ext == '.html':
            content_type = 'text/html'
        elif ext == '.css':
            content_type = 'text/css'

        print("content_type",content_type)
        response = httpVer + ' {}\r\n'.format(responseCode) # httpVer = HTTP/1.1, responseCode = "200 OK"
        print("response1",response)
        response += 'Cache-Control: no-cache\r\n'
        response += 'Content-Type: {0}; charset=utf-8\r\n'.format(content_type)
        response += 'Content-Length: {0}\r\n'.format(len(fileBuf))
        response += 'Connection: close\r\n'
        response += '\r\n\r\n'
        response += fileBuf.decode("utf-8")

        print("total response",response)

        self.request.sendall(str.encode(response))

if __name__ == "__main__":
    HOST, PORT = "localhost", 8080

    socketserver.TCPServer.allow_reuse_address = True
    # Create the server, binding to localhost on port 8080
    server = socketserver.TCPServer((HOST, PORT), MyWebServer)

    # Activate the server; this will keep running until you
    # interrupt the program with Ctrl-C
    server.serve_forever()
