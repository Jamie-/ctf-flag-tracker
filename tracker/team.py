import tracker.db as db

class Team():

    def __init__(self, name, event_id):
        self.name = name
        self.event_id = event_id


# Get team object from ID
def get_team(name, event_id):
    q = db.query_db('SELECT * FROM team WHERE name = ? AND event_id = ?', (name, event_id), one=True)
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
