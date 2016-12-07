from db_hashtable.mongo_dict import MongoDict, DB

mh = MongoDict()
doh = DB.DOH
ot = DB.OT

print([doh, "doesnotexist"] in mh)

mh.put(doh, "a", "value1")
mh.put(doh, "a", "value2")
mh.put(doh, "b", {"ad": 123})
mh.put(doh, "list", [{"ad": 123}])
