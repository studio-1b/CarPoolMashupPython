import datetime
class todaycgi:
    def __init__(self):
        self.name="today.cgi.py"
    def execute(self,request, response):
        print("Executing...", self.name)
        now = datetime.datetime.now()
        response.bufferWrite("<html>")
        response.bufferWrite("<head><title>Today's date and time</title></head>")
        response.bufferWrite("<body>")
        response.bufferWrite("you are {}<br>".format(request.remoteAddress))
        response.bufferWrite(now.strftime("%a, %d %b %Y %H:%M:%S %Z"))
        response.bufferWrite("</head>")
        response.bufferWrite("</html>")