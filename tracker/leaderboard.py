import tracker.db as db
import tracker.user as user

class Position():

    def __init__(self, pos, entity, score):
        self.pos = pos
        self.entity = entity
        self.score = score

    # Get rank from user's score
    def get_rank(self):
        if self.score > 70:
            return '1337 h4x0r!'
        elif self.score > 40:
            return 'Member of Anonymous'
        elif self.score > 20:
            return 'script kiddie'
        else:
            return 'noob'


# Leaderboard builder for user entities
def make_leaderboard(query, args=()):
    out = []
    data = db.query_db(query, args)
    if len(data) == 0: # If no flags found yet send None to template (render empty table)
        return out
    pos = 1
    for d in data:
        out.append(Position(pos, user.User(d['id'], d['name']), d['score']))
        pos += 1
    return out

# Get global leaderboard data
def get_global():
    return make_leaderboard('''
        SELECT u.id, u.name, SUM(f.value) AS score
        FROM flagsfound ff
        LEFT JOIN flags f ON f.flag = ff.flag_id
        LEFT JOIN users u ON u.id = ff.user_id
        GROUP BY u.id
        ORDER BY score DESC
    ''')
