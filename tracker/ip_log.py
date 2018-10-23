import logging
import flask
import flask_login
from tracker import app

logger = logging.getLogger(__name__)


@app.before_request
def ip_logging():
    if flask_login.current_user.is_authenticated:
        logger.info('^%s^ coming from %s, doing %s at %s', flask_login.current_user.get_id(), flask.request.remote_addr, flask.request.method, flask.request.path)
