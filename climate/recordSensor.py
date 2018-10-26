import Adafruit_DHT
import sqlite3
import sys
import os

dbpath = os.path.realpath(os.path.join(os.path.dirname(os.path.realpath(__file__)), "../climate.db"))

sensor = Adafruit_DHT.DHT22
pin = 4

humidity, temperature = Adafruit_DHT.read_retry(sensor, pin)

if humidity is not None and temperature is not None:
    temp = int(round(temperature*10))
    hum = int(round(humidity*10))
    
    db = sqlite3.connect(dbpath)
    db.row_factory = sqlite3.Row
    
    cur = db.execute("INSERT INTO entries (temperature, humidity) VALUES ({0:d}, {1:d})".format(temp, hum))
    
    db.commit()
    
    db.close()