# Source: https://github.com/havocesp/pygfs


import argparse
from pprint import pprint

import time
from datetime import datetime as dt, timedelta as td
from random import randint
from typing import List

import dateparser as date
from lxml import html
from pyshorteners.shorteners import Tinyurl
from splinter.browser import FirefoxWebDriver


URL_BASE = 'https://www.google.com/flights'


def short_url(url):
    return Tinyurl(timeout=30).short(url)


def _flight_request(args, date_start, date_end):
    """URL Builder.
    :param args:
    :param date_start:
    :param date_end:
    :return str:
    """
    # base_url = 'https://www.google.com/flights?'
    # from_airport = args.from_airport.upper()
    # to_airport = args.to_airport.upper()
    # date_start = args.date_start
    # date_end = args.date_end
    # currency = args.currency.upper()
    # country_code = args.country_code.lower()
    # if args.country_code:
    #     base_url += f'hl={args.country_code.lower()}'
    # ;s:0*0 -> 0 escalas en la ida * cero escalas en la vuelta
    # ;px:2,1,1,1 -> numero de pasajeros adultos, un niño, un bebe en regazo y un bebe con asiento
    params = vars(args)
    if int(args.adults) > 1 or args.children is not None:
        passengers = f';px:{args.adults}'
        if args.children:
            passengers += f',{args.children}'
    else:
        passengers = str()

    params.update({'passengers': passengers, 'date_start': date_start, 'date_end': date_end})
    url = '{base_url}/#flt={from_airport}.{to_airport}.{date_start}*{to_airport}.{from_airport}.{date_end}'
    url += ';c:{currency};e:1{passengers};sd:1;t:f'
    # url = URL_BASE + '/#flt={from_airport}.{to_airport}.{date_start}*{to_airport}.
    # {from_airport}.{date_end};c:{currency};e:1;s:0*0{passengers};sd:1;t:f'
    url = url.format(base_url=URL_BASE, **params)

    print(short_url(f'{url.replace("*", "%2A")}'), end=' - ')
    return url


def _parse_card(card, date_start, date_end, adults, children):
    """Parse flight card, getting company, flight timing and date, etc.
    :param card:
    :param date_start:
    :param date_end:
    :param children:
    :return: FlightOffer instance containing the a flight offer info.
    """
    data = FlightOffer()
    # '/html/body/div[2]/div[2]/div/div[2]/div[3]/div/jsl/div/div[2]/main[4]/div[7]/div[1]/div[5]/div[1]/ol/li/div/div[1]/div[2]/div[1]/div[1]/div[5]/div[1]'
    xpath_root = './div/div[1]/div[2]/div[1]/div[1]'
    try:
        data = FlightOffer(**{
            'date_start': date_start,
            'date_end': date_end,
            'adults': adults,
            'children': children,
            'price': card.xpath(f'{xpath_root}/div[5]/div[1]')[0].text.strip('\t ').replace('\xa0', ' '),
            'arrival': card.xpath(f'{xpath_root}/div[2]/div[1]/div/span[2]/span/span')[0].text,
            'duration': card.xpath(f'{xpath_root}/div[3]/div[1]')[0].text.replace('\xa0', ' '),
            'scales': card.xpath(f'{xpath_root}/div[4]/div[1]/div/div/span')[0].text,
            'airline': card.xpath(f'{xpath_root}/div[2]/div[2]/span[1]/span/span')[0].text_content()
            # 'date_start': card.xpath('./div/div[1]/div[2]/div[1]/div[1]/div[2]/div[1]/div/span[1]/span/span')[0].text,
        })
    except (AttributeError, ValueError) as inst:
        print(str(inst))
        print(' - [ERROR] Failed to parse card ...')
    return data


class FlightOffer:
    """Flight offer model class."""

    def __init__(self, **kwargs):
        self._data = dict(**kwargs)
        if len(self._data or dict()):
            self.timestamp = dt.now().timestamp()
            self.price = kwargs.get('price')
            self.duration = kwargs.get('duration')
            self.adults = kwargs.get('adults')
            self.children = kwargs.get('children', 0) or 0
            self.scales = str(kwargs.get('scales', '0,0') or '0,0').split(',')
            self.airline = kwargs.get('airline')
            self.date_start = date.parse(f"{kwargs.get('date_start')} {kwargs.get('date_start')}")
            self.date_end = date.parse(f"{kwargs.get('date_end')} {kwargs.get('date_end')}")
            self.day_range = date.parse(f"{kwargs.get('day_range')} {kwargs.get('arrival')}")

    def __str__(self):
        return str(self._data)

    def __repr__(self):
        return self.__str__()

    def items(self):
        return self._data.items()

    def get(self, key, default=None):
        self._data.get(key, default) or default


