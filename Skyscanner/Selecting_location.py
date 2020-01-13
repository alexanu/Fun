# Source: https://github.com/dezember/SkyscannerMultiCountry/blob/master/skyscanner.py


import random
import numpy 
import webbrowser
import time

'''
Old:
"http://www.skyscanner.net/transport/flights/nyca/ams/150310/150515/
airfares-from-new-york-to-amsterdam-in-march-2015-and-may-2015.html
?adults=1&children=0&infants=0
&cabinclass=economy
&preferdirects=false&rtn=1&outboundaltsenabled=false&inboundaltsenabled=false
&usrplace="+i+"&_ga=1.261604493.1064652340.1416570493"

New:
'https://www.skyscanner.de/transport/fluge/'+
'muc/hnl/'+
201102/201121/
?adults=2&children=1&adultsv2=2&childrenv2=4&infants=0
&cabinclass=economy
&rtn=1
&preferdirects=false
&outboundaltsenabled=false&inboundaltsenabled=false
&usrplace="+i+
&ref=home&duration=2100







https://www.espanol.skyscanner.com/transport/flights/muc/hnl/201102/201121/?adults=2&children=1&adultsv2=2&childrenv2=4&infants=0&cabinclass=economy&rtn=1&preferdirects=false&outboundaltsenabled=false&inboundaltsenabled=false&ref=home&market=PE&locale=en-US&currency=EUR

https://www.skyscanner.pt/transport/flights/muc/hnl/201102/201121/?adults=2&children=1&adultsv2=2&childrenv2=4&infants=0&cabinclass=economy&rtn=1&preferdirects=false&outboundaltsenabled=false&inboundaltsenabled=false&ref=home&market=PT&locale=en-US&currency=EUR
https://www.skyscanner.ro/transport/flights/muc/hnl/201102/201121/?adults=2&children=1&adultsv2=2&childrenv2=4&infants=0&cabinclass=economy&rtn=1&preferdirects=false&outboundaltsenabled=false&inboundaltsenabled=false&ref=home&market=RO&locale=en-US&currency=EUR
https://www.skyscanner.ro/transport/flights/muc/hnl/201102/201121/?adults=2&children=1&adultsv2=2&childrenv2=4&infants=0&cabinclass=economy&rtn=1&preferdirects=false&outboundaltsenabled=false&inboundaltsenabled=false&ref=home&market=RO&locale=en-GB&currency=EUR


https://www.skyscanner.com.ua/transport/flights/muc/hnl/201102/201121/?adults=2&children=1&adultsv2=2&childrenv2=4&infants=0&cabinclass=economy&rtn=1&preferdirects=false&outboundaltsenabled=false&inboundaltsenabled=false&ref=home

https://www.skyscanner.net/transport/fluge/muc/hnl/201102/201121/?adults=2&children=1&adultsv2=2&childrenv2=4&infants=0&cabinclass=economy&rtn=1&preferdirects=false&outboundaltsenabled=false&inboundaltsenabled=false&ref=home&previousCultureSource=COOKIE&redirectedFrom=www.skyscanner.de&market=BE&locale=uk-UA&currency=EUR&duration=2100
https://www.skyscanner.net/transport/fluge/muc/hnl/201102/201121/?adults=2&children=1&adultsv2=2&childrenv2=4&infants=0&cabinclass=economy&rtn=1&preferdirects=false&outboundaltsenabled=false&inboundaltsenabled=false&ref=home&previousCultureSource=COOKIE&redirectedFrom=www.skyscanner.de&market=BE&locale=de-DE&currency=EUR&duration=2100
https://www.tianxun.com/transport/fluge/muc/hnl/201102/201121/?adults=2&children=1&adultsv2=2&childrenv2=3&infants=0&cabinclass=economy&rtn=1&preferdirects=false&outboundaltsenabled=false&inboundaltsenabled=false&ref=home


'''

country=["IN","AF","AL","DZ","AS","AO","AI","AQ","AG","AR","AM","AW"
,"AU","AT","AZ","BS","BH","BD","BB","BY","BE","BZ","BJ","BM","BT","BO"
,"BA","BW","BR","VG","BN","BG","BF","BI","KH","CM","CA","CV","BQ","KY"
,"CF","TD","CL","CN","CX","CC","CO","KM","CG","CK","CR","HR","CU","CW"
,"CY","CZ","DK","DJ","DM","DO","CD","TL","EC","EG","SV","GQ","ER","EE"
,"ET","FK","FO","FJ","FI","FR","GF","PF","GA","GM","GE","DE","GH","GI"
,"GR","GL","GD","GP","GU","GT","GG","GN","GW","GY","HT","HN","HK","HU"
,"IS","IN","ID","IR","IQ","IE","IL","IT","CI","JM","JP","JO","KZ","KE"
,"KI","KO","KW","KG","LA","LV","LB","LS","LR","LY","LT","LU","MO","MG"
,"MW","MY","MV","ML","MT","MH","MQ","MR","MU","YT","MX","FM","MD","MC"
,"MN","ME","MS","MA","MZ","MM","NA","NR","NP","NL","NC","NZ","NI","NE"
,"NG","NU","KP","MP","NO","OM","PK","PW","PA","PG","PY","PE","PH","PL"
,"PT","PR","QA","MK","RE","RO","RU","RW","BL","KN","LC","VC","WS","ST"
,"SA","SN","RS","SC","SL","SG","SK","SI","SB","SO","ZA","KR","SS","ES"
,"LK","SX","PM","SD","SR","SZ","SE","CH","SY","TW","TJ","TZ","TH","TG"
,"TO","TT","TN","TR","TM","TC","TV","UG","UA","AE","UK","US","UY","UZ"
,"VU","VE","VN","VI","WF","YE","ZM","ZW"]
 

https://www.skyscanner.net/transport/flights/
muc/hnl/
201102/201121/
?adults=2&children=1&adultsv2=2&childrenv2=4&infants=0
&cabinclass=economy
&rtn=1
&preferdirects=false
&outboundaltsenabled=false&inboundaltsenabled=false
&ref=home
&market=PT
&locale=en-US&currency=EUR



for i in random.sample(country,k=3):
        url=('http://www.skyscanner.net/transport/flights/' +
            r'muc/hnl/'+
            r'201102/201121/'+
            r'?adults=2&children=1&adultsv2=2&childrenv2=4&infants=0'+
            r'&cabinclass=economy'+
            r'&rtn=1'+
            r'&preferdirects=false'+
            r'&outboundaltsenabled=false&inboundaltsenabled=false'+
            r'&ref=home&duration=2100'+
            r'&market='+i+
            r'&locale=en-US&currency=EUR')
        webbrowser.open_new_tab(url)
        time.sleep(4)
        #print i



https://www.skyscanner.net/transport/flights/muc/hnl/201102/201121/
?adults=2&children=1&adultsv2=2&childrenv2=4&infants=0
&cabinclass=economy
&rtn=1
&preferdirects=false&outboundaltsenabled=false&inboundaltsenabled=false
&ref=home&market=MZ&locale=en-US&currency=EUR&duration=2100





