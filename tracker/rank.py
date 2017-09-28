import tracker.db as db

class Rank():

    def __init__(self, rank, score):
        self.rank = rank
        self.score = score


# Get list of all ranks
def get_all():
    ranks = db.query_db('SELECT * FROM ranks')
    rlist = []
    if ranks is not None:
        for r in ranks:
            rlist.append(Rank(r['rank'], r['score']))
    return rlist

# Check rank exists
def exists(rank):
    if db.query_db('SELECT * FROM ranks WHERE rank = ?', [rank], one=True) is None:
        return False
    return True

# Add rank to DB
def add(rank, score):
    db.query_db('INSERT INTO ranks (rank, score) VALUES (?, ?)', (rank, score))

# Update rank in DB
def update(rank, score):
    db.query_db('UPDATE ranks SET score = ? WHERE rank = ?', (score, rank))

# Delete rank in DB
def delete(rank):
    db.query_db('DELETE FROM ranks WHERE rank = ?', [rank])
