#!/usr/bin/env python

# to support: from paramiko.py3compat import *
# copied from /usr/lib/python3/dist-packages/paramiko/py3compat.py
import base64
import sys
import time

decodebytes = base64.decodebytes
encodebytes = base64.encodebytes

def b(s, encoding="utf8"):
    """cast unicode or bytes to bytes"""
    if isinstance(s, bytes):
        return s
    elif isinstance(s, str):
        return s.encode(encoding)
    else:
        raise TypeError("Expected unicode or bytes, got {!r}".format(s))

def u(s, encoding="utf8"):
    """cast bytes or unicode to unicode"""
    if isinstance(s, bytes):
        return s.decode(encoding)
    elif isinstance(s, str):
        return s
    else:
        raise TypeError("Expected unicode or bytes, got {!r}".format(s))
