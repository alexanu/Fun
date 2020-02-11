
# Source: https://github.com/mcreduardo/flightTicketQuotes/blob/master/searchMultipleDestinations.py


import unirest
import json
import sys

def merge_dicts(x, y):
  z = x.copy()
  z.update(y)
  return z

def getCarrier(ids, carriers):
  carriers_found = ""
  for id in ids:
    for carrier in carriers:
      if carrier["CarrierId"] == id:
        carriers_found = carriers_found + " " + carrier["Name"]
  return carriers_found


def browseQuotes(required_params, printOutput):
  
  source = "https://skyscanner-skyscanner-flight-search-v1.p.rapidapi.com"\
    + "/apiservices/browsequotes/v1.0"\
    + "/" + required_params["country"]\
    + "/" + required_params["currency"]\
    + "/" + required_params["locale"]\
    + "/" + required_params["originPlace"]\
    + "/" + required_params["destinationPlace"]\
    + "/" + required_params["outboundDate"]\
    + "/" + required_params["inboundDate"]
  response = unirest.get(source,
    headers={
      "X-RapidAPI-Host": "skyscanner-skyscanner-flight-search-v1.p.rapidapi.com",
      "X-RapidAPI-Key": "e08015148bmsh741474b8af3942ap1b29d7jsnc1343256972b"
    }
  )

  # Error handling 
  if "ValidationErrors" in response.body:
    print "\nValidation error when browsing quotes:\n"
    print json.dumps(response.body["ValidationErrors"][0], indent=4)
    print ""
    sys.exit()

  if printOutput:

    if not response.body["Quotes"]:
      print "No results found for destination " + required_params["destinationPlace"] + "\n"
    else:
      print ""
      print "From " + required_params["originPlace"]\
        + " to " + required_params["destinationPlace"] + "."
      print "From " + required_params["outboundDate"]\
        + " to " + required_params["inboundDate"] + "."

      # Cheapest quotes:
      print "\nCheapest quotes ("+ response.body["Currencies"][0]["Code"] +"):\n"

      i = 1
      for quote in response.body["Quotes"]:
        if quote["Direct"]: direct_str = ", direct"
        else: direct_str = ", not direct"

        print "\t".expandtabs(2) + str(i) + ") " + "MinPrice: "\
          + str(quote["MinPrice"]) + direct_str
        print "\tOutbound:".expandtabs(6)
        print "\tDeparture: ".expandtabs(8) + quote["OutboundLeg"]["DepartureDate"]
        print "\tCarrier(s): ".expandtabs(8)\
          + getCarrier(quote["OutboundLeg"]["CarrierIds"], response.body["Carriers"])
        print "\tInbound:".expandtabs(6)
        print "\tDeparture: ".expandtabs(8) + quote["InboundLeg"]["DepartureDate"]
        print "\tCarrier(s): ".expandtabs(8)\
          + getCarrier(quote["InboundLeg"]["CarrierIds"], response.body["Carriers"])
        print ""

        i += 1
  
  return response


if __name__=="__main__":

  required_params = {
    "country": "US",
    "currency": "USD",
    "locale": "en-US",
    "originPlace": "SFO",
    "destinationPlace": "LHR",
    "outboundDate": "2019-05-01",
    "inboundDate": "2019-05-10",
  }
  # Optional parameters
  opt_params = {
  }

  
origin = "MSN"
destinations = [\
    "SFO",\
    "OAK",\
    "SJC"]
outboundDate = "2019-04-11"
inboundDate  = "2019-04-14"

for destination in destinations:
    # Search Parameters
    # required parameters
    required_params = {
    "country": "US",
    "currency": "USD",
    "locale": "en-US",
    "originPlace": origin,
    "destinationPlace": destination,
    "outboundDate": outboundDate,
    "inboundDate": inboundDate,
    }

    browseQuotes(required_params = required_params, printOutput = True)