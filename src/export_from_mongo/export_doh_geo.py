import tablib as tablib

from mongotable.mongo_dict import MongoDict

mongo = MongoDict()

data = tablib.Dataset()
data.headers = ["camis", "place_id", 'formatted_address', 'lat', 'lng', 'county']

for entry in mongo.client["db"]['doh_geo'].find({}):
    if len(entry['value']) >= 1:
        entry_dict = entry['value'][0]
    else:
        continue

    row = []

    row.append(entry["key"])
    row.append(entry_dict['place_id'])
    row.append(entry_dict['formatted_address'])
    row.append(entry_dict['geometry']['location']['lat'])
    row.append(entry_dict['geometry']['location']['lng'])

    for entry in entry_dict['address_components']:
            if 'administrative_area_level_2' in entry['types']:
                row.append(entry['long_name'])

    if len(row) == 5:
        row.append("county not found")

    # for key in data.headers:
    #     if type(entry_dict[key]) is str:
    #         entry_dict[key] = entry_dict[key].encode('ascii', errors="ignore").decode()
    #     row.append(entry_dict[key])
    print(row)
    data.append(row)

print(data.csv)
with open("doh_geo.csv", "w") as file:
    file.write(data.csv)
