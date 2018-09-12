import logging
import tracker
from tracker.user import User
import tracker.db as db
import werkzeug.security

logger = logging.getLogger(__name__)

@tracker.lm.user_loader
def load_user(id):
    user = db.query_db('SELECT * FROM users WHERE username = ?', [id], one=True)
    return User(user['username'], user['displayname'], user['admin'])

def create_user(username, display_name, password):
    pw_hash = werkzeug.security.generate_password_hash(password)
    db.query_db('INSERT INTO users(username, displayname, password) VALUES(?, ?, ?)', (username.lower(), display_name, pw_hash))
    return User(username.lower(), display_name, 0)

def check_login(username, password):
    if tracker.user.exists(username):
        pw_hash = db.query_db('SELECT password FROM users WHERE username = ?', [username], one=True)['password']
        valid = werkzeug.security.check_password_hash(pw_hash, password)
        if valid:
            return tracker.user.get_user(username)
    return False
