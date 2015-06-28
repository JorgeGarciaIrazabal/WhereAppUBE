import importlib
import os
import random
import string
import logging
import logging.config
import json

from tornado import web, ioloop
from WSHubsAPI.ConnectionHandlers.Tornado import ClientHandler
from WSHubsAPI.Hub import Hub

logging.config.dictConfig(json.load(open('logging.json')))
log = logging.getLogger(__name__)

settings = {"static_path": os.path.join(os.path.dirname(__file__), "static"), }


class IndexHandler(web.RequestHandler):
    def get(self):
        self.render("index.html")

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

app = web.Application([
    (r'/in', IndexHandler),
    (r'/(.*)', ClientHandler),
    (r'/upload', UploadHandler),
], **settings)

if __name__ == '__main__':
    importlib.import_module("Hubs.Hubs")
    # HubDecorator.constructJSFile(settings["static_path"])
    Hub.initHubsInspection()
    Hub.constructJAVAFile("com.application.jorge.whereappu.WebSocket","C:/Software Projects/WhereAppU/app/src/main/java/com/application/jorge/whereappu/WebSocket")
    log.debug("starting...")
    app.listen(8888)
    ioloop.IOLoop.instance().start()
