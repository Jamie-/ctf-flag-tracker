import flask
import flask_login
import logging
from tracker import app

logger = logging.getLogger(__name__)


@app.errorhandler(400)
def error_400(error):
    return flask.render_template('error.html', title='400', heading='Error 400', text="Oh no, that's an error!"), 400


@app.errorhandler(401)
def error_401(error):
    return flask.render_template('error.html', title='401', heading='Error 401', text="Oh no, that's an error!"), 401


@app.errorhandler(403)
def error_403(error):
    return flask.render_template('error.html', title='403', heading='Error 403', text="Oh no, that's an error!"), 403


@app.errorhandler(404)
def error_404(error):
    return flask.render_template('error.html', title='404', heading='Error 404', text="Oh no, that's an error!"), 404


@app.errorhandler(405)
def error_405(error):
    return flask.render_template('error.html', title='405', heading='Error 405', text="Oh no, that's an error!"), 405


@app.errorhandler(500)
def error_500(error):
    logger.error('500 Internal Server Error:')
    logger.error(error)
    if flask_login.current_user.is_authenticated:
        logger.error('Triggered by ^%s^', flask_login.current_user.get_id())
    else:
        logger.error('Triggered anonymously')  # i.e. by logged out user
    return flask.render_template('error.html', title='500', heading='Error 500', text="Oh no, that's an error!"), 500
