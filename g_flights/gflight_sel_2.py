# Source: https://github.com/sammccauley117/cheap-flight-bot/tree/master/index
# Nice csv destination table:


import csv

class Destination:
    def __init__(self, dest, tripLen, city, country):
        self.dest = dest
        self.tripLen = tripLen
        self.city = city
        self.country = country


# Parse CSV and return a list
def openCSV(path):
    with open(path) as filename:
        return list(csv.reader(filter(lambda row: row[0]!='#', filename)))

# File struc:
#     # Destination Code, Trip Length, City, Country
#     #
#     #####################################################
#     #                   Europe
#     #####################################################
#     AMS,10,Amsterdam,Netherlands
#     ATH,10,Athens,Greece
#     BCN,10,Barcelona,Spain
    
    
    
# Takes a list of destinations and turns them into a list of Destination objects
def destListToObject(list):
    toReturn = []
    for item in list:
        toReturn.append(Destination(item[0],int(item[1]),item[2],item[3]))
    return toReturn
    

import flightBotKeys as keys
import time, datetime, schedule, os, sys, locale, timeit
from selenium import webdriver
from selenium.webdriver.firefox.options import Options
from selenium.webdriver.common.action_chains import ActionChains
from selenium.webdriver.common.keys import Keys
from selenium.webdriver.common.by import By
from selenium.webdriver.support.ui import WebDriverWait
from selenium.webdriver.support import expected_conditions as EC

class Flight:
    def __init__(self, dep='', dest='', price=10000000, avg=1, logDate=datetime.date.today(),
        depDate=datetime.date.today(), retDate=datetime.date.today(), percentage=-1.00, tweeted=False):
        self.dep = dep         # (String) departing airport
        self.dest = dest       # (String) destination airport
        self.price = price     # (int) price
        self.avg = avg         # (int) average price
        self.logDate = logDate # (date) date at which this was logged
        self.depDate = depDate # (date) departing date
        self.retDate = retDate # (date) return date
        self.tweeted = tweeted # (bool) True = tweeted, False = not tweeted
        self.percentage = 1000000.0
    def __str__(self):
        city = 'N/A'
        country = 'N/A'
        searches = openCSV(paths.destinationsFile)
        destinations = destListToObject(searches)
        for dest in destinations:
            if dest.dest == self.dest:
                city = dest.city
                country = dest.country
        dateFormat = "%m/%d/%Y"
        ret = '$' + str(self.price) + ' round trip:\n'
        ret += 'Cincinnati, Ohio'
        ret += ' \xE2\x9C\x88 ' + city + ', ' + country + '\n'
        ret += self.depDate.strftime(dateFormat)
        ret += ' - ' + self.retDate.strftime(dateFormat) + '\n'
        ret += self.getURL()
        return ret

    def getURL(self):
        URL_DATE_FORMAT = "%Y-%m-%d"
        URL = 'https://www.google.com/flights/#search;f={};t={};d={};r={}'
        return URL.format(self.dep, self.dest, self.depDate.strftime(URL_DATE_FORMAT),
            self.retDate.strftime(URL_DATE_FORMAT))

    def setAverage(self, avg):
        self.avg = avg
        self.percentage = (float(self.price) / self.avg) * 100

    def log(self):
        # .csv format:
        # time, departing airport, price, average price, percentage, tweeted
        dateFormat = "%m/%d/%Y"
        with open(paths.dataFolder + self.dest + '.csv', 'a') as logFile:
            logFile.write(self.logDate.strftime(dateFormat) + ',' +
                self.dep + ',' +
                self.dest + ',' +
                self.depDate.strftime(dateFormat) + ',' +
                self.retDate.strftime(dateFormat) + ',' +
                str(self.price) + ',' +
                str(self.avg) + ',' +
                str(self.tweeted) + '\n')

# Pass: String in the format 'US$1,000'
# Returns: String parsed to integer
def toInt(price):
    ret = price.replace('US','')
    ret = price.replace('$','')
    ret = ret.replace(',','')
    return int(ret)


def getGraph(driver):
    # XPATHs
    dateContainerPath  = '//div[contains(@class,"LJV2HGB-G-s LJV2HGB-G-r LJV2HGB-c-r LJV2HGB-D-a")]'
    dateClickablePath  = '//div[contains(@class,"LJV2HGB-G-m")]'
    priceGraphTabPath  = '//div[contains(@class,"LJV2HGB-o-I LJV2HGB-o-x")]'
    graphContainerPath = '//div[contains(@class, "LJV2HGB-gb-s LJV2HGB-gb-b")]'
    arrowPath          = '//div[contains(@class, "LJV2HGB-fb-d LJV2HGB-c-b")]'

    element = driver.find_element(By.XPATH, dateContainerPath)
    element = element.find_element(By.XPATH, dateClickablePath)
    element.click()

    # Finds and clicks the price graph tab to pull up the price graph
    element = element.find_element(By.XPATH, priceGraphTabPath)
    element.click()

    graph = element.find_element(By.XPATH, graphContainerPath) # Graph container div
    arrow = element.find_element(By.XPATH, arrowPath) # Arrow to proceed down the graph

    return graph, arrow


