import json
import datetime
import requests
import pandas as pd
from dateutil import parser
import os


arrivalairports = ['MST','EIN','AMS']
departureairports = ['GRO']
fromdate = "2018-04-17"
todate = "2018-08-25"
duration = [2,3,4,5]
weekdaydeparture = [4,3]
weekdayreturn = [6,7]

    
url = "https://api.ryanair.com/farefinder/3/oneWayFares?&departureAirportIataCode={0}&arrivalAirportIataCode={1}&language=en&limit=5000&market=en-gb&offset=0&outboundDepartureDateFrom={2}&outboundDepartureDateTo={3}".format(departure,arrival,datein,dateout)
r = requests.get(url)
j = json.loads(r.content)

for fare in j['fares']:
    self.flightdict[fare['outbound']['departureDate']] ={
            'Dep_country{0}'.format(self.keyword): fare['outbound']['departureAirport']['countryName'],
            'Dep_airport{0}'.format(self.keyword): fare['outbound']['departureAirport']['name'],
            "Origin{0}".format(self.keyword) : fare['outbound']['departureAirport']['iataCode'],
            'Departure{0}'.format(self.keyword): parser.parse(fare['outbound']['departureDate']),

            'Arrival{0}'.format(self.keyword): parser.parse(fare['outbound']['arrivalDate']),
            'Dest_country{0}'.format(self.keyword): fare['outbound']['arrivalAirport']['countryName'],
            'Dest_airport{0}'.format(self.keyword): fare['outbound']['arrivalAirport']['name'],
            'Destination{0}'.format(self.keyword): fare['outbound']['arrivalAirport']['iataCode'],

        'Price{0}'.format(self.keyword) : fare['outbound']['price']['value']}

self.flightdict = {}


for date in dates:
    for i in range(0, len(self.departureairports)):
        for j in range(0, len(self.arrivalairports)):
            month = '{:02d}'.format(date.month)
            day = '{:02d}'.format(date.day)
            self.request(self.departureairports[i], self.arrivalairports[j], '{0!s}-{1!s}-{2!s}'.format(date.year,month,day), '{0!s}-{1!s}-{2!s}'.format(date.year,month,day,returnflight))
    print('Found {0} flights so far'.format(len(self.flightdict)))
if len(self.flightdict) == 0:
    print('No flights found')
else:
    df = pd.DataFrame.from_dict(self.flightdict, orient='index').sort_values(by='Price{0}'.format(self.keyword), ascending=True)


combidict = {}
for key, value in departureflight.items():
    for key2, value2 in returnflight.items():
        if value['Destination'] == value2['Origin_Return']:
            for item in duration:
                if (parser.parse(key).date() + datetime.timedelta(days=item)) == parser.parse(key2).date():
                    combidict[key + '__' + key2] = pd.concat(
                        [pd.DataFrame.from_dict(departureflight[key], orient='index'),
                            pd.DataFrame.from_dict(returnflight[key2], orient='index')]).T
                    combidict[key + '__' + key2]['Retour_price'] = value2['Price_Return'] + value['Price']
                    combidict[key + '__' + key2]['Duration_of_stay'] = value2['Arrival_Return'] - value[
                        'Arrival']
                    combidict[key + '__' + key2]['Price_per_hour'] = combidict[key + '__' + key2][
                                                                            'Retour_price'] / (((value2[
                                                                                                    'Arrival_Return'] -
                                                                                                value[
                                                                                                    'Arrival']).days) * 24) + (
                                                                                    ((value2['Arrival_Return'] -
                                                                                    value[
                                                                                        'Arrival']).seconds) / 3600)
if len(combidict) == 0:
    print('No round flight found, check your settings/dates')
else:
    df = (pd.concat(combidict.values(), ignore_index=True).sort_values('Retour_price'))
    df = df.drop(columns=['Dep_country_Return', 'Dep_airport_Return', 'Dest_country_Return','Origin_Return'])


# ----------------------------------------------------------------------------------------

 

from bs4 import BeautifulSoup
from urllib.request import urlopen
from urllib.error import HTTPError, URLError

try: #load soup
    src = urlopen('https://flights.ryanair.com/es-es/vuelos-a-londres').read()
except HTTPError as e:
    print(e)
except URLError:
    print("Server down or incorrect domain")
else:
    content = BeautifulSoup(src,'lxml') #parse

for deal in content.find_all('h1'): # find ocurrences of a certain class
    print('Oferta: ' + deal.text)