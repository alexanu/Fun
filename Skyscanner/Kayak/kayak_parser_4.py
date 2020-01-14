
# Source: https://github.com/hongthana/flight_scraper
# Description:
# https://towardsdatascience.com/if-you-like-to-travel-let-python-help-you-scrape-the-best-fares-5a1f26213086



from time import sleep, strftime
from random import randint
from selenium import webdriver
from email.mime.multipart import MIMEMultipart
import pandas as pd
import smtplib
from selenium.webdriver.common.keys import Keys
from util.countdown import countdown




def page_scrape():
    xpath_sections = '//*[@class="section duration"]'
    sections = driver.find_elements_by_xpath(xpath_sections)
    sections_list = [value.text for value in sections]

    section_out_list = sections_list[::2]
    section_in_list = sections_list[1::2]
    
    # if you run into a reCaptcha, you might want to do something about it
    # you will know there's a problem if the lists above are empty
    # this if statement lets you exit the bot or do something else
    # you can add a sleep here, to let you solve the captcha and continue scraping
    # i'm using a SystemExit because i want to test everything from the start
    if section_out_list == []:
        raise SystemExit   
    
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




def load_more():

    try:
        more_results = '//a[@class="moreButton"]'
        driver.find_element_by_xpath(more_results).click()
        sleep(randint(45, 60))
    except:
        pass



from loading import write, backspace

def countdown(start, wait):
    for i in range(start, 0, -1):
        write(str(i))
        time.sleep(wait)
        backspace(len(str(i)))


def is_recaptcha_on_page(driver):
    try:
        if len(driver.find_elements_by_css_selector('[id$="-captcha"]')) > 0:
            return True
    except:
        return False

def try_clear_recaptcha(driver):
    print('\nNeed to clear reCaptcha 😡')

    recaptcha_retries_remaining = 18
    has_cleared_recaptcha = False

    while not has_cleared_recaptcha and recaptcha_retries_remaining > 0:
        print('{} attempts left. Retrying in... '.format(recaptcha_retries_remaining)),
        countdown(10, 1)
        print('')
        has_cleared_recaptcha = not is_recaptcha_on_page(driver)
        recaptcha_retries_remaining -= 1

    if recaptcha_retries_remaining == 0:
        print('Retry failed... closing 😔')
        raise SystemExit




def open_kayak(city_from, city_to, date_start, date_return):
    """
    City codes follow IATA
    Date format as YYYY-MM-DD
    """

    kayak_address = ('https://www.kayak.co.th/flights/' + city_from + '-' 
                     + city_to + '/' + date_start + '-flexible/' + date_return
                     + '-flexible?sort=bestflight_a')
    driver.get(kayak_address)
    sleep(randint(15, 20))
    
    driver.refresh()
    sleep(randint(50, 60))
    load_more()
    
    df_flights_best = page_scrape()
    df_flights_best['sort'] = 'best'
    sleep(randint(60, 80))
    
    table = driver.find_elements_by_xpath('//*[contains(@id,"FlexMatrixCell")]')
    price_table = [price.text.replace('฿ ', '').replace(',', '') for price in table]
    price_table = list(map(int, price_table))
    price_min = min(price_table)
    price_avg = sum(price_table)/len(price_table)
    
    cheapest = '//a[@data-code = "price"]'
    driver.find_element_by_xpath(cheapest).click()
    sleep(randint(60, 90))
    load_more()
    
    df_flights_cheap = page_scrape()
    df_flights_cheap['sort'] = 'cheap'
    sleep(randint(60, 80))
    
    fastest = '//a[@data-code = "duration"]'
    driver.find_element_by_xpath(fastest).click()
    sleep(randint(60, 90))
    load_more()
    
    df_flights_fast = page_scrape()
    df_flights_fast['sort'] = 'fast'
    sleep(randint(60, 80))
    
    result_price = df_flights_best.append(df_flights_cheap).append(df_flights_fast)
    result_price.to_excel('airfair//{}_flights_{}-{}_from_{}_to_{}.xlsx'.format(strftime("%Y-%m-%d_%H%M"), 
                          city_from, city_to, date_start, date_return), index = False)

    xpath_advice = '//div[contains(@id,"advice")]'
    advice = driver.find_element_by_xpath(xpath_advice).text
    xpath_predict = '//span[@class="info-text"]'
    predict = driver.find_element_by_xpath(xpath_predict).text
    print(advice + '\n' + predict)
    
    ignore = '¯\(°_O)/¯'
    if advice == ignore:
        advice = 'ไม่มีข้อมูล'
        
    username = 'YOUR_EMAIL@hotmail.com'
    password = 'YOUR_PASSWORK'
    
    server = smtplib.SMTP('smtp.outlook.com', 587)
    server.ehlo()
    server.starttls()
    server.login(username, password)
    msg = ('Subject: Flight Scraper\n\nCheapest Flight: {}\nAverage Price: {}\n\nRecommendation: {}\n\nEnd of message'.format(price_min, price_avg, (advice + '\n' + predict)))
    message = MIMEMultipart()
    message['From'] = username
    message['to'] = username
    server.sendmail(username, username, msg)


city_from = input('สนามบินต้นทาง : (เช่่น BKK) ')
city_to = input('สนามบินปลายทาง : (เช่น LHR) ')
date_start = input('วันที่ออกเดินทาง : (yyyy-mm-dd) ')
date_return = input('วันที่เดินทางกลับ : (yyyy-mm-dd) ')

# For debugging
#city_from = 'BKK'
#city_to = 'SIN'
#date_start = '2019-05-22'
#date_return = '2019-06-09'

for n in range(0, 5):
    open_kayak(city_from, city_to, date_start, date_return)
    sleep(60 * 60 * 4)
    
# ดาวน์โหลด "chrome driver" ที่ http://chromedriver.chromium.org/
# chromedriver_path = 'C:/{YOUR PATH HERE}/chromedriver_win32/chromedriver.exe'
# chromedriver_path = '/{YOUR PATH HERE}/chromedriver'

driver = webdriver.Chrome(executable_path = chromedriver_path)
sleep(2)
