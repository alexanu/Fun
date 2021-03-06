# Source: https://github.com/Shivanshu26shiv/aircheapy/blob/master/aircheapy.py


from selenium import webdriver
from datetime import datetime
from datetime import timedelta
from selenium.webdriver.common.keys import Keys
from selenium.common.exceptions import (ElementClickInterceptedException,
                                        TimeoutException)
from selenium.webdriver.chrome.options import Options
from selenium.webdriver.support.ui import WebDriverWait
from selenium.webdriver.support import expected_conditions as EC
from selenium.webdriver.common.by import By
from functools import partial
from multiprocessing.pool import ThreadPool
import pprint
import geocoder
import requests
import time
import sys
import os

os.environ["LANG"] = "en_US.UTF-8"

options = Options()
options.add_argument("--headless")
options.add_argument('--disable-gpu')
options.add_argument('--no-sandbox')
options.add_argument("--start-maximized")
# options.add_argument("--disable-infobars")
options.add_argument("--disable-extensions")
options.add_argument('--disable-dev-shm-usage')        

# prefs = {'profile.managed_default_content_settings.images':2, 'disk-cache-size': 0}
prefs = {'profile.managed_default_content_settings.images':2}
options.add_experimental_option("prefs", prefs)

# args = ["hide_console", ]
        
