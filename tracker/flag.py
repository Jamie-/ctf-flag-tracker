import logging
import re
import tracker.db as db
import tracker.event as event

logger = logging.getLogger(__name__)

class Flag():

    def __init__(self, flag, value, event=None, notes=None):
        self.flag = flag
        self.value = value
        self.event = event
        self.notes = notes

    # Get number of people who found this flag
    def found_count(self):
        return db.query_db('''
            SELECT COUNT(*)
            FROM flagsfound
            WHERE flag_id = ?
        ''', [self.flag], one=True)[0]


def unwrap(flag_str):  # If flag is wrapped in flag{...}, strip it off
    flag_pattern = re.compile('^flag{.+}$')
    if flag_pattern.match(flag_str):
        return flag_str[5:-1]
    else:
        return flag_str

def check(flag_str, user):
    # Check if flag is wrapped in flag{...}
    flag = unwrap(flag_str)

    # Check if flag is valid
    f = db.query_db('SELECT * FROM flags WHERE flag = ?', [flag], one=True)
    if f is None:
        logger.info("'%s' submitted an invalid flag: '%s'.", user, flag)
        return False

    # Check if user already has flag
    f = db.query_db('SELECT * FROM flagsfound WHERE flag_id = ? AND user_id = ?', (flag, user), one=True)
    if f is not None:
        logger.info("'%s' submitted a flag they have submitted before ('%s').", user, flag)
        return None

    # If above complete, mark user as having found the flag
    db.query_db('INSERT INTO flagsfound (flag_id, user_id) VALUES (?, ?)', (flag, user))
    logger.info("'%s' found flag '%s'.", user, flag)
    return True

# Check if flag exists
def exists(flag):
    if db.query_db('SELECT * FROM flags WHERE flag = ?', [flag], one=True) is None:
        return False
    return True

# Add flag
def add(flag_str, value, event_id, notes):
    flag = unwrap(flag_str)  # Unwrap flag notation
    if event_id is None:
        db.query_db('''
          INSERT INTO flags (flag, value, notes)
          VALUES (?, ?, ?)
        ''', (flag, value, notes))
    else:
        db.query_db('''
            INSERT INTO flags (flag, value, event_id, notes)
            VALUES (?, ?, ?, ?)
        ''', (flag, value, event_id, notes))

# Update flag
def update(flag, value, event_id, notes):
    if event_id is None:
        db.query_db('''
          UPDATE flags
          SET value = ?, event_id = NULL, notes = ?
          WHERE flag = ?
        ''', (value, notes, flag))
    else:
        db.query_db('''
            UPDATE flags
          SET value = ?, event_id = ?, notes = ?
          WHERE flag = ?
        ''', (value, event_id, notes, flag))

# Delete flag
def delete(flag):
    db.query_db('DELETE FROM flags WHERE flag = ?', [flag])
    db.query_db('DELETE FROM flagsfound WHERE flag_id = ?', [flag])

def get_flag(flag_str):
    flag = unwrap(flag_str)
    f = db.query_db('SELECT * FROM flags WHERE flag = ?', [flag], one=True)
    if f is None:
        return None
    else:
        if f['event_id']:
            return Flag(f['flag'], f['value'], event.get_event(f['event_id']), f['notes'])
        return Flag(f['flag'], f['value'], notes=f['notes'])

# Get list of all flags
def get_all():
    flags = db.query_db('SELECT * FROM flags')
    flist = []
    if flags is not None:
        for f in flags:
            flist.append(Flag(f['flag'], f['value'], f['event_id'], f['notes']))
    return flist
