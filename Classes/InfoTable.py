from collections import OrderedDict
import json
from enum.enum import Enum
from ValidateStrings import getUnicode, getStr
from utils.DictPrint import dict2Str

class Order(Enum):
    ASC,DESC=False,True
__author__ = 'jgarc'

class InfoTableException(Exception):
    pass

class InfoRow():
    def __init__(self):
        self.dict=OrderedDict()
    def __getitem__(self, item):
        if isinstance(item, int):
            return self.dict.items()[item][1]
        return self.dict.__getitem__(item.lower())

    def __contains__(self, item):
        return self.dict.__contains__(item.lower())

    def __setitem__(self, key, value):
        if isinstance(key, int):
            self.dict.items()[key][1]=value
        self.dict.__setitem__(key.lower(),value)

    def get(self, k, d=None):
        if isinstance(k, int):
            try:
                return self.dict.items()[k][1]
            except:
                return d
        return self.dict.get(k.lower(), d)

    def __str__(self, rowSeparator="\n", columnSeparator="\t"):
        return getStr(dict2Str(self.dict))

    def __unicode__(self):
        return str(self)

    def __repr__(self):
        return str(self)



class InfoTable():
    """
    Structured data for tables (Database tables)
    """
    def __init__(self, data=None, rowSeparator="\n", columnSeparator="\t"):
        self._columns=list()
        self.headers=[]
        self._lowerHeaders=[]
        """@type: list of str"""
        if data is None:
            return
        if isinstance(data, list) or isinstance(data, tuple):
            self.constructFromArray(data)
        elif isinstance(data, (str, unicode)):
            self.constructFromString(data, rowSeparator, columnSeparator)

    def renameHeader(self,column, newHeader):
        column=self.__getColumn__(column)
        self.__dict__.pop(self._lowerHeaders[column])
        self.headers[column]=newHeader
        self._lowerHeaders[column]=newHeader.lower()
        self.__dict__[newHeader.lower()]=self[newHeader.lower()]

    def constructFromArray(self, data):
        """
        @param data: matrix  to construct the infoTable
        @type data: list of list
        """
        self._lowerHeaders = [header.lower() for header in data[0]]
        self.headers=data[0]
        for i in range(len(self.headers)):
            self._columns.append([data[j][i] for j in range(1,len(data))])
        for head in self._lowerHeaders:
            self.__dict__[head]=self[head]

    def constructFromString(self, data, rowSeparator="\n", columnSeparator="\t"):
        """
        @param data: string with rowSeparators and columnSeparators to construct the infoTable
        @type data: str
        """
        data = [row.split(columnSeparator) for row in data.split(rowSeparator)]
        self.constructFromArray(data)

    def get(self, column=0, row=0):
        """redundant of __getItem__ with the default values"""
        return self[column][row]

    def fastGet(self,column=0,row=0):
        """
        same as get but the column has to be an integer, it should be used if the performance is critical
        """
        return self._columns[column][row]

    def __getColumn__(self, column=""):
        """
        gets the column index from the column name, if column is a valid integer, it returns the integer
        @param column: can be a header value or its index
        @raise InfoTableException:
        """
        if isinstance(column, int) and abs(column) < len(self.headers):
            return column
        else:
            try:
                return self._lowerHeaders.index(column.lower())
            except:
                raise InfoTableException("Column not found:" + str(column))

    def __iter__(self):
        """
        returns an InfoRow of the row x
        @rtype: InfoRow
        """
        for x in range(self.size()):
            yield self.getRow(x)

    def __getitem__(self, item):
        """
        if item is a integer, gets the column in the index
        if item is a str, it gets the column where the header is the item
        @return: an array the all the column values
        """
        column=self.__getColumn__(item)
        return self._columns[column]

    def __setitem__(self, key, value):
        column=self.__getColumn__(key)
        self._columns[column]=value

    def getRow(self, row=0):
        if abs(row) > self.size():
            raise InfoTableException("Out of bounds, size = " + str(self.size()) + " row= " + str(row))
        infoRow = InfoRow()
        for column in self._lowerHeaders:
            infoRow[column] = self[column][row]
        return infoRow

    def hasColumn(self,column):
        if isinstance(column, int) and abs(column) < len(self.headers):
            return True
        else:
            return column.lower() in self._lowerHeaders

    def size(self):
        return self.__len__()

    def __len__(self):
        if len(self.headers) == 0 or len(self._columns) == 0: return 0
        return len(self._columns[0])

    def set(self, column, row, value):
        self[column][row] = value

    def fastSet(self, column, row, value):
       self._columns[column][row]=value

    def getColumn(self, column, join=None):
        if join is None:
            return self[column]
        else:
            return join.join([str(cell) for cell in self[column]])

    def __str__(self, rowSeparator="\n", columnSeparator="\t"):
        string = [columnSeparator.join(self.headers)]
        for i in range(self.size()):
            string.append([])
            for column in range(len(self.headers)):
                cell=getUnicode(self.get(column, i))
                string[-1].append(cell)
            string[-1]=columnSeparator.join(string[-1])
        return getStr(rowSeparator.join(string))

    def __unicode__(self):
        return str(self)

    def __repr__(self):
        return str(self)

    def findAll(self,column,value):
        index = []
        idx = -1
        while True:
            try:
                idx = self[column].index(value, idx+1)
                index.append(idx)
            except ValueError:
                break
        return index

    def findFirst(self,column,value, notValue=False):
        if not notValue:
            return self[column].index(value)
        else:
            for i,cellValue in enumerate(self[column]):
                if cellValue!=value:
                    return i
        raise ValueError("%s is not in list"%str(value))

    def getAll(self,column,value, refColumn=None):
        index=self.findAll(column,value)
        if refColumn is None:
            refColumn=column
        refColumn=self.__getColumn__(refColumn)
        values=[]
        for i in index:
            values.append(self.fastGet(refColumn,i))
        return values

    def getFirst(self, column, value, refColumn=None, notValue=False):
        if refColumn is None:
            refColumn=column
        return self.get(refColumn,self.findFirst(column,value, notValue=notValue))

    def addColumn(self,column, values=list()):
        lowerColumn=column.lower()
        if lowerColumn in self._lowerHeaders:
            raise Exception("Header already exists in info table")
        self.headers.append(column)
        self._lowerHeaders.append(lowerColumn)
        if not isinstance(values,list) or isinstance(values,tuple):
            values=[values]*self.size()
        if len(values) > 0 and len(values)!=self.size():
            Warning("Values length does not match with infoTable length, creating empty column")
            values=[None]*self.size()
        elif len(values) == 0:
            values=[None]*self.size() if self.size()>0 else []

        self._columns.append(values)

    def addRow(self):
        for i in range(len(self.headers)):
            self[i].append(None)

    def removeColumns(self, columns):
        if not (isinstance(columns,list) or  isinstance(columns,tuple)):
            columns=[columns]
        columns=sorted(set([self.__getColumn__(column) for column in columns if column.lower() in self._lowerHeaders]))
        for column in reversed(columns):
            self.headers.pop(column)
            self._lowerHeaders.pop(column)
            self._columns.pop(column)

    def sort(self, column, order=Order.ASC):
        data=self[column]
        sortedIndex=[i[0] for i in sorted(enumerate(data), key=lambda x:x[1], reverse=order.value)]
        for c in range(len(self.headers)):
            self[c]=[self[c][sortedIndex[j]] for j in range(len(self[c]))]

    def removeRows(self, rows):
        if not (isinstance(rows,list) or  isinstance(rows,tuple)):
            rows=[rows]
        for row in rows:
            for col in range(len(self.headers)):
                self[col].pop(row)

    def toJson(self):
        j={}
        for head in self.headers:
            j[head]=[getUnicode(d) for d in self.getColumn(head)]
        return json.dumps(j)




