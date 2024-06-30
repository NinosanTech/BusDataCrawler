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
        crawler = plataforma10_crawler(*args[1:])
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

    if type(data) is not df:
        Warning('Given serialization object is no data frame!')
        return
    serializer = Serializer()
    serializer.connect_database()
    table_name = date.strftime(date.today(), '%d/%m/%Y') + table_appendix
    serializer.write(data, table_name)

if __name__ == '__main__':
    from DataCrawler.location_controller import Location_Controller
    import multiprocessing

    number_processes = 1
    while True:
        location_controller = Location_Controller()
        cities_combinations = location_controller.get_next_location_combinations(number_processes, timedelta(hours=10))
        cities_combinations = cities_combinations.iloc[:, 0:3].values.tolist()
        searchdate = date.strftime(date.today() + timedelta(days=1), '%d/%m/%Y')
        results = []
    
        multiprocessing.set_start_method('spawn', True)
        with multiprocessing.Pool(processes=number_processes) as pool:
            inputs = [[c[0], c[1], c[2], searchdate] for c in cities_combinations]
            cities_output_logging = []
            for output in pool.imap_unordered(worker_wrapper, inputs):
                if len(output) < 2:
                    print(f"[{output[0][1]} to {output[0][2]}]: No output created due to error!")
                else:
                    new_result = output[0]
                    cities_output = output[1][0:3]
                    if new_result is None or (type(new_result) is list and new_result[0] is None):
                        location_controller.update_location_status(\
                            cities_output[0], cities_output[1], cities_output[2], False)
                    elif type(new_result) is not df and new_result == -1:
                        location_controller.update_location_status(\
                            cities_output[0], cities_output[1], cities_output[2], True)
                    elif type(new_result) is not df and new_result == -2:
                        location_controller.update_location_status(\
                            cities_output[0], cities_output[1], cities_output[2], True)
                    else:
                        if len(results) == 0:
                            results = pd.concat([new_result])
                        else:
                            results = pd.concat([results,new_result])
                        location_controller.update_location_status(\
                            cities_output[0], cities_output[1], cities_output[2], False)
        serialize(results)
        print(results)