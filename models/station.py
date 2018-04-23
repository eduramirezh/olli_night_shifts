import requests
SHUTTLE_SPEED = 30 #km/hr

class Stop():
    '''doc'''
    all_stops = {}
    def __init__(self, _id, name, station, lat, lon):
        self._id = _id
        self.name = name
        self.station = station
        self.location = [lat, lon]
        self.lines = set()
        type(self).all_stops[_id] = self


class Station():
    '''doc'''
    all_stations = {}
    def __init__(self, _id, name, lat, lon, weight):
        self._id = _id
        self.name = name
        self.location = [lat, lon]
        self.weight = float(weight)
        self.schedules = []
        self.linked_stations = []
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

    def next_departure(self, current_time):
        """tbd"""
        for schedule in sorted(self.schedules):
            if schedule >= current_time:
                return schedule

    def next_arrival_to(self, station_id, current_time):
        """tbd"""
        pass

    @classmethod
    def common_linked_stations(cls, station_a, station_b):
        """to be documented"""
        return set(station_a.linked_stations).intersection(set(station_b.linked_stations))

    @classmethod
    def time_between(cls, station_a, station_b):
        """to be documented"""
        distance = station_a.location - station_b.location # shapely distance something
        return distance/SHUTTLE_SPEED

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

    def modes(self):
        modes_set = set()
        for line in self.lines:
            modes_set.add(line.mode)
        return modes_set
