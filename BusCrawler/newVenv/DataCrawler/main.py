import logging
from BusPlatformCrawler.plataforma10_crawler import retrieve_plataforma10_info
import pandas as pd
from pandas import DataFrame as df
from datetime import date, timedelta
import _pydevd_bundle.pydevd_constants
_pydevd_bundle.pydevd_constants.PYDEVD_WARN_EVALUATION_TIMEOUT = 10

# Setup logging
logging.basicConfig(level=logging.INFO, format='%(asctime)s - %(processName)s - %(levelname)s - %(message)s')

def init_worker():
    import signal
    signal.signal(signal.SIGINT, signal.SIG_IGN)

def worker_wrapper(args):
    try:
        start_message = f"Worker started for {args}"
        logging.info(start_message)
        result = retrieve_plataforma10_info(*args)
        end_message = f"Worker finished for {args}"
        logging.info(end_message)
        return result
    except Exception as e:
        print(f"Error: {e}", flush=True)
        return None

def serialize(data: df):
    from sqlalchemy import create_engine
    import pyodbc
    # Verbindung zur Azure SQL Database herstellen
    server = 'busdata.database.windows.net'
    database = 'BusDataBase'
    username = credentials.sql_database_username
    password = credentials.sql_database_password
    driver = 'ODBC Driver 18 for SQL Server'
    database_url = f'mssql+pyodbc://{username}:{password}@{server}/{database}?driver={driver}'

    engine = create_engine(database_url)

    # DataFrame in die SQL-Datenbank schreiben
    today = date.strftime(date.today(), '%d/%m/%Y')
    data.to_sql(today, con=engine, if_exists='replace', index=False)


if __name__ == '__main__':
    from Helper.geographics import get_cities
    import multiprocessing

    multiprocessing.set_start_method('spawn', True)
    
    cities = get_cities('AR')
    cities_combinations = []
    for i in range(len(cities)):
        for j in range(len(cities)):
            if i != j:
                cities_combinations.append((cities[i], cities[j]))
    searchdate = date.strftime(date.today() + timedelta(days=1), '%d/%m/%Y')
    results = []

#    cities_combinations = cities_combinations[0:20]
    
    with multiprocessing.Pool(processes=10) as pool:
            inputs = [[c[0], c[1], searchdate] for c in cities_combinations]
            for new_result in pool.imap_unordered(worker_wrapper, inputs):
                if new_result is None or (type(new_result) is list and new_result[0] is None):
                    continue
                if len(results) == 0:
                    results = pd.concat([new_result])
                else:
                    results = pd.concat([results,new_result])
    serialize(results)
    print(results)