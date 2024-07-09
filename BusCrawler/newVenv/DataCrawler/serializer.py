from sqlalchemy import create_engine, update, text
import pyodbc
from pandas import DataFrame
import pandas as pd
from . import credentials
from enum import Enum

class ExistBehavior(Enum):
    APPEND = "append"
    OVERWRITE = "replace"

class Serializer():
    
    def __init__(self):
        self._engine = None

    def connect_database(self):
        server = 'busdata.database.windows.net'
        database = 'BusDataBase'
        username = credentials.sql_database_username
        password = credentials.sql_database_password
        driver = 'ODBC Driver 18 for SQL Server'
        database_url = f'mssql+pyodbc://{username}:{password}@{server}/{database}?driver={driver}'

        self._engine = create_engine(database_url)
    
    def write(self, data: DataFrame, table_name: str, exist_behavior: ExistBehavior=ExistBehavior.APPEND):
        data.to_sql(table_name, con=self._engine, if_exists=exist_behavior.value, index=True)

    def read(self, query: str) -> DataFrame:
        return pd.read_sql(query, con=self._engine)
    
    def update(self, query: str):
        with self._engine.connect() as conn:
            conn.execute(text(query))
            conn.commit()
