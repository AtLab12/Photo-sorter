from exif import Image
from geopy.geocoders import Nominatim
import geopy.exc as geoexc
import os
import Location_personalization as loc
from tqdm import tqdm
from os import path
import subprocess
import pandas as pd
from time import sleep
from random import randint
from config import path_to_timeline_csv  # python file containing path to timeline file

input_path = str(input("Please provide path to folder you want to sort: "))

while not path.exists(input_path):
    print("\nPath does not exist, please try again.\n")
    input_path = input("Please provide path to folder you want to sort: ")

geolocator = Nominatim(user_agent="Your_choice")

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

    for filename in tqdm(os.listdir(input_path)):
        f = os.path.join(input_path, filename)
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
                            sort_with_location_data(lat, lon, file_date, year, src.name)
                        else:
                            if 'software' in tags:
                                software = img.software
                                # throw to lighroom folder that needs to be manually sorted
                                # I assume if they were edited they are important ;)
                                if 'Lightroom' in software:
                                    ligthroom_path = os.path.join(loc.test_master_path, "Lightroom")
                                    file_name = src.name.split("/")[-1]
                                    if not path.exists(ligthroom_path):
                                        os.mkdir(ligthroom_path, 0o777)
                                    os.replace(src.name, ligthroom_path + "/" + file_name)
                elif src.name.endswith(".mov") or src.name.endswith(".MP4"):
                    exe = "exiftool"
                    process = subprocess.Popen(
                        [exe, f],
                        stdout=subprocess.PIPE,
                        stderr=subprocess.STDOUT
                    )
                    data_from_exiftoll = get_data_from_exiftool(process.stdout)

                    sort_with_location_data(
                        data_from_exiftoll[0],
                        data_from_exiftoll[1],
                        data_from_exiftoll[3],
                        data_from_exiftoll[2],
                        src.name,
                        isVideo=True
                    )

                # sorting srt files created by DJI drones
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
                                        lat = float(data[index + 1][:-1])
                                    elif 'longitude' in sub_data:
                                        lon = float(data[index + 1][:-1])
                                date = list(file_in)[master_index].split(" ")[0][:-1]
                                year = date.split("-")[0]
                                break

                    sort_with_location_data(
                        lat,
                        lon,
                        date,
                        year,
                        src.name,
                        isVideo=True
                    )

                    sort_with_location_data(
                        lat,
                        lon,
                        date,
                        year,
                        src.name.replace(".SRT", ".MP4"),
                        isVideo=True
                    )

    answer = input("Do you want to try sorting photos without location data, based on those already sorted? (Y/N)")

    if answer in ["Y", "y", "yes", "a jakze"]:
        # sort based on timeline csv
        sort_based_on_timeline_file()


def sort_with_location_data(lat, lon, file_date, year, file_name, isVideo=False):
    city_key = 'city'
    country_key = 'country_code'
    tourism_key = 'tourism'
    municipality_key = 'municipality'
    neighbourhood_key = 'neighbourhood'

    try:
        location = geolocator.reverse(str(lat) + "," + str(lon)).raw['address']
    except geoexc.GeocoderTimedOut:
        sleep(randint(1 * 100, 200) / 100)
        location = geolocator.reverse(str(lat) + "," + str(lon)).raw['address']
    except Exception as e:
        # write to log file
        return

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

    if neighbourhood_key in location.keys():
        neighbourhood = location[neighbourhood_key]
    else:
        neighbourhood = None

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
        municipality=municipality,
        neighbourhood=neighbourhood,
        isVideo=isVideo
    )

def get_data_from_exiftool(data):
    lat = None
    lon = None
    year = None
    full_date = None
    make = None
    camera_model_name = None

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
            year = data_line_components[1].replace(" ", "")
            month = data_line_components[2]
            sub_comp = data_line_components[3].split(" ")
            day = sub_comp[0]

            hour = sub_comp[1]
            minute = data_line_components[4]
            second = data_line_components[5].replace("'", "")

            full_date = year + ":" + month + ":" + day + " " + hour + ":" + minute + ":" + second
        if tag_name == 'Make':
            make = data_line_components[1].split(" ")
        if tag_name == 'Camera Model Name':
            camera_model_name == data_line_components[1]

    return lat, lon, year, full_date, make, camera_model_name


def sort_based_on_timeline_file():
    print("Sorting based on timeline file ...")

    for filename in tqdm(os.listdir(input_path)):
        isVideo = False
        f = os.path.join(input_path, filename)
        file_date = None
        with open(f, 'rb') as src:
            if os.path.isfile(f):
                if src.name.endswith(".jpeg") or src.name.endswith(".JPG"):
                    img = Image(src)
                    if img.has_exif:
                        tags = img.list_all()
                        file_date = img.datetime_original
                elif src.name.endswith(".mov") or src.name.endswith(".MP4"):
                    exe = "exiftool"
                    process = subprocess.Popen(
                        [exe, f],
                        stdout=subprocess.PIPE,
                        stderr=subprocess.STDOUT
                    )
                    data_from_exiftoll = get_data_from_exiftool(process.stdout)
                    file_date = data_from_exiftoll[3]
                    isVideo = True
                elif src.name.endswith(".SRT"):
                    with open(f) as file_in:
                        file_date = list(file_in)[2].split(" ")[0]
                        isVideo = True

        correct_file_type = src.name.endswith(".jpeg") or src.name.endswith(".JPG") or src.name.endswith(".MP4")

        if file_date is not None and correct_file_type:
            # place file based on date
            date = str(file_date.split(" ")[0]).split(":")
            time = str(file_date.split(" ")[1]).split(":")
            if path.exists(path_to_timeline_csv):
                df = pd.read_csv(path_to_timeline_csv)
                df_file_date = df.loc[
                    (df['Day'] == int(date[2])) &
                    (df['Month'] == int(date[1])) &
                    (df['Year'] == int(date[0]))
                    ]

                if df_file_date.shape[0] > 0:
                    # there was media made the same day
                    assigned_coordinates = find_closest_media_same_day(df_file_date, date, time)
                    lat = assigned_coordinates[0]
                    lon = assigned_coordinates[1]

                    sort_with_location_data(
                        lat,
                        lon,
                        file_date,
                        date[0],
                        src.name,
                        isVideo
                    )


# returns lat and lon of the closest (time wise) media found
def find_closest_media_same_day(data_frame, date, time) -> (float, float):
    hour_P = int(time[0])
    minute_P = int(time[1])

    hours = data_frame['Hour'].tolist()
    it = map(lambda hour: int(hour), hours)
    hours = list(it)
    hour_found = min(hours, key=lambda x: abs(x - hour_P))

    dataFrame = data_frame.loc[data_frame['Hour'] == hour_found]

    minutes = dataFrame['Minute'].tolist()
    it = map(lambda minute: int(minute), minutes)
    minutes = list(it)
    minute_found = min(minutes, key=lambda x: abs(x - minute_P))

    df = dataFrame.loc[(dataFrame['Hour'] == hour_found) & (dataFrame['Minute'] == minute_found)]

    return df.iloc[0]['Latitude'], df.iloc[0]['Longitude']

run_sort()
