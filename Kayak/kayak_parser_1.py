from lxml import html
import requests
#import isbnlib
import re
import time

def buildKayakURL( departA, departB, returnA, returnB, departDate, returnDate):
    print("Depart:")
    print(departA + " --> " + departB + " on " + departDate)
    print("Return:")
    print(returnA + " --> " + returnB + " on " + departDate)

    # append to https://www.kayak.com/flights/
    url = 'https://www.kayak.com/flights/' + departA + '-' + departB + "/" + departDate + "/"
    url = url + returnA + "-" + returnB + "/" + returnDate + "/"
    print(url)

    # get Amazon page
    headers = {
        'User-Agent': 'Mozilla/5.0 (Windows NT 6.1) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/41.0.2228.0 Safari/537.36',
    }
    tries = 1
    page = requests.get(url,headers=headers)
    while not page.status_code==requests.codes.ok and tries < 10:
        time.sleep(1)
        page = requests.get(url)
        print ( "Tries = " + str(tries) )
        tries = tries + 1

    tree = html.fromstring( page.text )
    # tree = html.parse(url)

    return tree


def getCheapestPrice( tree ):
    # find product name
    title =  tree.xpath('//h1[@id="title"]/span[@id="productTitle"]/text()')

    # find product dimensions
    dims =  tree.xpath('//li/b[contains(text(),"Product Dimensions:")]/following-sibling::text()')
    
    sizes = re.findall(r'\d+\.\d+|\d+',dims[0])
    sWidth = 'NaN'
    if(sizes):
        sWidth = min(sizes)
    # find page number and if it's paperback or hardcover
    bookType = 'None'
    pageNumbers = '0'
    hardcover = tree.xpath('//li/b[contains(text(),"Hardcover:")]/following-sibling::text()')
    paperback = tree.xpath('//li/b[contains(text(),"Paperback:")]/following-sibling::text()')

    if paperback:
        bookType = 'Paperback'
        pageNumbers = re.findall(r'\d+',paperback[0])
    elif hardcover:
        bookType = 'Hardcover'
        pageNumbers = re.findall(r'\d+',hardcover[0])
 
    print (sizes)
    print ( title[0] )
    print ( bookType + ": " + pageNumbers[0] )
    print ("Spine width is " + sWidth)
    return title[0],sWidth


def getBookInfo( isbn ):
    # tree = getAmznPageByISBN( '9780830844111' )
    #tree = getAmznPageByISBN( '9780545010221' )
    tree = getAmznPageByISBN(isbn[0])
    return getProductDimensions( tree );
    
def main():
    #tree = getAmznPageByISBN( '0830844112' )
    # getProductDimensions( tree );
    tree = buildKayakURL('MSP','PVG','HKG','MSP','2017-08-27','2017-09-08')
    print tree

if __name__ == "__main__":
    main()