#!/usr/bin/env python3
from models import Station, Stop, Line, coordinates_to_geography
from statistics import mean, median, mode

stations_instances = Station.get_stations()
stations_dict = Station.all_stations
line_instances = Line.get_lines()
lines_dict = Line.all_lines

number_of_combinations = []
for station in stations_instances:
    number_of_combinations.append(len(station.lines))

print(f'mean: {mean(number_of_combinations)}')
print(f'median: {median(number_of_combinations)}')
print(f'mode: {mode(number_of_combinations)}')
