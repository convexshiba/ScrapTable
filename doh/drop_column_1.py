import pyexcel

sheet = pyexcel.get_sheet(file_name="0_DOHMH_New_York_City_Restaurant_Inspection_Results.csv", name_columns_by_row=0)
sheet.column.select([0, 1, 2, 3, 4, 5, 8])
sheet.save_as("1_Only_Useful_Col_DOHMH_New_York_City_Restaurant_Inspection_Results.csv")
