from googleproxy import googleproxy
from scriptengineutil import scriptengineutil

class allmembersmapcgi:
    def __init__(self):
        self.name = "allmembersmapcgi.py" # useless, except for debugging

    def execute(self, request, response):
        print("Executing...", self.name)
        service=googleproxy()
        apikey=service.javascriptAPIKEY
        util = scriptengineutil(request,response)
        util.stream("allmembersmap.html", {"replacemewithgoogleapikey":apikey})


