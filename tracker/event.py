import tracker.db as db
import tracker.leaderboard as leaderboard
import tracker.user as user
import tracker.team as team

class Event():

    def __init__(self, id, name, no_flags=None, points=None):
        self.id = id
        self.name = name
        self.no_flags = no_flags
        self.points = points

    # Check to see if teams flag has been set for this event
    def has_teams(self):
        teams = db.query_db('SELECT has_teams FROM events WHERE id = ?', [self.id], one=True)[0]
        if teams is not None and teams == 1:
            return True
        return False

    # Get team given name in this event
    def get_team(self, team_name):
        return team.get_team(team_name, self.id)

    # Get team this user is in for given event ID
    def get_users_team(self, user_id):
        q = db.query_db('''
            SELECT t.name AS name, t.event_id AS event_id
            FROM teams t
            LEFT JOIN teamusers tu ON t.name = tu.team_name AND t.event_id = tu.event_id
            WHERE tu.user_id = ?
            AND t.event_id = ?
        ''', (user_id, self.id), one=True)
        if q is None:
            return None
        return team.Team(q['name'], q['event_id'])

    # Get event leaderboard (from leaderboard builder)
    def get_leaderboard(self, limit=None):
        if limit is not None:  # Limit number of users returned
            return leaderboard.make_leaderboard('SELECT u.id, u.name, SUM(f.value) AS score FROM flagsfound ff LEFT JOIN flags f ON f.flag = ff.flag_id LEFT JOIN users u ON u.id = ff.user_id WHERE f.event_id = ? GROUP BY u.id ORDER BY score DESC LIMIT ?', (self.id, limit))
        return leaderboard.make_leaderboard('SELECT u.id, u.name, SUM(f.value) AS score FROM flagsfound ff LEFT JOIN flags f ON f.flag = ff.flag_id LEFT JOIN users u ON u.id = ff.user_id WHERE f.event_id = ? GROUP BY u.id ORDER BY score DESC', [self.id])

    # Get leaderboard for team in this event (from the leaderboard builder)
    def get_team_leaderboard(self, limit=None):
        q = '''
            SELECT name, event_id, SUM(score) AS score
            FROM (
                SELECT tu.team_name AS name, tu.event_id as event_id, SUM(f.value) AS score
                FROM flagsfound ff
                LEFT JOIN flags f ON f.flag = ff.flag_id
                LEFT JOIN teamusers tu ON tu.event_id = f.event_id AND tu.user_id = ff.user_id
                WHERE tu.event_id = ?
                GROUP BY tu.team_name
                UNION
                SELECT t.name as name, t.event_id as event_id, 0 AS score
                FROM teams t
                WHERE event_id = ?
            ) GROUP BY name
            ORDER BY score DESC
        '''
        if limit is not None: # Limit number of teams returned
            return team.make_leaderboard(q + ' LIMIT ?', (self.id, self.id, limit))
        return team.make_leaderboard(q, (self.id, self.id))


# Get an event object from an event ID
def get_event(id):
    q = db.query_db('SELECT * FROM events WHERE id = ?', [id], one=True)
    if q is None:
        return None
    else:
        return Event(q['id'], q['name'], _get_no_flags(id))

# Get list of events attended by user (by looking at flags found)
def by_user(user_id):
    events = db.query_db('''
        SELECT e.id AS id, e.name AS name
        FROM events e
        LEFT JOIN flags f ON f.event_id = e.id
        LEFT JOIN flagsfound ff ON ff.flag_id = f.flag
        LEFT JOIN users u ON u.id = ff.user_id
        WHERE u.id IS NOT NULL AND u.id = ?
        GROUP BY e.id
    ''', [user_id])
    if events is None:
        return None
    else:
        elist = []
        for e in events:
            elist.append(Event(e['id'], e['name']))
        return elist

# Get currently active event
def get_active():
    q = db.query_db('SELECT * FROM events WHERE active = 1', one=True)
    if q is None:
        return None
    else:
        return Event(q['id'], q['name'])

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
