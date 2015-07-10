# coding: utf-8
from datetime import datetime

from sqlalchemy import Column, DateTime, Enum, ForeignKey, Integer, Text, text, create_engine, Float
from sqlalchemy.orm import relationship
from sqlalchemy.ext.declarative import declarative_base

Base = declarative_base()


class Task(Base):
    __tablename__ = 'task'

    class Types:
        Comment = u'Comment'
        Scheduled = u'Scheduled'
        Place = u'Place'

    ID = Column(Integer, primary_key=True)
    CreatorId = Column(ForeignKey(u'user.ID'), nullable=False, index=True)
    CreatedOn = Column(DateTime, nullable=False, server_default=text("CURRENT_TIMESTAMP"))
    Body = Column(Text(collation=u'utf8_unicode_ci'))
    Type = Column(Enum(u'Comment', u'Scheduled', u'Place'), nullable=False, server_default=text("'Comment'"))
    ReceiverId = Column(ForeignKey(u'user.ID'), nullable=False, index=True)
    UpdatedOn = Column(DateTime, nullable=False, server_default=text("CURRENT_TIMESTAMP"), onupdate=datetime.now)
    LocationId = Column(ForeignKey(u'place.ID'), nullable=True, index=True)
    Schedule = Column(DateTime, nullable=True)
    Status = Column(Integer, nullable=False, server_default=text("1"), index=True)

    rCreator = relationship(u'User', primaryjoin='Task.CreatorId == User.ID')
    rReceiver = relationship(u'User', primaryjoin='Task.ReceiverId == User.ID')
    rLocation = relationship(u'Place', primaryjoin='Task.LocationId == Place.ID')


class User(Base):
    __tablename__ = 'user'

    ID = Column(Integer, primary_key=True)
    Name = Column(Text(collation=u'utf8_unicode_ci'), nullable=False)
    PhoneNumber = Column(Text(collation=u'utf8_unicode_ci'), nullable=False)
    Email = Column(Text(collation=u'utf8_unicode_ci'))
    GCM_ID = Column(Text(collation=u'utf8_unicode_ci'))
    UpdatedOn = Column(DateTime, nullable=False, server_default=text("CURRENT_TIMESTAMP"), onupdate=datetime.now)


class Place(Base):
    __tablename__ = 'place'

    ID = Column(Integer, primary_key=True)
    OwnerId = Column(ForeignKey(u'user.ID'), nullable=False, index=True)
    CreatedOn = Column(DateTime, nullable=False, server_default=text("CURRENT_TIMESTAMP"))
    Name = Column(Text(collation=u'utf8_unicode_ci'))
    Type = Column(Enum(u'Public', u'Private'), nullable=False, server_default=text("'Public'"))
    IconURI = Column(Text(collation=u'utf8_unicode_ci'), nullable=False)
    UpdatedOn = Column(DateTime, nullable=False, server_default=text("CURRENT_TIMESTAMP"), onupdate=datetime.now)
    Longitude = Column(Float, nullable=False)
    Latitude = Column(Float, nullable=False)
    Range = Column(Integer, nullable=False)

    rUser = relationship(u'User', primaryjoin='Place.OwnerId == User.ID')


if __name__ == '__main__':
    engine = create_engine('mysql://root@localhost/wau', echo=True)
    Base.metadata.create_all(bind=engine)
    # com = engine.connect()
    # s = select([User])
    # com.execute(s)
