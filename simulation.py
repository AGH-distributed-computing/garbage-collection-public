import json
from time import sleep

from city import City

def load_time_series(file_path):
    try:
        with open(file_path, 'r', encoding='utf-8') as f:
            data = json.load(f)
    except FileNotFoundError:
        print(f"Error: File '{file_path}' not found.")
        raise
    except json.JSONDecodeError as e:
        print(f"Error: Invalid JSON format in file '{file_path}'.")
        print(f"Details: {e}")
        raise
    return data['garbageSeries']

#this json data is meant to be read single time, at start of the program
detached_house_time_series = load_time_series("data/detached_house.json")
apartment_building_time_series = load_time_series("data/apartment_building.json")
public_facility_time_series = load_time_series("data/public_facility.json")
production_plant_time_series = load_time_series("data/production_plant.json")
#this also read single time
city = City("data/city1_topography.json", "data/city1_trucks.json", verbose=True)

running = True
current_time = 0
tick_duration = 15
empty_bin_duration = 1
average_speed = 20 #to be swapped by getting speed on road for given time using traffic time series in the future

#this data is read as there is no web api yet, to be changed for receiving from api in the future
#example_trucks_orders.json is provided as an example of what can be used
filepath = "data/example_truck_orders.json"

try:
    with open(filepath, 'r', encoding='utf-8') as file:
        json_string = file.read()

    city.parseOrdersForTruck(json_string)
except FileNotFoundError:
    print(f"Error: File '{filepath}' not found")
    raise

#this data is also read as there is no web api yet
#bin_alert.json is provided as an example of what can be used
filepath = "data/bin_alert.json"

try:
    with open(filepath, 'r', encoding='utf-8') as file:
        json_string = file.read()

    city.setAlertLevels(json_string)
except FileNotFoundError:
    print(f"Error: File '{filepath}' not found")
    raise

#we calculate fuel consumption by hours, so at each loop iteration fuel should be decreased
while running:
    city.updateRubbish(detached_house_time_series,
                        apartment_building_time_series,
                        public_facility_time_series,
                        production_plant_time_series,
                        time_series_duration=672,
                        tick_duration=tick_duration,
                        current_time=current_time
                        )
    city.executeOrders(average_speed, tick_duration, empty_bin_duration)
    city.decreaseAllFuel(tick_duration)
    current_time += tick_duration

    print(city.getAlertBins())
#    sleep(0.05)