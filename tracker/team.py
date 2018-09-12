import tracker.db as db
import tracker.leaderboard as leaderboard

class Team():

    def __init__(self, name, event_id):
        self.name = name
        self.event_id = event_id

    # Get leaderboard of all users in this team
    def get_leaderboard(self, limit=None):
        q = '''
            SELECT u.username AS username, u.displayname AS displayname, SUM(f.value) AS score
            FROM flagsfound ff
            LEFT JOIN flags f ON f.flag = ff.flag_id
            LEFT JOIN teamusers tu ON ff.user_id = tu.user_id
            LEFT JOIN users u ON ff.user_id = u.username
            WHERE tu.event_id = ? AND f.event_id = ? AND tu.team_name = ?
            GROUP BY u.username
            ORDER BY score DESC
        '''
        if limit is not None:  # Limit number of users returned
            return leaderboard.make_leaderboard(q + ' LIMIT ?', (self.event_id, self.event_id, self.name, limit))
        return leaderboard.make_leaderboard(q, (self.event_id, self.event_id, self.name))

    # Get number of members in this team
    def get_num_members(self):
        num = db.query_db('''
            SELECT COUNT(*)
            FROM teamusers tu
            WHERE tu.event_id = ? AND tu.team_name = ?
            GROUP BY tu.team_name
        ''', (self.event_id, self.name), one=True)
        if num is None:
            return 0
        return num[0]


# Create a team (in DB)
def create_team(name, event_id):
    try:
        db.query_db('INSERT INTO teams (name, event_id) VALUES (?, ?)', (name, event_id))
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
