# CarPoolMashupPython
BCIT's CISA1360 Final Project in Python

See readme.txt for instructions to run

In hindsight, I would've liked to 
1) have the constructor of request, take the incoming tcp connection
2) have a serverconfig base object, which main's config inherits from and populates the necessary fields
3) the server constructor acccepts a serverconfig
4) server has a .nonblockingstart() method wich creates another thread, creates the socket on it, runs a loop listening
   basically moving socket code from main, to server.

But I'm not working on this project anymore.
