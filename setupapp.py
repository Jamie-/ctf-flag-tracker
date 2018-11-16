import os
import sys
import json
import logging
import tracker

logger = logging.getLogger(__name__)

def log_sys_info():
    import platform
    logger.info('Tracker initialisation starting...')
    logger.info('Version: %s', get_version())
    logger.info('Python version: %s', platform.python_version())
    logger.info('OS: %s', platform.platform())
    logger.info('On Git commit: %s', git_hash())

def get_version():
    with open('VERSION') as f:
        return f.readline().strip()

def git_hash():
    import subprocess
    return subprocess.check_output(['git', 'rev-parse', 'HEAD']).decode().strip()

def setupdb(uri):
    if not os.path.isfile(uri):
        logger.info('No database file found, initialising new database...')
        tracker.db.init_db()
        logger.info('Done.')
    else:
        logger.info('Database file found.')


if __name__ == '__main__':
    try:
        # Load config
        with open('/srv/tracker/config.json') as f:
            config = json.load(f)

        # Log status
        log_sys_info()

        # Setup DB
        setupdb(config['SQLITE_URI'])
    except Exception as e:
        logger.exception(e)
        sys.exit(1)
