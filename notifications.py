from twilio.rest import Client

    def send_msg(self, msg):
        # Your Account SID from twilio.com/console
        account_sid = "AC0dadb0ce3f1db887ecf2cc5209932676"
        # Your Auth Token from twilio.com/console
        auth_token = "7eb9f55beeb3cfea278ccc183cf0f46a"

        client = Client(account_sid, auth_token)

        message = client.messages.create(
            to="+601128174379",
            from_="+17067395816",
            body=msg)
        return message.sid
        
    def create_msg(self, time_to_send):
        if time_to_send in self.time_list:
            data = self.final_data.loc[
                self.final_data['tmsp_3_min'] == time_to_send].copy()
            data = json.loads(data.to_json(orient='records'))
            main_body = str()
            for each in data:
                body = "Based: "+each['economy']+"\n"\
                    + "Info: "+each['name']+"\n"\
                    + "Impact: "+str(each['impact'])+"\n"\
                    + "Time: "+each['timestamp_af']
                main_body = main_body + "\n"+body
            code = self.send_msg(msg=body)
            print(code)
            
            
# ------------------------------------------------------------------------------------------------------------------------            
# ------------------------------------------------------------------------------------------------------------------------

import smtplib, os
from email.mime.multipart import MIMEMultipart
from email.mime.base import MIMEBase
from email.mime.text import MIMEText
from email.utils import COMMASPACE, formatdate
from email import encoders

SUBSCRIBE_LIST = [
    'weiyi.alan.chen@gmail.com',
    'wchen7@baml.com'
]

def email_login():
    me = raw_input("Your Gmail Address: ")
    import getpass
    password = getpass.getpass("Password: ")
    return me, password

def send_mail(send_from, send_to, subject, text, files=[], server="localhost", port=587, username='', password='', isTls=True):
    msg = MIMEMultipart()
    msg['From'] = send_from
    msg['To'] = COMMASPACE.join(send_to)
    msg['Date'] = formatdate(localtime = True)
    msg['Subject'] = subject

    msg.attach( MIMEText(text) )

    for f in files:
        part = MIMEBase('application', "octet-stream")
        part.set_payload( open(f,"rb").read() )
        encoders.encode_base64(part)
        part.add_header('Content-Disposition', 'attachment; filename="{0}"'.format(os.path.basename(f)))
        msg.attach(part)

    smtp = smtplib.SMTP(server, port)
    if isTls: smtp.starttls()
    smtp.login(username,password)
    smtp.sendmail(send_from, send_to, msg.as_string())
    smtp.quit()

    
import pandas
import urllib2
from emails import SUBSCRIBE_LIST, email_login, send_mail

def get_ETF_fr_YH(filename):
    ls_etf = []
    the_page = urllib2.urlopen('http://finance.yahoo.com/etf/lists/?mod_id=mediaquotesetf&tab=tab3&rcnt=50').read()    
    splits = the_page.split('<a href=\\"\/q?s=')
    etf_symbols = [split.split('\\')[0] for split in splits[1:]]
    for etf in etf_symbols:
        ls_etf.append(etf)
    df = pandas.DataFrame({'ETF': ls_etf})
    df.set_index('ETF').to_csv(filename)

def run(me, password):
    get_ETF_fr_YH('ETF.csv')
    send_mail(
        send_from = 'NoReply@gmail.com', 
        send_to = SUBSCRIBE_LIST, 
        subject = 'Suggested ETF', 
        text = """Hello,
Attachment includes the ETFs.
Sincerely,
""", 
        files = ['ETF.csv'], 
        server = 'smtp.gmail.com',
        username = me,
        password = password
    )

if __name__ == '__main__':
    me, password = email_login()
    run(me, password)    

    
    
# ------------------------------------------------------------------------------------------------------------------------            
# ------------------------------------------------------------------------------------------------------------------------

import urllib2
import time
import smtplib, random
import os, sys
import personal

SECOND_PER_MINUTE = 60


def send_mail(subject):
# The below code never changes, though obviously those variables need values.
  GMAIL_USERNAME = personal.gmail_address
  GMAIL_PASSWORD = personal.password
  RECIPIENT = personal.recipient
  session = smtplib.SMTP('smtp.gmail.com', 587)
  session.ehlo()
  session.starttls()
  session.login(GMAIL_USERNAME, GMAIL_PASSWORD)
  
  headers = "\r\n".join(["from: " + "Do hackme",
                         "subject: " + subject,
                         "to: " + "me",
                         "mime-version: 1.0",
                         "content-type: text/html"])

  # body_of_email can be plaintext or html!                    
  content = headers + "\r\n\r\n" 
  session.sendmail(GMAIL_USERNAME, RECIPIENT, content)

pwd = personal.pwd
# print(pwd)
# read product names;
pfile = open(pwd + '/products.txt', 'r')
products = [line.strip() for line in pfile]

# read deal websites;
webFile = open(pwd + '/websites.txt', 'r')
webs = [line.strip() for line in webFile]

need = [True] * len(products)
count = 1

while True in need:
  for i in range(len(products)):
    if need[i]:
      product = products[i].lower()
      
      for address in webs:
        page = urllib2.urlopen(address).read()
        page = page.lower()
        if product in page:
          title = address + ' has ' + product
          send_mail(title)
          need[i] = False

  LB = 5
  UB = 15
  minute = random.randint(LB, UB)
  time.sleep(SECOND_PER_MINUTE * minute)

    
