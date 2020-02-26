# Source: https://github.com/Rage997/Cheap-Flight-Finder/blob/master/main.py

from torrequest import TorRequest
import smtplib



tr=TorRequest(password='efaage')
#
# import requests
# response= requests.get('http://ipecho.net/plain')
# print ("My Original IP Address:",response.text)

tr.reset_identity() #Reset Tor
response= tr.get('http://ipecho.net/plain')
print ("New Ip Address",response.text)


# Email settings
gmailUsername = "nick.zup@gmail.com"
gmailPassword = "efaage7568850"

def sendmail(username,password,msg):
    server = smtplib.SMTP('smtp.gmail.com:587')
    server.starttls()
    server.login(username,password)
    server.sendmail(username, username, msg)
    server.quit()

def searchOpodo(searchURL,maxPrice):
    # GET from server
    try:
        response = tr.get(searchURL)
    except Exception:
        sys.exit(
            'Problem finding your search page, please check the address in config.txt (searchURL) is correct and your network connection.')

    # the entire page as a string
    htmlPageAsString = response.read()

    # look for prices
    priceIndices = [m.start() for m in re.finditer(searchTerm, htmlPageAsString)]
    # print priceIndices
    minPrice = 1e9
    for index in priceIndices:
        priceSubString = htmlPageAsString[index:index + 20].split()[1].split("<")[0].replace(",", "")
        price = float(priceSubString)
        if price < minPrice: minPrice = price
        if price < maxPrice:
            message = "Time to check the flight company; the flight is available for " + str(
                price) + " GBP.\nFollow this link for the search results: " + searchURL + "\nGo, go, go!"
        print(message)
        sendmail(gmailUsername, gmailPassword, message)
        return


    print ('Min price for search was ' + minPrice + '... better luck next time!')
    return


if __name__ == "__main__":
    searchURL = " http://www.opodo.co.uk/opodo/flights/search?tripType=R&departureAirportCode=LON&departureAirport=London%2C%2520London%2C%2520United%2520Kingdom%2520%255BLON%255D&departureDay=17&departureMonth=201304&departureTime=ANY&arrivalAirportCode=KUL&arrivalAirport=Kuala%2520Lumpur%2520International%2520Airport%2C%2520Kuala%2520Lumpur%2C%2520Malaysia%2520%255BKUL%255D&directFlight=false&flexible=false&numberOfAdults=1&numberOfChildren=0&numberOfInfants=0&cabinType=&backButton=false&searchLowCost=true&includeRailAndFly=false&returnDay=17&returnMonth=201305&returnTime=ANY"

    searchOpodo(searchURL, 200)
