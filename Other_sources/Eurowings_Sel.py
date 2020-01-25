# Source: https://github.com/beyersdp/WebCrawler



from selenium import webdriver
from selenium.webdriver.common.keys import Keys
from selenium.webdriver.common.desired_capabilities import DesiredCapabilities
from selenium.common.exceptions import InvalidElementStateException, NoSuchElementException
from datetime import datetime, timedelta
import os

'''
	Function Summary:
	- generateQuery(url) 
		-> url = Link to the eurowings homepage
		<- res = array with all flights from Stuttgart at date_b and from Berlin at date_e
		<- False = if an error occurs
		
	- generateQuery(url, date_b=, date_e=)
		-> date_b = datetime object with %d.%m.%y that indicates the date for the flight from Stuttgart
		   default = tomorrow
		-> date_e = datetime object with %d.%m.%y that indicates the date for the flight from Berlin
		   default = tomorrow + 3 days
		   
	- saveResults(res)
		-> res = array with flights from Stuttgart and from Berlin at one date per departure (vgl. generateQuery(...))
		<- True = if data is saved in file with actuall date and header informations per flight tuple in it
		<- False = if an error occurs
		
	- saveResults(res, date_b=, date_e=) [harmonizes with generateQuery(...)]
		-> date_b = datetime object with %d.%m.%y that indicates the date for the flight from Stuttgart
		   default = tomorrow
		-> date_e = datetime object with %d.%m.%y that indicates the date for the flight from Berlin
		   default = tomorrow + 3 days
	
	- autoQueryAndSave(date_bIN, date_eIN, stop)
		-> date_bIn = string (e.g. "12.02.99") that indicates the start date for all following querys from Stuttgart
		-> date_eIn = string (e.g. "12.02.99") that indicates the start date for all following querys from Berlin
		-> stop = string (e.g. "12.02.99") that terminates the automatic if date_eIN reaches that date
		<- False = if an error occurs
	
	- printFlightList(flightList)
		-> flightList = array in memory with flights and headers from files or querys
		<-
	- analyzeFile(fileName)
		-> fileName = name of a data file in the result directory
		
	- analyzeFile(fileName, showHeaders=, showFlights=)
		-> showHeader = boolean
		   default = False
		-> showFlights = boolean
		   default = False
	
	-  getDayFromFile(fileName, date)
		-> fileName = name of a data file in the result directory
		-> date = string (e.g. 19990212) that indicates the date for the search in the file
		<- res  = array with all flights at that date with headers
		<- False = if no flights at that date in the file
	
	- getDay(date)
		-> date = string (e.g. 19990212) that indicates the date for the search in the directory
		<- res = array with all flights at the date with headers
		<- False = if an error occurs
	
	- plotDay(data, date) [harmonizes with getDayFromFile or getDay]
		-> data = array with multiple flights + headers at given date
		-> date = date of the flights in the array
	
	- getFlightFromFile(fileName, flightHour)
		-> fileName = name of a data file in the result directory
		-> flightHour = string (e.g. "14") that indicates the hour for the searched flight
		<- res = array with all flights and headers at the given hour
		<- False = if an error occurs
	
	- getFlight(flightHour)
		-> flightHour = string (e.g. "14") that indicates the hour for the searched flight
		- res = array with all flights and headers at the result directory
		<- False = if an error occurs
	
	- plotFlight(data, hour) [harmonizes with getFlightFromFile or getFlight]
		-> data = array with mutliple flights + headers in a given hour
		-> hour = string (e.g. "14") that indicates the hour of the given flight data
	
	- getCheapestFromFile(fileName, verbose=False)
		-> fileName = name of a data file in the result directory
		<- res = array with list of headers and prices
	
	- getCheapest(verbose=False) [harmonizes with getCheapestFromFile]
		<- res = array with list of headers and prices
	
	- analyzeCheapest(flightList) [harmonizes with getCheapestFromFile and getCheapest]
		-> flightList = array with lists of query headers and low price flight data 
		<- res = array with lists of unique latest query headers and flights 
'''





