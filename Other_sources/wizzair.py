# Source: https://github.com/mixnix/cheapFlights2/tree/master/cheap_flights_pro/outer_libraries


import requests
import json
from datetime import datetime, timedelta

url = 'https://be.wizzair.com/9.16.2/Api/search/timetable'
headers = {
    "Host": "be.wizzair.com",
    "User-Agent": "Mozilla/5.0 (Windows NT 10.0; Win64; x64; rv:69.0) Gecko/20100101 Firefox/69.0",
    "Content-Type": "application/json;charset=utf-8",
    "Accept": "application/json, text/plain, */*",
    "Accept-Language": "pl,en-US;q=0.7,en;q=0.3",
    "Accept-Encoding": "gzip, deflate, br",
    "Referer": "https://wizzair.com/en-gb/flights/timetable/warsaw-chopin/vienna--",
    "Content-Length": "260",
    "Origin": "https://wizzair.com",
    "Connection": "keep-alive",
    "TE": "Trailers",
    "Pragma": "no-cache",
    "Cache-Control": "no-cache"
}


def flights_timetable(departureFromDate="2019-09-06", departureToDate="2019-10-06", targetFromDate="2019-09-30", targetToDate="2019-11-03",
                      sourceLocation="WAW", targetLocation="VIE", adultCount = 1):
    body = {
        "flightList": [
            {
                "departureStation": sourceLocation,
                "arrivalStation": targetLocation,
                "from": departureFromDate,
                "to": departureToDate
            },
            {
                "departureStation": targetLocation,
                "arrivalStation": sourceLocation,
                "from": targetFromDate,
                "to": targetToDate
            }
        ],
        "priceType": "regular",
        "adultCount": adultCount,
        "childCount": 0,
        "infantCount": 0
    }

    return requests.post(url, data=json.dumps(body), headers=headers)
    


def get_30_days_periods(departure_from_date, departure_to_date, returning_from_date, returning_to_date):

    departure_from_date = datetime.strptime(departure_from_date, '%Y-%m-%d')
    departure_to_date = datetime.strptime(departure_to_date, '%Y-%m-%d')
    returning_from_date = datetime.strptime(returning_from_date, '%Y-%m-%d')
    returning_to_date = datetime.strptime(returning_to_date, '%Y-%m-%d')

    departures_list = []
    while departure_from_date < departure_to_date:
        departures_list.append((departure_from_date.strftime("%Y-%m-%d"), (departure_from_date + timedelta(days=30)).strftime("%Y-%m-%d")))
        departure_from_date += timedelta(days=31)

    returns_list = []
    while returning_from_date < returning_to_date:
        returns_list.append((returning_from_date.strftime("%Y-%m-%d"), (returning_from_date + timedelta(days=30)).strftime("%Y-%m-%d")))
        returning_from_date += timedelta(days=31)

    # fuse them here and not before because one of them might be longer
    length = len(departures_list) if len(departures_list) > len(returns_list) else len(returns_list)

    dates_list = []
    i = 0
    j = 0
    for aa in range(length):
        dates_list.append((departures_list[i][0], departures_list[i][1], returns_list[j][0], returns_list[j][1]))
        if i < len(departures_list)-1:
            i += 1
        if j < len(departures_list)-1:
            j += 1

    return dates_list


# zwracac loty dla dowolnej dlugosci odcinka czasu i obsluguje blad ale tylko dla jednego miasta
def get_flights(departure_from_date, departure_to_date, target_from_date, target_to_date,
                source_location="WAW", target_location="VIE", adult_count=1):
    time_periods_table = get_30_days_periods(departure_from_date, departure_to_date, target_from_date, target_to_date)

    flights_table = {'outboundFlights':[], 'returnFlights':[]}
    for periods in time_periods_table:
        # dla kazdego takiego trzeba wykonac request i zaapendowac do tablicy
        # podczas wykonywania requestu trzeba sprawdzic czy exception nie poleci i wydrukowac
        while True:
            try:
                r = flights_timetable(departureFromDate=periods[0],
                                        departureToDate=periods[1],
                                        targetFromDate=periods[2],
                                        targetToDate=periods[3],
                                        sourceLocation=source_location,
                                        targetLocation=target_location,
                                        adultCount=adult_count)
                flights_table['outboundFlights'] += json.loads(r.content)['outboundFlights']
                flights_table['returnFlights'] += json.loads(r.content)['returnFlights']
                break
            except Exception as e:
                print(r.content)
                continue
    return flights_table


def all_flights_for_given_city(all_possible_target_cities, departure_from_date,
                               departure_to_date, target_from_date, target_to_date,
                               from_city, adult_count):
    all_flights = {}
    for city in all_possible_target_cities:
        flights_table = get_flights(departure_from_date=departure_from_date, departure_to_date=departure_to_date,
                                    target_from_date=target_from_date, target_to_date=target_to_date,
                                    source_location=from_city, target_location=city, adult_count= adult_count)
        all_flights[city] = flights_table

    return all_flights


