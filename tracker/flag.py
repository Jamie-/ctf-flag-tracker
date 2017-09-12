import tracker.db as db
import tracker.event as event

class Flag():

    def __init__(self, flag, value, event=None):
        self.flag = flag
        self.value = value
        self.event = event


def check(flag, user):
    # Check if flag is valid
    f = db.query_db('SELECT * FROM flags WHERE flag = ?', [flag], one=True)
    if f is None:
        return False

    # Check if user already has flag
    f = db.query_db('SELECT * FROM flagsfound WHERE flag_id = ? AND user_id = ?', (flag, user), one=True)
    if f is not None:
        return None

    # If above complete, mark user as having found the flag
    db.query_db('INSERT INTO flagsfound (flag_id, user_id) VALUES (?, ?)', (flag, user))
    return True

def get_flag(flag):
    f = db.query_db('SELECT * FROM flags WHERE flag = ?', [flag], one=True)
    if f is None:
        return None
    else:
        if f['event_id']:
            return Flag(f['flag'], f['value'], event.get_event(f['event_id']))
        return Flag(f['flag'], f['value'])
