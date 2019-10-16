from urllib.request import urlopen
from bs4 import BeautifulSoup as bs
import pandas as pd
import datetime

mainURL = "https://deepindex.org/"


topic = []
size=[]

page = urlopen(mainURL)
soup = bs(page)
topics = soup.find_all('h3')
for topic in topics:
    print(topic.text)
	

topic = []
size=[]
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
