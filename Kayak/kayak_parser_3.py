# Source: https://github.com/omerkuper/Kayak

import os.path
import time
from time import sleep
from datetime import date, datetime, timedelta
from bs4 import BeautifulSoup as bs
from PyQt5.QtWebEngineWidgets import QWebEnginePage
from PyQt5 import QtCore, QtWidgets
import csv
import sys
from multiprocessing import Process

stops_dict = {
    "0": ('nonstop '),
    "1": ('1 stop '),
    "2": ('2 stops '),
    "3": ('nonstop ', '1 stop '),
    "4": ('1 stop ', '2 stops '),
    "5": ('nonstop ', '1 stop ', '2 stops '),
}

class openCsvAndRun:
    def __init__(self):
        self.date_set = set()

    def openCsvFile(self, file_csv):
        """
        :param file_csv: csv file name in the folder
        :return: split lists
        """
        directory = os.path.dirname(__file__)
        filename = os.path.join(directory, file_csv)
        testFile = open(filename).read()
        testFile.strip('\n')
        if file_csv == 'Destination List.csv':
            return testFile.split(',')
        else:
            split_by_n = testFile.split('\n')
            lst = [data_split.split('|') for data_split in split_by_n]
            return lst[:-1]

    def listsOfTrips(self):
        '''
        :return: creating list of data for each destiny [ date | price | destination | airline | direct ]
        '''
        csv_open_file = self.openCsvFile('Destination List.csv')
        destination_list_name = [destination.strip('\n') for destination in csv_open_file]
        data_list = [self.openCsvFile(f'{destination_list_name[trip]}.csv') for trip in range(len(csv_open_file) - 1)]
        return data_list[0]

    def splitToIndex(self):
        '''
        :return: list split by ", '"
        '''
        outside_list = []
        for outer_list in self.listsOfTrips():
            cleanDate = self.dateAndPlace(outer_list[0])
            middle_list = []
            for mid_list in outer_list[1:-1]:
                after_split = mid_list.split(',')
                clean_price = self.priceCleaner(after_split[0])
                clean_flight_details = self.flightDetials(after_split[1: 4])
                clean_stops = self.stopsClean(after_split[3: ])
                url = [cleanDate, outer_list[-1]]
                middle_list.append([clean_price, clean_flight_details, clean_stops, url])
            outside_list.append(middle_list)
        return outside_list

    def stopsClean(self, stops):
        stopA = stops[0].strip(" [''")
        stopB = stops[1].strip(" ']]")
        stops_list = []
        if stopA.startswith('nonstop') or stopA[2:6] == 'stop':
            if stopA[2: 6] == 'stop':
                stops_list.append(stopA[: 7])
            else:
                stops_list.append(stopA)
        if stopB.startswith('nonstop') or stopB[2:6] == 'stop':
            if stopB[2: 6] == 'stop':
                stops_list.append(stopB[: 7])
            else:
                stops_list.append(stopB)
        if len(stops_list) != 0:
            return stops_list
        else:
            return 'unknown', 'unknown'


    def flightDetials(self, flight_d):
        flight_A = flight_d[0].strip(" (''").replace('+1', '').replace('+2', '').split()
        flight_B = flight_d[1].strip(" ()''").replace('+1', '').replace('+2', '').split()
        flight_C = flight_d[2]
        flight_D = ''
        if flight_C[1] != '[':
            flight_D = flight_C.strip(" ()''").replace('+1', '').split()
        if flight_D == '':
            return flight_A, flight_B
        else:
            return flight_A, flight_B, flight_D


    def priceCleaner(self, price):
        try:
            return int(price.strip("[]''$"))
        except:
            pass


    def dateAndPlace(self, data):
        spliter = data.strip("[]").replace("'", '').split(',')
        return spliter[0], spliter[1][2:]

    def sortMainListByPrice(self):
        elmentList_a = self.splitToIndex()
        counter = 0
        sort_lst = []
        for elmentList in elmentList_a[1::2]:
            try:
                sortList = sorted(elmentList, key=lambda price: price[:])
                sort_lst.append(elmentList_a[counter])
                sort_lst.append(sortList)
                counter += 2
            except:
                pass

        return sort_lst

    def mostCeapestList(self):
        elmentList = self.sortMainListByPrice()
        sortList_a = sorted(elmentList, key=lambda price: price[:][0])
        return sortList_a

    def dateFrmat(self, dates):
        cln_date = dates.replace(' ', '').split('—')
        date_list = []
        for date_clean in cln_date:
            dates_a = time.strptime(date_clean, '%m/%d')
            dates_b = date(dates_a.tm_year, dates_a.tm_mon, dates_a.tm_mday)
            date_list.append(dates_b.strftime('%A, %d %B'))
        return date_list

    def printResults(self, results, stop=5, loops=3):
        counter = 0
        for pr_results in results():
            if len(pr_results[0][2]) != 2:
                stops = [pr_results[0][2][0], pr_results[0][2][0]]
            else:
                stops = pr_results[0][2]
            dates = self.dateFrmat(pr_results[1][3][0][1])
            if stops[0] in stops_dict[str(stop)] and stops[1] in stops_dict[str(stop)] and counter < loops:
                print(f"\nFlight: {pr_results[1][3][0][0]}\n"
                      f"Departure Flight : {dates[0]} --> {pr_results[0][1][0][0]} - {pr_results[0][1][0][1]} -->"
                      f"By : {' '.join(pr_results[0][1][0][2:])} --> {stops[0]} \n"
                      f"Return Flight : {dates[1]} --> {pr_results[0][1][1][0]} - {pr_results[0][1][1][1]} -->"
                      f"By : {' '.join(pr_results[0][1][1][2:])} --> {stops[1]}\n"
                      f"Price : ${pr_results[0][0]}\n"
                      f"{pr_results[1][3][1]}"
                      f"\n")
                counter += 1


