#!/usr/bin/env python3
# -*- coding: utf-8 -*-

from http.server import BaseHTTPRequestHandler, HTTPServer
from multiprocessing import Process, Value, Array
from lpd8806 import LPD8806

HOST_NAME = '0.0.0.0' #bind to all
PORT_NUMBER = 8000
NLEDS = 32

lpd = LPD8806(NLEDS)

red = []
for i in range(0,NLEDS):
    red.append([255,0,0])

class httpHandler(BaseHTTPRequestHandler):

    def do_GET(self):
        split = self.path.split("/")
        split.pop(0) #remove first '/'
        cmd = split.pop(0)

        if cmd == "pixels":
            if len(split) > NLEDS:
                raise Exception("Received color list too long (%i)" % ( len(split) ))

            lpd.setPixels(split,"hex")
            
        elif cmd == "hurt":
            lpd.setPixels(red,"rgb")
        elif cmd == "brightness":
            #analog
            pass
        
        self.send_response(200)
        self.send_header("Access-Control-Allow-Origin", "*")
        self.send_header("Content-type", "application/json")
        self.end_headers()
        self.wfile.write( bytes('{"path":"%s"}' % (self.path), "utf8") )
        

if __name__ == '__main__':

    httpd = HTTPServer((HOST_NAME, PORT_NUMBER), httpHandler)
    print("Server started at %s:%s" % (HOST_NAME, PORT_NUMBER))
    try:
        httpd.serve_forever()
    except KeyboardInterrupt:
        pass
    httpd.server_close()
