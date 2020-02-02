# Source: https://github.com/Flexximo/engine_ti



from datetime import datetime, timedelta
import time
import socket



def formatter(start, end, pattern="%d/%m/%Y"):
    try: 
        return [start.strftime(pattern), end.strftime(pattern)]
    except AttributeError:
        print("Use date only to get formatted data")



def get_min_price(index, firstTicket, fromTo, toFrom, d, secondTicket=None, a=None):   
    response = None
    cacheDeparture = []
    cacheArrival = []
    dLowest = None
    aLowest = None
    if a and secondTicket:
        for ti in firstTicket:    
            if ti[1] == d:
                cacheDeparture.append(ti)
        if len(cacheDeparture) == 0:
            response = f"No tickets for departure on {d}, try another day, or use correct date"
            return response
        
        for tic in secondTicket:
            if tic[1] == a:
                cacheArrival.append(tic)
        if len(cacheArrival) == 0:
            response = f"No tickets for arrival on {a}, try another day, or use correct date"
            return response        
    
        dLowest = cacheDeparture[0]
        dLowest = dLowest[0]
        aLowest = cacheArrival[0]
        aLowest = aLowest[0]
    else:
    
        for ti in firstTicket:            
            if ti[1] == d:
                cacheDeparture.append(ti)
              
        if len(cacheDeparture) == 0:
            response = f"No tickets for departure on {d}, try another day, or use correct date"
            return response      
        dLowest = cacheDeparture[0]
        dLowest = dLowest[0]
    if secondTicket:
        response = []
        ticket_Departure = None
        ticket_Arrival = None
        
        for t0 in cacheDeparture:
            dLowest = dLowest if dLowest <= t0[0] else t0[0]
        for t0 in cacheDeparture:
            if t0[0] == dLowest:
                ticket_Departure = t0      
        for t1 in cacheArrival:
            aLowest = aLowest if aLowest <= t1[0] else t1[0]
        for t1 in cacheArrival:
            if t1[0] == aLowest:
                ticket_Arrival = t1
        response.append(ticket_Departure)
        response.append(ticket_Arrival)
        response.append((fromTo, toFrom, index))
        return response    
    else:
        response = []
        ticket_Departure = None
        for t3 in cacheDeparture:
            dLowest = dLowest if dLowest <= t3[0] else t3[0]
        for t3 in cacheDeparture:
            if t3[0] == dLowest:
                ticket_Departure = t3
            response.append(ticket_Departure)
            response.append((fromTo, index))
            return response



from requests.adapters import HTTPAdapter
from datetime import datetime, timedelta
from threading import Thread, current_thread
from methods import get_min_price, formatter
from structures import tickets, directions, cache 
import requests
import json
import queue
import sys
import time
import logging



tickets = tickets
directions = directions
cache = cache
api_adapter = HTTPAdapter(max_retries=3)
session = requests.Session()
#For option if possible to use queue objects to keep cached data instead of using cache file
#    data_queue = queue.Queue()
def main():
    res = None
    fromTo = input("Enter the city of departure. E.g. ALA TSE MOW etc. only acceptable").strip()
    toFrom = input("Enter the city of arrival. E.g. ALA TSE MOW etc. only acceptable").strip()
    a = int(input("Enter number of adults. Max of 2").strip())
    i = int(input("Enter number of infants. Max of 2").strip())
    c = int(input("Enter number of infants. Max of 2").strip())
    depart = input("Enter date of arrival. E.g. 01/01/2020 etc. only acceptable").strip()
    arrival = input("Enter of departure. Optional for two-way tickets. E.g. 02/01/2020 etc. only acceptable").strip()
    res = searchEngine(fromTo, toFrom, a, i, c, depart, arrival)
    
def retrieveCache():
    import ast
    with open("cache.json", "r") as file:
        data_cache = json.loads(file.read())
    jsoned = ast.literal_eval(data_cache)["data"]  
    return jsoned


