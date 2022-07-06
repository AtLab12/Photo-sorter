from exif import Image
from geopy.geocoders import Nominatim
import os

test_path = "/Users/mikolajzawada/Documents/Photos_to_sort/Basia_zdj_test"
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


for filename in os.listdir(test_path):
    f = os.path.join(test_path, filename)
    # checking if it is a file
    if os.path.isfile(f):
        with open(f, 'rb') as src:
            if src.name.endswith(".jpeg") or src.name.endswith(".JPG"):
                img = Image(src)
                if img.has_exif:
                    tags = img.list_all()
                    if "gps_latitude" in tags and "gps_longitude" in tags:
                        lat = decimal_coords(img.gps_latitude, img.gps_latitude_ref)
                        lon = decimal_coords(img.gps_longitude, img.gps_longitude_ref)
                        location = geolocator.reverse(str(lat) + "," + str(lon)).raw['address']
                        year = get_year_from_date(img.datetime_original)
                        if 'city' in location.keys():
                            city = location['city']
                            print(year, " ", city)
                        else:
                            print(year, " " , location)

                    else:
                        print("no location data for ", src.name)
                else:
                    print("no exif data")

