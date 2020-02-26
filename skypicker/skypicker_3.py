# source: https://github.com/ganymed3/book_flight


import argparse                        # Script parameters parser
import requests                        # HTTP requests, JSON
import datetime
import pprint                          # Debug only
import json
from time import sleep
import sys                             # sys.stderr


class BookFlight(object):
   """ Main booking flight class """

   def __init__(self):
      self.args = []                # Parsed arguments
      self.search_result = {}       # Search result
      self.check_result  = {}       # Check result
      self.book_result   = {}       # Book result
      self.token = 0                # booking_token received from search_flight
      self.search_price  = 0        # Stored from search response
      self.check_price   = 0        # Stored from check response
      self.search_currency = 0      # Stored from search response
      self.check_currency  = 0      # Stored from check response
      self.search_duration = 0      # Stored from search response
      self.book_pnr      = 0        # Booking PNR code
      self.error         = False
      self.check_attempts= 30      # How many attempts when checking the flight
      self.check_wait    = 10       # Wait in seconds between attempts
      # API Endpoints
      self.c_EP_FLIGHTS = 'https://api.skypicker.com/flights?'
      self.c_HEADERS    = { 'Content-Type': 'application/json' }
      self.c_BAGS_MAX   = 4

   
   def search_flight (self, _limit=1, _currency='EUR'):
      param = {} 
      param['flyFrom'] = self.args.from_iata[0]
      param['to']      = self.args.to_iata[0]
      date = datetime.datetime.strptime(self.args.date[0], "%Y-%m-%d")
      date_str = date.strftime("%d/%m/%Y")
      param['dateFrom']       = date_str
      param['dateTo']         = date_str
      param['partner']        = 'picky'
      #param['partner_market'] = 'us'            # Required?
      
      # Optional parameters
      # RETURN vs ONEWAY
      if self.args.return_n:
         date_return = date + datetime.timedelta(days = self.args.return_n[0])
         date_return_str = date_return.strftime("%d/%m/%Y")
         param['returnFrom'] = date_return_str
         param['returnTo']   = date_return_str
         param['typeFlight'] = 'round'
      else:
         param['typeFlight'] = 'oneway'         # Default option

      if self.args.fastest:
         sort = 'duration'
      else:
         sort = 'price'             # Default option

      param['sort']  = sort
      param['asc']   = '1'          # 1 = ascending
      param['limit'] = _limit       # count of results
      param['curr']  = _currency   
      
      self.search_result = self._send_request(self.c_EP_FLIGHTS, param)
      
      # Obtain 'booking_token'
      try:
         json = self.search_result.json()
      except Exception as e:
         json = {}
         self.eprint("JSON: Invalid received data: EXCEPTION:", str(e) )
      
      try:
         self.token = json['data'][0]['booking_token']
      except (IndexError, KeyError):
         self.token = 0
         self.eprint("booking_token was not found in the search response")
                     
      # Just for information
      try:
         self.search_currency = json['currency']
         self.search_price    = json['data'][0]['price']
         self.search_duration = json['data'][0]['fly_duration']
      except (IndexError, KeyError):
         self.iprint("currency/price/fly_duration not found in search response")

      # Debug purposes
      if self.args.debug:
         pprint.pprint(self.search_result.url)
         pprint.pprint(self.search_result.json())
      
      return self.token


# ----------------------------------------------------------------------------------------------
# Source: https://github.com/opeixenada/travelcheck/tree/master/travelcheck/pricesretriever



import logging
from datetime import datetime
from urllib.parse import urlencode

import requests
from retrying import retry

from travelcheck.util import retry_if_result_none

LOGGER = logging.getLogger(__name__)


@retry(wait_exponential_multiplier=1000, wait_exponential_max=10000,
       retry_on_result=retry_if_result_none, stop_max_attempt_number=3)
def request_kiwi(subscription, config):
    
    host = "https://api.skypicker.com/flights"

    query = {
        'partner': config['apiKey'],
        'partner_market': config['market'],
        'fly_from': subscription['origin'],
        'fly_to': subscription['destination'],
        'date_from': subscription['earliest'].strftime("%d/%m/%Y"),
        'date_to': subscription['latest'].strftime("%d/%m/%Y"),
        'nights_in_dst_from': subscription['minDays'],
        'nights_in_dst_to': subscription['maxDays'],
        'max_stopovers': subscription['maxStops'],
        'curr': subscription['currency'],
        'locale': subscription['locale'],
        'sort': 'price',
        'asc': 1,
        'limit': 1
    }

    url = host + '?' + urlencode(query)

    logging.info("Requesting %s" % url)

    response = requests.get(url)

    if response.json() and response.json()['data']:
        return response.json()

    return None

def subscribe(subscription, config):
    
    # Call the Kiwi API
    response_json = request_kiwi(subscription, config)

    # Extract the relevant price details
    first_result = response_json['data'][0]
    subscription_response = dict()
    subscription_response['price'] = first_result['price']

    subscription_response['lastChecked'] = datetime.utcnow()

    subscription_response['outboundDate'] = datetime.utcfromtimestamp(first_result['dTimeUTC'])

    first_return_leg = next(leg for leg in first_result['route'] if leg['return'] == 1)
    subscription_response['inboundDate'] = datetime.utcfromtimestamp(
        first_return_leg['dTimeUTC'])

    subscription_response['deeplink'] = make_deeplink(subscription, config)

    return subscription_response

def make_deeplink(subscription, config):

        # Assemble the landing page using the original request parameters and Kiwi config

        deeplink_host = 'https://www.kiwi.com/deep'
        
        deeplink_params = (
            ('from', subscription['origin']),
            ('to', subscription['destination']),
            ('departure', subscription['earliest'].strftime("%d-%m-%Y") + '_' + subscription['latest'].strftime("%d-%m-%Y")),
            ('return', str(subscription['minDays']) + '-' + str(subscription['maxDays'])),
            ('lang', subscription['locale']),
            ('currency', subscription['currency']),
            ('affilid', config['deeplinksId'])
        )

        deeplink = deeplink_host + '?' + urlencode(deeplink_params)

        logging.info("Assembled deeplink: %s", deeplink)

        return deeplink