# filtrujej ze wszystkich lotow tylko te najtansze
def get_cheap_flights_for_given_city(departureFromDate="2019-09-13", departureToDate="2019-10-13", targetFromDate="2019-09-30", targetToDate="2019-11-03",
                                     from_city="WAW", adultCount = 1):
    possibleLocations = ['VIE', 'CRL', 'BOJ', 'SPU', 'LCA', 'BLL', 'TKU', 'BOD', 'GNB', 'LYS', 'NCE', 'KUT', 'CFU',
                         'BUD', 'KEF', 'ETM', 'TLV', 'AHO', 'BRI', 'BLQ', 'CTA', 'SUF', 'BGY', 'NAP', 'FCO', 'TRN',
                         'VRN', 'MLA', 'TGD', 'RAK', 'EIN', 'BGO', 'TRF', 'LIS', 'OPO', 'OTP', 'ALC', 'BCN', 'MAD',
                         'TFS', 'GOT', 'MMX', 'NYO', 'BSL', 'IEV', 'KBP', 'BHX', 'DSA', 'EDI', 'LPL', 'LTN']
    # possibleLocations = ['VIE', 'CRL']

    all_flights = all_flights_for_given_city(possibleLocations, departure_from_date=departureFromDate, departure_to_date=departureToDate,
                                             target_from_date=targetFromDate, target_to_date=targetToDate,
                                             from_city=from_city, adult_count=adultCount)

    cheap_flights = {}
    for key, flights_to_city in all_flights.items():

        temp_cheapest_outbound = {'priceType': 'price', 'price': {'amount': 9000000}}
        temp_cheapest_return = {'priceType': 'price', 'price': {'amount': 9000000}}
        for flight in flights_to_city['outboundFlights']:
            if flight['priceType'] == 'checkPrice':
                continue
            elif flight['price']['amount'] < temp_cheapest_outbound['price']['amount']:
                temp_cheapest_outbound = flight

        for flight in flights_to_city['returnFlights']:
            if flight['priceType'] == 'checkPrice':
                continue
            elif flight['price']['amount'] < temp_cheapest_return['price']['amount']:
                temp_cheapest_return = flight

        cheap_flights[key] = (temp_cheapest_outbound, temp_cheapest_return)
    cheap_flights_short = [(key, flight[0]['price']['amount'] + flight[1]['price']['amount']) for key, flight in
                           cheap_flights.items()]
    cheap_flights_short_sorted = sorted(cheap_flights_short, key=lambda x: x[1])
    return cheap_flights, cheap_flights_short_sorted


# -----------------------------------------------------------------------------------------------------------------------------
# Source: https://github.com/richpeaua/wizzair_scraper/blob/master/wizz_scrape.py

import os
import requests
import pymysql
from decimal import Decimal
import datetime
import csv
import json
import re
import pdb
import random

DB_HOST = '127.0.0.1'
DB_USER = 'root'
DB_PASS = ''
DB_NAME = 'wizzair'

DB_FILENAME = 'wizzair_allflights_allfares_kwi_cze18.db'

proxy_list = ['193.182.165.43:1212', '185.158.106.2:1212', '77.237.228.188:1212', '185.158.107.85:1212', '77.237.228.205:1212', '185.143.229.57:1212', '185.158.107.55:1212', '31.187.66.160:1212', '77.237.228.140:1212', '192.36.168.89:1212']
random_proxy = random.choice(proxy_list)
PROXIES = {'http': random_proxy}

