

from selenium import webdriver
from selenium.webdriver.common.action_chains import ActionChains
from selenium.webdriver.common.keys import Keys
from random import randint
from time import sleep


path_to_chromedriver = '/Users/arian/WorkSpace/dev/scraper/drivers/chromedriver'
driver = webdriver.Chrome(executable_path=path_to_chromedriver)
sleep(randint(8, 10))

def load_more():
    try:
        more_results = '//a[@class="moreButton"]'
        driver.find_element_by_xpath(more_results).click()
        sleep(randint(25, 30))
    except Exception as e:
        pass


def start_kayak(city_from, city_to, date_start, date_end):
    '''
        city_from, city_to : string(airport IATA code, 3 letters)
        date_start, date_end : string(date format is YYYY/MM/DD)
    '''

    full_URL = ('https://www.kayak.com/flights/' + city_from + '-' + city_to +
                '/' + date_start + '-flexible/' + date_end + '-flexible?sort=bestflight_a')

    # path_to_chromedriver = '/Users/arian/WorkSpace/dev/scraper/drivers/chromedriver'
    # driver = webdriver.Chrome(executable_path=path_to_chromedriver)
    # sleep(randint(8, 10))
    driver.get(full_URL)
    driver.maximize_window()
    sleep(randint(8, 10))
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
    sleep(randint(60, 95))

def page_scrape():
    result_list = driver.find_elements_by_xpath('//*[@id="searchResultsList"]/div')
    sections = [value.text.strip() for value in result_list]
    for section in sections:
        print(section)
        print()

city_from = 'YUL'
city_to = 'IST'
date_start = '2020-01-22'
date_end = '2020-02-18'
start_kayak(city_from, city_to, date_start, date_end)