#!/bin/bash

if [ "$(whoami)" != "root" ]; then
   echo "This should be run as root.  Use sudo -E"
   echo "or run 'sudo usermod -aG docker $(whoami)'"
   exit
fi


grep "ENV GOOGLE_MAP_JS_API_KEY -" Docker/dockerfile > /dev/null
if [ $? -eq 0 ]; then
   if [ "$GOOGLE_MAP_JS_API_KEY" != "" ]; then
      echo found the environment variable GOOGLE_MAP_JS_API_KEY
   else
      echo You have no Google API Key defined.  Get them from: 
      echo https://developers.google.com/maps/documentation/javascript/get-api-key
      echo https://console.cloud.google.com/google/maps-apis/credentials
      echo if you need new keys, see \"CLI testdata script.txt\"
      echo for which 4x API needs to be assigned to the key.
      echo "if you have the key, enter it now(empty to abort):"
      read GOOGLE_MAP_JS_API_KEY
   fi
   if [ "$GOOGLE_MAP_JS_API_KEY" == "" ]; then
      echo No API key, aborting Docker build
      exit
   else
      echo Applying GOOGLE_MAP_JS_API_KEY to dockerfile
      sed -i "s/ENV GOOGLE_MAP_JS_API_KEY -/ENV GOOGLE_MAP_JS_API_KEY ${GOOGLE_MAP_JS_API_KEY}/g" Docker/dockerfile
      sleep 1
   fi
fi

grep "GOOGLE_GEOCODE_API_KEY -" Docker/dockerfile > /dev/null
if [ $? -eq 0 ]; then
   if [ "$GOOGLE_GEOCODE_API_KEY" != "" ]; then
      echo found the environment variable GOOGLE_GEOCODE_API_KEY
   elif [ "$GOOGLE_MAP_JS_API_KEY" != "" ]; then
      echo found the environment variable GOOGLE_MAP_JS_API_KEY
      echo and copying to GOOGLE_GEOCODE_API_KEY
      GOOGLE_GEOCODE_API_KEY=$GOOGLE_MAP_JS_API_KEY
   else
      echo You have no Google API Key defined.  Get them from: 
      echo https://developers.google.com/maps/documentation/javascript/get-api-key
      echo https://console.cloud.google.com/google/maps-apis/credentials
      echo if you need new keys, see \"CLI testdata script.txt\"
      echo for which 4x API needs to be assigned to the key.
      echo "if you have the key, enter it now(empty to abort):"
      read GOOGLE_GEOCODE_API_KEY
   fi
   if [ "$GOOGLE_GEOCODE_API_KEY" == "" ]; then
      echo No API key, aborting Docker build
      exit
   else
      sed -i "s/ENV GOOGLE_GEOCODE_API_KEY -/ENV GOOGLE_GEOCODE_API_KEY ${GOOGLE_GEOCODE_API_KEY}/g" Docker/dockerfile
      sleep 1
   fi
fi




# docker build has to be run in project root, bc of relative paths below
# Docker/dockerfile also has relative paths, 
#   from project root, which is the working dir "docker image build" is run
sudo docker image build -t carpool-mashup -f Docker/dockerfile .




