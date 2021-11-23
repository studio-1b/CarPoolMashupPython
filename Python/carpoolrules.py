import datetime
import os

from debugging import debugging
from carpooldata import carpooldata
from carpoolconstants import ext
from googleproxy import *
from heldkarpe import *

# this class exists to take code out of the UI, which in my application has 2
# and hide carpooldata and the spanning tree and held-karpe algorithms
# *listrules are classes suffixed w listrules and are intended to manage lists of objects
# they are intended to act w/ carpool data to save json to files
#     .selection
#     def childkey(self,item): take json, return the value this list will index it by
#     def new(self): returns a new *rule object with new json
#     def list(self): returns either a list or dictionary w lazyrulesLoader, which .load() to get *rules
#                     if dictionary, each object one field user entered field that has to be unique
#     def search(self,criteria): iterator returns the a blurb about where it found it and *rules object
#     def get(self,key): accepts lazyrulesLoader to set .selection and return data
#     def add(self,item): accepts json or *rules, to add to it's list
#     def remove(self,key): accept json or *rules or the key
# * rules are classes suffixed with rules and is intended to manage a single data instance
#     def save()
#     def remove()
# all classes above, except one, have .parent for 2-way node tranversal, for data lookup
# intended structure
# 1 x destinationlistrules
#     * x destinationrules
#         1 x memberlistrules
#             * x memberrules
#         1 x poollistrules
#             * x poolrules
#                 0-6 x memberrules
# if I had time to redo this, the json would all be 2-way traversable
# and so the entire tree can be rebuilt from a single json



class lazyrulesLoader:
    # this makes the most consistent sense to use in list(),
    def __init__(self,lazytype,parent,key,filename):
        self.lazytype = lazytype  # what to construct
        self.parent = parent      # part of *rules constructor
        self.filename=filename    # part of *rules constructor
        self.key=key  # this value is only set by list() right now, and only used by get()
        self.instance=None        # instantiated class
    def load(self):
        if self.instance==None:
            self.instance= self.lazytype(self.parent,self.filename)
        return self.instance

class baselist:
    def __init__(self,filename):
        self.filename = filename
        self.now = datetime.datetime.now()
        self.childtype = None
        self.selected = None
        self._deldelegate = None
        self._adddelegate = None
        self._rulestype = None
    def _ischildtype(self,item):
        if item == None or "type" not in item or item != self.childtype:
            return False
        else:
            return True
    def _isdictequal(self,d,key,value):
        if d!=None and key in d and d[key]==value:
            return True
        else:
            return False
    def _highlight(self,label, fragment, footer, data):
        # print(label,data,footer)
        spaces = len(label) + 1
        spaces += data.index(fragment)
        underline = len(fragment)
        hilit = (" " * (spaces)) + ("-" * underline)
        return label + " " + data + " " + footer + "\n" + hilit

    def _jsonsearch(self,dictorlist, searchfor):
        if type(dictorlist) is dict:
            for item in dictorlist:
                result1, result2 = self._jsonsearch(dictorlist[item], searchfor)
                if result1 and result2: return item + "." + result1, result2
                if result2: return item, result2
        elif type(dictorlist) is list:
            counter = 0
            for item in dictorlist:
                result1, result2 = self._jsonsearch(item, searchfor)
                if result1 and result2: return str(counter) + "." + result1, result2
                if result2: return str(counter), result2
                counter += 1
        elif isinstance(dictorlist, str):
            if searchfor in dictorlist:
                return None, dictorlist
            else:
                return None, None
        else:
            try:
                text = str(dictorlist)
            except Exception as ex:
                if debugging.on: print("jsonsearch: Expected problem w converting to a string",dictorlist)
                return None, None
            return self._jsonsearch(dictorlist, text)
        return None, None

    def childkey(self,item):
        pass
    def new(self):
        pass
    def list(self):
        pass
    def search(self,criteria):
        pass
    def get(self,key):
        pass
    def add(self,item):
        pass
    def remove(self,key):
        pass

    def _get(self,key):
        if isinstance(key,lazyrulesLoader): #always rely on key to get data, over .load()
            key=key.key
            if key==None:
                raise Exception("only lazyloaders from list() have key right now, so it isnt supported right now making member active, that was retreived from somewhere else")
        index=self.list()
        if key in index:
            value=index[key].filename
            self.selected = self._rulestype(self,value)
            return self.selected
        else:
            return None
    def _addwithgeocode(self, item, geocode=True):
        # print("3",item)
        if self._ischildtype(item):
            raise ValueError("not destination type")
        self._adddelegate(item)
        verify=self.get(self.childkey(item)) # sets current selection to just added
        if verify==None:
            raise AssertionError("Cannot retrieve what was saved")
        if geocode:
            verify.refreshGeocode()
        return verify

    def _remove(self, key): # either key or item, I assume ambiguity is impossible here
        #need both filename and key
        item=None
        if isinstance(key,str) and key in self.list():
            filename = self.list()[key]
            item=carpooldata.load(filename)
        elif isinstance(key,self._rulestype): #child rules type
            item=key.json
        elif isinstance(key,dict):
            item = key
        else:
            raise ValueError("unknown key" + key)
        if self._ischildtype(item):
            raise ValueError("not " + self.childtype+ " type")
        self._deldelegate(item) # remove json from list!!!!

