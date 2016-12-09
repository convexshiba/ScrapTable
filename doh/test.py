with open("1_Only_Useful_Col_DOHMH_New_York_City_Restaurant_Inspection_Results.csv", mode='r',
          encoding='utf-8') as originFile:
    header = True
    dic = {}
    for row in originFile:
        if header:
            header = False
            continue
        camis = row.split(",")[0]
        dic[camis] = 1

    print(len(dic))