class WizzairScraper:
    connection = 0
    def __init__(self):
        self.create_db()
        self.read_all_wizz_flights()

    def read_all_wizz_flights(self):
        script_dir = os.path.dirname(os.path.abspath(__file__))
        all_wiz_flights_data = os.path.join(script_dir, 'wizz_flights_all.csv')
        self.flights_data = []
        f = open(all_wiz_flights_data, 'rt')
        reader = csv.reader(f)
        next(reader, None)
        for row in reader:
            self.flights_data.append((row[0],row[1],))

    def create_db(self):
        self.dbconn = pymysql.connect(DB_HOST, DB_USER, DB_PASS, DB_NAME)
        self.dbcur = self.dbconn.cursor()
        self.dbcur.execute('create table if not exists wizzair_flights_14d(retrievaldate date, from_airp varchar(5), to_airp  varchar(5), flightdate date, flighttime varchar(10), price numeric(7,2), currency varchar(10), bundle varchar(10))' )
        self.dbconn.commit()

    def scrape_data(self):
        request_url = 'https://wizzair.com/static/metadata.json'
        #request_url = 'https://be.wizzair.com/9.0.1/Api/search/search'
        url_request = requests.get(request_url, proxies=PROXIES, timeout=20)
        #url_request_json = url_request.json()
        #url = url_request_json['apiUrl'] + str('/search/search')
        url = 'https://be.wizzair.com/9.0.1/Api/search/search'
        for from_airp, to_airp in self.flights_data:
            checkdate = datetime.date.today() + datetime.timedelta(days=14)
            flights_scraped = self.scrape_fares(from_airp, to_airp, checkdate, url)
            WizzairScraper.connection += 1
            print ("connection ", WizzairScraper.connection)
            if flights_scraped == 0:
                print("No flight data available")

    def scrape_fares(self, from_airp, to_airp, checkdate, url):
        headers = {
        	'Content-Type': 'application/json',
        }

        data = """{
        	"isFlightChange":false,
        	"isSeniorOrStudent":false,
        	"flightList":[{
        			"departureStation":"%s",
        			"arrivalStation":"%s",
        			"departureDate":"%02d-%02d-%02d"
        			}
        	],
        	"adultCount":1,
        	"childCount":0,
        	"infantCount":0,
        	"wdc":false,
        	"rescueFareCode":""}""" % (from_airp, to_airp,checkdate.year, checkdate.month, checkdate.day)
        
        print(str(from_airp) + '->' + str(to_airp))
        
        try:
            r = requests.post(url, data=data, headers=headers, proxies=PROXIES, timeout=20)
            if r.status_code == 200:
                flight_data = r.json()
                total_flights = len(flight_data['outboundFlights'])
                if total_flights != 0:
                    arrivalDateTime = flight_data['outboundFlights'][0]['arrivalDateTime']
                    departureDateTime = flight_data['outboundFlights'][0]['departureDateTime'] 
                    match = re.search('\d{4}-\d{2}-\d{2}', departureDateTime)
                    flight_date = datetime.datetime.strptime(match.group(), '%Y-%m-%d').date()
                    flight_time = departureDateTime[-8:]
                    total_fares = len(flight_data['outboundFlights'][0]['fares'])
                    for i in range(0,total_fares):
                        bundle = flight_data['outboundFlights'][0]['fares'][i]['bundle']
                        print(str(from_airp) + '->' + str(to_airp) + '. Flight Time and date: ' + str(departureDateTime))
                        currencyCode = flight_data['outboundFlights'][0]['fares'][i]['fullBasePrice']['currencyCode']
                        price = flight_data['outboundFlights'][0]['fares'][i]['fullBasePrice']['amount']
                        
                        self.dbcur.execute('insert into wizzair_flights_14d(retrievaldate,from_airp,to_airp,flightdate, flighttime, price, currency, bundle) values(%s,%s,%s,%s,%s,%s,%s,%s)',
                                                   (datetime.date.today(), from_airp, to_airp, flight_date, flight_time, Decimal(price), currencyCode, bundle,))
                        self.dbconn.commit()
                    return total_fares;
                else:
                    return 0;
            else:
                return 0;
        except requests.exceptions.Timeout:
            print('No response from server. Request timed out. Retrying now..')
            r = requests.post(url, data=data, headers=headers, proxies=PROXIES, timeout=20)
            if r.status_code == 200:
                flight_data = r.json()
                total_flights = len(flight_data['outboundFlights'])
                if total_flights != 0:
                    arrivalDateTime = flight_data['outboundFlights'][0]['arrivalDateTime']
                    departureDateTime = flight_data['outboundFlights'][0]['departureDateTime'] 
                    match = re.search('\d{4}-\d{2}-\d{2}', departureDateTime)
                    flight_date = datetime.datetime.strptime(match.group(), '%Y-%m-%d').date()
                    flight_time = departureDateTime[-8:]
                    total_fares = len(flight_data['outboundFlights'][0]['fares'])
                    for i in range(0,total_fares):
                        bundle = flight_data['outboundFlights'][0]['fares'][i]['bundle']
                        WizzairScraper.connection += 1
                        print ("connection ", WizzairScraper.connection)
                        print(str(from_airp) + '->' + str(to_airp) + '. Flight Time and date: ' + str(departureDateTime))
                        currencyCode = flight_data['outboundFlights'][0]['fares'][i]['fullBasePrice']['currencyCode']
                        price = flight_data['outboundFlights'][0]['fares'][i]['fullBasePrice']['amount']
                        
                        self.dbcur.execute('insert into wizzair_flights_14d(retrievaldate,from_airp,to_airp,flightdate, flighttime, price, currency, bundle) values(%s,%s,%s,%s,%s,%s,%s,%s)',
                                                   (datetime.date.today(), from_airp, to_airp, flight_date, flight_time, Decimal(price), currencyCode, bundle,))
                        self.dbconn.commit()
                    return total_fares;
                else:
                    return 0;
            else:
                return 0;

if __name__ == '__main__':
    wizzairscraper = WizzairScraper()
    wizzairscraper.scrape_data()

