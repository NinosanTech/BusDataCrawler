from .serializer import Serializer, ExistBehavior
from Helper.geographics import get_cities
from abc import ABC, abstractmethod

class LocationControllerAbstract(ABC):

    def __init__(self, serializer: Serializer=None):
        self._date_string = '%Y-%m-%d %H:%M:%S'
        self._serializer = serializer        

    def __enter__(self):
        if self._serializer is None:
            self._serializer = Serializer()
        return self 

    def __exit__(self, exc_type, exc_value, traceback):
        self._serializer.__exit__()

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
        oldest_date = date.min.strftime(self._date_string)
        combinations_dataframe.insert(3, 'Last_Checked', [oldest_date]*len(combinations_dataframe))
        self._serializer.write(combinations_dataframe, self._LOCATION_STRING, ExistBehavior.OVERWRITE)
    
    @abstractmethod
    def update_location_status(self, id: int, origin: str, destination: str, increase_status: bool, status: int=-1, increase_status_value: int=0):
        pass