class destinationlistrules(baselist):
    # The filename is meaningless, the file is hardcoded in the getDestinationDict()
    # I'm too lazy to to make that branch re-useable
    def __init__(self,filename="destindex.json"):
        baselist.__init__(self,filename)
        self.childtype = "destination"
        self._deldelegate = carpooldata.delDestination
        self._adddelegate = carpooldata.addDestination
        self._rulestype = destinationrules
    def childkey(self,item):
        return item["destinationname"]
    def new(self):
        return destinationrules(self,carpooldata.destination(None,None,None))
    def list(self):
        return {k:lazyrulesLoader(self._rulestype,self,k,v) for (k,v) in carpooldata.getDestinationDict().items()}
    def search(self,searchfor):
        for item in self.list():
            destrules = self.get(item)
            destobj = destrules.json #carpooldata.load(destnameindex[item]["url"])
            found = None
            if searchfor in destobj["destinationname"]:
                found = self._highlight("Found [", searchfor, "] in destinationname", destobj["destinationname"])
            elif searchfor in destobj["address"]:
                found = self._highlight("Found [", searchfor, "] in address", destobj["address"])
            elif destobj["geocodefile"] and os.path.exists(destobj["geocodefile"]):
                geocodeobj = carpooldata.load(destobj["geocodefile"])
                result1, result2 = self._jsonsearch(geocodeobj, searchfor)
                if result1 and result2:
                    found = self._highlight("Found [", searchfor, "] in geocode " + result1, result2)
            if not found and destobj["memberlistfile"] and os.path.exists(destobj["memberlistfile"]):
                memberlistobj = carpooldata.load(destobj["memberlistfile"])
                # {"email": "byuan@bcit.ca", "memberfile": "9eab8a5b-b61e-4225-a1a1-9c49c5554cd1member.json"}
                for item2 in memberlistobj:
                    memberobj = carpooldata.load(item2["memberfile"])  # maybe use lockload() here, but reads should always be on a whole file bc of the "bufferserialize()"
                    result1, result2 = self._jsonsearch(memberobj, searchfor)
                    if result1 and result2:
                        found = self._highlight("Found [", searchfor, "] in members " + result1, result2)
                        break
            if found:
                yield found,destrules
    def get(self,key):
        return self._get(key)
    def add(self, item, geocode=True):
        if isinstance(item,destinationrules):
            item = item.json
        if self.childkey(item) in self.list():
            raise ValueError("Error!!!! Car pool destination ["+ item["destinationname"] + "] already used")
        return self._addwithgeocode(item, geocode)
    def remove(self, key): # either key or item, I assume ambiguity is impossible here
        self._remove(key) #remove() -> _remove -> _del (function set in init())


class basechildlist(baselist):
    def __init__(self,parent,filename):
        baselist.__init__(self,filename)
        self.now = datetime.datetime.now()
        self.parent=parent
        # self.filename=filename


