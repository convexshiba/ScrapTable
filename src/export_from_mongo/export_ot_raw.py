import tablib as tablib

from mongotable.mongo_dict import MongoDict

mongo = MongoDict()

data = tablib.Dataset()
data.headers = ["name", "address", 'price', 'neighborhood', 'county', 'type', 'reviews', 'stars', 'lng', 'lat']

for entry in mongo.client["ot_db_try7_fulll_stepped"]['20101206120344_1833'].find({}):
    entry_dict = entry['value']
    if not entry_dict['extract_success']:
        continue
    row = []
    for key in data.headers:
        try:
            if key == 'lat' or key == 'lng':
                if len(entry_dict['geocode']) != 0:
                    row.append(entry_dict['geocode']['geometry']['location'][key])
                else:
                    row.append("not found")
                continue
        except:
            print("_________________")
            print(entry_dict)
            exit(1)

        # if key == 'lat' or key == 'lng':
        #     if entry_dict['geocode'] != 0:
        #         row.append(entry_dict['geocode']['geometry']['location'][key])
        #     else:
        #         row.append("not found")
        #     continue

        try:
            if type(entry_dict[key]) is str:
                entry_dict[key] = entry_dict[key].encode('ascii', errors="ignore").decode()
        except KeyError:
            entry_dict[key] = 'not found'
        row.append(entry_dict[key])
    data.append(row)
    print(row)

print(data.csv)
with open("ot_201012_raw.csv", "w") as file:
    file.write(data.csv)
