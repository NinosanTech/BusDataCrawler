from sqlalchemy import create_engine, update, text
import pyodbc
from pandas import DataFrame
import pandas as pd
from . import credentials
from enum import Enum

class ExistBehavior(Enum):
    APPEND = "append"
    OVERWRITE = "replace"

class DataBase(Enum):
    AZURE = "azure"
    DIGITAL_OCEAN = "digital_ocean"

class Serializer():
    
    def __init__(self, type: DataBase=DataBase.DIGITAL_OCEAN):
        self._engine = None
        self._conn = None
        self._type = type

    def __enter__(self):
        self.connect_database()
        return self

    def __exit__(self, exc_type, exc_value, traceback):
        self._conn.close()
        self._engine.dispose()

    def connect_database(self):
        if self._type == DataBase.AZURE:
            server = 'busdata.database.windows.net'
            database = 'BusDataBase_v2'
            username = credentials.sql_database_username
            password = credentials.sql_database_password
            driver = 'ODBC Driver 18 for SQL Server'
            database_url = f'mssql+pyodbc://{username}:{password}@{server}/{database}?driver={driver}'
        elif self._type == DataBase.DIGITAL_OCEAN:
            server = 'db-mysql-fra1-bus-data-crawler-v1-do-user-17586954-0.d.db.ondigitalocean.com'
            port = 25060
            database = 'defaultdb'
            username = credentials.dig_ocean_username
            password = credentials.dig_ocean_password
            database_url = f'mysql+mysqlconnector://{username}:{password}@{server}:{port}/{database}'
        else:
            raise Exception(f"Data Base type {self._type.name} not valid!")
            return

        self._engine = create_engine(database_url)
        self._conn = self._engine.connect()
    
    def write(self, data: DataFrame, table_name: str, exist_behavior: ExistBehavior=ExistBehavior.APPEND, index_label:str = 'index'):
        data.to_sql(table_name, con=self._conn, if_exists=exist_behavior.value, index=False, index_label=index_label)

    def read(self, query: str) -> DataFrame:
        return pd.read_sql(query, con=self._conn)
    
    def update(self, query: str):
        self._conn.execute(text(query))
        self._conn.commit()
