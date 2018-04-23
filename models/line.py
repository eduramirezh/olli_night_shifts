#!/usr/bin/env python3
'''doc'''

import json
import requests
from models.station import Stop, Station

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


    def intersecting_lines(self):
        all_lines = type(self).all_lines
        intersecting_lines = {}
        for line_id in all_lines:
            if line_id == self._id:
                continue
            line = all_lines[line_id]
            common_stations = line.stations_set.intersection(self.stations_set)
            if len(common_stations) > 0:
                intersecting_lines[line._id] = common_stations
        return intersecting_lines



