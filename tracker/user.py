import tracker.db as db

class User():

    def __init__(self, id, name):
        self.id = id
        self.name = name

    ## FLASK_LOGIN #################
    def is_authenticated(self):
        return True

    def is_active(self):
        return True

    def is_anonymous(self):
        return False

    def get_id(self):
        return self.id

    def get_name(self):
        return self.name
    ## /FLASK_LOGIN ################

    def get_global_score(self):
        return db.query_db('SELECT SUM(f.value) FROM flagsfound ff LEFT JOIN flags f ON f.flag = ff.flag_id LEFT JOIN users u ON u.id = ff.user_id WHERE ff.user_id = ?', [self.id], one=True)[0]

    def __repr__(self):
        return '<User %r>' % self.id


# Check whether a user exists
def exists(id):
    u = db.query_db('SELECT * FROM users WHERE id = ?', [id])
    if u:
        return True
    else:
        return False
