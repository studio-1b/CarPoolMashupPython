import os.path
import sys
import math

class progressui:
    def __init__(self, progress=0,maxprogress=0):
        self.progress=progress
        self.maxprogress=progress
        self.onwrite=print
    def write(self):
        self.onwrite("\r", end="")
        self.onwrite(target.progress, "/",target.maxprogress,"   ", end="")
    def writeplus(self, target=None):
        self.progress+=1
        self.write(target)
    def reinit(self, maxprogress):
        if self.progress>=self.maxprogress:
            self.maxprogress=0
            self.progress=0
        self.maxprogress+=maxprogress
    def plus(self,num):
        self.progress+=num

class heldkarpe: #name of a permutation algorithm, not a optimization algorithm
    def __init__(self, distance2d=None):
        self.distance2d=distance2d
        self.length=0
        self.path = None
        self.onsolutionfound=None
        self.N = 0
        self.i = 0
        self.progress=None
        self.labels=None
        self.coordinates = None

    def getprogress(self):
        self.progress = progressui()
        return self.progress
    def offprogress(self):
        self.progress=None

    def __str__(self):
        try:
            labels=self.labels
            coordinates=self.coordinates
            distance2d=self.distance2d
            prev = None
            path = []
            output = []
            if coordinates:
                for item in self.path:
                    if prev != None:
                        a = coordinates[prev]
                        b = coordinates[item]
                        c = distance2d[prev][item]
                        aa = labels[prev] if labels else str(item)
                        bb = labels[item] if labels else str(item)
                        fmt = "{:<20}({:.4f},{:.4f}) {:<20}({:.4f},{:.4f}) {:.2f}km"
                        output.append(fmt.format(aa, a[0], a[1], bb, b[0], b[1], c))
                    prev = item
            else:
                for item in self.path:
                    if prev != None:
                        c = distance2d[prev][item]
                        aa = labels[prev] if labels else str(item)
                        bb = labels[item] if labels else str(item)
                        fmt = "{:<30} {:<30} {:.2f}km"
                        output.append(fmt.format(aa, bb, c))
                    prev = item
            fmt2 = "{:>60} {:.2f}km"
            output.append("-"*70)
            output.append(fmt2.format("",self.length))
            return "\n".join(output)
        except:
            return str(self)
    def getprogress(self):
        self.progress = progressui()
        return self.progress
    def factorial(self,n):
        if n>2:
            return n*self.factorial(n-1)
        elif n == 2:
            return 2
        elif n==1:
            return 1
        elif n<=0:
            return 0

    # this is Held-Karpe
    def permutationlist(self,n):
        if n>1:
            n_1=n-1
            for lst in self.permutationlist(n_1):
                for i in range(0,n_1):
                    cp=lst.copy()
                    cp.insert(i,n_1)
                    yield cp
                cp = lst.copy()
                cp.append(n_1)
                yield cp
        if n==1:
            yield [0]
        return None
    # this is held karpe indexed to 1
    def permutationlist2(self,n):
        if n>1:
            for lst in self.permutationlist(n-1):
                for i in range(0,n-1):
                    cp=lst.copy()
                    cp.insert(i,n)
                    yield cp
                cp = lst.copy()
                cp.append(n)
                yield cp
        if n==1:
            yield [1]
        return None

    def shortest(self, rejectfilter=None):
        if self.progress:
            self.progress.reinit(self.factorial(len(self.distance2d)))

        minimum=sys.maxsize
        dist=self.distance2d
        n=len(dist)
        n_1=n-1
        rangen_1=range(n_1)
        self.N=n
        j=0
        for item in self.permutationlist(n):
            if rejectfilter and rejectfilter(item):
                continue
            j+=1
            self.i=j
            current=self.distance(item)
            #for i in rangen_1:
            #    current+=dist[item[i]][item[i+1]]
            if current<minimum:
                self.path=item
                self.length=current
                minimum=current
                if self.onsolutionfound:
                    self.onsolutionfound(self)
            if self.progress != None:
                self.progress.writeplus()
        return minimum

    def distance(self,path):
        dist = self.distance2d
        n = len(path)
        n_1 = n - 1
        rangen_1 = range(n_1)
        current = 0
        for i in rangen_1:
            current += dist[path[i]][path[i + 1]]
        return current

    def map(self,labels):
        return list(map(lambda s:labels[s], self.path))

    def path2segments(self):
        path = []
        prev=None
        coordinates=self.coordinates
        if coordinates:
            for item in self.path:
                if prev != None:
                    a = coordinates[prev]
                    b = coordinates[item]
                    c = self.distance2d[prev][item]
                    segment = (a, b, c)
                    path.append(segment)
                prev = item
        else:
            for item in self.path:
                if prev != None:
                    a = prev
                    b = item
                    c = self.distance2d[prev][item]
                    segment = (a, b, c)
                    path.append(segment)
                prev = item
        return path

