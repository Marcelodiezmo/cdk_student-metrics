import smtplib  
import email.utils
from email.mime.multipart import MIMEMultipart
from email.mime.text import MIMEText
    
class Send_Email:
    def email_powerbi_notify(sender, sender_name, recipient, username_smtp, password_smtp, configuration_set, last_header,CREDENTIALS, api_response):
        HOST = "email-smtp.us-east-1.amazonaws.com"
        PORT = 587
        SUBJECT = "PowerBI Embedded Alarm"

        # The HTML body of the email.
        BODY_HTML = """"<html>
            <head></head>
            <body>
            <h1> PowerBI Embedded Alarm</h1>
            <p>PowerBI Embedded is down and backup credentials are not working.</p>
            <h3>API response:</h3>
            <p>"""+str(api_response)+"""</p>
            <h3>Last HEADER used:</h3>
            <p>"""+str(last_header)+"""</p>
            <h3>Last CREDENTIALS used:</h3>
            <p>"""+str(CREDENTIALS)+"""</p>
            <p><b>Do not repply, but fix it ASAP</b></p>
            <p>This email was set by PowerBI Embedded API</p>
            <p>Ubits Tech</p>
            </body>
            </html> """

        # Create message container - the correct MIME type is multipart/alternative.
        msg = MIMEMultipart('alternative')
        msg['Subject'] = SUBJECT
        msg['From'] = email.utils.formataddr((sender_name, sender))
        msg['To'] = recipient
        msg.add_header('X-SES-CONFIGURATION-SET', configuration_set)

        part1 = MIMEText(BODY_HTML, 'html')
        msg.attach(part1)

        # Try to send the message.
        try:  
            server = smtplib.SMTP(HOST, PORT)
            server.ehlo()
            server.starttls()
            server.ehlo()
            server.login(username_smtp, password_smtp)
            server.sendmail(sender, recipient, msg.as_string())
            server.close()
        except Exception as e: print ("Error: ", e)
        else: print ("Email "+recipient)