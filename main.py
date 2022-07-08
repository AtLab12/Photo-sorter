from exif import Image
from geopy.geocoders import Nominatim
import os
import Location_personalization as loc
from tqdm import tqdm

test_path = "/Users/mikolajzawada/Documents/Photos_to_sort/Official_test"
# unsorted_folder = input("Please provide path to folder you want to sort: ")
geolocator = Nominatim(user_agent="AtLabPhotosorter")

final_format = {}
paths = []


def decimal_coords(coords, ref):
    decimal_degrees = coords[0] + coords[1] / 60 + coords[2] / 3600
    if ref == 'S' or ref == 'W':
        decimal_degrees = -decimal_degrees
    return decimal_degrees


def get_year_from_date(date) -> str:
    date_elements = date.split(" ")
    year = date_elements[0].split(":")[0]
    return year


for filename in tqdm(os.listdir(test_path)):
    f = os.path.join(test_path, filename)
    if os.path.isfile(f):
        with open(f, 'rb') as src:
            if src.name.endswith(".jpeg") or src.name.endswith(".JPG"):
                img = Image(src)
                if img.has_exif:
                    tags = img.list_all()
                    if "gps_latitude" in tags and "gps_longitude" in tags:

                        city_key = 'city'
                        country_key = 'country_code'
                        tourism_key = 'tourism'
                        municipality_key = 'municipality'

                        lat = decimal_coords(img.gps_latitude, img.gps_latitude_ref)
                        lon = decimal_coords(img.gps_longitude, img.gps_longitude_ref)
                        location = geolocator.reverse(str(lat) + "," + str(lon)).raw['address']
                        year = get_year_from_date(img.datetime_original)
                        has_country_info = country_key in location.keys()
                        file_name = src.name.split("/")[-1]

                        if city_key in location.keys() and has_country_info:
                            city = location[city_key]
                            country = location[country_key]
                            #print(year, " ", city, " ", country)
                            loc.alocate_photo(year, location, city=city, country=country, originPath=src.name)
                        else:
                            if tourism_key in location.keys() and has_country_info:
                                tourism = location[tourism_key]
                                country = location[country_key]
                                #print(year, " ", tourism, " ", country)
                                loc.alocate_photo(year, location, country=country, tourism=tourism, originPath=src.name)
                            else:
                                if municipality_key in location.keys() and has_country_info:
                                    municipality = location[municipality_key]
                                    country = location[country_key]
                                    #print(year, " ", municipality, " ", country)
                                    loc.alocate_photo(year, location, country=country, municipality=municipality, originPath=src.name)
                                else:
                                    # here handle no location data
                                    #print(year, " ", location)
                                    pass

                    else:
                        pass
                        # move to unknown folder
                        # print("no location data for ", src.name)
                else:
                    pass
                    # print("no exif data")

