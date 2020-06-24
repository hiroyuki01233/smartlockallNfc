import sqlite3
import datetime


dt_now = datetime.datetime.now()
dt_now = str(dt_now)
dt_now = dt_now[:20]
print(dt_now)

name = "hiro"

message = "こんにちは"

conn = sqlite3.connect('history.db')

c = conn.cursor()

c.execute('insert into user\
        (datetime,username,message)values("%s","%s","%s");'%(dt_now,name,message))

conn.commit()
conn.close()


