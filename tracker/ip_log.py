import logging
import flask
import flask_login
from tracker import app

logger = logging.getLogger(__name__)


@app.before_request
def ip_logging():
    if flask_login.current_user.is_authenticated:
        ip_addr = flask.request.remote_addr
        if 'X-Real-IP' in flask.request.headers:  # Detect nginx reverse proxying
            ip_addr = flask.request.headers['X-Real-IP']
        logger.info('^%s^ coming from %s, doing %s at %s', flask_login.current_user.get_id(), ip_addr, flask.request.method, flask.request.path)