def calculate(to_single_iata):

    # driver = webdriver.Chrome(options=options, executable_path=r'C:\Users\Xarvis-PC\Desktop\chromedriver_win32\chromedriver.exe', service_args=args)
    driver = webdriver.Chrome(options=options, executable_path=r'C:\Users\Xarvis-PC\Desktop\chromedriver_win32\chromedriver.exe')

    def isvisible(attrib_type, locator, timeout=3):
        try:
            if attrib_type == 'ID':
                WebDriverWait(driver, timeout).until(EC.visibility_of_element_located((By.ID, locator)))
            elif attrib_type == 'TAG_NAME':
                WebDriverWait(driver, timeout).until(EC.visibility_of_element_located((By.TAG_NAME, locator)))
            elif attrib_type == 'CLASS_NAME':
                WebDriverWait(driver, timeout).until(EC.visibility_of_element_located((By.CLASS_NAME, locator)))
            return True
        except TimeoutException:
            return False
    
    try:
        final_output = {}
        
        from_single_iata=list(from_IATA.keys())[0]
        url = 'https://www.happyeasygo.com/flights/'+from_single_iata+'-'+to_single_iata
        url_params = '?adults='+str(adults)+'&cabinClass='+cabinClass
        # print('url+url_params:', url+url_params)
        driver.get(url+url_params)
        time.sleep(10)
        # driver.refresh()
        driver.execute_script("location.reload(true);")

        if not isvisible('TAG_NAME', 'body', 5):
            return {}
        
        webdriver.ActionChains(driver).send_keys(Keys.ESCAPE).perform()
        webdriver.ActionChains(driver).send_keys(Keys.HOME).perform()

        if round_trip:
            trip_type = from_IATA[from_single_iata]+'->'+to_IATA[to_single_iata]+'->'+from_IATA[from_single_iata]
        else:
            trip_type = from_IATA[from_single_iata]+'->'+to_IATA[to_single_iata]
        
        ld={}
        def calender(id_name):

            if isvisible('ID', id_name, 10):
                el = driver.find_element_by_id(id_name)
                actions = webdriver.ActionChains(driver)
                try:
                    actions.move_to_element(el).click().perform()
                except ElementClickInterceptedException:
                    print('Issue:', driver.current_url)
                    return {}
                except:
                    print(222)
            else:
                print('Poor connection!')
                return {}
            
            #    print('Poor connectivity or unknown error at '+driver.current_url+' ... skipping')
            #    return {}
                
            # not working
            # el=driver.find_element_by_id(id_name)
            # driver.execute_script("arguments[0].click();", el)
            
            time.sleep(5)
            l=[]
            # print('>>>', driver.current_url)
            # print('>>', len(driver.find_elements_by_class_name(r" ")))
            
            for c, e in enumerate(driver.find_elements_by_xpath('//td[@data-handler="selectDay"]')):
                # print(c, e)
                
                try:
                    if e.get_attribute("title") != '':
                        # print('Airfare:', e.get_attribute("title"))
                        l.append(((datetime.now() + timedelta(days=c)).strftime("%Y%m%d"), int(float(e.get_attribute("title")))))
                except:
                    print('Airfare issue:', e.get_attribute("title"))
                    continue

                if c==scan_till_N_days:
                    break
                
            ld[trip_type] = l
            # print('ld:', ld)
            return ld

        try:
            depart  = calender('D_date')[trip_type]
            if round_trip:
                arrival = calender('R_date')[trip_type]
        except KeyError:
            driver.quit()
            return

        d={}
        total_price = 0

        # print('depart:', depart)
        # print('arrival:', arrival)
        
        if round_trip:
            for i in depart:
                if depart_on_weekend:
                    if datetime.strptime(i[0], "%Y%m%d").weekday() < 5:
                        continue
                for j in arrival:
                    if arrive_on_weekend:
                        if datetime.strptime(j[0], "%Y%m%d").weekday() < 5:
                            continue
                    total_price = (i[1]+j[1]) * adults
                    day_diff = (datetime.strptime(j[0], "%Y%m%d")-datetime.strptime(i[0], "%Y%m%d")).days
                    # print('total_price:', total_price, day_diff, i[0], j[0])
                    if 0 <= day_diff <= maxGap and day_diff >= minGap and i[0] <= j[0] and total_price <= maxINR:
                        d[i[0]+'-'+j[0]] = total_price
        else:
            for i in depart:
                if depart_on_weekend:
                    if datetime.strptime(i[0], "%Y%m%d").weekday() < 5:
                        continue
                total_price = (i[1]) * adults
                # print('total_price:', total_price)
                if total_price <= maxINR:
                    d[i[0]] = total_price

        # if len(d)>0:
        # print('d:', d)
        # print('Path '+trip_type+' available...')

        new_d = {}
        if d != {}:
            d=sorted(d.items(), key=lambda item: item[1])[:cheapest_N_results]

            for date_strings, total_cached_price in d:
                cached_price = total_cached_price / adults
                from_str = datetime.strptime(date_strings.split('-')[0], '%Y%m%d')

                if round_trip:
                    to_str = datetime.strptime(date_strings.split('-')[1], '%Y%m%d')
                    new_url = url+'/'+from_str.strftime("%Y-%m-%d")+'-'+to_str.strftime("%Y-%m-%d")+url_params
                    key = (from_str.strftime("%d %B %Y (%A)")+' to '+to_str.strftime("%d %B %Y (%A)"))
                else:
                    new_url = url+'/'+from_str.strftime("%Y-%m-%d")+url_params
                    key = from_str.strftime("%d %B %Y (%A)")
                    
                # print('new_url:', new_url)
                try:
                    driver.get(new_url)
                    time.sleep(4)
                    driver.execute_script("location.reload(true);")
                    key = key+' ['+driver.current_url+']'

                    # print(driver.find_elements_by_class_name('fpr')[0])
                    
                    # class_name = 'fpr'
                    class_name = 'fpr' if round_trip else 'price-origin'
                    
                    if not isvisible('CLASS_NAME', class_name, 20):
                        print('Poor connection... at '+new_url, class_name)
                        continue
            
                    new_price = driver.find_elements_by_class_name(class_name)[0].text
                    new_price = eval((new_price.strip()).replace(',',''))
                    value = new_price
                except:
                    driver.refresh()
                    time.sleep(4)
                    if not isvisible('CLASS_NAME', 'no-search-result', 10):
                        print('Poor connection.. at '+new_url)
                        continue

                    ele = driver.find_element_by_id('no_result')

                    if ele.get_attribute("style").replace(' ', '').strip() != "display:none;":
                        print('No flight data-key:', key, ele.get_attribute("style"))
                        continue
                    else:
                        key = key+' (cached)'
                        value = cached_price

                if value * adults <= maxINR:
                    new_d[key] = value*adults
                    
            new_d=sorted(new_d.items(), key=lambda item: item[1])
            # print('new_d:', trip_type, new_d)
            if new_d != []:
                final_output[trip_type] = new_d
        # driver.quit()
        return
    
    finally:
        if final_output != {}:
            pprint.pprint(final_output)
        driver.quit()
        return


