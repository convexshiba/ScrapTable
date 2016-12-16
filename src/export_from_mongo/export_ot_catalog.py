import tablib as tablib

from mongotable.mongo_dict import MongoDict, COLLECTION

mongo = MongoDict()

data = tablib.Dataset()
data.headers = ["version_datetime", "version_datetime_string", 'entry_number', 'url']

for entry in mongo.get_collection_iterator(COLLECTION.OT_CATALOG):
    entry_dict = entry['value']
    row = []
    for key in data.headers:
        row.append(entry_dict[key])
    data.append(row)

print(data.csv)
with open("ot_catalog.csv", "w") as file:
    file.write(data.csv)
