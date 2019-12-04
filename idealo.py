
from urllib.request import urlopen
from bs4 import BeautifulSoup as bs
import pandas as pd
import datetime

import os
os.getcwd()

directory = 'c:\\Users\\oanuf\\GitHub\\Fun\\'


all=pd.read_csv(directory+"Travel.csv",sep=";") # reading current status

# Filling in empty regios from previous run
Regio=pd.read_csv(directory+"regio.csv",sep=";", index_col='Destination') # reading mapping for regions
if len(all[all.isna().any(axis=1)])>0: # if there is not-filled region from previous run ...
    	all.loc[all.isna().any(axis=1),'Regio']  = all.Destination.map(Regio.Regio) # ... vlookup it from updated region mapping

mainURL = "https://flug.idealo.de/deals/"
keyWords = {"herbstferien", "fernreisen", "sommerferien", "best-in-europe", "last-minute", 
			"staedtereisen", "kurzurlaub", "warme-reiseziele", "weihnachtsferien", "weihnachten"
			"beste-urlaubsziele-des-jahres", "osterferien"}
not_interested.values
not_interested = pd.read_csv(directory+"not_interesting.csv")
not_interested = ['Alghero', 'Belgrad', 'Bergen', 'Berlin Tegel', 'Bukarest', 'Banja Luka',
		   'Cluj', 'Frankfurt', 'Kishinev', 'Skopje', 'Moskau Scheremetjewo', 'Bremen', 
		   'Prag', 'Delhi', 'Detroit', 'Hatay', 'Düsseldorf', 'Hamburg', 'Jakarta', 
		   'Köln/Bonn', 'Sibiu','London Gatwick', 'London Heathrow', 'London Luton', 
		   'London Stansted', 'Ohrid', 'Lviv', 'Manchester', 'Monastir', 'München', 
		   'Pittsburgh', 'Podgorica', 'Pristina', 'Rostock', 'Tirana', 
		   'Ankara', 'Antalya', 'Istanbul', 'Istanbul Sabiha Gökcen', 'Izmir', 
		   'Simferopol', 'Sofia', 'Taschkent', 'Ulan Bator', 'Varna', 'Warschau']


prices = []
flight_dates = []
destins = []
groups =[]
status=[]

for keyword in keyWords:
		try:
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
		except:
			pass
			

angebots = pd.DataFrame({'Destination': destins,
						'Dates': flight_dates,
						'Price': prices,
						'Group': groups
						})
angebots=angebots[angebots['Destination'].str.contains('Münc')| # keep only the flights from Munich ...
					angebots['Destination'].str.contains('Memm')] # ... and Memmingen
angebots["Destination"]=angebots["Destination"].str.split(' - ').str[1] # after splitting keep only 2nd part: destination
angebots = angebots[~angebots['Destination'].isin(not_interested.Destination.values)] # removing not interesting destinations
angebots["Period"]=pd.to_datetime(angebots["Dates"].str[0], format='%d.%m.%Y').dt.strftime('%Y-%m') # new column: month of flight
angebots['Status'] = str(datetime.date.today()) # new column: when the query was done
angebots["Destination"]=angebots["Destination"].replace({'-': ' ', ',': ''}, regex=True) # some destinations contain bad-for-csv symbols

angebots['Regio'] = angebots.Destination.map(Regio.Regio) # vlookuping region

new=angebots[angebots.isnull().Regio]['Destination'].drop_duplicates() # new destinations
if len(new)>0:
	new.to_csv(directory+"regio.csv", # the file exists already
				mode='a', # append mode: puts new df in the end of csv
				sep=";", 
				header=False, # as we are appending, the file has headers already
				index=False) # we need to eliminate the index column

all=all.append(angebots, ignore_index = True) # adding new information to the main file below
all=all.sort_values(["Regio","Destination"])
# calculating the min price for every destination and putting it to separate col
all['min_price']=all.groupby(["Destination"])["Price"].transform(min).replace({'[\€,]': '', '[\,00 €,]': ''}, regex=True).astype(float)



record_price = all[(all.Status == str(datetime.date.today())) & 
					(all['Price'] < 1.2*all['min_price']) &
					(pd.DatetimeIndex(all["Period"]).year==2020)]
record_price = record_price.drop(['min_price','Status'],axis=1).sort_values(["Regio"])

all['min_price'].apply(type)



all.to_csv("Travel.csv", # creating new file
			sep=";", 
			index=False) # we need to eliminate the index column

# angebots.sort_values(by=['Group', 'Period'], inplace=True)


all.to_csv(directory+"Travel.csv", # the file exists already
			mode='a', # append mode: puts new df in the end of csv
			sep=";", 
			header=False, # as we are appending, the file has headers already
			index=False) # we need to eliminate the index column

# cities_db_url="https://simplemaps.com/static/data/world-cities/basic/simplemaps_worldcities_basicv1.5.zip"
# cities_db = pd.read_csv(cities_db_url)



import smtplib
from email.mime.text import MIMEText
from email.mime.multipart import MIMEMultipart
import os

email = EMAIL1
password = PASS1
send_to_email =["XXX","XXXX"]
subject = 'Record flight prices for yesterday'

ds=str(record_price.to_html())
messageHTML = 'Flights from Idealo'+ds
msg = MIMEMultipart('alternative')
msg['From'] = email
msg['To'] = ', '.join(send_to_email)
msg['Subject'] = subject

msg.attach(MIMEText(messageHTML, 'html'))

server = smtplib.SMTP("smtp.gmail.com",587)
server.starttls()
server.login(email, password)
text = msg.as_string()
server.sendmail(email, send_to_email, text)
server.quit()



all2 = all.copy()

all2['prices']=list(all2.Price.unique())



all2['prices'] = [list(set(all2['subreddit'].loc[all2['Destination'] == x['Destination']])) 
    for _, x in df2.iterrows()]
groupby(["Destination"])
