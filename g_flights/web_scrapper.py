
# Third party imports
import pandas as pd
import bs4 as bs
from selenium import webdriver
from selenium.webdriver.support.ui import WebDriverWait
from selenium.webdriver.support import expected_conditions
from selenium.webdriver.common.by import By


DEPARTURE_CITIES = {
    'ORY': 'Orly',
    'CDG': 'CDG',
    'STR': 'Stuttgart'
}


def extract_price(html_price):
    price = html_price.split('\xa0')[0]
    price = price.split(' ')[-1]
    return price


def format_flight_data(html_text):
    html_list = html_text.text.split('.')
    flight_data = {
        'price': "{}".format(extract_price(html_list[3])),
        "departure_time": html_list[1][-5:],
        "arrival_time": html_list[2][-5:]
    }
    return flight_data



def main():
    # init attributes
    weekend_options_df = pd.DataFrame()

    # max price in €
    max_price = 150

    # weekend
    departure_date = '2019-04-05'
    arrival_date = '2019-04-07'

    debug_write_html = False

    # loop over depeatures cities
    for departure_code in [
        # 'ORY', 
        # 'CDG',
        'STR'
    ]:
    
        print("\n{}: looking for flights...\n".format(DEPARTURE_CITIES[departure_code].upper()))  
        
        # init cities list
        city_df = pd.read_csv('stuttgart_direct_flights_destinations.csv')

        # init driver
        driver = webdriver.Chrome()

        # loop arrival cities
        for index in city_df.index:
            arrival_city = city_df.loc[index, 'name']
            arrival_code = city_df.loc[index, 'code']

            # format search URL  
            url = 'https://www.google.com/flights?hl=fr#flt={dc}.{ac}.{dd}*{ac}.{dc}.{ad};c:EUR;e:1;s:0*0;p:{mp}00.2.EUR;so:1;sd:1;t:f'.format(
                dc=departure_code,
                ac=arrival_code,
                dd=departure_date,
                ad=arrival_date,
                mp=max_price
            )

            # get HTML          
            driver.get(url)

            flight_list_class_name = 'gws-flights-results__result-list'
            no_flight_class_name = "gws-flights-results__error-msg"

            try:
                WebDriverWait(driver, 4).until(expected_conditions.presence_of_element_located((By.CLASS_NAME, no_flight_class_name)))
                print('{}: no result'.format(arrival_city))
                continue

            except Exception:
                try:
                    WebDriverWait(driver, 10).until(expected_conditions.presence_of_element_located((By.CLASS_NAME, flight_list_class_name)))
                    print('{}: scrapping flights...'.format(arrival_city))

                    # Wrangle HTML
                    raw_html = driver.execute_script('return document.documentElement.outerHTML')
                    html = bs.BeautifulSoup(raw_html, 'html.parser')

                    if debug_write_html:
                        with open('html_contents/content.html', 'w', encoding="utf-8") as html_file:
                            html_file.write(html.prettify())

                    options_df = pd.DataFrame()

                    # Parse data
                    for option in html.find_all('jsl'):
                        if option.get('jstcache') == '8940':
                            flight_data = format_flight_data(option)
                            options_df = options_df.append(flight_data, ignore_index=True)

                    # save data
                    if not options_df.empty:
                        options_df['departure_code'] = departure_code
                        options_df['arrival_code'] = arrival_code 
                        print(options_df[[
                            'departure_code',
                            'departure_time',
                            'arrival_time',
                            'arrival_code',
                            'price',
                        ]])

                    weekend_options_df = weekend_options_df.append(options_df)
                    weekend_options_df.reset_index(drop=True, inplace=True)

                    weekend_options_df.to_csv('departure_{dd}_from_{dc}_weekend_options.csv'.format(
                        dd=departure_date,
                        dc=departure_code
                    ))
                
                except Exception:
                    print('TimeoutError')

    driver.quit()


if __name__ == '__main__':
    main()
