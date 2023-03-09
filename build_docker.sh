#!/bin/bash

if [ "$(whoami)" != "root" ]; then
   echo "This should be run as root.  Use sudo"
   echo "or run 'sudo usermod -aG docker $(whoami)'"
   exit
fi

# docker build has to be run in project root, bc of relative paths below
# Docker/dockerfile also has relative paths, 
#   from project root, which is the working dir "docker image build" is run
sudo docker image build -t carpool-mashup -f Docker/dockerfile .
