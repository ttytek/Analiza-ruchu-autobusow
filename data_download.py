import urllib.request
import urllib.error
import json
from time import sleep

def bytes_to_json(data_bytes):
    data_str = data_bytes.decode('utf-8')
    data_dict = json.loads(data_str)
    results = data_dict["result"]
    return results

apikey = '5f006bb6-2ce2-44ab-b53f-63f67c58a022'
busestrams_id = 'f2e5503e-927d-4ad3-9500-4ab9e55deb59'
url = f'https://api.um.warszawa.pl/api/action/busestrams_get/?resource_id={busestrams_id}&apikey={apikey}&type=1'
error_message = 'Błędna metoda lub parametry wywołania'

vehicle_data = {}

iterations = 60
sleep_on_error = 2
sleep_after_loop = 60

file_path = "vehicle_data_new.json"

for i in range(iterations) :
    print(f'iteration {i} of {iterations}')

    try:
        with urllib.request.urlopen(url) as fileobj:
            data_bytes = fileobj.read()
    except urllib.error.HTTPError as e:
        pass

    results = bytes_to_json(data_bytes)
    slept_time = 0
    while results == error_message:
        print('error')
        try:
            with urllib.request.urlopen(url) as fileobj:
                data_bytes = fileobj.read()
        except urllib.error.HTTPError as e:
            pass
        results = bytes_to_json(data_bytes)
        sleep(sleep_on_error)
        slept_time += sleep_on_error
    print('ok')
    for result in results:
        vehicle_number = result["VehicleNumber"]
        if vehicle_number in vehicle_data:
            last_data = vehicle_data[vehicle_number][-1]
            if result != last_data:
                vehicle_data[vehicle_number].append(result)
        else:
            vehicle_data[vehicle_number] = [result]
    if sleep_after_loop-slept_time>0 :
        sleep(sleep_after_loop-slept_time)
    with open(file_path, "w") as json_file:
        json.dump(vehicle_data, json_file)



with open(file_path, "w") as json_file:
    json.dump(vehicle_data, json_file)

print("saved to:",file_path)


