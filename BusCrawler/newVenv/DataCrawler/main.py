import logging
import pandas as pd
from pandas import DataFrame as df
from datetime import date, timedelta
import _pydevd_bundle.pydevd_constants
_pydevd_bundle.pydevd_constants.PYDEVD_WARN_EVALUATION_TIMEOUT = 20
from crawler_worker import Worker, Worker_Type
import credentials
from BusPlatformCrawler.website_crawler_abstract import Debug


# Setup logging
logging.basicConfig(level=logging.INFO, format='%(asctime)s - %(processName)s - %(levelname)s - %(message)s')

def init_worker():
    import signal
    signal.signal(signal.SIGINT, signal.SIG_IGN)

def serialize(data: df, table_appendix: str=''):
    from serializer import Serializer

    if type(data) is not df:
        Warning('Given serialization object is no data frame!')
        return
    if data.empty:
        return
    serializer = Serializer()
    serializer.connect_database()
    table_name = date.strftime(date.today(), '%d/%m/%Y') + table_appendix
    serializer.write(data, table_name)

def worker_wrapper(worker: Worker, data: list) -> list:
    return worker.run(data)

if __name__ == '__main__':
    from location_controller import Location_Controller
    import multiprocessing
    from output_handler import handle_output

    number_processes = 4
    location_controller = Location_Controller()
    worker = Worker(Debug.AZURE_DEPLOY, Worker_Type.CRAWL)
    while True:
        cities_combinations = location_controller.get_next_location_combinations(number_processes, timedelta(hours=10))
        cities_combinations = cities_combinations.iloc[:, 0:3].values.tolist()
        searchdate = date.strftime(date.today() + timedelta(days=1), '%d/%m/%Y')
        results = df()
    
        multiprocessing.set_start_method('spawn', True)
        with multiprocessing.Pool(processes=number_processes) as pool:
            inputs = [[c[0], c[1], c[2], searchdate] for c in cities_combinations]
            cities_output_logging = []
            for output in pool.starmap(worker_wrapper, [(worker, i) for i in inputs]):
                results = pd.concat([results, handle_output(output)])
        serialize(results)
        print(results)