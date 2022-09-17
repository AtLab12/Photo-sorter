from IPython.core.display_functions import display
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
from config import path_to_timeline_csv  # python file containing path to timeline file
import json
import multiprocessing as mp

auto_zones = {}
auto_zones_sorted_keys = None
from_zone = 0
geolocator = Nominatim(user_agent="AtLabPhotosorter")

zone_stage = True


def decimal_coords(coords, ref):
    decimal_degrees = coords[0] + coords[1] / 60 + coords[2] / 3600
    if ref == 'S' or ref == 'W':
        decimal_degrees = -decimal_degrees
    return decimal_degrees


def get_year_from_date(date) -> str:
    date_elements = date.split(" ")
    year = date_elements[0].split(":")[0]
    return year

def sort_based_on_timeline_file():
    # change this from making a network call with lat and lon to automatically moving to
    # folder based on location name and year
    print("Sorting based on timeline file ...")

    for filename in tqdm(os.listdir(input_path)):
        try:
            is_video = False
            is_screenshot = False
            has_lens_id = False

            f = os.path.join(input_path, filename)
            file_date = None
            with open(f, 'rb') as src:

                isPhoto = src.name.endswith(".jpeg") \
                          or src.name.endswith(".JPG") \
                          or src.name.endswith(".JPEG") \
                          or src.name.endswith(".jpg")

                isVideo_or_png = src.name.endswith(".mov") \
                                 or src.name.endswith(".MP4") \
                                 or src.name.endswith(".MOV") \
                                 or src.name.endswith(".mp4") \
                                 or src.name.endswith(".png") \
                                 or src.name.endswith(".PNG")

                hidden_bullshit_comp = filename.split("-")

                if hidden_bullshit_comp[0] != ".filtered" and hidden_bullshit_comp[0] != ".segmented":
                    if os.path.isfile(f):
                        if isPhoto:
                            img = Image(src)
                            if img.has_exif:
                                tags = img.list_all()
                                if 'user_comment' in tags:
                                    if img.user_comment == "Screenshot":
                                        is_screenshot = True
                                if "datetime_original" in tags:
                                    file_date = img.datetime_original
                                if "lens_model" in tags:
                                    has_lens_id = True
                        elif isVideo_or_png:
                            exe = "exiftool"
                            process = subprocess.Popen(
                                [exe, f],
                                stdout=subprocess.PIPE,
                                stderr=subprocess.STDOUT
                            )
                            data_from_exiftoll = get_data_from_exiftool(process.stdout)
                            file_date = data_from_exiftoll[4]  # was 4
                            user_comment = data_from_exiftoll[6]
                            has_lens_id = data_from_exiftoll[7]

                            if user_comment is not None and "Screenshot" in user_comment:
                                is_screenshot = True

                            is_video = True

                        elif src.name.endswith(".SRT"):
                            with open(f) as file_in:
                                file_date = list(file_in)[2].split(" ")[0]
                                is_video = True

                    if __name__ == '__main__':
                        correct_file_type = src.name.endswith(".jpeg") \
                                            or src.name.endswith(".JPG") \
                                            or src.name.endswith(".MP4") \
                                            or src.name.endswith(".JPEG") \
                                            or src.name.endswith(".mp4") \
                                            or src.name.endswith(".jpg") \
                                            or src.name.endswith(".MOV") \
                                            or src.name.endswith(".png") \
                                            or src.name.endswith(".PNG")

                    # print(filename)
                    # print(is_screenshot)
                    # print(file_date)
                    if is_screenshot:
                        # path to screenshots
                        components = src.name.split("/")
                        components = components[:-2]
                        del components[0]

                        screenshot_path = ""
                        for component in components:
                            screenshot_path += "/"
                            screenshot_path += component

                        screenshot_path = screenshot_path.rstrip(screenshot_path[0]) + "/Screenshots"

                        # move all screenshots to seperate folder for manual check
                        if not os.path.exists(screenshot_path):
                            os.mkdir(screenshot_path, 0o777)

                        os.replace(src.name, screenshot_path + "/" + filename)
                    elif file_date is not None and correct_file_type:
                        if len(file_date.split(" ")) > 1:
                            # place file based on date
                            # print(file_date.split((" ")))
                            date = str(file_date.split(" ")[0]).split(":")
                            time = str(file_date.split(" ")[1]).split(":")
                            if os.path.exists(path_to_timeline_csv):
                                d_type = {
                                    "Year": int,
                                    "Month": int,
                                    "Day": int,
                                    "Hour": int,
                                    "Minute": int,
                                    "Second": int,
                                    "File_name": str,
                                    "Location_name": str,
                                    "Location_type": str,
                                    "Latitude": float,
                                    "Longitude": float
                                }
                                df = pd.read_csv(path_to_timeline_csv, low_memory=False)
                                # display(df.head(10))
                                df_file_date = df.loc[
                                    (df['Day'] == date[2]) &
                                    (df['Month'] == date[1]) &
                                    (df['Year'] == date[0])
                                    ]
                                if df_file_date.shape[0] > 0:
                                    # there was media made on the same day
                                    assigned_coordinates = find_closest_media_same_day(df_file_date, time)
                                    year = assigned_coordinates[2]
                                    loc_name = assigned_coordinates[3]
                                    destination_folder = loc_name + "_" + year

                                    path_comp = src.name.split("/")[1:]
                                    path_comp = path_comp[: -2]

                                    final_path = ""
                                    for comp in path_comp:
                                        final_path += "/"
                                        final_path += comp

                                    final_path += "/" + year + "/" + destination_folder

                                    os.replace(src.name, final_path + "/" + filename)
                    # probably snapchat
                    else:
                        # path to snapchats
                        components = src.name.split("/")
                        components = components[:-2]
                        del components[0]

                        snapchat_path = ""
                        for component in components:
                            snapchat_path += "/"
                            snapchat_path += component

                        snapchat_path = snapchat_path.rstrip(snapchat_path[0]) + "/Snapchats"

                        # move all screenshots to seperate folder for manual check
                        if not os.path.exists(snapchat_path):
                            os.mkdir(snapchat_path, 0o777)

                        os.replace(src.name, snapchat_path + "/" + filename)
        except:
            print("Failed to sort media")

