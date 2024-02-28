from geopy.distance import geodesic
from datetime import datetime
import matplotlib.pyplot as plt
import numpy as np
import json

data_path = 'vehicle_data_evening.json'
timetable_path = 'przystanki.json'
time_format = '%Y-%m-%d %H:%M:%S'
max_lat = 52.5
min_lat = 51.9
max_lon = 21.5
min_lon = 20.4


#check if bus coordinates are resonable
def correct_data(coords):

    if coords is None:
        return False
    if abs(coords['Lon']) > 60:
        return False
    if abs(coords['Lat']) > 60:
        return False
    if abs(coords['Lon']) < 20:
        return False
    if abs(coords['Lat']) < 20:
        return False
    return True

#used for creating a heatmap to visualize data
def add_to_heatmap(map, lat, lon):
    a = int((lat - min_lat) // 0.03)
    b = int((lon - min_lon) // 0.045)

    if (int(a) < 21) & (int(b) < 21) & (int(a) >= 0) & (int(b) >= 0):
        map[int(a)][int(b)] += 1


def show_heatmap(heatmap, name):
    plt.figure()
    plt.imshow(heatmap, cmap='hot', interpolation='nearest', origin='lower')
    plt.colorbar()
    plt.title(name)
    plt.show(block=False)


#generate unique id for each bus
def hash_bus(line, brigade):
    return line+'*'+brigade


def analyze_speeding(vehicle_data, results):
    results['all'] += 1
    is_moving = False
    is_speeding = False
    prev_coord_time = None
    for coord_time in vehicle_data:
        if (prev_coord_time is not None) & correct_data(prev_coord_time) & correct_data(coord_time):
            try:
                time = datetime.strptime(coord_time['Time'], time_format)
                prev_time = datetime.strptime(prev_coord_time['Time'], time_format)
                distance = geodesic((prev_coord_time['Lat'], prev_coord_time['Lon']),
                                    (coord_time['Lat'], coord_time['Lon']))
                if prev_coord_time['Time'] == coord_time['Time']:
                    continue
                delta_time = time.hour - prev_time.hour + (time.minute - prev_time.minute) / 60 + (
                        time.second - prev_time.second) / 3600

                speed = distance / abs(delta_time)
                #check if the bus is moving
                if speed > 5:
                    is_moving = True
                    results['buses_pos'][0].append(coord_time['Lat'])
                    results['buses_pos'][1].append(coord_time['Lon'])
                    add_to_heatmap(results['all_heatmap'], coord_time["Lat"], coord_time["Lon"])
                #check if speed limit is exceded
                if speed > 50:
                    is_speeding = True
                    results['speeding_pos'][0].append(coord_time['Lat'])
                    results['speeding_pos'][1].append(coord_time['Lon'])
                    add_to_heatmap(results['speeding_heatmap'], coord_time["Lat"], coord_time['Lon'])
            except ValueError as e:
                pass
        prev_coord_time = coord_time
        if is_moving:
            results['moving'] += 1
        if is_speeding:
            results['speeding'] += 1


def show_speeding_results(results):
    print(
        f'all buses: {results["all"]}\nmoving buses {results["moving"]}\nspeeding buses{results["speeding"]}\n')
    plt.figure()
    plt.scatter(results['speeding_pos'][0], results['speeding_pos'][1])
    plt.title("Speeding buses")
    plt.show(block=False)
    plt.figure()
    plt.scatter(results['buses_pos'][0], results['buses_pos'][1])
    plt.title("All buses")
    plt.show(block=False)
    show_heatmap(results['speeding_heatmap'], 'speeding')
    show_heatmap(results['all_heatmap'], 'all')
    speeding_ratio = np.nan_to_num(np.divide(results['speeding_heatmap'], results['all_heatmap']))
    show_heatmap(speeding_ratio, 'percent of speeding buses')


def analyze_delays(vehicle_data, timetable, results):
    results['all'] += 1
    prev_coord_time = None
    next_stop_idx = None
    arrival_times = sorted(timetable)
    for coord_time in vehicle_data:
        time = datetime.strptime(coord_time['Time'], time_format)
        time_seconds = time.hour * 3600 + time.minute * 60 + time.second
        if prev_coord_time is None:
            next_stop_idx = None
            for arrival_time in arrival_times:
                if int(arrival_time) > time_seconds:
                    next_stop_idx = arrival_times.index(arrival_time)
                    break
        if next_stop_idx is None:
            return
        if prev_coord_time is None:
            prev_coord_time = coord_time
            continue
        prev_time = datetime.strptime(prev_coord_time['Time'], time_format)
        prev_time_seconds = prev_time.hour * 3600 + prev_time.minute * 60 + prev_time.second
        dist_from_stop = geodesic((timetable[arrival_times[next_stop_idx]][0],
                                         timetable[arrival_times[next_stop_idx]][1]),
                                        (coord_time['Lat'], coord_time['Lon']))
        dist_from_stop_prev = geodesic((timetable[arrival_times[next_stop_idx]][0],
                                        timetable[arrival_times[next_stop_idx]][1]),
                                       (prev_coord_time['Lat'], prev_coord_time['Lon']))
        #check if bus is moving away from bus stop
        if (dist_from_stop > dist_from_stop_prev) & (dist_from_stop > 0.2) & (
                dist_from_stop - dist_from_stop_prev > 0.05):

            try:
                delay = prev_time_seconds - int(arrival_times[next_stop_idx])
                #if bus is earlier than 2 minutes before planned time, assume the data is incorrect and don't count
                if delay > -120:
                    if (coord_time["Lines"]) in results['opoznienia_lini']:
                        results['opoznienia_lini'][coord_time['Lines']].append(delay)
                    else:
                        results['opoznienia_lini'][coord_time['Lines']] = [delay]
                    dist_from_stop_prev = dist_from_stop_prev.km

                    results['odl'] += int(dist_from_stop_prev)
                    results['czas'] += prev_time_seconds - int(arrival_times[next_stop_idx])
                    results['liczba_op'] += 1
                    next_stop_idx += 1
            except IndexError as e:
                break

            if (len(arrival_times) <= next_stop_idx):
                break
        prev_coord_time = coord_time


def show_delays_results(results):
    avg_delays = {}
    print(
        f'licbza: {results["liczba_op"]}, czas opoznien: {results["czas"]},'
        f' srednia: {results["czas"] / results["liczba_op"]}')
    for el in results['opoznienia_lini']:
        avg_delays[el] = np.mean(results['opoznienia_lini'][el])
    sorted_delays=sorted(avg_delays.items(), key=lambda item: item[1], reverse=True)
    top_delays = sorted_delays[:5]
    print("5 Lines with biggest average delays:")
    for el in top_delays:
        print(f'Line {el[0]}: avg. delay: {np.floor(el[1])}s')


with open(data_path, 'r') as file:
    data = json.load(file)

with open(timetable_path, 'r') as file:
    timetable = json.load(file)


speeding_data = {'all': 0, 'moving': 0, 'speeding': 0, 'buses_pos': ([], []), 'speeding_pos': ([], []),
                 'all_heatmap': np.ones((21, 21)), 'speeding_heatmap': np.zeros((21, 21))}
delays_data = {'all': 0, 'odl': 0, 'czas': 0, 'liczba_op': 0, 'opoznienia_lini': {}}
for vehicle_data in data:
    analyze_speeding(data[vehicle_data], speeding_data)
    bus_id = hash_bus(data[vehicle_data][0]['Lines'], data[vehicle_data][0]['Brigade'])
    if bus_id in timetable:
        bus_timetable = timetable[bus_id]
        analyze_delays(data[vehicle_data], bus_timetable, delays_data)

show_speeding_results(speeding_data)
show_delays_results(delays_data)
plt.waitforbuttonpress()

