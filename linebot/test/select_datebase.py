import sqlite3
import datetime

conn = sqlite3.connect("history.db")

c = conn.cursor()
c.execute("select * from user order by id desc limit 10;")
data = c.fetchall()
data = str(data)
conn.close()
print(data)
