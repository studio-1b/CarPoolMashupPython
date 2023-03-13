# This is a sample Python script.
import socket, time
import sys
import os
import threading
import subprocess
import platform
import requests   #native python HTTP request maker (not custom receiver, like below)
from request import HttpRequest
from server import HttpServer
from response import HttpResponse
from staticfileserver import httpstaticfilehandler
from scriptengine import PythonScriptHandler


from debugging import debugging
#from carpooldata import carpooldata
#from googleproxy import googleproxy
#from heldkarpe import heldkarpe
from carpoolrules import *

from paramikoIO import ParamikoIO
from paramikoServer import ParamikoServer


def make_request(url):
    response = requests.get(url)
    if response.status_code == 200:
    	return response.text
    return None

def get_ip():
    s = socket.socket(socket.AF_INET, socket.SOCK_DGRAM)
    try:
        # doesn't even have to be reachable
        s.connect(('10.255.255.255', 1))
        IP = s.getsockname()[0]
    except Exception:
        IP = '127.0.0.1'
    finally:
        s.close()
    return IP

class config:
    index_port = 1
    index_path = 2
    def __init__(self, arg):
        self.listeningPort = 80
        self.hostedFilesPath = "."
        self.message = None
        self.sshdPort = None

        l = len(arg)
        if l >= 2:
            try:
                self.listeningPort = int(arg[config.index_port])
                if 1 <= self.listeningPort <=65535:
                    self.message = "Enter port number between 0 and 65535"
            except ValueError:
                self.message = "Port number must be integer"
        if l >= 3:
            try:
                self.hostedFilesPath = arg[config.index_path]
                if not os.path.exists(self.hostedFilesPath):
                    self.message = "Cannot verify [" + self.hostedFilesPath + "] exists"
            except ValueError:
                self.message = "Something went wrong when checking directory path where files are hosted"
        for i in range(l):
            # sshd port starts with -ssh
            sw=arg[i]
            if sw=="-ssh":
                self.sshdPort=22
                break
            elif sw.startswith("-ssh:"):
                port=sw[5:]
                if not str.isnumeric(port):
                    self.message="The SSH listening port should be numeric"
                else:
                    self.sshdPort = int(port)
                    if 1 <= self.sshdPort <=65535:
                        self.message = "Enter sshd port number between 0 and 65535"
                break



def threadedClient(server,conn,address,handlerlist):
    buffersize = 512
    data = conn.recv(buffersize)
    builder = [data]
    buffer = data
    while len(buffer) == buffersize:
        if debugging.on: print(".", end="")
        buffer = conn.recv(buffersize)
        builder.append(buffer)
    if len(builder) > 1:
        data = b"".join(builder)
        if debugging.on: print(".")

    if debugging.web: print("Incoming Stream:", data)

    request = None
    try:
        request = HttpRequest(server, data)
        request.remoteAddress = address[0]
        request.remotePort = address[1]
    except Exception:
        if debugging.on: print("Error occurred processing request")
        tmpresponse = HttpResponse(conn)
        try:
            tmpresponse.setInternalError500()
        except Exception:
            if debugging.on: print("Error occurred trying to send 500 error")
        conn.close()
        return
    response = HttpResponse(conn, request)
    for handler in handlerlist:
        if handler.ishandle(request):
            if debugging.on: print("request will be handled by...", handler.name)
            try:
                handler.execute(request, response)
            except Exception:
                response.setInternalError500()
            break
    else:
        if debugging.on: print("No handler for prev request")
        response.setNotFound404()

    # conn.sendall("Hello world".encode())
    conn.close()

running=True
globalsocket=None
def threadedServer():
    global running
    global globalsocket
    startup = config(sys.argv)
    print("Port:", startup.listeningPort)
    print("Serving files in:", startup.hostedFilesPath)

    with socket.socket(socket.AF_INET, socket.SOCK_STREAM) as soc:
        try:
            globalsocket = soc
            # With the help of bind() function
            # binding host and port
            soc.bind(("0.0.0.0", startup.listeningPort))

        except socket.error as message:
            # if any error occurs then with the
            # help of sys.exit() exit from the program
            if debugging.on: print('Bind failed. Error Code : '
                  + str(message[0]) + ' Message '
                  + message[1])
            sys.exit()

        server = HttpServer(startup)

        # print if Socket binding operation completed
        print('Socket binding operation completed')
        print("local interface", soc.getsockname()[0])
        hostname = socket.gethostname()
        print("hostname:", hostname)
        ip_address = socket.gethostbyname(hostname)
        print("ip:", ip_address)
        routable = get_ip()
        print("routerable:", routable)
        server.localAddress = routable

        # With the help of listening () function
        # starts listening

        handlerlist = [httpstaticfilehandler(), PythonScriptHandler()]
        handlerlist[0].cacheExpiration = 3600

        if debugging.on: print("before listen")
        soc.listen()
        while running:
            conn=None
            address=None
            if debugging.on: print("before accept")
            try:
                conn, address = soc.accept()
            except Exception as ex:
                if debugging.on: print("ERROR on soc.accept():", ex)
                continue
            if debugging.on: print("after accept")

            # print the address of connection
            if debugging.on: print('Connected with ' + address[0] + ':' + str(address[1]))

            thr = threading.Thread(target=threadedClient, args=(server,conn, address,handlerlist,), kwargs={})
            thr.start()



