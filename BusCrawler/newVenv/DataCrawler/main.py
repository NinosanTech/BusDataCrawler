import logging
from BusPlatformCrawler.plataforma10_crawler import plataforma10_crawler
import pandas as pd
from pandas import DataFrame as df
from datetime import date, timedelta
import _pydevd_bundle.pydevd_constants
_pydevd_bundle.pydevd_constants.PYDEVD_WARN_EVALUATION_TIMEOUT = 20
from BusPlatformCrawler.website_crawler_abstract import Debug
import credentials

DEBUG = Debug.AZURE_DEPLOY

# Setup logging
logging.basicConfig(level=logging.INFO, format='%(asctime)s - %(processName)s - %(levelname)s - %(message)s')

def init_worker():
    import signal
    signal.signal(signal.SIGINT, signal.SIG_IGN)

def worker_wrapper(args):
    try:
        start_message = f"Worker started for {args}"
        logging.info(start_message)
        crawler = plataforma10_crawler(*args)
        crawler.debug = DEBUG
        result = crawler.retrieve_info()
        end_message = f"Worker finished for {args}"
        logging.info(end_message)
        return [result, args]
    except Exception as e:
        print(f"Error: {e}", flush=True)
        return args

def serialize(data: df, table_appendix: str=''):
    from DataCrawler.serializer import Serializer

    serializer = Serializer()
    serializer.connect_database()
    table_name = date.strftime(date.today(), '%d/%m/%Y') + table_appendix
    serializer.write(table_name)

if __name__ == '__main__':
    from DataCrawler.location_controller import Location_Controller
    import multiprocessing

    location_controller = Location_Controller()
    cities_combinations = location_controller.get_usable_location_combinations()
    cities_combinations = cities_combinations.iloc[:, 0:2].values.tolist()
    searchdate = date.strftime(date.today() + timedelta(days=1), '%d/%m/%Y')
    results = []
   
    multiprocessing.set_start_method('spawn', True)
    with multiprocessing.Pool(processes=4) as pool:
        inputs = [[c[0], c[1], searchdate] for c in cities_combinations]
        cities_output_logging = []
        for output in pool.imap_unordered(worker_wrapper, inputs):
            if len(output) < 2:
                print(f"[{output[0][0]} to {output[0][1]}]: No output created due to error!")
            else:
                new_result = output[0]
                cities_output = output[1][0:2]
                if new_result is None or (type(new_result) is list and new_result[0] is None):
                    cities_output.append(0)
                elif type(new_result) is not df and new_result == -1:
                    cities_output.append(-1)
                elif type(new_result) is not df and new_result == -2:
                    cities_output.append(-2)
                else:
                    if len(results) == 0:
                        results = pd.concat([new_result])
                    else:
                        results = pd.concat([results,new_result])
                    cities_output.append(1)
                cities_output_logging.append(cities_output)
    serialize(results)
    cities_output_logging_dataframe = df(cities_output_logging,columns=['Origin', 'Destination', 'Status'])
    serialize(cities_output_logging_dataframe, '_input_logging')
    print(results)