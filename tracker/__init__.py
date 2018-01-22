import json
from flask import Flask
import flask_login
import logging

# Setup logging
logging.basicConfig(format='%(asctime)s[%(levelname)8s][%(module)s] %(message)s', datefmt='[%m/%d/%Y][%I:%M:%S %p]', level=logging.INFO)

app = Flask(__name__)

with open('/srv/tracker/config.json') as f:
    config = json.load(f)
app.config.update(config)

lm = flask_login.LoginManager()
lm.init_app(app)
lm.login_view = '/login'
lm.login_message = 'You need to be logged in to do that.'
lm.login_message_category = 'danger'

from tracker import views, user
