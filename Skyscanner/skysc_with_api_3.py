import time
from itertools import product
import pandas as pd
from os import path
import requests

RAPID_API_KEY = None


def get_prices_for(origin, destination, departure_date, return_date, country):
    if not RAPID_API_KEY:
        raise ValueError('''RAPID_API_KEY is empty.
        Please get your API KEY at https://rapidapi.com/ and set RAPID_API_KEY = 'API KEY'.
        ''')

    session_id = _init_query_session(origin, destination, departure_date, return_date, country)
    for (price, link) in _get_session_offers(session_id):
        yield {
            'origin': origin,
            'destination': destination,
            'departure_date': departure_date,
            'return_date': return_date,
            'country': country,
            'price': price,
            'link': link
        }


def _init_query_session(origin, destination, departure_date, return_date, country):
    print(f'Searching offers for {origin} -> {destination} ({country}, {departure_date} - {return_date})')
    response = _request('pricing/v1.0', method='post', data={
        'outboundDate': departure_date,
        'inboundDate': return_date,
        'country': country,
        'originPlace': origin,
        'destinationPlace': destination,
        'cabinClass': 'economy',
        'adults': 1,
        'children': 0,
        'infants': 0,
        'currency': 'USD',
        'locale': 'en-US',
    })

    if not response.ok:
        raise Exception('Got an exception while creating a new session ' + response.text)
    
    session_id = path.basename(response.headers['Location'])
    print(f'Session {session_id} succesfully created.')
    return session_id


def _get_session_offers(session_id):
    print(f'Fetching session {session_id} offers.')
    while True:
        time.sleep(1)
        response = _request(f'pricing/uk2/v1.0/{session_id}?pageIndex=0&pageSize=100', method='get')
        data = response.json()
        if data['Status'].lower() == 'updatescomplete':
            break

    print(f'Parsing session {session_id} offers.')
    for itinerary in data['Itineraries']:
        for pricing in itinerary['PricingOptions']:
            yield (pricing['Price'], pricing['DeeplinkUrl'])


def _request(url_path, method, data=None):
    url = f'https://skyscanner-skyscanner-flight-search-v1.p.rapidapi.com/apiservices/{url_path}'
    if method.lower() == 'get':
        return requests.get(url, 
            headers={
                'X-RapidAPI-Host': 'skyscanner-skyscanner-flight-search-v1.p.rapidapi.com',
                'X-RapidAPI-Key': RAPID_API_KEY
            })
    else:
        return requests.post(url,
            data=data,
            headers={
                'X-RapidAPI-Host': 'skyscanner-skyscanner-flight-search-v1.p.rapidapi.com',
                'X-RapidAPI-Key': RAPID_API_KEY,
                'Content-Type': 'application/x-www-form-urlencoded'
            })


def build_query_queue(origin, destination, country):
    travels = product(origin.split(','), destination.split(','))
    for origin, destination in travels:
        try:
            (origin, origin_country) = origin.split("/")
        except:
            origin_country = country

        if origin == destination:
            print(f'Skipping same location ({origin} -> {destination}).')
            continue

        yield (f"{origin.strip()}-sky", origin_country, f"{destination.strip()}-sky")


if __name__ == '__main__':
    sky_scanner_rapid_api.RAPID_API_KEY = args.api_key
    df = pd.DataFrame(
        columns=['origin', 'destination', 'departure_date', 'return_date', 'price', 'country', 'link']
    )

    query_queue = list(build_query_queue(args.origin, args.destination, args.country))
    while query_queue:
        (origin, country, destination) = query_queue.pop()

        try:
            time.sleep(1)
            offers = list(sky_scanner_rapid_api.get_prices_for(
                origin,
                destination,
                args.departure_date,
                args.return_date,
                country
            ))
            if offers:
                df = df.append(offers)
            else:
                print(f'No offers found for {query}')
        except Exception as e:
            print(f'EXCEPTION while processing {origin} -> {destination} (Enqueing again):: {e}.')
            query_queue.append((origin, country, destination))
            time.sleep(2)

    df.to_csv(args.output)

    prices = df.groupby(by=['origin', 'destination'])['price'].nsmallest(30)
    prices = prices.groupby(by=['origin', 'destination'])
    prices = prices.median().unstack()
    prices.to_csv(args.output_summary)