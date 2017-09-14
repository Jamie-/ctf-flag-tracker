import tracker.db as db

class Position():

    def __init__(self, pos, id, name, rank, score):
        self.pos = pos
        self.id = id
        self.name = name
        self.rank = rank
        self.score = score


# Get global leaderboard data
def get_data():
    return get_leaderboard('SELECT u.id, u.name, SUM(f.value) AS score FROM flagsfound ff LEFT JOIN flags f ON f.flag = ff.flag_id LEFT JOIN users u ON u.id = ff.user_id GROUP BY u.id ORDER BY score DESC')

# Create list of positions from SQL query
def get_leaderboard(query, args=()):
    users = []
    data = db.query_db(query, args)

    if len(data) == 0:  # If no flags found yet send None to template (render empty table)
        return None

    pos = 1
    for u in data:
        users.append(Position(pos, u[0], u[1], get_rank(u[2]), u[2]))
        pos += 1

    return users

# Get rank from user's score
def get_rank(score):
    if score > 70:
        return '1337 h4x0r!'
    elif score > 40:
        return 'Member of Anonymous'
    elif score > 20:
        return 'script kiddie'
    else:
        return 'noob'