############################################3


appstate = destinationlistrules()


def delpoolmenu():
    global appstate
    #global selecteddestination
    #global selecteddestinationheader
    #global selectedpool

    destrules = appstate.selected
    destobj = destrules.json
    poollistrules = destrules.poollist()
    #poollistobj = poollistrules.list()
    poolrules = poollistrules.selected
    data = poolrules.json


    print()
    print("=========================================================")
    print("Deleting car pool [",str(poolrules),"]")
    print("from [", destobj["destinationname"], "]")
    print("=========================================================")
    print()

    # this is where you can add a : Are you sure?

    #carpooldata.delFromPoolfileList(poolobj)  # it's poollistfile is a attribute, for reverse lookup
    try:
        poolrules.remove()
        print("Deleted!")
    except Exception as ex:
        print("\nThere might have been a problem\n", ex)
        time.sleep(3000)
    return poollistmenu


def pooldistancematrixmenu():
    global appstate

    destrules = appstate.selected
    destobj = destrules.json
    poollistrules = destrules.poollist()
    #poollistobj = poollistrules.list()
    poolrules = poollistrules.selected
    data = poolrules.json

    print("=========================================================")
    print("  Refreshing Distance Matrix for Pool")
    print(" Destination [", destobj["destinationname"], "]")
    print("=========================================================")
    print()
    print()
    print("Members (getting distances) for:")
    print("   ", poolrules.email1())
    print("   ", poolrules.email2())
    print("   ", poolrules.email3())
    print("   ", poolrules.email4())
    print("   ", poolrules.email5())
    print("   ", poolrules.email6())
    print()

    try:
        json=poolrules.refreshDistanceMatrix()
        if json and "status" in json and json["status"]=="OK":
            print("Distance Matrix refreshed!!!",json)
        else:
            print("\nThere might have been a problem w address\n",json)
            time.sleep(3000)
    except GoogleError:
        print("\nNo data returned from Google.  Please re-check connectivity.\n", ex)
        time.sleep(3000)
    except Exception as ex:
        print("\nThere might have been a problem\n", ex)
        time.sleep(3000)

    print()

    return pooldetailsmenu


def poolpathmenu():
    global appstate
    #global selecteddestination
    #global selecteddestinationheader
    #global selectedpoolormemberlistfile
    #global selectedpool

    destrules = appstate.selected
    destobj = destrules.json
    poollistrules = destrules.poollist()
    poollistobj = poollistrules.list()
    poolrules = poollistrules.selected
    data = poolrules.json

    #data = carpooldata.load(selectedpool)
    #destobj = carpooldata.load(selecteddestination)

    print("=========================================================")
    print("  Recalculating shortest distance for Pool")
    print(" Destination [", destobj["destinationname"], "]")
    print("=========================================================")
    print()

    print("Refreshing path....")
    path = poolrules.refreshPath()
    try:
        path=poolrules.refreshPath()
        if path:
            print()
            print(path)
            print()
            print("Finished!  Saved!")
    except Exception as ex:
        print("\nUnknown problem pathing",ex,"\n\n")
        time.sleep(3000)

    return pooldetailsmenu


