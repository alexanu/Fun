import time
import datetime
import os.path as paths
from selenium import webdriver
from selenium.webdriver.common.by import By
import re
import csv

# Pass: String in the format 'US$1,000'
# Returns: String parsed to integer

class GoogleFlight:
    def __init__(self):
        pass

    def get_flights(self, driver, departing, destination, tripLen, lowBound=datetime.date.today(), highBound=datetime.date.today()):
        # Initializations
        self.driver = driver
        self.open_url(departing, destination, tripLen, lowBound, highBound)
        flights = None
        try:
            self.sort_ascindingly()
            self.load_all_flights()
            xpath = '//*[contains(@class, "gws-flights-results__result-item gws-flights__flex-box")]'
            flights = self.get_all_flights(xpath)
        except Exception:
            flights = []
        print('----------------------------------------')
        print(destination)
        print('number of flights : ', str(len(flights)))
        
        if len(flights) > 0:
            counter = 0
            for flight in flights:
                self.expand_flight(flight)
                price               = self.get_price(flight)
                departing_airport   = self.get_departing_airport(flight)
                destination_airport = self.get_destination_airport(flight)
                depart_date         = self.get_departDate(flight)
                url                 = self.get_url(flight)
                row_dictionary = {
                    'Price'                 : price,
                    'Departing airport'     : departing_airport,
                    'Destination airport'   : destination_airport,
                    'Depart date'           : depart_date,
                    'URL'                   : url,
                }
                self.write_csv(row_dictionary)
            #returns the best deal for a given destination
            return ''

    def open_url(self, departing, destination, tripLen, lowBound=datetime.date.today(), highBound=datetime.date.today()):
        departure_time = lowBound  # Initial departure for URL
        # Initial return for URL
        return_time = lowBound + datetime.timedelta(tripLen)
        if lowBound is datetime.date.today() and highBound is datetime.date.today():
            # preserves the count accuracy
            departure_time += datetime.timedelta(40)
            return_time += datetime.timedelta(40)
        URL_DATE_FORMAT = "%Y-%m-%d"
        URL = 'https://www.google.com/flights/#search;f={};t={};d={};r={}'.format(
            departing, destination, departure_time.strftime(URL_DATE_FORMAT), return_time.strftime(URL_DATE_FORMAT))
        print(URL)
        self.driver.get(URL)

    def get_all_flights(self, xpath):
        try:
            time.sleep(1)
            return self.driver.find_elements_by_xpath(xpath)
        except Exception:
            return []

    def sort_ascindingly(self):
        xpath = '/html/body/div[2]/div[2]/div[2]/div[3]/div/jsl/div/div[2]/main[4]/div[7]/div[1]/div[4]/div[1]/div[2]/div/div/dropdown-menu/div/div[1]'
        sort_div = self.driver.find_element(By.XPATH, xpath)
        sort_div.click()
        time.sleep(1)
        by_price_button = self.get_menu_item()
        by_price_button.click()
        time.sleep(1.5)

    def get_menu_item(self):
        xpath = '//*[contains(@class, "gws-flights-results__sort-menu-option")]'
        menu_items = self.driver.find_elements(By.XPATH, xpath)
        for menu_item in menu_items:
            #if menu_item.text == 'السعر':
            if menu_item.text == 'Price':
                return menu_item

    def load_all_flights(self):
        xpath = '//*[contains(@class, "gws-flights-results__dominated-link")]'
        self.driver.find_element(By.XPATH, xpath).click()
        time.sleep(1)

    def get_price(self, flight):
        xpath = './/*[contains(@class, "flt-subhead1 gws-flights-results__price")]'
        try:
            price_divs = flight.find_elements_by_xpath(xpath)
        except Exception:
            print('the same bug.')
            return ''
        digits = re.findall(r'\d+', price_divs[1].text)
        num_string = ''
        for digit in digits:
                num_string = num_string + digit
        # use strings for now because of arabic
        #     prices.append(int(num_string))
        return arabic_to_english(num_string)


    def arabic_to_english(string):
        arabic = ['٠', '١', '٢', '٣', '٤', '٥', '٦', '٧', '٨', '٩']
        english = ['0', '1', '2', '3', '4', '5', '6', '7', '8', '9']
        for i in range(10):
            string = string.replace(arabic[i], english[i])
        return string


    def expand_flight(self, flight):
        flight_xpath = '//*[contains(@class, "gws-flights-results__more z1asCe QFl0Ff")]'
        expand = flight.find_element(By.XPATH, flight_xpath)
        expand.click()
        time.sleep(0.5)

    def get_departing_airport(self, flight):
        xpath = './/*[contains(@class, "gws-flights-results__leg-arrival gws-flights__flex-box flt-subhead1Normal")]'
        # element = flight.find_elements_by_xpath(xpath)[2]
        # element = element.find_element_by_tag_name('span')
        # return element.text
        return self.text_from_xpath(xpath, flight)

    def get_destination_airport(self, flight):
        xpath = './/*[contains(@class, "gws-flights-results__leg-departure gws-flights__flex-box flt-subhead1Normal")]'
        return self.text_from_xpath(xpath, flight)

    def get_departDate(self, flight):
        xpath = './/*[contains(@class, "gws-flights__flex-filler gws-flights-results__itinerary-details-heading-text")]'
        return self.text_from_xpath(xpath, flight)

    def get_url(self, flight):
        xpath = './/*[contains(@class, "gws-flights__flex-filler gws-flights-results__itinerary-details-heading-text")]'
        attribute = 'href'
        return self.attribute_from_xpath(xpath, flight, attribute)

    def attribute_from_xpath(self, xpath, element, attribute):
        return element.find_element_by_xpath(xpath).get_attribute(attribute)

    def text_from_xpath(self, xpath, element):
        print(element.find_element_by_xpath(xpath).text)
        return element.find_element_by_xpath(xpath).text

    def write_csv(self, row_dictionary):
        csv_filename = 'data.csv'
        fieldnames = ['Price', 'Departing airport', 'Destination airport', 'Depart date', 'URL']
        csv_file = open(csv_filename, 'a')
        csv_file_writer = csv.DictWriter(csv_file, fieldnames=fieldnames)
        csv_file_writer.writerow(row_dictionary)
        csv_file.close()

    def flightObject(self, flight):
        flight_object = None
        try:
            expand_flight(flight)
            departing_ariport = get_departing_airport(flight)
            detination_ariport = get_destination_airport(flight)
            depart_date = get_departDate(flight)
            return_date = get_returnDate(flight)
            flight_object = Flight(
                dep=departing_ariport, dest=get_destination_airport, deptDate=depart_date, retDate=return_date)
        except Exception:
            pass
        return flight_object