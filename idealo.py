
'''
Parsing tickets:

exampleURL = "https://flug.idealo.de/deals/fernreisen/"
sourceStruct = "view-source:https://flug.idealo.de/deals/fernreisen/"

mainURL = "https://flug.idealo.de/deals/"
keyWords = {"herbstferien", "fernreisen", "sommerferien", "best-in-europe", "last-minute", "staedtereisen", "kurzurlaub", "warme-reiseziele"}


'''

from urllib.request import Request, urlopen
from bs4 import BeautifulSoup
import pandas as pd
import time
from datetime import datetime 

start_time = time.time()

tsmw_url = "http://thestockmarketwatch.com/markets/pre-market/today.aspx"
# use alternative browser agent to bypass mod_security that blocks known spider/bot user agents
url_request = Request(tsmw_url, headers = {"User-Agent" : "mozilla/5.0"})
page = urlopen(url_request).read()

# collect all the text data in a list
text_data = []
soup = BeautifulSoup(page, "html.parser")

# get col data for p_change, tickers, prices and vol 
p_changes = list(map(lambda x: float(x.get_text()[:-1]), soup.find_all('div', class_ ="chgUp")))[:15]
tickers = list(map(lambda x: x.get_text(), soup.find_all('td', class_ = "tdSymbol")))[:15]
prices = list(map(lambda x: float(x.get_text()[1:]), soup.find_all('div', class_ = "lastPrice")))[:15]
# vols = list(map(lambda x: int(x.get_text()), soup.find_all('td', class_ = "tdVolume")))[:15]

# put lists into dataframe
df = pd.DataFrame(
        {'change (%)': p_changes,
         'ticker': tickers,
         'price ($)': prices
         })
    
change_criteria = df['change (%)'].map(lambda x: x > 8) # above 8% (temporary) 
price_criteria = df['price ($)'].map(lambda x: x > 0.5 and x < 5)     # 0.5 < price < 5
return list(df[change_criteria & price_criteria]['ticker'])
