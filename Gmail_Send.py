#!/usr/bin/env python2
# -*- coding: utf-8 -*-

import datetime
import smtplib
from email.mime.text import MIMEText

REC_EMAIL = "shawnmil@buffalo.edu"
SND_EMAIL = "stratus.print.ub@gmail.com"
SND_PSSWD = ""

def send_email(msg       = "",
               subject   = "Test email",
               rec_email = REC_EMAIL,
               snd_email = SND_EMAIL,
               snd_psswd = SND_PSSWD
              ):
    """Will send an email via gmail

    msg:        Message to be sent, converted to a string, default=""
    subject:    Subject of the email, default=Test email
    rec_email:  Address of the recipient, defaulted
    snd_email:  Address of the sender, defaulted
    snd_psswd:  Password for sender's account
    """

    dt = datetime.datetime.now();
    body     = str(dt) + "\n" + str(msg)
    e_msg            = MIMEText(body)
    e_msg['From']    = snd_email
    e_msg['To']      = rec_email
    e_msg['Subject'] = subject
    text = e_msg.as_string()

    server = smtplib.SMTP_SSL("smtp.gmail.com", 465)
    server.login(snd_email, snd_psswd)
    server.sendmail(snd_email, rec_email, text)
    print("Done!")
    server.close()

if __name__ == "__main__":
    my_dict = {
            'temperature': '22C',
            'hostname': 'testname'
    }
    send_email(my_dict)
