
'''
Parsing tickets:

exampleURL = "https://flug.idealo.de/deals/fernreisen/"
sourceStruct = "view-source:https://flug.idealo.de/deals/fernreisen/"

mainURL = "https://flug.idealo.de/deals/"
keyWords = {"herbstferien", "fernreisen", "sommerferien", "best-in-europe", "last-minute", "staedtereisen", "kurzurlaub", "warme-reiseziele"}


'''

# ----------------------- 1st code block ---------------------------------------
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



