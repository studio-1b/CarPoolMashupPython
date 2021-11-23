import os
import datetime
import time
from request import HttpRequest
from response import HttpResponse

from debugging import debugging

class httphandler:
    # https://developer.mozilla.org/en-US/docs/Web/HTTP/Basics_of_HTTP/MIME_types/Common_types
    contentType = {".aac":"audio/aac",
        ".abw":"application/x-abiword",
        ".arc":"application/x-freearc",
        ".avi":"video/x-msvideo",
        ".azw":"application/vnd.amazon.ebook",
        ".bin":"application/octet-stream",
        ".bmp":"image/bmp",
        ".bz":"application/x-bzip",
        ".bz2":"application/x-bzip2",
        ".cda":"application/x-cdf",
        ".csh":"application/x-csh",
        ".css":"text/css",
        ".csv":"text/csv",
        ".doc":"application/msword",
        ".docx":"application/vnd.openxmlformats-officedocument.wordprocessingml.document",
        ".eot":"application/vnd.ms-fontobject",
        ".epub":"application/epub+zip",
        ".gz":"application/gzip",
        ".gif":"image/gif",
        ".htm":"text/html",
        ".html": "text/html",
        ".ico":"image/vnd.microsoft.icon",
        ".ics":"text/calendar",
        ".jar":"application/java-archive",
        ".jpeg":"image/jpeg",
        ".jpg": "image/jpeg",
        ".js":"text/javascript",
        ".json":"application/json",
        ".jsonld":"application/ld+json",
        ".mid":"audio/midi",
        ".midi": "audio/x-midi",
        ".mjs":"text/javascript",
        ".mp3":"audio/mpeg",
        ".mp4":"video/mp4",
        ".mpeg":"video/mpeg",
        ".mpkg":"application/vnd.apple.installer+xml",
        ".odp":"application/vnd.oasis.opendocument.presentation",
        ".ods":"application/vnd.oasis.opendocument.spreadsheet",
        ".odt":"application/vnd.oasis.opendocument.text",
        ".oga":"audio/ogg",
        ".ogv":"video/ogg",
        ".ogx":"application/ogg",
        ".opus":"audio/opus",
        ".otf":"font/otf",
        ".png":"image/png",
        ".pdf":"application/pdf",
        ".php":"application/x-httpd-php",
        ".ppt":"application/vnd.ms-powerpoint",
        ".pptx":"application/vnd.openxmlformats-officedocument.presentationml.presentation",
        ".rar":"application/vnd.rar",
        ".rtf":"application/rtf",
        ".sh":"application/x-sh",
        ".svg":"image/svg+xml",
        ".swf":"application/x-shockwave-flash",
        ".tar":"application/x-tar",
        ".tif .tiff":"image/tiff",
        ".ts":"video/mp2t",
        ".ttf":"font/ttf",
        ".txt":"text/plain",
        ".vsd":"application/vnd.visio",
        ".wav":"audio/wav",
        ".weba":"audio/webm",
        ".webm":"video/webm",
        ".webp":"image/webp",
        ".woff":"font/woff",
        ".woff2":"font/woff2",
        ".xhtml":"application/xhtml+xml",
        ".xls":"application/vnd.ms-excel",
        ".xlsx":"application/vnd.openxmlformats-officedocument.spreadsheetml.sheet",
        ".xml":"application/xml",
        ".xul":"application/vnd.mozilla.xul+xml",
        ".zip":"application/zip",
        ".3gp":"video/3gpp",
        ".3g2":"video/3gpp2",
        ".7z":"application/x-7z-compressed",
    }

    def __init__(self):
        self.name = "base class"
    def getContentType(self,ext):
        if ext in httphandler.contentType:
            return httphandler.contentType[ext]
        else:
            return None

    def ishandle(self, request):
        return False

    def execute(self,request,response):
        html = b"<html><head><title>No handler defined</title></head><body><h1>hello world</h1></body></html>"
        response.setContentLength(len(html))
        response.setContentType(httphandler.contentType[".htm"])
        response.send()
        return

class httpstaticfilehandler:
    def __init__(self):
        self.name = "[static file server, no directory support]"
        self.cacheExpiration=0

    def ishandle(self, request):
        filename = request.virtualpath
        name, ext = os.path.splitext(filename)
        if filename==0:
            return False
        elif filename[0] != "/":
            return False
        elif filename[-1] == "/":
            return True
        elif not ext in httphandler.contentType:
            return False
        else:
            return True

    def execute(self, request, response):
        # ignore the method and always process as GET
        depth = request.virtualpath.count("/")
        if depth>1 or request.virtualpath[0] != "/":
            response.setInternalError500("<html><body>This web server does not support virtual directories")
        else:
            filename = request.virtualpath[1:]
            if len(filename)==0:
                filename = request.server.defaultFile
                if debugging.web: print("using default file")
            if os.path.isfile(filename):
                contentlen = os.path.getsize(filename)
                response.setContentLength(contentlen)
                name,ext = os.path.splitext(filename)
                if ext in httphandler.contentType:
                    mime = httphandler.contentType[ext]
                    response.setContentType(mime)
                    if self.cacheExpiration>0:
                        try:
                            lastmod=os.path.getmtime(filename)
                            epoch=time.time()
                            age=int(epoch - lastmod)
                            expdate = datetime.datetime.now() + datetime.timedelta(0, self.cacheExpiration-age)
                            lastmod2 = datetime.datetime.now() - datetime.timedelta(0, age)
                            response.setHeader("age", "{}".format(age))
                            response.setHeader("Cache-Control","max-age={}".format(self.cacheExpiration))
                            response.setHeader("expires", "{}".format(expdate.strftime(HttpResponse.HEADER_DATE_FMT)))
                            response.setHeader("last-modified", "{}".format(lastmod2.strftime(HttpResponse.HEADER_DATE_FMT)))
                        except:
                            if debugging.web: print("Ignored Error in calculating expiration date for:", filename)
                    if debugging.web: print("opening...",filename)
                    try:
                        with open(filename, 'rb') as reader:
                            buffersize=4096
                            buffer = reader.read(buffersize)
                            response.stream(buffer)
                            while len(buffer)==buffersize:
                                buffer = reader.read(buffersize)
                                response.stream(buffer)
                    except:
                        if debugging.on: print("We could pretend we know exactly what we're doing here, but that would be dishonest, so you might as well start panicing")
                else:
                    response.setInternalError500("<html><body>We don't recognize the extension of the file you requested, and though we could give it to you and not send the header, we're just going to ignore you, and pretend we don't understand")
            else:
                response.setNotFound404()
