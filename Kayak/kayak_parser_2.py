
# Source: https://github.com/leonj3813/Kayak

'''
Kayak.com does not like scraping their website ...
... and too much accessing will cause them to flag you as a bot. 
Must use a headless browser to render the javascript.
'''

from bs4 import BeautifulSoup
from selenium import webdriver
from selenium.webdriver.common.keys import Keys
import requests
from user_agent import generate_user_agent

import os
import string
import re

from time import sleep, strftime
import time
import datetime
from dateutil import rrule

from random import randint
import pandas as pd
import numpy as np







def close_popup():
    ## CLOSING POPUP
    try:
        xp_popup_close = '//button[contains(@id,"dialog-close") and contains(@class, "Button-No-Standard-Style close ")]'
        driver.find_elements_by_xpath(xp_popup_close)[5].click()
        print('ALG.1 : SUCCESS')
    except Exception as e:
        print("ALG.1 : FAIL")
        pass

   try:
        xp_popup_close = '//button[contains(@id,"-dialog-close") and contains(@class, "Button-No-Standard-Style close ")]'
        button = driver.find_element_by_xpath(xp_popup_close)
        driver.implicitly_wait(10)
        ActionChains(driver).move_to_element(button).click(button).perform()
        print('ALG.2 : SUCCESS')
    except Exception as e:
        print("ALG.2 : FAIL")
        pass

    try:
        button = driver.find_element_by_name('alert')
        button.click()
        sleep(2)
        # Switch the control to the Alert window
        obj = driver.switch_to.alert
        # Dismiss the Alert using
        obj.dismiss()
        print('ALG.3 : SUCCESS')
    except:
        print('ALG.3 : FAIL')
        pass
 





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






base_url = "http://www.kayak.com/flights/"
city_from = "SCE"
city_to = "ATL"

today = datetime.date.today()
dates = list(rrule.rrule(rrule.WEEKLY, count=4, byweekday=rrule.FR(1),dtstart=today))
date_format = "%Y-%m-%d"
URLs = []
for date in dates:
    range = date.strftime(date_format) + "/" + (date + datetime.timedelta(days=2)).strftime(date_format)
    URLs.append(base_url + city_from + '-' + city_to + '/' + range)
    # Another way:     
    # full_URL = ('https://www.kayak.com/flights/' + city_from + '-' + city_to + 
    #           '/' + date_start + '-flexible/' + date_end + '-flexible?sort=bestflight_a')





