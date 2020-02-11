
# Source: https://github.com/leonj3813/Kayak

'''
Program to scrape the prices from kayak.com to find a weekend ...
... when round trip travel from State College, PA to Atlanta, GA will be cheapest.
Scans the next 10 weekends for prices.
Kayak.com does not like scraping their website ...
... and too much accessing will cause them to flag you as a bot. 
Must use a headless browser to render the javascript.
'''

from bs4 import BeautifulSoup
from selenium import webdriver
from time import sleep
import os
import string
import time
import datetime
from dateutil import rrule

def filter_results(soup):
    """Given a kayak soup, returns the list [price, 1st Departure time, 2nd Departure time]"""
    output = []
    for each in soup.find_all(class_ = "flightresult"):
        # find the price and print it out
        price = each.find(class_ = "results_price")
        flight = [price.string.strip()]
        
        # find the first leg of the trip
        leg1 = each.find(class_= "singleleg0")
        Departure = string.replace(string.replace(leg1.find(class_ = "flightTimeDeparture").string.strip(),'p', 'PM'),'a','AM')
        flight.append(time.strptime(Departure, "%I:%M%p"))
                
        # find the second leg of the trip
        leg2 = each.find(class_ = "singleleg1")
        Departure = string.replace(string.replace(leg2.find(class_ = "flightTimeDeparture").string.strip(),'p', 'PM'),'a','AM')
        flight.append(time.strptime(Departure, "%I:%M%p"))

        # append price and times to return array
        output.append(flight)
    return output

def return_URLs():
    """Generates the URLs for finding flights on the weekend on kayak"""
    base_url = "http://www.kayak.com/flights/SCE-ATL/"
    today = datetime.date.today()
    dates = list(rrule.rrule(rrule.WEEKLY, count=1, byweekday=rrule.FR(1),
        dtstart=today))
    
    date_format = "%Y-%m-%d"
    URLs = []
    for date in dates:
        range = date.strftime(date_format) + "/" + (date + datetime.timedelta(days=2)).strftime(date_format)
        URLs.append(base_url + range)
    return URLs

next_urls = return_URLs()

for url in next_urls:
    # use phantomjs headless browser to fetch webpage
    driver = webdriver.PhantomJS("phantomjs")
    driver.get(url)
   #driver.delete_all_cookies()

    soup = BeautifulSoup(driver.page_source)
    print url
    results = helper.filter_results(soup)

    for item in results:
        Departure1 = item[1]
        latest_departure1 = time.strptime("13:30", "%H:%M")
        Departure2 = item[2]
        latest_departure2 = time.strptime("15:00", "%H:%M")  

        #if (Departure1 > latest_departure1) and (Departure2 > latest_departure2):
        print url
        print item[0] + ", " + time.strftime("%H:%M", Departure1) + ", " + time.strftime("%H:%M", Departure2)

    driver.close()


# -----------------------------------------------------
# Source: https://github.com/jkol36/flight-scraper/blob/master/main.py


import os
from time import sleep, strftime
from random import randint
import pandas as pd
from selenium import webdriver
from selenium.webdriver.common.keys import Keys
import smtplib
from email.mime.multipart import MIMEMultipart

chromedriver = "/Users/Jon/Downloads/chromedriver"
os.environ["webdriver.chrome.driver"] = chromedriver
driver = webdriver.Chrome(chromedriver)

def start_kayak(city_from, city_to,date_start,date_end):
	kayak = ('https://www.kayak.com/flights/' + city_from + '-' + city_to +
             '/' + date_start + '-flexible/' + date_end + '-flexible?sort=bestflight_a')
	driver.get(kayak)


start_kayak("phl", "mia", "2019-05-05", "2019-05-07")


# --------------------------------------------------------------------------------------
# Source: https://github.com/lordmalcher/FlightPrices/blob/master/scraper.py

from bs4 import BeautifulSoup
import pandas as pd
import re
import numpy as np
from datetime import datetime
import time
import requests
from user_agent import generate_user_agent


def get_page(origin, destination, date):
    url = f'https://www.kayak.pl/flights/{origin}-{destination}/{date}?sort=bestflight_a&fs=stops=0;providers=-ONLY_DIRECT'
    headers = {
        'User-Agent': generate_user_agent(device_type="desktop", os=('mac', 'linux', 'win'))
    }

    print(f'{url}\n{headers}')

    try:
        r = requests.get(url, headers=headers)
    except requests.exceptions.ProxyError:
        return 'FAIL'

    soup = BeautifulSoup(r.text, 'lxml')
    if soup.find_all('p')[0].getText() == "Potwierdź, że jesteś użytkownikiem KAYAK.":
        print('BOT DETECTED')
        return 'fail'

    if soup.find_all('p')[0].getText() == "Please confirm that you are a real KAYAK user.":
        print("Kayak thinks I'm a bot, which I am ... so let's wait a bit and try again")
        return 'fail'

    with open(f'requests/request-{origin}-{destination}-{date}.html', 'w', encoding='utf-8') as f:
        f.write(r.text)

    return 'success'


def scrape(origin, destination, date):
    r = ''
    with open(f'requests/request-{origin}-{destination}-{date}.html', 'r', encoding='utf-8') as f:
        r = f.read()
    soup = BeautifulSoup(r, 'lxml')

    prices = list()
    operators = list()
    iata_origin = list()
    iata_destination = list()
    currencies = list()

    departure_times = [departure_time.text for departure_time in
                       soup.find_all('span', attrs={'class': 'depart-time base-time'})]
    arrival_times = [arrival_time.text for arrival_time in
                     soup.find_all('span', attrs={'class': 'arrival-time base-time'})]

    regex = re.compile('Common-Booking-MultiBookProvider (.*)multi-row Theme-featured-large(.*)')
    for price in soup.find_all('div', attrs={'class': regex}):
        price = price.find('span', attrs={'class': 'price option-text'}).text[1:]
        prices.append(int(price[:-4]))
        currencies.append(price[-3:-1])

    for operator in soup.find_all('div', attrs={'class': 'section times'}):
        operators.append(operator.find('div', attrs={'class': 'bottom'}).text)

    for iata in soup.find_all('div', attrs={'class': 'section duration'}):
        iata_origin.append(iata.find('div', attrs={'class': 'bottom'}).find('span').text)

    for iata in soup.find_all('div', attrs={'class': 'section duration'}):
        iata_destination.append(iata.find('div', attrs={'class': 'bottom'}).find_all('span')[2].text)

    data = {
        'origin': iata_origin,
        'destination': iata_destination,
        'date': date,
        'departure_time': departure_times,
        'arrival_time': arrival_times,
        'operator': operators,
        'currency': currencies,
        'price': prices
    }

    df = pd.DataFrame(data)

    return df