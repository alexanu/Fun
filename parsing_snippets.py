
from urllib.request import Request, urlopen
from bs4 import BeautifulSoup as bs
import html5lib
import requests

import time
from datetime import datetime 
import pandas as pd
import numpy as np
import csv

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

def _download(self, ticker, report_type):
        url = (r'http://financials.morningstar.com/ajax/' +
               r'ReportProcess4HtmlAjax.html?&t=' + ticker +
               r'&region=usa&culture=en-US&cur=USD' +
               r'&reportType=' + report_type + r'&period=12' +
               r'&dataType=A&order=asc&columnYear=5&rounding=3&view=raw')
        with urllib.request.urlopen(url) as response:
            json_text = response.read().decode(u'utf-8')
            json_data = json.loads(json_text)
            result_soup = BeautifulSoup(json_data[u'result'],u'html.parser')
            left = soup.find(u'div', u'left').div # Left node contains the labels
	    main = soup.find(u'div', u'main').find(u'div', u'rf_table') # Main node contains the (raw) data
	    year = main.find(u'div', {u'id': u'Year'})
	    self._year_ids = [node.attrs[u'id'] for node in year]
	    period_month = pd.datetime.strptime(year.div.text, u'%Y-%m').month
	    return pd.DataFrame(self._data,columns=[u'parent_index', u'title'] + list(self._period_range))	
	
for report_type, table_name in [(u'is', u'income_statement'), (u'bs', u'balance_sheet'),(u'cf', u'cash_flow')]:
	frame = self._download(ticker, report_type)
	result[table_name] = frame


