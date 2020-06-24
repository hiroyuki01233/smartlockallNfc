import RPi.GPIO as GPIO
import os
import requests
import urllib.request
import base64
import sqlite3
import time
import datetime
import binascii
import nfc
import os
import userInfo 

open_key_words = ["開けて","開ける","開","open","開け","開く","解除","あ","あけて","あける"]

close_key_words = ["閉めて","閉める","閉","close","閉じろ","閉まる","施錠","し","しめる","しめて"]

user = userInfo.USER_ID

def getNewMessage():
    conn = sqlite3.connect("/var/apps/smartLock/linebot/history.db")

    c = conn.cursor()

    c.execute("select message from user order by id desc limit 1;")

    data = c.fetchall()
    data = str(data)
    data = data[3:]
    data = data[:-4]
    conn.close()
    return data

def openedFlg():
    lastMessage = getNewMessage()
    if lastMessage in close_key_words:
        return True
    else:
        return False

def open_key(angle):

    GPIO.setmode(GPIO.BCM)
    
    gp_out = 2
    GPIO.setup(gp_out, GPIO.OUT)
    motor = GPIO.PWM(gp_out, 50)
    motor.start(0.0)
    motor.ChangeDutyCycle(angle)
    time.sleep(0.5)

    GPIO.cleanup()
    return True

def database_history(name,mess):

    dt_now = datetime.datetime.now()
    dt_now = str(dt_now)
    dt_now = dt_now[:20]

    conn = sqlite3.connect('/var/apps/smartLock/linebot/history.db')

    c = conn.cursor()
    userName = user[name]

    testname = "testName"
    c.execute('insert into user\
            (datetime,username,message,user_id)values("%s","%s","%s","%s");'%(dt_now,userName,mess,name))

    conn.commit()
    conn.close()

def openCloseKey(cardId):
    now = openedFlg()
    if now == True:
        open_key(7.5)
        database_history(cardId,"あ")
    else:
        open_key(2.5) 
        database_history(cardId,"し")

class MyCardReader(object):
    def on_connect(self, tag):
 
        self.idm = binascii.hexlify(tag._nfcid)
        cardId = self.idm.decode()
        if cardId in user:
            openCloseKey(cardId)
 
        return True
 
    def read_id(self):
        clf = nfc.ContactlessFrontend('usb')
        try:
            clf.connect(rdwr={'on-connect': self.on_connect})
        finally:
            clf.close()
 
if __name__ == '__main__':
    cr = MyCardReader()
    while True:
        cr.read_id()
