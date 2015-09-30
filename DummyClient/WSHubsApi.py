import json
import logging
import threading
from threading import Timer
import jsonpickle
from jsonpickle.pickler import Pickler
from ws4py.client.threadedclient import WebSocketClient
from wshubsapi import utils

utils.setSerializerDateTimeHandler()

class WSSimpleObject(object):
    def __setattr__(self, key, value):
        return super(WSSimpleObject, self).__setattr__(key, value)

class WSReturnObject:
    class WSCallbacks:
        def __init__(self, onSuccess=None, onError=None):
            self.onSuccess = onSuccess
            self.onError = onError

    def done(self, onSuccess, onError=None):
        pass

class GenericServer(object):
    __messageID = 0
    __messageLock = threading.RLock()

    def __init__(self, wsClient, hubName, pickler):
        """
        :type wsClient: WSHubsAPIClient
        """
        self.wsClient = wsClient
        self.hubName = hubName
        self.pickler = pickler

    @classmethod
    def _getNextMessageID(cls):
        with cls.__messageLock:
            cls.__messageID += 1
            return cls.__messageID

    def _serializeObject(self, obj2ser):
        return jsonpickle.encode(self.pickler.flatten(obj2ser))


class WSHubsAPIClient(WebSocketClient):
    def __init__(self, api, url, serverTimeout):
        super(WSHubsAPIClient, self).__init__(url)
        self.__returnFunctions = dict()
        self.isOpened = False
        self.serverTimeout = serverTimeout
        self.api = api
        self.log = logging.getLogger(__name__)
        self.log.addHandler(logging.NullHandler())

    def opened(self):
        self.isOpened = True
        self.log.debug("Connection opened")

    def closed(self, code, reason=None):
        self.log.debug("Connection closed with code:\n%s\nAnd reason:\n%s" % (code, reason))

    def received_message(self, m):
        try:
            msgObj = json.loads(m.data.decode('utf-8'))
        except Exception as e:
            self.onError(e)
            return
        if "replay" in msgObj:
            f = self.__returnFunctions.get(msgObj["ID"], None)
            if f and msgObj["success"]:
                f.onSuccess(msgObj["replay"])
            elif f and f.onError:
                f.onError(msgObj["replay"])
        else:
            self.api.__getattribute__(msgObj["hub"]).client.__dict__[msgObj["function"]](*msgObj["args"])
        self.log.debug("Received message: %s" % m.data.decode('utf-8'))

    def getReturnFunction(self, ID):
        """
        :rtype : WSReturnObject
        """

        def returnFunction(onSuccess, onError=None):
            callBacks = self.__returnFunctions.get(ID, WSReturnObject.WSCallbacks())

            def onSuccessWrapper(*args, **kwargs):
                onSuccess(*args, **kwargs)
                self.__returnFunctions.pop(ID, None)

            callBacks.onSuccess = onSuccessWrapper
            if onError is not None:
                def onErrorWrapper(*args, **kwargs):
                    onError(*args, **kwargs)
                    self.__returnFunctions.pop(ID, None)

                callBacks.onError = onErrorWrapper
            else:
                callBacks.onError = None
            self.__returnFunctions[ID] = callBacks
            r = Timer(self.serverTimeout, self.onTimeOut, (ID,))
            r.start()

        retObject = WSReturnObject()
        retObject.done = returnFunction

        # todo create timeout
        return retObject

    def onError(self, exception):
        self.log.exception("Error in protocol")

    def onTimeOut(self, messageId):
        f = self.__returnFunctions.pop(messageId, None)
        if f and f.onError:
            f.onError("timeOut Error")

