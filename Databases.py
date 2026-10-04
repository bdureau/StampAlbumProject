import configparser
from pathlib import Path
import pyodbc
import sqlite3


class DB:

    def __init__(self, country: str):
        self.country = country
        self.dbtype = "sqlite"

        # Chemins de fichiers portables
        self.base_dir = Path(__file__).resolve().parent
        self.db_dir = self.base_dir / "databases"
        config_path = self.base_dir / "stamp_album.cfg"

        # Lecture de la configuration
        configParser = configparser.RawConfigParser()
        if config_path.exists():
            configParser.read(config_path)
            if configParser.has_option("CONF", "database type"):
                self.dbtype = configParser.get("CONF", "database type")

        # Initialisation des connexions
        self.con_master = None
        self.con_country = None
        self.dbCurMaster = None
        self.dbCurCountry = None

        self._init_db_connections(country)

    def _init_db_connections(self, country: str):
        if self.dbtype == "sqlite":
            master_db = self.db_dir / "master.db"
            country_db = self.db_dir / f"{country}.db"

            self.con_master = sqlite3.connect(master_db)
            self.dbCurMaster = self.con_master.cursor()

            self.con_country = sqlite3.connect(country_db)
            self.dbCurCountry = self.con_country.cursor()
        else:
            master_conn_str = f"Driver={{Microsoft Access Driver (*.mdb, *.accdb)}};DBQ={self.db_dir / 'master.mdb'};"
            self.con_master = pyodbc.connect(master_conn_str)
            self.dbCurMaster = self.con_master.cursor()

            self.OpenCountryDB(country)

    def OpenCountryDB(self, country: str):
        # Fermeture propre de la base country existante
        if self.dbCurCountry:
            self.dbCurCountry.close()
        if self.con_country:
            self.con_country.close()

        if self.dbtype == "sqlite":
            country_db = self.db_dir / f"{country}.db"
            self.con_country = sqlite3.connect(country_db)
            self.dbCurCountry = self.con_country.cursor()
        else:
            country_conn_str = f"Driver={{Microsoft Access Driver (*.mdb, *.accdb)}};DBQ={self.db_dir / f'{country}.mdb'};"
            self.con_country = pyodbc.connect(country_conn_str)
            self.dbCurCountry = self.con_country.cursor()

    def DBExecute(self, cursor, statement: str, params: tuple = ()):
        """Exécution sécurisée avec paramètres tuple"""
        cursor.execute(statement, params)
        return cursor

    def loadBoxList(self):
        print("load list")
        query = "SELECT pochette FROM StampBox ORDER BY lx, ly ASC"
        res = self.DBExecute(self.dbCurMaster, query)
        print("after load list")
        return [row[0] for row in res.fetchall()]

    def getCurrentBox(self, SelectedBox: str):
        print("getCurrentBox")
        query = "SELECT lx, ly FROM StampBox WHERE pochette = ?"
        res = self.DBExecute(self.dbCurMaster, query, (SelectedBox,))
        row = res.fetchone()
        print("after getCurrentBox")
        return [row[0], row[1]] if row else []

    def loadStampType(self):
        print("before execute stamp type")
        query = (
            "SELECT DISTINCT type FROM Stamp_List WHERE type IS NOT NULL ORDER"
            " BY type ASC"
        )
        res = self.DBExecute(self.dbCurCountry, query)
        print("after execute2")
        return [row[0] for row in res.fetchall() if row[0] is not None]

    def loadStampList(self, stampType: str, year: str):
        print("loadStampList")
        query = """
            SELECT key, nbr FROM Stamp_list 
            WHERE type = ? AND year = ? 
            ORDER BY sequence, ascii_seq, nbr, year ASC
        """
        res = self.DBExecute(self.dbCurCountry, query, (stampType, year))
        print("after loadStampList")
        return [[row[0], row[1]] for row in res.fetchall() if row[0] is not None]

    def getMinYearForType(self, stampType: str):
        print("getMinYearForType")
        query = (
            "SELECT DISTINCT year FROM Stamp_List WHERE type = ? AND year IS NOT"
            " NOT NULL ORDER BY year ASC"
        )
        res = self.DBExecute(self.dbCurCountry, query, (stampType,))
        row = res.fetchone()
        print("after getMinYearForType")
        return row[0] if row else ""

    def loadYearList(self, stampType: str):
        print("loadYearList")
        query = """
            SELECT DISTINCT year FROM Stamp_list 
            WHERE type = ? AND year IS NOT NULL 
            ORDER BY year ASC
        """
        res = self.DBExecute(self.dbCurCountry, query, (stampType,))
        print("after loadYearList")
        return [row[0] for row in res.fetchall()]

    def getStampSubNbr(self, Key):
        print("getStampSubNbr")
        query = "SELECT sub_nbr FROM stamp_list WHERE Key = ?"
        res = self.DBExecute(self.dbCurCountry, query, (Key,))
        print("after getStampSubNbr")
        return [row[0] for row in res.fetchall()]

    def getPochette(self, stampNbr, stampType, stampYear, stampKey):
        print("getPochette")
        query1 = """
            SELECT width, height FROM stamp_list 
            WHERE type = ? AND year = ? AND nbr = ? AND key = ?
        """
        res = self.DBExecute(
            self.dbCurCountry,
            query1,
            (str(stampType), str(stampYear), str(stampNbr), stampKey),
        )
        row = res.fetchone()

        width = row[0] if row and row[0] else "0"
        height = row[1] if row and row[1] else "0"

        query2 = "SELECT pochette FROM StampBox WHERE lx = ? AND ly = ?"
        res2 = self.DBExecute(self.dbCurMaster, query2, (width, height))
        ret = [r[0] for r in res2.fetchall()]

        if not ret:
            ret.append("Pochette 30x41")
        print("after getPochette")
        return ret

    def stampChanged(self, stampNbr, Key):
        print("stampChanged")
        query = """
            SELECT nbr, year, valuecolor, stampDescription, width, height, sub_nbr, stampDescription1 
            FROM stamp_list
            WHERE nbr = ? AND Key = ?
        """
        print(query)
        res = self.DBExecute(self.dbCurCountry, query, (str(stampNbr), Key))
        print("after query")
        row = res.fetchone()
        print("after stampChanged")
        return list(row) if row else []

    def getMessage(self, msgLanguage: str, msgCode):

        query = (
            "SELECT message_text, message_type FROM messages WHERE"
            " message_language = ? AND message_code = ?"
        )
        res = self.DBExecute(
            self.dbCurMaster, query, (msgLanguage, str(msgCode))
        )
        return [row[0] for row in res.fetchall()]

    def getTranslation(self, msgLanguage: str, msgCode):
        query = (
            "SELECT msg_text FROM translations WHERE msg_language = ? AND"
            " msg_code = ?"
        )
        res = self.DBExecute(
            self.dbCurMaster, query, (msgLanguage, str(msgCode))
        )
        return [row[0] for row in res.fetchall()]

    def close(self):
        """Fermeture explicite des connexions"""
        if self.con_country:
            self.con_country.close()
        if self.con_master:
            self.con_master.close()