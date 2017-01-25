import tablib as tablib

from mongotable.mongo_dict import MongoDict

mongo = MongoDict()

data = tablib.Dataset()
data.headers = ["name", "address", 'price', 'neighborhood', 'county', 'type', 'reviews', 'stars', 'match_camis', 'match_distance', 'match_name']

for entry in mongo.client["ot_db_try7_fulll_stepped_matched"]['20101206120344_1833'].find({}):
    entry_dict = entry['value']
    row = []
    for key in data.headers:
        if type(entry_dict[key]) is str:
            entry_dict[key] = entry_dict[key].encode('ascii', errors="ignore").decode()
        row.append(entry_dict[key])
    data.append(row)

print(data.csv)
with open("ot_201012_raw.csv", "w") as file:
    file.write(data.csv)
