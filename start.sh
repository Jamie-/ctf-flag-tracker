#!/usr/bin/env bash

# Check for database existence, create if required
/opt/tracker/venv/bin/python3 /opt/tracker/tracker/db.py

/opt/tracker/venv/bin/gunicorn -b 0.0.0.0:8080 -w 3 --chdir /opt/tracker tracker:app
