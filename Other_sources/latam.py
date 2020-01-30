import requests
import time


def bestPrices():
    url = "https://bff.latam.com/ws/proxy/booking-webapp-bff/v1/public/revenue/bestprices/outbound"

    departure_date = "2019-07-27"
    return_date = "2019-07-29"

    data = {
        "departure": departure_date,
        "origin": "BOG",
        "destination": "MDE",
        "adult": 1,
        "cabin": "Y",
        "promoCode": "",
        "return": return_date,
        "country": "CO"
    }

    r = requests.get(url, params=data)
    data = r.json()

    for date in data["bestPrices"]:
        if date["available"]:
            price = f'{date["price"]["ammount"]} {date["price"]["currency"]}'
            fly_date = date["date"]
            fly_time = 
            print(fly_date, fly_time, price)


def find_flights(departure_date="2019-07-27", return_date="2019-07-29", adult=1):
    url = "https://bff.latam.com/ws/proxy/booking-webapp-bff/v1/public/revenue/recommendations/outbound"
    data = {
        "departure": departure_date,
        "return": return_date,
        "country": "CO",
        "language": "ES",
        "home": "es_co",
        "origin": "BOG",
        "destination": "MDE",
        "adult": adult,
        "cabin": "Y",
        "promoCode": "",
    }
    r = requests.get(url, params=data)
    data = r.json()
    # ['flights', 'currency', 'recommendedFlightCode']
    # data["data"].keys() 

    flights = list()

    for flight in data["data"]["flights"]:
        # get the date
        departure_time = flight["departure"]["dateTime"]
        # get the price information
        price = flight["cabins"][0]["fares"][0]["pricesPerPassenger"]
        single_trip = price["adult"]["slice"]["total"]
        whole_trip = price["adult"]["wholeTrip"]["total"]
        currency = price["adult"]["currency"]
        # print(f'{departure_time} {single_trip} {currency} {whole_trip} {currency}')
        flights.append({
            "one_way": single_trip,
            "wholetrip": whole_trip,
            "currency": currency,
            "departure_date": departure_time,
            # "arrival_time": arrival_time
            })



def lambda_handler(event, context):
    pass

if __name__ == "__main__":
    find_flights()