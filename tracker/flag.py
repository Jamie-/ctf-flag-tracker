import tracker.db as db

def check(flag, user):
    f = db.query_db('SELECT * FROM flags WHERE flag = ?', [flag], one=True)
    if f is None:
        return False
    else:
        return True
