# Source: https://github.com/FAD28/Fs-sc-EXP/blob/ded5df09d6c471dc162b5ab9edaf3b435cc4bd17/cheap_flights.py


from selenium import webdriver
from selenium.webdriver.common.keys import Keys
import pandas as pd
import time
from copy import copy
import datetime

# LINKS:
# https://www.tuifly.com/flugangebote?tts=GVABCNc~20191119-VY6198-NonX3~20191126-VY6201-NonX3|STRPMIc~20191201-X32172-X3Pure~20191208-VY3440-NonX3
# https://www.tuifly.com/flugangebote
# https://www.kayak.de/flugangebote
# https://www.statravel.de/aktuelle-flugangebote.htm
# https://www.lufthansa.com/de/de/fluege
df = pd.DataFrame
# self.tui_dep_time = []
# self.tui_ret_time = []
# Listen bsp: self.dep_times_list = []

def compile_data_tui():
    j = 0
    while j < 61:
        j += 1
        try:

            t_destiny = driver.find_elements_by_xpath( f"/html/body/div[2]/main/section[2]/div/div/div[3]/div[{j}]/label[1]/div[2]/div[1]/span[2]")
            tui_destiny = [element.text for element in t_destiny]

            t_price = driver.find_elements_by_xpath(f"/html/body/div[2]/main/section[2]/div/div/div[3]/div[{j}]/label[1]/div[2]/div[2]/div")
            tui_price = [element.text for element in t_price]

            t_departure = driver.find_elements_by_xpath(f"/html/body/div[2]/main/section[2]/div/div/div[3]/div[{j}]/label[1]/div[2]/div[1]/span[1]")
            tui_departure = [element.text for element in t_departure]

        except:
            print("Konnte nicht durchgeführt werden")
            pass

def tui_chooser():
    i = 0
    while i < 61:
        try:
            i += 1
            try:
                show_more = driver.find_element_by_xpath(f"/html/body/div[2]/main/section[2]/div/div/div[3]/div[{i}]/label[2]")
                show_more.click()
                time.sleep(3)
                # driver.execute_script("window.scrollTo(500, 1000)")
                time.sleep(3)
            except:
                # print("jetzt wird nach css gesucht")
                show_more2 = driver.find_element_by_css_selector(f"body > div.page.underlay-spacer.js-underlay-spacer > main > section.box > div > div > div.js-trip-tile-list > div:nth-child({i}) > label.trip-tile__button")
                driver.execute_script("arguments[0].click();", show_more2)
        except:
            print("Alles wurde geöffnet")


links = ["https://www.tuifly.com/flugangebote", "https://www.kayak.de/flugangebote"]

for item in links:
    chromedriver = "/Users/Fabi/Downloads/chromedriver"
    driver = webdriver.Chrome(chromedriver)
    print(item)
    time.sleep(2)
    driver.get(item)
    time.sleep(2)

    # TUI
    if item == links[0]:
        # tui_chooser()
        # time.sleep(3)
        print("**********************")
        # time.sleep(3)
        compile_data_tui()
    else:
        print("ist kein Tui-link")
        pass

    time.sleep(5)
    driver.close()
    time.sleep(2)