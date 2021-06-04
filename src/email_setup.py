import smtplib, ssl
from email.mime.multipart import MIMEMultipart

import datetime
from datetime import date

import requests

class email:
    receiver_address =""
    message = ""

    def __init__(self, config_data):
        self.receiver_address = config_data['Login'][0]['username']

    def send_email(self):
        return requests.post(
		"mailgun api link",
		auth=("api", ""),
		data={"from": "Nice Hash Trade Report <mailgun address provided in your mailgun dashboard>",
			"to": "Jane Doe <Jane_doe@jane.doe>",
			"subject": f"NiceHash Trade Report {date.today()}\n\n",
			"text": f"{self.message}"})


        #context = ssl.create_default_context()

        #with smtplib.SMTP_SSL("smtp.gmail.com", self.port, context = context) as server:
            #server.login(self.sender_address, self.password)
            #server.sendmail(self.sender_address, self.reciever_address, self.message)
    
    def write_email_message(self, text):
        self.message += (f'{text}\n')