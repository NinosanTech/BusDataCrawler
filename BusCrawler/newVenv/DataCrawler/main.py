import logging
from BusPlatformCrawler.plataforma10_crawler import retrieve_plataforma10_info

# Setup logging
logging.basicConfig(level=logging.INFO, format='%(asctime)s - %(processName)s - %(levelname)s - %(message)s')

def init_worker():
    import signal
    signal.signal(signal.SIGINT, signal.SIG_IGN)

def worker_wrapper(args):
    
    start_message = f"Worker started for {args}"
    logging.info(start_message)
    result = retrieve_plataforma10_info(*args)
    end_message = f"Worker finished for {args}"
    logging.info(end_message)
    return result

if __name__ == '__main__':

    from Helper.geographics import get_cities
    
    import pandas as pd
    import multiprocessing
    from datetime import date, timedelta

    multiprocessing.set_start_method('spawn', True)
    
    cities = get_cities('AR')
    cities_combinations = []
    for i in range(len(cities)):
        for j in range(len(cities)):
            if i != j:
                cities_combinations.append((cities[i], cities[j]))
    searchdate = date.strftime(date.today() + timedelta(days=1), '%d/%m/%Y')
    results = []
    
    with multiprocessing.Pool(processes=1) as pool:

    #for comb in cities_combinations:
    #print(f"Searching from {comb[0]} to {comb[1]}:\n")
    #    new_result = retrieve_plataforma10_info(comb[0], comb[1], date)
        
        try:
            inputs = [[c[0], c[1], searchdate] for c in cities_combinations]
            #for new_result in pool.starmap(retrieve_plataforma10_info, inputs):
            for new_result in pool.imap_unordered(worker_wrapper, inputs):
                if new_result is None or (type(new_result) is list and new_result[0] is None):
                    continue
                if len(results) == 0:
                    results = pd.concat([new_result])
                else:
                    results = pd.concat([results,new_result])
        except Exception as e:
            pool.terminate()
            pool.join()
            print(f"Error: {e}", flush=True)

    print(results)