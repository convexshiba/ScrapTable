from pymongo import MongoClient

from wayback.spiders.ot_restaurants_spider import OTRestaurantsSpider

client = MongoClient()
db = client.testdb
db.res.create_index([('borough', 1)], unique=True)
db.res.update({"borough": "Manhattan"},{
    "address": {
        "street": "2 Avenue",
        "zipcode": "hahahah",
        "building": "1480",
        "coord": [-73.9557413, 40.7720266]
    },
    "borough": "Manhattan",
    "cuisine": "Italian",
    "grades": [
    ],
    "name": "Vella",
    "restaurant_id": "41704620"
}, upsert=True)

print(db.res.find({"borough": "Manhattan"}).count())
print(db.res.find({"borough": "Manhattan"})[0])

s = OTRestaurantsSpider()