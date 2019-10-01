
Parsing tickets:

exampleURL = "https://flug.idealo.de/deals/fernreisen/"
sourceStruct = "view-source:https://flug.idealo.de/deals/fernreisen/"

import html5lib
import requests
import urllib2
import csv

import ast
import re



from urllib.request import Request, urlopen
from bs4 import BeautifulSoup as bs

import time
import pandas as pd
import numpy as np


mainURL = "https://flug.idealo.de/deals/"
keyWords = {"herbstferien", "fernreisen", "sommerferien", "best-in-europe", "last-minute", "staedtereisen", "kurzurlaub", "warme-reiseziele"}

prices = []
flight_dates = []
destins = []
groups =[]


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
						'Datea': flight_dates,
						'Price': prices,
						'Group': groups
						})
angebots=angebots[angebots['Destination'].str.contains('Münc')|
					angebots['Destination'].str.contains('Memm')]
angebots["Destination"]=angebots["Destination"].str.split(' - ').str[1]
angebots["Period"]=pd.to_datetime(ang["Datea"].str[0], format='%d.%m.%Y').dt.strftime('%Y-%m')
angebots.sort_values(by=['Group', 'Period'], inplace=True)
angebots.to_csv("Travel.csv",sep=";")

import os
os.getcwd()