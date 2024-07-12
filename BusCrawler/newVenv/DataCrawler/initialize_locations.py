from location_controller import Location_Controller
import multiprocessing
from output_handler import handle_location_output
from crawler_worker import Worker, Worker_Type
from BusPlatformCrawler.website_crawler_abstract import Debug
from datetime import date, timedelta
from pandas import DataFrame as df

def worker_wrapper(worker: Worker, data: list) -> list:
    return worker.run(data)

loc = Location_Controller()
combs = loc.get_location_combinations()
loc.serialize_location_combinations(combs)
if __name__ == '__main__':
    number_processes = 4
    location_controller = Location_Controller()
    worker = Worker(Debug.AZURE_DEPLOY, Worker_Type.CHECK_LOCATIONS)
    while True:
        cities_combinations = location_controller.get_next_location_combinations(number_processes, timedelta(hours=0))
        cities_combinations = cities_combinations.iloc[:, 0:3].values.tolist()
        searchdate = date.strftime(date.today() + timedelta(days=1), '%d/%m/%Y')
        results = df()

        multiprocessing.set_start_method('spawn', True)
        with multiprocessing.Pool(processes=number_processes) as pool:
            inputs = [[c[0], c[1], c[2], searchdate] for c in cities_combinations]
            cities_output_logging = []
            for output in pool.starmap(worker_wrapper, [(worker, i) for i in inputs]):
                handle_location_output(output)