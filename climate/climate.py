import os
import sqlite3
import json
import re
import time
import random
import string
from flask import Flask, request, session, g, redirect, url_for, abort, \
    render_template, flash, jsonify
#from crontab import CronTab


app = Flask(__name__) # create the application instance :)
#print os.path.join(app.root_path, '../config.py')
app.config.from_pyfile(os.path.join(app.root_path, 'config.py')) # load config from this file
#print app.config['USERNAME']

# load config from file specified in environment variable, do not complain if not set
app.config.from_envvar('FLASKR_SETTINGS', silent=True)

# define function that maps a intensity value [0,100] to the corresponding pwm value [0,1000]
def mapIntensityToPWM(intensity):
    if intensity < 0:
        return 1000
    elif intensity > 100:
        return 0
    else:
        return 1000 - intensity*10
    
# variable that holds the current light status
app.config['LIGHT_STATUS'] = False
# load intensity from config, if not possible leave default value
app.config['INTENSITY'] = 0

# changing names for light on/off
app.config['LIGHTON_PATH'] = ''.join(random.choice(string.ascii_uppercase + string.digits) for _ in range(16))
app.config['LIGHTOFF_PATH'] = ''.join(random.choice(string.ascii_uppercase + string.digits) for _ in range(16))

try:
    with open(app.config['LIGHT_CONFIG']) as json_data_file:
        data = json.load(json_data_file)
        app.config['INTENSITY'] = int(data["intensity"])
        currentHour = time.localtime()[3]
        lightOn = int(data["light_on"].split(':')[0])
        lightOff = int(data["light_off"].split(':')[0])
        
        if currentHour < lightOn and currentHour < lightOff:
            if lightOff < lightOn:
                app.config['LIGHT_STATUS'] = True
            else:
                app.config['LIGHT_STATUS'] = False
        elif currentHour >= lightOn and currentHour >= lightOff:
            if lightOff < lightOn:
                app.config['LIGHT_STATUS'] = True
            else:
                app.config['LIGHT_STATUS'] = False
        else:
            if lightOff < lightOn:
                app.config['LIGHT_STATUS'] = False
            else:
                app.config['LIGHT_STATUS'] = True
except:
    pass

if app.config['RASPBERRY']:
    # wait for system resources to be loaded
    time.sleep(10)
    os.system("gpio -g mode 18 pwm")
    os.system("gpio pwm-ms")
    os.system("gpio pwmc 96")
    os.system("gpio pwmr 1000")
    if app.config['LIGHT_STATUS']:
        os.system("gpio -g pwm 18 "+str(mapIntensityToPWM(app.config['INTENSITY'])))
    else:
        os.system("gpio -g pwm 18 "+str(mapIntensityToPWM(0)))
    
    try:
        my_cron = None#CronTab(user=True)
        
        with open(app.config['LIGHT_CONFIG']) as json_data_file:
            data = json.load(json_data_file)
            lightOn = int(data["light_on"].split(':')[0])
            lightOff = int(data["light_off"].split(':')[0])
            
            my_cron.remove_all(comment='MEANWELL_LED')
            
            jobOn = my_cron.new(command='wget 127.0.0.1:5000/intern/'+app.config['LIGHTON_PATH'], comment='MEANWELL_LED')
            jobOff = my_cron.new(command='wget 127.0.0.1:5000/intern/'+app.config['LIGHTOFF_PATH'], comment='MEANWELL_LED')
            
            jobOn.hour.on(lightOn)
            jobOff.hour.on(lightOff)
            
            my_cron.write_to_user(user=True)
    except:
        pass

def connect_db():
    """Connects to the specific database."""
    rv = sqlite3.connect(app.config['DATABASE'])
    rv.row_factory = sqlite3.Row
    return rv

def init_db():
    db = get_db()
    with app.open_resource('schema.sql', mode='r') as f:
        db.cursor().executescript(f.read())
    db.commit()

def get_db():
    """Opens a new database connection if there is none yet for the
    current application context.
    """
    if not hasattr(g, 'sqlite_db'):
        g.sqlite_db = connect_db()
    return g.sqlite_db