# function that opens a webside by given url
# and inputs parameters to find flights
# from Stuttgart to Berlin-Tegel
def generateQuery(url, date_b=datetime.now() + timedelta(days=1), date_e=datetime.now() + timedelta(days=3)):

	# init web driver with given url
	driver = webdriver.Chrome()
	driver.get(url)
	
	# input the parameters for the flight search
	try:
		departure = driver.find_element_by_id("gid-autocomplete-1-input")
		departure.send_keys("Stuttgart")
		destination = driver.find_element_by_id("gid-autocomplete-2-input")
		destination.send_keys("Berlin-Tegel")
		begin = driver.find_element_by_id("gid-autocomplete-3-input")
		begin.send_keys(date_b.strftime("%d.%m.%y")) 
		end = driver.find_element_by_id("gid-autocomplete-4-input")
		end.send_keys(date_e.strftime("%d.%m.%y")) 
		end.send_keys(Keys.ENTER)
		submit = driver.find_element_by_css_selector(".a-cta.a-cta--block.a-cta-prio1")
		submit.click()
	except InvalidElementStateException:
		print("[GENERATE-QUERY][ERR] Problem by inputting the parameters\n")
		return False
	except NoSuchElementException:
		print("[GENERATE-QUERY][ERR] Problem by inputting the parameters\n")
		return False
	except Exception:
		print("[GENERATE-QUERY][FATAL ERR] No specific Exception Handler\n")
		return False
	
	# iterate over flights and save time, destination and price in result list
	res = []
	for flight in driver.find_elements_by_xpath("//*[@data-number-of-flights='false']"):
		details = []
		
		try:
			details.append(flight.find_element_by_css_selector(".ibe-flight-selection-time.inline-block.ibe-full-width").text)
			details.append(flight.find_element_by_css_selector(".ibe-flight-selection-grey-text").text)
			details.append((flight.find_element_by_css_selector(".ibe-flight-selection-price-placeholder").text).replace(",","."))
			res.append(details)
		except NoSuchElementException:
			print("[GENERATE-QUERY][ERR] Problem by reading the flights\n")
			return False
		except Exception:
			print("[GENERATE-QUERY][FATAL ERR] No specific Exception Handler\n")
			return False
	
	driver.close()
	
	if res == []:
		print("[GENERATE-QUERY][ERR] No flights found\n")
		return False
	
	return res



# function that saves the flight result list
# in a file per date in result directory
def saveResults(res, date_b=datetime.now() + timedelta(days=1), date_e=datetime.now() + timedelta(days=3)):
	date = datetime.now().strftime('%d.%m.%y')
	time = datetime.now().strftime('%H.%M.%S')
	
	try:
		file = open('results/' + date + '.ew', 'a')
	except IOError:
		print("[SAVE-RESULTS][ERR] Cannot open file results/" + date + ".ew")
		return False
	
	print("[SAVE-RESULTS] Open file results/" + date + ".ew")
	file.write("H," + date + "," + time + "\n")
	
	for flight in res:
		if flight[1] == "Stuttgart":
			file.write("{},{},{},{}\n".format(date_b.strftime("%Y%m%d"), flight[0], flight[1], flight[2].replace(' €', '')))
		if flight[1] == "Berlin-Tegel":
			file.write("{},{},{},{}\n".format(date_e.strftime("%Y%m%d"), flight[0], flight[1], flight[2].replace(' €', '')))
	
	file.close()
	return True


	
# function that automatically creates results
# for a given date range and saves them in the result directory
def autoQueryAndSave(date_bIN, date_eIN, stop):
	
	# convert given strings to date object
	try:
		date_b = datetime.strptime(date_bIN, '%d.%m.%y')
		date_e = datetime.strptime(date_eIN, '%d.%m.%y')
	except ValueError:
		print("[AUTOQUERY][ERR] ValueError - cannot convert strings to date object")
		return False
	
	while date_e.strftime('%d.%m.%y') != stop:
		print("[AUTOQUERY] Search flights for {} and {}".format(date_b.strftime('%d.%m.%y'), date_e.strftime('%d.%m.%y')))
		res = generateQuery("https://www.eurowings.com/de.html", date_b=date_b, date_e=date_e)
		if res:
			saveResults(res, date_b=date_b, date_e=date_e)
		
		date_b = date_b + timedelta(days=1)
		date_e = date_e + timedelta(days=1)


	
