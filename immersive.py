#!/usr/bin/env python3
# -*- coding: utf-8 -*-

from http.server import BaseHTTPRequestHandler, HTTPServer
from multiprocessing import Process, Value, Array
from lpd8806 import LPD8806
import RPi.GPIO as GPIO ,time

HOST_NAME = '0.0.0.0' #bind to all
PORT_NUMBER = 8000
NLEDS = 32

lpd = LPD8806(NLEDS)

red = []
blank = []
for i in range(0,NLEDS):
    red.append([255,0,0])
    blank.append([0,0,0])

shared = Value("i", 0)

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
            time.sleep(0.1)
            lpd.setPixels(blank,"rgb")
        
        self.send_response(200)
        self.send_header("Access-Control-Allow-Origin", "*")
        self.send_header("Content-type", "application/json")
        self.end_headers()
        self.wfile.write( bytes('{"brightness":"%i"}' % (shared.value), "utf8") )
        

class rctimerHandler:

    def __init__(self,pin):
        self.flag = Value("i", 1)
        self.shared = shared
        self.p = Process(target=rctimer, args=(pin,self.flag,self.shared))
        self.p.start()

    def stop(self):
        self.flag.value = 0
        self.p.join() # wait for process exit

def rctimer(pin,flag,shared):
    GPIO.setmode(GPIO.BCM)
    while flag.value == 1:
        reading = 0
        GPIO.setup(pin, GPIO.OUT)
        GPIO.output(pin, GPIO.LOW)
        time.sleep(0.1)
 
        GPIO.setup(pin, GPIO.IN)
        # This takes about 1 millisecond per loop cycle
        while (GPIO.input(pin) == GPIO.LOW):
                reading += 1
        shared.value = reading


    print("cleaning up GPIO")
    GPIO.cleanup()


if __name__ == '__main__':

    rc = rctimerHandler(18)
    httpd = HTTPServer((HOST_NAME, PORT_NUMBER), httpHandler)
    print("Server started at %s:%s" % (HOST_NAME, PORT_NUMBER))
    try:
        httpd.serve_forever()
    except KeyboardInterrupt:
        pass
    httpd.server_close()
    rc.stop()
