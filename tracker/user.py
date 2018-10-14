import logging
import flask_login
import werkzeug.security
import tracker.db as db

logger = logging.getLogger(__name__)


class User():

    def __init__(self, username, display_name, perm):
        self.username = username
        self.display_name = display_name
        self.perm = perm

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

    # Update user's password
    def update_password(self, new_password):
        pw_hash = werkzeug.security.generate_password_hash(new_password)
        db.query_db('UPDATE users SET password = ? WHERE username = ?', [pw_hash, self.username])
        logger.info('^%s^ updated their password.', self.username)

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
        import tracker.event as event
        import tracker.flag as flag
        res = db.query_db('''
            SELECT f.flag, f.value, f.event_id, f.notes FROM flags f
            LEFT JOIN flagsfound ff ON f.flag = ff.flag_id
            WHERE ff.user_id = ?
        ''', [self.username])
        flags = []
        for f in res:
            flags.append(flag.Flag(f['flag'], f['value'], event=event.get_event(f['event_id']), notes=f['notes']))
        return flags

    # Check if user is admin
    def is_admin(self):
        return self.perm >= 2

    # Check if user is super-admin
    def is_super_admin(self):
        return self.perm == 10

    # Set user's permission
    def set_perm(self, perm):
        if perm is None:
            db.query_db('UPDATE users SET permission = NULL WHERE username = ?', [self.username])
            self.perm = None
            return
        if perm < 0 or perm > 10:
            raise ValueError('Permission value out of range (0-10).')
        db.query_db('UPDATE users SET permission = ? WHERE username = ?', (perm, self.username))
        self.perm = perm

    # Remove user and all data
    def remove(self):
        db.query_db('DELETE FROM flagsfound WHERE user_id = ?', [self.username])
        db.query_db('DELETE FROM teamusers WHERE user_id = ?', [self.username])
        db.query_db('DELETE FROM users WHERE username = ?', [self.username])
        if flask_login.current_user.get_id() == self.username:
            logger.info('^%s^ deleted their own account.', self.username)
        else:
            logger.info('^%s^ deleted the user ^%s^.', flask_login.current_user.get_id(), self.username)

    def __repr__(self):
        return '<User %r>' % self.username


# Check whether a user exists
def exists(username):
    u = db.query_db('SELECT * FROM users WHERE username = ?', [username.lower()])
    if u:
        return True
    else:
        return False

# Get a user from ID
def get_user(username):
    u = db.query_db('SELECT * FROM users WHERE username = ?', [username.lower()], one=True)
    if u is None:
        return None
    else:
        return User(u['username'], u['displayname'], u['permission'])

# Get list of all users
def get_all(sort_asc=False, admin_first=False):
    query_string = 'SELECT * FROM users'
    if admin_first:
        query_string += ' ORDER BY permission DESC'
        if sort_asc:
            query_string += ', username ASC'
    elif sort_asc:
        query_string += ' ORDER BY username ASC'
    users = db.query_db(query_string)
    ulist = []
    for u in users:
        ulist.append(User(u['username'], u['displayname'], u['permission']))
    return ulist
