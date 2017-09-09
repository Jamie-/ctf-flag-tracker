class User():

    def __init__(self, id, name):
        self.id = id
        self.name = name
        self.score = 0

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

    def add_score(self, n):
        self.score += n

    def get_rank_html(self):
        return 'noob'

    def __repr__(self):
        return '<User %r>' % self.id
