# coding: utf-8
from datetime import datetime
from jsonpickle import handlers

from sqlalchemy import Column, DateTime, Enum, ForeignKey, Integer, Text, text, create_engine, Float
from sqlalchemy.orm import relationship
from sqlalchemy.ext.declarative import declarative_base, AbstractConcreteBase

Base = declarative_base()

class MyBase(AbstractConcreteBase,Base):
    @classmethod
    def insertOrUpdateFormDict(cls, session, newEntryDict):
        """
        :type _class: Base
        :type newEntryDict: dict

        """
        if "id" in newEntryDict:
            return cls.updateFormDict(session,newEntryDict)
        else:
            return cls.insertFormDict(session,newEntryDict)

    @classmethod
    def __updateValuesFormDict(cls, entry, newEntryDict):
        """
        :type entry: Base
        """
        for newEntryKey in newEntryDict:
            if newEntryKey in entry.__table__.columns and not isinstance(entry.__getattribute__(newEntryKey), Base):
                entry.__dict__[newEntryKey] = newEntryDict[newEntryKey]

    @classmethod
    def insertFormDict(cls, session, newEntryDict):
        """
        :type newEntryDict: dict
        """
        entry = cls()
        newEntryDict.pop('id', None)
        cls.__updateValuesFormDict(entry,newEntryDict)
        session.add(entry)
        return entry

    @classmethod
    def updateFormDict(cls, session, newEntryDict):
        id = newEntryDict.pop("id")
        entry = session.query(cls).get(id)
        cls.__updateValuesFormDict(entry,newEntryDict)
        session.add(entry)
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
    creatorId = Column(ForeignKey(u'user.ID'), nullable=False, index=True)
    createdOn = Column(DateTime, nullable=False, default=datetime.now, index=True)
    body = Column(Text(collation=u'utf8_unicode_ci'))
    type = Column(Enum(u'Comment', u'Scheduled', u'Place'), nullable=False, server_default=text("'Comment'"))
    receiverId = Column(ForeignKey(u'user.ID'), nullable=False, index=True)
    updatedOn = Column(DateTime, nullable=False, default=datetime.now, onupdate=datetime.now)
    locationId = Column(ForeignKey(u'place.ID'), nullable=True, index=True)
    schedule = Column(DateTime, nullable=True)
    state = Column(Integer, nullable=False, server_default=text("1"), index=True)

    creator = relationship(u'User', primaryjoin='Task.CreatorId == User.ID')
    receiver = relationship(u'User', primaryjoin='Task.ReceiverId == User.ID')
    location = relationship(u'Place', primaryjoin='Task.LocationId == Place.ID')


class User(MyBase):
    __tablename__ = 'user'

    id = Column(Integer, primary_key=True)
    name = Column(Text(collation=u'utf8_unicode_ci'), nullable=False)
    phoneNumber = Column(Text(collation=u'utf8_unicode_ci'), nullable=False)
    email = Column(Text(collation=u'utf8_unicode_ci'))
    GCM_ID = Column(Text(collation=u'utf8_unicode_ci'), default='123456789123456789')
    updatedOn = Column(DateTime, nullable=False, default=datetime.now, onupdate=datetime.now)


class Place(MyBase):
    __tablename__ = 'place'

    id = Column(Integer, primary_key=True)
    ownerId = Column(ForeignKey(u'user.ID'), nullable=False, index=True)
    createdOn = Column(DateTime, nullable=False, default=datetime.now, index=True)
    name = Column(Text(collation=u'utf8_unicode_ci'))
    type = Column(Enum(u'Public', u'Private'), nullable=False, server_default=text("'Public'"))
    iconURI = Column(Text(collation=u'utf8_unicode_ci'), nullable=False)
    updatedOn = Column(DateTime, nullable=False, default=datetime.now, onupdate=datetime.now)
    longitude = Column(Float, nullable=False)
    latitude = Column(Float, nullable=False)
    range = Column(Integer, nullable=False)
    deletedOn = Column(DateTime, nullable=True, default=None)

    rUser = relationship(u'User', primaryjoin='Place.OwnerId == User.ID')

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