class poollistrules(basechildlist):
    def __init__(self,parent,filename):
        basechildlist.__init__(self,parent,filename)
        self.childtype = "pool"
        self._deldelegate = carpooldata.delFromPoolfileList
        self._adddelegate = carpooldata.addToPoolfileList
        self._rulestype = poolrules
    def childkey(self, item):
        raise Exception("There is no user-definable unique identifier for a pool, even the filename combination isn't forced to be unique yet")
    def new(self):
        # newdata = carpooldata.pool(None,selecteddestination,None,None,None,None,None,None,0,selectedpoolormemberlistfile)
        return poolrules(self, carpooldata.pool(None, self.parent.filename, None,None,None,None,None,None,0,self.filename) )
    def list(self):
        #return self.json
        lst=carpooldata.getPoolfileList(self.filename)
        return [ lazyrulesLoader(poolrules,self,i,lst[i]) for i in range(len(lst)) ]
    def search(self, searchfor):
        raise Exception("Not Implemented")
        for item in self.list():
            # {"type": "member", "filename": "e58007f7-a428-4e45-ab03-2aaaad55352dmember.json", "email": "ak@gmail.com", "displayname": "A Kumar", "address": "Executive Suites Hotel & Conference Center, Metro Vancouver, Burnaby", "hascar": "N", "destinationfile": "af12d742-140f-4641-acd1-722096e7d147dest.json"}
            memberrules = self.get(item)
            memberobj = memberrules.json
            found = None
            if searchfor in memberobj["email"]:
                found = self._highlight("Found [", searchfor, "] in destinationname", memberobj["email"])
            elif searchfor in memberobj["displayname"]:
                found = self._highlight("Found [", searchfor, "] in address", memberobj["displayname"])
            elif searchfor in memberobj["address"]:
                found = self._highlight("Found [", searchfor, "] in address", memberobj["address"])
            elif searchfor == "hascar" and memberobj["hascar"].upper() == "Y":
                found = self._highlight("Found [", "hascar", "] in hascar", "hascar")
            elif "geocodefile" in memberobj and memberobj["geocodefile"] != None and os.path.exists(
                    memberobj["geocodefile"]):
                geocodeobj = carpooldata.load(memberobj["geocodefile"])
                result1, result2 = self._jsonsearch(geocodeobj, searchfor)
                if result1 and result2:
                    found = self._highlight("Found [", searchfor, "] in geocode " + result1, result2)
            if found:
                yield found, memberrules
    def get(self, key):
        if isinstance(key,int):
            filename = self.list()[key].filename
            self.selected = poolrules(self,filename)
            return self.selected
        else:
            raise Exception("poollistrules.get() only accepts numbers right now")
        #return self._get(key)
    def add(self, item):
        if isinstance(item, poolrules):
            item = item.json
        self._adddelegate(item)
        return item
    def remove(self, key):  # either key or item, I assume ambiguity is impossible here
        self._remove(key)

class memberlistrules(basechildlist):
    def __init__(self,parent,filename):
        basechildlist.__init__(self,parent,filename)
        self.childtype="member"
        self._deldelegate = carpooldata.delMember
        self._adddelegate = carpooldata.addMember
        self._rulestype = memberrules
    def childkey(self,item):
        return item["email"]
    def new(self):
        #print(type(self.parent))
        #print("new()",self.parent.filename)
        return memberrules(self, carpooldata.member(None,None,None,None,None,self.parent.filename) )
    def list(self):
        #return carpooldata.getMemberDict(self.filename)
        return {k: lazyrulesLoader(memberrules, self,k, v) for (k, v) in carpooldata.getMemberDict(self.filename).items()}
    def search(self,searchfor):
        for item in self.list():
            # {"type": "member", "filename": "e58007f7-a428-4e45-ab03-2aaaad55352dmember.json", "email": "ak@gmail.com", "displayname": "A Kumar", "address": "Executive Suites Hotel & Conference Center, Metro Vancouver, Burnaby", "hascar": "N", "destinationfile": "af12d742-140f-4641-acd1-722096e7d147dest.json"}
            memberrules = self.get(item)
            memberobj = memberrules.json
            found = None
            if searchfor in memberobj["email"]:
                found = self._highlight("Found [", searchfor, "] in destinationname", memberobj["email"])
            elif searchfor in memberobj["displayname"]:
                found = self._highlight("Found [", searchfor, "] in address", memberobj["displayname"])
            elif searchfor in memberobj["address"]:
                found = self._highlight("Found [", searchfor, "] in address", memberobj["address"])
            elif searchfor == "hascar" and memberobj["hascar"].upper() == "Y":
                found = self._highlight("Found [", "hascar", "] in hascar", "hascar")
            elif "geocodefile" in memberobj and memberobj["geocodefile"] != None and os.path.exists(
                    memberobj["geocodefile"]):
                geocodeobj = carpooldata.load(memberobj["geocodefile"])
                result1, result2 = self._jsonsearch(geocodeobj, searchfor)
                if result1 and result2:
                    found = self._highlight("Found [", searchfor, "] in geocode " + result1, result2)
            if found:
                yield found,memberrules
    def get(self, key):
        return self._get(key)
    def add(self, item, geocode=True, suggest=True):
        if isinstance(item,memberrules):
            item = item.json
        #("1",item)
        proposedkey = self.childkey(item)
        existingmembers = self.list()
        if proposedkey in existingmembers:
            raise ValueError("Error!!!! User ["+ item["email"]+ "] exists.  Please re-check.")
        #print("2", item)
        inserteddata =  self._addwithgeocode(item, geocode)
        if suggest:
            destparent = inserteddata.parent.parent
            destparent.refreshMST()
            destparent.refreshSuggest()
        return inserteddata
    def remove(self, key):  # either key or item, I assume ambiguity is impossible here
        self._remove(key)
    def reverseKeyLookup(self,filename):
        for k,v in carpooldata.getMemberDict(self.filename).items():
            if v==filename:
                return k
        return v
