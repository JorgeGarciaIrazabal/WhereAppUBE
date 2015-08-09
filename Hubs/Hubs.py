import os
from datetime import datetime
from sqlalchemy import create_engine, or_
from sqlalchemy.orm import sessionmaker, Session
from DBContext.tables import User, Task, Place
from wshubsapi.Hub import Hub

__author__ = 'Jorge'

# This is a throwaway variable to deal with a python bug
throwaway = datetime.strptime('20110101', '%Y%m%d')


def getSession():
    """
    :rtype : Session
    """
    engine = create_engine('mysql://root@localhost/wau')
    Session = sessionmaker(bind=engine,
                           expire_on_commit=False)
    session = Session()
    session._model_changes = {}
    return session


def getDateTime(dateStr):
    if dateStr is None: return None
    return datetime.strptime(dateStr, '%Y/%m/%d %H:%M:%S %f')


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
        place = self.__updatePlaceValues(place, newPlace)
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
        places = session.query(Place).filter(Place.OwnerId == ownerID)
        session.close()
        return places.all()


class TaskHub(Hub):
    def syncTasks(self, tasks):
        idsCorrelation = list()
        session = getSession()
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
        finally:
            session.close()
        return idsCorrelation

    def getNotUpdatedTasks(self, since, userId):
        session = getSession()
        try:
            return session.query(Task).filter(Task.UpdatedOn > getDateTime(since),
                                              or_(Task.ReceiverId == userId,
                                                  Task.CreatorId == userId)).all()
        finally:
            session.close()

    def syncTask(self, newTask):
        session = getSession()
        try:
            self.__syncTask(newTask,session)
            session.commit()
        except Exception as e:
            session.rollback()
        finally:
            session.close()

    def __syncTask(self, newTask, session):
        if newTask["ID"] < 0:
            return self.__createTask(newTask, session)
        else:
            return self.__updateTask(newTask, session)



    def __updateTask(self, newTask, session):
        task = session.query(Task).get(newTask["ID"])
        self.__updateTaskValues(task, newTask)
        session.add(task)
        session.flush()
        otherClientId = task.CreatorId if self.sender.ID == task.ReceiverId else task.ReceiverId
        client = self.getClient(otherClientId)
        if client is not None:
            client.taskUpdated(task)
        return task.ID

    def __createTask(self, newTask, session):
        task = Task()
        self.__updateTaskValues(task, newTask)
        session.add(task)
        session.flush()
        if task.CreatorId != task.ReceiverId:
            client = self.getClient(task.ReceiverId)
            if client is not None:
                client.newTask(task)
        return task.ID

    @staticmethod
    def __updateTaskValues(task, newTask):
        """
        :type task: Task
        """
        task.CreatedOn = getDateTime(newTask["CreatedOn"])
        task.CreatorId = newTask["CreatorId"]
        task.ReceiverId = newTask["ReceiverId"]
        task.Body = newTask["Body"]
        task.Type = newTask["Type"]
        newState = Task.States.Uploaded if newTask["State"] == Task.States.Created else newTask["State"]
        if task.State < newState:
            task.State = newState
        if task.Type == task.Types.Place:
            task.LocationId = newTask["LocationId"]
        if task.Type == task.Types.Scheduled:
            task.Schedule = getDateTime(newTask["Schedule"])
        return task

class UtilsHub(Hub):
    def setID(self, id):
        assert isinstance(id, int)
        self.connections.pop(self.sender.ID)
        self.sender.ID = id
        self.connections[id] = self.sender