# registers the command to flask, now in the shell flask initdb initializes the database
@app.cli.command('initdb')
def initdb_command():
    """Initializes the database."""
    init_db()
    print('Initialized the database.')

@app.teardown_appcontext
def close_db(error):
    """Closes the database again at the end of the request."""
    if hasattr(g, 'sqlite_db'):
        g.sqlite_db.close()

@app.route('/test')
def show_entries():
    db = get_db()
    cur = db.execute("select id, datetime(dt, 'localtime'), temperature, humidity from entries order by id asc")
    entries = cur.fetchall()
    print entries[0].keys()
    #entries = []
    return render_template('test.html', entries=entries)

@app.route('/admin', methods=['GET','POST'])
def admin():
    if not session.get('logged_in'):
        return redirect(url_for('index'))
    if request.method == 'POST':
        # some sanity checking
        try:
            intensity = int(request.form['intensity'])
            assert (intensity >= 0) & (intensity <= 100)
            light_on = request.form['light_on']
            light_off = request.form['light_off']
            assert checkTime(light_on)
            assert checkTime(light_off)
        except:
            print "[*] BAD REQUEST from /admin"
        else:
            data = {}
            data['intensity'] = intensity
            data['light_on'] = light_on
            data['light_off'] = light_off
            with open(app.config['LIGHT_CONFIG'], 'w') as outfile:
                json.dump(data, outfile)
            app.config['INTENSITY'] = intensity
            if app.config['RASPBERRY']:
                if app.config['LIGHT_STATUS']:
                    os.system("gpio -g pwm 18 "+str(mapIntensityToPWM(app.config['INTENSITY'])))
                    
                my_cron = None#CronTab(user=True)
                
                my_cron.remove_all(comment='MEANWELL_LED')
            
                jobOn = my_cron.new(command='wget 127.0.0.1:5000/intern/'+app.config['LIGHTON_PATH'], comment='MEANWELL_LED')
                jobOff = my_cron.new(command='wget 127.0.0.1:5000/intern/'+app.config['LIGHTOFF_PATH'], comment='MEANWELL_LED')
            
                jobOn.hour.on(int(light_on.split(':')[0]))
                jobOff.hour.on(int(light_off.split(':')[0]))
            
                my_cron.write_to_user(user=True)
                
        return render_template('admin.html')
        #return redirect(url_for('index'))
    else:
        return render_template('admin.html')
    
@app.route('/admin/config.json')
def admin_config():
    try:
        with open(app.config['LIGHT_CONFIG']) as json_data_file:
            data = json.load(json_data_file)
    except:
        data = {}
        data["intensity"] = 0
        
    return jsonify(data)

@app.route("/admin/<action>")
def admin_action(action):
    if not session.get('logged_in'):
        return redirect(url_for('index'))
    if action == "light_on":
        print "[*] Light ON"
        if app.config['RASPBERRY']:
            os.system("gpio -g pwm 18 "+str(mapIntensityToPWM(app.config['INTENSITY'])))
            app.config['LIGHT_STATUS'] = True
    elif action == "light_off":
        print "[*] Light OFF"
        if app.config['RASPBERRY']:
            os.system("gpio -g pwm 18 "+str(mapIntensityToPWM(0)))
            app.config['LIGHT_STATUS'] = False
    return redirect(url_for('admin'))

@app.route('/intern/<action>')
def intern(action):
    if action == app.config['LIGHTON_PATH']:
        if app.config['RASPBERRY']:
            os.system("gpio -g pwm 18 "+str(mapIntensityToPWM(app.config['INTENSITY'])))
            app.config['LIGHT_STATUS'] = True
    elif action == app.config['LIGHTOFF_PATH']:
        if app.config['RASPBERRY']:
            os.system("gpio -g pwm 18 "+str(mapIntensityToPWM(0)))
            app.config['LIGHT_STATUS'] = False
    return jsonify()
    