###################################################################################################################

# stops_dict = {
#     "0": 'nonstop ',
#     "1": '1 stop ',
#     "2": '2 stops ',
#     "3": ('nonstop ', '1 stop '),
#     "4": ('1 stop', '2 stops'),
#     "5": ('nonstop ', '1 stop ', '2 stops '),
# }

run = openCsvAndRun()
run.printResults(run.mostCeapestList, stop=5, loops=5)



class FormatDate:
    def __init__(self, original_date, long_stay, starting, destination, direct, loops, flexible, loops_to_run):
        if len(destination) == 0:
            self.destination = ['']
        else:
            self.destination = destination
        self.original_date = original_date
        self.time_to_stay = long_stay
        self.starting_point = starting
        self.direct = direct
        self.fix = flexible
        self.go_loop = loops_to_run
        if len(self.destination) >= len(self.starting_point):
            self.loops = loops - loops % len(self.destination)
        else:
            self.loops = loops - loops % len(self.starting_point)

    def mainFunction(self):
        '''
        :return: list of urls address [url1, url2 ...].
                 results of that function passing to Web_Loader class.
        '''

        urls_address = []
        self.counter = 0
        self.runLoop = 0
        self.loopTrip = self.countIndex(self.loops)
        for jump in range(self.loops):
            if jump % self.loopTrip[0] == 0 and jump != 0:
                self.runLoop = 0
                self.counter += 1

            elif self.loopTrip[1] == 0:
                self.runLoop = 0

            elif jump % self.loopTrip[1] == 0 and jump != 0 and self.fix == 'yes':
                self.runLoop += 1
            self.jump = jump
            urls_address.append(self.urlAddres())
        return urls_address

    def countIndex(self, totLoop):  #####
        if len(self.destination) < len(self.starting_point):
            alooPerDest = totLoop // len(self.starting_point)
            perLoop = self.alocaetionPerLoop(alooPerDest)
            return alooPerDest, perLoop
        else:
            alooPerDest = totLoop // len(self.destination)
            perLoop = self.alocaetionPerLoop(alooPerDest)
            return alooPerDest, perLoop

    def alocaetionPerLoop(self, alooPerDest):
        if self.go_loop == 0:
            return 0
        else:
            return alooPerDest // self.go_loop

    def dateAddDayDeparture(self, index):
        '''
        :return: changing the original departure date by one day in each loop [190301, 190302 ....]
        '''
        departure_date = time.strptime(str(self.original_date[index]), '%y%m%d')
        date_out = date(departure_date.tm_year, departure_date.tm_mon, departure_date.tm_mday) + \
                   timedelta(self.findRightDates())
        departure = (date_out.strftime('%Y-%m-%d'))
        return departure

    def findRightDates(self):

        func = {
            "a": self.jump - (self.loopTrip[0] * self.counter),
            "b": self.loopTrip[1],
        }

        if self.fix == 'no':
            return func["a"]

        elif self.fix == 'yes':
            return func["a"] % func["b"]

    def addDaysDeparture(self):
        '''
        :return: the results of dateAddDayDeparture function based on the sending condition.
        '''

        if len(self.original_date) == 1:
            return self.dateAddDayDeparture(0)
        else:
            return self.dateAddDayDeparture(self.counter)

    def dateAddDayArrivel(self, index):
        '''
        :return: adding days from departure date (dateAddDayDeparture) to return date based on self.time_to_stay.
        '''

        if self.fix == 'yes':
            self.runLoop = self.runLoop
        else:
            self.runLoop = 0
        if self.time_to_stay[index] != 0:
            departure = self.addDaysDeparture()
            date_return = time.strptime(departure, '%Y-%m-%d')
            date_return_i = date(date_return.tm_year, date_return.tm_mon,
                                 date_return.tm_mday) + timedelta(self.time_to_stay[index] + self.runLoop)
            arrivel = (date_return_i.strftime('%Y-%m-%d'))
            return arrivel
        else:
            return 0

    def addDaysArrivel(self):  ######
        '''
        :return: the results of dateAddDayArrivel function based on the sending condition.
        '''

        if len(self.time_to_stay) == 1 or \
                len(self.starting_point) >= 1 and len(self.destination) == 1 and len(self.time_to_stay) == 1:
            return self.dateAddDayArrivel(0)

        elif len(self.time_to_stay) > 1:
            return self.dateAddDayArrivel(self.counter)

    def startPoint(self):
        '''
        :return: the place of departure .
        '''

        if len(self.starting_point) == 1:
            return self.starting_point[0]
        else:
            return self.starting_point[self.counter]

    def urlAddres(self):
        '''
        :return: url address
        '''
        departure_date = self.addDaysDeparture()
        arriving_date = self.addDaysArrivel()
        start_point = self.startPoint()

        if len(self.destination) >= len(self.starting_point):
            self.url = f'https://www.kayak.com/flights/{start_point.upper()}-' \
                f'{self.destination[self.counter].upper()}/{departure_date}/{arriving_date}'

        elif len(self.destination) < len(self.starting_point):
            self.url = f'https://www.kayak.com/flights/{start_point.upper()}-' \
                f'{self.destination[0].upper()}/{departure_date}/{arriving_date}'

        # print(self.url)
        return self.url


