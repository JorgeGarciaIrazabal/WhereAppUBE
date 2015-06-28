from Classes.QueryTable import QueryTable
import MySQLdb

__author__ = 'jorge'

class QueryManager():
    def __init__(self):
        self.init()

    def init(self):
        self.connection = MySQLdb.connect(user="root", passwd="", db="WAU",
                                          unix_socket="/opt/lampp/var/mysql/mysql.sock",)

    def select(self, query, parameters=list()):
        cursor = self.connection.cursor()
        cursor.execute("select " + query, parameters)
        return cursor

    def selectQt(self, query, parameters=list()):
        return QueryTable(self.select(query, parameters))

    def insertUser(self, email, phoneNumber, GCMID):
        cursor = self.connection.cursor()
        cursor.callproc("LogIn",(email,phoneNumber,GCMID))
        qt = QueryTable(cursor)
        self.connection.commit()
        return qt