#!/usr/bin/env python3
from models import Station, Stop, Line, coordinates_to_geography
from datetime import datetime
from shapely import wkt
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

BERLIN_CENTER = coordinates_to_geography(wkt.loads('POLYGON((13.397554705226526 52.55577511250286,13.34399635561715 52.53990827773609,13.277735064113244 52.53092844861436,13.274988482081994 52.49749899889902,13.312753985011682 52.476174448880776,13.427258835295106 52.457571347161775,13.475324020841981 52.47116746155413,13.487059832063096 52.509231759524376,13.480193376984971 52.53555255182724,13.436248064484971 52.55559590471181,13.397554705226526 52.55577511250286))'))
MAX_DISTANCE = 2000 # 2km

START = int(datetime.now(TIMEZONE) \
            .replace(hour=0, minute=1, second=0) \
            .astimezone(pytz.utc).timestamp())
END = int(datetime.now(TIMEZONE) \
            .replace(hour=3, minute=0, second=0) \
            .astimezone(pytz.utc).timestamp())

candidates = []
with open(f'sim_results/results-{datetime.now().timestamp()}.csv', 'w') as file:
    for station in stations_instances:
        if not station.location.within(BERLIN_CENTER):
            continue
        for line in station.lines:
            for direction in line.next_stations(station): # en teoria 2
                i = 1
                while True: #while more stations in direction
                    common_station = line.station_from_direction_steps(station, direction, i)
                    i += 1
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
                                j += 1
                                print('is candidate valid?')
                                if candidate is None:
                                    print('nope, no more stations remain')
                                    break
                                candidate = candidate.station
                                is_within = candidate.location.within(BERLIN_CENTER)
                                is_closer_than_max_distance = candidate.location.distance(station.location) <= MAX_DISTANCE
                                if not is_within or not is_closer_than_max_distance:
                                    print('nope, too far away')
                                    continue
                                print('candidate:')
                                print(candidate.name)
                                loops_without_new_candidate = 0
                                for minute in range(START, END, 120):
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

print('*******CANDIDATES********')
for candidate in candidates:
    print('............')
    print(f'From: {candidate[0]}')
    print(f'To: {candidate[1]}')
    print(f'Common_destination: {candidate[2]}')
    print(f'Time:{candidate[3]}')