class basechild:
    def __init__(self,parent,filename):
        self.now = datetime.datetime.now()
        self.selftype = parent.childtype
        self.parent=parent
        self.filename = filename
        self.userfields=None
        if isinstance(filename,dict):
            self.json = filename
            self.filename = self.json["filename"]
            if "type" in self.json and self.json["type"]!=self.selftype:
                raise ValueError("Wrong type submitted for constructor")
        else:
            self.json = carpooldata.load(filename)
    @staticmethod
    def _isnull(item, key=None):
        if item and key in item and item[key]:
            return False
        else:
            return True
    @staticmethod
    def _ifnull(item, other):
        return item if item else other

    def _isdictequal(self,d,key,value):
        if d!=None and key in d and d[key]==value:
            return True
        else:
            return False
    def _refreshFromService(self,sendmsg,sendmechanism,savenamefactory,referencekey,isstatusable=True):
        item=self.json
        filename = savenamefactory()
        json = sendmechanism(sendmsg, filename)

        if isstatusable and not self._isdictequal(json, "status", "OK"):
            print("Problem response:",json)
            raise ValueError("cannot get status from service, for:"+sendmsg)
        if not self._isdictequal(item, referencekey, filename):
            item[referencekey] = filename
            carpooldata.save(item)  # again
        return json
    def _refreshGeocode(self):
        item=self.json
        if "address" not in item:
            raise TypeError("Only json with string field named Address can be used with _refreshGeocode().  Programmer should be careful")
        geocodefile = self._generateGeocodeFilename()
        proxy = googleproxy()
        json = proxy.getGeocodeFor(item["address"], geocodefile)
        if not self._isdictequal(json, "status", "OK"):
            raise GoogleError("cannot get geocode from google, data saved but no pathing will work w/o coordinates for (user should try another address): "+item["address"])
        if not self._isdictequal(item, "geocodefile", geocodefile):
            item["geocodefile"] = geocodefile
            carpooldata.save(item)  # again
        return json
    def _generateGeocodeFilename(self):
        name, extension = os.path.splitext(self.filename)
        return name+ext.geo
    def save(self):
        carpooldata.save(self.json)
    def remove(self):
        self.parent.remove(self.json)
        # os.remove(self.filename) # it's been coded in the data layer already