def _url_builder(args):
    urls = list()
    date_start = date.parse(args.date_start)
    date_end = date.parse(args.date_end)
    # days_range = [int(d) for d in args.day_range.split(',')]
    # days = days_range[1] - days_range[0]
    start, end = map(int, args.day_range.split(','))
    days_diff = (date_end - date_start).days - int(start)
    for x in range(days_diff - 1):
        start_date = date_start + td(days=x)
        for i in range(start, end + 1):
            # TODO range days iterator
            end_date = date_start + td(days=i + x + 1)
            print(f'{start_date.date()} - {end_date.date()}')
            url = _flight_request(args, date_start=start_date.date(), date_end=end_date.date())
            if url:
                urls.append(url)
    return urls


class FlightCollector:
    """Flight data collector class."""

    def __init__(self):
        self.browser = FirefoxWebDriver(headless=True)

    def search_all(self, args, time_sleep=3) -> List[FlightOffer]:
        """Search for all flights for all searches.
        NOTE: might be useful to add search name
        :param args: list of dictionaries, defininf search
        :param int time_sleep: seconds to sleep TODO: need to define/replace/improve
        :return: list of flight dicts
        """
        results = list()

        date_start = date.parse(args.date_start)
        date_end = date.parse(args.date_end)

        range_init, range_end = [int(d) for d in args.day_range.split(',')]

        for offset in range((date_end - date_start).days - range_end + 1):
            start = date_start + td(offset)
            for days in range(range_init, range_end + 1):
                end = start + td(days)
                end_str = end.date() if isinstance(end or "", dt) else ""
                days_str = f'{days:02d} day{"" if days == 1 else "s"}'

                print(f' - ({days_str}) {start.date()} - {end_str}', end=' ')

                url = _flight_request(args, date_start=start.date(), date_end=end.date())

                self.browser.visit(url)
                time.sleep(randint(1, time_sleep))

                dom = html.fromstring(self.browser.html)

                flights = dom.xpath('//ol/li')

                if flights:
                    parsed_data = _parse_card(
                        flights[0],
                        date_start=start,
                        date_end=end,
                        adults=args.adults,
                        children=args.children
                    )
                    print(f'[{parsed_data.price}]')
                    results.append(parsed_data)

        return sorted(results, key=lambda i: i.price)


def load_airports_info():
    cwd: Path = Path(__file__).resolve(True).parent
    data_file = cwd.joinpath('data', 'airports-code-min.csv')
    if data_file.is_file():
        content = data_file.read_text('utf-8')
        return [l.split(',') for l in content.splitlines() if l]


def get_iata_code(airport):
    airports = load_airports_info()
    results = list()
    if airports:
        for a in airports:
            if airport in str(' '.join(a[1:])).lower():
                results.append(a[0])

    return results[0] if results and len(results) == 1 else results


def parse_args():
    parser = argparse.ArgumentParser(
        description='Google flights scrapper.')
    subparsers = parser.add_subparsers()
    search = subparsers.add_parser('search')
    search.add_argument('-f', '--from-airport',
                        help='Departure airport IATA code.')
    search.add_argument('-t', '--to-airport',
                        help='Destiny airport IATA code.')
    search.add_argument('-s', '--date-start', help='Starting date.')
    search.add_argument('-e', '--date-end', help='Final date.')
    search.add_argument('-d', '--day-range',
                        help='A comma separated days range. Example: 7,10')
    search.add_argument('-C', '--country-code', default='es',
                        help='Two characters length country code. (Default: es)')
    search.add_argument('-c', '--currency', default='EUR',
                        help='Three characters length currency  code. (Default: EUR)')
    search.add_argument('-a', '--adults', type=int, default=1,
                        help='Amount of adult passengers.')
    search.add_argument('--children', help='Amount of children passengers.')

    search = subparsers.add_parser('airport')
    search.add_argument('airport')

    return parser.parse_args()


def main(args):
    """Sample of data collection routine."""
    if args.airport:
        print(get_iata_code(args.airport))
    else:
        fs = FlightCollector()
        try:
            flights = fs.search_all(args)
            if flights and len(flights):
                pprint(flights)
            else:
                print(' - Sorry, no flights found.')
        except Exception as err:
            raise err


if __name__ == '__main__':
    # TODO: remove me (just for testing purposes)
    import sys

    sys.argv.extend(['airport', 'madrid'])
    # sys.argv.extend([
    #     '-t', 'FUE',
    #     '-f', 'AGP',
    #     '-s', '2019-11-24',
    #     '-e', '2020-04-30',
    #     '-d', '7,18',
    #     '-C', 'es',
    #     '--adults', '2',
    #     '--children', '1'
    # ])

    # TODO parser.add_argument('--max-scales', help='Comma sep max. scales for date_start and arrival. Example: 0,1')
    # TODO parser.add_argument('--airline', help='IATA airline code.')
    # TODO parser.add_argument('--date_start-time', help='Earliest time filter for results. (Example: 10:00)')
    # TODO parser.add_argument('--arrival-time', help='Latest time filter for results. (Example: 20:00)')
    # TODO Add IATA airline code searcher by airline name.')
    main(parse_args())
