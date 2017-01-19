from geo.googlemap import GoogleMap

gm = GoogleMap()

client = gm.get_client()

print(client.geocode("Brasserie Ruhlmann, 45 Rockefeller Plaza, New York, NY"))
print(client.place("ChIJd0GZTPlYwokRwXU9VndMnbg"))