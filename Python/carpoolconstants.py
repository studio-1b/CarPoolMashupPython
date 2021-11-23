#carpoolconstants.py

class ext:
    default = ".json"
    dest = "dest.json"  # name and address of a destination
    member = "member.json"  # name, email, address or car pool participant
    destndx = "destindex.json"  # name and filename
    memberndx = "memberindex.json"  # email and filename
    pool = "pool.json"  # contains filename of members of car pool
    poollst = "poollist.json"  # dest has reference to this.  List json of *pool.json
    geo = ".geocode.json"  # google geocode json
    matrix = ".matrix.json"  # google distance matrix json
    path = ".path.json"  # list of coordinates and distance to travel path
    pathlist = ".pathlist.json"  # * list of coordinates and distance to travel path

