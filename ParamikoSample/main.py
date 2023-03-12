#!/usr/bin/env python

# Copyright (C) 2003-2007  Robey Pointer <robeypointer@gmail.com>
#
# This file is NOT part of paramiko.
#
# Paramiko is free software; you can redistribute it and/or modify it under the
# terms of the GNU Lesser General Public License as published by the Free
# Software Foundation; either version 2.1 of the License, or (at your option)
# any later version.
#
# this is only free software bc I can do nothing about the stupid cunts who
# keep stealing it without compensation.  And they fucking take the fun out
# of it, too.


import base64
from binascii import hexlify
import os
import socket
import sys
import threading
import traceback

import paramiko  # https://stackoverflow.com/questions/71368098/creating-python-sshserver
from paramiko.py3compat import b, u, decodebytes

from paramikoServer import ParamikoServer
from paramikoServer import sampleGreetHandler
from paramikoServer import sampleClientHandler



if __name__ == '__main__':
    try:
        sshd=ParamikoServer()
        sshd.ongreet=sampleGreetHandler
        sshd.onclientready=sampleClientHandler
        sshd.start("127.0.0.1",8022)
    except Exception as e:
        print("*** Caught exception: " + str(e.__class__) + ": " + str(e))
        traceback.print_exc()
        try:
            t.close()
        except:
            pass
        sys.exit(1)
