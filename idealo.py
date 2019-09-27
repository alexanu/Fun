
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

import time
from datetime import datetime 
import pandas as pd
import numpy as np
import ast
import re


# ----------------------- 1st code block ---------------------------------------

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


# ------------ 2nd code block -----------------------------------------------------------------------------------

    div_data = soup.find_all('div', id="_advanced")
    tbody_data = []
    # find table data in html_data 
    for elem in div_data:
        tbody_data = elem.find_all('td')
    stocks = []        
    for stock in tbody_data:
        stocks.append(stock.get_text())


# ------------ 3rd code block -----------------------------------------------------------------------------------

        date = dt.datetime.today().strftime('%Y-%m-%d')
        data = []
        header = ['Ticker', 'Recommendation', 'Target Price', 'Current Price']
        url = 'http://www.marketwatch.com/investing/stock/' + ticker + '/analystestimates'
        page = urllib2.urlopen(url)
        soup = BeautifulSoup(page)
        tr = soup.find('tr')
        price = soup.find('p', {"class":"data bgLast"}).text
        target = tr.findAll('td')[-1].text
        rec = str(tr.find('td', attrs={'class': 'recommendation'}).text)
        data.append([ticker, rec, target, price])
        df = pd.DataFrame(data, columns=header)        
        df['Date'] = date
        df = df.set_index(['Date'])
        df.index = pd.to_datetime(df.index)
        df['Target Price'] = pd.to_numeric(df['Target Price'], errors='coerce')
        df['Current Price'] = pd.to_numeric(df['Current Price'], errors='coerce')
        return df 

# -------- 4th code block --------------------------------------------------------------------------------------------

        sup = []
        url = 'http://www.nasdaq.com/symbol/' + ticker + '/earnings-surprise'
        page = urllib2.urlopen(url)
        soup = BeautifulSoup(page)
        table = soup.find('div', attrs={'class': 'genTable'}).find('table').findAll('tr')[1:]
        temp = []
        headers = []
        for td in table:
            tData = td.findAll('td')
            data = tData[4].text
            temp.insert(0, data)
            headData = tData[1].text
            headData = dt.datetime.strptime(headData, '%m/%d/%Y')
            headData = headData.strftime('%Y-%m-%d')
            headers.insert(0, headData)

        sup.append(temp)
        df = pd.DataFrame(sup, columns=headers) 
        df = df.transpose()
        df = df.rename(columns={0: 'Surprise'})
        df['Ticker'] = ticker
        df.index.name = 'Date'
        cols = df.columns.tolist()
        cols.insert(0, cols.pop(cols.index('Ticker')))
        df = df.reindex(columns=cols)
        df.index = pd.to_datetime(df.index)
        df['Surprise'] = pd.to_numeric(df['Surprise'], errors='coerce')
        df.to_string(columns=['Ticker'])
        return df 

#--------5th code block ------------------------------------------------------------------------------

    for ticker in ticker_list:

        print "getting data for", ticker
        time.sleep(1) #don't scrape to fast and overload their servers!

        try:
            df = quarterly_fundamentals(ticker)
            if len(quarterly_df) == 0: #empty df, need to create
                quarterly_df = df
            else: #append 
                quarterly_df = quarterly_df.append(df, ignore_index=False)
        except:
            print "Could not access quart", ticker

#--------5th code block ------------------------------------------------------------------------------

url = "http://bloomberg.com/quote/" + str(ticker) + ":US"
html = urllib.request.urlopen(url).read()
soup = bs(html, "lxml")
ratio_pattern = re.compile(r'Expense Ratio')		
percent_pattern = re.compile(r'%$')
ratio = soup.find('div', text=ratio_pattern).find_next_sibling().text.rstrip('\n ').lstrip('\n ')
self.expense_ratio = self.convert_percent(ratio)

#--------6th code block ------------------------------------------------------------------------------