class coordinate:
    def __init__(self,json):
        self.json=json # (a,b)
    def __sub__(self, other):
        return distancecalculator.haversine(self.json[0], self.json[0], other.json[0], other.json[1])

    @staticmethod
    def fromgooglegeocode(json):
        if json["status"]=="OK":
            coordinates=json["results"][0]["geometry"] ["location"]
            return (coordinates["lat"],coordinates["lng"])
        else:
            return None


# This technically is the only class that knows anything about distances and coordinates
# and the interrelationship between them
class distancecalculator:
    def __init__(self, progress=None):
        self.progress = progress

    def getprogress(self):
        self.progress = progressui()
        return self.progress
    def offprogress(self):
        self.progress=None

    # https://www.movable-type.co.uk/scripts/latlong.html
    # I cannot even to begin to explain the math derivation to explain this equation
    @staticmethod
    def haversine(lat1, lon1, lat2, lon2):
        R = 6371e3  # metres
        φ1 = lat1 * math.pi / 180  # φ, λ in radians
        φ2 = lat2 * math.pi / 180
        Δφ = (lat2 - lat1) * math.pi / 180
        Δλ = (lon2 - lon1) * math.pi / 180

        a = math.sin(Δφ / 2) * math.sin(Δφ / 2) + \
            math.cos(φ1) * math.cos(φ2) * \
            math.sin(Δλ / 2) * math.sin(Δλ / 2)

        c = 2 * math.atan2(math.sqrt(a), math.sqrt(1 - a))

        d = R * c  # in metres
        return d

    def birdfliesdistancematrix(self,coordinatelist):
        progress=self.progress
        if progress:
            progress.reinit((len(coordinatelist) * len(coordinatelist) - len(coordinatelist)) / 2)

        l = len(coordinatelist)
        lst = range(l)
        rows=list(map(lambda s:list(range(l)), range(l)))
        for r in lst:
            cols=rows[r]
            for c in lst:
                if c<=r:
                    a = coordinatelist[r]
                    b = coordinatelist[c]
                    if c == r:
                        cols[c]=0.0
                    else:
                        d = distancecalculator.haversine(a[0], a[1], b[0], b[1])
                        cols[c] = d
                        rows[c][r] = d
                    if progress != None:
                        progress.writeplus()
        return rows

    def birdfliesdistancelist(self, coordinatelist):
        progress=self.progress
        if progress:
            progress.reinit((len(coordinatelist)*len(coordinatelist)-len(coordinatelist))/2)

        l=len(coordinatelist)
        lst = range(l)
        table=[]
        for r in lst:
            for c in lst:
                if c<r:
                    a = coordinatelist[r]
                    b = coordinatelist[c]
                    d = self.haversine(a[0],a[1],b[0],b[1])
                    table.append((a,b,d))

                    if progress!=None:
                        self.writeplus()
        return table

    @staticmethod
    def fromgoogledistancematrix(json):
        if json["status"] == "OK" and all(map(lambda s:all(map(lambda t:t["status"]=="OK",s["elements"])),json["rows"])):
            r=json["rows"]
            matrix=list(map(lambda s:list(map(lambda t:t["duration"]["value"],s["elements"])),json["rows"]))
            return matrix
        else:
            return None





