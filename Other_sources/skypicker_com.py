# Source: https://github.com/adjanybekov/Flight-Optimizer/blob/master/django/myproject/main.py


import requests
import json
from haversine import haversine, Unit
import sys
import datetime

# Replace with the correct URL



def getCityData(cityName):
    locUrl = "https://api.skypicker.com/locations?term=%s&locale=en-US&location_types=airport&limit=1&active_only=true&sort=name"
    cityUrl = locUrl%cityName
    cityResp = requests.get(cityUrl,verify=True)
    return  json.loads(cityResp.content) if cityResp.ok else None

def getDistance(srcData,destData):    
    srcLoc = (srcData["locations"][0]["location"]["lat"],srcData["locations"][0]["location"]["lon"])
    destLoc = (destData["locations"][0]["location"]["lat"],destData["locations"][0]["location"]["lon"])

    # print(haversine(srcLoc,destLoc),"km")
    return haversine(srcLoc,destLoc)


def getCheapestFlight(srcData,destData):    
    srcCode = srcData["locations"][0]["code"]
    destCode = destData["locations"][0]["code"]
    
    today = datetime.date.today()    
    # dd/mm/YY
    d1 = today.strftime("%d/%m/%Y")    

    tomorrow = datetime.date.today() + datetime.timedelta(days=1)
    d2= tomorrow.strftime("%d/%m/%Y")    

    searchUrl = "https://api.skypicker.com/aggregation_flights?fly_from=%s&fly_to=%s&v=3&date_from=%s&date_to=%s&flight_type=oneway&one_for_city=0&one_per_date=1&adults=1&partner=picky&curr=USD&limit=3&sort=price"%(srcCode,destCode,d1,d2)
    searchResp = requests.get(searchUrl,verify=True)
    searchData = json.loads(searchResp.content)
    # print(searchData["data"][0]["price"],"USD")
    return searchData["data"][0]["price"] if len(searchData["data"])>0 else None


src = "Bishkek"
dest = "Istanbul"
destList = []
if len(sys.argv)>=3:
    src = sys.argv[1]
    for i in range(2,len(sys.argv)):
        dest = sys.argv[i]
        destList.append(dest)
    
else:
    destList.append(dest)


resultDic = {}
distDic = {}
flag = False
for dest in destList:
    srcData = getCityData(src)
    destData = getCityData(dest)   
    #if city data is not found or server error occured
    if( (srcData is None or destData is None ) or len(srcData["locations"])<1 or len(destData["locations"])<1):        
        continue    
    distance = getDistance(srcData,destData)
    price = getCheapestFlight(srcData,destData)
    if(price is None):        
        continue
    else:
        flag = True

    # print("distance from %s to %s is %d km"%(src,dest,distance))
    # print("price from %s to %s is %d USD"%(src,dest,price))
    # print("price/distance from %s to %s is %.3f USD/km"%(src,dest,price/distance))
    resultDic[dest] = price/distance
    distDic[dest] = distance

cheapestFlight = sys.maxsize
cheapestDest = ""
# print(resultDic)
for key in resultDic:
    if resultDic[key]<cheapestFlight:
        cheapestFlight = resultDic[key]
        cheapestDest = key

if(not flag):
    print("No flights found in this directions")
else:
    print("The cheapest destination is %s with price/distance =  %.3f USD/km"%(cheapestDest,cheapestFlight))
    print("Distance travelled from %s to %s is %d km"%(src,cheapestDest,distDic[cheapestDest]))#km
    print("Price from %s to %s is %d USD"%(src,cheapestDest,cheapestFlight*distDic[cheapestDest]))#usd