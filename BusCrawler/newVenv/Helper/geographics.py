import geonamescache

def get_cities(country_code: str) -> list:
    gc = geonamescache.GeonamesCache()
    cities = gc.get_cities()
    return_cities = []
    for key in cities:
        cities_for_key = cities[key]
        if cities_for_key['countrycode'] == country_code:
            city_name = cities_for_key['name']
            if city_name not in return_cities:
                return_cities.append(city_name)
    return return_cities