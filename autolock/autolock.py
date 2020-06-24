import RPi.GPIO as GPIO
import sqlite3
import datetime
import time

open_key_words = ["開けて","開ける","開","open","開け","開く","解除","あ","あけて","あける"]

close_key_words = ["閉めて","閉める","閉","close","閉じろ","閉まる","施錠","し","しめる","しめて"]

def getNewMessage():
    conn = sqlite3.connect("/home/pi/app/linebot/history.db")

    c = conn.cursor()

    c.execute("select message from user order by id desc limit 1;")

    data = c.fetchall()
    data = str(data)
    data = data[3:]
    data = data[:-4]
    conn.close()
    return data

def database_history():

    dt_now = datetime.datetime.now()
    dt_now = str(dt_now)
    dt_now = dt_now[:20]

    conn = sqlite3.connect("/home/pi/app/linebot/history.db")

    c = conn.cursor()

    c.execute('insert into user\
            (datetime,username,message,user_id)values("%s","System","しめる","System");'%(dt_now))
    conn.commit()
    conn.close()

def close_key():

    data = getNewMessage()

    if data in close_key_words:
        return False
    else:
        GPIO.setmode(GPIO.BCM)

        gp_out = 2
        GPIO.setup(gp_out, GPIO.OUT)
        motor = GPIO.PWM(gp_out, 50)
        motor.start(0.0)
        motor.ChangeDutyCycle(2.5)
        time.sleep(0.5)

        GPIO.cleanup()

        database_history()

        return True


    conn.commit()
    conn.close()

close_key()
