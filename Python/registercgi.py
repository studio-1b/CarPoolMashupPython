from carpoolrules import *

class registercgi:
    def __init__(self):
        self.name="registercgi.py"
    def execute(self,request, response):
        print("Executing...", self.name)

        destination = request.post("destname")
        waypoint = request.post("address")
        submit = request.post("submit")
        cancel = request.post("cancel")
        if submit!=None:
            destlistrules = destinationlistrules()
            destrules = destlistrules.new()
            data = destrules.json
            data["destinationname"] = destination
            data["address"] = waypoint

            #data = carpooldata.destination(None,destination,waypoint)
            print("Web submitted new destination", data)
            #carpooldata.addDestination(data)
            destlistrules.add(destrules)


        response.bufferWrite("<html>")
        response.bufferWrite("<head><title>{} saved!</title></head>".format(destination))
        response.bufferWrite("<body>")
        response.bufferWrite("{} saved!<br>".format(destination))
        response.bufferWrite("Now you can tell people to join your carpool, but you're gonna have to do it yourself bc this programmer is too lazy to figure out how to connect to a email processor.")
        response.bufferWrite("</head>")
        response.bufferWrite("</html>")
        