class destinationrules(basechild):
    def __init__(self,parent,filename):
        basechild.__init__(self,parent,filename)
        self.userfields = ["destinationname", "address"]
        self._memberlistlazy = None
        self._poollistlazy = None
    def __str__(self):
        return self.json["destinationname"]+"; "+self.json["address"]
    def _isdictequal(self,d,key,value):
        if d!=None and key in d and d[key]==value:
            return True
        else:
            return False
    def memberlist(self):
        if self._memberlistlazy:
            return self._memberlistlazy
        self._memberlistlazy = memberlistrules(self,self.json["memberlistfile"])
        return self._memberlistlazy
    def poollist(self):
        if self._poollistlazy:
            return self._poollistlazy
        self._poollistlazy = poollistrules(self,self.json["poollistfile"])
        return self._poollistlazy
    def save(self):
        if self.isNameUsed():
            raise ValueError("Error!!!! Car pool destination ["+ self.json["destinationname"] + "] already used")
        if self.isAnyUserFieldsMissing():
            raise ValueError("All user fields are not filled for destination")
        basechild.save(self)
    def generateSuggestFilename(self):
        name, extension = os.path.splitext(self.filename)
        return name + ext.pathlist
    def refreshSuggest(self):
        # graph traversal to grouping
        json=self.mstJSON()
        graphing=graphreader(json)
        startgeocode=self.googleGeocodeJSON()
        start=list(coordinate.fromgooglegeocode(startgeocode))
        lastgroup=[]
        groups = [lastgroup]
        lastttl=0
        for item,ttl in graphing.traverseGraph(None,start):
            if item!=start:
                # there is no proven logic to this, it's just better than random grouping
                lastgroup.append(item)
                if len(lastgroup)>=4:
                    lastgroup.append(start)
                    lastgroup = []
                    groups.append(lastgroup)
                lastttl=ttl
        if len(lastgroup)==0:
            groups.remove(lastgroup)
        else:
            lastgroup.append(start)

        # optimize each group
        counter=0
        for item in groups:
            distcalc = distancecalculator()
            pathing = heldkarpe(distcalc.birdfliesdistancematrix(item))
            last = len(item) - 1
            mindistance = pathing.shortest(lambda s: s[last]!=last)
            reordered = list(map(lambda s:item[s], pathing.path))
            groups[counter]=reordered
            counter+=1

        #save
        suggfile = self.generateSuggestFilename()
        if not self._isdictequal(self.json, "suggestfile", suggfile):
            self.json["suggestfile"] = suggfile
            self.save()  # again
        carpooldata.clobberingserialize(groups, suggfile)
        return groups

    def _geocodelist(self):
        graphing = distancecalculator(None)
        lst = []
        index=self.memberlist().list()
        for item in index:
            memberrules = index[item].load()
            geocodeJSON = memberrules.googleGeocodeJSON()
            if self._isdictequal(geocodeJSON,"status","OK"):
                cood = coordinate.fromgooglegeocode(geocodeJSON)
                lst.append(cood)
                # we are ignoring any members w/o geocoding
        return lst
    def generateMstFilename(self):
        name, extension = os.path.splitext(self.filename)
        return name + ext.path
    def refreshMST(self):
        lst = self._geocodelist()
        startgeocode = self.googleGeocodeJSON()
        lst.append(coordinate.fromgooglegeocode(startgeocode))

        # graphing.onprogress = onelineprogress
        graphcalc=graphmaker()
        mstgraph = graphcalc.minimumSpanningTree(lst)
        if mstgraph:
            # write path to jsonfile
            destobj = self.json
            if destobj != None:
                mstfile = self.generateMstFilename()
                if not self._isdictequal(destobj, "mstpathfile", mstfile):
                    destobj["mstpathfile"] = mstfile
                    self.save()  # again
                carpooldata.clobberingserialize(mstgraph, mstfile)
            else:
                raise Exception("The json object should never be empty")

            return mstgraph,self.refreshSuggest()
        else:
            raise Exception("The minimumSpanningTree() returned none")
        return mstgraph,None
    def mstJSON(self): #external json, depend on it, but not intricately
        return None if basechild._isnull(self.json,"mstpathfile") else carpooldata.load(self.json["mstpathfile"])
    def generateGeocodeFilename(self):
        return self._generateGeocodeFilename()
    def refreshGeocode(self):
        return self._refreshGeocode()
    def googleGeocodeJSON(self): #external json, depend on it, but not intricately
        return None if basechild._isnull(self.json,"geocodefile") else carpooldata.load(self.json["geocodefile"])
    def isNameUsed(self):
        data=self.json
        filename=data["filename"]
        name=self.parent.childkey(self.json)
        index=self.parent.list()
        return (name in index and filename!=index[name].filename)
    def isAnyUserFieldsMissing(self):
        return not all(map(lambda s: len(self.json[s]) > 0, self.userfields))

