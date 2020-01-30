import requests
from .errors import KiwiAPIError


def get_flight_prices_between_interval(departure_place, arrival_place, interval_start_date, interval_end_date):
    url = 'https://api.skypicker.com/umbrella/graphql?featureName=calendar'
    graphql_query = """
    query AggregationFlights ($parameters: AggregationParameters!, $pagination: Pagination) {
      get_aggregation_flights(
        parameters: $parameters
        pagination: $pagination
      ) {
          currencyRate
          currency
          connections
          allStopoverAirports
          allAirlines
          data {
            map {
              cityId
              sortOrder
              price
            }
            calendar {
              date
              price
            }
          }
        }
    }
    """
    graphql_query_parameters = {
        "adult_hand_bag": [0],
        "adult_hold_bag": [0],
        "adults": 1,
        "affilid": "skypicker",
        "asc": 1,
        "child_hand_bag": [],
        "child_hold_bag": [],
        "children": 0,
        "dateFrom": interval_start_date,
        "dateTo": interval_end_date,
        "featureName": "calendar",
        "flyFrom": '{}:{}'.format(departure_place['type'], departure_place['name']),
        "infants": 0,
        "locale": "US",
        "one_per_date": True,
        "oneforcity": False,
        "partner": "skypicker",
        "refresh": "fast",
        "sort": "quality",
        "to": '{}:{}'.format(arrival_place['type'], arrival_place['name']),
        "typeFlight": "oneway",
        "v": 3,
        "vehicle_type": ["aircraft"]
    }
    headers = {
        'Content-Type': 'application/json',
        'Origin': 'https://www.kiwi.com',
        'Referer': 'https://www.kiwi.com/us/search/tiles/iasi-international-iasi-romania/lyon-france-250km/2019-08-19/no-return',
        'User-Agent': 'Mozilla/5.0 (Macintosh; Intel Mac OS X 10_14_4) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/74.0.3729.157 Safari/537.36',
        'X-Agent': 'web',
        'X-API-Version': "3",
    }
    data = {
        "query": graphql_query,
        "variables": { "parameters": graphql_query_parameters }
    }
    response = requests.post(url, json=data, headers=headers)
    if response.ok:
        return response.json()
    else:
        raise KiwiAPIError(response)


def get_flight_prices_for_specific_date(departure_place, arrival_place, departure_date, direct_flights=False):
    url = 'https://api.skypicker.com/umbrella/graphql?featureName=poll_results'
    graphql_query = """
      fragment TransferAirportFragment on TransferAirport {
        terminal
        airport
       }

      fragment TransferFragment on Transfers {
        dtime
        dtime_utc
        atime
        atime_utc
        type
        carrier
        eur
        index
        src {
          ...TransferAirportFragment
        }
        dst {
          ...TransferAirportFragment
        }
      }

      fragment FlightInterfaceFragment on FlightInterface {
          id
          searchProvider
          mapIdfrom
          duration {
            return: return_time  # match flights API name
            departure
          }
          flyTo
          mapIdto
          nightsInDest
          countryTo {
            code
            name
          }
          countryFrom {
            code
            name
          }
          price
          baglimit {
            cabinWeight: hand_weight
            checkedWeight: hold_weight
          }
          bags_price: baggagePrice {  # match flights API name
            bags: tier
            price
          }
          cityTo
          cityFrom
          transfers {
            ...TransferFragment
          }
          flyFrom
          booking_token
          distance
          route {
            id
            bags_recheck_required
            mapIdfrom
            flight_no
            lngFrom
            latFrom
            latTo
            lngTo
            flyTo
            flyFrom
            guarantee
            dTimeUTC
            dTime
            aTimeUTC
            aTime
            source
            price
            cityTo
            cityFrom
            mapIdto
            airline
            return: _return  # match flights API name
            stationTo
            stationFrom
            vehicle_type
            forced_priority_boarding
            operatingAirline {
              iata
            }
            cabinClass
          }
          providers {
            code
            booking_url
            name
            price
            price_change_probability
          }
        }
      fragment BestResultsFragment on BestResult {
        sort
        price
        duration
        quality
      }

      query Flights ($parameters: Parameters!, $pagination: Pagination!, $providers: [Providers], $tags: [String]) {
        get_flights(
          parameters: $parameters
          pagination: $pagination
          providers: $providers
          tags: $tags
        ) {
          _results
          more_pending
          missingProviders
          all_stopover_airports
          all_airlines
          locationHashtags
          bestResults {
            ...BestResultsFragment
          }
          allPrices {
            price_range
            flights_number
          }
          hashtags {
            name
            count
          }
          travelTips {
            type
            changedParameters {
              dateFrom
              dateTo
              flyFrom
              radiusCenter
            }
            diff{
              price
              duration {
                total
              }
            }
          }
          data {
            ...FlightInterfaceFragment
            sectorIds
          }
        }
      }
    """
    graphql_query_pagination = {'offset': 0, 'limit': 30}
    graphql_query_parameters = {
        "adult_hand_bag": [0],
        "adult_hold_bag": [0],
        "adults": 1,
        "affilid": "skypicker",
        "asc": 1,
        "child_hand_bag": [],
        "child_hold_bag": [],
        "children": 0,
        "curr": "EUR",
        "dateFrom": departure_date,
        "dateTo": departure_date,
        "device": "DESKTOP",
        "featureName": "poll_results",
        "flyFrom": departure_place,
        "infants": 0,
        "locale": "US",
        "one_per_date": False,
        "oneforcity": False,
        "partner": "skypicker",
        "refresh": "parallel",
        "sort": "quality",
        "to": arrival_place,
        "typeFlight": "oneway",
        "v": 3,
        "vehicle_type": ["aircraft"]
    }
    if direct_flights:
        graphql_query_parameters['maxstopovers'] = '0'
    graphql_query_providers = ['KIWI', 'KAYAK']
    headers = {
        'Content-Type': 'application/json',
        'Origin': 'https://www.kiwi.com',
        'Referer': 'https://www.kiwi.com/us/search/tiles/iasi-international-iasi-romania/lyon-france-250km/2019-08-19/no-return',
        'User-Agent': 'Mozilla/5.0 (Macintosh; Intel Mac OS X 10_14_4) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/74.0.3729.157 Safari/537.36',
        'X-Agent': 'web',
        'X-API-Version': "3",
    }
    data = {
        "query": graphql_query,
        "variables": {"parameters": graphql_query_parameters, "pagination": graphql_query_pagination, "providers": graphql_query_providers}
    }
    response = requests.post(url, json=data, headers=headers)
    if response.ok and response.json()['data'] is not None:
        return response.json()['data']['get_flights']['data']
    else:
        raise KiwiAPIError(response)