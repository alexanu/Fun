# Source: https://github.com/AricsHuang/Flight-Search
# Continue from https://github.com/alexanu/Flight-Search/blob/master/method_getSix.py

from time import sleep
import pickle
from email.mime.text import MIMEText
import smtplib
import requests
import json


import method_getSix
import checkEachDcit
import method_Change_flightMSGdat


# --------------------------------------------------------------------------------------------

class Flight():
    FlightNumber = None
    AirlineName = None
    CraftTypeName = None
    Bcity = None
    Bairport = None
    BTN = None  # Begin-Terminal-name
    BTSN = None  # Begin-Terminal-short-name
    Acity = None
    Aairport = None
    ATN = None  # Arrive-Terminal-name
    ATSN = None  # Arrive-Terminal-short-name
    BTime = None
    ATime = None
    stopTime = None
    stopInfo = None
    Price = None

    def inputMSG(__name__, flightMSG, departureAirportInfoMSG, arrivalAirportInfoMSG, timeMSG, priceMSG):
        __name__.FlightNumber = flightMSG.setdefault("航班编号")
        __name__.AirlineName = flightMSG.setdefault("航空公司")
        __name__.CraftTypeName = flightMSG.setdefault("飞机型号")

        __name__.Bcity = departureAirportInfoMSG.setdefault("起飞城市")
        __name__.Bairport = departureAirportInfoMSG.setdefault("起飞机场")
        __name__.BTN = departureAirportInfoMSG.setdefault("Begin Terminal name")
        __name__.BTSN = departureAirportInfoMSG.setdefault("Begin Terminal short-name")

        __name__.Acity = arrivalAirportInfoMSG.setdefault("到达城市")
        __name__.Aairport = arrivalAirportInfoMSG.setdefault("到达机场")
        __name__.ATN = arrivalAirportInfoMSG.setdefault("Arrive Terminal name")
        __name__.ATSN = arrivalAirportInfoMSG.setdefault("Arrive Terminal short-name")

        __name__.BTime = timeMSG.setdefault("起飞时间")
        __name__.ATime = timeMSG.setdefault("到达时间")
        __name__.stopTime = timeMSG.setdefault("stopTime")
        __name__.stopInfo = timeMSG.setdefault("stopInfo")

        __name__.Price = priceMSG  # 字典组成的列表


    def writeSendMail(__name__):
        file_SendMail = open("Mail.txt", "a")
        file_SendMail.write("|               Flight Message                 |\n")

        file_SendMail.write("航班编号：" + str(__name__.FlightNumber) + "\n")
        file_SendMail.write("航空公司：" + str(__name__.AirlineName) + "\n")
        file_SendMail.write("飞机型号：" + str(__name__.CraftTypeName) + "\n")

        file_SendMail.write("起飞城市：" + str(__name__.Bcity) + "\n")
        file_SendMail.write("起飞机场：" + str(__name__.Bairport) + "\n")
        file_SendMail.write("Begin Terminal name：" + str(__name__.BTN) + "\n")
        file_SendMail.write("Begin Terminal short-name：" + str(__name__.BTSN) + "\n")

        file_SendMail.write("到达城市：" + str(__name__.Acity) + "\n")
        file_SendMail.write("到达机场：" + str(__name__.Aairport) + "\n")
        file_SendMail.write("Arrive Terminal name：" + str(__name__.ATN) + "\n")
        file_SendMail.write("Arrive Terminal short-name：" + str(__name__.ATSN) + "\n")

        file_SendMail.write("起飞时间：" + str(__name__.BTime) + "\n")
        file_SendMail.write("到达时间：" + str(__name__.ATime) + "\n")
        file_SendMail.write("stopTimes：" + str(__name__.stopTime) + "\n")
        file_SendMail.write("stopInfo：" + str(__name__.stopInfo) + "\n")

        file_SendMail.write("\n============PRICE============" + "\n")
        for each_cabinPrice in __name__.Price:
            file_SendMail.write(
                str(each_cabinPrice[0]) + str(each_cabinPrice[1]) +
                str(each_cabinPrice[2]) + ": " + str(each_cabinPrice[3]) +
                ": " + str(each_cabinPrice[4]) + "\n")
            file_SendMail.write("-----------------------------" + "\n")
        file_SendMail.write("\n\n" + "\n")
        file_SendMail.close()
 
#------------------------------------------------------------------------------------------------------------

