from pymongo import MongoClient

client = MongoClient()
db = client.testdb
db.res.create_index([('borough', 1)], unique=True)
# db.res.update({"borough": "Manhattan"},{
#     "address": {
#         "street": "2 Avenue",
#         "zipcode": "hahahah",
#         "building": "1480",
#         "coord": [-73.9557413, 40.7720266]
#     },
#     "borough": "Manhattan",
#     "cuisine": "Italian",
#     "grades": [
#         {
#             "date": datetime.strptime("2014-10-01", "%Y-%m-%d"),
#             "grade": "A",
#             "score": 11
#         },
#         {
#             "date": datetime.strptime("2014-01-16", "%Y-%m-%d"),
#             "grade": "B",
#             "score": 17
#         }
#     ],
#     "name": "Vella",
#     "restaurant_id": "41704620"
# }, upsert=True)

print(db.res.find({"borough": "Manhattan"}).count())
