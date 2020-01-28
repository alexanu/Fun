import argparse
from pprint import pprint as pp
import requests
from requests.packages.urllib3.util.retry import Retry
from requests.adapters import HTTPAdapter
import log
from datetime import datetime
from NBRB import convert_currency_into_BYN
import json


filename = "api-logs.txt"

def log_raw_request(request, tag):
    with open(filename, "a") as file:
        file.write('Request_{}: {}\n'.format(tag, request.method + ' ' + request.url))


def log_raw_response(response, tag):
    with open(filename, "a") as file:
        file.write('Response_{}: {}\n'.format(tag, "URL " + response.url + '; STATUS CODE: ' + str(response.status_code)))

def reset_file():
    file = open(filename, "w+")
    file.truncate(0)
    file.close()


# retry request up to five times if 500/503 status codes are returned
session = requests.Session()
retries = Retry(total=5, backoff_factor=0.1, status_forcelist=[500, 503])
session.mount('https://', HTTPAdapter(max_retries=retries))
ticketing_data_sources = ['gatwick-connect', 'dohop-connect', 'easyjet-connect']


def requests_get(url):
    request = requests.Request('GET', url, params={'partner':'picky'})
    prepared = request.prepare()
    log.log_raw_request(prepared, 'kiwi')
    response = session.send(prepared)
    log.log_raw_response(response, 'kiwi')
    if response.status_code == requests.codes.ok:
        return response.json()
    else:
        return None


def get_all_flights(response):
    pp(response.keys())
    pp(response['currency'])
    itineraries = response['data']
    return itineraries


def get_all_available_tickets_and_currency_code(city_from, city_to, date_departure, date_return):
    data_departure_formatted = date_departure.strftime('%d/%m/%Y')
    url_pattern = 'https://api.skypicker.com/flights?flyFrom={}&to={}&dateFrom={}&dateTo={}'
    date_return_formatted = None
    if date_return:
        date_return_formatted = date_return.strftime('%d/%m/%Y')
        url_pattern += '&returnFrom={}&returnTo={}'
    response = requests_get(
        url_pattern.format(
            city_from, city_to, data_departure_formatted, data_departure_formatted, date_return_formatted, date_return_formatted))
    if response and 'data' in response and 'currency' in response:
        return response['data'], response['currency']
    else:
        return [], None





class Ticket:
    def __init__(self, json_content):
        self.json_content = json_content

    def get_departure_time(self):
        raise NotImplementedError()

    def get_price(self):
        raise NotImplementedError()

    def __repr__(self):
        return str(self.json_content)


class DohopTicket(Ticket):
    def get_departure_time(self):
        return datetime.strptime(self.json_content['flights-out'][0][0][3], '%Y-%m-%d %H:%M')

    def get_price(self):
        if 'best_price_BYN' in self.json_content:
            return self.json_content['best_price_BYN']
        else:
            fare_combinations = self.json_content['fare-combinations']
            cheapest_fare = min(fare_combinations, key=get_price_of_fare)
            self.json_content['best_price_BYN'] = get_price_of_fare(cheapest_fare)
            return self.json_content['best_price_BYN']

    def __repr__(self):
        out_dict = {}
        out_dict['price'] = self.get_price()
        out_dict['flight-details'] = {}
        out_dict['flight-details']['flights-out'] = []
        for flight in self.json_content['flights-out']:
            flight = flight[0]
            out_dict['flight-details']['flights-out'].append({'departure-airport': flight[0],
                                                              'arrival-airport': flight[1],
                                                              'flight-number': flight[2],
                                                              'time-of-departure': flight[3],
                                                              'time-of-arrival': flight[4]})
        if 'flights-home' in self.json_content:
            out_dict['flight-details']['flights-home'] = []
            for flight in self.json_content['flights-home']:
                flight = flight[0]
                out_dict['flight-details']['flights-home'].append({
                    'departure-airport': flight[0],
                    'arrival-airport': flight[1],
                    'flight-number': flight[2],
                    'time-of-departure': flight[3],
                    'time-of-arrival': flight[4]})
        return json.dumps(out_dict, indent=4, sort_keys=True)


def get_price_of_fare(fare):
    return convert_currency_into_BYN(fare['fare-including-fee']['currency'],
                                    fare['fare-including-fee']['amount'])




