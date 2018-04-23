#!/usr/bin/env python3
import folium
import folium.plugins
import os
from models.station import Station, Stop
from models.line import Line

m = folium.Map(location=[52, 13], tiles='stamentoner', max_zoom=18, zoom_start=4)
marker_cluster = folium.plugins.MarkerCluster().add_to(m)

stations = Station.get_stations()
lines = Line.get_lines()

for station in stations:
    if 'train' in station.modes():
        folium.Marker(station.location, popup=station.name).add_to(marker_cluster)

is_ubahn = False
colors = ['red', 'green', 'yellow', 'black', 'pink', 'brown', 'red', 'green', 'yellow', 'black', 'pink', 'brown', 'red', 'green', 'yellow', 'black', 'pink', 'brown', 'red', 'green', 'yellow', 'black', 'pink', 'brown']
for line in lines:
    # if not line.mode == 'train':
    if line.name != 'U8':
        continue
    color = 'green'
    if line.product == 'subway':
        color = 'blue'
    multipolyline = []
    i = 0
    for variant in line.variants:
        polyline = [station.location for station in variant]
        multipolyline.append(polyline)
        folium.features.PolyLine(polyline, color=colors[i]).add_to(m)
        i += 1


m.save(os.path.join('results', 'stopsandlines.html'))
