import inspect
import json
import os
from concurrent import futures

from mongotable.mongo_dict import MongoDict, DB
from util.googlemap import GoogleMap
from util.tool import AtomicCounter


class DummyClass: pass


def generate_address(row):
    elements = row.strip().split(",")
    return elements[3] + " " + elements[4] + "," + elements[2] + "," + elements[5]


def load_camis_address():
    with open(OUTPUT_FILE) as output_file:
        return json.load(output_file)


def store_address_to_db(camis, address):
    total = total_counter.increment()
    counter1 = 0
    counter2 = 0
    if [DB.DOH, camis] not in mongo_map:
        mongo_map.put(DB.DOH, camis, gm.get_client().geocode(address))
        counter1 = query_counter.increment()
    else:
        counter2 = skipped_counter.increment()
    if total % 10 == 0:
        print("> Queried: " + str(counter1) + " items." + " Skipped: " + str(counter2) + " items.")


OUTPUT_FILE = os.path.join(os.path.dirname(os.path.abspath(inspect.getsourcefile(DummyClass))), '3_address_dict.json')

if __name__ == "__main__":

    gm = GoogleMap()

    progress = 0
    query_counter = AtomicCounter()
    skipped_counter = AtomicCounter()
    total_counter = AtomicCounter()

    mongo_map = MongoDict()

    with open("2_with_yearCol_Only_Useful_Col_DOHMH_New_York_City_Restaurant_Inspection_Results.csv", mode='r',
              encoding='utf-8') as originFile:
        with futures.ThreadPoolExecutor(max_workers=None) as executor:
            header = True
            for row in originFile:
                if header:
                    header = False
                    continue
                address = generate_address(row)
                camis = row.strip().split(",")[0]

                executor.submit(store_address_to_db, camis, address)

                # print(address)

                # data = gm.get_client().geocode(address)
                # parsed = json.loads(data)
                # print(json.dump(parsed, indent=4, sort_keys=True))

                # progress += 1
                #
                # if progress % 20 == 0:
                #     print("> Processed " + str(progress) + " items.")

                # if progress == 400:
                #     break

