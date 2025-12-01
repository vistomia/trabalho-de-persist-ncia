# import logging
# import logger as logger
import sqlite3
from models.user import User
from sqlalchemy import event
from sqlmodel import create_engine, Session
class Database:
    """Gerencia um banco de dados baseado em um arquivo CSV com um índice sequencial.
    
    :param str uri: URI do banco de dados.
    :return: None
    """
    def __init__(self, uri: str):
        self.__engine = create_engine(uri, echo_pool=True)
        # self.logger = logging.getLogger(__name__)
        user = User()

        event.listen(self.__engine, "connect", self._set_sqlite_pragma)

    @staticmethod
    def _set_sqlite_pragma(dbapi_connection, connection_record):
        if isinstance(dbapi_connection, sqlite3.Connection):
            cursor = dbapi_connection.cursor()
            cursor.execute("PRAGMA foreign_keys=ON")
            cursor.close()
    
    def get_engine(self):
        return self.__engine
    
    def get_session(self):
        return Session(self.__engine)
