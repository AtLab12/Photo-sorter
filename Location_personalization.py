import pandas as pd
import os
from os import path
import csv
from enum import Enum
from config import config  # python file containing dictionary with custom config
from config import path_to_timeline_csv
from shapely.geometry import Point
from shapely.geometry.polygon import Polygon
import hashlib


class LocationType(Enum):
    City = 'city'
    Tourism = 'tourism'
    Muniplicity = 'municipality'
    Country = 'country'
    Zone = 'zone'
    Neighbourhood = 'neighbourhood'


def alocate_photo(file_date, year, origin_path, loc, lat, lon, city=None, country=None, tourism=None, municipality=None,
                  neighbourhood=None, zone=None, isVideo=False):
    if country is not None:
        country_name = get_country_name(country)
    parent_folder = None
    loc_type = None
    name = None
    hash = get_hash(origin_path)
    path_components = origin_path.split("/")
    file_name = path_components[-1]
    path_components.pop()
    path_components.pop()
    path_components.pop(0)
    master_path = ""

    for comp in path_components:
        master_path += "/"
        master_path += comp

    if zone is not None:
        parent_folder = zone + "_" + year
        loc_type = LocationType.Zone
        name = zone

    if city is not None and parent_folder is None:
        if city in config[country_name]:
            parent_folder = city + "_" + year
            loc_type = LocationType.City
            name = city

    if parent_folder is None and tourism is not None:
        if tourism in config["Tourism"]:
            parent_folder = tourism + "_" + year
            name = tourism
            loc_type = LocationType.Tourism

    if parent_folder is None and neighbourhood is not None:
        if neighbourhood in config["Tourism"]:
            parent_folder = neighbourhood + "_" + year
            name = neighbourhood
            loc_type = LocationType.Neighbourhood

    if parent_folder is None and municipality is not None:
        if municipality in config[country_name]:
            parent_folder = municipality + "_" + year
            name = municipality
            loc_type = LocationType.Muniplicity

    if parent_folder is None and country is not None:
        parent_folder = country_name + "_" + year
        name = country_name
        loc_type = LocationType.Country

    mode = 0o777
    master_path = os.path.join(master_path, str(year))

    if parent_folder is not None:
        if not path.exists(master_path):
            os.mkdir(master_path, mode)

        if isVideo:
            parent_path = os.path.join(master_path, parent_folder)
            full_parent_path = os.path.join(parent_path, "Video")
        else:
            parent_path = os.path.join(master_path, parent_folder)

        if not path.exists(parent_path):
            os.mkdir(parent_path, mode)

        if isVideo and not path.exists(full_parent_path):
            os.mkdir(full_parent_path, mode)

        if isVideo:
            os.replace(origin_path, full_parent_path + "/" + file_name)
        else:
            os.replace(origin_path, parent_path + "/" + file_name)

        add_photo_info(file_name, parent_path, year, name, file_date, loc_type, municipality, lon, lat, hash)

        update_timeline_file(file_date, file_name, name, loc_type.value, lat, lon, hash)

    else:
        unknown_master_path = os.path.join(master_path, "unknown_location")
        if not path.exists(unknown_master_path):
            os.mkdir(unknown_master_path, mode)

        un_parent_path = os.path.join(unknown_master_path, year)

        if not path.exists(un_parent_path):
            os.mkdir(un_parent_path, mode)

        os.replace(origin_path, un_parent_path + "/" + file_name)

        with open(master_path + '/' + "sortLog.txt", 'a') as f:
            f.write("\n")
            f.write(file_name)
            f.write("\n")
            f.write(str(loc))
            f.write("\n")


def get_country_name(country_code) -> str:
    df = pd.read_csv('data.csv')
    data = df[df['Code'] == country_code.upper()]
    name = data['Name'].item()
    return name


def add_photo_info(file_name, parent_path, year, name, full_date, type: LocationType, municipality=None,
                   longitude=None, latitude=None, hash=None):
    path_to_info = parent_path + '/' + "photoInfo.csv"
    full_date = full_date.split(" ")[0]
    parameters = ['File_name', 'Year', 'Name', 'Municipality', 'Full_date', 'Latitude', 'Longitude', 'Type', 'Hash']
    if path.exists(path_to_info):
        with open(path_to_info, 'a') as f:
            writer = csv.writer(f)
            writer.writerow([file_name, year, name, municipality, full_date, latitude, longitude, type.value, hash])
    else:
        with open(path_to_info, 'a') as f:
            writer = csv.writer(f)
            writer.writerow(parameters)
            writer.writerow([file_name, year, name, municipality, full_date, latitude, longitude, type.value, hash])


def tourism_in_folder(path_a) -> (str, [str]):
    result = False
    tourist_files: [str] = []

    for filename in os.listdir(path_a):
        f = os.path.join(path_a, filename)
        data_path = f + "/" + 'photoInfo.csv'

        if path.exists(data_path):
            df = pd.read_csv(data_path)
            if 'tourism' in df['Type'].tolist():
                result = True
                tourist_files.append(filename)
    return result, tourist_files


