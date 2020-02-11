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
