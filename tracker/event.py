import tracker.db as db
import tracker.leaderboard as leaderboard
import tracker.team as team

class Event():

    def __init__(self, id, name):
        self.id = id
        self.name = name

    # Get number of flags available in this event
    def get_num_flags(self):
        num = db.query_db('''
            SELECT COUNT(*)
            FROM flags f
            WHERE f.event_id = ?
            GROUP BY f.event_id
        ''', [self.id], one=True)
        if num is None:
            return 0
        return num[0]

    # Get number of points available in this event
    def get_num_points(self):
        num = db.query_db('''
            SELECT SUM(f.value)
            FROM events e
            LEFT JOIN flags f ON f.event_id = e.id
            WHERE e.id = ?
            GROUP BY e.id;
        ''', [self.id], one=True)[0]
        if num is None:
            return 0
        return num

    # Check to see if current event is active event
    def is_active(self):
        teams = db.query_db('SELECT active FROM events WHERE id = ?', [self.id], one=True)[0]
        if teams is not None and teams == 1:
            return True
        return False

    # Check to see if teams flag has been set for this event
    def has_teams(self):
        teams = db.query_db('SELECT has_teams FROM events WHERE id = ?', [self.id], one=True)[0]
        if teams is not None and teams == 1:
            return True
        return False

    # Get team given name in this event
    def get_team(self, team_name):
        q = db.query_db('SELECT * FROM teams WHERE name = ? AND event_id = ?', (team_name, self.id), one=True)
        if q is None:
            return None
        return team.Team(q['name'], q['event_id'])

    # Add a user to a team in this event
    def add_user_to_team(self, user_id, team_name):
        # See if team exists
        t = self.get_team(team_name)
        if t is None:
            return False
        try:
            db.query_db('INSERT INTO teamusers (team_name, event_id, user_id) VALUES (?, ?, ?)', (team_name, self.id, user_id))
        except db.IntegrityError:
            return False
        return True

    # Get team given user is in for this event
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

    # Get event individual leaderboard (from user leaderboard builder)
    def get_leaderboard(self, limit=None):
        q = '''
            SELECT u.id, u.name, SUM(f.value) AS score
            FROM flagsfound ff
            LEFT JOIN flags f ON f.flag = ff.flag_id
            LEFT JOIN users u ON u.id = ff.user_id
            WHERE f.event_id = ?
            GROUP BY u.id
            ORDER BY score DESC
        '''
        if limit is not None:  # Limit number of users returned
            return leaderboard.make_leaderboard(q + ' LIMIT ?', (self.id, limit))
        return leaderboard.make_leaderboard(q, [self.id])

    # Get leaderboard of teams in this event (from team leaderboard builder)
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


# Check event exists
def exists(id):
    if db.query_db('SELECT * FROM events WHERE id = ?', [id], one=True) is None:
        return False
    return True

# Get an event object from an event ID
def get_event(id):
    return make_event_from_row(db.query_db('''
        SELECT e.id AS id, e.name AS name
        FROM events e
        WHERE e.id = ?
    ''', [id], one=True))

# Create event
def create(id, name, teams, active):
    if (active is 1) and (get_active() is not None): # Deactive current active event
        db.query_db('UPDATE events SET active = 0 WHERE active = 1')
    # Insert new event
    db.query_db('''
        INSERT INTO events (id, name, has_teams, active)
        VALUES (?, ?, ?, ?)
    ''', (id, name, teams, active))

# Update event
def update(id, name, teams, active):
    if (active is 1) and (get_active() is not None): # Deactive current active event
        db.query_db('UPDATE events SET active = 0 WHERE active = 1')
    # Update record
    db.query_db('''
        UPDATE events
        SET name = ?, has_teams = ?, active = ?
        WHERE id = ?
    ''', (name, teams, active, id))

# Delete event
def delete(id):
    db.query_db('''
        DELETE FROM events
        WHERE id = ?
    ''', [id])

#TODO Not happy with this being here, it ideally needs to be in user: u.get_events(), but this causes loop on event import.
# Get list of events attended by user (by looking at flags found)
def by_user(user_id):
    return make_list_from_query(db.query_db('''
        SELECT e.id AS id, e.name AS name
        FROM events e
        LEFT JOIN flags f ON f.event_id = e.id
        LEFT JOIN flagsfound ff ON ff.flag_id = f.flag
        LEFT JOIN users u ON u.id = ff.user_id
        WHERE u.id IS NOT NULL AND u.id = ?
        GROUP BY e.id
    ''', [user_id]))

# Get currently active event
def get_active():
    return make_event_from_row(db.query_db('SELECT * FROM events WHERE active = 1', one=True))

# Get list of all events
def get_all():
    return make_list_from_query(db.query_db('''
        SELECT e.id AS id, e.name AS name
        FROM events e
        ORDER BY e.id DESC
    '''))

# Make list of events from DB query result
def make_list_from_query(query):
    l = []
    if query is not None:
        for e in query:
            l.append(make_event_from_row(e))
    return l

# Make event object from DB row
def make_event_from_row(row):
    if row is None:
        return None
    return Event(row['id'], row['name'])