class graphmaker:
    def __init__(self):
        self.graph=None
        self.progress = None

    def getprogress(self):
        self.progress = progressui()
        return self.progress
    def offprogress(self):
        self.progress=None


    # technically the coordinate list is a edge list of a pair of vertices.
    # The labels are just coordinates, but could easily be (A,B,10),(B,C,20)
    def minimumSpanningTree(self,coordinatelist):
        if self.progress:
            self.progress.reinit((len(coordinatelist)*len(coordinatelist)-len(coordinatelist))/2)

        distcalc = distancecalculator()
        table=distcalc.birdfliesdistancelist(coordinatelist)
        table.sort(key=lambda s:s[2])
        left = set(coordinatelist)
        used=[]
        i=0
        mst=[]
        while len(left)!=0 or len(used)>1: # every point connected, no closed loops, in 2d space- max 6 w common vertice w hexagon, only 1 graph at end (this is the biggest problem of all of them, since it's possible to have every point used in a graph, but have 2 graphs if they are "bi-modal" arranged)
            span = table[i]
            a = span[0]
            b = span[1]
            aa = None
            bb = None

            for item in used:
                if a in item:
                    aa=item
                    break
            for item in used:
                if b in item:
                    bb=item
                    break
            if aa==None and bb==None: #new graph
                used.append(set([a,b]))
                left.remove(a)
                left.remove(b)
                mst.append(span)
            elif aa==None and bb!=None: # existing bb graph
                bb.add(a)
                left.remove(a)
                mst.append(span)
            elif aa!=None and bb==None: # existing aa graph
                aa.add(b)
                left.remove(b)
                mst.append(span)
            elif aa!=bb: # combine graphs
                used.remove(bb)
                aa|=bb
                mst.append(span)
            # if both are found in same graph, do nothing

            i+=1
            if self.progress!=None:
                self.progress.writeplus()
        else:
            if self.progress!=None:
                self.progress.plus(((len(coordinatelist)*len(coordinatelist)-len(coordinatelist))/2)-i+1)
        # mst=list(used[0])
        return mst

class graphreader:
    def __init__(self,graph):
        self.graph=graph

    # graph is non-continuous [ ((x1,y1),(x2,y2),distance), ((x2,y2),(x3,y3),distance),...]
    def traverseGraph(self, lastedge, lastvertice, ttl=-1):
        return self._traverseGraph(self.graph, lastedge, lastvertice, ttl)
    @staticmethod
    def _traverseGraph(graph, lastedge, lastvertice, ttl=-1):
        if graph==None: raise AssertionError("graph is supposed to be from constructor")
        if ttl==-1: ttl=len(graph)
        if ttl!=0: # in case of bad graph
            less=graph.copy()
            next=list(filter(lambda s:s[0]==lastvertice or s[1]==lastvertice,graph))
            next.sort(key=lambda s: s[2])
            for item in next:
                if item!=lastedge:
                    less.remove(item)
                    other = item[0] if lastvertice==item[1] else item[1]
                    for item2 in graphreader._traverseGraph(less, item, other, ttl-1):
                        yield item2
        yield lastvertice,ttl

if __name__ == '__main__':
    #unit testing or diagnostics, you choose...
    expected=[2,3,4,1,0] #[0,1,4,3,2]
    tester = heldkarpe([[  0,  5,999,999,999],
                        [  5,  0,999,999,  5],
                        [999,999,  0,  5,999],
                        [999,999,  5,  0,  5],
                        [999,  5,999,  5,999]])
    tester.shortest()
    print(expected==tester.path)
    print("expected",expected) #20
    print("actual",tester.path)
    if expected!=tester.path:
        print("expected distance",tester.distance(expected))
        print("expected distance", tester.distance(tester.path))
    # held-karpe shortest() works, unless you changed it


    #filename="f4029073-49ee-4694-8237-7d2525e65485pool.matrix.json"
    filename="donotrun.tmp"
    if os.path.exists(filename):
        from carpooldata import carpooldata
        googlejson=carpooldata.load(filename)
        print(googlejson)
        jaggedarray = distancecalculator.fromgoogledistancematrix(googlejson)
        print(jaggedarray)

        randomresult=[0,1,2,3,4,5,6]
        tester = heldkarpe(jaggedarray)
        tester.shortest(lambda s:s[0]!=0)
        print(randomresult==tester.path)
        print("expected",randomresult) #20
        print("actual",tester.path)
        if expected!=tester.path:
            print("randomresult distance",tester.distance(randomresult))
            print("expected distance", tester.distance(tester.path))

        tester.coordinates=googlejson["destination_addresses"]
        print("actual", tester.path)
        print("actual human format",tester.path2segments())
        # tester.path2segments() works w/o error, unless you changed it
