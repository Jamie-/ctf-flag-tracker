import json
from flask import Flask
import flask_login
import logging
import sys

app = Flask(__name__)

with open('/srv/tracker/config.json') as f:
    config = json.load(f)
app.config.update(config)
if 'VIEW_CONFIG' in app.config:
    app.jinja_env.globals['VIEW_CONFIG'] = app.config['VIEW_CONFIG']  # Allow view config access in templates
else:
    app.jinja_env.globals['VIEW_CONFIG'] = {}


# Setup logging
log_formatter = logging.Formatter('%(asctime)s[%(levelname)8s][%(module)s] %(message)s', datefmt='[%m/%d/%Y][%I:%M:%S %p]')
root_logger = logging.getLogger()
root_logger.setLevel(logging.getLevelName(app.config['LOG_LEVEL'].upper()))

# Console log handler
log_console_handler = logging.StreamHandler(sys.stdout)
log_console_handler.setFormatter(log_formatter)
root_logger.addHandler(log_console_handler)

# Log file handler
log_file_handler = logging.FileHandler(app.config['LOG_FILE_PATH'])
log_file_handler.setFormatter(log_formatter)
root_logger.addHandler(log_file_handler)


lm = flask_login.LoginManager()
lm.init_app(app)
lm.login_view = '/login'
lm.login_message = 'You need to be logged in to do that.'
lm.login_message_category = 'danger'

from tracker import views, user
