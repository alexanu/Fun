# Source: https://github.com/benataranburu/expedia-flight-deals/blob/master/flightdeals.py

from selenium import webdriver
from selenium.webdriver.common.by import By
from selenium.webdriver.common.keys import Keys

import pandas as pd
import time
import datetime

browser = webdriver.Chrome(executable_path='chromedriver')

# Ticket type path
return_ticket = "//label[@id='flight-type-roundtrip-label-hp-flight']"
one_way_ticket = "//label[@id='flight-type-one-way-label-hp-flight']"
multi_ticket = "//label[@id='flight-type-multi-dest-label-hp-flight']"

# Choose ticket type
def ticket_chooser(ticket):
    try:
        ticket_type = browser.find_element_by_xpath(ticket)
        ticket_type.click()
    except Exception as e:
        pass

# Choose departure country
def departure_city_chooser(departure_country):
    fly_from = browser.find_element_by_xpath("//input[@id='flight-origin-hp-flight']")
    time.sleep(1)
    fly_from.clear()
    time.sleep(1.5)
    fly_from.send_keys('  ' + departure_country)
    time.sleep(1.5)
    first_item = browser.find_element_by_xpath("//a[@id='aria-option-0']")
    time.sleep(1.5)
    first_item.click()

# Choose arrival arrival country
def arrival_city_chooser(arrival_country):
    fly_to = browser.find_element_by_xpath("//input[@id='flight-destination-hp-flight']")
    time.sleep(1)
    fly_to.clear()
    time.sleep(1.5)
    fly_to.send_keys('  ' + arrival_country)
    time.sleep(1.5)
    first_item = browser.find_element_by_xpath("//a[@id='aria-option-0']")
    time.sleep(1.5)
    first_item.click()

# Choose departure date
def departure_date_chooser(month, day, year):
    dep_date_button = browser.find_element_by_xpath("//input[@id='flight-departing-hp-flight']")
    dep_date_button.clear()
    dep_date_button.send_keys(month + '/' + day + '/' + year)

# Choose return dates
def return_date_chooser(month, day, year):
    return_date_button = browser.find_element_by_xpath("//input[@id='flight-returning-hp-flight']")
    for i in range(11):
        return_date_button.send_keys(Keys.BACKSPACE)
    return_date_button.send_keys(month + '/' + day + '/' + year)

# Search!
def search():
    search = browser.find_element_by_xpath("//button[@class='btn-primary btn-action gcw-submit']")
    search.click()
    time.sleep(10)

# Create data frame
df = pd.DataFrame()
def compile_data():
    global df
    global dep_times_list
    global arr_times_list
    global airlines_list
    global price_list
    global durations_list
    global stops_list
    global layovers_list

    #departure times
    dep_times = browser.find_elements_by_xpath("//span[@data-test-id='departure-time']")
    dep_times_list = [value.text for value in dep_times]

    #arrival times
    arr_times = browser.find_elements_by_xpath("//span[@data-test-id='arrival-time']")
    arr_times_list = [value.text for value in arr_times]

    #airline name
    airlines = browser.find_elements_by_xpath("//span[@data-test-id='airline-name']")
    airlines_list = [value.text for value in airlines]

    #prices
    prices = browser.find_elements_by_xpath("//span[@data-test-id='listing-price-dollars']")
    price_list = [value.text.split('$')[1] for value in prices]

    #durations
    durations = browser.find_elements_by_xpath("//span[@data-test-id='duration']")
    durations_list = [value.text for value in durations]

    #stops
    stops = browser.find_elements_by_xpath("//span[@class='number-stops']")
    stops_list = [value.text for value in stops]

    #layovers
    layovers = browser.find_elements_by_xpath("//span[@data-test-id='layover-airport-stops']")
    layovers_list = [value.text for value in layovers]

    for i in range(len(dep_times_list)):
        try:
            df.loc[i, 'departure_time'] = dep_times_list[i]
        except Exception as e:
            pass
        try:
            df.loc[i, 'arrival_time'] = arr_times_list[i]
        except Exception as e:
            pass
        try:
            df.loc[i, 'airline'] = airlines_list[i]
        except Exception as e:
            pass
        try:
            df.loc[i, 'duration'] = durations_list[i]
        except Exception as e:
            pass
        try:
            df.loc[i, 'stops'] = stops_list[i]
        except Exception as e:
            pass
        try:
            df.loc[i, 'layovers'] = layovers_list[i]
        except Exception as e:
            pass
        try:
            df.loc[i, 'prices'] = price_list[i]
        except Exception as e:
            pass

