
'''
Parsing tickets:

exampleURL = "https://flug.idealo.de/deals/fernreisen/"
sourceStruct = "view-source:https://flug.idealo.de/deals/fernreisen/"

mainURL = "https://flug.idealo.de/deals/"
keyWords = {"herbstferien", "fernreisen", "sommerferien", "best-in-europe", "last-minute", "staedtereisen", "kurzurlaub", "warme-reiseziele"}


'''

from urllib.request import Request, urlopen
from bs4 import BeautifulSoup as bs
import html5lib
import requests
import urllib2

import time
from datetime import datetime 
import pandas as pd
import numpy as np
import csv

import ast
import re

url = 'https://flug.idealo.de/deals/fernreisen/'
soup = urlopen(url).bs


print(soup)



price = soup.find_all('span',class_="deals-card-offer-price")
flight_date = soup.find_all('div',class_="deals-card-date")
destin = soup.find_all('div',class_="deals-card-destination-container")
for el1, el2, el3 in [destin, flight_date, price]:
     print(el1['title'], el2.text.split(" - "), el3.text)

describe(price)
len(price), len(flight_date),len(destin)
	
while i<len(price):
    	


etfName = str(etfName.text)

flight_date = soup.find_all('div',class_="deals-card-date")
for elem in flight_date:
     print(elem.text.split(" - "))


flight_date = soup.find_all('div',{"class" : "deals-card-date", "class" : "deals-card-destination-container"})

titlesarray = []
for title in flight_date:
    titlesarray.append(title.text)