# function thats prints a given flight list
# with additional informations
def printFlightList(flightList):
	
	if not flightList:
		print("[PRINTFLIGHTLIST][ERR] Value Error - no flight data")
		return False
	
	lastDate = ""
	lastDest = ""
	lastH = ""
	lowestPrice = 0.0
	highestPrice = 0.0
	numFlights = 0
	
	for flight in flightList:
		
		if flight[0] == "H":
			lastH = flight.replace("\n","")
			print("\nSource: " + lastH)
			
		else:
			flightData = flight.split(",")
			
			if lastDate == "":
				lastDate = flightData[0]
				print("\nFlights at {}.{}.{}:".format(flightData[0][6:8], flightData[0][4:6], flightData[0][0:4]))
			
			if lastDest == "":
				lastDest = flightData[2]
			
			if lastDest != flightData[2]:
				print("")
				lastDest = flightData[2]
			
			
			if lastDate == flightData[0]:
				print(" - {} from {} (Price = {}€)".format(flightData[1], flightData[2], flightData[3].replace("\n", "")))
				numFlights +=  1
		
			else:
				lastDate = flightData[0]
				print("\nFlights at {}.{}.{}".format(flightData[0][6:8], flightData[0][4:6], flightData[0][0:5]))
				print(" - {} from {} (Price = {}€)".format(flightData[1], flightData[2], flightData[3].replace("\n", "")))
				numFlights += 1
			
			
			if lowestPrice == 0.0:
				lowestPrice = float(flightData[3])
			
			if lowestPrice > float(flightData[3]):
				lowestPrice = float(flightData[3])
			
			if highestPrice < float(flightData[3]):
				highestPrice = float(flightData[3])
	
	print("\nNumber of Flights = {}".format(numFlights))
	print("Highest Price     = {}€".format(highestPrice))
	print("Lowest Price      = {}€".format(lowestPrice))



# function that analyzes a given flight file
# with multiple measurements and sums
def analyzeFile(fileName, showHeaders=False, showFlights=False):
	
	numH = 0
	flightsD = dict()
	
	with open('results/' + fileName, 'r') as file:
		for line in file:
			
			if line[0] == "H":
				numH += 1
				if showHeaders:
					print("[ANALYZEFILE][HEADERS] " + line.replace("\n", ""))
			
			else:
				flightData = line.split(",")
				key = flightData[0] + "&" + flightData[2]
				
				if key in flightsD:
					flightsD[key] += 1
				else:
					flightsD[key] = 1
	
	fromStuttg = 0
	fromBerlin = 0
	

	for k,v in flightsD.items():
		if showFlights:
			if k.split("&")[1] == "Stuttgart":
				print("[ANALYZEFILE][FLIGHTS] {} from {}    {}x".format(k.split("&")[0], k.split("&")[1], v))
			else:
				print("[ANALYZEFILE][FLIGHTS] {} from {} {}x".format(k.split("&")[0], k.split("&")[1], v))
		
		if k.split("&")[1] == "Stuttgart":
			fromStuttg += 1
		else:
			fromBerlin += 1
	
	print("[ANALYZEFILE][RESULTS] {} Measurements".format(numH))
	print("[ANALYZEFILE][RESULTS] {} differnet flight-dates".format(len(flightsD.keys())))
	print("[ANALYZEFILE][RESULTS] {} different flight-dates from Stuttgart".format(fromStuttg))
	print("[ANALYZEFILE][RESULTS] {} different flight-dates from Berlin-Tegel".format(fromBerlin))

	
	
# function that search in given file flights 
# for a given date and returns the results
def getDayFromFile(fileName, date):

	res = []
	lastH = ""
	inserted = False

	with open('results/' + fileName, 'r') as file:
		for line in file:
		
			if line[0] == "H":
				lastH = line
				inserted = False
		
			if line.split(",")[0] == date:
				if not inserted:
					res.append(lastH)
					inserted = True
				res.append(line)
	
	if res == []:
		print("[GETDAYFROMFILE][ERR] No flights found in {}\n".format(fileName))
		return False
	
	return res


	
# function that analyzes all files in the result directory
# and searchs flights with headers at the given date
def getDay(date):

	res = []
	for filename in os.listdir('results/'):
		resf = getDayFromFile(filename, date)
		if resf:
			for element in resf:
				res.append(element)
	
	if res == []:
		print("[GETDAY][ERR] No flights found\n")
		return False
		
	return res


	