# Run code
for i in range(24):
    link = 'https://www.expedia.com/'
    browser.get(link)
    time.sleep(5)

    #choose flights only
    flights_only = browser.find_element_by_xpath("//button[@id='tab-flight-tab-hp']")
    flights_only.click()
    ticket_chooser(return_ticket)
    departure_city_chooser('Bilbao')
    arrival_city_chooser('London')
    departure_date_chooser('10', '03', '2019')
    return_date_chooser('20', '03', '2019')
    search()
    compile_data()
    print(df)

    time.sleep(3600)


# ---------------------------------------------------------------------------------------------------

# Source: https://github.com/Maanav-G/flight-prices/blob/master/main.py


from selenium import webdriver
from selenium.webdriver.common.by import By
from selenium.webdriver.common.keys import Keys

# pandas for data structuring 
import pandas as pd

import time
import datetime

# connecting email
import smtplib
from email.mime.multipart import MIMEMultipart

from openpyxl import Workbook


# connect to the web broswer for automated testing
browser = webdriver.Chrome(executable_path='/Users/maanav/chromedriver')


# set the fligth path 
return_ticket = "//label[@id='flight-type-roundtrip-label-hp-flight']"
one_way_ticket = "//label[@id='flight-type-one-way-label-hp-flight']"
multi_ticket = "//label[@id='flight-type-multi-dest-label-hp-flight']"

# function that chooses a ticket type 
def ticket_chooser(ticket):
    try:
        ticket_type = browser.find_element_by_xpath(ticket)
        ticket_type.click()
    except Exception as e:
        pass

# function that chooses departure country
# used time.sleep to give browser enough time to adapte to updates 
def dep_country_chooser(dep_country):
    fly_from = browser.find_element_by_xpath("//input[@id='flight-origin-hp-flight']")
    time.sleep(1)
    # clear any preexisting value
    fly_from.clear()
    time.sleep(1.5)
    fly_from.send_keys('  ' + dep_country)
    time.sleep(1.5)
    # click first option
    first_item = browser.find_element_by_xpath("//a[@id='aria-option-0']")
    time.sleep(1.5)
    first_item.click()

# same logic for arrival country 
def arrival_country_chooser(arrival_country):
    fly_to = browser.find_element_by_xpath("//input[@id='flight-destination-hp-flight']")
    time.sleep(1)
    fly_to.clear()
    time.sleep(1.5)
    fly_to.send_keys('  ' + arrival_country)
    time.sleep(1.5)
    first_item = browser.find_element_by_xpath("//a[@id='aria-option-0']")
    time.sleep(1.5)
    first_item.click()

# choose departure dates
def dep_date_chooser(month, day, year):
    # find element on page
    dep_date_button = browser.find_element_by_xpath("//input[@id='flight-departing-hp-flight']")
    # clear any preexisting value
    dep_date_button.clear()
    # fill element with date
    dep_date_button.send_keys(month + '/' + day + '/' + year)

# choose return date 
# clearning was not working, used .BACKSPACE instead
def return_date_chooser(month, day, year):
    return_date_button = browser.find_element_by_xpath("//input[@id='flight-returning-hp-flight']")
    
    for i in range(11):
        return_date_button.send_keys(Keys.BACKSPACE)
    return_date_button.send_keys(month + '/' + day + '/' + year)


# function clicks the search button
def search():
    # finds search element on page
    search = browser.find_element_by_xpath("//button[@class='btn-primary btn-action gcw-submit']")
    # clicks search
    search.click()
    # time delay to let browser process
    time.sleep(15)
    print('Results ready!')


