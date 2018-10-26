from climate.climate import app
import os
# Load default config and override config from an environment variable
DATABASE=os.path.join(app.root_path, '../climate.db')
SECRET_KEY=os.urandom(32)
USERNAME='admin'
PASSWORD='pass'
LIGHT_CONFIG=os.path.join(app.root_path, '../light_config.json')
RASPBERRY=False
LIGHT_CONTROL_SCRIPT=os.path.join(app.root_path, '../lightControl.py')