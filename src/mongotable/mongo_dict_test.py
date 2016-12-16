from mongotable.mongo_dict import MongoDict, COLLECTION

mh = MongoDict()
test = COLLECTION.TEST

print([test, "doesnotexist"] in mh)

mh.put(test, "a", "value1")
mh.put(test, "a", "value2")
mh.put(test, "b", {"ad": 123})
mh.put(test, "list", [{"ad": 123}])