class Method():
    def getJSON(__name__, time, BcityName, AcityName):
        Method_Code = Code.Code()
        cityCode_dir = Method_Code.cityCode()
        BcityCode = cityCode_dir.setdefault(BcityName)
        AcityCode = cityCode_dir.setdefault(AcityName)
        headers = {'Accept':'*/*','Accept-encoding':'gzip, deflate, br',
            'Accept-language':'zh-CN,zh;q=0.8,zh-TW;q=0.7,zh-HK;q=0.5,en-US;q=0.3,en;q=0.2',
            'Connection':'keep-alive','Content-length':'290','Content-type':'application/json',
            'Cookie':r'_abtest_userid=aa51aa25-2900-4b5f-b8b0-e8ab6de1d4fc; _bfa=1.1575209493112.1801er.1.1575621253145.1575648985735.10.33; _RF1=113.4.53.44; _RSG=mu40V0ntd83qTvwvYxJZq9; _RDG=285d676ac5ebc524150d5faf0fa00c5953; _RGUID=3227df10-1f00-4e30-9d23-4fb8b9eb9774; Union=AllianceID=1095794&SID=2280904&OUID=; Session=SmartLinkCode=U2280904&SmartLinkKeyWord=&SmartLinkQuary=&SmartLinkHost=&SmartLinkLanguage=zh; _jzqco=%7C%7C%7C%7C1575650181832%7C1.532513354.1575209496384.1575648989004.1575650179591.1575648989004.1575650179591.undefined.0.0.29.29; __zpspc=9.11.1575648989.1575650179.2%231%7Cbaiduppc%7Cbaidu%7Cty%7C%25E6%259C%25BA%25E7%25A5%25A8api%7C%23; MKT_Pagesource=PC; DomesticUserHostCity=HRB|%b9%fe%b6%fb%b1%f5; appFloatCnt=6; FD_SearchHistorty={"type":"S","data":"S%24%u54C8%u5C14%u6EE8%28%u592A%u5E73%u56FD%u9645%u673A%u573A%29%28HRB%29%24HRB%242020-01-11%24%u53A6%u95E8%28XMN%29%24XMN"}; StartCity_Pkg=PkgStartCity=5; _bfi=p1%3D600001375%26p2%3D10320673302%26v1%3D32%26v2%3D31; MKT_CKID=1575622305172.62cqm.mf3u; _bfs=1.4',
            'DNT':'1','Host':'flights.ctrip.com','Origin':'https://flights.ctrip.com',
            'Referer':'https://flights.ctrip.com/itinerary/oneway/hrb-xmn?date=' + time,
            'TE':'Trailers','User-agent':'Mozilla/5.0 (Windows NT 10.0; Win64; x64; rv:71.0) Gecko/20100101 Firefox/71.0',}

        data = {"airportParams": [{"acity": AcityCode,"acityid": 25,"acityname": AcityName,"date": time,
                "dcity": BcityCode,"dcityid": 5,"dcityname": BcityName}],
            "classType":"ALL","date":time,"flightWay":"Oneway","hasBaby":'false',"hasChild":'false',"searchIndex":1,
            "token":"e048188e0dc27a8c2dfc1b0c25536782"}

        url = 'https://flights.ctrip.com/itinerary/api/12808/products'
        response = requests.post(url=url, headers=headers, json=data)
        # print(response.text)

        dict_str = json.loads(response.text)
        return dict_str

    def get_routeList(__name__, dict_str):
        data = dict_str.setdefault("data")
        routeList = data.setdefault("routeList")  # Flight list
        return routeList

    def get_legs_dict(__name__, routeList_dict):
        legs = routeList_dict.setdefault("legs")  # 本航班总信息
        legs_dict = legs[0]  # 只有一个字典元素
        return legs_dict

#------------------------------------------------------------------------------------------------------------

