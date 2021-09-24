#  coding: utf-8 
import socketserver
import os

# Copyright 2013 Abram Hindle, Eddie Antonio Santos, Michelle Wang (ccid: mxwang)
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
        destination_og = http_request_list[1]
        http_ver = http_request_list[2]

        # if it's a folder, go to index.html in that folder 
        if destination_og[-1] == '/':
            destination_og += "index.html"
        print("destination_og1",destination_og) # /index.html
        print("http_ver",http_ver) # HTTP/1.1

        # requirement 14
        if http_method != "GET": # or if "POST" in http_request and "PUT" in http_request and "DELETE" in http_request:
            self.request.sendall(str.encode('HTTP/1.1 '+MSG_405))
            print("Method Not Allowed")
            return 
        
        # Requirement 1 
        # cite: https://stackoverflow.com/questions/3430372/how-do-i-get-the-full-path-of-the-current-files-directory
        abs_path = os.path.abspath(os.getcwd()) + "/www" # /Users/michellewang/Desktop/School/Cmput_404/assginment1/www
        print("os.get.cwd()",os.path.abspath(os.getcwd())+"/www")

        destination_og = os.path.normpath(destination_og) # normalize path to remove/convert extra ..//\\ etc.
        print("destination_og2",destination_og) # /index.html
        if destination_og[0] in ['\\', '/']:
            destination_og = destination_og[1:]
        print("destination_og3",destination_og) # index.html

        dest_path = os.path.join(abs_path, destination_og)
        print("dest_path", dest_path) # /Users/michellewang/Desktop/School/Cmput_404/assginment1/www/index.html

        status_code = MSG_200
        # check if filepath exists
        if os.path.exists(dest_path) is False:
            status_code = MSG_404
            self.request.sendall(str.encode('HTTP/1.1 '+status_code))
            print("404 Path not found:", dest_path) # dest_path = /Users/michellewang/Desktop/School/Cmput_404/assginment1/www/do-not-implement-this-page-it-is-not-found
            return 

        # check if path is a directory 
        is_directory = str(os.path.isdir(dest_path))
        if is_directory=="True" and dest_path[-1]!="/":
            dest_path += "/index.html"
            status_code = MSG_301
        print("status_code",status_code)

        # if file exists, find file extension 
        # cite: https://stackoverflow.com/questions/541390/extracting-extension-from-filename-in-python
        extension = os.path.splitext(dest_path)[1]
        print("ext",extension)

        # read file 
        f=open(dest_path,"rb")
        fileBuf = f.read()
        file_len = len(fileBuf)
        f.close()
        
        # Requirements 5, 6: display file in correct MIME content type 
        content_type = 'application/octet-stream'
        if '.html' in extension:
            content_type = 'text/html'
        elif '.css' in extension:
            content_type = 'text/css'

        print("content_type",content_type)
        response = http_ver + ' {}\r\n'.format(status_code) # http_ver = HTTP/1.1, status_code = "200 OK"
        print("response1",response)
        if status_code == MSG_301:
            response += "Location: " + "http://127.0.0.1:8080/" + destination_og + "\r\n"
        response += 'Content-Type: ' + content_type + '; charset=utf-8\r\n'
        response += 'Content-Length: {}\r\n'.format(file_len)
        response += 'Connection: close\r\n\r\n'
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
