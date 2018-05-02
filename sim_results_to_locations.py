#!/usr/bin/env python3
from models import Station
from shapely.geometry import LineString

stations_instances = Station.get_stations()
stations_dict = Station.all_stations

with open('sim_results/15kmhr_with_coordinates.csv', 'w') as result_file:
    result_file.write('the_geom,timestamp\n')
    with open('./sim_results/15kmhr-results-1525275666.18206.csv') as csvfile:
        for line in csvfile:
            data = line.split(';')
            origin_id = data[1]
            origin = stations_dict[origin_id]
            shuttle_combination_id = data[3]
            shuttle_combination = stations_dict[shuttle_combination_id]
            common_station_id = data[5]
            common_station = stations_dict[common_station_id]
            line = LineString([origin.location, common_station.location, shuttle_combination.location])
            timestamp = data[6]
            result = [f'"{line.wkt}"', timestamp]
            result_file.write(','.join(result))
print('Done')