class Mail():

    def Mail(__name__, mailMSG):
        msg = MIMEText(mailMSG)
        msg["Subject"] = "xxx"
        msg["From"] = 'xxx'
        msg["To"] = ''

        from_addr = 'xxx'
        password = 'xxx'
        smtp_server = ''
        to_addr_list = ['']

        for to_addr in to_addr_list:
            try:
                server = smtplib.SMTP_SSL(smtp_server, 465, timeout=2)
                server.login(from_addr, password)
                server.sendmail(from_addr, [to_addr], msg.as_string())
                server.quit()
                print('success')
            except (Exception):
                print('Faild')
                
    def writeMail(__name__, Add, Delete, Change, FlightDict):
        file = open("Mail.txt", "a")
        Flight = FlightClass.Flight()
        if len(Add) != 0:
            file.write("======================Add=======================\n")
            file.close()
            for each in Add:
                Flight = FlightDict.setdefault(each)
                Flight.writeSendMail()
            file = open("Mail.txt", "a")
            file.write("====================================\n")
            file.close()
        else:
            file = open("Mail.txt", "a")
            file.write("No Add.\n")
            file.close()

        if len(Delete) != 0:
            file = open("Mail.txt", "a")
            file.write("=========================Delete===========================\n")
            file.close()
            file_old = open("flightMSG.dat", "rb")
            FlightDict_old = pickle.load(file_old)
            file_old.close()
            for each in Delete:
                Flight = FlightDict_old.setdefault(each)
                Flight.writeSendMail()
            file = open("Mail.txt", "a")
            file.write("===========================================\n")
            file.close()
        else:
            file = open("Mail.txt", "a")
            file.write("No Delete.\n")
            file.close()

        if len(Change) != 0:
            file = open("Mail.txt", "a")
            file.write("=================Change============\n")
            file.close()
            for each in Change:
                Flight = FlightDict.setdefault(each)
                Flight.writeSendMail()
            file = open("Mail.txt", "a")
            file.write("====================================\n")
            file.close()
        else:
            file = open("Mail.txt", "a")
            file.write("No Change.\n")
            file.close()

    def SendMail(__name__, judgeList):
        if 1 in judgeList:
            file = open("Mail.txt", "r")
            mailMSG = file.read()
            file.close()
            msg = MIMEText(mailMSG)
            msg["Subject"] = "xxxx"
            msg["From"] = 'xxx'
            msg["To"] = 'xxx'
            from_addr = 'xxxx'
            password = 'xxx'
            smtp_server = 'smtp.qq.com'
            to_addr_list = ['xxx']

            for to_addr in to_addr_list:
                try:
                    server = smtplib.SMTP_SSL(smtp_server, 465, timeout=2)
                    server.login(from_addr, password)
                    server.sendmail(from_addr, [to_addr], msg.as_string())
                    server.quit()                    
                except (Exception):
                    print("|       Send mail error!       |")
        else:
            print("| No change, didn't send mail. |")


# ----------------------------------------------------------------------------------------------


if __name__ == '__main__':
    sleep_time = 'xxx'
    BcityName = 'xxx'
    AcityName = 'xxx'
    time = 'xxx' # Deaprture time
    aroundTime = 0
    while (1):
        aroundTime += 1
        FlightDict = {}

        dict_str = Method.getJSON(time, BcityName,AcityName) 
        routeList = Method.get_routeList(dict_str)  # Flight list

        for routeList_dict in routeList:  # for each_flight in routeList
            if routeList_dict.setdefault("routeType") == "Flight":
                legs_dict = Method.get_legs_dict(routeList_dict)  # 本航班总信息

                method_Six = method_getSix.getSix()
                flightMSG = {}
                departureAirportInfoMSG = {}
                arrivalAirportInfoMSG = {}
                timeMSG = {}
                priceMSG = []
                method_Six.getSix(legs_dict, flightMSG, departureAirportInfoMSG, arrivalAirportInfoMSG, timeMSG, priceMSG)
                
                Flight = Flight()
                Flight.inputMSG(flightMSG, departureAirportInfoMSG,arrivalAirportInfoMSG, timeMSG, priceMSG)

                FlightDict[Flight.FlightNumber] = Flight
            elif routeList_dict.setdefault("routeType") == "FlightTrain":
                pass

        # print(FlightDict)
        file = open("flightMSG_temp.dat", "wb")
        pickle.dump(FlightDict, file)
        file.close()


        Add = []
        Delete = []
        Change = []
        Method_checkEachDict = checkEachDcit.check()
        Method_Change = method_Change_flightMSGdat.changeFile()
        judgeList = Method_checkEachDict.check(Add, Delete, Change)


        file_Mail = open("Mail.txt", "w")
        file_Mail.close()
        Mail.writeMail(Add, Delete, Change, FlightDict)
        Mail.SendMail(judgeList)

        Method_Change.changeFile()
        print("Sleep for " + str(sleep_time) + " second.")
        sleep(int(sleep_time))
