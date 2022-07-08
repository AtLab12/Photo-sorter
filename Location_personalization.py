import pandas as pd
import os
from os import path



test_master_path = "/Users/mikolajzawada/Documents/Photos_to_sort"

def alocate_photo(year, originPath, loc, city=None, country=None, tourism=None, municipality=None):
    country_name = get_country_name(country)
    master_folder = year
    parent_folder = None
    file_name = originPath.split("/")[-1]
    #print(file_name)
    if city is not None:
        if city in config[country_name]:
            parent_folder = city + "_" + year
        else:
            pass
            #print("Unfamiliar city ", city)
    if parent_folder is None and tourism is not None:
        if tourism in config["Tourism"]:
            parent_folder = tourism + "_" + year
        else:
            pass
            #print("Unknown turism")
    if parent_folder is None and municipality is not None:
        if municipality in config[country_name]:
            parent_folder = municipality + "_" + year
        else:
            pass
            #print("Unknown municipality")

    mode = 0o777
    master_path = os.path.join(test_master_path, str(year))

    if parent_folder is not None:
        if not path.exists(master_path):
            os.mkdir(master_path, mode)

        parent_path = os.path.join(master_path, parent_folder)

        if not path.exists(parent_path):
            os.mkdir(parent_path, mode)

        os.replace(originPath, parent_path+"/"+file_name)
    else:
        unknown_master_path = os.path.join(test_master_path, "unknown")
        if not path.exists(unknown_master_path):
            os.mkdir(unknown_master_path, mode)

        un_parent_path = os.path.join(unknown_master_path, year)

        if not path.exists(un_parent_path):
            os.mkdir(un_parent_path, mode)

        os.replace(originPath, un_parent_path+"/"+file_name)

        with open(test_master_path+'/'+"sortLog.txt", 'w') as f:
            f.write("\n", file_name, "\n", loc)


    #print("Folders: ", master_folder, " ", parent_folder)

def get_country_name(country_code) -> str:
    df = pd.read_csv('data.csv')
    data = df[df['Code'] == country_code.upper()]
    name = data['Name'].item()
    return name