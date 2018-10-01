import logging
import tracker.db as db

logger = logging.getLogger(__name__)


class User():

    def __init__(self, username, display_name, admin):
        self.username = username
        self.display_name = display_name
        if admin is not None and (admin or admin == 1):
            self.admin = 1
        else:
            self.admin = 0

    ## FLASK_LOGIN #################
    def is_authenticated(self):
        return True

    def is_active(self):
        return True

    def is_anonymous(self):
        return False

    def get_id(self):
        return self.username

    def get_name(self):
        return self.display_name
    ## /FLASK_LOGIN ################

    # Update user's display name
    def update_display_name(self, display_name):
        self.display_name = display_name
        db.query_db('UPDATE users SET displayname = ? WHERE username = ?', [display_name, self.username])
        logger.info("^%s^ updated their display name to '%s'", self.username, display_name)

    # Get global score for this user
    def get_global_score(self):
        score = db.query_db('''
            SELECT SUM(f.value)
            FROM flagsfound ff
            LEFT JOIN flags f ON f.flag = ff.flag_id
            LEFT JOIN users u ON u.username = ff.user_id
            WHERE ff.user_id = ?
        ''', [self.username], one=True)[0]
        if score is None:
            score = 0
        return score

    # Get number of flags found by user
    def get_no_flags(self):
        return db.query_db('SELECT COUNT(*) FROM flagsfound WHERE user_id = ?', [self.username], one=True)[0]

    # Get user's score for current event
    def get_current_event_score(self):
        score = db.query_db('''
            SELECT SUM(f.value) FROM users u
            LEFT JOIN flagsfound ff ON ff.user_id = u.username
            LEFT JOIN flags f ON f.flag = ff.flag_id
            LEFT JOIN events e ON f.event_id = e.id
            WHERE e.active = 1
            AND u.username = ?
        ''', [self.username], one=True)[0]
        if score is None:
            return 0
        return score

    # Get user's score for given event
    def get_event_score(self, event_id):
        score = db.query_db('''
            SELECT SUM(f.value) FROM users u
            LEFT JOIN flagsfound ff ON ff.user_id = u.username
            LEFT JOIN flags f ON f.flag = ff.flag_id
            LEFT JOIN events e ON f.event_id = e.id
            WHERE e.id = ?
            AND u.username = ?
        ''', (event_id, self.username), one=True)[0]
        if score is None:
            return 0
        return score

    # Get flags submitted by user
    def get_flags(self):
        return db.query_db('''
            SELECT f.flag, f.value, f.event_id FROM flags f
            LEFT JOIN flagsfound ff ON f.flag = ff.flag_id
            WHERE ff.user_id = ?
        ''', [self.username])

    # Check if user is admin
    def is_admin(self):
        u = db.query_db('SELECT * FROM users WHERE username = ?', [self.username], one=True)
        if u['admin'] is 1:
            return True
        return False

    # Set user admin privs
    def set_admin(self, admin):
        if admin:
            db.query_db('UPDATE users SET admin = 1 WHERE username = ?', [self.username])
        else:
            db.query_db('UPDATE users SET admin = 0 WHERE username = ?', [self.username])

    # Remove user and all data
    def remove(self):
        db.query_db('DELETE FROM flagsfound WHERE user_id = ?', [self.username])
        db.query_db('DELETE FROM teamusers WHERE user_id = ?', [self.username])
        db.query_db('DELETE FROM users WHERE username = ?', [self.username])

    def __repr__(self):
        return '<User %r>' % self.username


# Check whether a user exists
def exists(username):
    u = db.query_db('SELECT * FROM users WHERE username = ?', [username])
    if u:
        return True
    else:
        return False

# Get a user from ID
def get_user(username):
    u = db.query_db('SELECT * FROM users WHERE username = ?', [username], one=True)
    if u is None:
        return None
    else:
        return User(u['username'], u['displayname'], u['admin'])

# Get list of all users
def get_all():
    users = db.query_db('SELECT * FROM users')
    ulist = []
    for u in users:
        ulist.append(User(u['username'], u['displayname'], u['admin']))
    return ulist