url='http://etfdailynews.com/tools/what-is-in-your-etf/?FundVariable=' + str(ticker)
# decode to unicode, then re-encode to utf-8 to avoid gzip
html = urllib.request.urlopen(url).read().decode('cp1252').encode('utf-8')
soup = bs(html, "lxml")

# Build Holdings Table - find the only tbody element on the page
holdings_table = "<table>" + str(soup.tbody).lstrip('<tbody>').rstrip('</tbody') + "</table>"

# Fetch expense ratio
ratio_pattern = re.compile(r'Expense Ratio')		
percent_pattern = re.compile(r'%$')		
td = soup.find('td', text=ratio_pattern)		
if not td: 		
        return False		
# find_next_siblings returns a Result Set object - take first matching item and strip the tags
expense_ratio = str(td.find_next_siblings('td', text=percent_pattern)[0]).lstrip('<td>').rstrip('</td>')		
self.expense_ratio = self.convert_percent(expense_ratio)

#--------7th code block ------------------------------------------------------------------------------


def clean_name(str_input): 
        if "<span" in str_input:
                soup = bs(str_input, "lxml")
                return soup.find('span')['onmouseover'].lstrip("tooltip.show('").rstrip(".');")
        return str_input

def clean_ticker(str_input):
        soup = bs(str_input, "lxml")
        return soup.find('a').text

def clean_allocation(str_input): 
        if str_input == "NA":
                return 0
        return float(str_input)/100

url = 'https://www.zacks.com/funds/etf/' + str(ticker) + '/holding'
html = urllib.request.urlopen(url).read().decode('cp1252')
str_start, str_end = html.find('data:  [  [ '), html.find(' ]  ]')
if str_start == -1 or str_end == -1: 
        # If Zacks does not have data for the given ETF
	print("Could not fetch data for {}".format(ticker))
	return
list_str = "[["+html[(str_start+12):str_end]+"]]"
holdings_list = ast.literal_eval(list_str)

df = pd.DataFrame(holdings_list).drop(2,1).drop(4,1).drop(5,1)
df.columns = ['name', 'ticker', 'allocation']
df['allocation'] = df.allocation.map(lambda x: clean_allocation(x))
df['name'] = df.name.map(lambda x: clean_name(x))
df['ticker'] = df.ticker.map(lambda x: clean_ticker(x))
self.holdings, self.num_holdings = df, len(df)


# 8th code block ----------------------------------------------------------------------------------------

self.rootURLStr = StringVar()

self.rootURLNum = self.rootURLNum.get()
if(self.rootURLNum == 1):
	self.rootURLStr = "http://www.etf.com/"
elif(self.rootURLNum == 2):
	self.rootURLStr = "http://www.maxfunds.com/funds/data.php?ticker="
elif(self.rootURLNum == 3):
        self.rootURLStr = "http://www.marketwatch.com/investing/Fund/"