def menage_media(f):
    global zone_stage
    with open(f, 'rb') as src:
        search_zone = zone_stage
        if src.name.endswith(".jpeg") or src.name.endswith(".JPG") or src.name.endswith(
                ".JPEG") or src.name.endswith(".jpg"):
            img = Image(src)
            if img.has_exif:
                tags = img.list_all()
                if "datetime_original" in tags:
                    file_date = img.datetime_original
                    year = get_year_from_date(file_date)
                    if "gps_latitude" in tags and "gps_longitude" in tags:

                        city_key = 'city'
                        country_key = 'country_code'
                        tourism_key = 'tourism'
                        municipality_key = 'municipality'

                        lat = decimal_coords(img.gps_latitude, img.gps_latitude_ref)
                        lon = decimal_coords(img.gps_longitude, img.gps_longitude_ref)
                        sort_with_location_data(
                            lat,
                            lon,
                            file_date,
                            year,
                            src.name,
                            search_zone=search_zone
                        )
                    else:
                        if 'software' in tags:
                            # throw to lighroom folder that needs to be manually sorted
                            # I assume if they were edited they are important ;)
                            if 'Lightroom' in img.software:
                                ligthroom_path = os.path.join(master_path, "Lightroom")
                                file_name = src.name.split("/")[-1]
                                if not path.exists(ligthroom_path):
                                    os.mkdir(ligthroom_path, 0o777)
                                os.replace(src.name, ligthroom_path + "/" + file_name)
        elif src.name.endswith(".mov") or src.name.endswith(".MP4") or src.name.endswith(".MOV"):
            exe = "exiftool"
            process = subprocess.Popen(
                [exe, f],
                stdout=subprocess.PIPE,
                stderr=subprocess.STDOUT
            )
            data_from_exiftoll = get_data_from_exiftool(process.stdout)

            if data_from_exiftoll[0]:
                sort_with_location_data(
                    data_from_exiftoll[1],
                    data_from_exiftoll[2],
                    data_from_exiftoll[4],
                    data_from_exiftoll[3],
                    src.name,
                    isVideo=True,
                    search_zone=search_zone
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
                isVideo=True,
                search_zone=search_zone
            )

            sort_with_location_data(
                lat,
                lon,
                date,
                year,
                src.name.replace(".SRT", ".MP4"),
                isVideo=True,
                search_zone=search_zone
            )