# function that creates plot files for given data
# with multiple flights for one date
# and also multiple measurements for one day
def plotDay(data, date):

	lastH = ""
	lastDepa = ""
	numStuttg = 0
	dateStuttg = []
	numBerlin = 0
	dateBerlin = []
	
	for flight in data:
		
		if flight[0] == "H":
			lastH = flight
		else:
		
			flightinfo = flight.split(",")
			
			if lastDepa == "":
				lastDepa = flightinfo[2]
				if flightinfo[2] == "Stuttgart":
					numStuttg += 1
					dateStuttg.append([lastH])
					
				else:
					numBerlin += 1
					dateBerlin.append([lastH])
			
			if lastDepa == flightinfo[2]:
				if flightinfo[2] == "Stuttgart":
					resFile = open(lastH.replace("\n","") + "_S" + str(numStuttg) + ".temp", 'a')
					resFile.write(flightinfo[1] + " " + flightinfo[3].replace(",",".").replace("\n","") + "\n")
					resFile.close()
					dateStuttg[numStuttg - 1].append(flightinfo[1])
				else:
					resFile = open(lastH.replace("\n","") + "_B" + str(numBerlin) + ".temp", 'a')
					resFile.write(flightinfo[1] + " " + flightinfo[3].replace(",",".").replace("\n","") + "\n")
					resFile.close()
					dateBerlin[numBerlin - 1].append(flightinfo[1])
			
			if lastDepa != flightinfo[2]:
				lastDepa = flightinfo[2]
				if flightinfo[2] == "Stuttgart":
					numStuttg += 1
					resFile = open(lastH.replace("\n","") + "_S" + str(numStuttg) + ".temp", 'a')
					resFile.write(flightinfo[1] + " " + flightinfo[3].replace(",",".").replace("\n","") + "\n")
					resFile.close()
					dateStuttg.append([lastH])
					dateStuttg[numStuttg - 1].append(flightinfo[1])
				else:
					numBerlin += 1
					resFile = open(lastH.replace("\n","") + "_B" + str(numBerlin) + ".temp", 'a')
					resFile.write(flightinfo[1] + " " + flightinfo[3].replace(",",".").replace("\n","") + "\n")
					resFile.close()
					dateBerlin.append([lastH])
					dateBerlin[numBerlin - 1].append(flightinfo[1])
	
	
	if numStuttg > 0:
		plotFile = open('plotS.temp', 'a')
		plotFile.write("set title \"Flights at {} from Stuttgart\"\n".format(date))
		plotFile.write("set xlabel \"Hours of the Day\"\n")
		plotFile.write("set timefmt \"%H:%M\"\n")
		plotFile.write("set xrange [ \"{}\":\"{}\" ]\n".format(dateStuttg[0][1], dateStuttg[0][-1]))
		plotFile.write("set ylabel \"Prices for the Flight\"\n")
		plotFile.write("set grid\n")
		plotFile.write("set key left top\n")
		plotFile.write("plot \"{}_S1.temp\" using 1:2 with lines\n".format(dateStuttg[0][0].replace("\n","")))
		
		for i in range(2, numStuttg + 1):
			plotFile.write("replot \"{}_S{}.temp\" using 1:2 with lines\n".format(dateStuttg[i - 1][0].replace("\n",""), i))
		
		plotFile.close()
		os.system("gnuplot -p plotS.temp")

	if numBerlin > 0:
		plotFile = open('plotB.temp', 'a')
		plotFile.write("set title \"Flights at {} from Berlin-Tegel\"\n".format(date))
		plotFile.write("set xlabel \"Hours of the Day\"\n")
		plotFile.write("set timefmt \"%H:%M\"\n")
		plotFile.write("set xrange [ \"{}\":\"{}\" ]\n".format(dateBerlin[0][1], dateBerlin[0][-1])) #TODO: biggest range in data 
		plotFile.write("set ylabel \"Prices for the Flight\"\n")
		plotFile.write("set grid\n")
		plotFile.write("set key left top\n")
		plotFile.write("plot \"{}_B1.temp\" using 1:2 with lines\n".format(dateBerlin[0][0].replace("\n","")))
		
		for i in range(2, numBerlin + 1):
			plotFile.write("replot \"{}_B{}.temp\" using 1:2 with lines\n".format(dateBerlin[i - 1][0].replace("\n",""), i))
		
		plotFile.close()
		os.system("gnuplot -p plotB.temp")
	
	
	os.system("del *.temp")


	
# function that search in a given file flights at a given hour
# and returns the flight data with corresponding headers
def getFlightFromFile(fileName, flightHour):
	
	res = []
	lastH = ""
	inserted = False

	with open('results/' + fileName, 'r') as file:
		for line in file:
		
			if line[0] == "H":
				lastH = line
				inserted = False
		
			if line.split(",")[1][0:2] == flightHour:
				if not inserted:
					res.append(lastH)
					inserted = True
				res.append(line)
	
	if res == []:
		print("[GETFLIGHTFROMFILE][ERR] No flights found in {}\n".format(fileName))
		return False
	
	return res
	


