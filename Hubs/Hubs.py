import os
from sqlalchemy import create_engine
from sqlalchemy.orm import sessionmaker, Session
from DBContext.tables import User, Task, Place
from WSHubsAPI.Hub import Hub

__author__ = 'Jorge'


def getSession():
    """
    :rtype : Session
    """
    engine = create_engine('mysql://root@localhost/wau')
    Session = sessionmaker(bind=engine)
    session = Session()
    session._model_changes = {}
    return session


class LoggingHub(Hub):
    def logIn(self, phoneNumber, gcmId, name=None, email=None):
        session = getSession()
        user = session.query(User).filter_by(PhoneNumber=phoneNumber).first()
        if not user:
            user = User()
        user.Name, user.PhoneNumber, user.Email, user.GCM_ID = name, phoneNumber, email, gcmId
        session.add(user)
        session.commit()
        self.connections[user.ID] = self.connections.pop(self.sender.ID)
        self.connections[user.ID].ID = user.ID
        session.close()
        return user.ID


class SyncHub(Hub):
    def phoneNumbers(self, phoneNumberArray):
        session = getSession()
        users = session.query(User).filter(User.PhoneNumber.in_(phoneNumberArray))
        return users.all()


class PlaceHub(Hub):
    @staticmethod
    def __updatePlaceValues(place, newPlace):
        place.Name = newPlace["Name"]
        place.OwnerId = newPlace["OwnerId"]
        place.Latitude = newPlace["Latitude"]
        place.Longitude = newPlace["Longitude"]
        place.IconURI = newPlace["IconURI"]
        place.Type = newPlace["Type"]
        place.Range = newPlace["Range"]
        place.CreatedOn = newPlace["CreatedOn"]

    def createPlace(self, newPlace):
        session = getSession()
        place = Place()
        self.__updatePlaceValues(place, newPlace)

        session.add(place)
        session.commit()
        session.close()
        return place.ID

    def updatePlace(self, newPlace):
        session = getSession()
        place = session.query(Place).get(newPlace["ID"])
        self.__updatePlaceValues(place, newPlace)
        session.add(place)
        session.commit()
        session.close()
        return place.ID

    def syncPlace(self, newPlace):
        if newPlace["ID"] < 0:
            return self.createPlace(newPlace)
        else:
            return self.updatePlace(newPlace)

    def getPlaces(self, ownerID):
        session = getSession()
        places = session.query(Place).filter_by(OwnerId=ownerID)
        session.close()
        return places.all()


class ChatHub(Hub):
    def sendToAll(self, message):
        self.sender.otherClients.alert(message)


class TaskHub(Hub):
    def addTask(self, newTask):
        session = getSession()
        task = self.cloneTask(newTask)
        session.add(task)
        session.commit()
        if task.CreatorId != task.ReceiverId:
            client = self.getClient(task.ReceiverId)
            if client is not None:
                client.newTask(task)
        session.close()
        return task.ID

    @staticmethod
    def cloneTask(newTask):
        task = Task()
        task.CreatedOn = newTask["CreatedOn"]
        task.CreatorId = newTask["CreatorId"]
        task.ReceiverId = newTask["ReceiverId"]
        task.Body = newTask["Body"]
        task.Type = newTask["Type"]
        if task.Type == task.Types.Place:
            task.LocationId = newTask["LocationId"]
        task.Schedule = newTask["Schedule"]
        return task

    def successfullyReceived(self, taskId):
        session = getSession()
        task = session.query(Task).get(taskId)
        assert isinstance(task, Task)
        if task.CreatorId != task.ReceiverId:
            client = self.getClient(task.CreatorId)
            if client is not None:
                client.confirmReceived(taskId)
        session.close()


class UtilsHub(Hub):
    def setID(self, id):
        assert isinstance(id, int)
        self.connections[id] = self.connections.pop(self.sender.ID)
        self.connections[id].ID = id


path = "C:/Software Projects/WhereAppU/app/src/main/res/drawable-mdpi/"
for fn in os.listdir(path):
    os.rename(path + fn, path + fn.replace("-", "_"))
