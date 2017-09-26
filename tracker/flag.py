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

# Check if flag exists
def exists(flag):
    if db.query_db('SELECT * FROM flags WHERE flag = ?', [flag], one=True) is None:
        return False
    return True

# Add flag
def add(flag, value, event_id):
    if event_id is None:
        db.query_db('''
          INSERT INTO flags (flag, value)
          VALUES (?, ?)
        ''', (flag, value))
    else:
        db.query_db('''
            INSERT INTO flags (flag, value, event_id)
            VALUES (?, ?, ?)
        ''', (flag, value, event_id))

# Update flag
def update(flag, value, event_id):
    if event_id is None:
        db.query_db('''
          UPDATE flags
          SET value = ?, event_id = NULL
          WHERE flag = ?
        ''', (value, flag))
    else:
        db.query_db('''
            UPDATE flags
          SET value = ?, event_id = ?
          WHERE flag = ?
        ''', (value, event_id, flag))

# Delete flag
def delete(flag):
    db.query_db('DELETE FROM flags WHERE flag = ?', [flag])

def get_flag(flag):
    f = db.query_db('SELECT * FROM flags WHERE flag = ?', [flag], one=True)
    if f is None:
        return None
    else:
        if f['event_id']:
            return Flag(f['flag'], f['value'], event.get_event(f['event_id']))
        return Flag(f['flag'], f['value'])

# Get list of all flags
def get_all():
    flags = db.query_db('SELECT * FROM flags')
    flist = []
    if flags is not None:
        for f in flags:
            flist.append(Flag(f['flag'], f['value'], f['event_id']))
    return flist
