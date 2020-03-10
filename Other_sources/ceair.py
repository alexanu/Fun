# Source: https://github.com/ZZYSonny/FlightTracker

import requests
import json
import datetime



def myfloat(x):
    return 3600 if x==None else float(x)

def newline(x):
    s=''
    for i in range(0,x): s+=' '
    return s

class flight():
    def __init__(self, id:str, deptPort:str, arrPort:str, deptTime:str, arrTime:str):
        self.id=id
        self.port=[deptPort, arrPort]
        self.time=[deptTime, arrTime]

    def __str__(self,indent=0):
        s_newline=newline(indent)
        return s_newline+'Flight No: '+self.id\
                +'\n'+s_newline+'Airport: '+self.port[0]+' '+self.port[1]\
                +'\n'+s_newline+self.time[0]\
                +'\n'+s_newline+self.time[1]+'\n'

class price():
    def __init__(self,totalCost:float,totalCostStr:str,cabinCode:str):
        self.totalCost=totalCost
        self.totalCostStr=totalCostStr
        self.cabinCode=cabinCode

    def __str__(self,indent=0):
        s_newline=newline(indent)
        return s_newline+'Cost: '+str(self.totalCost)+'='+self.totalCostStr\
                +'\n'+s_newline+'CabinCode: '+self.cabinCode

class group():
    def __init__(self, trip:[[flight]], price:price):
        self.trip=trip
        self.price=price
    
    def __str__(self,indent=0):
        s_newline=newline(indent)

        s_trip=['','']
        for i in range(0,2):
            for x in self.trip[i]:
                if(s_trip[i]!=''): s_trip[i]+=s_newline+'-------------------\n'
                s_trip[i]+=flight.__str__(x,indent=indent+4)

        return 'Trip0:\n'+s_trip[0]\
                +'Trip1:\n'+s_trip[1]\
                +'Price:\n'+price.__str__(self.price,indent=indent+4)+'\n'



