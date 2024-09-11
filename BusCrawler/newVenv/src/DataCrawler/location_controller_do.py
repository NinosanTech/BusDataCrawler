from Helper.geographics import get_cities
from pandas import DataFrame as df
from .serializer import Serializer, ExistBehavior
from datetime import date, timedelta, datetime
import numpy as np
from .location_controller_abstract import LocationControllerAbstract
from typing import override

class LocationControllerDigitalOcean(LocationControllerAbstract):

    def __init__(self, serializer: Serializer=None):
        super().__init__(serializer)
        self._LOCATION_STRING = "location_combinations"

    def get_usable_location_combinations(self) -> df:
        return self._serializer.read(f'SELECT * FROM "{self._LOCATION_STRING}" where STATUS < 7.0')
    
    def get_next_location_combinations(self, amount: int = 1, min_time_delta: timedelta = timedelta(0)) -> df:
        last_time_ok = datetime.strftime(datetime.now() - timedelta(hours=1), self._date_string)
        data = self._serializer.read(f"SELECT * FROM \"{self._LOCATION_STRING}\" \
            where Status < 10 and (Blocked IS NULL or Blocked < '{last_time_ok}') ORDER BY Last_Checked ASC \
                LIMIT {amount}")
        non_fulfilling_rows = [(datetime.now() - datetime.strptime(d, self._date_string)) \
            < min_time_delta for d in data['Last_Checked']]
        data.drop(np.where(non_fulfilling_rows)[0])
        current_time = datetime.strftime(datetime.now(), self._date_string)
        [self._serializer.update(f"UPDATE \"{self._LOCATION_STRING}\" \
            SET Blocked = '{current_time}' \
            WHERE Origin = '{o}' \
            AND Destination = '{d}'") \
            for o,d in zip(data['Origin'], data['Destination'])]
        return data

    def origin_not_available(self, id: int, origin: str, destination: str, increase_status: bool, status: int=-1):
        current_date = datetime.now().strftime(self._date_string)
        self._serializer.update(f"UPDATE \"{self._LOCATION_STRING}\" \
            SET Last_Checked = '{current_date}', Status = {status} \
            WHERE Origin = '{origin}' \
            OR Destination = '{origin}'")

    def destination_not_available(self, id: int, origin: str, destination: str, increase_status: bool, status: int=-1):
        current_date = datetime.now().strftime(self._date_string)
        self._serializer.update(f"UPDATE \"{self._LOCATION_STRING}\" \
            SET Last_Checked = '{current_date}', Status = {status} \
            WHERE Origin = '{destination}' \
            OR Destination = '{destination}'")

    @override
    def update_location_status(self, id: int, origin: str, destination: str, increase_status: bool, status: int=-1, increase_status_value: int=0):
        current_date = datetime.now().strftime(self._date_string)
        if status != -1:
            self._serializer.update(f"UPDATE \"{self._LOCATION_STRING}\" \
                SET Last_Checked = '{current_date}', Status = {status}, Blocked = null \
                WHERE Origin = '{origin}' \
                AND Destination = '{destination}'")
        elif increase_status:
            self._serializer.update(f"UPDATE {self._LOCATION_STRING} \
                SET Last_Checked = '{current_date}', Status = Status + 1, Blocked = null \
                WHERE Origin = '{origin}' \
                AND Destination = '{destination}'")
        elif increase_status_value > 0:
            self._serializer.update(f"UPDATE {self._LOCATION_STRING} \
                SET Last_Checked = '{current_date}', Status = Status + {increase_status_value}, Blocked = null \
                WHERE Origin = '{origin}' \
                AND Destination = '{destination}'")
        else:
            self._serializer.update(f"UPDATE {self._LOCATION_STRING} \
                SET Last_Checked = '{current_date}', Status = 0, Blocked = null \
                WHERE Origin = '{origin}' \
                AND Destination = '{destination}'")