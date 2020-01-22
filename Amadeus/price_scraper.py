from amadeus import Client
import pandas as pd
import datetime as dt
import glob


api_file = open('AMADEUS_API_KEY.txt', 'r')
api_credentials = api_file.read()
c_id = api_credentials.split(' ', 1)[0]
c_secret = api_credentials.split(' ', 1)[1]
api_file.close()

amadeus = Client(
    client_id = c_id,
    client_secret = c_secret,
    log_level = 'debug'
)

cities_code = ['HNL', 'ODS', 'BIA']
cities_name = ['Honolulu', 'Odessa', 'Corsica']


today_date = dt.date.today()

gap_days = [1, 7, 15, 30, 60, 90]

finalDf = pd.DataFrame()

for to_city_code in cities_code:
    
    for days in gap_days:
        
        from_date = str(today_date + dt.timedelta(days = days))
        to_date = str(today_date + dt.timedelta(days = days + 20))
        
        result = amadeus.shopping.flight_offers.get(
            origin = 'MUC', 
            destination = to_city_code,
            departureDate = from_date,
            returnDate = to_date,
            currency = 'EUR',
            max = 250
        )
        result_data = result.data
        
        airlineName = []
        priceList = []
        
        for i in range(len(result_data)):
            x = result_data[i]['offerItems'][0]['price']['total']
            y = result_data[i]['offerItems'][0]['price']['totalTaxes']
            z = float(x) + float(y)
            a = result_data[i]['offerItems'][0]['services'][0]['segments'][0]['flightSegment']['carrierCode']
            airlineName.append(a)
            priceList.append(float(x))
        
        df = pd.DataFrame()
        df['airline_code'] = airlineName
        df['ticket_price'] = priceList
        df.sort_values('ticket_price', ascending = True, inplace = True)
        df = df.drop_duplicates('airline_code', keep = 'first')
        
        df = df[df['airline_code'] != '9B']
        df['airline_name'] = df['airline_code'].map({'BA': 'British Airways', 'LH': 'Lufthansa', 'WY': 'Oman Air', 
                                              'EK': 'Emirates', 'EY': 'Etihad', 'TK': 'Turkish Airlines',
                                              'KL': 'KLM Royal Dutch Airlines', 'AZ': 'Alitalia',
                                              'AF': 'Air France', 'LX': 'Swiss Air', 'QR': 'Qatar Airways',
                                              'QF': 'Qantas Airways', 'SQ': 'Singapore Airlines',
                                              'TG': 'Thai Airways', 'AY': 'Finn Air', 'SU': 'Aeroflot',
                                              'LO': 'LOT Polish Airlines', 'UL': 'Sri Lankan Airlines',
                                              'OS': 'Austrian Airlines', 'CX': 'Cathay Pacific', 
                                              'AI': 'Air India', 'KU': 'Kuwait Airways', 'MS': 'Egypt Air',
                                              'PS': 'Ukraine International Airlines', 'SV': 'Saudia',
                                              'MU': 'China Eastern Airlines', 'NH': 'All Nippon Airways',
                                              'CA': 'Air China'})
        df['from_city'] = 'MUC'
        df['to_city'] = to_city_code
        df['from_date'] = from_date
        df['to_date'] = to_date
        df['crawl_date'] = str(today_date)
        finalDf = finalDf.append(df)
        
export_file_name = 'dataset/_' + str(today_date) + '_muc_in.csv'
finalDf.to_csv(export_file_name, index = False)

list_of_files = glob.glob('dataset/*')

bigDf = pd.DataFrame()

for i in list_of_files:
    smallDf = pd.read_csv(i)
    bigDf = bigDf.append(smallDf)
    
bigDf.to_csv('final_data/_raw_dataset.csv', index = False)