def pooldetailsmenu():
    global appstate
    #global selecteddestination
    #global selecteddestinationheader
    #global selectedpoolormemberlistfile
    #global selectedpool

    destrules = appstate.selected
    destobj = destrules.json
    poollistrules = destrules.poollist()
    #poollistobj = poollistrules.list()
    poolrules = poollistrules.selected
    #poolobj = poolrules.json

    #poolobj = carpooldata.load(selectedpool)
    #if debugging.on: print("still on dest", selecteddestination)
    #destobj=carpooldata.load(selecteddestination)
    #memberlistindex = carpooldata.getMemberDict(destobj["memberlistfile"])
    # memberlistindex = destrules.memberlist().list()

    selection = ""
    nonupdateable = ["type", "filename", "destinationfile", "matrixfile", "pathfile", "progress", "poollistfile"]
    while selection != "Q":
        print()
        print("=========================================================")
        print("Car pool group management SUB-MENU for [", destobj["destinationname"], "]")
        print("=========================================================")
        print()
        print("1.........[", poolrules.email1(),"]")
        print("2.........[", poolrules.email2(),"]")
        print("3.........[", poolrules.email3(),"]")
        print("4.........[", poolrules.email4(),"]")
        print("5.........[", poolrules.email5(),"]")
        print("6.........[", poolrules.email6(),"]")
        print("M.........Refresh Distance (M)atrix")
        print("P.........Recalculate (P)ath")
        print()
        print("D.........(D)elete this car pool group")
        print("          But it's members' information is not deleted")
        print()
        print("Q.........(Q)uit")
        print()
        selection = None
        while selection not in ["1", "2", "3", "4", "5", "6", "S", "D", "M", "P", "Q"]:
            selection = input("Pick menu choice>").upper()

        promptdict = {"1": poolrules.email1(), "2": poolrules.email2(), "3": poolrules.email3() \
                    , "4": poolrules.email4(), "5": poolrules.email5(), "6": poolrules.email6()}
        prompt = "{:.<30}>"
        if selection in ["1", "2", "3", "4", "5", "6"]:
            if promptdict[selection]!=None and promptdict[selection]!="":
                print("Enter e-mail address of member that is going to be replaced")
                print("or leave blank to remove existing member")
                emailaddress = input(prompt.format("["+promptdict[selection]+"]"))
            else:
                print("Enter e-mail address of member")
                emailaddress = input(prompt.format("[]"))
                print("you entered",emailaddress)
            if emailaddress=="" or poolrules.isOneEmailValid(emailaddress):
                # this indirect form of input is b/c the member fields arent user input but reference to other files
                # so the input needs to be stored and translated
                poolrules.setmember(emailaddress.strip(), "member" + selection)
                poolrules.save()
                #carpooldata.save(poolobj)
                print("Saved!")
            else:
                print("ERROR!  Validation problems:")
                print("email address doesn't belong to a car pool participant")
        elif selection=="D":
            return delpoolmenu
        elif selection=="M":
            return pooldistancematrixmenu
        elif selection == "P":
            return poolpathmenu
    return poollistmenu

def addpoolmenu():
    global appstate
    #global selecteddestination
    #global selecteddestinationheader
    #global selectedpool
    #global selectedpoolormemberlistfile

    destrules = appstate.selected
    destobj = destrules.json
    poollistrules = destrules.poollist()
    #poollistobj = poollistrules.list()

    print()
    print("=========================================================")
    print("Adding NEW Car pool to [", destobj["destinationname"], "]")
    print("=========================================================")
    #newdata = carpooldata.pool(None,selecteddestination,None,None,None,None,None,None,0,selectedpoolormemberlistfile)
    poolrules = poollistrules.new()
    email = {}   #poolrules.json()

    # need destination to validate the new members
    #destobj = carpooldata.load(selecteddestination)
    #memberlistrules = destrules.memberlist()
    #memberlistindex = memberlistrules.list()

    yn = "n"
    while yn != "y":
        print("Enter email addresses for members in this pool (up to 6):")
        for item in poolrules.keysforsetmember():
            email[item] = input("{:.<15}{}".format(item, ">"))
        invalid = poolrules.isAllEmailValid(list(email.values()))
        if invalid:
            print("Validation problems, unable to find these email :")
            print("Do they exist as members?  Have them register")
            print(invalid)
            yn = input(
                "Not every field needs to be filled, but they all have to be valid members.  Do you wish to abort data entry \n(y, anything else retries)?").lower()
        elif not poolrules.isNoRepeatingMembers(list(email.values())):
            print("Validation problems:")
            yn = input("Email was entered more than once. Do you wish to abort data entry \n(y, anything else retries)?").lower()
        else:
            # convert all the email addresses to filenames
            for item in poolrules.keysforsetmember():
                if email[item]:
                    poolrules.setmember(email[item],item)
            if debugging.on: print("Trying to insert...", email)
            try:
                poollistrules.add(poolrules)
                #carpooldata.addToPoolfileList(newdata)
                # save destpoollistfile too.
                print("\nSaved!\n")
            except Exception as ex:
                print("\nThere was a problem, and we don't know what to do, so feel free and knock yourself and keep trying\n",ex)
                time.sleep(3000)
            yn = "y"

    return poollistmenu


def searchpoolmenu():
    global appstate
    global selecteddestinationheader
    global selectedpoolormemberlistfile
    global selectedpool

    print("searchpoolmenu NOT IMPLEMENTED YET")

    return poollistmenu

def isempstr(value):
    if value==None:
        return True
    elif len(value)==0:
        return True
    return False

