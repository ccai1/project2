import json
from urllib import request, parse
from datetime import datetime

from util import routes

# api authentication
with open("data/keys.json") as f:
	api_keys = json.load(f)

app_id = api_keys["transit_id"]
app_code = api_keys["transit_code"]

"""
    Gets the data of the directions to the desired location
    Returns a list of possible routes
    Parameters: location -> starting address
                destination -> ending address

    To-do:
        Check to make sure that addresses are appropriate and return geocodes
"""
def get_transit_info(location, destination): # hide key, vars for start/end address, key

    # try:
    #     URL_STUB = "https://transit.api.here.com/v3/route.json?dep={},{}&arr={},{}&time={}&app_id={}&app_code={}"
	#
    #     # optains a list => [latitude, longitude] of address given
    #     dep = get_geo(location)
    #     arr = get_geo(destination)
	#
    #     # assign the lat and longs to variables
    #     dep_lat = dep["lat"]
    #     dep_long = dep["lng"]
    #     arr_lat = arr["lat"]
    #     arr_long = arr["lng"]
	#
    #     # current time + 5 minutes
    #     time = curr_time()
	#
	# 	# setting the url
    #     URL = URL_STUB.format(dep_lat, dep_long, arr_lat, arr_long, time, app_id, app_code)
    #     # print(URL)
	#
    #     # getting data
    #     response = request.urlopen(URL)
    #     response = response.read()
    #     data = json.loads(response)
	#
    #     # getting just the routes
    #     routes = data["Res"]["Connections"]["Connection"]
	#
    #     #print(routes)
    #     return routes
	#
    # except:
    #     return False

	URL_STUB = "https://transit.api.here.com/v3/route.json?dep={},{}&arr={},{}&time={}&app_id={}&app_code={}"

	# optains a list => [latitude, longitude] of address given
	dep = get_geo(location)
	arr = get_geo(destination)

	# assign the lat and longs to variables
	dep_lat = dep["lat"]
	dep_long = dep["lng"]
	arr_lat = arr["lat"]
	arr_long = arr["lng"]

	# current time + 5 minutes
	time = curr_time()

	# setting the url
	URL = URL_STUB.format(dep_lat, dep_long, arr_lat, arr_long, time, app_id, app_code)
	print(URL)

	# getting data
	response = request.urlopen(URL)
	response = response.read()
	data = json.loads(response)

	# getting just the routes
	routes = data["Res"]["Connections"]["Connection"]

	#print(routes)
	return routes

########################################
#####   START OF GETS FROM ROUTE   #####
########################################

"""
    Returns the total time for a single route
    Parameter: data -> one possible route
    Ex: total_time( get_transit_info( something1, something2 )[ 0 ] )

    To-do:
        try except
"""
def get_total_time(data):
    time = data["duration"][2:-1]

    if len(time) == 5:
        time = int(time[0:2]) * 3600 + int(time[3:5]) * 60
    else:
        time = int(time[0:2]) * 60

    # if len(time) == 5:
	#
    #     if time[0] == '0':
	#
    #         if time[3] == '0':
    #             time = time[1:2] + " hours and " + time[4:] + " minutes"
    #         elif time[1] == '1':
    #             time = time[1:2] + " hour and " + time[4:] + " minutes"
    #         else:
    #             time = time[1:2] + " hours and " + time[3:] + " minutes"
	#
    #     else:
	#
    #         if time[3] == '0':
    #             time = time[0:2] + " hours and " + time[4:] + " minutes"
    #         elif time[1] == '1':
    #             time = time[0:2] + " hour and " + time[4:] + " minutes"
    #         else:
    #             time = time[0:2] + " hours and " + time[3:] + " minutes"
    # else:
	#
    #     if time[0] == '0':
    #         time = time[1:] + 'minutes'
    #     else:
    #         time = time + 'minutes'

    # time += " minutes"
    # print ("---DATA IS---")
    # print (time)

    return time

"""
    Returns the number of transfers for a single route
    Parameter: data -> one possible route
"""
def get_num_transfers(data):
    return data["transfers"]

