import tracker.db as db
import tracker.user as user
import tracker.rank as rank

class Position():

    def __init__(self, pos, entity, score, num_flags):
        self.pos = pos
        self.entity = entity
        self.score = score
        self.num_flags = num_flags

    # Get rank from user's score - only applied if self.entity is User
    def get_rank(self):
        return rank.get_rank(self.entity.get_global_score())


# Leaderboard builder for user entities
def make_leaderboard(query, args=()):
    out = []
    data = db.query_db(query, args)
    if len(data) == 0: # If no flags found yet send None to template (render empty table)
        return out
    pos = 1
    for d in data:
        out.append(Position(pos, user.User(d['username'], d['displayname'], 0), d['score'], d['num_flags']))  # Using 0 for admin as ignored in this context
        pos += 1
    return out

# Get global leaderboard data
def get_global():
    return make_leaderboard('''
        SELECT u.username, u.displayname, SUM(f.value) AS score, COUNT(f.flag) as num_flags
        FROM flagsfound ff
        LEFT JOIN flags f ON f.flag = ff.flag_id
        LEFT JOIN users u ON u.username = ff.user_id
        GROUP BY u.username
        ORDER BY score DESC
    ''')
