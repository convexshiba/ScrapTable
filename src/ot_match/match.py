from queue import PriorityQueue

import Levenshtein

from geo.googlemap import Tacheometer
from mongotable.mongo_dict import MongoDict, to_dict


def similar(a, b):
    a = a.lower()
    b = b.lower()

    if len(a) == 0 or len(b) == 0:
        return 1
    # return 1 - SequenceMatcher(None, a, b).ratio()
    if a in b or b in a:
        return 0

    return 1 - Levenshtein.ratio(a, b)

def init_doh() -> dict:
    result = {}
    for entry in client['db']['doh_geo'].find({}):
        if len(entry['value']) == 1:
            result[entry['key']] = get_loc(entry['value'][0])
    return result


def get_loc(value: dict) -> tuple:
    return value['geometry']["location"]["lat"], value['geometry']["location"]["lng"]


def find_match(value: dict, collection: str, ot_key: str):

    if value['is_nyc'] != "True":
        return
    tacheo = Tacheometer()

    pq = PriorityQueue(maxsize=0)

    restaurant_loc_dict = value['geocode']['geometry']["location"]
    restaurant_loc = (restaurant_loc_dict["lat"], restaurant_loc_dict["lng"])

    # smallest = None
    # smallest_dist = None

    for key in doh_dict:
        dist = tacheo.distance(restaurant_loc, doh_dict[key])
        pq.put((dist, key))

        # if smallest_dist is None or dist < smallest_dist:
        #     smallest_dist = dist
        #     smallest = key

    # print(smallest_dist)
    # print(client['db']['doh_raw'].find({'key': smallest})[0]['value'].strip())
    # print(value['name'])
    # print(value['geocode']['formatted_address'])
    # print("-----------")
    print("******************")
    print(value['name'])
    print(value['geocode']['formatted_address'])

    pq2 = PriorityQueue(maxsize=0)

    for i in range(60):
        (dist, key) = pq.get()
        # print(client['db']['doh_raw'].find({'key': key})[0]['value'].strip().split(",")[1].lower())
        # print(similar(value['name'].lower(), client['db']['doh_raw'].find({'key': key})[0]['value'].strip().split(",")[1].lower()))
        pq2.put((similar(value['name'], client['db']['doh_raw'].find({'key': key})[0]['value'].strip().split(",")[1]), (dist, key)))
        # pq2.put((0, (dist, key)))

    # for i in range(10):
    #     (similar_score, (dist, key)) = pq2.get()
    #     print(client['db']['doh_raw'].find({'key': key})[0]['value'].strip())
    #     print(client['db']['doh_geo'].find({'key': key})[0]['value'][0]['formatted_address'])
    #     print(dist)
    #     print(similar_score)
    (similar_score, (dist, key)) = pq2.get()
    value["name_similarity"] = similar_score
    value["match_camis"] = key
    value["match_distance"] = dist
    value["match_name"] = client['db']['doh_raw'].find({'key': key})[0]['value'].strip().split(",")[1].lower()

    save_result(collection, ot_key, value)


def save_result(c, key, value):
    output_db[c].update({'key': key}, to_dict(key, value), upsert=True)


client = MongoDict().client

doh_dict = init_doh()

print(len(doh_dict))

db_name = "ot_db_try7_fulll_stepped"

db = client[db_name]
output_db = client[db_name + "_matched"]

for c in db.collection_names():

    if c != "20101206120344_1833":
        continue

    print(c)
    for entry in db[c].find({}):
        if 'geocode' in entry['value'] and len(entry['value']['geocode']) != 0:
            find_match(entry["value"], c, entry['key'])


