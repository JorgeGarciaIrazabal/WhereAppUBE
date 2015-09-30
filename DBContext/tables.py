# coding: utf-8
from datetime import datetime
from jsonpickle import handlers

from sqlalchemy import Column, DateTime, Enum, ForeignKey, Integer, Text, text, create_engine, Float, or_
from sqlalchemy.orm import relationship
from sqlalchemy.ext.declarative import declarative_base, AbstractConcreteBase

Base = declarative_base()


def getDateTime(dateStr):
    if dateStr is None: return None
    try:
        return datetime.strptime(dateStr, '%Y/%m/%d %H:%M:%S.%f')
    except ValueError as e:
        try:
            return datetime.strptime(dateStr, '%Y/%m/%d %H:%M:%S %f')
        except ValueError as e:
            return datetime.strptime(dateStr, "%Y-%m-%dT%H:%M:%S.%fZ")


class MyBase(AbstractConcreteBase, Base):
    @classmethod
    def insertOrUpdateFormDict(cls, session, newEntryDict):
        """
        :type _class: Base
        :type newEntryDict: dict

        """
        if "id" in newEntryDict:
            return cls.updateFormDict(session, newEntryDict)
        else:
            return cls.insertFormDict(session, newEntryDict)

    @classmethod
    def __updateValuesFormDict(cls, entry, newEntryDict):
        """
        :type entry: Base
        """
        for newEntryKey in newEntryDict:
            if newEntryKey in entry.__table__.columns and not isinstance(entry.__getattribute__(newEntryKey), Base):
                if isinstance(cls.__dict__[newEntryKey].type, DateTime):
                    entry.__setattr__(newEntryKey, getDateTime(newEntryDict[newEntryKey]))
                else:
                    entry.__setattr__(newEntryKey,  newEntryDict[newEntryKey])

    @classmethod
    def insertFormDict(cls, session, newEntryDict):
        """
        :type newEntryDict: dict
        """
        entry = cls()
        id = newEntryDict.pop('id', None)
        if id > 0:
            newEntryDict['id'] = id
        cls.__updateValuesFormDict(entry, newEntryDict)
        session.add(entry)

        return entry

    @classmethod
    def updateFormDict(cls, session, newEntryDict, force=False):
        id = newEntryDict["id"]
        entry = session.query(cls).get(id)
        if entry is None: return cls.insertFormDict(session, newEntryDict)

        newEntryDict.pop('id')
        if force or entry.updatedOn < getDateTime(newEntryDict["updatedOn"]):
            cls.__updateValuesFormDict(entry, newEntryDict)
        return entry


class Task(MyBase):
    __tablename__ = 'task'

    class Types:
        Comment = u'Comment'
        Scheduled = u'Scheduled'
        Place = u'Place'

    class States:
        Created = 0
        Uploaded = 1
        Arrived = 2
        Read = 3
        Completed = 4
        Dismissed = 5

    id = Column(Integer, primary_key=True)
    creatorId = Column(ForeignKey(u'user.id'), nullable=False, index=True)
    createdOn = Column(DateTime, nullable=False, default=datetime.utcnow, index=True)
    body = Column(Text(collation=u'utf8_unicode_ci'))
    kind = Column(Enum(u'Comment', u'Scheduled', u'Place'), nullable=False, server_default=text("'Comment'"))
    receiverId = Column(ForeignKey(u'user.id'), nullable=False, index=True)
    updatedOn = Column(DateTime, nullable=False, default=datetime.utcnow, onupdate=datetime.utcnow)
    locationId = Column(ForeignKey(u'place.id'), nullable=True, index=True)
    schedule = Column(DateTime, nullable=True)
    state = Column(Integer, nullable=False, server_default=text("1"), index=True)  # todo: check this

    creator = relationship(u'User', primaryjoin='Task.creatorId == User.id')
    receiver = relationship(u'User', primaryjoin='Task.receiverId == User.id')
    location = relationship(u'Place', primaryjoin='Task.locationId == Place.id')

    @staticmethod
    def getNotSyncedEntries(session, userId, since, usersIds=[]):
        return session.query(Task).filter(Task.updatedOn > getDateTime(since),
                                          or_(Task.receiverId == userId,
                                              Task.creatorId == userId)).all()


class User(MyBase):
    __tablename__ = 'user'

    id = Column(Integer, primary_key=True)
    name = Column(Text(collation=u'utf8_unicode_ci'), nullable=False)
    phoneNumber = Column(Text(collation=u'utf8_unicode_ci'), nullable=False)
    email = Column(Text(collation=u'utf8_unicode_ci'))
    GCM_ID = Column(Text(collation=u'utf8_unicode_ci'), default='123456789123456789')
    updatedOn = Column(DateTime, nullable=False, default=datetime.utcnow, onupdate=datetime.utcnow)

    @staticmethod
    def getNotSyncedEntries(session, userId, since, usersIds=[]):
        return session.query(User).filter(User.updatedOn > getDateTime(since),
                                          User.id.in_(usersIds)).all()


class Place(MyBase):
    __tablename__ = 'place'

    id = Column(Integer, primary_key=True)
    ownerId = Column(ForeignKey(u'user.id'), nullable=False, index=True)
    createdOn = Column(DateTime, nullable=False, default=datetime.utcnow, index=True)
    name = Column(Text(collation=u'utf8_unicode_ci'))
    kind = Column(Enum(u'Public', u'Private'), nullable=False, server_default=text("'Public'"))
    iconUrl = Column(Text(collation=u'utf8_unicode_ci'), nullable=False)
    updatedOn = Column(DateTime, nullable=False, default=datetime.utcnow, onupdate=datetime.utcnow)
    longitude = Column(Float, nullable=False)
    latitude = Column(Float, nullable=False)
    range = Column(Integer, nullable=False)
    deletedOn = Column(DateTime, nullable=True, default=None)

    rUser = relationship(u'User', primaryjoin='Place.ownerId == User.id')

    @staticmethod
    def getNotSyncedEntries(session, userId, since, usersIds=[]):
        return session.query(Place).filter(Place.updatedOn > getDateTime(since),
                                           Place.ownerId.in_(usersIds)).all()


class MyBaseObject(handlers.BaseHandler):
    def flatten(self, obj, data):
        state = obj.__dict__.copy()
        for key in state:
            if isinstance(state[key], Base):
                state[key] = state[key].__dict__.copy()
                del state[key]['_sa_instance_state']

        del state['_sa_instance_state']
        return state


handlers.register(Base, MyBaseObject, base=True)

if __name__ == '__main__':
    engine = create_engine('mysql://root@localhost/wau', echo=True)
    Base.metadata.create_all(bind=engine)
    # com = engine.connect()
    # s = select([User])
    # com.execute(s)
