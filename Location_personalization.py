import pandas as pd
import os
from os import path
import csv
from enum import Enum
import geopy.distance
from config import config # python file containing only dictoary with custom config


class Location_Type(Enum):
    City = 'city'
    Tourism = 'tourism'
    Muniplicity = 'municipality'
    Country = 'country'


# .value

test_master_path = "/Users/mikolajzawada/Documents/Photos_to_sort"


def alocate_photo(file_date, year, origin_path, loc, lat, lon, city=None, country=None, tourism=None,
                  municipality=None):
    country_name = get_country_name(country)
    parent_folder = None
    file_name = origin_path.split("/")[-1]
    loc_type = None
    name = None

    # print(file_name)
    if city is not None:
        if city in config[country_name]:
            parent_folder = city + "_" + year
            loc_type = Location_Type.City
            name = city
        else:
            pass
            # print("Unfamiliar city ", city)

    if parent_folder is None and tourism is not None:
        if tourism in config["Tourism"]:
            parent_folder = tourism + "_" + year
            name = tourism
            loc_type = Location_Type.Tourism
        else:
            pass
            # print("Unknown tourism")

    if parent_folder is None and municipality is not None:
        if municipality in config[country_name]:
            parent_folder = "M_" + municipality + "_" + year
            name = municipality
            loc_type = Location_Type.Muniplicity
        else:
            pass
            # print("Unknown municipality")

    if parent_folder is None and country is not None:
        parent_folder = country_name + "_" + year
        name = country_name
        loc_type = Location_Type.Country

    mode = 0o777
    master_path = os.path.join(test_master_path, str(year))

    if parent_folder is not None:
        if not path.exists(master_path):
            os.mkdir(master_path, mode)

        parent_path = os.path.join(master_path, parent_folder)

        if not path.exists(parent_path):
            os.mkdir(parent_path, mode)

        os.replace(origin_path, parent_path + "/" + file_name)
        add_photo_info(file_name, parent_path, year, name, file_date, loc_type, municipality, lon, lat)

    else:
        unknown_master_path = os.path.join(test_master_path, "unknown")
        if not path.exists(unknown_master_path):
            os.mkdir(unknown_master_path, mode)

        un_parent_path = os.path.join(unknown_master_path, year)

        if not path.exists(un_parent_path):
            os.mkdir(un_parent_path, mode)

        os.replace(origin_path, un_parent_path + "/" + file_name)

        with open(test_master_path + '/' + "sortLog.txt", 'a') as f:
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


def add_photo_info(file_name, parent_path, year, name, full_date, type: Location_Type, municipality=None,
                   longitude=None, latitude=None):
    path_to_info = parent_path + '/' + "photoInfo.csv"
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


def average_distance_from_set(folder_path, latitude, longitude):
    path_to_data_file = folder_path + "/" + 'photoInfo.csv'
    if path.exists(path_to_data_file):
        df = pd.read_csv(path_to_data_file)
        df = df.reset_index()

        for index, row in df.iterrows():
            tmp_lat = row['Latitude']
            tmp_lon = row['Longitude']
            print(folder_path)
            print(geopy.distance.geodesic((latitude, longitude), (tmp_lat, tmp_lon)).km)
        pass


def tourism_in_folder(path_a) -> (str, [str]):
    result = False
    tourist_files: [str] = []

    for filename in os.listdir(path_a):
        f = os.path.join(path_a, filename)
        data_path = f + "/" + 'photoInfo.csv'

        if path.exists(data_path):
            df = pd.read_csv(data_path)
            # print(df['Type'].tolist())
            if 'tourism' in df['Type'].tolist():
                print("has tourism in folder")
                result = True
                tourist_files.append(filename)
    return result, tourist_files
