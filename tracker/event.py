import tracker.db as db
import tracker.leaderboard as leaderboard

class Event():

    def __init__(self, id, name, no_flags=None, points=None):
        self.id = id
        self.name = name
        self.no_flags = no_flags
        self.points = points


# Get an event object from an event ID
def get_event(id):
    q = db.query_db('SELECT * FROM events WHERE id = ?', [id], one=True)
    if q is None:
        return None
    else:
        return Event(q['id'], q['name'], _get_no_flags(id))

# Get currently active event
def get_active():
    q = db.query_db('SELECT * FROM events WHERE active = 1', one=True)
    if q is None:
        return None
    else:
        return Event(q['id'], q['name'])

# Get event leaderboard (from leaderboard builder)
def get_leaderboard(event_id):
    return leaderboard.get_leaderboard('SELECT u.id, u.name, SUM(f.value) AS score FROM flagsfound ff LEFT JOIN flags f ON f.flag = ff.flag_id LEFT JOIN users u ON u.id = ff.user_id WHERE f.event_id = ? GROUP BY u.id ORDER BY score DESC', [event_id])

def get_all_events():
    events = db.query_db('SELECT e.id AS id, e.name AS name, COUNT(e.name) AS num, SUM(f.value) as points FROM events e LEFT JOIN flags f ON f.event_id = e.id GROUP BY e.name ORDER BY e.id DESC')
    if events is None:
        return None

    e_list = []
    for e in events:
        e_list.append(Event(e['id'], e['name'], e['num'], e['points']))

    return e_list

# Get number of flags in an event
def _get_no_flags(event_id):
    return db.query_db('SELECT COUNT(*) AS num FROM flags WHERE event_id = ?', [event_id], one=True)['num']
