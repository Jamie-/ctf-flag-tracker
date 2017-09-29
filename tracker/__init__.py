import json
from flask import Flask
import flask_login

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
