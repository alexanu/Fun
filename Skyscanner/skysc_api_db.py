# Source: https://github.com/tommybox3377/FlightSpider

import requests
import re
import TravelVars as tv
import json
import Creds
import mysql.connector


# travel_origin = ["EWR","ABE","PHL"]
# travel_destination = ["YYC","YYT","YDF","ANC"]
# departure_dates = ["2020-09-10","2020-10-11"]
# return_dates = ["2020-09-12","2020-10-13"]
# adults = 2
# max_stops = 2
# max_duration = 720

tv = {
    "travel_origin": [],
    "travel_destination": [],
    "departure_dates": [],
    "return_dates": [],
    "adults": 1,
    "max_stops": 5,
    "max_duration": 1440
}



mydb = mysql.connector.connect(
    host=Creds.host,
    user=Creds.user,
    password=Creds.password,
    database=Creds.database
)

my_cursor = mydb.cursor()


def get_skyscanner_search_vars(id):
    travel_vars = {
        "travel_origin": [],
        "travel_destination": [],
        "departure_dates": [],
        "return_dates": [],
        "adults": 1,
        "max_stops": 5,
        "max_duration": 720
    }
    my_cursor.execute(f"SELECT * FROM inq_req WHERE id = {id}")
    db_vars = my_cursor.fetchone()

    travel_vars["travel_origin"] = json.loads(db_vars[2])
    travel_vars["travel_destination"] = json.loads(db_vars[3])
    travel_vars["departure_dates"] = json.loads(db_vars[4])
    travel_vars["return_dates"] = json.loads(db_vars[5])
    travel_vars["adults"] = db_vars[6]
    travel_vars["max_stops"] = db_vars[7]
    travel_vars["max_duration"] = db_vars[8]

    return travel_vars


def get_email(id):
    my_cursor.execute(f"SELECT email FROM inq_req WHERE ID = {id}")
    return my_cursor.fetchone()



def add_test_data_to_db(id):
    l = ["2020-09-12"]
    jl = json.dumps(l)
    my_cursor.execute(f"update inq_req SET return_dates = '{jl}' WHERE id = {id}")
    mydb.commit()



# #Notes:
# 1)get API key
# 2)get token  https://skyscanner.github.io/slate/#authentication
#  note https://skyscanner.github.io/slate/#getting-started for quotes vs routes vs dates vs grid
#       see what you get back with each. probably a combination for initial price history, then shoot live prices at time_check interval
# note: for dest/origin places : https://skyscanner.github.io/slate/#places
# 3)create live price session
# NOTE: LIVE Flight prices will only retunr a session that you have to poll
#        checkk for these first https://skyscanner.github.io/slate/#carhire-home-page-supported-parameters-schema
# 4)poll result
#       use a  paging and payload system cause we are really only looking for the cheapest flights
# 5) look into booking details
# Add no-follow attribut to deeplink??
# !!!Please do not cache the deeplinks as they are only valid while your session is active. Once the session has timed out you will need to create a new session and refresh all the results and deeplink urls.
#
#
#

# keys = []
# prices = []


def create_session(rtn, origin, destination, depart, adults):
    url = "https://skyscanner-skyscanner-flight-search-v1.p.rapidapi.com/apiservices/pricing/v1.0"
    payload = f"inboundDate={rtn}&country=US&currency=USD&locale=en-US&originPlace={origin}-sky&destinationPlace={destination}-sky&outboundDate={depart}&adults={adults}"
    headers = {
        'x-rapidapi-host': "skyscanner-skyscanner-flight-search-v1.p.rapidapi.com",
        'x-rapidapi-key': Creds.xrapid_key,
        'content-type': "application/x-www-form-urlencoded"
    }

    response = requests.request("POST", url, data=payload, headers=headers)
    return response.headers["Location"]


# def make_all_combo_sessions(tv):
#     for origin in tv.travel_origin:
#         for destination in tv.travel_destination:
#             for depart in tv.departure_dates:
#                 for rtn in tv.return_dates:
#                     key = re.search(r"v1\.0/(.*)", create_session(rtn, origin, destination, depart))
#                     keys.append(key[1])


def poll_session(key, max_dur, max_stops):
    url = "https://skyscanner-skyscanner-flight-search-v1.p.rapidapi.com/apiservices/pricing/uk2/v1.0/" + key

    querystring = {
        "sortType": "price",
        "sortOrder": "asc",
        "duration": str(max_dur),
        "stops": str(max_stops),
        "pageIndex": "0",
        # TODO change/check this to 1 or 2 if we are just grabbing to lowest one
        "pageSize": "10"
    }

    headers = {
        'x-rapidapi-host': "skyscanner-skyscanner-flight-search-v1.p.rapidapi.com",
        'x-rapidapi-key': Creds.xrapid_key
    }

    response = requests.request("GET", url, headers=headers, params=querystring)
    return response.json()


def get_best_price(tv):
    price = 0
    key = create_session(tv["return_dates"][0], tv["travel_origin"][0], tv["travel_destination"][0],
                         tv["departure_dates"][0], tv["adults"])
    just_key = re.search(r"v1\.0/(.*)", key)[1]

    te = "489a48ad-5cae-43d5-b986-0e9946e0ef1e"
    # print(poll_session(just_key, tv["max_duration"], tv["max_stops"]))
    poll = poll_session(te, tv["max_duration"], tv["max_stops"])
    for key in poll:
        print(type(key))
    return price




    # try:
    #     prices.append([
    #         response.json()["Itineraries"][0]["PricingOptions"][0]["Price"],
    #         response.json()["Itineraries"][0]["PricingOptions"][0]["DeeplinkUrl"]
    #     ])
    # except:
    #     prices.append([
    #         0, "Error for key:" + key
    #     ])


# vars = {
# 'travel_origin': ['EWR'],
# 'travel_destination': ['YYC'],
# 'departure_dates': ['2020-09-10'],
#  'return_dates': ['2020-09-12'],
#  'adults': 1,
#  'max_stops': 2,
#  'max_duration': 720}


# def create_session(rtn, origin, destination, depart):
#     url = "https://skyscanner-skyscanner-flight-search-v1.p.rapidapi.com/apiservices/pricing/v1.0"
#
#     payload = f"inboundDate={rtn}&country=US&currency=USD&locale=en-US&originPlace={origin}-sky&destinationPlace={destination}-sky&outboundDate={depart}&adults={tv.adults}"
#     headers = {
#         'x-rapidapi-host': "skyscanner-skyscanner-flight-search-v1.p.rapidapi.com",
#         'x-rapidapi-key': Creds.xrapid_key,
#         'content-type': "application/x-www-form-urlencoded"
#     }
#
#     response = requests.request("POST", url, data=payload, headers=headers)
#     print(response)
#     return response.headers["Location"]



# make_all_combo_sessions()
# for key in keys:
#     poll_session(key)
#
# for price in prices:
#     print(price)


MySQL.my_cursor.execute("SELECT id FROM inq_req")
db_id = MySQL.my_cursor.fetchone()
while db_id:
    id = db_id[0]
    travel_vars = MySQL.get_skyscanner_search_vars(id)
    best_price = SkyScannerAPI.get_best_price(travel_vars)
    print(best_price)
    db_id = MySQL.my_cursor.fetchone()
