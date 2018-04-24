#!/usr/bin/env python3
from models.station import Station, Stop, Line
import time

stations_instances = Station.get_stations()
stations_dict = Station.all_stations
line_instances = Line.get_lines()
lines_dict = Line.all_lines

#for line in line_instances:
#    if not line.name.startswith('U'):
#        continue
#    intersecting_lines = line.intersecting_lines()
#    print(f'** Line: {line.name}**')
#    print(f'All stations: {[x.name for x in line.stations_set]}')
#    print('Intersecting:')
#    for line_id in intersecting_lines:
#        line = lines_dict[line_id]
#        print(f' -- {line.name}:')
#        for station in intersecting_lines[line_id]:
#            print(f' -- -- {station.name}')

START = 1000
END = 7000

#for minute in range(START, END):
for station in stations_instances[:2]:
    print(station.departures(time.time()))
