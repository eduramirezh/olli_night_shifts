#!/usr/bin/env python3
from models.station import Station, Stop, Line
from datetime import datetime
import pytz

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

START = datetime.now(pytz.timezone("Europe/Berlin")) \
            .replace(hour=1, minute=0, second=0) \
            .astimezone(pytz.utc).timestamp()
START = datetime.now(pytz.timezone("Europe/Berlin")) \
            .replace(hour=1, minute=0, second=0) \
            .astimezone(pytz.utc).timestamp()

#for minute in range(START, END):
for station in stations_instances[:10]:
    for journey in station.departures(int(START)):
        current_line = journey.line
        direction = journey.direction
        intersecting_lines = current_line.intersecting_lines(station, direction)
        print(intersecting_lines)
