# Source: https://github.com/smithers63/fly-range/blob/master/get_flight.py


from selenium import webdriver
from selenium.webdriver.common.by import By
from selenium.webdriver.support.ui import WebDriverWait
from selenium.webdriver.support import expected_conditions as EC
from selenium.webdriver.support.expected_conditions import staleness_of
from selenium.webdriver.support.ui import Select
from selenium.common.exceptions import TimeoutException, StaleElementReferenceException
from random import randint
from selenium.webdriver.common.action_chains import ActionChains
from datetime import datetime, timedelta, date
import os, stat
import shutil
import time
import sys
import math
import cgi
import pdb
import re
import glob


stashPrice = 0
driver = webdriver.Firefox()
wait = WebDriverWait(driver, 30)
bestPriceURL = ''

def refresh(url=driver.current_url):
    driver.get(url)

def rmFiles(dir='images', ext='.png'):
    files = glob.glob(dir + '/*' + ext)

    for f in files:
        os.remove(f)

def performSearch():
    global stashPrice

    driver.get('https://www.google.com/flights#flt=/m/02_n7.BZN.2020-01-11*BZN./m/02_n7.2020-01-15;c:USD;e:1;so:1;sd:1;t:f')
    # driver.get('https://www.google.com/flights#flt=/m/02_n7./m/0bld8.2019-08-30*/m/0bld8./m/02_n7.2019-09-03;c:USD;e:1;so:1;sd:1;t:f') # POLAND
    # driver.get("https://www.google.com/flights#flt=/m/01_d4./m/07dfk.2019-11-01*/m/07dfk./m/01_d4.2019-11-02;c:USD;e:1;so:1;sd:1;t:f") JAPAN
    driver.execute_script('''
        var guinnea = document.querySelector("div");
        guinnea.innerHTML = guinnea.innerHTML +
        "<style> * { -o-transition-property: none !important; -moz-transition-property: none !important; -ms-transition-property: none !important; -webkit-transition-property: none !important; transition-property: none !important; } </style>";
    ''')

    def compareResult():
        global stashPrice
        global bestPriceURL

        def getResultPrice():
            try:
                wait.until(EC.element_to_be_clickable((By.CSS_SELECTOR, 'div.flt-subhead1.gws-flights-results__price')))
                resultsEle = driver.find_element_by_css_selector('div.flt-subhead1.gws-flights-results__price')
                resultsEle.text

                if resultsEle and resultsEle is not None and resultsEle.text:
                    return resultsEle
                else:
                    raise Exception('None type object')
            except (TimeoutException, StaleElementReferenceException, Exception) as e:
                refresh()
                getResultPrice()

        resultPriceEle = getResultPrice()
        roundTripStr = re.sub('[^\d]', '', resultPriceEle.text).strip()
        roundTripPrice = (int(roundTripStr) if roundTripStr else 0)

        if roundTripPrice:
            priceStamp = 'images/best_price_' + str(int(time.time())) + '.png'

            if roundTripPrice < stashPrice:
                stashPrice = roundTripPrice
                driver.implicitly_wait(5)
                bestPriceURL = driver.current_url
                rmFiles()
                driver.save_screenshot(priceStamp)
            elif roundTripPrice == stashPrice:
                driver.save_screenshot(priceStamp)

        return [roundTripPrice, resultPriceEle]

    stashPrice = compareResult()[0]

    if stashPrice:
        for dept in range(0, 500):
            currURL = driver.current_url
            replStart = currURL.rfind('.') + 1
            lastDate = currURL[replStart:(replStart + 10)]
            firstDateIdx = currURL.index(currURL.split('.')[4])
            firstDate = currURL[firstDateIdx:(firstDateIdx + 10)]
            firstDateObj = datetime.strptime(firstDate, '%Y-%m-%d') + timedelta(days=1)

            driver.get(
                currURL
                    .replace(firstDate, str(firstDateObj).split(' ')[0])
                    .replace(lastDate, str(firstDateObj + timedelta(days=2)).split(' ')[0])
            )

            for rtn in range(0, 5):
                try:
                    returnEle = compareResult()[1]
                    nextBtn = driver.find_elements_by_css_selector('.gws-flights-form__next')[1]
                    nextBtn.click()
                    wait.until(
                        EC.staleness_of(returnEle)
                    )
                except:
                    print('fail')


    return stashPrice