# function that analyzes all files in the result directory
# and searchs flights with headers at the given hour
def getFlight(flightHour):
	
	res = []
	for filename in os.listdir('results/'):
		resf = getFlightFromFile(filename, flightHour)
		if resf:
			for element in resf:
				res.append(element)
	
	if res == []:
		print("[GETFLIGHT][ERR] No flights found\n")
		return False
		
	return res

	
	
# function that creates plot files for given data
# with multiple flights for one hour
# and also multiple measurements for one day
def plotFlight(data, hour): 

	datesStuttg = []
	datesBerlin = []
	priceStuttg = dict()
	priceBerlin = dict()
	
	for flight in data:
	
		if flight[0] != 'H':
			
			flightinfo = flight.split(",")
			
			if  flightinfo[2] == "Stuttgart":
				if flightinfo[0] not in datesStuttg:
					datesStuttg.append(flightinfo[0])
				if flightinfo[0] in priceStuttg:
					priceStuttg[flightinfo[0]].append(flightinfo[3].replace("\n",""))
				else:
					priceStuttg[flightinfo[0]] = [flightinfo[3].replace("\n","")]
			
			else:
				if flightinfo[0] not in datesBerlin:
					datesBerlin.append(flightinfo[0])
				if flightinfo[0] in priceBerlin:
					priceBerlin[flightinfo[0]].append(flightinfo[3].replace("\n",""))
				else:
					priceBerlin[flightinfo[0]] = [flightinfo[3].replace("\n","")]
	
	datesStuttg.sort()
	firstDateStuttg = 0
	lastDateStuttg = 0
	if datesStuttg != []:
		firstDateStuttg = datesStuttg[0]
		lastDateStuttg = datesStuttg[-1]
	
	numStuttg = 1
	maxNumPricesStuttg = 0
	
	file = open("Flights_S" + str(numStuttg) + ".temp", "w")
	for date in sorted(datesStuttg): #unefficent
		file.write(date + " " + priceStuttg[date][numStuttg - 1] + "\n")
		if len(priceStuttg[date]) > maxNumPricesStuttg:
			maxNumPricesStuttg = len(priceStuttg[date])
		if len(priceStuttg[date]) == numStuttg:
			datesStuttg.remove(date)
	file.close()
	
	numStuttg += 1
	while numStuttg <= maxNumPricesStuttg:
		file = open("Flights_S" + str(numStuttg) + ".temp", "w")
		for date in sorted(datesStuttg): #unefficent
			file.write(date + " " + priceStuttg[date][numStuttg - 1] + "\n")
			if len(priceStuttg[date]) == numStuttg:
				datesStuttg.remove(date)
	
		file.close()
		numStuttg += 1
	
	datesBerlin.sort()
	firstDateBerlin = 0
	lastDateBerlin = 0
	if datesBerlin != []:
		firstDateBerlin = datesBerlin[0]
		lastDateBerlin = datesBerlin[-1]
	
	numBerlin = 1
	maxNumPricesBerlin = 0
		
	file = open("Flights_B" + str(numBerlin) + ".temp", "w")
	for date in sorted(datesBerlin): #unefficent
		file.write(date + " " + priceBerlin[date][numBerlin - 1] + "\n")
		if len(priceBerlin[date]) > maxNumPricesBerlin:
			maxNumPricesBerlin = len(priceBerlin[date])
		if len(priceBerlin[date]) == numBerlin:
			datesBerlin.remove(date)
	file.close()
	
	numBerlin += 1
	while numBerlin <= maxNumPricesBerlin:
		file = open("Flights_B" + str(numBerlin) + ".temp", "w")
		for date in sorted(datesBerlin): #unefficent
			file.write(date + " " + priceBerlin[date][numBerlin - 1] + "\n")
			if len(priceBerlin[date]) == numBerlin:
				datesBerlin.remove(date)
	
		file.close()
		numBerlin += 1
	
	if maxNumPricesStuttg > 0:
		plotFile = open('plotS.temp', 'w')
		plotFile.write("set title \"Flights at {} o' clock from Stuttgart\"\n".format(hour))
		plotFile.write("set xlabel \"Dates of the Year\"\n")
		plotFile.write("set timefmt \"%Y%m%d\"\n")
		plotFile.write("set xrange [ \"{}\":\"{}\" ]\n".format(firstDateStuttg, lastDateStuttg))
		plotFile.write("set ylabel \"Prices for the Flight\"\n")
		plotFile.write("set grid\n")
		plotFile.write("set nokey\n")
		plotFile.write("set format x \"%.0f\"\n")
		plotFile.write("plot \"Flights_S1.temp\" using 1:2 with lines\n")
		
		for i in range(2, maxNumPricesStuttg + 1):
			plotFile.write("replot \"Flights_S{}.temp\" using 1:2 with lines\n".format(i))
		
		plotFile.close()
		os.system("gnuplot -p plotS.temp")

	if maxNumPricesBerlin > 0:
		plotFile = open('plotB.temp', 'w')
		plotFile.write("set title \"Flights at {} o' clock from Berlin-Tegel\"\n".format(hour))
		plotFile.write("set xlabel \"Dates of the Year\"\n")
		plotFile.write("set timefmt \"%Y%m%d\"\n")
		plotFile.write("set xrange [ \"{}\":\"{}\" ]\n".format(firstDateBerlin, lastDateBerlin))
		plotFile.write("set ylabel \"Prices for the Flight\"\n")
		plotFile.write("set grid\n")
		plotFile.write("set nokey\n")
		plotFile.write("set format x \"%.0f\"\n")
		plotFile.write("plot \"Flights_B1.temp\" using 1:2 with lines\n")
		
		for i in range(2, maxNumPricesBerlin + 1):
			plotFile.write("replot \"Flights_B{}.temp\" using 1:2 with lines\n".format(i))
		
		plotFile.close()
		os.system("gnuplot -p plotB.temp")
	
	os.system("del *.temp")