def update_timeline_file(data, file_name, location_name, location_type, lat, lon, hash=None):
    date_comp = data.split(" ")[0]

    if ":" in date_comp:
        date = str(date_comp).split(":")
    elif "-" in date_comp:
        date = str(date_comp).split("-")

    time = ["0", "0", "0"]

    if len(data.split(" ")) > 1:
        time = str(data.split(" ")[1]).split(":")

    if path.exists(path_to_timeline_csv):
        with open(path_to_timeline_csv, 'a') as f:
            writer = csv.writer(f)
            writer.writerow(
                [
                    date[0],
                    date[1],
                    date[2],
                    time[0],
                    time[1],
                    time[2],
                    file_name,
                    location_name,
                    location_type,
                    lat,
                    lon,
                    hash
                ]
            )
    else:
        with open(path_to_timeline_csv, 'a') as f:
            writer = csv.writer(f)
            writer.writerow(
                [
                    "Year",
                    "Month",
                    "Day",
                    "Hour",
                    "Minute",
                    "Second",
                    "File_name",
                    "Location_name",
                    "Location_type",
                    "Latitude",
                    "Longitude",
                    "Hash"
                ]
            )

            writer.writerow(
                [
                    date[0],
                    date[1],
                    date[2],
                    time[0],
                    time[1],
                    time[2],
                    file_name,
                    location_name,
                    location_type,
                    lat,
                    lon
                ]
            )


def file_in_zone(lat, lon, year, auto_zones, auto_zones_keys_sorted, ):
    name = None

    # checking if media is from a hand made zone
    point = Point(lat, lon)
    for zone_name, points in config['Zones'].items():
        zone = Polygon(points)
        if zone.contains(point):
            name = zone_name
            break

    # checking if photo was taken in an usa national park
    if name is None:
        df = pd.read_csv('nps_boundary.csv')
        national_parks_df = df[df['UNIT_TYPE'] == 'National Park']
        point = Point(lat, lon)

        for index, park in national_parks_df.iterrows():
            shape_type = park['WKT'].split()[0]
            park_name = park['UNIT_NAME']

            if shape_type == 'POLYGON':
                data = park['WKT'].split("POLYGON Z ((")[1]
                data = data.split(" 0))")[0].split(" 0, ")

                polygon = []

                for lat_lon in data:
                    sub_data = lat_lon.split(" ")
                    polygon.append((float(sub_data[1]), float(sub_data[0])))
                polygon = Polygon(polygon)

                if polygon.contains(point):
                    name = park_name
                    break

            elif shape_type == 'MULTIPOLYGON':
                data = park['WKT'].split("))")
                data[0] = data[0].split("MULTIPOLYGON Z (((")[1]
                data.pop()

                tmp_ind = 1
                for item in data[1:]:
                    data[tmp_ind] = item.split(", ((")[1]
                    tmp_ind += 1

                polygons = []

                for item in data:
                    lat_lon_data = item.split(" 0, ")
                    lat_lon_data[-1] = lat_lon_data[-1][:-2]
                    polygon = []
                    for lat_lon in lat_lon_data:
                        sub_data = lat_lon.split(" ")
                        polygon.append((float(sub_data[1]), float(sub_data[0])))
                    polygons.append(Polygon(polygon))

                for polygon in polygons:
                    if polygon.contains(point):
                        name = park_name
                        break

    # checking if media is from a automatically created zone (saved in json file)
    if name is None:
        if auto_zones_keys_sorted != None:
            safe_countries = [
                "Poland",
                # "Italy",
                "Netherlands"
            ]

            for key in auto_zones_keys_sorted:
                zone_country_config = int(auto_zones[key]["Level"]) < 3 or key in safe_countries
                if "Norm_coord" in auto_zones[key].keys() and zone_country_config:
                    coord = list(map(lambda x: [float(x[0]), float(x[1])], auto_zones[key]["Norm_coord"]))
                    zone = Polygon(coord)
                    if zone.contains(point):
                        name = auto_zones[key]["ID"]
                        # print("auto zone found ", name)
                        break
                """
                elif "Norm_coord_1" in auto_zones[key].keys() and "Norm_coord_2" in auto_zones[key].keys():
                    coord_1 = list(map(lambda x: [float(x[0]), float(x[1])], auto_zones[key]["Norm_coord_1"]))
                    coord_2 = list(map(lambda x: [float(x[0]), float(x[1])], auto_zones[key]["Norm_coord_2"]))
                    zone_1 = Polygon(coord_1)
                    zone_2 = Polygon(coord_2)
                    if zone_1.contains(point) or zone_2.contains(point):
                        name = auto_zones[key]["ID"]
                        break
                """

    return name


def get_hash(img_path):
    with open(img_path, "rb") as f:
        img_hash = hashlib.md5()
        while chunk := f.read(8192):
            img_hash.update(chunk)

        hash = img_hash.hexdigest()
    return str(hash)
