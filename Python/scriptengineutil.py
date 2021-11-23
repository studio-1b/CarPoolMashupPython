class scriptengineutil:
    def __init__(self, request, response):
        self.request = request
        self.response = response
    def stream(self, filename,replacedict):
        buffer=""
        with open(filename, 'r') as reader:
            buffer = reader.read()
        for key in replacedict:
            token2 = "<!--@" + key + "/-->"
            if token2 in buffer:
                buffer = buffer.replace(token2, replacedict[key])
            token="@" + key + "/"
            if token in buffer:
                buffer = buffer.replace(token,replacedict[key])

        self.response.stream(buffer.encode())
