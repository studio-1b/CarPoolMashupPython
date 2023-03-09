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

docker run -dp 80:8080 carpool-mashup
