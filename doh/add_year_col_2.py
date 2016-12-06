from datetime import datetime


def get_year(date):
    return str(datetime.strptime(date, '%m/%d/%Y').year)


with open("1_Only_Useful_Col_DOHMH_New_York_City_Restaurant_Inspection_Results.csv", mode='r',
          encoding='utf-8') as originFile:
    with open("2_with_yearCol_Only_Useful_Col_DOHMH_New_York_City_Restaurant_Inspection_Results.csv", mode='w',
              encoding='utf-8') as output:
        header = True
        for row in originFile:
            if header:
                output.write(row.strip() + ",YEAR\n")
                header = False
                continue
            stripped = row.strip()
            date = stripped[-10:]
            output.write(row.strip() + "," + get_year(date) + "\n")
