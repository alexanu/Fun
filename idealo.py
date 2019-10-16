
from urllib.request import urlopen
from bs4 import BeautifulSoup as bs
import pandas as pd
import datetime



all=pd.read_csv("travel.csv",sep=";") # reading current status


mainURL = "https://flug.idealo.de/deals/"
keyWords = {"herbstferien", "fernreisen", "sommerferien", "best-in-europe", "last-minute", 
			"staedtereisen", "kurzurlaub", "warme-reiseziele"}

not_interested = ['Alghero', 'Belgrad', 'Bergen', 'Berlin Tegel', 'Bukarest', 
				'Cluj', 'Frankfurt', 'Moskau Scheremetjewo', 'Bremen', 'Prag', 'Delhi', 'Detroit', 'Düsseldorf', 'Hamburg', 'Jakarta', 
				'Köln/Bonn', 'Sibiu','London Gatwick', 'London Heathrow', 'London Luton', 
				'London Stansted', 'Lviv', 'Manchester', 'Monastir', 'München', 
				'Pittsburgh', 'Podgorica', 'Pristina', 'Rostock', 'Tirana', 
				'Ankara', 'Antalya', 'Istanbul', 'Istanbul Sabiha Gökcen', 'Izmir', 
				'Simferopol', 'Sofia', 'Taschkent', 'Ulan Bator', 'Varna', 'Warschau']


prices = []
flight_dates = []
destins = []
groups =[]
status=[]

for keyword in keyWords:
		url = mainURL+keyword
		page = urlopen(url)
		soup = bs(page)
		trips = soup.find_all('div', class_ = 'deals-card deals-card--default')
		for trip in trips:
			price = trip.find('span',class_="deals-card-offer-price").text
			prices.append(price)
			flight_date = trip.find('div',class_="deals-card-date").text.split(" - ")
			flight_dates.append(flight_date)
			destin = trip.find('div',class_="deals-card-destination-container")['title']
			destins.append(destin)
			groups.append(keyword)
			

angebots = pd.DataFrame({'Destination': destins,
						'Dates': flight_dates,
						'Price': prices,
						'Group': groups
						})
angebots=angebots[angebots['Destination'].str.contains('Münc')| # keep only the flights from Munich ...
					angebots['Destination'].str.contains('Memm')] # ... and Memmingen
angebots["Destination"]=angebots["Destination"].str.split(' - ').str[1] # after splitting keep only 2nd part: destination
angebots = angebots[~angebots['Destination'].isin(not_interested)] # removing not interesting destinations
angebots["Period"]=pd.to_datetime(angebots["Dates"].str[0], format='%d.%m.%Y').dt.strftime('%Y-%m') # new column: month of flight
angebots['Status'] = str(datetime.date.today()) # new column: when the query was done
angebots["Destination"]=angebots["Destination"].replace({'-': ' ', ',': ''}, regex=True) # some destinations contain bad-for-csv symbols

Regio=pd.read_csv("regio.csv",sep=";", index_col='Destination')
angebots['Regio'] = angebots.Destination.map(Regio.Regio) # vlookuping region

new=angebots[angebots.isnull().Regio]['Destination'].drop_duplicates() # new destinations
if len(new)>0:
	new.to_csv("regio.csv", # the file exists already
				mode='a', # append mode: puts new df in the end of csv
				sep=";", 
				header=False, # as we are appending, the file has headers already
				index=False) # we need to eliminate the index column

all.append(angebots, ignore_index = True) # adding new information to the main file below

# calculating the min price for every destination and putting it to separate col
all['min_price']=all.groupby(["Destination"])["Price"].transform(min)                                                        


all[(all.Status == str(datetime.date.today())) & (all['Price'] == all['min_price'])]



all.to_csv("Travel5.csv", # creating new file
				sep=";", 
				index=False) # we need to eliminate the index column

# angebots.sort_values(by=['Group', 'Period'], inplace=True)
'''

angebots.to_csv("Travel.csv", # the file exists already
				mode='a', # append mode: puts new df in the end of csv
				sep=";", 
				header=False, # as we are appending, the file has headers already
				index=False) # we need to eliminate the index column

ang = angebots.copy()
ang["Destination"]=ang["Destination"].str.split(' - ').str[1]
ang['Status'] = str(datetime.date.today())
ang["Period"]=pd.to_datetime(ang["Datea"].str[0], format='%d.%m.%Y').dt.strftime('%Y-%m')
ang = ang[~ang['Destination'].isin(not_interested)]

# cities_db_url="https://simplemaps.com/static/data/world-cities/basic/simplemaps_worldcities_basicv1.5.zip"
# cities_db = pd.read_csv(cities_db_url)

'''

all2 = all.copy()

all2['min_price']=all2.groupby(["Destination"])["Price"].transform(min)                                                        

