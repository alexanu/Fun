# Source: https://github.com/jquetzalcoatl/FlightScraping
# Based on: https://dzone.com/articles/make-python-surf-the-web-for-you-and-send-best-fli

from selenium import webdriver
from selenium.webdriver.common.by import By
from selenium.webdriver.common.keys import Keys

import pandas as pd

import time
import datetime

browser = webdriver.Chrome(executable_path='./chromedriver')

#Setting ticket types paths
return_ticket = "//label[@id='flight-type-roundtrip-label-hp-flight']"
one_way_ticket = "//label[@id='flight-type-one-way-label-hp-flight']"
multi_ticket = "//label[@id='flight-type-multi-dest-label-hp-flight']"

def ticket_chooser(ticket):
    try:
        ticket_type = browser.find_element_by_xpath(ticket)
        ticket_type.click()
    except Exception as e:
        pass

def dep_country_chooser(dep_country):
    fly_from = browser.find_element_by_xpath("//*[@id='sb_ifc50']/input") #browser.find_element_by_xpath("//input[@id='flt-app']")
    time.sleep(1)
    fly_from.clear()
    time.sleep(1.5)
    fly_from.send_keys('  ' + dep_country)
    time.sleep(1.5)
    first_item = browser.find_element_by_xpath("//*[@id='sbse0']")
    time.sleep(1.5)
    first_item.click()
#//*[@id="sb_ifc50"]/input
def arrival_country_chooser(arrival_country):
    fly_to = browser.find_element_by_xpath("//*[@id='sb_ifc50']/input") #browser.find_element_by_xpath("//input[@id='flight-destination-hp-flight']")
    time.sleep(1)
    fly_to.clear()
    time.sleep(1.5)
    fly_to.send_keys('  ' + arrival_country)
    time.sleep(1.5)
    first_item = browser.find_element_by_xpath("//*[@id='sbse0']")
    time.sleep(1.5)
    first_item.click()

def dep_date_chooser(month, day, year):
    dep_date_button = browser.find_element_by_xpath("//input[@value]")
    dep_date_button.clear()
    time.sleep(0.5)
    #dep_date_button.send_keys(month + '/' + day + '/' + year)
    dep_date_button.send_keys(day + '/' + month + '/' + year[-2:])

def return_date_chooser(month, day, year):
    return_date_button = browser.find_element_by_xpath("//input[@value='']")
    #return_date_button.clear()
    time.sleep(0.5)
    for i in range(11):
        return_date_button.send_keys(Keys.BACKSPACE)
    return_date_button.send_keys(day + '/' + month + '/' + year[-2:])
    return_date_button.send_keys(Keys.ENTER)

def search():
    search = browser.find_element_by_xpath("//g-raised-button[@data-flt-ve='done']")
    search.click()
    time.sleep(5)
    print('Results ready!')

def compile_data(df, origin, destination, date1, date2):
    # global df
    # global dep_times_list
    # global arr_times_list
    # global airlines_list
    # global price_list
    # global durations_list
    # global stops_list
    # global layovers_list
    #departure times /span[contains(@class, 'gws-flights-results__more')]
    #browser.find_element_by_xpath("//*[@id='flt-app']/div[2]/main[4]/div[7]/div[1]/div[5]/div[1]/ol/li[1]/div/div[1]/div[2]/div[2]/span/svg").click()
    #browser.find_element_by_xpath("//a[@href='javascript:void(0)']").click()
    #time.sleep(1)
    button_expand = browser.find_elements(By.XPATH, "//span[contains(@class, 'gws-flights-results')]")
    # print(len(button_expand))
    # for i in range(1):
    #     button_expand[i].click()
    #     time.sleep(.8)
    dep_times = browser.find_elements_by_xpath("//span[@jscontroller and @jsdata and @jsaction]")
    times_list = list(filter(lambda x: (x != ''), [value.text for value in dep_times]))
    dep_times_list = [times_list[2*i] for i in range(int(len(times_list)/2))] #list(filter(lambda x: (x % 2 == 1), times_list))
    #print(dep_times_list)
    #arrival times
    #arr_times = browser.find_elements_by_xpath("//span[@data-test-id='arrival-time']")
    #arr_times_list = [value.text for value in arr_times]
    arr_times_list = [times_list[2*i+1] for i in range(int(len(times_list)/2))]
    #print(arr_times_list)
    #airline name
    airlines = browser.find_elements_by_xpath("//span[contains(@class, 'gws-flights__ellipsize')]")
    airlines_list_prev = [value.text for value in airlines]
    airlines_list = [airlines_list_prev[2*i] for i in range(int(len(airlines_list_prev)/2))]
    airlines_op_list = [airlines_list_prev[2 * i+1] for i in range(int(len(airlines_list_prev) / 2))]
    #print(airlines_list)
    #prices
    prices = browser.find_elements_by_xpath("//div[contains(@class, 'flt-subhead1 gws-flights-results__price')]")
    price_list_prev = [value.text for value in prices]      #(') .split
    price_list = [price_list_prev[2*i] for i in range(int(len(price_list_prev)/2))]
    #print(price_list)
    #print(price_list)
    #durations
    durations = browser.find_elements_by_xpath("//div[contains(@class, 'gws-flights-results__duration')]")
    durations_list = [value.text for value in durations]
    #print(durations_list)
    #stops
    stops = browser.find_elements_by_xpath("//div[contains(@class, 'gws-flights-results__stops')]")
    stops_list = [value.text for value in stops]
    #print(stops_list)
    #layovers
    layovers = browser.find_elements_by_xpath("//div[contains(@class, 'gws-flights-results__layover-time')]")
    layovers_list = [value.text for value in layovers]
    #print(layovers_list)
    now = datetime.datetime.now()
    current_date = (str(now.year) + '-' + str(now.month) + '-' + str(now.day))
    current_time = (str(now.hour) + ':' + str(now.minute))
    current_price = 'price' # + '(' + current_date    # + '---' + current_time + ')'
    ind = len(df)
    for i in range(len(dep_times_list)):
        try:
            df.loc[ind, 'origin'] = origin
        except Exception as e:
            pass
        try:
            df.loc[ind, 'destination'] = destination
        except Exception as e:
            pass
        try:
            df.loc[ind, 'departure_day'] = date1
        except Exception as e:
            pass
        try:
            df.loc[ind, 'arrival_day'] = date2
        except Exception as e:
            pass
        try:
            df.loc[ind, 'departure_time'] = dep_times_list[i]
        except Exception as e:
            pass
        try:
            df.loc[ind, 'arrival_time'] = arr_times_list[i]
        except Exception as e:
            pass
        try:
            df.loc[ind, 'airline'] = airlines_list[i]
        except Exception as e:
            pass
        try:
            df.loc[ind, 'duration'] = durations_list[i]
        except Exception as e:
            pass
        try:
            df.loc[ind, 'stops'] = stops_list[i]
        except Exception as e:
            pass
        try:
            df.loc[ind, 'layovers'] = layovers_list[i]
        except Exception as e:
            pass
        try:
            df.loc[ind, str(current_price)] = price_list[i]
        except Exception as e:
            pass
        ind = ind + 1
    print('Excel Sheet Created!')

