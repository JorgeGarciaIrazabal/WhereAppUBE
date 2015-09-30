import sys

if sys.version_info[0] == 2:
    input = raw_input

# file created by the server
from WSHubsApi import HubsAPI

if __name__ == '__main__':
    ws = HubsAPI('ws://192.168.1.3:8844/')
    ws.connect()

    ws.UtilsHub.client.messageReceiver = lambda m: sys.stdout.write(m)

    while True:
        message = raw_input("write a message")
        ws.UtilsHub.server.sentToAll(message)
