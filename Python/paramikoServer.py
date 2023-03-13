#!/usr/bin/env python

# Copyright (C) 2003-2007  Robey Pointer <robeypointer@gmail.com>
#
# This file is part of paramiko.
#
# Paramiko is free software; you can redistribute it and/or modify it under the
# terms of the GNU Lesser General Public License as published by the Free
# Software Foundation; either version 2.1 of the License, or (at your option)
# any later version.
#
# Paramiko is distributed in the hope that it will be useful, but WITHOUT ANY
# WARRANTY; without even the implied warranty of MERCHANTABILITY or FITNESS FOR
# A PARTICULAR PURPOSE.  See the GNU Lesser General Public License for more
# details.
#
# You should have received a copy of the GNU Lesser General Public License
# along with Paramiko; if not, write to the Free Software Foundation, Inc.,
# 51 Franklin Street, Fifth Floor, Boston, MA  02110-1301 USA.


# if need to build: https://github.com/paramiko/paramiko.git



import base64
from binascii import hexlify
import os
import socket
import sys
import threading
import traceback
import json
import threading

import paramiko  # https://stackoverflow.com/questions/71368098/creating-python-sshserver
from paramiko.py3compat import b, u, decodebytes
from collections import namedtuple
from paramikoIO import ParamikoIO





class ParamikoServer(paramiko.ServerInterface):

    def __init__(self):
        self.event = threading.Event()
        self.onconnect=self.connectHandler
        self.ongreet=None
        self.onclientready=None
        self.echoRecv=True
        self.isrunning=True

        # setup logging
        paramiko.util.log_to_file("demo_server.log")

        ENV_VAR_SSH_HOST_FILE="CARPOOL_SSHD_HOSTKEY_NAMENAME"
        TEST_KEY_FILENAME="test_rsa.key"
        ENV_VAR_NAME="CARPOOL_SSHD_HOST_PUB_KEY"
        if (ENV_VAR_SSH_HOST_FILE in os.environ) and (os.path.isfile(os.environ[ENV_VAR_SSH_HOST_FILE])):
            host_pub_key = paramiko.RSAKey(filename=os.environ[ENV_VAR_SSH_HOST_FILE])
            print("Read "+os.environ[ENV_VAR_SSH_HOST_FILE]+" key: " + u(hexlify(host_pub_key.get_fingerprint())))
        elif ENV_VAR_NAME in os.environ:
            host_pub_key = paramiko.RSAKey(data=os.environ[ENV_VAR_NAME])
            print("ENV key: " + u(hexlify(host_pub_key.get_fingerprint())))
        elif os.path.isfile(TEST_KEY_FILENAME):
            host_pub_key = paramiko.RSAKey(filename=TEST_KEY_FILENAME)
            print("Read test key: " + u(hexlify(host_pub_key.get_fingerprint())))
        else:
            # 'data' is the output of base64.b64encode(key)
            # (using the "user_rsa_key" files)
            data = (
                b"AAAAB3NzaC1yc2EAAAABIwAAAIEAyO4it3fHlmGZWJaGrfeHOVY7RWO3P9M7hp"
                b"fAu7jJ2d7eothvfeuoRFtJwhUmZDluRdFyhFY/hFAh76PJKGAusIqIQKlkJxMC"
                b"KDqIexkgHAfID/6mqvmnSJf0b5W8v5h2pI/stOSwTQ+pxVhwJ9ctYDhRSlF0iT"
                b"UWT10hcuO4Ks8="
            )
            host_pub_key = paramiko.RSAKey(data=decodebytes(data))
            print("default sshd host key")

        self.host_key = host_pub_key


    def check_channel_request(self, kind, chanid):
        if kind == "session":
            return paramiko.OPEN_SUCCEEDED
        return paramiko.OPEN_FAILED_ADMINISTRATIVELY_PROHIBITED

    def check_auth_password(self, username, password):
        if "CARPOOL_SSH_USER" in os.environ:
            dbjson=os.environ["CARPOOL_SSH_USER"]
        else:
            dbjson='{"jdoe":"foo"}'
        dict = json.loads(dbjson)
        if (username in dict) and (password == dict[username]):
            return paramiko.AUTH_SUCCESSFUL
        return paramiko.AUTH_FAILED

    def check_auth_publickey(self, username, key):
        print("Auth attempt with key: " + u(hexlify(key.get_fingerprint())))
        if (username == "robey") and (key == self.good_pub_key):
            return paramiko.AUTH_SUCCESSFUL
        return paramiko.AUTH_FAILED

    def check_auth_gssapi_with_mic(
        self, username, gss_authenticated=paramiko.AUTH_FAILED, cc_file=None
    ):
        """
        .. note::
            We are just checking in `AuthHandler` that the given user is a
            valid krb5 principal! We don't check if the krb5 principal is
            allowed to log in on the server, because there is no way to do that
            in python. So if you develop your own SSH server with paramiko for
            a certain platform like Linux, you should call ``krb5_kuserok()`` in
            your local kerberos library to make sure that the krb5_principal
            has an account on the server and is allowed to log in as a user.

        .. seealso::
            `krb5_kuserok() man page
            <http://www.unix.com/man-page/all/3/krb5_kuserok/>`_
        """
        if gss_authenticated == paramiko.AUTH_SUCCESSFUL:
            return paramiko.AUTH_SUCCESSFUL
        return paramiko.AUTH_FAILED

    def check_auth_gssapi_keyex(
        self, username, gss_authenticated=paramiko.AUTH_FAILED, cc_file=None
    ):
        if gss_authenticated == paramiko.AUTH_SUCCESSFUL:
            return paramiko.AUTH_SUCCESSFUL
        return paramiko.AUTH_FAILED

    def enable_auth_gssapi(self):
        return False

    def get_allowed_auths(self, username):
        return "password"

    def check_channel_shell_request(self, channel):
        self.event.set()
        return True

    def check_channel_pty_request(
        self, channel, term, width, height, pixelwidth, pixelheight, modes
    ):
        return True

    def start(self, bindaddress="127.0.0.1", port=22):
        if self.onclientready==None:
            raise paramiko.SSHException("Please supply handler for .clientready")

        print("Starting SSH Server on:",bindaddress)
        print("port:",port)

        # now connect
        try:
            sock = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
            sock.setsockopt(socket.SOL_SOCKET, socket.SO_REUSEADDR, 1)
            sock.bind((bindaddress, port))
            self.socket=sock
        except Exception as e:
            print("*** Bind failed: " + str(e))
            traceback.print_exc()
            return False

        # open thread, run loop in thread
        thr = threading.Thread(target=self.loop, args=(sock,), kwargs={})
        thr.start()

        return True


    def loop(self, sock):
        self.isrunning=True
        while self.isrunning:
            try:
                sock.listen(100)
                print("Listening for connection ...")
                # client, addr = sock.accept()
                client = sock.accept()
                if self.onconnect!=None:
                    self.onconnect(client)
            except Exception as e:
                print("*** Listen/accept failed: " + str(e))
                traceback.print_exc()
        if self.isrunning:
            self.isrunning=False
        print("Stopped listening for new connections ...")

    def connectHandler(self, e):
        client, addr = e
        print("Got a connection!")

        try:
            self.servername=socket.getfqdn("")
            print("Server is ", self.servername)
    
            # this module is necessary for the implementation below:
            #   pip install python-gssapi
    
            t = paramiko.Transport(client)
    
            # t.set_gss_host(socket.getfqdn(""))
            #try:
            #    t.load_server_moduli()
            #except:
            #    print("(Failed to load moduli -- gex will be unsupported.)")
            #    raise
    
            print("Host key: " + u(hexlify(self.host_key.get_fingerprint())))
            t.add_server_key(self.host_key)
    
            try:
                t.start_server(server=self)
            except paramiko.SSHException:
                print("*** SSH negotiation failed.")
                return False

            # wait for auth
            chan = t.accept(20)
            if chan is None:
                print("*** No channel.")
                return False

            print("Authenticated!")

            self.event.wait(10)
            if not self.event.is_set():
                print("*** Client never asked for a shell.")
                return False

            if self.ongreet!=None:
                Eargs1=namedtuple("Eargs1", "transport channel")
                e1=Eargs1(t,chan)
                self.ongreet(self,e1)

            Eargs2=namedtuple("Eargs2", "input output")
            io1=ParamikoIO(chan)
            io2=ParamikoIO(chan)
            e3=Eargs2(io1,io2)
            # open new thread for clientproxy
            thr = threading.Thread(target=self.onclientready, args=(self,e3,), kwargs={})
            thr.start()
            #self.onclientready(self,e3)
            return True

        except Exception as ex:
            print("*** Caught exception: " + str(ex.__class__) + ": " + str(ex))
            traceback.print_exc()
            try:
                t.close()
            except:
                pass

    def stop(self):
        self.onconnect=None
        self.isrunning=False


