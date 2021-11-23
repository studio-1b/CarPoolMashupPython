import os
import datetime
from request import HttpRequest

from debugging import debugging

class HttpResponse:
    HEADER_DATE_FMT="%a, %d %b %Y %H:%M:%S %Z"

    def _pairs2tuple(key, lst, separator="="):
        return HttpRequest._pairs2tuple(key, lst, separator)

    def _tuple2pairs(tple, lst, separator="="):
        HttpRequest._tuple2pairs(tple, lst, separator)

    def __init__(self, tcpout, request=None):
        serverip=""
        if not request==None:
            serverip=request.server.localAddress
        now = datetime.datetime.now()
        self.headerpairs = [ "Date: {}".format(now.strftime(HttpResponse.HEADER_DATE_FMT)),
                             "Server: {}".format(serverip) ]
        self._buffer = []
        self._headerssent = False
        self.httpversion = "HTTP/1.1"
        self.status = "200"
        self.message = "OK"
        self.tcpout = tcpout
        self._bufferin = 0

    def setStatus(self,status):
        if not self._headerssent:
            self.status = status
        else:
            raise ValueError("You are again ignoring the past.  Once the headers are sent, you can't change the status, unless starting over with new request.")

    def setNotFound404(self, message=None):
        self.setStatus(404)
        self.message = "Not Found"
        html = "<html><head><title>File not found</title></head><body><h1>File not found</h1></body></html>"
        if message!=None and len(message)!=0:
            html = message
        self.bufferWrite(html)
        self.send()

    def setInternalError500(self, message=None):
        self.setStatus(500)
        self.message = "Internal Error"
        html = "<html><head><title>Program crashed</title></head><body><h1>what you are seeing here is a euphemism that web servers tell you when a server has crashed</h1></body></html>"
        if message!=None and len(message)!=0:
            html = message
        self.bufferWrite(html)
        self.send()

    def setContentLength(self, length):
        HttpResponse._tuple2pairs(("Content-Length", str(length)), self.headerpairs, ": ")

    def setContentType(self, mimetype):
        HttpResponse._tuple2pairs(("Content-Type", mimetype), self.headerpairs, ": ")

    def setHeader(self, headername, value):
        HttpResponse._tuple2pairs((headername, value), self.headerpairs, ": ")

    def bufferWrite(self,text):
        buffer = text.encode()
        self._buffer.append(buffer) # UTF-8 is default, thank god
        self._bufferin += len(buffer)

        # "".encode(encoding=utf_8)
        # "".encode(encoding=utf_16)
        # "".encode(encoding=ascii)

    def send(self):
        if len(self._buffer)>0:
            if not self._headerssent:
                self.tcpout.sendall("{} {} {}\r\n".format(self.httpversion,self.status,self.message).encode()) # again, UTF-8 is default
                if debugging.web: print("Sending...")
                if debugging.web: print("{} {} {}".format(self.httpversion,self.status,self.message).encode())
                for item in self.headerpairs: # headers
                    self.tcpout.sendall(item.encode()) # again, UTF-8 is default
                    self.tcpout.sendall(b"\r\n")
                    if debugging.web: print(item.encode())
                self.tcpout.sendall(b"\r\n")
                if debugging.web: print()
                self._headerssent = True
            for item in self._buffer:
                self.tcpout.sendall(item)
                if debugging.web: print(item)
            self._buffer = []

    def stream(self, buffer):
        self._buffer.append(buffer)
        self.send()
        self._buffer = []