selectedpool=None
def poollistmenu():
    global appstate
    #global selecteddestinationheader
    #global selectedpoolormemberlistfile
    #global selectedpool
    choices = {"Q":destinationmenu, "A":addpoolmenu,"/":searchpoolmenu}
    parameters = {}

    destrules = appstate.selected
    destobj = destrules.json
    poollistrules = destrules.poollist()
    poollistobj = poollistrules.list()

    #poollistobj = carpooldata.load(selectedpoolormemberlistfile,False)
    #if debugging.on: print(" poollistmenu() loading poolist file",selectedpoolormemberlistfile)
    l=len(poollistobj)
    perpage=10
    start=0
    while True:
        print()
        print("=========================================================")
        print("Car pool group management MENU for [",destobj["destinationname"],"]")
        print("Number of pools ({}-{}/{})".format(start+1,min(l,start+perpage),l))
        print("=========================================================")
        print()
        print("/.........Search for a member")
        print("A.........(A)dd a car pool group, to destination")
        print("U.........Page (U)p")
        print("D.........Page (D)own")
        print()
        end=start+perpage
        if end>=l:
            end=l
        for i in range(0,l):
            choices[str(i+1)] = pooldetailsmenu
            parameters[str(i+1)] = i #poollistobj[i]

        for i in range(start,end):
            poolrules = None
            try:
                poolrules = poollistobj[i].load()  # carpooldata.load(poollistobj[i])
                if poolrules==None:
                    raise Exception
            except Exception as ex:
                print("Problem we don't what to do",ex)
                print("ERROR: file not found",poollistobj[i].filename)
                continue
            #poolobj = poolrules.json
            #email1 = "" if isempstr(poolobj["member1"]) else poolrules.member1().json["email"]
            #email2 = "" if isempstr(poolobj["member2"]) else poolrules.member2().json["email"]
            #email3 = "" if isempstr(poolobj["member3"]) else poolrules.member3().json["email"]
            #email4 = "" if isempstr(poolobj["member4"]) else poolrules.member4().json["email"]
            #email5 = "" if isempstr(poolobj["member5"]) else poolrules.member5().json["email"]
            #email6 = "" if isempstr(poolobj["member6"]) else poolrules.member6().json["email"]
            poolid=str(poolrules)
            print("{}.........{}".format(i+1,poolid))
            #print("{}.........{} {} {} {} {} {}".format(i + 1, email1, email2, email3, email4, email5, email6))
            # choices[str(i+1)] = memberdetailsmenu
            # parameters[str(i+1)] = destobj[keys[i]]["memberfile"]
        print()
        print("Q.........(Q)uit to Previous menu")

        selection=None
        while selection not in choices:
            selection = input("Pick menu choice>").upper()
            if selection.upper()=="U":
                if start-perpage>=0:
                    start-=perpage
                break;
            elif selection.upper()=="D":
                if start+perpage>=0:
                    start+=perpage
                break;
        if selection in parameters:
            #selectedpool = parameters[selection]
            poollistrules.get(parameters[selection])
            print("getting pool",parameters[selection])
            print(poollistrules.selected)
        if selection in choices:
            break;
    return choices[selection]

def delmembermenu():
    global appstate
    #global selectedmember
    #global selectedmemberdata
    #global selecteddestinationheader
    #olddata = selectedmemberdata

    destrules = appstate.selected
    destobj = destrules.json
    memberlistrules = destrules.memberlist()
    memberrules=memberlistrules.selected
    olddata = memberrules.json

    print()
    print("================================================")
    print("Deleting MEMBER going to destination[", destobj["destinationname"], "]")
    print(olddata["displayname"])
    print(olddata["email"])
    print(olddata["address"])
    print("================================================")
    print("....")
    try:
        memberrules.remove();
        print("deleted!")
    except Exception as ex:
        print()
        print("Error detected, and we don't know what to do with it",ex)
        print()
        time.sleep(5)
    return memberlistmenu

def updatemembermenu():
    global appstate
    #global selecteddestinationheader
    #global selectedmember
    #global selectedmemberdata
    #olddata = selectedmemberdata
    #newdata = carpooldata.member("*", None, None, None, None, None)

    destrules = appstate.selected
    destobj = destrules.json
    memberlistrules = destrules.memberlist()
    memberrules=memberlistrules.selected
    olddata = memberrules.json

    print("=========================================================")
    print("Updating [",olddata["displayname"],"] for [", destobj["destinationname"], "]")
    print("=========================================================")

    yn = "n"
    while yn != "y":
        counter = 0
        while yn != "y":
            for item in memberrules.userfields:
                changes = input("{:.<20}{:.>20}]{}".format(item, "[" + olddata[item], ">"))
                if len(changes.strip()) != 0:
                    olddata[item] = changes.strip()
                    counter += 1
            if counter == 0:
                print()
                print("No changes recorded")
                print()
                time.sleep(5)
                yn = "y"
            else:
                # memberindex = carpooldata.getMemberDict(olddata["destinationfile"]);
                if memberrules.isEmailUsed():
                    print()
                    print("Error!!!! E-mail address [", olddata["email"],
                          "] already exists, and is taken already.  You cannot use same e-mail for car pool member participants.")
                    print()
                    time.sleep(5)
                    yn = "y"
                else:
                    if debugging.on: print("Trying to update...", olddata)
                    #carpooldata.save(olddata)
                    try:
                        memberrules.save()
                        print()
                        print("Saved!")
                        print()
                    except GoogleError:
                        print("\nSaved, but trouble getting new Geocode from google")
                        print("Re-establish connection, and refresh the geocode for this member\n")
                        time.sleep(3)
                    except Exception as ex:
                        print("\nThere might have been a problem",ex,"\n")
                        time.sleep(3)
                    yn = "y"
    return memberdetailsmenu