df = pd.DataFrame()
def compile_data():
    global df
    global dep_times_list
    global arr_times_list
    global airlines_list
    global price_list
    global durations_list
    global stops_list
    global layovers_list

    # create variables for all features
    # find all elements for the attribute 

    # departure times
    dep_times = browser.find_elements_by_xpath("//span[@data-test-id='departure-time']")
    dep_times_list = [value.text for value in dep_times]
    
    # arrival times
    arr_times = browser.find_elements_by_xpath("//span[@data-test-id='arrival-time']")
    arr_times_list = [value.text for value in arr_times]

    # airline name
    airlines = browser.find_elements_by_xpath("//span[@data-test-id='airline-name']")
    airlines_list = [value.text for value in airlines]

    # prices
    prices = browser.find_elements_by_xpath("//span[@data-test-id='listing-price-dollars']")
    price_list = [value.text for value in prices]

    # durations
    durations = browser.find_elements_by_xpath("//span[@data-test-id='duration']")
    durations_list = [value.text for value in durations]

    # stops
    stops = browser.find_elements_by_xpath("//span[@class='number-stops']")
    stops_list = [value.text for value in stops]

    # layovers
    layovers = browser.find_elements_by_xpath("//span[@data-test-id='layover-airport-stops']")
    layovers_list = [value.text for value in layovers]

    now = datetime.datetime.now()
    current_date = (str(now.year) + '-' + str(now.month) + '-' + str(now.day))
    current_time = (str(now.hour) + ':' + str(now.minute))
    # create the excel file
    # putting all lists side by side as columns
    current_price = 'price' + '(' + current_date + '---' + current_time + ')'
    for i in range(len(dep_times_list)):
        try:
            df.loc[i, 'departure_time'] = dep_times_list[i]
        except Exception as e:
            pass
        try:
            df.loc[i, 'arrival_time'] = arr_times_list[i]
        except Exception as e:
            pass
        try:
            df.loc[i, 'airline'] = airlines_list[i]
        except Exception as e:
            pass
        try:
            df.loc[i, 'duration'] = durations_list[i]
        except Exception as e:
            pass
        try:
            df.loc[i, 'stops'] = stops_list[i]
        except Exception as e:
            pass
        try:
            df.loc[i, 'layovers'] = layovers_list[i]
        except Exception as e:
            pass
        try:
            df.loc[i, str(current_price)] = price_list[i]
        except Exception as e:
            pass
    
    print('Excel Sheet Created!')


# # email credentials 
# username: MYEMAIL
# password: MYPASSWORD

# # connect mail server 
# def connect_mail(username, password):
#     global server
#     server = smtplib.SMTP('smtp.outlook.com', 587)
#     server.ehlo()
#     server.starttls()
#     server.login(username, password)

# # create message
# def create_msg():
#     global msg
#     msg = '\nCurrent Cheapest flight:\n\nDeparture time: {}\nArrival time: {}\nAirline: {}\nFlight duration: {}\nNo. of stops: {}\nPrice: {}\n'.format(cheapest_dep_time,
#                        cheapest_arrival_time,
#                        cheapest_airline,
#                        cheapest_duration,
#                        cheapest_stops,
#                        cheapest_price)

# # send email
# def send_email(msg):
#     global message
#     message = MIMEMultipart()
#     message['Subject'] = 'Current Best flight'
#     message['From'] = 'MYEMAIL'
#     message['to'] = 'MYotherEMAIL'
#     server.sendmail('MYEMAIL', 'MYotherEMAIL', msg)



for i in range(8):    
    link = 'https://www.expedia.com/'
    browser.get(link)
    time.sleep(5)
    #choose flights only
    flights_only = browser.find_element_by_xpath("//button[@id='tab-flight-tab-hp']")
    flights_only.click()
    ticket_chooser(return_ticket)
    dep_country_chooser('Toronto')
    arrival_country_chooser('Costa Rica')
    dep_date_chooser('01', '01', '2020')
    return_date_chooser('01', '09', '2020')
    search()
    compile_data()
    #save values for email
    # current_values = df.iloc[0]
    # cheapest_dep_time = current_values[0]
    # cheapest_arrival_time = current_values[1]
    # cheapest_airline = current_values[2]
    # cheapest_duration = current_values[3]
    # cheapest_stops = current_values[4]
    # cheapest_price = current_values[-1]
    # print('run {} completed!'.format(i))
    # create_msg()
    # connect_mail(username,password)
    # send_email(msg)
    # print('Email sent!')
    df.to_excel('flights.xlsx')
    time.sleep(3600)



# ------------------------------------------------------------------------------------------------
# Source: https://github.com/nedak96/Expedia-Scraper/blob/master/ExpediaScraper.py

import urllib
from lxml import html
from selenium.webdriver import Firefox
from selenium.webdriver.firefox.options import Options
from selenium.webdriver.support import expected_conditions
from selenium.webdriver.support.wait import WebDriverWait
from selenium.webdriver.common.by import By
from selenium.common.exceptions import TimeoutException
from argparse import ArgumentParser

