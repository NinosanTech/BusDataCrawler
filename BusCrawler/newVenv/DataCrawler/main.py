
if __name__ == '__main__':

    from Helper.geographics import get_cities
    from BusPlatformCrawler.plataforma10_crawler import retrieve_plataforma10_info
    import pandas as pd
    from multiprocessing import Pool

    cities = get_cities('AR')
    cities_combinations = []
    for i in range(len(cities)):
        for j in range(len(cities)):
            if i != j:
                cities_combinations.append((cities[i], cities[j]))
    date = "21/05/2024"
    results = []
    with Pool(processes=3) as pool:

        #for comb in cities_combinations:
    #     print(f"Searching from {comb[0]} to {comb[1]}:\n")
            #new_result = retrieve_plataforma10_info(comb[0], comb[1], date)

        inputs = [[c[0], c[1], date] for c in cities_combinations]
        for new_result in pool.starmap(retrieve_plataforma10_info, inputs):
            if new_result is None or (type(new_result) is list and new_result[0] is None):
                continue
            if len(results) == 0:
                results = pd.concat([new_result])
            else:
                results = pd.concat([results,new_result])

    print(results)