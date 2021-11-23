from carpoolrules import *


class registermembercgi:
    def __init__(self):
        self.name = "registermembercgi.py" # useless, except for debugging

    def execute(self, request, response):
        print("Executing...", self.name)
        submit = request.post("submit")
        cancel = request.post("cancel")
        if submit!=None:
            dest=request.post("dest")
            if ("/" in dest) or ("\\" in dest):
                dest=None

            destlistrules = destinationlistrules()
            destrules = destinationrules(destlistrules, dest)
            memberlistrules = destrules.memberlist()
            memberrules = memberlistrules.new()
            data = memberrules.json
            data["email"] = request.post("email")
            data["displayname"] = request.post("displayname")
            data["address"] = request.post("address")
            data["hascar"] = request.post("hascar")

            #data = carpooldata.member(None, request.post("email"), request.post("displayname"), request.post("address"), request.post("hascar"), dest)
            print("web submitted data", data)
            #carpooldata.addMember(data)
            memberlistrules.add(memberrules)

        response.bufferWrite("<html>")
        response.bufferWrite("<head><title>{} saved!</title></head>".format(data["displayname"]))
        response.bufferWrite("<body>")
        response.bufferWrite("<h1>{} saved!</h1><br>".format(data["displayname"]))
        response.bufferWrite("{}<br>".format(data["email"]))
        response.bufferWrite("{}<br>".format(data["address"]))
        if data["hascar"]!=None:
            response.bufferWrite("Vroom vroom!")
        response.bufferWrite("Now goto the waiting room and see if you can find friends")
        response.bufferWrite("</body>")
        response.bufferWrite("</html>")
