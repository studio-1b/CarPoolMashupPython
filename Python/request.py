class HttpRequest:
    def _pairs2tuple(key, lst, separator="="):
        for item in filter(lambda s: False if s==None else s.startswith(key), lst):
            if separator in item and item.startswith(key + separator):
                half = item.split(separator)
                return (half[0], half[1])
            elif item == key:
                return (item, None)
        else:
            return None

    def _tuple2pairs(tple, lst, separator="="):
        key = tple[0]
        pair = tple[0] if len(tple) == 1 or tple[1] == None else tple[0] + separator + tple[1]
        for i in range(len(lst)):
            item = lst[i]
            if item.startswith(key):
                if item.startswith(key + separator):
                    lst[i] = pair
                elif item == key:
                    lst[i] = pair
        else:
            lst.append(pair)

    # https://developer.classpath.org/doc/java/net/URLDecoder-source.html
    def urldecode(encoded):
        buffer=[]
        step=0
        instr=0
        last=""
        ord0 = ord("0")
        ordA = ord("A")
        orda = ord("a")
        for ch in encoded:
            if step==0:
                if ch=="+":
                    buffer.append(" ")
                elif ch=="%":
                    step=1
                else:
                    buffer.append(ch)
            elif step==1:
                last=ch
                if "0"<=ch<="9":
                    instr=ord(ch)-ord0
                    step=2
                elif "a"<=ch<="f":
                    instr=10+ord(ch)-orda
                    step=2
                elif "A"<=ch<="F":
                    instr=10+ord(ch)-ordA
                    step=2
                else:
                    buffer.append("%")
                    buffer.append(ch)
                    step = 0
            elif step==2:
                if "0"<=ch<="9":
                    instr=instr*16 + ord(ch)-ord0
                    buffer.append(chr(instr))
                    step=0
                elif "a"<=ch<="f":
                    instr=instr*16 + (10+ord(ch)-orda)
                    buffer.append(chr(instr))
                    step=0
                elif "A"<=ch<="F":
                    instr=instr*16 + (10+ord(ch)-ordA)
                    buffer.append(chr(instr))
                    step=0
                else:
                    buffer.append("%")
                    buffer.append(last)
                    buffer.append(ch)
                    step = 0
        decoded = ''.join(buffer)
        return decoded

    def __init__(self, server, buffer=[]):
        LINE_METHOD_AND_URL = 0

        self.server = server
        self.raw=buffer
        self.decoded = buffer.decode() # Assuming UTF8, no coding occurred
        lines = self.decoded.split("\r\n")
        if len(lines)==1:
            lines = self.decoded.split("\r")
            if len(lines) == 1:
                lines = self.decoded.split("\n")
        requestline = lines[LINE_METHOD_AND_URL].split(" ")
        if len(requestline)<2:
            print("please verify abnormal request",lines[LINE_METHOD_AND_URL])
        self.method = requestline[0]
        self.urlraw = requestline[1]
        self.url = self.urlraw
        self.querystringall = None
        self.querystringpairs = None
        try:
            middle = self.urlraw.index("?")
            self.url = self.urlraw[:middle]
            self.querystringall = self.urlraw[middle:]
            self.querystringpairs = self.querystringall[1:].split("&")
        except ValueError:
            self.url = self.urlraw

        if "//" in self.url:
            start = self.url.index("//")+2
            end = self.url[start:].index("/")
            self.virtualhost = self.url[start:end+2]
            self.virtualpath = self.url[end:]
        else:
            self.virtualhost = None
            self.virtualpath = self.url
        self.version = "" if len(requestline)<3 else requestline[2]

        self.postraw = None
        self.postall = None
        self.postpairs = None
        if self.method.lower()=="post":
            start=0
            try:
                start=self.raw.find(b"\r\n\r\n")
            except ValueError:
                #no POST found
                self.postraw = None
            if start!=0:
                self.postraw = self.raw[start+4:]
                self.postall = self.postraw.decode()
                self.postpairs = self.postall.split("&")

        if len(lines)>1:
            start = self.raw.find(b"\r\n")
            end = self.raw.find(b"\r\n\r\n")
            if end==0:
                self.headersraw = self.raw[start+2:].decode()
            else:
                self.headersraw = self.raw[start + 2:end].decode()
            self.headers = self.headersraw.split("\r\n")

        # b'GET / HTTP/1.1\r\nHost: localhost\r\nConnection: keep-alive\r\nCache-Control: max-age=0\r\nsec-ch-ua: "Microsoft Edge";v="95", "Chromium";v="95", ";Not A Brand";v="99"\r\nsec-ch-ua-mobile: ?0\r\nsec-ch-ua-platform: "Windows"\r\nUpgrade-Insecure-Requests: 1\r\nUser-Agent: Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/95.0.4638.54 Safari/537.36 Edg/95.0.1020.30\r\nAccept: text/html,application/xhtml+xml,application/xml;q=0.9,image/webp,image/apng,*/*;q=0.8,application/signed-exchange;v'


    def header(self,key):
        obj = HttpRequest._pairs2tuple(key, self.headers, ": ")
        if obj!=None and obj[0]==key:
            return obj[1]
        else:
            return None;
    def querystring(self, key):
        obj = HttpRequest._pairs2tuple(key, map(HttpRequest.urldecode, self.querystringpairs))
        if obj!=None and obj[0]==key:
            return obj[1]
        else:
            return None;
    def post(self, key):
        obj = HttpRequest._pairs2tuple(key, map(HttpRequest.urldecode, self.postpairs))
        if obj!=None and obj[0]==key:
            return obj[1]
        else:
            return None;

