from sqlalchemy import create_engine, update, text
import pyodbc
from pandas import DataFrame
import pandas as pd
from DataCrawler import credentials

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
    
    def write(self, data: DataFrame, table_name: str):
        data.to_sql(table_name, con=self._engine, if_exists='replace', index=True)

    def read(self, query: str) -> DataFrame:
        return pd.read_sql(query, con=self._engine)
    
    def update(self, query: str):
        with self._engine.connect() as conn:
            conn.execute(text(query))
            conn.commit()
