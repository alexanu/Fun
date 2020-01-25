from datetime import datetime, date, timedelta
from .kiwi_api import get_flight_prices_for_specific_date


locations_map = {
    'New York': {'name': 'New York', 'code': 'new-york-city_ny_us'},
    'Bucharest': {'name': 'Bucharest', 'code': 'bucharest_ro'},
    'Berlin': {'name': 'Berlin', 'code': 'berlin_de'},
    'Barcelona': {'name': 'Barcelona', 'code': 'barcelona_es'},
    'Paris': {'name': 'Paris', 'code': 'paris_fr'},
    'London': {'name': 'London', 'code': 'london_gb'},
    'Frankfurt': {'name': 'Frankfurt', 'code': 'frankfurt_de'},
    'Amsterdam': {'name': 'Amsterdam', 'code': 'amsterdam_nl'}
}


def map_flight_data(flight_data):
    return {
        'city_from': flight_data['cityFrom'],
        'city_to': flight_data['cityTo'],
        'distance': flight_data['distance'],
        'airport_from': flight_data['flyFrom'],
        'airport_to': flight_data['flyTo'],
        'kiwi_flight_id': flight_data['id'],
        'price': flight_data['price'],
        'departure_time': datetime.fromtimestamp(flight_data['route'][0]['dTimeUTC']).isoformat(),
        # 'departure_time': str(flight_data['route'][0]['dTimeUTC']),
        'arrival_time': datetime.fromtimestamp(flight_data['route'][0]['aTimeUTC']).isoformat(),
        # 'arrival_time': str(flight_data['route'][0]['aTimeUTC']),
        'flight_number': flight_data['route'][0]['flight_no'],
        'cabin_class': flight_data['route'][0]['cabinClass'],
        'airline_code': flight_data['route'][0]['airline'],
    }


def find_flights(departure_date, departure_city):
    departure_city_code = locations_map[departure_city]['code']
    for destination_city in locations_map.values():
        fligths = get_flight_prices_for_specific_date(departure_city_code, destination_city['code'], departure_date, direct_flights=True)
        # Go through flights and insert the in the db - request to api
        # Catch potential errors and update db with worker status


def find_flights_from_today_until_specified_date(departure_city, end_date):
    current_date = date.today()
    delta = end_date - current_date
    for i in range(delta.days):
        departure_date = current_date + timedelta(days=i)
        print('Fetching Results for {}'.format(departure_date))
        find_flights(departure_date, departure_city)
