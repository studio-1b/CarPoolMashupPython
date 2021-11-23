import threading

from carpoolrules import *
from debugging import debugging

class savepoolcgi:
    def __init__(self):
        self.name = "savepoolcgi.py"

    @staticmethod
    def refreshMatrixInBackground(pool):
        pool.refreshDistanceMatrix()

    def execute(self, request, response):
        if debugging.web: print("Executing...", self.name)

        poolfile = request.post("poolfilename")
        destinationfile = request.post("destinationfile")
        memberfile1 = request.post("member1")
        memberfile2 = request.post("member2")
        memberfile3 = request.post("member3")
        memberfile4 = request.post("member4")
        memberfile5 = request.post("member5")
        memberfile6 = request.post("member6")

        if debugging.web: print("Web submitted pool update", poolfile, destinationfile, memberfile1, memberfile2, memberfile3, memberfile4, memberfile5, memberfile6)

        try:
            destlistrules = destinationlistrules()
            destrules = destinationrules(destlistrules, destinationfile)
            poollistrules = destrules.poollist()

            #destobj=carpooldata.load(destinationfile)
            #poollistfile=destobj["poollistfile"]

            #data=carpooldata.pool(poolfile, destinationfile, memberfile1, memberfile2, memberfile3, memberfile4, memberfile5, memberfile6, 0, poollistfile)
            print("poollistrules",poollistrules.filename)
            if poolfile:
                if debugging.web: print("existing", poolfile)
                # carpooldata.save(data)
                carpoolrules = poolrules(poollistrules, poolfile)
                data = carpoolrules.json
                if debugging.web: print("json to be saved", data)
                data["member1"] = memberfile1
                data["member2"] = memberfile2
                data["member3"] = memberfile3
                data["member4"] = memberfile4
                data["member5"] = memberfile5
                data["member6"] = memberfile6
                carpoolrules.save(matrixupdate=False)
                if carpoolrules.count()>2:
                    thr = threading.Thread(target=savepoolcgi.refreshMatrixInBackground, args=(carpoolrules,), kwargs={})
                    thr.start()
            else:
                if debugging.web: print("new")
                carpoolrules = poollistrules.new()
                data = carpoolrules.json
                if debugging.web: print(data)
                data["member1"] = memberfile1
                data["member2"] = memberfile2
                data["member3"] = memberfile3
                data["member4"] = memberfile4
                data["member5"] = memberfile5
                data["member6"] = memberfile6
                poollistrules.add(carpoolrules)
            if debugging.web: print("data saved to", data["filename"])

            response.bufferWrite(data["filename"])
        except Exception as ex:
            print("Savepoolcgi.py ERROR")
            print(ex)
            response.setInternalError500("error in savepoolcgi")