class WebPage(QWebEnginePage):
    def __init__(self, num):
        super(QWebEnginePage, self).__init__()
        self.loadFinished.connect(self.handleLoadFinished)
        self.num = num
        self.location = set()

    def start(self, urls):
        self._urls = iter(urls)
        self.fetchNext()

    def fetchNext(self):
        try:
            url = next(self._urls)
            self.web_address = url
        except StopIteration:
            return False
        else:
            print(url)
            self.load(QtCore.QUrl(url))
        return True

    def processCurrentPage(self, html_str):
        self.html = html_str
        self.soup = bs(self.html, 'html.parser')
        blocks = self.soup.find_all('div', class_='inner-grid keel-grid')
        if len(blocks) != 0:
            all_results = []
            place_n_date = self.soup.title.text.split(',')
            all_results.append(place_n_date)
            for tag in blocks:
                results = []

                price = [cost.text for cost in tag.find_all('span', class_='price-text')[:1]]
                results.append(price)

                data = [details.text.replace('\n', '').replace('am', '').replace('pm', '')
                     for details in tag.find_all('div', class_='section times')]
                results.append((data[0].replace('–', ''), data[1].replace('–', '')))

                stops = [stop_q.text.replace('\n', '').replace('PFO ', '')
                         for stop_q in tag.find_all('div', class_='section stops')]
                results.append(stops)
                all_results.append(results)
            all_results.append(self.web_address)
            print('Well Done :-)')
            if self.num == 1:
                self.saveDataToCsv(all_results)
            else:
                self.saveDataToCsv(all_results)
                self.saveDestinationInFile(all_results[0][0])
        if not self.fetchNext():
            QtWidgets.qApp.quit()


    def handleLoadFinished(self):
        sleep(13)  # 17
        self.html = self.toHtml(self.processCurrentPage)


    def saveDataToCsv(self, data_list):
        directory = os.path.dirname(__file__)
        myFile = open(os.path.join(directory, f'{data_list[0][0]}.csv'), 'a', newline='')
        with myFile:
            writer = csv.writer(myFile, delimiter='|', quotechar='"', quoting=csv.QUOTE_MINIMAL)
            writer.writerows([data_list])
        myFile.close()

    def saveDestinationInFile(self, destinationList):
        directory = os.path.dirname(__file__)
        myFile = open(os.path.join(directory, 'Destination List.csv'), 'a', newline='')
        if destinationList in self.location:
            pass
        else:
            writer = csv.writer(myFile, delimiter=',', quotechar='"', quoting=csv.QUOTE_MINIMAL)
            writer.writerow(''.join(f'{destinationList},').split(','))
            self.location.add(destinationList)
            myFile.close()



# **********************************************************************************************************************

starting = ['tlv']
destination = ['mil']

# **********************************************************************************************************************

original_date = [200501]
long_stay = [5]

# **********************************************************************************************************************

direct = 'false'

# **********************************************************************************************************************

flexible_date = 'no'  # ('yes' or 'no')
looping = 3

# **********************************************************************************************************************

searching = 20

# **********************************************************************************************************************

# **** START YOUR APPLICETION ****#

# **********************************************************************************************************************

url = FormatDate(original_date, long_stay, starting, destination,
                 direct, searching, flexible_date, looping).mainFunction()


####################################################################################

def func1():
    # sleep(3)
    app = QtWidgets.QApplication(sys.argv)
    webPage = WebPage(0)
    print('PART 1')
    webPage.start(url[:: 3])
    sys.exit(app.exec_())


def func2():
    sleep(5)  # 5
    app1 = QtWidgets.QApplication(sys.argv)
    webPage1 = WebPage(1)
    print('PART 2')
    webPage1.start(url[1:: 3])
    sys.exit(app1.exec_())


def func3():
    sleep(10)
    app2 = QtWidgets.QApplication(sys.argv)
    webPage2 = WebPage(1)
    print('PART 3')
    webPage2.start(url[2:: 3])
    sys.exit(app2.exec_())



if __name__ == '__main__':
    p1 = Process(name='p1', target=func1)
    p2 = Process(name='p2', target=func2)
    p3 = Process(name='p3', target=func3)
    p1.start()
    p2.start()
    p3.start()