# 10th code block ----------------------------------------------------------------------------------------        

    def download(self, ticker, conn = None, region = 'usa', culture = 'en-US'):
        url = (r'http://financials.morningstar.com/ajax/exportKR2CSV.html?' +
               r'&callback=?&t={t}&region={reg}&culture={cult}'.format(
                   t=ticker, reg=region, cult=culture))
        with urllib.request.urlopen(url) as response:
            tables = self._parse_tables(response)
            response_structure = [
                # Original Name, New pandas.DataFrame Name
                (u'Financials', u'Key Financials'),
                (u'Key Ratios -> Profitability', u'Key Margins % of Sales'),
                (u'Key Ratios -> Profitability', u'Key Profitability'),
                (u'Key Ratios -> Growth', None),
                (u'Revenue %', u'Key Revenue %'),
                (u'Operating Income %', u'Key Operating Income %'),

            frames = self._parse_frames(tables, response_structure)

            return frames


# 11th code block ----------------------------------------------------------------------------------------------------------        

def get_soup(url=''):
	headers = {'User-Agent': 'Mozilla/5.0 (Macintosh; Intel Mac OS X 10_11_5) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/50.0.2661.102 Safari/537.36'}
	html=requests.get(url, verify=False,headers=headers).text
	soup=BeautifulSoup(html, "html.parser")
	return soup

def get_text(soup=''):
	text_array=[]
	for script in soup(["script", "style"]):
		script.extract()
	text = soup.get_text()
	lines = (line.strip() for line in text.splitlines())
	chunks = (phrase.strip() for line in lines for phrase in line.split("  "))
	text = '\n'.join(chunk for chunk in chunks if chunk)
	text= text.encode('utf-8','ignore')
	return text		    

def get_text_element(soup='',TagName='',AttributeName='',AttributeValue=''):
	text_el=[]
	if AttributeName and AttributeValue !='':
		tag=soup(TagName,{AttributeName:AttributeValue})
		for t in tag:
			el=t.renderContents()
			text_el.append(el)	
	else:
		tag=soup(TagName)
		for t in tag:
			el=t.renderContents()
			text_el.append(el)
	for t in text_el:			
		t=soup.get_text().encode('utf-8-sig').strip()
	return text_el
		    
def get_classes(soup='',TagName='',AttributeName='',AttributeValue=''):
	classes=soup(TagName,{AttributeName:AttributeValue})
	return classes		    

		    
def get_from_bank(link,stock):
	soup=jscraper.get_soup(url=link['Profile'][0].replace('&t='+stock+':','&t='))
	Classes=jscraper.get_classes(soup=soup,TagName='tr',AttributeName='class',AttributeValue='text3')
	DayAvgVol=jscraper.get_text_element(soup=Classes[0],TagName='td')[0]
	Industry=jscraper.get_text_element(soup=Classes[1],TagName='td')[4]
	soup3=jscraper.get_soup(url=link['Profile'][2].replace('&t='+stock+':','&t='))
	Executives=' '.join(jscraper.get_text_element(soup=soup3,TagName='a'))
	soup5=jscraper.get_soup(url=link['Stocks'][0].replace('&t='+stock+':','&t='))	     
	Keystats=' '.join(jscraper.get_text_element(soup=soup5,TagName='tbody')).strip().lstrip()
	Keystats=' '.join(Keystats.split())
	jsondata={'DayAvgVol':DayAvgVol,'Industry':Industry,'Executives':Executives,'Keystats':Keystats}
	return jsondata



# 12th code block ----------------------------------------------------------------------------------------------------------        
	    
print datetime.datetime.now()
print "Finviz Performance Start"

# Overview = 111, Valuation = 121, Financial = 161, Ownership = 131, Performance = 141
# pagesarray = [111,121,161,131,141]

url = "http://www.finviz.com/screener.ashx?v=141&f=geo_usa"
response = requests.get(url)
html = response.content
soup = BeautifulSoup(html)
firstcount = soup.find_all('option')
lastnum = len(firstcount) - 1
lastpagenum = firstcount[lastnum].attrs['value']
currentpage = int(lastpagenum)

alldata = []
templist = []

titleslist = soup.find_all('td',{"class" : "table-top"})
titleslisttickerid = soup.find_all('td',{"class" : "table-top-s"})
titleticker = titleslisttickerid[0].text
titlesarray = []
for title in titleslist:
    titlesarray.append(title.text)

titlesarray.insert(1,titleticker)
i = 0
currentpage = 21
while(currentpage > 0):
    i += 1
    print str(i) + " page(s) done"
    secondurl = "http://www.finviz.com/screener.ashx?v=" + str(141) + "&f=geo_usa" + "&r=" + str(currentpage)
    secondresponse = requests.get(secondurl)
    secondhtml = secondresponse.content
    secondsoup = BeautifulSoup(secondhtml)
    stockdata = secondsoup.find_all('a', {"class" : "screener-link"})
    stockticker = secondsoup.find_all('a', {"class" : "screener-link-primary"})
    datalength = len(stockdata)
    tickerdatalength = len(stockticker)

    while(datalength > 0):
        templist = [stockdata[datalength - 15].text,stockticker[tickerdatalength-1].text,stockdata[datalength - 14].text,stockdata[datalength - 13].text,stockdata[datalength - 12].text,stockdata[datalength - 11].text,stockdata[datalength - 10].text,stockdata[datalength - 9].text,stockdata[datalength - 8].text,stockdata[datalength - 7].text,stockdata[datalength - 6].text,stockdata[datalength - 5].text,stockdata[datalength - 4].text,stockdata[datalength - 3].text,stockdata[datalength - 2].text,stockdata[datalength - 1].text,]
        alldata.append(templist)
        templist = []
        datalength -= 15
        tickerdatalength -= 1
    currentpage -= 20

with open('stockownership.csv', 'wb') as csvfile:
    ownership = csv.DictWriter(csvfile, delimiter=',', lineterminator='\n', fieldnames=titlesarray)
    ownership.writeheader()

    for stock in alldata:
        ownership.writerow({titlesarray[0] : stock[0], 
			    titlesarray[1] : stock[1],
			    titlesarray[2] : stock[2],
			    titlesarray[3] : stock[3],
			    titlesarray[4] : stock[4]})

print datetime.datetime.now()
print "Finviz Ownership Completed"


		    
# 13th code block ----------------------------------------------------------------------------------------------------------        
		    
url = "http://www.finviz.com/quote.ashx?t=intc"
response = requests.get(url)
html = response.content
soup = BeautifulSoup(html)
titleslist = soup.find_all('a',{"class" : "tab-link-news"})		    
		    
		    
# 14th code block ----------------------------------------------------------------------------------------------------------    		    
		    
finviz_url = "http://finviz.com/screener.ashx?v=111&s=ta_topgainers&f=sh_curvol_o500,sh_price_1to20"
page = urlopen(finviz_url)

hasNextPage = True
firstPage = True
currentPageIndex = 0 # from page 2 onwards 
text_data = [] # collect all the text data in a list

while hasNextPage: 
	if not firstPage:
		finviz_url += "&r=" + str(currentPageIndex)
		page = urlopen(finviz_url)
	soup = BeautifulSoup(page, "html.parser")
        
        html_data = soup.find_all('td', class_="screener-body-table-nw")
        counter = 0 
        for row in html_data:
            counter+= 1
            text_data.append(row.get_text())

        firstPage = False
        if currentPageIndex == 0:
            currentPageIndex += 21
        else:
            currentPageIndex += 20 
        if counter < 220:
            hasNextPage = False       


# 15th code block ----------------------------------------------------------------------------------------------------------    		    
		    
	    
		    
req = requests.get("https://finviz.com/quote.ashx?t=FB")
soup = BeautifulSoup(req.content, 'html.parser')
table = soup.find_all(lambda tag: tag.name=='table')
rows = table[8].findAll(lambda tag: tag.name=='tr')
out=[]
for i in range(len(rows)):
	td=rows[i].find_all('td')
	out=out+[x.text for x in td]

ls=['Ticker','Sector','Sub-Sector','Country']+out[::2]

dict_ls={k:ls[k] for k in range(len(ls))}
df=pd.DataFrame()

for j in range(len(symbols)):
	req = requests.get("https://finviz.com/quote.ashx?t="+symbols[j])
	if req.status_code !=200:
		continue
	soup = BeautifulSoup(req.content, 'html.parser')
	table = soup.find_all(lambda tag: tag.name=='table')

	rows=table[6].findAll(lambda tag: tag.name=='tr')
	sector=[]
	for i in range(len(rows)):
		td=rows[i].find_all('td')
		sector=sector+[x.text for x in td]
	sector=sector[2].split('|')
	rows = table[8].findAll(lambda tag: tag.name=='tr')
	out=[]
	for i in range(len(rows)):
		td=rows[i].find_all('td')
		out=out+[x.text for x in td]
	out=[symbols[j]]+sector+out[1::2]
	out_df=pd.DataFrame(out).transpose()
	df=df.append(out_df,ignore_index=True)

df=df.rename(columns=dict_ls)

output.put(df)		    
		    
