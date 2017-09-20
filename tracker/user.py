import tracker.db as db
import tracker.leaderboard as leaderboard

class User():

    def __init__(self, id, name):
        self.id = id
        self.name = name

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

    # Get user's global score
    def get_global_score(self):
        return db.query_db('''
            SELECT SUM(f.value)
            FROM flagsfound ff
            LEFT JOIN flags f ON f.flag = ff.flag_id
            LEFT JOIN users u ON u.id = ff.user_id
            WHERE ff.user_id = ?
        ''', [self.id], one=True)[0]

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

# Leaderboard builder for user entities
def make_leaderboard(query, args=()):
    out = []
    data = db.query_db(query, args)
    if len(data) == 0: # If no flags found yet send None to template (render empty table)
        return []
    pos = 1
    for d in data:
        out.append(leaderboard.Position(pos, User(d['id'], d['name']), d['score']))
        pos += 1
    return out

# Get global leaderboard data
def get_global_leaderboard():
    return make_leaderboard('''
        SELECT u.id, u.name, SUM(f.value) AS score
        FROM flagsfound ff
        LEFT JOIN flags f ON f.flag = ff.flag_id
        LEFT JOIN users u ON u.id = ff.user_id
        GROUP BY u.id
        ORDER BY score DESC
    ''')
