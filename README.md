# CarPoolMashupPython
BCIT's CISA1360 Final Project in Python
https://youtu.be/gVCEGnfhxrs

Working demonstration is posted at: http://100.24.142.145/carpoolmashup/allmembersmapcgi.py

## 1. To run the source code in python

> [!WARNING]
> Carpool uses Google for it's Google Maps product, as well as get coordinates from street addresses.
> You need a Google Cloud API KEY, to try any of the options below (except for the working demonstration link above).  See [https://www.tictawf.com/blog/using-google-cloud-apis/](https://www.tictawf.com/blog/using-google-cloud-apis/) to read how to get started, on getting a API key, and assigning it the correct API to make it function for Carpool

copy to your linux (or windows, if you have git on windows)
```
git clone https://github.com/studio-1b/CarPoolMashupPython.git
```

You need python installed, and be comfortable with command line.
If you don't have python installed, run
```
apt install python3
```

Add to bottom of .bashrc
```
export GOOGLE_GEOCODE_API_KEY=<GOOGLE API_KEY>
export GOOGLE_MAP_JS_API_KEY=<GOOGLE API_KEY>
```
and re-login, or run the above commands in linux command line to set them in current environment

To run the program, to listen to port 8080, to the map application
```
python3 main.py 8080
```

Read for additional instructions to run, if you encounter problems
```
cat "CLI testdata script.txt" 
```
BTW: "readme.txt" has surpisingly useless data.  I was using it as project task list.

Use your internet browser (ie. chrome) to visit
```
http://localhost:8080
```

The command line portion of the program, is to add/change data.  It has a menu, so it should be easy enough to figure out.


## Re: source code.  In hindsight, I would've liked to 
1) have the constructor of request, take the incoming tcp connection
2) have a serverconfig base object, which main's config inherits from and populates the necessary fields
3) the server constructor acccepts a serverconfig
4) server has a .nonblockingstart() method wich creates another thread, creates the socket on it, runs a loop listening
   basically moving socket code from main, to server.

But I don't plan on working on this project in future.  
It was fun, but there are no Web Servers that accept python as scripting language



## Docker instructions added:

### To create a Docker image from source code, and to run this container
1) Install docker on Linux
2) run the script "sudo ./build_docker.sh", to create a container
3) To see the container, run "docker image ls"
4) run the script "sudo ./run_as_docker.sh", and access http://localhost:8080
&nbsp;&nbsp;&nbsp;&nbsp;if you want to use a port 80, 
&nbsp;&nbsp;&nbsp;&nbsp;look for 8080 in script and change it to what you want,
&nbsp;&nbsp;&nbsp;&nbsp;BUT leave 80 alone 
&nbsp;&nbsp;&nbsp;&nbsp;(bc it has to match EXPOSE and CMD in dockerfile)

### Use Docker with testdata already uploaded to internet

> [!WARNING]
> This option still needs the Google Maps API key 

This container image was built with slightly different Dockerfile, than the one in source code.  It runs on default on port 80 (above shows it runs on 8080).  The instructions below tells to pull and run the image on the public internet repository where I uploaded carpool image, and change to listening port to 8000.  There is a reason, I used 8000, it is b/c 80 is often used by any webserver running on your computer and they will conflict.
Notice the API keys still need to be supplied as arguments.

```
docker run -x GOOGLE_GEOCODE_API_KEY=<GOOGLE API_KEY> -x GOOGLE_MAP_JS_API_KEY=<GOOGLE API_KEY>
-it -8000:80 public.ecr.aws/y8w3p2i4/carpoolmashup-with-testdata:latest
```

if you use the instructions above, direct your browser to:
```
http://localhost:8000
```
or if the container is running on a different computer than the one the browser is running on, find the ip address using
for windows
```
ipconfig
```
Ethernet adapter Ethernet ... :
(or Wireless LAN adapter Local Area Connection ... :)
   Connection-specific DNS Suffix  . :
   Link-local IPv6 Address . . . . . : fe80::e023:889:8b1c:bc97%4
   IPv4 Address. . . . . . . . . . . : 192.168.1.102


for linux (eth0 may be different for you, but always starts w/ "e"thernet or "w"ireless)
```
ifconfig
ip addr
```
eth0: ...
        inet 192.168.1.102  ...
...

2: eth0: <BROADCAST,MULTICAST,UP,LOWER_UP> mtu 1500 qdisc mq state UP group default qlen 1000
...
inet 192.168.1.102/24 ...


and paste (the 192.168.1.102, in above is example, use the output from your computer)
```
http://<ipaddress>:8000
```


### Read Instructions for running the container image above in AWS ECS

For about USD$24/mo, you can run the container above in Amazon AWS, and get a public IP address.  The public IP address is temporary, though.  And will be release and re-assigned when you shutdown (or restart) the container

[Aws/README.md](Aws/README.md)



# Images of the Sample app, built on top of homemade HTTP platform

Images for Web Console for CarPoolMashup
![Web Destination Console](https://raw.githubusercontent.com/studio-1b/CarPoolMashupPython/main/SampleApplicationImages/sample%20intermediate%20level%20html%20app%20-%20CarPoolMashup%20Web%20Console.png)
![Web Pool Console](https://raw.githubusercontent.com/studio-1b/CarPoolMashupPython/main/SampleApplicationImages/sample%20intermediate%20level%20html%20app%20-%20CarPoolMashup%20Web%20Carpool%20view.png)
![Web Members Console](https://raw.githubusercontent.com/studio-1b/CarPoolMashupPython/main/SampleApplicationImages/sample%20intermediate%20level%20html%20app%20-%20CarPoolMashup%20Web%20Members%20view.png)
![Web Suggested Car Pool Arrangement View](https://raw.githubusercontent.com/studio-1b/CarPoolMashupPython/main/SampleApplicationImages/sample%20intermediate%20level%20html%20app%20-%20CarPoolMashup%20Web%20Suggest%20view.png)
![Web Optimal Car Pool Path View](https://raw.githubusercontent.com/studio-1b/CarPoolMashupPython/main/SampleApplicationImages/sample%20intermediate%20level%20html%20app%20-%20CarPoolMashup%20Web%20Optimal%20Car%20Pool%20view.png)

Images for CLI Console for CarPoolMashup
![Destination Console](https://raw.githubusercontent.com/studio-1b/CarPoolMashupPython/main/SampleApplicationImages/sample%20intermediate%20level%20html%20app%20-%20CarPoolMashup%20Console%20Destination.png)
![Member Console](https://raw.githubusercontent.com/studio-1b/CarPoolMashupPython/main/SampleApplicationImages/sample%20intermediate%20level%20html%20app%20-%20CarPoolMashup%20Console%20Member.png)
![Pool Console](https://raw.githubusercontent.com/studio-1b/CarPoolMashupPython/main/SampleApplicationImages/sample%20intermediate%20level%20html%20app%20-%20CarPoolMashup%20Console%20Pool.png)

# Issues with python program

executing python3 main.py, returns unable to find "requests": run "pip3 install requests"

executing python3 main.py, return "urllib3 v2.0 only supports OpenSSL 1.1.1+, currently the 'ssl' module is compiled with LibreSSL 2.8.3": run "pip install urllib3==1.26.6"
