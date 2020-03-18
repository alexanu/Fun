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
        csv_open_file = self.openCsvFile('Destination List.csv')
        destination_list_name = [destination.strip('\n') for destination in csv_open_file]
        data_list = [self.openCsvFile(f'{destination_list_name[trip]}.csv') for trip in range(len(csv_open_file) - 1)]
        return data_list[0]

    def splitToIndex(self):
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





###################################################################################################################


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


starting = ['tlv']
destination = ['mil']
original_date = [200501]
long_stay = [5]
direct = 'false'
flexible_date = 'no'  # ('yes' or 'no')
looping = 3
searching = 20

url = FormatDate(original_date, long_stay, starting, destination,
                 direct, searching, flexible_date, looping).mainFunction()



def mainFunction(self):
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




# **********************************************************************************************************************



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