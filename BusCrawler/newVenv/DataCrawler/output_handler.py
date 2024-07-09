from location_controller import Location_Controller
import pandas as pd
from pandas import DataFrame as df

def handle_output(output: list) -> df:
    results = df()
    location_controller = Location_Controller()
    if type(output[1]) is not list:
        print(f"No output created due to error!")
    else:
        new_result = output[0]
        cities_output = output[1][0:3]
        if new_result is None or (type(new_result) is list and new_result[0] is None):
            location_controller.update_location_status(\
                cities_output[0], cities_output[1], cities_output[2], False)
        elif type(new_result) is not df and new_result == -1:
            location_controller.update_location_status(\
                cities_output[0], cities_output[1], cities_output[2], True)
        elif type(new_result) is not df and new_result == -2:
            location_controller.update_location_status(\
                cities_output[0], cities_output[1], cities_output[2], True)
        elif type(new_result) is not df:
            print(f"Unexpected data type for result")
            print(f"Result is: {new_result}")
        else:
            results = pd.concat([new_result])
            location_controller.update_location_status(\
                cities_output[0], cities_output[1], cities_output[2], False)
    return results

#def handle_location_output(output: int):