for url in URLs:
    driver = webdriver.PhantomJS("phantomjs")     # use phantomjs headless browser to fetch webpage

    # http://chromedriver.chromium.org/
    chromedriver = "/Users/Jon/Downloads/chromedriver"
    os.environ["webdriver.chrome.driver"] = chromedriver
    driver = webdriver.Chrome(chromedriver)
    # driver = webdriver.Chrome(executable_path=path_to_chromedriver)
    sleep(2)
    # sleep(randint(8, 10))
    driver.get(url)
    driver.maximize_window()
    sleep(randint(15, 20))
    driver.refresh()
    close_popup()
    sleep(randint(50, 60))

 
    # Try quick version:
    '''
    result_list = driver.find_elements_by_xpath('//*[@id="searchResultsList"]/div')
    sections = [value.text.strip() for value in result_list]
    for section in sections:
        print(section)
        print()

    '''

    cheapest = '//a[@data-code = "price"]'
    driver.find_element_by_xpath(cheapest).click()
    sleep(randint(60, 90))
    # load more
    try:
        more_results = '//a[@class="moreButton"]'
        driver.find_element_by_xpath(more_results).click()
        sleep(randint(45, 60))
    except:
        pass

    #driver.delete_all_cookies()


    headers = {'User-Agent': 'Mozilla/5.0 (Macintosh; Intel Mac OS X 10_10_1) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/39.0.2171.95 Safari/537.36'}
    # Cookie must be updated every 52 days ca. .
    # Last Cookie: 23 Jan 2020 . On 17 Jan 2020 previous cookie (26 Nov 2019) stopped working
    headers = {
        "Host": "www.kayak.com",
        "User-Agent": "Mozilla/5.0 (Windows NT 6.1; Win64; x64; rv:72.0) Gecko/20100101 Firefox/72.0",
        # "Accept": "text/html,application/xhtml+xml,application/xml;q=0.9,*/*;q=0.8",
        "Accept-Language": "en-US,en;q=0.5",
        "Accept-Encoding": "gzip, deflate, br",
        "Connection": "keep-alive",
        "Upgrade-Insecure-Requests": "1",
        "Cache-Control": "max-age=0",
        "TE": "Trailers",
        "Accept": "*/*",
        "Referer": "https://www.kayak.com",
        "Content-type": "application/x-www-form-urlencoded",
        "Origin": "https://www.kayak.com",

        # cookie retrieved METHOD POST DOMAIN www.kayak.com FILE collector. Shouldn't it be under GET??
        "Cookie": 'vid=1ed3f1e2-1001-11ea-9d54-0242ac12000c; vid=1ed3f1e2-1001-11ea-9d54-0242ac12000c; '
                  'xp-session-seg=xp20; Apache=JAFJAB1D8Ddhww$Jbk538w-AAABbnn3YNw-98-YclfRQ; '
                  'kayak=Jv1vDB_C2TAPMt2$Fzna; kayak.mc'
                  '=Adb2nXsU9zQyjBymb6rKZk5jtrx1pzhfVQCnsEMLyfa3UabrS_crZxLmahh1xpukY7sQ46OeysLYSgsmL9u5UEmsLI0yWKhNhx'
                  'a0xAh85mqBaGiFaqDg0xpm-SSz4Vj8nFLm47wl_SjunwXpU3VzjN-D0Vh5jYrt7Mc-uVqDzxzsqDf9UnPz4Cohi1zu3VfnHnM0R6'
                  'ArZPhpjPpkSUe53l_KjHdqM0plm8K90YP-POnse4xCg-M1jO_-m8dUhBoMCHgAoHmBgLBqewRNLFo_rYV8B-9uWI5mQ5OlZ-LrU'
                  'CuoNfZB1Jms2EH7yR9zarTqS0zFHlSLmaHcNa8kkUOLe3ertvlrDM6HYoLob7lvZBfG4l8pvFpo8-kHfub5ufCzOo6HpqqYtgs1k'
                  'hbg_CzpGncxGtNAO91taSgzCCctdqonJW0g9xpwY-5umG2MydC_1h-z3HYGWuG2oQEgiVcYlytncQYl5gbMtZfvncTPZLzjQqsO'
                  '-jIdY2zJSQRwN-UtRR9cL1XsNr0AY7hryLTMxvk; _pxhd=""; p1.med.sc=17; _pxvid=1ed3f1e2-1001-11ea-9d54-0242'
                  'ac12000c; _gcl_au=1.1.777878553.1574740783; _ga=GA1.2.109955462.1574740783; _up=1.2.1950175204.15747'
                  '40784; G_ENABLED_IDPS=google; __gads=ID=22dffd3207285d34:T=1574740790:S=ALNI_Mb4b-OLfcBGBRp4DiGjBqsV'
                  '82WR7w; _gd_moveFromP13nTopContent="guidesbanner"; intent_media_prefs=; kykprf=274; cluster=5; p1.me'
                  'd.sid=H-51sGEXOweTrHBUZBTvxeL-YJ_zj1rrA5PhwASxyRiewanF_Zt_6qCOwegMT4jdw; kmkid=ApLYTE2rbbsgYyeXpP9Me'
                  'TU; NSC_q5-tqbslmf-cmvf=ffffffff0989bdf345525d5f4f58455e445a4a422a59; NSC_q5-lbqj-cmvf=ffffffff0989b'
                  '94345525d5f4f58455e445a4a42299c; _pxff_tm=1; _gid=GA1.2.1704400075.1579773435; _gat=1; _gat_UA422091'
                  '8541=1; _gat_UA4220918542=1; _px3=31d2768d83a8167dfeb29a51904cd657551c94caff79bf4def58f26aa1aca4fb:1'
                  'VzBo+ZO8UM8SWW8ztSfGF12yODUZSDDkCxfPaTsnSsB0flQEd3VacQb2KqZsxhOtPyM8Olw8bF2BwLzeBG0Ew==:1000:VIQ9ZG0'
                  'BcTgB2s15r+PCVXpx6LQJZA9sfCRetRwUGAOYZ/AZZqOU5cIOiiCex8dd0Ypr2JsdCOS8O6OXtMLXeL'
                  '/T7vzrX3cZSrO9SFMzpy3y7Gfnrt6soaPssxCsSD4Q6ZUXpWvWnwUbCscPHvv3+Ke7vUexzJGFN4lw0z3vqYw=; '
                  'hiddenParamsLAX-ATL%2F2020-01-23=page_origin%3DF..FD..M0%26src%3D%26searchingagain%3D%26c2s%3D'
                  '%26po%3D%26personality%3D%26provider%3D%26pageType%3DFD%26id%3DDR2E '
    }

    soup = BeautifulSoup(driver.page_source)
    results = filter_results(soup)