# function that iterates throw a file and searches the cheapest flights
# these will be printed out with the corresponding query header
def getCheapestFromFile(fileName, verbose=False):
	
	res = []
	lastH = ""
	cheapest = 1000.00
	
	with open('results/' + fileName, 'r') as file:
		for line in file:
		
			if line[0] == "H":
				lastH = line
			
			else:
				if float(line.split(",")[3]) <= cheapest:
					res.append([lastH, line])
					cheapest = float(line.split(",")[3])

				for flight in res:
					if float(flight[1].split(",")[3]) > cheapest:
						res.remove(flight)
	
	if verbose:
		for flight in res:
			infos = flight[1].split(",")
			print("[getCheapest][{}] {}€ from {} at {} - {} o'clock ({})".format(fileName, infos[3].replace("\n",""), infos[2], infos[0], infos[1]
																				 , flight[0].replace("\n", "").replace("H,", "")))
	
	return res

	
# function that analyzes all files in the result directory
# using getCheapestFromFile function and returns array with all
# the cheapest flights and corresponding query headers
def getCheapest(verbose=False):
	
	res = []
	
	for filename in os.listdir('results/'):
		resf = getCheapestFromFile(filename, verbose)
		
		for flight in resf:
			res.append(flight)
	
	return res

	
	
# function that finds in a list of low price flights
# the latest measurements using the query header
# and returns this results in an array
def analyzeCheapest(flightList):

	flight2headers = dict()
	res = []
	
	for flight in flightList:
		
		if flight[1] not in flight2headers:
			flight2headers[flight[1]] = [flight[0]]
		else:
			flight2headers[flight[1]].append(flight[0])
	
	for flights, headers in flight2headers.items():
		dates = []
		for head in headers:
			copy = head
			copy.replace("\n", "").replace("H,", "")
			dates.append(datetime.strptime(copy.replace("\n", "").replace("H,", ""), '%d.%m.%y,%H.%M.%S'))

		res.append([max(dates), flights])
	
	for flight in res:
		print(flight)
	
	for flight in res:
		infos = flight[1].split(",")
		print("[AnalyzeCheapest] {}€ from {} at {} - {} o'clock ({})".format(infos[3].replace("\n",""), infos[2], infos[0], infos[1], flight[0]))
	
	return res

# -------------------------------------------------------------------------------------



def main():

	#autoQueryAndSave("13.03.19", "13.03.19", "01.05.19")

	'''
	day = "20190411"
	res = getDay(day)
	printFlightList(res)
	plotDay(res, day)
	'''
	
	#analyzeFile("28.02.19.ew")
	
	'''
	hour = "15"
	res = getFlight(hour)
	#printFlightList(res)
	if res:
		plotFlight(res,hour)
	'''
	
	
	cheapest = getCheapest()
	analyzeCheapest(cheapest)
	
	
main()
