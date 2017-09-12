import tracker.db as db

class Event():

    def __init__(self, id, name):
        self.id = id
        self.name = name


# Get an event object from an event ID
def get_event(id):
    f = db.query_db('SELECT * FROM events WHERE id = ?', [id], one=True)
    if f is None:
        return None
    else:
        return Event(f['id'], f['name'])