LOAD_TIMEOUT = 60
NUM_FLIGHTS_TO_DISPLAY = 5
NUM_RETURN_FLIGHTS_TO_DISPLAY = 5
SELECT_BUTTON_XPATH = "//li[@data-test-id='offer-listing']//button[@data-test-id='select-button']"
FLIGHTS_XPATH = "//li[@data-test-id='offer-listing']"
DEPARTURE_TIME_XPATH = ".//span[@data-test-id='departure-time']//text()"
ARRIVAL_TIME_XPATH = ".//span[@data-test-id='arrival-time']//text()"
ARRIVES_NEXT_DAY_XPATH = ".//span[@data-test-id='arrives-next-day']//text()"
PRICES_XPATH = ".//span[@data-test-id='listing-price-dollars']//text()"
DURATION_XPATH = ".//span[@data-test-id='duration']//text()"
LEG_KEY_XPATH = ".//div[@data-test-id='listing-summary']"
LEG_KEY_ATTRIBUTE = "data-leg-natural-key"


def get_url(args):
	departure_airport = args.departure_airport
	destination_airport = args.destination_airport
	departure_date = args.departure_date
	return_date = args.return_date
	num_children = args.children
	num_adults = args.adults
	is_round_trip = False

	params = {
		"mode": "search",
		"leg1": "from:"+departure_airport+",to:"+destination_airport+",departure:"+departure_date+"TANYT",
		"passengers": "children:"+str(num_children)+",adults:"+str(num_adults)
	}
	if return_date:
		is_round_trip = True
		params["trip"] = "roundtrip"
		params["leg2"] = "from:"+destination_airport+",to:"+departure_airport+",departure:"+return_date+"TANYT"
		print("Checking round trip flights from " + departure_airport + " to " + destination_airport + " from " + departure_date + " to " + return_date)
	else:
		params["trip"] = "oneway"
		print("Checking one-way flights from " + departure_airport + " to " + destination_airport + " on " + departure_date)

	return "https://www.expedia.com/Flights-Search?" + urllib.urlencode(params), is_round_trip

def get_flights(driver, url, is_round_trip, is_return_flight = False):
	driver.get("about:blank")
	driver.get(url)
	try:
		WebDriverWait(driver, LOAD_TIMEOUT).until(expected_conditions.element_to_be_clickable((By.XPATH, SELECT_BUTTON_XPATH)))
	except TimeoutException:
		print("Timeout Exception: Page didn't loaded successfully")
	page_source = driver.page_source
	doc = html.fromstring(page_source)

	flights = doc.xpath(FLIGHTS_XPATH)
	if is_return_flight:
		flights = flights[:NUM_RETURN_FLIGHTS_TO_DISPLAY]
	else:
		flights = flights[:NUM_FLIGHTS_TO_DISPLAY]

	for flight in flights:
		prices = flight.xpath(PRICES_XPATH)
		if not prices:
			break
		price = prices[0].strip()
		duration = flight.xpath(DURATION_XPATH)[0].strip()
		departure_time = flight.xpath(DEPARTURE_TIME_XPATH)[0].strip()
		arrival_time = flight.xpath(ARRIVAL_TIME_XPATH)[0].strip()
		arrives_next_day = flight.xpath(ARRIVES_NEXT_DAY_XPATH)
		if arrives_next_day:
			arrival_time += arrives_next_day[0].strip()

		if is_return_flight:
			print("   %-11s %-11s %-11s %-11s" % (departure_time, arrival_time, price, duration))
			continue
		print("%-11s %-11s %-11s %-11s" % (departure_time, arrival_time, price, duration))

		if is_round_trip:
			leg_key = flight.xpath(LEG_KEY_XPATH)[0].attrib[LEG_KEY_ATTRIBUTE]
			get_flights(driver, url + "#leg/" + leg_key, is_round_trip, True)