def requests_get(url):
    request = requests.Request('GET', url, params={'ticketing-partner': '36fd0d405f4541b7be72d117b574a70f'})
    prepared = request.prepare()
    log.log_raw_request(prepared, 'dohop')
    response = session.send(prepared)
    log.log_raw_response(response, 'dohop')
    if response.status_code == requests.codes.ok:
        return response.json()
    else:
        return None


def get_available_flights(city_from, city_to, date_departure, date_return):
    tickets = []
    url_pattern = 'https://partners-api.dohop.com/api/v2/ticketing/{}/DE/EUR/{}/{}/{}'
    data_departure_formatted = date_departure.strftime('%Y-%m-%d')
    date_return_formatted = None
    if date_return:
        date_return_formatted = date_return.strftime('%Y-%m-%d')
        url_pattern += '/{}'
    for data_source in ticketing_data_sources:
        tickets_per_datasource = requests_get(url_pattern.format(
            data_source, city_from,
            city_to,
            data_departure_formatted,
            date_return_formatted))
        if tickets_per_datasource and 'itineraries' in tickets_per_datasource:
            tickets.extend(tickets_per_datasource['itineraries'])
    return tickets






class KiwiTicket(Ticket):
    def __init__(self, json_content, currency):
        self.json_content = json_content
        self.currency = currency

    def get_departure_time(self):
        return datetime.utcfromtimestamp(self.json_content['dTime'])

    def get_price(self):
        if 'price_in_BYN' in self.json_content:
            return self.json_content['price_in_BYN']
        else:
            price_in_BYN = convert_currency_into_BYN(self.currency, self.json_content['price'])
            self.json_content['price_in_BYN'] = price_in_BYN
            return price_in_BYN

    def __repr__(self):
        out_dict = {}
        out_dict['price'] = self.get_price()
        out_dict['flight-details'] = {}
        out_dict['flight-details']['flights-out'] = []
        for flight in self.json_content['route']:
            time_arrival = datetime.utcfromtimestamp(flight['aTimeUTC']).strftime(
                '%Y-%m-%d %H:%M')

            time_departure = datetime.utcfromtimestamp(flight['dTimeUTC']).strftime(
                '%Y-%m-%d %H:%M')

            flight_details = {'departure-airport': flight['flyFrom'],
                                                              'arrival-airport': flight['flyTo'],
                                                              'flight-number': flight['flight_no'],
                                                              'time-of-departure': time_departure,
                                                              'time-of-arrival': time_arrival}
            if flight['return'] == 0:
                out_dict['flight-details']['flights-out'].append(flight_details)
            else:
                if 'flights-home' not in out_dict['flight-details']:
                    out_dict['flight-details']['flights-home'] = []
                out_dict['flight-details']['flights-home'].append(flight_details)

        return json.dumps(out_dict, indent=4, sort_keys=True)


def get_departure_time(obj):
    return obj.get_departure_time()


def get_price(obj):
    return obj.get_price()

def create_parser():
    parser = argparse.ArgumentParser()
    parser.add_argument("airport_from", help="the departure location")
    parser.add_argument("airport_to", help="the arrival destination")
    parser.add_argument("departure_date", help="search flights upto this date (YYYY-mm-dd)")
    # "return_date" is optional argument
    parser.add_argument("return_date", help="return date (YYYY-mm-dd)", nargs='?',)
    args = parser.parse_args()
    return args


def main():
    args = create_parser()
    log.reset_file()
    datetime_return = None
    if args.return_date:
        datetime_return = datetime.strptime(args.return_date, '%Y-%m-%d')
    tickets_list = tickets_processor.get_available_ticket_list(args.airport_from, args.airport_to,
                                                               datetime.strptime(args.departure_date, '%Y-%m-%d'), datetime_return)
    if not tickets_list:
        pp('The system didn\'t find any ticket! Try to change dates')
        return 0
    cheapest_ticket = tickets_processor.get_cheapest_ticket(tickets_list)
    pp('-------------cheapest_ticket------------------')
    pp(cheapest_ticket)

    sorted_tickets_list = tickets_processor.get_sorted_tickets_by_departure_time(tickets_list)
    pp('------10 tickets with earliest departures ------')
    pp(sorted_tickets_list[:10])
    print('-------------------------------------------------')



if __name__ == '__main__':
    main()
