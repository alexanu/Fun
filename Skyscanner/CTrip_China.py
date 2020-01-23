# Source: https://github.com/AricsHuang/Flight-Search

import FlightClass
import method_getRouteList
import pickle
import method_getSix
import checkEachDcit
import method_print
import method_Mail
import method_Change_flightMSGdat
from time import sleep
import method_input

if __name__ == '__main__':
    Method_Input = method_input.Input()
    sleep_time = Method_Input.inputSleepTime()
    BcityName = Method_Input.inputCityName()
    AcityName = Method_Input.inputCityName()
    time = Method_Input.inputTime()
    aroundTime = 0
    while (1):
        aroundTime += 1
        Method = method_getRouteList.Method()
        FlightDict = {}

        dict_str = Method.getJSON(time, BcityName,
                                  AcityName)  # dict_str 为api返回json数据(dict)
        routeList = Method.get_routeList(dict_str)  # Flight list

        for routeList_dict in routeList:  # for each_flight in routeList
            if routeList_dict.setdefault("routeType") == "Flight":
                legs_dict = Method.get_legs_dict(routeList_dict)  # 本航班总信息
                # flight = Method.get_flight(legs_dict)

                method_Six = method_getSix.getSix()
                flightMSG = {}
                departureAirportInfoMSG = {}
                arrivalAirportInfoMSG = {}
                timeMSG = {}
                priceMSG = []
                method_Six.getSix(legs_dict, flightMSG,
                                  departureAirportInfoMSG,
                                  arrivalAirportInfoMSG, timeMSG, priceMSG)

                Flight = FlightClass.Flight()
                Flight.inputMSG(flightMSG, departureAirportInfoMSG,
                                arrivalAirportInfoMSG, timeMSG, priceMSG)

                FlightDict[Flight.FlightNumber] = Flight
            elif routeList_dict.setdefault("routeType") == "FlightTrain":
                pass

        # print(FlightDict)
        file = open("flightMSG_temp.dat", "wb")
        # file1 = open("flightMSG.dat", "wb")
        pickle.dump(FlightDict, file)
        # pickle.dump(FlightDict, file1)
        file.close()
        # file1.close()

        Add = []
        Delete = []
        Change = []
        Method_checkEachDict = checkEachDcit.check()
        Method_Mail = method_Mail.Mail()
        Method_Change = method_Change_flightMSGdat.changeFile()
        judgeList = Method_checkEachDict.check(Add, Delete, Change)

        Method_printMSG = method_print.printMSG()
        Method_printMSG.printStatusCode(judgeList)
        Method_printMSG.printAroundTime(aroundTime)

        Method_printMSG.printAddMSG(Add, FlightDict)
        Method_printMSG.printDeleteMSG(Delete)
        Method_printMSG.printChangeMSG(Change, FlightDict)
        # Method_printMSG.printFlightMSG(FlightDict)

        file_Mail = open("Mail.txt", "w")
        file_Mail.close()
        Method_Mail.writeMail(Add, Delete, Change, FlightDict)
        Method_Mail.SendMail(judgeList)

        Method_Change.changeFile()
        print("Sleep for " + str(sleep_time) + " second.")
        sleep(int(sleep_time))
