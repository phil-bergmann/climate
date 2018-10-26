select datetime(timestamp, 'localtime') from

export FLASK_APP=hello.py
export FLASK_DEBUG=1

externaly visible
flask run --host=0.0.0.0

http://people.iola.dk/olau/flot/examples/visitors.html

http://stackoverflow.com/questions/15321431/how-to-pass-a-list-from-python-by-jinja2-to-javascript

save config files: https://martin-thoma.com/configuration-files-in-python/

select current time in sqlite: SELECT date('now');

https://github.com/adafruit/Adafruit_Python_DHT

Tutorial Large App: https://github.com/pallets/flask/wiki/Large-app-how-to

$ pacman -S wiringpi
$ gpio mode 1 pwm
$ gpio pwm-ms
$ gpio pwmc 1920
$ gpio pwmr 200     # 0.1 ms per unit
$ gpio pwm 1 15     # 1.5 ms (0º)
$ gpio pwm 1 20     # 2.0 ms (+90º)
$ gpio pwm 1 10     # 1.0 ms (-90º)
