import inspect
import json
import os

from util.googlemap import GoogleMap


class DummyClass: pass


def generate_address(row):
    elements = row.strip().split(",")
    return elements[3] + " " + elements[4] + "," + elements[2] + "," + elements[5]


def load_camis_address():
    with open(OUTPUT_FILE) as output_file:
        return json.load(output_file)


OUTPUT_FILE = os.path.join(os.path.dirname(os.path.abspath(inspect.getsourcefile(DummyClass))), '3_address_dict.json')

if __name__ == "__main__":

    if os.path.isfile(OUTPUT_FILE):
        res = input(
            "> DICT ALREADY EXIST! DO YOU WISH TO OVERRIDE! THIS WOULD QUERY ~25000 GOOGLE MAP API! \n> type OVERRIDE/N:  ")
        if res != "OVERRIDE":
            print("> Aborted")
            exit(0)

    gm = GoogleMap()

    progress = 0

    address_data = {}

    with open("2_with_yearCol_Only_Useful_Col_DOHMH_New_York_City_Restaurant_Inspection_Results.csv", mode='r',
              encoding='utf-8') as originFile:
        header = True
        for row in originFile:
            if header:
                header = False
                continue
            address = generate_address(row)
            camis = row.strip().split(",")[0]

            if camis not in address_data:
                address_data[camis] = gm.get_client().geocode(address)

            # print(address)

            data = gm.get_client().geocode(address)
            # parsed = json.loads(data)
            # print(json.dump(parsed, indent=4, sort_keys=True))

            progress += 1
            if progress % 20 == 0:
                print("> Processed " + str(progress) + " items.")

                # if progress == 50:
                #     break

    with open("3_address_dict.json", "w") as f:
        json.dump(address_data, f)
