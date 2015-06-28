import warnings

from Decorators.Asynchronous import asynchronous
from Decorators.InGuiThread import InGuiThread
from InfoTable import InfoTable

__author__ = 'jgarc'

class QueryTableExceptiom(Exception):
    pass

class NoEnoughDataProvided(QueryTableExceptiom):
    pass

class QueryColumn(list):
    def __init__(self, type, null_ok):
        list.__init__(self)
        self.type = type
        self.null_ok = null_ok

class QueryTable(InfoTable):
    INSERT_TEMPLATE = "insert into %s (%s) values(%s)"
    UPDATE_TEMPLATE = "update %s set %s where %s=?"
    SET_TEMPLATE = "[%s] = ?"

    INSERT_OR_UPDATE_TEMPLATE = """
    if exists (select * from %s where %s = ?)
    begin
       %s
    end
    else
    begin
       %s
    end
    """

    def __init__(self, cursor=None, queryManager=None, table=None):
        """
        @param cursor:
        @param queryManager: Query manager to preform the updates or inserts
        @param table: Table name that represent the query table (could not represent any table)
        @type cursor: pyodbc.Cursor
        @type queryManager: QueryManagerInterface
        @type table: str
        """
        InfoTable.__init__(self)
        self.qm = queryManager
        self.table = table
        self.primaryKeyColumn = None
        if cursor is not None:
            for (i, x) in enumerate(cursor.description):
                self.headers.append(x[0].encode("unicode-escape"))
                self._lowerHeaders.append(self.headers[-1].lower())
                self._columns.append(QueryColumn(x[1], x[6]))
            for i, row in enumerate(cursor.fetchall()):
                for j, cell in enumerate(row):
                    if isinstance(cell, str):
                        self._columns[j].append(cell.decode("unicode-escape",'replace').encode("utf-8"))
                    else:
                        self._columns[j].append(cell)
            for head in self._lowerHeaders:
                self.__dict__[head] = self[head]
            cursor.close()
        if table is not None and self.qm is not None:
            # todo: get primary key directly from table
            """
            try:
                self.primaryKeyColumn=QueryTable(self.qm.__runQuery__("SQLPrimaryKeys")).getColumn("tableName")[0]
                self.primaryKeyColumn=self.__getColumn__(self.primaryKeyColumn)
            except:
                self.primaryKeyColumn=None"""

    def insert(self, rows):
        if self.qm is None or self.primaryKeyColumn is None or self.table is None:
            raise NoEnoughDataProvided("Necessary to set qm, primaryKeyColumn and table")
        if not (isinstance(rows, list) or isinstance(rows, tuple)):
            rows = [rows]

        for row in rows:
            insertSubTemplate, values = self.__getInsertString(row)
            self.qm.__runQuery__(insertSubTemplate, values)

    @InGuiThread()
    def insertedCallback(self, *args, **kwargs):
        pass

    @asynchronous(callback=insertedCallback)
    def asyncInsert(self, rows):
        return self.insert

    def __getInsertString(self, row):
        headers = []
        values = []
        rowData = self.getRow(row)
        for key, data in rowData.items():
            if data is not None:
                headers.append("[%s]" % key)
                values.append(data)
        maks = ",".join(["?" * len(headers)])
        insertSubTemplate = self.INSERT_TEMPLATE % (self.table, ",".join(headers), maks)
        return insertSubTemplate, values

    def update(self, rows):
        if self.qm is None or self.primaryKeyColumn is None or self.table is None:
            raise NoEnoughDataProvided("Necessary to now set qm, primaryKeyColumn and table")
        if not (isinstance(rows, list) or isinstance(rows, tuple)):
            rows = [rows]

        for row in rows:
            primaryKeyValue = self.get(self.primaryKeyColumn, row)
            if primaryKeyValue is not None:
                updateString, values = self.__getUpdateString(primaryKeyValue, row)
                self.qm.__runQuery__(updateString, values)
            else:
                warnings.warn("Trying to update a row with no primaryKey", RuntimeWarning)

    def updatedCallback(self, *args, **kwargs):
        pass

    @asynchronous(callback=updatedCallback)
    def asyncUpdate(self, rows):
        return self.update(rows)

    def __getUpdateString(self, primaryKeyValue, row):
        values = []
        sets = []
        rowData = self.getRow(row)
        for key, data in rowData.items():
            sets.append(self.SET_TEMPLATE % key)
            values.append(data)
        values.append(primaryKeyValue)
        updateSubTemplate = self.UPDATE_TEMPLATE % (self.table, ",".join(sets), self.primaryKeyColumnName)
        return updateSubTemplate, values

    @property
    def primaryKeyColumnName(self):
        return self.headers[self.primaryKeyColumn]

    def insertOrUpdate(self, rows):
        if not (isinstance(rows, list) or isinstance(rows, tuple)):
            rows = [rows]
        for row in rows:
            primaryKeyValue = self.get(self.primaryKeyColumn, row)
            if primaryKeyValue is not None:
                globalValues = [primaryKeyValue]
                updateString, updateValues = self.__getUpdateString(primaryKeyValue, row)
                insertString, insertValues = self.__getInsertString(row)
                globalValues.extend(updateValues)
                globalValues.extend(insertValues)
                template = self.INSERT_OR_UPDATE_TEMPLATE % (self.primaryKeyColumnName, updateString, insertString)
                self.qm.__runQuery__(template,globalValues)
            else:
                warnings.warn("Trying to update a row with no primaryKey %s" % str(row), RuntimeWarning)
