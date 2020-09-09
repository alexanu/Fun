
# Source: https://github.com/JanAdamiak/Flights-prices-tracker/blob/master/flights.py

import requests
import os, sys, json
import pandas as pd

def merge_dicts(x, y):
  z = x.copy()
  z.update(y)
  return z

def getCarrier(ids, carriers):
  carriers_found = ""
  for id in ids:
    for carrier in carriers:
      if carrier["CarrierId"] == id:
        carriers_found = carriers_found + " " + carrier["Name"]
  return carriers_found


rapidapi_host = 'skyscanner-skyscanner-flight-search-v1.p.rapidapi.com'
rapidapi_key = '7a3621970amsh9275d1c7c9ed661p15c96ajsnbc45c95d106c'


headers={'X-RapidAPI-Host': rapidapi_host,'X-RapidAPI-Key': rapidapi_key}
response = requests.get('https://skyscanner-skyscanner-flight-search-v1.p.rapidapi.com/apiservices/reference/v1.0/countries/en-GB', headers=headers)
response = json.loads(response.text)
data = pd.json_normalize(pd.DataFrame(response)['Countries'])
data.to_csv("SKYSC_COUNTRY_CODES.csv", index=False)

'''
'PlaceId': 'MUC-sky',
'PlaceName': 'Munich',
'CountryId': 'DE-sky',
'RegionId': '',
'CityId': 'MUNI-sky',
'CountryName': 'Germany'},
'''


country_code = 'DE'
origin_id = 'MUC-sky'
destination_id = 'HNL'
trip_duration_in_dys=10
outbound_date = '2021-01-30'
inboundDate = (datetime.strptime(outbound_date, '%Y-%m-%d') + timedelta(days=trip_duration_in_dys)).strftime('%Y-%m-%d')

apicall = 'https://skyscanner-skyscanner-flight-search-v1.p.rapidapi.com/apiservices/pricing/v1.0'
headers = {'X-RapidAPI-Host': rapidapi_host,'X-RapidAPI-Key': rapidapi_key,'Content-Type': 'application/x-www-form-urlencoded'}
params={
        'cabinClass': 'economy',
        'children': 1,
        'infants': 0,
        'country': country_code,
        'currency': 'EUR',
        'locale': 'en-US',
        'originPlace': origin_id,
        'destinationPlace': destination_id,
        'outboundDate': outbound_date,
        'adults': 2
        }

        
r = requests.post(apicall, headers=headers, data=params)
session_key = r.headers['Location'].split('/')[-1]
apicall = 'https://skyscanner-skyscanner-flight-search-v1.p.rapidapi.com/apiservices/pricing/uk2/v1.0/{}?sortType=price&pageIndex=0&pageSize=10'.format(session_key)
headers = {'X-RapidAPI-Host': rapidapi_host,'X-RapidAPI-Key': rapidapi_key}
r = requests.get(apicall, headers=headers)
body = json.loads(r.text)
itineraries = body['Itineraries']
results = []
for i in range(len(itineraries)):
for j in range(len(itineraries[i]['PricingOptions'])):
url = itineraries[i]['PricingOptions'][j]['DeeplinkUrl']
price = itineraries[i]['PricingOptions'][j]['Price']
results.append((price, url))
return results


##########################################################################

  required_params = {
    "country": "DE",
    "currency": "EUR",
    "locale": "de-DE",
    "originPlace": "MUC-sky",
    "destinationPlace": "HNL-sky",
    "outboundDate": "2021-02-01",
    "inboundDate": "2021-02-10",
  }
  # Optional parameters
  opt_params = {
  }

  
origin = "MUC"
destinations = ["SFO","HNL","KBP"]
outboundDate = "2021-02-01"
inboundDate  = "2021-02-10"

for destination in destinations:
    # Search Parameters
    # required parameters
    required_params = {
    "country": "DE",
    "currency": "EUR",
    "locale": "de-DE",
    "originPlace": origin,
    "destinationPlace": destination,
    "outboundDate": outboundDate,
    "inboundDate": inboundDate,
    }

    source = "https://skyscanner-skyscanner-flight-search-v1.p.rapidapi.com"\
              + "/apiservices/browsequotes/v1.0"\
              + "/" + required_params["country"]\
              + "/" + required_params["currency"]\
              + "/" + required_params["locale"]\
              + "/" + required_params["originPlace"]\
              + "/" + required_params["destinationPlace"]\
              + "/" + required_params["outboundDate"]\
              + "/" + required_params["inboundDate"]
    response = requests.get(source,
                            headers={
                              "X-RapidAPI-Host": "skyscanner-skyscanner-flight-search-v1.p.rapidapi.com",
                              "X-RapidAPI-Key": "7a3621970amsh9275d1c7c9ed661p15c96ajsnbc45c95d106c",
                              "useQueryString": 'true'
                            }
                            )
    print("")
    print("From " + required_params["originPlace"] + " to " + required_params["destinationPlace"] + ".")
    print("From " + required_params["outboundDate"] + " to " + required_params["inboundDate"] + ".")

    # Cheapest quotes:
    print("\nCheapest quotes ("+ response.body["Currencies"][0]["Code"] +"):\n")
    i = 1
    for quote in response.body["Quotes"]:
        if quote["Direct"]: direct_str = ", direct"
        else: direct_str = ", not direct"
        print("\t".expandtabs(2) + str(i) + ") " + "MinPrice: " + str(quote["MinPrice"]) + direct_str)
        print("\tOutbound:".expandtabs(6))
        print("\tDeparture: ".expandtabs(8) + quote["OutboundLeg"]["DepartureDate"])
        print("\tCarrier(s): ".expandtabs(8) + getCarrier(quote["OutboundLeg"]["CarrierIds"], response.body["Carriers"]))
        print("\tInbound:".expandtabs(6))
        print("\tDeparture: ".expandtabs(8) + quote["InboundLeg"]["DepartureDate"])
        print("\tCarrier(s): ".expandtabs(8) + getCarrier(quote["InboundLeg"]["CarrierIds"], response.body["Carriers"]))
        print("")

      i += 1


#


source ='https://skyscanner-skyscanner-flight-search-v1.p.rapidapi.com/apiservices/browsequotes/v1.0/DE/EUR/en-DE/MUC-sky/HNL-sky/2021-02-01/2021-03-01'
response = requests.get(source,
                            headers={
                              "X-RapidAPI-Host": "skyscanner-skyscanner-flight-search-v1.p.rapidapi.com",
                              "X-RapidAPI-Key": "7a3621970amsh9275d1c7c9ed661p15c96ajsnbc45c95d106c",
                              "useQueryString": 'true'
                            }
                            )
response = json.loads(response.text)
data = pd.json_normalize(pd.DataFrame(response)['Quotes'])
pd.json_normalize(response)


import requests

url = "https://skyscanner-skyscanner-flight-search-v1.p.rapidapi.com/apiservices/browsequotes/v1.0/DE/EUR/en-DE/MUC-sky/HNL-sky/2021-02-01"

querystring = {"inboundpartialdate":"2021-02-21"}

headers = {
    'x-rapidapi-host': "skyscanner-skyscanner-flight-search-v1.p.rapidapi.com",
    'x-rapidapi-key': "7a3621970amsh9275d1c7c9ed661p15c96ajsnbc45c95d106c"
    }

response = requests.request("GET", url, headers=headers, params=querystring)

print(response.text)
