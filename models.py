import requests
import dateparser
import json
from shapely.geometry import Point
from shapely.ops import transform
from functools import partial
import pyproj

SHUTTLE_SPEED = 20 #km/hr

def coordinates_to_geography(shapely_point):
    project = partial(
        pyproj.transform,
        pyproj.Proj(init='EPSG:4326'),
        pyproj.Proj(init='EPSG:32633')
    )
    return transform(project, shapely_point)


class Stop():
    '''doc'''
    all_stops = {}
    def __init__(self, _id, name, station, lat, lon):
        self._id = _id
        self.name = name
        self.station = station
        self.location = coordinates_to_geography(Point(lon, lat))
        self.lines = set()
        type(self).all_stops[_id] = self


class Station():
    '''doc'''
    all_stations = {}
    def __init__(self, _id, name, lat, lon, weight):
        self._id = _id
        self.name = name
        self.location = coordinates_to_geography(Point(lon, lat))
        self.weight = float(weight)
        self.schedules = []
        self.linked_stations = []
        self.station = self
        self.stops = []
        self.lines = set()
        type(self).all_stations[_id] = self

    def departures_between(self, start, end):
        """tbd"""
        result = []
        for schedule in sorted(self.schedules):
            if schedule >= start and schedule <= end:
                result.append(schedule)
        return result


    def time_to_station(self, station):
        pass


    def contiguous_stations(self):
        contiguous = []
        for line in self.lines:
            contiguous.extend(line.next_stations(self))
        return contiguous



    def next_departure(self, current_time):
        """tbd"""
        for schedule in sorted(self.schedules):
            if schedule >= current_time:
                return schedule

    def next_arrival_to(self, station_id, current_time):
        """tbd"""
        pass

    def departures(self, timestamp):
        """tbd"""
        journeys = []
        directions = self.contiguous_stations()
        for direction in directions:
            url = f'http://localhost:3000/stations/{self._id}/departures?when={int(timestamp)}&nextStation={direction._id}'
            journeys_data = requests.get(url).json()
            for journey in journeys_data:
                if journey.get('cancelled', False):
                    continue
                journeys.append(Journey(journey['journeyId'], self, journey['when'], direction, journey['line'], journey['trip'], journey['delay']))
        return journeys


    @classmethod
    def common_linked_stations(cls, station_a, station_b):
        """to be documented"""
        return set(station_a.linked_stations).intersection(set(station_b.linked_stations))

    @classmethod
    def minutes_between(cls, station_a, station_b):
        """to be documented"""
        distance = station_a.location.distance(station_b.location)/1000
        return (distance/SHUTTLE_SPEED)*60

    @classmethod
    def can_reach(cls, station_a, station_b, current_time):
        """doc"""
        common_stations = cls.common_linked_stations(station_a, station_b)
        reachable_stations = []
        time_between = cls.time_between(station_a, station_b)
        for station in common_stations:
            next_arrival_a = station_a.next_arrival_to(station, current_time)
            next_arrival_b = station_b.next_arrival_to(station, current_time + time_between)
            if  next_arrival_a >= next_arrival_b:
                reachable_stations.append(station)
        return reachable_stations

    @classmethod
    def get_stations(cls):
        '''doc'''
        stations_data = requests.get('http://localhost:3000/stations/all').json()
        as_dictionary = {}
        as_list = []
        for key in stations_data:
            data = stations_data[key]
            station = cls(key, data['name'],
                          data['location']['latitude'],
                          data['location']['longitude'],
                          data['weight'])
            for stop_data in data['stops']:
                stop = Stop(stop_data['id'], stop_data['name'], station,
                            stop_data['location']['latitude'],
                            stop_data['location']['longitude'])
                station.stops.append(stop)
            as_list.append(station)
            as_dictionary[key] = station
        return as_list

    @classmethod
    def find_by_name(cls, name):
        for station_id in cls.all_stations:
            station = cls.all_stations[station_id]
            if station.name == name:
                return station
        return None

    def modes(self):
        modes_set = set()
        for line in self.lines:
            modes_set.add(line.mode)
        return modes_set


class Journey():
    '''doc'''
    def __init__(self, _id, station, when, direction, line, trip, delay):
        self._id = _id
        self.station = station
        self.when = dateparser.parse(when)
        self.direction = direction # station
        self.line = Line.find_by_name(line['name'])
        self.line_name = line['name']
        self.trip = trip
        self.delay = delay


class Line():
    '''doc'''
    all_lines = {}
    def __init__(self, _id, name, operator, mode, product, variants):
        self._id = _id
        type(self).all_lines[_id] = self
        self.name = name
        self.operator = operator
        self.mode = mode
        self.product = product
        self.variants = []
        self.stations_set = set()
        self.stops_set = set()
        for variant in variants:
            new_variant = []
            for stop_id in variant:
                stop = None
                try:
                    stop = Stop.all_stops[stop_id]
                    self.stops_set.add(stop)
                    self.stations_set.add(stop.station)
                    stop.station.lines.add(self)
                except:
                    stop = Station.all_stations[stop_id]
                    self.stations_set.add(stop)
                stop.lines.add(self)
                new_variant.append(stop)
            self.variants.append(new_variant)


    def station_from_direction_steps(self, origin, direction, steps=1):
        for variant in self.variants:
            index_origin = None
            index_direction = None
            index_result = None
            for i in range(len(variant)):
                if variant[i] == origin:
                    index_origin = i
                elif variant[i] == direction:
                    index_direction = i
                if index_direction and index_origin:
                    if index_direction > index_origin:
                        index_result = index_origin + steps
                    else:
                        index_result = index_origin - steps
                if index_result and index_result < len(variant):
                    return variant[index_result]
        return None

    @classmethod
    def get_lines(cls, return_dictionary=False):
        '''doc'''
        lines_data = requests.get('http://localhost:3000/lines?variants=true')
        as_dictionary = {}
        as_list = []
        for line_data in lines_data.text.split('\n'):
            if len(line_data) < 2:
                continue
            data = json.loads(line_data)
            line = cls(data['id'], data['name'], data['operator'], data['mode'],
                       data['product'], data['variants'])
            as_list.append(line)
            as_dictionary[data['id']] = line
        if return_dictionary:
            return as_dictionary
        return as_list


    def contains_stop_or_station(self, stop_or_station):
        return stop_or_station in self.stations_set

    def next_stations(self, station):
        result = []
        for variant in self.variants:
            for i in range(len(variant)):
                if variant[i].station == station:
                    if i > 0:
                        result.append(variant[i - 1])
                    if i + 1 < len(variant):
                        result.append(variant[i + 1])
                    continue
        return result


    def intersecting_lines(self, origin, dest):
        for variant in self.variants:
            try:
                origin_index = variant.index(origin)
                dest_index = variant.index(dest)
            except:
                continue
            if dest_index > origin_index:
                origin_index = origin_index + 1
            else:
                origin_index = origin_index - 1

            intersections = []
            for i in range(origin_index, dest_index):
                current_station = variant[i]
                intersections.append([current_station, current_station.lines.remove(self)])
            return intersections
        return None

    @classmethod
    def find_by_name(cls, name):
        name = name.split()
        if len(name)>1:
            name = name[1]
        else:
            name = name[0]
        for line_id in cls.all_lines:
            line = cls.all_lines[line_id]
            if line.name == name:
                return line
        return None
