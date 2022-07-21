
<h1 align="center">
  <br>
  <img width="330" alt="SorterLogo" src="https://user-images.githubusercontent.com/40431386/178159216-f24445de-bd2f-472e-8330-efe2b81a3846.png">
  <br>
  Location based media sorter
  <br>
</h1>

<h4 align="center">Simple media sorter that based on your customization will sort any mess.</h4>

<p align="center">
  <a href="#key-features">Key Features</a> •
  <a href="#how-to-use">How To Use</a> •
  <a href="#license">License</a>
</p>

## Key Features

* Select cities of interest
  - Fill dictionary with names of cities within countries your photos were taken. If a photo was taken in a city which name is not in a dictionary it will be placed in a folder with the coutry name and year. For example: Austria_2022
* Select and name special zones
  - Fill dictionary with cooridnates of boudries of special zones. For example, if you want to have all your photos taken inside your house and your garden in one folder for best accuracy create a zone (like in the example below) around your house and name it so in few years you will remember what you meant. 
* Select tourist attractions
  - Fill dictionary with tourist attractions names you want to be stored seperately. For example if under "Tourism" you add "Universal City", all photos taken in Universal City will be placed in a folder Universal City_YEAR.
* Supported file types
  - JPG, MOV, MP4, SRT(DJI)


Example config dictionary:

```bash

config = {
    "United States": [
        "Los Angeles",
        "San Francisco",
        "New York",
        "Las Vegas",
        "Anchorage",
        "Fairbanks",
        "Whitter",
        "Denver",
        "Estes Park",
        "Seattle"
    ]
    "Austria": [
        "Vien"
    ],
    "United Kingdom": [
        "London",
        "Cambridge"
    ],
    "Canada": [
        "Toronto",
        "Vancouver"
    ],
    "Germany": [

    ],
    "Czech Republic": [
        "Praha"
    ],
    "Tourism": [
        "Universal City"
    ],
    "Zones": {
        "Whitter": [
            (60.788566, -148.817399),
            (60.758982, -148.706227),
            (60.757976, -148.632069),
            (60.799709, -148.596020),
            (60.795186, -148.826390)
        ]
    }
}
```

## How To Use

To clone and run this application, you'll need [Git](https://git-scm.com) and [Python](https://www.python.org/downloads/) 
From your command line:

```bash
# Clone this repository
$ git clone https://github.com/AtLab12/Photo-sorter.git

# Go into the repository
$ cd Photo-sorter

# Install dependencies

# Run the script
$ python3 main.py

# follow instructions
```

## License

MIT



