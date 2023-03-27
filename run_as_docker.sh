#!/bin/bash

if [ "$(whoami)" != "root" ]; then
   echo "This should be run as root.  Use sudo"
   echo "or run 'sudo usermod -aG docker $(whoami)'"
   exit
fi

#see if this image exists
docker 2>&1 > /dev/null
IS_DOCKER_MISSING=$?
if [ $IS_DOCKER_MISSING -ne 0 ]; then
    echo "please install docker"
    exit
fi

sudo docker image inspect carpool-mashup 2>&1 > /dev/null
IS_BUILD_MISSING=$?
if [ $IS_BUILD_MISSING -ne 0 ]; then
    echo "cannot find docker container.  Building..."
    ./build_docker.sh
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
echo "  by uncommenting the 'docker run' line in this script"


#docker run -itp 80:8080 -p 8022:8022 carpool-mashup-w-ssh
#press ^p^q to detach docker interactive console to carpool

# to attach to carpool console menu
#docker ps
#docker attach -it container-id

# to start container on reboot
#docker run  --restart unless-stopped -i -tdp 80:8080 -p 8022:8022 carpool-mashup-w-ssh   # restart on boot
#  -it for console
#  -d to detech console
#  -p container has port 8080, forward to port 80 on host
