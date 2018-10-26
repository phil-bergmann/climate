# climate

This is a small project for the Raspberry Pi. It consits of a web server (Flask) and additionaly records the humidity and temperature data through a DHT22 sensor and stores the values in a database. The measurements are plotted on the main page and through a password protected - not very good prtotected indeed but security was not a big aspect in this toy project - area one hardware PWM output of the Pi can be set to a certain value and additionaly a timer clock switches the ouput ON/OFF on a certain time.

Now one may ask for what this is all good? At least for what I used this is to measure the humidity and temperature in my student dorm room and the PWM output was used to control a constant current source that powered LED lamps in order for small room plants not to die in the winter when they don't get enough light in my room :)

To record temperature / humidity data use a chron job on climate/recordSensor.py. I recorded values every 15 minutes. To start the server on every restart just put startClimate.sh in autostart (can also be done with a chron job).

Still not happy with design and everything and stopped working on this project but perhaps still interesting for you out there :)

Have fun!
