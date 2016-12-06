
## File explanation
### 0_DOHMH_New_York_City_Restaurant_Inspection_Results.csv
Original data.

### 1_Only_Useful_Col_DOHMH_New_York_City_Restaurant_Inspection_Results.csv
Extracted only `CAMIS, DBA, BORO, BUILDING, STREET, ZIPCODE, INSPECTION DATE` columns.

### 2_with_yearCol_Only_Useful_Col_DOHMH_New_York_City_Restaurant_Inspection_Results.csv
* Data `1_Only_Useful_Col` with an addition year column indicating the year of the inspection.
* `CAMIS, DBA, BORO, BUILDING, STREET, ZIPCODE, INSPECTION DATE, YEAR`

### 3_address_dict.json
* A serialized python diction file contains all Google Maps json response for all DOH camis DATA.
* It can be used by `address_dict = load_camis_address()`. See `3_address_dict_example.py` for example.