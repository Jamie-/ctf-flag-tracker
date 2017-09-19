import tracker.db as db
import tracker.leaderboard as leaderboard

class Team():

    def __init__(self, name, event_id):
        self.name = name
        self.event_id = event_id

    # Get leaderboard of all users in this team
    def get_leaderboard(self, limit=None):
        q = '''
            SELECT u.name AS name, u.id AS id, SUM(f.value) AS score
            FROM flagsfound ff
            LEFT JOIN flags f ON f.flag = ff.flag_id
            LEFT JOIN teamusers tu ON ff.user_id = tu.user_id
            LEFT JOIN users u ON ff.user_id = u.id
            WHERE tu.event_id = ? AND f.event_id = ? AND tu.team_name = ?
            GROUP BY u.id
            ORDER BY score DESC
        '''
        if limit is not None:  # Limit number of users returned
            return leaderboard.get_leaderboard(q + ' LIMIT ?', (self.event_id, self.event_id, self.name, limit))
        return leaderboard.get_leaderboard(q, (self.event_id, self.event_id, self.name))


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
