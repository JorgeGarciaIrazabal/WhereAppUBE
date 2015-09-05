from datetime import datetime

from sqlalchemy import or_
from wshubsapi.Hub import Hub

from DBContext.DataBaseHelper import DataBaseHelper
from DBContext.tables import User, Task, Place

__author__ = 'Jorge'

# This is a throwaway variable to deal with a python bug
throwaway = datetime.strptime('20110101', '%Y%m%d')


getSession = DataBaseHelper.getSession


def getDateTime(dateStr):
    if dateStr is None: return None
    return datetime.strptime(dateStr, '%Y/%m/%d %H:%M:%S %f')


class LoggingHub(Hub):
    def logIn(self, phoneNumber, name=None, email=None):
        with getSession() as session:
            user = session.query(User).filter_by(PhoneNumber=phoneNumber).first()
            if not user:
                user = User()
            user.Name, user.PhoneNumber, user.Email = name, phoneNumber, email
            session.add(user)
            session.commit()
            self.connections.pop(self.sender.ID)
            self.sender.client.ID = user.ID
            self.sender.ID = user.ID
            self.connections[user.ID] = self.sender
            return user.ID


class SyncHub(Hub):
    def phoneNumbers(self, phoneNumberArray):
        session = getSession()
        users = session.query(User).filter(User.PhoneNumber.in_(phoneNumberArray))
        return users.all()


class PlaceHub(Hub):
    @staticmethod
    def __updatePlaceValues(place, newPlace):
        if place is None: place = Place()
        place.Name = newPlace["Name"]
        place.OwnerId = newPlace["OwnerId"]
        place.Latitude = newPlace["Latitude"]
        place.Longitude = newPlace["Longitude"]
        place.IconURI = newPlace["IconURI"]
        place.Type = newPlace["Type"]
        place.Range = newPlace["Range"]
        place.CreatedOn = getDateTime(newPlace["CreatedOn"])
        place.DeletedOn = getDateTime(newPlace["DeletedOn"])
        return place

    def createPlace(self, newPlace):
        with  getSession() as session:
            place = Place.insertFormDict(session, newPlace)
            session.commit()
            return place.ID

    def updatePlace(self, newPlace):
        with  getSession() as session:
            place = Place.updateFormDict(session, newPlace)
            session.commit()
            return place.ID

    def syncPlace(self, newPlace):
        if newPlace["ID"] < 0:
            return self.createPlace(newPlace)
        else:
            return self.updatePlace(newPlace)

    def getPlaces(self, ownerID):
        session = getSession()
        places = session.query(Place).filter(Place.OwnerId == ownerID)
        session.close()
        return places.all()


class TaskHub(Hub):
    def syncTasks(self, tasks):
        idsCorrelation = list()
        with getSession() as session:
            try:
                for task in tasks:
                    try:
                        newTaskId = self.__syncTask(task, session)
                        idsCorrelation.append([task["ID"], newTaskId])
                    except:
                        pass
                session.commit()
            except:
                session.rollback()
            return idsCorrelation

    def getNotUpdatedTasks(self, since, userId):
        with getSession() as session:
            return session.query(Task).filter(Task.UpdatedOn > getDateTime(since),
                                              or_(Task.ReceiverId == userId,
                                                  Task.CreatorId == userId)).all()

    def syncTask(self, newTask):
        with getSession() as session:
            try:
                self.__syncTask(newTask,session)
                session.commit()
            except Exception as e:
                session.rollback()

    def __syncTask(self, newTask, session):
        if newTask["ID"] < 0:
            return self.__createTask(newTask, session)
        else:
            return self.__updateTask(newTask, session)

    def __updateTask(self, newTask, session):
        task = Task.updateFormDict(session,newTask)
        session.add(task)
        session.flush()
        otherClientId = task.CreatorId if self.sender.ID == task.ReceiverId else task.ReceiverId
        self.getClient(otherClientId).taskUpdated(task)
        return task.ID

    def __createTask(self, newTask, session):
        task = Task.insertFormDict(session,newTask)
        session.flush()
        if task.CreatorId != task.ReceiverId:
            self.getClient(task.ReceiverId).newTask(task)
        return task.ID

class UtilsHub(Hub):
    def setId(self, id):
        assert isinstance(id, (int, long))
        self.connections.pop(self.sender.ID)
        self.sender.client.ID = id
        self.sender.ID = id
        self.connections[id] = self.sender

