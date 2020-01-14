

import requests, bs4
import urllib.request
import shutil
import sys
import os
import os.path
from selenium import webdriver
import time
import json
from pprint import pprint
import re
from twilio.rest import TwilioRestClient




url = "https://www.kayak.com/flights/PIT-DEN/2017-04-19/2017-04-26"

#url = "https://www.kayak.com/flights/" + startAirport + "-" + endAirport + "/" + startDate + "/" + endDate

headers = {'User-Agent': 'Mozilla/5.0 (Macintosh; Intel Mac OS X 10_10_1) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/39.0.2171.95 Safari/537.36'}

res = requests.get(url, headers=headers)
res.raise_for_status()
soup = bs4.BeautifulSoup(res.text, 'html.parser')

pricePanel = soup.select("#searchResultsList")

print(str(pricePanel))

before_scrape_time = 5
wait_time = 1 
sleep_time = 60*5 #seconds
alertPrice = 600

## FLight Data
loc1 = "BDL"
loc2 = "HKG"	#"LAX"
date1 = "2017-04-18"
date2 = "2017-04-22"

user_actn = "caleb" ## must tailor os. locations to your computer
file_path = "/home/"+user_actn+"/Downloads/data.json"

priceAlertZone = 0


while(1):

	if os.path.exists(file_path):
		os.remove(file_path) 

	chromedriver = "/usr/bin/chromedriver"
	os.environ["webdriver.chrome.driver"] = chromedriver
	driver = webdriver.Chrome(chromedriver)
	driver.get("https://www.kayak.com/flights/"+loc1+"-"+loc2+"/"+date1+"/"+date2)

	time.sleep(wait_time)

	driver.execute_script("""
	var script = document.createElement( 'script' );
	script.type = 'text/javascript';
	url = "//medialab.github.io/artoo/public/dist/artoo-latest.min.js";
	script.src = url;
	$("body").append( script );
	""")

	time.sleep(before_scrape_time)  
	driver.execute_script("""
	artoo.scrape('.bigPrice', {
	  content: 'text'
	}, artoo.savePrettyJson);
	""")

	time.sleep(wait_time) #enough time to download?
	driver.quit()


	if os.path.exists(file_path):
		with open(file_path) as data_file:    
		    data = json.load(data_file)

		lowPrice = data[0]["content"]
		lowPrice = lowPrice[1:]
		print('Low Price:'+lowPrice)
		if(float(lowPrice) <= alertPrice and priceAlertZone == 0):
			priceAlertZone = 1
			print('Zone:'+str(priceAlertZone))

			###TWILIO
			### put your own credentials here
			ACCOUNT_SID = 'ACbd3283ed65be0d347aa621dd4fbac5d8'  #'<AccountSid>'
			AUTH_TOKEN = '27cc9d1a87b03c7e203d952a0307be5a'  #'<AuthToken>'
			client = TwilioRestClient(ACCOUNT_SID, AUTH_TOKEN)
			client.messages.create(
			to =    '8607597185',	#'<ToNumber>',
			from_ = '8609692659',	#'<FromNumber>',
			body =  'PYTHON: LOWEST PRICE IS:'+str(lowPrice),	#'<BodyText>',
			)
		elif(float(lowPrice) >= alertPrice and priceAlertZone == 1):
			priceAlertZone = 0
			print('Zone:'+str(priceAlertZone))
			ACCOUNT_SID = 'ACbd3283ed65be0d347aa621dd4fbac5d8'  #'<AccountSid>'
			AUTH_TOKEN = '27cc9d1a87b03c7e203d952a0307be5a'  #'<AuthToken>'
			client = TwilioRestClient(ACCOUNT_SID, AUTH_TOKEN)
			client.messages.create(
			to =    '8607597185',	#'<ToNumber>',
			from_ = '8609692659',	#'<FromNumber>',
			body =  'Your Low Price Has Ended:'+str(lowPrice),	#'<BodyText>',
			)
		elif(priceAlertZone == 1):
			#print("continued price alert zone")
			print("Zone:1")

	else:
		print("file did not download properly")


	### Exit program
	time.sleep(sleep_time)

sys.exit()