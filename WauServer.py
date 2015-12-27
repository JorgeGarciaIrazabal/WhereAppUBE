import importlib
import os
import random
import string
import logging
import logging.config
import json
import threading

from tornado import web, ioloop
from wshubsapi.ConnectionHandlers.Tornado import ClientHandler
from wshubsapi.Hub import Hub
from wshubsapi.ValidateStrings import getUnicode
import wshubsapi.utils as wsUtils

abspath = os.path.abspath(__file__)
dirName = os.path.dirname(abspath)
os.chdir(dirName)

wsUtils.DATE_TIME_FORMAT = '%Y/%m/%d %H:%M:%S.%f'

logging.config.dictConfig(json.load(open('logging.json')))
log = logging.getLogger(__name__)

settings = {"static_path": os.path.join(os.path.dirname(__file__), "static"), }


class IndexHandler(web.RequestHandler):
    def get(self):
        self.write("Hello, world")


class UploadHandler(web.RequestHandler):
    def post(self):
        file1 = self.request.files['filearg'][0]
        original_fname = file1['filename']
        extension = os.path.splitext(original_fname)[1]
        fname = ''.join(random.choice(string.ascii_lowercase + string.digits) for x in range(6))
        final_filename = fname + extension
        output_file = open(final_filename, 'w')
        output_file.write(file1['body'])
        self.finish("file" + final_filename + " is uploaded")


class WAUClientHandler(ClientHandler):
    lock = threading.Lock()
    def __init__(self, application, request, **kwargs):
        super(WAUClientHandler, self).__init__(application, request, **kwargs)
        self._commHandler = self.commProtocol.constructCommHandler(self)
        self._commHandler.writeMessage = self.writeMessage
        self.ID = None
        self.isBackground = False

    def open(self, *args):
        with self.lock:
            try:
                args = args[0].split("/")
                id = int(args[0])
                if len(args) > 1:
                    self.isBackground = True
            except:
                id = None

            connections = self._commHandler.connections
            if connections.has_key(id):
                isConnectedABackground = connections[id].client.isBackground
                if isConnectedABackground:
                    background = connections.pop(id)
                    background.ID = str(id) + "_background"
                    connections[background.ID] = background
                    background.client.close(code=9999, reason="")
                    log.warn("Client connected while background " + str(id) + " was connected")
                if self.isBackground and not isConnectedABackground:
                    self.close(code=9999, reason="")
                    log.info("Connected background existing foreground: %s " % getUnicode(id))
                    return
                elif not self.isBackground and not isConnectedABackground:


                    log.warn("Already connected user: %s " % getUnicode(id))
                    connections[id].client.close()
                    del connections[id]
                    return

            self.ID = self._commHandler.onOpen(id)
            clientType = "background" if self.isBackground else "client"
            log.info("open new %s with ID: %s " % (clientType, getUnicode(self.ID)))

    def on_close(self):
        clientType = "background" if self.isBackground else "client"
        log.info("%s closed %s" % (clientType, self._commHandler.__dict__.get("ID", "None")))
        self._commHandler.onClose()


app = web.Application([
    (r'/in', IndexHandler),
    (r'/upload', UploadHandler),
    (r'/(.*)', WAUClientHandler),
    (r'/(.*)/(.*)', WAUClientHandler),
], **settings)

if __name__ == '__main__':
    importlib.import_module("Hubs.Hubs")
    Hub.initHubsInspection()
    Hub.constructJSFile("C:/Software Projects/ionicWAU/www/dependencies")
    Hub.constructPythonFile("DummyClient")
    # Hub.constructJAVAFile("com.application.jorge.whereappu.WebSocket","C:/Software Projects/WhereAppU/app/src/main/java/com/application/jorge/whereappu/WebSocket")
    log.debug("starting...")
    app.listen(8845)
    ioloop.IOLoop.instance().start()
