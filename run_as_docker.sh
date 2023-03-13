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

docker run -itp 80:8080 carpool-mashup
#press ^p^q to detach docker interactive console to carpool

# to attach to carpool console menu
#docker ps
#docker attach -it container-id

# to start container on reboot
#docker run  --restart unless-stopped -i -tdp 80:8080 carpool-mashup   # restart on boot
#  -it for console
#  -d to detech console
#  -p container has port 8080, forward to port 80 on host