@app.route('/tempHumData.json')
def tempHumData():
    db = get_db()
    cur = db.execute("select strftime('%s','now','localtime')")
    entries = cur.fetchall()
    now = int(entries[0][0])
    cur = db.execute("select id, strftime('%s',dt,'localtime'), temperature, humidity from entries where datetime(dt, 'localtime') > datetime('now', 'localtime', '-7 days') order by id asc")
    entries = cur.fetchall()
    temp7 = []
    hum7 = []
    time7 = []
    temp3 = []
    hum3 = []
    time3 = []
    temp1 = []
    hum1 = []
    time1 = []
    delta3 = now - 3600*24*3
    delta1 = now - 3600*24*1
    deltaNow = now - 1800
    for e in entries:
        t = e["temperature"]/10.
        h = e["humidity"]/10.
        time = int(e["strftime('%s',dt,'localtime')"])
        temp7.append(t)
        hum7.append(h)
        time7.append(time*1000)
        if time > delta3:
            temp3.append(t)
            hum3.append(h)
            time3.append(time*1000)
        if time > delta1:
            temp1.append(t)
            hum1.append(h)
            time1.append(time*1000)
            
    data = {}
    
    data['temp7'] = zip(time7, temp7)
    data['hum7'] = zip(time7, hum7)
    data['temp3'] = zip(time3, temp3)
    data['hum3'] = zip(time3, hum3)
    data['temp1'] = zip(time1, temp1)
    data['hum1'] = zip(time1, hum1)
    
    data['tempNOW'] = 'NO DATA!'
    data['humNOW'] = 'NO DATA!'
    if time1:
        if max(time1) > deltaNow:
            data['tempNOW'] = temp1[-1]
            data['humNOW'] = hum1[-1]
        data['temp1MAX'] = max(temp1)
        data['hum1MAX'] = max(hum1)
        data['temp1MIN'] = min(temp1)
        data['hum1MIN'] = min(hum1)
    else:
        data['temp1MAX'] = 'NO DATA!'
        data['hum1MAX'] = 'NO DATA!'
        data['temp1MIN'] = 'NO DATA!'
        data['hum1MIN'] = 'NO DATA!'
    
    if time3:
        data['temp3MAX'] = max(temp3)
        data['hum3MAX'] = max(hum3)
        data['temp3MIN'] = min(temp3)
        data['hum3MIN'] = min(hum3)
    else:
        data['temp3MAX'] = 'NO DATA!'
        data['hum3MAX'] = 'NO DATA!'
        data['temp3MIN'] = 'NO DATA!'
        data['hum3MIN'] = 'NO DATA!'
        
    if time7:
        data['temp7MAX'] = max(temp7)
        data['hum7MAX'] = max(hum7)
        data['temp7MIN'] = min(temp7)
        data['hum7MIN'] = min(hum7)
    else:
        data['temp7MAX'] = 'NO DATA!'
        data['hum7MAX'] = 'NO DATA!'
        data['temp7MIN'] = 'NO DATA!'
        data['hum7MIN'] = 'NO DATA!'
    
    return jsonify(data)
    
@app.route('/')
def index():
    return render_template('index.html')

@app.route('/login', methods=['POST'])
def login():
    data = "fail"
    if request.form['user'] != app.config['USERNAME']:
        error = 'Invalid username'
    elif request.form['pin'] != app.config['PASSWORD']:
        error = 'Invalid password'
    else:
        session['logged_in'] = True
        data = "success"
    return jsonify(data)

@app.route('/logout', methods=['POST'])
def logout():
    session.pop('logged_in', None)
    #flash('You were logged out')
    return jsonify()

@app.route('/webcam')
def webcam():
    """Not implemented yet."""
    return redirect(url_for('index'))

def checkTime(timeString):
    """checks a string if it is a valid time (e.g. 0:15, 22:43)
    string is not allowed to contain any extra characters
    """
    match = re.match(r'^(\d{1,2}):(\d{2})$', timeString)
    if match == None:
        return False
    hours = int(match.group(1))
    minutes = int(match.group(2))
    if (hours < 0) | (hours > 23):
        return False
    if (minutes < 0) | (minutes > 59):
        return False
    return True