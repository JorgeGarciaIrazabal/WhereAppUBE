import os
from sqlalchemy.engine import create_engine
#os.system("C://Python27/scripts/sqlacodegen mysql://root@localhost:3306/WAU  --outfile tables.py")
from sqlalchemy.ext.declarative import declarative_base
from DBContext.tables import *

Base = declarative_base()
__author__ = 'Jorge'
try:
    engine = create_engine('mysql://root@localhost/wau', pool_recycle=3600)
    connection = engine.connect()
    Base.metadata.create_all(engine)
    print(1)
except Exception as e:
    raise e

