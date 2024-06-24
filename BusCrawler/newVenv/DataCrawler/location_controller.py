from Helper.geographics import get_cities
from pandas import DataFrame as df
from DataCrawler.serializer import Serializer

class Location_Controller():

    def __init__(self):
        self._serializer = None
    
    def _connect_serializer(self):
        if self._serializer is None:
            serializer = Serializer()
            serializer.connect_database()

    def get_location_combinations(country: str = 'AR') -> list:
        cities = get_cities('AR')
        cities_combinations = []
        for i in range(len(cities)):
            for j in range(len(cities)):
                if i != j:
                    cities_combinations.append((cities[i], cities[j]))
        return cities_combinations

    def serialize_location_combinations(self, combinations: list):
        combinations_dataframe = df(combinations,columns=['Origin', 'Destination'])
        combinations_dataframe.insert(2, 'Status', [0]*len(combinations_dataframe))
        table_name = 'location_combinations'
        self._connect_serializer()
        self._serializer.write(combinations_dataframe, table_name)

    def get_usable_location_combinations(self) -> df:
        self._connect_serializer()
        return self._serializer.read('SELECT * FROM [dbo].[location_combinations] where STATUS < 5.0')