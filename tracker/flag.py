import logging
import hashlib
import datetime
import re
import flask_login
import tracker.db as db
import tracker.user as user
import tracker.event as event

logger = logging.getLogger(__name__)

class Flag():

    def __init__(self, flag, value, event=None, notes=None):
        self.flag = flag
        self.value = value
        self.event = event
        self.notes = notes

    # Generate (URL safe) hash for flag
    def compute_hash(self):
        return _compute_hash(self.flag)

    # Get number of people who found this flag
    def found_count(self):
        return db.query_db('''
            SELECT COUNT(*)
            FROM flagsfound
            WHERE flag_id = ?
        ''', [self.flag], one=True)[0]

    def get_timestamp(self, username):
        res = db.query_db('SELECT * FROM flagsfound WHERE flag_id = ? AND user_id = ?', (self.flag, username), one=True)
        if res is None or res['timestamp'] is None:
            return None
        return datetime.datetime.strptime(res['timestamp'], '%Y-%m-%d %H:%M:%S')

    def get_timestamp_str(self, username):
        t = self.get_timestamp(username)
        if t is None:
            return None
        return t.strftime('%d-%m-%Y %H:%M:%S UTC')

    # Get name of event flag is part of (or None if not part of an event)
    def get_event_name(self):
        if self.event == None:
            return None
        return db.query_db('SELECT * FROM events WHERE id = ?', [self.event.id], one=True)['name']

    # Get list of users who found this flag
    def get_users_found(self):
        res = db.query_db('SELECT * FROM flagsfound WHERE flag_id = ?', [self.flag])
        users = []
        for u in res:
            users.append(user.get_user(u['user_id']))
        return users

    # Get owner of flag if specified
    def get_owner(self):
        res = db.query_db('SELECT * FROM flags WHERE flag = ?', [self.flag], one=True)
        if res['user'] is None:
            return None
        return user.get_user(res['user'])


# Generate (URL safe) hash for flag
def _compute_hash(flag):
    return hashlib.sha256(flag.encode('utf-8')).hexdigest()[:16]

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
    if not exists(flag):
        logger.info("^%s^ submitted an invalid flag: '%s'.", user, flag)
        return False

    # Check if user already has flag
    f = db.query_db('SELECT * FROM flagsfound WHERE flag_id = ? AND user_id = ?', (flag, user), one=True)
    if f is not None:
        logger.info("^%s^ submitted a flag they have submitted before ('%s').", user, flag)
        return None

    # If above complete, mark user as having found the flag
    ts = datetime.datetime.now().strftime('%Y-%m-%d %H:%M:%S')
    db.query_db('INSERT INTO flagsfound (flag_id, user_id, timestamp) VALUES (?, ?, ?)', (flag, user, ts))
    logger.info("^%s^ found flag '%s'.", user, flag)
    return True

#(admin) delete flag from user
def remove_flag(flag, user):
    # Unmark user as having found the flag.
    db.query_db('DELETE FROM flagsfound WHERE flag_id = ? AND user_id = ?', (flag, user))
    logger.info("^%s^ removed flag '%s' from ^%s^.", flask_login.current_user.get_id(), flag, user)

# Check if flag exists
def exists(flag):
    if db.query_db('SELECT * FROM flags WHERE flag = ?', [flag], one=True) is None:
        return False
    return True

# Add flag
def add(flag_str, value, event_id, notes, user_id):
    flag = unwrap(flag_str)  # Unwrap flag notation
    if event_id is None:
        db.query_db('''
          INSERT INTO flags (flag, hash, value, notes, user)
          VALUES (?, ?, ?, ?, ?)
        ''', (flag, _compute_hash(flag), value, notes, user_id))
    else:
        db.query_db('''
            INSERT INTO flags (flag, hash, value, event_id, notes, user)
            VALUES (?, ?, ?, ?, ?, ?)
        ''', (flag, _compute_hash(flag), value, event_id, notes, user_id))
    logger.info("^%s^ added the flag '%s'.", flask_login.current_user.get_id(), flag)


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
    logger.info("^%s^ updated the flag '%s'.", flask_login.current_user.get_id(), flag)


# Delete flag
def delete(flag):
    db.query_db('DELETE FROM flags WHERE flag = ?', [flag])
    db.query_db('DELETE FROM flagsfound WHERE flag_id = ?', [flag])
    logger.info("^%s^ deleted the flag '%s'.", flask_login.current_user.get_id(), flag)


def get_flag(flag_str):
    flag = unwrap(flag_str)
    f = db.query_db('SELECT * FROM flags WHERE flag = ?', [flag], one=True)
    if f is None:
        return None
    else:
        if f['event_id']:
            return Flag(f['flag'], f['value'], event.get_event(f['event_id']), f['notes'])
        return Flag(f['flag'], f['value'], notes=f['notes'])


# Get flag by hash
def get_by_hash(hash):
    f = db.query_db('SELECT * FROM flags WHERE hash = ?', [hash], one=True)
    if f is None:
        return None
    return get_flag(f['flag'])


# Get list of all flags
def get_all(user=None):
    if user is None:
        res = db.query_db('SELECT * FROM flags')
    else:
        res = db.query_db('SELECT * FROM flags WHERE user = ?', [user.get_id()])
    flags = []
    if res is not None:
        for f in res:
            flags.append(Flag(f['flag'], f['value'], event.get_event(f['event_id']), f['notes']))
    return flags
