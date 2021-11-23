import threading
import os
import json
import uuid
import copy


from carpoolconstants import ext
from debugging import debugging


class listsink:
    def __init__(self,toelement):
        self.sink=[]
        self.select=toelement
    def convert(self, value):
        self.sink.append(self.select(value))
    def funnel(self, lst):
        for item in lst:
            self.convert(item)
        return self.sink
class dictsink:
    def __init__(self,totuple):
        self.sink = {}
        self.select = totuple
    def convert(self, value):
        key, self.sink[key] = self.select(value)
    def funnel(self, lst):
        for item in lst:
            self.convert(item)
        return self.sink

class carpooldata:
    import carpoolconstants as ext

    # https://www.educative.io/edpresso/what-are-locks-in-python
    # I am assuming each lock prevents 2 instances from acquiring at same time, but 2 different locks can acquire simultaneously
    # bc above website does something funny, it instantiates a different lock object for each call, which shouldn't lock anything
    __lockdestindex = threading.Lock()
    __lockmemberindex = threading.Lock()
    __destinations = [None]
    __members = [None]
    __filelock = {}
    __filecache = {}



    # since every file system has it's own type of locking, I'm going to implement threading locks here.
    # and use them as record/file locks.  This won't prevent other processes from simulaneously messing with one
    # record, but it will prevent multiple request from this app from tripping over it's own feet.
    # this is going to be a it of a memory leak as im not releasing the lock object from memory, but
    # I doubt this is going to be an issue for a class project
    @staticmethod
    def __getLock(filename):
        if filename not in carpooldata.__filelock:
            carpooldata.__filelock[filename]=threading.Lock()
        return carpooldata.__filelock[filename]

    @staticmethod
    def __getCache(filename):
        if filename not in carpooldata.__filecache:
            carpooldata.__filecache[filename]=[None]
        return carpooldata.__filecache[filename]

    @staticmethod
    def __getTemporaryFiles(filename):
        actualfile = filename
        #name, ext = os.path.splitext(filename)
        delfile = actualfile+".del"
        tmpfile = actualfile+".tmp"
        return tmpfile, delfile

    @staticmethod
    def __getLockableIndex(named2pair, indexfile,cache,lock):
        cache2=None
        if cache: #the index is another cache
            cache2 = carpooldata.__getCache(indexfile+".index")
        if cache2 and len(cache2)!=0 and cache2[0]!=None:
            return cache2[0]
        indexobject = None
        if lock:
            lock.acquire()
        try:
            listobject = carpooldata.__getLockableList(indexfile, cache, None)
            if listobject!=None:
                indexobject = dictsink(named2pair).funnel(listobject)
                # indexobject = carpooldata.__list2dict(listobject,indexkey)
            else:
                listobject = []
                carpooldata.__bufferserialize(listobject, indexfile)
                indexobject = {}
            if cache2 and len(cache2) != 0:
                cache2[0] = indexobject
        finally:
            if lock:
                lock.release()
        return indexobject

    @staticmethod
    def __saveLockableIndex(value,named2pair,pair2named, indexfile,cache,lock):
        if debugging.on: print(value,named2pair,pair2named, indexfile,cache,lock)

        if cache: #the index is another cache
            cache2 = carpooldata.__getCache(indexfile+".index")
        indexobject=None
        if cache2 and len(cache2)!=0 and cache2[0]!=None:
            indexobject=copy.deepcopy(cache2[0])
        if lock:
            lock.acquire()
        try:
            if indexobject==None:
                listobject = carpooldata.__getLockableList(indexfile, cache, None)
                indexobject = dictsink(named2pair).funnel(listobject)
            # listobject = listsink(pair2named).funnel(indexobject)
            key, indexobject[key] = value  # add to index, before conversion
            carpooldata.__saveLockableList(pair2named(value), indexfile, cache, None)
            if cache2 and len(cache2) != 0:
                cache2[0] = indexobject
        finally:
            if lock:
                lock.release()
        # if debugging.on: print("locked write:",indexfile,tobesaved)

    @staticmethod
    def __removeFromLockableIndex(key, named2pair,pair2named, indexfile, cache, lock):
        if cache: #the index is another cache
            cache2 = carpooldata.__getCache(indexfile+".index")
        indexobject=None
        if cache2 and len(cache2)!=0 and cache2[0]!=None:
            indexobject=copy.deepcopy(cache2[0])
        if lock:
            lock.acquire()
        try:
            if indexobject==None:
                listobject = carpooldata.__getLockableList(indexfile, cache, None)
                indexobject = dictsink(named2pair).funnel(listobject)
            value=None
            if key in indexobject:
                value=pair2named( (key,indexobject[key]) ) # input is new instance of tuple
                del indexobject[key]
            else:
                print(indexobject)
                raise KeyError("cannot find " +key)
            # listobject = listsink(pair2named).funnel(indexobject.index())
            # carpooldata.__saveLockableList(listobject, cache, None)
            if debugging.on: print("__removeFromLockableIndex --> __removeFromLockableList",value, indexfile, cache)
            print("before__removeFromLockableList")
            print(value)
            carpooldata.__removeFromLockableList(value, indexfile, cache, None)
            if cache2 and len(cache2) != 0:
                cache2[0] = indexobject
        finally:
            if lock:
                lock.release()

    @staticmethod
    def __getLockableList(listfile,cache,lock):
        if cache and len(cache)!=0 and cache[0]!=None:
            return cache[0]
        listobject = None
        if lock:
            lock.acquire()
        try:
            listobject = carpooldata.__deserialize(listfile)
            if listobject==None:
                listobject = []
                carpooldata.__bufferserialize(listobject, listfile)
            if cache and len(cache) != 0:
                cache[0] = listobject
        finally:
            if lock:
                lock.release()
        return listobject

    @staticmethod
    def __saveLockableList(item, listfile, cache,lock):
        listobject=None
        if cache and len(cache)!=0 and cache[0]!=None:
            listobject = copy.deepcopy(cache[0])
        if lock:
            lock.acquire()
        try:
            if listobject==None:
                listobject = carpooldata.__deserialize(listfile) # no writes during this read, they can serve from cache, in mean time
            listobject.append(item)
            carpooldata.__bufferserialize(listobject,listfile)
            if cache and len(cache) != 0:
                cache[0]=listobject # reload cache, hopefully atomic write
        finally:
            if lock:
                lock.release()
        if debugging.on: print("locked write:",listfile,listobject)

    @staticmethod
    def __removeFromLockableList(item, listfile, cache, lock):
        listobject = None
        if cache and len(cache) != 0 and cache[0] != None:
            listobject = copy.deepcopy(cache[0])
        if lock:
            lock.acquire() # no writes, during read
        try:
            if listobject == None:
                listobject = carpooldata.__deserialize(listfile) # no writes during this read, they can serve from cache, in mean time
            print("remove from list")
            print(listobject)
            print(item)
            listobject.remove(item)
            carpooldata.__bufferserialize(listobject, listfile)
            if cache and len(cache) != 0:
                cache[0]=listobject # reload cache, hopefully atomic write
        finally:
            if lock:
                lock.release()
        if debugging.on: print("locked write:", listfile, listobject)

    @staticmethod
    # https://stackabuse.com/reading-and-writing-json-to-a-file-in-python/
    def __serialize(tobesaved, filename):
        #filename = "data" + os.sep + filename
        with open(filename, 'w') as outfile:
            json.dump(tobesaved, outfile)
        if debugging.on: print("Saved", filename, tobesaved)
    def clobberingserialize(tobesaved, filename):
        carpooldata.__serialize(tobesaved, filename)

    @staticmethod
    def __bufferserialize(tobesaved, filename, lock=None):
        tmpname, deletename = carpooldata.__getTemporaryFiles(filename)
        #tmpname = "data" + os.sep + tmpname
        #deletename = "data" + os.sep + deletename
        carpooldata.__serialize(tobesaved, tmpname)
        if os.path.exists(filename):
            os.rename(filename, deletename)
        if lock:
            lock.acquire()
        try:
            os.rename(tmpname, filename)
        finally:
            if lock:
                lock.release()
        if os.path.exists(deletename):
            os.remove(deletename)
        if debugging.on: print("Final Saved", filename, tobesaved)

    @staticmethod
    def __deserialize(filename):
        #filename="data"+os.sep+filename
        if os.path.exists(filename):
            dataobject = None
            with open(filename) as f:
                dataobject = json.load(f)
                if debugging.on: print("loaded",dataobject)
            return dataobject
        else:
            if debugging.on:  print("Cannot find", filename,"returning None")
            return None;





    @staticmethod
    def getDestinationDict():
        list2dict = lambda s:(s["name"],s["url"])
        # dict2list = lambda s:{"name":s[0],"url": s[1]}
        indexfile = 'destindex.json'
        cache = carpooldata.__destinations
        return carpooldata.__getLockableIndex(list2dict,indexfile, cache, carpooldata.__lockdestindex)

    @staticmethod
    def addDestination(destobject):
        if destobject["filename"]==None:
            destobject["filename"] = str(uuid.uuid4())+ext.default
        if "/" in destobject["filename"] or "\\" in destobject["filename"]:
            raise ValueError # This shouldn't be allowed, we don't allow the static file server to access directories, so the server scripts shouldnt shoul

        if destobject["memberlistfile"] == None:
            # create empty member list file, put the filename here
            memberlistfile=str(uuid.uuid4())+ext.memberndx
            carpooldata.__serialize([],memberlistfile)
            destobject["memberlistfile"] = memberlistfile

        if destobject["poollistfile"] == None:
            # create empty pool list file, put the filename here
            poollistfile = str(uuid.uuid4()) + ext.poollst
            carpooldata.__serialize([], poollistfile)
            destobject["poollistfile"] = poollistfile

        actualfile = destobject["filename"]
        carpooldata.__bufferserialize(destobject, actualfile)

        #destindex = carpooldata.getDestinationDict()
        #indexkey = destobject["destinationname"]
        # indexstore = {"name":destobject["destinationname"],"url": destobject["filename"]}
        list2dict = lambda s:(s["name"],s["url"])
        dict2list = lambda s:{"name":s[0],"url":s[1]}
        namevalue = (destobject["destinationname"], destobject["filename"])
        indexfile = 'destindex.json'
        cache = carpooldata.__destinations
        carpooldata.__saveLockableIndex(namevalue, list2dict,dict2list,indexfile, cache, carpooldata.__lockdestindex)

    @staticmethod
    def delDestination(destobject):
        if destobject["filename"]==None:
            raise ValueError
        if "/" in destobject["filename"] or "\\" in destobject["filename"]:
            raise ValueError # This shouldn't be allowed, we don't allow the static file server to access directories, so the server scripts shouldnt shoul

        if destobject["memberlistfile"] != None:
            # cascade delete
            if os.path.exists(destobject["memberlistfile"]):
                os.remove(destobject["memberlistfile"])

        if destobject["poollistfile"] != None:
            # cascade delete
            if os.path.exists(destobject["poollistfile"]):
                os.remove(destobject["poollistfile"])

        # destindex = carpooldata.getDestinationDict()
        list2dict = lambda s:(s["name"],s["url"])
        dict2list = lambda s:{"name":s[0],"url": s[1]}
        indexkey = destobject["destinationname"]
        indexfile = 'destindex.json'
        cache = carpooldata.__destinations
        print("before__removeFromLockableIndex")
        print(indexkey)
        carpooldata.__removeFromLockableIndex(indexkey, list2dict,dict2list, indexfile, cache, carpooldata.__lockdestindex)

        actualfile = destobject["filename"]
        if os.path.exists(actualfile):
            os.remove(actualfile)

    @staticmethod
    def getMemberDict(filename):
        list2dict = lambda s: (s["email"], s["memberfile"])
        cache = carpooldata.__getCache(filename)
        return carpooldata.__getLockableIndex(list2dict,filename, cache, carpooldata.__lockmemberindex)

    @staticmethod
    def addMember(memberobject):
        if memberobject["filename"]==None:
            memberobject["filename"] = str(uuid.uuid4())+ext.member
        if "/" in memberobject["filename"] or "\\" in memberobject["filename"]:
            raise ValueError("filename doesnt match this programmer rules") # This shouldn't be allowed, we don't allow the static file server to access directories, so the server scripts shouldnt shoul
        destinationfile = memberobject["destinationfile"]
        destinationobject = carpooldata.__deserialize(destinationfile)
        if debugging.on: print("addMember().loaded destinationobject", destinationobject)
        memberlistfile = destinationobject["memberlistfile"]
        if debugging.on: print("addMember().loaded memberlistfile", memberlistfile)

        actualfile = memberobject["filename"]
        carpooldata.__bufferserialize(memberobject, actualfile)

        #memberindex = carpooldata.getMemberDict(memberlistfile)
        #if debugging.on: print("addMember().loaded memberindex",memberindex)
        list2dict = lambda s:(s["email"],s["memberfile"])
        dict2list = lambda s:{"email":s[0],"memberfile":s[1]}
        #indexkey = memberobject["email"]
        #indexstore = {"email":memberobject["email"],"memberfile":memberobject["filename"]}
        indexstore = (memberobject["email"], memberobject["filename"])
        if debugging.on: print("addMember(). saving index entry",indexstore)
        cache = carpooldata.__getCache(memberlistfile)
        lock = carpooldata.__getLock(memberlistfile)

        carpooldata.__saveLockableIndex(indexstore,list2dict,dict2list, memberlistfile, cache, lock)

    @staticmethod
    def delMember(memberobject):
        if memberobject["filename"]==None:
            raise ValueError
        if "/" in memberobject["filename"] or "\\" in memberobject["filename"]:
            raise ValueError # This shouldn't be allowed, we don't allow the static file server to access directories, so the server scripts shouldnt shoul

        if memberobject["geocodefile"] != None:
            # cascade delete
            if os.path.exists(memberobject["geocodefile"]):
                os.remove(memberobject["geocodefile"])

        print("remember he needs to be deleted from pool membership as well")

        indexkey = memberobject["email"]
        # carpooldata.__getLockableIndex(list2dict, indexfile, cache, carpooldata.__lockdestindex)
        destobj = carpooldata.load(memberobject["destinationfile"])
        # memberindex = carpooldata.getMemberDict(indexfile)
        indexfile = destobj["memberlistfile"]
        list2dict = lambda s: (s["email"], s["memberfile"])
        dict2list = lambda s: {"email": s[0], "memberfile": s[1]}

        lock = carpooldata.__getLock(indexfile)
        cache = carpooldata.__getCache(indexfile)
        carpooldata.__removeFromLockableIndex(indexkey, list2dict, dict2list, indexfile, cache, lock)

        actualfile = memberobject["filename"]
        if os.path.exists(actualfile):
            os.remove(actualfile)

    @staticmethod
    def getPoolfileList(filename):
        if "/" in filename or "\\" in filename:
            raise ValueError # This shouldn't be allowed, we don't allow the static file server to access directories, so the server scripts shouldnt shoul
        cache = carpooldata.__getCache(filename)
        if cache and len(cache)!=0 and cache[0]:
            return cache[0]
        poollistobj = carpooldata.load(filename,False)
        if cache and len(cache)!=0 and cache[0]:
            cache[0] = poollistobj
        return poollistobj

    @staticmethod
    def addToPoolfileList(poolobj):
        filename=poolobj["filename"]
        if filename==None:
            raise ValueError
        if "/" in filename or "\\" in filename:
            raise ValueError # This shouldn't be allowed, we don't allow the static file server to access directories, so the server scripts shouldnt shoul
        # save the poolobj
        # take the filename and save to poollistfile... what is easiest way to get this file
        carpooldata.save(poolobj)

        poollistfilename = poolobj["poollistfile"]
        poollistobj = carpooldata.load(poollistfilename)
        if poolobj["filename"] not in poollistobj:
            cache = carpooldata.__getCache(poollistfilename)
            lock = carpooldata.__getLock(poollistfilename)
            # filename is the object to be inserted, normally a complex json, but not in this case
            carpooldata.__saveLockableList(filename,poollistfilename,cache,lock)

    @staticmethod
    def delFromPoolfileList(poolobj):
        filename = poolobj["filename"]
        if filename == None:
            raise ValueError
        if "/" in filename or "\\" in filename:
            raise ValueError  # This shouldn't be allowed, we don't allow the static file server to access directories, so the server scripts shouldnt shoul

        poollistfilename = poolobj["poollistfile"]
        cache = carpooldata.__getCache(poollistfilename)
        lock = carpooldata.__getLock(poollistfilename)
        carpooldata.__removeFromLockableList(filename, poollistfilename, cache, lock)
        os.remove(filename)

    @staticmethod
    def merge(oldobj,changesobj,nonuser=[],checktype=True):
        if checktype:
            if oldobj["type"]!=changesobj["type"] and changesobj["type"]!="*":
                if debugging.on: print(oldobj["type"],changesobj["type"],oldobj["filename"],changesobj["filename"])
                raise ValueError # the types need to be the same, otherwise merge isnt supposed to work and that is why this is exception, not return False
        for item in changesobj:
            if item not in nonuser and (item not in oldobj or changesobj[item] != None):
                oldobj[item] = changesobj[item]
        return oldobj

    @staticmethod
    def member(filename,email,displayname,address,hascar, destination, geocode=None):
        if filename==None:
            filename = str(uuid.uuid4())+ext.member
        if geocode==None:
            name, extension = os.path.splitext(filename)
            geocode=name+ext.geo
        if "/" in filename or "\\" in filename:
            raise ValueError # This shouldn't be allowed, we don't allow the static file server to access directories, so the server scripts shouldnt shoul
        return {
            "type" :"member",
            "filename" :filename,
            "email" :email,
            "displayname" :displayname,
            "address" :address,
            "hascar" :hascar,
            "geocodefile": None,
            "destinationfile" :destination
        }

    @staticmethod
    def destination(filename,destination,address,geocode=None):
        if filename==None:
            filename = str(uuid.uuid4())+ext.dest
        if ("/" in filename) or ("\\" in filename):
            raise ValueError # This shouldn't be allowed, we don't allow the static file server to access directories, so the server scripts shouldnt shoul
        if geocode==None:
            name, extension = os.path.splitext(filename)
            geocode=name+".geocode.json"
        return {
            "type" :"destination",
            "filename":filename,
            "destinationname":destination,
            "address" : address,
            "geocodefile": geocode,
            "memberlistfile": None,
            "poollistfile" : None,
            "mstpathfile": None,
            "suggestfile":None
        }

    @staticmethod
    def pool(filename,destination,member1,member2,member3,member4,member5,member6,progress,poollistfile,matrix=None,path=None):
        if not filename or filename==None:
            filename = str(uuid.uuid4())+ext.pool
        if "/" in filename or "\\" in filename:
            raise ValueError # This shouldn't be allowed, we don't allow the static file server to access directories, so the server scripts shouldnt shoul
        if not matrix or matrix==None:
            name, extension = os.path.splitext(filename)
            matrix=name+ext.matrix
        if not path or path==None:
            name, extension = os.path.splitext(filename)
            matrix=name+ext.path
        return {
            "type" :"pool",
            "filename":filename,
            "destinationfile":destination,
            "member1":member1,
            "member2":member2,
            "member3":member3,
            "member4":member4,
            "member5":member5,
            "member6":member6,
            "matrixfile": matrix,
            "pathfile": path,
            "poollistfile":poollistfile,
            "progress":progress,
            "matrixreply":None
        }

    @staticmethod
    def load(filename, checktype=None):
        if debugging.on: print("deserializing...",filename)
        obj = carpooldata.__deserialize(filename)
        if checktype!=None:
            if "type" in obj and obj["type"]!=checktype:
                if debugging.on: print("load() error checking deserializing[", filename, "]is not a[" ,checktype,"]")
                raise ValueException
        return obj

    @staticmethod
    def lockload(filename, checktype=None):
        if debugging.on: print("deserializing...",filename)
        lock=carpooldata.__getLock(filename) # for files that have a lot of writes
        if lock:
            lock.acquire()
        try:
            obj = carpooldata.__deserialize(filename)
        finally:
            lock.release()
        if checktype!=None:
            if "type" in obj and obj["type"]!=checktype:
                if debugging.on: print("load() error checking deserializing[", filename, "]is not a[" ,checktype,"]")
                raise ValueException
        return obj


    @staticmethod
    def save(objectdata,chkclobber=True,filename=None,lock=None):
        if objectdata["filename"]==None:
            if filename!=None:
                objectdata["filename"] = filename
            else:
                objectdata["filename"] = str(uuid.uuid4()) + ext.default
        # clobber checking
        if chkclobber:
            # print("serializing", filename, "clobber check")
            existingname = objectdata["filename"]
            old = carpooldata.__deserialize(existingname)
            if old!=None and type(objectdata) is dict:
                if "type" in objectdata and "type" in old:
                    if objectdata["type"] != old["type"]:
                        if debugging.on: print("save() error checking for [", filename, "], type mismatch:",objectdata["type"],old["type"])
                        raise ValueError  # clobber, reason type mismatch
                else:
                    raise ValueError # clobber, version mismatch
                if "filename" in objectdata and "filename" in old:
                    if objectdata["filename"] != old["filename"]:
                        if debugging.on: print("save() error checking for [", filename, "], filename mismatch:",objectdata["filename"],old["filename"])
                        raise ValueError  # clobber, version mismatch
                else:
                    if debugging.on: print("save() error checking for [", filename, "], missing filename field in either new or old",objectdata,old)
                    raise ValueError # clobber, version mismatch

        actualfile=objectdata["filename"]
        carpooldata.__bufferserialize(objectdata, actualfile, lock)