#selectedmemberdata=None
def memberdetailsmenu():
    global appstate
    #global selectedmember
    #global selectedmemberdata
    #olddata = carpooldata.load(selectedmember)
    #selectedmemberdata = olddata

    destrules = appstate.selected
    destobj = destrules.json
    memberlistrules = destrules.memberlist()
    memberrules=memberlistrules.selected
    olddata = memberrules.json

    choices = {"U": updatemembermenu, "D": delmembermenu, "G": membergeocodemenu,"Q":memberlistmenu}
    parameters = {}
    print("=========================================================")
    print("  Member Details")
    print(" [",olddata["displayname"],"] to [", destobj["destinationname"], "]")
    print("=========================================================")
    print()
    for item in memberrules.userfields:
        print("{:.<30}{:.>30}".format(item,olddata[item]))
    print()
    print("U.........(U)pdate Member information")
    print("D.........(D)elete Member, including participating in car pool")
    print("G.........Refresh (G)eocode")
    print()
    print("Q.........(Q)uit to Previous menu")

    selection = None
    while selection not in choices:
        selection = input("Pick menu choice>").upper()
    #if selection in parameters:
    #    #selectedmember = parameters[selection]

    return choices[selection]

def membergeocodemenu():
    global appstate
    #global selectedmember
    #global selectedmemberdata
    #global selecteddestinationheader

    destrules = appstate.selected
    destobj = destrules.json
    memberlistrules = destrules.memberlist()
    memberrules=memberlistrules.selected
    data = memberrules.json

    print("=========================================================")
    print("  Member Geocode refresh")
    print(" [", data["displayname"],"] to [", destobj["destinationname"], "]")
    print("=========================================================")
    print()

    try:
        json=memberrules.refreshGeocode()
        if json:
            print("Member Geocode refreshed!!!",json)
        else:
            raise GoogleError("No response returned")
    except GoogleError:
        print("Unable to get data from Google.  Please re-establish connection and retry.",json)
        time.sleep(3)
    except Exception as ex:
        if debugging.on: raise ex
        print("There might have been a problem", ex)
        time.sleep(3)
    print()
    return memberdetailsmenu

def addmembermenu():
    global appstate
    #global selecteddestinationheader
    #global selecteddestination
    destrules = appstate.selected
    destobj = destrules.json
    memberlistrules = destrules.memberlist()

    print()
    print("=========================================================")
    print("Adding NEW Member for [",destobj["destinationname"],"]")
    print("=========================================================")
    #newdata = carpooldata.member(None,None,None,None,None,None)
    #newdata["destinationfile"] = selecteddestination
    newdatarules = memberlistrules.new()
    newdata = newdatarules.json

    yn="n"
    while yn!="y":
        for item in newdatarules.userfields:
            newdata[item]=input("{:.<15}{}".format(item,">"))
        if not newdatarules.isAnyUserFieldsMissing():
            if not newdatarules.isEmailUsed():
                if debugging.on: print("Trying to insert...",newdata)
                #carpooldata.addMember(newdata)
                try:
                    memberlistrules.add(newdata)
                    print("Saved!")
                except GoogleError:
                    print("Saved, but Unable to contact Google Geoservices.")
                    print("Please refresh Geocode after re-establishing connectivity to ... https://maps.googleapis.com")
                    time.sleep(3)
                except Exception as ex:
                    print("Error!", ex)
                    time.sleep(3)
            else:
                print()
                print("Error!!!! User [",newdata["email"],"] exists.  Please re-check.")
                print()
                time.sleep(5)
            yn="y"
        else:
            yn = input("Every field is required.  Do you wish to abort data entry \n(y, anything else retries)?").lower()

    return memberlistmenu


def searchmembermenu():
    global appstate
    #global selectedpoolormemberlistfile
    #global selectedmember
    destrules = appstate.selected
    destobj = destrules.json
    memberlistrules = destrules.memberlist()

    choices = {"Q":memberlistmenu}
    parameters = {}
    memberlistindexobj = memberlistrules.list()
    print()
    print("==============================================================")
    print("Car Pool, Search Members going to ["+destobj["destinationname"]+"]")
    print("==============================================================")
    print()
    print("Search looks in all fields")
    searchfor = input("Enter search term>")
    print()
    print("Looking for [",searchfor,"]")
    print()
    counter=0
    # email,memberfile
    #for item in memberlistindexobj:
    for blurb,item in memberlistrules.search(searchfor):
        key=memberlistrules.childkey(item.json)    # item.json["email"]
        #{"type": "member", "filename": "e58007f7-a428-4e45-ab03-2aaaad55352dmember.json", "email": "ak@gmail.com", "displayname": "A Kumar", "address": "Executive Suites Hotel & Conference Center, Metro Vancouver, Burnaby", "hascar": "N", "destinationfile": "af12d742-140f-4641-acd1-722096e7d147dest.json"}
        print("{}.........Goto member menu [{}]".format(counter+1,item.json["displayname"]))
        print(blurb)
        choices[str(counter+1)]=memberdetailsmenu
        parameters[str(counter+1)]=key # get will accept lazyloader  #memberlistindexobj[item]
        counter+=1
    print("Q.........(Q)uit to Previous menu")
    print()
    selection = input("Pick menu choice>").upper()
    counter=0
    while selection not in choices:
        selection = input("Pick menu choice>").upper()
    if selection in parameters:
        memberlistrules.get(parameters[selection])
        #selectedmember = parameters[selection]
    return choices[selection]


