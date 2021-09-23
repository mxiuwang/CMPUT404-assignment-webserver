#  coding: utf-8 
import socketserver
import os

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

'''Deep/test
assume it's a file (or check if it's a directory)
If it's a directory, return 301 Moved Permenantly, and add "/" so it goes it /index.html
'''

MSG_200 = "200 OK"
MSG_301 = "301 Moved Permanently"
MSG_404 = "404 Not Found"
MSG_405 = "405 Method Not Allowed"

class MyWebServer(socketserver.BaseRequestHandler):
    
    def handle(self):
        self.data = self.request.recv(1024).strip()
        print ("Got a request of: %s\n" % self.data)
        
        all_data_list = self.data.decode("utf-8").split('\r\n')
        http_request = all_data_list[0]
        print("http_request",http_request) # http_request = GET /index.html HTTP/1.1
        
        # get info from http_request 
        http_request_list = http_request.split(" ")
        http_method = http_request_list[0]
        requestURL = http_request_list[1]
        httpVer = http_request_list[2]

        # if it's a folder, go to index.html in that folder 
        if requestURL[-1] == '/':
            requestURL += "index.html"
        print("requestURL1",requestURL) # /index.html
        print("httpVer",httpVer) # HTTP/1.1

        # requirement 14
        if http_method != "GET": # or if "POST" in http_request and "PUT" in http_request and "DELETE" in http_request:
            self.request.sendall(str.encode('HTTP/1.1 '+MSG_405))
            print("Method Not Allowed")
            return 
        
        # Requirement 1 
        # cite: https://stackoverflow.com/questions/3430372/how-do-i-get-the-full-path-of-the-current-files-directory
        pyPath = os.path.abspath(os.getcwd()) + "/www" # /Users/michellewang/Desktop/School/Cmput_404/assginment1/www
        print("os.get.cwd()",os.path.abspath(os.getcwd())+"/www")

        requestURL = os.path.normpath(requestURL)
        print("requestURL2",requestURL) # /index.html
        if requestURL[0] in ['\\', '/']:
            requestURL = requestURL[1:]
        print("requestURL3",requestURL) # index.html

        requestPath = os.path.join(pyPath, requestURL)
        print("requestPath", requestPath) # /Users/michellewang/Desktop/School/Cmput_404/assginment1/www/index.html

        responseCode = MSG_200
        # check if path is a directory 
        is_directory = str(os.path.isdir(requestPath))
        if is_directory=="True" and requestPath[-1]!="/":
            requestPath += "/index.html"
            responseCode = MSG_301

        # check if filepath exists
        if os.path.exists(requestPath) is False:
            responseCode = MSG_404
            self.request.sendall(str.encode('HTTP/1.1 '+responseCode))
            print("404 Path not found:", requestPath) # requestPath = /Users/michellewang/Desktop/School/Cmput_404/assginment1/www/do-not-implement-this-page-it-is-not-found
            return 
        # assume path is a file 
        requestPath = os.path.normpath(requestPath)
        print("requestPath normalized", requestPath)

        # if file exists, find file extension 
        extension = os.path.splitext(requestPath)[1]
        print("ext",extension)

        with open(requestPath, 'rb') as f:
            fileBuf = f.read()
        
        # Requirements 5, 6: display the right MIME content type 
        content_type = 'application/octet-stream'
        if '.html' in extension:
            content_type = 'text/html'
        elif '.css' in extension:
            content_type = 'text/css'

        print("content_type",content_type)
        response = httpVer + ' {}\r\n'.format(responseCode) # httpVer = HTTP/1.1, responseCode = "200 OK"
        print("response1",response)
        response += 'Cache-Control: no-cache\r\n'
        response += 'Content-Type: {}; charset=utf-8\r\n'.format(content_type)
        response += 'Content-Length: {}\r\n'.format(len(fileBuf))
        response += 'Connection: close\r\n'
        response += '\r\n'
        response += fileBuf.decode("utf-8")

        print("total response",response)

        self.request.sendall(str.encode(response, "utf-8"))

if __name__ == "__main__":
    HOST, PORT = "localhost", 8080

    socketserver.TCPServer.allow_reuse_address = True
    # Create the server, binding to localhost on port 8080
    server = socketserver.TCPServer((HOST, PORT), MyWebServer)

    # Activate the server; this will keep running until you
    # interrupt the program with Ctrl-C
    server.serve_forever()
