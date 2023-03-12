#!/usr/bin/env python
from io import StringIO
import paramiko  # https://stackoverflow.com/questions/71368098/creating-python-sshserver


class ParamikoIO(StringIO):
    def __init__(self, channel):
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
        return self.ch.recv(bufferSize)
    def write(self,text):
        self.ch.send(text)
    def close(self):
        self.ch.close()




if __name__ == '__main__':
    print("no unit tests defined for this object")
