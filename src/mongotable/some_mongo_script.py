from queue import PriorityQueue

from mongotable.mongo_dict import MongoDict


def get_count():
    map = {}

    for collection in mongo.client['ot_db_try7_fulll_stepped_matched'].collection_names():
        size = mongo.client['ot_db_try7_fulll_stepped_matched'][collection].find({}).count()
        print(collection + ": " + str(size))
        month = collection[:6]
        if month in map:
            map[month] = map[month] if int(map[month][0]) > size else [str(size), collection[-4:], collection]
        else:
            map[month] = [str(size), collection[-4:], collection]

    pq = PriorityQueue()

    for key in map:
        pq.put((key, map[key]))

    for i in range(len(map)):
        (key, value) = pq.get()
        print(key + "," + ",".join(map[key]))


def iterate():
    for entry in mongo.client['ot_db_try7_fulll_stepped']['20091130142052_1414'].find({}):
        print(entry['key'])


mongo = MongoDict()
# mongo.client['db']['ot_catalog'].delete_many({'key': 20110625170217})
get_count()