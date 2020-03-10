
# see https://github.com/Skyscanner/skyscanner-python-sdk
from skyscanner.skyscanner import Flights

flights_service = Flights('7a3621970amsh9275d1c7c9ed661p15c96ajsnbc45c95d106c')
result = flights_service.get_result(
    country='DE',
    currency='EUR',
    locale='de-DE',
    originplace='MUC-sky',
    destinationplace='HNL-sky',
    outbounddate='2020-05-28',
    inbounddate='2020-05-31',
    adults=1).parsed

print(result)
