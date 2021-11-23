import os
import time
class HttpServer:
    def __init__(self,config):
        self.startupConfig = config
        self.defaultFile = "index.html"
        self.physicalDir = os.getcwd()
        self.protocol = "http"

        self.last5min = range(300)
        self.last5minlabels = range(300)
        epoch_time = int(time.time())
        self.last=epoch_time%300

    # the main needs to log all the requests to file or list in serialized fashion
    # filter out older than 5min
    # save to file, in fashion below
    def ishandle(self, request):
        epoch_time = int(time.time())
        rolling_epoch = epoch_time%300
        if rolling_epoch!=self.last:
            self.last5min[rolling_epoch] = 0
            self.last = rolling_epoch
            now = datetime.datetime.now()
            if rolling_epoch%60==0:
                self.last5minlabels[rolling_epoch] = now
            else:
                self.last5minlabels[rolling_epoch] = None

            # write a json file with the data [] and labels
            json1 = "[" + ",".join(map(str,self.last5min)) + "]"
            json2 = "[" + ",".join(["null" if s==None else s.strftime("%a, %d %b %Y %H:%M:%S %Z") for s in self.last5minlabels ]) + "]"
            json = "\{data:{}, label:{}\}".format(json1,json2)
            activejson = "loadsummary.json"
            tempjson = "loadsummarynew.json"
            deljson = "loadsummaryold.json"
            with open(json, 'w') as writer:
                buffer = writer.write(json)

            if os.path.isfile(tempjson):
                os.remove(tempjson)
            os.rename(activejson, deljson)
            os.rename(tempjson, activejson)
            os.remove(deljson)
            # os.remove("demofile.txt")
            # os.rename(old_file_name, new_file_name)
            # os.remove("demofile.txt")
        self.last5min[self.last] +=1

        return False
