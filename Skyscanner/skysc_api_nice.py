
# Source: https://github.com/JanAdamiak/Flights-prices-tracker/blob/master/flights.py


rapidapi_host = 'skyscanner-skyscanner-flight-search-v1.p.rapidapi.com'
rapidapi_key = '5b*************************************************d8'



def get_placeID(location):
    apicall = 'https://skyscanner-skyscanner-flight-search-v1.p.rapidapi.com/apiservices/autosuggest/v1.0/UK/USD/en-GB/?query=' + str(location)
    headers = {
    'X-RapidAPI-Host': rapidapi_host,
    'X-RapidAPI-Key': rapidapi_key
    }
    r = requests.get(apicall, headers=headers)
    body = json.loads(r.text)
    places = body['Places']
    top_place_id = places[0]['PlaceId']
    return top_place_id


def get_country_code(country):
    headers={
    'X-RapidAPI-Host': rapidapi_host,
    'X-RapidAPI-Key': rapidapi_key
    }
    response = requests.get('https://skyscanner-skyscanner-flight-search-v1.p.rapidapi.com/apiservices/reference/v1.0/countries/en-GB',
    headers=headers)
    response = json.loads(response.text)
    country_code = [item['Code'] for item in response['Countries'] if item['Name'] == country][0]
    return country_code


def create_session(origin, destination, user_country_code, outbound_date):
    apicall = 'https://skyscanner-skyscanner-flight-search-v1.p.rapidapi.com/apiservices/pricing/v1.0'
    headers = {
    'X-RapidAPI-Host': rapidapi_host,
    'X-RapidAPI-Key': rapidapi_key,
    'Content-Type': 'application/x-www-form-urlencoded'
    }
    params={
    'cabinClass': 'economy',
    'children': 1,
    'infants': 0,
    'country': user_country_code,
    'currency': 'GBP',
    'locale': 'en-GB',
    'originPlace': origin,
    'destinationPlace': destination,
    'outboundDate': outbound_date,
    'adults': 3
    }
    r = requests.post(apicall, headers=headers, data=params)
    session_key = r.headers['Location'].split('/')[-1]
    return session_key


def poll_results(session_key):
    apicall = 'https://skyscanner-skyscanner-flight-search-v1.p.rapidapi.com/apiservices/pricing/uk2/v1.0/{}?sortType=price&pageIndex=0&pageSize=10'.format(session_key)
    headers = {
    'X-RapidAPI-Host': rapidapi_host,
    'X-RapidAPI-Key': rapidapi_key
    }
    r = requests.get(apicall, headers=headers)
    body = json.loads(r.text)
    itineraries = body['Itineraries']
    return itineraries


def search_flights(origin, destination, user_country, outbound_date):
    country_code = get_country_code(user_country)
    origin_id = get_placeID(origin)
    destination_id = get_placeID(destination)
    session_key = create_session(origin_id, destination_id, country_code, outbound_date)
    itineraries = poll_results(session_key)
    results = []
    for i in range(len(itineraries)):
    for j in range(len(itineraries[i]['PricingOptions'])):
    url = itineraries[i]['PricingOptions'][j]['DeeplinkUrl']
    price = itineraries[i]['PricingOptions'][j]['Price']
    results.append((price, url))
    return results