from carpooldata import carpooldata
from scriptengineutil import scriptengineutil

class registermemberwithdestcgi:
    def __init__(self):
        self.name = "registermemberwithdestcgi.py" # useless, except for debugging

    def execute(self, request, response):
        print("Executing...", self.name)

        dest = request.querystring("dest")
        destJSON = carpooldata.load(dest,"destination")
        if destJSON==None:
            response.setInternalError500("<html><body>Hmm, you seem to have requested to join something that doesn't exist</body></html>")
            return
        joinmessage = "You are joining other car poolers to [" + destJSON["destinationname"] + "]"
        util = scriptengineutil(request,response)
        util.stream("registermember.html", {"replacemewithdestinationcode":dest, "replacemewithjoinmessage":joinmessage})


