import os
from flask import Flask
import flask_login

app = Flask(__name__)
app.config.from_object('config')

lm = flask_login.LoginManager()
lm.init_app(app)
lm.login_view = '/login'
lm.login_message = 'You need to be logged in to do that.'
lm.login_message_category = 'danger'

from tracker import views, user
