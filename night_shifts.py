#!/usr/bin/env python3
from models import Station, Stop, Line
from datetime import datetime
import pytz

stations_instances = Station.get_stations()
stations_dict = Station.all_stations
line_instances = Line.get_lines()
lines_dict = Line.all_lines

TIMEZONE = pytz.timezone("Europe/Berlin")

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

START = int(datetime.now(TIMEZONE) \
            .replace(hour=0, minute=1, second=0) \
            .astimezone(pytz.utc).timestamp())
END = int(datetime.now(TIMEZONE) \
            .replace(hour=6, minute=0, second=0) \
            .astimezone(pytz.utc).timestamp())

candidates = []
with open(f'sim_results/results-{datetime.now().timestamp()}.csv', 'w') as file:
    for station in stations_instances:
        for line in station.lines:
            for direction in line.next_stations(station): # en teoria 2
                i = 1
                while True: #while more stations in direction
                    common_station = line.station_from_direction_steps(station, direction, i)
                    if common_station is None:
                        print('no common station')
                        break
                    common_station = common_station.station
                    for different_line in common_station.lines:
                        if different_line == line:
                            continue
                        print('========')
                        print(station.name)
                        print(common_station.name)
                        print(different_line.name)
                        print(f'distance: {station.location.distance(common_station.location)}')
                        print('...............')
                        print('different_line next_stations')
                        [print(x.name) for x in different_line.next_stations(common_station)]
                        print('========')
                        for different_direction in different_line.next_stations(common_station):
                            j = 1
                            while True: #while more stations in direction
                                candidate = different_line.station_from_direction_steps(common_station, different_direction, j)
                                if candidate is None:
                                    break
                                candidate = candidate.station
                                print('candidate:')
                                print(candidate.name)
                                loops_without_new_candidate = 0
                                for minute in range(START, END, 60):
                                    readable_minute = str(datetime.fromtimestamp(minute, TIMEZONE))
                                    if station.time_to_station(common_station, minute) > (station.time_by_shuttle_in_minutes(candidate) + candidate.time_to_station(common_station, minute)):
                                        result = [station.name, station._id, candidate.name, candidate._id, common_station.name, common_station._id, readable_minute]
                                        candidates.append(result)
                                        file.write(",".join(result) + '\n')
                                        print('New candidate!')
                                        loops_without_new_candidate = 0
                                    else:
                                        loops_without_new_candidate += 1
                                    if loops_without_new_candidate > 30:
                                        break
                                j += 1
                    i += 1

print('*******CANDIDATES********')
for candidate in candidates:
    print('............')
    print(f'From: {candidate[0]}')
    print(f'To: {candidate[1]}')
    print(f'Common_destination: {candidate[2]}')
    print(f'Time:{candidate[3]}')