class poolrules(basechild):
    def __init__(self,parent,filename):
        basechild.__init__(self,parent,filename)
        self.userfields = []
        self._lazycache = {}
    def __str__(self):
        lst = map(lambda s:s.load(),self.membersinlist())
        return ", ".join(map(lambda t:t.json["email"],lst))
    def poollistparent(self):
        return self.parent
    def destinationparent(self):
        return self.parent.parent
    def destinationlistparent(self):
        return self.parent.parent.parent
    def keysforsetmember(self):
        return ["member1","member2","member3","member4","member5","member6"]
    def _nextempty(self):
        for item in self.keysforsetmember():
            if not self.json[item]:
                return item
        return None
    def isfull(self):
        return self._nextempty()==None
    def setmember(self,item, overwrite=None):
        if overwrite:
            # is number or key
            if isinstance(overwrite,str) :
                if overwrite not in self.keysforsetmember():
                    raise ValueError("No such field")
            elif isinstance(overwrite,str):
                if not 1<=overwrite<=6:
                    raise Exception("There is no index" + str(overwrite))
                overwrite="member"+str(overwrite)
        else:
            if self.isfull():
                raise ValueError("Pool is full.  pick another or remove")
            overwrite=self._nextempty()
        # print(item)
        if isinstance(item, str) and (item=="" or item in self.parent.parent.memberlist().list()):
            if debugging.on: print("setmember(str) or by email")
            index=self.destinationparent().memberlist().list()
            if item=="" :
                self.json[overwrite] = None
            elif self.isOneEmailValid(item,index):
                filename=index[item].filename # look up email, for filename
                self.json[overwrite]=filename
            else:
                raise ValueError("Could not resolve email address:" + item)
        elif isinstance(item,poolrules):
            if debugging.on: print("setmember(poolrules)")
            self.json[overwrite] = item.filename
        elif isinstance(item,lazyrulesLoader) and item.lazytype==lazyrulesLoader:
            if debugging.on: print("setmember(lazyrulesLoader)")
            self.json[overwrite] = item.filename
        elif isinstance(item,dict) and "type" in item and item["type"]=="member":
            if debugging.on: print("setmember(dict)")
            self.json[overwrite] = item["filename"]
        else:
            raise ValueError("you can only submit a member json, memberrules object, or a email address")
    def isOneEmailValid(self, oneemail, index=None):
        if index == None:
            index = self.destinationparent().memberlist().list()
        return oneemail in index
    def isAllEmailValid(self,emaillist):
        if isinstance(emaillist,list):
            a = set(emaillist)
            b = set(self.destinationparent().memberlist().list().keys())
            invalid = list(a - b - set(['', None]))
            if len(invalid)!=0:
                return invalid
            else:
                return False
        elif isinstance(emaillist,dict):
            keys=set(emaillist.keys())
            expected=set(self.keysforsetmember())
            if keys!=expected:
                raise Exception("Wrong keys in dict:"+(",".join(keys-expected)))
            return self.isAllEmailValid(emaillist.value())
        else:
            raise ValueError("isAllEmailValid() Unrecognized input")
    def isNoRepeatingMembers(self,memberlist):
        filtered=list(filter(lambda s:s,memberlist))
        return len(filtered)==len(set(filtered))
    def save(self, matrixupdate=True):
        basechild.save(self)
        if matrixupdate and self.count()>2:
            self.refreshDistanceMatrix()
    def _lookupformemberbyemail(self,email):
        return self.parent.parent.memberlist().list()[email]
    def _lazymember(self,field): # members1-6 are lazy loaded and linked to this class
        if self._lazycache and field in self._lazycache:
            return self._lazycache[field]
        #self._lazycache[field]=self._lookupformemberbyemail(self.json[field]) #memberrules(self.json[field])
        filename=self.json[field]
        #emailkey = self.destinationparent().memberlist().reverseKeyLookup(filename)
        emailkey=None # using this w/ get is not supported right now
        memberrulesarechildofthis = self.destinationparent().memberlist()
        self._lazycache[field] = lazyrulesLoader(memberrules,memberrulesarechildofthis,emailkey,filename)
        return self._lazycache[field]
    def _ifmemberthen(self,key): #this is to remove redundant lookup code
        item=self.json
        return None if basechild._isnull(item,key) else self._lazymember(key)
    def member1(self):
        return self._ifmemberthen("member1")
    def member2(self):
        return self._ifmemberthen("member2")
    def member3(self):
        return self._ifmemberthen("member3")
    def member4(self):
        return self._ifmemberthen("member4")
    def member5(self):
        return self._ifmemberthen("member5")
    def member6(self):
        return self._ifmemberthen("member6")
    def _ifmemberthenhisemail(self,key,field):
        item=self.json
        memberlistisparent = self.destinationparent().memberlist()
        return None if basechild._isnull(item,key) else memberrules(memberlistisparent,item[key]).json[field]
    def email1(self):
        return self._ifmemberthenhisemail("member1","email")
    def email2(self):
        return self._ifmemberthenhisemail("member2","email")
    def email3(self):
        return self._ifmemberthenhisemail("member3","email")
    def email4(self):
        return self._ifmemberthenhisemail("member4","email")
    def email5(self):
        return self._ifmemberthenhisemail("member5","email")
    def email6(self):
        return self._ifmemberthenhisemail("member6","email")
    def membersinlist(self):
        lst=[self.member1(),self.member2(),self.member3(),self.member4(),self.member5(),self.member6()]
        return list(filter(lambda s:s!=None, lst))
    def count(self):
        return len(self.membersinlist())
    def memberstostrlist(self):
        lst=self.membersinlist()
        return list(map(lambda s:str(s),lst))

    def googledistancematrixJSON(self): #external json, depend on it, but not intricately
        return None if poolrules._isnull(self.json,"matrixfile") else carpooldata.load(self.json["matrixfile"])
    def generateMatrixFilename(self):
        name, extension = os.path.splitext(self.filename)
        return name + ext.matrix
    def refreshDistanceMatrix(self):
        # need to get the actual member addresses
        lst = [self.member1(), self.member2(), self.member3(), self.member4(), self.member5(), self.member6()]
        #more= list(filter(lambda s: s != None, lst))
        justaddress = list(map(lambda s:s.load().json["address"], self.membersinlist()))
        addresslist = [self.destinationparent().json["address"]] + justaddress
        #psv="|".join(addresslist)

        proxy = googleproxy()
        mjson=self._refreshFromService(addresslist,proxy.getDistanceFor,self.generateMatrixFilename,"matrixfile")
        # mjson=self.googledistancematrixJSON()
        if self._isdictequal(mjson, "status", "OK"): # google "rewrites" the addresses, so we need to record the mapping
            if debugging.on: print("Distance Matrix refreshed!!!", mjson)
            origin = mjson["origin_addresses"] #this should be there if OK
            indices = range(len(addresslist))
            self.json["matrixreply"] = list(map(lambda s: (addresslist[s], origin[s]), indices))
            self.save(matrixupdate=False) # we need to lock this write, and save() should do that
        self.refreshPath()
        return mjson
    def generatePathFilename(self):
        name, extension = os.path.splitext(self.filename)
        return name + ext.path
    def refreshPath(self):
        data=self.json
        # checking matrix is consistent w pool... this should always pass if programming was right, but who knows
        inaddr2matrixmap = data["matrixreply"]
        matrixjson = self.googledistancematrixJSON()
        origin = matrixjson["origin_addresses"]
        if len(origin)!=len(inaddr2matrixmap) or origin!=list(map(lambda s:s[1],inaddr2matrixmap)):
            if debugging.on: print("distance matrix does not match recorded reply",origin,data["matrixreply"])
            raise Exception("distance matrix does not match recorded reply (Maybe refreshing the matrix will help)")
        for item in filter(lambda s:s[1]=="",data["matrixreply"]):
            if debugging.on: print("Google distance matrix could not identify address:",item[0])
            raise ValueError("Google distance matrix could not identify address (have user try another address):"+item[0])

        lst=self.membersinlist()
        first = []
        # now we need to derive rules and mapping from indices back to members
        # in: input name : google name
        # out: origin index -- () --> geocode
        matrix2geo = {}
        matrix2member = {}
        for index,value in enumerate(data["matrixreply"]):
            item = value
            inputaddr = item[0]
            googleaddr = item[1]
            if index==0: # first is always destination
                #destrules = self.parent.parent;  # pool<-poolist<-dest
                #destobj = destrules.json
                #matrix2member[index]=destobj
                #geocode = carpooldata.load(destobj["geocodefile"])
                destrules = self.destinationparent()
                matrix2member[index] = destrules.json
                geocode = destrules.googleGeocodeJSON()
                if geocode:
                    matrix2geo[index]=geocode # preparing each address number with coordinates
                else:
                    if debugging.on: print("This address belonging to", destrules.json["destinationname"], " has no geocode for", destrules.json["address"]);
                    raise ValueError("This address belonging to "+ destrules.json["destinationname"]+ " has no geocode for (Can user update address for destination) "+ destobj["address"])
            else:
                memberrulesloader=next(filter(lambda s: s.load().json["address"] == inputaddr, lst),None)
                if memberrulesloader==None:
                    if debugging.on: print("Google replied for", inputaddr, " but cannot find a member in pool w matching address");
                    raise Exception("Google replied for", inputaddr, " but cannot find a member in pool w matching address :"+self.filename)
                memberrulesobj=memberrulesloader.load()
                matrix2member[index] = memberrulesobj.json # attaching indices to member data
                if memberrulesobj.json["hascar"].upper()=="Y": #identifying address numbers that have car, should start path
                    first.append(index)
                geocode = memberrulesobj.googleGeocodeJSON()
                if geocode:
                    matrix2geo[index]=geocode # correlating indices with coordinates
                else:
                    if debugging.on: print("This address belonging to", memberrulesobj.json["displayname"], " has no geocode for", memberrulesobj.json["address"]);
                    raise ValueError("This address belonging to"+ memberrulesobj.json["displayname"]+ " has no geocode for"+memberrulesobj.json["address"]);

        # making sure that we aren't just wasting CPU, by rejecting every path before we start
        if len(first)==0:
            #print("No addresses have cars, ignoring the hascar requirement...")
            first=range(1,len(origin)-2)  # actually last b/c pathing stops at destination, which is always 0
        # everything checks out, run pathing
        pathing = heldkarpe()
        pathing.distance2d = distancecalculator.fromgoogledistancematrix(matrixjson)
        last = len(origin) - 1
        # the criteria is reject any path that doesnt start w 0 (destination),
        # or reject any path that doesnt end w/ number belonging to car driver(first)
        mindistance = pathing.shortest(lambda s: s[0] != 0 or s[last] not in first)
        # restructuring pathing to output to easier to use objects
        #pathing.labels=list(map(lambda s:pathing.fromgooglegeocode(matrix2geo[s]),pathing.path))
        # the matrix2geo should be ordered alrady, as if path is 0,1,2,3...,  it needs to assigned in same order...
        # ...path2segments() will assign to correct order.
        sequence = range(last+1)
        pathing.coordinates=list(map(lambda s:coordinate.fromgooglegeocode(matrix2geo[s]),sequence))
        path=pathing.path2segments()
        # saving to path JSON to file
        pathfile = self.generatePathFilename()
        if not self._isdictequal(data, "pathfile", pathfile):
            data["pathfile"] = pathfile
            carpooldata.save(data)  # again
        carpooldata.clobberingserialize(path, pathfile)

        return pathing

class memberrules(basechild):
    def __init__(self,parent,filename):
        basechild.__init__(self,parent,filename)
        self.userfields = ["email","displayname","address","hascar"]
    def __str__(self):
        return self.json["displayname"]+"; "+self.json["email"]+ "; " +self.json["address"]
    def generateGeocodeFilename(self):
        return self._generateGeocodeFilename()
    def refreshGeocode(self):
        return self._refreshGeocode()
    def googleGeocodeJSON(self): #external json, depend on it, but not intricately
        return None if basechild._isnull(self.json,"geocodefile") else carpooldata.load(self.json["geocodefile"])
    def isAnyUserFieldsMissing(self):
        return not all(map(lambda s: len(self.json[s]) > 0, self.userfields))
    def isEmailUsed(self):
        data=self.json
        email=data["email"]
        filename = data["filename"]
        index=self.parent.list()
        return (data["email"] in index and index[email].filename != filename)
