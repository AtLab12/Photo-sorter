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
                        try:
                            location = geolocator.reverse(str(lat) + "," + str(lon)).raw['address']
                        except:
                            # internet to slow or other error
                            pass
                        file_date = img.datetime_original
                        year = get_year_from_date(file_date)
                        has_country_info = country_key in location.keys()
                        file_name = src.name.split("/")[-1]

                        if has_country_info:
                            country = location[country_key]
                        else:
                            country = None

                        if city_key in location.keys():
                            city = location[city_key]
                        else:
                            city = None

                        if tourism_key in location.keys():
                            tourism = location[tourism_key]
                        else:
                            tourism = None

                        if municipality_key in location.keys():
                            municipality = location[municipality_key]
                        else:
                            municipality = None

                        loc.alocate_photo(
                            file_date,
                            year,
                            src.name,
                            location,
                            lat,
                            lon,
                            city=city,
                            country=country,
                            tourism=tourism,
                            municipality=municipality
                        )

                    else:
                        pass
                        # move to unknown folder
                        # print("no location data for ", src.name)
                else:
                    pass
                    # print("no exif data")