def isValid(ticket, a, i, c):
    import math   
    url = None
    message = "Success"
    cache = None
    pnum = sum([a, i, c])
    bnum = sum([a, i, c])
    data = []
    tickets = ticket
    print(tickets)
    if len(ticket) == 3:
        route = ticket.pop(2)
    else: 
        route = ticket.pop(1)
    #Link to cache for instant access
    cache = retrieveCache()
    
    for t in tickets:

        url = f"https://booking-api.skypicker.com/api/v0.1/check_flights?v=2&booking_token={t[3]}&bnum={bnum}&pnum={pnum}&affily=picky&currency=USD&adults={a}&infants={i}&children={c}"
        session.mount(url, api_adapter)
        try:
            check = requests.get(url)
            check.raise_for_status()
            check.raw.decode_content = True
        else:
            data.append(check.json())           
    #if ticket invalid - erase from cache, if price update -> update price in db -> return new price
    try:
        if len(data) > 1:       
            if data[0]["flights_invalid"] is True:
                        message = f"Ticket {route[0]} for {tickets[0][1]} is invalid, we have updated our data for better result, search it again please." 
                        print(message)              
                        for ticket in cache[route[0]][0]["tickets"]:
                            if ticket[3] == data[0]["booking_token"]:
                                cache[route[0]][0]["tickets"].remove(ticket)

            elif data[1]["flights_invalid"] is True:
                        message = f"Ticket for {route[1]} for {tickets[1][1]} is invalid, we have updated our data for better result, search again please."
                        print(message)
                        for ticket in cache[route[1]][0]["tickets"]:
                            if ticket[3] == data[0]["booking_token"]:
                                cache[route[0]][0]["tickets"].remove(ticket)
                            
            elif data[0]["price_change"] is True:
                        message = f"Ticket price of {route[0]} for {tickets[0][1]} is invalid, we have updated our database for better result and provided you with new price."
                        print(message)
                        for ticket in cache[route[0]][0]["tickets"]:
                            if ticket[3] == data[0]["booking_token"]:
                                ticket[0] = data[0]["conversion"]["amount"]
                                tickets[0][0] = data[0]["conversion"]["amount"]  
            elif data[1]["price_change"] is True:
                        message = f"Ticket price of {route[1]} for {tickets[1][1]} is invalid, we have updated our database for better result and provided you with new price."
                        print(message)
                        for ticket in cache[route[1]][0]["tickets"]:
                            if ticket[3] == data[0]["booking_token"]:
                                ticket[0] = data[0]["conversion"]["amount"]
                                tickets[1][0] = data[0]["conversion"]["amount"]          
        else:
            if data[0]["flights_invalid"] is True:
                        message = f"Ticket {route[0]} for {tickets[0][1]} is invalid, we have updated our data for better result, search again please."
                        print(message)
                        for ticket in cache[route[0]][0]["tickets"]:
                            if ticket[3] == data[0]["booking_token"]:
                                cache[route[0]][0]["tickets"].remove(ticket)

            elif data[0]["price_change"] is True:
                        message = f"Ticket price of {route[0]} for {tickets[0][1]} is invalid, we have updated our database for better result and provided you with new price."
                        print(message)
                        for ticket in cache[route[0]][0]["tickets"]:
                            if ticket[3] == data[0]["booking_token"]:
                                ticket[0] = data[0]["conversion"]["amount"]
                                tickets[0][0] = data[0]["conversion"]["amount"]
                                
    #to handle exceptions for this try/catch to have a sense in its presence
    except InterruptedError:
        pass
    else:
        return tickets
    finally:
        modifiedCache = {}
        modifiedCache["data"] = cache
        with open("cache.json", "w+") as file:
            json.dump(str(modifiedCache), file)
            
#middleware function for gettting lowest price for 1-way/2-way flights           
def sendData(date_departure, is_one_way, index, fromTo, toFrom=None, date_arrival=None):
    jsoned = retrieveCache()
    if is_one_way:
        result = None
        jsonedD = jsoned[fromTo][index]["tickets"]
        result = get_min_price(index, jsonedD, fromTo, toFrom, date_departure)
        return result
    else:
        result = None
        jsonedD = jsoned[fromTo][index]["tickets"]
        jsonedA = jsoned[toFrom][index]["tickets"]
        result = get_min_price(index, jsonedD, fromTo, toFrom, date_departure, jsonedA, date_arrival)
        return result
    return jsoned

#Looking for the cheapest ticket for 1-way/2-way flights
def searchEngine(fromTo, toFrom, a, i, c, date_departure, date_arrival=None):
    message = None
    is_one_way = False 
    respond = None
    fromTo_ = (fromTo, toFrom)
    toFrom_ = (toFrom, fromTo)
    if a == 1 and i == 1 and c == 1:                          
        respond = sendData(date_departure, is_one_way, 0, fromTo_, toFrom_, date_arrival=date_arrival)    
    elif a == 2 and i == 0 and c == 1:
        respond = sendData(date_departure, is_one_way, 6, fromTo_, toFrom_, date_arrival=date_arrival)
    isValid_ = isValid(respond, a, i, c)
    message = f"Found for {fromTo_[0]}-{fromTo_[1]} and {toFrom_[0]}-{toFrom_[1]}. Price {isValid_[0][0]} USD and {isValid_[1][0]} USD accordingly"       
    print(message)


#To update cache on everydaybasis and on first run.
#a, c, i are for adults, children, infants @Captain Obviousness
#the function is for handling in thread 
def searchDaily(cache=cache, start=datetime.today(), delta=timedelta(days=31), directions=directions, tickets=tickets, curr="USD", a=None, i=None, c=None):
    end = start + delta or None
    formatted = formatter(start, end)
    for d in directions:        
        print(f"#### Searching from {d[0]} to {d[1]}... ###")        
        url = f"https://api.skypicker.com/flights?fly_from={d[0]}&fly_to={d[1]}&date_from={formatted[0]}&date_to={formatted[1]}&curr={curr}&children={c}&adults={a}&infants={i}&partner=picky"
        session.mount(url, api_adapter)        
        
        try :
            request = session.get(url)
            request.raise_for_status()
            request.raw.decode_content = True
            tickets[d] = request.json()["data"]
            
            with open("cache2.json", "w+") as f:
                json.dump(str(tickets), f)

            #if d == ("ALA", "TSE"):                  
            #    if a == 1 and c == 1 and i == 1:
            #       for n in tickets[d]:
            #            cache["data"][d][0]["tickets"].append([n["price"], time.strftime('%d/%m/%Y', time.localtime(n["dTime"])), time.strftime('%d/%m/%Y', time.localtime(n["aTime"])), n["booking_token"],])              

    #saving all the data in cache variable as queue        
    with open("raw.json", "w+") as file:
        json.dump(str(cache), file)
    return None   



def filteredData(cache=tickets, handler=searchDaily):
    processA = Thread(target=handler, kwargs={"a": 1, "i": 1, "c": 1}).start()
    processB = Thread(target=handler, kwargs={"a": 1, "i": 1, "c": 0}).start()
    processC = Thread(target=handler, kwargs={"a": 1, "i": 0, "c": 1}).start()     


if __name__ == "__main__":
    main()


delta = timedelta(hours=12)

if __name__ == "__main__":
    filteredData()
    time.sleep(60)
    while True:
        print("Server is running on", socket.gethostbyname(socket.gethostname()), time.ctime())
        time.sleep(2)   
        if datetime.now().hour == timedelta and datetime.now().minute == 0:
            filteredData()
            time.sleep(60)