class ETFDataCollector:
	def __init__(self, etfSymbol, row, baseURL):
		self.etfSymbol = etfSymbol
		self.row = row 
		self.baseURL = baseURL
		self.ETFInfoToWrite = []

	def parseTargetWebPage(self):
		try:
			website = urllib2.urlopen(self.baseURL + self.etfSymbol)
			sourceCode = website.read()
			self.soup = BeautifulSoup(sourceCode)
		except:
			e = sys.exc_info()[0]
			print self.etfSymbol + " Cannot Be Found while parsing " + str(e)
			e = ""
		else:
			pass

	def etfDotComInfo(self):
		row = self.row
		etfName = self.soup.find('h1', class_="etf") #parse document to find etf name 
		#extract etfName contents (etfTicker & etfLongName)
		etfTicker = etfName.contents[0]
		etfLongName = etfName.contents[1]
		etfTicker = str(etfTicker)
		etfLongName = etfLongName.text
		etfLongName = str(etfLongName)

		#get the time stamp for the data scraped 
		etfInfoTimeStamp = self.soup.find('div', class_="footNote")
		dataTimeStamp = etfInfoTimeStamp.contents[1]

		#create vars 
		etfScores = []
		cleanEtfScoreList = []
		etfScores = self.soup.find_all('div', class_="score") # find all divs with the class score
		for etfScore in etfScores: #clean them and add them to the cleanedEtfScoreList
			strippedEtfScore = etfScore.string.extract()
			strippedEtfScore = str(strippedEtfScore)
			cleanEtfScoreList.append(strippedEtfScore)
                        
		#turn cleanedEtfScoreList into a dictionary for easier access
		self.ETFInfoToWrite = [etfTicker, etfLongName, formatedTimeStamp, int(cleanEtfScoreList[0]), int(cleanEtfScoreList[1]), int(cleanEtfScoreList[2])]
		

	def maxfundsDotComInfo(self):
		row = self.row
 		etfName = self.soup.find('div', class_="dataTop")
 		etfName = self.soup.find('h2')
 		etfName = str(etfName.text)
 		endIndex = etfName.find('(')
 		endIndex = int(endIndex)
 		fullEtfName = etfName[0:endIndex]
 		startIndex = endIndex + 1
 		startIndex = int(startIndex)
 		lastIndex = etfName.find(')')
 		lastIndex = int(lastIndex)
 		lastIndex = lastIndex - 1
 		tickerSymbol = etfName[startIndex: lastIndex]
 		etfMaxRating = self.soup.find('span', class_="maxrating") #get ETFs Max rating score
 		etfMaxRating = str(etfMaxRating.text)
 		self.ETFInfoToWrite = [fullEtfName, tickerSymbol, int(etfMaxRating)] #create array to store name and rating 
 		ETFInfoToWrite = self.ETFInfoToWrite
 		excel = excelSetup(ETFInfoToWrite,row)
		excel.maxfundsSetup()

	def smartmoneyDotComInfo(self):
		row = self.row
 		etfName = self.soup.find('h1', id="instrumentname")
 		etfName = str(etfName.text)
 		etfTicker = self.soup.find('p', id="instrumentticker")
 		etfTicker = str(etfTicker.text)
 		etfTicker = etfTicker.strip()

 		self.ETFInfoToWrite.append(etfName)
 		self.ETFInfoToWrite.append(etfTicker)

 		#get Lipper scores ***NEEDS REFACTORING***
 		lipperScores = self.soup.find('div', 'lipperleader')
 		lipperScores = str(lipperScores)
 		lipperScores = lipperScores.split('/>')
 		for lipperScore in lipperScores:
 			startIndex = lipperScore.find('alt="')
 			startIndex = int(startIndex)
 			endIndex = lipperScore.find('src="')
 			endIndex = int(endIndex)
 			lipperScore = lipperScore[startIndex:endIndex]
 			startIndex2 = lipperScore.find('="')
 			startIndex2 = startIndex2 + 2
 			endIndex2 = lipperScore.find('" ')
 			lipperScore = lipperScore[startIndex2:endIndex2]
 			seperatorIndex = lipperScore.find(':')
 			endIndex3 = seperatorIndex
 			startIndex3 = seperatorIndex + 1

 			lipperScoreNumber = lipperScore[startIndex3:]
 			if lipperScoreNumber == '' and lipperScoreNumber == '':
 				pass
 			else:
 				self.ETFInfoToWrite.append(int(lipperScoreNumber))

                
for etfSymbol in fundList:
	row += 1
	myEtf = ETFDataCollector(etfSymbol, row, self.rootURLStr)
	myEtf.parseTargetWebPage()
	#use an if statement to find out which website we are scraping
	if(self.rootURLStr == "http://www.etf.com/"):
		myEtf.etfDotComInfo()
	elif(self.rootURLStr == "http://www.maxfunds.com/funds/data.php?ticker="):
		myEtf.maxfundsDotComInfo()
	elif(self.rootURLStr == "http://www.marketwatch.com/investing/Fund/"):
		myEtf.smartmoneyDotComInfo()
        
# 9th code block ----------------------------------------------------------------------------------------        
# Put here smth from morningstar project


# 10th code block ----------------------------------------------------------------------------------------        















