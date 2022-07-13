import sys
from exif import Image
from geopy.geocoders import Nominatim
import os
import Location_personalization as loc
from tqdm import tqdm
from os import path
import subprocess

# test_path = "/Users/mikolajzawada/Documents/Photos_to_sort/Official_test"
# test_path = "/Users/mikolajzawada/Documents/Photos_to_sort/iPhone_2"
# test_path = "/Users/mikolajzawada/Documents/Photos_to_sort/Official_test_video"
test_path = "/Users/mikolajzawada/Documents/Photos_to_sort/DJI_Video_test"
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


def run_sort():
    years = set(())

    for filename in tqdm(os.listdir(test_path)):
        f = os.path.join(test_path, filename)
        if os.path.isfile(f):
            with open(f, 'rb') as src:
                if src.name.endswith(".jpeg") or src.name.endswith(".JPG"):
                    img = Image(src)
                    if img.has_exif:
                        tags = img.list_all()
                        file_date = img.datetime_original
                        year = get_year_from_date(file_date)

                        if "gps_latitude" in tags and "gps_longitude" in tags:

                            lat = decimal_coords(img.gps_latitude, img.gps_latitude_ref)
                            lon = decimal_coords(img.gps_longitude, img.gps_longitude_ref)

                            # (lat, lon, date, year, file_name, parent_path):
                            sort_with_lcoation_data(lat, lon, file_date, year, src.name)
                        else:
                            pass
                        # move to unknown folder
                        # print("no location data for ", src.name)
                    else:
                        pass
                elif src.name.endswith(".mov"):
                    exe = "exiftool"
                    process = subprocess.Popen(
                        [exe, f],
                        stdout=subprocess.PIPE,
                        stderr=subprocess.STDOUT
                    )
                    data_from_exiftoll = get_data_from_exiftool(process.stdout)
                    # lat, lon, file_date, year, file_name
                    sort_with_lcoation_data(
                        data_from_exiftoll[0],
                        data_from_exiftoll[1],
                        data_from_exiftoll[3],
                        data_from_exiftoll[2],
                        src.name
                    )
                elif src.name.endswith(".SRT"):
                    lat = None
                    lon = None
                    date = None
                    year = None
                    with open(f) as file_in:
                        for master_index, line in enumerate(file_in):
                            if 'latitude' in line:
                                data = line.split(" ")
                                for index, sub_data in enumerate(data):
                                    if 'latitude' in sub_data:
                                        lat = float(data[index+1][:-1])
                                    elif 'longitude' in sub_data:
                                        lon = float(data[index+1][:-1])
                                date = list(file_in)[master_index].split(" ")[0][:-1]
                                year = date.split("-")[0]
                                break

                    sort_with_lcoation_data(
                        lat,
                        lon,
                        date,
                        year,
                        src.name
                    )

                    sort_with_lcoation_data(
                        lat,
                        lon,
                        date,
                        year,
                        src.name.replace(".SRT", ".MP4")
                    )



def sort_with_lcoation_data(lat, lon, file_date, year, file_name):
    city_key = 'city'
    country_key = 'country_code'
    tourism_key = 'tourism'
    municipality_key = 'municipality'

    try:
        location = geolocator.reverse(str(lat) + "," + str(lon)).raw['address']
    except:
        # internet to slow or other error
        # simply
        return
    # years.add(year)

    has_country_info = country_key in location.keys()

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
        file_name,
        location,
        lat,
        lon,
        city=city,
        country=country,
        tourism=tourism,
        municipality=municipality
    )

def get_data_from_exiftool(data):
    lat = None
    lon = None
    year = None
    full_date = None
    for result in data:
        data_line = str(result.strip())[2:]
        data_line_components = data_line.split(":")
        tag_name = data_line_components[0].replace(" ", "")

        if tag_name == 'GPSLatitude' or tag_name == 'GPSLongitude':
            lat_data_components = data_line_components[1].split(" ")
            first = float(lat_data_components[1])
            second = float(lat_data_components[3].replace("\\", "").replace("'", ""))
            third = float(lat_data_components[4][:-1])
            direct = lat_data_components[5].replace("'", "")
            if tag_name == 'GPSLatitude':
                lat = decimal_coords((first, second, third), direct)
            else:
                lon = decimal_coords((first, second, third), direct)
        if tag_name == 'MediaCreateDate':
            year = data_line_components[1]
            month = data_line_components[2]
            sub_comp = data_line_components[3].split(" ")
            day = sub_comp[0]

            hour = sub_comp[1]
            minute = data_line_components[4]
            second = data_line_components[5].replace("'", "")

            full_date = year+":"+month+":"+day+" "+hour+":"+minute+":"+second

    return lat, lon, year, full_date

run_sort()