def mstmenu():
    global appstate
    #global selecteddestination
    #global selecteddestinationheader
    #global selectedpoolormemberlistfile

    destrules = appstate.selected
    destobj = destrules.json
    # memberlistrules = destrules.memberlist()
    # memberlistindexobj = memberlistrules.list()

    print()
    print("=========================================================")
    print(" Generating Spanning Tree MENU for [",destobj["destinationname"],"]")
    print("=========================================================")
    print()
    graphjson, pathjson = destrules.refreshMST()
    #graphing.onprogress = onelineprogress
    try:
        graphjson,pathjson = destrules.refreshMST()

        if graphjson:
            print("Spanning Tree Created!",graphjson)
            if debugging.on: print(destobj["mstpathfile"])
        else:
            print("Error, mstmenu() could not regenerate Minimum spanning Tree")
            time.sleep(3000)
        if pathjson:
            print("Suggest Saved!",pathjson)
            if debugging.on: print(destobj["mstpathfile"])
        else:
            print("Error, mstmenu() could not regenerate Minimum spanning Tree")
            time.sleep(3000)
    except Exception as ex:
        print("Error, Unexpected error", ex)
        time.sleep(3000)
    print()

    return destinationmenu


# selectedmember=None
def memberlistmenu():
    global appstate
    #global selectedpoolormemberlistfile
    #global selectedmember
    choices = {"Q":destinationmenu, "A":addmembermenu,"/":searchmembermenu}
    parameters = {}

    destrules = appstate.selected
    destobj=destrules.json
    memberlistrules = destrules.memberlist()
    memberlistindexobj = memberlistrules.list()
    keys=list(memberlistindexobj.keys())
    l=len(keys)
    perpage=10
    start=0

    while True:
        print()
        print("=========================================================")
        print("Member list management MENU for [",destobj["destinationname"],"]")
        print("Number of members ({}-{}/{})".format(start+1,min(l,start+perpage),l))
        print("=========================================================")
        print()
        print("/.........Search for a member")
        print("A.........(A)dd a new car pool member to destination")
        print("U.........Page (U)p")
        print("D.........Page (D)own")
        print()
        end=start+perpage
        if end>=l:
            end=l
        for i in range(0,l):
            choices[str(i+1)] = memberdetailsmenu
            parameters[str(i+1)] = keys[i]
        for i in range(start,end):
            memberrules = memberlistrules.get(keys[i])   #  carpooldata.load(memberlistindexobj[keys[i]])
            member = memberrules.json
            found = ""
            if debugging.on:
                if memberrules.googleGeocodeJSON():
                    found = "*"

            print("{:.<10}.........{} ({}){}".format(i+1,member["displayname"],member["email"],found))
            # choices[str(i+1)] = memberdetailsmenu
            # parameters[str(i+1)] = destobj[keys[i]]["memberfile"]
        print()
        print("Q.........(Q)uit to Previous menu")

        selection=None
        while selection not in choices:
            selection = input("Pick menu choice>").upper()
            if selection.upper()=="U":
                if start-perpage>=0:
                    start-=perpage
                break;
            elif selection.upper()=="D":
                if start+perpage<l:
                    start+=perpage
                break;
        if selection in parameters:
            #selectedmember = parameters[selection]
            memberlistrules.get(parameters[selection])
        if selection in choices:
            break;
    return choices[selection]


#selectedpoolormemberlistfile=None
#selecteddestinationheader=None
#selecteddestination=None
def destinationmenu():
    global appstate
    #global selecteddestination
    #global selecteddestinationheader
    #global selectedpoolormemberlistfile
    choices = {"Q": menu,"C":updatedestinationmenu,"D":deldestinationmenu,"M": memberlistmenu, "P":poollistmenu, "G":destgeocodemenu, "S":mstmenu }

    destrules=appstate.selected
    destobj = destrules.json
    selecteddestinationheader = destobj["destinationname"]

    parameters = {"C":destobj,"D":destobj,"M":destobj["memberlistfile"],"P":destobj["poollistfile"],"G":destobj["geocodefile"]}

    print()
    print("================================================")
    print("Car Pool MENU for[",selecteddestinationheader,"]")
    print(destobj["address"])
    print("================================================")
    print()
    print("C.........(C)hange Name or Address")
    print("D.........(D)elete this destination")
    print("M.........View and Manage Car Pool (M)embers")
    print("P.........View Car (P)ool Groups")
    print("G.........Refresh (G)eocode")
    print("S.........Refresh (S)panning Tree")
    print("Q.........(Q)uit and Manage to previous menu")
    print()
    selection = input("Pick menu choice>").upper()
    while selection not in choices:
        selection = input("Pick menu choice>").upper()
    #if selection in parameters:
    #    selectedpoolormemberlistfile = parameters[selection]
    return choices[selection]

