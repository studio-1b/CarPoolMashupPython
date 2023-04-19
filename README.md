# CarPoolMashupPython
BCIT's CISA1360 Final Project in Python

to copy to your linux (or windows, if you have git on windows)

&nbsp;&nbsp;git clone https://github.com/studio-1b/CarPoolMashupPython.git

You need python installed, and be comfortable with command line

&nbsp;&nbsp;See "CLI testdata script.txt" for instructions to run
  
BTW: "readme.txt" has surpisingly useless data.  I was using it as project task list.


In hindsight, I would've liked to 
1) have the constructor of request, take the incoming tcp connection
2) have a serverconfig base object, which main's config inherits from and populates the necessary fields
3) the server constructor acccepts a serverconfig
4) server has a .nonblockingstart() method wich creates another thread, creates the socket on it, runs a loop listening
   basically moving socket code from main, to server.

But I don't plan on working on this project in future.  
It was fun, but there are no Web Servers that accept python as scripting language



Docker instructions added:
1) Install docker on Linux
2) run the script "sudo ./build_docker.sh", to create a container
3) To see the container, run "docker image ls"
4) run the script "sudo ./run_as_docker.sh", and access http://localhost:8080
&nbsp;&nbsp;&nbsp;&nbsp;if you want to use a port 80, 
&nbsp;&nbsp;&nbsp;&nbsp;look for 8080 in script and change it to what you want,
&nbsp;&nbsp;&nbsp;&nbsp;BUT leave 80 alone 
&nbsp;&nbsp;&nbsp;&nbsp;(bc it has to match EXPOSE and CMD in dockerfile)



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
