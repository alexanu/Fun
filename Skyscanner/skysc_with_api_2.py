import requests
import os, sys, json
from datetime import date, timedelta, datetime


ENDPOINT_PREFIX = "https://skyscanner-skyscanner-flight-search-v1.p.rapidapi.com/apiservices/"
TAG = "Return \\ Depart"
END_TAG = " | "
CELL_LENGTH = int(len(TAG))

init_market = "US"
init_from = "SFO"
init_to = "JFK"
init_connect = "Y"
init_currency = "USD"
init_depart = (date.today() + timedelta(days=7)).strftime('%Y-%m-%d')
init_return = (date.today() + timedelta(days=11)).strftime('%Y-%m-%d')

profile_dict = {
    "API_KEY": API_KEY,
    "init_market": init_market,
    "init_from": init_from, 
    "init_to": init_to,
    "init_connect": init_connect,
    "init_currency": init_currency,
    "init_depart": init_depart,
    "init_return": init_return,
  }

market= profile_dict['init_market']
place_from = profile_dict['init_from']
place_to = profile_dict['init_to'] 
connect = profile_dict['init_connect']
currency = profile_dict['init_currency']
date_depart = profile_dict['init_depart']
date_return = profile_dict['init_return']



def handleAPIException(responseText, apiname):
      print(json.dumps(json.loads(responseText), indent=3, sort_keys=True))
      sys.exit(f"API exception on [{apiname}]")

def getIataCodeByString(place_string, market, currency, headers):
    url = ENDPOINT_PREFIX+f"autosuggest/v1.0/{market}/{currency}/en-US/"
    querystring = {"query":place_string}
    response = requests.request("GET", url, headers=headers, params=querystring)
    place_json = json.loads(response.text)
    for place in place_json["Places"]:
        if len(place['PlaceId']) == 7:
            Place.upsert({'search_string':place_string, 'iata':place['PlaceId'][:3], 'name':place['PlaceName'], 'country':place['CountryName']}, Query().api_key.exists())
            iata_code = place['PlaceId'][:3]
            break
    return iata_code

def getCheapQuote(market, currency, place_from, place_to, date_depart, date_return, check_place):    
    url = ENDPOINT_PREFIX+f"browsequotes/v1.0/{market}/{currency}/en-US/{place_from}/{place_to}/{date_depart}/{date_return}"
    response = requests.request("GET", url, headers=headers)
    quotes_json = json.loads(response.text)
    min_price_low = None
    carrier_names = []
    is_direct = "N/A"
    for quote in quotes_json["Quotes"]:
        direct_flight = quote['Direct']
        if (connect==False and direct_flight==False): continue
        min_price_this = quote['MinPrice']     
        if (min_price_low == None or min_price_this < min_price_low):  
            min_price_low = min_price_this
            is_direct = direct_flight
            carrier_id_outbound = quote['OutboundLeg']['CarrierIds']
            carrier_id_inbound = quote['InboundLeg']['CarrierIds']
            carrier_ids = set(carrier_id_outbound + carrier_id_inbound)

    if min_price_low != None: 
        for carrier in quotes_json["Carriers"]:
          carrier_id = carrier['CarrierId']
          if carrier_id in carrier_ids:
            carrier_name = carrier['Name']
            carrier_names.append(carrier_name)
            if len(carrier_names) == len(carrier_ids): break
        if (check_place):    
          for place in quotes_json["Places"]:     
            iata_code = place['IataCode']
            if (iata_code == place_from): 
              place_from = f"{place_from} - {place['Name']}, {place['CityName']}, {place['CountryName']}"
            elif (iata_code == place_to): 
              place_to = f"{place_to} - {place['Name']}, {place['CityName']}, {place['CountryName']}"

    cheapquote_dict = {
      "price": min_price_low,
      "carriers": carrier_names,
      "is_direct": is_direct,
      "place_from": place_from, 
      "place_to": place_to
    }         
    return cheapquote_dict

headers = {
    'x-rapidapi-host': "skyscanner-skyscanner-flight-search-v1.p.rapidapi.com",
    'x-rapidapi-key': profile_dict["API_KEY"]
    }


place_from = getIataCodeByString(place_from, market, currency, headers) if (len(place_from) > 3) else place_from  
place_to = getIataCodeByString(place_to, market, currency, headers) if (len(place_to) > 3) else place_to  

selected_cheapquote_dict = getCheapQuote(market, currency, place_from, place_to, date_depart, date_return, True)

dates_depart = []
dates_return = []
selected_date_depart = date_depart
selected_date_return = date_return
dates_depart.append(date_depart)
dates_return.append(date_return)


