import tracker.db as db
import tracker.user as user
import tracker.rank as rank

class Position():

    def __init__(self, pos, entity, score):
        self.pos = pos
        self.entity = entity
        self.score = score

    # Get rank from user's score
    def get_rank(self):
        return rank.get_rank(self.score)


# Leaderboard builder for user entities
def make_leaderboard(query, args=()):
    out = []
    data = db.query_db(query, args)
    if len(data) == 0: # If no flags found yet send None to template (render empty table)
        return out
    pos = 1
    for d in data:
        out.append(Position(pos, user.User(d['username'], d['displayname'], 0), d['score']))  # Using 0 for admin as ignored in this context
        pos += 1
    return out

# Get global leaderboard data
def get_global():
    return make_leaderboard('''
        SELECT u.username, u.displayname, SUM(f.value) AS score
        FROM flagsfound ff
        LEFT JOIN flags f ON f.flag = ff.flag_id
        LEFT JOIN users u ON u.username = ff.user_id
        GROUP BY u.username
        ORDER BY score DESC
    ''')
