[X] Static diagram of components (4)
       static dependencies for just static web pages.png
       static dependencies no CLI.png
       static dependencies.png
       carpoolrules class static dependencies.png
[X] One sequence diagram (3)
       sequence of saving a carpool drag drop, from web.png
       sequence of serving a static file.png
       sequence of updating a destination record thru CLI.png
[ ] Static relationship between file types/tables




Installation notes:
---------------------------------------------------------------------------
[X] Document system requires these environment variables to store Google Cloud API Keys
        environment variables.txt
    The javascript keys need to have these settings
        googleapiconsole.png
    The API keys need
        distance matrix
        geocoding
[X] Test script to insert test data, for demonstration of
    Just cut and paste the keystrokes inside each section, to generate data
        CLI testdata script.txt
[X] To run, just goto Python directory and run "python main.py"
    1) The webserver starts immediately, accessible thru url http://localhost/
    2) The CLI menu paused for 2seconds, before outputting initial menu
    2) Press "W" - Enter, to turn off output from web server
    3) Use menu as normal
    4) On windows machine, it will start msedge web browser with http://localhost/
       There should be link at bottom to Car Pool Mashup.  
    5) Web interface can create destinations, add members, define car pools and add members to pools
    6) CLI interface can do all that, and also :
          1) refresh coordinates for Destination Address (geocoding), which give coordinates for web map markers
          2) refresh coordinates for Member Address (geocoding), which give coordinates for web map markers
          3) refresh spanning tree for Destination Members, which give checkbox on web map to draw paths for suggested pools
          4) refresh distance matrix for Pools, which give checkbox on web map to draw shortest driving directions for pool
          5) delete destinations, pools, and members




Checklist of completed functions
---------------------------------------------------------------------------

List Destination CLI
=====================
[X] Add Destination
[X] List Destinations
[X] Update Destinations
[ ] Updating the name should update the index
    This actually really adverely affects delete, as the delete tries to delete the record based on it's key value from the original record, rather than what was used to select the record in the index
    But otherwise, if you prevent them from updating the name, it has no effect.  It's just a bad user experience
    For user to fix, they need to change the destination name back to the way it was, then delete
[X] Search for Destination
[X] Toggle debugging
[X] Quit


Destination Details CLI
=====================
[X] Change Name or Address
[X] View and Manage Car Pool Members
[X] View Car Pool Groups
[ ] View Distance by pools and distance/person
[X] Refresh Geocode
[X] recalculate MST (Spanning Tree)
[X] Quit and Manage to previous menu


Member List CLI
=====================
[X] List Members
[X] Add a new car pool member to destination
[X] Member search
[X] Goto Member Details
[X] Quit

Member Details CLI
=====================
[X] Update Members
[ ] Updating the name should update the index
    same problem deleting, except I haven't written code to allow them to update back
[X] Delete Member from Car Pool Destination
[X] Refresh Geocode
[X] Quit


Pool List CLI
=====================
[X] List Pools
[X] Add pool
    [X] allows you to create a initial list
    [X] add to list and save
[X] Pool Details
[ ] Search for member in pool
[X] Refresh Geocode


Pool Details CLI
=====================
[X] List Members
[X] Add Members to pool
[X] Remove Member from pool
[X] Delete Pool
[X] Refresh Distance Matrix
[X] Recalculate shortest distance


System todo
===========
[ ] delete is incomplete.  There is "file leaks", of left over json files, that were not cleaned up.
    hardly anything to worry about for a test demonstration.