if __name__=="__main__":
	argparser = ArgumentParser()
	argparser.add_argument('departure_airport', help='Departure airport code')
	argparser.add_argument('destination_airport', help='Destination airport code')
	argparser.add_argument('departure_date', help='MM/DD/YYYY')
	argparser.add_argument('return_date', help='MM/DD/YYYY',nargs='?', default="")
	argparser.add_argument('-a', '--adults', help='Number of adults: default 1', default=1)
	argparser.add_argument('-c', '--children', help='Number of adults: default 0', default=0)

	url, is_round_trip = get_url(argparser.parse_args())

	opts = Options()
	opts.set_headless()
	driver = Firefox(options=opts)

	print("Departure   Arrival     Price       Duration   ")
	if is_round_trip:
		print("-> Return Flight Details")

	get_flights(driver, url, is_round_trip)

	driver.close()
	
# --------------------------------------------------------------------------------------------------------------------------
# Source: https://github.com/Shruti-Pattajoshi/Travel-Website-Scraping-for-the-Cheapest-Fares/blob/master/flights_scraping.py


from selenium import webdriver
from selenium.webdriver.common.by import By
from selenium.webdriver.common.keys import Keys

import pandas as pd

import time
import datetime

import smtplib
from email.mime.multipart import MIMEMultipart

#webdriver location in my system /path/
browser = webdriver.Chrome(executable_path='C:/Users/WORK/Desktop/SECOND YEAR PROJECTS/chromedriver.exe')

#choosing the type of ticket
return_ticket = "//label[@id='flight-type-roundtrip-label-hp-flight']"
one_way_ticket = "//label[@id='flight-type-one-way-label-hp-flight']"
multi_ticket = "//label[@id='flight-type-multi-dest-label-hp-flight']"


#choosing the type of ticket
def ticket_chooser(ticket):
    try:
        ticket_type = browser.find_element_by_xpath(ticket)
        ticket_type.click()
    except Exception as e:
        pass

#choosing the source place
def dep_country_chooser(dep_country):
    fly_from = browser.find_element_by_xpath("//input[@id='flight-origin-hp-flight']")
    time.sleep(1)
    fly_from.clear()
    time.sleep(1.5)
    fly_from.send_keys('  ' + dep_country)
    time.sleep(1.5)
    first_item = browser.find_element_by_xpath("//a[@id='aria-option-0']")
    time.sleep(1.5)
    first_item.click()

#choosing the destination place
def arrival_country_chooser(arrival_country):
    fly_to = browser.find_element_by_xpath("//input[@id='flight-destination-hp-flight']")
    time.sleep(1)
    fly_to.clear()
    time.sleep(1.5)
    fly_to.send_keys('  ' + arrival_country)
    time.sleep(1.5)
    first_item = browser.find_element_by_xpath("//a[@id='aria-option-0']")
    time.sleep(1.5)
    first_item.click()

#choosing the departure date
def dep_date_chooser(month, day, year):
    dep_date_button = browser.find_element_by_xpath("//input[@id='flight-departing-hp-flight']")
    dep_date_button.clear()
    dep_date_button.send_keys(month + '/' + day + '/' + year)

#choosing the return date
def return_date_chooser(month, day, year):
    return_date_button = browser.find_element_by_xpath("//input[@id='flight-returning-hp-flight']")
    for i in range(11):
        return_date_button.send_keys(Keys.BACKSPACE)
    return_date_button.send_keys(month + '/' + day + '/' + year)


def search():
    search = browser.find_element_by_xpath("//button[@class='btn-primary btn-action gcw-submit']")
    search.click()
    time.sleep(15)
    print('Results ready!')


df = pd.DataFrame()

