from sqlalchemy.orm import Session, sessionmaker
from DBContext.tables import *

class DataBaseHelper:
    DB_URL = 'mysql://root@localhost/wau?charset=utf8'
    DB_URL_DEBUG = 'mysql://root@localhost/wau?charset=utf8'

    class MySession(Session):
        def __enter__(self):
            return self
        def __exit__(self, exc_type, exc_val, exc_tb):
            self.close()
            self.itWasClosed = True #todo: change this for a mock

    @classmethod
    def getSession(cls):
        """
        :rtype : DataBaseHelper.MySession
        """
        engine = create_engine(cls.DB_URL)
        Session = sessionmaker(bind=engine, expire_on_commit=False, class_=DataBaseHelper.MySession)
        session = Session()
        session._model_changes = {}
        return session
