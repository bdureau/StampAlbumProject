import pyodbc
import sqlite3

class DB:
    def __init__(self, country):
        print(country)
        self.countryCursor = None
        self.dbtype = "sqlite"
        if self.dbtype == "sqlite":
            conMaster = sqlite3.connect("databases/master.db")
            self.dbCurMaster = conMaster.cursor()
            conCountry = sqlite3.connect("databases/" + country + ".db")
            self.countryCursor = conCountry.cursor()
            print("cursor open")
        else:
            self.dbCurMaster = self.OpenDB(r'Driver={Microsoft Access Driver (*.mdb, *.accdb)};DBQ=databases\master.mdb;')
            self.countryCursor = self.OpenCountryDB(country)


    def OpenCountryDB(self, country):
        print("OpenDB %s" % country)
        if self.countryCursor is not None:
            print("closing db")

            self.countryCursor.close()
            self.countryCursor = None

        if self.dbtype == "sqlite":
            conCountry = sqlite3.connect("databases/" + country + ".db")
            self.dbCurCountry = conCountry.cursor()
            print("done")
        else:
            self.dbCurCountry = self.OpenDB(
                r'Driver={Microsoft Access Driver (*.mdb, *.accdb)};DBQ=databases\\' + country + '.mdb' + ';')

    def OpenDB(self, database):
        conn = pyodbc.connect(database)
        cursor = conn.cursor()
        return cursor

    def DBExecute(self, cursor, statment):
        res = cursor.execute(statment)
        return res

    def loadBoxList(self):
        print("load list")
        res = self.DBExecute(self.dbCurMaster, "SELECT pochette FROM StampBox order by lx,ly asc")
        print("after load list")
        ret = []
        for row in res.fetchall():
            ret.append(row[0])
        return ret

    def getCurrentBox(self, SelectedBox):
        res = self.DBExecute(self.dbCurMaster, "SELECT lx,ly  FROM StampBox where pochette ='" + SelectedBox + "'")
        ret = []
        for row in res.fetchall():
            print(row[0])
            ret.append(row[0])
            ret.append(row[1])

        return ret

    def loadStampType(self):
        print("before execute stamp type")
        res = self.DBExecute(self.dbCurCountry, "SELECT distinct type FROM Stamp_List order by type asc")
        print("after execute")
        ret = []
        for row in res.fetchall():
            print("test row")
            ret.append(row[0])
            print(row[0])

        print("after execute2")
        print(ret)
        return ret

    def loadStampList(self, stampType, year):
        res = self.DBExecute(self.dbCurCountry, "SELECT key, nbr  FROM Stamp_list where type ='" + stampType +"' and year = '" + year + "' order by  sequence,ascii_seq, nbr, year asc")
        ret = []
        for row in res.fetchall():
            #print(row[0])
            ret.append([row[0], row[1]])
        return ret

    def getMinYearForType(self, stampType):
        res = self.DBExecute(self.dbCurCountry, "SELECT distinct year  FROM Stamp_List where type = '" + stampType + "'")
        ret = ""
        res.fetchall()
        if len(res) > 0:
            ret = res[0]
        return ret

    def loadYearList(self, stampType):
        res = self.DBExecute(self.dbCurCountry, "SELECT distinct year  FROM Stamp_list where type ='" + stampType + "' and year is not null order by year asc")
        ret = []
        for row in res.fetchall():
            #print(row[0])
            ret.append(row[0])
        return ret

    def getStampSubNbr(self, Key):
        res = self.DBExecute(self.dbCurCountry, "SELECT sub_nbr FROM stamp_list where  Key =" + Key)
        ret = []
        for row in res.fetchall():
            #print(row[0])
            ret.append(row[0])
        return ret

    #get the pochette from the list using the width and height of the stamp
    def getPochette(self, stampNbr, stampType, stampYear, stampKey):

        query1 = "SELECT width, height FROM stamp_list where type = '" + str(stampType) + "' and year = '" + \
                 str(stampYear) + "' and nbr = '" + str(stampNbr) + "' and key = " + str(stampKey) + ""

        res = self.DBExecute(self.dbCurCountry, query1)

        ret = []
        width = "0"
        height = "0"

        for row in res.fetchall():
            width = row[0]
            height = row[1]

        if width == "":
            width = "0"
        if height == "":
            height = "0"
        print("width")
        print(width)

        # attempt to get a valid pochette from the master db if cannot find one then select the first one
        query2 = "SELECT pochette FROM StampBox where lx = " + width + " and ly =" + height
        print("before query")
        res2 = self.DBExecute(self.dbCurMaster, query2)
        print("after query")
        for row2 in res2.fetchall():
            #print(row2[0])
            ret.append(row2[0])

        print(len(ret))
        if len(ret) == 0:
            print("empty")
            ret.append('Pochette 30x41')
        print(ret)
        return ret

    def stampChanged(self, stampNbr, Key):
        query = "SELECT nbr,year,valuecolor, stampDescription,width, height,sub_nbr,stampDescription1 FROM stamp_list where nbr = '" + str(stampNbr) + "' and Key = " + str(Key)
        print(query)
        res = self.DBExecute(self.dbCurCountry, query)
        print("after query")
        ret = []
        for row in res.fetchall():
        #    print(row[0])
        #    print(row[1])
            ret.append(row[0])
            ret.append(row[1])
            ret.append(row[2])
            ret.append(row[3])
            ret.append(row[4])
            ret.append(row[5])
            ret.append(row[6])
            ret.append(row[7])
        #ret = res.fetchall()

        return ret

    def getMessage(self, msgLanguage, msgCode):
        res = self.DBExecute(self.dbCurMaster, "SELECT message_text, message_type FROM messages where message_language ='" + msgLanguage + "' and message_code =" + msgCode)
        ret = []
        for row in res.fetchall():
            #print(row[0])
            ret.append(row[0])
        return ret

    def getTranslation(self, msgLanguage, msgCode):
        res = self.DBExecute(self.dbCurMaster, "SELECT msg_text FROM translations where msg_language ='" + msgLanguage + "' and msg_code =" + msgCode + "")
        ret = []
        for row in res.fetchall():
            #print(row[0])
            ret.append(row[0])
        return ret

    def getInputBox(self, msgLanguage, msgCode):
        res = self.DBExecute(self.dbCurMaster, "SELECT message_text, message_type FROM messages where message_language ='" + msgLanguage + "' and message_code =" + msgCode)
        ret = []
        for row in res.fetchall():
            #print(row[0])
            ret.append(row[0])
        return ret
