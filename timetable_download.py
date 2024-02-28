import urllib.request
import urllib.error
import json
from datetime import datetime


time_format = '%H:%M:%S'


def bytes_to_json(data_bytes):
    data_str = data_bytes.decode('utf-8')
    data_dict = json.loads(data_str)
    results = data_dict["result"]
    return results


def load_data_from_url(url):
    try:
        with urllib.request.urlopen(url) as fileobj:
            data = fileobj.read()

    except Exception as e:
        print(e)
        print('dupa')
    return bytes_to_json(data)


def load_data_from_file(file_path):
    with open(file_path, "r") as json_file:
        results = json.load(json_file)
    return results


def time_to_int(time):
    try:
        tmp = datetime.strptime(time, time_format)
    except ValueError as e:
        return 0
    return tmp.hour*3600+tmp.minute*60+tmp.second


def hash_bus(line, brigade):
    return line+'*'+brigade


apikey = '5f006bb6-2ce2-44ab-b53f-63f67c58a022'
url = ("https://api.um.warszawa.pl/api/action/dbstore_get/?id=ab75c33d-3a26-4342-b36a-6e5fef0a3ac3&line=167&apikey="
       + apikey)
url_rozklad = ("https://api.um.warszawa.pl/api/action/dbtimetable_get?id=e923fa0e-d96c-43f9-ae6e-60518c9f3238"
               + "&busstopId=4182&busstopNr=02&line=715&apikey=") + apikey

file_path = 'przystanki.json'

results = load_data_from_url(url)

line_brigade_data = {}
data = []
iteration = 0
for el in results:
    iteration += 1
    print(f'iteration {iteration} of {len(results)}')
    data.append({})
    for el2 in el['values']:
        data[-1][el2['key']] = el2['value']
    url_linie = (f'https://api.um.warszawa.pl/api/action/dbtimetable_get?id=88cd555f-6f31-43ca-9de4-66c479ad5942'
                 + f'&busstopId={data[-1]["zespol"]}&busstopNr={data[-1]["slupek"]}&apikey={apikey}')
    linie = load_data_from_url(url_linie)
    data[-1]['linie'] = []
    for el in linie:
        line = el['values'][0]['value']
        data[-1]['linie'].append(line)
        coords = [data[-1]['szer_geo'],data[-1]['dlug_geo']]
        url_rozklad = (f'https://api.um.warszawa.pl/api/action/dbtimetable_get?id=e923fa0e-d96c-43f9-ae6e-60518c9f3238'
                       + f'&busstopId={data[-1]["zespol"]}&busstopNr={data[-1]["slupek"]}&line={line}&apikey={apikey}')
        rozklad = load_data_from_url(url_rozklad)
        for roz in rozklad:
            brigade = roz['values'][2]['value']
            time = roz['values'][5]['value']
            if hash_bus(line, brigade) in line_brigade_data:
                line_brigade_data[hash_bus(line, brigade)][time_to_int(time)] = coords
            else:
                line_brigade_data[hash_bus(line, brigade)] = {}

    if iteration % 100 == 0:
        with open(file_path, "w") as json_file:
            json.dump(line_brigade_data, json_file)
with open(file_path, "w") as json_file:
    json.dump(line_brigade_data, json_file)


