
# Source: https://github.com/gaisin/weekend_flights

import requests
import json
import datetime
import time
import logging


weekends = [('2019-01-04', '2019-01-07'), ('2019-01-04', '2019-01-06')]
may_weekends = [
	('2019-04-27', '2019-05-01'),
	('2019-04-27', '2019-05-02'),
	('2019-04-27', '2019-05-03')]

cities_code_to_name_dict = {'ZSH': 'Санта-Фе', 'WNU': 'Ванума'}
countries_code_to_name_dict = {'FI': 'Финляндия', 'ME': 'Черногория'}
willing_countries = ['FI','ME','GB']
willing_cities = ['PRX', 'BML', 'BRU', 'LEJ',]
unwilling_destinations = ['KLF', 'PEZ', 'SGC', 'KUF', 'ESL', 'PES']



def print_flights(flights_data, notice='Билет'):
        for flight in flights_data:
            flight_info = '{notice}: Москва - {destination} за {price}р., {depart_date} ({depart_week_day})'\
                          '-{return_date} ({return_week_day})'.format(
                                    notice=notice,
                                    destination=flight['destination'],
                                    price=flight['value'],
                                    depart_date=flight['depart_date'],
                                    depart_week_day=flight['depart_week_day'],
                                    return_date=flight['return_date'],
                                    return_week_day=flight['return_week_day']
                            )
            print(flight_info)


def get_latest_flights(destination_codes, months):
    # cheapest flights for last 48 hours, 
    # documentation: https://support.travelpayouts.com/hc/ru/articles/203956163#02
    url='http://api.travelpayouts.com/v2/prices/latest'

    found_flights = []

    for key in months.keys():
        for code in destination_codes:
            destination = code
            payload = {
                'token': TRAVELPAYOUTS_TOKEN, 
                'origin': 'MOW',
                'destination': destination,
                'beginning_of_period': months[key],
                'period_type': 'month',  
                'limit': 1000
            }
            response = requests.get(url, params=payload)
            flights_raw = response.json()
            flights_data = flights_raw['data']
            found_flights += flights_data

    return found_flights


def find_weekend_flights(flights_data, days, max_value):
    found_flights = []

    for flight in flights_data:
        found_at = flight['found_at']
        try:
            found_at_datetime = datetime.datetime.strptime(found_at, '%Y-%m-%dT%H:%M:%S')
        except:
            found_at_datetime = datetime.datetime.strptime(found_at, '%Y-%m-%dT%H:%M:%S.%f')
        
        time_now = datetime.datetime.now()
        time_difference = time_now - found_at_datetime
        time_difference_in_hours = time_difference / datetime.timedelta(hours=1)

        if time_difference_in_hours <= 6 and flight['value'] <= max_value and flight['destination'] not in unwilling_destinations:
            for date in days:
                if flight['depart_date'] == date[0] and flight['return_date'] == date[1]:
                    depart_date_formatted = ''.join(reversed(flight['depart_date'][5:].split('-')))
                    return_date_formatted = ''.join(reversed(flight['return_date'][5:].split('-')))

                    depart_date_str_list = flight['depart_date'].split('-')
                    depart_date_int_list = [int(elem) for elem in depart_date_str_list]
                    depart_date = datetime.date(depart_date_int_list[0], depart_date_int_list[1], depart_date_int_list[2])
                    depart_week_day = depart_date.isoweekday()

                    return_date_str_list = flight['return_date'].split('-')
                    return_date_int_list = [int(elem) for elem in return_date_str_list]
                    return_date = datetime.date(return_date_int_list[0], return_date_int_list[1], return_date_int_list[2])
                    return_week_day = return_date.isoweekday()

                    origin = cities_code_to_name_dict[flight['origin']]
                    destination = cities_code_to_name_dict[flight['destination']]

                    link = 'https://www.aviasales.ru/search/{}{}{}{}1?marker=207849'.format(
                        flight['origin'],
                        depart_date_formatted,
                        flight['destination'],
                        return_date_formatted
                    )

                    flight_dict = {
                        'origin': origin,
                        'destination': destination,
                        'depart_date': flight['depart_date'],
                        'depart_week_day': weekday_names[depart_week_day],
                        'return_date': flight['return_date'],
                        'return_week_day': weekday_names[return_week_day],
                        'value': flight['value'],
                        'link': link
                    }
                    found_flights.append(flight_dict)
                    
    return found_flights


def main():
    months = {
        'february': '2019-02-01',
        'march': '2019-03-01',
        'april': '2019-04-01',
        'may': '2019-05-01',
        'june': '2019-06-01',
    }

    willing_destinations = willing_countries + willing_cities

    flights_data = get_latest_flights(willing_destinations, months)


    # для всех выходных
    max_weekend_ticket_price = 4000
    weekend_flights = find_weekend_flights(flights_data, weekends, max_weekend_ticket_price)
    weekend_notice = 'На выходные'
    print_flights(weekend_flights, weekend_notice)

    # для майских
    max_may_weekend_ticket_price = 8000
    may_weekend_flights = find_weekend_flights(flights_data, may_weekends, max_may_weekend_ticket_price)
    may_notice = 'На майские'
    print_flights(may_weekend_flights, may_notice)

    # на выходных в Уфу
    max_ufa_ticket_price = 3500
    ufa_weekend_flights = find_weekend_flights(ufa_flights_data, weekends, max_ufa_ticket_price)
    ufa_notice = 'В Уфу на выходные'
    print_flights(ufa_weekend_flights, ufa_notice)


if __name__ == '__main__':
    main()