"""
    Get the directions of a single route
    Returns a list where each element contains information via a dictionary on a single step in the route
"""
def get_directions(data):
    directions = data["Sections"]["Sec"]

    # modes of transportation
    mode = {0 : "high speed train",
            1 : "intercity train",
            2 : "inter regional train",
            3 : "regional train",
            4 :	"city train",
            5 :	"bus",
            6 :	"ferry",
            7 :	"train",
            8 :	"light rail",
            9 :	"private bus",
            10 : "inclined",
            11 : "aerial",
            12 : "bus rapid",
            13 : "monorail",
            14 : "flight",
            }

    ret = []

    for step in directions:

        dicts = {}

        time = step["Journey"]["duration"][2:-1]
        if time[0] == '0':

            if time[1] == '1':
                dicts["time"] = time[1:]  + " minute" # time to complete single step
            else:
                dicts["time"] = time[1:]  + " minutes"

        else:

            dicts["time"] = time + " minutes"

        if step["mode"] == 20:

            # get the starting address either from a station or a place
            if "Addr" in step["Dep"].keys():
                to_lat = step["Dep"]["Addr"]["y"]
                to_lng = step["Dep"]["Addr"]["x"]

            if "Stn" in step["Dep"].keys():
                to_lat = step["Dep"]["Stn"]["y"]
                to_lng = step["Dep"]["Stn"]["x"]

            start = get_rev_geo(to_lat, to_lng)

            # get the destination address either from a station or a place
            if "Addr" in step["Arr"].keys():
                to_lat = step["Arr"]["Addr"]["y"]
                to_lng = step["Arr"]["Addr"]["x"]

            if "Stn" in step["Arr"].keys():
                to_lat = step["Arr"]["Stn"]["y"]
                to_lng = step["Arr"]["Stn"]["x"]

            end = get_rev_geo(to_lat, to_lng)

            # print("Starting address: " + start)
            # print("Ending address: " + end)
            walking = routes.get_directions(routes.getDirectionsInfo(start, end, "pedestrian"))
            # print(walking)

            dir = ""
            for i in walking:
                dir += i + " "

        else:

            dir = "Take the {} {} headed towards {} for {} stops. Get off at {}."

            transit_name = step["Dep"]["Transport"]["name"]
            transit_type = mode[step["mode"]]
            towards = step["Dep"]["Transport"]["dir"]

            num_stops = len( step["Journey"]["Stop"] )
            dest = step["Arr"]["Stn"]["name"] + " station"

            dir = dir.format(transit_name, transit_type, towards, num_stops, dest)

        dicts["dir"] = dir
        ret.append(dicts)

    return ret



######################################
#####   END OF GETS FROM ROUTE   #####
######################################


"""
    Acquire the geocode of any address
    Parameter: place -> legitamate address

    To-do:
        Check to make sure an incorrect address isn't entered
        if it is then soemthing should be returned.
"""
def get_geo(place):
    URL_STUB = "http://www.mapquestapi.com/geocoding/v1/address?key={}&location={}"

    key = "HetYdvBFjsiAKOqjuLAUOmCWrHaRvqDS"
    location = fix_url(place)

    URL = URL_STUB.format(key, location)
    print(URL)
    print()

    response = request.urlopen(URL)
    response = response.read()
    data = json.loads(response)

    #print(data)

    geo_code = data["results"][0]["locations"][0]["latLng"]
    # print(geo_code)

    return geo_code

"""
    Acquire the geocode of any address
    Parameter: lat -> latitude
               long -> longitude

    To-do:
        Check to make sure an incorrect latitude or longitude isn't entered
        if it is then soemthing should be returned.
"""
def get_rev_geo(lat, long):
    URL_STUB = "http://www.mapquestapi.com/geocoding/v1/reverse?key={}&location={},{}"

    key = "HetYdvBFjsiAKOqjuLAUOmCWrHaRvqDS"

    URL = URL_STUB.format(key, lat, long)
    print(URL)
    print()

    response = request.urlopen(URL)
    response = response.read()
    data = json.loads(response)

    #print(data)
    my_data = data["results"][0]["locations"][0]
    address = my_data["street"] + ' '
    address += my_data["adminArea5"] + ' '
    address += my_data["adminArea3"] + ' '
    address += my_data["postalCode"]
    # print(address)

    return address

"""
    Fixes the address to make it appropriate for the api to take in
    Parameter; place -> address
"""
def fix_url(place):
    place = place.replace(" ", "%20")
    place = place.replace("&", "")
    return place

"""
    Returns a time appropriate to use for acquiring directions
"""
def curr_time():
    # must be in format yyyy-mm-ddThh:mm:ss
    # must be at or after local time
    "2018-12-02 16:18:58.718602"
    t = str(datetime.now())
    t = t.split(" ")
    time = t[0]
    time += "T{}%3A{}%3A00"

    ti = t[1].split(":")

    if ti[1] == "55":
        hour = int(ti[0]) + 1
        if hour < 10:
            hour = "0" + str(hour)
        else:
            hour = str(hour)
    else:
        hour = int(ti[0])
        if hour // 10 == 0:
            hour = '0' + str(hour)
        print('---HOUR---')
        print (hour)

    minute = (int(ti[1]) + 5) % 60
    # print('---MINUTE---')
    # print (minute)
    if minute // 10 == 0:
        minute = '0' + str(minute)
    time = time.format(hour, minute)

    # print(time)
    return time


now = "345 Chambers St New York NY 10282"
to = "116th St & Broadway, New York, NY 10027"
#
# x = get_geo(now)
# y = get_geo(to)
#
# print ('---TESTING transit.py---')
#
# print ('rou')
# rou = get_transit_info(now, to)
# # print (rou)
# #
# print ('time')
# print(get_total_time(rou[0]))
# print("\n Getting the directions to the first route: ")
# print(get_directions(rou[0]))

# print(x)
# get_rev_geo(x["lat"], x["lng"])
# get_rev_geo(y["lat"], y["lng"])

# lat = 40.715478
# long = -74.009266
#
# get_rev_geo(lat, long)

# print(get_total_time(rou[0]))

# get_rev_geo(lat, long)
