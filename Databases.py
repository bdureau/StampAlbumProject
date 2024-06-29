import pyodbc
import sqlite3
import configparser

class DB:
    def __init__(self, country):
        print(country)
        self.countryCursor = None
        self.dbtype = "sqlite"
        # get it from config
        configParser = configparser.RawConfigParser()
        configFilePath = r'stamp_album.cfg'
        configParser.read(configFilePath)
        if configParser.has_section('CONF'):
            conf = configParser['CONF']
            if configParser.has_option('CONF', 'database type'):
                self.dbtype = conf['database type']

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

        ret = []
        for row in res.fetchall():
            ret.append(row[0])
        print("after load list")
        return ret

    def getCurrentBox(self, SelectedBox):
        print("getCurrentBox")
        res = self.DBExecute(self.dbCurMaster, "SELECT lx,ly  FROM StampBox where pochette ='" + SelectedBox + "'")
        ret = []
        for row in res.fetchall():
            print(row[0])
            ret.append(row[0])
            ret.append(row[1])
        print("after getCurrentBox")
        return ret

    def loadStampType(self):
        print("before execute stamp type")
        res = self.DBExecute(self.dbCurCountry, "SELECT distinct type FROM Stamp_List order by type asc")
        print("after execute")
        ret = []
        for row in res.fetchall():
            print("test row")
            if row[0] is not None:
                ret.append(row[0])
            print(row[0])

        print("after execute2")
        print(ret)
        return ret

    def loadStampList(self, stampType, year):
        res = self.DBExecute(self.dbCurCountry, "SELECT key, nbr  FROM Stamp_list where type ='" + stampType +"' and year = '" + year + "' order by  sequence,ascii_seq, nbr, year asc")
        ret = []
        print("loadStampList")
        for row in res.fetchall():
            #print(row[0])
            if row[0] is not None:
                ret.append([row[0], row[1]])
        print("after loadStampList")
        return ret

    def getMinYearForType(self, stampType):
        print("getMinYearForType")
        res = self.DBExecute(self.dbCurCountry, "SELECT distinct year  FROM Stamp_List where type = '" + stampType + "'")
        ret = ""
        res.fetchall()
        if len(res) > 0:
            ret = res[0]
        print("after getMinYearForType")
        return ret

    def loadYearList(self, stampType):
        print("loadYearList")
        res = self.DBExecute(self.dbCurCountry, "SELECT distinct year  FROM Stamp_list where type ='" + stampType + "' and year is not null order by year asc")
        ret = []
        for row in res.fetchall():
            #print(row[0])
            ret.append(row[0])
        print("after loadYearList")
        return ret

    def getStampSubNbr(self, Key):
        print("getStampSubNbr")
        res = self.DBExecute(self.dbCurCountry, "SELECT sub_nbr FROM stamp_list where  Key =" + Key)
        ret = []
        for row in res.fetchall():
            #print(row[0])
            ret.append(row[0])
        print("after getStampSubNbr")
        return ret

    #get the pochette from the list using the width and height of the stamp
    def getPochette(self, stampNbr, stampType, stampYear, stampKey):
        print("getPochette")
        query1 = "SELECT width, height FROM stamp_list where type = '" + str(stampType) + "' and year = '" + \
                 str(stampYear) + "' and nbr = '" + str(stampNbr) + "' and key = " + str(stampKey) + ""

        res = self.DBExecute(self.dbCurCountry, query1)

        ret = []
        width = "0"
        height = "0"

        for row in res.fetchall():
            width = row[0]
            height = row[1]

        if width == "" or width is None:
            width = "0"
        if height == "" or height is None:
            height = "0"

        #print("middle getPochette")
        #print(width)
        #print(height)
        # attempt to get a valid pochette from the master db if cannot find one then select the first one
        query2 = "SELECT pochette FROM StampBox where lx = " + width + " and ly =" + height
        #print(query2)
        res2 = self.DBExecute(self.dbCurMaster, query2)
        #print("middle 2 getPochette")
        for row2 in res2.fetchall():
            #print(row2[0])
            ret.append(row2[0])

        if len(ret) == 0:
            ret.append('Pochette 30x41')
        print("after getPochette")
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