currLow = performSearch()

if currLow:
    print('The lowest price found was: ' + '${:,.2f}'.format(currLow))
    print(bestPriceURL)
else:
    print('Price not found, adjust date range.')

driver.close()





import requests
import json
import sys
import urllib
from datetime import datetime, timedelta, date

def strDate(dateObj, addDays=0):
    return str(datetime.strptime(str(dateObj), '%Y-%m-%d') + timedelta(days=addDays)).split(' ')[0]

params = {'from': '', 'to': '', 'spread': 5, 'seek': 3, 'range': 100, 'start': strDate(date.today())}
args = sys.argv
lowPrice = 0

for key, arg in enumerate(args):
    stripVar = arg.replace('--', '')

    if stripVar in params:
        params[stripVar] = args[key + 1].upper()

if params['from'] and params['to']:
    for day in range(0, int(params['range'])):
        arrive = strDate(params['start'], params['spread'])

        for dayOut in range(0, int(params['seek']) + 1):
            asyncParams = '[[[[[[null,[["' + params['from'] + '",0]]],[null,[["' + params['to'] + '",0]]],["' + params['start'] + '"]],[[null,[["' + params['to'] + '",0]]],[null,[["' + params['from'] + '",0]]],["' + strDate(arrive, dayOut) + '"]]],null,[],null,null,null,null,1,null,2,null,null,null,null,null,true],[[[null,[],[],[],[],null,[],[]],[null,[],[],[],[],null,[],[]]]],null,"USD",null,[]],[0]]'
            url = 'http://www.google.com/async/flights/search?async=data:' + urllib.quote(asyncParams.encode("utf-8")) + ',s:s,tfg-bgr:%5B%22!HR6lHj9C6Hein_9L_R5YnfVDgE9EmCQCAAAAN1IAAAAJmQGTwQN3PvwWZNvYd4HMWByoNCmygBioNH0KHeMzTg3zT__t46hHogAda8OaO-nEj9FpftdXY1y8HoxSTYxpYyBzRAvaW5FrmbCC4WnG6qC-pfnBbliWYUPSRknXCdgMID-vTgG1kIK_U3hQs8NLjTokU9EZ_dPiSXFbDeEbFv1KwVup7HkmEn_HUhtw4nz6as03ar5dTNxHf19oS6N5UzKmo-brJqdXtoaVLw7HkgWMgXXV9U89iqcfEMoIFwjxFVFYAj9N9UJXIvJIo4lr5TyBXIqo4v1IK2I6_zlSYBJNOg_Zt2FMg1kWfpSVC6Q0lBUXVE1mzr5HX85lWT3nR49UHEpgYetX8X7j2RCWTKIKlwAy0VZOTcWgYAB2WEQtleR1bT-0_iONaJQJfnWJ1Is8V6oNcoMptze96RLhuzbxg0khJAF6fBwEpLqSOEsvBPmLHduiwOdD74ooyr5bSWSqtDfaZ3EyY6dTek_yWU0glI9YSPyfySmogaIZxhLOoX5yNyBTOQ0P96XAwM7d8Vd3fFA_zA%22%2Cnull%2Cnull%2C10%2C62%2Cnull%2Cnull%2C0%5D,_fmt:jspb'
            content = requests.get(url, allow_redirects=True).content
            flightData = json.loads(content.replace(content.split('\n')[0], '', 1))

            def recursiveArray(childAry):
                global lowPrice

                for item in childAry:
                    if type(item) == list:
                        recursiveArray(item)
                        
                    if type(item) == unicode and '$' in item and 'USD' in childAry:
                        thisLow = [priceInt for priceInt in childAry if type(priceInt) == int][0]

                        if not lowPrice or thisLow < lowPrice:
                            lowPrice = thisLow
                            print childAry, params['start'], strDate(arrive, dayOut)
                        if thisLow == lowPrice:
                            print childAry, params['start'], strDate(arrive, dayOut)

            recursiveArray(flightData[flightData.keys()[0]])

        params['start'] = strDate(params['start'], 1)