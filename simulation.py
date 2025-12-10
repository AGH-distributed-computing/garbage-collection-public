import json
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


detached_house_time_series = load_time_series("data/detached_house.json")
apartment_building_time_series = load_time_series("data/apartment_building.json")
public_facility_time_series = load_time_series("data/public_facility.json")
production_plant_time_series = load_time_series("data/production_plant.json")

city = City("data/city1_topography.json", "data/city1_trucks.json")

running = True
current_time = 0
tick_duration = 15
empty_bin_duration = 1
average_speed = 20 #to be swapped by getting speed on road for given time using traffic time series in the future

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