#compiling the data to form the pandas dataframe
def compile_data():
    global df
    global dep_times_list
    global arr_times_list
    global airlines_list
    global price_list
    global durations_list
    global stops_list
    global layovers_list

    dep_times = browser.find_elements_by_xpath("//span[@data-test-id='departure-time']")
    dep_times_list = [value.text for value in dep_times]
    
    arr_times = browser.find_elements_by_xpath("//span[@data-test-id='arrival-time']")
    arr_times_list = [value.text for value in arr_times]
   
    airlines = browser.find_elements_by_xpath("//span[@data-test-id='airline-name']")
    airlines_list = [value.text for value in airlines]
   
    prices = browser.find_elements_by_xpath("//span[@data-test-id='listing-price-dollars']")
    price_list = [value.text for value in prices]
   
    durations = browser.find_elements_by_xpath("//span[@data-test-id='duration']")
    durations_list = [value.text for value in durations]
    
    stops = browser.find_elements_by_xpath("//span[@class='number-stops']")
    stops_list = [value.text for value in stops]
    
    layovers = browser.find_elements_by_xpath("//span[@data-test-id='layover-airport-stops']")
    layovers_list = [value.text for value in layovers]
    
    #getting the optimal values for the feilds 
    now = datetime.datetime.now()
    current_date = (str(now.year) + '-' + str(now.month) + '-' + str(now.day))
    current_time = (str(now.hour) + ':' + str(now.minute))
    current_price = 'price' + '(' + current_date + '---' + current_time + ')'
    
    for i in range(len(dep_times_list)):
        try:
            df.loc[i, 'departure_time'] = dep_times_list[i]
        except Exception as e:
            pass
        try:
            df.loc[i, 'arrival_time'] = arr_times_list[i]
        except Exception as e:
            pass
        try:
            df.loc[i, 'airline'] = airlines_list[i]
        except Exception as e:
            pass
        try:
            df.loc[i, 'duration'] = durations_list[i]
        except Exception as e:
            pass
        try:
            df.loc[i, 'stops'] = stops_list[i]
        except Exception as e:
            pass
        try:
            df.loc[i, 'layovers'] = layovers_list[i]
        except Exception as e:
            pass
        try:
            df.loc[i, str(current_price)] = price_list[i]
        except Exception as e:
            pass
    print('Data Frame converted into Excel Sheet')

#mail id by which the mail will go to you
username = 'sweetshruti110096@gmail.com'
password = 'XXXXXXXXXXXX'

# Connecting over email
def connect_mail(username, password):
    global server
    server = smtplib.SMTP('smtp.gmail.com', 587)
    server.ehlo()
    server.starttls()
    server.login(username, password)


# Creating message template for email
def create_msg():
    global msg
    msg = '\nCurrent Cheapest flight:\n\nDeparture time: {}\nArrival time: {}\nAirline: {}\nFlight duration: {}\nNo. of stops: {}\nPrice: {}\n'.format(
        cheapest_dep_time,
        cheapest_arrival_time,
        cheapest_airline,
        cheapest_duration,
        cheapest_stops,
        cheapest_price)

# Sending message email
def send_email(msg):
    global message
    message = MIMEMultipart()
    message['Subject'] = 'Current Best flight'
    message['From'] = 'sweetshruti110096@gmail.com'
    message['to'] = 'spj11@iitbbs.ac.in'
    server.sendmail('sweetshruti110096@gmail.com', 'spj11@iitbbs.ac.in', msg)

for i in range(4): # 4 times after every one hour
    link = 'https://www.expedia.co.in/' #easy to access website comparitively
    browser.get(link)

    time.sleep(5)
    # choose flights only
    flights_only = browser.find_element_by_xpath("//button[@id='tab-flight-tab-hp']")
    flights_only.click()
     # choose flight type
    ticket_chooser(return_ticket)
     # choosing the source and destination
    dep_country_chooser('Bangalore')
    arrival_country_chooser('Bhubaneswar')
     # choosing the dep date and arr date
    dep_date_chooser('04', '07', '2019')
    return_date_chooser('05', '07', '2019')
    search()
    compile_data()
    # saving values for email
    current_values = df.iloc[0]
    cheapest_dep_time = current_values[0]
    cheapest_arrival_time = current_values[1]
    cheapest_airline = current_values[2]
    cheapest_duration = current_values[3]
    cheapest_stops = current_values[4]
    cheapest_price = current_values[-1]
    print('Run completed!')
    connect_mail(username, password)
    create_msg()
    send_email(msg)

    print('Email sent!')
    df.to_excel('flights.xlsx')
    time.sleep(3600)


# ----------------------------------------------------------------------------------------

# Source: https://github.com/WinEisEis/flight_expedia_scraper

from selenium import webdriver
from selenium.webdriver.common.by import By
from selenium.webdriver.common.keys import Keys
import pandas as pd
import time
import datetime

# Edit Chrome webdriver based on your installation path
PATH = "/Users/chayaphatnicrothanon/PycharmProjects/flight_expedia_scraper"
browser = webdriver.Chrome(executable_path=PATH + '/chromedriver')

# Choose ticket type
return_ticket = "//label[@id='flight-type-roundtrip-label-hp-flight']"
one_way = "//label[@id='flight-type-one-way-label-hp-flight']"
multi = "//label[//[@id='flight-type-multi-dest-label-hp-flight']]"


