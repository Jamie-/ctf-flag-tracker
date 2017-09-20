import tracker.db as db

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
