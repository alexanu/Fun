
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