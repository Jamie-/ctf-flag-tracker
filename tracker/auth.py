import ldap3
import json
import tracker
from tracker.user import User
import tracker.db as db

@tracker.lm.user_loader
def load_user(id):
    user = db.query_db('SELECT * FROM users WHERE id = ?', [id], one=True)
    return User(user['id'], user['name'])

def check_login(user, password):
    try:
        conn = ldap3.Connection(ldap3.Server(tracker.app.config['LDAP_HOST'], port=636, use_ssl=True),
                    auto_bind=ldap3.AUTO_BIND_NO_TLS,
                    read_only=True,
                    check_names=True,
                    user=user.lower()+'@'+tracker.app.config['LDAP_DOMAIN'],
                    password=password)

        conn.search(search_base=tracker.app.config['LDAP_SEARCH_BASE'],
                    search_filter='(samAccountName=' + user.lower() + ')',
                    search_scope=ldap3.SUBTREE,
                    attributes=ldap3.ALL_ATTRIBUTES)

        try:
            response = json.loads(conn.response_to_json())
        except ValueError:
            return False

        conn.unbind()

        if response:
            attrs = response['entries'][0]['attributes']
            name = user # Fallback if unable to get name from LDAP
            try: # Try 'display name' first
                name = attrs['displayName']
            except KeyError:
                try: # Try 'name' second
                    name = attrs['name']
                except KeyError:
                    try:  # Try first + last third
                        name = attrs['givenName'] + ' ' + attrs['sn']
                    except KeyError:
                        pass # Give up and just use username

            # Add user to DB or update user in DB before returning
            db_user = db.query_db('SELECT * FROM users WHERE id = ?', [user.lower()], one=True)
            if db_user is None:
                # Add user
                db.query_db('INSERT INTO users(id, name) VALUES(?, ?)', (user.lower(), name))
            elif not db_user['name'] == name:
                # Update user's name if changed in LDAP
                db.query_db('UPDATE users SET name = ? WHERE id = ?', (name, user.lower()))

            return User(user.lower(), name)
        return False
    except ldap3.core.exceptions.LDAPBindError:
        return False