class HubsAPI(object):
    def __init__(self, url, serverTimeout=5.0, pickler=Pickler(max_depth=4, max_iter=100, make_refs=False)):
        self.wsClient = WSHubsAPIClient(self, url, serverTimeout)
        self.pickler = pickler
        self.SyncHub = self.__SyncHub(self.wsClient, self.pickler)
        self.TaskHub = self.__TaskHub(self.wsClient, self.pickler)
        self.UtilsHub = self.__UtilsHub(self.wsClient, self.pickler)
        self.PlaceHub = self.__PlaceHub(self.wsClient, self.pickler)
        self.UserHub = self.__UserHub(self.wsClient, self.pickler)
        self.LoginHub = self.__LoginHub(self.wsClient, self.pickler)

    def connect(self):
        self.wsClient.connect()


    class __SyncHub(object):
        def __init__(self, wsClient, pickler):
            hubName = self.__class__.__name__[2:]
            self.server = self.__Server(wsClient, hubName, pickler)
            self.client = WSSimpleObject()

        class __Server(GenericServer):
            
            def getNotSyncedEntries(self, tableName, since, usersIds=[]):
                """
                :rtype : WSReturnObject
                """
                args = list()
                args.append(tableName)
                args.append(since)
                args.append(usersIds)
                id = self._getNextMessageID()
                body = {"hub": self.hubName, "function": "getNotSyncedEntries", "args": args, "ID": id}
                retFunction = self.wsClient.getReturnFunction(id)
                self.wsClient.send(self._serializeObject(body))
                return retFunction
        
            def phoneNumbers(self, phoneNumberArray):
                """
                :rtype : WSReturnObject
                """
                args = list()
                args.append(phoneNumberArray)
                id = self._getNextMessageID()
                body = {"hub": self.hubName, "function": "phoneNumbers", "args": args, "ID": id}
                retFunction = self.wsClient.getReturnFunction(id)
                self.wsClient.send(self._serializeObject(body))
                return retFunction
        
            def syncModel(self, tableName, entries, since, usersIds=[]):
                """
                :rtype : WSReturnObject
                """
                args = list()
                args.append(tableName)
                args.append(entries)
                args.append(since)
                args.append(usersIds)
                id = self._getNextMessageID()
                body = {"hub": self.hubName, "function": "syncModel", "args": args, "ID": id}
                retFunction = self.wsClient.getReturnFunction(id)
                self.wsClient.send(self._serializeObject(body))
                return retFunction
        
    class __TaskHub(object):
        def __init__(self, wsClient, pickler):
            hubName = self.__class__.__name__[2:]
            self.server = self.__Server(wsClient, hubName, pickler)
            self.client = WSSimpleObject()

        class __Server(GenericServer):
            
            def getNotUpdatedTasks(self, since, userId):
                """
                :rtype : WSReturnObject
                """
                args = list()
                args.append(since)
                args.append(userId)
                id = self._getNextMessageID()
                body = {"hub": self.hubName, "function": "getNotUpdatedTasks", "args": args, "ID": id}
                retFunction = self.wsClient.getReturnFunction(id)
                self.wsClient.send(self._serializeObject(body))
                return retFunction
        
            def syncTask(self, newTask):
                """
                :rtype : WSReturnObject
                """
                args = list()
                args.append(newTask)
                id = self._getNextMessageID()
                body = {"hub": self.hubName, "function": "syncTask", "args": args, "ID": id}
                retFunction = self.wsClient.getReturnFunction(id)
                self.wsClient.send(self._serializeObject(body))
                return retFunction
        
            def syncTasks(self, tasks):
                """
                :rtype : WSReturnObject
                """
                args = list()
                args.append(tasks)
                id = self._getNextMessageID()
                body = {"hub": self.hubName, "function": "syncTasks", "args": args, "ID": id}
                retFunction = self.wsClient.getReturnFunction(id)
                self.wsClient.send(self._serializeObject(body))
                return retFunction
        
            def writingTo(self, userId, start):
                """
                :rtype : WSReturnObject
                """
                args = list()
                args.append(userId)
                args.append(start)
                id = self._getNextMessageID()
                body = {"hub": self.hubName, "function": "writingTo", "args": args, "ID": id}
                retFunction = self.wsClient.getReturnFunction(id)
                self.wsClient.send(self._serializeObject(body))
                return retFunction
        
    class __UtilsHub(object):
        def __init__(self, wsClient, pickler):
            hubName = self.__class__.__name__[2:]
            self.server = self.__Server(wsClient, hubName, pickler)
            self.client = WSSimpleObject()

        class __Server(GenericServer):
            
            def sentToAll(self, message):
                """
                :rtype : WSReturnObject
                """
                args = list()
                args.append(message)
                id = self._getNextMessageID()
                body = {"hub": self.hubName, "function": "sentToAll", "args": args, "ID": id}
                retFunction = self.wsClient.getReturnFunction(id)
                self.wsClient.send(self._serializeObject(body))
                return retFunction
        
            def setId(self, id):
                """
                :rtype : WSReturnObject
                """
                args = list()
                args.append(id)
                id = self._getNextMessageID()
                body = {"hub": self.hubName, "function": "setId", "args": args, "ID": id}
                retFunction = self.wsClient.getReturnFunction(id)
                self.wsClient.send(self._serializeObject(body))
                return retFunction
        
    class __PlaceHub(object):
        def __init__(self, wsClient, pickler):
            hubName = self.__class__.__name__[2:]
            self.server = self.__Server(wsClient, hubName, pickler)
            self.client = WSSimpleObject()

        class __Server(GenericServer):
            
            def createPlace(self, newPlace):
                """
                :rtype : WSReturnObject
                """
                args = list()
                args.append(newPlace)
                id = self._getNextMessageID()
                body = {"hub": self.hubName, "function": "createPlace", "args": args, "ID": id}
                retFunction = self.wsClient.getReturnFunction(id)
                self.wsClient.send(self._serializeObject(body))
                return retFunction
        
            def getPlaces(self, ownerId):
                """
                :rtype : WSReturnObject
                """
                args = list()
                args.append(ownerId)
                id = self._getNextMessageID()
                body = {"hub": self.hubName, "function": "getPlaces", "args": args, "ID": id}
                retFunction = self.wsClient.getReturnFunction(id)
                self.wsClient.send(self._serializeObject(body))
                return retFunction
        
            def syncPlace(self, newPlace):
                """
                :rtype : WSReturnObject
                """
                args = list()
                args.append(newPlace)
                id = self._getNextMessageID()
                body = {"hub": self.hubName, "function": "syncPlace", "args": args, "ID": id}
                retFunction = self.wsClient.getReturnFunction(id)
                self.wsClient.send(self._serializeObject(body))
                return retFunction
        
            def updatePlace(self, newPlace):
                """
                :rtype : WSReturnObject
                """
                args = list()
                args.append(newPlace)
                id = self._getNextMessageID()
                body = {"hub": self.hubName, "function": "updatePlace", "args": args, "ID": id}
                retFunction = self.wsClient.getReturnFunction(id)
                self.wsClient.send(self._serializeObject(body))
                return retFunction
        
    class __UserHub(object):
        def __init__(self, wsClient, pickler):
            hubName = self.__class__.__name__[2:]
            self.server = self.__Server(wsClient, hubName, pickler)
            self.client = WSSimpleObject()

        class __Server(GenericServer):
            
            def isConnected(self, id):
                """
                :rtype : WSReturnObject
                """
                args = list()
                args.append(id)
                id = self._getNextMessageID()
                body = {"hub": self.hubName, "function": "isConnected", "args": args, "ID": id}
                retFunction = self.wsClient.getReturnFunction(id)
                self.wsClient.send(self._serializeObject(body))
                return retFunction
        
            def syncUser(self, user):
                """
                :rtype : WSReturnObject
                """
                args = list()
                args.append(user)
                id = self._getNextMessageID()
                body = {"hub": self.hubName, "function": "syncUser", "args": args, "ID": id}
                retFunction = self.wsClient.getReturnFunction(id)
                self.wsClient.send(self._serializeObject(body))
                return retFunction
        
    class __LoginHub(object):
        def __init__(self, wsClient, pickler):
            hubName = self.__class__.__name__[2:]
            self.server = self.__Server(wsClient, hubName, pickler)
            self.client = WSSimpleObject()

        class __Server(GenericServer):
            
            def login(self, phoneNumber, name=None, email=None):
                """
                :rtype : WSReturnObject
                """
                args = list()
                args.append(phoneNumber)
                args.append(name)
                args.append(email)
                id = self._getNextMessageID()
                body = {"hub": self.hubName, "function": "login", "args": args, "ID": id}
                retFunction = self.wsClient.getReturnFunction(id)
                self.wsClient.send(self._serializeObject(body))
                return retFunction
        