# https://towardsdatascience.com/if-you-like-to-travel-let-python-help-you-scrape-the-best-fares-5a1f26213086

    xpath_sections = '//*[@class="section duration"]'
    sections = driver.find_elements_by_xpath(xpath_sections)
    sections_list = [value.text for value in sections]

    section_out_list = sections_list[::2]
    section_in_list = sections_list[1::2]
    
    
    out_duration = []
    out_section_names = []
    for n in section_out_list:
        out_duration.append(''.join(n.split()[0:2]))
        out_section_names.append(''.join(n.split()[2:5]))
    
    in_duration = []
    in_section_names = []
    for n in section_in_list:
        in_duration.append(''.join(n.split()[0:2]))
        in_section_names.append(''.join(n.split()[2:5]))
    
    xpath_dates = '//div[@class="section date"]'
    dates = driver.find_elements_by_xpath(xpath_dates)
    dates_list = [value.text for value in dates]
    out_date_list = dates_list[::2]
    in_date_list = dates_list[1::2]
    
    out_day = [value.split()[0] for value in out_date_list]
    out_weekday = [value.split()[1] for value in out_date_list]
    in_day = [value.split()[0] for value in in_date_list]
    in_weekday = [value.split()[1] for value in in_date_list]
    
    xpath_prices = '//div[contains(@id,"price-bookingSection")]//span[@class="price option-text"]'
    prices = driver.find_elements_by_xpath(xpath_prices)
    prices_list = [price.text.replace('฿ ', '').replace(',', '') for price in prices if price.text != '']
    prices_list = list(map(int, prices_list))
    
    # the stops are a big list with one leg on the even index and second leg on odd index
    xpath_stops = '//div[@class="section stops"]/div[1]'
    stops = driver.find_elements_by_xpath(xpath_stops)
    stops_list = [stop.text[0].replace('n','0') for stop in stops]
    out_stop_list = stops_list[::2]
    in_stop_list = stops_list[1::2]
    
    xpath_stops_cities = '//div[@class="section stops"]/div[2]'
    stops_cities = driver.find_elements_by_xpath(xpath_stops_cities)
    stops_cities_list = [stop.text for stop in stops_cities]
    out_stop_name_list = stops_cities_list[::2]
    in_stop_name_list = stops_cities_list[1::2]
    
    xpath_schedule = '//div[@class="section times"]'
    schedules = driver.find_elements_by_xpath(xpath_schedule)
    hours_list = []
    airlines_list = []
    for schedule in schedules:
        hours_list.append(schedule.text.split('\n')[0])
        airlines_list.append(schedule.text.split('\n')[1])
    
    out_hours = hours_list[::2]
    out_airlines = airlines_list[1::2]
    in_hours = hours_list[::2]
    in_airlines = airlines_list[1::2]
        
    cols = (['Out Day', 'Out Weekday', 'Out Duration', 'Out Cities', 'Return Day', 
             'Return Weekday', 'Return Duration', 'Return Cities', 'Out Stops', 
             'Out Stop Cities', 'Return Stops', 'Return Stop Cities', 
             'Out Time', 'Out Airline', 'Return Time', 
             'Return Airline', 'Price'])
    

    flights_df = pd.DataFrame({'Out Day': out_day,
                               'Out Weekday': out_weekday,
                               'Out Duration': out_duration,
                               'Out Cities': out_section_names,
                               'Return Day': in_day,
                               'Return Weekday': in_weekday,
                               'Return Duration': in_duration,
                               'Return Cities': in_section_names,
                               'Out Stops': out_stop_list,
                               'Out Stop Cities': out_stop_name_list,
                               'Return Stops': in_stop_list,
                               'Return Stop Cities': in_stop_name_list,
                               'Out Time': out_hours,
                               'Out Airline': out_airlines,
                               'Return Time': in_hours,
                               'Return Airline': in_airlines,                           
                               'Price': prices_list})[cols]
    
    flights_df['timestamp'] = strftime("%Y-%m-%d-%H:%M") # so we can know when it was scraped
    return flights_df

    # Another option:
    '''
    # verify that db.csv is in folder
    try:
        with open("db.csv") as data_file:
            pass

    except FileNotFoundError:
        print("db.csv NOT PRESENT.\nGenerating db.csv .")
        empty_dictionary = {'arrival': list(), 
                            'carrier': list(), 
                            'departure': list(), 
                            'flight_date': list(),
                            'is_best_flight': list(), 
                            'price': list(), 
                            'route': list(), 
                            'website': list(), 
                            'url': list(),
                            'retrieved_on': list(), 
                            'retrieved_at': list()}
        empty_df = pd.DataFrame(empty_dictionary)
        empty_df.to_csv("db.csv")
    '''



# End of article ##############################################################################################################







    for item in results:
        Departure1 = item[1]
        latest_departure1 = time.strptime("13:30", "%H:%M")
        Departure2 = item[2]
        latest_departure2 = time.strptime("15:00", "%H:%M")  

        #if (Departure1 > latest_departure1) and (Departure2 > latest_departure2):
        print url
        print item[0] + ", " + time.strftime("%H:%M", Departure1) + ", " + time.strftime("%H:%M", Departure2)

    driver.close()



# --------------------------------------------------------------------------------------
# Source: https://github.com/lordmalcher/FlightPrices/blob/master/scraper.py



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

