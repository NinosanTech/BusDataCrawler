from Helper.geographics import get_cities
from pandas import DataFrame as df
from serializer import Serializer, ExistBehavior
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
        self._serializer.write(combinations_dataframe, table_name, ExistBehavior.OVERWRITE)

    def get_usable_location_combinations(self) -> df:
        return self._serializer.read('SELECT * FROM [dbo].[location_combinations] where STATUS < 7.0')
    
    def get_next_location_combinations(self, amount: int = 1, min_time_delta: timedelta = timedelta(0)) -> df:
        last_time_ok = datetime.strftime(datetime.now() - timedelta(hours=1), self._date_string)
        data = self._serializer.read(f"SELECT TOP {amount} * FROM [dbo].[location_combinations] \
            where Status < 10 and (Blocked IS NULL or Blocked < '{last_time_ok}') ORDER BY Last_Checked ASC")
        non_fulfilling_rows = [(datetime.now() - datetime.strptime(d, self._date_string)) \
            < min_time_delta for d in data['Last_Checked']]
        data.drop(np.where(non_fulfilling_rows)[0])
        current_time = datetime.strftime(datetime.now(), self._date_string)
        [self._serializer.update(f"UPDATE [dbo].[location_combinations] \
            SET Blocked = '{current_time}' \
            WHERE Origin = '{o}' \
            AND Destination = '{d}'") \
            for o,d in zip(data['Origin'], data['Destination'])]
        return data

    def origin_not_available(self, id: int, origin: str, destination: str, increase_status: bool, status: int=-1):
        current_date = datetime.now().strftime(self._date_string)
        self._serializer.update(f"UPDATE [dbo].[location_combinations] \
            SET Last_Checked = '{current_date}', Status = {status} \
            WHERE Origin = '{origin}' \
            OR Destination = '{origin}'")

    def destination_not_available(self, id: int, origin: str, destination: str, increase_status: bool, status: int=-1):
        current_date = datetime.now().strftime(self._date_string)
        self._serializer.update(f"UPDATE [dbo].[location_combinations] \
            SET Last_Checked = '{current_date}', Status = {status} \
            WHERE Origin = '{destination}' \
            OR Destination = '{destination}'")

    def update_location_status(self, id: int, origin: str, destination: str, increase_status: bool, status: int=-1, increase_status_value: int=0):
        current_date = datetime.now().strftime(self._date_string)
        if status != -1:
            self._serializer.update(f"UPDATE [dbo].[location_combinations] \
                SET Last_Checked = '{current_date}', Status = {status}, Blocked = null \
                WHERE Origin = '{origin}' \
                AND Destination = '{destination}'")
        elif increase_status:
            self._serializer.update(f"UPDATE [dbo].[location_combinations] \
                SET Last_Checked = '{current_date}', Status = Status + 1, Blocked = null \
                WHERE Origin = '{origin}' \
                AND Destination = '{destination}'")
        elif increase_status_value > 0:
            self._serializer.update(f"UPDATE [dbo].[location_combinations] \
                SET Last_Checked = '{current_date}', Status = Status + {increase_status_value}, Blocked = null \
                WHERE Origin = '{origin}' \
                AND Destination = '{destination}'")
        else:
            self._serializer.update(f"UPDATE [dbo].[location_combinations] \
                SET Last_Checked = '{current_date}', Status = 0, Blocked = null \
                WHERE Origin = '{origin}' \
                AND Destination = '{destination}'")