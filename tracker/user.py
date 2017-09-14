import tracker.db as db
import tracker.event as event

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

    def get_global_score(self):
        return db.query_db('SELECT SUM(f.value) FROM flagsfound ff LEFT JOIN flags f ON f.flag = ff.flag_id LEFT JOIN users u ON u.id = ff.user_id WHERE ff.user_id = ?', [self.id], one=True)[0]

    # Get list of events attended by user (by looking at flags found)
    def get_events_attended(self):
        events = db.query_db('SELECT e.id AS id, e.name AS name FROM events e LEFT JOIN flags f ON f.event_id = e.id LEFT JOIN flagsfound ff ON ff.flag_id = f.flag LEFT JOIN users u ON u.id = ff.user_id WHERE u.id IS NOT NULL AND u.id = ? GROUP BY e.id', [self.id])
        if events is None:
            return None
        else:
            elist = []
            for e in events:
                elist.append(event.Event(e['id'], e['name']))
            return elist

    # Get number of flags found by user
    def get_no_flags(self):
        return db.query_db('SELECT COUNT(*) FROM flagsfound WHERE user_id = ?', [self.id], one=True)[0]

    # Get user's score for current event
    def get_current_event_score(self):
        score = db.query_db(
            'SELECT SUM(f.value) FROM users u LEFT JOIN flagsfound ff ON ff.user_id = u.id LEFT JOIN flags f ON f.flag = ff.flag_id WHERE f.event_id = ? AND u.id = ?',
            (event.get_active().id, self.id),
            one=True
        )[0]
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
