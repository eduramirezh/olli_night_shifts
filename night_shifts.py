#!/usr/bin/env python3
from models import Station, Stop, Line
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
END = datetime.now(pytz.timezone("Europe/Berlin")) \
            .replace(hour=1, minute=0, second=0) \
            .astimezone(pytz.utc).timestamp()

candidates = []
#for minute in range(START, END):
for station in stations_instances[:10]:
    for line in station.lines:
        for direction in line.next_stations(station): # en teoria 2
            i = 1
            while True: #while more stations in direction
                common_station = line.station_from_direction_steps(station, direction, i)
                if common_station is None:
                    print('no common station')
                    break
                for different_line in common_station.lines:
                    if different_line == line:
                        continue
                    for different_direction in different_line.next_stations(common_station):
                        j = 1
                        while True: #while more stations in direction
                            candidate = different_line.station_from_direction_steps(common_station, different_direction, j)
                            if station.time_to_station(common_station) > (station.time_by_shuttle_in_minutes(candidate) + candidate.time_to_station(common_station)):
                                candidates.append(candidate)
                            j += 1
                i += 1
