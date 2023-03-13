#!/usr/bin/env python
import sys
from io import StringIO
import paramiko  # https://stackoverflow.com/questions/71368098/creating-python-sshserver


class ParamikoIO(StringIO):
    def __init__(self, channel):
        StringIO.__init__(self)
        self.ch = channel
        self.bufferSize = 1024
    def isatty(self):
        return True
    def readable(self):
        return True
    def writable(self):
        return True
    def seekable(self):
        return False
    def closed(self):
        return False
    def read(self):
        #sys.stderr.write("read()")
        txt=self.ch.recv(self.bufferSize)
        print(txt.decode())
        return txt
    def readline(self):
        #sys.stderr.write("readline()")
        list=[]
        ch=self.read()
        while ch!=b"\n" and ch!=b"\r":
            #sys.stderr.write(ch.decode())
            list.append(ch.decode())
            ch=self.read()
        line=''.join(list)
        if line=="":
            return "\n"
        else:
            return line
    def write(self,text):
        #sys.stderr.write("write()")
        if text == b"\r":
            self.ch.send("\r\n")
        elif "\r" in text:
            self.ch.send(text.replace("\r","\r\n"))
        elif "\n" in text:
            self.ch.send(text.replace("\n","\r\n"))
        else:
            self.ch.send(text)
    def close(self):
        self.ch.close()




if __name__ == '__main__':
    print("no unit tests defined for this object")