#courtesy of robey pointer
def sampleGreetHandler(server, e):
    t,chan = e
    chan.send("\r\n\r\n" + server.servername)
    chan.send("\r\n\r\nWelcome to my dorky little BBS!\r\n\r\n")
    chan.send(
        "We are on fire all the time!  Hooray!  Candy corn for everyone!\r\n"
    )
    chan.send("Happy birthday to Robot Dave!\r\n\r\n")


def sampleClientHandler(server,e):
    input,output = e
    chan = output.ch
 
    chan.send("Username: ")
    f = chan.makefile("rU")
    username = f.readline().strip("\r\n")
    chan.send("\r\nI don't like you, " + username + ".\r\n")

    chan.send("Type anything and result will be echoed back:\r\n")
    chan.send("Press ESC to exit\r\n")
    purpose=""
    while purpose!=b'\x1b':
        purpose = chan.recv(1024)
        print(purpose)
        if purpose == b"\r":
            chan.send("----\r\n")
        chan.send(purpose.decode())

    #f2 = chan.makefile("rU")
    #chan.send("how much: ")
    #amt = chan.recv(1024).strip("\r\n")
    #chan.send("\r\n" + amt + "isnt enough.\r\n")

    chan.send(" Bye Bye.\r\n")
    chan.close()

    print("client left")
