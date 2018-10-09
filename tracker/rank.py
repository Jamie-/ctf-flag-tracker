import logging
import flask_login
import tracker.db as db

logger = logging.getLogger(__name__)


class Rank():

    def __init__(self, rank, score):
        self.rank = rank
        self.score = score


# Get list of all ranks
def get_all():
    ranks = db.query_db('SELECT * FROM ranks ORDER BY score ASC')
    rlist = []
    if ranks is not None:
        for r in ranks:
            rlist.append(Rank(r['rank'], r['score']))
    return rlist

# Get rank for score
def get_rank(score):
    ranks = db.query_db('SELECT * FROM ranks ORDER BY score DESC')
    if ranks is not None:
        for r in ranks:
            if score >= r['score']:
                return r['rank']

# Check rank exists
def exists(rank):
    if db.query_db('SELECT * FROM ranks WHERE rank = ?', [rank], one=True) is None:
        return False
    return True


# Add rank to DB
def add(rank, score):
    db.query_db('INSERT INTO ranks (rank, score) VALUES (?, ?)', (rank, score))
    logger.info("^%s^ added the rank '%s'.", flask_login.current_user.username, rank)


# Update rank in DB
def update(rank, score):
    db.query_db('UPDATE ranks SET score = ? WHERE rank = ?', (score, rank))
    logger.info("^%s^ updated the rank '%s'.", flask_login.current_user.username, rank)


# Delete rank in DB
def delete(rank):
    db.query_db('DELETE FROM ranks WHERE rank = ?', [rank])
    logger.info("^%s^ deleted the rank '%s'.", flask_login.current_user.username, rank)
