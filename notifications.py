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
