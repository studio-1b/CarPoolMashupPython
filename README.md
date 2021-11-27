# CarPoolMashupPython
BCIT's CISA1360 Final Project in Python

See readme.txt for instructions to run

In hindsight, I would've liked to 
1) have the constructor of request, take the incoming tcp connection
2) have a serverconfig base object, which main's config inherits from and populates the necessary fields
3) the server constructor acccepts a serverconfig
4) server has a .nonblockingstart() method wich creates another thread, creates the socket on it, runs a loop listening
   basically moving socket code from main, to server.

But I don't plan on working on this project in future.  
It was fun, but there are no Web Servers that accept python as scripting language

![](https://raw.githubusercontent.com/studio-1b/CarPoolMashupPython/main/SampleApplicationImages/sample%20intermediate%20level%20html%20app%20-%20CarPoolMashup%20Console%20Destination.png)
!(https://raw.githubusercontent.com/studio-1b/CarPoolMashupPython/main/SampleApplicationImages/sample%20intermediate%20level%20html%20app%20-%20CarPoolMashup%20Console%20Member.png)
!(https://raw.githubusercontent.com/studio-1b/CarPoolMashupPython/main/SampleApplicationImages/sample%20intermediate%20level%20html%20app%20-%20CarPoolMashup%20Console%20Pool.png)
!(https://raw.githubusercontent.com/studio-1b/CarPoolMashupPython/main/SampleApplicationImages/sample%20intermediate%20level%20html%20app%20-%20CarPoolMashup%20Web%20Carpool%20view.png)
!(https://raw.githubusercontent.com/studio-1b/CarPoolMashupPython/main/SampleApplicationImages/sample%20intermediate%20level%20html%20app%20-%20CarPoolMashup%20Web%20Console.png)
!(https://raw.githubusercontent.com/studio-1b/CarPoolMashupPython/main/SampleApplicationImages/sample%20intermediate%20level%20html%20app%20-%20CarPoolMashup%20Web%20Members%20view.png)
!(https://raw.githubusercontent.com/studio-1b/CarPoolMashupPython/main/SampleApplicationImages/sample%20intermediate%20level%20html%20app%20-%20CarPoolMashup%20Web%20Optimal%20Car%20Pool%20view.png)
!(https://raw.githubusercontent.com/studio-1b/CarPoolMashupPython/main/SampleApplicationImages/sample%20intermediate%20level%20html%20app%20-%20CarPoolMashup%20Web%20Suggest%20view.png)
