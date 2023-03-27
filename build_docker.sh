#!/bin/bash

if [ "$(whoami)" != "root" ]; then
   echo "This should be run as root.  Use sudo"
   echo "or run 'sudo usermod -aG docker $(whoami)'"
   exit
fi

echo "This project requires a paramiko library in python to simulate SSH server"
echo "This library does not run as intended in Docker container"
echo "Specifically, your client to handle a incoming connection, will need"
echo "  to call Transport.accept(timeout in sec),"
echo "  which should return a channel object, which according to source code"
echo "  the server should set by calling _queue_incoming_channel in 1 of 3 methods"
echo "    request_port_forward, _set_forward_agent_handler, _set_x11_handler"
echo "which it doesnt in a docker container"
echo "if you wish to try, feel free to try building the image"
echo "  by uncommenting the last line in this script"

# docker build has to be run in project root, bc of relative paths below
# Docker/dockerfile also has relative paths, 
#   from project root, which is the working dir "docker image build" is run
#sudo docker image build -t carpool-mashup-w-ssh -f Docker/dockerfile .
