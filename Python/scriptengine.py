import importlib
import os
import time
import datetime
from request import HttpRequest
from response import HttpResponse
from staticfileserver import httphandler
from debugging import debugging

class PythonScriptHandler:
    def __init__(self):
        self.name = "[write python programs]"

    def ishandle(self, request):
        filename = request.virtualpath
        name, ext = os.path.splitext(filename)
        if filename==0:
            return False
        elif filename[0] != "/":
            return False
        elif filename[-6:].lower() == "cgi.py":
            return True
        else:
            return False

    def execute(self, request, response):
        depth = request.virtualpath.count("/")
        if depth>1 or request.virtualpath[0] != "/":
            response.setInternalError500("<html><body>This web server does not support virtual directories")
        else:
            filename = request.virtualpath[1:]
            if debugging.web: ("searching...", filename)
            if os.path.isfile(filename):
                classname,ext = os.path.splitext(filename)
                if debugging.web: print("stripping off .py extension, to load...", classname, ext)
                try:
                    mime = httphandler.contentType[".html"]
                    response.setContentType(mime)

                    runtime_module = importlib.import_module(classname)
                    if debugging.web: print("looking for class...", classname)
                    webscriptclass = getattr(runtime_module, classname)
                    if debugging.web: print("instantiating...", classname)
                    webscript = webscriptclass()
                    if debugging.web: print("executing...", classname)
                    webscript.execute(request,response)
                    if debugging.web: print("flushing buffers...")
                    if not response._headerssent:
                        response.setContentLength(response._bufferin)
                    response.send()
                except Exception as ex:
                    if debugging.web: print("Error in PythonScriptHandler:",ex)
                    response.setInternalError500("<html><body>500 is the euphemism that we messed up our code somewhere")
            else:
                response.setNotFound404()