def destgeocodemenu():
    global appstate
    #global selecteddestination
    #global selecteddestinationheader
    #global selectedpoolormemberlistfile

    destrules = appstate.selected
    destobj = destrules.json


    print()
    print("================================================")
    print("Refreshing Geocode for[",destobj["destinationname"],"]")
    print(destobj["address"])
    print("================================================")
    print()
    try:
        json=destrules.refreshGeocode()
        if json:
            print("Dest Geocode refreshed!!!",json)
        else:
            raise GoogleError("No response received")
    except GoogleError:
        print("Unable to contact google, please re-establish connectivity")
        time.sleep(3)
    except Exception as ex:
        if debugging.on: raise ex
        print("There might have been a problem",ex)
        time.sleep(3)

    return destinationmenu

def deldestinationmenu():
    global appstate
    #global selecteddestination
    #global selecteddestinationheader
    #global selectedpoolormemberlistfile
    #olddata = selectedpoolormemberlistfile
    destinationrules = appstate.selected
    destinationjson = destinationrules.json

    print()
    print("================================================")
    print("Deleting car pool destination[", destinationjson["destinationname"], "]")
    print(destinationjson["address"])
    print("================================================")
    print("....")
    destinationrules.remove()
    #appstate.remove(destinationjson)
    #carpooldata.delDestination(olddata);
    print("deleted!")

    return menu

def updatedestinationmenu():
    global appstate
    #global current
    #global selecteddestination
    #global selecteddestinationheader
    #global selectedpoolormemberlistfile
    #olddata = selectedpoolormemberlistfile
    # olddata = current.getDestination()
    #newdata = carpooldata.destination("*", None, None) # * put as filename so it can't be saved accidentally, it has to be merged
    destrules = appstate.selected
    olddata = appstate.selected.json

    print()
    print("================================================")
    print("Update information for car pool destination[", olddata["destinationname"], "]")
    print(olddata["address"])
    print("================================================")
    print("Leave blank for no changes")
    yn="n"
    counter=0
    while yn!="y":
        for item in destrules.userfields:
            changes=input("{:.<20}{:.>20}]{}".format(item,"["+olddata[item],">"))
            if len(changes.strip())!=0:
                olddata[item]=changes.strip()
                counter+=1
        if counter==0:
            print()
            print("No changes recorded")
            print()
            time.sleep(5)
            yn = "y"
        else:
            destindex = appstate.list();
            # the filename should be "primary key"-like, but destinationname is also supposed to be unique
            # so they are supposed to match, and the filename is not user-updateable
            # The UI doesn't allow you to "blank" data
            if destrules.isNameUsed():
                print()
                print("Error!!!! Car pool destination [", olddata["destinationname"], "] already exists, and is taken already.  You cannot use same name for 2 destinations.")
                print()
                time.sleep(5)
            else:
                if debugging.on: print("Trying to update...", olddata)
                destrules.save()
                print("Saved!")
                yn="y"

    return destinationmenu


def adddestinationmenu():
    global appstate
    print()
    print("======================")
    print("Adding NEW Destination")
    print("======================")
    #newdata = carpooldata.destination(None,None,None)
    newdestination = appstate.new()
    newdata = newdestination.json
    yn="n"
    while yn!="y":
        for item in newdestination.userfields:
            newdata[item]=input("{:.<20}{}".format(item,">"))

        if not newdestination.isAnyUserFieldsMissing():
            if not newdestination.isNameUsed():
                try:
                    appstate.add(newdata)
                    print("Saved!")
                    yn="y"
                except GoogleError:
                    print("Saved, but unable to get coordinates for address for google.")
                    print("Please re-establish connectivity and refresh geocode")
                    yn = "y"
                    time.sleep(3)
                except Exception as ex:
                    print("Error encountered during save.",ex)
                    yn = "y"
                    time.sleep(3)
            else:
                print()
                print("Error!!!! Car pool destination [", newdata["destinationname"],
                      "] already exists, and is taken already.  You cannot use same name for 2 destinations.")
                print()
                time.sleep(5)
        else:
            yn = input("Every field is required.  Do you wish to abort data entry \n(y, anything else retries)?").lower()
    return menu