now = datetime.datetime.now()
current_date = (str(now.year) + '-' + str(now.month) + '-' + str(now.day))
current_time = (str(now.hour) + ':' + str(now.minute))
current_price = 'price' + '(' + current_date + '---' + current_time + ')'

def bulk(origin, destination, d1, d2, origin_time_interval, destination_time_interval, df):
    date1, date2 = getdates(d1, d2, origin_time_interval, destination_time_interval)
    #df = pd.DataFrame()
    #for i in range(1):
    link = 'https://www.google.com/flights'
    #browser.execute_script('window.open()')
    #browser.switch_to.window(browser.window_handles[0])
    browser.get(link)
    time.sleep(2)
    #choose flights only
    flights_only = browser.find_element_by_xpath("//*[@id='flt-app']/div[2]/main[1]/div[4]/div/div[3]/div/div[2]/div[1]") # browser.find_element_by_xpath("//button[@id='flt-app']")
    flights_only.click()
    ticket_chooser(return_ticket)
    dep_country_chooser(origin)
    time.sleep(1)
    flights_only = browser.find_element_by_xpath("//*[@id='flt-app']/div[2]/main[1]/div[4]/div/div[3]/div/div[2]/div[2]")
    flights_only.click()
    arrival_country_chooser(destination)
    time.sleep(1)
    flights_only = browser.find_element_by_xpath("//*[@id='flt-app']/div[2]/main[1]/div[4]/div/div[3]/div/div[2]/div[4]/div[1]")
    flights_only.click()
    dep_date_chooser(date1.split('/')[0], date1.split('/')[1], date1.split('/')[2])     # '04', '01', '2020')
    time.sleep(2)
    flights_only = browser.find_element_by_xpath("//*[@id='flt-modaldialog']/div/div[4]/div[2]/div[3]/date-input/input")
    flights_only.click()
    return_date_chooser(date2.split('/')[0], date2.split('/')[1], date2.split('/')[2]) #'05', '02', '2020')
    search()
    compile_data(df, origin, destination, date1, date2)
    #save values for email
    current_values = df.iloc[0]
    cheapest_dep_time = current_values[0]
    cheapest_arrival_time = current_values[1]
    cheapest_airline = current_values[2]
    cheapest_duration = current_values[3]
    cheapest_stops = current_values[4]
    cheapest_price = current_values[-1]
    #print('run {} completed!'.format(i))
    # create_msg()
    # connect_mail()
    # send_email(msg)
    # print('Email sent!')
    #df.to_excel('flights.xlsx')
    #time.sleep(3600)
    #browser.close()

def getdates(d1, d2, i, j):
    date1 = datetime.datetime.strptime(d1, '%m/%d/%Y') + datetime.timedelta(days=i)
    date2 = datetime.datetime.strptime(d2, '%m/%d/%Y') + datetime.timedelta(days=j)
    return date1.strftime('%m/%d/%Y'), date2.strftime('%m/%d/%Y')


def mainFunction(origin, d1, d2, flexibility):
    df = pd.DataFrame()
    cities = ['barcelona', 'roma', 'london', 'paris', 'dresden', 'budapest']
    for i in range(flexibility+1):
        for city in cities:
            bulk(origin, city, d1, d2, i, 0, df)
    df.to_excel('flights.xlsx')
    browser.close()
    sortbyprice(df)

def sortbyprice(df):
    prices = [int(df['price'].iloc[i].split(' ')[1].replace(",", "")) for i in range(len(df))]
    # index = sorted(range(len(prices)), key=lambda k: prices[k])
    # print(prices)
    # print(index)
    df_price = df
    del df_price['price']
    df_price['price'] = prices
    df_price.sort_values(by=['price']).to_excel('flights_sort_by_price.xlsx')


mainFunction('san diego', '04/01/2020', '05/02/2020', 4)