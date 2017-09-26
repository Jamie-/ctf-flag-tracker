import tracker.db as db

class User():

    def __init__(self, id, name, admin=None):
        self.id = id
        self.name = name
        self.admin = admin

    ## FLASK_LOGIN #################
    def is_authenticated(self):
        return True

    def is_active(self):
        return True

    def is_anonymous(self):
        return False

    def get_id(self):
        return self.id

    def get_name(self):
        return self.name
    ## /FLASK_LOGIN ################

    # Get global score for this user
    def get_global_score(self):
        score = db.query_db('''
            SELECT SUM(f.value)
            FROM flagsfound ff
            LEFT JOIN flags f ON f.flag = ff.flag_id
            LEFT JOIN users u ON u.id = ff.user_id
            WHERE ff.user_id = ?
        ''', [self.id], one=True)[0]
        if score is None:
            score = 0
        return score

    # Get number of flags found by user
    def get_no_flags(self):
        return db.query_db('SELECT COUNT(*) FROM flagsfound WHERE user_id = ?', [self.id], one=True)[0]

    # Get user's score for current event
    def get_current_event_score(self):
        score = db.query_db('''
            SELECT SUM(f.value) FROM users u
            LEFT JOIN flagsfound ff ON ff.user_id = u.id
            LEFT JOIN flags f ON f.flag = ff.flag_id
            LEFT JOIN events e ON f.event_id = e.id
            WHERE e.active = 1
            AND u.id = ?
        ''', [self.id], one=True)[0]
        if score is None:
            return 0
        return score

    # Get user's score for given event
    def get_event_score(self, event_id):
        score = db.query_db('''
            SELECT SUM(f.value) FROM users u
            LEFT JOIN flagsfound ff ON ff.user_id = u.id
            LEFT JOIN flags f ON f.flag = ff.flag_id
            LEFT JOIN events e ON f.event_id = e.id
            WHERE e.id = ?
            AND u.id = ?
        ''', (event_id, self.id), one=True)[0]
        if score is None:
            return 0
        return score

    # Check if user is admin
    def is_admin(self):
        u = db.query_db('SELECT * FROM users WHERE id = ?', [self.id], one=True)
        if u['admin'] is 1:
            return True
        return False

    # Set user admin privs
    def set_admin(self, admin):
        if admin:
            db.query_db('UPDATE users SET admin = 1 WHERE id = ?', [self.id])
        else:
            db.query_db('UPDATE users SET admin = 0 WHERE id = ?', [self.id])

    def __repr__(self):
        return '<User %r>' % self.id


# Check whether a user exists
def exists(id):
    u = db.query_db('SELECT * FROM users WHERE id = ?', [id])
    if u:
        return True
    else:
        return False

# Get a user from ID
def get_user(id):
    u = db.query_db('SELECT * FROM users WHERE id = ?', [id], one=True)
    if u is None:
        return None
    else:
        return User(u['id'], u['name'])

# Get list of all users
def get_all():
    users = db.query_db('SELECT * FROM users')
    ulist = []
    for u in users:
        adm = False
        if u['admin'] is 1:
            adm = True
        ulist.append(User(u['id'], u['name'], adm))
    return ulist