def searchdestmenu():
    global appstate
    #global current
    #global selecteddestination

    choices = {"Q":menu}
    parameters = {}
    #destnameindex = carpooldata.getDestinationDict()
    print()
    print("==============================================================")
    print("Car Pool, Search Destinations")
    print("==============================================================")
    print()
    print("Search looks in all fields")
    searchfor = input("Enter search term>")
    print()
    print("Looking for [",searchfor,"]")
    print()
    counter=0
    for blurb,item in appstate.search(searchfor):
        key=item.json["destinationname"]
        print("{}.........Goto destination menu [{}]".format(counter+1,key))
        print(blurb)
        choices[str(counter+1)]=destinationmenu
        parameters[str(counter+1)]=key
        counter+=1
    print("Q.........(Q)uit to Previous menu")
    print()
    selection = input("Pick menu choice>").upper()
    counter=0
    while selection not in choices:
        selection = input("Pick menu choice>").upper()
    if selection in parameters:
        #selecteddestination = parameters[selection]
        appstate.get(parameters[selection])
    return choices[selection]

def toggledebugging():
    debugging.on = not debugging.on
    print("Debugging messages turned on [",debugging.on,"]")
    return menu
def togglewebrequestoutput():
    debugging.web = not debugging.web
    print("Web requests turned on [",debugging.on,"]")
    return menu


def menu():
    global appstate
    #global current
    #global selecteddestination
    choices = {"Q":None,"/":searchdestmenu,"A":adddestinationmenu,"D":toggledebugging,"W":togglewebrequestoutput}
    parameters = {}
    submenu = appstate.list()
    print()
    print("=============")
    print("Car Pool MENU")
    print("=============")
    print("A.........(A)dd Destination")
    print("/.........Search Destination by text")
    counter=0
    for item in submenu:
        found=""
        if debugging.on:
            #obj=carpooldata.load(submenu[item])
            destrules=appstate.get(item)
            if destrules.googleGeocodeJSON():
                found="*"
        print("{}.........Update destination [{}]{}".format(counter+1,item,found))
        choices[str(counter+1)]=destinationmenu
        parameters[str(counter+1)]=item #submenu[item]
        counter+=1
    print("D.........Toggle (D)ebugging[",debugging.on,"]")
    print("W.........Toggle (W)eb input[", debugging.web, "]")
    print("Q.........(Q)uit")
    print()
    selection = input("Pick menu choice>").upper()
    while selection not in choices:
        selection = input("Pick menu choice>").upper()
    if selection in parameters:
        #selecteddestination = parameters[selection]
        appstate.get(parameters[selection])
    return choices[selection]



def carpoolSshdGreetHandler(server, e):
    t,chan = e
    chan.send("\r\n\r\n" + server.servername)
    chan.send("\r\n\r\nThis is the SSH control for Carpool Mashup!\r\n\r\n")
    chan.send("It isn't the best console\r\n")
    chan.send("But maybe good enough is ok\r\n")
    chan.send("It only supports single user\r\n")

def clientHandler(server,e):
    input,output = e
    #chan = output.ch

    #sshclient=ParamikoIO()
    sys.stdout=output
    sys.stdin=input
    #sys.stderr=output

    #output.write("Type anything and result will be echoed back:\r\n")
    #output.write("Press ESC to exit\r\n")

    clientstate=currentstate
    while clientstate!=None:
        clientstate=clientstate()
        output.write("\r\n")
        # New guy always kicks
        # previous guy.  
        # Unless we replace print in menus

    #pressed=""
    #while pressed!=b'\x1b': #esc exits SSH
    #    pressed = input.read()
    #    if pressed == b"\r":
    #        output.write("\r\n")
    #    output.write(pressed.decode())

    output.write(" Bye Bye.\r\n")
    output.close()

    sys.stderr.write("client left")
    #print("client left")





# Press the green button in the gutter to run the script.
if __name__ == '__main__':
    if "USER" in os.environ:
        print("Running as:")
        print(os.environ["USER"])
        print()

    thr = threading.Thread(target=threadedServer, args=(), kwargs={})
    thr.start()

    # The front-end is implemented using a finite state machine idea...
    time.sleep(2)
    print("starting, browser")
    if platform.system()=="Windows":
        subprocess.call(["cmd","/c","start msedge http://localhost"])



    startuparg = config(sys.argv)
    if startuparg.sshdPort!=None:
        sshd=ParamikoServer()
        sshd.ongreet=carpoolSshdGreetHandler
        sshd.onclientready=clientHandler
        sshd.start("",startuparg.sshdPort)


    print("CLI running...")
    currentstate = menu
    while currentstate!=None:
        currentstate = currentstate()


    running=False
    if globalsocket!=None:
        try:
            # sending last request, to unblock tcp wait in server thread
            if startuparg.listeningPort == 80:
                make_request("http://localhost")
            else:
                make_request("http://localhost:" + str(startuparg.listeningPort))
            globalsocket.close()
        except Exception as ex:
            print("Expected error received trying to close socket...")
        finally:
            print()
            print("web server stopped")

    if startuparg.sshdPort!=None:
        sshd.stop()
        try:
            make_request("http://localhost:" + str(startuparg.sshdPort))
        except Exception as ex:
            pass
        finally:
            print("SSH stopped")


    print()
    print("Bye bye!")