def collectData(driver, departing, destination, tripLen, lowBound=datetime.date.today(),
    highBound=datetime.date.today()):
    print destination
    # Initializations
    OFFSET = 28 # This is the ammount that the arrow progresses the chart by
    D = lowBound # Initial departure for URL
    R = lowBound + datetime.timedelta(tripLen) # Initial return for URL
    if lowBound is datetime.date.today() and highBound is datetime.date.today():
        D += datetime.timedelta(40) # preserves the count accuracy
        R += datetime.timedelta(40)
    URL_DATE_FORMAT = "%Y-%m-%d"
    URL = 'https://www.google.com/flights/#search;f={};t={};d={};r={}'.format(
        departing, destination, D.strftime(URL_DATE_FORMAT), R.strftime(URL_DATE_FORMAT))

    driver.get(URL) # Opens URL
    # startTime = timeit.default_timer() # Start testing timer
    graph, arrow = getGraph(driver)

    flights = [] # List of all Flight objects
    valid = True # Becomes false when data is failed to be collected (when a bar is gray)
    inBound = True # Becomes false when dates leave the upper and lower bounds
    count = 0 # Used to efficiently calculate what day it is by adding timedelta(count)
    barsPath  = '//div[contains(@class, "LJV2HGB-gb-z")]' # XPATH for finding bars
    pricePath = '//div[contains(@class, "LJV2HGB-gb-I")]'

    # Loops through bound of bars
    while(valid):
        bars = graph.find_elements(By.XPATH, barsPath)
        for i in range(len(bars) - OFFSET, len(bars)):
            if inBound:
                ActionChains(driver).move_to_element(bars[i]).perform()
                try:
                    WebDriverWait(driver, 2).until(EC.visibility_of_element_located((By.XPATH, pricePath)))
                except: # Not loading
                    valid = False
                    inBounds = False
                    # print "EXCEPTION"
                else: # Success, gather info
                    price = bars[i].find_element(By.XPATH, pricePath).text
                    # print price
                    if price != '':
                        depDate = D + datetime.timedelta(count)
                        retDate = R + datetime.timedelta(count)
                        flights.append(Flight(dep=departing, dest=destination, price=toInt(price), depDate=depDate, retDate=retDate))
                        if flights[-1].retDate > highBound or flights[-1].depDate < lowBound:
                            valid = False
                            inBounds = False
                count += 1
        if valid and inBound:
            ActionChains(driver).move_to_element(arrow).perform()
            arrow.click()

    # Finds the best deal of all the flights
    priceSum = 0.0
    lowestFlight = Flight()
    for flight in flights:
        priceSum += flight.price
        if(flight.price < lowestFlight.price):
                lowestFlight = flight
    lowestFlight.setAverage(int(priceSum/len(flights)))
    # stopTime = timeit.default_timer()
    print str(lowestFlight) + '\n'#+ '\nTime: ' + str(stopTime-startTime) + '\n'

    # Return best deal
    return lowestFlight


# Returns either a headless or headed webdriver
# Parameters:
#   headless: (Bool) if True, create a headless driver
# Returns:
#   driver: (Selenium.webdriver) Selenium webdriver object
def getDriver(headless=True):
    if headless:
        options = Options()
        options.add_argument("--headless")
        return webdriver.Firefox(firefox_options=options)
    else:
        return webdriver.Firefox()

# Returns list of cheapest flight objects based on destinations.csv searches
# Parameters:
#   driver: (Selenium.webdriver) Selenium driver object
# Returns:
#   cheapest: (list<Flight>) list of cheapest Flight objects
def search(driver):
    cheapest = []
    summerStart = datetime.date(2018, 5, 5)
    summerEnd = datetime.date(2018, 8, 15)
    searches = helpers.openCSV(paths.destinationsFile)
    destinations = helpers.destListToObject(searches)

    for dest in destinations:
        cheapFlight = collectData.collectData(driver=driver, departing='CVG', destination=dest.dest,
            tripLen=dest.tripLen, lowBound=summerStart, highBound=summerEnd)
        cheapest.append(cheapFlight)
    return cheapest

def log(flights):
    for flight in flights:
        flight.log()

if __name__ == '__main__':
    driver = getDriver('headless')
    cheapest = search(driver)
    driver.quit()
    log(cheapest)
