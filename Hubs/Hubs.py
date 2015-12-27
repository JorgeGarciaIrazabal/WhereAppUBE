from datetime import datetime

from sqlalchemy import or_
from wshubsapi.Hub import Hub

from DBContext.DataBaseHelper import DataBaseHelper
from DBContext.tables import User, Task, Place, Base

__author__ = 'Jorge'

# This is a throwaway variable to deal with a python bug
throwaway = datetime.strptime('20110101', '%Y%m%d')

getSession = DataBaseHelper.getSession


def getDateTime(dateStr):
    if dateStr is None: return None
    try:
        return datetime.strptime(dateStr, '%Y/%m/%d %H:%M:%S %f')
    except ValueError as e:
        return datetime.strptime(dateStr, "%Y-%m-%dT%H:%M:%S.%fZ")


class LoginHub(Hub):
    def login(self, phoneNumber, name=None, email=None):
        with getSession() as session:
            user = session.query(User).filter_by(phoneNumber=phoneNumber).first()
            if not user:
                user = User()
            user.name, user.phoneNumber, user.email = name, phoneNumber, email
            session.add(user)
            session.commit()
            self.connections.pop(self.sender.ID)
            self.sender.client.ID = user.id
            self.sender.ID = user.id
            self.connections[user.id] = self.sender
            return user.id


class SyncHub(Hub):
    def phoneNumbers(self, phoneNumberArray):
        session = getSession()
        users = session.query(User).filter(User.phoneNumber.in_(phoneNumberArray))
        return users.all()

    def getNotSyncedEntries(self, tableName, since, usersIds=list()):
        baseClass = globals()[tableName]
        assert (issubclass(baseClass, Base))
        with  getSession() as session:
            return baseClass.getNotSyncedEntries(session, self.sender.ID, since, usersIds)

    def syncModel(self, tableName, entries, since, usersIds=list()):
        baseClass = globals()[tableName]
        assert (issubclass(baseClass, Base))
        with  getSession() as session:
            syncDate = datetime.utcnow()
            notSyncedEntries = self.getNotSyncedEntries(tableName, since, usersIds)
            newIds = []
            for entry in entries:
                newIds.append(baseClass.insertOrUpdateFormDict(session, entry))
            session.commit()
            newIds = map(lambda x: x.id, newIds)
        return {'notSyncedEntries': notSyncedEntries, 'newIds': newIds, 'syncDate': syncDate}


class UserHub(Hub):
    def syncUser(self, user):
        with  getSession() as session:
            if user['id'] < 1:
                user.pop('id')
            user.insertOrUpdateFormDict(session, user)
            session.commit()
            return user.id

    def isConnected(self, id):
        return self.connections.has_key(id)


class PlaceHub(Hub):
    def createPlace(self, newPlace):
        with  getSession() as session:
            place = Place.insertFormDict(session, newPlace)
            session.commit()
            return place.ID

    def updatePlace(self, newPlace):
        with  getSession() as session:
            place = Place.updateFormDict(session, newPlace)
            session.commit()
            return place.id

    def syncPlace(self, newPlace):
        if newPlace["id"] < 0:
            return self.createPlace(newPlace)
        else:
            return self.updatePlace(newPlace)

    def getPlaces(self, ownerId):
        with getSession() as session:
            places = session.query(Place).filter(Place.ownerId == ownerId)
            return places.all()


class TaskHub(Hub):
    def syncTasks(self, tasks):
        idsCorrelation = list()
        with getSession() as session:
            try:
                for task in tasks:
                    try:
                        newTaskId = self.__syncTask(task, session)
                        idsCorrelation.append([task["id"], newTaskId])
                    except:
                        pass
                session.commit()
            except:
                session.rollback()
            return idsCorrelation

    def getNotUpdatedTasks(self, since, userId):
        with getSession() as session:
            return session.query(Task).filter(Task.updatedOn > getDateTime(since),
                                              or_(Task.receiverId == userId,
                                                  Task.creatorId == userId)).all()

    def syncTask(self, newTask):
        with getSession() as session:
            try:
                task = self.__syncTask(newTask, session)
                task.state = max([task.States.Uploaded, task.state])
                session.commit()
                return True
            except Exception as e:
                session.rollback()

    def __syncTask(self, newTask, session):
        if newTask["id"] < 0:
            return self.__createTask(newTask, session)
        else:
            return self.__updateTask(newTask, session)

    def __updateTask(self, newTask, session):
        task = Task.updateFormDict(session, newTask, force=True)
        session.add(task)
        session.flush()
        self._replay(task.id)
        if task.creatorId != task.receiverId:
            otherClientId = task.creatorId if self.sender.ID == task.receiverId else task.receiverId
            self.getClient(otherClientId).taskUpdated(task)
        return task

    def __createTask(self, newTask, session):
        task = Task.insertFormDict(session, newTask)
        session.flush()
        self._replay(task.id)
        if task.creatorId != task.receiverId:
            self.getClient(task.receiverId).newTask(task)
        return task

    def writingTo(self, userId, start):
        self.getClient(userId).showIsWriting(self.sender.ID, start)
        return None


class UtilsHub(Hub):
    def setId(self, id):
        assert isinstance(id, (int, long))
        self.connections.pop(self.sender.ID)
        self.sender.client.ID = id
        self.sender.ID = id
        self.connections[id] = self.sender

    def getId(self):
        return self.sender.ID

    def sentToAll(self, message):
        self.allClients.messageReceiver(message)

    def isConnected(self, id):
        return self.connections.has_key(id)
