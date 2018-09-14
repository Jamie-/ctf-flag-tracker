if __name__ == '__main__':
    import tracker
    import os.path
    import json

    with open('/srv/tracker/config.json') as f:
        config = json.load(f)
    if not os.path.isfile(config['SQLITE_URI']):
        print('No database file found, will initialise new database.')
        tracker.db.init_db()
        print('Done.')
    else:
        print('Database file found, skipping.')
