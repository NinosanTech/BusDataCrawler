from Helper.geographics import get_cities
from pandas import DataFrame as df
from serializer import Serializer
from datetime import date, timedelta, datetime
import numpy as np

class Location_Controller():

    def __init__(self):
        self._connect_serializer()
        self._date_string = '%Y-%m-%d %H:%M:%S'
    
    def _connect_serializer(self):
        self._serializer = Serializer()
        self._serializer.connect_database()

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
        table_name = 'location_combinations'
        self._connect_serializer()
        self._serializer.write(combinations_dataframe, table_name)

    def get_usable_location_combinations(self) -> df:
        return self._serializer.read('SELECT * FROM [dbo].[location_combinations] where STATUS < 5.0')
    
    def get_next_location_combinations(self, amount: int = 1, min_time_delta: timedelta = timedelta(0)) -> df:
        data = self._serializer.read(f'SELECT TOP {amount} * FROM [dbo].[location_combinations] \
            where Status < 5 ORDER BY Last_Checked ASC')
        non_fulfilling_rows = [(datetime.now() - datetime.strptime(d, self._date_string)) \
            < min_time_delta for d in data['Last_Checked']]
        return data.drop(np.where(non_fulfilling_rows)[0])

    def update_location_status(self, id: int, origin: str, destination: str, increase_status: bool):
        current_date = datetime.now().strftime(self._date_string)
        if increase_status:
            self._serializer.update(f"UPDATE [dbo].[location_combinations] \
                SET Last_Checked = '{current_date}', Status = Status + 1 \
                WHERE Origin = '{origin}' \
                AND Destination = '{destination}'")
        else:
            self._serializer.update(f"UPDATE [dbo].[location_combinations] \
                SET Last_Checked = '{current_date}' \
                WHERE Origin = '{origin}' \
                AND Destination = '{destination}'")