.DEFAULT_GOAL := run
.PHONY: clean, clean-db, init, run

clean:
	rm -rf *.pyc
	rm -rf __pycache__/

clean-db:
	rm -rf *.db

init:
	flask/bin/python3 -c 'from tracker.db import init_db; init_db()'

venv:
	virtualenv -p python3 flask
	flask/bin/pip3 install flask flask_login flask_wtf ldap3

run:
	flask/bin/python3 run.py