def ticket_chooser(ticket):
    try:
        # Find the ticket type's button
        ticket_type = browser.find_element_by_xpath(ticket)
        ticket_type.click()

    except Exception as e:
        print("Ticket type not found")

def departure_chooser(dep):
    """
    Choose the departure country and select the first options provided by Expedia
    Example: if the user type "BKK" -> the first item will show "Bangkok, Thailand all airports"
    Note: that we need to sleep the program for some occasions for the webpage to be fetched
    """

    departure_from = browser.find_element_by_xpath("//input[@id='flight-origin-hp-flight']")
    time.sleep(1.5)
    departure_from.clear() # Clear the text in the box
    departure_from.send_keys(dep) # Specify the departure country
    time.sleep(2)
    try: # Select the first result 
        first_item = browser.find_element_by_xpath("//a[@id='aria-option-0']")
    except Exception as e:
        print("Fail to click the departure country")

    first_item.click()


def arrival_chooser(arrive):
    # Find the input box of arrival country
    arrive_to = browser.find_element_by_xpath("//input[@id='flight-destination-hp-flight']")
    time.sleep(1.5)
    arrive_to.clear()
    arrive_to.send_keys(arrive) # Specify the arrival country
    time.sleep(2)

    try:     # Select first result in the list
        first_item = browser.find_element_by_xpath("//a[@id='aria-option-0']")
    except Exception as e:
        print("Fail to click the arrival country")
    first_item.click()


def departure_date_picker(month, day, year):
    # Select the input box of the departure date
    dep_date_btn = browser.find_element_by_xpath("//input[@id='flight-departing-hp-flight']")
    dep_date_btn.clear()
    dep_date_btn.send_keys(month + '/' + day + '/' + year)
    time.sleep(1)

def arrival_date_picker(month, day, year):
    # Select the input box of the arrival date
    return_date_btn = browser.find_element_by_xpath("//input[@id='flight-returning-hp-flight']")
    return_date_btn.clear()
    return_date_btn.send_keys(month + '/' + day + '/' + year)
    time.sleep(1)

def search_click():
    search_box = browser.find_element_by_xpath("//button[@class='btn-primary btn-action gcw-submit']")
    search_box.click()
    time.sleep(20)  # Quite long delay when searching ...
    print('Search button has been clicked!')

df = pd.DataFrame()

def get_all_flight():
    global df
    global dep_time_list
    global arr_time_list
    global airlines_list
    global price_list
    global durations_list
    global stops_list
    global layovers_list

    dep_time = browser.find_elements_by_xpath("//span[@data-test-id='departure-time']")
    dep_time_list = [elem.text for elem in dep_time]
    arr_time = browser.find_elements_by_xpath("//span[@data-test-id='arrival-time']")
    arr_time_list = [elem.text for elem in arr_time]
    airlines = browser.find_elements_by_xpath("//span[@data-test-id='airline-name']")
    airlines_list = [value.text for value in airlines]
    durations = browser.find_elements_by_xpath("//span[@data-test-id='duration']")
    durations_list = [value.text for value in durations]
    stops = browser.find_elements_by_xpath("//span[@class='number-stops']")
    stops_list = [value.text for value in stops]
    prices = browser.find_elements_by_xpath("//span[@data-test-id='listing-price-dollars']")
    price_list = [value.text for value in prices]

    now = datetime.datetime.now()
    current_date = (str(now.year) + '-' + str(now.month) + '-' + str(now.day))
    current_time = (str(now.hour) + ':' + str(now.minute))
    current_price = 'price' + '(' + current_date + '---' + current_time + ')'

    for i in range(len(dep_time_list)):
        try:
            df.loc[i, 'departure_time'] = dep_time_list[i]
        except Exception as e:
            pass
        try:
            df.loc[i, 'arrival_time'] = arr_time_list[i]
        except Exception as e:
            pass
        try:
            df.loc[i, 'airline'] = airlines_list[i]
        except Exception as e:
            pass
        try:
            df.loc[i, 'duration'] = durations_list[i]
        except Exception as e:
            pass
        try:
            df.loc[i, 'stops'] = stops_list[i]
        except Exception as e:
            pass
        try:
            df.loc[i, str(current_price)] = price_list[i]
        except Exception as e:
            pass

        df.to_csv('output.csv', index=False)
    print('Excel Sheet Created!')