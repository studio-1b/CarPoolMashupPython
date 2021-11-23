import os
import urllib.request
import json

from debugging import debugging

class googleproxy:
    def __init__(self):
        self.javascriptAPIKEY = os.environ["GOOGLE_MAP_JS_API_KEY"]
        self.geocodeAPIKEY = os.environ["GOOGLE_GEOCODE_API_KEY"]
        self.geocodeurl="https://maps.googleapis.com/maps/api/geocode/json?address={}&sensor=false&key={}"
        self.distancematrixurlmetric = "https://maps.googleapis.com/maps/api/distancematrix/json?origins={}&destinations={}&mode=driving&units=metric&language=en-US&sensor=false&key={}"
        self.distancematrixurl = "https://maps.googleapis.com/maps/api/distancematrix/json?origins=6920+Canada+Way|3700+Willingdon+Ave|4700+Kingsway+Burnaby&destinations=6920+Canada+Way|3700%20Willingdon%20Ave|4700+Kingsway+Burnaby&mode=driving&units=imperial&language=en-US&sensor=false&key={}"
    def _saveToFile(self,url,savein):
        # https://stackoverflow.com/questions/645312/what-is-the-quickest-way-to-http-get-in-python
        try:
            contents = urllib.request.urlopen(url).read()
            with open(savein,"wb") as f:
                f.write(contents)
            return contents
        except Exception as ex:
            if debugging.on: print("Error getting data from",url,ex)
            return None

    def getGeocodeFor(self,foraddress,savein):
        encoded = self.urlencode(foraddress)
        url = self.geocodeurl.format(encoded, self.geocodeAPIKEY)
        if url:
            contents = self._saveToFile(url,savein)
            if contents:
                return json.loads(contents)
        return None

    def getDistanceFor(self,addresslist,savein):
        o = "|".join(map(lambda s: self.urlencode(s), addresslist))
        d = "|".join(map(lambda s: self.urlencode(s), addresslist))
        url = self.distancematrixurlmetric.format(o,d,self.geocodeAPIKEY)
        contents = self._saveToFile(url,savein)
        return json.loads(contents)


    # https://developer.classpath.org/doc/java/net/URLDecoder-source.html
    def urlencode(self,text):
        buffer=[]
        step=0
        instr=0
        last=""
        ord0 = ord("0")
        ordA = ord("A")
        orda = ord("a")
        safe = ["-", ".", "_", "~", "(", ")", "'", "!", "*", ":", "@", ",", ";"]
        safe += range(ord("A"),ord("Z")+1)
        safe += range(ord("a"),ord("z")+1)
        safe += range(ord("0"),ord("9")+1)
        safe = set(safe) # list turns into set here
        for ch in text:
            if ch==" ":
                buffer.append("+")
            elif ch in safe:
                buffer.append(ch)
            else:
                num=ord(ch)
                buffer.append("%{:02X}".format(num))
        encoded = ''.join(buffer)
        return encoded

class GoogleError(ValueError):
    def __init__(self, msg=None):
        ValueError.__init__(self,msg)