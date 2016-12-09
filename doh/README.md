
## File explanation
### 0_DOHMH_New_York_City_Restaurant_Inspection_Results.csv
Original data. _too large, omited_

### 1_Only_Useful_Col_DOHMH_New_York_City_Restaurant_Inspection_Results.csv
Extracted only `CAMIS, DBA, BORO, BUILDING, STREET, ZIPCODE, INSPECTION DATE` columns.

### 2_with_yearCol_Only_Useful_Col_DOHMH_New_York_City_Restaurant_Inspection_Results.csv
* Data `1_Only_Useful_Col` with an addition year column indicating the year of the inspection.
* `CAMIS, DBA, BORO, BUILDING, STREET, ZIPCODE, INSPECTION DATE, YEAR`

### ~~3_address_dict.json~~
(use json to store geocode info is very unstable, have switched to mongoDB since it's more json-friendly than SQL database)
(Mongo db file is too large to store in github so it's excluded from uploading to github)