def aircheapy(params, get_current_ips_IATA=False, use_threading=True):
    
    global scan_till_N_days
    global cheapest_N_results
    global maxINR
    global cabinClass
    global adults
    global maxGap
    global minGap
    global from_IATA
    global to_IATA
    global round_trip
    global depart_on_weekend
    global arrive_on_weekend

    end_time = datetime.now()
    
    to_IATA = params['to_IATA']

    if 'scan_till_N_days' not in params.keys(): scan_till_N_days = 30
    else: scan_till_N_days = params['scan_till_N_days']
    if 'cheapest_N_results' not in params.keys(): cheapest_N_results = None
    else: cheapest_N_results = params['cheapest_N_results']
    if 'maxINR' not in params.keys(): maxINR = 9999999
    else: maxINR = params['maxINR']
    if 'cabinClass' not in params.keys(): cabinClass = 'Economy'
    else: cabinClass = params['cabinClass']
    if 'adults' not in params.keys(): adults = 1
    else: adults = params['adults']
    if 'round_trip' not in params.keys(): round_trip = False
    else: round_trip = params['round_trip']
    if 'depart_on_weekend' not in params.keys(): depart_on_weekend = False
    else: depart_on_weekend = params['depart_on_weekend']


    if round_trip:
        if 'maxGap' not in params.keys(): maxGap = scan_till_N_days-2
        else: maxGap = params['maxGap']
        if 'minGap' not in params.keys(): minGap = 0
        else: minGap = params['minGap']
        if 'arrive_on_weekend' not in params.keys(): arrive_on_weekend = False
        else: arrive_on_weekend = params['arrive_on_weekend']
    else:
        maxGap = scan_till_N_days-2
        minGap = 0
        arrive_on_weekend = False

    from_IATA = params['from_IATA']
    
    dup_check = list(from_IATA.keys())[0]
    if dup_check in list(to_IATA.keys()):
        print('From-To cities same. Skipping:'+to_IATA.pop(dup_check))

    print('Params:', '\n')
    pprint.pprint(params)
    print('')
    
    if to_IATA == {}:
        print('From-To cities same. Exiting.')
        return

    try:
        if use_threading:
            func = partial(calculate)
            pool = ThreadPool(processes=3)
            pool.map(func, list(to_IATA.keys()))
            pool.close()
            pool.join()
        else:
            for to_single_iata in to_IATA.keys():
                calculate(to_single_iata)     
    finally:
        # pp.pprint(final_output)
        print('\nStart:', end_time, ' Stop:', datetime.now())


budget_dict = {'DXB': 'Dubai', 'BKK': 'Bangkok', 'SIN': 'Singapore',
                   'PBH': 'Paro', 'KTM': 'Kathmandu', 'KUL': 'Sepang_Malaysia', 'SGN': 'Ho_Chi_Vietnam',
                   'CAI': 'Cairo', 'NBO': 'Nairobi', 'SEZ': 'Seychelles','PNH': 'Combodia', 'AMM':'Queen_Jordan',
                    'DPS': 'Denpasar_Indonesia', 'SAW': 'Istanbul'}

luxury_dict = {'LHR': 'London', 'CDG': 'Paris', 'HKG': 'Hong Kong', 'FCO': 'Rome',
                   'DXB': 'Dubai', 'SIN': 'Singapore', 'PVG': 'Shanghai', 'KUL': 'Sepang_Malaysia', 
                   'SEZ': 'Seychelles', 'HND':'Tokyo'}

params = {
        'maxINR': 30000,
        'cheapest_N_results': 3,
        'scan_till_N_days': 30,
        'adults': 2, 
        'cabinClass': 'Economy', # Economy, Business, First, Premium Economy
        'from_IATA': {'BLR': 'Bengaluru'},
        'to_IATA': {'DXB': 'Dubai', 'BKK': 'Bangkok'},
        'depart_on_weekend': False,
        'round_trip': True,
        # below 3 flags are ignored if round_trip flag is off
        'minGap': 3, 
        # 'maxGap': 3, 
        'arrive_on_weekend': True
        }


aircheapy(params, get_current_ips_IATA=False, use_threading=True)
