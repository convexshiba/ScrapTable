from mongotable.mongo_dict import MongoDict, DB

mh = MongoDict()
test = DB.TEST

print([test, "doesnotexist"] in mh)

mh.put(test, "a", "value1")
mh.put(test, "a", "value2")
mh.put(test, "b", {"ad": 123})
mh.put(test, "list", [{"ad": 123}])
