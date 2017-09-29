import os

# Flask WTForms
WTF_CSRF_ENABLED = True
SECRET_KEY = 'Put a secret key here!'

# LDAP
LDAP_HOST = 'ldap.example.com'
LDAP_DOMAIN = 'example.com'
LDAP_SEARCH_BASE = 'CN=Users,DC=example,DC=com'

# DB
SQLITE_URI = os.path.join(os.path.abspath(os.path.dirname(__file__)), 'data.db')