def sort_with_location_data(lat, lon, file_date, year, file_name, isVideo=False, search_zone=True, deep_search=False):
    city_key = 'city'
    country_key = 'country_code'
    tourism_key = 'tourism'
    municipality_key = 'municipality'
    neighbourhood_key = 'neighbourhood'
    town_key = 'town'
    location = None
    city = None
    country = None
    tourism = None
    municipality = None
    neighbourhood = None
    zone = None
    to_from_zone = 0

    sort_ready = False
    if search_zone:
        zone = loc.file_in_zone(lat, lon, year, auto_zones, auto_zones_sorted_keys)
        sort_ready = True

    if zone is None:
        if not search_zone:
            try:
                location = geolocator.reverse(str(lat) + "," + str(lon)).raw['address']
                sort_ready = True
                # print(location)
                # print(lat, lon)
            except geoexc.GeocoderTimedOut:
                sleep(randint(1 * 100, 200) / 100)
                location = geolocator.reverse(str(lat) + "," + str(lon)).raw['address']
            except Exception as e:
                # write to log file
                #print("No location found for file: ", file_name, " ", str(e))
                return

            has_country_info = country_key in location.keys()

            if has_country_info:
                country = location[country_key]

            if city_key in location.keys():
                city = location[city_key]
                if city not in loc.config.keys():
                    if town_key in location.keys():
                        city = location[town_key]
            else:
                if town_key in location.keys():
                    city = location[town_key]

            if tourism_key in location.keys():
                tourism = location[tourism_key]

            if municipality_key in location.keys():
                municipality = location[municipality_key]

            if neighbourhood_key in location.keys():
                neighbourhood = location[neighbourhood_key]
        else:
            sort_ready = False
    else:
        to_from_zone = 1

    if sort_ready and year != "0000": # for some reason some files have this year
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
            zone=zone,
            isVideo=isVideo
        )

    if sort_ready:
        return None, to_from_zone
    else:
        return file_name, to_from_zone


# returns lat and lon of the closest (time wise) media found
def find_closest_media_same_day(data_frame, time) -> (float, float):
    hour_P = int(time[0])
    minute_P = int(time[1])

    hours = data_frame['Hour'].tolist()
    it = map(lambda hour: int(hour), hours)
    hours_int = list(it)
    hour_found = min(hours_int, key=lambda x: abs(x - hour_P))
    if hour_found < 10:
        hour_found = "0" + str(hour_found)
    dataFrame = data_frame.loc[data_frame['Hour'] == str(hour_found)]

    minutes = dataFrame['Minute'].tolist()
    it = map(lambda minute: int(minute), minutes)
    minutes_int = list(it)
    minute_found = min(minutes_int, key=lambda x: abs(x - minute_P))

    if minute_found < 10:
        minute_found = "0" + str(minute_found)

    df = dataFrame.loc[dataFrame['Minute'] == str(minute_found)]

    if df.shape[0] < 1:
        print(hour_found)
        print(minute_found)

    return float(df.iloc[0]['Latitude']), float(df.iloc[0]['Longitude']), df.iloc[0]['Year'], df.iloc[0][
        'Location_name']


def get_data_from_exiftool(data):
    lat = None
    lon = None
    year = None
    full_date = None
    make = None
    user_comment = None
    has_lens_id = False

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
        if tag_name == 'UserComment':
            user_comment = data_line_components[1]
        if tag_name == 'LensID':
            has_lens_id = True

        has_location_data = lat is not None

    return has_location_data, lat, lon, year, full_date, make, user_comment, has_lens_id


if __name__ == '__main__':
    input_path = str(input("Please provide path to folder you want to sort: "))

    path_components = input_path.split("/")
    path_components.pop()
    path_components.pop()
    path_components.pop(0)
    master_path = ""

    for comp in path_components:
        master_path += "/"
        master_path += comp

    while not path.exists(input_path):
        print("\nPath does not exist, please try again.\n")
        input_path = input("Please provide path to folder you want to sort: ")

    final_format = {}
    paths = []

    # json_path = str(input("Please provide path to json zones: (type n to skip)"))
    json_path = "/Users/mikolajzawada/Documents/zones.json"

    # creating zones dictionary
    if json_path != "n":
        while not path.exists(json_path):
            print("\nPath does not exist, please try again.\n")
            json_path = input("Please provide path to json zones: (type n to skip)")

        with open(json_path) as json_file:
            auto_zones = json.load(json_file)
            auto_zones_sorted_keys = sorted(auto_zones, key=lambda x: auto_zones[x]["Level"])
    else:
        json_path = None

    paths = []
    for filename in os.listdir(input_path):
        media_path = os.path.join(input_path, filename)
        if os.path.isfile(media_path):
            paths.append(media_path)

    print("Searching local zones")

    if __name__ == '__main__':
        with mp.Pool() as p:
            p.imap_unordered(menage_media, tqdm(paths))
            p.close()
            p.join()
            p.terminate()

    zone_stage = False

    paths_to_delete = []

    for path_a in paths:
        if not path.exists(path_a):
            from_zone += 1
            paths_to_delete.append(path_a)

    for bad_path in paths_to_delete:
        paths.remove(bad_path)

    minutes, seconds = divmod(len(paths), 60)
    print("Looking up media, time remaining min: ", minutes, " sec: ", seconds)

    for path in tqdm(paths):
        try:
            menage_media(path)
        except:
            print("failed to sort media")

    print("Files sorted from zones: ", from_zone)
    print("Do you want to try sorting photos without location data, based on those already sorted? (Y/N)")
    answer = input("")

    if answer in ["Y", "y", "yes", "a jakze"]:
        # sort based on timeline csv
        sort_based_on_timeline_file()