class ceair():
    raw = {}
    searchDetail = {
        "adtCount": 1,
        "chdCount": 0,
        "infCount": 0,
        "currency": "CNY",
        "tripType": "RT",
        "recommend": False,
        "reselect": "",
        "page": "0",
        "sortType": "a",
        "sortExec": "a",
        "segmentList": [
            {
                "deptCd": "SHA",
                "arrCd": "LHR",
                "deptDt": "2019-10-07",
                "deptCityCode": "SHA",
                "arrCityCode": "LON"
            },
            {
                "deptCd": "LHR",
                "arrCd": "SHA",
                "deptDt": "2019-12-09",
                "deptCityCode": "LON",
                "arrCityCode": "SHA"
            }
        ],
        "version": "A.1.0"
    }

    def init(Date1: str, Date2: str, fromfile=False):
        '''Give raw flight json fetched from ceair.com||| please leave leading zeros'''

        # Get from Internet
        if(fromfile):
            s = open("./json/samplecompress.json",
                     encoding='gb18030', errors='ignore').readline()
            ceair.raw = json.loads(s)
        else:
            print('[INFO] Downloading '+Date1+" <-> "+Date2)
            ceair.searchDetail['segmentList'][0]['deptDt'] = Date1
            ceair.searchDetail['segmentList'][1]['deptDt'] = Date2
            r = requests.get(('http://www.ceair.com/otabooking/flight-search!doFlightSearch.shtml?searchCond='+json.dumps(ceair.searchDetail)).replace(' ', ''))            
            ceair.raw = r.json()
            print(r.text.encode('utf-8'), file=open('./json/cur.json', 'w'))
            print('[INFO] Downloading finished')

        ceair.findCost.init()
        return

    class findCost():
        '''cost module'''

        bestChoice = {}

        def init():
            for x in ceair.raw['searchProduct']:
                s = x['productGroupIndex']
                nowcost = myfloat(x['salePrice'])+myfloat(x['referenceTax'])
                if(not s in ceair.findCost.bestChoice):
                    ceair.findCost.bestChoice[s] = x
                else:
                    bestcost = myfloat(ceair.findCost.bestChoice[s]['salePrice'])+myfloat(
                        ceair.findCost.bestChoice[s]['referenceTax'])
                    if(nowcost < bestcost):
                        ceair.findCost.bestChoice[s] = x
            return

        def search(s: str):
            bestx = ceair.findCost.bestChoice[s]
            mincost = myfloat(bestx['salePrice']) + \
                myfloat(bestx['referenceTax'])
            return price(
                totalCost=mincost,
                totalCostStr=str(bestx['salePrice']) +
                '+'+str(bestx['referenceTax']),
                cabinCode=bestx['cabin']['cabinCode']
            )

        def linearsearch(s: str):
            bestx = {}
            mincost = 1e10
            for x in ceair.raw['searchProduct']:
                if(x['productGroupIndex'] == s):
                    nowcost = myfloat(x['salePrice']) + \
                        myfloat(x['referenceTax'])
                    if(nowcost < mincost):
                        bestx = x
                        mincost = nowcost
            return price(
                totalCost=mincost,
                totalCostStr=str(bestx['salePrice']) +
                '+'+str(myfloat(bestx['referenceTax'])),
                cabinCode=bestx['cabin']['cabinCode']
            )

    class obj():
        def flight(id: int):
            flightdetail = ceair.raw['flightInfo'][id]
            return flight(
                id=flightdetail['flightNo'],
                deptPort=flightdetail['departAirport']['code'],
                arrPort=flightdetail['arrivalAirport']['code'],
                deptTime=flightdetail['departDateTime'] +
                ' UTC+'+str(flightdetail['arrivalZone']),
                arrTime=flightdetail['arrivalDateTime'] +
                ' UTC+'+str(flightdetail['departZone'])
            )

        def group(id=-1, s=''):
            if id != -1:
                s = ceair.raw['flightGroup'][id]

            trip = [[], []]
            for i in range(0, 2):
                s_trip = s.split('/')[i]
                for x in s_trip.split('-'):
                    trip[i].append(ceair.obj.flight(int(x)))

            return group(
                trip=trip,
                price=ceair.findCost.search(s)
            )

        def allGroup(directOnly=True):
            res = []
            for s in ceair.raw['flightGroup']:
                if(directOnly and s.find('-') != -1):
                    continue
                x = ceair.obj.group(s=s)
                res.append(x)
            return res

    class output():
        def flight(id: int):
            print(ceair.obj.flight(id))

        def group(id=-1, s=''):
            print(ceair.obj.group(id, s))

        def allGroup(directOnly=True):
            t = ceair.obj.allGroup(directOnly)
            for x in t:
                print(x)
                print('-------------------------')

    class analyze():
        def lowest(s: str):
            accept = ['/', 'Z']
            for ch in s:
                if (not ch in accept):
                    return False
            return True

        def evaluate(expectedPrice: int, directOnly=True):
            minPrice = 1e10
            for x in ceair.obj.allGroup():
                if(x.price.totalCost < minPrice):
                    minPrice = x.price.totalCost
                    bestx = x
            return {
                'goodPrice': minPrice < expectedPrice,
                'lowest': ceair.analyze.lowest(bestx.price.cabinCode),
                'info': bestx
            }
        
        def scan(Date1,Date2,goodPrice,interval=1):
            d1=datetime.datetime.strptime(Date1, '%Y-%m-%d')
            d2=datetime.datetime.strptime(Date2, '%Y-%m-%d')
            while True:
                ceair.init(d1.date().strftime("%Y-%m-%d"),d2.date().strftime("%Y-%m-%d"),fromfile=False)
                x=ceair.analyze.evaluate(goodPrice)

                print("[Analyze] GoodPrice:",x['goodPrice'],"|Lowest:",x['lowest'])
                if(x['goodPrice'] and x['lowest']):
                    print("[Analyze] Printing solution")
                    print(x['info'])
                    break
                else:
                    d1=d1+datetime.timedelta(days=interval)
                    d2=d2+datetime.timedelta(days=interval)

        def bestInterval(Dates1:[str],Dates2:[str],directOnly=True):
            minPrice = 1e10
            for d1 in Dates1:
                for d2 in Dates2:
                    ceair.init(d1,d2)           
                    for x in ceair.obj.allGroup(directOnly=directOnly):
                        if(x.price.totalCost < minPrice):
                            minPrice = x.price.totalCost
                            bestx = x 
            return bestx




ceair.analyze.bestInterval(['2019-10-06','2019-10-07'],['2019-12-08','2019-12-09'])