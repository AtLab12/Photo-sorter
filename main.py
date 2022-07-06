from exif import Image
from geopy.geocoders import Nominatim

test_path = "/Users/mikolajzawada/Developer/Photo_sorter/IMG_0250.JPG"
#unsorted_folder = input("Please provide path to folder you want to sort: ")
geolocator = Nominatim(user_agent="AtLabPhotosorter")

final_format = {}

def decimal_coords(coords, ref):
    decimal_degrees = coords[0] + coords[1] / 60 + coords[2] / 3600
    if ref == 'S' or ref == 'W':
        decimal_degrees = -decimal_degrees
    return decimal_degrees

def get_year_from_date(date) -> str:
    date_elements = date.split(" ")
    year = date_elements[0].split(":")[0]
    return year

with open(test_path, 'rb') as src:
    img = Image(src)
    print(src.name, img)

    if img.has_exif:
        print(img.exif_version)
        data = img.get_all()
        for element in data:
            print(element, data[element])
        lat = decimal_coords(data['gps_latitude'], data['gps_latitude_ref'])
        lon = decimal_coords(data['gps_longitude'], data['gps_longitude_ref'])
        location = geolocator.reverse(str(lat) + "," + str(lon)).raw['address']
        year = get_year_from_date(data['datetime_original'])
        city = location['city']
    else:
        print("no exif data")
