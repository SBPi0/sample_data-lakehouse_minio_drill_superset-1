# Eksempel på at bruge REST-API kald til at hente højdedata, 
#   til at supplere de upræcise målinger fra løbeuret.
# I data fra urets FIT-fil får vi det unøgagtige data felt `altitude` 
#   (svarende til det man bruger i en flyvemaskine), 
#   fra opentopodata.org får vi data `elevation`.som jeg gemmer i datasettet, under samme navn.


# Vi skal lige have nogen geopunkter, som vi ksla finde elevation til
def indlaes_fra_fit(fname = "data/hok_klubmesterskab_2022/CA8D1347.FIT"):
    from fit_file import read
    points = read.read_points(fname)
    return points

punkter = indlaes_fra_fit()

# print(f"Der er indlæst {len(punkter)} punkter fra filen")
print(punkter[300])

## -----------------------------------------------------------------

## ----------------

import requests
from time import sleep

# En funktion som kan hente en højde, fra et punkt.
def getElevation(lat, long):
    """
    Fetch elevation for geolocation
    
    lat, long: Latitude and longitude representing geolocation
    return: elevation for geolocation
    """

    url = "https://api.opentopodata.org/v1/srtm90m"

    data = {
    "locations": f"{lat},{long}",
     "interpolation": "cubic",
    }
    response = requests.post(url, json=data)
  
    if response.status_code == 200:
        print("response:", response.json())
        json = response.json()
        elevation = json['results'][0]['elevation']
    else:
        print(response)
        print(response.status_code)
        print(response.reason)
        print(response.text)

    
    # to avoid congestion of to many requst pr second
    sleep(1)
    return elevation

lat = punkter[300]['latitude']
long = punkter[300]['longitude']

e = getElevation(lat, long)
print(f"lat: {lat}, long: {long} : elevastion {e} m above sea level")

def addElevations(punkter):
    """
    adds elevation to points, fetched from opentopodata.org

    punkter: points to add elevation to
    return: List of points with elevation added to each dict
    """
    elevatedPoints = []
    for p in punkter:
        lat = p['latitude']
        long = p['longitude']
        e = getElevation(lat, long)
        print(f"lat: {lat}, long: {long} : elevastion {e} m above sea level")

        p['elevation'] = e
        elevatedPoints.append(p)
    return elevatedPoints

# elevatedPoints = addElevations(punkter)
# print(elevatedPoints[300])
    
def getElevations(L):
    """
    A more advanced funtion to add elevation to a list of points, from a FIT-file.
    This version packs as many as 100 geopositions in each request, 
    repeating as many requests as required to fetch elevation for all points.
    
    L: a list of dicts, each containing `latitude` and `longitude`
    return: a new list with `elevation` added to each point
    """
    eL = []
    # each request to opentopodata, can handle a maximum og 100 geolocations
    for page in range(0, len(L), 100):
        print(page)
        geoStr = [f"{p['latitude']},{p['longitude']}" for p in L[page:page+100]  ] # a list of strings with "{lat},{long}"
        # print(geoStr)
        # print( len(geoStr) )
        locations = '|'.join(geoStr) # all strings in one, separated by `|`
        # print(locations)

        url = "https://api.opentopodata.org/v1/srtm90m"

        data = {
        "locations": locations,
        "interpolation": "cubic",
        }
        response = requests.post(url, json=data)

    
        if response.status_code == 200:
            # print(response.json())
            pass
        else:
            print(response)
            print(response.status_code)
            print(response.reason)
            print(response.text)

        json = response.json()

        for i, r in enumerate(json['results']):
            p = L[page + i]
            p['elevation'] = r['elevation']
            eL.append(p)

        # to avoid congestion of to many requst pr second
        sleep(1)
    return eL

ePoints = getElevations(punkter)
print(ePoints[300])

import csv

def storeCSV(filename, dictList):
    """
    Store a list of dicts as CSV file
    filename: Name of file to store data in 
    """
    with open(filename, 'w', newline='') as f:  
        w = csv.DictWriter(f, dictList[0].keys()) 
        w.writeheader()
        w.writerows(dictList)

    sleep(1)
storeCSV('elevatedPoints.csv', ePoints)

