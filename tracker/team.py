import tracker.db as db
import tracker.user as user
import tracker.leaderboard as leaderboard

class Team():

    def __init__(self, name, event_id):
        self.name = name
        self.event_id = event_id

    # Get leaderboard of all users in this team
    def get_leaderboard(self, limit=None):
        q = '''
            SELECT u.id AS id, u.name AS name, SUM(f.value) AS score
            FROM flagsfound ff
            LEFT JOIN flags f ON f.flag = ff.flag_id
            LEFT JOIN teamusers tu ON ff.user_id = tu.user_id
            LEFT JOIN users u ON ff.user_id = u.id
            WHERE tu.event_id = ? AND f.event_id = ? AND tu.team_name = ?
            GROUP BY u.id
            ORDER BY score DESC
        '''
        if limit is not None:  # Limit number of users returned
            return user.make_leaderboard(q + ' LIMIT ?', (self.event_id, self.event_id, self.name, limit))
        return user.make_leaderboard(q, (self.event_id, self.event_id, self.name))

    # Get number of members in this team
    def get_num_members(self):
        return db.query_db('''
            SELECT COUNT(*)
            FROM teams t
            LEFT JOIN teamusers tu ON tu.team_name = t.name AND tu.event_id = t.event_id
            WHERE t.event_id = ? AND t.name = ?
            GROUP BY t.name
        ''', (self.event_id, self.name), one=True)[0]

# Get team object from ID
def get_team(name, event_id):
    q = db.query_db('SELECT * FROM teams WHERE name = ? AND event_id = ?', (name, event_id), one=True)
    if q is None:
        return None
    return Team(q['name'], q['event_id'])

# Create a team (in DB)
def create_team(name, event_id):
    try:
        db.query_db('INSERT INTO teams (name, event_id) VALUES (?, ?)', (name, event_id))
    except db.IntegrityError:
        return False
    return True

# Add a user to a team
def join_team(user_id, name, event_id):
    # See if team exists
    q = db.query_db('SELECT * FROM teams WHERE name = ? AND event_id = ?', (name, event_id))
    if len(q) is 0:
        return False

    try:
        db.query_db('INSERT INTO teamusers (team_name, event_id, user_id) VALUES (?, ?, ?)', (name, event_id, user_id))
    except db.IntegrityError:
        return False
    return True

# Leaderboard builder for team entities
def make_leaderboard(query, args=()):
    out = []
    data = db.query_db(query, args)
    if len(data) == 0:  # If no flags found yet send None to template (render empty table)
        return out
    pos = 1
    for d in data:
        out.append(leaderboard.Position(pos, Team(d['name'], d['event_id']), d['score']))
        pos += 1
    return out
