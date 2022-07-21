import pandas as pd
import os
from os import path
import csv
from enum import Enum
from config import config  # python file containing dictionary with custom config
from config import path_to_timeline_csv
from shapely.geometry import Point
from shapely.geometry.polygon import Polygon


class LocationType(Enum):
    City = 'city'
    Tourism = 'tourism'
    Muniplicity = 'municipality'
    Country = 'country'
    Zone = 'zone'
    Neighbourhood = 'neighbourhood'

def alocate_photo(file_date, year, origin_path, loc, lat, lon, city=None, country=None, tourism=None, municipality=None, neighbourhood=None, isVideo=False):
    country_name = get_country_name(country)
    parent_folder = None
    path_components = origin_path.split("/")
    file_name = path_components[-1]
    path_components.pop()
    path_components.pop()
    path_components.pop(0)
    master_path = ""

    for comp in path_components:
        master_path += "/"
        master_path += comp

    loc_type = None
    name = None

    point = Point(lat, lon)
    for zone_name, points in config['Zones'].items():
        zone = Polygon(points)
        if zone.contains(point):
            parent_folder = zone_name + "_" + year
            name = zone_name
            loc_type = LocationType.Zone
            break

    if city is not None:
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

        add_photo_info(file_name, parent_path, year, name, file_date, loc_type, municipality, lon, lat)

        # updating timeline file
        update_timeline_file(file_date, file_name, name, loc_type.value, lat, lon)

    else:
        print("unknown")
        unknown_master_path = os.path.join(master_path, "unknown")
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

    # print("Folders: ", master_folder, " ", parent_folder)


def get_country_name(country_code) -> str:
    df = pd.read_csv('data.csv')
    data = df[df['Code'] == country_code.upper()]
    name = data['Name'].item()
    return name


def add_photo_info(file_name, parent_path, year, name, full_date, type: LocationType, municipality=None,
                   longitude=None, latitude=None):
    path_to_info = parent_path + '/' + "photoInfo.csv"
    full_date = full_date.split(" ")[0]
    parameters = ['File_name', 'Year', 'Name', 'Municipality', 'Full_date', 'Latitude', 'Longitude', 'Type']
    if path.exists(path_to_info):
        with open(path_to_info, 'a') as f:
            writer = csv.writer(f)
            writer.writerow([file_name, year, name, municipality, full_date, latitude, longitude, type.value])
    else:
        with open(path_to_info, 'a') as f:
            writer = csv.writer(f)
            writer.writerow(parameters)
            writer.writerow([file_name, year, name, municipality, full_date, latitude, longitude, type.value])


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


def update_timeline_file(data, file_name, location_name, location_type, lat, lon):
    date = str(data.split(" ")[0]).split(":")
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
                    lon
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
                    "Longitude"
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
